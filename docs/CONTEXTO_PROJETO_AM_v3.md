# CONTEXTO DO PROJETO — SISTEMA POLÍTICO DO AMAZONAS v3
> Cole este arquivo no início de novas conversas com o Claude para restaurar o contexto completo.

---

## 🧠 INSTRUÇÃO OBRIGATÓRIA PARA O CLAUDE
Você está num projeto longo e técnico com Alberto. Sua janela de contexto é limitada.

**Sua obrigação:** Monitore o tamanho da conversa. Quando perceber que está ficando longa demais (mais de 30-40 trocas), avise proativamente:

> ⚠️ "Alberto, nossa conversa está ficando longa. Recomendo gerar um novo arquivo de contexto atualizado antes de continuarmos."

Depois gere um novo arquivo `.md` atualizado com tudo que foi feito, seguindo o mesmo formato deste documento.

---

## 🎭 COMO O CLAUDE DEVE OPERAR NESTE PROJETO

Operar em dois modos simultaneamente:

**Modo Arquiteto:** Definir arquitetura, sugerir tecnologias, criar estruturas prontas (modelos de banco, fluxos de dados, dashboards)

**Modo Professor:** Explicar passo a passo (nível intermediário), ensinar como implementar, permitir evolução para nível avançado

### Regras importantes:
- Sempre usar dados aplicáveis ao Amazonas quando possível
- Evitar respostas genéricas — ser prático e estratégico
- Explicar E propor implementação
- Nível técnico do Alberto: intermediário — já programou, já usou Linux/Bash, mas faz tempo. Absorve rápido mas precisa de orientação passo a passo.
- Sempre conectar: Dados → Diagnóstico → Problema → Ação → Monitoramento

### Indicadores sempre presentes:
Economia, Saúde, Educação, Segurança, Infraestrutura, Gestão fiscal, Social, Meio ambiente

---

## 👤 Perfil do usuário
- **Nome:** Alberto (Rolim)
- **Contexto:** Membro de partido político de oposição no Amazonas
- **Objetivo:** Usar dados públicos para gestão política e tomada de decisão
- **Hardware:** PC com Xeon 2680 v4, 32GB RAM 2400, HD 2TB (~556GB livre)

---

## 🎯 Objetivo do projeto
Criar um **sistema de inteligência política para o Amazonas** com:
1. Coleta e visualização de dados públicos (saúde, educação, contratos, sanções, etc.)
2. Mapa interativo dos 62 municípios do AM com indicadores
3. Sistema de registro e acompanhamento de problemas por município
4. Dashboards para tomada de decisão política
5. Foco especial no estado do Amazonas

---

## 🖥️ Ambiente do usuário
- **Sistema operacional:** Windows 11
- **Usuário Windows:** Rolim
- **Terminal usado:** Git Bash
- **Path do Python:** `/c/Python314/python.exe`
- **Python3 wrapper:** `~/bin/python3`
- **WSL:** v2.6.3 com `.wslconfig` configurado (24GB RAM)

---

## 🛠️ Infraestrutura instalada

### Ferramentas
| Ferramenta | Versão |
|---|---|
| Docker Desktop | Última (WSL2 backend) |
| Git + Git Bash | Última |
| Chocolatey | v2.7.1 |
| Make | v4.4.1 |
| Python | v3.14.4 |
| WSL 2 | v2.6.3 |
| uv | v0.11.7 (instalado em `~/.local/bin`) |

### Containers Docker
| Container | Porta | Status |
|---|---|---|
| bracc-neo4j | 7474/7687 | ✅ Rodando |
| br-acc-novo-api-1 | 8000 | ✅ Rodando |
| br-acc-novo-frontend-1 | 3000 | ✅ Rodando |

> ⚠️ Containers não sobem automaticamente — rodar `docker compose up -d` ao ligar o PC

### Credenciais
- **Neo4j:** usuário `neo4j`, senha `changeme`
- **PostgreSQL:** usuário `admin`, senha `admin123`, banco `politica_am`

---

## 📦 Projetos instalados

### br-acc (World Transparency Graph)
- **Repositório:** https://github.com/World-Open-Graph/br-acc
- **Pasta:** `C:\Users\Rolim\Downloads\br-acc-novo` ← usar esta!
- **Comunidade:** Discord: discord.gg/YyvGGgNGVD | Twitter: @brunoclz | Site: bracc.org

---

## 🔍 STATUS ATUAL DO BR/ACC (22/04/2026 — noite)

### Download CNPJ ✅ CONCLUÍDO
- Todos os arquivos baixados via mirror Casa dos Dados
- **Pasta:** `C:\Users\Rolim\Downloads\br-acc-novo\data\cnpj\`
- **Tamanho:** ~28GB de dados
- **Arquivos presentes:**
  - `Empresas1-9.zip` (Empresas0.zip estava corrompido — 9.5KB — foi deletado)
  - `Estabelecimentos0-9.zip`
  - `K3241...ESTABELE` (arquivos RF originais)
  - `K3241...SOCIOCSV` (arquivos RF originais)
  - `K3241...EMPRECSV` (arquivos RF originais)

### Pipeline CNPJ 🔄 RODANDO AGORA
- **Comando rodando:**
```bash
cd ~/Downloads/br-acc-novo/etl && uv run bracc-etl run --source cnpj --neo4j-password "changeme" --data-dir ../data --streaming --start-phase 2 2>&1 | tee ../pipeline.log
```
- **Status:** Fase 2 em andamento — gravando Empresas no Neo4j (50k linhas por batch)
- **Log em tempo real:** `tail -f ~/Downloads/br-acc-novo/pipeline.log`

### Correções feitas no código

#### 1. URLs de download (`etl/src/bracc_etl/runner.py`)
```python
# Mirror Casa dos Dados (adicionada 2026)
casadosdados_base = "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/2026-04-12/"
```

#### 2. Fix start_phase na Fase 1 (`etl/src/bracc_etl/pipelines/cnpj.py`, linha ~1107)
```python
# ANTES (bug — ignorava start_phase):
# Phase 1: Build estab_lookup
if use_bq:

# DEPOIS (corrigido):
# Phase 1: Build estab_lookup
if start_phase > 1:
    logger.info("Skipping Phase 1 -- start_phase=%d", start_phase)
elif use_bq:
```

### Problema pendente — Fase 1 (estab_lookup)
- A Fase 1 lê todos os `Estabelecimentos*.zip` para montar um dicionário de lookup (CNPJ → CNAE, UF, município)
- O processo morre **silenciosamente** ao ler `Estabelecimentos0.zip` (2GB comprimido)
- Zip não está corrompido (testado com Python)
- Memória não é o problema (17GB disponíveis no WSL2)
- Causa provável: bug do Python 3.14 com zipfile em arquivos muito grandes, ou OOM killer do Windows
- **Impacto:** campos `uf`, `municipio`, `cnae_principal` ficam vazios nas empresas
- **Pendente:** investigar e resolver a Fase 1 depois que Fases 2 e 3 terminarem

---

## 🗃️ Fontes relevantes para o Amazonas

### Federais (no br/acc)
CNPJ, Portal Transparência, IBAMA, TSE, PGFN, MapBiomas

### AM específicas (não estão no br/acc)
- TCE-AM: https://www.tce.am.gov.br/ — listado como `not_built`
- Portal Transparência AM: https://www.transparencia.am.gov.br/ — não listado

---

## 🏗️ Arquitetura planejada

```
FONTES DE DADOS PÚBLICOS
  ↓ (br-acc ETL pipelines)
Neo4j (grafos de relações) + PostgreSQL (dados estruturados + gestão)
  ↓
Metabase (dashboards + mapas)
  ↓
Painel Político do Amazonas
  • Mapa interativo dos 62 municípios
  • Indicadores por área
  • Sistema de registro de problemas
  • Acompanhamento de ações
```

### Fases
- **Fase 1 ✅** — Infraestrutura instalada
- **Fase 2 🔄** — Pipeline CNPJ rodando (Fases 2 e 3 do streaming)
- **Fase 3 ⏳** — PostgreSQL + tabelas de municípios, problemas, indicadores
- **Fase 4 ⏳** — Conectar Metabase ao PostgreSQL + dashboards
- **Fase 5 ⏳** — Mapa interativo dos 62 municípios do AM

---

## 💡 Comandos úteis

```bash
# Iniciar containers (rodar sempre que ligar o PC)
cd ~/Downloads/br-acc-novo && docker compose up -d

# Verificar containers
docker ps

# Rodar pipeline streaming (pula Fase 1)
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run bracc-etl run --source cnpj --neo4j-password "changeme" --data-dir ../data --streaming --start-phase 2 2>&1 | tee ../pipeline.log

# Rodar pipeline streaming completo (com Fase 1 — pode travar)
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv run bracc-etl run --source cnpj --neo4j-password "changeme" --data-dir ../data --streaming 2>&1 | tee ../pipeline.log

# Monitorar log em tempo real
tail -f ~/Downloads/br-acc-novo/pipeline.log

# Verificar dados no Neo4j
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Verificar memória containers
docker stats --no-stream

# Acessar PostgreSQL
docker exec -it politica-am-db psql -U admin -d politica_am

# uv precisa do PATH — rodar antes se necessário
source ~/.local/bin/env
```

---

## ⚠️ Problemas conhecidos
1. **Fase 1 do pipeline** — morre silenciosamente ao ler `Estabelecimentos0.zip`. Causa desconhecida. Workaround: `--start-phase 2` pula a fase.
2. **Empresas0.zip corrompido** — arquivo de 9.5KB, foi deletado. Pipeline usa Empresas1-9.zip.
3. **uv não está no PATH padrão** — rodar `source ~/.local/bin/env` antes de usar `uv`
4. **Containers não sobem automaticamente** — rodar `docker compose up -d` manualmente
5. **ComprasNet/DATASUS** — scripts não existem na versão pública do projeto
6. **Credenciais BigQuery** — DOU, RAIS, STF, MiDES precisam de `GOOGLE_APPLICATION_CREDENTIALS`
7. **Servidor Receita Federal** — `dadosabertos.rfb.gov.br` fora do ar. Usar mirror Casa dos Dados.

---

## 📋 Próximos passos
- [ ] Aguardar Fases 2 e 3 do pipeline terminarem
- [ ] Verificar dados no Neo4j após conclusão
- [ ] Investigar problema da Fase 1 (estab_lookup / Estabelecimentos0.zip)
- [ ] Confirmar instalação do PostgreSQL (`politica-am-db`)
- [ ] Criar tabelas no PostgreSQL (municípios AM, problemas, indicadores)
- [ ] Conectar Metabase ao PostgreSQL
- [ ] Criar primeiros dashboards no Metabase
- [ ] Mapa interativo dos 62 municípios do AM
- [ ] Contribuir correções de volta para o dev no Discord

---

*Documento gerado em 22/04/2026 — versão 3*
