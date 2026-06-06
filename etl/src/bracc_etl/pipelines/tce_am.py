"""
tce_am.py
=========
Pipeline ETL para contratos e licitações do TCE-AM.

Fontes:
  data/tce_am/contratos.csv   — contratos municipais e estaduais AM
  data/tce_am/licitacoes.csv  — licitações municipais e estaduais AM

Nodes criados:
  Contract — contrato com valor, objeto, datas, número DOE
  Bid      — licitação com valor, modalidade, objeto

Relações criadas:
  (Company)-[:VENCEU]->(Contract)         — via cpfCnpj do contratado
  (Contract)-[:CONTRATADO_POR]->(Company) — órgão contratante via cnpjUnidadeGestora
  (Company)-[:LICITOU_AM]->(Bid)          — órgão que abriu licitação
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from bracc_etl.base import Pipeline

if TYPE_CHECKING:
    from neo4j import Driver

from bracc_etl.loader import Neo4jBatchLoader
from bracc_etl.transforms import (
    deduplicate_rows,
    normalize_name,
    parse_date,
    strip_document,
)


def _clean_cnpj(val: str) -> str:
    return strip_document(str(val or ""))


def _safe_float(val: str) -> float | None:
    try:
        return float(str(val).replace(",", ".")) if val else None
    except (ValueError, TypeError):
        return None


class TceAmPipeline(Pipeline):
    """ETL pipeline para contratos e licitações do TCE-AM."""

    name = "tce_am"
    source_id = "tce_am"

    def __init__(
        self,
        driver: "Driver",
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        **kwargs: Any,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size, **kwargs)
        self.contracts: list[dict[str, Any]] = []
        self.bids: list[dict[str, Any]] = []
        self.venceu_rels: list[dict[str, Any]] = []
        self.contratado_por_rels: list[dict[str, Any]] = []
        self.licitou_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        tce_dir = Path(self.data_dir) / "tce_am"
        self._contratos = pd.DataFrame()
        self._licitacoes = pd.DataFrame()

        contratos_csv = tce_dir / "contratos.csv"
        if contratos_csv.exists():
            self._contratos = pd.read_csv(contratos_csv, dtype=str, encoding="utf-8", keep_default_na=False)
            logger.info("Contratos carregados: %d linhas", len(self._contratos))
        else:
            logger.warning("contratos.csv não encontrado em %s", tce_dir)

        licitacoes_csv = tce_dir / "licitacoes.csv"
        if licitacoes_csv.exists():
            self._licitacoes = pd.read_csv(licitacoes_csv, dtype=str, encoding="utf-8", keep_default_na=False)
            logger.info("Licitações carregadas: %d linhas", len(self._licitacoes))
        else:
            logger.warning("licitacoes.csv não encontrado em %s", tce_dir)

    def transform(self) -> None:
        contracts: list[dict[str, Any]] = []
        bids: list[dict[str, Any]] = []
        venceu_rels: list[dict[str, Any]] = []
        contratado_por_rels: list[dict[str, Any]] = []
        licitou_rels: list[dict[str, Any]] = []

        # ── Contratos ──────────────────────────────────────────────────────
        for _, row in self._contratos.iterrows():
            contract_id = f"tce_am_contrato_{row.get('idContrato', '')}"
            cnpj_contratado = _clean_cnpj(row.get("cpfCnpj", ""))
            cnpj_orgao = _clean_cnpj(row.get("cnpjUnidadeGestora", ""))

            contracts.append({
                "contract_id":     contract_id,
                "num_contrato":    str(row.get("numContrato", "")).strip(),
                "objeto":          str(row.get("desObjetivo", "")).strip(),
                "valor":           _safe_float(row.get("vlContrato", "")),
                "data_assinatura": parse_date(str(row.get("dtAssinaturaContrato", ""))),
                "data_publicacao": parse_date(str(row.get("dtPublicacaoContrato", ""))),
                "num_doe":         str(row.get("numDoe", "")).strip(),
                "orgao_nome":      normalize_name(str(row.get("nomeUnidadeGestora", ""))),
                "orgao_cnpj":      cnpj_orgao,
                "contratado_nome": normalize_name(str(row.get("nome", ""))),
                "contratado_cnpj": cnpj_contratado,
                "exercicio":       str(row.get("exercicio", "")).strip(),
                "tipo_pessoa":     str(row.get("desTipoPessoa", "")).strip(),
                "source":          "tce_am",
            })

            # (Company)-[:VENCEU]->(Contract)
            if len(cnpj_contratado) in (11, 14):
                venceu_rels.append({
                    "source_key": cnpj_contratado,
                    "target_key": contract_id,
                })

            # (Contract)-[:CONTRATADO_POR]->(Company)
            if len(cnpj_orgao) == 14:
                contratado_por_rels.append({
                    "source_key": contract_id,
                    "target_key": cnpj_orgao,
                })

        # ── Licitações ─────────────────────────────────────────────────────
        for _, row in self._licitacoes.iterrows():
            bid_id = f"tce_am_licitacao_{row.get('idLicitacao', '')}"
            cnpj_orgao = _clean_cnpj(row.get("cnpjUnidadeGestora", ""))

            bids.append({
                "bid_id":          bid_id,
                "numero":          str(row.get("numeroLicitacao", "")).strip(),
                "objeto":          str(row.get("descricaoObjeto", "")).strip(),
                "valor":           _safe_float(row.get("valorTotal", "")),
                "data_publicacao": parse_date(str(row.get("dtPublicacaoEdital", ""))),
                "modalidade":      str(row.get("desTipoLicitacao", "")).strip(),
                "natureza":        str(row.get("desTipoNaturezaProcedimento", "")).strip(),
                "num_doe":         str(row.get("numDoe", "")).strip(),
                "orgao_nome":      normalize_name(str(row.get("nomeUnidadeGestora", ""))),
                "orgao_cnpj":      cnpj_orgao,
                "exercicio":       str(row.get("exercicio", "")).strip(),
                "source":          "tce_am",
            })

            # (Company)-[:LICITOU_AM]->(Bid)
            if len(cnpj_orgao) == 14:
                licitou_rels.append({
                    "source_key": cnpj_orgao,
                    "target_key": bid_id,
                })

        self.contracts = deduplicate_rows(contracts, ["contract_id"])
        self.bids = deduplicate_rows(bids, ["bid_id"])
        self.venceu_rels = venceu_rels
        self.contratado_por_rels = contratado_por_rels
        self.licitou_rels = licitou_rels

        logger.info(
            "Transform: %d contratos, %d licitações, %d VENCEU, %d CONTRATADO_POR, %d LICITOU_AM",
            len(self.contracts), len(self.bids),
            len(self.venceu_rels), len(self.contratado_por_rels), len(self.licitou_rels),
        )

    def load(self) -> None:
        loader = Neo4jBatchLoader(self.driver)

        with loader.open_session() as session:
            if self.contracts:
                loader.load_nodes("Contract", self.contracts, key_field="contract_id", session=session)

            if self.bids:
                loader.load_nodes("Bid", self.bids, key_field="bid_id", session=session)

            if self.venceu_rels:
                loader.load_relationships(
                    "VENCEU", self.venceu_rels,
                    "Company", "cnpj",
                    "Contract", "contract_id",
                    session=session,
                )

            if self.contratado_por_rels:
                loader.load_relationships(
                    "CONTRATADO_POR", self.contratado_por_rels,
                    "Contract", "contract_id",
                    "Company", "cnpj",
                    session=session,
                )

            if self.licitou_rels:
                loader.load_relationships(
                    "LICITOU_AM", self.licitou_rels,
                    "Company", "cnpj",
                    "Bid", "bid_id",
                    session=session,
                )
