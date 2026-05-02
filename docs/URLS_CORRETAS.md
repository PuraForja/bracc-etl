# MAPA DE URLs CORRETAS — Scripts de Download
> Criado em 30/04/2026
> Usar este arquivo ao corrigir os scripts de download

---

## Problema Geral

Os scripts usam a URL do portal como intermediária:
```
https://portaldatransparencia.gov.br/download-de-dados/FONTE/DATA
```
Essa URL faz redirect para o servidor real `dadosabertos-download.cgu.gov.br`, que barra com **403** porque não recebe os cookies/headers corretos.

**Solução:** Apontar direto para o servidor real + passar `Referer` correto no header.

O `_download_utils.py` já passa `User-Agent` mas **não passa `Referer`** — essa é a correção central.

---

## URLs Corretas por Fonte

### CEPIM
```
Script:    etl/scripts/download_cepim.py
Problema:  URL intermediária + sem Referer
URL real:  https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/cepim/{YYYYMMDD}_CEPIM.zip
Referer:   https://portaldatransparencia.gov.br/download-de-dados/cepim
Padrão:    YYYYMMDD (data completa, atualização diária útil)
Testado:   20260429_CEPIM.zip → 200 OK ✅
Obs:       Hoje (30/04) ainda deu 403 — arquivo gerado no dia anterior
```

### PEP (Pessoas Expostas Politicamente)
```
Script:    etl/scripts/download_pep_cgu.py
Problema:  URL intermediária + sem Referer
URL real:  https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/pep/{YYYYMMDD}_PEP.zip
Referer:   https://portaldatransparencia.gov.br/download-de-dados/pep
Padrão:    YYYYMMDD (data completa)
Testado:   Ainda não testado — aplicar mesma lógica do CEPIM
```

### Servidores (Transparência)
```
Script:    etl/scripts/download_transparencia.py
Problema:  403 em todos os meses
URL real:  https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/servidores/{YYYYMM}.zip
Referer:   https://portaldatransparencia.gov.br/download-de-dados/servidores
Padrão:    YYYYMM
Testado:   Não — mesmo problema de Referer provavelmente
```

---

## Lógica de Fallback (para datas)

Para fontes com atualização diária (CEPIM, PEP), o script deve tentar
datas retroativas até encontrar o arquivo mais recente:

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
        except:
            pass
        d -= timedelta(days=1)
    return None
```

---

## Correção no `_download_utils.py`

Adicionar `Referer` como parâmetro opcional no `download_file`:

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

## Status de Cada Script

| Script | URL correta mapeada | Referer identificado | Testado | Corrigido |
|---|---|---|---|---|
| download_cepim.py | ✅ | ✅ | ✅ 200 OK | ⏳ |
| download_pep_cgu.py | ✅ | ✅ | ⏳ | ⏳ |
| download_transparencia.py (servidores) | ✅ | ✅ | ⏳ | ⏳ |
| download_bcb.py | ⏳ investigar | — | ❌ 400 | ⏳ |
| download_eu_sanctions.py | ⏳ investigar | — | ❌ 403 | ⏳ |
| download_world_bank.py | ⏳ investigar | — | ❌ URL morta | ⏳ |

---

## Próximos Passos

1. Testar URL do PEP com mesmo script de varredura usado no CEPIM
2. Corrigir `_download_utils.py` — adicionar parâmetro `referer`
3. Corrigir `download_cepim.py` — URL direta + Referer + fallback de datas
4. Corrigir `download_pep_cgu.py` — mesma lógica
5. Investigar BCB — nova URL da API de penalidades
6. Investigar EU Sanctions — alternativa ao webgate.ec.europa.eu
7. Investigar World Bank — nova URL ou fonte alternativa

---

*Atualizar este arquivo conforme novos testes forem feitos*
