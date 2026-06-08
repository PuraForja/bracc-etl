from __future__ import annotations
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any
import pandas as pd
from bracc_etl.base import Pipeline
if TYPE_CHECKING:
    from neo4j import Driver
from bracc_etl.loader import Neo4jBatchLoader
from bracc_etl.transforms import deduplicate_rows, normalize_name
logger = logging.getLogger(__name__)
class ServidoresFederaisPipeline(Pipeline):
    """Servidores federais lotados no Amazonas — Portal da Transparência CGU."""
    name = "servidores_federais"
    source_id = "portal_transparencia_servidores"
    def __init__(
        self,
        driver: "Driver",
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        **kwargs: Any,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size, **kwargs)
        self._csv_paths: list[str] = []
    def extract(self) -> None:
        srv_dir = Path(self.data_dir) / "servidores_federais"
        if not srv_dir.exists():
            logger.warning("[%s] Diretório não encontrado: %s", self.name, srv_dir)
            return
        csvs = sorted(srv_dir.glob("servidores_federais_AM_*.csv"), reverse=True)
        if not csvs:
            logger.warning("[%s] Nenhum CSV encontrado em %s", self.name, srv_dir)
            return
        self._csv_paths = [str(c) for c in csvs]
        logger.info("[%s] %d arquivos encontrados", self.name, len(csvs))
    def transform(self) -> None:
        pass  # processamento em chunks no load
    def load(self) -> None:
        if not self._csv_paths:
            logger.warning("[%s] Sem arquivo para importar", self.name)
            return
        loader = Neo4jBatchLoader(self.driver, batch_size=500)
        total = 0
        for csv_path in self._csv_paths:
            logger.info("[%s] Processando: %s", self.name, csv_path)
            for chunk in pd.read_csv(
                csv_path,
                sep=";",
                encoding="utf-8",
                dtype=str,
                chunksize=self.chunk_size,
                nrows=self.limit,
            ):
                chunk.columns = chunk.columns.str.strip().str.upper()
                chunk = chunk.fillna("")
                rows = []
                for _, row in chunk.iterrows():
                    id_servidor = row.get("ID_SERVIDOR_PORTAL", "").strip()
                    if not id_servidor:
                        continue
                    nome = normalize_name(row.get("NOME", ""))
                    cpf = row.get("CPF", "").strip()
                    orgao = row.get("ORG_EXERCICIO", "").strip()
                    cargo = row.get("DESCRICAO_CARGO", "").strip()
                    uf = row.get("UF_EXERCICIO", "AM").strip()
                    rows.append({
                        "emp_id": id_servidor,
                        "name": nome,
                        "cpf_mascarado": cpf,
                        "orgao": orgao,
                        "cargo": cargo.replace("Sem informaç", "Sem informação"),
                        "uf": uf,
                        "fonte": "servidores_federais",
                    })
                if not rows:
                    continue
                rows = deduplicate_rows(rows, ["emp_id"])
                loader.load_nodes("GovEmployee", rows, key_field="emp_id")
                total += len(rows)
                logger.info("[%s] GovEmployee importados: %d", self.name, total)
        logger.info("[%s] Concluído: %d GovEmployee", self.name, total)
