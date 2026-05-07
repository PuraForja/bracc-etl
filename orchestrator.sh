#!/usr/bin/env bash
# orchestrator.sh — Setup + Download + Importação sequencial
# Uso: bash orchestrator.sh [fonte1 fonte2 ...]
# Sem argumentos: usa a fila padrão abaixo
# Logs: pipeline_imports.log
#
# ── COMO PULAR UMA FONTE ──────────────────────────────────────────────────────
# Adicione o nome na lista SKIP abaixo.
# A fonte será completamente ignorada (nem download nem importação).
# Para reativar, remova da lista.
# ─────────────────────────────────────────────────────────────────────────────
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ETL_DIR="$ROOT/etl"
DATA_DIR="$ROOT/data"
LOG="$ROOT/pipeline_imports.log"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-changeme}"
INSTALLED_FLAG="$ROOT/.installed"

# ── FONTES A IGNORAR ──────────────────────────────────────────────────────────
SKIP=(
    pncp            # roda em background separado — nunca na fila
    senado          # dando problema — aguardar fix
    camara          # importação travando — aguardar fix do colega
    # cnpj          # exemplo: descomente para pular
)

# ── FILA COMPLETA — menores primeiro, pesadas por último ─────────────────────
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
    camara
    transparencia
    tse
    viagens
    cnpj
)

# ─────────────────────────────────────────────────────────────────────────────
CURRENT_FONTE=""
CURRENT_PID=""

graceful_shutdown() {
    echo "" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
    echo "  ┌─────────────────────────────────────────────┐" | tee -a "$LOG"
    echo "  │  ⚠️   INTERRUPÇÃO DETECTADA (Ctrl+C)         │" | tee -a "$LOG"
    echo "  │  Encerrando com segurança...                 │" | tee -a "$LOG"
    echo "  └─────────────────────────────────────────────┘" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
    if [[ -n "$CURRENT_PID" ]] && kill -0 "$CURRENT_PID" 2>/dev/null; then
        echo "  │  Aguardando processo atual terminar (PID $CURRENT_PID)..." | tee -a "$LOG"
        kill -TERM "$CURRENT_PID" 2>/dev/null
        local waited=0
        while kill -0 "$CURRENT_PID" 2>/dev/null && [[ $waited -lt 30 ]]; do
            sleep 1
            waited=$((waited + 1))
            echo -n "." >&2
        done
        echo "" | tee -a "$LOG"
        if kill -0 "$CURRENT_PID" 2>/dev/null; then
            echo "  │  Processo demorou — forçando encerramento..." | tee -a "$LOG"
            kill -9 "$CURRENT_PID" 2>/dev/null
        else
            echo "  │  ✅ Processo encerrado com segurança" | tee -a "$LOG"
        fi
    fi
    echo "" | tee -a "$LOG"
    if [[ -n "$CURRENT_FONTE" ]]; then
        echo "  │  Parou em: $CURRENT_FONTE" | tee -a "$LOG"
        echo "  │  Para retomar: bash orchestrator.sh $CURRENT_FONTE" | tee -a "$LOG"
    fi
    echo "" | tee -a "$LOG"
    echo "  ──────────────────────────────────────────────" | tee -a "$LOG"
    echo "  ⛔  ORQUESTRADOR ENCERRADO  —  $(date '+%d/%m/%Y %H:%M')" | tee -a "$LOG"
    echo "  ──────────────────────────────────────────────" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
    echo "  💡  PNCP continua rodando em background" | tee -a "$LOG"
    echo "  💡  Para retomar: bash orchestrator.sh $CURRENT_FONTE" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
    exit 0
}
trap graceful_shutdown INT TERM

# ─────────────────────────────────────────────────────────────────────────────
log() {
    echo "$(date '+%d/%m/%Y %H:%M:%S')  $*" | tee -a "$LOG"
}
log_blank() { echo "" | tee -a "$LOG"; }
log_banner() {
    echo "" | tee -a "$LOG"
    echo "  ──────────────────────────────────────────────" | tee -a "$LOG"
    echo "  $1" | tee -a "$LOG"
    echo "  ──────────────────────────────────────────────" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
}
log_section() {
    echo "" | tee -a "$LOG"
    echo "  ┌─ $*" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
}
log_ok()   { echo "  └─ ✅  $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_err()  { echo "  └─ ❌  $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_skip() { echo "  └─ ⏭   $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_info() { echo "  │  $*" | tee -a "$LOG"; }
beep()       { powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)" 2>/dev/null || true; }
beep_error() { powershell.exe -Command "[console]::beep(400,500); [console]::beep(400,500)" 2>/dev/null || true; }

# Filtra traceback Python — mostra só linhas relevantes
filter_output() {
    grep -v "^  File \|^    \|^Traceback (most recent\|site-packages\|__main__\|sys\.exit\|\.invoke\|\.main\|\.callback\|frozen\|_run_module\|_run_code\|_process_result"
}

is_skipped() {
    local fonte="$1"
    for s in "${SKIP[@]}"; do [[ "$s" == "$fonte" ]] && return 0; done
    return 1
}

# ── SETUP — só roda se .installed não existir ─────────────────────────────────
run_setup() {
    log_banner "🔧  SETUP INICIAL — verificando dependências"
    local errors=0

    log_info "Verificando Docker..."
    if ! command -v docker &>/dev/null; then
        log_err "Docker não encontrado. Instale: https://www.docker.com/products/docker-desktop"
        errors=$((errors + 1))
    else
        log_ok "Docker OK ($(docker --version | cut -d' ' -f3 | tr -d ','))"
    fi

    log_info "Verificando uv..."
    if ! command -v uv &>/dev/null && ! ~/.local/bin/uv --version &>/dev/null 2>&1; then
        log_err "uv não encontrado. Instale: curl -LsSf https://astral.sh/uv/install.sh | sh"
        errors=$((errors + 1))
    else
        log_ok "uv OK"
    fi

    log_info "Verificando Git..."
    if ! command -v git &>/dev/null; then
        log_err "Git não encontrado. Instale: https://git-scm.com/downloads"
        errors=$((errors + 1))
    else
        log_ok "Git OK ($(git --version | cut -d' ' -f3))"
    fi

    if [[ $errors -gt 0 ]]; then
        log_err "$errors dependência(s) faltando — instale e execute novamente"
        exit 1
    fi

    log_info "Instalando dependências Python (uv sync)..."
    cd "$ETL_DIR"
    if uv sync 2>&1 | filter_output | tee -a "$LOG"; then
        log_ok "Dependências Python instaladas"
    else
        log_err "Falha ao instalar dependências Python"
        exit 1
    fi

    echo "installed: $(date '+%Y-%m-%d %H:%M:%S')" > "$INSTALLED_FLAG"
    echo "docker: $(docker --version)" >> "$INSTALLED_FLAG"
    echo "uv: $(uv --version 2>/dev/null || echo 'ok')" >> "$INSTALLED_FLAG"
    echo "git: $(git --version)" >> "$INSTALLED_FLAG"

    log_ok "Setup concluído — arquivo .installed criado"
    log_info "Próximas execuções pulam este passo automaticamente"
    log_blank
}

# ── DOCKER ────────────────────────────────────────────────────────────────────
start_docker() {
    log_banner "🐳  DOCKER — subindo containers"
    cd "$ROOT"
    docker compose up -d 2>&1 | filter_output | tee -a "$LOG"
    log_blank
    log_info "Aguardando Neo4j ficar healthy..."
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        local status
        status=$(docker inspect --format='{{.State.Health.Status}}' bracc-neo4j 2>/dev/null || echo "starting")
        if [[ "$status" == "healthy" ]]; then
            log_ok "Neo4j healthy"
            return 0
        fi
        attempts=$((attempts + 1))
        log_info "Neo4j: $status — aguardando... ($attempts/30)"
        sleep 10
    done
    log_err "Neo4j não ficou healthy — continuando mesmo assim"
}

# ── PNCP ──────────────────────────────────────────────────────────────────────
start_pncp_background() {
    log_banner "📥  PNCP — download em background"
    (
        while true; do
            cd "$ETL_DIR"
            uv run python scripts/download_pncp.py --output-dir "../data/pncp"
            echo "[PNCP] caiu ou terminou — reiniciando em 30s..."
            sleep 30
        done >> "$LOG" 2>&1
    ) &
    log_ok "PNCP rodando em background (PID $!)"
}

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
run_download() {
    local fonte="$1"
    local script="$ETL_DIR/scripts/download_${fonte}.py"

    if [[ ! -f "$script" ]]; then
        log_skip "sem script de download — indo para importação"
        return 0
    fi

    if [[ -d "$DATA_DIR/$fonte" ]] && [[ -n "$(ls -A "$DATA_DIR/$fonte" 2>/dev/null)" ]]; then
        log_skip "data/$fonte já existe — pulando download"
        return 0
    fi

    log_info "Baixando $fonte..."
    cd "$ETL_DIR"
    uv run python "scripts/download_${fonte}.py" \
        --output-dir "../data/${fonte}" \
        2>&1 | filter_output | tee -a "$LOG" &
    CURRENT_PID=$!
    wait $CURRENT_PID
    local exit_code=$?
    CURRENT_PID=""

    if [[ $exit_code -eq 0 ]]; then
        log_ok "Download concluído: $fonte"
    else
        log_err "Download falhou: $fonte (código $exit_code) — pulando importação"
        beep_error
        return 1
    fi
}

# ── IMPORTAÇÃO ────────────────────────────────────────────────────────────────
run_import() {
    local fonte="$1"
    log_info "Importando $fonte para o Neo4j..."
    cd "$ETL_DIR"
    uv run bracc-etl run \
        --source "$fonte" \
        --neo4j-password "$NEO4J_PASSWORD" \
        --data-dir "$DATA_DIR" \
        2>&1 | filter_output | tee -a "$LOG" &
    CURRENT_PID=$!
    wait $CURRENT_PID
    local exit_code=$?
    CURRENT_PID=""

    if [[ $exit_code -eq 0 ]]; then
        log_ok "Importação concluída: $fonte"
        beep
    else
        log_err "Importação falhou: $fonte (código $exit_code)"
        beep_error
        return 1
    fi
}

# ── MAIN ─────────────────────────────────────────────────────────────────────
log_banner "🚀  BRACC-ETL ORQUESTRADOR  —  $(date '+%d/%m/%Y %H:%M')"
log_blank
log_info "  Pressione Ctrl+C a qualquer momento para encerrar com segurança."
log_info "  O processo atual será aguardado antes de encerrar."
log_info "  Ao encerrar, será informado onde parou e como retomar."
log_blank
log_info "Iniciando em 5 segundos..."
sleep 5
log_blank

# Setup — só na primeira vez
if [[ ! -f "$INSTALLED_FLAG" ]]; then
    run_setup
else
    log_info "✅ Dependências já instaladas ($(grep 'installed:' "$INSTALLED_FLAG" | cut -d' ' -f2)) — pulando setup"
    log_blank
fi

start_docker
start_pncp_background

if [[ $# -gt 0 ]]; then
    QUEUE=("$@")
    log_info "Fila customizada: ${QUEUE[*]}"
else
    QUEUE=("${DEFAULT_QUEUE[@]}")
    log_info "Fila padrão: ${#QUEUE[@]} fontes"
fi

log_blank

TOTAL=${#QUEUE[@]}
COUNT=0
SKIPPED=0
ERRORS=0

for fonte in "${QUEUE[@]}"; do
    COUNT=$((COUNT + 1))
    CURRENT_FONTE="$fonte"

    if is_skipped "$fonte"; then
        log_section "[$COUNT/$TOTAL] $fonte"
        log_skip "na lista SKIP — ignorada"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    log_section "[$COUNT/$TOTAL] $fonte"
    run_download "$fonte" || { ERRORS=$((ERRORS + 1)); continue; }
    run_import "$fonte"   || { ERRORS=$((ERRORS + 1)); continue; }
    log_ok "[$COUNT/$TOTAL] $fonte concluído"
done

CURRENT_FONTE=""

log_banner "✅  ORQUESTRADOR CONCLUÍDO  —  $(date '+%d/%m/%Y %H:%M')"
log_info "Total: $TOTAL  |  Puladas: $SKIPPED  |  Erros: $ERRORS"
log_blank
beep
beep
