# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v28
> Gerado em 16/05/2026 ~19h30
> Cole este arquivo ou use o PROMPT_INICIALIZACAO_IA.md no início de qualquer nova sessão.

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
12. Se não aparecer OK, houve erro

---

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU

```bash
docker ps | grep neo4j
cd ~/Downloads/br-acc-novo && docker compose up -d
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"
tail -10 ~/Downloads/br-acc-novo/pipeline_imports.log | grep -v "contratacoes\|HTTP\|WARNING"
ps aux | grep pncp | grep -v grep
ps aux | grep bracc-etl | grep -v grep
```

---

## PERFIL

| Campo | Valor |
|---|---|
| Nome | Alberto (Rolim) |
| Contexto | Oposição política no Amazonas |
| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |
| SO | Windows 11 / Git Bash |
| uv | ~/.local/bin/env |
| GitHub | https://github.com/PuraForja/bracc-etl |

---

## INFRAESTRUTURA

Subir: `cd ~/Downloads/br-acc-novo && docker compose up -d`

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |

---

## STATUS NEO4J (16/05/2026 ~19h30)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.671.726 | OK |
| Partner | 17.774.658 | OK |
| Expense | 3.836.389 | OK |
| MunicipalFinance | 3.469.721 | OK |
| Person | 2.628.401 | OK |
| Health | 612.561 | OK |
| TaxWaiver | 291.799 | OK |
| GovTravel | 260.000 | OK |
| GovCardExpense | 131.950 | OK |
| GlobalPEP | 117.910 | OK |
| GovEmployee | 112.590 | PARCIAL — transparencia_am incompleto |
| Amendment | 101.801 | OK |
| Contract | 64.121 | OK |
| Fund | 41.107 | OK |
| Payment | 40.000 | OK |
| Election | 33.602 | OK |
| Sanction | 24.077 | OK |
| InternationalSanction | 9.707 | OK |
| OffshoreOfficer | 6.575 | OK |
| OffshoreEntity | 4.820 | OK |
| Expulsion | 4.074 | OK |
| BarredNGO | 3.572 | OK |
| CVMProceeding | 537 | OK |
| LeniencyAgreement | 115 | OK |
| Inquiry | 105 | OK |
| CPI | 105 | OK |
| **TOTAL** | **~87M** | OK |

---

## PROBLEMA CRÍTICO — transparencia_am morre silenciosamente

### Sintoma
Processo morre após `Processando 1/6857 158_201705.csv` sem erro.

### Fixes já aplicados (commit 8c595bc)
- ✅ `transparencia_am.py` reescrito com streaming (um CSV por vez)
- ✅ `loader.py` — `tx.run().consume()` para evitar cursor leak
- ✅ Sessão por CSV em vez de sessão global
- ✅ Índice `gov_employee_id` criado em `GovEmployee.emp_id`

### Ainda não resolvido
O processo ainda morre silenciosamente no primeiro CSV.

### Próximos passos recomendados
1. **faulthandler** — adicionar no início do pipeline para ver stack trace:
```python
import faulthandler
faulthandler.enable()
```
2. **SHOW TRANSACTIONS** — quando travar, em outra janela:
```bash
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "SHOW TRANSACTIONS"
```
3. **Heartbeat** — adicionar log a cada 10s dentro do `_process_csv`
4. **Tempo por CSV** — logar quanto tempo cada CSV levou
5. **PYTHONUNBUFFERED=1** — já sendo usado mas confirmar no orquestrador

### Suspeita atual
Cursor leak ou pool de conexões esgotado mesmo com sessão por CSV.
O `consume()` foi adicionado mas pode não ser suficiente se o `execute_write` já faz consume internamente.

---

## STATUS DOWNLOADS (16/05/2026)

| Fonte | Download | Importação |
|---|---|---|
| todos nacionais | OK | OK |
| transparencia_am | 6857 CSVs | PARCIAL 112.590/~500k |
| pncp | ~62% | AGUARDAR |
| bndes, ibama, inep, pgfn, tcu, comprasnet, transferegov | SEM SCRIPT | — |

---

## ORQUESTRADOR

```bash
bash ~/Downloads/br-acc-novo/orchestrator.sh              # fila completa
bash ~/Downloads/br-acc-novo/orchestrator.sh --amazonas   # só Amazonas
bash ~/Downloads/br-acc-novo/orchestrator.sh --force transparencia_am
MODO_TESTE=Y bash ~/Downloads/br-acc-novo/orchestrator.sh --amazonas
```

---

## PNCP — RELANÇAR SE MORREU

```bash
cd ~/Downloads/br-acc-novo && while true; do cd etl && source ~/.local/bin/env && uv run python scripts/download_pncp.py --output-dir ../data/pncp && cd ..; sleep 30; done >> download_pncp.log 2>&1 &
```

---

## COMANDOS ÚTEIS

```bash
# Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Transações presas (quando pipeline travar)
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "SHOW TRANSACTIONS"

# Monitor GovEmployee
while true; do docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n:GovEmployee) RETURN count(n) as total"; sleep 15; done

# Backup
docker run --rm -v br-acc-novo_neo4j-data:/data -v //c/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main
```

---

## PENDENTES TÉCNICOS

```
[ ] transparencia_am — resolver travamento silencioso (ver seção acima)
[ ] PNCP — aguardar 100% e importar
[ ] Fix sessão única — aplicar nos pipelines pendentes (senado_cpis, cnpj, etc.)
[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] Backup Neo4j
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
[ ] link_persons.cypher — script ausente
```

---

## HISTÓRICO

| Data | O que foi feito |
|---|---|
| 20-25/04 | Infraestrutura + CNPJ + patches |
| 26/04 | CNPJ completo + backup |
| 27-30/04 | Downloads massivos + CEPIM + BCB |
| 01-03/05 | run_query_with_retry + batch_size fixes |
| 04-05/05 | heap Neo4j 16GB + BCB API Olinda + siop+opensanctions |
| 06/05 | tse+transparencia+datasus importados |
| 07-08/05 | orchestrator + camara fix índice + loader execute_write |
| 09/05 | camara 3.836M expenses + backup 9.9GB |
| 10/05 | barra progresso + watchdog + MODO_TESTE |
| 12/05 | senado OK + transparencia_am download 4934 CSVs |
| 13/05 | catálogo v5 + changelog unificado + fix sessão única loader 1800x |
| 14/05 | orquestrador fila Amazonas separada + --amazonas flag |
| 15/05 | transparencia_am.py reescrito streaming + loader consume + sessão por CSV |
| 16/05 | fix _download_utils rename Windows + transparencia_am 6857 CSVs + índice GovEmployee |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG.md
[ ] docker ps | grep neo4j
[ ] Verificar PNCP rodando
[ ] Verificar Neo4j totais
[ ] Continuar debug transparencia_am (faulthandler + SHOW TRANSACTIONS)
[ ] Gerar v29 ao final
```

---

v28 — 16/05/2026 ~19h30
transparencia_am: 6857 CSVs, 112.590 GovEmployee (parcial) — morre silenciosamente
PRÓXIMO: faulthandler + SHOW TRANSACTIONS + heartbeat para diagnosticar
