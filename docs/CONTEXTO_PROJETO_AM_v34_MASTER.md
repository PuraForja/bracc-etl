# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v34
> Gerado em 31/05/2026

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
9. Abrir arquivos grandes no Notepad — heredoc trava no Git Bash do Windows
10. Comandos longos na vertical travam o Git Bash — mandar em linha única
11. Todo comando deve terminar com && echo "OK" para confirmar execução
12. NUNCA usar curl para sobrescrever loader.py do GitHub
13. Subir ambiente SEMPRE pelo compose da raiz: cd ~/bracc && docker compose up -d
14. NUNCA usar -f infra/docker-compose.yml
15. WSL e Git Bash são ambientes separados — credenciais Git nao compartilhadas

---

## ORIENTAÇÃO OBRIGATÓRIA — SESSÃO ÚNICA NO LOADER

Pipelines pendentes do fix:
senado_cpis, cnpj, camara_inquiries, mides, transferegov, transparencia, tse, senado, tcu, datajud, ibama, icij, tse_filiados

---

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU

cd ~/bracc && docker compose up -d && echo "OK"
cd ~/bracc && docker compose ps && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10" && echo "OK"

---

## PERFIL

Nome: Alberto (Rolim)
Contexto: Oposição política no Amazonas
Hardware: Xeon 2680 v4, 32GB RAM, HD 2TB
SO: Windows 11 / Git Bash + WSL
GitHub: https://github.com/PuraForja/bracc-etl
Email GitHub: arolim2002@gmail.com

---

## INFRAESTRUTURA

Neo4j: localhost:7474 — neo4j / changeme
API: localhost:8000
Frontend: localhost:3000 — teste@bracc.com / senha123 / invite: rolim

Projeto em: ~/bracc/ (WSL) — NAO em ~/Downloads/br-acc-novo/ (caminho antigo Git Bash)

---

## STATUS NEO4J (31/05/2026)

Company: 40.671.726+
Partner: 17.774.658
GovEmployee: 10.269.641
Expense: 3.836.389
MunicipalFinance: 3.469.721
Person: 2.780.851
Bid: 2.099.331 — PNCP importado 31/05
Health: 612.561
TaxWaiver: 291.799
GovTravel: 260.000
GovCardExpense: 131.950
GlobalPEP: 117.910
Amendment: 101.801
Contract: 64.121
Fund: 41.107
Election: 33.602 — TSE 2002-2024 completo
Sanction: 24.077
InternationalSanction: 9.707
SAME_AS (relacoes): 543.079
LICITOU (relacoes): 2.099.331
TOTAL: ~83M

---

## FIXES APLICADOS SESSAO 23-31/05/2026

PNCP importacao: 2.099.331 Bid + 17.585 Company + 2.099.331 LICITOU
bid_id index: adicionado SETUP_INDICES.md e orchestrator.sh
PNCP checkpoint fix: 58/65 meses baixados
WSL Git: credential.helper store configurado

## FIXES APLICADOS SESSAO 21-23/05/2026

graph_expand adaptativo: 1s depth=2 — antes 32s+ 504 timeout
SAME_AS em lote: 543.079 relacoes Person→Partner
SAME_AS manual Diego: SOCIO_DE=4 Empresa=10 no grafo

---

## CASO VALIDADO — DIEGO ROBERTO AFONSO

CPF: 784.440.632-15
Element ID Person CPF: 4:91a9add5-04eb-4574-a38d-fd9437d62144:58716976
Element ID Person TSE: 4:91a9add5-04eb-4574-a38d-fd9437d62144:58528356
Element ID Partner: 4:91a9add5-04eb-4574-a38d-fd9437d62144:40474788
Servidor: SUHAB + SECT (dupla lotacao AM)
Empresas: DRA Derivados Petroleo, DH Lojas Conveniencias, Gelabrea Gelo, ID Vestuario
Conflito: DRA forneceu R$67.386 para Adail Filho e Sidney Leite
Grafo depth=2: SOCIO_DE=4, Empresa=10

---

## CASO AMOM MANDEL LINS FILHO

CPF: 072.847.254-60
4 nodes separados — deduplicacao pendente
Emendas: ~R$84M (deputado federal AM 2022)
Padrasto: Mario Coelho de Mello (TCE-AM)

---

## PENDENTES TECNICOS

[ ] Backup Neo4j — URGENTE (ultimo: 09/05 — 22 dias)
[ ] SAME_AS Person→Person entre fontes (TSE vs transparencia)
[ ] POSSIVEL_MESMO_INDIVIDUO + TEM_REMUNERACAO — frontend
[ ] Deduplicacao automatica CPF no orchestrator
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] Fix sessao unica — senado_cpis, cnpj, etc.
[ ] Amom Mandel — 4 nodes separados
[ ] BigQuery (rais, dou, stf, mides) — apos credencial GCP
[ ] CNES download_cnes_am.py + pipeline
[ ] Relatorio exportavel casos conflito de interesse

---

## SETUP OBRIGATORIO — NOVA INSTALACAO

Ver docs/SETUP_INDICES.md — indices obrigatorios incluindo bid_id

---

## ORQUESTRADOR

bash ~/bracc/orchestrator.sh
bash ~/bracc/orchestrator.sh --amazonas
MODO_TESTE=Y bash ~/bracc/orchestrator.sh --force tse

---

## COMANDOS UTEIS

# Backup Neo4j
docker run --rm -v bracc_neo4j-data:/data -v /home/rolim:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo "OK"

# Commitar (WSL)
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"

# Busca fulltext
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL db.index.fulltext.queryNodes('entity_search', 'NOME') YIELD node, score RETURN labels(node)[0], node.name, node.cpf, score ORDER BY score DESC LIMIT 10" && echo "OK"

# Testar API grafo
curl -s "http://localhost:8000/api/v1/graph/ELEMENT_ID?depth=2" | python3 -c "import sys,json; d=json.load(sys.stdin); print('nodes:', len(d.get('nodes',[])), 'edges:', len(d.get('edges',[])), 'truncated:', len(d.get('truncated_nodes',[])))" && echo "OK"

# Monitor PNCP import
bash ~/bracc/monitor_pncp.sh

---

## HISTORICO

08-09/05: camara 3.836M expenses + loader sessao unica
12-13/05: transparencia_am download 6857 CSVs
15-17/05: transparencia_am 10.269M GovEmployee + entity resolution
17-19/05: POSSIVEL_MESMO_INDIVIDUO 211k + 58 conflitos
21/05: TSE completo 2002-2024 + fulltext index + graph_expand
21-23/05: graph_expand adaptativo 1s + SAME_AS 543k + PNCP checkpoint fix
23-31/05: PNCP 2.099M Bids importados + bid_id index + WSL Git config

---

## CHECKLIST NOVA SESSAO

[ ] Ler CHANGELOG.md
[ ] cd ~/bracc && docker compose up -d
[ ] Neo4j totais
[ ] Fazer backup Neo4j (URGENTE — 22 dias sem backup)
[ ] Gerar v35 ao final

---

v34 — 31/05/2026
PNCP: 2.099.331 Bids importados + 2.099.331 LICITOU
bid_id index adicionado ao SETUP_INDICES.md e orchestrator.sh
Total banco: ~83M nodes
PROXIMO: backup Neo4j + SAME_AS Person→Person + frontend pendentes
