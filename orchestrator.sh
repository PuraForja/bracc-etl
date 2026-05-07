#!/usr/bin/env bash
# orchestrator.sh — Download + Importação sequencial
# Uso: bash orchestrator.sh [fonte1 fonte2 ...]
# Sem argumentos: usa a fila padrão abaixo
# Logs: pipeline_imports.log
#
# ── COMO PULAR UMA FONTE ──────────────────────────────────────────────────────
# Adicione o nome na lista SKIP abaixo.
# A fonte será completamente ignorada (nem download nem importação).
# Para reativar, remova da lista SKIP.
# ─────────────────────────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ETL_DIR="$ROOT/etl"
DATA_DIR="$ROOT/data"
LOG="$ROOT/pipeline_imports.log"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-changeme}"

# ── FONTES A IGNORAR (adicione aqui para pular) ───────────────────────────────
SKIP=(
    pncp            # roda em background separado — nunca na fila
    senado          # dando problema — aguardar fix
    # cnpj          # exemplo: descomente para pular
)
# ─────────────────────────────────────────────────────────────────────────────

# ── FILA COMPLETA — todas as fontes com script de download disponível
# Ordem: menores e mais rápidas primeiro, pesadas por último
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

# ── FONTES SEM SCRIPT DE DOWNLOAD (só importação, dados já devem estar em data/)
IMPORT_ONLY=(bndes ibama inep pgfn tcu comprasnet transferegov stj_dados_abertos)

# ── FONTES BIGQUERY (precisam credencial GCP — ignoradas por padrão)
BIGQUERY=(tse_bens tse_filiados caged dou stf mides rais datajud)

# ─────────────────────────────────────────────────────────────────────────────

log() {
    echo "$(date '+%d/%m/%Y %H:%M:%S') $*" | tee -a "$LOG"
}

beep() {
    powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)" 2>/dev/null || true
}

is_skipped() {
    local fonte="$1"
    for s in "${SKIP[@]}"; do
        [[ "$s" == "$fonte" ]] && return 0
    done
    return 1
}

start_docker() {
    log "[DOCKER] Subindo containers..."
    cd "$ROOT"
    docker compose up -d 2>&1 | tee -a "$LOG"
    log "[DOCKER] Aguardando Neo4j ficar healthy..."
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        local status
        status=$(docker inspect --format='{{.State.Health.Status}}' bracc-neo4j 2>/dev/null || echo "starting")
        if [[ "$status" == "healthy" ]]; then
            log "[DOCKER] Neo4j healthy ✅"
            return 0
        fi
        attempts=$((attempts + 1))
        log "[DOCKER] Neo4j: $status — aguardando... ($attempts/30)"
        sleep 10
    done
    log "[DOCKER] AVISO: Neo4j não ficou healthy — continuando mesmo assim"
}

start_pncp_background() {
    local running
    running=$(pgrep -f "download_pncp.py" || true)
    if [[ -n "$running" ]]; then
        log "[PNCP] já rodando (PID $running) — mantendo"
        return
    fi
    log "[PNCP] iniciando em background com loop de reinício automático..."
    (
        while true; do
            cd "$ETL_DIR"
            uv run python scripts/download_pncp.py --output-dir "../data/pncp"
            log "[PNCP] caiu ou terminou — reiniciando em 30s..."
            sleep 30
        done >> "$LOG" 2>&1
    ) &
    log "[PNCP] PID $!"
}

run_download() {
    local fonte="$1"
    local script="$ETL_DIR/scripts/download_${fonte}.py"

    if [[ ! -f "$script" ]]; then
        log "  [SKIP download] sem script — indo direto para importação"
        return 0
    fi

    # Verifica se já tem dados — pula download
    if [[ -d "$DATA_DIR/$fonte" ]] && [[ -n "$(ls -A "$DATA_DIR/$fonte" 2>/dev/null)" ]]; then
        log "  [SKIP download] data/$fonte já existe — pulando"
        return 0
    fi

    log "  [DOWNLOAD] iniciando $fonte..."
    cd "$ETL_DIR"

    if uv run python "scripts/download_${fonte}.py" \
        --output-dir "../data/${fonte}" \
        2>&1 | tee -a "$LOG"; then
        log "  [DOWNLOAD OK] $fonte ✅"
    else
        log "  [DOWNLOAD ERRO] $fonte — pulando importação"
        return 1
    fi
}

run_import() {
    local fonte="$1"
    log "  [IMPORT] iniciando $fonte..."
    cd "$ETL_DIR"

    if uv run bracc-etl run \
        --source "$fonte" \
        --neo4j-password "$NEO4J_PASSWORD" \
        --data-dir "$DATA_DIR" \
        2>&1 | tee -a "$LOG"; then
        log "  [IMPORT OK] $fonte ✅"
        beep
    else
        log "  [IMPORT ERRO] $fonte"
        beep
        return 1
    fi
}

# ── MAIN ─────────────────────────────────────────────────────────────────────
log "============================================"
log "ORQUESTRADOR INICIADO"
log "============================================"

start_docker
start_pncp_background

# Define fila
if [[ $# -gt 0 ]]; then
    QUEUE=("$@")
    log "Fila customizada: ${QUEUE[*]}"
else
    QUEUE=("${DEFAULT_QUEUE[@]}")
    log "Fila padrão: ${#QUEUE[@]} fontes"
fi

# Processa cada fonte
for fonte in "${QUEUE[@]}"; do

    # Verifica se está na lista SKIP
    if is_skipped "$fonte"; then
        log ""
        log "====== FONTE: $fonte — IGNORADA (lista SKIP) ======"
        continue
    fi

    log ""
    log "====== FONTE: $fonte ======"

    run_download "$fonte" || continue
    run_import "$fonte" || continue

    log "  [CONCLUÍDO] $fonte"
done

log ""
log "============================================"
log "ORQUESTRADOR CONCLUÍDO"
log "============================================"
beep
beep
