from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Any
import pandas as pd
from bracc_etl.base import Pipeline
from bracc_etl.loader import Neo4jBatchLoader
from bracc_etl.transforms import (
    format_cnpj,
    normalize_name,
    strip_document,
)
if TYPE_CHECKING:
    from neo4j import Driver

COLUMN_MAP = {
    "CO_CNES": "codigo_cnes",
    "NU_CNPJ": "numero_cnpj",
    "NU_CNPJ_MANTENEDORA": "numero_cnpj_entidade",
    "NO_RAZAO_SOCIAL": "nome_razao_social",
    "NO_FANTASIA": "nome_fantasia",
    "TP_UNIDADE": "codigo_tipo_unidade",
    "DS_ESFERA_ADMINISTRATIVA": "descricao_esfera_administrativa",
    "CO_IBGE": "codigo_municipio",
    "CO_UF": "codigo_uf",
    "ST_ATEND_AMBULATORIAL": "estabelecimento_faz_atendimento_ambulatorial_sus",
    "ST_ATEND_HOSPITALAR": "estabelecimento_possui_atendimento_hospitalar",
    "DS_NATUREZA_ORGANIZACAO": "descricao_natureza_juridica_estabelecimento",
}

class DatasusPipeline(Pipeline):
    """ETL pipeline for CNES health facility data from DATASUS."""
    name = "datasus"
    source_id = "cnes"

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
        self.facilities: list[dict[str, Any]] = []
        self.company_links: list[dict[str, Any]] = []

    def extract(self) -> None:
        datasus_dir = Path(self.data_dir) / "datasus"
        csv_path = datasus_dir / "cnes_all.csv"
        if not csv_path.exists():
            msg = f"CNES data not found at {csv_path}. Run scripts/download_datasus.py first."
            raise FileNotFoundError(msg)
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, sep=";", encoding="latin-1")
        df = df.rename(columns=COLUMN_MAP)
        self._raw = df
        if self.limit:
            self._raw = self._raw.head(self.limit)

    def transform(self) -> None:
        facilities: list[dict[str, Any]] = []
        company_links: list[dict[str, Any]] = []
        nd = r"\D"
        ws = r"\s+"

        raw = self._raw.copy()

        # Vetorizacao
        cnes_code = raw.get("codigo_cnes", pd.Series(dtype=str)).fillna("").astype(str).str.strip()
        mask_valid = cnes_code.str.len() > 0
        raw = raw[mask_valid].copy()
        cnes_code = cnes_code[mask_valid]

        cnpj_raw = raw.get("numero_cnpj_entidade", pd.Series(dtype=str)).fillna("").astype(str).str.strip()
        cnpj_fallback = raw.get("numero_cnpj", pd.Series(dtype=str)).fillna("").astype(str).str.strip()
        cnpj_raw = cnpj_raw.where(cnpj_raw != "", cnpj_fallback)

        cnpj_digits = cnpj_raw.str.replace(nd, "", regex=True)
        mask_cnpj = cnpj_digits.str.len() == 14

        def fmt_cnpj_vec(s):
            d = s.str.replace(nd, "", regex=True).str.zfill(14)
            return d.str[:2]+"."+d.str[2:5]+"."+d.str[5:8]+"/"+d.str[8:12]+"-"+d.str[12:14]

        cnpj_formatted = pd.Series("", index=raw.index)
        if mask_cnpj.any():
            cnpj_formatted[mask_cnpj] = fmt_cnpj_vec(cnpj_raw[mask_cnpj])

        razao = raw.get("nome_razao_social", pd.Series(dtype=str)).fillna("").astype(str).str.strip().str.upper().str.replace(ws, " ", regex=True)
        fantasia = raw.get("nome_fantasia", pd.Series(dtype=str)).fillna("").astype(str).str.strip().str.upper().str.replace(ws, " ", regex=True)
        facility_name = fantasia.where(fantasia != "", razao)

        raw["_cnes_code"] = cnes_code.values
        raw["_cnpj_formatted"] = cnpj_formatted.values
        raw["_razao"] = razao.values
        raw["_fantasia"] = fantasia.values
        raw["_facility_name"] = facility_name.values

        cols = {
            "cnes_code": "_cnes_code",
            "name": "_facility_name",
            "razao_social": "_razao",
            "tipo_unidade": "codigo_tipo_unidade",
            "esfera": "descricao_esfera_administrativa",
            "municipio": "codigo_municipio",
            "uf": "codigo_uf",
            "atende_sus": "estabelecimento_faz_atendimento_ambulatorial_sus",
            "hospitalar": "estabelecimento_possui_atendimento_hospitalar",
            "natureza_juridica": "descricao_natureza_juridica_estabelecimento",
        }

        for out_col, in_col in cols.items():
            if in_col in raw.columns:
                raw[out_col] = raw[in_col].fillna("").astype(str).str.strip()
            else:
                raw[out_col] = ""

        raw["source"] = "cnes"

        facility_cols = ["cnes_code","name","razao_social","tipo_unidade","esfera","municipio","uf","atende_sus","hospitalar","natureza_juridica","source"]
        self.facilities = raw[facility_cols].drop_duplicates(subset=["cnes_code"]).to_dict("records")

        link_df = raw[mask_cnpj.values][["_cnpj_formatted","_cnes_code","_razao"]].copy()
        link_df.columns = ["source_key","target_key","razao_social"]
        self.company_links = link_df.drop_duplicates().to_dict("records")

    def load(self) -> None:
        loader = Neo4jBatchLoader(self.driver, batch_size=500)
        if self.facilities:
            loader.load_nodes("Health", self.facilities, key_field="cnes_code")
        if self.company_links:
            company_rows = [{"cnpj": l["source_key"], "razao_social": l["razao_social"]} for l in self.company_links]
            loader.load_nodes("Company", company_rows, key_field="cnpj")
            loader.load_relationships(
                rel_type="OPERA_UNIDADE",
                rows=self.company_links,
                source_label="Company",
                source_key="cnpj",
                target_label="Health",
                target_key="cnes_code",
            )