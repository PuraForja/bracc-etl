MATCH (center)
WHERE elementId(center) = $entity_id
  AND (center:Person OR center:Company OR center:Contract OR center:Sanction OR center:Election
       OR center:Amendment OR center:Finance OR center:Embargo OR center:Health OR center:Education
       OR center:Convenio OR center:LaborStats OR center:PublicOffice
       OR center:OffshoreEntity OR center:OffshoreOfficer OR center:GlobalPEP
       OR center:CVMProceeding OR center:Expense OR center:GovEmployee OR center:Partner
       OR center:InternationalSanction OR center:TaxWaiver OR center:GovTravel OR center:GovCardExpense OR center:Bid)
// Resolve cluster de identidade via community_id (WCC) — SAME_AS nao conta como salto
WITH center, center.community_id AS cid
OPTIONAL MATCH (identity_node)
WHERE cid IS NOT NULL AND identity_node.community_id = cid AND identity_node <> center
WITH center, collect(DISTINCT identity_node) + [center] AS cluster
// Expande depth=1 a partir de todos os nodes do cluster
UNWIND cluster AS cluster_node
OPTIONAL MATCH (cluster_node)-[r1]-(n1)
WHERE NOT (n1:User OR n1:Investigation OR n1:Annotation OR n1:Tag)
  AND type(r1) IN $rel_types
  AND NOT n1 IN cluster
WITH center, cluster,
     collect(DISTINCT n1) AS neighbors,
     collect(DISTINCT r1) AS neighbor_rels,
     collect(DISTINCT cluster_node) AS cluster_nodes
WITH center,
     neighbors + cluster_nodes AS raw_nodes,
     neighbor_rels AS raw_rels
UNWIND raw_nodes AS n
WITH center, collect(DISTINCT n) AS nodes, raw_rels
UNWIND CASE WHEN size(raw_rels) = 0 THEN [NULL] ELSE raw_rels END AS r
WITH center, nodes, collect(DISTINCT r) AS rels
RETURN nodes,
       [x IN rels WHERE x IS NOT NULL] AS relationships,
       elementId(center) AS center_id
