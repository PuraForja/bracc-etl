cat >> \~/Downloads/br-acc-novo/docs/PENDENCIAS\_FEATURES.md << 'EOF'

\## \[12/05/2026] — Features planejadas — NÃO IMPLEMENTADAS



\### FEATURE 1 — Orquestrador multi-estado (sources.yaml)

\*\*Ideia:\*\* Separar fontes por escopo em arquivo YAML externo.

\- `geral:` — fontes federais, valem para qualquer estado (cnpj, tse, pncp, etc.)

\- `estados:` — fontes específicas por estado (amazonas, para, piaui, rj, etc.)

\- Se estado não tem fontes mapeadas: exibir mensagem orientando como contribuir

\- Usuário marca quais estados quer no YAML antes de rodar o orchestrator

\- Vantagem: adicionar novo estado = editar só o YAML, sem mexer no shell

\- \*\*Motivação:\*\* empresa investigada age em todo o estado/país, não só no município



\*\*Estrutura prevista:\*\*

```yaml

geral:

&#x20; - cnpj

&#x20; - tse

&#x20; - transparencia

&#x20; - siop

&#x20; - pncp

&#x20; - opensanctions



estados:

&#x20; amazonas:

&#x20;   - transparencia\_am

&#x20;   - ibama

&#x20;   - antaq

&#x20;   - inpe\_prodes

&#x20;   - sicar

&#x20; para:

&#x20;   status: a\_implementar

&#x20;   orientacao: "adicionar fontes em estados.para\[] e abrir PR"

&#x20; piaui:

&#x20;   status: a\_implementar

&#x20;   orientacao: "adicionar fontes em estados.piaui\[] e abrir PR"

```



\---



\### FEATURE 2 — Modo --check-links no orquestrador

\*\*Ideia:\*\* Flag `--check-links` que testa todos os endpoints/URLs das fontes

sem baixar nada, listando quais estão fora do ar ou com erro.



\*\*Comportamento esperado:\*\*

bash orchestrator.sh --check-links
[OK]   cnpj         https://dadosabertos.rfb.gov.br/...
[OK]   tse          https://dadosabertos.tse.jus.br/...
[FAIL] pncp         https://pncp.gov.br/... → timeout
[FAIL] transparencia_am → 403 Forbidden
[OK]   opensanctions ...
---
### PENDENCIA Entity Resolution AM Clusters Desconectados
Registrado em: 17/05/2026
Prioridade: Alta

PROBLEMA:
Dois clusters desconectados no grafo:
- Cluster A CNPJ/CPF: Company Partner Contract Sanction Election GovTravel
- Cluster B nome: GovEmployee 10.269M servidores AM sem CPF no portal estadual

FONTES PESQUISADAS PARA CPF - TODAS FALHARAM:
- Portal Transparencia Federal: 403
- API CGU: requer Gov.br
- Brasil.io: requer autenticacao
- CAGED FTP: sem CPF individual
- CNES FTP: CPF criptografado por LGPD

CAMINHOS NAO EXPLORADOS:
1. DOE-AM via OCR - portarias tem CPF parcial maior ROI
2. Conselhos CRM COREN CREA OAB - nao investigados
3. TSE doadores x GovEmployee - dados no banco cruzamento pendente
4. CNES CNS como ponte parcial

CNES MAPEADO:
FTP: ftp://ftp.datasus.gov.br/cnes/
Arquivos: PROFISSIONAIS_BRASIL_AM_YYYYMM.ZIP e SCNES_ARQUIVOS_AM_YYYYMM.ZIP
Em claro: CNS + CBO + vinculo + municipio
CPF: criptografado por LGPD
Pendente: download_cnes_am.py + pipeline importacao

INVESTIGACOES POSSIVEIS COM CNS:
LARANJA: Servidor assina procedimentos em clinica X. Clinica contratada pela SES. Socio tem mesmo nome. Score alto. Laranja sem CPF.
FANTASMA: Servidor recebe salario mas CNS nunca aparece no SIA/SIH. Nao trabalha.
DUPLO VINCULO: CNS em dois estabelecimentos no mesmo horario. Portaria 134.
DIRECIONAMENTO: Medico assina AIHs para empresa X. Empresa contratada pela SES. Socio com mesmo nome.
NEPOTISMO: Mesmo sobrenome raro + mesma lotacao + admissao proxima. Cruza TSE.
SUPERFATURAMENTO: Procedimento caro assinado por CBO incompativel.

ARQUITETURA SUGERIDA IA4:
No intermediario (:Identity) com (:SourceRecord)-[:REPRESENTS {score}]->(:Identity)
score > 0.95: auto-link
0.80 a 0.95: revisao manual
menor 0.80: apenas sugestao
