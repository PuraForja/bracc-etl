# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v22
> Gerado em 07/05/2026 ~19h00
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

Ao iniciar nova sessão, execute estes comandos em ordem:

```bash
# 1. Verificar se Docker está rodando
docker ps | grep neo4j

# 2. Se não estiver, subir
cd ~/Downloads/br-acc-novo && docker compose up -d

# 3. Estado atual do banco
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# 4. Ver últimas linhas do log de importação
tail -20 ~/Downloads/br-acc-novo/pipeline_imports.log

# 5. Ver progresso do PNCP
tail -3 ~/Downloads/br-acc-novo/download_pncp.log

# 6. Ver se PNCP está rodando
ps aux | grep pncp

# 7. Se PNCP não estiver rodando, relançar
cd ~/Downloads/br-acc-novo && while true; do cd etl && uv run python scripts/download_pncp.py --output-dir ../data/pncp && cd ..; echo "Reiniciando em 30s..."; sleep 30; done >> download_pncp.log 2>&1 &

# 8. Ver o que falta importar comparando com o catálogo
cat ~/Downloads/br-acc-novo/docs/CHANGELOG_TECNICO.md | grep "TODO\|\[ \]"
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

## STATUS NEO4J (07/05/2026 ~19h00)

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
| Election | 33.602 | OK |
| Sanction | 24.077 | OK |
| InternationalSanction | 8.435 | OK |
| OffshoreOfficer | 6.575 | OK |
| OffshoreEntity | 4.820 | OK |
| Expulsion | 4.074 | OK |
| BarredNGO | 3.572 | OK |
| CVMProceeding | 537 | OK |
| LeniencyAgreement | 115 | OK |
| Inquiry/CPI | 105 | OK |
| **TOTAL** | **~87M** | OK |

---

## STATUS DOWNLOADS E IMPORTAÇÕES (07/05/2026)

| Fonte | Tamanho | Download | Importação | Obs |
|---|---|---|---|---|
| cnpj | 28G | OK | OK | |
| tse | 43G | OK | OK | importado 06/05 |
| viagens | 7.7G | OK | OK | |
| transparencia | 3.0G | OK | OK | servidores.csv ausente |
| opensanctions | 2.6G | OK | OK | importado 05/05 |
| siop | 2.4G | OK | OK | importado 05/05 |
| camara | 1.7G | OK | PENDENTE | código vetorizado pronto — rodar separado |
| siconfi | 763M | OK | OK | |
| icij | 667M | OK | OK | |
| pncp | ~600M+ | ~57% | AGUARDAR | baixando — loop com reinício ativo |
| renuncias | 510M | OK | OK | |
| datasus | 263M | OK | OK | CNES 612k |
| senado | 71M | OK | PROBLEMA | dando erro — aguardar fix |
| sanctions | 62M | OK | OK | |
| cpgf | 50M | OK | OK | |
| cvm_funds | 18M | OK | OK | |
| holdings | 10M | OK | OK | |
| ofac | 7.9M | OK | OK | |
| bcb | 4.7M | OK | OK | API Olinda |
| ceaf | 4.0M | OK | OK | |
| cepim | 1.4M | OK | OK | |
| un_sanctions | 2.4M | OK | OK | |
| cvm | 652K | OK | OK | |
| leniency | 560K | OK | OK | |
| senado_cpis | 108K | OK | OK | |
| querido_diario | 8K | OK | OK | parcial |
| bndes | — | SEM SCRIPT | — | pipeline existe, download não |
| ibama | — | SEM SCRIPT | — | crítico AM |
| inep | — | SEM SCRIPT | — | |
| pgfn | — | SEM SCRIPT | — | |
| tcu | — | SEM SCRIPT | — | |
| comprasnet | — | SEM SCRIPT | — | |
| transferegov | — | SEM SCRIPT | — | |
| tse_bens | — | BigQuery | — | credencial GCP |
| tse_filiados | — | BigQuery | — | credencial GCP |
| caged | — | BigQuery | — | credencial GCP |
| datajud | — | BigQuery/credencial | — | |
| dou/stf/mides/rais | — | BigQuery | — | credencial GCP |

---

## ORQUESTRADOR (07/05/2026 — NOVO)

Arquivo: `orchestrator.sh` na raiz do projeto.

**Uso:**
```bash
# Fila completa
bash ~/Downloads/br-acc-novo/orchestrator.sh

# Fontes específicas
bash ~/Downloads/br-acc-novo/orchestrator.sh bcb ceaf cepim

# Retomar de onde parou
bash ~/Downloads/br-acc-novo/orchestrator.sh FONTE_QUE_PAROU
```

**O que faz:**
- Sobe Docker + aguarda Neo4j healthy
- Inicia PNCP em background com loop de reinício automático
- Para cada fonte: verifica se dados existem → baixa se não tiver → importa
- Fontes na lista SKIP são ignoradas
- Ctrl+C encerra com segurança — aguarda processo atual terminar, informa onde parou e como retomar
- Beep ao concluir cada fonte (tom diferente para erros)

**Lista SKIP atual:**
```bash
SKIP=(
    pncp      # sempre em background
    senado    # dando problema — aguardar fix
)
```

---

## FILA ATUAL (07/05/2026 ~19h00)

- PNCP: ~57% baixado, rodando em background com loop
- camara: código pronto, rodar separado após orquestrador
- Próximo passo: rodar `bash orchestrator.sh` para completar as fontes restantes

---

## PENDENTES TÉCNICOS

```
[ ] camara — rodar importação separada (código vetorizado OK)
[ ] senado — investigar erro e corrigir
[ ] PNCP — aguardar 100% e importar
[ ] Criar scripts de download para: bndes, ibama, inep, pgfn, tcu, comprasnet, transferegov
[ ] SIHSUS (DATASUS) — implementar download FTP — CRÍTICO AM
[ ] INPE PRODES + SICAR — implementar — CRÍTICO AM
[ ] ANTAQ — implementar — hidrovias AM
[ ] Backup Neo4j — fazer após orquestrador terminar
[ ] INICIO.md — criar guia de entrada do projeto
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] Nginx timeout — incorporar no Dockerfile
[ ] BigQuery — após credencial GCP
```

---

## COMANDOS ÚTEIS

```bash
# Monitorar log geral
tail -f ~/Downloads/br-acc-novo/pipeline_imports.log

# Monitorar PNCP
tail -f ~/Downloads/br-acc-novo/download_pncp.log

# Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup (NUNCA com importação rodando!)
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh && git status --short && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main

# PNCP progresso
wc -l ~/Downloads/br-acc-novo/data/pncp/.checkpoint
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
| 04/05 | heap Neo4j 16GB. referer cepim+pep. BCB reescrito API Olinda |
| 05/05 | camara.py vetorizado OK. siop+opensanctions importados. fila transparencia→tse. backup 10.2GB |
| 06/05 | tse+transparencia importados. datasus confirmado 612k. catálogo v3 gerado. PNCP loop reinício |
| 07/05 | orquestrador criado (docker+pncp+download+import+Ctrl+C seguro). MASTER v22 gerado |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG_TECNICO.md
[ ] Executar passo a passo de identificação (seção acima)
[ ] Verificar se PNCP está rodando — se não, relançar
[ ] Verificar se Docker está up
[ ] Conferir neo4j totais
[ ] Continuar pela lista PENDENTES TÉCNICOS acima
[ ] Gerar v23 ao final da sessão
```

---

v22 — 07/05/2026 ~19h00
PNCP: ~57% baixando
Orquestrador: criado e testado
Próximo: rodar orchestrator.sh + camara separado + backup
