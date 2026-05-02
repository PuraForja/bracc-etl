# MAPA DE CORREÇÕES DOS SCRIPTS DE DOWNLOAD
> Criado em 30/04/2026 — atualizar conforme novos testes
> Este arquivo documenta TODOS os problemas encontrados e as correções a fazer

---

## CORREÇÃO CENTRAL — `_download_utils.py`

Adicionar parâmetro `referer` opcional no `download_file`:

```python
def download_file(url: str, dest: Path, *, timeout: int = 600, referer: str = None) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    if referer:
        headers["Referer"] = referer
    # resto do código igual...
```

---

## 1. CEPIM ✅ RESOLVIDO

**Script:** `etl/scripts/download_cepim.py`

**Problema:** Script tentava baixar arquivo do dia atual que ainda não existe → 403.

**Solução:** Passar data D-1 manualmente. Funciona sem alteração de código.

**Comando que funciona:**
```bash
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_cepim.py --output-dir ../data/cepim \
  --date 20260429 2>&1 | tee ../download_cepim.log
```

**Melhoria futura no código** — adicionar fallback automático de D-1:
```python
from datetime import date, timedelta

def _find_latest_date(base_url, referer, max_days=5):
    """Tenta datas de hoje para trás até achar arquivo disponível."""
    import urllib.request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": referer,
    }
    d = date.today()
    for _ in range(max_days):
        date_str = d.strftime("%Y%m%d")
        url = f"{base_url}/{date_str}_CEPIM.zip"
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    return date_str
        except:
            pass
        d -= timedelta(days=1)
    return None
```

**URL real:** `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/cepim/{YYYYMMDD}_CEPIM.zip`
**Referer:** `https://portaldatransparencia.gov.br/download-de-dados/cepim`
**Atualização:** Diária (dia útil)
**Resultado testado:** `20260429_CEPIM.zip` → 200 OK → 3.572 registros ✅

---

## 2. PEP CGU ❌ BLOQUEADO — REQUER AÇÃO MANUAL

**Script:** `etl/scripts/download_pep_cgu.py`

**Problema:** Arquivo ZIP retorna 403 em TODAS as datas testadas (60 dias para trás). Bloqueio intencional — exige autenticação.

**O que o PEP contém:**
- CPF, nome, cargo/função, órgão, datas de exercício
- Fonte: TCU, Câmara, Senado, Ministérios, CGU, Estados e Municípios
- Todos políticos e servidores de alto escalão com CPF

**Soluções possíveis (escolher uma):**

### Opção A — Token com e-mail descartável (recomendada por privacidade)
1. Criar e-mail descartável (ex: guerrillamail.com, temp-mail.org)
2. Acessar: `https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email`
3. Autenticar com Gov.br (CPF+senha+2FA) ou conta Prata/Ouro
4. Cadastrar o e-mail descartável
5. Receber token no e-mail
6. Modificar script para usar API em vez de ZIP:

```python
# Nova URL via API (retorna JSON paginado)
API_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/pep"
# Header obrigatório:
headers = {"chave-api-dados": "SEU_TOKEN_AQUI"}
# Limite: 400 req/min (horário comercial), 700 req/min (madrugada)
# Parâmetros: pagina=1, tamanhoPagina=500 (máx)
```

### Opção B — OpenSanctions (já baixado, já importado)
- O OpenSanctions agrega PEP de várias fontes incluindo Brasil
- Já está no Neo4j como `InternationalSanction`
- Menos completo que a CGU para cargos municipais/estaduais

### Opção C — Selenium/Playwright (complexo)
- Simular navegador com login real
- Obter cookie de sessão e usar no download
- Mais frágil — quebra quando o site muda

**Decisão pendente:** Escolher entre Opção A ou B.

---

## 3. BCB (Banco Central) — REQUER REESCRITA DO SCRIPT

**Script:** `etl/scripts/download_bcb.py`

**Problema:** URL antiga morreu — `https://www3.bcb.gov.br/rdrweb/rest/ext/ranking/arquivo?tipo=2` retorna 400.

**Nova fonte:** BCB migrou para API Olinda (dados abertos).

**Nova URL da API:**
```
https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador?$format=json&$top=500&$skip=0
```

**Swagger/documentação:**
```
https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/swagger-ui3#/
```

**Como reescrever o script:**
```python
import urllib.request, json, pandas as pd
from pathlib import Path

API_BASE = "https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata"
ENDPOINT = "QuadroGeralProcessoAdministrativoSancionador"
PAGE_SIZE = 500

def download_bcb_penalties(output_path: Path):
    all_records = []
    skip = 0
    while True:
        url = f"{API_BASE}/{ENDPOINT}?$format=json&$top={PAGE_SIZE}&$skip={skip}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        records = data.get("value", [])
        if not records:
            break
        all_records.extend(records)
        skip += PAGE_SIZE
        print(f"  Baixados: {len(all_records)} registros...")
        if len(records) < PAGE_SIZE:
            break
    df = pd.DataFrame(all_records)
    df.to_csv(output_path, index=False, sep=";", encoding="utf-8")
    print(f"✅ BCB: {len(df)} penalidades salvas")
```

**Cobertura:** Decisões de 1º instância a partir de 01/01/2013
**Atualização:** Conforme novas penalidades
**Testado:** API confirmada existente — script não testado ainda

**TODO:**
1. Testar API manualmente: `curl "https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador?$format=json&$top=5"`
2. Ver quais campos retorna
3. Mapear campos para o EXPECTED_COLUMNS do script atual
4. Reescrever `download_bcb.py` com paginação via Olinda API

---

## 4. EU Sanctions ❌ BLOQUEADO — INVESTIGAR ALTERNATIVA

**Script:** `etl/scripts/download_eu_sanctions.py`

**Problema:** `https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList/content` → 403 Forbidden

**O que contém:** Lista consolidada de sanções da União Europeia

**Alternativas a investigar:**
1. **OpenSanctions** — já baixado, provavelmente inclui sanções EU
2. **URL alternativa oficial EU:**
   ```
   https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions
   ```
3. **API do EU Financial Sanctions Files:**
   ```
   https://eeas.europa.eu/topics/sanctions-policy/8442/consolidated-list-of-sanctions_en
   ```

**TODO:**
1. Verificar se OpenSanctions já cobre EU sanctions suficientemente
2. Se não, testar URL alternativa da Europa
3. Atualizar script com nova URL

---

## 5. World Bank ❌ URLs MORTAS — INVESTIGAR

**Script:** `etl/scripts/download_world_bank.py` (verificar nome exato)

**Problema:** URLs originais mortas

**Alternativa oficial:**
```
https://projects.worldbank.org/en/projects-operations/procurement/debarred-firms
```
Download direto:
```
https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_PDF_19_03_FINAL/SUPPLIER/debarr
```

**TODO:**
1. `cat ~/Downloads/br-acc-novo/etl/scripts/download_world_bank.py` para ver URL atual
2. Testar nova URL
3. Verificar formato dos dados (JSON/CSV/PDF)
4. Atualizar script

---

## 6. Servidores CGU ❌ 403 — MESMA CORREÇÃO DO CEPIM

**Script:** `etl/scripts/download_transparencia.py`

**Problema:** Servidores retornam 403 em todos os meses testados

**Análise:** Mesmo padrão do CEPIM — provavelmente arquivo do mês atual não gerado ainda.

**TODO:**
1. Testar com mês anterior: `--year 2025` ou `--month 202503`
2. Verificar se existe arquivo em `dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/servidores/`
3. Aplicar mesma lógica de fallback de datas

---

## RESUMO — PRIORIDADE DE CORREÇÃO

| # | Fonte | Esforço | Impacto | Status |
|---|---|---|---|---|
| 1 | CEPIM | ✅ zero | Médio | Resolvido com D-1 |
| 2 | BCB | Médio — reescrever script | Alto | API nova mapeada |
| 3 | Servidores CGU | Baixo — testar mês anterior | Alto | Investigar |
| 4 | PEP CGU | Médio — token e-mail descartável | Muito alto | Aguarda decisão |
| 5 | EU Sanctions | Baixo — nova URL | Médio | Investigar |
| 6 | World Bank | Baixo — nova URL | Médio | Investigar |

---

## CHECKLIST QUANDO FOR CORRIGIR

```
[ ] Corrigir _download_utils.py — adicionar parâmetro referer
[ ] Testar CEPIM com fallback automático de datas
[ ] Testar BCB API Olinda — curl manual primeiro
[ ] Reescrever download_bcb.py com paginação Olinda
[ ] Testar servidores CGU com mês anterior
[ ] Decidir PEP: token e-mail descartável ou OpenSanctions
[ ] Se token: modificar download_pep_cgu.py para usar API
[ ] Investigar EU Sanctions URL alternativa
[ ] Investigar World Bank nova URL
[ ] Testar todos os scripts corrigidos
[ ] Atualizar URLS_CORRETAS.md com resultados
```

---

*Atualizado em 30/04/2026*
*Próxima sessão de correções: quando downloads e importações terminarem*
