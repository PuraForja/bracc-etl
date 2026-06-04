from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from bracc_etl.base import Pipeline

if TYPE_CHECKING:
    from neo4j import Driver
from bracc_etl.loader import Neo4jBatchLoader
from bracc_etl.transforms import (
    deduplicate_rows,
    format_cpf,
    normalize_name,
    strip_document,
)

logger = logging.getLogger(__name__)


def _parse_value(raw: str) -> float:
    """Parse a monetary value string to float. Returns 0.0 on failure."""
    if not raw:
        return 0.0
    cleaned = raw.strip().replace(",", ".")
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def _make_asset_id(cpf: str, year: str, asset_type: str, value: str, description: str) -> str:
    """Generate deterministic asset_id from key fields."""
    payload = f"{cpf}|{year}|{asset_type}|{value}|{description}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class TseBensPipeline(Pipeline):
    """ETL pipeline for TSE Bens Declarados (candidate declared assets)."""

    name = "tse_bens"
    source_id = "tse_bens"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        **kwargs: Any,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size, **kwargs)
        self._raw: pd.DataFrame = pd.DataFrame()
        self.assets: list[dict[str, Any]] = []
        self.person_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        bens_dir = Path(self.data_dir) / "tse_bens"
        csv_path = bens_dir / "bens.csv"
        if not csv_path.exists():
            msg = f"Data file not found: {csv_path}"
            raise FileNotFoundError(msg)

        self._csv_path = str(csv_path)
        self._raw = pd.DataFrame()  # nao carrega em memoria
        logger.info("[tse_bens] CSV path set: %s", csv_path)

    def transform(self) -> None:
        pass  # processamento feito em chunks no load

    def load(self) -> None:
        import logging as _logging
        _log = _logging.getLogger(__name__)
        loader = Neo4jBatchLoader(self.driver, batch_size=500)
        chunk_size = 50_000
        total_assets = 0
        total_rels = 0

        for chunk in pd.read_csv(
            self._csv_path,
            dtype=str,
            keep_default_na=False,
            encoding="latin-1",
            chunksize=chunk_size,
            nrows=self.limit,
        ):
            assets = []
            person_rels = []
            persons_seen: set = set()
            unique_persons = []

            for _, row in chunk.iterrows():
                cpf_raw = str(row.get("cpf", "")).strip()
                digits = strip_document(cpf_raw)
                if len(digits) != 11:
                    continue
                cpf_formatted = format_cpf(digits)
                nome = normalize_name(str(row.get("nome", "")))
                year = str(row.get("ANO_ELEICAO", "")).strip()
                asset_type = str(row.get("DS_TIPO_BEM_CANDIDATO", "")).strip()
                description = str(row.get("DS_BEM_CANDIDATO", "")).strip()
                value_raw = str(row.get("VR_BEM_CANDIDATO", "")).strip()
                value = _parse_value(value_raw)
                uf = str(row.get("SG_UF", "")).strip()

                asset_id = _make_asset_id(digits, year, asset_type, value_raw, description)
                assets.append({
                    "asset_id": asset_id,
                    "candidate_cpf": cpf_formatted,
                    "candidate_name": nome,
                    "asset_type": asset_type,
                    "asset_description": description,
                    "asset_value": value,
                    "election_year": int(year) if year.isdigit() else 0,
                    "uf": uf,
                    "source": "tse_bens",
                })
                person_rels.append({
                    "source_key": cpf_formatted,
                    "target_key": asset_id,
                    "person_name": nome,
                })
                if cpf_formatted not in persons_seen:
                    persons_seen.add(cpf_formatted)
                    unique_persons.append({"cpf": cpf_formatted, "name": nome})

            if not assets:
                continue

            assets = deduplicate_rows(assets, ["asset_id"])
            loader.load_nodes("DeclaredAsset", assets, key_field="asset_id")

            if unique_persons:
                loader.load_nodes("Person", unique_persons, key_field="cpf")

            if person_rels:
                loader.run_query_with_retry(
                    "UNWIND $rows AS row "
                    "MATCH (p:Person {cpf: row.source_key}) "
                    "MATCH (a:DeclaredAsset {asset_id: row.target_key}) "
                    "MERGE (p)-[:DECLAROU_BEM]->(a)",
                    person_rels,
                )

            total_assets += len(assets)
            total_rels += len(person_rels)
            _log.info("[tse_bens] processados: %d assets, %d rels", total_assets, total_rels)

        _log.info("[tse_bens] Concluido: %d assets, %d rels", total_assets, total_rels)

