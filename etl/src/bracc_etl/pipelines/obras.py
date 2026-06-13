"""ETL pipeline for Obras.gov federal infrastructure projects.

Ingests physical infrastructure project data from Obras.gov JSON files.
Creates Obra nodes linked to Company (executor) and Company (contratante)
nodes via EXECUTA and CONTRATOU relationships.

Distinct from PNCP/ComprasNet — these are physical obras with:
- Percentual de execução física
- Situação da obra (em execução, paralisada, concluída, etc.)
- Valor contratado vs. valor medido
- Município/UF da obra

Data source: https://api.obras.gov.br/api/v2/empreendimentos
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from bracc_etl.base import Pipeline
from bracc_etl.loader import Neo4jBatchLoader
from bracc_etl.transforms import (
    deduplicate_rows,
    format_cnpj,
    normalize_name,
    strip_document,
)

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)

# Situação codes to labels
_SITUACAO_MAP: dict[str, str] = {
    "1": "nao_iniciada",
    "2": "em_execucao",
    "3": "paralisada",
    "4": "concluida",
    "5": "cancelada",
    "6": "em_licitacao",
}


def _parse_float(value: Any) -> float:
    """Safely parse a float from mixed types."""
    if value is None:
        return 0.0
    try:
        return float(str(value).replace(",", ".").strip())
    except (ValueError, TypeError):
        return 0.0


def _parse_percent(value: Any) -> float:
    """Parse percentage value, clamping to [0.0, 100.0]."""
    pct = _parse_float(value)
    return max(0.0, min(100.0, pct))


class ObrasPipeline(Pipeline):
    """ETL pipeline for Obras.gov federal infrastructure projects."""

    name = "obras"
    source_id = "obras_gov"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        **kwargs: Any,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size, **kwargs)
        self._raw_records: list[dict[str, Any]] = []
        self.obras: list[dict[str, Any]] = []
        self.executores: list[dict[str, Any]] = []
        self.contratantes: list[dict[str, Any]] = []
        self.executa_rels: list[dict[str, Any]] = []
        self.contratou_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        """Load pre-downloaded Obras.gov JSON files from data/obras/."""
        src_dir = Path(self.data_dir) / "obras"
        json_files = sorted(src_dir.glob("obras_page_*.json"))
        if not json_files:
            logger.warning("No Obras.gov JSON files found in %s", src_dir)
            return

        all_records: list[dict[str, Any]] = []
        for f in json_files:
            try:
                payload = json.loads(f.read_text(encoding="utf-8"), strict=False)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to parse %s: %s", f.name, exc)
                continue
            if isinstance(payload, list):
                all_records.extend(payload)
            elif isinstance(payload, dict):
                records = (
                    payload.get("data")
                    or payload.get("content")
                    or payload.get("empreendimentos")
                    or []
                )
                all_records.extend(records)
            logger.info("  Loaded records from %s (total so far: %d)", f.name, len(all_records))

        logger.info("Total raw records: %d", len(all_records))
        self._raw_records = all_records

    def transform(self) -> None:
        """Normalize fields and build node/relationship lists."""
        if not self._raw_records:
            return

        obras: list[dict[str, Any]] = []
        executores: list[dict[str, Any]] = []
        contratantes: list[dict[str, Any]] = []
        executa_rels: list[dict[str, Any]] = []
        contratou_rels: list[dict[str, Any]] = []
        skipped = 0

        for rec in self._raw_records:
            # Stable obra ID
            obra_id = str(rec.get("id") or rec.get("codigoObra") or "").strip()
            if not obra_id:
                skipped += 1
                continue

            nome = normalize_name(str(rec.get("nome") or rec.get("descricao") or ""))
            municipio = str(rec.get("municipio") or rec.get("municipioNome") or "").strip()
            uf = str(rec.get("uf") or rec.get("ufSigla") or "").strip()
            situacao_raw = str(rec.get("situacao") or rec.get("situacaoId") or "").strip()
            situacao = _SITUACAO_MAP.get(situacao_raw, situacao_raw)

            valor_contratado = _parse_float(
                rec.get("valorContratado") or rec.get("valorContrato")
            )
            valor_medido = _parse_float(
                rec.get("valorMedido") or rec.get("valorExecutado")
            )
            percentual_fisico = _parse_percent(
                rec.get("percentualExecucaoFisica") or rec.get("percentualFisico")
            )
            percentual_financeiro = _parse_percent(
                rec.get("percentualExecucaoFinanceira") or rec.get("percentualFinanceiro")
            )

            data_inicio = str(rec.get("dataInicio") or rec.get("dataInicioObra") or "").strip()[:10]
            data_fim = str(rec.get("dataFimPrevisto") or rec.get("dataFimObra") or "").strip()[:10]

            obras.append({
                "obra_id": obra_id,
                "name": nome,
                "municipality": municipio,
                "uf": uf,
                "situacao": situacao,
                "value_contracted": valor_contratado,
                "value_measured": valor_medido,
                "pct_physical": percentual_fisico,
                "pct_financial": percentual_financeiro,
                "date_start": data_inicio,
                "date_end": data_fim,
                "source": "obras_gov",
            })

            # Executor (empresa que executa a obra)
            executor = rec.get("executor") or rec.get("empresa") or {}
            if isinstance(executor, dict):
                cnpj_raw = str(executor.get("cnpj") or executor.get("cpfCnpj") or "").strip()
                cnpj_digits = strip_document(cnpj_raw)
                if len(cnpj_digits) == 14:
                    cnpj = format_cnpj(cnpj_raw)
                    executores.append({
                        "cnpj": cnpj,
                        "razao_social": normalize_name(
                            str(executor.get("razaoSocial") or executor.get("nome") or "")
                        ),
                    })
                    executa_rels.append({"cnpj": cnpj, "obra_id": obra_id})

            # Contratante (órgão que contratou)
            contratante = rec.get("contratante") or rec.get("orgao") or rec.get("unidadeGestora") or {}
            if isinstance(contratante, dict):
                cnpj_raw = str(contratante.get("cnpj") or "").strip()
                cnpj_digits = strip_document(cnpj_raw)
                if len(cnpj_digits) == 14:
                    cnpj = format_cnpj(cnpj_raw)
                    contratantes.append({
                        "cnpj": cnpj,
                        "razao_social": normalize_name(
                            str(contratante.get("razaoSocial") or contratante.get("nome") or "")
                        ),
                    })
                    contratou_rels.append({"cnpj": cnpj, "obra_id": obra_id})

        self.obras = deduplicate_rows(obras, ["obra_id"])
        self.executores = deduplicate_rows(executores, ["cnpj"])
        self.contratantes = deduplicate_rows(contratantes, ["cnpj"])
        self.executa_rels = executa_rels
        self.contratou_rels = contratou_rels

        logger.info(
            "Transformed: %d obras, %d executores, %d contratantes (skipped %d)",
            len(self.obras), len(self.executores), len(self.contratantes), skipped,
        )
        if self.limit:
            self.obras = self.obras[: self.limit]

    def load(self) -> None:
        """Load Obra nodes and relationships into Neo4j."""
        if not self.obras:
            logger.warning("No obras to load")
            return

        loader = Neo4jBatchLoader(self.driver)

        # 1. Obra nodes
        count = loader.load_nodes("Obra", self.obras, key_field="obra_id")
        logger.info("Loaded %d Obra nodes", count)

        # 2. Company nodes for executores
        if self.executores:
            count = loader.load_nodes("Company", self.executores, key_field="cnpj")
            logger.info("Merged %d Company (executor) nodes", count)

        # 3. Company nodes for contratantes
        if self.contratantes:
            count = loader.load_nodes("Company", self.contratantes, key_field="cnpj")
            logger.info("Merged %d Company (contratante) nodes", count)

        # 4. Company -[:EXECUTA]-> Obra
        if self.executa_rels:
            count = loader.load_relationships(
                rel_type="EXECUTA",
                rows=self.executa_rels,
                source_label="Company",
                source_key="cnpj",
                target_label="Obra",
                target_key="obra_id",
            )
            logger.info("Created %d EXECUTA relationships", count)

        # 5. Company -[:CONTRATOU]-> Obra
        if self.contratou_rels:
            count = loader.load_relationships(
                rel_type="CONTRATOU",
                rows=self.contratou_rels,
                source_label="Company",
                source_key="cnpj",
                target_label="Obra",
                target_key="obra_id",
            )
            logger.info("Created %d CONTRATOU relationships", count)
