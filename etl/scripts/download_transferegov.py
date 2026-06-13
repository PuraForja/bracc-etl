#!/usr/bin/env python3
"""Download TransfereGov parliamentary amendments bulk CSV files.

Sources: Portal da Transparência federal bulk download.
Three files:
  - EmendasParlamentares.csv
  - EmendasParlamentares_PorFavorecido.csv
  - EmendasParlamentares_Convenios.csv

Usage:
    python etl/scripts/download_transferegov.py
    python etl/scripts/download_transferegov.py --output-dir ./data/transferegov
    python etl/scripts/download_transferegov.py --skip-existing
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

import click
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares"

FILES = [
    "EmendasParlamentares.csv",
    "EmendasParlamentares_PorFavorecido.csv",
    "EmendasParlamentares_Convenios.csv",
]

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5.0
CHUNK_SIZE = 8192


def _download_file(
    client: httpx.Client,
    url: str,
    dest: Path,
) -> bool:
    """Download a single file with retry logic. Returns True on success."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("  Downloading %s (attempt %d/%d)...", url, attempt, MAX_RETRIES)
            with client.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                downloaded = 0
                with dest.open("wb") as f:
                    for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
                        downloaded += len(chunk)
                if total and downloaded < total:
                    logger.warning(
                        "  Incomplete download: got %d of %d bytes", downloaded, total
                    )
                    dest.unlink(missing_ok=True)
                    continue
                logger.info("  Saved %d bytes to %s", downloaded, dest.name)
                return True
        except httpx.HTTPStatusError as e:
            logger.warning(
                "  HTTP %d for %s (attempt %d/%d)",
                e.response.status_code, url, attempt, MAX_RETRIES,
            )
            dest.unlink(missing_ok=True)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
        except httpx.HTTPError as e:
            logger.warning(
                "  Network error for %s (attempt %d/%d): %s",
                url, attempt, MAX_RETRIES, e,
            )
            dest.unlink(missing_ok=True)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    logger.error("  Gave up on %s after %d attempts", url, MAX_RETRIES)
    return False


@click.command()
@click.option("--output-dir", default="./data/transferegov", help="Output directory")
@click.option(
    "--skip-existing/--no-skip-existing",
    default=True,
    help="Skip files that already exist on disk",
)
@click.option("--timeout", type=int, default=300, help="HTTP request timeout in seconds")
def main(output_dir: str, skip_existing: bool, timeout: int) -> None:
    """Download TransfereGov parliamentary amendments CSV files."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    logger.info("=== TransfereGov Download ===")
    logger.info("Output: %s", out)

    client = httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": "BR-ACC-ETL/1.0 (public data research)"},
    )

    success = 0
    skipped = 0
    failed = 0

    try:
        for filename in FILES:
            dest = out / filename
            if skip_existing and dest.exists() and dest.stat().st_size > 0:
                logger.info("  Skipping %s (already exists)", filename)
                skipped += 1
                continue

            url = f"{BASE_URL}/{filename}"
            ok = _download_file(client, url, dest)
            if ok:
                success += 1
            else:
                failed += 1
    finally:
        client.close()

    logger.info(
        "=== Done: %d downloaded, %d skipped, %d failed ===",
        success, skipped, failed,
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
