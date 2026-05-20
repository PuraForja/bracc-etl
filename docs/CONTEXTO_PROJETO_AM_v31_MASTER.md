# SISTEMA DE INTELIGENCIA POLITICA - AMAZONAS
## Documento Master Consolidado v31
> Gerado em 19/05/2026 ~20h00

## PERFIL
Nome: Alberto (Rolim)
Contexto: Oposicao politica no Amazonas
Hardware: Xeon 2680 v4, 32GB RAM, HD 2TB
SO: Windows 11 / Git Bash
GitHub: https://github.com/PuraForja/bracc-etl

## STATUS NEO4J (19/05/2026 ~20h00)
Company: 40.671.726
Partner: 17.774.658
GovEmployee: 10.269.641 - transparencia_am completo
Expense: 3.836.389
Person: 2.780.851
TOTAL: ~80M

## ENTITY RESOLUTION AM
POSSIVEL_MESMO_INDIVIDUO implementado 17-19/05/2026
211.883 arestas criadas
2.417 pessoas unicas conectadas
77 orgaos cobertos
Metodo: nome_exato_tse score 0.90
Indices criados: gov_employee_nome, person_name

521 servidores AM socios de empresas
58 servidores com empresas que FORNECEU ou VENCEU licitacoes
93 empresas com contratos publicos

## CASO DESTAQUE - DIEGO ROBERTO AFONSO
Servidor SUHAB/SECT + socio D R A DERIVADOS DE PETROLEO (iniciais dele)
Rede familiar: DH LOJAS DE CONVENIENCIAS + TREVO DA AMAZONIA NAVEGACAO
Forneceu R$ 67.386 em combustivel para parlamentares AM:
- ADAIL FILHO deputado federal MDB/AM: R$ 62.586
- SIDNEY LEITE senador PSD/AM: R$ 4.600
Sem sancoes registradas.

## STATUS DOWNLOADS (19/05/2026)
todos nacionais: OK importado
transparencia_am: 6857 CSVs OK 10.269.641 GovEmployee
pncp: 58% (38/65 meses) rodando em background
CNES FTP mapeado: ftp://ftp.datasus.gov.br/cnes/ - CPF criptografado LGPD

## PENDENTES TECNICOS
[ ] PNCP aguardar 100% e importar
[ ] Fix sessao unica pipelines pendentes
[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] Bug frontend grafo vazio Person nodes
[ ] SOCIO_DE incompletos 18.7M vs 26.8M
[ ] CNES download_cnes_am.py + pipeline
[ ] DOE-AM via OCR portarias CPF parcial
[ ] Relatorio exportavel casos conflito interesse

## HISTORICO
17-19/05: POSSIVEL_MESMO_INDIVIDUO 211k arestas + 58 casos conflito interesse + caso Diego Afonso documentado + CNES FTP mapeado + orchestrator melhorado

## CHECKLIST NOVA SESSAO
[ ] Ler CHANGELOG.md
[ ] docker ps | grep neo4j
[ ] Verificar PNCP rodando
[ ] Neo4j totais
[ ] Gerar v32 ao final

v31 - 19/05/2026 ~20h00
