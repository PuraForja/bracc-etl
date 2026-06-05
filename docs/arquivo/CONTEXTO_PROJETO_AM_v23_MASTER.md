# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v23
> Gerado em 07/05/2026 ~21h00
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

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU — LEIA ANTES DE QUALQUER COISA

```bash
# 1. Verificar se Docker está rodando
docker ps | grep neo4j
# 2. Se não estiver, subir
cd ~/Downloads/br-acc-novo && docker compose up -d
# 3. Estado atual do banco
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"
# 4. Ver últimas linhas do log
tail -20 ~/Downloads/br-acc-novo/pipeline_imports.log
# 5. Ver progresso do PNCP
tail -3 ~/Downloads/br-acc-novo/download_pncp.log
# 6. Ver se PNCP está rodando
ps aux | grep pncp | grep -v grep
# 7. Se PNCP não estiver rodando, relançar
cd ~/Downloads/br-acc-novo && while true; do cd etl && uv run python scripts/download_pncp.py --output-dir ../data/pncp && cd ..; echo "Reiniciando em 30s..."; sleep 30; done >> download_pncp.log 2>&1 &
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

## STATUS NEO4J (07/05/2026 ~20h40)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.636.929 | OK |
| Partner | 17.774.658 | OK |
| MunicipalFinance | 3.469.721 | OK |
| Person | 2.625.042 | OK |
| Health | 612.561 | OK — DATASUS CNES |
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

## STATUS DOWNLOADS E IMPORTAÇÕES (07/05/2026)

| Fonte | Download | Importação | Obs |
|---|---|---|---|
| cnpj | OK | OK | |
| tse | OK | OK | |
| viagens | OK | OK | |
| transparencia | OK | OK | servidores.csv ausente — 403 CGU |
| opensanctions | OK | OK | |
| siop | OK | OK | |
| camara | OK | PENDENTE | código pronto — importação travando |
| siconfi | OK | OK | |
| icij | OK | OK | |
| pncp | ~57% | AGUARDAR | loop com reinício ativo |
| renuncias | OK | OK | |
| datasus | OK | OK | CNES 612k |
| senado | OK | PROBLEMA | erro na importação — investigar |
| sanctions | OK | OK | |
| cpgf | OK | OK | |
| cvm_funds | OK | OK | |
| holdings | OK | OK | |
| ofac | OK | OK | |
| bcb | OK | OK | |
| ceaf | OK | OK | |
| cepim | OK | OK | |
| un_sanctions | OK | OK | |
| cvm | OK | OK | |
| leniency | OK | OK | |
| senado_cpis | OK | OK | |
| querido_diario | OK | OK | parcial |
| tesouro_emendas | OK | OK | Amendment 101k |
| bndes | SEM SCRIPT | — | |
| ibama | SEM SCRIPT | — | crítico AM |
| inep | SEM SCRIPT | — | |
| pgfn | SEM SCRIPT | — | |
| tcu | SEM SCRIPT | — | |
| comprasnet | SEM SCRIPT | — | |
| transferegov | SEM SCRIPT | — | |
| tse_bens | BigQuery | — | credencial GCP |
| tse_filiados | BigQuery | — | credencial GCP |

---

## ORQUESTRADOR (07/05/2026 v3 — ATUAL)

Arquivo: `orchestrator.sh` na raiz do projeto.

**Uso:**
```bash
# Fila completa
bash ~/Downloads/br-acc-novo/orchestrator.sh

# Fontes específicas
bash ~/Downloads/br-acc-novo/orchestrator.sh bcb ceaf

# Forçar reimportação
bash ~/Downloads/br-acc-novo/orchestrator.sh --force bcb tesouro_emendas
```

**O que faz:**
- Sobe Docker + aguarda Neo4j healthy
- Verifica `.installed` — pula fontes já importadas
- Inicia PNCP em background com loop de reinício
- Para cada fonte: verifica cache → baixa se não tiver → importa
- Registra importações no `.installed` com data/hora
- Validação final — lê Neo4j e confirma nodes por label
- Ctrl+C encerra com segurança

**BUG PENDENTE:**
O orquestrador verifica o cache `.installed` mas NÃO lê o Neo4j antes de iniciar.
A lógica correta seria:
1. Sobe Docker
2. Lê Neo4j — `MATCH (n:Label) RETURN count(n)`
3. Se count > 0 → pula importação (já tem dados)
4. Se count = 0 → baixa e importa

Isso evita reimportar fontes que já estão no banco mas não estão no `.installed`.

**LABEL_MAP** (fonte → label Neo4j) está definido no `orchestrator.sh`.

---

## FILA ATUAL (07/05/2026 ~21h00)

- PNCP: ~57% baixado, loop rodando em background
- Orquestrador: parado — aguardando fix do bug de leitura Neo4j
- camara: código pronto, aguardando fix do colega
- senado: erro na importação — investigar

---

## PENDENTES TÉCNICOS

```
[ ] orchestrator: implementar leitura Neo4j ANTES da fila
    — se label tem nodes>0, pular importacao sem precisar do .installed
    — LABEL_MAP ja existe no orchestrator.sh
[ ] camara: aguardar fix colega — ver BRIEFING_CAMARA_PROBLEMA.md
[ ] senado: investigar erro na importacao
[ ] PNCP: aguardar 100% e importar
[ ] Scripts de download faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] SIHSUS (DATASUS tabelas adicionais) — CRÍTICO AM
[ ] INPE PRODES + SICAR + IBAMA — tríade ambiental AM
[ ] TCE-AM — criar pipeline do zero — máxima prioridade política
[ ] Backup Neo4j — URGENTE
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
[ ] Nginx timeout — incorporar no Dockerfile
```

---

## COMANDOS ÚTEIS

```bash
# Monitorar log
tail -f ~/Downloads/br-acc-novo/pipeline_imports.log

# Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup (NUNCA com importação rodando!)
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main

# PNCP progresso
wc -l ~/Downloads/br-acc-novo/data/pncp/.checkpoint 2>/dev/null || tail -1 ~/Downloads/br-acc-novo/download_pncp.log
```

---

## HISTÓRICO

| Data | O que foi feito |
|---|---|
| 20-25/04 | Infraestrutura + CNPJ + patches |
| 26/04 | CNPJ completo + backup |
| 27/04 | TSE 2024 + Camara baixada |
| 28/04 | Downloads massivos |
| 29/04 | Viagens OK + User-Agent CGU OK |
| 30/04 | Backup OK + CEPIM OK + BCB OK |
| 01/05 | run_query_with_retry + batch_size=1000 em 12 pipelines |
| 02/05 | batch_size→500. sanctions+siconfi+icij+senado OK |
| 03/05 | find_latest_date centralizado. CEPIM+PEP corrigidos |
| 04/05 | heap Neo4j 16GB. BCB reescrito API Olinda |
| 05/05 | camara.py vetorizado. siop+opensanctions importados. backup 10.2GB |
| 06/05 | tse+transparencia importados. datasus 612k. PNCP loop reinício |
| 07/05 | orchestrator v3 (cache+validacao+--force). tesouro_emendas OK. MASTER v23 |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG_TECNICO.md
[ ] Executar passo a passo de identificação (seção acima)
[ ] Verificar se PNCP está rodando — se não, relançar
[ ] Verificar Docker up + Neo4j totais
[ ] Resolver bug orchestrator (ler Neo4j antes da fila)
[ ] Continuar pela lista PENDENTES TÉCNICOS
[ ] Gerar v24 ao final da sessão
```

---

v23 — 07/05/2026 ~21h00
PNCP: ~57% baixando
Orquestrador: v3 com cache — bug de leitura Neo4j pendente
Próximo: fix orchestrator + scripts bndes/ibama/inep + TCE-AM
