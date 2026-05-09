"""ETL pipeline for Camara dos Deputados CEAP expense data.

Ingests CEAP (Cota para o Exercicio da Atividade Parlamentar) expenses.
Creates Expense nodes linked to Person (deputy) via GASTOU
and to Company (supplier) via FORNECEU.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from bracc_etl.base import Pipeline
from bracc_etl.loader import Neo4jBatchLoader

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class CamaraPipeline(Pipeline):
    """ETL pipeline for Camara dos Deputados CEAP expenses."""

    name = "camara"
    source_id = "camara"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 10_000,
        **kwargs: Any,
    ) -> None:
        super().__init__(driver, data_dir, limit=limit, chunk_size=chunk_size, **kwargs)

    def extract(self) -> None:
        """No-op — processamento feito em run() por arquivo."""
        pass

    def transform(self) -> None:
        """No-op — processamento feito em run() por arquivo."""
        pass

    def load(self) -> None:
        """No-op — processamento feito em run() por arquivo."""
        pass

    def cleanup(self) -> None:
        """Libera memória após conclusão."""
        import gc
        gc.collect()
        logger.info("[camara] Memória liberada.")

    def _transform_chunk(self, df: pd.DataFrame) -> tuple:
        """Transforma um chunk (DataFrame) usando vetorização 100% pandas."""
        nd = "\\D"

        df = df.copy()

        # Strings básicas
        ws = "\\s+"
        df["deputy_name"]      = df["txNomeParlamentar"].fillna("").astype(str).str.strip().str.upper().str.replace(ws, " ", regex=True)
        df["deputy_cpf_raw"]   = df["cpf"].fillna("").astype(str).str.strip()
        df["deputy_id"]        = df["nuDeputadoId"].fillna("").astype(str).str.strip()
        df["uf"]               = df["sgUF"].fillna("").astype(str).str.strip()
        df["partido"]          = df["sgPartido"].fillna("").astype(str).str.strip()
        df["supplier_doc_raw"] = df["txtCNPJCPF"].fillna("").astype(str)
        df["supplier_name"]    = df["txtFornecedor"].fillna("").astype(str).str.strip().str.upper().str.replace(ws, " ", regex=True)
        df["expense_type"]     = df["txtDescricao"].fillna("").astype(str).str.strip()

        # Parse de data vetorizado
        date_raw = df["datEmissao"].fillna("").astype(str).str.strip()
        parsed = pd.to_datetime(date_raw, format="%d/%m/%Y %H:%M:%S", errors="coerce")
        parsed = parsed.where(~parsed.isna(), pd.to_datetime(date_raw, format="%d/%m/%Y", errors="coerce"))
        parsed = parsed.where(~parsed.isna(), pd.to_datetime(date_raw, format="%Y-%m-%d", errors="coerce"))
        parsed = parsed.where(~parsed.isna(), pd.to_datetime(date_raw, format="%Y%m%d", errors="coerce"))
        df["date"] = parsed.dt.strftime("%Y-%m-%d").fillna("")

        # Parse de valor BRL vetorizado
        val_raw = df["vlrLiquido"].fillna("").astype(str).str.strip()
        val_clean = val_raw.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df["value"] = pd.to_numeric(val_clean, errors="coerce").fillna(0.0)

        # Limpar documentos
        df["supplier_digits"]     = df["supplier_doc_raw"].str.replace(nd, "", regex=True)
        df["supplier_digits_len"] = df["supplier_digits"].str.len()

        # Filtrar inválidos
        mask_valid = (df["supplier_digits"].str.len() > 0) & (df["deputy_id"].str.len() > 0)
        df = df[mask_valid].copy()
        mask_cnpj = df["supplier_digits_len"] == 14
        mask_cpf  = df["supplier_digits_len"] == 11
        df = df[mask_cnpj | mask_cpf].copy()
        mask_cnpj = df["supplier_digits_len"] == 14
        mask_cpf  = df["supplier_digits_len"] == 11

        # Formatar CNPJ/CPF vetorizado
        def fmt_cnpj_vec(s: pd.Series) -> pd.Series:
            d = s.str.replace(nd, "", regex=True).str.zfill(14)
            return d.str[:2]+"."+d.str[2:5]+"."+d.str[5:8]+"/"+d.str[8:12]+"-"+d.str[12:14]

        def fmt_cpf_vec(s: pd.Series) -> pd.Series:
            d = s.str.replace(nd, "", regex=True).str.zfill(11)
            return d.str[:3]+"."+d.str[3:6]+"."+d.str[6:9]+"-"+d.str[9:11]

        df["supplier_doc"] = ""
        if mask_cnpj.any():
            df.loc[mask_cnpj, "supplier_doc"] = fmt_cnpj_vec(df.loc[mask_cnpj, "supplier_doc_raw"])
        if mask_cpf.any():
            df.loc[mask_cpf, "supplier_doc"] = fmt_cpf_vec(df.loc[mask_cpf, "supplier_doc_raw"])

        # expense_id — hash vetorizado
        df["expense_id"] = pd.util.hash_pandas_object(
            df[["deputy_id", "date", "supplier_doc", "value"]], index=False
        ).astype(str).str[:16]

        # Expenses
        exp = df[["expense_id", "deputy_id", "expense_type", "value", "date", "supplier_doc"]].copy()
        exp = exp.rename(columns={"expense_type": "type"})
        exp["description"] = exp["type"]
        exp["source"] = "camara"
        exp = exp.drop_duplicates(subset=["expense_id"])
        expenses = exp.to_dict("records")

        # Deputies com CPF
        df["deputy_cpf_digits"] = df["deputy_cpf_raw"].str.replace(nd, "", regex=True)
        mask_has_cpf = df["deputy_cpf_digits"].str.len() == 11
        df_cpf = df[mask_has_cpf].copy()
        if not df_cpf.empty:
            df_cpf["deputy_cpf"] = fmt_cpf_vec(df_cpf["deputy_cpf_raw"])
            deputies_cpf = df_cpf[["deputy_cpf", "deputy_name", "deputy_id", "uf", "partido"]].rename(
                columns={"deputy_cpf": "cpf", "deputy_name": "name"}
            ).drop_duplicates(subset=["cpf"]).to_dict("records")
            gastou_cpf = df_cpf[["deputy_cpf", "expense_id"]].rename(
                columns={"deputy_cpf": "source_key", "expense_id": "target_key"}
            ).drop_duplicates().to_dict("records")
        else:
            deputies_cpf = []
            gastou_cpf   = []

        # Deputies sem CPF
        df_noid = df[~mask_has_cpf].copy()
        if not df_noid.empty:
            deputies_id = df_noid[["deputy_id", "deputy_name", "uf", "partido"]].rename(
                columns={"deputy_name": "name"}
            ).drop_duplicates(subset=["deputy_id"]).to_dict("records")
            gastou_id = df_noid[["deputy_id", "expense_id"]].rename(
                columns={"expense_id": "target_key"}
            ).drop_duplicates().to_dict("records")
        else:
            deputies_id = []
            gastou_id   = []

        # Suppliers
        suppliers_cnpj = (
            df[mask_cnpj][["supplier_doc", "supplier_name"]]
            .rename(columns={"supplier_doc": "cnpj", "supplier_name": "razao_social"})
            .drop_duplicates(subset=["cnpj"]).to_dict("records")
        ) if mask_cnpj.any() else []

        suppliers_cpf = (
            df[mask_cpf][["supplier_doc", "supplier_name"]]
            .rename(columns={"supplier_doc": "cpf", "supplier_name": "name"})
            .drop_duplicates(subset=["cpf"]).to_dict("records")
        ) if mask_cpf.any() else []

        forneceu = df[["supplier_doc", "expense_id"]].rename(
            columns={"supplier_doc": "source_key", "expense_id": "target_key"}
        ).drop_duplicates().to_dict("records")

        return (expenses, deputies_cpf, deputies_id, suppliers_cnpj, suppliers_cpf, gastou_cpf, gastou_id, forneceu)

    def run(self) -> None:
        """Processa cada CSV da câmara um por vez — sem acumular RAM.

        FIX vs colega: pd.read_csv com chunksize retorna TextFileReader,
        não DataFrame. Iteramos os chunks e processamos cada um separadamente.
        """
        camara_dir = Path(self.data_dir) / "camara"
        csv_files = sorted(camara_dir.glob("*.csv"))
        if not csv_files:
            logger.warning("[camara] Nenhum CSV encontrado em %s", camara_dir)
            return

        loader = Neo4jBatchLoader(self.driver, batch_size=250)

        # Deduplicação global entre arquivos e chunks
        seen_expenses:  set[str] = set()
        seen_deputies:  set[str] = set()
        seen_dep_id:    set[str] = set()
        seen_suppliers: set[str] = set()

        total_expenses = 0
        total_files = len(csv_files)

        for i, f in enumerate(csv_files, 1):
            logger.info("[camara] Processando %d/%d: %s", i, total_files, f.name)

            # Lê o CSV em chunks — nunca carrega o arquivo inteiro na RAM
            reader = pd.read_csv(
                f,
                sep=";",
                dtype=str,
                encoding="utf-8-sig",
                keep_default_na=False,
                chunksize=self.chunk_size,
            )

            chunk_num = 0
            for chunk_df in reader:  # ← FIX: itera o TextFileReader corretamente
                chunk_num += 1
                logger.info("  chunk %d — %d linhas", chunk_num, len(chunk_df))

                (
                    expenses, deputies_cpf, deputies_id,
                    suppliers_cnpj, suppliers_cpf,
                    gastou_cpf, gastou_id, forneceu,
                ) = self._transform_chunk(chunk_df)

                del chunk_df  # libera RAM imediatamente

                # Aplicar limit
                if self.limit:
                    remaining = self.limit - total_expenses
                    if remaining <= 0:
                        logger.info("[camara] Limit %d atingido — parando.", self.limit)
                        self.cleanup()
                        return
                    expenses = expenses[:remaining]

                # Deduplica expenses entre chunks e arquivos
                new_expenses = [e for e in expenses if e["expense_id"] not in seen_expenses]
                seen_expenses.update(e["expense_id"] for e in new_expenses)

                if not new_expenses:
                    logger.info("  Sem expenses novos neste chunk — próximo.")
                    continue

                expense_ids = {e["expense_id"] for e in new_expenses}

                # Load Expenses
                with loader.open_session() as session:

                    count = loader.load_nodes("Expense", new_expenses, key_field="expense_id", session=session)
                    logger.info("  Loaded %d Expense nodes", count)
                    total_expenses += count

                    # Load Deputies CPF
                    new_dep_cpf = [d for d in deputies_cpf if d["cpf"] not in seen_deputies]
                    seen_deputies.update(d["cpf"] for d in new_dep_cpf)
                    if new_dep_cpf:
                        loader.load_nodes("Person", new_dep_cpf, key_field="cpf", session=session)

                    # Load Deputies ID (sem CPF)
                    new_dep_id = [d for d in deputies_id if d["deputy_id"] not in seen_dep_id]
                    seen_dep_id.update(d["deputy_id"] for d in new_dep_id)
                    if new_dep_id:
                        query = (
                            "UNWIND $rows AS row "
                            "MERGE (p:Person {deputy_id: row.deputy_id}) "
                            "SET p.name = row.name, p.uf = row.uf, p.partido = row.partido"
                        )
                        loader.run_query_with_retry(query, new_dep_id, session=session)

                    # Load Suppliers CNPJ
                    new_sup_cnpj = [s for s in suppliers_cnpj if s["cnpj"] not in seen_suppliers]
                    seen_suppliers.update(s["cnpj"] for s in new_sup_cnpj)
                    if new_sup_cnpj:
                        loader.load_nodes("Company", new_sup_cnpj, key_field="cnpj", session=session)

                    # Load Suppliers CPF
                    new_sup_cpf = [s for s in suppliers_cpf if s["cpf"] not in seen_suppliers]
                    seen_suppliers.update(s["cpf"] for s in new_sup_cpf)
                    if new_sup_cpf:
                        loader.load_nodes("Person", new_sup_cpf, key_field="cpf", session=session)

                    # GASTOU CPF
                    gastou_cpf_new = [r for r in gastou_cpf if r["target_key"] in expense_ids]
                    if gastou_cpf_new:
                        loader.load_relationships(
                            rel_type="GASTOU",
                            rows=gastou_cpf_new,
                            source_label="Person",
                            source_key="cpf",
                            target_label="Expense",
                            target_key="expense_id",
                            session=session,
                        )

                    # GASTOU deputy_id
                    gastou_id_new = [r for r in gastou_id if r["target_key"] in expense_ids]
                    if gastou_id_new:
                        query = (
                            "UNWIND $rows AS row "
                            "MATCH (p:Person {deputy_id: row.deputy_id}) "
                            "MATCH (e:Expense {expense_id: row.target_key}) "
                            "MERGE (p)-[:GASTOU]->(e)"
                        )
                        loader.run_query_with_retry(query, gastou_id_new, session=session)

                    # FORNECEU
                    forneceu_new = [r for r in forneceu if r["target_key"] in expense_ids]
                    if forneceu_new:
                        query = (
                            "UNWIND $rows AS row "
                            "MATCH (e:Expense {expense_id: row.target_key}) "
                            "OPTIONAL MATCH (c:Company {cnpj: row.source_key}) "
                            "OPTIONAL MATCH (p:Person {cpf: row.source_key}) "
                            "WITH e, coalesce(c, p) AS src WHERE src IS NOT NULL "
                            "MERGE (src)-[:FORNECEU]->(e)"
                        )
                        loader.run_query_with_retry(query, forneceu_new, session=session)

            logger.info("  ✅ %s concluído — total acumulado: %d expenses", f.name, total_expenses)

        logger.info("[camara] ✅ CONCLUÍDO — %d expenses no total", total_expenses)
        self.cleanup()
