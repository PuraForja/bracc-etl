\# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS

\## Documento Master Consolidado v20

> Gerado em 04/05/2026 \~01h30

> Cole este arquivo ou use o PROMPT\_INICIALIZACAO\_IA.md no início de qualquer nova sessão.



\---



\## 🤖 INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO



1\. \*\*Leia o CHANGELOG antes de qualquer correção de código\*\*

2\. \*\*Leia o ORIENTACOES\_IA.md para regras de comportamento\*\*

3\. Após qualquer alteração de código → atualize o CHANGELOG → commite

4\. Ao final de cada sessão → gere novo MASTER .md e commite

5\. \*\*Sempre inclua data/hora nos logs\*\*

6\. \*\*⚠️ Avise quando a sessão estiver no limite — OBRIGATÓRIO\*\*

7\. \*\*Nunca reescrever scripts com requests puro — sempre usar \_download\_utils.py\*\*

8\. \*\*Confirme alterações antes de executar\*\*

9\. \*\*Abrir arquivos grandes no Notepad — heredoc trava no Git Bash do Windows\*\*



\---



\## 👤 Perfil



| Campo | Valor |

|---|---|

| Nome | Alberto (Rolim) |

| Contexto | Oposição política no Amazonas |

| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |

| SO | Windows 11 / Git Bash |

| uv | `\~/.local/bin/env` |

| GitHub | https://github.com/PuraForja/bracc-etl |



\---



\## 🛠️ Infraestrutura



```bash

cd \~/Downloads/br-acc-novo \&\& docker compose up -d

```



| Sistema | Acesso | Credencial |

|---|---|---|

| Neo4j | localhost:7474 | neo4j / changeme |

| API | localhost:8000 | — |

| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |



\---



\## ✅ STATUS NEO4J (04/05/2026 \~01h30)



| Tipo | Qtd | Status |

|---|---|---|

| Company | 40.483.645+ | ✅ |

| Partner | 17.774.658 | ✅ |

| Person | 1.559.007+ | ✅ |

| Expense | 430.000 | ⚠️ só viagens — câmara importando agora |

| TaxWaiver | 291.799 | ✅ |

| GovTravel | 260.000 | ✅ |

| GovCardExpense | 131.950 | ✅ |

| Fund | 41.107 | ✅ |

| Contract | 32.259 | ✅ |

| Amendment | 27.943 | ✅ |

| Election | 16.898 | ✅ |

| InternationalSanction | 8.435+ | ✅ |

| Expulsion | 4.074 | ✅ |

| BarredNGO | 3.572 | ✅ |

| CVMProceeding | 537 | ✅ |

| LeniencyAgreement | 115 | ✅ |

| Inquiry/CPI | 105 | ✅ |

| MunicipalGazetteAct | 10 | ✅ |



\---



\## 📦 STATUS DOWNLOADS E IMPORTAÇÕES



| Fonte | Download | Importação | Obs |

|---|---|---|---|

| cnpj 28G | ✅ | ✅ | |

| viagens 7.7G | ✅ | ✅ | |

| tse 43G | ✅ | ⏳ | fila |

| transparencia 2.7G | ✅ | ⏳ | fila |

| siop 2.4G | ✅ | ⏳ | fila |

| opensanctions 2.6G | ✅ | ⏳ | fila |

| camara 1.7G | ✅ | 🔄 | importando agora — heap 16GB |

| siconfi 763M | ✅ | ✅ | |

| icij 667M | ✅ | ✅ | |

| senado 71M | ✅ | ✅ | |

| sanctions 62M | ✅ | ✅ | |

| renuncias 510M | ✅ | ✅ | |

| cpgf 50M | ✅ | ✅ | |

| cvm\_funds 18M | ✅ | ✅ | |

| holdings 10M | ✅ | ✅ | |

| ofac 7.9M | ✅ | ✅ | |

| ceaf 4M | ✅ | ✅ | |

| un\_sanctions 2.4M | ✅ | ✅ | |

| bcb 2.4M | ✅ | ✅ | API Olinda — 16.395 registros |

| cepim 1.4M | ✅ | ✅ | |

| leniency 560K | ✅ | ✅ | |

| cvm 652K | ✅ | ✅ | |

| senado\_cpis 108K | ✅ | ✅ | |

| querido\_diario 8K | ✅ | ✅ | |

| pncp parcial | 🔄 \~66% | ⏳ | baixando agora — retomou 3097/4680 |

| eu\_sanctions | ❌ | ❌ | IP BR bloqueado |

| pep\_cgu | ❌ | ❌ | autenticação 403 |

| world\_bank | ❌ | ❌ | URL morta |

| datasus | ❌ | ❌ | requer Visual C++ |



\---



\## 🔧 CORREÇÕES DESTA SESSÃO (04/05/2026)



| Correção | Arquivo | Status |

|---|---|---|

| heap Neo4j 1GB→16GB, pagecache 512m→4g, transação 1G→4G | docker-compose.yml | ✅ commitado |

| referer adicionado no download\_file | download\_cepim.py linha 63 | ✅ commitado |

| referer adicionado no download\_file | download\_pep\_cgu.py linha 127 | ✅ commitado |

| reescrito com API Olinda — 16.395 registros | download\_bcb.py | ✅ commitado |



\---



\## 🔴 FILA DE IMPORTAÇÃO ATUAL



Rodando agora: \*\*câmara\*\* (transformando desde 01:15 — \~5.1M linhas)

Próximos: transparencia → siop → opensanctions → tse → pncp



Comando para relançar fila se morrer:

```bash

echo "▶️ FILA: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a \~/Downloads/br-acc-novo/pipeline\_imports.log \&\& cd \~/Downloads/br-acc-novo/etl \&\& source \~/.local/bin/env \&\& for FONTE in camara transparencia siop opensanctions tse; do echo "▶️ $FONTE: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline\_imports.log \&\& uv run bracc-etl run --source $FONTE --neo4j-password "changeme" --data-dir ../data 2>\&1 | tee -a ../pipeline\_imports.log \&\& echo "✅ $FONTE: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline\_imports.log \&\& powershell.exe -Command "\[console]::beep(1000,300); \[console]::beep(1200,300)"; done

```



Monitor de log:

```bash

while true; do LAST=$(tail -1 \~/Downloads/br-acc-novo/pipeline\_imports.log); echo "$(date '+%H:%M:%S') — $LAST"; sleep 30; done

```



\---



\## 🔧 TESTES DE URLs (04/05/2026)



| URL | Status |

|---|---|

| BCB API Olinda | ✅ 200 OK |

| Transparencia servidores dadosabertos-download | ❌ 403 persistente |

| World Bank apigwext | ❌ 404 morta |



\---



\## ⚠️ PROBLEMAS CONHECIDOS



| # | Problema | Prioridade |

|---|---|---|

| 1 | Backup desatualizado — fazer após câmara importar | 🔴 URGENTE |

| 2 | Câmara importando — monitorar se passa com heap 16GB | 🔴 |

| 3 | Transparencia servidores 403 persistente | 🟡 |

| 4 | pep\_cgu autenticação 403 | 🟡 |

| 5 | world\_bank URL morta | 🟡 |

| 6 | SOCIO\_DE incompletos 18.7M vs 26.8M | 🟡 |

| 7 | Bug frontend Person grafo vazio | 🟡 |

| 8 | Orquestrador de downloads não existe ainda | 🟡 |

| 9 | DATASUS Visual C++ | 🟠 |

| 10 | Nginx timeout volátil | 🟠 |



\---



\## 💡 COMANDOS ÚTEIS



```bash

\# Monitoramento

while true; do LAST=$(tail -1 \~/Downloads/br-acc-novo/pipeline\_imports.log); echo "$(date '+%H:%M:%S') — $LAST"; sleep 30; done



\# Neo4j totais

docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)\[0] as tipo, count(n) as total ORDER BY total DESC"



\# Backup (NUNCA com importação rodando!)

docker run --rm -v br-acc-novo\_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data \&\& echo "✅ Backup: $(date '+%d/%m/%Y %H:%M:%S')" \&\& powershell.exe -Command "\[console]::beep(1000,500); \[console]::beep(1500,1000)"



\# Abrir arquivo no Notepad (evita travar Git Bash)

notepad \~/Downloads/br-acc-novo/ARQUIVO



\# Commitar

cd \~/Downloads/br-acc-novo \&\& git add docs/ etl/scripts/ etl/src/ \&\& git status --short \&\& git commit -m "sync $(date '+%Y-%m-%d %H:%M')" \&\& git push origin main

```



\---



\## 📅 HISTÓRICO



| Data | O que foi feito |

|---|---|

| 20-25/04 | Infraestrutura + CNPJ + patches |

| 26/04 | CNPJ completo + backup |

| 27/04 | TSE 2024 + Câmara baixada |

| 28/04 | Downloads massivos |

| 29/04 | Viagens ✅ + User-Agent CGU ✅ |

| 30/04 | Backup ✅ + CEPIM ✅ + BCB ✅ |

| 01/05 | run\_query\_with\_retry + batch\_size=1\_000 |

| 02/05 | batch\_size→500. sanctions+siconfi+icij+senado ✅ |

| 03/05 | find\_latest\_date centralizado. CEPIM+PEP corrigidos. |

| 04/05 | heap Neo4j 16GB. referer cepim+pep. BCB reescrito API Olinda. Câmara importando. PNCP retomado. |



\---



\## ⚠️ CHECKLIST NOVA SESSÃO

\[ ] Docker Desktop aberto

\[ ] cd \~/Downloads/br-acc-novo \&\& docker compose up -d

\[ ] cat docs/CHANGELOG\_TECNICO.md

\[ ] tail -5 pipeline\_imports.log

\[ ] ps aux | grep bracc (fila viva?)

\[ ] Se câmara passou: BACKUP PRIMEIRO

\[ ] Depois backup: fila transparencia→siop→opensanctions→tse

\[ ] Depois fila: importar PNCP



\---



\*v20 — 04/05/2026 \~01h30\*

\*Câmara importando com heap 16GB\*

\*PNCP baixando em paralelo\*

\*⚠️ Backup URGENTE após câmara importar\*

