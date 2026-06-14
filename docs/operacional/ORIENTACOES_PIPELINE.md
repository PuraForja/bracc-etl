# ORIENTAÇÕES OBRIGATÓRIAS — NOVOS PIPELINES
> Atualizado em 12/06/2026
> Toda regra foi alinhada com erros reais. Não ignore nenhuma.

---

## REGRA #1 — TODO NOVO PIPELINE DEVE SER REGISTRADO NO ORCHESTRATOR
Ao criar qualquer novo `download_FONTE.py` ou `pipelines/FONTE.py`, registrar em 4 lugares no `orchestrator.sh`:

### 1. LABEL_MAP
```bash
LABEL_MAP[nova_fonte]="LabelNeo4j"
```

### 2. TIMEOUT_MAP
```bash
TIMEOUT_MAP[nova_fonte]=600   # médias
TIMEOUT_MAP[nova_fonte]=1800  # pesadas (cnpj, tse, camara)
```

### 3. Fila correta
```bash
DEFAULT_QUEUE=(... nova_fonte ...)    # federal/nacional
AMAZONAS_QUEUE=(... nova_fonte ...)  # estadual AM
```

### 4. INCREMENTAL_SOURCES (se download incremental)
Fontes com API paginada ou download por período DEVEM estar em INCREMENTAL_SOURCES.
Sem isso o orchestrator pula o download se a pasta já tiver qualquer arquivo.
```bash
local INCREMENTAL_SOURCES=("transparencia_am" "tce_am" "servidores_federais" "comprasnet" "obras" "transferegov" "nova_fonte")
```

**Rolim não aceita rodar downloads diretamente pelo script — tudo passa pelo orchestrator.**
**Sem registro = tarefa incompleta.**

---

## REGRA #2 — AVALIAÇÃO DE MEMÓRIA OBRIGATÓRIA
Antes de criar qualquer pipeline:
1. **Tamanho estimado do CSV** — se > 500k linhas: OBRIGATÓRIO usar chunked
2. **Nunca usar `pd.read_csv` sem `chunksize`** em arquivos grandes
3. **`batch_size` do Neo4jBatchLoader** — padrão 500, reduzir para 200 em pipelines pesados

---

## REGRA #3 — PADRÃO OBRIGATÓRIO PARA CSV > 500K LINHAS
```python
# CORRETO — chunked
for chunk in pd.read_csv(path, encoding="latin-1", dtype=str, chunksize=50_000):
    rows = []
    for _, row in chunk.iterrows():
        rows.append({...})
    if rows:
        loader.load_nodes("Label", rows, key_field="id")

# ERRADO — carrega tudo em memória
df = pd.read_csv(path, encoding="latin-1", dtype=str)
rows = [...]
loader.load_nodes("Label", rows, key_field="id")
```

---

## REGRA #4 — ÍNDICE ANTES DE IMPORTAR
Todo campo usado em MATCH/MERGE DEVE ter índice criado ANTES da importação.
Sem índice = full scan = trava com volume alto.
```bash
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme \
  "CREATE INDEX nome_indice IF NOT EXISTS FOR (n:Label) ON (n.campo)" && echo "OK"
```
Após criar, adicionar em `docs/operacional/SETUP_INDICES.md`.

---

## REGRA #5 — PADRÃO DE DOWNLOAD POR TIPO DE FONTE

### Arquivo bulk (ZIP/CSV único)
Usar `_download_utils.download_file` + `safe_extract_zip`:
- Portal redireciona (302) para o arquivo real — seguir o redirect
- Não dividir por ano se o portal já entrega tudo em um arquivo único
- Exemplos: transferegov, cnpj, tse_bens

### API REST paginada
Usar `httpx.Client` direto com retry manual — **NÃO usar `_download_utils`**:
- Implementar checkpoint (`.checkpoint`) para retomada após erro
- Testar o volume real antes de definir tamanho da janela de data
- Registrar em `INCREMENTAL_SOURCES` no orchestrator
- Exemplos: comprasnet (janela 2 dias), pncp (janela 10 dias), obras (por página)
- Referência de padrão: `etl/scripts/download_tce_am.py`

### Incremental por período (ano/mês)
Iterar períodos, pular arquivos já existentes com `skip_existing`:
- Flag `--historico` para primeira execução completa quando aplicável
- Registrar em `INCREMENTAL_SOURCES` no orchestrator
- Exemplos: servidores_federais, transparencia_am

### Antes de escrever qualquer download_FONTE.py
1. Testar a URL com `curl -sI URL`
2. Se redirecionar (302): testar a URL final
3. Se API: ler o swagger para descobrir endpoints reais
4. Testar um endpoint real com dados antes de codar
5. Só então escrever o script

---

## REGRA #6 — WCC APÓS IMPORTAÇÃO COM SAME_AS
Se o pipeline cria relações SAME_AS, re-rodar WCC obrigatório:
```bash
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme \
  "CALL gds.graph.drop('identity-graph') YIELD graphName" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme \
  "CALL gds.graph.project('identity-graph', ['Person','Partner','GlobalPEP','OffshoreOfficer'], {SAME_AS: {orientation: 'UNDIRECTED'}}) YIELD graphName, nodeCount, relationshipCount" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme \
  "CALL gds.wcc.write('identity-graph', {writeProperty: 'community_id'}) YIELD componentCount, nodePropertiesWritten" && echo "OK"
```

---

## REGRA #7 — SESSÃO ÚNICA NO LOADER
```python
# CORRETO
with loader.open_session() as session:
    loader.load_nodes("Label", rows, key_field="id", session=session)
    loader.load_relationships(..., session=session)
```

---

## PIPELINES JÁ CORRIGIDOS PARA CHUNKED
| Pipeline | Data | Motivo |
|---|---|---|
| tse.py — doações | 02/06/2026 | 3.1M linhas travavam em memória |
| tse_bens.py | 03/06/2026 | 17.5M linhas |

## PIPELINES COM CORREÇÃO DE SESSÃO PENDENTE
- `camara.py`, `senado_cpis.py`, `camara_inquiries.py`, `mides.py`
- `transferegov.py`, `transparencia.py`, `tse.py`, `senado.py`
- `tcu.py`, `datajud.py`, `ibama.py`, `icij.py`, `tse_filiados.py`

---
*Atualizar este arquivo quando novos padrões forem alinhados com Rolim*
