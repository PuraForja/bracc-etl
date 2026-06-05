# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v32
> Gerado em 21/05/2026 ~19h00

---

## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO

1. Leia o CHANGELOG antes de qualquer correção de código
2. Leia o ORIENTACOES_IA.md para regras de comportamento
3. Após qualquer alteração de código: atualize o CHANGELOG e commite
4. Ao final de cada sessão: gere novo MASTER e commite
5. Sempre inclua data/hora nos logs
6. Avise quando a sessão estiver no limite — OBRIGATÓRIO
7. Nunca reescrever scripts com requests puro — sempre usar _download_utils.py
8. Confirmar alterações antes de executar
9. Abrir arquivos grandes no Notepad — heredoc trava no Git Bash do Windows
10. Comandos longos na vertical travam o Git Bash — mandar em linha única
11. Todo comando deve terminar com && echo "OK" para confirmar execução
12. NUNCA usar curl para sobrescrever loader.py do GitHub

---

## ⚠️ ORIENTAÇÃO OBRIGATÓRIA — SESSÃO ÚNICA NO LOADER

```python
# CORRETO
with loader.open_session() as session:
    loader.load_nodes("Label", rows, key_field="id", session=session)
    loader.load_relationships(..., session=session)
```

**Pipelines pendentes do fix:**
senado_cpis, cnpj, camara_inquiries, mides, transferegov, transparencia, tse, senado, tcu, datajud, ibama, icij, tse_filiados

---

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU

```bash
docker ps | grep neo4j && echo "OK"
cd ~/Downloads/br-acc-novo && docker compose up -d && echo "OK"
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC" && echo "OK"
ps aux | grep pncp | grep -v grep && echo "OK"
tail -3 ~/Downloads/br-acc-novo/download_pncp.log && echo "OK"
```

---

## PERFIL

| Campo | Valor |
|---|---|
| Nome | Alberto (Rolim) |
| Contexto | Oposição política no Amazonas |
| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |
| SO | Windows 11 / Git Bash |
| GitHub | https://github.com/PuraForja/bracc-etl |

---

## INFRAESTRUTURA

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |

---

## STATUS NEO4J (21/05/2026)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.671.726 | OK |
| Partner | 17.774.658 | OK |
| GovEmployee | 10.269.641 | OK — transparencia_am completo |
| Expense | 3.836.389 | OK |
| MunicipalFinance | 3.469.721 | OK |
| Person | 2.780.851 | OK |
| Health | 612.561 | OK |
| TaxWaiver | 291.799 | OK |
| GovTravel | 260.000 | OK |
| GovCardExpense | 131.950 | OK |
| GlobalPEP | 117.910 | OK |
| Amendment | 101.801 | OK |
| Contract | 64.121 | OK |
| Fund | 41.107 | OK |
| Payment | 40.000 | OK |
| Election | 33.602 | OK — TSE 2002-2024 completo |
| Sanction | 24.077 | OK |
| InternationalSanction | 9.707 | OK |
| **TOTAL** | **~80M** | OK |

---

## FIXES APLICADOS NESTA SESSÃO (21/05/2026)

### Fulltext Index entity_search — atualizado
Labels adicionados: GovEmployee, Election, Sanction, GlobalPEP, InternationalSanction, Expense, GovTravel, GovCardExpense, TaxWaiver, Fund
Campos adicionados: nm_candidato, emp_id, orgao
Motivo: frontend não encontrava servidores AM nem eleições na busca

### graph_expand.cypher — atualizado
Labels adicionados no center: GovEmployee, Partner, InternationalSanction, TaxWaiver, GovTravel, GovCardExpense
Relações adicionadas: TEM_REMUNERACAO, POSSIVEL_MESMO_INDIVIDUO
Motivo: grafo não expandia servidores AM nem entity resolution

### TSE — reimportado com todos os anos
Anos: 2002-2024 (antes só 2016 e 2024)
Bug corrigido: download_tse.py default years=[2024] → todos os anos

---

## ENTITY RESOLUTION AM (19/05/2026)

- 211.883 arestas POSSIVEL_MESMO_INDIVIDUO criadas
- 2.417 pessoas únicas conectadas
- 77 órgãos cobertos
- 58 casos de conflito de interesse identificados
- 93 empresas com contratos públicos

---

## CASO VALIDADO — DIEGO ROBERTO AFONSO

CPF: 784.440.632-15
Servidor: SUHAB + SECT (dupla lotação)
Empresas (4):
- D.R.A. Derivados de Petróleo (10.773.536/0001-01) — combustíveis
- DH Lojas de Conveniências (26.267.883/0001-94)
- Gelabrea Fábrica de Gelo (21.602.531/0001-24)
- ID Comércio Vestuário (11.318.770/0001-01)

Conflito de interesse confirmado:
- DRA forneceu R$ 67.386 em 8 transações para gabinetes federais AM
- Adail Filho (MDB/AM): R$ 62.736 em 6 transações
- Sidney Leite (PSD/AM): R$ 4.600 em 1 transação

---

## CASO AMOM MANDEL LINS FILHO

CPF: 072.847.254-60
Problema: 4 nodes separados no banco (deduplicação pendente)
- Person AMOM MANDEL LINS FILHO — 45 doadores + eleição 2024
- Person AMOM MANDEL — 23 emendas (~R$84M) + eleição 2022 + doações Amazonino
- Partner AMOM MANDEL LINS FILHO — sócio A.M LINS FILHO E-COMM (35.715.111/0001-69)
- GlobalPEP AMOM MANDEL LINS FILHO

Família: avô Domingos Jorge Chalub (desembargador), padrasto Mário Coelho de Mello (TCE-AM)

---

## PENDENTES TÉCNICOS

```
[ ] Deduplicação automática por CPF — orchestrator deve fundir nodes com mesmo CPF
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M esperados
[ ] PNCP — aguardar 100% e importar
[ ] Fix sessão única — pipelines pendentes
[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] Backup Neo4j — URGENTE (último: 09/05)
[ ] Bug frontend — grafo vazio para Person nodes (parcialmente resolvido)
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
[ ] Relatório exportável casos conflito de interesse
[ ] CNES download_cnes_am.py + pipeline
[ ] DOE-AM via OCR portarias CPF parcial
```

---

## SETUP OBRIGATÓRIO — NOVA INSTALAÇÃO

Ver docs/SETUP_INDICES.md — índices de performance + fulltext

```bash
# Fulltext index (obrigatório para busca no frontend)
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "CREATE FULLTEXT INDEX entity_search FOR (n:Person|Partner|Company|Health|Contract|Amendment|GovEmployee|Election|Sanction|GlobalPEP|InternationalSanction|Expense|GovTravel|GovCardExpense|TaxWaiver|Fund|Inquiry|InquiryRequirement|MunicipalGazetteAct) ON EACH [n.name, n.razao_social, n.cpf, n.cnpj, n.doc_partial, n.doc_raw, n.object, n.nm_candidato, n.emp_id, n.orgao]"
```

---

## ORQUESTRADOR

```bash
bash ~/Downloads/br-acc-novo/orchestrator.sh
bash ~/Downloads/br-acc-novo/orchestrator.sh --amazonas
MODO_TESTE=Y bash ~/Downloads/br-acc-novo/orchestrator.sh --force tse
```

---

## PNCP — RELANÇAR SE MORREU

```bash
cd ~/Downloads/br-acc-novo && while true; do cd etl && source ~/.local/bin/env && uv run python scripts/download_pncp.py --output-dir ../data/pncp && cd ..; sleep 30; done >> download_pncp.log 2>&1 & echo "OK"
```

---

## COMANDOS ÚTEIS

```bash
# Busca fulltext
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "CALL db.index.fulltext.queryNodes('entity_search', 'NOME') YIELD node, score RETURN labels(node)[0], node.name, node.cpf, score ORDER BY score DESC LIMIT 10"

# Backup
MSYS_NO_PATHCONV=1 docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo "OK"

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"
```

---

## HISTÓRICO

| Data | O que foi feito |
|---|---|
| 08-09/05 | camara 3.836M expenses + loader sessão única 1800x |
| 12-13/05 | transparencia_am download 6857 CSVs + catálogo v5 |
| 15-17/05 | transparencia_am 10.269M GovEmployee + entity resolution |
| 17-19/05 | POSSIVEL_MESMO_INDIVIDUO 211k arestas + 58 conflitos + Diego Afonso |
| 21/05 | TSE completo 2002-2024 + fulltext index + graph_expand + Amom/Diego validados |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG.md
[ ] docker ps | grep neo4j
[ ] Verificar PNCP rodando
[ ] Neo4j totais
[ ] Fazer backup Neo4j (URGENTE)
[ ] Gerar v33 ao final
```

---

v32 — 21/05/2026 ~19h00
TSE: completo 2002-2024
Fulltext index: atualizado com GovEmployee e novos labels
graph_expand: atualizado com TEM_REMUNERACAO e POSSIVEL_MESMO_INDIVIDUO
PRÓXIMO: backup + deduplicação CPF + SOCIO_DE completo
