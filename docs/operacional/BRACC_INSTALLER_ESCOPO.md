# BRACC Installer — Escopo do Projeto

## Contexto

O BRACC (Brazilian Anti-Corruption and Compliance) é um sistema de inteligência política que agrega dezenas de fontes de dados públicos brasileiros em um banco de dados Neo4j (grafo). O sistema é usado para investigação de conflitos de interesse, corrupção e redes políticas, com foco no estado do Amazonas.

O projeto atualmente possui um orquestrador em bash (`orchestrator.sh`) que foi crescendo de forma incremental e atingiu seus limites. Precisamos reescrevê-lo como um instalador/gerenciador profissional em Python.

---

## Stack Atual

- **OS:** Windows 11 + WSL Ubuntu
- **Banco:** Neo4j 5.26 Community + APOC + GDS 2.13.10 (~83M nodes)
- **ETL:** Python 3.12 + pandas + neo4j driver, gerenciado via `uv`
- **Interface atual:** bash script (~400 linhas), sem TUI
- **Fontes:** ~35 fontes de dados públicos brasileiros

---

## Fontes de Dados Atuais

### Federais
| Fonte | Descrição | Nodes |
|---|---|---|
| CNPJ (Receita Federal) | Empresas e sócios | 40M+ Company, 17M+ Partner |
| TSE Candidaturas | Candidatos 2016-2024 | 3M+ Person |
| TSE Bens Declarados | Patrimônio declarado | em implantação |
| TSE Doações | Financiamento eleitoral | 6M+ DOOU |
| CGU Servidores | Servidores federais | via GovEmployee |
| Portal Transparência | Contratos, emendas, viagens | 64k+ Contract |
| Câmara Federal | Despesas parlamentares | 3.8M+ Expense |
| Senado | CPIs, votações | 105 CPI |
| PNCP | Licitações | 2M+ Bid |
| SICONFI | Finanças municipais | 3.4M+ MunicipalFinance |
| CEAF | Expulsões | 4k+ Expulsion |
| CGU CEPIM | ONGs impedidas | 3.5k+ BarredNGO |
| ICIJ OffshoreLeaks | Empresas offshore | 4.8k+ OffshoreEntity |
| GlobalPEP / OpenSanctions | PEPs internacionais | 117k+ GlobalPEP |
| OFAC / ONU / UE | Sanções internacionais | 9.7k+ InternationalSanction |
| CVM | Processos CVM | 537 CVMProceeding |
| BCB | Penalidades financeiras | em implantação |
| INPE PRODES | Desmatamento | em implantação |
| SICAR | Propriedades rurais | em implantação |

### Estaduais (Amazonas)
| Fonte | Descrição | Nodes |
|---|---|---|
| Transparência AM | Servidores estaduais 80 órgãos 2014-2026 | 10M+ GovEmployee |
| DATASUS CNES | Unidades de saúde | 612k+ Health |

### Planejadas
- Transparência de outros estados (PA, RO, RR, AC, AP)
- Diário Oficial municipal (Querido Diário)
- TSE Filiação Partidária
- Dados de assembleias legislativas estaduais

---

## O Que o BRACC Installer Precisa Fazer

### 1. Interface TUI (Terminal UI)
- Tela principal com lista de todas as fontes
- Checkboxes para selecionar quais fontes baixar/importar
- Filtro por categoria: Federal | Estadual | Internacional
- Filtro por estado: AM | PA | RO | etc.
- Status visual por fonte:
  - ✅ Importado (data da última importação)
  - 🔄 Atualização disponível (novos arquivos detectados)
  - ⏳ Pendente (nunca importado)
  - ❌ Erro (falhou na última execução)
  - 🔗 Link quebrado (URL não responde)

### 2. Gerenciamento de Estado Incremental
Cada fonte tem um arquivo `~/.bracc/state/{fonte}.json` com:
```json
{
  "fonte": "tse_bens",
  "last_download": "2026-06-03T20:00:00",
  "last_import": "2026-06-03T21:00:00",
  "watermark": "2024",
  "files_downloaded": ["bem_candidato_2022.zip", "bem_candidato_2024.zip"],
  "files_available": ["bem_candidato_2022.zip", "bem_candidato_2024.zip"],
  "url_pattern": "https://cdn.tse.jus.br/.../bem_candidato_{ano}.zip",
  "url_status": "ok",
  "last_url_check": "2026-06-03T19:00:00"
}
```

Na execução:
1. Consulta online quais arquivos estão disponíveis (`list_available()`)
2. Compara com `files_downloaded`
3. Baixa apenas os arquivos novos
4. Atualiza o watermark após sucesso

### 3. Verificação de Links
- Opção **"Verificar todos os links"** — faz HEAD request em todas as URLs sem baixar
- Resultado: verde (200), amarelo (redirect), vermelho (404/403/timeout)
- Para links quebrados: tela de reparo assistido com:
  - URL que quebrou e data da última vez que funcionou
  - Sugestões de mirrors conhecidos (dados.gov.br, Base dos Dados, archive.org)
  - Campo para colar nova URL manualmente
  - Salva automaticamente no state.json

### 4. Progress Bar por Fonte
- Barra de progresso com: arquivos baixados / total, velocidade (MB/s), ETA
- Log em tempo real das últimas N linhas
- Estimativa de tempo restante para importação Neo4j

### 5. Sessões Estaduais
Sub-menu dedicado por estado:
- **AM (Amazonas):** transparência estadual, CNES, dados municipais
- **PA (Pará):** idem
- **RO, RR, AC, AP:** demais estados da região Norte
- Cada estado tem suas próprias fontes, URLs e pipelines
- Possibilidade de rodar só um estado específico

### 6. Atualização Incremental
- Job de verificação: consulta online se há novos arquivos desde o último download
- Lógica: `arquivos_disponíveis - arquivos_baixados = arquivos_a_baixar`
- Nunca deleta arquivos já baixados — só adiciona novos
- Re-importação inteligente: só reimporta se houver arquivos novos

### 7. Agendamento
- Opção de configurar jobs automáticos (cron/agendamento Windows)
- Frequências sugeridas por fonte:
  - Diário: Portal Transparência, PNCP
  - Semanal: TSE, CNPJ
  - Mensal: SICONFI, SICAR

---

## Problemas do Orquestrador Atual que Precisam ser Resolvidos

1. **Sem TUI** — só texto no terminal, difícil acompanhar
2. **Sem estado incremental** — sempre baixa tudo do zero
3. **Sem verificação de links** — só descobre link quebrado na hora do download
4. **Timeout fixo** — alerta de "travado" após 3 minutos para qualquer fonte
5. **Sem seleção granular** — para re-rodar uma fonte precisa pedir para a IA
6. **Bash limitado** — difícil adicionar lógica complexa
7. **Sem suporte a estados** — fontes estaduais misturadas com federais

---

## Tecnologias Sugeridas

- **TUI:** `textual` (Python) — framework moderno para TUI com widgets, CSS
- **Progress:** `rich` — barra de progresso, tabelas, logs coloridos
- **State:** JSON por fonte em `~/.bracc/state/`
- **HTTP:** `httpx` — já usado nos downloaders, suporta async
- **Agendamento:** `schedule` ou `APScheduler`
- **Config:** TOML por fonte definindo URL, frequência, dependências

---

## Perguntas para Outras IAs

1. **TUI:** `textual` vs `urwid` vs `curses` — qual melhor para este caso de uso?
2. **Estado incremental:** JSON por arquivo vs SQLite local vs Neo4j mesmo — onde guardar o estado?
3. **Detecção de novos arquivos:** para fontes sem API (só CDN com padrão de URL), qual a melhor forma de descobrir novos arquivos sem varrer toda a URL?
4. **Links quebrados:** existe alguma biblioteca Python que automaticamente testa mirrors e fallbacks?
5. **Sessões estaduais:** como estruturar o código para que adicionar um novo estado seja trivial (idealmente só um arquivo de config TOML)?
6. **Paralelismo:** baixar múltiplas fontes em paralelo (async) vs sequencial — qual o impacto no Neo4j?

---

*Gerado em 03/06/2026 — BRACC v35*
