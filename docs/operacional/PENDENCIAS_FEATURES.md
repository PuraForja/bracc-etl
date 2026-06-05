# PENDÊNCIAS E FEATURES — BRACC
> Atualizado em 03/06/2026
> Padrão de registro obrigatório para IAs — ver seção COMO REGISTRAR ao final

---

## BUGS ABERTOS

### [BUG] Frontend — grafo trava após primeiro drag/zoom
- **Data:** 02/06/2026
- **Prioridade:** Média
- **Sintoma:** react-force-graph-2d perde controle após primeiro drag/zoom — segundo comando não responde
- **Provável causa:** re-renderização do grafo dessincroniza estado interno
- **Arquivo:** `frontend/src/components/graph/GraphCanvas.tsx`
- **Status:** ABERTO

---

## FEATURES ABERTAS

### [FEATURE] Expansão adaptativa depth=2
- **Data:** 21/05/2026
- **Prioridade:** Alta
- **Descrição:** Query com `*1..4` variável causa 504 timeout em depth=2. Fix temporário aplicado (dois MATCH separados, slice fixo de 4 vizinhos). Perde conexões relevantes.
- **Solução planejada:**
  1. Query em lote para medir grau de todos os nodes do depth=1
  2. Classificação por bucket: grau ≤30 expande tudo | 31-100 limita 15 | 101-1000 limita 5 | >1000 limita 2
  3. Orçamento global de 800 edges no depth=2
  4. `apoc.cypher.runTimeboxed(8000ms)` como fallback
  5. Retorno JSON com campo `truncated_nodes`
- **Expansão incremental por clique duplo** — modelo Maltego/Palantir
  - Clique duplo → `GET /api/v1/graph/expand/{node_id}`
  - Merge dos novos nodes/edges sem recarregar grafo
- **Arquivos a modificar:**
  - `api/src/bracc/queries/graph_expand.cypher`
  - `api/src/bracc/queries/node_degrees.cypher` (novo)
  - `api/src/bracc/routers/graph.py`
  - `api/src/bracc/models/graph.py`
  - `frontend/src/stores/graphExplorer.ts`
  - `frontend/src/hooks/useGraphData.ts`
  - `frontend/src/components/graph/GraphCanvas.tsx`
- **Referência:** consulta 4 IAs em 21/05/2026 — consenso: busca adaptativa com degree em lote é a solução correta
- **Status:** ABERTO

### [FEATURE] Orquestrador multi-estado (sources.yaml)
- **Data:** 12/05/2026
- **Prioridade:** Média
- **Descrição:** Separar fontes por escopo em YAML externo. Federais vs estaduais. Adicionar novo estado = editar só o YAML.
- **Estrutura prevista:**
```yaml
geral:
  - cnpj
  - tse
  - pncp
estados:
  amazonas:
    - transparencia_am
    - inpe_prodes
    - sicar
  para:
    status: a_implementar
```
- **Status:** ABERTO — substituído parcialmente pelo BRACC Installer (ver docs/operacional/BRACC_INSTALLER_ESCOPO.md)

### [FEATURE] --check-links no orchestrator
- **Data:** 12/05/2026
- **Prioridade:** Média
- **Descrição:** Flag que testa todos os endpoints sem baixar nada. Lista quais estão fora do ar.
- **Status:** ABERTO — incorporado no escopo do BRACC Installer

---

## PENDÊNCIAS TÉCNICAS

### [PENDENCIA] Entity Resolution — GovEmployee AM sem CPF
- **Data:** 17/05/2026
- **Prioridade:** Alta
- **Descrição:** 10.269M servidores AM identificados só por nome — sem CPF no portal estadual. Cluster desconectado do restante do grafo.
- **Fontes testadas (falharam):**
  - Portal Transparência Federal: 403
  - API CGU: requer Gov.br
  - Brasil.io: requer autenticação
  - CAGED FTP: sem CPF individual
  - CNES FTP: CPF criptografado por LGPD
- **Caminhos não explorados:**
  1. DOE-AM via OCR — portarias têm CPF parcial — maior ROI
  2. Conselhos CRM/COREN/CREA/OAB — não investigados
  3. Cruzamento TSE doadores × GovEmployee — dados no banco
  4. CNES CNS como ponte parcial (CNS em claro, CPF criptografado)
- **CNES FTP mapeado:**
  - `ftp://ftp.datasus.gov.br/cnes/PROFISSIONAIS_BRASIL_AM_YYYYMM.ZIP`
  - Em claro: CNS + CBO + vínculo + município
  - Pendente: `download_cnes_am.py` + pipeline
- **Investigações possíveis com CNS:**
  - LARANJA: servidor assina procedimentos em clínica contratada pela SES
  - FANTASMA: servidor recebe salário mas CNS nunca aparece no SIA/SIH
  - DUPLO VÍNCULO: CNS em dois estabelecimentos no mesmo horário
  - NEPOTISMO: mesmo sobrenome raro + mesma lotação + admissão próxima
- **Status:** PARCIALMENTE RESOLVIDO — WCC resolve Person/Partner. GovEmployee continua pendente.

### [PENDENCIA] Amom Mandel Lins Filho — 4 nodes separados
- **Data:** maio/2026
- **Prioridade:** Média
- **CPF:** 072.847.254-60
- **Descrição:** 4 nodes Person separados para o mesmo indivíduo. Deduplicação pendente.
- **Emendas:** ~R$84M
- **Status:** ABERTO

### [PENDENCIA] Backup Neo4j
- **Data:** 03/06/2026
- **Prioridade:** URGENTE
- **Último backup:** 31/05/2026 — 13GB
- **Comando:**
```bash
docker run --rm -v bracc_neo4j-data:/data -v /home/rolim:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo "OK"
```
- **Status:** ABERTO

---

## RESOLVIDOS

### [RESOLVIDO] WCC community_id — depth=1 não alcançava empresas
- **Data resolução:** 01/06/2026
- **Problema:** `Person→SAME_AS→Partner→SOCIO_DE→Company` = 3 saltos, depth=2 não alcançava
- **Solução:** GDS WCC escreve `community_id` em 21M nodes. Query usa índice direto.

### [RESOLVIDO] TSE pipeline travava com 3.1M linhas de doações
- **Data resolução:** 02/06/2026
- **Solução:** Reescrito para chunked 50k linhas

### [RESOLVIDO] Neo4j heap limitado a 1GB ignorando docker-compose.yml
- **Data resolução:** 01/06/2026
- **Causa:** `.env` tinha `NEO4J_HEAP_MAX=1G` sobrescrevendo
- **Solução:** Corrigido para `NEO4J_HEAP_MAX=8G`

---

## COMO REGISTRAR — PADRÃO OBRIGATÓRIO PARA IAs

### Novo BUG:
[BUG] Nome curto do bug

Data: DD/MM/AAAA
Prioridade: Alta/Média/Baixa
Sintoma: o que o usuário vê
Provável causa: hipótese técnica
Arquivo: caminho do arquivo relevante
Status: ABERTO


### Nova FEATURE:
[FEATURE] Nome da feature

Data: DD/MM/AAAA
Prioridade: Alta/Média/Baixa
Descrição: uma linha
Detalhes: (opcional)
Status: ABERTO


### Nova PENDENCIA:
[PENDENCIA] Nome

Data: DD/MM/AAAA
Prioridade: Alta/Média/Baixa/URGENTE
Descrição: uma linha
Detalhes: (opcional)
Status: ABERTO


### Ao resolver:
1. Mover item para seção RESOLVIDOS
2. Adicionar `- **Data resolução:** DD/MM/AAAA`
3. Adicionar `- **Solução:** descrição curta`
4. Remover detalhes extensos (manter só resumo)

### Regras:
- NUNCA editar itens RESOLVIDOS
- NUNCA misturar BUG com FEATURE com PENDENCIA
- SEMPRE usar o padrão acima — não inventar formato novo
- Caminhos SEMPRE relativos a `~/bracc/` — nunca `~/Downloads/br-acc-novo/`
