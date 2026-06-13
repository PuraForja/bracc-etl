#!/usr/bin/env python3
"""Download Obras.gov federal infrastructure projects via REST API.

Fetches physical infrastructure projects (obras) from the Obras.gov public API.
Saves paginated JSON files for ObrasPipeline consumption.

API: https://api.obras.gov.br/api/v2/empreendimentos
Docs: https://www.gov.br/transferegov/pt-br/acesso-a-informacao/dados-abertos

Usage:
    python etl/scripts/download_obras.py
    python etl/scripts/download_obras.py --output-dir ./data/obras
    python etl/scripts/download_obras.py --uf AM
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import click
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

API_BASE = "https://api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento"
PAGE_SIZE = 100
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5.0
REQUEST_DELAY_SECONDS = 1.0


def _fetch_page(
    client: httpx.Client,
    page: int,
    uf: str | None,
    timeout: int,
) -> dict | None:
    """Fetch a single page from the Obras.gov API."""
    params: dict = {"pagina": page, "tamanhoPagina": PAGE_SIZE}
    if uf:
        params["uf"] = uf.upper()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.get(API_BASE, params=params, timeout=timeout)
            if response.status_code == 204:
                return None
            response.raise_for_status()
            text = response.text.strip()
            if not text:
                return None
            return json.loads(text, strict=False)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (400, 404):
                return None
            if e.response.status_code == 429:
                wait = RETRY_BACKOFF_SECONDS * attempt * 2
                logger.warning("Rate limited (429), waiting %.0fs (attempt %d/%d)", wait, attempt, MAX_RETRIES)
                time.sleep(wait)
                continue
            if attempt < MAX_RETRIES:
                logger.warning(
                    "HTTP %d page=%d (attempt %d/%d)",
                    e.response.status_code, page, attempt, MAX_RETRIES,
                )
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            logger.warning("Giving up on page %d after %d attempts", page, MAX_RETRIES)
            return None
        except httpx.HTTPError as e:
            if attempt < MAX_RETRIES:
                logger.warning("Network error page=%d (attempt %d/%d): %s", page, attempt, MAX_RETRIES, e)
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            return None
    return None


def _load_checkpoint(path: Path) -> set[int]:
    if not path.exists():
        return set()
    try:
        return {int(x) for x in path.read_text(encoding="utf-8").strip().splitlines() if x.isdigit()}
    except OSError:
        return set()


def _save_checkpoint(path: Path, page: int) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{page}\n")


def _flush_page(out_dir: Path, page: int, records: list[dict]) -> None:
    out_file = out_dir / f"obras_page_{page:05d}.json"
    out_file.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")


@click.command()
@click.option("--output-dir", default="./data/obras", help="Output directory")
@click.option("--uf", default=None, help="Filter by UF (ex: AM). Default: all Brazil.")
@click.option("--skip-existing/--no-skip-existing", default=True)
@click.option("--timeout", type=int, default=90, help="HTTP timeout in seconds")
@click.option(
    "--request-delay",
    type=float,
    default=REQUEST_DELAY_SECONDS,
    help="Delay between requests in seconds",
)
def main(
    output_dir: str,
    uf: str | None,
    skip_existing: bool,
    timeout: int,
    request_delay: float,
) -> None:
    """Download Obras.gov federal infrastructure projects."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    logger.info("=== Obras.gov Download ===")
    logger.info("Output: %s | UF filter: %s", out, uf or "all")

    checkpoint_file = out / ".checkpoint"
    completed_pages = _load_checkpoint(checkpoint_file) if skip_existing else set()
    if completed_pages:
        logger.info("Resuming: %d pages already completed", len(completed_pages))

    client = httpx.Client(
        follow_redirects=True,
        headers={"User-Agent": "BR-ACC-ETL/1.0 (public data research)"},
    )

    total_records = 0
    page = 1

    try:
        while True:
            if page in completed_pages:
                page += 1
                continue

            logger.info("Fetching page %d...", page)
            data = _fetch_page(client, page, uf, timeout)

            if data is None:
                logger.info("No more data at page %d — finished.", page)
                break

            # Handle both list and wrapped response
            if isinstance(data, list):
                records = data
                total_pages = None
            elif isinstance(data, dict):
                records = data.get("data") or data.get("content") or data.get("empreendimentos") or []
                total_pages = data.get("totalPaginas") or data.get("totalPages")
            else:
                logger.warning("Unexpected response format at page %d", page)
                break

            if not records:
                logger.info("Empty page %d — finished.", page)
                break

            _flush_page(out, page, records)
            _save_checkpoint(checkpoint_file, page)
            total_records += len(records)

            logger.info("  Page %d: %d records (total: %d)", page, len(records), total_records)

            if total_pages and page >= int(total_pages):
                logger.info("Reached last page (%d).", total_pages)
                break

            page += 1
            if request_delay > 0:
                time.sleep(request_delay)

    except KeyboardInterrupt:
        logger.info("Interrupted. Progress saved — rerun with --skip-existing to resume.")
    finally:
        client.close()

    logger.info("=== Done: %d total records across %d pages ===", total_records, page - 1)


if __name__ == "__main__":
    main()
