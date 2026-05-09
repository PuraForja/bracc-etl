"""Teste isolado do pipeline camara com logs detalhados em cada etapa."""
import logging
import sys
from pathlib import Path
import pandas as pd
from neo4j import GraphDatabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

DATA_DIR = Path("../data/camara")
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "changeme")
CHUNK_SIZE = 5000

def transform(df):
    nd = "\\D"
    ws = "\\s+"
    log.info("  [T1] strings basicas...")
    df = df.copy()
    df["deputy_name"]      = df["txNomeParlamentar"].fillna("").astype(str).str.strip().str.upper().str.replace(ws, " ", regex=True)
    df["deputy_cpf_raw"]   = df["cpf"].fillna("").astype(str).str.strip()
    df["deputy_id"]        = df["nuDeputadoId"].fillna("").astype(str).str.strip()
    df["uf"]               = df["sgUF"].fillna("").astype(str).str.strip()
    df["partido"]          = df["sgPartido"].fillna("").astype(str).str.strip()
    df["supplier_doc_raw"] = df["txtCNPJCPF"].fillna("").astype(str)
    df["supplier_name"]    = df["txtFornecedor"].fillna("").astype(str).str.strip().str.upper().str.replace(ws, " ", regex=True)
    df["expense_type"]     = df["txtDescricao"].fillna("").astype(str).str.strip()
    log.info("  [T2] parse data...")
    date_raw = df["datEmissao"].fillna("").astype(str).str.strip()
    parsed = pd.to_datetime(date_raw, format="%d/%m/%Y %H:%M:%S", errors="coerce")
    parsed = parsed.where(~parsed.isna(), pd.to_datetime(date_raw, format="%d/%m/%Y", errors="coerce"))
    parsed = parsed.where(~parsed.isna(), pd.to_datetime(date_raw, format="%Y-%m-%d", errors="coerce"))
    df["date"] = parsed.dt.strftime("%Y-%m-%d").fillna("")
    log.info("  [T3] parse valor...")
    val_raw = df["vlrLiquido"].fillna("").astype(str).str.strip()
    val_clean = val_raw.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df["value"] = pd.to_numeric(val_clean, errors="coerce").fillna(0.0)
    log.info("  [T4] limpar documentos...")
    df["supplier_digits"]     = df["supplier_doc_raw"].str.replace(nd, "", regex=True)
    df["supplier_digits_len"] = df["supplier_digits"].str.len()
    mask_valid = (df["supplier_digits"].str.len() > 0) & (df["deputy_id"].str.len() > 0)
    df = df[mask_valid].copy()
    mask_cnpj = df["supplier_digits_len"] == 14
    mask_cpf  = df["supplier_digits_len"] == 11
    df = df[mask_cnpj | mask_cpf].copy()
    mask_cnpj = df["supplier_digits_len"] == 14
    mask_cpf  = df["supplier_digits_len"] == 11
    log.info("  [T5] formatar CNPJ/CPF (%d rows validos)...", len(df))
    def fmt_cnpj_vec(s):
        d = s.str.replace(nd, "", regex=True).str.zfill(14)
        return d.str[:2]+"."+d.str[2:5]+"."+d.str[5:8]+"/"+d.str[8:12]+"-"+d.str[12:14]
    def fmt_cpf_vec(s):
        d = s.str.replace(nd, "", regex=True).str.zfill(11)
        return d.str[:3]+"."+d.str[3:6]+"."+d.str[6:9]+"-"+d.str[9:11]
    df["supplier_doc"] = ""
    if mask_cnpj.any():
        df.loc[mask_cnpj, "supplier_doc"] = fmt_cnpj_vec(df.loc[mask_cnpj, "supplier_doc_raw"])
    if mask_cpf.any():
        df.loc[mask_cpf, "supplier_doc"] = fmt_cpf_vec(df.loc[mask_cpf, "supplier_doc_raw"])
    log.info("  [T6] expense_id hash...")
    df["expense_id"] = pd.util.hash_pandas_object(
        df[["deputy_id", "date", "supplier_doc", "value"]], index=False
    ).astype(str).str[:16]
    log.info("  [T7] to_dict expenses...")
    exp = df[["expense_id", "deputy_id", "expense_type", "value", "date", "supplier_doc"]].copy()
    exp = exp.rename(columns={"expense_type": "type"})
    exp["description"] = exp["type"]
    exp["source"] = "camara"
    exp = exp.drop_duplicates(subset=["expense_id"])
    expenses = exp.to_dict("records")
    log.info("  [T8] to_dict deputies/suppliers (%d expenses)...", len(expenses))
    df["deputy_cpf_digits"] = df["deputy_cpf_raw"].str.replace(nd, "", regex=True)
    mask_has_cpf = df["deputy_cpf_digits"].str.len() == 11
    df_cpf = df[mask_has_cpf].copy()
    if not df_cpf.empty:
        df_cpf = df_cpf.copy()
        df_cpf["deputy_cpf"] = fmt_cpf_vec(df_cpf["deputy_cpf_raw"])
        deputies_cpf = df_cpf[["deputy_cpf","deputy_name","deputy_id","uf","partido"]].rename(
            columns={"deputy_cpf":"cpf","deputy_name":"name"}
        ).drop_duplicates(subset=["cpf"]).to_dict("records")
        gastou_cpf = df_cpf[["deputy_cpf","expense_id"]].rename(
            columns={"deputy_cpf":"source_key","expense_id":"target_key"}
        ).drop_duplicates().to_dict("records")
    else:
        deputies_cpf, gastou_cpf = [], []
    df_noid = df[~mask_has_cpf].copy()
    if not df_noid.empty:
        deputies_id = df_noid[["deputy_id","deputy_name","uf","partido"]].rename(
            columns={"deputy_name":"name"}
        ).drop_duplicates(subset=["deputy_id"]).to_dict("records")
        gastou_id = df_noid[["deputy_id","expense_id"]].rename(
            columns={"expense_id":"target_key"}
        ).drop_duplicates().to_dict("records")
    else:
        deputies_id, gastou_id = [], []
    suppliers_cnpj = df[mask_cnpj][["supplier_doc","supplier_name"]].rename(
        columns={"supplier_doc":"cnpj","supplier_name":"razao_social"}
    ).drop_duplicates(subset=["cnpj"]).to_dict("records") if mask_cnpj.any() else []
    suppliers_cpf = df[mask_cpf][["supplier_doc","supplier_name"]].rename(
        columns={"supplier_doc":"cpf","supplier_name":"name"}
    ).drop_duplicates(subset=["cpf"]).to_dict("records") if mask_cpf.any() else []
    forneceu = df[["supplier_doc","expense_id"]].rename(
        columns={"supplier_doc":"source_key","expense_id":"target_key"}
    ).drop_duplicates().to_dict("records")
    log.info("  [T9] transform CONCLUIDO — %d expenses, %d forneceu", len(expenses), len(forneceu))
    return dict(expenses=expenses, deputies_cpf=deputies_cpf, deputies_id=deputies_id,
                suppliers_cnpj=suppliers_cnpj, suppliers_cpf=suppliers_cpf,
                gastou_cpf=gastou_cpf, gastou_id=gastou_id, forneceu=forneceu)

def main():
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        log.error("Nenhum CSV em %s", DATA_DIR)
        sys.exit(1)
    f = csv_files[0]
    log.info("Testando: %s", f.name)
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    log.info("Neo4j conectado")
    reader = pd.read_csv(f, sep=";", dtype=str, encoding="utf-8-sig",
                         keep_default_na=False, chunksize=CHUNK_SIZE)
    for chunk_num, chunk_df in enumerate(reader, 1):
        log.info("chunk %d — %d linhas", chunk_num, len(chunk_df))
        result = transform(chunk_df)
        del chunk_df
        expenses = result["expenses"]
        log.info("  [L1] load Expense (%d)...", len(expenses))
        with driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "UNWIND $rows AS row MERGE (n:Expense {expense_id: row.expense_id}) SET n.value = row.value",
                    rows=expenses[:500]
                )
            )
        log.info("  [L2] Expense OK")
        if chunk_num >= 2:
            log.info("2 chunks OK — SUCESSO")
            break
    driver.close()
    log.info("TESTE CONCLUIDO")

if __name__ == "__main__":
    main()
