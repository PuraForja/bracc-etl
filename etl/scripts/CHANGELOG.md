
## [03/05/2026] - Refatoração: Centralização de Downloads
- **Decisão Técnica**: Remover lógicas de download redundantes dos scripts individuais[cite: 1, 2].
- **Ação**: Atualizar todos os scripts `download_*.py` para utilizarem exclusivamente as funções nativas de `_download_utils.py`[cite: 2, 8].
- **Objetivo**: Garantir segurança (ZIP bombs), suporte a retomada de download e validação padronizada de CSVs em um único local[cite: 2, 7].
- **Scripts Pendentes**:
  - download_bcb.py*
  - download_caged.py*
  - download_camara.py*
  - download_camara_inquiries.py*
  - download_ceaf.py*
  - download_cepim.py
  - download_cnpj.py*
  - download_cnpj_bq.py*
  - download_cpgf.py*
  - download_cvm.py*
  - download_cvm_funds.py*
  - download_datajud.py*
  - download_dou.py*
  - download_eu_sanctions.py*
  - download_holdings.py*
  - download_icij.py*
  - download_leniency.py*
  - download_mides.py*
  - download_ofac.py*
  - download_opensanctions.py*
  - download_pep.py
  - download_pep_cgu.py*
  - download_pncp.py*
  - download_querido_diario.py*
  - download_renuncias.py*
  - download_sanctions.py*
  - download_senado.py*
  - download_senado_cpi_archive.py*
  - download_senado_cpis.py*
  - download_senado_parlamentares.py*
  - download_siconfi.py*
  - download_siop.py*
  - download_stf.py*
  - download_tesouro_emendas.py
  - download_transparencia.py*
  - download_tse.py*
  - download_tse_bens.py*
  - download_tse_filiados.py*
  - download_un_sanctions.py*
  - download_viagens.py*
  - download_world_bank.py*


---

## 2026-05-08 — Fix crítico: sessão única por chunk — loader.py + camara.py

### [08/05/2026] — loader.py + camara.py — fix crítico de performance ✅

**Problema:** Qualquer pipeline com múltiplas chamadas ao loader por chunk abria
uma conexão Neo4j nova por chamada. Overhead de ~4s por conexão.
camara.py fazia ~64 conexões por chunk → 4 minutos por chunk de 5000 linhas.

**Solução:** Adicionado parâmetro session=None em todos os métodos do loader.
Novo método open_session(). No camara.py: todo o bloco de load do chunk
envolvido em "with loader.open_session() as session:".

**Resultado:** 64 conexões → 1 por chunk. 4min 36s → 175ms. 1800x mais rápido.

**Commit:** 250d548

---

### ⚠️ ORIENTAÇÃO OBRIGATÓRIA — LEIA ANTES DE TOCAR EM QUALQUER PIPELINE

**REGRA: qualquer pipeline com 3+ chamadas ao loader por chunk DEVE usar sessão única.**

CORRETO:
    with loader.open_session() as session:
        loader.load_nodes("Label", rows, key_field="id", session=session)
        loader.load_relationships(..., session=session)
        loader.run_query_with_retry(query, rows, session=session)

ERRADO:
    loader.load_nodes("Label", rows, key_field="id")   # abre conexão nova por chamada
    loader.load_relationships(...)                      # outra conexão
    loader.run_query_with_retry(query, rows)            # outra conexão

**Pipelines pendentes do fix (por impacto):**
    [ ] senado_cpis.py      15 chamadas — URGENTE
    [ ] cnpj.py             14 chamadas — URGENTE
    [ ] camara_inquiries.py  9 chamadas — URGENTE
    [ ] mides.py             9 chamadas — URGENTE
    [ ] transferegov.py      9 chamadas — URGENTE
    [ ] transparencia.py     9 chamadas — URGENTE
    [ ] tse.py               9 chamadas — URGENTE
    [ ] senado.py            6 chamadas — ALTO
    [ ] tcu.py               5 chamadas — ALTO
    [ ] datajud.py           5 chamadas — ALTO
    [ ] ibama.py             4 chamadas — ALTO
    [ ] icij.py              4 chamadas — ALTO
    [ ] tse_filiados.py      4 chamadas — ALTO
    [ ] bcb/ceaf/cepim/cpgf/datasus/siconfi/siop/pncp/sanctions — 3 chamadas

**Verificar quais ainda não têm o fix:**
    grep -L "open_session" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/*.py

