# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v36
> Gerado em 05/06/2026

---

## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO

Antes de qualquer ação leia:
1. docs/operacional/ORIENTACOES_IA.md — regras obrigatórias
2. docs/operacional/CHANGELOG.md | tail -30 — o que já foi feito
3. docs/operacional/TAREFA_PENTE_FINO_DOCS.md — tarefas pendentes

---

## PASSO A PASSO — NOVA SESSÃO

cd ~/bracc && docker compose up -d && echo OK
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10" && echo OK

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

## STATUS NEO4J (05/06/2026)

Company:             40.674.210
Partner:             17.774.658
GovEmployee:         10.269.641
Expense:              3.836.389
MunicipalFinance:     3.469.721
Person:               3.113.425
DeclaredAsset:        2.817.000
Bid:                  2.099.354
Health:                 612.561
TaxWaiver:              291.799
GovTravel:              260.000
GovCardExpense:         131.950
GlobalPEP:              117.910
Amendment:              101.801
Contract:                64.190
Election:                50.497
Fund:                    41.107
Payment:                 40.000
Sanction:                24.077
InternationalSanction:    9.707
SAME_AS (relacoes):   ~2.5M
LICITOU (relacoes):   2.099.331
DECLAROU_BEM:        11.322.572
TOTAL: ~88M+

---

## O QUE FOI FEITO NESTA SESSÃO (05/06/2026)

### TCE-AM — pipeline completo
- download_tce_am.py: baixa contratos e licita de 466 unidades x 14 anos
- pipelines/tce_am.py: Contract + Bid + VENCEU + CONTRATADO_POR + LICITOU_AM
- orchestrator.sh: LABEL_MAP + TIMEOUT_MAP + AMAZONAS_QUEUE + URL_MAP + INCREMENTAL_SOURCES
- Download rodando via orchestrator update tce_am (incremental)

### Pente fino documentação
- ORIENTACOES_PIPELINE.md: reescrito com regras completas
- CATALOGO_FONTES.md: tce_am marcado implementado, tse_bens corrigido
- TAREFA_PENTE_FINO_DOCS.md: itens 4, 5, 6, 7 concluidos
- .gitignore: Zone.Identifier, .installed, *.tmp adicionados

---

## TAREFAS PENDENTES DO PENTE FINO

Ver TAREFA_PENTE_FINO_DOCS.md — itens restantes:
- Criar CLAUDE.md (doc estatico de entrada)
- Criar docs/operacional/ESTADO_ATUAL.md
- Deletar TAREFA_PENTE_FINO_DOCS.md
- Gerar v37 apos completar

---

## PENDENTES TECNICOS

[ ] Backup Neo4j — URGENTE (ultimo: 31/05 — 5 dias)
[ ] TCE-AM download completo — rodando em background via orchestrator
[ ] TSE Filiacao Partidaria — download CDN sem BigQuery
[ ] BCB Penalidades — reescrever com API Olinda
[ ] PEP CGU — token email descartavel
[ ] INPE PRODES + SICAR
[ ] Amom Mandel — 4 nodes separados
[ ] Expansao adaptativa depth=2
[ ] Bug frontend — react-force-graph-2d trava apos drag/zoom
[ ] CNES download_cnes_am.py + pipeline
[ ] BRACC Installer — ver BRACC_INSTALLER_ESCOPO.md

---

## ARQUITETURA WCC

Re-rodar apos qualquer importacao que cria SAME_AS:
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.graph.drop('identity-graph') YIELD graphName" && echo OK
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.graph.project('identity-graph', ['Person','Partner','GlobalPEP','OffshoreOfficer'], {SAME_AS: {orientation: 'UNDIRECTED'}}) YIELD graphName, nodeCount, relationshipCount" && echo OK
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.wcc.write('identity-graph', {writeProperty: 'community_id'}) YIELD componentCount, nodePropertiesWritten" && echo OK

---

## CASO VALIDADO — DIEGO ROBERTO AFONSO

CPF: 784.440.632-15
Element ID Person CPF: 4:91a9add5-04eb-4574-a38d-fd9437d62144:58716976
community_id: 118904
Servidor: SUHAB + SECT (dupla lotacao AM)
Grafo depth=1: 109 nodes, 113 edges — SOCIO_DE funcionando via WCC

---

## COMANDOS UTEIS

# Subir ambiente
cd ~/bracc && docker compose up -d && echo OK

# Backup
docker run --rm -v bracc_neo4j-data:/data -v /home/rolim:/backup alpine tar czf /backup/neo4j-backup-20260605.tar.gz /data && echo OK

# Commitar
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync 2026-06-05 23:23" && git push origin main && echo OK

# Orchestrator
bash ~/bracc/orchestrator.sh help
bash ~/bracc/orchestrator.sh update tce_am
bash ~/bracc/orchestrator.sh update --am
bash ~/bracc/orchestrator.sh list
bash ~/bracc/orchestrator.sh check

---

## HISTORICO

01/06: GDS + WCC + community_id + graph_expand_d1 reescrito
01/06: SAME_AS Person x GlobalPEP 7.217 + TSE historico 189k
02/06: TSE pipeline corrigido — chunked + data_nascimento + titulo_eleitor
02/06: TSE reimportado — 3.1M candidatos + 6M doacoes
03/06: TSE bens — 5.6M DeclaredAsset + 11.3M DECLAROU_BEM
03/06: WCC re-rodado — 21M nodes com community_id
03/06: docs reorganizados — operacional/referencia/arquivo/publico
04/06: SETUP_INDICES.md — fix docker compose
05/06: TCE-AM — pipeline + download + orchestrator
05/06: pente fino docs — ORIENTACOES_PIPELINE, CATALOGO_FONTES, TAREFA itens 4-7

---

## CHECKLIST NOVA SESSAO

[ ] cd ~/bracc && docker compose up -d
[ ] Verificar totais Neo4j
[ ] Fazer backup Neo4j — URGENTE
[ ] Continuar pente fino: CLAUDE.md + ESTADO_ATUAL.md
[ ] Verificar TCE-AM download progress
[ ] Gerar v37 ao final

---

v36 — 05/06/2026
TCE-AM: pipeline completo registrado no orchestrator
Pente fino: itens 4-7 concluidos
Total banco: ~88M nodes
PROXIMO: backup + CLAUDE.md + ESTADO_ATUAL.md + TCE-AM download completo
