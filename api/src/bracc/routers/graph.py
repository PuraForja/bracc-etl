import logging
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import AsyncSession
from bracc.constants import PEP_ROLES
from bracc.dependencies import get_session
from bracc.models.entity import SourceAttribution
from bracc.models.graph import GraphEdge, GraphNode, GraphResponse, TruncatedNode
from bracc.services.neo4j_service import execute_query, sanitize_props
from bracc.services.public_guard import (
    enforce_entity_lookup_enabled,
    enforce_person_access_policy,
    has_person_labels,
    infer_exposure_tier,
    sanitize_public_properties,
    should_hide_person_entities,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/graph", tags=["graph"])

_GRAPH_PROPS = {
    "name", "razao_social", "cnpj", "cpf", "value", "date",
    "type", "uf", "cargo", "partido",
}
_DEFAULT_LABEL_FILTER = "-User|-Investigation|-Annotation|-Tag"
_LABEL_MAP: dict[str, str] = {
    "person": "Person",
    "company": "Company",
    "contract": "Contract",
    "sanction": "Sanction",
    "election": "Election",
    "amendment": "Amendment",
    "finance": "Finance",
    "embargo": "Embargo",
    "health": "Health",
    "education": "Education",
    "convenio": "Convenio",
    "laborstats": "LaborStats",
}

_ALLOWED_REL_TYPES = [
    "SOCIO_DE", "DOOU", "CANDIDATO_EM", "VENCEU", "AUTOR_EMENDA", "SANCIONADA",
    "OPERA_UNIDADE", "DEVE", "RECEBEU_EMPRESTIMO", "EMBARGADA", "MANTEDORA_DE",
    "BENEFICIOU", "GEROU_CONVENIO", "SAME_AS", "POSSIBLY_SAME_AS", "OFFICER_OF",
    "INTERMEDIARY_OF", "GLOBAL_PEP_MATCH", "CVM_SANCIONADA", "GASTOU", "FORNECEU",
    "TEM_REMUNERACAO", "POSSIVEL_MESMO_INDIVIDUO",
]

# Orçamento global de edges no depth=2
_DEPTH2_BUDGET = 800


def _degree_limit(degree: int) -> int:
    """Retorna o limite de vizinhos a expandir baseado no grau do node."""
    if degree <= 30:
        return degree  # expande tudo
    if degree <= 100:
        return 15
    if degree <= 1000:
        return 5
    return 2


def _is_pep(properties: dict[str, Any]) -> bool:
    role = str(properties.get("role", "")).lower()
    return any(keyword in role for keyword in PEP_ROLES)


def _extract_label(node: Any, labels: list[str]) -> str:
    props = dict(node)
    entity_type = labels[0].lower() if labels else ""
    if entity_type == "company":
        return str(props.get("razao_social", props.get("name", props.get("nome_fantasia", ""))))
    if entity_type == "finance":
        if props.get("value"):
            return f"Finance: R$ {props.get('value', 0):,.2f}"
        return str(props.get("type", "Finance"))
    if entity_type == "embargo":
        return str(props.get("description", props.get("uf", "Embargo")))
    if entity_type == "convenio":
        return str(props.get("object", props.get("convenio_id", "Convenio")))
    return str(props.get("name", str(props.get("id", ""))))


def _slim_props(node_props: dict[str, Any]) -> dict[str, str | float | int | bool | None]:
    return sanitize_props({k: v for k, v in node_props.items() if k in _GRAPH_PROPS})


def _build_label_filter(type_list: list[str] | None) -> str:
    if not type_list:
        return _DEFAULT_LABEL_FILTER
    parts: list[str] = []
    for t in type_list:
        neo4j_label = _LABEL_MAP.get(t)
        if neo4j_label:
            parts.append(f"+{neo4j_label}")
    if not parts:
        return _DEFAULT_LABEL_FILTER
    return "|".join(parts) + "|-User|-Investigation|-Annotation|-Tag"


def _parse_nodes(raw_nodes: list, center_id: str, node_ids: set) -> list[GraphNode]:
    nodes: list[GraphNode] = []
    for node in raw_nodes:
        node_id = node.element_id
        labels = list(node.labels)
        if should_hide_person_entities() and has_person_labels(labels):
            if node_id == center_id:
                enforce_person_access_policy(labels)
            continue
        node_ids.add(node_id)
        props = dict(node)
        source_val = props.pop("source", None)
        sources: list[SourceAttribution] = []
        if isinstance(source_val, str):
            sources = [SourceAttribution(database=source_val)]
        elif isinstance(source_val, list):
            sources = [SourceAttribution(database=s) for s in source_val]
        doc_id = (
            props.get("cpf") or props.get("cnpj") or props.get("contract_id")
            or props.get("sanction_id") or props.get("amendment_id")
            or props.get("cnes_code") or props.get("finance_id")
            or props.get("embargo_id") or props.get("school_id")
            or props.get("convenio_id") or props.get("stats_id")
        )
        nodes.append(GraphNode(
            id=node_id,
            label=_extract_label(node, labels),
            type=labels[0].lower() if labels else "unknown",
            document_id=str(doc_id) if doc_id else None,
            properties=sanitize_public_properties(_slim_props(props)),
            sources=sources,
            is_pep=_is_pep(props),
            exposure_tier=infer_exposure_tier(labels),
        ))
    return nodes


def _parse_edges(raw_rels: list, node_ids: set) -> list[GraphEdge]:
    edges: list[GraphEdge] = []
    seen: set[str] = set()
    for rel in raw_rels:
        rel_id = rel.element_id
        if rel_id in seen:
            continue
        seen.add(rel_id)
        source_id = rel.start_node.element_id
        target_id = rel.end_node.element_id
        if source_id not in node_ids or target_id not in node_ids:
            continue
        rel_props = dict(rel)
        confidence = float(rel_props.pop("confidence", 1.0))
        rel_source_val = rel_props.pop("source", None)
        rel_sources: list[SourceAttribution] = []
        if isinstance(rel_source_val, str):
            rel_sources = [SourceAttribution(database=rel_source_val)]
        elif isinstance(rel_source_val, list):
            rel_sources = [SourceAttribution(database=s) for s in rel_source_val]
        edges.append(GraphEdge(
            id=rel_id,
            source=source_id,
            target=target_id,
            type=rel.type,
            properties=sanitize_public_properties(sanitize_props(rel_props)),
            confidence=confidence,
            sources=rel_sources,
            exposure_tier="public_safe",
        ))
    return edges


@router.get("/{entity_id}", response_model=GraphResponse)
async def get_graph(
    entity_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    depth: Annotated[int, Query(ge=1, le=4)] = 2,
    entity_types: Annotated[str | None, Query()] = None,
) -> GraphResponse:
    enforce_entity_lookup_enabled()
    type_list = [t.strip().lower() for t in entity_types.split(",")] if entity_types else None

    # Grau do node central — supernode guard
    degree_records = await execute_query(
        session, "node_degree", {"entity_id": entity_id}, timeout=5,
    )
    if not degree_records:
        raise HTTPException(status_code=404, detail="Entity not found")
    center_degree = degree_records[0]["degree"] if degree_records else 0
    if center_degree > 500:
        logger.info("Supernode central (degree=%d) para %s, limitando depth=1", center_degree, entity_id)
        depth = min(depth, 1)

    # --- DEPTH 1 ---
    d1_records = await execute_query(
        session,
        "graph_expand_d1",
        {"entity_id": entity_id, "rel_types": _ALLOWED_REL_TYPES},
        timeout=15,
    )
    if not d1_records:
        raise HTTPException(status_code=404, detail="Entity not found")

    d1 = d1_records[0]
    raw_nodes_d1 = list(d1["nodes"])
    raw_rels_d1 = list(d1["relationships"])

    node_ids: set[str] = set()
    nodes = _parse_nodes(raw_nodes_d1, entity_id, node_ids)
    edges = _parse_edges(raw_rels_d1, node_ids)

    truncated_nodes: list[TruncatedNode] = []

    if depth >= 2:
        # Mede grau de todos os nodes do depth=1 em uma única query
        d1_node_ids = [n.id for n in nodes if n.id != entity_id]

        if d1_node_ids:
            degree_records = await execute_query(
                session,
                "node_degrees",
                {"node_ids": d1_node_ids, "rel_types": _ALLOWED_REL_TYPES},
                timeout=10,
            )
            degree_map: dict[str, int] = {
                r["id"]: r["degree"] for r in degree_records
            }

            # Monta plano de expansão com orçamento global
            budget = _DEPTH2_BUDGET
            expand_plan: list[dict] = []
            for node_id in d1_node_ids:
                if budget <= 0:
                    break
                degree = degree_map.get(node_id, 0)
                limit = min(_degree_limit(degree), budget)
                expand_plan.append({
                    "node_id": node_id,
                    "limit": limit,
                    "total_degree": degree,
                })
                budget -= limit

            # Expande depth=2 com limites adaptativos por node
            if expand_plan:
                d2_records = await execute_query(
                    session,
                    "graph_expand_d2",
                    {
                        "expand_plan": expand_plan,
                        "rel_types": _ALLOWED_REL_TYPES,
                        "center_id": entity_id,
                    },
                    timeout=20,
                )

                raw_nodes_d2 = []
                raw_rels_d2 = []
                for r in d2_records:
                    raw_nodes_d2.extend(r.get("nodes", []))
                    raw_rels_d2.extend(r.get("relationships", []))

                new_nodes = _parse_nodes(raw_nodes_d2, entity_id, node_ids)
                new_edges = _parse_edges(raw_rels_d2, node_ids)
                nodes.extend(new_nodes)
                edges.extend(new_edges)

                # Registra truncamentos para o frontend
                returned_counts: dict[str, int] = {}
                for n in new_nodes:
                    parent_id = None
                    for e in new_edges:
                        if e.target == n.id and e.source in {p["node_id"] for p in expand_plan}:
                            parent_id = e.source
                            break
                        if e.source == n.id and e.target in {p["node_id"] for p in expand_plan}:
                            parent_id = e.target
                            break
                    if parent_id:
                        returned_counts[parent_id] = returned_counts.get(parent_id, 0) + 1

                for plan in expand_plan:
                    nid = plan["node_id"]
                    total = plan["total_degree"]
                    returned = returned_counts.get(nid, 0)
                    if returned < total:
                        truncated_nodes.append(TruncatedNode(
                            id=nid,
                            total_degree=total,
                            returned=returned,
                        ))

    return GraphResponse(
        nodes=nodes,
        edges=edges,
        center_id=entity_id,
        truncated_nodes=truncated_nodes,
    )