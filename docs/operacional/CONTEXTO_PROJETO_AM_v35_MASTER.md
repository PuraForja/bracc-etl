# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v35
> Gerado em 03/06/2026
---
## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO
1. Leia o CHANGELOG antes de qualquer correção de código
2. Leia o ORIENTACOES_IA.md para regras de comportamento
3. Após qualquer alteração de código: atualize o CHANGELOG e commite
4. Ao final de cada sessão: gere novo MASTER e commite
5. Sempre inclua data/hora nos logs
6. Avise quando a sessão estiver no limite — OBRIGATÓRIO
7. Nunca reescrever scripts com requests puro — sempre usar _download_utils.py
8. Confirmar alterações antes de executar — avisar se altera banco, arquivo ou config
9. Todo comando deve terminar com && echo "OK"
10. NUNCA usar curl para sobrescrever loader.py do GitHub
11. Subir ambiente SEMPRE: cd ~/bracc && docker compose up -d
12. NUNCA usar -f infra/docker-compose.yml
13. Todo novo pipeline com CSV > 500k linhas DEVE usar chunksize=50_000
14. Todo novo campo usado em MATCH/MERGE DEVE ter índice criado ANTES da importação
15. Projeto em ~/bracc/ (WSL) — não em ~/Downloads/br-acc-novo/
---
## PASSO A PASSO — NOVA SESSÃO
cd ~/bracc && docker compose up -d && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10" && echo "OK"
---
## PERFIL
Nome: Alberto (Rolim)
Contexto: Oposição política no Amazonas — Partido Missão
Hardware: Xeon 2680 v4, 32GB RAM, HD 2TB
SO: Windows 11 + WSL Ubuntu
GitHub: https://github.com/PuraForja/bracc-etl
---
## INFRAESTRUTURA
Neo4j: localhost:7474 — neo4j / changeme
API: localhost:8000
Frontend: localhost:3000 — teste@bracc.com / senha123 / invite: rolim
Projeto: ~/bracc/ (WSL)
Neo4j heap: 8GB (NEO4J_HEAP_MAX=8G no .env)
GDS: 2.13.10 instalado e funcionando
---
## STATUS NEO4J (03/06/2026)
Company: 40.674.210
Partner: 17.774.658
GovEmployee: 10.269.641
Expense: 3.836.389
MunicipalFinance: 3.469.721
Person: 3.113.425
Bid: 2.099.331
DeclaredAsset: 2.817.000 — NOVO
Health: 612.561
TaxWaiver: 291.799
GovTravel: 260.000
GovCardExpense: 131.950
GlobalPEP: 117.910
Amendment: 101.801
Election: 50.497
Contract: 64.121
Fund: 41.107
Payment: 40.000
Sanction: 24.077
InternationalSanction: 9.707
SAME_AS (relações): ~2.5M
DOOU (relações): 6M+
DECLAROU_BEM (relações): 11.3M — NOVO
LICITOU (relações): 2.099.331
TOTAL: ~88M+
---
## FIXES APLICADOS SESSÕES 01-03/06/2026

### GDS + WCC + community_id
- GDS 2.13.10 instalado
- .env corrigido: NEO4J_HEAP_MAX=1G → 8G
- WCC rodado: community_id em 21M nodes
- graph_expand_d1.cypher: usa community_id indexado
- Índices: community_id_person, community_id_partner, community_id_globalpep, titulo_eleitor_person, declared_asset_id

### SAME_AS em escala
- Person↔GlobalPEP: 7.217 relações (CPF)
- TSE histórico: 189k relações (candidatos 2024 sem CPF → anos anteriores)
- link_tse_nocpf.py: script que cruza 463k Person TSE sem CPF com CSVs 2016-2022
- Pipeline TSE: grava data_nascimento + titulo_eleitor nos nodes
- Pipeline TSE: SAME_AS automático via titulo_eleitor (confiança 1.0) e nome+nascimento (0.97)

### TSE pipeline
- download_tse.py: adicionado DT_NASCIMENTO + NR_TITULO_ELEITORAL ao mapeamento
- pipelines/tse.py: doações reescritas para chunked 50k (antes travava com 3.1M linhas)
- 6.045.442 doações processadas

### TSE Bens Declarados
- download_tse_bens_cdn.py: baixa direto do CDN TSE sem BigQuery
- 17.5M linhas, 2006-2024, JOIN com candidatos.csv para CPF (85% cobertura)
- pipelines/tse_bens.py: chunked 50k linhas
- 5.636.173 DeclaredAsset + 11.322.572 DECLAROU_BEM

### Documentação reorganizada
- docs/ reorganizado em: operacional/ referencia/ arquivo/ publico/
- CATALOGO_FONTES.md: consolidação de 5 arquivos em 1
- DOWNLOADS_STATUS.md: fusão de CORRECOES_SCRIPTS_DOWNLOAD + URLS_CORRETAS
- BRACC_INSTALLER_ESCOPO.md: escopo completo do novo instalador TUI
- ORIENTACOES_PIPELINE.md: regras obrigatórias para novos pipelines

---
## CASO VALIDADO — DIEGO ROBERTO AFONSO
CPF: 784.440.632-15
Element ID Person CPF: 4:91a9add5-04eb-4574-a38d-fd9437d62144:58716976
community_id: 118904
Servidor: SUHAB + SECT (dupla lotação AM)
Grafo depth=1: 109 nodes, 113 edges (person=101, company=4, election=3, partner=1)
Status: SOCIO_DE funcionando — WCC resolve o problema de 3 saltos

---
## ARQUITETURA WCC — COMANDOS
# Re-rodar WCC (obrigatório após importação que cria SAME_AS)
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.graph.drop('identity-graph') YIELD graphName" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.graph.project('identity-graph', ['Person','Partner','GlobalPEP','OffshoreOfficer'], {SAME_AS: {orientation: 'UNDIRECTED'}}) YIELD graphName, nodeCount, relationshipCount" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.wcc.write('identity-graph', {writeProperty: 'community_id'}) YIELD componentCount, nodePropertiesWritten" && echo "OK"

---
## PENDENTES TÉCNICOS
[ ] Backup Neo4j — URGENTE (último: 31/05)
[ ] BRACC Installer — novo orquestrador TUI (docs/operacional/BRACC_INSTALLER_ESCOPO.md)
[ ] TSE Filiação Partidária — download CDN por partido/UF
[ ] BCB Penalidades — reescrever com API Olinda (mapeado em DOWNLOADS_STATUS.md)
[ ] PEP CGU — token email descartável
[ ] INPE PRODES + SICAR — desmatamento e propriedades rurais
[ ] TCE-AM — auditoria contratos estaduais
[ ] Amom Mandel — 4 nodes separados
[ ] Expansão adaptativa depth=2
[ ] Bug frontend — react-force-graph-2d trava após drag/zoom
[ ] Entity resolution GovEmployee AM — 10M servidores sem CPF
[ ] CNES download_cnes_am.py + pipeline
[ ] Atualizar CATALOGO_FONTES.md com status atual de todos os pipelines
[ ] Consultar outras IAs com BRACC_INSTALLER_ESCOPO.md

---
## DOCUMENTAÇÃO
docs/operacional/ORIENTACOES_IA.md — regras de comportamento
docs/operacional/ORIENTACOES_PIPELINE.md — regras para novos pipelines
docs/operacional/SETUP_INDICES.md — índices obrigatórios
docs/operacional/PENDENCIAS_FEATURES.md — features planejadas e bugs
docs/operacional/DOWNLOADS_STATUS.md — problemas e soluções de download
docs/operacional/BRACC_INSTALLER_ESCOPO.md — escopo novo instalador
docs/referencia/CATALOGO_FONTES.md — catálogo completo de fontes

---
## COMANDOS ÚTEIS
# Subir ambiente
cd ~/bracc && docker compose up -d && echo "OK"

# Estado banco
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10" && echo "OK"

# Backup
docker run --rm -v bracc_neo4j-data:/data -v /home/rolim:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo "OK"

# link_tse_nocpf
cd ~/bracc && python3 etl/scripts/link_tse_nocpf.py 2>&1 | tail -5 && echo "OK"

# Commitar
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"

# Busca fulltext
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL db.index.fulltext.queryNodes('entity_search', 'NOME') YIELD node, score RETURN labels(node)[0], node.name, node.cpf, score ORDER BY score DESC LIMIT 10" && echo "OK"

# Testar API Diego
curl -s "http://localhost:8000/api/v1/graph/4:91a9add5-04eb-4574-a38d-fd9437d62144:58716976?depth=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print('nodes:', len(d.get('nodes',[])), 'edges:', len(d.get('edges',[])))" && echo "OK"

---
## HISTÓRICO
01/06: GDS + WCC + community_id + graph_expand_d1 reescrito
01/06: SAME_AS Person↔GlobalPEP 7.217 + TSE histórico 189k
02/06: TSE pipeline corrigido — chunked + data_nascimento + titulo_eleitor
02/06: TSE reimportado — 3.1M candidatos + 6M doações
03/06: TSE bens — 5.6M DeclaredAsset + 11.3M DECLAROU_BEM
03/06: WCC re-rodado — 21M nodes com community_id
03/06: docs reorganizados — operacional/referencia/arquivo/publico
03/06: CATALOGO_FONTES.md consolidado de 5 arquivos

---
## CHECKLIST NOVA SESSÃO
[ ] cd ~/bracc && docker compose up -d
[ ] Verificar totais Neo4j
[ ] Fazer backup Neo4j — URGENTE
[ ] Consultar IAs com BRACC_INSTALLER_ESCOPO.md
[ ] Iniciar BRACC Installer ou próxima fonte pendente

---
v35 — 03/06/2026
TSE bens: 5.6M DeclaredAsset + 11.3M DECLAROU_BEM
WCC: 21M nodes com community_id atualizado
docs: reorganizados e consolidados
Total banco: ~88M nodes
PRÓXIMO: Backup + BRACC Installer + TSE Filiação + BCB/PEP CGU
