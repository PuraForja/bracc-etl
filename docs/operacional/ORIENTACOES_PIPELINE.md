# Orientações Obrigatórias — Novos Pipelines

## Regra: Todo novo pipeline deve ser avaliado para uso de memória

### Checklist antes de criar qualquer pipeline novo

1. **Tamanho estimado do CSV** — se > 500k linhas, OBRIGATÓRIO usar chunked processing
2. **Nunca usar `pd.read_csv` sem `chunksize`** em arquivos grandes
3. **Nunca usar `iterrows()` para carregar dados em lista** — usar processamento direto no chunk
4. **`batch_size` do Neo4jBatchLoader** — padrão 500, reduzir para 200 em pipelines pesados

### Padrão obrigatório para pipelines com CSV > 500k linhas

```python
# CORRETO — chunked
for chunk in pd.read_csv(path, encoding="latin-1", dtype=str, chunksize=50_000):
    rows = []
    for _, row in chunk.iterrows():
        # processa linha
        rows.append({...})
    if rows:
        loader.load_nodes("Label", rows, key_field="id")

# ERRADO — carrega tudo em memória
df = pd.read_csv(path, encoding="latin-1", dtype=str)
for _, row in df.iterrows():
    rows.append({...})
```

### Pipelines já corrigidos para chunked
| Pipeline | Data | Motivo |
|---|---|---|
| tse.py — doações | 02/06/2026 | 3.1M linhas travavam em memória |

### Pipelines que ainda precisam de revisão
- `camara.py` — 3.35M+ registros (pendente diagnóstico Neo4j memory)
- `cnpj.py` — volume alto

## Regra: Novos `download_*.py` devem usar `_download_utils`
- Sempre importar `download_file` e `extract_zip` de `_download_utils`
- Nunca reimplementar lógica de download diretamente
- Sempre terminar comandos com `&& echo "OK"`
