MATCH (center)
WHERE elementId(center) = $entity_id
  AND (center:Person OR center:Company OR center:Contract OR center:Sanction OR center:Election
       OR center:Amendment OR center:Finance OR center:Embargo OR center:Health OR center:Education
       OR center:Convenio OR center:LaborStats OR center:PublicOffice
       OR center:OffshoreEntity OR center:OffshoreOfficer OR center:GlobalPEP
       OR center:CVMProceeding OR center:Expense OR center:GovEmployee OR center:Partner
       OR center:InternationalSanction OR center:TaxWaiver OR center:GovTravel OR center:GovCardExpense)
OPTIONAL MATCH (center)-[r1]-(n1)
WHERE NOT (n1:User OR n1:Investigation OR n1:Annotation OR n1:Tag)
  AND type(r1) IN $rel_types
WITH center, collect(DISTINCT n1) + [center] AS raw_nodes, collect(DISTINCT r1) AS raw_rels
UNWIND raw_nodes AS n
WITH center, collect(DISTINCT n) AS nodes, raw_rels
UNWIND CASE WHEN size(raw_rels) = 0 THEN [NULL] ELSE raw_rels END AS r
WITH center, nodes, collect(DISTINCT r) AS rels
RETURN nodes,
       [x IN rels WHERE x IS NOT NULL] AS relationships,
       elementId(center) AS center_id
