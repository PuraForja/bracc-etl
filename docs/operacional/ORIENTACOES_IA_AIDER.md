# ORIENTAÇÕES PARA IA NO AIDER — BRACC
> Para: sessões aider (qualquer modelo)
> Atualizado em 24/06/2026
> Cada regra foi alinhada com o usuário após erros reais. Não ignore nenhuma.

---

## QUEM É ALBERTO (ROLIM)
- Membro de partido político de oposição no Amazonas — Partido Missão
- Não é programador profissional mas aprende rápido
- Quer resultados práticos, não teoria
- Trabalha com dados públicos para inteligência política

---

## FERRAMENTAS DISPONÍVEIS NO AMBIENTE

### RTK — Rust Token Killer (`rtk 0.42.4`)
Filtra outputs de comandos shell antes de enviá-los ao contexto da IA.
- **O que faz:** reduz tokens de outputs de `git`, `grep`, `docker`, `pytest`, etc. em 60–90%
- **O que NÃO faz:** não intercepta chamadas de API
- **Uso:** prefixar comandos com `rtk` — ex: `rtk git status`, `rtk git diff`, `rtk grep "padrão" .`
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
No início de toda sessão, execute:
```
/read /tmp/changelog_resumo.md
```
Se o arquivo não existir, peça para o Rolim rodar antes de entrar no aider:
```bash
tail -80 ~/bracc/docs/operacional/CHANGELOG.md > /tmp/changelog_resumo.md
```
Se já foi feito antes → não refaça.

---

## REGRA #2 — ACESSO A ARQUIVOS
Você tem acesso ao sistema de arquivos via `/read` e `/add`. Use corretamente:

| Situação | Comando |
|---|---|
| Ler para contexto/referência | `/read caminho/arquivo.py` |
| Editar o arquivo | `/add caminho/arquivo.py` |
| Remover do contexto | `/drop caminho/arquivo.py` |

**Fluxo obrigatório:**
1. `/read` nos arquivos de referência no início da sessão
2. `/add` só no arquivo que será editado naquela sessão
3. Nunca `/add` arquivos desnecessários — cada arquivo adicionado consome tokens em toda chamada

**Início de sessão recomendado:**
```
/read docs/operacional/ORIENTACOES_IA_AIDER.md
/read docs/operacional/ORIENTACOES_PIPELINE.md
/read /tmp/changelog_resumo.md
```

Para tarefas de pipeline/download, adicionar também:
```
/read etl/scripts/download_tce_am.py     ← referência de padrão API paginada
/read etl/scripts/_download_utils.py     ← referência de padrão bulk
```

---

## REGRA #3 — MONITORAMENTO É SEU TRABALHO
Quando acompanhar downloads e importações, use os comandos shell diretamente:

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

## REGRA #4 — NUNCA EXECUTE COMANDOS PERIGOSOS SEM VERIFICAR
Antes de qualquer `git add`, `rm`, ou comando destrutivo:
- O `.gitignore` protege `data/`, `*.log`, `*.zip`
- Nunca rode `git add -A` direto — sempre verifique com `git status --short` primeiro
- Avisar ANTES de qualquer comando que altera banco, arquivo ou config

---

## REGRA #5 — ANTES DE CRIAR QUALQUER DOWNLOAD
Toda fonte nova exige investigação antes de escrever código:
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
Então gere novo MASTER e commite.

---

## REGRA #8 — REGISTRO OBRIGATÓRIO DE ALTERAÇÕES
Toda vez que alterar um arquivo `.py`:
1. Faça a alteração via `/add` + edição
2. Atualize `docs/operacional/CHANGELOG.md`
3. Lembre Rolim de commitar

---

## REGRA #9 — AO FINAL DE CADA SESSÃO
1. Descobrir versão atual do MASTER:
```bash
ls ~/bracc/docs/operacional/CONTEXTO_PROJETO_AM_v*_MASTER.md | sort -V | tail -1
```
2. Gerar novo MASTER incrementando a versão
3. Atualizar `docs/operacional/CHANGELOG.md`
4. Atualizar `docs/operacional/ESTADO_ATUAL.md`
5. Commitar:
```bash
cd ~/bracc && git add docs/ etl/scripts/ etl/src/ orchestrator.sh api/ && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"
```

---

## REGRA #10 — NOVOS PIPELINES E DOWNLOADS
Todo `download_*.py` criado e testado DEVE ser registrado no orchestrator
**antes de ser considerado concluído**. Rolim não aceita rodar downloads diretamente
pelo script — tudo passa pelo orchestrator. Sem registro = tarefa incompleta.
Registrar em 4 lugares no `orchestrator.sh`:
1. `LABEL_MAP[fonte]="LabelNeo4j"`
2. `TIMEOUT_MAP[fonte]=600`
3. Fila correta: federal → `DEFAULT_QUEUE`, estadual AM → `AMAZONAS_QUEUE`
4. Se incremental → `INCREMENTAL_SOURCES`

Todo novo pipeline com CSV > 500k linhas DEVE usar `chunksize=50_000`.
Todo novo campo em MATCH/MERGE DEVE ter índice criado ANTES da importação.

---

## REGRA #11 — CHANGELOG ÚNICO
O único CHANGELOG oficial é: `docs/operacional/CHANGELOG.md`
- Não atualizar `etl/scripts/CHANGELOG.md` — descontinuado
- `~/bracc/CHANGELOG.md` (raiz) — só em releases

---

## O QUE NÃO FAZER — ERROS QUE JÁ ACONTECERAM
| Erro | Como evitar |
|---|---|
| `/add` em arquivo só para leitura | Usar `/read` para referência |
| `/add` em múltiplos arquivos desnecessários | Só o arquivo que será editado |
| Sugeriu correção já feita | Ler CHANGELOG primeiro |
| Mandou `git add -A` | Verificar `git status` antes |
| Fez importações em paralelo | Sempre sequencial |
| Criou campo sem índice | Índice ANTES de importar |
| Pipeline sem chunksize | chunksize=50_000 obrigatório |
| Não re-rodou WCC após SAME_AS | WCC obrigatório |
| Pipeline não registrado no orchestrator | Registrar SEMPRE |
| Usou URL sem testar | Testar curl antes de codar |
| Assumiu versão do MASTER | Sempre verificar com ls + sort -V |
| Download incremental sem INCREMENTAL_SOURCES | Registrar em INCREMENTAL_SOURCES |
| Rodou download direto pelo script | Sempre pelo orchestrator |
| Copiou dados manualmente do navegador | Usar agent-browser |
| Output longo foi para o contexto sem filtro | Prefixar com rtk |

---

*Atualizar este arquivo se novas regras forem alinhadas com o Rolim*
