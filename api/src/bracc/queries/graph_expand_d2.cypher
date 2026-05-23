UNWIND $expand_plan AS plan
MATCH (n1)
WHERE elementId(n1) = plan.node_id
OPTIONAL MATCH (n1)-[r2]-(n2)
WHERE NOT (n2:User OR n2:Investigation OR n2:Annotation OR n2:Tag)
  AND type(r2) IN $rel_types
  AND elementId(n2) <> $center_id
WITH plan, n1, n2, r2
ORDER BY
  CASE type(r2)
    WHEN 'SOCIO_DE'     THEN 1
    WHEN 'FORNECEU'     THEN 2
    WHEN 'DOOU'         THEN 3
    WHEN 'SANCIONADA'   THEN 4
    WHEN 'AUTOR_EMENDA' THEN 5
    ELSE 10
  END
WITH plan, collect(DISTINCT n2)[..plan.limit] AS nodes2, collect(DISTINCT r2)[..plan.limit] AS rels2
UNWIND CASE WHEN size(rels2) = 0 THEN [NULL] ELSE rels2 END AS r
WITH nodes2, collect(DISTINCT r) AS rels
UNWIND CASE WHEN size(nodes2) = 0 THEN [NULL] ELSE nodes2 END AS n
RETURN collect(DISTINCT n) AS nodes,
       rels AS relationships
