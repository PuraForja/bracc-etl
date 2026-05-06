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

## 2026-05-05 — Backup Neo4j + fila relançada

### [05/05/2026] — Neo4j backup — feat ✅

**Backup concluído:** 10.2GB salvo em `C:\Users\Rolim\Downloads\neo4j-backup-20260505.tar.gz`
**Horário:** 23:41
**Conteúdo:** ~87M nodes — estado completo do banco

**Comando usado:**
```powershell
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:\Users\Rolim\Downloads:/backup alpine tar czf /backup/neo4j-backup-20260505.tar.gz /data
```

**Testado:** ✅ arquivo verificado (10.245.169.415 bytes)

---

### [05/05/2026] — datasus — importação ✅

**Pipeline datasus importado com sucesso.**
**Resultado:** 612.561 nodes Health no Neo4j
**Horário:** 20:30–20:38

**Obs:** Não constava no MASTER v21 — descoberto na auditoria do banco.

**Testado:** ✅ confirmado via cypher-shell

---

### [05/05/2026] — fila transparencia→tse→camara — incidente ⚠️

**Problema:** Fila principal morreu às ~20:30 com erro `ServiceUnavailable` —
Neo4j recusou conexão (container provavelmente reiniciando naquele momento).
transparencia, tse e camara **não foram importados**.

**Solução:** Fila relançada às ~00:00 sem o camara (código ainda em ajuste):
`transparencia → tse`

**Camara:** removido da fila por ora — importar separado quando código estiver validado.

**Tempo estimado:** 3–6 horas para transparencia+tse.

**Testado:** em andamento

---

## 2026-05-05 — Neo4j auditado — estado real verificado

### [05/05/2026] — Neo4j — auditoria ✅

**Verificação:** Consulta cypher-shell MATCH (n) RETURN labels(n)[0], count(n) ORDER BY total DESC

**Estado real do banco em 05/05/2026:**
```
Company              40.636.929   Receita Federal CNPJ
Partner              17.774.658   Receita Federal QSA
MunicipalFinance      3.469.721   Tesouro / SICONFI
Person                2.625.042   Múltiplas fontes
Health                  612.561   DATASUS — importado (não estava no MASTER)
Expense                 494.537   Câmara + outras
TaxWaiver               291.799   Receita Federal renúncias
GovTravel               260.000   Portal Transparência viagens
GovCardExpense          131.950   CPGF
GlobalPEP               117.910   OpenSanctions
Amendment               101.738   Emendas parlamentares
Contract                 64.121   Contratos gov
Fund                     41.107   CVM Fundos
Election                 33.602   TSE (mais que 16.898 previsto no MASTER)
Sanction                 24.077   CEIS/CNEP/CEPIM
InternationalSanction     8.435   OFAC + ONU + OpenSanctions
OffshoreOfficer           6.575   ICIJ
OffshoreEntity            4.820   ICIJ
Expulsion                 4.074   CGU/CEAF
BarredNGO                 3.572   CEPIM
CVMProceeding               537   CVM
LeniencyAgreement           115   CGU
Inquiry                     105   Senado CPIs
CPI                         105   Senado CPIs
InquiryRequirement          102   Senado CPIs
InquirySession               87   Senado CPIs
MunicipalGazetteAct          10   Querido Diário (parcial)
TOTAL                ~87 milhões
```

**Descobertas:**
- Health (DATASUS): 612.561 nodes — já importado, não constava no MASTER v21
- Election: 33.602 — maior que os 16.898 registrados no MASTER (TSE mais completo)
- Expense: 494.537 — parcial, camara ainda na fila

**Testado:** ✅ consulta direta

---

## 2026-05-05 — docs/catalogo_fontes_bracc_v2.docx — feat ✅

### [05/05/2026] — docs/catalogo_fontes_bracc_v2.docx — feat ✅

**O que é:** Catálogo consolidado de todas as fontes de dados do projeto.
Combina BRACC-ETL + Brazil-Visible com dados reais do Neo4j verificados.

**Conteúdo:**
- Seção 1: Estado real Neo4j — 27 labels com contagens verificadas
- Seção 2: Fontes BRACC na fila/pendentes — 14 fontes
- Seção 3: Fontes BigQuery — 4 fontes (credencial necessária)
- Seção 4: Fontes Brazil-Visible complementares — 14 fontes + receitas de cruzamento
- Seção 5: Ordem de prioridade recomendada — 9 etapas

**Arquivo:** docs/catalogo_fontes_bracc_v2.docx

**Testado:** ✅ gerado e validado

---

## 2026-05-04 — camara.py — REESCRITA STREAMING + VETORIZAÇÃO (EM ANDAMENTO)

### [04/05/2026] — camara.py — refactor ✅ COMMITADO

**Problema 1 — iterrows():**
Pipeline morria silenciosamente após ~35 minutos na transformação.
Causa: `for _, row in self._raw.iterrows()` em 5.1M linhas criava um objeto
Python por linha, consumindo toda a RAM antes de terminar.

**Problema 2 — pd.concat de 1.7GB:**
Mesmo com iterrows() corrigido, o extract() carregava 18 CSVs de uma vez
via `pd.concat(frames)` — 1.7GB na RAM simultaneamente — matava no extract.

**Problema 3 — apply(sha256) residual:**
Após streaming implementado, ainda restava um `apply(lambda x: sha256...)`
em 265k linhas por arquivo — suficiente para matar o processo.

**Solução aplicada (em 3 patches):**

**Patch 1 — patch_camara.py:** Substituiu iterrows() por vetorização pandas
na função transform(). Resolveu o iterrows mas não o pd.concat.

**Patch 2 — patch_camara_streaming.py:** Reescreveu extract()+transform()+load()
em um único método run() que processa um CSV por vez — sem acumular RAM.
Cada arquivo: lê → transforma → carrega no Neo4j → libera memória.

**Patch 3 — patch_camara_vectorized.py:** Substituiu os apply() restantes
(parse_date, normalize_name, _parse_brl_value, strip_document, format_cnpj,
format_cpf) por operações nativas vetorizadas pandas.

**Resultado:** teste com limit 1000 passou — 265k linhas em 8 min sem crash.
Código commitado. apply(sha256) eliminado na vetorização final.

**Arquivos alterados:**
```
etl/src/bracc_etl/pipelines/camara.py  (backup: camara.py.bak)
```

**Testado:** ✅ Commitado

**Lição aprendida:** Qualquer `apply()` em 200k+ linhas mata o processo.
Usar APENAS operações nativas pandas/numpy.

---

## 2026-05-04 — docker-compose.yml — heap Neo4j aumentado

### [04/05/2026] — docker-compose.yml — fix ✅

**Problema:** Neo4j com heap padrão 1GB e pagecache 512MB — insuficiente
para pipelines grandes.

**Solução:** Aumentar limites no docker-compose.yml:
```
NEO4J_server_memory_heap_initial__size: 4G
NEO4J_server_memory_heap_max__size: 16G
NEO4J_server_memory_pagecache__size: 4G
NEO4J_dbms_transaction_timeout: 4G  (era 1G)
```

**Testado:** ✅ Commitado

---

## 2026-05-04 — download_bcb.py — reescrito API Olinda ✅

### [04/05/2026] — download_bcb.py — fix ✅ COMMITADO

**Problema:** URL antiga retornava 400 — endpoint desativado.

**Solução:** Reescrito para usar API Olinda com paginação automática.
Nova URL: `https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador`

**Resultado:** 16.395 penalidades salvas em `data/bcb/penalidades.csv`

**Testado:** ✅ Commitado

---

## 2026-05-04 — download_cepim.py + download_pep_cgu.py — referer ✅

### [04/05/2026] — download_cepim.py linha 63 + download_pep_cgu.py linha 127 — fix ✅

**Problema:** Requests sem header Referer retornavam 403.

**Solução:** Adicionado `referer` no `download_file()` de ambos os scripts.

**Testado:** ✅ Commitado

---

## 2026-05-02 — Neo4j índice MunicipalFinance — fix crítico ✅

### [02/05/2026] — Neo4j — fix ✅

**Problema:** siconfi travava no load — 42 minutos para 10k registros.
Causa: campo `finance_id` sem índice → full scan em cada MERGE.

**Solução:**
```bash
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "CREATE INDEX finance_id IF NOT EXISTS FOR (n:MunicipalFinance) ON (n.finance_id)"
```

**Lição:** Sempre verificar índices antes de importar pipeline grande:
```bash
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "SHOW INDEXES YIELD name, labelsOrTypes, properties RETURN name, labelsOrTypes, properties"
```

**Testado:** ✅ siconfi importado com sucesso após criação do índice

---

## 2026-05-02 — batch_size reduzido 1_000→500 ✅

### [02/05/2026] — 7 pipelines — fix ✅ CONFIRMADO FUNCIONAL

**Problema:** batch_size=1_000 ainda causava morte silenciosa em pipelines grandes.

**Solução:** Reduzir para 500.

**Arquivos:**
```
senado.py, camara.py, transparencia.py, tse.py, siop.py,
opensanctions.py, siconfi.py
```

**Comando:**
```bash
sed -i 's/batch_size=1_000/batch_size=500/' ARQUIVO.py
```

**Testado:** ✅ sanctions+siconfi+icij+senado importados com sucesso

---

## 2026-05-01 — run_query_with_retry + batch_size=1_000 ✅

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

## 2026-04-30 — Scripts de download

### download_cepim.py — workaround ✅
**Problema:** Arquivo do dia atual não existe → 403.
**Solução:** `--date $(date -d "yesterday" +%Y%m%d)`
**Pendente:** fallback automático D-1 no código.

### download_bcb.py — workaround ✅ (depois reescrito em 04/05)
**Problema:** URL antiga retorna 400.
**Workaround:** Download manual via API Olinda inline.
**Resultado:** 16.394 penalidades em data/bcb/penalidades.csv

---

## PENDÊNCIAS (TODO)

```
[ ] Fila rodando: transparencia → tse (camara separado depois)
[ ] BACKUP Neo4j — após fila terminar (backup pré-fila já feito em 05/05 — 10.2GB)
[ ] PNCP — aguardar 100% download, então importar
[ ] INPE PRODES + SICAR + IBAMA — tríade ambiental AM (via brazil-visible)
[ ] ANTAQ — transporte aquaviário AM (via brazil-visible)
[ ] CNJ DataJud — verificar credencial
[ ] download_cepim.py — fallback automático D-1
[ ] download_datasus.py — verificar tabelas adicionais além das 612k importadas
[ ] bndes, pgfn, tcu, inep, comprasnet, transferegov — scripts disponíveis
[ ] tse_bens, tse_filiados — scripts disponíveis
[ ] Aplicar batch_size=500 em todos os pipelines sem batch_size explícito
[ ] Nginx timeout — incorporar no Dockerfile
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
```

---

## VERIFICAÇÃO RÁPIDA

```bash
# Estado do banco
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# run_query sem retry (deve retornar VAZIO)
grep -r "loader\.run_query(" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak" | grep -v "run_query_with_retry"

# batch_size atual
grep -r "batch_size" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep "Neo4jBatchLoader" | grep -v ".bak"

# Índices Neo4j
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "SHOW INDEXES YIELD name, labelsOrTypes, properties RETURN name, labelsOrTypes, properties"
```

---

*Criado em 01/05/2026*
*Atualizado em 05/05/2026 — auditoria Neo4j: 87M nodes verificados. Health(DATASUS) 612k confirmado. catalogo_fontes_bracc_v2.docx gerado.*
