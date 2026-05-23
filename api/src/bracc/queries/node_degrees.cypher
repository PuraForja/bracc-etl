UNWIND $node_ids AS nid
MATCH (n)
WHERE elementId(n) = nid
RETURN
    elementId(n) AS id,
    size([(n)-[r]-() WHERE type(r) IN $rel_types | r]) AS degree
