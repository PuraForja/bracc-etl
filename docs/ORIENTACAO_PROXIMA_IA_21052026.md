# ORIENTAÇÃO PARA PRÓXIMA IA — CONTINUAR SESSÃO
> Gerado em 21/05/2026 ~18h30
> Leia este documento antes de continuar o trabalho

---

## CONTEXTO RÁPIDO

Sistema de inteligência política do Amazonas. Grafo Neo4j com ~80M nodes.
Repositório: https://github.com/PuraForja/bracc-etl
Leia sempre: docs/CHANGELOG.md e o MASTER mais recente (v32).

---

## O QUE ESTAVA SENDO FEITO NESTA SESSÃO

### 1. Grafo do frontend — problema resolvido parcialmente

**Problema:** grafo não mostrava dados ao clicar em entidades.
**Causa raiz:** timeout 504 com profundidade 2 — query muito pesada.
**Solução aplicada:** 
- Fulltext index `entity_search` atualizado com GovEmployee, Election, etc.
- `graph_expand.cypher` atualizado com TEM_REMUNERACAO e POSSIVEL_MESMO_INDIVIDUO
- Timeout da API aumentado de 5s para 30s

**Estado atual com profundidade 1:** FUNCIONA — mostra 35 Pessoas, 2 Empresas, 1 Eleição para Diego Roberto Afonso.
**Estado atual com profundidade 2:** FALHA com 504 timeout.

**Próximo passo:** resolver o timeout com profundidade 2. Opções:
1. Aumentar timeout no nginx (já estava pendente)
2. Otimizar a query `graph_expand.cypher` com LIMIT
3. Mudar o default do frontend para profundidade 1

---

### 2. SOCIO_DE não aparece no grafo

Diego tem 4 empresas via Partner→SOCIO_DE mas o grafo mostra `SOCIO_DE=0`.
As 2 empresas que aparecem vieram via DOOU (doação de campanha), não via SOCIO_DE.

**Por quê:** o node center é Person, mas o SOCIO_DE está no node Partner.
São nodes separados — Person e Partner do mesmo Diego não estão linkados.

**Solução necessária:** 
- Criar relação SAME_AS entre Person e Partner quando CPF bater
- Ou adicionar SOCIO_DE direto no Person durante importação

**Verificar:**
```bash
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (p:Person {cpf: '784.440.632-15'})-[:SAME_AS|POSSIBLY_SAME_AS]-(partner:Partner) RETURN partner.name, partner.doc_digits"
```

---

### 3. POSSIVEL_MESMO_INDIVIDUO não aparece no frontend

A relação existe no banco (211k arestas) mas não aparece na lista de tipos de conexão do frontend.

**Verificar no frontend:**
```bash
grep -rn "POSSIVEL_MESMO\|TEM_REMUNERACAO" ~/Downloads/br-acc-novo/frontend/src/
```

Provavelmente precisa adicionar esses tipos no mapa de relações do frontend.

---

### 4. Nginx timeout — URGENTE

Com profundidade 2 a query explode. Nginx precisa de timeout maior.

```bash
find ~/Downloads/br-acc-novo -name "nginx.conf" -o -name "*.nginx" 2>/dev/null
grep -rn "proxy_read_timeout\|timeout" ~/Downloads/br-acc-novo/infra/ 2>/dev/null
```

---

## CASO EM VALIDAÇÃO — DIEGO ROBERTO AFONSO

CPF: 784.440.632-15
Servidor: SUHAB + SECT (dupla lotação AM)
4 empresas: DRA Derivados Petróleo, DH Lojas Conveniências, Gelabrea Gelo, ID Vestuário
Conflito confirmado: DRA forneceu R$67.386 para Adail Filho e Sidney Leite

**O grafo mostra:**
- 35 Person (doadores de campanha)
- 2 Company (via DOOU, não via SOCIO_DE)
- 1 Election
- SOCIO_DE = 0 (bug — empresas não linkadas ao Person)

---

## CASO AMOM MANDEL LINS FILHO

CPF: 072.847.254-60
4 nodes separados no banco — deduplicação pendente
Emendas: ~R$84M (deputado federal AM 2022)
Padrasto: Mário Coelho de Mello — conselheiro TCE-AM

---

## PNCP

Estava baixando dados de fevereiro/2026 — quase 100%.
Se morreu, relança:
```bash
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run python scripts/download_pncp.py --output-dir ../data/pncp 2>&1
```

---

## PENDENTES DESTA SESSÃO (não concluídos)

```
[ ] Nginx timeout — resolver 504 com profundidade 2
[ ] SOCIO_DE no grafo — linkar Person com Partner via CPF (SAME_AS)
[ ] POSSIVEL_MESMO_INDIVIDUO — adicionar no frontend
[ ] TEM_REMUNERACAO — adicionar no frontend
[ ] Deduplicação automática por CPF no orchestrator
[ ] Backup Neo4j — URGENTE (último: 09/05)
```

---

## COMANDOS ÚTEIS PARA CONTINUAR

```bash
# Estado do banco
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC" && echo "OK"

# Busca fulltext
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "CALL db.index.fulltext.queryNodes('entity_search', 'NOME') YIELD node, score RETURN labels(node)[0], node.name, node.cpf, score ORDER BY score DESC LIMIT 10" && echo "OK"

# Testar API grafo
curl -s "http://localhost:8000/api/v1/graph/ELEMENT_ID?depth=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print('nodes:', len(d.get('nodes',[])), 'edges:', len(d.get('edges',[])))" && echo "OK"

# Nginx config
find ~/Downloads/br-acc-novo -name "*.conf" | xargs grep -l "timeout" 2>/dev/null && echo "OK"
```
