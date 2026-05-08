#!/usr/bin/env python3
"""Download World Bank debarred firms and individuals via OpenSanctions.

Source: https://data.opensanctions.org/datasets/latest/worldbank_debarred/
Formato: CSV simplificado com entidades sancionadas pelo World Bank Group.
Sem autenticação necessária.
"""
from __future__ import annotations

import logging
from pathlib import Path

import click
import httpx

logger = logging.getLogger(__name__)

# OpenSanctions publica o dataset do World Bank processado e atualizado
WB_URL = (
    "https://data.opensanctions.org/datasets/latest/worldbank_debarred/targets.simple.csv"
)


def _download(dest: Path, timeout: int) -> bool:
    """Baixa o CSV do World Bank via OpenSanctions."""
    logger.info("Baixando World Bank debarred list: %s", WB_URL)
    try:
        with httpx.stream("GET", WB_URL, follow_redirects=True, timeout=timeout) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        size_kb = dest.stat().st_size // 1024
        logger.info("Download concluído: %s (%d KB)", dest, size_kb)
        return True
    except httpx.HTTPError as exc:
        logger.error("Falha no download: %s", exc)
        return False


@click.command()
@click.option("--output-dir", default="./data/world_bank", help="Diretório de saída")
@click.option("--skip-existing/--no-skip-existing", default=True)
@click.option("--timeout", type=int, default=120, help="Timeout HTTP em segundos")
def main(output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download World Bank debarred firms list via OpenSanctions."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "debarred.csv"

    if skip_existing and dest.exists():
        logger.info("Arquivo já existe, pulando: %s", dest)
        return

    if not _download(dest, timeout):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
