# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v24
> Gerado em 08/05/2026 ~21h30
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
8. Confirme alterações antes de executar
9. Abrir arquivos grandes no Notepad — heredoc trava no Git Bash do Windows
10. Comandos longos na vertical travam o Git Bash — mandar em linha única

---

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU

```bash
# 1. Docker
docker ps | grep neo4j
cd ~/Downloads/br-acc-novo && docker compose up -d
# 2. Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"
# 3. Log
tail -20 ~/Downloads/br-acc-novo/pipeline_imports.log | grep -v "contratacoes\|HTTP Request\|WARNING Network"
# 4. PNCP
tail -3 ~/Downloads/br-acc-novo/download_pncp.log
ps aux | grep pncp | grep -v grep
# 5. Se PNCP morreu, relançar
cd ~/Downloads/br-acc-novo && while true; do cd etl && source ~/.local/bin/env && uv run python scripts/download_pncp.py --output-dir ../data/pncp && cd ..; sleep 30; done >> download_pncp.log 2>&1 &
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

## STATUS NEO4J (08/05/2026 ~21h00)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.636.929 | OK |
| Partner | 17.774.658 | OK |
| MunicipalFinance | 3.469.721 | OK |
| Person | 2.625.042 | OK |
| Health | 612.561 | OK |
| Expense | 494.537 | OK — parcial, camara pendente |
| TaxWaiver | 291.799 | OK |
| GovTravel | 260.000 | OK |
| GovCardExpense | 131.950 | OK |
| GlobalPEP | 117.910 | OK |
| Amendment | 101.801 | OK |
| Contract | 64.121 | OK |
| Fund | 41.107 | OK |
| Payment | 40.000 | OK |
| Election | 33.602 | OK |
| Sanction | 24.077 | OK |
| InternationalSanction | 8.435 | OK |
| **TOTAL** | **~87M** | OK |

---

## PROBLEMA CÂMARA — INVESTIGAÇÃO EM ANDAMENTO (08/05/2026)

### Sintoma
Processo morre silenciosamente após logar `chunk 1 — 5000 linhas`. Nenhum erro, nenhum traceback.

### O que foi descartado
- ❌ Problema no pandas — testado isolado com 5000 linhas: OK
- ❌ Problema no Neo4j — testado MERGE 5000 nodes isolado: OK
- ❌ Problema de RAM — 13.6GB livre
- ❌ Problema de iterrows — já corrigido para vetorização
- ❌ Problema de TextFileReader — já corrigido pelo colega

### O que foi corrigido nesta sessão
- ✅ `loader.py` — `session.run()` → `session.execute_write()` com retry (commit `385a051`)
- ✅ `runner.py` — chunk_size default 50_000 → 5_000 (commit `385a051`)
- ✅ `camara.py` — pipeline com chunksize correto pelo colega

### Próximo passo OBRIGATÓRIO
Rodar o script de diagnóstico que já está no repositório:

```bash
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run python scripts/test_camara.py
```

Este script tem logs em CADA etapa da transformação e do load:
- T1 strings básicas
- T2 parse data
- T3 parse valor
- T4 limpar documentos
- T5 formatar CNPJ/CPF
- T6 expense_id hash
- T7 to_dict expenses
- T8 to_dict deputies/suppliers
- T9 transform concluído
- L1 load Expense
- L2 Expense OK

**O log vai mostrar exatamente onde o processo para.**

### Hipótese atual
O processo morre na combinação pandas + Neo4j no mesmo processo. Possível causa: o driver Neo4j abre uma conexão que conflita com threads do pandas, ou há um deadlock silencioso na primeira transação.

---

## STATUS DOWNLOADS (08/05/2026)

| Fonte | Download | Importação |
|---|---|---|
| cnpj | OK | OK |
| tse | OK | OK |
| viagens | OK | OK |
| transparencia | OK | OK |
| opensanctions | OK | OK |
| siop | OK | OK |
| camara | OK | PENDENTE — ver problema acima |
| datasus | OK | OK |
| tesouro_emendas | OK | OK |
| pncp | ~60%+ | AGUARDAR |
| senado | OK | PROBLEMA — investigar |
| world_bank | OK | OK — 1272 nodes |
| todos os outros | OK | OK |
| bndes, ibama, inep, pgfn, tcu, comprasnet, transferegov | SEM SCRIPT | — |

---

## ORQUESTRADOR

```bash
# Fila completa
bash ~/Downloads/br-acc-novo/orchestrator.sh

# Força reimportação
bash ~/Downloads/br-acc-novo/orchestrator.sh --force camara

# Força senado
bash ~/Downloads/br-acc-novo/orchestrator.sh --force senado
```

Cache de importações em `.installed`. LABEL_MAP definido no `orchestrator.sh`.

---

## PENDENTES TÉCNICOS

```
[ ] camara — rodar test_camara.py e identificar etapa exata do crash
[ ] senado — investigar erro na importação
[ ] PNCP — aguardar 100% e importar
[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] TCE-AM — criar pipeline do zero
[ ] Backup Neo4j — URGENTE
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
```

---

## COMANDOS ÚTEIS

```bash
# Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main
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
| 07/05 | orchestrator v3 + tesouro_emendas + MASTER v23 |
| 08/05 | world_bank fix + CNPJ fix + camara refactor colega + loader execute_write + runner chunk_size 5k + test_camara.py |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG_TECNICO.md
[ ] docker ps | grep neo4j
[ ] Verificar PNCP rodando
[ ] Rodar test_camara.py — ver onde para
[ ] Se camara OK: rodar importação completa
[ ] Investigar senado
[ ] Gerar v25 ao final
```

---

v24 — 08/05/2026 ~21h30
PROBLEMA CÂMARA: processo morre após chunk 1, etapa exata desconhecida
PRÓXIMO: rodar test_camara.py para isolar o problema
