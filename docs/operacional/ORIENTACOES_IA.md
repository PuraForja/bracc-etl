# ORIENTAÇÕES PARA A IA — LEIA ANTES DE QUALQUER COISA
> Atualizado em 03/06/2026
> Cada regra foi alinhada com o usuário após erros reais. Não ignore nenhuma.

---

## QUEM É ALBERTO (ROLIM)
- Membro de partido político de oposição no Amazonas — Partido Missão
- Não é programador profissional mas aprende rápido
- Quer resultados práticos, não teoria
- Trabalha com dados públicos para inteligência política
- Tem sessões longas com muitos comandos — precisa de acompanhamento próximo

---

## REGRA #1 — LEIA O CHANGELOG ANTES DE QUALQUER COISA
```bash
cat ~/bracc/docs/operacional/CHANGELOG.md | tail -50 && echo "OK"
```
Sempre leia antes de sugerir qualquer correção de código.
Se já foi feito antes → não refaça.

---

## REGRA #2 — VOCÊ NÃO TEM ACESSO AO GITHUB
Não tente fazer login no GitHub. Trabalhe só com arquivos locais no terminal.
Quando precisar ver um arquivo, peça para o Rolim colar o conteúdo ou rodar `cat ARQUIVO`.

---

## REGRA #3 — MONITORAMENTO É SEU TRABALHO
Quando acompanhar downloads e importações:
1. Peça o output dos logs com um único comando
2. Avalie o que está rodando, travou ou terminou
3. Se travou: identifique a causa, corrija, relance
4. Não espere ele perceber que travou — seja proativo

**Comando padrão de monitoramento:**
```bash
ps aux | grep -E "orchestrator|bracc-etl|python" | grep -v grep && echo "OK"
```

**Verificar transações Neo4j:**
```bash
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "SHOW TRANSACTIONS YIELD transactionId, status, elapsedTime, currentQuery RETURN transactionId, status, elapsedTime, currentQuery" && echo "OK"
```

---

## REGRA #4 — NUNCA MANDE COMANDOS PERIGOSOS SEM VERIFICAR
Antes de qualquer `git add`, `rm`, ou comando destrutivo:
- Verifique o que será afetado
- O `.gitignore` protege `data/`, `*.log`, `*.zip`
- Nunca rode `git add -A` direto — sempre verifique com `git status --short` primeiro
- Avisar ANTES de qualquer comando que altera banco, arquivo ou config

---

## REGRA #5 — SEQUÊNCIA OBRIGATÓRIA DE IMPORTAÇÃO
1. Downloads primeiro — nunca importar enquanto baixa da mesma fonte
2. Uma importação por vez — Neo4j não suporta paralelo
3. Backup NUNCA simultâneo com importação
4. Backup SEMPRE após fila terminar

**Após qualquer importação que cria SAME_AS — re-rodar WCC obrigatório:**
```bash
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.graph.drop('identity-graph') YIELD graphName" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.graph.project('identity-graph', ['Person','Partner','GlobalPEP','OffshoreOfficer'], {SAME_AS: {orientation: 'UNDIRECTED'}}) YIELD graphName, nodeCount, relationshipCount" && echo "OK"
cd ~/bracc && docker compose exec neo4j cypher-shell -u neo4j -p changeme "CALL gds.wcc.write('identity-graph', {writeProperty: 'community_id'}) YIELD componentCount, nodePropertiesWritten" && echo "OK"
```

---

## REGRA #6 — AVISE QUANDO A SESSÃO ESTIVER NO LIMITE
Após 30-40 trocas de mensagens, avise:
> "⚠️ Esta conversa está próxima do limite. Vou gerar o vXX agora antes de continuar."
Então gere novo MASTER e commite no GitHub.

---

## REGRA #7 — COMO DETECTAR TRAVAMENTO
```bash
ps aux | grep -E "orchestrator|bracc-etl" | grep -v grep && echo "OK"
```
Vazio = processo morto. Re-rodar a partir da fonte que travou.

---

## REGRA #8 — REGISTRO OBRIGATÓRIO DE ALTERAÇÕES
Toda vez que alterar um arquivo `.py`:
1. Faça a alteração
2. Atualize `docs/operacional/CHANGELOG.md` com data, arquivo, problema, solução
3. Lembre Rolim de commitar

---

## REGRA #9 — AO FINAL DE CADA SESSÃO
1. Gere novo `docs/operacional/CONTEXTO_PROJETO_AM_vXX_MASTER.md` (incrementar versão)
2. Atualize `docs/operacional/CHANGELOG.md`
3. Atualize `docs/operacional/ESTADO_ATUAL.md` com totais do banco
4. Commite:
```bash
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"
```

---

## REGRA #10 — NOVOS PIPELINES E DOWNLOADS
Todo novo `download_*.py` DEVE ser registrado no orchestrator em 3 lugares:
1. `LABEL_MAP[fonte]="LabelNeo4j"`
2. `TIMEOUT_MAP[fonte]=600` (padrão 180, fontes pesadas 1800)
3. Na lista de fontes da fila principal

Todo novo pipeline com CSV > 500k linhas DEVE usar `chunksize=50_000`.
Todo novo campo usado em MATCH/MERGE DEVE ter índice criado ANTES da importação.

---

## REGRA #11 — CHANGELOG ÚNICO
O único CHANGELOG oficial é: `docs/operacional/CHANGELOG.md`
- `etl/scripts/CHANGELOG.md` — descontinuado, não atualizar
- `~/bracc/CHANGELOG.md` (raiz) — é o CHANGELOG público do repo, atualizar só em releases

---

## O QUE NÃO FAZER — ERROS QUE JÁ ACONTECERAM
| Erro | O que aconteceu | Como evitar |
|---|---|---|
| Não detectou travamento | Processo morreu, percebeu horas depois | Verificar com `ps aux` |
| Sugeriu correção já feita | Refez trabalho | Ler CHANGELOG primeiro |
| Mandou `git add -A` | Quase subiu dados grandes | Verificar com `git status` antes |
| Não avisou sobre limite da sessão | Contexto perdido | Avisar após 30-40 trocas |
| Fez importações em paralelo | Neo4j travou | Sempre sequencial |
| Criou campo sem índice | Query travou com full scan | Índice ANTES de importar |
| Pipeline sem chunksize | OOM com CSV grande | chunksize=50_000 obrigatório |
| Não re-rodou WCC após SAME_AS | community_id desatualizado | WCC após toda importação com SAME_AS |

---

## ESTRUTURA DO PROJETO
~/bracc/
├── CLAUDE.md                      ← LEIA PRIMEIRO — contexto para IA
├── docker-compose.yml
├── orchestrator.sh
├── .env                           ← NEO4J_HEAP_MAX=8G
├── docs/
│   ├── operacional/               ← docs de trabalho ativos
│   │   ├── CONTEXTO_PROJETO_AM_v35_MASTER.md
│   │   ├── ESTADO_ATUAL.md        ← estado do banco — atualizar toda sessão
│   │   ├── CHANGELOG.md           ← changelog oficial
│   │   ├── ORIENTACOES_IA.md      ← este arquivo
│   │   ├── ORIENTACOES_PIPELINE.md
│   │   ├── SETUP_INDICES.md
│   │   ├── PENDENCIAS_FEATURES.md
│   │   ├── DOWNLOADS_STATUS.md
│   │   └── BRACC_INSTALLER_ESCOPO.md
│   ├── referencia/
│   │   └── CATALOGO_FONTES.md     ← todas as fontes de dados
│   ├── arquivo/                   ← histórico, não editar
│   └── publico/                   ← docs do repo público original
├── etl/
│   ├── scripts/                   ← download_FONTE.py
│   └── src/bracc_etl/
│       ├── pipelines/             ← FONTE.py
│       ├── loader.py
│       └── runner.py
└── data/                          ← dados brutos (no .gitignore)

---

## INFRAESTRUTURA
| Sistema | Acesso |
|---|---|
| Neo4j browser | http://localhost:7474 — neo4j / changeme |
| API | http://localhost:8000 |
| Frontend | http://localhost:3000 — teste@bracc.com / senha123 / invite: rolim |
| GitHub | https://github.com/PuraForja/bracc-etl |

```bash
# Subir tudo
cd ~/bracc && docker compose up -d && echo "OK"
```

---

*Atualizar este arquivo se novas regras forem alinhadas com o Rolim*
