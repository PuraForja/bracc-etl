# ESTADO ATUAL — BRACC
> Atualizar manualmente ao final de cada sessão
> Última atualização: 08/06/2026

---

## NEO4J (08/06/2026)

| Label | Nodes | Fonte | Status |
|---|---|---|---|
| Company | 40.674.210 | CNPJ Receita Federal | ✅ OK |
| Partner | 17.774.658 | QSA Receita Federal | ✅ OK |
| GovEmployee | 10.277.914 | Transparência AM + Servidores Federais | ✅ OK |
| Expense | 3.836.389 | Câmara | ✅ OK |
| MunicipalFinance | 3.469.721 | SICONFI | ✅ OK |
| Person | 3.113.425 | Múltiplas fontes | ✅ OK |
| DeclaredAsset | 2.817.000 | TSE Bens | ✅ OK |
| Bid | 2.170.419 | PNCP + TCE-AM | ✅ OK |
| Health | 612.561 | DATASUS | ✅ OK |
| TaxWaiver | 291.799 | Renúncias Fiscais | ✅ OK |
| GovTravel | 260.000 | Viagens | ✅ OK |
| Contract | 214.701 | Contratos + TCE-AM | ✅ OK |
| GovCardExpense | 131.950 | CPGF | ✅ OK |
| GlobalPEP | 117.910 | OpenSanctions | ✅ OK |
| Amendment | 101.801 | Emendas / SIOP | ✅ OK |
| Election | 50.497 | TSE | ✅ OK |
| Fund | 41.107 | CVM Fundos | ✅ OK |
| Payment | 40.000 | BNDES | ✅ OK |
| Sanction | 24.077 | CEIS/CNEP/CEPIM | ✅ OK |
| InternationalSanction | 9.707 | OFAC/ONU/OpenSanctions | ✅ OK |
| OffshoreOfficer | 6.575 | ICIJ | ✅ OK |
| OffshoreEntity | 4.820 | ICIJ | ✅ OK |
| Expulsion | 4.074 | CGU/CEAF | ✅ OK |
| BarredNGO | 3.572 | CEPIM | ✅ OK |
| CVMProceeding | 537 | CVM | ✅ OK |
| LeniencyAgreement | 115 | CGU | ✅ OK |
| Inquiry/CPI | 105 | Senado CPIs | ✅ OK |
| **TOTAL** | **~89M+** | | |

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
| Amazonas (AMAZONAS_QUEUE) | ✅ transparencia_am + tce_am + servidores_federais importados |

## BACKUP
- Último backup: 06/06/2026 — /home/rolim/neo4j-backup-20260606.tar.gz

## PENDENTES TÉCNICOS

- [ ] Pipeline servidores_federais importa só CSV mais recente — 10 meses históricos ignorados
- [ ] Índice emp_id em GovEmployee — queries lentas (~14s)
- [ ] SAME_AS servidores_federais ↔ Person via CPF/nome
- [ ] TSE Filiação Partidária — download CDN sem BigQuery
- [ ] BCB Penalidades — reescrever com API Olinda
- [ ] PEP CGU — token email descartável
- [ ] INPE PRODES + SICAR
- [ ] Amom Mandel — 4 nodes separados
- [ ] Expansão adaptativa depth=2
- [ ] CNES — download_cnes_am.py + pipeline
- [ ] BRACC Installer — ver BRACC_INSTALLER_ESCOPO.md
- [ ] Fix sessão única — senado_cpis, cnpj, etc.

## AUDITORIA ORQUESTRADOR

| # | Problema | Prioridade | Status |
|---|---|---|---|
| P1 | docker exec bracc-neo4j | ALTA | ✅ CORRIGIDO 06/06 |
| P2 | bndes, comprasnet, pgfn, transferegov, inep, tcu sem fila | MÉDIA | ABERTO |
| P3 | URLs mortas: world_bank, bcb, senado, cvm | MÉDIA | ABERTO |
| P4 | _sync_neo4j marca por label não por fonte | MÉDIA | ABERTO |
| P5 | Pipelines sem mapeamento: caged, datajud, dou, mides, pep_cgu, rais, stf, stj_dados_abertos | BAIXA | ABERTO |
| P6 | SKIP comentário contraditório pncp | BAIXA | ABERTO |

## FRONTEND

| Item | Status |
|---|---|
| Bug grafo trava após drag/zoom | ✅ RESOLVIDO 07/06 |
| Busca por nome não abre grafo | ABERTO |
| Expansão adaptativa depth=2 | ABERTO |

---
*Criado em 06/06/2026*
*Atualizado em 08/06/2026 — servidores_federais + TCE-AM validados*
