cat >> \~/Downloads/br-acc-novo/docs/PENDENCIAS\_FEATURES.md << 'EOF'

\## \[12/05/2026] — Features planejadas — NÃO IMPLEMENTADAS



\### FEATURE 1 — Orquestrador multi-estado (sources.yaml)

\*\*Ideia:\*\* Separar fontes por escopo em arquivo YAML externo.

\- `geral:` — fontes federais, valem para qualquer estado (cnpj, tse, pncp, etc.)

\- `estados:` — fontes específicas por estado (amazonas, para, piaui, rj, etc.)

\- Se estado não tem fontes mapeadas: exibir mensagem orientando como contribuir

\- Usuário marca quais estados quer no YAML antes de rodar o orchestrator

\- Vantagem: adicionar novo estado = editar só o YAML, sem mexer no shell

\- \*\*Motivação:\*\* empresa investigada age em todo o estado/país, não só no município



\*\*Estrutura prevista:\*\*

```yaml

geral:

&#x20; - cnpj

&#x20; - tse

&#x20; - transparencia

&#x20; - siop

&#x20; - pncp

&#x20; - opensanctions



estados:

&#x20; amazonas:

&#x20;   - transparencia\_am

&#x20;   - ibama

&#x20;   - antaq

&#x20;   - inpe\_prodes

&#x20;   - sicar

&#x20; para:

&#x20;   status: a\_implementar

&#x20;   orientacao: "adicionar fontes em estados.para\[] e abrir PR"

&#x20; piaui:

&#x20;   status: a\_implementar

&#x20;   orientacao: "adicionar fontes em estados.piaui\[] e abrir PR"

```



\---



\### FEATURE 2 — Modo --check-links no orquestrador

\*\*Ideia:\*\* Flag `--check-links` que testa todos os endpoints/URLs das fontes

sem baixar nada, listando quais estão fora do ar ou com erro.



\*\*Comportamento esperado:\*\*

bash orchestrator.sh --check-links
[OK]   cnpj         https://dadosabertos.rfb.gov.br/...
[OK]   tse          https://dadosabertos.tse.jus.br/...
[FAIL] pncp         https://pncp.gov.br/... → timeout
[FAIL] transparencia_am → 403 Forbidden
[OK]   opensanctions ...
---
### PENDENCIA Entity Resolution AM Clusters Desconectados
Registrado em: 17/05/2026
Prioridade: Alta

PROBLEMA:
Dois clusters desconectados no grafo:
- Cluster A CNPJ/CPF: Company Partner Contract Sanction Election GovTravel
- Cluster B nome: GovEmployee 10.269M servidores AM sem CPF no portal estadual

FONTES PESQUISADAS PARA CPF - TODAS FALHARAM:
- Portal Transparencia Federal: 403
- API CGU: requer Gov.br
- Brasil.io: requer autenticacao
- CAGED FTP: sem CPF individual
- CNES FTP: CPF criptografado por LGPD

CAMINHOS NAO EXPLORADOS:
1. DOE-AM via OCR - portarias tem CPF parcial maior ROI
2. Conselhos CRM COREN CREA OAB - nao investigados
3. TSE doadores x GovEmployee - dados no banco cruzamento pendente
4. CNES CNS como ponte parcial

CNES MAPEADO:
FTP: ftp://ftp.datasus.gov.br/cnes/
Arquivos: PROFISSIONAIS_BRASIL_AM_YYYYMM.ZIP e SCNES_ARQUIVOS_AM_YYYYMM.ZIP
Em claro: CNS + CBO + vinculo + municipio
CPF: criptografado por LGPD
Pendente: download_cnes_am.py + pipeline importacao

INVESTIGACOES POSSIVEIS COM CNS:
LARANJA: Servidor assina procedimentos em clinica X. Clinica contratada pela SES. Socio tem mesmo nome. Score alto. Laranja sem CPF.
FANTASMA: Servidor recebe salario mas CNS nunca aparece no SIA/SIH. Nao trabalha.
DUPLO VINCULO: CNS em dois estabelecimentos no mesmo horario. Portaria 134.
DIRECIONAMENTO: Medico assina AIHs para empresa X. Empresa contratada pela SES. Socio com mesmo nome.
NEPOTISMO: Mesmo sobrenome raro + mesma lotacao + admissao proxima. Cruza TSE.
SUPERFATURAMENTO: Procedimento caro assinado por CBO incompativel.

ARQUITETURA SUGERIDA IA4:
No intermediario (:Identity) com (:SourceRecord)-[:REPRESENTS {score}]->(:Identity)
score > 0.95: auto-link
0.80 a 0.95: revisao manual
menor 0.80: apenas sugestao

---

## [21/05/2026] — Expansão Adaptativa do Grafo (depth=2)
Registrado em: 21/05/2026
Prioridade: Alta

### CONTEXTO
Query original com *1..4 variável causava 504 timeout em depth=2.
Fix temporário aplicado: dois MATCH separados com slice fixo de 4 vizinhos por node.
Resultado atual: ~117 nodes, ~3.7s. Funciona mas perde conexões relevantes.

### SOLUÇÃO PLANEJADA — Busca Adaptativa na API
Implementar no graph.py + nova query node_degrees.cypher:

1. Depth=1 completo (já funciona)
2. Query em lote para medir grau de todos os nodes do depth=1 (uma só chamada)
3. Classificação por bucket na API Python:
   - grau <= 30: expande tudo
   - grau 31-100: limita a 15 vizinhos
   - grau 101-1000: limita a 5 vizinhos
   - grau > 1000: limita a 2 vizinhos
4. Orçamento global de 800 edges no depth=2
5. apoc.cypher.runTimeboxed(8000ms) como fallback de segurança
6. Metadados no retorno JSON:
   { "truncated_nodes": [{"id": "...", "total_degree": 312, "returned": 5}] }

### SOLUÇÃO PLANEJADA — Expansão Incremental no Frontend
Adicionar expansão por clique duplo em node (react-force-graph-2d já suporta):
- Clique simples: abre painel de detalhe (comportamento atual)
- Clique duplo: chama novo endpoint GET /api/v1/graph/expand/{node_id}
- Store graphExplorer: novo campo expandedNodeIds + ação expandNode
- GraphCanvas: merge dos novos nodes/edges no grafo existente sem recarregar tudo

### ARQUIVOS A MODIFICAR
- api/src/bracc/queries/graph_expand.cypher (query atual com fix temporário)
- api/src/bracc/queries/node_degrees.cypher (novo — ainda não existe)
- api/src/bracc/routers/graph.py (lógica adaptativa)
- api/src/bracc/models/graph.py (adicionar campo truncated_nodes no GraphResponse)
- frontend/src/stores/graphExplorer.ts (expandedNodeIds + expandNode)
- frontend/src/hooks/useGraphData.ts (novo hook useExpandNode)
- frontend/src/components/graph/GraphCanvas.tsx (onNodeDoubleClick)

### REFERÊNCIA
Consulta feita em 21/05/2026 com 4 IAs externas — consenso:
- Nunca usar *1..N variável em produção
- Busca adaptativa com degree em lote é a solução correta
- runTimeboxed como cinto de segurança, não solução principal
- Expansão incremental por clique é o modelo ideal para investigação (Maltego, Palantir)
