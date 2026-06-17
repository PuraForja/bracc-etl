# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v38
> Gerado em 16/06/2026 — consolida v37 + sessões de 12-16/06/2026
---
## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO
Antes de qualquer ação leia:
1. docs/operacional/ORIENTACOES_IA_ONLINE.md — regras obrigatórias
2. tail -80 docs/operacional/CHANGELOG.md — o que já foi feito
3. docs/operacional/ESTADO_ATUAL.md — estado dinâmico do banco e filas
---
## PASSO A PASSO — NOVA SESSÃO
```bash
cd ~/bracc && docker compose up -d && echo OK
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10" && echo OK
cat ~/bracc/docs/operacional/ESTADO_ATUAL.md
tail -80 ~/bracc/docs/operacional/CHANGELOG.md
```
---
## PERFIL
Nome: Alberto (Rolim)
Contexto: Oposição política no Amazonas — Partido Missão
Hardware: Xeon 2680 v4, 32GB RAM, HD 2TB
SO: Windows 11 + WSL Ubuntu
GitHub: https://github.com/PuraForja/bracc-etl
Projeto: ~/bracc/ (WSL)
---
## INFRAESTRUTURA
Neo4j: localhost:7474 — neo4j / changeme
API: localhost:8000
Frontend: localhost:3000 — teste@bracc.com / senha123 / invite: rolim
GDS: 2.13.10 instalado
Neo4j heap: 8GB (.env)
---
## STATUS NEO4J (16/06/2026)
Company:             40.682.561
Partner:             17.774.658
GovEmployee:         10.280.321  ← histórico trimestral completo (2023-2026)
Expense:              3.836.389
MunicipalFinance:     3.469.721
Person:               3.113.426
DeclaredAsset:        2.817.000
Bid:                  2.170.419
Health:                 612.561
TaxWaiver:              291.799
GovTravel:              260.000
Contract:               217.854  ← +comprasnet (todo Brasil, 2021-hoje)
Amendment:              177.606  ← transferegov
GovCardExpense:         131.950
GlobalPEP:              117.910
Convenio:                70.357  ← transferegov
Election:                50.497
Fund:                    41.107
Payment:                 40.000  ← SIAFI (volume suspeito — ver pendências)
Sanction:                24.077
InternationalSanction:    9.707
OffshoreOfficer:          6.575
OffshoreEntity:           4.820
Expulsion:                4.074
BarredNGO:                3.572
Obra:                     2.584  ← obras.gov AM (novo)
CVMProceeding:              537
TOTAL: ~88M+
---
## O QUE FOI FEITO (12-16/06/2026)

### [12/06/2026] — Novos pipelines criados
- download_transferegov.py: criado e funcional
- download_comprasnet.py: criado — endpoint PNCP contratos, checkpoint, 996 janelas desde 2021
- download_obras.py: criado — API Obras.gov paginada com checkpoint
- pipelines/obras.py: criado — ObrasPipeline com nós Obra, EXECUTA, CONTRATOU
- orchestrator.sh: obras e comprasnet registrados

### [13/06/2026] — transferegov importado
- 177.606 Amendment nodes
- 70.357 Convenio nodes
- 103.811 AUTOR_EMENDA relationships
- 354.451 BENEFICIOU relationships
- 73.914 GEROU_CONVENIO relationships

### [14/06/2026] — obras.py corrigido (3 campos)
- ID: rec.get("id")/rec.get("codigoObra") → rec.get("idUnico")
- Situacao: _SITUACAO_MAP removido → string direta rec.get("situacao")
- Executor/Contratante: dict único → loop em lista executores/repassadores

### [14/06/2026] — comprasnet importado
- 3.153 Contract nodes (todo Brasil, 2021-hoje)
- TIMEOUT_MAP[comprasnet]=1800 adicionado
- Filtro UF=AM considerado e descartado — dados leves (5.4MB)

### [14/06/2026] — limpeza banco
- Índice obra_id_unique criado
- 2 índices órfãos dropados (index_343aff4e, index_f7700477)

### [16/06/2026] — obras.py corrigido (relações)
- campo codigo é int na API — zfill(14) adicionado para restaurar zeros à esquerda
- códigos SIAFI curtos (<11 dígitos) ignorados (ministérios sem CNPJ)
- rows de relacionamento corrigidas: {"cnpj","obra_id"} → {"source_key","target_key"}
- Resultado: 1.616 EXECUTA + 277 CONTRATOU relationships criadas
- _SITUACAO_MAP (código morto) removido do arquivo

### [16/06/2026] — servidores_federais histórico completo
- 11 CSVs trimestrais (2023-2026) confirmados no banco
- 10.280.321 GovEmployee (histórico completo)

---
## PENDENTES PRIORITÁRIOS
- [ ] SIAFI — 40k Payment nodes suspeito: API tem dados desde 2014, verificar volume real
- [ ] Índice emp_id GovEmployee — queries lentas (~14s)
- [ ] SAME_AS servidores_federais ↔ Person
- [ ] Pipeline servidores_federais — importa só CSV mais recente (verificar)
- [ ] Pipelines com correção de sessão pendente: camara.py, senado_cpis.py, camara_inquiries.py, mides.py, transferegov.py, transparencia.py, tse.py, senado.py, tcu.py, datajud.py, ibama.py, icij.py, tse_filiados.py
- [ ] TSE Filiação Partidária
- [ ] Expansão adaptativa depth=2
- [ ] Busca por nome não abre grafo no frontend

---
## PADRÕES TÉCNICOS IMPORTANTES (aprendidos em produção)

### load_relationships — rows devem ter source_key/target_key
O Neo4jBatchLoader.load_relationships() filtra rows por r.get("source_key") e r.get("target_key").
Pipelines devem usar exatamente esses nomes nos dicts de relacionamento:
```python
rels.append({"source_key": cnpj, "target_key": obra_id})
```
NÃO usar nomes semânticos como {"cnpj": ..., "obra_id": ...} — serão descartados silenciosamente.

### CNPJs como int na API Obras.gov
campo codigo vem como int, perdendo zeros à esquerda.
Solução: str(int(v)).zfill(14) + ignorar se len < 11 (códigos SIAFI)

### Download com checkpoint
Ao rodar --force, o orchestrator não passa --skip-existing.
O checkpoint é ignorado e o download recomeça, mas _flush_to_disk faz merge nos arquivos existentes.
Log "0 total records" pode ser falso positivo quando todas as páginas estão no checkpoint.

---
## COMANDOS ÚTEIS
```bash
# Subir ambiente
cd ~/bracc && docker compose up -d && echo OK

# Estado do banco
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup
docker run --rm -v bracc_neo4j-data:/data -v /home/rolim:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo OK

# Orquestrador
bash ~/bracc/orchestrator.sh help
bash ~/bracc/orchestrator.sh list
bash ~/bracc/orchestrator.sh validate
bash ~/bracc/orchestrator.sh update --am
bash ~/bracc/orchestrator.sh update --force obras

# Commitar
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh && git status --short && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo OK
```

---
## HISTÓRICO RESUMIDO
| Data | O que foi feito |
|---|---|
| 20-26/04 | Infraestrutura + CNPJ + patches |
| 27-30/04 | Downloads massivos + viagens + cepim + bcb |
| 01-02/05 | run_query_with_retry + batch_size=500 + índices |
| 03-05/05 | camara vetorizado + heap Neo4j + auditoria banco |
| 07-09/05 | orchestrator v1 + sessão única loader + câmara completa |
| 10/05 | Barra de progresso + MODO_TESTE + watchdog |
| 12-13/05 | Senado + transparencia_am início + _download_utils |
| 17/05 | transparencia_am completa + WCC + entity resolution |
| 23-31/05 | PNCP importação + bid_id index + backup |
| 01-03/06 | GDS + WCC community_id + TSE bens + docs reorganizados |
| 04-05/06 | TCE-AM pipeline + orchestrator refactor |
| 06/06 | parse_date fix + backup + GraphCanvas fix + docs |
| 07-08/06 | servidores_federais histórico + grafo fix + limpeza docs |
| 12-13/06 | transferegov + comprasnet + obras pipelines criados |
| 14/06 | obras.py campos corrigidos + comprasnet importado + limpeza índices |
| 16/06 | obras relações corrigidas (zfill+source_key) + servidores histórico confirmado |

---
## CHECKLIST NOVA SESSÃO
[ ] cd ~/bracc && docker compose up -d
[ ] Verificar totais Neo4j
[ ] tail -80 CHANGELOG.md
[ ] cat ESTADO_ATUAL.md
[ ] Continuar pendentes prioritários

---
v38 — 16/06/2026
obras.gov: 2.584 Obra + 1.616 EXECUTA + 277 CONTRATOU
transferegov: 177k Amendment + 70k Convenio
comprasnet: 3.153 Contract (todo Brasil 2021-hoje)
servidores_federais: 10.28M GovEmployee histórico completo
PRÓXIMO: SIAFI auditoria + índice emp_id + SAME_AS servidores↔Person
