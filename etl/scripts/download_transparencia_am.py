"""
download_transparencia_am.py
============================
Download de remuneração de servidores do Portal da Transparência do Amazonas.
https://www.transparencia.am.gov.br/pessoal/

COMO FUNCIONA:
  1. Para cada órgão × ano, chama a API WordPress (admin-ajax.php) com
     action=get_meses_docs para obter as URLs reais dos CSVs.
  2. Baixa cada CSV usando _download_utils.py (streaming + resume).
  3. Salva em: data/transparencia_am/{orgao_slug}/{ano}/{arquivo}.csv

API INTERNA:
  POST https://www.transparencia.am.gov.br/wp-admin/admin-ajax.php
  Body: action=get_meses_docs&ano={ano}&orgao_id={id}
  Resposta: JSON com lista de meses e URLs dos arquivos

ESTRUTURA DO CSV (separado por ;):
  NOME; LOTACAO; CARGO; CLASSE/PADRÃO; FUNCAO; CARGA HR SEM;
  DT DE ADMISSAO; VINCULO; REMUNERACAO LEGAL TOTAL(R$); DESC.TETO(R$);
  REMUNERACAO LEGAL DEVIDA(R$); DESCONTOS LEGAIS(R$); LIQUIDO DISPONIVEL(R$)

ANOS DISPONÍVEIS: 2014 a 2026
ÓRGÃOS: 80 órgãos do Poder Executivo Estadual do Amazonas

USO:
  cd ~/Downloads/br-acc-novo/etl
  source ~/.local/bin/env
  uv run python scripts/download_transparencia_am.py --output-dir ../data/transparencia_am

REGRAS OBRIGATÓRIAS DO PROJETO:
  - SEMPRE usar _download_utils.download_file() — nunca requests puro
  - Confirmar antes de executar downloads massivos
  - Comandos longos em linha única (Git Bash trava com multilinha)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import httpx

# Adiciona o diretório scripts ao path para importar _download_utils
sys.path.insert(0, str(Path(__file__).parent))
from _download_utils import download_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapa completo de órgãos — obtido via Vue $data.orgaos em 12/05/2026
# Formato: {"nome_orgao": "...", "id": "..."}
# O campo "id" é o orgao_id usado na API admin-ajax.php
# ---------------------------------------------------------------------------
ORGAOS = [
    {"nome": "ADAF",                      "id": "76"},
    {"nome": "ADS",                       "id": "445"},
    {"nome": "APOSENTADOS_EXECUTIVO",     "id": "127"},
    {"nome": "APOSENTADOS_ALEAM",         "id": "10113"},
    {"nome": "APOSENTADOS_PGJ",           "id": "10108"},
    {"nome": "APOSENTADOS_TCE",           "id": "10106"},
    {"nome": "APOSENTADOS_TJA",           "id": "10110"},
    {"nome": "ARSEPAM",                   "id": "93"},
    {"nome": "CASA_CIVIL",                "id": "77"},
    {"nome": "CASA_MILITAR",              "id": "94"},
    {"nome": "CB_CIVIS",                  "id": "95"},
    {"nome": "CBMAM",                     "id": "96"},
    {"nome": "CETAM",                     "id": "74"},
    {"nome": "CGE",                       "id": "75"},
    {"nome": "CSC",                       "id": "97"},
    {"nome": "DEFESA_CIVIL",              "id": "13891"},
    {"nome": "DETRAN",                    "id": "98"},
    {"nome": "ERGSP",                     "id": "99"},
    {"nome": "FAAR",                      "id": "4572"},
    {"nome": "FAPEAM",                    "id": "100"},
    {"nome": "FCECON",                    "id": "101"},
    {"nome": "FEH",                       "id": "86"},
    {"nome": "FEPIAM",                    "id": "396"},
    {"nome": "FHAJ",                      "id": "102"},
    {"nome": "FHEMOAM",                   "id": "103"},
    {"nome": "FMT_AM",                    "id": "104"},
    {"nome": "FUHAM",                     "id": "92"},
    {"nome": "FUNATI",                    "id": "12954"},
    {"nome": "FUNDACAO_AMAZONPREV",       "id": "87"},
    {"nome": "FUNDACAO_VILA_OLIMPICA",    "id": "105"},
    {"nome": "FUNTEC",                    "id": "106"},
    {"nome": "FVS",                       "id": "17"},
    {"nome": "IDAM",                      "id": "107"},
    {"nome": "IMPRENSA_OFICIAL",          "id": "108"},
    {"nome": "IPAAM",                     "id": "109"},
    {"nome": "IPEM_AM",                   "id": "110"},
    {"nome": "JUCEA",                     "id": "111"},
    {"nome": "OUVIDORIA_GERAL",           "id": "112"},
    {"nome": "PENSIONISTAS_EXECUTIVO",    "id": "128"},
    {"nome": "PENSIONISTAS_ALEAM",        "id": "10112"},
    {"nome": "PENSIONISTAS_PGJ",          "id": "10107"},
    {"nome": "PENSIONISTAS_TCE",          "id": "10105"},
    {"nome": "PENSIONISTAS_TJA",          "id": "10109"},
    {"nome": "PGE",                       "id": "80"},
    {"nome": "PM_ATIVOS",                 "id": "113"},
    {"nome": "PM_CIVIS",                  "id": "114"},
    {"nome": "POLICIA_CIVIL",             "id": "115"},
    {"nome": "PROCON",                    "id": "4573"},
    {"nome": "PRODAM",                    "id": "136"},
    {"nome": "SEAD",                      "id": "90"},
    {"nome": "SEAD_PENSAO_ESPECIAL_I",    "id": "129"},
    {"nome": "SEAD_PENSAO_ESPECIAL_II",   "id": "133"},
    {"nome": "SEAD_PENSAO_HANSENIANOS",   "id": "132"},
    {"nome": "SEAP",                      "id": "73"},
    {"nome": "SEAS",                      "id": "82"},
    {"nome": "SEC",                       "id": "126"},
    {"nome": "SECOM",                     "id": "72"},
    {"nome": "SECT",                      "id": "122"},
    {"nome": "SEDECTI",                   "id": "83"},
    {"nome": "SEDEL",                     "id": "13378"},
    {"nome": "SEDUC",                     "id": "91"},
    {"nome": "SEDURB",                    "id": "13748"},
    {"nome": "SEFAZ",                     "id": "89"},
    {"nome": "SEGOV",                     "id": "13280"},
    {"nome": "SEIND",                     "id": "22"},
    {"nome": "SEINFRA",                   "id": "116"},
    {"nome": "SEJEL",                     "id": "117"},
    {"nome": "SEJUSC",                    "id": "84"},
    {"nome": "SEMA",                      "id": "81"},
    {"nome": "SEMIG",                     "id": "13281"},
    {"nome": "SEPA",                      "id": "14377"},
    {"nome": "SEPCD",                     "id": "14378"},
    {"nome": "SEPED",                     "id": "118"},
    {"nome": "SEPET",                     "id": "14376"},
    {"nome": "SEPROR",                    "id": "119"},
    {"nome": "SERFI",                     "id": "397"},
    {"nome": "SERGB",                     "id": "79"},
    {"nome": "SES",                       "id": "88"},
    {"nome": "SETRAB",                    "id": "120"},
    {"nome": "SGVG",                      "id": "78"},
    {"nome": "SNPH",                      "id": "121"},
    {"nome": "SRMM",                      "id": "71"},
    {"nome": "SSP",                       "id": "123"},
    {"nome": "SUHAB",                     "id": "124"},
    {"nome": "UEA",                       "id": "125"},
    {"nome": "UGPADEAM",                  "id": "13800"},
    {"nome": "UGPE",                      "id": "85"},
]

# Anos disponíveis no portal
ANOS = list(range(2014, 2027))  # 2014 a 2026

API_URL = "https://www.transparencia.am.gov.br/wp-admin/admin-ajax.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.transparencia.am.gov.br/pessoal/",
}


def get_urls_for_orgao_ano(orgao_id: str, ano: int) -> list[dict]:
    """Chama admin-ajax.php e retorna lista de {mes, url_csv}."""
    try:
        resp = httpx.post(
            API_URL,
            data=f"action=get_meses_docs&ano={ano}&orgao_id={orgao_id}",
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "error" in data:
            # Órgão não tem dados para este ano — normal
            return []
        results = []
        for mes_info in data:
            for arq in mes_info.get("arquivos", []):
                if arq["extensao"] == ".csv":
                    results.append({
                        "mes": mes_info["mes"],
                        "mes_descricao": mes_info["mes_descricao"],
                        "url": arq["url"],
                    })
        return results
    except Exception as e:
        logger.warning("Erro ao consultar órgão %s ano %s: %s", orgao_id, ano, e)
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Transparência AM — Servidores")
    parser.add_argument("--output-dir", required=True, help="Diretório de saída, ex: ../data/transparencia_am")
    parser.add_argument("--orgao", help="Baixar só este órgão (ex: SEFAZ)")
    parser.add_argument("--ano", type=int, help="Baixar só este ano (ex: 2026)")
    parser.add_argument("--dry-run", action="store_true", help="Listar arquivos sem baixar")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    orgaos = ORGAOS
    if args.orgao:
        orgaos = [o for o in ORGAOS if o["nome"].upper() == args.orgao.upper()]
        if not orgaos:
            logger.error("Órgão '%s' não encontrado. Opções: %s", args.orgao, [o["nome"] for o in ORGAOS])
            sys.exit(1)

    anos = ANOS
    if args.ano:
        anos = [args.ano]

    total_baixados = 0
    total_pulados = 0
    total_erros = 0

    for orgao in orgaos:
        for ano in anos:
            logger.info("Consultando %s / %s...", orgao["nome"], ano)
            urls = get_urls_for_orgao_ano(orgao["id"], ano)

            if not urls:
                logger.debug("  Sem dados para %s/%s", orgao["nome"], ano)
                continue

            for item in urls:
                url = item["url"]
                filename = url.split("/")[-1]
                dest_dir = output_dir / orgao["nome"] / str(ano)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / filename

                if dest.exists():
                    logger.info("  Já existe: %s", filename)
                    total_pulados += 1
                    continue

                if args.dry_run:
                    logger.info("  [DRY-RUN] %s → %s", url, dest)
                    continue

                logger.info("  Baixando %s/%s %s...", orgao["nome"], ano, item["mes_descricao"])
                ok = download_file(url, dest)
                if ok:
                    total_baixados += 1
                else:
                    total_erros += 1

            # Pausa entre órgãos para não sobrecarregar o servidor
            time.sleep(0.5)

    logger.info("=" * 50)
    logger.info("CONCLUÍDO — Baixados: %d | Pulados: %d | Erros: %d",
                total_baixados, total_pulados, total_erros)


if __name__ == "__main__":
    main()
