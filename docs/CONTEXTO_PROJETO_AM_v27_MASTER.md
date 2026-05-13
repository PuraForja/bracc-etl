\# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS

\## Documento Master Consolidado v27

> Gerado em 12/05/2026 \~21h30

> Cole este arquivo ou use o PROMPT\_INICIALIZACAO\_IA.md no início de qualquer nova sessão.



\---



\## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO



1\. Leia o CHANGELOG antes de qualquer correção de código

2\. Leia o ORIENTACOES\_IA.md para regras de comportamento

3\. Após qualquer alteração de código: atualize o CHANGELOG e commite

4\. Ao final de cada sessão: gere novo MASTER e commite

5\. Sempre inclua data/hora nos logs

6\. Avise quando a sessão estiver no limite — OBRIGATÓRIO

7\. Nunca reescrever scripts com requests puro — sempre usar \_download\_utils.py

8\. Confirmar alterações antes de executar

9\. Abrir arquivos grandes no Notepad — heredoc trava no Git Bash do Windows

10\. Comandos longos na vertical travam o Git Bash — mandar em linha única

11\. ⚠️ NUNCA usar curl para sobrescrever loader.py do GitHub — o repo pode estar desatualizado. Usar heredoc ou cat direto.

12\. Git Bash não suporta \\r para sobrescrever linha em scripts — usar linha nova por evento.



\---



\## ⚠️ ORIENTAÇÃO OBRIGATÓRIA — LEIA ANTES DE TOCAR EM QUALQUER PIPELINE



\*\*REGRA: qualquer pipeline com 3+ chamadas ao loader por chunk DEVE usar sessão única.\*\*



```python

\# CORRETO

with loader.open\_session() as session:

&#x20;   loader.load\_nodes("Label", rows, key\_field="id", session=session)

&#x20;   loader.load\_relationships(..., session=session)

&#x20;   loader.run\_query\_with\_retry(query, rows, session=session)



\# ERRADO — abre conexão nova por chamada (\~4s overhead cada)

loader.load\_nodes("Label", rows, key\_field="id")

loader.load\_relationships(...)

```



\*\*Pipelines pendentes do fix (por impacto):\*\*

\[ ] senado\_cpis.py      15 chamadas

\[ ] cnpj.py             14 chamadas

\[ ] camara\_inquiries.py  9 chamadas

\[ ] mides.py             9 chamadas

\[ ] transferegov.py      9 chamadas

\[ ] transparencia.py     9 chamadas

\[ ] tse.py               9 chamadas

\[ ] senado.py            6 chamadas

\[ ] tcu.py               5 chamadas

\[ ] datajud.py           5 chamadas

\[ ] ibama.py             4 chamadas

\[ ] icij.py              4 chamadas

\[ ] tse\_filiados.py      4 chamadas

\[ ] bcb/ceaf/cepim/cpgf/datasus/siconfi/siop/pncp/sanctions — 3 chamadas



\---



\## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU



```bash

\# 1. Docker

docker ps | grep neo4j

cd \~/Downloads/br-acc-novo \&\& docker compose up -d

\# 2. Neo4j totais

docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)\[0] as tipo, count(n) as total ORDER BY total DESC"

\# 3. Log

tail -20 \~/Downloads/br-acc-novo/pipeline\_imports.log | grep -v "contratacoes\\|HTTP Request\\|WARNING Network"

\# 4. PNCP

tail -3 \~/Downloads/br-acc-novo/download\_pncp.log

ps aux | grep pncp | grep -v grep

\# 5. Transparência AM

tail -3 \~/Downloads/br-acc-novo/transparencia\_am.log

ps aux | grep transparencia\_am | grep -v grep

\# 6. Se PNCP morreu, relançar

cd \~/Downloads/br-acc-novo \&\& while true; do cd etl \&\& source \~/.local/bin/env \&\& uv run python scripts/download\_pncp.py --output-dir ../data/pncp \&\& cd ..; sleep 30; done >> download\_pncp.log 2>\&1 \&

\# 7. Se Transparência AM morreu, relançar

cd \~/Downloads/br-acc-novo/etl \&\& source \~/.local/bin/env \&\& while true; do uv run python scripts/download\_transparencia\_am.py --output-dir ../data/transparencia\_am; echo "\[TRANSPARENCIA\_AM] reiniciando em 60s..."; sleep 60; done >> \~/Downloads/br-acc-novo/transparencia\_am.log 2>\&1 \&

```



\---



\## PERFIL



| Campo | Valor |

|---|---|

| Nome | Alberto (Rolim) |

| Contexto | Oposição política no Amazonas |

| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |

| SO | Windows 11 / Git Bash |

| uv | \~/.local/bin/env |

| GitHub | https://github.com/PuraForja/bracc-etl |



\---



\## INFRAESTRUTURA



Subir: `cd \~/Downloads/br-acc-novo \&\& docker compose up -d`



| Sistema | Acesso | Credencial |

|---|---|---|

| Neo4j | localhost:7474 | neo4j / changeme |

| API | localhost:8000 | — |

| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |



\---



\## STATUS NEO4J (12/05/2026 \~21h30)



| Tipo | Qtd | Status |

|---|---|---|

| Company | 40.671.726 | OK |

| Partner | 17.774.658 | OK |

| Expense | 3.836.389 | OK |

| MunicipalFinance | 3.469.721 | OK |

| Person | 2.627.995 | OK |

| Health | 612.561 | OK |

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

| InternationalSanction | 9.707 | OK |

| OffshoreOfficer | 6.575 | OK |

| OffshoreEntity | 4.820 | OK |

| Expulsion | 4.074 | OK |

| BarredNGO | 3.572 | OK |

| CVMProceeding | 537 | OK |

| LeniencyAgreement | 115 | OK |

| Inquiry | 105 | OK |

| CPI | 105 | OK |

| InquiryRequirement | 102 | OK |

| InquirySession | 87 | OK |

| IngestionRun | 85 | OK |

| MunicipalGazetteAct | 10 | OK — parcial |

| SourceDocument | 3 | OK |

| User | 1 | OK |

| \*\*TOTAL\*\* | \*\*\~87M\*\* | OK |



\---



\## STATUS DOWNLOADS (12/05/2026)



| Fonte | Download | Importação |

|---|---|---|

| cnpj | OK | OK |

| tse | OK | OK |

| viagens | OK | OK |

| transparencia | OK | OK |

| opensanctions | OK | OK |

| siop | OK | OK |

| camara | OK | OK — 3.836M expenses |

| datasus | OK | OK |

| tesouro\_emendas | OK | OK |

| senado | OK | OK — 272.429 expenses confirmados |

| world\_bank | OK | OK |

| todos os outros | OK | OK |

| pncp | \~62% (abr/2024) | AGUARDAR |

| transparencia\_am | \~408 CSVs baixados | EM ANDAMENTO — bug rename Windows |

| bndes, ibama, inep, pgfn, tcu, comprasnet, transferegov | SEM SCRIPT | — |



\---



\## BUG PENDENTE — \_download\_utils.py



\*\*Problema:\*\* No Windows, `partial.rename(dest)` falha com `FileExistsError` se `dest` já existe.

\*\*Correção:\*\* Adicionar `dest.unlink()` antes do rename nas duas ocorrências.

\*\*Arquivo:\*\* `etl/scripts/\_download\_utils.py`

```python

\# SUBSTITUIR as duas ocorrências de:

partial.rename(dest)

\# POR:

if dest.exists():

&#x20;   dest.unlink()

partial.rename(dest)

```



\---



\## ORQUESTRADOR — FEATURES (12/05/2026)



```bash

\# Fila completa

bash \~/Downloads/br-acc-novo/orchestrator.sh



\# Força reimportação

bash \~/Downloads/br-acc-novo/orchestrator.sh --force camara



\# Modo teste — pula Neo4j sync, uv sync e PNCP

MODO\_TESTE=Y bash \~/Downloads/br-acc-novo/orchestrator.sh --force camara



\# Pipeline direto com log visível

cd \~/Downloads/br-acc-novo/etl \&\& source \~/.local/bin/env \&\& uv run bracc-etl run --source camara --neo4j-password changeme --data-dir \~/Downloads/br-acc-novo/data 2>\&1 | tee \~/Downloads/br-acc-novo/camara\_debug.log

```



\*\*Features do orchestrator:\*\*

\- Barra de progresso por arquivo

\- Watchdog — avisa se pipeline parar por 3min sem atividade

\- MODO\_TESTE=Y — pula leitura Neo4j, uv sync e PNCP

\- PNCP em background com reinício automático

\- Transparência AM em background com reinício automático (log: transparencia\_am.log)

\- Seção AMAZONAS separada na fila e no LABEL\_MAP



\---



\## FONTES AMAZONAS



| Fonte | Status | Observações |

|---|---|---|

| transparencia\_am | EM ANDAMENTO | 80 órgãos × 2014-2026 — bug rename Windows pendente |

| ibama | A IMPLEMENTAR | CRÍTICO AM — embargos ambientais |

| antaq | A IMPLEMENTAR | Hidrovias AM |

| inpe\_prodes | A IMPLEMENTAR | Desmatamento |

| sicar | A IMPLEMENTAR | Cadastro Ambiental Rural |

| portal\_transparencia\_am | ANALISADO | API via admin-ajax.php — servidores estaduais |



\---



\## PENDENTES TÉCNICOS

\[ ] \_download\_utils.py — fix rename Windows (FileExistsError)

\[ ] transparencia\_am — aguardar download completo e criar pipeline importação

\[ ] PNCP — aguardar 100% e importar

\[ ] Fix sessão única — aplicar nos pipelines pendentes (ver lista acima)

\[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov

\[ ] TCE-AM — descartado por ora (JSF sem API pública)

\[ ] Backup Neo4j — fazer após próxima sessão

\[ ] Bug frontend — grafo vazio para Person nodes

\[ ] SOCIO\_DE incompletos — 18.7M vs 26.8M

\[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP

\[ ] link\_persons.cypher — script ausente (warning no camara e senado)

\[ ] PENDENCIAS\_FEATURES.md — sources.yaml multi-estado + --check-links (ver arquivo)



\---



\## COMANDOS ÚTEIS



```bash

\# Neo4j totais

docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)\[0] as tipo, count(n) as total ORDER BY total DESC"



\# Backup

docker run --rm -v br-acc-novo\_neo4j-data:/data -v //c/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data



\# Verificar índices

docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "SHOW INDEXES YIELD name, labelsOrTypes, properties RETURN name, labelsOrTypes, properties"



\# Commitar

cd \~/Downloads/br-acc-novo \&\& git add docs/ etl/scripts/ etl/src/ orchestrator.sh \&\& git commit -m "sync $(date '+%Y-%m-%d %H:%M')" \&\& git push origin main

```



\---



\## HISTÓRICO



| Data | O que foi feito |

|---|---|

| 20-25/04 | Infraestrutura + CNPJ + patches |

| 26/04 | CNPJ completo + backup |

| 27-30/04 | Downloads massivos + CEPIM + BCB |

| 01-03/05 | run\_query\_with\_retry + batch\_size fixes |

| 04-05/05 | heap Neo4j 16GB + BCB API Olinda + siop+opensanctions |

| 06/05 | tse+transparencia+datasus importados |

| 07/05 | orchestrator v3 + tesouro\_emendas + MASTER v23 |

| 08/05 | world\_bank fix + CNPJ fix + camara refactor + fix sessão única loader.py (1800x) |

| 09/05 | camara importação completa 3.79M + backup 9.9GB + MASTER v25 |

| 10/05 | barra progresso orchestrator + MODO\_TESTE + watchdog + MASTER v26 |

| 12/05 | senado confirmado OK + TCE-AM analisado (descartado) + Portal Transparência AM mapeado (80 órgãos, API admin-ajax.php) + download\_transparencia\_am.py criado e testado + orchestrator seção Amazonas + transparencia\_am em background + PENDENCIAS\_FEATURES.md + MASTER v27 |



\---



\## CHECKLIST NOVA SESSÃO

\[ ] Ler CHANGELOG\_TECNICO.md

\[ ] docker ps | grep neo4j

\[ ] Verificar PNCP rodando

\[ ] Verificar transparencia\_am rodando

\[ ] Fix \_download\_utils.py rename Windows

\[ ] Aplicar fix sessão única nos pipelines pendentes

\[ ] Gerar v28 ao final



\---



v27 — 12/05/2026 \~21h30

SENADO: ✅ confirmado OK 272.429 expenses

TRANSPARÊNCIA AM: ⏳ download em andamento \~408 CSVs — bug rename Windows pendente

ORCHESTRATOR: seção Amazonas + transparencia\_am background

PRÓXIMO: fix \_download\_utils + pipeline importação transparencia\_am + PNCP 100%

