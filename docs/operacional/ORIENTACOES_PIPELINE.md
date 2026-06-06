# ORIENTAÇÕES OBRIGATÓRIAS — NOVOS PIPELINES
> Atualizado em 04/06/2026
> Toda regra foi alinhada com erros reais. Não ignore nenhuma.

---

## REGRA #1 — TODO NOVO PIPELINE DEVE SER REGISTRADO NO ORCHESTRATOR

Ao criar qualquer novo pipeline `pipelines/FONTE.py`, registrar em 3 lugares no `orchestrator.sh`:

### 1. LABEL_MAP — mapeia fonte para label Neo4j
```bash
LABEL_MAP[nova_fonte]="LabelNeo4j"
```

### 2. TIMEOUT_MAP — timeout em segundos (opcional, padrão 180)
```bash
TIMEOUT_MAP[nova_fonte]=600   # padrão para fontes médias
TIMEOUT_MAP[nova_fonte]=1800  # fontes pesadas (cnpj, tse, camara)
```

### 3. Fila correta
- Fonte federal/nacional → `DEFAULT_QUEUE`
- Fonte estadual AM → `AMAZONAS_QUEUE`
```bash
DEFAULT_QUEUE=(
  ...
  nova_fonte
  ...
)
```

---

## REGRA #2 — AVALIAÇÃO DE MEMÓRIA OBRIGATÓRIA

Antes de criar qualquer pipeline:

1. **Tamanho estimado do CSV** — se > 500k linhas: OBRIGATÓRIO usar chunked
2. **Nunca usar `pd.read_csv` sem `chunksize`** em arquivos grandes
3. **Nunca usar `iterrows()` para carregar dados em lista** — usar processamento direto no chunk
4. **`batch_size` do Neo4jBatchLoader** — padrão 500, reduzir para 200 em pipelines pesados

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
# Criar índice antes de rodar o pipeline
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme   "CREATE INDEX nome_indice IF NOT EXISTS FOR (n:Label) ON (n.campo)" && echo "OK"
```

Após criar, adicionar em `docs/operacional/SETUP_INDICES.md`.

---

## REGRA #5 — DOWNLOADS DEVEM USAR _download_utils

- Sempre importar `download_file` e `extract_zip` de `_download_utils`
- Nunca reimplementar lógica de download diretamente
- Novo `download_FONTE.py` deve seguir o padrão dos existentes

---

## REGRA #6 — WCC APÓS IMPORTAÇÃO COM SAME_AS

Se o pipeline cria relações SAME_AS ou POSSIBLY_SAME_AS, re-rodar WCC obrigatório:

```bash
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme   "CALL gds.graph.drop('"identity-graph"') YIELD graphName" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme   "CALL gds.graph.project('"identity-graph"', ['"Person"','"Partner"','"GlobalPEP"','"OffshoreOfficer"'], {SAME_AS: {orientation: '"UNDIRECTED"'}}) YIELD graphName, nodeCount, relationshipCount" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme   "CALL gds.wcc.write('"identity-graph"', {writeProperty: '"community_id"'}) YIELD componentCount, nodePropertiesWritten" && echo "OK"
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

## PIPELINES QUE AINDA PRECISAM DE REVISÃO

- `camara.py` — 3.35M+ registros (pendente diagnóstico Neo4j memory)
- `cnpj.py` — volume alto
- `senado_cpis.py`, `camara_inquiries.py`, `mides.py`, `transferegov.py`, `transparencia.py`, `tse.py`, `senado.py`, `tcu.py`, `datajud.py`, `ibama.py`, `icij.py`, `tse_filiados.py` — fix sessão única pendente

---

*Atualizar este arquivo quando novos padrões forem alinhados com Rolim*
