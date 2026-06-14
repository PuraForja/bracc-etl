# BRACC — Ponto de Entrada para IA
> Leia este arquivo primeiro. Depois siga a ordem abaixo.

## ORDEM DE LEITURA OBRIGATÓRIA

1. Escolha o arquivo de orientações correto para o seu contexto:
   - **IA online** (Claude.ai, ChatGPT, Gemini): `docs/operacional/ORIENTACOES_IA_ONLINE.md`
   - **Aider**: `docs/operacional/ORIENTACOES_IA_AIDER.md`

2. MASTER mais recente — descobrir a versão atual:
```bash
ls ~/bracc/docs/operacional/CONTEXTO_PROJETO_AM_v*_MASTER.md | sort -V | tail -1
```

3. CHANGELOG recente:
```bash
cat ~/bracc/docs/operacional/CHANGELOG.md | tail -80
```

4. `docs/operacional/ESTADO_ATUAL.md` — estado dinâmico do banco

5. Para tarefas de pipeline/download: `docs/operacional/ORIENTACOES_PIPELINE.md`

---

## COMO ACESSAR ARQUIVOS

**IA online:** peça para o Rolim rodar `cat ARQUIVO` e colar o output.

**Aider:** use `/read` para contexto e `/add` para edição:
```
/read docs/operacional/ORIENTACOES_IA_AIDER.md
/read docs/operacional/ORIENTACOES_PIPELINE.md
/read /tmp/changelog_resumo.md
```
Antes de entrar no aider, Rolim deve rodar:
```bash
tail -80 ~/bracc/docs/operacional/CHANGELOG.md > /tmp/changelog_resumo.md
```

---

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

```bash
# Subir ambiente
cd ~/bracc && docker compose up -d && echo OK

# Verificar banco
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC LIMIT 10"

# Orquestrador
bash ~/bracc/orchestrator.sh help
bash ~/bracc/orchestrator.sh list
bash ~/bracc/orchestrator.sh validate
```

## ESTRUTURA
```
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
│   ├── operacional/
│   │   ├── ORIENTACOES_IA_ONLINE.md
│   │   ├── ORIENTACOES_IA_AIDER.md
│   │   ├── ORIENTACOES_PIPELINE.md
│   │   ├── CONTEXTO_PROJETO_AM_vXX_MASTER.md
│   │   ├── ESTADO_ATUAL.md
│   │   ├── CHANGELOG.md
│   │   ├── SETUP_INDICES.md
│   │   ├── PENDENCIAS_FEATURES.md
│   │   └── DOWNLOADS_STATUS.md
│   ├── referencia/          ← CATALOGO_FONTES.md
│   ├── arquivo/             ← docs antigos
│   └── publico/             ← docs públicos
└── pipeline_imports.log
```

## REGRAS CRÍTICAS
- Nunca `git add -A` — sempre `git status --short` primeiro
- Importação sempre sequencial — nunca paralela
- Backup antes de qualquer reimportação em massa
- Todo pipeline novo registrado no orchestrator.sh antes de ser considerado concluído
- Usar `docker compose exec neo4j` (não `docker exec bracc-neo4j`)
- Downloads sempre pelo orchestrator — nunca direto pelo script

---
*Atualizado em 12/06/2026*
