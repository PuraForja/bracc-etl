# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v25
> Gerado em 09/05/2026 ~21h50
> Cole este arquivo ou use o PROMPT_INICIALIZACAO_IA.md no início de qualquer nova sessão.

---

## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO

1. Leia o CHANGELOG antes de qualquer correção de código
2. Leia o ORIENTACOES_IA.md para regras de comportamento
3. Após qualquer alteração de código: atualize o CHANGELOG e commite
4. Ao final de cada sessão: gere novo MASTER e commite
5. Sempre inclua data/hora nos logs
6. Avise quando a sessão estiver no limite — OBRIGATÓRIO
7. Nunca reescrever scripts com requests puro — sempre usar _download_utils.py
8. Confirme alterações antes de executar
9. Abrir arquivos grandes no Notepad — heredoc trava no Git Bash do Windows
10. Comandos longos na vertical travam o Git Bash — mandar em linha única
11. ⚠️ NUNCA usar curl para sobrescrever loader.py do GitHub — o repo pode estar desatualizado. Usar heredoc ou cat direto.

---

## ⚠️ ORIENTAÇÃO OBRIGATÓRIA — LEIA ANTES DE TOCAR EM QUALQUER PIPELINE

**REGRA: qualquer pipeline com 3+ chamadas ao loader por chunk DEVE usar sessão única.**

```python
# CORRETO
with loader.open_session() as session:
    loader.load_nodes("Label", rows, key_field="id", session=session)
    loader.load_relationships(..., session=session)
    loader.run_query_with_retry(query, rows, session=session)

# ERRADO — abre conexão nova por chamada (~4s overhead cada)
loader.load_nodes("Label", rows, key_field="id")
loader.load_relationships(...)
```

**Verificar pendentes:**
```bash
grep -L "open_session" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/*.py
```

**Pipelines pendentes do fix (por impacto):**
```
[ ] senado_cpis.py      15 chamadas
[ ] cnpj.py             14 chamadas
[ ] camara_inquiries.py  9 chamadas
[ ] mides.py             9 chamadas
[ ] transferegov.py      9 chamadas
[ ] transparencia.py     9 chamadas
[ ] tse.py               9 chamadas
[ ] senado.py            6 chamadas
[ ] tcu.py               5 chamadas
[ ] datajud.py           5 chamadas
[ ] ibama.py             4 chamadas
[ ] icij.py              4 chamadas
[ ] tse_filiados.py      4 chamadas
[ ] bcb/ceaf/cepim/cpgf/datasus/siconfi/siop/pncp/sanctions — 3 chamadas
```

---

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU

```bash
# 1. Docker
docker ps | grep neo4j
cd ~/Downloads/br-acc-novo && docker compose up -d
# 2. Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"
# 3. Log
tail -20 ~/Downloads/br-acc-novo/pipeline_imports.log | grep -v "contratacoes\|HTTP Request\|WARNING Network"
# 4. PNCP
tail -3 ~/Downloads/br-acc-novo/download_pncp.log
ps aux | grep pncp | grep -v grep
# 5. Se PNCP morreu, relançar
cd ~/Downloads/br-acc-novo && while true; do cd etl && source ~/.local/bin/env && uv run python scripts/download_pncp.py --output-dir ../data/pncp && cd ..; sleep 30; done >> download_pncp.log 2>&1 &
```

---

## PERFIL

| Campo | Valor |
|---|---|
| Nome | Alberto (Rolim) |
| Contexto | Oposição política no Amazonas |
| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |
| SO | Windows 11 / Git Bash |
| uv | ~/.local/bin/env |
| GitHub | https://github.com/PuraForja/bracc-etl |

---

## INFRAESTRUTURA

Subir: `cd ~/Downloads/br-acc-novo && docker compose up -d`

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |

---

## STATUS NEO4J (09/05/2026 ~21h50)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.670.009 | OK |
| Partner | 17.774.658 | OK |
| Expense | 3.793.960 | OK — câmara concluída 09/05 ~21h46 |
| MunicipalFinance | 3.469.721 | OK |
| Person | 2.626.942 | OK |
| Health | 612.561 | OK |
| TaxWaiver | 291.799 | OK |
| GovTravel | 260.000 | OK |
| GovCardExpense | 131.950 | OK |
| GlobalPEP | 117.910 | OK |
| Amendment | 101.801 | OK |
| Contract | 64.121 | OK |
| Fund | 41.107 | OK |
| Payment | 40.000 | OK |
| Election | 33.602 | OK |
| Sanction | 24.077 | OK |
| InternationalSanction | 9.707 | OK |
| OffshoreOfficer | 6.575 | OK |
| OffshoreEntity | 4.820 | OK |
| Expulsion | 4.074 | OK |
| BarredNGO | 3.572 | OK |
| CVMProceeding | 537 | OK |
| LeniencyAgreement | 115 | OK |
| Inquiry | 105 | OK |
| CPI | 105 | OK |
| InquiryRequirement | 102 | OK |
| InquirySession | 87 | OK |
| IngestionRun | 84 | OK |
| MunicipalGazetteAct | 10 | OK — parcial |
| SourceDocument | 3 | OK |
| User | 1 | OK |
| **TOTAL** | **~87M** | OK |

---

## STATUS DOWNLOADS (09/05/2026)

| Fonte | Download | Importação |
|---|---|---|
| cnpj | OK | OK |
| tse | OK | OK |
| viagens | OK | OK |
| transparencia | OK | OK |
| opensanctions | OK | OK |
| siop | OK | OK |
| camara | OK | ✅ OK — concluído 09/05 ~21h46 |
| datasus | OK | OK |
| tesouro_emendas | OK | OK |
| pncp | ~60%+ | AGUARDAR |
| senado | OK | PROBLEMA — investigar |
| world_bank | OK | OK |
| todos os outros | OK | OK |
| bndes, ibama, inep, pgfn, tcu, comprasnet, transferegov | SEM SCRIPT | — |

---

## FIX CRÍTICO 08/05/2026 — Sessão única por chunk

**Problema:** loader.py abria ~64 conexões Neo4j por chunk → 4min por chunk.
**Solução:** open_session() reutiliza 1 conexão por chunk → 36ms por chunk. 1800x mais rápido.
**Commits:** 250d548 (loader+camara), 9aa5035 (loader correto), 2a97807 (orchestrator)
**Aplicado em:** camara.py ✅
**Pendente:** todos os outros pipelines com 3+ chamadas (ver lista acima)

---

## ORQUESTRADOR

```bash
# Fila completa
bash ~/Downloads/br-acc-novo/orchestrator.sh

# Força reimportação
bash ~/Downloads/br-acc-novo/orchestrator.sh --force camara

# Rodar pipeline direto com log visível (recomendado para debug)
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run bracc-etl run --source camara --neo4j-password changeme --data-dir ~/Downloads/br-acc-novo/data 2>&1 | tee ~/Downloads/br-acc-novo/camara_debug.log
```

Cache de importações em `.installed`. LABEL_MAP definido no `orchestrator.sh`.

---

## PENDENTES TÉCNICOS

```
[ ] senado — investigar erro na importação
[ ] PNCP — aguardar 100% e importar
[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] TCE-AM — criar pipeline do zero
[ ] Backup Neo4j — URGENTE (último: 05/05 10.2GB)
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
[ ] Fix sessão única — aplicar nos pipelines pendentes (ver lista acima)
[ ] Watchdog orchestrator — detectar morte silenciosa de pipelines
[ ] link_persons.cypher — script ausente (warning no camara)
```

---

## COMANDOS ÚTEIS

```bash
# Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data

# Verificar índices
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "SHOW INDEXES YIELD name, labelsOrTypes, properties RETURN name, labelsOrTypes, properties"

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main

# Pipeline direto com log visível
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run bracc-etl run --source FONTE --neo4j-password changeme --data-dir ~/Downloads/br-acc-novo/data 2>&1 | tee ~/Downloads/br-acc-novo/debug_FONTE.log
```

---

## HISTÓRICO

| Data | O que foi feito |
|---|---|
| 20-25/04 | Infraestrutura + CNPJ + patches |
| 26/04 | CNPJ completo + backup |
| 27-30/04 | Downloads massivos + CEPIM + BCB |
| 01-03/05 | run_query_with_retry + batch_size fixes |
| 04-05/05 | heap Neo4j 16GB + BCB API Olinda + siop+opensanctions |
| 06/05 | tse+transparencia+datasus importados |
| 07/05 | orchestrator v3 + tesouro_emendas + MASTER v23 |
| 08/05 | world_bank fix + CNPJ fix + camara refactor + loader execute_write + runner chunk_size 5k + test_camara.py + índices Neo4j + fix sessão única loader.py (1800x mais rápido) |
| 09/05 | camara importação completa 3.79M expenses + loader.py commitado correto + MASTER v25 |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG_TECNICO.md
[ ] docker ps | grep neo4j
[ ] Verificar PNCP rodando
[ ] Investigar senado
[ ] Aplicar fix sessão única nos pipelines pendentes
[ ] Fazer backup Neo4j (último: 05/05)
[ ] Gerar v26 ao final
```

---

v25 — 09/05/2026 ~21h50
CÂMARA: ✅ concluída — 3.79M expenses
PRÓXIMO: senado + backup + fix sessão única nos demais pipelines
