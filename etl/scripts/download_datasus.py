"""Download DATASUS CNES data via S3 (dadosabertos.saude.gov.br)."""
from __future__ import annotations
import logging
import sys
import zipfile
from pathlib import Path
from _download_utils import download_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

URL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/CNES/cnes_estabelecimentos_csv.zip"
OUTPUT_DIR = Path("../data/datasus")
ZIP_FILE = OUTPUT_DIR / "cnes_estabelecimentos_csv.zip"
OUTPUT_CSV = OUTPUT_DIR / "cnes_all.csv"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Baixando CNES Estabelecimentos (~54MB)...")
    ok = download_file(URL, ZIP_FILE)
    if not ok:
        logger.error("Falha no download — abortando")
        sys.exit(1)

    logger.info("Extraindo ZIP...")
    with zipfile.ZipFile(ZIP_FILE, "r") as z:
        csvs = [f for f in z.namelist() if f.lower().endswith(".csv")]
        logger.info("Arquivos no ZIP: %s", csvs)
        if not csvs:
            logger.error("Nenhum CSV encontrado no ZIP")
            sys.exit(1)

        with z.open(csvs[0]) as src, open(OUTPUT_CSV, "wb") as dst:
            dst.write(src.read())

    logger.info("Salvo: %s", OUTPUT_CSV)
    logger.info("Tamanho: %.1f MB", OUTPUT_CSV.stat().st_size / 1e6)
    logger.info("✅ CNES pronto — rode: bracc-etl run --source datasus")


if __name__ == "__main__":
    main()
