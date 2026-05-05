# CHANGELOG TÉCNICO — Alterações no Código Fonte
> Este arquivo registra TODAS as alterações feitas nos arquivos do projeto.
> Qualquer IA deve ler este arquivo ANTES de qualquer correção de código.
> Atualizar sempre que fizer qualquer alteração.

---

## 2026-05-03 — TAREFA PENDENTE PARA PRÓXIMA IA

### [03/05/2026] — Análise de docs/analise_outra_ia/ — PENDENTE

**O que precisa ser feito:**
1. Ler o conteúdo de `diff_completo_outra_ia.txt` — pode ter alterações não vistas
2. Ler o conteúdo de `download_pep_versao_outra_ia.py` — não foi analisado
3. Registrar no CHANGELOG qualquer descoberta relevante

**Comandos:**
```bash
cat ~/Downloads/br-acc-novo/docs/analise_outra_ia/diff_completo_outra_ia.txt
cat ~/Downloads/br-acc-novo/docs/analise_outra_ia/download_pep_versao_outra_ia.py
```

**Após análise:** atualizar este CHANGELOG com o que encontrar.

---

## 2026-05-03 — CORREÇÕES NOS SCRIPTS DE DOWNLOAD

### [03/05/2026 ~23h] — _download_utils.py — feat ✅ COMMITADO (fa778cf)

**O que foi feito:** Adicionada função `find_latest_date()` centralizada.
Todos os scripts de download que precisarem de fallback de datas devem usar esta função.

```python
find_latest_date(base_url, filename_pattern, referer, max_days=7)
# Exemplo CEPIM:
find_latest_date(
    "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/cepim",
    "{date}_CEPIM.zip",
    "https://portaldatransparencia.gov.br/download-de-dados/cepim"
)
```

**Localização:** linha 148 do `_download_utils.py`

---

### [03/05/2026 ~23h] — download_cepim.py — fix ✅ COMMITADO (fa778cf)

**Problema:** Formato de data errado (`%Y%m` em vez de `%Y%m%d`) e sem fallback automático.
**Solução:** Usa `find_latest_date()` com loop de 7 dias + D-1 como segurança.

```python
# Import adicionado:
from _download_utils import download_file, extract_zip, validate_csv, find_latest_date

# Default da data:
default=lambda: find_latest_date(
    "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/cepim",
    "{date}_CEPIM.zip",
    "https://portaldatransparencia.gov.br/download-de-dados/cepim"
) or (datetime.now() - timedelta(days=1)).strftime("%Y%m%d"),
```

---

### [03/05/2026 ~23h] — download_pep_cgu.py — fix ✅ COMMITADO (fa778cf)

**Problema:** Sem fallback automático de datas.
**Solução:** Mesma lógica do CEPIM com URL do PEP.

```python
default=lambda: find_latest_date(
    "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/pep",
    "{date}_PEP.zip",
    "https://portaldatransparencia.gov.br/download-de-dados/pep"
) or (datetime.now() - timedelta(days=1)).strftime("%Y%m%d"),
```

**Obs:** PEP ainda tem bloqueio de autenticação (403) — a lógica está correta mas
o arquivo em si não é acessível sem token Gov.br.

---

### [03/05/2026] — Restauração de scripts alterados por outra IA ✅ COMMITADO

**O que aconteceu:** Outra IA alterou scripts sem registro adequado em sessão de 03/05.
**Arquivos restaurados:** `download_cepim.py` (reescrito com requests puro → restaurado original)
**Arquivo removido:** `download_pep.py` (criado vazio → movido para análise)
**Preservado em:** `docs/analise_outra_ia/`

**O que a outra IA propôs (válido para implementar futuramente):**
- Centralizar downloads no `_download_utils.py` — **já implementado parcialmente** (find_latest_date)
- Constraints únicas no Neo4j — **pendente diagnóstico**
- Limitar heap Neo4j a 20GB — **pendente diagnóstico**

---

## 2026-05-02 — batch_size reduzido para 500

### [02/05/2026] — 6 pipelines grandes — fix ⚠️ NÃO RESOLVE CÂMARA

**Problema:** batch_size=1_000 ainda causava morte silenciosa no load.
**Solução aplicada:** batch_size=500 — câmara ainda morre.
**Próximo passo:** diagnóstico de memória + constraints antes de tentar batch=250.

**Arquivos:**
```
senado.py ✅ importou
camara.py ❌ ainda morrendo
transparencia.py, tse.py, siop.py, opensanctions.py ⏳ aguardando câmara
```

---

## 2026-05-01 — CORREÇÃO CRÍTICA: run_query_with_retry + batch_size=1_000

### [01/05/2026] — 12 pipelines — fix ✅ COMMITADO (fb14cba)

**Problema:** `loader.run_query()` mandava todas as relações de uma vez → OOM.
**Solução:** `run_query_with_retry` com batches de 500 + retry automático.

**Arquivos:**
```
senado.py, camara.py, transparencia.py, tse.py, sanctions.py,
cvm.py, ibama.py, inep.py, tcu.py, tesouro_emendas.py,
transferegov.py, cnpj.py
```

---

## 2026-04-30 — Scripts de download

### download_cepim.py
**Solução definitiva:** `find_latest_date()` com 7 dias ✅ aplicado em 03/05

### download_bcb.py
**Problema:** URL antiga retorna 400.
**Nova URL:** `https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador`
**Pendente:** Reescrever script usando `_download_utils.py` + API Olinda.
**Dados:** ✅ 16.394 penalidades em data/bcb/penalidades.csv

---

## ARQUITETURA DOS SCRIPTS DE DOWNLOAD

```
_download_utils.py              ← BASE — nunca reescrever com requests puro
    ├── download_file()         retomada, streaming, User-Agent, httpx
    ├── extract_zip()           proteção ZIP bombs
    ├── validate_csv()          validação de colunas
    └── find_latest_date()      fallback de datas (7 dias) — adicionado 03/05

download_FONTE.py               ← cada fonte tem seu script
    ├── importa _download_utils ← OBRIGATÓRIO
    ├── find_latest_date()      ← para fontes com atualização diária
    └── mapeamento de colunas
```

**Scripts corrigidos:** download_cepim.py ✅ download_pep_cgu.py ✅
**Scripts pendentes:** download_bcb.py, download_transparencia.py, download_world_bank.py

---

## PENDÊNCIAS

```
[ ] Analisar docs/analise_outra_ia/ — diff_completo e download_pep_versao (PRÓXIMA IA)
[ ] Resolver câmara — diagnóstico memória Neo4j ANTES de relançar
[ ] Implementar constraints únicas no Neo4j (CNPJ, CPF)
[ ] Limitar heap Neo4j a 20GB no docker-compose.yml
[ ] download_bcb.py — reescrever para API Olinda usando _download_utils.py
[ ] download_pep_cgu.py — token Gov.br ou OpenSanctions (ainda bloqueado)
[ ] download_world_bank.py — testar URL legada
[ ] download_transparencia.py — loop de meses para trás
[ ] Nginx timeout — incorporar no Dockerfile
[ ] Bug frontend — grafo vazio para Person
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] Backup urgente após câmara importar
```

---

## VERIFICAÇÃO RÁPIDA

```bash
# find_latest_date no _download_utils
grep -n "def find_latest_date" ~/Downloads/br-acc-novo/etl/scripts/_download_utils.py

# Scripts usando find_latest_date
grep -rl "find_latest_date" ~/Downloads/br-acc-novo/etl/scripts/ | grep -v ".bak"

# run_query sem retry (deve retornar VAZIO)
grep -r "loader\.run_query(" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak" | grep -v "run_query_with_retry"

# Ver o que não foi commitado
cd ~/Downloads/br-acc-novo && git status --short
```

---

## REGRAS

- Nunca reescrever scripts com `requests` puro — sempre usar `_download_utils.py`
- Confirmar alterações antes de executar
- Sempre incluir data/hora nos logs
- Salvar versão anterior antes de restaurar — `docs/analise_outra_ia/`

*Atualizado em 03/05/2026 ~23h55*

## 2026-05-04 — CORREÇÃO: referer no download_file
**Problema:** download_file chamado sem referer — 403 no dadosabertos-download.cgu.gov.br
**Solução:** referer=f"{BASE_URL}/cepim" e referer=f"{BASE_URL}/pep" adicionados
**Arquivos:** download_cepim.py linha 63, download_pep_cgu.py linha 127
**Também:** docker-compose.yml heap 1G->16g, pagecache 512m->4g, transacao 1G->4G
**Testado:** nao

## 2026-05-04 — TESTES DE URLs
**BCB Olinda:** https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador — FUNCIONANDO 200 OK
**Transparencia servidores:** dadosabertos-download.cgu.gov.br/saida/servidores/YYYYMM.zip — 403 PERSISTENTE mesmo com Referer
**World Bank:** apigwext.worldbank.org URL — 404 MORTA

## 2026-05-05 — SESSAO 05/05
**Cache Python limpo** — camara.py vetorizado ja estava correto, cache antigo causava execucao do iterrows
**camara.py** — commitado codigo vetorizado sem iterrows, arquivo por arquivo com del df
**Teste camara** — limit 1000 passou: 265k linhas processadas, 1000 Expense nodes carregados OK
**Fila rodando** — siop OK, opensanctions em load, transparencia e tse na fila
**dbfread** — instalado e adicionado ao pyproject.toml para conversao DBC DATASUS
**Analise 4 pendentes** — eu_sanctions/pep_cgu/world_bank ja cobertos pelo opensanctions. DATASUS via FTP+dbfread viavel
**FTP DATASUS** — acessivel sem login: ftp://ftp.datasus.gov.br/dissemin/publicos/
**download_datasus.py** — PENDENTE implementar usando FTP + dbfread

**eu_sanctions** — IP BR bloqueado, solucao: dados ja estao dentro do opensanctions importado
**pep_cgu** — auth 403, solucao: opensanctions tem GlobalPEP + TSE cobre PEPs eleitos
**world_bank** — URL morta, solucao: dados debarred ja estao dentro do opensanctions
**datasus** — pipeline datasus.py existe, falta download_datasus.py via FTP+dbfread — PENDENTE
**Constraints Neo4j** — verificadas, ja existiam: company_cnpj_unique e person_cpf_unique
**siop** — importado 05/05 com sucesso: 73.795 LaborStats nodes
**opensanctions** — importado 05/05: 117.910 GlobalPEP, 8.044 CPF match relationships
**PNCP** — 69% baixado (3241/4680 combos) em 05/05 ~02h
**download_bcb.py** — reescrito API Olinda, paginacao PAGE_SIZE=500, retry automatico, 16.395 registros OK

## PENDENCIAS PARA PROXIMA IA — VERIFICAR E REGISTRAR
[ ] Verificar se referer cepim+pep foi testado com sucesso apos correcao
[ ] Registrar resultado final da fila transparencia->tse->camara (ainda rodando)
[ ] Registrar contagem final de nodes apos fila terminar
[ ] Fazer BACKUP urgente apos fila terminar
[ ] Implementar download_datasus.py via FTP+dbfread
[ ] Verificar PNCP progresso e retomar se parou
[ ] Gerar v22 ao final da proxima sessao

### [05/05/2026] — transparencia/servidores.csv — PENDENTE
**Problema:** servidores.csv nao encontrado em data/transparencia durante importacao
**Causa:** download_transparencia.py retorna 403 para servidores (URL do mes atual nao disponivel)
**Impacto:** servidores publicos federais ausentes do Neo4j (nome, CPF, orgao, cargo, salario)
**Acao:** testar download com mes anterior: uv run python scripts/download_transparencia.py --output-dir ../data/transparencia --month 202503
**Apos download:** reimportar so transparencia sem refazer fila toda
**Testado:** nao

### [05/05/2026] — transparencia/servidores.csv — PENDENTE
**Problema:** servidores.csv nao encontrado em data/transparencia durante importacao
**Causa:** download_transparencia.py retorna 403 para servidores (URL do mes atual nao disponivel)
**Impacto:** servidores publicos federais ausentes do Neo4j (nome, CPF, orgao, cargo, salario)
**Acao:** testar download com mes anterior: uv run python scripts/download_transparencia.py --output-dir ../data/transparencia --month 202503
**Apos download:** reimportar so transparencia sem refazer fila toda
**Testado:** nao

### [05/05/2026] — download_transparencia.py servidores+compras — 403 PERSISTENTE
**Resultado:** 403 em servidores e compras para 202503 — bloqueio CGU nao e questao de data
**Emendas:** OK 200 — 859.216 rows baixados
**Causa provavel:** CGU exige token de API ou navegador autenticado para servidores/compras
**Acao futura:** cadastrar token em portaldatransparencia.gov.br/api-de-dados/cadastrar-email (mesmo fluxo do PEP)
**Testado:** sim — 202503 retorna 403 em servidores e compras

### [05/05/2026] — camara.py linha 147 — fix sha256 vetorizado
**Problema:** apply(sha256) em 265k linhas por arquivo matava o processo apos ~40min sem logar erro
**Solucao:** substituir por pd.util.hash_pandas_object() — operacao vetorizada nativa pandas
**Testado:** nao — relancando agora

### [05/05/2026] — camara.py — fix sha256 + diagnostico + batch_size=250
**Problema 1:** apply(sha256) em 265k linhas matava o processo
**Solucao 1:** pd.util.hash_pandas_object() vetorizado — commit 2b648f0
**Problema 2:** load_nodes 192k Expense nodes batch_size=500 matava Neo4j
**Solucao 2:** batch_size=250 — linha 198 camara.py
**Logs adicionados:** expense_id gerado + to_dict OK para diagnostico
**Status:** camara rodando com batch_size=250 — aguardando resultado
**Testado:** parcial — transformacao OK, load em andamento
