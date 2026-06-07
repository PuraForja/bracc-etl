# ESTADO ATUAL — BRACC
> Atualizar manualmente ao final de cada sessão

---

## NEO4J (06/06/2026)

| Label | Nodes | Fonte | Status |
|---|---|---|---|
| Company | 40.674.210 | CNPJ Receita Federal | ✅ OK |
| Partner | 17.774.658 | QSA Receita Federal | ✅ OK |
| GovEmployee | 10.269.641 | Transparência AM | ✅ OK |
| Expense | 3.836.389 | Câmara | ✅ OK |
| MunicipalFinance | 3.469.721 | SICONFI | ✅ OK |
| Person | 3.113.425 | Múltiplas fontes | ✅ OK |
| DeclaredAsset | 2.817.000 | TSE Bens | ✅ OK |
| Bid | 2.099.354 | PNCP | ✅ OK |
| Health | 612.561 | DATASUS | ✅ OK |
| TaxWaiver | 291.799 | Renúncias Fiscais | ✅ OK |
| GovTravel | 260.000 | Viagens | ✅ OK |
| GovCardExpense | 131.950 | CPGF | ✅ OK |
| GlobalPEP | 117.910 | OpenSanctions | ✅ OK |
| Amendment | 101.801 | Emendas / SIOP | ✅ OK |
| Contract | 64.190 | Contratos / TCE-AM | ✅ OK |
| Election | 50.497 | TSE | ✅ OK |
| Fund | 41.107 | CVM Fundos | ✅ OK |
| Payment | 40.000 | BNDES | ✅ OK |
| Sanction | 24.077 | CEIS/CNEP/CEPIM | ✅ OK |
| InternationalSanction | 9.707 | OFAC/ONU/OpenSanctions | ✅ OK |
| **TOTAL** | **~88M+** | | |

## RELAÇÕES RELEVANTES

| Relação | Qtd | Obs |
|---|---|---|
| SAME_AS | ~2,5M | WCC identity graph |
| LICITOU | 2.099.331 | PNCP |
| DECLAROU_BEM | 11.322.572 | TSE Bens |

## FILAS

| Fila | Status |
|---|---|
| Federal (DEFAULT_QUEUE) | ✅ Concluída |
| Amazonas (AMAZONAS_QUEUE) | ✅ transparencia_am + tce_am importados |
| TCE-AM download incremental | 🔄 Rodando em background |

## PENDENTES TÉCNICOS

- [ ] **Backup Neo4j — URGENTE** (último: 31/05 — 6 dias atrás)
- [ ] TSE Filiação Partidária — download CDN sem BigQuery
- [ ] BCB Penalidades — reescrever com API Olinda
- [ ] PEP CGU — token email descartável
- [ ] INPE PRODES + SICAR
- [ ] Amom Mandel — 4 nodes separados
- [ ] Expansão adaptativa depth=2
- [ ] Bug frontend — react-force-graph-2d trava após drag/zoom
- [ ] CNES — download_cnes_am.py + pipeline
- [ ] BRACC Installer — ver BRACC_INSTALLER_ESCOPO.md

## AUDITORIA ORQUESTRADOR (06/06/2026)

Problemas identificados — **não corrigidos ainda**:

| # | Problema | Prioridade |
|---|---|---|
| P1 | `docker exec bracc-neo4j` em vez de `docker compose exec neo4j` | ALTA |
| P2 | `bndes`, `comprasnet`, `pgfn`, `transferegov`, `inep`, `tcu` têm pipeline mas não estão em nenhuma fila | MÉDIA |
| P3 | URLs mortas/erradas: `world_bank`, `bcb`, `senado`, `cvm` | MÉDIA |
| P4 | `_sync_neo4j` marca por label, não por fonte — pode marcar incorretamente fontes que compartilham label `Sanction` | MÉDIA |
| P5 | Pipelines sem mapeamento: `caged`, `datajud`, `dou`, `mides`, `pep_cgu`, `rais`, `stf`, `stj_dados_abertos` | BAIXA |
| P6 | SKIP com comentário contraditório sobre pncp | BAIXA |

---
*Criado em 06/06/2026*
*Próxima atualização: após backup + TCE-AM download completo*
