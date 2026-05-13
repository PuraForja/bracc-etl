# CHANGELOG TÉCNICO — Alterações no Código Fonte
> Este arquivo registra TODAS as alterações feitas nos arquivos do projeto.
> Qualquer IA ou desenvolvedor deve ler este arquivo antes de continuar o trabalho.
> Atualizar sempre que fizer qualquer alteração no código.

---

## FORMATO DE ENTRADA

```
### [DATA] — [ARQUIVO] — [TIPO: fix/feat/refactor]
**Problema:** O que estava errado ou faltando
**Solução:** O que foi feito
**Comando:** (se aplicável)
**Testado:** sim/não/parcial
```

---

## COMO IDENTIFICAR ONDE PAROU — EXECUTE SEMPRE AO INICIAR

```bash
# 1. Docker rodando?
docker ps | grep neo4j
# 2. Se não: subir
cd ~/Downloads/br-acc-novo && docker compose up -d
# 3. Estado do banco
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"
# 4. Últimas importações
tail -20 ~/Downloads/br-acc-novo/pipeline_imports.log | grep -v "contratacoes\|HTTP Request\|WARNING Network"
# 5. PNCP rodando?
ps aux | grep pncp | grep -v grep
# 6. Transparência AM rodando?
ps aux | grep transparencia_am | grep -v grep
# 7. Progresso PNCP
tail -3 ~/Downloads/br-acc-novo/download_pncp.log
# 8. O que falta
cat ~/Downloads/br-acc-novo/docs/CHANGELOG.md | grep "\[ \]"
```

---

## 2026-04-30 — Scripts de download

### [30/04/2026] — download_cepim.py — workaround ✅
**Problema:** Arquivo do dia atual não existe → 403.
**Solução:** `--date $(date -d "yesterday" +%Y%m%d)`
**Pendente:** fallback automático D-1 no código.

### [30/04/2026] — download_bcb.py — workaround ✅ (depois reescrito em 04/05)
**Problema:** URL antiga retorna 400.
**Workaround:** Download manual via API Olinda inline.
**Resultado:** 16.394 penalidades em data/bcb/penalidades.csv

---

## 2026-05-01 — run_query_with_retry + batch_size=1_000

### [01/05/2026] — 12 pipelines — fix ✅ COMMITADO (commit fb14cba)

**Problema 1:** `loader.run_query()` mandava todas as relações de uma vez → OOM.
**Solução:** `loader.run_query_with_retry()` — batches de 500 com retry.
**Arquivos:**
```
senado.py, camara.py, transparencia.py, tse.py, sanctions.py,
cvm.py, ibama.py, inep.py, tcu.py, tesouro_emendas.py,
transferegov.py, cnpj.py
```

**Problema 2:** batch_size padrão 10.000 → OOM antes das relações.
**Solução:** batch_size=1_000 (depois reduzido para 500 em 02/05).
**Arquivos:** senado.py, camara.py, transparencia.py, tse.py, siop.py, opensanctions.py

---

## 2026-05-02 — Neo4j índice MunicipalFinance + batch_size 500

### [02/05/2026] — Neo4j índice MunicipalFinance — fix crítico ✅
**Problema:** siconfi travava no load — 42 minutos para 10k registros.
Causa: campo `finance_id` sem índice → full scan em cada MERGE.
**Solução:**
```bash
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "CREATE INDEX finance_id IF NOT EXISTS FOR (n:MunicipalFinance) ON (n.finance_id)"
```
**Lição:** Sempre verificar índices antes de importar pipeline grande.
**Testado:** ✅ siconfi importado com sucesso após criação do índice

### [02/05/2026] — 7 pipelines — batch_size 1_000→500 — fix ✅ CONFIRMADO FUNCIONAL
**Problema:** batch_size=1_000 ainda causava morte silenciosa em pipelines grandes.
**Solução:** Reduzir para 500.
**Arquivos:**
```
senado.py, camara.py, transparencia.py, tse.py, siop.py,
opensanctions.py, siconfi.py
```
**Testado:** ✅ sanctions+siconfi+icij+senado importados com sucesso

---

## 2026-05-03 — Refatoração: Centralização de Downloads

### [03/05/2026] — _download_utils.py — decisão técnica ✅
**Decisão:** Remover lógicas de download redundantes dos scripts individuais.
**Ação:** Atualizar todos os scripts `download_*.py` para utilizarem exclusivamente
as funções nativas de `_download_utils.py`.
**Objetivo:** Garantir segurança (ZIP bombs), suporte a retomada de download
e validação padronizada de CSVs em um único local.

**Scripts pendentes de migração:**
```
download_bcb.py, download_caged.py, download_camara.py,
download_camara_inquiries.py, download_ceaf.py, download_cepim.py,
download_cnpj.py, download_cnpj_bq.py, download_cpgf.py,
download_cvm.py, download_cvm_funds.py, download_datajud.py,
download_dou.py, download_eu_sanctions.py, download_holdings.py,
download_icij.py, download_leniency.py, download_mides.py,
download_ofac.py, download_opensanctions.py, download_pep.py,
download_pep_cgu.py, download_pncp.py, download_querido_diario.py,
download_renuncias.py, download_sanctions.py, download_senado.py,
download_senado_cpi_archive.py, download_senado_cpis.py,
download_senado_parlamentares.py, download_siconfi.py, download_siop.py,
download_stf.py, download_tesouro_emendas.py, download_transparencia.py,
download_tse.py, download_tse_bens.py, download_tse_filiados.py,
download_un_sanctions.py, download_viagens.py, download_world_bank.py
```

---

## 2026-05-04 — camara.py reescrita + docker heap + bcb + cepim

### [04/05/2026] — camara.py — refactor ✅ COMMITADO
**Problema 1 — iterrows():** Pipeline morria silenciosamente após ~35 minutos.
Causa: `for _, row in self._raw.iterrows()` em 5.1M linhas criava objeto Python por linha.
**Problema 2 — pd.concat de 1.7GB:** extract() carregava 18 CSVs de uma vez → OOM.
**Problema 3 — apply(sha256) residual:** apply() em 265k linhas suficiente para matar.
**Solução (3 patches):**
- Patch 1: iterrows() → vetorização pandas
- Patch 2: extract()+transform()+load() → run() streaming por CSV
- Patch 3: apply() restantes → operações nativas vetorizadas pandas
**Resultado:** 265k linhas em 8 min sem crash. apply(sha256) eliminado.
**Lição:** Qualquer `apply()` em 200k+ linhas mata o processo. Usar APENAS pandas/numpy nativos.
**Testado:** ✅ Commitado

### [04/05/2026] — docker-compose.yml — heap Neo4j aumentado — fix ✅
**Problema:** Neo4j com heap padrão 1GB — insuficiente para pipelines grandes.
**Solução:**
```
NEO4J_server_memory_heap_initial__size: 4G
NEO4J_server_memory_heap_max__size: 16G
NEO4J_server_memory_pagecache__size: 4G
NEO4J_dbms_transaction_timeout: 4G
```
**Testado:** ✅ Commitado

### [04/05/2026] — download_bcb.py — reescrito API Olinda — fix ✅ COMMITADO
**Problema:** URL antiga retornava 400 — endpoint desativado.
**Solução:** Reescrito para usar API Olinda com paginação automática.
Nova URL: `https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador`
**Resultado:** 16.395 penalidades salvas em `data/bcb/penalidades.csv`
**Testado:** ✅ Commitado

### [04/05/2026] — download_cepim.py + download_pep_cgu.py — referer — fix ✅
**Problema:** Requests sem header Referer retornavam 403.
**Solução:** Adicionado `referer` no `download_file()` de ambos os scripts.
**Testado:** ✅ Commitado

---

## 2026-05-05 — Backup + auditoria Neo4j + catálogo

### [05/05/2026] — Neo4j backup — feat ✅
**Backup concluído:** 10.2GB salvo em `C:\Users\Rolim\Downloads\neo4j-backup-20260505.tar.gz`
**Horário:** 23:41
**Comando:**
```powershell
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:\Users\Rolim\Downloads:/backup alpine tar czf /backup/neo4j-backup-20260505.tar.gz /data
```
**Testado:** ✅ arquivo verificado (10.245.169.415 bytes)

### [05/05/2026] — datasus — importação ✅
**Resultado:** 612.561 nodes Health no Neo4j. Horário: 20:30–20:38.
**Obs:** Não constava no MASTER v21 — descoberto na auditoria.
**Testado:** ✅

### [05/05/2026] — Neo4j auditoria — estado real verificado ✅
```
Company              40.636.929
Partner              17.774.658
MunicipalFinance      3.469.721
Person                2.625.042
Health                  612.561
Expense                 494.537
TaxWaiver               291.799
GovTravel               260.000
GovCardExpense          131.950
GlobalPEP               117.910
Amendment               101.738
Contract                 64.121
Fund                     41.107
Election                 33.602
Sanction                 24.077
InternationalSanction     8.435
OffshoreOfficer           6.575
OffshoreEntity            4.820
Expulsion                 4.074
BarredNGO                 3.572
CVMProceeding               537
LeniencyAgreement           115
Inquiry/CPI/etc             399
MunicipalGazetteAct          10
TOTAL                ~87 milhões
```

### [05/05/2026] — docs/catalogo_fontes_bracc_v2.docx — feat ✅
Catálogo consolidado BRACC-ETL + Brazil-Visible com dados reais do Neo4j.

---

## 2026-05-07 — orchestrator.sh criado + MASTER v22

### [07/05/2026] — orchestrator.sh v1 — feat ✅
Script bash que orquestra download + importação de todas as fontes em sequência.
- Docker automático + aguarda Neo4j healthy
- PNCP em background com reinício automático
- SKIP list, Ctrl+C seguro, beep, resumo final
**Testado:** ✅ bcb passou download + importação

### [07/05/2026] — orchestrator.sh v3 — feat ✅
- sync_neo4j_to_installed(): lê Neo4j antes da fila, pula fontes com nodes>0
- Validação final com query direta ao banco
- Download com verificação de arquivo
- mark_imported sem duplicatas
- needs_update: compara mtime dados vs .installed
- --force corrigido para processar só a fonte especificada
**Testado:** ✅ world_bank baixou e importou 1272 nodes com --force

### [07/05/2026] — download_world_bank.py — fix ✅
**Problema:** URLs legadas mortas (404/403).
**Solução:** Reescrito para usar OpenSanctions como fonte.
**Resultado:** 1272 linhas baixadas, 1272 InternationalSanction nodes.

### [07/05/2026] — world_bank.py (pipeline) — fix ✅
**Problema:** Pipeline esperava colunas do formato legado.
**Solução:** Transform reescrito para formato OpenSanctions.

### [07/05/2026] — download_cnpj.py — fix ✅
**Problema:** `_check_nextcloud_token()` retornava falso positivo.
**Solução:** `return True` no início da função.
**Identificado por:** colega crepedequeijo

### [07/05/2026] — DESCOBERTA: scripts de download ausentes
bndes, ibama, inep, pgfn, tcu, comprasnet, transferegov — só pipeline, sem download.

---

## 2026-05-08 — Fix crítico sessão única + índices Neo4j + camara debug

### [08/05/2026] — Neo4j índices Expense/Person/Company/Health — fix crítico ✅
**Problema:** camara.py travava no L1 por 5+ minutos para 3.773 linhas.
Causa: expense_id sem índice → full scan em 87M nodes por MERGE.
**Solução:**
```bash
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "
CREATE INDEX expense_id IF NOT EXISTS FOR (n:Expense) ON (n.expense_id);
CREATE INDEX person_cpf IF NOT EXISTS FOR (n:Person) ON (n.cpf);
CREATE INDEX company_cnpj IF NOT EXISTS FOR (n:Company) ON (n.cnpj);
CREATE INDEX health_cnes IF NOT EXISTS FOR (n:Health) ON (n.cnes_code)"
```
**Lição:** Verificar índices ANTES de importar qualquer pipeline.
**Testado:** ✅ chunk 1 passou

### [08/05/2026] — loader.py + camara.py — fix crítico de performance ✅ (commit 250d548)
**Problema:** loader.py abria ~64 conexões Neo4j por chunk → 4 minutos por chunk.
Cada chamada a load_nodes/load_relationships/run_query_with_retry abria sessão nova (~4s overhead).
**Solução:** Adicionado parâmetro `session=None` em todos os métodos do loader.
Novo método `open_session()`. No camara.py: todo bloco de load envolvido em
`with loader.open_session() as session:`.
**Resultado:** 64 conexões → 1 por chunk. 4min 36s → 175ms. **1800x mais rápido.**
**Retrocompatível:** session=None mantém comportamento original nos outros pipelines.
**Testado:** ✅ test_camara.py — 2 chunks OK

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

## 2026-05-09 — Câmara concluída + backup + loader commitado

### [09/05/2026] — camara — importação completa ✅
**Resultado:** 3.793.960 Expense nodes no Neo4j.
**Duração:** ~3h50 (17:55 → 21:46).
**Comando usado:**
```bash
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run bracc-etl run --source camara --neo4j-password changeme --data-dir ~/Downloads/br-acc-novo/data 2>&1 | tee ~/Downloads/br-acc-novo/camara_debug.log
```
**Obs:** Rodar pipeline direto (não pelo orchestrator) para ver log em tempo real.

### [09/05/2026] — loader.py — commitado versão correta (commit 9aa5035)
**Problema:** curl sobrescreveu loader.py com versão antiga do GitHub durante sessão anterior.
**Regra adicionada:** NUNCA usar curl para sobrescrever loader.py — usar heredoc ou cat.

### [09/05/2026] — Neo4j backup — feat ✅
**Backup:** 9.9GB salvo em `neo4j-backup-20260509.tar.gz`
**Horário:** 00:09
**Comando:**
```bash
MSYS_NO_PATHCONV=1 docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-20260509.tar.gz /data
```

---

## 2026-05-10 — Orchestrator: barra de progresso + MODO_TESTE + watchdog

### [10/05/2026] — orchestrator.sh — barra de progresso por arquivo — feat ✅
**O que faz:** Mostra progresso real por arquivo CSV durante importação.
```
[████░░░░░░░░░░░░░░░░] 4/18 (22%) Ano-2012.csv
```
**Implementação:** Pipeline roda em background gravando em PROGRESS_FILE.
Spinner no processo principal lê o arquivo e imprime linha nova por arquivo concluído.
**Obs:** Git Bash não suporta \r em scripts — linha nova por evento é o máximo possível.

### [10/05/2026] — orchestrator.sh — MODO_TESTE — feat ✅
**O que faz:** `MODO_TESTE=Y` pula leitura Neo4j (~60s), uv sync (~10s) e PNCP.
**Uso:** `MODO_TESTE=Y bash ~/Downloads/br-acc-novo/orchestrator.sh --force camara`

### [10/05/2026] — orchestrator.sh — watchdog — feat ✅
**O que faz:** Se pipeline ficar 3 minutos sem nova linha no log, imprime aviso:
`⚠️ [fonte] sem atividade há Xmin — pode ter travado`

---

## 2026-05-12 — Senado confirmado + TCE-AM + Transparência AM + features

### [12/05/2026] — senado — importação confirmada OK ✅
**Resultado:** 272.429 Expense nodes confirmados no Neo4j.
**Status:** removido da lista de pendentes.

### [12/05/2026] — TCE-AM — análise e descarte
**Análise:** Portal TCE-AM usa JSF (JavaServer Faces) sem API pública acessível.
**Decisão:** Descartado por ora — tecnologia incompatível com scraping automatizado.

### [12/05/2026] — Portal Transparência AM — mapeamento ✅
**Descoberta:** Portal usa API via `admin-ajax.php` com 80 órgãos mapeados.
**Script criado:** `etl/scripts/download_transparencia_am.py`
**Status download:** ~408 CSVs baixados, em andamento.
**Bug pendente:** No Windows, `partial.rename(dest)` falha com `FileExistsError`.

### [12/05/2026] — _download_utils.py — bug Windows rename — fix PENDENTE ⚠️
**Problema:** `partial.rename(dest)` falha com `FileExistsError` no Windows se dest já existe.
**Correção a aplicar:**
```python
# Substituir as duas ocorrências de:
partial.rename(dest)
# Por:
if dest.exists():
    dest.unlink()
partial.rename(dest)
```
**Arquivo:** `etl/scripts/_download_utils.py`
**Testado:** NÃO — pendente

### [12/05/2026] — orchestrator.sh — seção Amazonas — feat ✅
**O que faz:** Fila separada para fontes AM. transparencia_am roda em background
com reinício automático (log: transparencia_am.log).

### [12/05/2026] — docs/PENDENCIAS_FEATURES.md — criado ✅
**Conteúdo:**
- FEATURE 1: Orquestrador multi-estado via sources.yaml
- FEATURE 2: Flag --check-links para testar endpoints sem baixar

---

## PENDÊNCIAS ATUAIS (13/05/2026)

```
[ ] _download_utils.py — fix rename Windows (FileExistsError) — URGENTE
[ ] transparencia_am — aguardar download completo e criar pipeline importação
[ ] PNCP — aguardar 100% e importar (~62% em abr/2024)
[ ] Fix sessão única — aplicar nos pipelines pendentes (ver lista acima)
[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] Backup Neo4j — fazer nesta sessão (último: 09/05 9.9GB)
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
[ ] link_persons.cypher — script ausente (warning no camara e senado)
[ ] PENDENCIAS_FEATURES.md — sources.yaml multi-estado + --check-links
[ ] Catálogo fontes — mover lista órgãos AM do download_transparencia_am.py para catalogo_fontes_bracc
[ ] download_cepim.py — fallback automático D-1
[ ] Nginx timeout — incorporar no Dockerfile
```

---

## VERIFICAÇÃO RÁPIDA

```bash
# Estado do banco
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Pipelines sem fix sessão única
grep -L "open_session" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/*.py

# Índices Neo4j
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "SHOW INDEXES YIELD name, labelsOrTypes, properties RETURN name, labelsOrTypes, properties"

# run_query sem retry (deve retornar VAZIO)
grep -r "loader\.run_query(" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak" | grep -v "run_query_with_retry"
```

---

*Criado em 01/05/2026*
*Consolidado em 13/05/2026 — unificado local + GitHub + sessões 08-12/05*
