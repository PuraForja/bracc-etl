# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v21
> Gerado em 05/05/2026 ~03h00
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

Subir: cd ~/Downloads/br-acc-novo && docker compose up -d

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |

---

## STATUS NEO4J (05/05/2026 ~03h00)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.483.645+ | OK |
| Partner | 17.774.658 | OK |
| Person | 1.559.007+ | OK |
| Expense | 430.000+ | parcial — camara na fila |
| TaxWaiver | 291.799 | OK |
| GovTravel | 260.000 | OK |
| GovCardExpense | 131.950 | OK |
| GlobalPEP | 117.910 | OK — opensanctions importado 05/05 |
| Fund | 41.107 | OK |
| Contract | 32.259 | OK |
| Amendment | 27.943 | OK |
| Election | 16.898 | OK |
| InternationalSanction | 8.435+ | OK |
| Expulsion | 4.074 | OK |
| BarredNGO | 3.572 | OK |
| CVMProceeding | 537 | OK |
| LeniencyAgreement | 115 | OK |
| Inquiry/CPI | 105 | OK |
| LaborStats | 73.795 | OK — siop importado 05/05 |

---

## STATUS DOWNLOADS E IMPORTAÇÕES

| Fonte | Download | Importação | Obs |
|---|---|---|---|
| cnpj 28G | OK | OK | |
| viagens 7.7G | OK | OK | |
| tse 43G | OK | na fila | proximo apos transparencia |
| transparencia 2.7G | OK | na fila | rodando agora |
| siop 2.4G | OK | OK | importado 05/05 |
| opensanctions 2.6G | OK | OK | importado 05/05 — 117.910 GlobalPEP |
| camara 1.7G | OK | na fila | apos tse — codigo vetorizado OK |
| siconfi 763M | OK | OK | |
| icij 667M | OK | OK | |
| senado 71M | OK | OK | |
| sanctions 62M | OK | OK | |
| renuncias 510M | OK | OK | |
| cpgf 50M | OK | OK | |
| cvm_funds 18M | OK | OK | |
| holdings 10M | OK | OK | |
| ofac 7.9M | OK | OK | |
| ceaf 4M | OK | OK | |
| un_sanctions 2.4M | OK | OK | |
| bcb 2.4M | OK | OK | API Olinda — 16.395 registros |
| cepim 1.4M | OK | OK | |
| leniency 560K | OK | OK | |
| cvm 652K | OK | OK | |
| senado_cpis 108K | OK | OK | |
| querido_diario 8K | OK | OK | |
| pncp parcial | 69% | pendente | baixando — retomou 3241/4680 |
| eu_sanctions | N/A | N/A | coberto pelo opensanctions |
| pep_cgu | N/A | N/A | coberto pelo opensanctions + TSE |
| world_bank | N/A | N/A | coberto pelo opensanctions |
| datasus | pendente | pendente | download_datasus.py via FTP+dbfread — PENDENTE |

---

## FILA ATUAL (05/05/2026 ~03h00)

Ordem: transparencia (rodando) -> tse -> camara

Comando para relançar se morrer:
```
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && for FONTE in transparencia tse camara; do echo "FONTE: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline_imports.log && uv run bracc-etl run --source $FONTE --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "OK $FONTE: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline_imports.log && powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"; done
```

Monitor de log:
```
while true; do LAST=$(tail -1 ~/Downloads/br-acc-novo/pipeline_imports.log); echo "$(date '+%H:%M:%S') -- $LAST"; sleep 30; done
```

---

## CORRECOES DESTA SESSAO (04-05/05/2026)

| Correcao | Arquivo | Status |
|---|---|---|
| heap Neo4j 1GB->16GB, pagecache 4g, transacao 4G | docker-compose.yml | OK commitado |
| referer adicionado no download_file | download_cepim.py linha 63 | OK commitado |
| referer adicionado no download_file | download_pep_cgu.py linha 127 | OK commitado |
| reescrito com API Olinda — 16.395 registros | download_bcb.py | OK commitado |
| vetorizacao completa — sem iterrows | camara.py | OK commitado |
| dbfread adicionado nas dependencias | pyproject.toml | OK commitado |

---

## SOLUCAO DOS 4 PENDENTES

| Fonte | Problema | Solucao |
|---|---|---|
| eu_sanctions | IP BR bloqueado | Dados ja estao dentro do opensanctions importado |
| pep_cgu | auth 403 | opensanctions tem GlobalPEP + TSE cobre PEPs eleitos |
| world_bank | URL morta | Dados debarred ja estao dentro do opensanctions |
| datasus | formato DBC | FTP oficial acessivel + dbfread instalado — download_datasus.py PENDENTE |

FTP DATASUS: ftp://ftp.datasus.gov.br/dissemin/publicos/
Pastas: CNES, SIHSUS, SIM, SINAN, etc
Formato: .dbc — converter com dbfread (ja instalado e no pyproject.toml)

---

## PROBLEMA CAMARA — RESOLVIDO

Causa: iterrows() em 5.1M linhas criava 5.1M objetos Series — estourava RAM
Solucao: vetorizacao pandas — processa colunas inteiras em C
Resultado: teste com limit 1000 passou — 265k linhas em 8 min sem crash
Codigo: camara.py reescrito com _transform_chunk() — arquivo por arquivo com del df

---

## TESTES DE URLs

| URL | Status |
|---|---|
| BCB API Olinda | OK 200 |
| Transparencia servidores dadosabertos-download | 403 persistente |
| World Bank apigwext | 404 morta |
| FTP DATASUS | OK sem login |

---

## PROBLEMAS CONHECIDOS

| # | Problema | Prioridade |
|---|---|---|
| 1 | Backup desatualizado — fazer apos fila terminar | URGENTE |
| 2 | download_datasus.py — implementar FTP+dbfread | alta |
| 3 | Transparencia servidores 403 persistente | media |
| 4 | SOCIO_DE incompletos 18.7M vs 26.8M | media |
| 5 | Bug frontend Person grafo vazio | media |
| 6 | Orquestrador de downloads nao existe | media |
| 7 | Nginx timeout volatil | baixa |

---

## DEPENDENCIAS DO PROJETO

pyproject.toml — dependencias principais:
- neo4j, pandas, httpx, click, pydantic, pypdf, defusedxml, pandera, requests, dbfread

Instalacao manual necessaria (pip):
- dbfread — para conversao DBC do DATASUS (ja instalado 05/05)

---

## COMANDOS UTEIS

```
# Monitoramento
while true; do LAST=$(tail -1 ~/Downloads/br-acc-novo/pipeline_imports.log); echo "$(date '+%H:%M:%S') -- $LAST"; sleep 30; done

# Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup (NUNCA com importacao rodando!)
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo "Backup OK" && powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# Abrir arquivo no Notepad
notepad ~/Downloads/br-acc-novo/ARQUIVO

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ && git status --short && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main

# PNCP progresso
tail -1 ~/Downloads/br-acc-novo/download_pncp.log
```

---

## HISTORICO

| Data | O que foi feito |
|---|---|
| 20-25/04 | Infraestrutura + CNPJ + patches |
| 26/04 | CNPJ completo + backup |
| 27/04 | TSE 2024 + Camara baixada |
| 28/04 | Downloads massivos |
| 29/04 | Viagens OK + User-Agent CGU OK |
| 30/04 | Backup OK + CEPIM OK + BCB OK |
| 01/05 | run_query_with_retry + batch_size=1000 em 12 pipelines |
| 02/05 | batch_size->500. sanctions+siconfi+icij+senado OK |
| 03/05 | find_latest_date centralizado. CEPIM+PEP corrigidos. |
| 04/05 | heap Neo4j 16GB. referer cepim+pep. BCB reescrito API Olinda. |
| 05/05 | camara.py vetorizado OK. siop+opensanctions importados. fila transparencia->tse->camara rodando. dbfread adicionado. 4 pendentes analisados e solucionados. |

---

## CHECKLIST NOVA SESSAO

```
[ ] Docker Desktop aberto
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] cat docs/CHANGELOG_TECNICO.md
[ ] tail -5 pipeline_imports.log
[ ] Se fila terminou: BACKUP PRIMEIRO
[ ] Depois backup: implementar download_datasus.py
[ ] Verificar PNCP progresso
[ ] Gerar v22 ao final da sessao
```

---

v21 — 05/05/2026 ~03h00
Fila: transparencia->tse->camara rodando
PNCP: 69% baixando
URGENTE: backup apos fila terminar
