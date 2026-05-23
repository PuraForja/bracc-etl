# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v33
> Gerado em 23/05/2026

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
11. Todo comando deve terminar com `&& echo "OK"` para confirmar execução
12. NUNCA usar curl para sobrescrever loader.py do GitHub
13. Subir ambiente SEMPRE pelo compose da raiz: `cd ~/Downloads/br-acc-novo && docker compose up -d`
14. NUNCA usar `-f infra/docker-compose.yml`

---

## ORIENTAÇÃO OBRIGATÓRIA — SESSÃO ÚNICA NO LOADER

```python
# CORRETO
with loader.open_session() as session:
    loader.load_nodes("Label", rows, key_field="id", session=session)
    loader.load_relationships(..., session=session)
```

**Pipelines pendentes do fix:**
senado_cpis, cnpj, camara_inquiries, mides, transferegov, transparencia, tse, senado, tcu, datajud, ibama, icij, tse_filiados

---

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU

```bash
cd ~/Downloads/br-acc-novo && docker compose up -d && echo "OK"
cd ~/Downloads/br-acc-novo && docker compose ps && echo "OK"
cd ~/Downloads/br-acc-novo && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10" && echo "OK"
python3 -c "import os; expected=[f'pncp_{y}{m:02d}.json' for y in range(2021,2027) for m in range(1,13) if (y,m)<=(2026,5)]; path=os.path.expanduser('~/Downloads/br-acc-novo/data/pncp/'); downloaded=[f for f in expected if os.path.exists(os.path.join(path,f))]; print(f'PNCP: {len(downloaded)}/{len(expected)} ({len(downloaded)/len(expected)*100:.1f}%)')"
```

---

## PERFIL

| Campo | Valor |
|---|---|
| Nome | Alberto (Rolim) |
| Contexto | Oposição política no Amazonas |
| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |
| SO | Windows 11 / Git Bash |
| GitHub | https://github.com/PuraForja/bracc-etl |

---

## INFRAESTRUTURA

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |

---

## STATUS NEO4J (23/05/2026)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.671.726 | OK |
| Partner | 17.774.658 | OK |
| GovEmployee | 10.269.641 | OK |
| Expense | 3.836.389 | OK |
| MunicipalFinance | 3.469.721 | OK |
| Person | 2.780.851 | OK |
| Health | 612.561 | OK |
| TaxWaiver | 291.799 | OK |
| GovTravel | 260.000 | OK |
| GovCardExpense | 131.950 | OK |
| GlobalPEP | 117.910 | OK |
| Amendment | 101.801 | OK |
| Contract | 64.121 | OK |
| Fund | 41.107 | OK |
| Election | 33.602 | OK — TSE 2002-2024 completo |
| Sanction | 24.077 | OK |
| InternationalSanction | 9.707 | OK |
| SAME_AS (relações) | 543.079 | OK — criadas em lote 23/05 |
| **TOTAL** | **~80M** | OK |

---

## FIXES APLICADOS SESSÃO 21-23/05/2026

### graph_expand — reescrita adaptativa ✅
- `graph_expand_d1.cypher` — depth=1 limpo sem path variável
- `graph_expand_d2.cypher` — depth=2 adaptativo com ORDER BY prioridade + slice por node
- `node_degrees.cypher` — grau em lote (uma única query)
- `graph.py` router — supernode guard + buckets grau + orçamento 800 edges
- `graph.py` model — TruncatedNode + truncated_nodes no GraphResponse
- **Resultado:** 1s, 120 nodes — antes 32s+, 10.597 nodes, 504 timeout

**Buckets de grau:**
- ≤30: expande tudo
- 31-100: limita 15 vizinhos
- 101-1000: limita 5 vizinhos
- >1000: limita 2 vizinhos

### SAME_AS em lote ✅
- 543.079 relações Person→Partner criadas
- Critério: nome exato igual + `substring(cpf_sem_mask, 3, 6) == doc_digits`
- Filtro: mínimo 2 tokens no nome
- Index criado: `partner_doc_digits` em Partner.doc_digits (RANGE, ONLINE)

### SAME_AS manual Diego Roberto Afonso ✅
- 3 relações SAME_AS criadas manualmente
- Person TSE (58528356) → Person CPF (58716976) → Partner (40474788)
- Person TSE → Partner (direto)
- Resultado frontend: SOCIO_DE=4, Empresa=10, depth=2 em 1s

### PNCP checkpoint corrigido ✅
- Problema: .checkpoint marcava 23 meses como completos sem arquivos no disco
- Fix: removidas 1.380 entradas do checkpoint referentes aos gaps
- Status atual: 43/65 meses (66.2%) — download em andamento

---

## ENTITY RESOLUTION AM (19/05/2026)

- 211.883 arestas POSSIVEL_MESMO_INDIVIDUO criadas
- 2.417 pessoas únicas conectadas
- 77 órgãos cobertos
- 58 casos de conflito de interesse identificados
- 93 empresas com contratos públicos

---

## CASO VALIDADO — DIEGO ROBERTO AFONSO

- CPF: 784.440.632-15
- Element ID Person CPF: `4:91a9add5-04eb-4574-a38d-fd9437d62144:58716976`
- Element ID Person TSE: `4:91a9add5-04eb-4574-a38d-fd9437d62144:58528356`
- Element ID Partner: `4:91a9add5-04eb-4574-a38d-fd9437d62144:40474788`
- Servidor: SUHAB + SECT (dupla lotação AM)
- Empresas (4): DRA Derivados Petróleo, DH Lojas Conveniências, Gelabrea Gelo, ID Vestuário
- Conflito confirmado: DRA forneceu R$67.386 para Adail Filho e Sidney Leite
- **Grafo depth=2:** SOCIO_DE=4, Empresa=10 ✅

---

## CASO AMOM MANDEL LINS FILHO

- CPF: 072.847.254-60
- 4 nodes separados — deduplicação pendente
- Emendas: ~R$84M (deputado federal AM 2022)
- Padrasto: Mário Coelho de Mello (TCE-AM)

---

## PENDENTES TÉCNICOS

```
[ ] Backup Neo4j — URGENTE (último: 09/05 — 14 dias)
[ ] PNCP — completar gaps (43/65) e importar quando 100%
[ ] SAME_AS Person→Person entre fontes (TSE vs transparência)
[ ] POSSIVEL_MESMO_INDIVIDUO + TEM_REMUNERACAO — adicionar no frontend
[ ] Deduplicação automática CPF no orchestrator
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] Fix sessão única — senado_cpis, cnpj, etc.
[ ] Amom Mandel — 4 nodes separados
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
[ ] CNES download_cnes_am.py + pipeline
[ ] DOE-AM via OCR portarias CPF parcial
[ ] Relatório exportável casos conflito de interesse
```

---

## SETUP OBRIGATÓRIO — NOVA INSTALAÇÃO

Ver docs/SETUP_INDICES.md

```bash
cd ~/Downloads/br-acc-novo && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CREATE FULLTEXT INDEX entity_search FOR (n:Person|Partner|Company|Health|Contract|Amendment|GovEmployee|Election|Sanction|GlobalPEP|InternationalSanction|Expense|GovTravel|GovCardExpense|TaxWaiver|Fund|Inquiry|InquiryRequirement|MunicipalGazetteAct) ON EACH [n.name, n.razao_social, n.cpf, n.cnpj, n.doc_partial, n.doc_raw, n.object, n.nm_candidato, n.emp_id, n.orgao]" && echo "OK"
```

---

## ORQUESTRADOR

```bash
bash ~/Downloads/br-acc-novo/orchestrator.sh
bash ~/Downloads/br-acc-novo/orchestrator.sh --amazonas
MODO_TESTE=Y bash ~/Downloads/br-acc-novo/orchestrator.sh --force tse
```

---

## PNCP

```bash
# Monitorar
python3 -c "import os; expected=[f'pncp_{y}{m:02d}.json' for y in range(2021,2027) for m in range(1,13) if (y,m)<=(2026,5)]; path=os.path.expanduser('~/Downloads/br-acc-novo/data/pncp/'); downloaded=[f for f in expected if os.path.exists(os.path.join(path,f))]; missing=[f.replace('pncp_','').replace('.json','') for f in expected if f not in downloaded]; print(f'Baixados: {len(downloaded)}/{len(expected)} ({len(downloaded)/len(expected)*100:.1f}%) | Gaps: {missing}')"

# Relançar
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run python scripts/download_pncp.py --output-dir ../data/pncp 2>&1
```

---

## COMANDOS ÚTEIS

```bash
# Backup Neo4j
MSYS_NO_PATHCONV=1 docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo "OK"

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"

# Busca fulltext
cd ~/Downloads/br-acc-novo && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL db.index.fulltext.queryNodes('entity_search', 'NOME') YIELD node, score RETURN labels(node)[0], node.name, node.cpf, score ORDER BY score DESC LIMIT 10" && echo "OK"

# Testar API grafo
curl -s "http://localhost:8000/api/v1/graph/ELEMENT_ID?depth=2" | python3 -c "import sys,json; d=json.load(sys.stdin); print('nodes:', len(d.get('nodes',[])), 'edges:', len(d.get('edges',[])), 'truncated:', len(d.get('truncated_nodes',[])))" && echo "OK"
```

---

## HISTÓRICO

| Data | O que foi feito |
|---|---|
| 08-09/05 | camara 3.836M expenses + loader sessão única 1800x |
| 12-13/05 | transparencia_am download 6857 CSVs + catálogo v5 |
| 15-17/05 | transparencia_am 10.269M GovEmployee + entity resolution |
| 17-19/05 | POSSIVEL_MESMO_INDIVIDUO 211k arestas + 58 conflitos + Diego Afonso |
| 21/05 | TSE completo 2002-2024 + fulltext index + graph_expand + Amom/Diego validados |
| 21-23/05 | graph_expand adaptativo 1s + SAME_AS 543k em lote + PNCP checkpoint fix |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG.md
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] Verificar PNCP rodando
[ ] Neo4j totais
[ ] Fazer backup Neo4j (URGENTE)
[ ] Gerar v34 ao final
```

---

v33 — 23/05/2026
graph_expand adaptativo: 32s→1s, depth=2 funcional
SAME_AS em lote: 543.079 Person→Partner
PNCP: 43/65 meses (66.2%)
PRÓXIMO: backup + PNCP 100% + importar PNCP + SAME_AS Person→Person
