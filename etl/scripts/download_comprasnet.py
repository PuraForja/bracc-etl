#!/usr/bin/env python3
"""Download PNCP federal contracts via REST API.

Fetches executed contracts (not bids) from the PNCP public API.
Saves monthly JSON files for ComprasnetPipeline consumption.

API: https://pncp.gov.br/api/consulta/v1/contratos
Swagger: https://pncp.gov.br/api/consulta/swagger-ui/index.html

Usage:
    python etl/scripts/download_comprasnet.py
    python etl/scripts/download_comprasnet.py --start-date 2021-01-01 --end-date 2026-02-25
    python etl/scripts/download_comprasnet.py --output-dir ./data/comprasnet
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import click
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

API_BASE = "https://pncp.gov.br/api/consulta/v1/contratos"

MAX_PAGE_SIZE = 50
MAX_DATE_RANGE_DAYS = 2
REQUEST_DELAY_SECONDS = 1.0
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5.0


def _fetch_page(
    client: httpx.Client,
    date_start: str,
    date_end: str,
    page: int,
    timeout: int,
) -> dict | None:
    """Fetch a single page from the PNCP contracts API."""
    params = {
        "dataInicial": date_start,
        "dataFinal": date_end,
        "pagina": page,
        "tamanhoPagina": MAX_PAGE_SIZE,
    }
    response = client.get(API_BASE, params=params, timeout=timeout)
    if response.status_code == 204:
        return None
    response.raise_for_status()
    text = response.text.strip()
    if not text:
        return None
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        return None


def _fetch_window(
    client: httpx.Client,
    date_start: str,
    date_end: str,
    timeout: int,
) -> list[dict]:
    """Fetch all pages for a single date window."""

    def fetch_with_retry(page: int) -> dict | None:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return _fetch_page(client, date_start, date_end, page, timeout)
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (400, 404):
                    return None
                if e.response.status_code == 429:
                    wait = RETRY_BACKOFF_SECONDS * attempt * 2
                    logger.warning("Rate limited (429), waiting %.0fs", wait)
                    time.sleep(wait)
                    continue
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue
                return None
            except httpx.HTTPError as e:
                if attempt < MAX_RETRIES:
                    logger.warning("Network error (attempt %d/%d): %s", attempt, MAX_RETRIES, e)
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue
                return None
        return None

    first = fetch_with_retry(1)
    if first is None:
        return []
    items = first.get("data", [])
    if not items or first.get("empty", True):
        return []

    all_records: list[dict] = list(items)
    total_pages = int(first.get("totalPaginas", 1) or 1)

    for page in range(2, total_pages + 1):
        data = fetch_with_retry(page)
        if data is None:
            continue
        page_items = data.get("data", [])
        if page_items and not data.get("empty", False):
            all_records.extend(page_items)
        time.sleep(REQUEST_DELAY_SECONDS)

    return all_records


def _date_windows(start: datetime, end: datetime) -> list[tuple[str, str]]:
    windows: list[tuple[str, str]] = []
    current = start
    while current <= end:
        window_end = min(current + timedelta(days=MAX_DATE_RANGE_DAYS - 1), end)
        windows.append((current.strftime("%Y%m%d"), window_end.strftime("%Y%m%d")))
        current = window_end + timedelta(days=1)
    return windows


def _month_key(rec: dict, fallback: str) -> str:
    raw = str(rec.get("dataAssinatura", fallback))
    if len(raw) >= 7:
        return raw[:7].replace("-", "")
    return fallback[:6]


def _flush_to_disk(out_dir: Path, month_key: str, new_records: list[dict]) -> int:
    out_file = out_dir / f"comprasnet_{month_key}_contratos.json"
    existing: list[dict] = []
    if out_file.exists():
        try:
            raw = json.loads(out_file.read_text(encoding="utf-8"), strict=False)
            existing = raw if isinstance(raw, list) else []
        except (json.JSONDecodeError, OSError):
            pass

    seen: set[str] = {str(r.get("numeroControlePNCP", "")) for r in existing}
    unique = [r for r in new_records if str(r.get("numeroControlePNCP", "")) not in seen]
    merged = existing + unique
    out_file.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
    return len(merged)


def _load_checkpoint(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        return set(path.read_text(encoding="utf-8").strip().splitlines())
    except OSError:
        return set()


def _save_checkpoint(path: Path, key: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(key + "\n")


@click.command()
@click.option("--start-date", default="2021-01-01", help="Start date (YYYY-MM-DD)")
@click.option(
    "--end-date",
    default=lambda: datetime.now().strftime("%Y-%m-%d"),
    help="End date (YYYY-MM-DD). Default: today.",
)
@click.option("--output-dir", default="./data/comprasnet", help="Output directory")
@click.option("--skip-existing/--no-skip-existing", default=True)
@click.option("--timeout", type=int, default=90, help="HTTP timeout in seconds")
@click.option(
    "--request-delay",
    type=float,
    default=REQUEST_DELAY_SECONDS,
    help="Delay between requests in seconds",
)
def main(
    start_date: str,
    end_date: str,
    output_dir: str,
    skip_existing: bool,
    timeout: int,
    request_delay: float,
) -> None:
    """Download PNCP executed contracts (comprasnet)."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    windows = _date_windows(start, end)

    logger.info("=== Comprasnet/PNCP Contracts Download ===")
    logger.info("Date range: %s to %s — %d windows", start_date, end_date, len(windows))

    checkpoint_file = out / ".checkpoint"
    completed = _load_checkpoint(checkpoint_file) if skip_existing else set()
    if completed:
        logger.info("Resuming: %d windows already completed", len(completed))

    client = httpx.Client(
        follow_redirects=True,
        headers={"User-Agent": "BR-ACC-ETL/1.0 (public data research)"},
    )

    total_records = 0
    done = len(completed)

    try:
        for win_start, win_end in windows:
            key = f"{win_start}_{win_end}"
            if key in completed:
                continue

            logger.info("[%d/%d] Fetching %s-%s...", done + 1, len(windows), win_start, win_end)
            records = _fetch_window(client, win_start, win_end, timeout)

            if records:
                by_month: dict[str, list[dict]] = {}
                for rec in records:
                    mk = _month_key(rec, win_start)
                    by_month.setdefault(mk, []).append(rec)
                for mk, recs in by_month.items():
                    count = _flush_to_disk(out, mk, recs)
                    logger.info("  %s: +%d records (file total: %d)", mk, len(recs), count)
                total_records += len(records)

            _save_checkpoint(checkpoint_file, key)
            completed.add(key)
            done += 1

            if request_delay > 0:
                time.sleep(request_delay)

    except KeyboardInterrupt:
        logger.info("Interrupted. Progress saved — rerun with --skip-existing to resume.")
    finally:
        client.close()

    logger.info("=== Done: %d records fetched across %d windows ===", total_records, done)


if __name__ == "__main__":
    main()
