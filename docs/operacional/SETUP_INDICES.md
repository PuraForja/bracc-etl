# Setup Obrigatório — Índices Neo4j

Execute ANTES de qualquer importação em base nova.
O orchestrator cria estes índices automaticamente na primeira execução via setup_neo4j_indexes().

## Índices de Performance (obrigatórios)

```bash
docker compose exec neo4j cypher-shell -u neo4j -p changeme "
CREATE INDEX expense_id IF NOT EXISTS FOR (n:Expense) ON (n.expense_id);
CREATE INDEX person_cpf IF NOT EXISTS FOR (n:Person) ON (n.cpf);
CREATE INDEX person_person_id IF NOT EXISTS FOR (n:Person) ON (n.person_id);
CREATE INDEX company_cnpj IF NOT EXISTS FOR (n:Company) ON (n.cnpj);
CREATE INDEX health_cnes IF NOT EXISTS FOR (n:Health) ON (n.cnes_code);
CREATE INDEX finance_id IF NOT EXISTS FOR (n:MunicipalFinance) ON (n.finance_id);
CREATE INDEX gov_employee_id IF NOT EXISTS FOR (n:GovEmployee) ON (n.emp_id);
CREATE INDEX bid_id IF NOT EXISTS FOR (n:Bid) ON (n.bid_id)
"
```

## Por que cada índice existe

| Índice | Motivo |
|---|---|
| expense_id | MERGE camara.py — sem índice: full scan em 87M nodes (4min/chunk) |
| person_cpf | MERGE Person por CPF — base principal de deduplicação |
| person_person_id | MERGE transparencia_am — sem índice: full scan em 2.6M nodes (trava) |
| company_cnpj | MERGE Company — 40M nodes |
| health_cnes | MERGE Health — 612k nodes |
| finance_id | MERGE MunicipalFinance — sem índice: 42min para 10k registros |
| gov_employee_id | MERGE GovEmployee — transparencia_am |
| bid_id | MERGE Bid — pncp — sem índice: full scan travou importação com 2M registros |

## Verificar índices existentes

```bash
docker compose exec neo4j cypher-shell -u neo4j -p changeme "SHOW INDEXES YIELD name, labelsOrTypes, properties RETURN name, labelsOrTypes, properties ORDER BY labelsOrTypes"
```

## Histórico

- 02/05/2026: finance_id — siconfi travava 42min/10k
- 08/05/2026: expense_id, person_cpf, company_cnpj, health_cnes — camara travava
- 16/05/2026: gov_employee_id — transparencia_am
- 17/05/2026: person_person_id — transparencia_am travava no MERGE Person
- 31/05/2026: bid_id — pncp travava com 2M registros sem índice

## Índices WCC — community_id
Criados após rodar `gds.wcc.write` para resolver identidade entre Person/Partner/GlobalPEP.
```bash
docker compose exec neo4j cypher-shell -u neo4j -p changeme "
CREATE INDEX community_id_person IF NOT EXISTS FOR (n:Person) ON (n.community_id);
CREATE INDEX community_id_partner IF NOT EXISTS FOR (n:Partner) ON (n.community_id);
CREATE INDEX community_id_globalpep IF NOT EXISTS FOR (n:GlobalPEP) ON (n.community_id)
"
```
| Índice | Motivo |
|---|---|
| community_id_person | WCC — expansão de grafo via cluster de identidade |
| community_id_partner | WCC — expansão de grafo via cluster de identidade |
| community_id_globalpep | WCC — expansão de grafo via cluster de identidade |

- 01/06/2026: community_id — WCC GDS resolve Person↔Partner em depth=1
- 02/06/2026: titulo_eleitor_person — SAME_AS TSE via titulo de eleitor
- 03/06/2026: declared_asset_id — tse_bens MERGE DeclaredAsset
CREATE INDEX obra_id_unique IF NOT EXISTS FOR (n:Obra) ON (n.obra_id);
