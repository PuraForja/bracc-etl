# STATUS DOS SCRIPTS DE DOWNLOAD — BRACC
> Atualizado em 03/06/2026
> Padrão de registro obrigatório para IAs — ver seção COMO REGISTRAR ao final

---

## CORREÇÃO CENTRAL PENDENTE — `_download_utils.py`

**Status:** PENDENTE — nunca implementado

Adicionar parâmetro `referer` opcional no `download_file`. Sem isso, downloads da CGU retornam 403.

```python
def download_file(url: str, dest: Path, *, timeout: int = 600, referer: str = None) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    if referer:
        headers["Referer"] = referer
```

**Impacto:** CEPIM, PEP CGU, Servidores CGU dependem disso.

---

## SCRIPTS COM PROBLEMAS

### [BLOQUEADO] PEP CGU
- **Script:** `etl/scripts/download_pep_cgu.py`
- **Problema:** 403 em todas as datas — requer autenticação
- **URL real:** `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/pep/{YYYYMMDD}_PEP.zip`
- **Referer:** `https://portaldatransparencia.gov.br/download-de-dados/pep`
- **O que contém:** CPF + nome + cargo + órgão de todos os políticos e servidores de alto escalão
- **Solução A (recomendada):** Token via email descartável
  1. Criar email em guerrillamail.com ou temp-mail.org
  2. Acessar `https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email`
  3. Autenticar com Gov.br (CPF+senha+2FA)
  4. Receber token no email
  5. Usar API paginada: `https://api.portaldatransparencia.gov.br/api-de-dados/pep`
  6. Header: `{"chave-api-dados": "SEU_TOKEN"}`
  7. Limite: 400 req/min (comercial), 700 req/min (madrugada), tamanhoPagina=500
- **Solução B:** OpenSanctions já importado — menos completo para cargos municipais
- **Orchestrator:** NÃO registrado
- **Última verificação:** 30/04/2026
- **Status:** BLOQUEADO — aguarda decisão token

### [PENDENTE] BCB Penalidades
- **Script:** `etl/scripts/download_bcb.py`
- **Problema:** URL antiga morta — `https://www3.bcb.gov.br/rdrweb/rest/ext/ranking/arquivo?tipo=2` retorna 400
- **Nova API Olinda:**
https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador?format=json&
top=500&$skip=0
- **Swagger:** `https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/swagger-ui3`
- **Teste manual:**
```bash
  curl "https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador?$format=json&$top=5" && echo "OK"
```
- **Como reescrever:** paginação com `$top=500&$skip=N` até retornar vazio
- **Orchestrator:** registrado como `bcb` — precisa atualizar URL
- **Última verificação:** 04/05/2026
- **Status:** PENDENTE — API mapeada, script não reescrito

### [PENDENTE] EU Sanctions
- **Script:** `etl/scripts/download_eu_sanctions.py`
- **Problema:** `https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList/content` → 403
- **URL alternativa:**
https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions
- **Nota:** OpenSanctions já importado — verificar se cobre EU suficientemente antes de corrigir
- **Orchestrator:** registrado como `eu_sanctions`
- **Última verificação:** 30/04/2026
- **Status:** PENDENTE — verificar cobertura OpenSanctions primeiro

### [PENDENTE] World Bank
- **Script:** `etl/scripts/download_world_bank.py`
- **Problema:** URLs originais mortas
- **URL alternativa:** `https://projects.worldbank.org/en/projects-operations/procurement/debarred-firms`
- **Download direto:** `https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_PDF_19_03_FINAL/SUPPLIER/debarr`
- **Orchestrator:** registrado como `world_bank`
- **Última verificação:** 30/04/2026
- **Status:** PENDENTE — URL nova não testada

### [PENDENTE] Servidores CGU
- **Script:** `etl/scripts/download_transparencia.py`
- **Problema:** 403 em todos os meses testados
- **URL real:** `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/servidores/{YYYYMM}.zip`
- **Referer:** `https://portaldatransparencia.gov.br/download-de-dados/servidores`
- **Solução:** mesmo padrão do CEPIM — fallback D-1 + Referer
- **Depende de:** correção do `_download_utils.py` com parâmetro referer
- **Orchestrator:** registrado como `transparencia`
- **Última verificação:** 30/04/2026
- **Status:** PENDENTE — aguarda correção _download_utils.py

---

## SCRIPTS FUNCIONANDO

### [OK] CEPIM
- **Script:** `etl/scripts/download_cepim.py`
- **URL real:** `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/cepim/{YYYYMMDD}_CEPIM.zip`
- **Referer:** `https://portaldatransparencia.gov.br/download-de-dados/cepim`
- **Padrão:** YYYYMMDD — atualização diária útil — usar D-1
- **Orchestrator:** registrado como `cepim`
- **Última verificação:** 03/05/2026 — 200 OK ✅
- **Status:** OK

### [OK] TSE Candidaturas
- **Script:** `etl/scripts/download_tse.py`
- **URL:** `https://cdn.tse.jus.br/estatistica/sead/odsele/`
- **Orchestrator:** registrado como `tse`
- **Última verificação:** 02/06/2026 ✅
- **Status:** OK

### [OK] TSE Bens Declarados
- **Script:** `etl/scripts/download_tse_bens_cdn.py`
- **URL:** `https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato/bem_candidato_{ano}.zip`
- **Orchestrator:** NÃO registrado ainda — adicionar
- **Última verificação:** 03/06/2026 ✅
- **Status:** OK — precisa ser adicionado ao orchestrator

### [OK] CNPJ
- **Script:** `etl/scripts/download_cnpj.py`
- **URL:** `https://dadosabertos.rfb.gov.br/CNPJ/dados_abertos_cnpj/`
- **Orchestrator:** registrado como `cnpj`
- **Status:** OK

---

## LÓGICA DE FALLBACK — PADRÃO PARA DATAS

Para fontes com atualização diária (CEPIM, PEP), tentar datas retroativas:

```python
from datetime import date, timedelta
import urllib.request

def find_latest_file(base_url, suffix, referer, max_days=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": referer,
    }
    d = date.today()
    for _ in range(max_days):
        url = f"{base_url}/{d.strftime('%Y%m%d')}{suffix}"
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    return url
        except Exception:
            pass
        d -= timedelta(days=1)
    return None
```

---

## ORCHESTRATOR — COMO REGISTRAR NOVO DOWNLOAD

**OBRIGATÓRIO:** Todo novo script `download_*.py` deve ser registrado no orchestrator.

Verificar padrão existente:
```bash
grep -A3 "tse_bens\|tse\b" ~/bracc/orchestrator.sh | head -20 && echo "OK"
```

Adicionar em 3 lugares no `orchestrator.sh`:
1. `LABEL_MAP[fonte]="LabelNeo4j"` — mapeia fonte para label do Neo4j
2. `TIMEOUT_MAP[fonte]=600` — timeout em segundos (padrão 180, fontes pesadas 1800)
3. Na lista de fontes da fila principal

Exemplo:
```bash
LABEL_MAP[tse_bens]="DeclaredAsset"
TIMEOUT_MAP[tse_bens]=1800
```

---

## COMO REGISTRAR — PADRÃO OBRIGATÓRIO PARA IAs

### Novo problema encontrado:
[STATUS] NOME_FONTE

Script: etl/scripts/download_X.py
Problema: descrição do erro
URL real: https://...
Referer: https://... (se necessário)
Solução: descrição ou PENDENTE
Orchestrator: registrado como X / NÃO registrado
Última verificação: DD/MM/AAAA
Status: BLOQUEADO/PENDENTE/OK


### Ao resolver:
1. Mover para seção SCRIPTS FUNCIONANDO
2. Mudar status para `[OK]`
3. Atualizar `Última verificação`
4. Remover detalhes de solução (manter só URL e Referer)

### Regras:
- Caminhos SEMPRE relativos a `~/bracc/` — nunca `~/Downloads/br-acc-novo/`
- SEMPRE verificar se script está no orchestrator — se não, registrar
- SEMPRE testar URL com curl antes de marcar como OK
- NUNCA marcar OK sem teste confirmado
