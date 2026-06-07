#!/usr/bin/env python3
"""
download_servidores_federais.py
================================
Download de Servidores Federais do Portal da Transparência (CGU).
Filtra por UF_EXERCICIO=AM e salva CSV reduzido em data/servidores_federais/.

USO:
  cd ~/bracc/etl
  uv run python scripts/download_servidores_federais.py --output-dir ../data/servidores_federais
  uv run python scripts/download_servidores_federais.py --output-dir ../data/servidores_federais --ano-mes 202603

REGRAS:
  - Usar httpx com timeout e retry — nunca requests puro
  - Tentar D-1, D-2 etc se arquivo do mês atual não existir (403)
  - Filtrar só AM para reduzir volume
  - Deletar ZIP após extração
"""
from __future__ import annotations
import argparse
import logging
import sys
import zipfile
from datetime import date, timedelta
from pathlib import Path

import httpx
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _download_utils import download_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://portaldatransparencia.gov.br/download-de-dados/servidores"
REFERER = "https://portaldatransparencia.gov.br/download-de-dados/servidores"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": REFERER,
}


def find_latest_ano_mes(max_months: int = 6) -> str | None:
    """Tenta meses retroativos até encontrar arquivo disponível."""
    d = date.today().replace(day=1)
    for _ in range(max_months):
        d = (d - timedelta(days=1)).replace(day=1)
        ano_mes = d.strftime("%Y%m")
        url = f"{BASE_URL}/{ano_mes}_Servidores_SIAPE"
        try:
            r = httpx.head(url, headers=HEADERS, timeout=15, follow_redirects=True)
            if r.status_code == 200:
                logger.info("Arquivo disponível: %s", ano_mes)
                return ano_mes
            logger.info("Mês %s retornou %s — tentando anterior", ano_mes, r.status_code)
        except Exception as e:
            logger.warning("Erro ao testar %s: %s", ano_mes, e)
    return None


def download_e_filtra(ano_mes: str, output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_final = output_dir / f"servidores_federais_AM_{ano_mes}.csv"

    if csv_final.exists():
        logger.info("Arquivo já existe: %s — pulando", csv_final.name)
        return True

    url = f"{BASE_URL}/{ano_mes}_Servidores_SIAPE"
    zip_dest = output_dir / f"{ano_mes}_servidores.zip"

    logger.info("Baixando %s...", url)
    try:
        download_file(url, zip_dest, headers=HEADERS)
    except Exception as e:
        logger.error("Falha no download: %s", e)
        return False

    logger.info("Extraindo e filtrando AM...")
    try:
        with zipfile.ZipFile(zip_dest, "r") as z:
            cadastro = next(
                (n for n in z.namelist() if "Cadastro" in n and n.endswith(".csv")),
                None,
            )
            if not cadastro:
                logger.error("Arquivo Cadastro não encontrado no ZIP")
                return False

            chunks = []
            with z.open(cadastro) as f:
                for chunk in pd.read_csv(
                    f, sep=";", encoding="iso-8859-1",
                    chunksize=50_000, dtype=str,
                ):
                    chunk.columns = chunk.columns.str.strip().str.upper()
                    filtered = chunk[chunk.get("UF_EXERCICIO", pd.Series()) == "AM"]
                    if not filtered.empty:
                        chunks.append(filtered)

        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            df.to_csv(csv_final, sep=";", index=False, encoding="utf-8")
            logger.info("Salvos %d servidores AM em %s", len(df), csv_final)
        else:
            logger.warning("Nenhum servidor AM encontrado")

    except zipfile.BadZipFile:
        logger.error("ZIP corrompido")
        return False
    finally:
        if zip_dest.exists():
            zip_dest.unlink()
            logger.info("ZIP removido")

    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="./data/servidores_federais")
    parser.add_argument("--ano-mes", default=None, help="Ex: 202604")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    ano_mes = args.ano_mes

    if not ano_mes:
        logger.info("Buscando mês mais recente disponível...")
        ano_mes = find_latest_ano_mes()
        if not ano_mes:
            logger.error("Nenhum arquivo disponível nos últimos 6 meses")
            sys.exit(1)

    sucesso = download_e_filtra(ano_mes, output_dir)
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()
