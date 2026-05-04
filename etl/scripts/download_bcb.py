#!/usr/bin/env python3
"""Download BCB (Banco Central do Brasil) penalties data via API Olinda.
Usage:
    python etl/scripts/download_bcb.py
    python etl/scripts/download_bcb.py --output-dir ./data/bcb
"""
from __future__ import annotations
import json
import logging
import sys
import time
from pathlib import Path
import click
import pandas as pd
import urllib.request
sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
API_BASE = "https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata"
ENDPOINT = "QuadroGeralProcessoAdministrativoSancionador"
PAGE_SIZE = 500
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def _fetch_page(skip: int, timeout: int) -> list:
    url = f"{API_BASE}/{ENDPOINT}?$format=json&$top={PAGE_SIZE}&$skip={skip}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read())
    return data.get("value", [])

def _download_penalties(output_dir: Path, *, skip_existing: bool, timeout: int) -> Path | None:
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "penalidades_raw.csv"
    if skip_existing and csv_path.exists():
        logger.info("Skipping (exists): %s", csv_path.name)
        return csv_path
    logger.info("Downloading BCB penalties via API Olinda...")
    all_records = []
    skip = 0
    while True:
        try:
            records = _fetch_page(skip, timeout)
        except Exception as e:
            logger.warning("Error fetching page skip=%d: %s — retrying in 5s", skip, e)
            time.sleep(5)
            try:
                records = _fetch_page(skip, timeout)
            except Exception as e2:
                logger.error("Failed after retry: %s", e2)
                return None
        if not records:
            break
        all_records.extend(records)
        logger.info("  Baixados: %d registros...", len(all_records))
        if len(records) < PAGE_SIZE:
            break
        skip += PAGE_SIZE
        time.sleep(0.5)
    if not all_records:
        logger.error("Nenhum registro retornado pela API")
        return None
    df = pd.DataFrame(all_records)
    df.to_csv(csv_path, sep=";", index=False, encoding="utf-8")
    logger.info("Salvos %d registros em %s", len(df), csv_path)
    return csv_path

def _process_csv(csv_path: Path, output_path: Path) -> bool:
    try:
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8", dtype=str, keep_default_na=False)
    except Exception as e:
        logger.warning("Failed to read %s: %s", csv_path, e)
        return False
    logger.info("BCB penalties: %d rows, columns: %s", len(df), list(df.columns))
    df.to_csv(output_path, sep=";", index=False, encoding="utf-8")
    logger.info("Wrote %d rows to %s", len(df), output_path)
    return True

@click.command()
@click.option("--output-dir", default="./data/bcb", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True, help="Skip existing files")
@click.option("--timeout", type=int, default=60, help="Timeout por requisicao em segundos")
def main(output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download BCB penalties data via API Olinda."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    logger.info("=== BCB Penalties (API Olinda) ===")
    csv_path = _download_penalties(out, skip_existing=skip_existing, timeout=timeout)
    if csv_path is None:
        logger.warning("Failed to download BCB penalties")
        sys.exit(1)
    output_path = out / "penalidades.csv"
    if not _process_csv(csv_path, output_path):
        sys.exit(1)
    logger.info("=== Done ===")

if __name__ == "__main__":
    main()