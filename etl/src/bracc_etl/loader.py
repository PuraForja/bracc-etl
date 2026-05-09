import logging
import os
import re
import time
from typing import Any
from neo4j import Driver, Session
from neo4j.exceptions import TransientError, ServiceUnavailable

logger = logging.getLogger(__name__)
_SAFE_KEY = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_MAX_RETRIES = 5


class Neo4jBatchLoader:
    def __init__(self, driver: Driver, batch_size: int = 500, neo4j_database: str | None = None) -> None:
        self.driver = driver
        self.batch_size = batch_size
        self.neo4j_database = neo4j_database or os.getenv("NEO4J_DATABASE", "neo4j")
        self._total_written = 0

    def open_session(self):
        return self.driver.session(database=self.neo4j_database)

    def _run_batch_once(self, query: str, batch: list[dict[str, Any]], session=None) -> None:
        def _tx(tx: Any) -> None:
            tx.run(query, rows=batch)
        if session is not None:
            session.execute_write(_tx)
        else:
            with self.driver.session(database=self.neo4j_database) as s:
                s.execute_write(_tx)

    def _run_batches(self, query: str, rows: list[dict[str, Any]], session=None) -> int:
        total = 0
        for i in range(0, len(rows), self.batch_size):
            batch = rows[i: i + self.batch_size]
            for attempt in range(_MAX_RETRIES):
                try:
                    self._run_batch_once(query, batch, session=session)
                    total += len(batch)
                    self._total_written += len(batch)
                    break
                except (TransientError, ServiceUnavailable) as e:
                    wait = 2 ** attempt
                    logger.warning("Erro transiente batch %d, tentativa %d/%d em %ds: %s", i // self.batch_size, attempt + 1, _MAX_RETRIES, wait, e)
                    time.sleep(wait)
                except Exception as e:
                    logger.error("Erro inesperado batch %d: %s — pulando", i // self.batch_size, e)
                    break
            else:
                logger.error("Batch %d falhou após %d tentativas — pulando", i // self.batch_size, _MAX_RETRIES)
        if total >= 10_000:
            logger.info("  Batch written: %d rows (cumulative: %d)", total, self._total_written)
        return total

    def run_query_with_retry(self, query: str, rows: list[dict[str, Any]], batch_size: int = 500, session=None) -> int:
        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i: i + batch_size]
            for attempt in range(_MAX_RETRIES):
                try:
                    self._run_batch_once(query, batch, session=session)
                    total += len(batch)
                    self._total_written += len(batch)
                    break
                except (TransientError, ServiceUnavailable) as e:
                    wait = 2 ** attempt
                    logger.warning("Deadlock batch %d, retry %d/%d em %ds: %s", i // batch_size, attempt + 1, _MAX_RETRIES, wait, e)
                    time.sleep(wait)
                except Exception as e:
                    logger.error("Erro inesperado batch %d: %s — pulando", i // batch_size, e)
                    break
            else:
                logger.error("Batch %d falhou após %d retries — pulando", i // batch_size, _MAX_RETRIES)
            if total > 0 and total % 100_000 == 0:
                logger.info("  Progress: %d rows loaded", total)
        return total

    def load_nodes(self, label: str, rows: list[dict[str, Any]], key_field: str, session=None) -> int:
        rows = [r for r in rows if r.get(key_field)]
        if not rows:
            return 0
        all_keys: set[str] = set()
        for r in rows:
            all_keys.update(r.keys())
        all_keys.discard(key_field)
        all_keys = {k for k in all_keys if _SAFE_KEY.match(k)}
        props = ", ".join(f"n.{k} = row.{k}" for k in sorted(all_keys)) if all_keys else ""
        set_clause = f"SET {props}" if props else ""
        query = f"UNWIND $rows AS row MERGE (n:{label} {{{key_field}: row.{key_field}}}) {set_clause}"
        return self._run_batches(query, rows, session=session)

    def load_relationships(self, rel_type: str, rows: list[dict[str, Any]], source_label: str, source_key: str, target_label: str, target_key: str, properties: list[str] | None = None, session=None) -> int:
        rows = [r for r in rows if r.get("source_key") and r.get("target_key")]
        if not rows:
            return 0
        props = ""
        if properties:
            props = f"SET {', '.join(f'r.{p} = row.{p}' for p in properties)}"
        query = f"UNWIND $rows AS row MATCH (a:{source_label} {{{source_key}: row.source_key}}) MATCH (b:{target_label} {{{target_key}: row.target_key}}) MERGE (a)-[r:{rel_type}]->(b) {props}"
        return self._run_batches(query, rows, session=session)

    def run_query(self, query: str, rows: list[dict[str, Any]]) -> int:
        return self._run_batches(query, rows)
