"""
transparencia_am.py
===================
Pipeline ETL para remuneração de servidores do Portal da Transparência do Amazonas.
https://www.transparencia.am.gov.br/pessoal/

Estrutura dos CSVs (separado por ;):
  NOME; LOTACAO; CARGO; FUNCAO; VINCULO;
  REMUNERACAO LEGAL TOTAL(R$); DESC.TETO(R$);
  REMUNERACAO LEGAL DEVIDA(R$); DESCONTOS LEGAIS(R$); LIQUIDO DISPONIVEL(R$)

Estrutura de diretórios:
  data/transparencia_am/{ORGAO}/{ANO}/{arquivo}.csv

Nodes criados:
  - GovEmployee (remuneração mensal — label principal para o orquestrador)
  - Person      (chave: nome+orgao hash — CPF não está no CSV)

STREAMING: processa um CSV por vez — nunca acumula tudo na RAM.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

import faulthandler
import os
faulthandler.enable()
from bracc_etl.base import Pipeline
from bracc_etl.loader import Neo4jBatchLoader
from bracc_etl.transforms import normalize_name

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)

# Colunas esperadas → nome normalizado
_COL_MAP = {
    "NOME": "nome",
    "LOTACAO": "lotacao",
    "CARGO": "cargo",
    "FUNCAO": "funcao",
    "CLASSE/PADRÃO": "classe",
    "CARGA HR SEM": "carga_hr",
    "DT DE ADMISSAO": "dt_admissao",
    "VINCULO": "vinculo",
    "REMUNERACAO LEGAL TOTAL(R$)": "rem_total",
    "DESC.TETO(R$)": "desc_teto",
    "REMUNERACAO LEGAL DEVIDA(R$)": "rem_devida",
    "DESCONTOS LEGAIS(R$)": "descontos",
    "LIQUIDO DISPONIVEL(R$)": "liquido",
}

_MES_NOME = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03",
    "abril": "04", "maio": "05", "junho": "06", "julho": "07",
    "agosto": "08", "setembro": "09", "outubro": "10",
    "novembro": "11", "dezembro": "12",
}


def _extract_mes_ano(csv_path: Path) -> str:
    """Extrai YYYYMM do nome do arquivo ex: 158_202301.csv → 202301."""
    m = re.search(r"_(\d{6})\.csv$", csv_path.name, re.IGNORECASE)
    if m:
        return m.group(1)
    return "000000"


def _parse_brl(value: str) -> float:
    """Converte formato BRL (1.234,56) para float."""
    if not value or not value.strip():
        return 0.0
    cleaned = value.strip().replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _employee_id(nome: str, orgao: str, mes_ano: str) -> str:
    raw = f"{nome.upper().strip()}|{orgao}|{mes_ano}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _person_id(nome: str) -> str:
    raw = nome.upper().strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class TransparenciaAmPipeline(Pipeline):
    """ETL pipeline para servidores do Amazonas — streaming por CSV."""

    name = "transparencia_am"
    source_id = "transparencia_am"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 5_000,
        **kwargs: Any,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size, **kwargs)

    def extract(self) -> None:
        """No-op — processamento feito em run() por CSV."""
        pass

    def transform(self) -> None:
        """No-op — processamento feito em run() por CSV."""
        pass

    def load(self) -> None:
        """No-op — processamento feito em run() por CSV."""
        pass

    def _process_csv(self, csv_path: Path, loader: Neo4jBatchLoader, session: Any) -> int:
        """Lê, transforma e carrega um único CSV. Retorna nº de employees carregados."""
        parts = csv_path.relative_to(Path(self.data_dir) / "transparencia_am").parts
        orgao = parts[0] if len(parts) >= 3 else "DESCONHECIDO"
        ano = parts[1] if len(parts) >= 3 else "0000"
        mes_ano = _extract_mes_ano(csv_path)

        try:
            df = pd.read_csv(
                csv_path,
                sep=";",
                dtype=str,
                encoding="latin-1",
                keep_default_na=False,
            )
        except Exception as e:
            logger.warning("Erro ao ler %s: %s", csv_path.name, e)
            return 0

        if df.empty:
            return 0

        df.columns = [c.strip() for c in df.columns]
        rename = {k: v for k, v in _COL_MAP.items() if k in df.columns}
        df = df.rename(columns=rename)

        if "nome" not in df.columns:
            return 0

        # Filtrar linhas inválidas
        df = df[df["nome"].str.strip().str.upper().ne("NOME")]
        df = df[df["nome"].str.strip().ne("")]
        if df.empty:
            return 0

        df["orgao"] = orgao
        df["ano"] = ano
        df["mes_ano"] = mes_ano

        # Vetorizado
        nomes = df["nome"].fillna("").astype(str).str.strip()
        import hashlib as _hl
        _emp_raw = nomes.str.upper() + "|" + orgao + "|" + mes_ano
        df["emp_id"] = [_hl.sha256(x.encode()).hexdigest()[:16] for x in _emp_raw]
        df["person_id"] = [_hl.sha256(x.encode()).hexdigest()[:16] for x in nomes.str.upper()]
        df["nome_norm"] = nomes.str.upper().str.replace(r"\s+", " ", regex=True)

        employees = df[[
            "emp_id", "nome_norm", "orgao", "ano", "mes_ano",
        ]].rename(columns={"nome_norm": "nome"}).copy()

        for col in ["lotacao", "cargo", "funcao", "classe", "vinculo", "dt_admissao"]:
            if col in df.columns:
                employees[col] = df[col].fillna("").astype(str).str.strip()
            else:
                employees[col] = ""

        for col_src, col_dst in [
            ("rem_total", "rem_total"), ("desc_teto", "desc_teto"),
            ("rem_devida", "rem_devida"), ("descontos", "descontos"),
            ("liquido", "liquido"),
        ]:
            if col_src in df.columns:
                employees[col_dst] = [_parse_brl(str(x)) for x in df[col_src]]
            else:
                employees[col_dst] = 0.0

        employees["source"] = "transparencia_am"
        employees["person_id"] = df["person_id"].values

        persons = df[["person_id", "nome_norm"]].rename(
            columns={"nome_norm": "name"}
        ).drop_duplicates(subset=["person_id"]).copy()
        persons["source"] = "transparencia_am"

        person_rels = df[["person_id", "emp_id"]].drop_duplicates().to_dict("records")

        emp_records = employees.drop_duplicates(subset=["emp_id"]).to_dict("records")
        per_records = persons.to_dict("records")

        # Load
        if emp_records:
            loader.load_nodes("GovEmployee", emp_records, key_field="emp_id", session=session)
        if per_records:
            loader.load_nodes("Person", per_records, key_field="person_id", session=session)
        if person_rels:
            query = (
                "UNWIND $rows AS row "
                "MATCH (p:Person {person_id: row.person_id}) "
                "MATCH (e:GovEmployee {emp_id: row.emp_id}) "
                "MERGE (p)-[:TEM_REMUNERACAO]->(e)"
            )
            loader.run_query_with_retry(query, person_rels, session=session)

        return len(emp_records)

    def run(self) -> None:
        """Processa cada CSV individualmente — sem acumular RAM."""
        base = Path(self.data_dir) / "transparencia_am"
        _orgao_filter = os.environ.get("TRANSPARENCIA_AM_ORGAO", "").upper()
        csv_files = sorted(f for f in base.rglob("*.csv") if not _orgao_filter or f.parts[-3].upper() == _orgao_filter)

        if not csv_files:
            logger.warning("[transparencia_am] Nenhum CSV encontrado em %s", base)
            return

        total_files = len(csv_files)
        logger.info("[transparencia_am] Processando %d CSVs...", total_files)

        loader = Neo4jBatchLoader(self.driver, batch_size=500)
        total_employees = 0

        for i, csv_path in enumerate(csv_files, 1):
            if i % 100 == 0 or i == 1:
                logger.info("Processando %d/%d %s", i, total_files, csv_path.name)

            with loader.open_session() as session:
                count = self._process_csv(csv_path, loader, session)
            total_employees += count

            if self.limit and total_employees >= self.limit:
                logger.info("[transparencia_am] Limit %d atingido — parando.", self.limit)
                break

        logger.info(
            "[transparencia_am] ✅ CONCLUÍDO — %d employees em %d CSVs",
            total_employees,
            total_files,
        )
