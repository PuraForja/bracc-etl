#!/usr/bin/env python3
"""Download TransfereGov parliamentary amendments bulk ZIP from Portal da Transparência.

Source: https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares
Redirects to: https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/

Usage:
    uv run python scripts/download_transferegov.py --output-dir ../data/transferegov
"""
from __future__ import annotations
import logging
import sys
from pathlib import Path
import click
from _download_utils import download_file, safe_extract_zip

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PORTAL_URL = "https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/2024"
REFERER = "https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares"
ZIP_NAME = "EmendasParlamentares.zip"
EXPECTED_FILES = [
    "EmendasParlamentares.csv",
    "EmendasParlamentares_PorFavorecido.csv",
    "EmendasParlamentares_Convenios.csv",
]

@click.command()
@click.option("--output-dir", default="./data/transferegov", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True)
@click.option("--timeout", type=int, default=600)
def main(output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download TransfereGov parliamentary amendments ZIP."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    logger.info("=== TransfereGov Download ===")
    if skip_existing and all((out / f).exists() for f in EXPECTED_FILES):
        logger.info("Todos os CSVs ja existem — pulando download")
        return
    zip_dest = out / ZIP_NAME
    logger.info("Baixando %s...", PORTAL_URL)
    ok = download_file(PORTAL_URL, zip_dest, timeout=timeout, referer=REFERER)
    if not ok:
        logger.error("Falha no download do ZIP")
        sys.exit(1)
    extracted = safe_extract_zip(zip_dest, out)
    if not extracted:
        logger.error("Falha na extracao do ZIP")
        sys.exit(1)
    missing = [f for f in EXPECTED_FILES if not (out / f).exists()]
    if missing:
        logger.warning("Arquivos nao encontrados: %s", missing)
    else:
        logger.info("Todos os CSVs extraidos com sucesso")
    if zip_dest.exists():
        zip_dest.unlink()
    logger.info("=== Done ===")

if __name__ == "__main__":
    main()
