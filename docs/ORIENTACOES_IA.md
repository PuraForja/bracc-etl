# ORIENTAÇÕES PARA A IA — LEIA ANTES DE QUALQUER COISA
> Criado em 01/05/2026
> Este arquivo define como a IA deve se comportar neste projeto.
> Não ignore nenhum item — cada um foi alinhado com o usuário após erros reais.

---

## QUEM É ALBERTO (ROLIM)

- Membro de partido político de oposição no Amazonas
- Não é programador profissional mas aprende rápido
- Quer resultados práticos, não teoria
- Trabalha com dados públicos para inteligência política
- Tem sessões longas com muitos comandos — precisa de acompanhamento próximo

---

## REGRA #1 — LEIA O CHANGELOG ANTES DE QUALQUER COISA

```bash
cat ~/Downloads/br-acc-novo/docs/CHANGELOG.md
```

**Sempre** leia este arquivo antes de sugerir qualquer correção de código.
Se já foi feito antes → não refaça. Ponto final.

---

## REGRA #2 — VOCÊ NÃO TEM ACESSO AO GITHUB

Não tente fazer login no GitHub. Não tente acessar URLs do GitHub.
GitHub bloqueia robôs. Você trabalha com os arquivos locais no terminal do Rolim.
Quando precisar ver um arquivo, peça para ele colar o conteúdo ou rodar `cat ARQUIVO`.

---

## REGRA #3 — MONITORAMENTO É SEU TRABALHO

Quando o Rolim pedir para acompanhar downloads e importações, faça assim:

1. Peça o output dos logs com um único comando
2. Avalie o que está rodando, o que travou, o que terminou
3. Se travou: identifique a causa, corrija, relance
4. Não espere ele perceber que travou — seja proativo

**Comando padrão de monitoramento:**
```bash
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log && echo "---" && \
tail -3 ~/Downloads/br-acc-novo/download_pncp.log && echo "---" && \
ps aux | grep bracc-etl | grep -v grep
```

---

## REGRA #4 — NUNCA MANDE COMANDOS PERIGOSOS SEM VERIFICAR

Antes de qualquer `git add`, `rm`, ou comando destrutivo:
- Verifique o que será afetado
- Lembre que tem 28G+ de dados que NÃO devem ir para o GitHub
- O `.gitignore` já protege `data/`, `*.log`, `*.zip`, etc.
- Nunca rode `git add -A` direto — sempre verifique com `git status --short` primeiro

---

## REGRA #5 — SEQUÊNCIA OBRIGATÓRIA DE IMPORTAÇÃO

1. **Downloads primeiro** — nunca importar enquanto baixa da mesma fonte
2. **Uma importação por vez** — Neo4j não suporta paralelo
3. **Backup NUNCA simultâneo com importação**
4. **Backup SEMPRE após fila terminar** — antes de qualquer outra coisa

**Ordem de importação (leve → pesado):**
```
cepim → bcb → ceaf → senado → sanctions → siconfi → icij →
camara → transparencia → siop → opensanctions → tse → pncp
```

---

## REGRA #6 — SINAIS SONOROS SÃO OBRIGATÓRIOS

Todo comando longo deve ter beep no final:
```bash
&& powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"
```
Fila completa usa 3 beeps:
```bash
&& powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"
```

---

## REGRA #7 — AVISE QUANDO A SESSÃO ESTIVER NO LIMITE

Após 30-40 trocas de mensagens, avise:
> "⚠️ Esta conversa está próxima do limite. Vou gerar o v[XX] agora antes de continuar."

Então gere o novo MASTER .md e lembre de commitar no GitHub.

---

## REGRA #8 — COMO DETECTAR TRAVAMENTO

O processo de importação morre silenciosamente sem logar erro.
Verifique sempre os dois:
```bash
ps aux | grep bracc-etl | grep -v grep   # vazio = morto
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log  # parou há >10min = travado
```
Se morreu: relance a fila a partir da fonte que travou.

---

## REGRA #9 — REGISTRO OBRIGATÓRIO DE ALTERAÇÕES

Toda vez que alterar um arquivo `.py`:
1. Crie backup: `cp ARQUIVO.py ARQUIVO.py.bak`
2. Faça a alteração
3. Atualize `docs/CHANGELOG.md` com data, arquivo, problema, solução
4. Lembre Rolim de commitar no GitHub

---

## REGRA #10 — AO FINAL DE CADA SESSÃO

Faça estes 3 passos obrigatoriamente:
1. Gere novo `CONTEXTO_PROJETO_AM_vXX_MASTER.md` (incrementar versão)
2. Atualize `CHANGELOG.md` se houve alterações de código
3. Mande comando para commitar os 4 arquivos no GitHub:

```bash
cd ~/Downloads/br-acc-novo && \
  git add docs/ && \
  git commit -m "docs: contexto vXX + changelog atualizado $(date '+%Y-%m-%d')" && \
  git push origin main
```

---

## O QUE NÃO FAZER — ERROS QUE JÁ ACONTECERAM

| Erro | O que aconteceu | Como evitar |
|---|---|---|
| Tentou logar no GitHub | Perdeu tempo — GitHub bloqueia robôs | Trabalhe só com arquivos locais |
| Não detectou travamento por horas | Processo morreu às 18h, percebeu às 23h | Sempre verificar com `ps aux` |
| Sugeriu correção já feita | Refez trabalho desnecessário | Ler CHANGELOG primeiro |
| Mandou `git add -A` | Quase subiu 28G de dados | Verificar com `git status` antes |
| Não avisou sobre limite da sessão | Contexto perdido | Avisar após 30-40 trocas |
| Fez importações em paralelo | Neo4j travou | Sempre sequencial |

---

## ESTRUTURA DO PROJETO

```
br-acc-novo/
├── docker-compose.yml
├── docs/                          ← 4 arquivos de referência ficam aqui
│   ├── CONTEXTO_PROJETO_AM_vXX_MASTER.md
│   ├── CHANGELOG.md
│   ├── CORRECOES_SCRIPTS_DOWNLOAD.md
│   └── URLS_CORRETAS.md
├── etl/
│   ├── scripts/                   ← download_FONTE.py (baixar dados)
│   └── src/bracc_etl/
│       ├── pipelines/             ← FONTE.py (importar para Neo4j)
│       ├── loader.py              ← Neo4jBatchLoader
│       └── runner.py              ← orquestra pipelines
└── data/                          ← dados brutos (NO .gitignore — não commitar!)
```

---

## INFRAESTRUTURA RÁPIDA

| Sistema | Acesso |
|---|---|
| Neo4j browser | http://localhost:7474 |
| API | http://localhost:8000 |
| Frontend | http://localhost:3000 |
| Neo4j user/pass | neo4j / changeme |
| Frontend login | teste@bracc.com / senha123 |

```bash
# Subir tudo
cd ~/Downloads/br-acc-novo && docker compose up -d
```

---

*Criado em 01/05/2026*
*Atualizar este arquivo se novas regras forem alinhadas com o Rolim*


---

## CHANGELOG — REGRA OBRIGATÓRIA

O único changelog oficial é: `docs/CHANGELOG.md`

- `etl/scripts/CHANGELOG.md` foi descontinuado — não atualizar
- Toda IA DEVE ler `docs/CHANGELOG.md` antes de qualquer alteração
- Toda IA DEVE atualizar `docs/CHANGELOG.md` após qualquer alteração
