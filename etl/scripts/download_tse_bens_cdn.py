#!/usr/bin/env python3
"""Download TSE Bens Declarados direto do CDN do TSE (sem BigQuery).
Usage:
    python etl/scripts/download_tse_bens_cdn.py --output-dir ./data/tse_bens
    python etl/scripts/download_tse_bens_cdn.py --output-dir ./data/tse_bens --years 2018 2022
"""
from __future__ import annotations
import logging
import sys
from pathlib import Path
import click
sys.path.insert(0, str(Path(__file__).parent))
from _download_utils import download_file, extract_zip
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TSE_CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato"
DEFAULT_YEARS = [2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024]

@click.command()
@click.option("--output-dir", default="./data/tse_bens", help="Output directory")
@click.option("--years", multiple=True, type=int, default=DEFAULT_YEARS, help="Election years")
@click.option("--skip-existing", is_flag=True, default=True, help="Skip existing ZIPs")
def main(output_dir: str, years: tuple, skip_existing: bool) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_dir = out / "raw"
    raw_dir.mkdir(exist_ok=True)

    for year in sorted(years):
        url = f"{TSE_CDN}/bem_candidato_{year}.zip"
        zip_path = raw_dir / f"bem_candidato_{year}.zip"
        if skip_existing and zip_path.exists():
            logger.info("Skipping (exists): %s", zip_path.name)
            continue
        logger.info("Downloading %d...", year)
        try:
            download_file(url, zip_path)
            extract_zip(zip_path, raw_dir / f"bens_{year}_extracted")
            logger.info("Done: %d", year)
        except Exception as e:
            logger.warning("Failed %d: %s", year, e)

    # Consolida todos os CSVs em bens.csv
    import pandas as pd
    frames = []
    for year in sorted(years):
        ext_dir = raw_dir / f"bens_{year}_extracted"
        if not ext_dir.exists():
            continue
        for csv_file in ext_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file, sep=";", encoding="latin-1", dtype=str)
                frames.append(df)
                logger.info("Loaded: %s (%d rows)", csv_file.name, len(df))
            except Exception as e:
                logger.warning("Failed to load %s: %s", csv_file.name, e)

    if frames:
        combined = pd.concat(frames, ignore_index=True)

        # JOIN com candidatos.csv para obter CPF via SQ_CANDIDATO
        candidatos_path = Path(output_dir).parent / "tse" / "candidatos.csv"
        if candidatos_path.exists():
            logger.info("Cruzando com candidatos.csv para obter CPF...")
            cands = pd.read_csv(candidatos_path, encoding="latin-1", dtype=str,
                                usecols=["sq_candidato", "cpf", "nome"])
            cands = cands.dropna(subset=["sq_candidato"])
            cands["SQ_CANDIDATO"] = cands["sq_candidato"].str.strip()
            combined["SQ_CANDIDATO"] = combined["SQ_CANDIDATO"].str.strip()
            combined = combined.merge(cands[["SQ_CANDIDATO", "cpf", "nome"]],
                                      on="SQ_CANDIDATO", how="left")
            matched = combined["cpf"].notna().sum()
            logger.info("CPF encontrado para %d/%d registros", matched, len(combined))
        else:
            logger.warning("candidatos.csv nao encontrado em %s", candidatos_path)

        dest = out / "bens.csv"
        combined.to_csv(dest, index=False, encoding="latin-1")
        logger.info("Wrote %d rows to %s", len(combined), dest)
    else:
        logger.warning("Nenhum CSV encontrado")

if __name__ == "__main__":
    main()
    sys.exit(0)
