"""
link_tse_nocpf.py
Cruza Person TSE sem CPF com candidaturas históricas (2016-2022)
onde o CPF era público, e cria SAME_AS no Neo4j.
"""
import os
import re
import unicodedata
import logging
import pandas as pd
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "changeme")

TSE_RAW = os.path.expanduser("~/bracc/data/tse/raw")
ANOS = [2016, 2018, 2020, 2022]
BRASIL_FILES = [
    f"{TSE_RAW}/candidatos_{ano}_extracted/consulta_cand_{ano}_BRASIL.csv"
    for ano in ANOS
]

def normalize(name: str) -> str:
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = re.sub(r"[^A-Z0-9 ]", "", name.upper())
    return " ".join(name.split())

def build_cpf_lookup() -> dict[str, set]:
    """nome_normalizado → set of CPFs from 2016-2022."""
    lookup: dict[str, set] = {}
    for path in BRASIL_FILES:
        if not os.path.exists(path):
            logger.warning("Arquivo nao encontrado: %s", path)
            continue
        logger.info("Carregando %s ...", path)
        df = pd.read_csv(path, sep=";", encoding="latin-1", dtype=str,
                         usecols=["NM_CANDIDATO", "NR_CPF_CANDIDATO"])
        df = df.dropna(subset=["NM_CANDIDATO", "NR_CPF_CANDIDATO"])
        df = df[~df["NR_CPF_CANDIDATO"].str.strip().isin(["-4", "", "#NULO"])]
        for _, row in df.iterrows():
            nome = normalize(str(row["NM_CANDIDATO"]))
            cpf_raw = re.sub(r"\D", "", str(row["NR_CPF_CANDIDATO"]))
            if len(cpf_raw) == 11:
                lookup.setdefault(nome, set()).add(cpf_raw)
    logger.info("Lookup construido: %d nomes unicos", len(lookup))
    return lookup

def fetch_nocpf_persons(driver) -> list[dict]:
    """Busca Person TSE sem CPF no Neo4j."""
    query = (
        "MATCH (p:Person) "
        "WHERE p.sq_candidato IS NOT NULL AND p.cpf IS NULL "
        "RETURN p.sq_candidato AS sq, p.name AS name, elementId(p) AS eid"
    )
    with driver.session() as session:
        result = session.run(query)
        rows = [dict(r) for r in result]
    logger.info("Person TSE sem CPF: %d", len(rows))
    return rows

def create_same_as(driver, links: list[dict]) -> None:
    """Cria SAME_AS entre Person TSE (sq_candidato) e Person CPF."""
    query = (
        "UNWIND $rows AS row "
        "MATCH (tse:Person {sq_candidato: row.sq}) "
        "MATCH (cpf:Person {cpf: row.cpf_fmt}) "
        "WHERE tse <> cpf "
        "MERGE (tse)-[:SAME_AS {source: 'historico_tse', confidence: 0.99}]->(cpf)"
    )
    batch_size = 500
    total = 0
    with driver.session() as session:
        for i in range(0, len(links), batch_size):
            batch = links[i:i+batch_size]
            session.run(query, rows=batch)
            total += len(batch)
            if total % 5000 == 0:
                logger.info("SAME_AS criados: %d", total)
    logger.info("Total SAME_AS criados: %d", total)

def format_cpf(cpf: str) -> str:
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def main():
    lookup = build_cpf_lookup()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    persons = fetch_nocpf_persons(driver)

    links = []
    skipped_homonym = 0
    skipped_notfound = 0

    for p in persons:
        nome_norm = normalize(str(p["name"]))
        cpfs = lookup.get(nome_norm)
        if not cpfs:
            skipped_notfound += 1
            continue
        if len(cpfs) > 1:
            skipped_homonym += 1
            continue
        cpf_raw = next(iter(cpfs))
        links.append({"sq": p["sq"], "cpf_fmt": format_cpf(cpf_raw)})

    logger.info("Links a criar: %d", len(links))
    logger.info("Nao encontrados: %d", skipped_notfound)
    logger.info("Homonimos ignorados: %d", skipped_homonym)

    if links:
        create_same_as(driver, links)

    driver.close()
    logger.info("Concluido.")

if __name__ == "__main__":
    main()
