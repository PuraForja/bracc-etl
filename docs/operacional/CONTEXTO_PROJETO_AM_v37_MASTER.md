# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v37
> Gerado em 08/06/2026

---

## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO
Antes de qualquer ação leia:
1. docs/operacional/ORIENTACOES_IA.md — regras obrigatórias
2. docs/operacional/CHANGELOG.md | tail -30 — o que já foi feito
3. docs/operacional/ESTADO_ATUAL.md — estado dinâmico do banco e filas

---

## PASSO A PASSO — NOVA SESSÃO
```bash
cd ~/bracc && docker compose up -d && echo OK
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10" && echo OK
cat ~/bracc/docs/operacional/ESTADO_ATUAL.md
tail -30 ~/bracc/docs/operacional/CHANGELOG.md
```

---

## PERFIL
Nome: Alberto (Rolim)
Contexto: Oposição política no Amazonas — Partido Missão
Hardware: Xeon 2680 v4, 32GB RAM, HD 2TB
SO: Windows 11 + WSL Ubuntu
GitHub: https://github.com/PuraForja/bracc-etl
Email: arolim2002@gmail.com
Projeto: ~/bracc/ (WSL)

---

## INFRAESTRUTURA
Neo4j: localhost:7474 — neo4j / changeme
API: localhost:8000
Frontend: localhost:3000 — teste@bracc.com / senha123 / invite: rolim
GDS: 2.13.10 instalado
Neo4j heap: 8GB (.env)

---

## STATUS NEO4J (08/06/2026)
Company:             40.674.210
Partner:             17.774.658
GovEmployee:         10.277.914  ← +8.273 servidores federais AM
Expense:              3.836.389
MunicipalFinance:     3.469.721
Person:               3.113.425
DeclaredAsset:        2.817.000
Bid:                  2.170.419  ← +71.065 TCE-AM licitações
Health:                 612.561
TaxWaiver:              291.799
GovTravel:              260.000
Contract:               214.701  ← +150.511 TCE-AM contratos
GovCardExpense:         131.950
GlobalPEP:              117.910
Amendment:              101.801
Election:                50.497
Fund:                    41.107
Payment:                 40.000
Sanction:                24.077
InternationalSanction:    9.707
TOTAL: ~89M+

---

## O QUE FOI FEITO (06-08/06/2026)
- CLAUDE.md criado na raiz — ponto de entrada para IA
- ESTADO_ATUAL.md criado — estado dinâmico do banco
- parse_date — suporte ISO 8601 com timezone
- TCE-AM reimportado — data_assinatura e data_publicacao corrigidos
- orchestrator P1 — docker compose exec neo4j corrigido
- pncp removido de INCREMENTAL_SOURCES
- GraphCanvas.tsx — bug grafo resolvido (pauseAnimation + reheat)
- ZoomControls.tsx — onMouseDown preventDefault
- servidores_federais — download histórico trimestral + pipeline + 8.273 GovEmployee
- Backup Neo4j — 06/06/2026

---

## PENDENTES PRIORITÁRIOS
- [ ] Pipeline servidores_federais importa só CSV mais recente — histórico ignorado
- [ ] Índice emp_id GovEmployee — queries lentas
- [ ] SAME_AS servidores_federais ↔ Person
- [ ] TSE Filiação Partidária
- [ ] BCB Penalidades — API Olinda
- [ ] Amom Mandel — 4 nodes separados
- [ ] Expansão adaptativa depth=2
- [ ] CNES pipeline
- [ ] Busca por nome não abre grafo no frontend
- [ ] Orquestrador P2-P6

---

## COMANDOS ÚTEIS
```bash
# Subir ambiente
cd ~/bracc && docker compose up -d && echo OK

# Estado do banco
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup
docker run --rm -v bracc_neo4j-data:/data -v /home/rolim:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo OK

# Orquestrador
bash ~/bracc/orchestrator.sh help
bash ~/bracc/orchestrator.sh list
bash ~/bracc/orchestrator.sh validate
bash ~/bracc/orchestrator.sh update --am
bash ~/bracc/orchestrator.sh update --force servidores_federais

# Commitar
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh frontend/src/ && git status --short && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo OK
```

---

## HISTÓRICO RESUMIDO
| Data | O que foi feito |
|---|---|
| 20-26/04 | Infraestrutura + CNPJ + patches |
| 27-30/04 | Downloads massivos + viagens + cepim + bcb |
| 01-02/05 | run_query_with_retry + batch_size=500 + índices |
| 03-05/05 | camara vetorizado + heap Neo4j + auditoria banco |
| 07-09/05 | orchestrator v1 + sessão única loader + câmara completa |
| 10/05 | Barra de progresso + MODO_TESTE + watchdog |
| 12-13/05 | Senado + transparencia_am início + _download_utils |
| 17/05 | transparencia_am completa + WCC + entity resolution |
| 23-31/05 | PNCP importação + bid_id index + backup |
| 01-03/06 | GDS + WCC community_id + TSE bens + docs reorganizados |
| 04-05/06 | TCE-AM pipeline + orchestrator refactor |
| 06/06 | parse_date fix + backup + GraphCanvas fix + docs |
| 07-08/06 | servidores_federais histórico + grafo fix + limpeza docs |

---

## CHECKLIST NOVA SESSÃO
[ ] cd ~/bracc && docker compose up -d
[ ] Verificar totais Neo4j
[ ] tail -30 CHANGELOG.md
[ ] cat ESTADO_ATUAL.md
[ ] Continuar pendentes prioritários

---
v37 — 08/06/2026
servidores_federais: 8.273 GovEmployee AM importados
TCE-AM: 214.701 contratos + 2.170.419 bids validados
Grafo frontend: bug resolvido
PRÓXIMO: pipeline servidores_federais histórico + índice emp_id + SAME_AS
