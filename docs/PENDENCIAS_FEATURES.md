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
