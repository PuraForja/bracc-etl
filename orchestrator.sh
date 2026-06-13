#!/usr/bin/env bash
# orchestrator.sh — BRACC ETL CLI
#
# Uso: bash orchestrator.sh <comando> [opções]
#
# Comandos:
#   help                    lista todos os comandos disponíveis
#   list                    status das fontes (importado/pendente/data)
#   install                 setup completo do zero
#   update                  atualiza todas as fontes
#   update --am             atualiza só fila Amazonas
#   update <fonte...>       atualiza fontes específicas
#   update --force <fonte>  força reimportação mesmo já importado
#   validate                conta nodes no Neo4j por label
#   check                   testa links de todas as fontes
#   check --save            idem + salva relatório em arquivo
#
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
LABEL_MAP[obras]="Obra"
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
LABEL_MAP[servidores_federais]="GovEmployee"
LABEL_MAP[pncp]="Bid"
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

# Timeouts por fonte (segundos) — padrão 180s
declare -A TIMEOUT_MAP
TIMEOUT_MAP[tse]=1800
TIMEOUT_MAP[cnpj]=1800
TIMEOUT_MAP[camara]=1800
TIMEOUT_MAP[tse_bens]=1800
TIMEOUT_MAP[tse_filiados]=1800
TIMEOUT_MAP[transparencia_am]=1800
TIMEOUT_MAP[tce_am]=900
TIMEOUT_MAP[servidores_federais]=600
TIMEOUT_MAP[transparencia]=600
TIMEOUT_MAP[siconfi]=900
TIMEOUT_MAP[datasus]=600
TIMEOUT_MAP[camara_inquiries]=600
TIMEOUT_MAP[transferegov]=600
TIMEOUT_MAP[obras]=600
TIMEOUT_MAP[senado]=600
TIMEOUT_MAP[tcu]=600
TIMEOUT_MAP[ibama]=600
TIMEOUT_MAP[senado_cpis]=300
TIMEOUT_MAP[bcb]=300
TIMEOUT_MAP[cvm]=300
TIMEOUT_MAP[cvm_funds]=300

# ── MAPA fonte → URL para check de links ─────────────────────────────────────
declare -A URL_MAP
URL_MAP[tse]="https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato/votacao_candidato_2024.zip"
URL_MAP[tse_bens]="https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato/bem_candidato_2024.zip"
URL_MAP[tse_filiados]="https://cdn.tse.jus.br/estatistica/sead/odsele/filiados/filiados_AC.zip"
URL_MAP[cnpj]="https://dadosabertos.rfb.gov.br/CNPJ/Empresas0.zip"
URL_MAP[transparencia]="https://portaldatransparencia.gov.br/download-de-dados/contratos"
URL_MAP[pncp]="https://pncp.gov.br/api/pncp/v1/contratos"
URL_MAP[camara]="https://www.camara.leg.br/cotas/Verba-indenizatoria-2024.csv.zip"
URL_MAP[senado]="https://www6.senado.gov.br/scon/downloads/legislacao.zip"
URL_MAP[siconfi]="https://siconfi.tesouro.gov.br/siconfi/pages/public/declaracao/declaracao_list.jsf"
URL_MAP[ceaf]="https://www.portaltransparencia.gov.br/download-de-dados/expulsoes-quadros"
URL_MAP[cepim]="https://www.portaltransparencia.gov.br/download-de-dados/cepim"
URL_MAP[icij]="https://offshoreleaks-data.icij.org/offshoreleaks/csv/full-oldb-20240930.zip"
URL_MAP[opensanctions]="https://data.opensanctions.org/datasets/latest/peps/targets.simple.csv"
URL_MAP[ofac]="https://www.treasury.gov/ofac/downloads/sdn.csv"
URL_MAP[un_sanctions]="https://scsanctions.un.org/resources/xml/en/consolidated.xml"
URL_MAP[eu_sanctions]="https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList/content"
URL_MAP[world_bank]="https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_PDF/FIRM/INDVIDUAL"
URL_MAP[cvm]="https://www.gov.br/cvm/pt-br/assuntos/noticias/2024"
URL_MAP[bcb]="https://www.bcb.gov.br/acessoinformacao/legado?url=https://www.bcb.gov.br/fis/info/penalidades.asp"
URL_MAP[servidores_federais]="https://portaldatransparencia.gov.br/download-de-dados/servidores"
URL_MAP[tce_am]="https://econtasapi.tce.am.gov.br/transparencia/dados-abertos/unidades"
URL_MAP[ibama]="https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php"
URL_MAP[leniency]="https://www.portaltransparencia.gov.br/download-de-dados/acordos-leniencia"
URL_MAP[cpgf]="https://www.portaltransparencia.gov.br/download-de-dados/cartoes"
URL_MAP[viagens]="https://www.portaltransparencia.gov.br/download-de-dados/viagens"
URL_MAP[renuncias]="https://www.portaltransparencia.gov.br/download-de-dados/renuncias"
URL_MAP[siop]="https://www.portaltransparencia.gov.br/download-de-dados/emendas"
URL_MAP[tesouro_emendas]="https://www.tesourotransparente.gov.br/ckan/dataset/emendas-parlamentares"
URL_MAP[transferegov]="https://www.portaltransparencia.gov.br/download-de-dados/transferencias"
URL_MAP[holdings]="https://dadosabertos.rfb.gov.br/CNPJ/Socios0.zip"
URL_MAP[datasus]="https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp"
URL_MAP[querido_diario]="https://queridodiario.ok.org.br/api/gazettes"
URL_MAP[sanctions]="https://www.portaltransparencia.gov.br/download-de-dados/responsabilizados-administrativamente"
URL_MAP[tcu]="https://portal.tcu.gov.br/orcamento-financas-e-gestao/tecnologia-da-informacao/"
URL_MAP[pgfn]="https://www.portaltransparencia.gov.br/download-de-dados/cnep"
URL_MAP[camara_inquiries]="https://dadosabertos.camara.leg.br/api/v2/proposicoes?siglaTipo=RIC"
URL_MAP[senado_cpis]="https://legis.senado.leg.br/dadosabertos/comissao/lista/cpi"
URL_MAP[cvm_funds]="https://dados.cvm.gov.br/dados/FI/CAD/DADOS/"
URL_MAP[inep]="https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos"
URL_MAP[transparencia_am]="https://www.transparencia.am.gov.br/pessoal/"
URL_MAP[ibama_am]="https://servicos.ibama.gov.br/ctf/publico/areasembargadas/ConsultaPublicaAreasEmbargadas.php"

# ── AMAZONAS ──────────────────────────────────────────────────────────────────
LABEL_MAP[transparencia_am]="Person"
LABEL_MAP[ibama_am]="Sanction"
LABEL_MAP[inpe_prodes]="Deforestation"
LABEL_MAP[sicar]="RuralProperty"
LABEL_MAP[antaq]="Contract"

# ── FONTES A IGNORAR ─────────────────────────────────────────────────────────
SKIP=(
    # pncp  # download concluído — importar via fila normal
)

# ── FILAS ─────────────────────────────────────────────────────────────────────
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
    pncp
    comprasnet
    obras
)

AMAZONAS_QUEUE=(
    transparencia_am
    tce_am
    servidores_federais  # filtrado por UF=AM — só servidores lotados no Amazonas
    # ibama_am     # a implementar — embargos ambientais AM
    # inpe_prodes  # a implementar — desmatamento
    # sicar        # a implementar — Cadastro Ambiental Rural
    # antaq        # a implementar — hidrovias AM
)

# ─────────────────────────────────────────────────────────────────────────────
CURRENT_FONTE=""
CURRENT_PID=""
FORCE_REIMPORT=0
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
        echo "  │  Para retomar: bash orchestrator.sh update $CURRENT_FONTE" | tee -a "$LOG"
        echo "  │  Para forçar:  bash orchestrator.sh update --force $CURRENT_FONTE" | tee -a "$LOG"
    fi
    echo "  ⛔  ENCERRADO — $(date '+%d/%m/%Y %H:%M')" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
    exit 0
}
trap graceful_shutdown INT TERM

# ── HELPERS DE LOG ────────────────────────────────────────────────────────────
log_blank()   { echo "" | tee -a "$LOG"; }
log_banner()  {
    echo "" | tee -a "$LOG"
    echo "  ══════════════════════════════════════════════" | tee -a "$LOG"
    echo "  $1" | tee -a "$LOG"
    echo "  ══════════════════════════════════════════════" | tee -a "$LOG"
    echo "" | tee -a "$LOG"
}
log_section() { echo "" | tee -a "$LOG"; echo "  ┌─ $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_ok()      { echo "  └─ ✅  $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_err()     { echo "  └─ ❌  $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_skip()    { echo "  └─ ⏭   $*" | tee -a "$LOG"; echo "" | tee -a "$LOG"; }
log_info()    { echo "  │  $*" | tee -a "$LOG"; }

beep() {
    powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)" 2>/dev/null \
    || (echo -e "\a"; sleep 0.3; echo -e "\a") 2>/dev/null \
    || true
}
beep_error() {
    powershell.exe -Command "[console]::beep(400,500); [console]::beep(400,500)" 2>/dev/null \
    || (echo -e "\a"; sleep 0.2; echo -e "\a"; sleep 0.2; echo -e "\a") 2>/dev/null \
    || true
}

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
    docker compose exec neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
        "MATCH (n:$label) RETURN count(n) as total" 2>/dev/null \
        | grep -E '^[0-9]+$' | head -1
}

# ── SUBCOMANDO: help ──────────────────────────────────────────────────────────
cmd_help() {
    echo ""
    echo "  ══════════════════════════════════════════════════════════════"
    echo "  🧠  BRACC-ETL — CLI de Inteligência Política"
    echo "  ══════════════════════════════════════════════════════════════"
    echo ""
    echo "  Uso: bash orchestrator.sh <comando> [opções]"
    echo ""
    echo "  COMANDOS:"
    echo ""
    echo "    help                       esta mensagem"
    echo "    list                       status de todas as fontes"
    echo "    install                    setup completo do zero"
    echo "    validate                   conta nodes no Neo4j por label"
    echo "    check                      testa links de todas as fontes"
    echo "    check --save               idem + salva relatório em arquivo"
    echo ""
    echo "    update                     atualiza todas as filas"
    echo "    update --am                atualiza só fila Amazonas"
    echo "    update <fonte...>          atualiza fontes específicas"
    echo "    update --force <fonte...>  força reimportação"
    echo ""
    echo "  EXEMPLOS:"
    echo ""
    echo "    bash orchestrator.sh install"
    echo "    bash orchestrator.sh update"
    echo "    bash orchestrator.sh update tse cnpj"
    echo "    bash orchestrator.sh update --am"
    echo "    bash orchestrator.sh update --force tse
    bash orchestrator.sh update servidores_federais"
    echo "    bash orchestrator.sh check --save"
    echo "    bash orchestrator.sh list"
    echo "    bash orchestrator.sh validate"
    echo ""
    echo "  VARIÁVEIS DE AMBIENTE:"
    echo ""
    echo "    NEO4J_PASSWORD=<senha>     padrão: changeme"
    echo "    MODO_TESTE=Y               pula Neo4j sync, uv sync e PNCP"
    echo ""
    echo "  ══════════════════════════════════════════════════════════════"
    echo ""
}

# ── SUBCOMANDO: list ──────────────────────────────────────────────────────────
cmd_list() {
    echo ""
    echo "  ══════════════════════════════════════════════════════════════"
    echo "  📋  STATUS DAS FONTES — $(date '+%d/%m/%Y %H:%M')"
    echo "  ══════════════════════════════════════════════════════════════"
    echo ""
    printf "  %-25s  %-8s  %s\n" "FONTE" "TIMEOUT" "STATUS"
    echo "  ──────────────────────────────────────────────────────────────"

    echo "  🇧🇷  FEDERAL"
    for fonte in "${DEFAULT_QUEUE[@]}"; do
        local status timeout_val
        timeout_val="${TIMEOUT_MAP[$fonte]:-180}s"
        if is_skipped "$fonte"; then
            status="⏭  SKIP"
        elif is_imported "$fonte"; then
            local data
            data=$(grep "^imported: $fonte " "$INSTALLED_FLAG" 2>/dev/null | tail -1 | awk '{print $3, $4}')
            status="✅ $data"
        else
            status="⏳ pendente"
        fi
        printf "    %-23s  %-8s  %s\n" "$fonte" "$timeout_val" "$status"
    done

    echo ""
    echo "  🌿  AMAZONAS"
    for fonte in "${AMAZONAS_QUEUE[@]}"; do
        local status timeout_val
        timeout_val="${TIMEOUT_MAP[$fonte]:-180}s"
        if is_skipped "$fonte"; then
            status="⏭  SKIP"
        elif is_imported "$fonte"; then
            local data
            data=$(grep "^imported: $fonte " "$INSTALLED_FLAG" 2>/dev/null | tail -1 | awk '{print $3, $4}')
            status="✅ $data"
        else
            status="⏳ pendente"
        fi
        printf "    %-23s  %-8s  %s\n" "$fonte" "$timeout_val" "$status"
    done

    echo ""
    echo "  ══════════════════════════════════════════════════════════════"
    echo ""
}

# ── SUBCOMANDO: check ─────────────────────────────────────────────────────────
cmd_check() {
    local save_flag="$1"
    local ok=0 redirect=0 error=0 sem_url=0
    local report_file=""
    [[ "$save_flag" == "--save" ]] && report_file="$ROOT/link_check_$(date '+%Y%m%d_%H%M').txt"

    _out() { echo "$*"; [[ -n "$report_file" ]] && echo "$*" >> "$report_file"; }

    _check_fonte() {
        local fonte="$1"
        local url="${URL_MAP[$fonte]:-}"
        if [[ -z "$url" ]]; then
            printf "    %-25s  ⚪ sem URL cadastrada\n" "$fonte"
            [[ -n "$report_file" ]] && printf "    %-25s  ⚪ sem URL cadastrada\n" "$fonte" >> "$report_file"
            sem_url=$((sem_url + 1))
            return
        fi
        local http_code
        http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 --head "$url" 2>/dev/null)
        local status_icon
        if [[ "$http_code" =~ ^2 ]]; then
            status_icon="✅ $http_code"
            ok=$((ok + 1))
        elif [[ "$http_code" =~ ^3 ]]; then
            status_icon="🔀 $http_code redirect"
            redirect=$((redirect + 1))
        elif [[ "$http_code" == "000" ]]; then
            status_icon="❌ timeout/erro de rede"
            error=$((error + 1))
        else
            status_icon="❌ $http_code"
            error=$((error + 1))
        fi
        printf "    %-25s  %s\n" "$fonte" "$status_icon"
        [[ -n "$report_file" ]] && printf "    %-25s  %s\n" "$fonte" "$status_icon" >> "$report_file"
    }

    _out ""
    _out "  ══════════════════════════════════════════════════════════════"
    _out "  🔗  CHECK DE LINKS — $(date '+%d/%m/%Y %H:%M')"
    _out "  ══════════════════════════════════════════════════════════════"
    _out ""
    _out "  🇧🇷  FEDERAL"
    for fonte in "${DEFAULT_QUEUE[@]}"; do _check_fonte "$fonte"; done
    _out ""
    _out "  🌿  AMAZONAS"
    for fonte in "${AMAZONAS_QUEUE[@]}"; do _check_fonte "$fonte"; done
    _out ""
    _out "  ══════════════════════════════════════════════════════════════"
    _out "  RESUMO: ✅ $ok OK  |  🔀 $redirect redirect  |  ❌ $error erro  |  ⚪ $sem_url sem URL"
    _out "  ══════════════════════════════════════════════════════════════"
    _out ""

    if [[ -n "$report_file" ]]; then
        echo "  💾  Relatório salvo em: $report_file"
        echo ""
    fi
}

# ── SUBCOMANDO: validate ──────────────────────────────────────────────────────
cmd_validate() {
    log_banner "🔍  VALIDAÇÃO — Neo4j"
    local raw
    raw=$(docker compose exec neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
        "MATCH (n) RETURN labels(n)[0] as label, count(n) as total ORDER BY total DESC" \
        2>/dev/null | grep -v "^label\|^$\|rows\|ms")
    [[ -z "$raw" ]] && { log_err "Não foi possível conectar ao Neo4j"; return; }
    local ok=0 total_nodes=0
    while IFS= read -r line; do
        local label count
        label=$(echo "$line" | awk -F'"' '{print $2}')
        count=$(echo "$line" | awk -F',' '{print $2}' | tr -d ' ')
        [[ -z "$label" || -z "$count" ]] && continue
        log_info "✅  $label: $count nodes"
        ok=$((ok + 1)); total_nodes=$((total_nodes + count))
    done <<< "$raw"
    log_blank
    log_info "Total: $ok labels | ~$total_nodes nodes no banco"
    log_blank
}

# ── SUBCOMANDO: install ───────────────────────────────────────────────────────
cmd_install() {
    log_banner "🔧  INSTALL — Setup Completo"
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

    log_info "Subindo Docker..."
    cd "$ROOT" && docker compose up -d 2>&1 | filter_output | tee -a "$LOG"
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        local status
        status=$(docker inspect --format='{{.State.Health.Status}}' bracc-neo4j 2>/dev/null || echo "starting")
        [[ "$status" == "healthy" ]] && { log_ok "Neo4j healthy"; break; }
        attempts=$((attempts + 1)); log_info "Neo4j: $status ($attempts/30)..."; sleep 10
    done

    log_info "Criando índices Neo4j..."
    docker compose exec neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "
CREATE INDEX expense_id IF NOT EXISTS FOR (n:Expense) ON (n.expense_id);
CREATE INDEX person_cpf IF NOT EXISTS FOR (n:Person) ON (n.cpf);
CREATE INDEX person_person_id IF NOT EXISTS FOR (n:Person) ON (n.person_id);
CREATE INDEX company_cnpj IF NOT EXISTS FOR (n:Company) ON (n.cnpj);
CREATE INDEX health_cnes IF NOT EXISTS FOR (n:Health) ON (n.cnes_code);
CREATE INDEX finance_id IF NOT EXISTS FOR (n:MunicipalFinance) ON (n.finance_id);
CREATE INDEX gov_employee_id IF NOT EXISTS FOR (n:GovEmployee) ON (n.emp_id);
CREATE INDEX bid_id IF NOT EXISTS FOR (n:Bid) ON (n.bid_id)
" 2>&1 | filter_output | tee -a "$LOG"
    log_ok "Índices criados"

    echo "installed: $(date '+%Y-%m-%d %H:%M:%S')" > "$INSTALLED_FLAG"
    log_banner "✅  INSTALL CONCLUÍDO — $(date '+%d/%m/%Y %H:%M')"
}

# ── INTERNOS: update ──────────────────────────────────────────────────────────
_run_download() {
    local fonte="$1"
    local script="$ETL_DIR/scripts/download_${fonte}.py"
    [[ ! -f "$script" ]] && { log_skip "sem script de download — indo para importação"; return 0; }
    local INCREMENTAL_SOURCES=("transparencia_am" "tce_am" "servidores_federais" "comprasnet" "obras" "transferegov")
    local is_incremental=0
    for src in "${INCREMENTAL_SOURCES[@]}"; do [[ "$src" == "$fonte" ]] && is_incremental=1; done
    if [[ $is_incremental -eq 0 ]] && [[ -d "$DATA_DIR/$fonte" ]] && [[ -n "$(ls -A "$DATA_DIR/$fonte" 2>/dev/null)" ]]; then
        local file_count
        file_count=$(find "$DATA_DIR/$fonte" -name "*.csv" 2>/dev/null | wc -l)
        log_skip "data/$fonte já existe ($file_count arquivos) — pulando download"
        return 0
    fi
    log_info "Baixando $fonte..."
    cd "$ETL_DIR"
    local PROGRESS_FILE="$ROOT/bracc_download_${fonte}.tmp"
    rm -f "$PROGRESS_FILE"
    if [[ "$fonte" == "servidores_federais" ]]; then
        local sf_count
        sf_count=$(find "$DATA_DIR/servidores_federais" -name "*.csv" 2>/dev/null | wc -l)
        if [[ "$sf_count" -lt 20 ]]; then
            log_info "servidores_federais: primeira execucao — baixando historico desde 2014..."
            uv run python "scripts/download_${fonte}.py" --output-dir "../data/${fonte}" --historico >> "$PROGRESS_FILE" 2>&1 &
        else
            log_info "servidores_federais: atualizacao trimestral..."
            uv run python "scripts/download_${fonte}.py" --output-dir "../data/${fonte}" >> "$PROGRESS_FILE" 2>&1 &
        fi
    else
        uv run python "scripts/download_${fonte}.py" --output-dir "../data/${fonte}" >> "$PROGRESS_FILE" 2>&1 &
    fi
    CURRENT_PID=$!
    local last_shown="" last_log_size=0 last_change warned=0
    last_change=$(date +%s)
    while kill -0 $CURRENT_PID 2>/dev/null; do
        if [[ -f "$PROGRESS_FILE" ]]; then
            local last_line
            last_line=$(tail -1 "$PROGRESS_FILE" 2>/dev/null)
            if [[ -n "$last_line" && "$last_line" != "$last_shown" ]]; then
                echo "  |  $last_line" | tee -a "$LOG"
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
            if [[ $elapsed -ge 180 && $warned -eq 0 ]]; then
                echo "  ⚠️  [$fonte] download sem atividade ha $(( elapsed / 60 ))min — pode ter travado"
                warned=1
            fi
        fi
        sleep 1
    done
    wait $CURRENT_PID; local exit_code=$?; CURRENT_PID=""
    cat "$PROGRESS_FILE" >> "$LOG" 2>/dev/null
    rm -f "$PROGRESS_FILE"
    local file_count=0
    file_count=$(find "$DATA_DIR/$fonte" -name "*.csv" 2>/dev/null | wc -l)
    if [[ $exit_code -eq 0 ]] && [[ "$file_count" -gt 0 ]]; then
        log_ok "Download concluído: $fonte ($file_count arquivo(s))"
    elif [[ $exit_code -eq 0 ]] && [[ "$file_count" -eq 0 ]]; then
        log_err "Download OK mas nenhum arquivo gerado: $fonte"; beep_error; return 1
    else
        log_err "Download falhou: $fonte (código $exit_code)"; beep_error; return 1
    fi
}

_run_import() {
    local fonte="$1"
    local WATCHDOG_TIMEOUT=${TIMEOUT_MAP[$fonte]:-180}
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
            local last_lines
            last_lines=$(grep "Processando" "$PROGRESS_FILE" 2>/dev/null | tail -3)
            if [[ -n "$last_lines" && "$last_lines" != "$last_shown" ]]; then
                local last_line
                last_line=$(echo "$last_lines" | tail -1)
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
                last_shown="$last_lines"
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

_run_queue() {
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
        _run_download "$fonte" || { errors=$((errors + 1)); continue; }
        _run_import "$fonte"   || { errors=$((errors + 1)); continue; }
        log_ok "[$count/$total] $fonte concluído"
    done
    CURRENT_FONTE=""
    log_info "Fila $queue_name: $total fontes | Puladas: $skipped | Erros: $errors"
    log_blank
    SKIPPED=$((SKIPPED + skipped))
    ERRORS=$((ERRORS + errors))
}


_sync_neo4j() {
    log_banner "🗄️   SINCRONIZANDO COM NEO4J"
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

_start_docker() {
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

# ── SUBCOMANDO: update ────────────────────────────────────────────────────────
cmd_update() {
    local FORCE_FONTES=()
    local CUSTOM_QUEUE=()
    local MODO_AMAZONAS=0
    local args=("$@")
    local i=1
    while [[ $i -le ${#args[@]} ]]; do
        local arg="${args[$((i-1))]}"
        if [[ "$arg" == "--force" ]]; then
            FORCE_REIMPORT=1; i=$((i + 1))
            while [[ $i -le ${#args[@]} ]]; do
                local next="${args[$((i-1))]}"
                [[ "$next" == --* ]] && break
                FORCE_FONTES+=("$next"); i=$((i + 1))
            done
        elif [[ "$arg" == "--am" ]]; then
            MODO_AMAZONAS=1; i=$((i + 1))
        else
            CUSTOM_QUEUE+=("$arg"); i=$((i + 1))
        fi
    done

    log_banner "🚀  BRACC-ETL UPDATE — $(date '+%d/%m/%Y %H:%M')"
    _start_docker
    [[ "$MODO_TESTE" == "Y" ]] || _sync_neo4j

    if [[ ${#CUSTOM_QUEUE[@]} -gt 0 ]]; then
        _run_queue "Customizada" "${CUSTOM_QUEUE[@]}"
    elif [[ $MODO_AMAZONAS -eq 1 ]]; then
        _run_queue "🌿 Amazonas" "${AMAZONAS_QUEUE[@]}"
    elif [[ $FORCE_REIMPORT -eq 1 && ${#FORCE_FONTES[@]} -gt 0 ]]; then
        _run_queue "--force" "${FORCE_FONTES[@]}"
    else
        _run_queue "Federal" "${DEFAULT_QUEUE[@]}"
        _run_queue "🌿 Amazonas" "${AMAZONAS_QUEUE[@]}"
    fi

    log_banner "✅  UPDATE CONCLUÍDO — $(date '+%d/%m/%Y %H:%M')"
    log_info "Total puladas: $SKIPPED  |  Total erros: $ERRORS"
    log_blank
    beep; beep
}

# ── MAIN ─────────────────────────────────────────────────────────────────────
COMANDO="${1:-help}"
shift || true

case "$COMANDO" in
    help)     cmd_help ;;
    list)     cmd_list ;;
    install)  cmd_install ;;
    validate) cmd_validate ;;
    check)    cmd_check "$@" ;;
    update)   cmd_update "$@" ;;
    *)
        echo ""
        echo "  ❌  Comando desconhecido: '$COMANDO'"
        echo "  💡  Use: bash orchestrator.sh help"
        echo ""
        exit 1
        ;;
esac
