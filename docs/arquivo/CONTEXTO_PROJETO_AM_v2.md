# CONTEXTO DO PROJETO — SISTEMA POLÍTICO DO AMAZONAS v2
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
- **Hardware:** PC com Xeon 2680 v4, 32GB RAM 2400, HD 2TB (~600GB livre)

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
- **Path do Python:** `/c/Python314/python`
- **Python3 wrapper:** `~/bin/python3`
- **WSL:** v2.6.3 com `.wslconfig` configurado (20GB RAM, 10 CPUs, 4GB swap)

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

### Containers Docker rodando
| Container | Porta | Acesso | Status |
|---|---|---|---|
| bracc-neo4j | 7474/7687 | http://localhost:7474 | ✅ Rodando |
| infra-api-1 | 8000 | http://localhost:8000/health | ✅ Rodando |
| infra-frontend-1 | 3000 | http://localhost:3000 | ✅ Rodando |
| metabase | 3001 | http://localhost:3001 | ✅ Instalado |
| politica-am-db (PostgreSQL) | 5432 | — | ⏳ Pendente confirmar |

### Credenciais
- **Neo4j:** usuário `neo4j`, senha `changeme`
- **PostgreSQL:** usuário `admin`, senha `admin123`, banco `politica_am`

---

## 📦 Projetos instalados

### br-acc (World Transparency Graph)
- **Repositório:** https://github.com/World-Open-Graph/br-acc
- **Pasta:** `C:\Users\Rolim\Downloads\br-acc-novo` ← usar esta! (clonada via git)
- **Pasta antiga:** `C:\Users\Rolim\Downloads\br-acc-main` (ZIP, obsoleta)
- **Comunidade:** Discord: discord.gg/YyvGGgNGVD | Twitter: @brunoclz | Site: bracc.org

### Correções feitas no código
Editamos `etl/src/bracc_etl/runner.py` adicionando dois fallbacks de URL:

```python
# --- Mirror Casa dos Dados (adicionada 2026) ---
casadosdados_base = "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/2026-04-12/"

# --- Nova URL dados.gov.br (adicionada 2026) ---
dados_gov_base = "https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj"
```

---

## 🔍 STATUS ATUAL DO BR/ACC (22/04/2026)

### Download CNPJ ✅ CONCLUÍDO
- Todos os arquivos baixados via mirror Casa dos Dados
- **Pasta:** `C:\Users\Rolim\Downloads\br-acc-novo\data\cnpj\`
- **Tamanho:** ~25-30GB de dados
- **Arquivos:** Empresas0-9, Socios0-9, Estabelecimentos0-9 (todos baixados)

### Pipeline CNPJ ❌ FALHANDO
- **Erro:** `ingestion_exit_code: 137` = processo morto por excesso de memória
- **Causa:** Pipeline lê em chunks de 50.000 linhas MAS acumula todos os chunks numa lista `frames` antes de processar — resultado: 100M+ linhas na RAM simultâneamente
- **Onde trava:** Ao começar a ler `K3241.K03200Y0.D60411.ESTABELE` (Estabelecimentos0 — 1.9GB comprimido)
- **Dados carregados antes de travar:**
  - ✅ 40.453.740 linhas de Empresas
  - ✅ 27.494.742 linhas de Sócios
  - ❌ Estabelecimentos — trava aqui

### Próxima investigação pendente
```bash
grep -n "pd.concat\|frames\|concat" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/cnpj.py | head -20
```
Ver onde os frames são concatenados para entender se dá para processar em streaming sem acumular tudo na RAM.

### Arquivo do pipeline CNPJ
```
/c/Users/Rolim/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/cnpj.py
```
1315 linhas. chunk_size padrão = 50.000.

### Outras fontes
- `blocked_external` — portais do governo fora do ar. Rodar `make bootstrap-all` novamente quando voltarem.
- `blocked_credentials` (DOU, RAIS, STF, MiDES) — precisam de `GOOGLE_APPLICATION_CREDENTIALS` no `.env`
- `failed_download` (ComprasNet, DATASUS) — scripts não existem na versão pública

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
- **Fase 2 🔄** — Resolver pipeline CNPJ (problema de memória no ETL)
- **Fase 3 ⏳** — PostgreSQL + tabelas de municípios, problemas, indicadores
- **Fase 4 ⏳** — Conectar Metabase ao PostgreSQL + dashboards
- **Fase 5 ⏳** — Mapa interativo dos 62 municípios do AM

---

## 💡 Comandos úteis

```bash
# Iniciar containers (rodar sempre que ligar o PC)
cd ~/Downloads/br-acc-novo
docker compose up -d

# Verificar containers
docker ps

# Tentar bootstrap (responder "no" no reset)
make bootstrap-all

# Monitorar tamanho da pasta de dados
while true; do du -sh ~/Downloads/br-acc-novo/data/cnpj/ 2>/dev/null; sleep 3; done

# Verificar memória dos containers
docker stats --no-stream

# Acessar PostgreSQL
docker exec -it politica-am-db psql -U admin -d politica_am
```

---

## ⚠️ Problemas conhecidos
1. **Pipeline CNPJ** — exit code 137 ao processar Estabelecimentos. Causa: acumula todos os chunks na RAM. Investigar `pd.concat/frames` no `cnpj.py`
2. **Python wrapper** — resolvido criando `~/bin/python3` apontando para `/c/Python314/python`
3. **ComprasNet/DATASUS** — scripts não existem na versão pública do projeto
4. **Credenciais BigQuery** — DOU, RAIS, STF, MiDES precisam de `GOOGLE_APPLICATION_CREDENTIALS`
5. **Servidor Receita Federal** — `dadosabertos.rfb.gov.br` fora do ar. Usar mirror Casa dos Dados.

---

## 📋 Próximos passos
- [ ] Investigar `pd.concat/frames` no `cnpj.py` para corrigir problema de memória
- [ ] Verificar se dados parciais (Empresas + Sócios) já estão no Neo4j
- [ ] Finalizar instalação/confirmação do PostgreSQL
- [ ] Criar tabelas no PostgreSQL (municípios AM, problemas, indicadores)
- [ ] Conectar Metabase ao PostgreSQL
- [ ] Criar primeiros dashboards no Metabase
- [ ] Contribuir correção das URLs de volta para o dev no Discord

---

*Documento gerado em 22/04/2026 — versão 2*
