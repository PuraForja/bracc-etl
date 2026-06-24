# ORIENTAÇÕES PARA IA ONLINE — BRACC
> Para: Claude.ai, ChatGPT, Gemini e similares
> Atualizado em 24/06/2026
> Cada regra foi alinhada com o usuário após erros reais. Não ignore nenhuma.

---

## QUEM É ALBERTO (ROLIM)
- Membro de partido político de oposição no Amazonas — Partido Missão
- Não é programador profissional mas aprende rápido
- Quer resultados práticos, não teoria
- Trabalha com dados públicos para inteligência política
- Tem sessões longas com muitos comandos — precisa de acompanhamento próximo

---

## FERRAMENTAS DISPONÍVEIS NO AMBIENTE

### RTK — Rust Token Killer (`rtk 0.42.4`)
Filtra outputs de comandos shell antes de enviá-los ao contexto da IA.
- **O que faz:** reduz tokens de outputs de `git`, `grep`, `docker`, etc. em 60–90%
- **O que NÃO faz:** não intercepta chamadas de API
- **Uso:** prefixar comandos com `rtk` — ex: `rtk git status`, `rtk grep "padrão" .`
- Sempre que sugerir um comando shell com output longo, prefixe com `rtk`

### Agent Browser (`agent-browser 0.29.1`)
CLI de automação de navegador headless para agentes de IA.
- **Quando usar:** sempre que precisar coletar dados de um site, extrair conteúdo de páginas, ou quando Rolim precisaria copiar dados manualmente do navegador/console para a IA
- **Fluxo básico:**
  ```bash
  agent-browser open https://exemplo.com
  agent-browser snapshot -i          # lista elementos interativos com refs
  agent-browser get text @e1         # extrai texto do elemento
  agent-browser close
  ```

---

## REGRA #1 — LEIA O CHANGELOG ANTES DE QUALQUER COISA
Peça para o Rolim rodar:
```bash
cat ~/bracc/docs/operacional/CHANGELOG.md | tail -80 && echo "OK"
```
Sempre leia antes de sugerir qualquer correção de código.
Se já foi feito antes → não refaça.

---

## REGRA #2 — VOCÊ NÃO TEM ACESSO AO SISTEMA DE ARQUIVOS
Você não consegue abrir pastas nem ler arquivos diretamente.
Para ver qualquer arquivo, peça para o Rolim rodar `cat ARQUIVO` e colar o output aqui.
Nunca assuma o conteúdo de um arquivo sem tê-lo lido.

---

## REGRA #3 — MONITORAMENTO É SEU TRABALHO
Quando acompanhar downloads e importações:
1. Peça o output dos logs com um único comando
2. Avalie o que está rodando, travou ou terminou
3. Se travou: identifique a causa, corrija, relance
4. Não espere ele perceber que travou — seja proativo

**Verificar processos:**
```bash
ps aux | grep -E "orchestrator|bracc-etl|python" | grep -v grep && echo "OK"
```
Vazio = processo morto. Re-rodar a partir da fonte que travou.

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

## REGRA #5 — ANTES DE CRIAR QUALQUER DOWNLOAD
Toda fonte nova exige investigação antes de escrever código.
Peça para o Rolim rodar os testes e colar o output:
1. **Testar a URL:**
```bash
curl -sI "URL_DA_FONTE" && echo "OK"
```
2. **Se redirecionar (302):** seguir o redirect e testar a URL final
3. **Se for API REST:** buscar o swagger:
```bash
curl -s "https://dominio/v3/api-docs" | python3 -c "import json,sys; [print(p) for p in json.load(sys.stdin).get('paths',{}).keys()]"
```
4. **Se o domínio não resolver:** pesquisar a URL correta em:
   - https://dados.gov.br
   - https://www.gov.br/conecta/catalogo
   - Documentação oficial do portal
5. **Testar um endpoint real antes de codar:**
```bash
curl -s "URL_ENDPOINT?param=valor" | head -100
```
6. **Só depois de confirmar que a URL funciona** → escrever o script

---

## REGRA #6 — SEQUÊNCIA OBRIGATÓRIA DE IMPORTAÇÃO
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

## REGRA #7 — AVISE QUANDO A SESSÃO ESTIVER NO LIMITE
Após 30-40 trocas de mensagens, avise:
> "⚠️ Esta conversa está próxima do limite. Vou gerar o vXX agora antes de continuar."
Então gere novo MASTER e commite no GitHub.

---

## REGRA #8 — REGISTRO OBRIGATÓRIO DE ALTERAÇÕES
Toda vez que alterar um arquivo `.py`:
1. Faça a alteração
2. Atualize `docs/operacional/CHANGELOG.md` com data, arquivo, problema, solução
3. Lembre Rolim de commitar

---

## REGRA #9 — AO FINAL DE CADA SESSÃO
1. Descobrir versão atual do MASTER:
```bash
ls ~/bracc/docs/operacional/CONTEXTO_PROJETO_AM_v*_MASTER.md | sort -V | tail -1
```
2. Gerar novo MASTER incrementando a versão
3. Atualizar `docs/operacional/CHANGELOG.md`
4. Atualizar `docs/operacional/ESTADO_ATUAL.md` com totais do banco
5. Commitar:
```bash
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"
```

---

## REGRA #10 — NOVOS PIPELINES E DOWNLOADS
Todo novo `download_*.py` criado e testado DEVE ser registrado no orchestrator
**antes de ser considerado concluído**. Rolim não aceita rodar downloads diretamente
pelo script — tudo passa pelo orchestrator. Sem registro = tarefa incompleta.
Registrar em 4 lugares:
1. `LABEL_MAP[fonte]="LabelNeo4j"`
2. `TIMEOUT_MAP[fonte]=600` (padrão 180, fontes pesadas 1800)
3. Fila correta: federal → `DEFAULT_QUEUE`, estadual AM → `AMAZONAS_QUEUE`
4. Se download incremental (API paginada ou por período) → `INCREMENTAL_SOURCES`

Todo novo pipeline com CSV > 500k linhas DEVE usar `chunksize=50_000`.
Todo novo campo usado em MATCH/MERGE DEVE ter índice criado ANTES da importação.

---

## REGRA #11 — CHANGELOG ÚNICO
O único CHANGELOG oficial é: `docs/operacional/CHANGELOG.md`
- `etl/scripts/CHANGELOG.md` — descontinuado, não atualizar
- `~/bracc/CHANGELOG.md` (raiz) — atualizar só em releases

---

## O QUE NÃO FAZER — ERROS QUE JÁ ACONTECERAM
| Erro | O que aconteceu | Como evitar |
|---|---|---|
| Não detectou travamento | Processo morreu, percebeu horas depois | Verificar com `ps aux` |
| Sugeriu correção já feita | Refez trabalho | Ler CHANGELOG primeiro |
| Mandou `git add -A` | Quase subiu dados grandes | Verificar `git status` antes |
| Não avisou sobre limite da sessão | Contexto perdido | Avisar após 30-40 trocas |
| Fez importações em paralelo | Neo4j travou | Sempre sequencial |
| Criou campo sem índice | Query travou com full scan | Índice ANTES de importar |
| Pipeline sem chunksize | OOM com CSV grande | chunksize=50_000 obrigatório |
| Não re-rodou WCC após SAME_AS | community_id desatualizado | WCC obrigatório |
| Pipeline não registrado no orchestrator | Fonte invisível para monitoramento | Registrar SEMPRE |
| Usou URL sem testar | Script falhou com 404/conexão | Testar curl antes de codar |
| Assumiu versão do MASTER | Gerou versão errada | Sempre verificar com ls + sort -V |
| Download incremental sem INCREMENTAL_SOURCES | Orchestrator pulava download | Registrar em INCREMENTAL_SOURCES |
| Rodou download direto pelo script | Bypassa monitoramento | Sempre pelo orchestrator |
| Copiou dados manualmente do navegador | Perdeu horas | Usar agent-browser |
| Output longo foi para o contexto sem filtro | Estourou tokens | Prefixar com rtk |

---

## ESTRUTURA DO PROJETO
```
~/bracc/
├── CLAUDE.md
├── docker-compose.yml
├── orchestrator.sh
├── .env                           ← NEO4J_HEAP_MAX=8G
├── docs/operacional/
│   ├── CONTEXTO_PROJETO_AM_vXX_MASTER.md
│   ├── ESTADO_ATUAL.md
│   ├── CHANGELOG.md
│   ├── ORIENTACOES_IA_ONLINE.md   ← este arquivo
│   ├── ORIENTACOES_IA_AIDER.md
│   ├── ORIENTACOES_PIPELINE.md
│   ├── SETUP_INDICES.md
│   ├── PENDENCIAS_FEATURES.md
│   └── DOWNLOADS_STATUS.md
├── etl/
│   ├── scripts/                   ← download_FONTE.py
│   └── src/bracc_etl/
│       ├── pipelines/             ← FONTE.py
│       ├── loader.py
│       └── runner.py
└── data/                          ← dados brutos (no .gitignore)
```

## INFRAESTRUTURA
| Sistema | Acesso |
|---|---|
| Neo4j browser | http://localhost:7474 — neo4j / changeme |
| API | http://localhost:8000 |
| Frontend | http://localhost:3000 — teste@bracc.com / senha123 / invite: rolim |
| GitHub | https://github.com/PuraForja/bracc-etl |

```bash
cd ~/bracc && docker compose up -d && echo "OK"
```

---
*Atualizar este arquivo se novas regras forem alinhadas com o Rolim*
