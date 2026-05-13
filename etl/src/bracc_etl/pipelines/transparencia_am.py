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
  - Person  (chave: cpf ou nome+orgao+mes_ano — CPF não está no CSV, usamos hash)
  - GovEmployee (remuneração mensal — label principal para o orquestrador)
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from bracc_etl.base import Pipeline
from bracc_etl.loader import Neo4jBatchLoader
from bracc_etl.transforms import deduplicate_rows, normalize_name

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


def _parse_brl(value: str) -> float | None:
    """Converte '2.428,85' ou '2428,85' para float."""
    if not value or value.strip() in ("", "-"):
        return None
    try:
        return float(value.strip().replace(".", "").replace(",", "."))
    except ValueError:
        return None


def _employee_id(nome: str, orgao: str, mes_ano: str) -> str:
    """ID determinístico: hash de nome+orgao+mes_ano (CSV não tem CPF)."""
    raw = f"{nome.upper().strip()}:{orgao}:{mes_ano}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _person_id(nome: str) -> str:
    """ID de pessoa baseado no nome normalizado."""
    raw = normalize_name(nome).upper().strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _extract_mes_ano(filepath: Path) -> str:
    """Extrai YYYYMM do nome do arquivo. Ex: 158_201705.csv → 2017-05"""
    m = re.search(r"(\d{6})", filepath.stem)
    if m:
        yyyymm = m.group(1)
        return f"{yyyymm[:4]}-{yyyymm[4:]}"
    return "0000-00"


class TransparenciaAmPipeline(Pipeline):
    """ETL pipeline para remuneração de servidores — Portal Transparência AM."""

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
        self.employees: list[dict[str, Any]] = []
        self.persons: list[dict[str, Any]] = []
        self.person_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        base = Path(self.data_dir) / "transparencia_am"
        csv_files = sorted(base.rglob("*.csv"))

        if not csv_files:
            raise FileNotFoundError(f"Nenhum CSV encontrado em {base}")

        logger.info("Carregando %d CSVs de %s...", len(csv_files), base)

        all_rows: list[dict[str, Any]] = []
        for i, csv_path in enumerate(csv_files):
            # Estrutura: transparencia_am/{ORGAO}/{ANO}/{arquivo}.csv
            parts = csv_path.relative_to(base).parts
            orgao = parts[0] if len(parts) >= 3 else "DESCONHECIDO"
            ano = parts[1] if len(parts) >= 3 else "0000"
            mes_ano = _extract_mes_ano(csv_path)

            if i % 100 == 0:
                logger.info("Processando %d/%d %s", i + 1, len(csv_files), csv_path.name)

            try:
                df = pd.read_csv(
                    csv_path,
                    sep=";",
                    dtype=str,
                    encoding="latin-1",
                    keep_default_na=False,
                )
                df.columns = [c.strip() for c in df.columns]

                # Renomeia colunas conhecidas
                rename = {k: v for k, v in _COL_MAP.items() if k in df.columns}
                df = df.rename(columns=rename)

                df["orgao"] = orgao
                df["ano"] = ano
                df["mes_ano"] = mes_ano
                df["arquivo"] = csv_path.name

                all_rows.extend(df.to_dict("records"))

                if self.limit and len(all_rows) >= self.limit:
                    all_rows = all_rows[: self.limit]
                    break

            except Exception as e:
                logger.warning("Erro ao ler %s: %s", csv_path.name, e)

        self._raw = all_rows
        logger.info("Total de registros extraídos: %d", len(self._raw))

    def transform(self) -> None:
        employees: list[dict[str, Any]] = []
        persons: list[dict[str, Any]] = []
        person_rels: list[dict[str, Any]] = []

        for row in self._raw:
            nome_raw = str(row.get("nome", "")).strip()
            if not nome_raw or nome_raw.upper() in ("NOME", ""):
                continue

            nome = normalize_name(nome_raw)
            orgao = str(row.get("orgao", "")).strip()
            mes_ano = str(row.get("mes_ano", "")).strip()

            emp_id = _employee_id(nome_raw, orgao, mes_ano)
            pid = _person_id(nome_raw)

            employees.append({
                "emp_id": emp_id,
                "nome": nome,
                "orgao": orgao,
                "ano": str(row.get("ano", "")).strip(),
                "mes_ano": mes_ano,
                "lotacao": str(row.get("lotacao", "")).strip(),
                "cargo": str(row.get("cargo", "")).strip(),
                "funcao": str(row.get("funcao", "")).strip(),
                "classe": str(row.get("classe", "")).strip(),
                "vinculo": str(row.get("vinculo", "")).strip(),
                "dt_admissao": str(row.get("dt_admissao", "")).strip(),
                "rem_total": _parse_brl(str(row.get("rem_total", ""))),
                "desc_teto": _parse_brl(str(row.get("desc_teto", ""))),
                "rem_devida": _parse_brl(str(row.get("rem_devida", ""))),
                "descontos": _parse_brl(str(row.get("descontos", ""))),
                "liquido": _parse_brl(str(row.get("liquido", ""))),
                "source": "transparencia_am",
                "person_id": pid,
            })

            persons.append({
                "person_id": pid,
                "name": nome,
                "source": "transparencia_am",
            })

            person_rels.append({
                "person_id": pid,
                "emp_id": emp_id,
            })

        self.employees = deduplicate_rows(employees, ["emp_id"])
        self.persons = deduplicate_rows(persons, ["person_id"])
        self.person_rels = person_rels

        logger.info(
            "Transform: %d registros | %d pessoas únicas",
            len(self.employees),
            len(self.persons),
        )

    def load(self) -> None:
        loader = Neo4jBatchLoader(self.driver)

        with loader.open_session() as session:
            if self.employees:
                loader.load_nodes(
                    "GovEmployee",
                    self.employees,
                    key_field="emp_id",
                    session=session,
                )

            if self.persons:
                loader.load_nodes(
                    "Person",
                    self.persons,
                    key_field="person_id",
                    session=session,
                )

            if self.person_rels:
                query = (
                    "UNWIND $rows AS row "
                    "MATCH (p:Person {person_id: row.person_id}) "
                    "MATCH (e:GovEmployee {emp_id: row.emp_id}) "
                    "MERGE (p)-[:TEM_REMUNERACAO]->(e)"
                )
                loader.run_query_with_retry(query, self.person_rels, session=session)
