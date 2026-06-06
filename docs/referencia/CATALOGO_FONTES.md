# CATÁLOGO DE FONTES DE DADOS — BRACC
> Atualizado em 03/06/2026 — Sistema de Inteligência Política — Amazonas
> Consolidado de: data-sources.md + pipeline_status.md + source_registry_br_v1.csv + FONTES_EXTERNAS_REFERENCIA.md + matriz-bases-publicas-brasil.md

---

## 1. STATUS ATUAL — BRACC (03/06/2026)

### 1.1 Importadas e Funcionando
| Pipeline | Descrição | Nodes | Relações | Obs |
|---|---|---|---|---|
| cnpj | Receita Federal — empresas e sócios | 40.6M Company + 17.7M Partner | 17.7M SOCIO_DE | Base principal do grafo |
| tse | TSE candidaturas 2016-2024 | 3.1M Person | 6M DOOU, CANDIDATO_EM | Reimportado 02/06 com data_nascimento |
| tse_bens | TSE bens declarados 2006-2024 | 5.6M DeclaredAsset | 11.3M DECLAROU_BEM | Importado 03/06 |
| transparencia_am | Servidores AM 80 órgãos 2014-2026 | 10.2M GovEmployee | EMPREGADO_EM | |
| datasus | CNES estabelecimentos saúde | 612k Health | 435k OPERA_UNIDADE | |
| siconfi | Finanças municipais | 3.4M MunicipalFinance | DECLAROU_FINANCA | |
| pncp | Licitações federais | 2M Bid | 2M LICITOU | |
| tce_am | TCE-AM contratos e licitações AM | Contract + Bid | VENCEU, CONTRATADO_POR, LICITOU_AM | Importado 05/06 |
| camara | Despesas parlamentares CEAP | 3.8M Expense | GASTOU, FORNECEU | |
| transparencia | Contratos, emendas, viagens federal | 64k Contract | VENCEU, AUTOR_EMENDA | |
| senado | CPIs, despesas senado | 105 CPI | | |
| viagens | Viagens a serviço | 260k GovTravel | VIAJOU | |
| cpgf | Cartão corporativo governo | 131.9k GovCardExpense | GASTOU_CARTAO | |
| renuncias | Renúncias fiscais | 291.8k TaxWaiver | RECEBEU_RENUNCIA | |
| siop | Emendas parlamentares | 101.7k Amendment | AUTOR_EMENDA | |
| tesouro_emendas | Execução emendas tesouro | 40k Payment | | |
| icij | ICIJ Offshore Leaks | 4.8k OffshoreEntity + 6.5k OffshoreOfficer | OFFICER_OF | Panama/Paradise/Pandora |
| opensanctions | PEPs globais | 117.9k GlobalPEP | GLOBAL_PEP_MATCH | |
| cvm | Processos CVM | 537 CVMProceeding | CVM_SANCIONADA | |
| cvm_funds | Fundos de investimento | 41.1k Fund | ADMINISTRA | |
| holdings | Holdings derivadas do CNPJ | — | 59k HOLDING_DE | |
| ceaf | Expulsões servidores | 4k Expulsion | EXPULSO | |
| cepim | ONGs impedidas | 3.5k BarredNGO | IMPEDIDA | |
| leniency | Acordos de leniência | 115 LeniencyAgreement | FIRMOU_LENIENCIA | |
| sanctions | CEIS/CNEP sanções | 24k Sanction | SANCIONADA | |
| ofac | Sanções OFAC EUA | 9.7k InternationalSanction | SANCIONADA_INTERNACIONALMENTE | Inclui ONU e UE |
| un_sanctions | Sanções ONU | (merged acima) | | |
| eu_sanctions | Sanções UE | (merged acima) | | |
| world_bank | Debarred World Bank | (merged acima) | | |
| tcu | Acórdãos TCU | — | SANCIONADA | |
| transferegov | Convênios e emendas | — | BENEFICIOU, GEROU_CONVENIO | |
| bcb | Penalidades Banco Central | — | BCB_PENALIZADA | API Olinda |
| senado_cpis | CPIs Senado | 105 CPI | PARTICIPOU_CPI | |
| querido_diario | Diário oficial municipal | 10 MunicipalGazetteAct | PUBLICOU | Parcial |

### 1.2 Pendentes / Com Problemas
| Pipeline | Problema | Solução Mapeada | Prioridade |
|---|---|---|---|
| pep_cgu | 403 — requer token API | Cadastrar email no portal CGU, usar API paginada | Alta |
| tse_filiados | Requer BigQuery ou download manual | Download por partido/UF do CDN TSE | Alta |
| inpe_prodes | Não implementado | CDN INPE — terrabrasilis.dpi.inpe.br | Alta AM |
| sicar | Não implementado | car.gov.br/publico/municipios/downloads | Alta AM |
| tce_am | ✅ Implementado 05/06/2026 | download_tce_am.py + pipelines/tce_am.py | Alta AM |
| datajud | Credenciais não operacionais | Requer chave API CNJ | Alta |
| ibama | Não baixado | Script disponível | Alta AM |
| comprasnet | Stale — precisa atualização | Re-download | Média |
| bndes | Não baixado | Script disponível | Média |
| inep | Não baixado | Script disponível | Média |
| pgfn | Não baixado | Script disponível | Média |
| eu_sanctions | 403 na URL original | URL alternativa data.europa.eu | Média |
| world_bank | URL morta | Nova URL apigwext.worldbank.org | Média |
| transparencia (servidores) | 403 | Testar mês anterior, fallback D-1 | Média |

---

## 2. PRIORIDADE DE IMPLEMENTAÇÃO — AM

| # | Fonte | URL | Relevância |
|---|---|---|---|
| 1 | tce_am | https://www.tce.am.gov.br/ | ✅ Implementado 05/06/2026 |
| 2 | mapbiomas_alertas | https://alerta.mapbiomas.org/api | Desmatamento |
| 3 | anm_mining_rights | https://dados.gov.br/dados/conjuntos-dados/anm | Mineração |
| 4 | sicar_rural_registry | https://www.car.gov.br/publico/municipios/downloads | Propriedades rurais |
| 5 | cnciai_improbidade | https://www.cnj.jus.br/sistemas/cnciai/ | Improbidade administrativa |
| 6 | camara_votes_bills | https://dadosabertos.camara.leg.br/api/v2 | Votações deputados |
| 7 | anp_royalties | https://dados.gov.br/dados/conjuntos-dados/anp | Royalties petróleo |
| 8 | tesouro_emendas | https://www.tesourotransparente.gov.br/ | Execução orçamentária |
| 9 | ibama | https://servicos.ibama.gov.br/ | Embargos ambientais AM |
| 10 | pep_cgu | https://portaldatransparencia.gov.br/download-de-dados/pep | PEPs com CPF |

---

## 3. FONTES NÃO IMPLEMENTADAS — CATÁLOGO COMPLETO

### 3.1 Judiciário
| Fonte | URL | Volume Est. | Valor | Obs |
|---|---|---|---|---|
| CNJ DataJud | api-publica.datajud.cnj.jus.br | Dezenas de M | MUITO ALTO | Requer chave API |
| STJ Dados Abertos | dadosabertos.stj.jus.br | ~500K | ALTO | |
| CNCIAI Improbidade | cnj.jus.br/sistemas/datajud | ~10K | MUITO ALTO | |
| CARF Recursos Fiscais | carf.fazenda.gov.br | ~500K | MÉDIO | |

### 3.2 Agências Reguladoras
| Fonte | URL | Valor |
|---|---|---|
| ANP (petróleo/royalties) | dados.gov.br/dados/conjuntos-dados/anp | MÉDIO |
| ANEEL (energia) | dadosabertos.aneel.gov.br | MÉDIO |
| ANM (mineração) | dados.gov.br/dados/conjuntos-dados/anm | ALTO |
| ANTT (rodovias) | dados.gov.br/dados/conjuntos-dados/antt | BAIXO |
| ANS (saúde) | dados.gov.br/dados/conjuntos-dados/ans | BAIXO |
| ANVISA | dados.gov.br/dados/conjuntos-dados/anvisa | BAIXO |
| ANAC (aviação) | dados.gov.br/dados/conjuntos-dados/anac | BAIXO |
| ANTAQ (portos) | dados.gov.br/dados/conjuntos-dados/antaq | BAIXO |
| ANA (água) | dados.gov.br/dados/conjuntos-dados/ana | BAIXO |
| ANATEL | dados.gov.br/dados/conjuntos-dados/anatel | BAIXO |
| SUSEP (seguros) | dados.gov.br/dados/conjuntos-dados/susep | BAIXO |

### 3.3 Ambiental
| Fonte | URL | Valor |
|---|---|---|
| MapBiomas Alertas | alerta.mapbiomas.org/api | ALTO |
| SICAR (CAR) | car.gov.br/publico/municipios/downloads | ALTO |
| ICMBio/CNUC | icmbio.gov.br | BAIXO |
| INPE PRODES | terrabrasilis.dpi.inpe.br | ALTO AM |
| INPE DETER | terrabrasilis.dpi.inpe.br | ALTO AM |

### 3.4 Orçamento / Fiscal
| Fonte | URL | Valor |
|---|---|---|
| SIAFI | tesouro.gov.br | MÉDIO |
| SIGA Brasil | senado.leg.br/orcamento/sigabrasil | MÉDIO |
| Tesouro Emendas | tesourotransparente.gov.br | ALTO |

### 3.5 Legislativo
| Fonte | URL | Valor |
|---|---|---|
| Câmara — Votações/Projetos | dadosabertos.camara.leg.br/api/v2 | MÉDIO |
| Senado — Votações | legis.senado.leg.br/dadosabertos | MÉDIO |

### 3.6 Estaduais / Municipais
| Fonte | URL | Valor |
|---|---|---|
| TCE-AM | tce.am.gov.br | ALTO AM |
| TCE-PA | tce.pa.gov.br | ALTO |
| TCE-SP | transparencia.tce.sp.gov.br | ALTO |
| TCE-RJ | dados.tce.rj.gov.br | MÉDIO |
| TCE-PE | sistemas.tce.pe.gov.br | MÉDIO |
| MiDES | basedosdados.org (br_mides) | MUITO ALTO |
| Querido Diário | queridodiario.ok.org.br/api | ALTO |
| Portais Estaduais SP/MG/BA/CE/GO/PR/SC/RS/PE/RJ | Variado | MÉDIO |

### 3.7 Internacional
| Fonte | URL | Valor |
|---|---|---|
| INTERPOL Red Notices | interpol.int | MÉDIO — requer chave |

---

## 4. METADADOS TÉCNICOS
> Extraído de source_registry_br_v1.csv (2026-03-01)

| Source ID | Categoria | Tier | Frequência | URL Principal | Formato |
|---|---|---|---|---|---|
| cnpj | identity | P0 | monthly | https://dadosabertos.rfb.gov.br/CNPJ/ | file |
| tse | electoral | P0 | biennial | https://dadosabertos.tse.jus.br/ | file |
| transparencia | contracts | P0 | monthly | https://portaldatransparencia.gov.br/download-de-dados | file |
| sanctions | sanctions | P0 | monthly | https://portaldatransparencia.gov.br/sancoes/consulta | file |
| pep_cgu | integrity | P1 | monthly | https://portaldatransparencia.gov.br/download-de-dados/pep | file |
| pgfn | fiscal | P0 | monthly | https://www.regularize.pgfn.gov.br/dados-abertos | file |
| ibama | environment | P1 | monthly | https://servicos.ibama.gov.br/ | file |
| tcu | audit | P1 | monthly | https://contas.tcu.gov.br/ | file |
| transferegov | transfers | P0 | monthly | https://www.transferegov.sistema.gov.br/ | file |
| rais | labor | P1 | annual | https://basedosdados.org/dataset/br-me-rais | bigquery |
| inep | education | P2 | annual | https://www.gov.br/inep/ | file |
| dou | gazette | P0 | daily | https://www.in.gov.br/ | bigquery |
| datasus | health | P1 | monthly | https://opendatasus.saude.gov.br/ | file |
| icij | offshore | P1 | yearly | https://offshoreleaks.icij.org/ | file |
| opensanctions | sanctions | P1 | monthly | https://www.opensanctions.org/ | file |
| cvm | market | P1 | monthly | https://dados.cvm.gov.br/ | file |
| cvm_funds | market | P1 | monthly | https://dados.cvm.gov.br/dados/FI/ | file |
| pncp | procurement | P0 | daily | https://pncp.gov.br/api/consulta/ | api |
| siconfi | fiscal | P1 | monthly | https://apidatalake.tesouro.gov.br/docs/siconfi/ | api |

---

## 5. BIGQUERY — BASE DOS DADOS

| Dataset | Tabelas Principais | Status BRACC |
|---|---|---|
| br_rf_cnpj | empresas, socios, estabelecimentos | ✅ via CSV direto |
| br_tse_eleicoes | candidatos, receitas, despesas, bens_candidato, filiacao_partidaria | ✅ parcial (bens via CDN, filiados pendente) |
| br_me_rais | microdados_vinculos | ✅ agregado |
| br_me_caged | microdados_movimentacao | ❌ |
| br_stf_corte_aberta | decisoes | ❌ |
| br_camara_dados_abertos | votacao, proposicao, deputado | ✅ parcial (despesas ok, votos não) |
| br_mides | licitacao, contrato, item | ❌ |
| br_bd_diretorios_brasil | municipio, uf | ❌ |

---

## 6. PROJETOS DE REFERÊNCIA EXTERNOS

| Projeto | URL | Utilidade |
|---|---|---|
| brazil-visible (nferdica) | https://github.com/nferdica/brazil-visible | 92 fontes, health check 6h, headers Chrome para 403s |
| rictom/rede-cnpj | https://github.com/rictom/rede-cnpj | SQLite pré-computado CNPJ + TSE + Transparência |
| DanielFillol/DataJUD_API_CALLER | https://github.com/DanielFillol/DataJUD_API_CALLER | Go-based bulk downloader CNJ |
| SINARC | — | Grafo anti-corrupção 90GB — referência |
| Serenata de Amor | suspicions.xz | 8K anomalias CEAP pré-analisadas |
| brasil-io holdings | brasil-io-public.s3.amazonaws.com/holding.csv.gz | 787K relações holding — pronto para carregar |

---

## 7. MATRIZ LEGAL — FUNDAMENTO JURÍDICO DAS FONTES
> Referência para o BRACC Installer — base legal de acesso a cada fonte

| # | Base de Dados | O que Divulga | URL | Fundamento Legal |
|---|---|---|---|---|
| 1 | Portal Dados Abertos | Acesso central a dados federais | dados.gov.br | Lei 12.527/2011 (LAI) + Dec. 8.777/2016 |
| 2 | Portal da Transparência | Gastos, contratos, servidores, sanções | portaldatransparencia.gov.br | LC 131/2009 + LAI |
| 3 | Tesouro Transparente | Dados fiscais da União | tesourotransparente.gov.br | LC 101/2000 (LRF) |
| 4 | Base dos Dados | Dados públicos tratados | basedosdados.org | Iniciativa privada |
| 5 | BCB APIs | Câmbio, juros, crédito, PIX | dadosabertos.bcb.gov.br | Lei 4.595/1964 + LAI |
| 6 | CNPJ | Empresas, sócios, estabelecimentos | arquivos.receitafederal.gov.br | LAI + Dec. 8.777/2016 |
| 7 | Contratos Federais | Contratos do governo | portaldatransparencia.gov.br | LC 131/2009 + LAI |
| 8 | Servidores Federais | Remuneração, cargos, lotação | portaldatransparencia.gov.br | LC 131/2009 + LAI |
| 9 | Emendas Parlamentares | Autor, valor, destinação | portaldatransparencia.gov.br | LC 131/2009 + EC 86/2015 |
| 10 | CEIS/CNEP | Sanções administrativas | portaldatransparencia.gov.br | Lei 12.846/2013 Art. 22 |
| 11 | CEPIM | ONGs impedidas | portaldatransparencia.gov.br | LAI + Dec. 7.592/2011 |
| 12 | CEAF | Expulsões servidores | portaldatransparencia.gov.br | Lei 8.112/1990 + LAI |
| 13 | Viagens a Serviço | Diárias e passagens | portaldatransparencia.gov.br | LC 131/2009 |
| 14 | SICONFI | Finanças estados e municípios | siconfi.tesouro.gov.br | LRF + LC 131/2009 |
| 15 | SIOP | Orçamento federal, LOA, emendas | siop.planejamento.gov.br | LRF |
| 16 | CNES | Estabelecimentos de saúde | datasus.saude.gov.br | Port. GM/MS 1.646/2015 + LAI |
| 17 | SIH/SIM/SINASC | Internações, óbitos, nascimentos | datasus.saude.gov.br | Port. GM/MS 1.646/2015 + LAI |
| 18 | Censo Escolar | Escolas, turmas, matrículas | inep.gov.br | Dec. 6.425/2008 + LAI |
| 19 | TSE Candidaturas | Registros de candidatos | dadosabertos.tse.jus.br | Lei 9.504/1997 |
| 20 | TSE Doações | Receitas, despesas, doadores | dadosabertos.tse.jus.br | Lei 9.504/1997 Art. 28 |
| 21 | TSE Bens Declarados | Patrimônio candidatos | dadosabertos.tse.jus.br | Lei 9.504/1997 Art. 11 §1° IV |
| 22 | TSE Filiados | Base de filiados partidários | dadosabertos.tse.jus.br | Lei 9.096/1995 Art. 19 |
| 23 | DataJud | Processos judiciais | datajud.cnj.jus.br | CF Art. 93 IX + LAI |
| 24 | IBAMA | Multas ambientais, embargos | dadosabertos.ibama.gov.br | Dec. 6.514/2008 + LAI |
| 25 | PRODES/DETER | Desmatamento Amazônia | terrabrasilis.dpi.inpe.br | LAI |
| 26 | CAR/SICAR | Cadastro Ambiental Rural | car.gov.br | Lei 12.651/2012 |
| 27 | RAIS | Vínculos formais e salários | bi.mte.gov.br | Dec. 76.900/1975 + LAI |
| 28 | CAGED | Admissões e demissões | bi.mte.gov.br | Lei 4.923/1965 + LAI |
| 29 | CVM | Demonstrações financeiras, fundos | dados.cvm.gov.br | Lei 6.385/1976 + LAI |
| 30 | DOU | Nomeações, contratos, leis, decretos | in.gov.br | CF Art. 37 + Dec. 10.222/2020 |
| 31 | ANEEL | Geração, distribuição, tarifas | aneel.gov.br | Lei 9.427/1996 + LAI |
| 32 | ANP | Produção petróleo, preços | anp.gov.br | Lei 9.478/1997 + LAI |
| 33 | ANATEL | Banda larga, telecom | anatel.gov.br | Lei 9.472/1997 + LAI |
| 34 | ANVISA | Registros medicamentos | anvisa.gov.br | Lei 9.782/1999 + LAI |
| 35 | IBGE | Censo, PNAD, PIB municipal | ibge.gov.br | Lei 8.184/1991 + LAI |
| 36 | INCRA | Imóveis rurais, assentamentos | incra.gov.br | LAI |
| 37 | SINESP | Estatísticas criminalidade | sinesp.gov.br | Lei 13.675/2018 + LAI |
| 38 | ANS | Operadoras saúde suplementar | ans.gov.br | Lei 9.656/1998 + LAI |
| 39 | ANTAQ | Portos, navegação | antaq.gov.br | LAI |
| 40 | ANM | Direitos minerários | dados.gov.br/conjuntos-dados/anm | LAI |

---

*Atualizado em 03/06/2026 — BRACC v35*
