# BRACC — Ponto de Entrada para IA

> Leia este arquivo primeiro. Depois siga a ordem abaixo.

## ORDEM DE LEITURA OBRIGATÓRIA

1. `docs/operacional/ORIENTACOES_IA.md` — regras de comportamento
2. `docs/operacional/CONTEXTO_PROJETO_AM_v36_MASTER.md` — estado atual do projeto
3. `docs/operacional/CHANGELOG.md` (tail -30) — o que foi feito recentemente
4. `docs/operacional/ESTADO_ATUAL.md` — estado dinâmico do banco e filas

## PROJETO

**Nome:** BRACC — Sistema de Inteligência Política do Amazonas
**Repo:** https://github.com/PuraForja/bracc-etl
**Diretório:** ~/bracc/
**Stack:** Python 3.12 + uv + Neo4j 5 + FastAPI + React

## INFRAESTRUTURA

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 |

\`\`\`bash
# Subir ambiente
cd ~/bracc && docker compose up -d && echo OK

# Verificar banco
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10"

# Orquestrador
bash ~/bracc/orchestrator.sh help
bash ~/bracc/orchestrator.sh list
bash ~/bracc/orchestrator.sh validate
\`\`\`

## ESTRUTURA

\`\`\`
~/bracc/
├── orchestrator.sh          ← CLI principal de ETL
├── docker-compose.yml
├── CLAUDE.md                ← este arquivo
├── etl/
│   ├── scripts/             ← download_FONTE.py
│   └── src/bracc_etl/
│       └── pipelines/       ← FONTE.py (importação Neo4j)
├── data/                    ← dados brutos (no .gitignore)
├── docs/
│   ├── operacional/         ← docs de trabalho
│   ├── referencia/          ← CATALOGO_FONTES.md
│   ├── arquivo/             ← docs antigos
│   └── publico/             ← docs públicos
└── pipeline_imports.log
\`\`\`

## REGRAS CRÍTICAS

- Nunca \`git add -A\` — sempre \`git status --short\` primeiro
- Importação sempre sequencial — nunca paralela
- Backup antes de qualquer reimportação em massa
- Todo pipeline novo deve ser registrado no orchestrator.sh
- Usar \`docker compose exec neo4j\` (não \`docker exec bracc-neo4j\`)

---
*Criado em 06/06/2026*
