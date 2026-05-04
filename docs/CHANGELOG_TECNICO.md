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
**Comando usado:** (se aplicável)
**Impacto:** Quais fontes/pipelines afetados
**Testado:** sim/não/parcial
```

---

## 2026-05-01 — CORREÇÃO CRÍTICA: batch_size + run_query_with_retry

### [01/05/2026] — Múltiplos pipelines — fix

**Problema 1:** Vários pipelines usavam `loader.run_query()` que mandava TODAS as relações
de uma vez para o Neo4j sem dividir em batches. Com centenas de milhares de relações,
o processo estourava memória e morria silenciosamente sem logar nenhum erro.
O senado travava 4+ vezes sempre no "Starting load..." sem deixar rastro.

**Solução 1:** Trocar `run_query` por `run_query_with_retry` que já divide em batches
de 500 com retry automático em deadlocks.

**Arquivos corrigidos:**
```
etl/src/bracc_etl/pipelines/senado.py
etl/src/bracc_etl/pipelines/camara.py
etl/src/bracc_etl/pipelines/transparencia.py
etl/src/bracc_etl/pipelines/tse.py
etl/src/bracc_etl/pipelines/sanctions.py
etl/src/bracc_etl/pipelines/cvm.py
etl/src/bracc_etl/pipelines/ibama.py
etl/src/bracc_etl/pipelines/inep.py
etl/src/bracc_etl/pipelines/tcu.py
etl/src/bracc_etl/pipelines/tesouro_emendas.py
etl/src/bracc_etl/pipelines/transferegov.py
etl/src/bracc_etl/pipelines/cnpj.py
```

**Comando usado:**
```bash
sed -i 's/loader\.run_query(/loader.run_query_with_retry(/g' ARQUIVO.py
```

**Testado:** Parcial — senado rodando com correção aplicada

---

**Problema 2:** `Neo4jBatchLoader` tem `batch_size` padrão de 10.000 nós por batch.
Para pipelines com 272k+ nós (senado, camara, tse, etc.), isso estourava memória
no load de nós antes mesmo de chegar nas relações.

**Solução 2:** Instanciar o loader com `batch_size=1_000` nos pipelines grandes.

**Arquivos corrigidos:**
```
etl/src/bracc_etl/pipelines/senado.py      — linha 252
etl/src/bracc_etl/pipelines/camara.py      — linha 226
etl/src/bracc_etl/pipelines/transparencia.py — linha 185
etl/src/bracc_etl/pipelines/tse.py         — linha 145
etl/src/bracc_etl/pipelines/siop.py        — linha 219
etl/src/bracc_etl/pipelines/opensanctions.py — linha 186
```

**Comando usado:**
```bash
sed -i 's/loader = Neo4jBatchLoader(self\.driver)/loader = Neo4jBatchLoader(self.driver, batch_size=1_000)/' ARQUIVO.py
```

**Backups criados:** `ARQUIVO.py.bak` no mesmo diretório para cada arquivo alterado.

**Testado:** Parcial — senado rodando com correção aplicada

---

## 2026-04-30 — CORREÇÕES NOS SCRIPTS DE DOWNLOAD

### [30/04/2026] — download_cepim.py — fix (workaround, não alteração de código)

**Problema:** Script tenta baixar arquivo do dia atual que não existe ainda → 403.
O arquivo é gerado no dia seguinte (D-1).

**Solução:** Passar `--date YYYYMMDD` com a data de ontem manualmente.
Sem alteração de código — workaround via parâmetro.

**Comando que funciona:**
```bash
uv run python scripts/download_cepim.py --output-dir ../data/cepim \
  --date $(date -d "yesterday" +%Y%m%d)
```

**Melhoria pendente:** Adicionar fallback automático D-1 no código do script.

**Testado:** ✅ 20260429_CEPIM.zip → 200 OK → 3.572 registros

---

### [30/04/2026] — download_bcb.py — workaround (script não alterado ainda)

**Problema:** URL antiga `https://www3.bcb.gov.br/rdrweb/rest/ext/ranking/arquivo?tipo=2`
retorna 400 — endpoint foi desativado.

**Solução temporária:** Download manual via API Olinda com script inline.
O arquivo `download_bcb.py` ainda NÃO foi reescrito — usa URL morta.

**Nova URL:** `https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador`

**Melhoria pendente:** Reescrever `download_bcb.py` para usar API Olinda com paginação.
Ver `CORRECOES_SCRIPTS_DOWNLOAD.md` para o código completo.

**Testado:** ✅ 16.394 penalidades salvas em `data/bcb/penalidades.csv`

---

## ALTERAÇÕES PENDENTES (TODO)

```
[ ] download_cepim.py — adicionar fallback automático D-1
[ ] download_bcb.py — reescrever para API Olinda
[ ] download_pep_cgu.py — implementar via API com token (ou marcar como substituído)
[ ] download_world_bank.py — testar URL legada e atualizar se necessário
[ ] download_transparencia.py — testar mês anterior (servidores 403)
[ ] Nginx timeout — incorporar configuração no Dockerfile permanentemente
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M esperados
```

---

## COMO VERIFICAR SE AS CORREÇÕES ESTÃO APLICADAS

```bash
# Verificar run_query_with_retry (deve retornar as linhas corrigidas)
grep -r "run_query_with_retry" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak"

# Verificar batch_size=1_000 (deve retornar os 6 arquivos)
grep -r "batch_size=1_000" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak"

# Verificar se ainda existe run_query sem retry (deve retornar VAZIO)
grep -r "loader\.run_query(" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak" | grep -v "run_query_with_retry"
```

---

*Criado em 01/05/2026*
*Atualizar este arquivo a cada alteração de código*
