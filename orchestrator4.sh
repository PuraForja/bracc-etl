#!/usr/bin/env bash
# orchestrator.sh — Setup + Download + Importação sequencial
# Uso: bash orchestrator.sh [fonte1 fonte2 ...]
#      bash orchestrator.sh --force fonte1     # força reimportação
#      bash orchestrator.sh --amazonas         # roda só fila Amazonas
#      bash orchestrator.sh --force --amazonas # força fila Amazonas
# Logs: pipeline_imports.log
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ETL_DIR="$ROOT/etl"
DATA_DIR="$ROOT/data"
LOG="$ROOT/pipeline_imports.log"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-changeme}"
MODO_TESTE="${MODO_TESTE:-N}"  # Y = pula leitura Neo4j, uv sync e PNCP
INSTALLED_FLAG="$ROOT/.installed"

# ── MAPA fonte → label Neo4j ──────────────────────────────────────────────────
declare -A LABEL_MAP
LABEL_MAP[bcb]="Sanction"
LABEL_MAP[bndes]="Payment"
LABEL_MAP[camara]="Expense"
LABEL_MAP[camara_inquiries]="Inquiry"
LABEL_MAP[ceaf]="Expulsion"
LABEL_MAP[cepim]="BarredNGO"
LABEL_MAP[cnpj]="Company"
LABEL_MAP[comprasnet]="Contract"
LABEL_MAP[cpgf]="GovCardExpense"
LABEL_MAP[cvm]="CVMProceeding"
LABEL_MAP[cvm_funds]="Fund"
LABEL_MAP[datasus]="Health"
LABEL_MAP[eu_sanctions]="InternationalSanction"
LABEL_MAP[holdings]="Partner"
LABEL_MAP[ibama]="Sanction"
LABEL_MAP[icij]="OffshoreEntity"
LABEL_MAP[inep]="MunicipalGazetteAct"
LABEL_MAP[leniency]="LeniencyAgreement"
LABEL_MAP[ofac]="InternationalSanction"
LABEL_MAP[opensanctions]="GlobalPEP"
LABEL_MAP[pgfn]="Sanction"
LABEL_MAP[querido_diario]="MunicipalGazetteAct"
LABEL_MAP[renuncias]="TaxWaiver"
LABEL_MAP[sanctions]="Sanction"
LABEL_MAP[senado]="Expense"
LABEL_MAP[senado_cpis]="CPI"
LABEL_MAP[siconfi]="MunicipalFinance"
LABEL_MAP[siop]="Amendment"
LABEL_MAP[tce_am]="Contract"
LABEL_MAP[tcu]="Sanction"
LABEL_MAP[tesouro_emendas]="Amendment"
LABEL_MAP[transferegov]="Payment"
LABEL_MAP[transparencia]="Contract"
LABEL_MAP[tse]="Election"
LABEL_MAP[tse_bens]="Person"
LABEL_MAP[tse_filiados]="Person"
LABEL_MAP[un_sanctions]="InternationalSanction"
LABEL_MAP[viagens]="GovTravel"
LABEL_MAP[world_bank]="InternationalSanction"
# ── AMAZONAS ──────────────────────────────────────────────────────────────────
LABEL_MAP[transparencia_am]="Person"
LABEL_MAP[ibama_am]="Sanction"
LABEL_MAP[inpe_prodes]="Sanction"
LABEL_MAP[sicar]="Contract"
LABEL_MAP[antaq]="Contract"

# ── FONTES A IGNORAR ─────────────────────────────────────────────────────────
SKIP=(
    pncp            # roda em background separado — download leva dias
)

# ── FILA NACIONAL ─────────────────────────────────────────────────────────────
DEFAULT_QUEUE=(
    tesouro_emendas
    bcb
    ceaf
    cepim
    un_sanctions
    leniency
    cvm
    cvm_funds
    ofac
    holdings
    senado_cpis
    sanctions
    querido_diario
    camara_inquiries
    cpgf
    renuncias
    datasus
    icij
    siconfi
    siop
    opensanctions
    transparencia
    tse
    viagens
    cnpj
)

# ── FILA AMAZONAS ─────────────────────────────────────────────────────────────
# Fontes específicas do estado do Amazonas
# Para adicionar novo estado: criar FILA_<ESTADO>_QUEUE com as fontes
AMAZONAS_QUEUE=(
    transparencia_am
    # ibama_am     # a implementar — embargos ambientais AM
    # inpe_prodes  # a implementar — desmatamento
    # sicar        # a implementar — Cadastro Ambiental Rural
    # antaq        # a implementar — hidrovias AM
)

# ─────────────────────────────────────────────────────────────────────────────
CURRENT_FONTE=""
CURRENT_PID=""
FORCE_REIMPORT=0
MODO_AMAZONAS=0
SKIPPED=0
ERRORS=0

graceful_shutdown() {
    echo "" | tee -a "$LOG"
    echo "  ┌─────────────────────────────────────────────┐" | tee -a "$LOG"
    echo "  │  ⚠️   INTERRUPÇÃO DETECTADA (Ctrl+C)         │" | tee -a "$LOG"
    echo "  │  Encerrando com segurança...                 │" | tee -a "$LOG"
    echo "  └─────────────────────────────────────────────┘" | tee -a "$LOG"
    if [[ -n "$CURRENT_PID" ]] && kill -0 "$CURRENT_PID" 2>/dev/null; then
        echo "  │  Aguardando processo atual terminar..." | tee -a "$LOG"
        kill -TERM "$CURRENT_PID" 2>/dev/null
        local waited=0
        while kill -0 "$CURRENT_PID" 2>/dev/null && [[ $waited -lt 30 ]]; do
            sleep 1; waited=$((waited + 1)); echo -n "." >&2
        done
        echo "" | tee -a "$LOG"
        kill -0 "$CURRENT_PID" 2>/dev/null && kill -9 "$CURRENT_PID" 2>/dev/null
        echo "  │  ✅ Processo encerrado" | tee -a "$LOG"
    fi
    echo "" | tee -a "$LOG"
    if [[ -n "$CURRENT_FONTE" ]]; then
        echo "  │  Parou em: $CURRENT_FONTE" | tee -a "$LOG"
        echo "  │  Para retomar: bash orchestrator.sh $CURRENT_FONTE" | tee -a "$LOG"
        echo "  │  Para forçar: bash orchestrator.sh --force $CURRENT_FONTE" | tee -a "$LOG"
    fi
    echo "  ⛔  ENCERRADO — $(date '+%d/%m/%Y %H:%M')" | tee -a "$LOG"
    echo "  💡  PNCP continua em background" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
    exit 0
}
trap graceful_shutdown INT TERM

# ─────────────────────────────────────────────────────────────────────────────
log_blank() { echo "" | tee -a "$LOG"; }
log_banner() {
    echo "" | tee -a "$LOG"
    echo "  ══════════════════════════════════════════════" | tee -a "$LOG"
    echo "  $1" | tee -a "$LOG"
    echo "  ══════════════════════════════════════════════" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
}
log_section() { echo "" | tee -a "$LOG"; echo "  ┌─ $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_ok()   { echo "  └─ ✅  $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_err()  { echo "  └─ ❌  $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_skip() { echo "  └─ ⏭   $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_info() { echo "  │  $*" | tee -a "$LOG"; }
beep()       { powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)" 2>/dev/null || true; }
beep_error() { powershell.exe -Command "[console]::beep(400,500); [console]::beep(400,500)" 2>/dev/null || true; }

filter_output() {
    grep -v "^  File \|^    \|^Traceback (most recent\|site-packages\|__main__\|sys\.exit\|\.invoke\|\.main\|\.callback\|frozen\|_run_module\|_run_code\|_process_result"
}

is_skipped() {
    local fonte="$1"
    for s in "${SKIP[@]}"; do [[ "$s" == "$fonte" ]] && return 0; done
    return 1
}

is_imported() {
    local fonte="$1"
    grep -q "^imported: $fonte " "$INSTALLED_FLAG" 2>/dev/null
}

mark_imported() {
    local fonte="$1"
    local tmpfile
    tmpfile=$(mktemp)
    grep -v "^imported: $fonte " "$INSTALLED_FLAG" > "$tmpfile" 2>/dev/null && mv "$tmpfile" "$INSTALLED_FLAG" || rm -f "$tmpfile"
    echo "imported: $fonte $(date '+%Y-%m-%d %H:%M:%S')" >> "$INSTALLED_FLAG"
}

neo4j_count() {
    local label="$1"
    docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
        "MATCH (n:$label) RETURN count(n) as total" 2>/dev/null \
        | grep -E '^[0-9]+$' | head -1
}

sync_neo4j_to_installed() {
    log_banner "🗄️   LENDO NEO4J"
    local synced=0 already=0 zero=0
    for fonte in "${!LABEL_MAP[@]}"; do
        local label="${LABEL_MAP[$fonte]}"
        local count
        count=$(neo4j_count "$label")
        if [[ -n "$count" ]] && [[ "$count" -gt 0 ]]; then
            if is_imported "$fonte"; then already=$((already + 1))
            else mark_imported "$fonte"; synced=$((synced + 1)); fi
        else
            zero=$((zero + 1))
        fi
    done
    log_info "Sync: $((already + synced)) com dados | $synced novas registradas | $zero sem dados"
    log_blank
}

run_setup() {
    log_banner "🔧  SETUP INICIAL"
    local errors=0
    for tool in docker git; do
        if ! command -v $tool &>/dev/null; then log_err "$tool não encontrado"; errors=$((errors + 1))
        else log_ok "$tool OK"; fi
    done
    if ! command -v uv &>/dev/null && ! ~/.local/bin/uv --version &>/dev/null 2>&1; then
        log_err "uv não encontrado. Instale: curl -LsSf https://astral.sh/uv/install.sh | sh"
        errors=$((errors + 1))
    else log_ok "uv OK"; fi
    [[ $errors -gt 0 ]] && { log_err "$errors dependência(s) faltando"; exit 1; }
    log_info "Instalando dependências Python..."
    [[ "$MODO_TESTE" == "Y" ]] || { cd "$ETL_DIR" && uv sync 2>&1 | filter_output | tee -a "$LOG"; }
    log_ok "Dependências instaladas"
    echo "installed: $(date '+%Y-%m-%d %H:%M:%S')" > "$INSTALLED_FLAG"
    log_blank
}

run_validation() {
    log_banner "🔍  VALIDAÇÃO FINAL — Neo4j"
    local raw
    raw=$(docker exec bracc-neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
        "MATCH (n) RETURN labels(n)[0] as label, count(n) as total ORDER BY total DESC" \
        2>/dev/null | grep -v "^label\|^$\|rows\|ms")
    [[ -z "$raw" ]] && { log_err "Não foi possível conectar ao Neo4j"; return; }
    local ok=0 total_nodes=0
    while IFS= read -r line; do
        local label count
        label=$(echo "$line" | awk -F'"' '{print $2}')
        count=$(echo "$line" | awk -F',' '{print $2}' | tr -d ' ')
        [[ -z "$label" || -z "$count" ]] && continue
        log_info "  ✅  $label: $count nodes"
        ok=$((ok + 1)); total_nodes=$((total_nodes + count))
    done <<< "$raw"
    log_blank
    log_info "Total: $ok labels | ~$total_nodes nodes no banco"
    log_blank
}

start_docker() {
    log_banner "🐳  DOCKER"
    cd "$ROOT"
    docker compose up -d 2>&1 | filter_output | tee -a "$LOG"
    log_info "Aguardando Neo4j healthy..."
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        local status
        status=$(docker inspect --format='{{.State.Health.Status}}' bracc-neo4j 2>/dev/null || echo "starting")
        [[ "$status" == "healthy" ]] && { log_ok "Neo4j healthy"; return 0; }
        attempts=$((attempts + 1)); log_info "Neo4j: $status ($attempts/30)..."; sleep 10
    done
    log_err "Neo4j não ficou healthy — continuando mesmo assim"
}

start_pncp_background() {
    [[ "$MODO_TESTE" == "Y" ]] && { log_info "MODO_TESTE: pulando PNCP"; return 0; }
    log_banner "📥  PNCP — background (download leva dias)"
    (
        while true; do
            cd "$ETL_DIR"
            uv run python scripts/download_pncp.py --output-dir "../data/pncp"
            echo "[PNCP] reiniciando em 30s..."; sleep 30
        done >> "$LOG" 2>&1
    ) &
    log_ok "PNCP em background (PID $!)"
}

run_download() {
    local fonte="$1"
    local force="${2:-0}"
    local script="$ETL_DIR/scripts/download_${fonte}.py"
    [[ ! -f "$script" ]] && { log_skip "sem script de download — indo para importação"; return 0; }
    if [[ "$force" -eq 0 ]]; then
        if [[ "$fonte" == "transparencia_am" ]]; then
            local csv_count
            csv_count=$(find "$DATA_DIR/$fonte" -name "*.csv" 2>/dev/null | wc -l)
            [[ "$csv_count" -gt 0 ]] && { log_skip "data/$fonte já existe ($csv_count CSVs) — pulando download"; return 0; }
        fi
        if [[ -d "$DATA_DIR/$fonte" ]] && [[ -n "$(ls -A "$DATA_DIR/$fonte" 2>/dev/null)" ]]; then
            log_skip "data/$fonte já existe — pulando download"; return 0
        fi
    fi
    log_info "Baixando $fonte..."
    cd "$ETL_DIR"
    uv run python "scripts/download_${fonte}.py" --output-dir "../data/${fonte}" 2>&1 | filter_output | tee -a "$LOG" &
    CURRENT_PID=$!; wait $CURRENT_PID; local exit_code=$?; CURRENT_PID=""
    local file_count=0
    file_count=$(ls -A "$DATA_DIR/$fonte" 2>/dev/null | wc -l)
    if [[ $exit_code -eq 0 ]] && [[ "$file_count" -gt 0 ]]; then
        log_ok "Download concluído: $fonte ($file_count arquivo(s))"
    elif [[ $exit_code -eq 0 ]] && [[ "$file_count" -eq 0 ]]; then
        log_err "Download OK mas nenhum arquivo gerado: $fonte"; beep_error; return 1
    else
        log_err "Download falhou: $fonte (código $exit_code)"; beep_error; return 1
    fi
}

run_import() {
    local fonte="$1"
    local WATCHDOG_TIMEOUT=180
    log_info "Importando $fonte..."
    cd "$ETL_DIR"
    local PROGRESS_FILE="$ROOT/bracc_progress_${fonte}.tmp"
    rm -f "$PROGRESS_FILE"
    uv run bracc-etl run --source "$fonte" --neo4j-password "$NEO4J_PASSWORD" --data-dir "$DATA_DIR" >> "$PROGRESS_FILE" 2>&1 &
    CURRENT_PID=$!
    local last_shown="" last_log_size=0 last_change warned=0
    last_change=$(date +%s)
    while kill -0 $CURRENT_PID 2>/dev/null; do
        if [[ -f "$PROGRESS_FILE" ]]; then
            local last_line
            last_line=$(grep "Processando" "$PROGRESS_FILE" 2>/dev/null | tail -1)
            if [[ -n "$last_line" && "$last_line" != "$last_shown" ]]; then
                local cur_num total_files cur_file pct filled empty bar=""
                cur_num=$(echo "$last_line" | grep -oE "[0-9]+/[0-9]+" | grep -oE "^[0-9]+")
                total_files=$(echo "$last_line" | grep -oE "[0-9]+/[0-9]+" | grep -oE "[0-9]+$")
                cur_file=$(echo "$last_line" | grep -oE "[^ ]+\.csv" | tail -1)
                if [[ -n "$total_files" && "$total_files" -gt 0 ]]; then
                    pct=$(( cur_num * 100 / total_files ))
                    filled=$(( cur_num * 20 / total_files ))
                    empty=$(( 20 - filled ))
                    for ((b=0; b<filled; b++)); do bar+="█"; done
                    for ((b=0; b<empty; b++)); do bar+="░"; done
                    echo "  [$bar] $cur_num/$total_files ($pct%) $cur_file"
                fi
                last_shown="$last_line"
            fi
        fi
        local cur_size now elapsed
        cur_size=$(wc -c < "$PROGRESS_FILE" 2>/dev/null || echo 0)
        now=$(date +%s)
        if [[ "$cur_size" -gt "$last_log_size" ]]; then
            last_log_size=$cur_size; last_change=$now; warned=0
        else
            elapsed=$(( now - last_change ))
            if [[ $elapsed -ge $WATCHDOG_TIMEOUT && $warned -eq 0 ]]; then
                echo "  ⚠️  [$fonte] sem atividade ha $(( elapsed / 60 ))min — pode ter travado"
                warned=1
            fi
        fi
        sleep 1
    done
    wait $CURRENT_PID; local exit_code=$?; CURRENT_PID=""
    cat "$PROGRESS_FILE" >> "$LOG" 2>/dev/null
    rm -f "$PROGRESS_FILE"
    if [[ $exit_code -eq 0 ]]; then
        mark_imported "$fonte"; log_ok "Importação concluída: $fonte"; beep
    else
        log_err "Importação falhou: $fonte (código $exit_code)"; beep_error; return 1
    fi
}

# ── PROCESSAR FILA ────────────────────────────────────────────────────────────
run_queue() {
    local queue_name="$1"; shift
    local queue=("$@")
    local total=${#queue[@]} count=0 skipped=0 errors=0

    log_banner "▶️   FILA: $queue_name (${total} fontes)"

    for fonte in "${queue[@]}"; do
        count=$((count + 1))
        CURRENT_FONTE="$fonte"
        log_section "[$count/$total] $fonte"

        if is_skipped "$fonte"; then
            log_skip "na lista SKIP — ignorada"; skipped=$((skipped + 1)); continue
        fi

        local force_this=0
        for ff in "${FORCE_FONTES[@]}"; do [[ "$ff" == "$fonte" ]] && force_this=1; done
        if [[ $FORCE_REIMPORT -eq 0 ]] || [[ $FORCE_REIMPORT -eq 1 && $force_this -eq 0 ]]; then
            if is_imported "$fonte"; then
                local data_mtime installed_ts local_date
                data_mtime=$(find "$DATA_DIR/$fonte" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1 | cut -d. -f1)
                installed_ts=$(date -d "$(grep "^imported: $fonte " "$INSTALLED_FLAG" | tail -1 | awk '{print $3, $4}')" +%s 2>/dev/null || echo "0")
                if [[ -n "$data_mtime" && "$data_mtime" -gt "${installed_ts:-0}" ]]; then
                    local_date=$(grep "^imported: $fonte " "$INSTALLED_FLAG" | tail -1 | awk '{print $3, $4}')
                    log_info "🔄 dados atualizados desde $local_date — reimportando"
                else
                    local_date=$(grep "^imported: $fonte " "$INSTALLED_FLAG" | tail -1 | awk '{print $3, $4}')
                    log_skip "já importado em $local_date — sem alteração"
                    skipped=$((skipped + 1)); continue
                fi
            fi
        fi

        run_download "$fonte" "$force_this" || { errors=$((errors + 1)); continue; }
        run_import "$fonte"   || { errors=$((errors + 1)); continue; }
        log_ok "[$count/$total] $fonte concluído"
    done

    CURRENT_FONTE=""
    log_info "Fila $queue_name: $total fontes | Puladas: $skipped | Erros: $errors"
    log_blank
    SKIPPED=$((SKIPPED + skipped))
    ERRORS=$((ERRORS + errors))
}

# ── MAIN ─────────────────────────────────────────────────────────────────────
FORCE_FONTES=()
CUSTOM_QUEUE=()
i=1
while [[ $i -le $# ]]; do
    arg="${!i}"
    if [[ "$arg" == "--force" ]]; then
        FORCE_REIMPORT=1; i=$((i + 1))
        while [[ $i -le $# ]]; do
            next="${!i}"
            [[ "$next" == --* ]] && break
            FORCE_FONTES+=("$next"); i=$((i + 1))
        done
    elif [[ "$arg" == "--amazonas" ]]; then
        MODO_AMAZONAS=1; i=$((i + 1))
    else
        CUSTOM_QUEUE+=("$arg"); i=$((i + 1))
    fi
done

clear
log_banner "🚀  BRACC-ETL ORQUESTRADOR  —  $(date '+%d/%m/%Y %H:%M')"
echo ""
echo "  Este programa baixa e importa todas as fontes de dados."
echo "  Fontes já importadas são puladas automaticamente."
echo ""
echo "  ┌────────────────────────────────────────────────────────────┐"
echo "  │  Ctrl+C encerra com segurança a qualquer momento           │"
echo "  │  Para retomar: bash orchestrator.sh <fonte>                │"
echo "  ├────────────────────────────────────────────────────────────┤"
echo "  │  --amazonas            roda só fontes do Amazonas          │"
echo "  │  --force <fonte>       força reimportação específica       │"
echo "  │  MODO_TESTE=Y          pula Neo4j sync, uv sync e PNCP     │"
echo "  └────────────────────────────────────────────────────────────┘"
echo ""
[[ $FORCE_REIMPORT -eq 1 ]] && echo "  ⚠️  Modo --force: ${FORCE_FONTES[*]:-todas}" && echo ""
[[ $MODO_AMAZONAS -eq 1 ]] && echo "  🌿  Modo --amazonas: só fila Amazonas" && echo ""
read -rp "  Pressione ENTER para iniciar..." _
echo "" | tee -a "$LOG"

if [[ ! -f "$INSTALLED_FLAG" ]]; then
    run_setup
else
    log_info "✅ Setup já feito ($(grep 'installed:' "$INSTALLED_FLAG" | cut -d' ' -f2)) — pulando"
    log_blank
fi

start_docker
[[ "$MODO_TESTE" == "Y" ]] || sync_neo4j_to_installed
start_pncp_background

if [[ ${#CUSTOM_QUEUE[@]} -gt 0 ]]; then
    run_queue "Customizada" "${CUSTOM_QUEUE[@]}"
elif [[ $MODO_AMAZONAS -eq 1 ]]; then
    run_queue "🌿 Amazonas" "${AMAZONAS_QUEUE[@]}"
elif [[ $FORCE_REIMPORT -eq 1 && ${#FORCE_FONTES[@]} -gt 0 ]]; then
    run_queue "--force" "${FORCE_FONTES[@]}"
else
    run_queue "Nacional" "${DEFAULT_QUEUE[@]}"
    run_queue "🌿 Amazonas" "${AMAZONAS_QUEUE[@]}"
fi

run_validation

log_banner "✅  CONCLUÍDO  —  $(date '+%d/%m/%Y %H:%M')"
log_info "Total puladas: $SKIPPED  |  Total erros: $ERRORS"
log_blank
beep; beep
