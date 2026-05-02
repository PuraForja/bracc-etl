# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v5
> Gerado em 24/04/2026 — consolida todas as versões anteriores (v1 a v4)
> Cole este arquivo no início de QUALQUER nova conversa para restaurar contexto completo.

---

## 🧠 INSTRUÇÃO OBRIGATÓRIA PARA O CLAUDE

Você está num projeto longo e técnico com Alberto (Rolim). Sua janela de contexto é limitada.

**Obrigações:**
1. Opere sempre em dois modos: **Arquiteto** (propõe soluções) + **Professor** (explica passo a passo)
2. Monitore o tamanho da conversa. Após 30-40 trocas, avise:
   > ⚠️ "Alberto, nossa conversa está ficando longa. Vou gerar um novo arquivo de contexto antes de continuar."
3. Gere novo `.md` atualizado seguindo este formato
4. Sempre conectar: **Dados → Diagnóstico → Problema → Ação → Monitoramento**
5. Nível técnico: intermediário — já programou, já usou Linux/Bash, absorve rápido mas precisa de orientação passo a passo
6. Sempre usar dados e exemplos do Amazonas quando possível

---

## 👤 Perfil do Usuário

| Campo | Valor |
|---|---|
| Nome | Alberto (Rolim) |
| Contexto | Membro de partido político de oposição no Amazonas |
| Objetivo | Usar dados públicos para gestão política e tomada de decisão |
| Hardware | Xeon 2680 v4, 32GB RAM 2400, HD 2TB (~556GB livre) |
| SO | Windows 11 |
| Terminal | Git Bash |
| Python | `/c/Python314/python.exe` (v3.14.4) |
| uv | `~/.local/bin/uv` v0.11.7 |
| WSL2 | v2.6.3, configurado com 24GB RAM |

---

## 🎯 Objetivo do Projeto

Criar um **sistema de inteligência política para o Amazonas** com:
1. Coleta e visualização de dados públicos (saúde, educação, contratos, sanções, CNPJ, etc.)
2. Mapa interativo dos 62 municípios do AM com indicadores
3. Sistema de registro e acompanhamento de problemas por município
4. Dashboards para tomada de decisão política
5. Cruzamento de dados: CPF/CNPJ de políticos e empresas ligadas ao governo

### Indicadores sempre presentes
Economia, Saúde, Educação, Segurança, Infraestrutura, Gestão fiscal, Social, Meio ambiente

---

## 🛠️ Infraestrutura Instalada

### Ferramentas
| Ferramenta | Versão |
|---|---|
| Docker Desktop | Última (WSL2 backend) |
| Git + Git Bash | Última |
| Chocolatey | v2.7.1 |
| Make | v4.4.1 |
| Python | v3.14.4 |
| WSL 2 | v2.6.3 |
| uv | v0.11.7 |

### Containers Docker
| Container | Porta | Status | Observação |
|---|---|---|---|
| bracc-neo4j | 7474/7687 | ✅ | Neo4j 5.26.24 com APOC |
| br-acc-novo-api-1 | 8000 | ✅ | API FastAPI do br-acc |
| br-acc-novo-frontend-1 | 3000 | ✅ | Frontend React/Nginx |

> ⚠️ **IMPORTANTE:** Containers não sobem automaticamente. Sempre rodar ao ligar o PC:
> ```bash
> cd ~/Downloads/br-acc-novo && docker compose up -d
> ```

### Credenciais
| Sistema | Usuário | Senha | Observação |
|---|---|---|---|
| Neo4j | neo4j | changeme | |
| Frontend BR-ACC | teste@bracc.com | senha123 | Perdido ao reiniciar container |
| Invite code | — | rolim | Para criar novos usuários |
| PostgreSQL | admin | admin123 | banco: politica_am (pendente) |

> ⚠️ **Usuários do frontend são perdidos ao reiniciar containers** — recriar com comando na seção de comandos úteis

---

## 📦 Projeto br-acc

| Campo | Valor |
|---|---|
| Repositório | https://github.com/World-Open-Graph/br-acc |
| Pasta ativa | `C:\Users\Rolim\Downloads\br-acc-novo` |
| Pasta antiga | `C:\Users\Rolim\Downloads\br-acc-main` (ZIP obsoleto — não usar) |
| Discord | discord.gg/YyvGGgNGVD |
| Twitter dev | @brunoclz |
| Site | bracc.org |

### O que o br-acc faz
- **Download** de dados públicos federais (CNPJ, TSE, IBAMA, Portal Transparência, etc.)
- **ETL** — lê, transforma e importa para o Neo4j
- **API** — disponibiliza os dados via HTTP
- **Frontend** — interface web para busca por CPF/CNPJ e visualização de grafos de relações

---

## ✅ STATUS ATUAL DOS DADOS (24/04/2026)

### Neo4j — dados carregados
| Tipo | Quantidade | Status |
|---|---|---|
| Company (empresas) | 40.453.740 | ✅ Completo |
| Partner (sócios c/ CPF mascarado) | 17.774.658 | ✅ Carregado |
| SOCIO_DE (relacionamentos) | 18.528.366 | ⚠️ Incompleto |
| Person (CPF válido) | 0 | ⚠️ RF mascara maioria dos CPFs |

### Frontend — funcionando
- ✅ Login: `http://localhost:3000`
- ✅ Busca por nome/CNPJ funcionando
- ✅ Grafo de relações carregando
- ⚠️ Grafo mostra poucas conexões (relacionamentos incompletos)

### Dados de arquivo no HD
```
C:\Users\Rolim\Downloads\br-acc-novo\data\cnpj\
├── Empresas1-9.zip       (~75-95MB cada) ✅
├── Estabelecimentos0-9.zip (~320MB-2GB cada) ✅
├── Socios0-9.zip         (~217-329MB cada) ✅
├── K3241...EMPRECSV      (arquivos RF originais) ✅
├── K3241...ESTABELE      (arquivos RF originais) ✅
└── K3241...SOCIOCSV      (arquivos RF originais) ✅
⚠️ Empresas0.zip DELETADO (estava corrompido — 9.5KB)
```

---

## 🔧 CORREÇÕES APLICADAS NO CÓDIGO

### Correção 1 — URLs de download
**Arquivo:** `etl/src/bracc_etl/runner.py`
**Problema:** Servidor da Receita Federal (`dadosabertos.rfb.gov.br`) fora do ar desde início de 2026. URLs antigas retornavam 404.
**Solução:** Adicionado mirror Casa dos Dados como fallback.

```python
# Mirror Casa dos Dados (adicionada 2026) — FUNCIONA ✅
casadosdados_base = "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/2026-04-12/"

# dados.gov.br (adicionada 2026) — retorna HTML, não funciona bem ⚠️
dados_gov_base = "https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj"
```

> ⚠️ A data `2026-04-12` no URL do mirror pode mudar. Verificar data mais recente em:
> https://dados-abertos-rf-cnpj.casadosdados.com.br/

---

### Correção 2 — Bug do start_phase na Fase 1
**Arquivo:** `etl/src/bracc_etl/pipelines/cnpj.py` (~linha 1107)
**Problema:** O parâmetro `--start-phase` era ignorado na Fase 1. Mesmo passando `--start-phase 2`, o pipeline sempre executava a Fase 1 (estab_lookup).
**Causa:** Faltava verificação do `start_phase` antes do bloco da Fase 1.

**ANTES (com bug):**
```python
        # Phase 1: Build estab_lookup
        if use_bq:
            logger.info("Phase 1: Building estab_lookup from %d BQ files", len(bq_estab))
```

**DEPOIS (corrigido):**
```python
        # Phase 1: Build estab_lookup
        if start_phase > 1:
            logger.info("Skipping Phase 1 -- start_phase=%d", start_phase)
        elif use_bq:
            logger.info("Phase 1: Building estab_lookup from %d BQ files", len(bq_estab))
```

**Como aplicar:**
```bash
/c/Python314/python.exe -c "
f = open('etl/src/bracc_etl/pipelines/cnpj.py', 'r', encoding='utf-8')
content = f.read()
f.close()
old = '        # Phase 1: Build estab_lookup\n        if use_bq:'
new = '        # Phase 1: Build estab_lookup\n        if start_phase > 1:\n            logger.info(\"Skipping Phase 1 -- start_phase=%d\", start_phase)\n        elif use_bq:'
content = content.replace(old, new, 1)
f = open('etl/src/bracc_etl/pipelines/cnpj.py', 'w', encoding='utf-8')
f.write(content)
f.close()
print('OK')
"
```

---

### Correção 3 — Nginx timeout
**Arquivo:** `/etc/nginx/conf.d/default.conf` dentro do container `br-acc-novo-frontend-1`
**Problema:** Nginx com timeout padrão de 60s. Queries no Neo4j com 40M+ nós demoram mais que isso. Resultado: erro 504 Gateway Timeout na busca do frontend.
**Solução:** Aumentar timeouts para 300s.

**ANTES:**
```nginx
location /api {
    proxy_pass http://api:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

**DEPOIS:**
```nginx
location /api {
    proxy_pass http://api:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
}
```

> ⚠️ **Esta correção é VOLÁTIL** — some toda vez que o container reinicia.
> **Pendente:** incorporar no `frontend/Dockerfile` ou no `docker-compose.yml` para ser permanente.

**Comando para reaplicar após reiniciar containers:**
```bash
docker exec br-acc-novo-frontend-1 sh -c 'echo "server {
    listen 3000;
    root /usr/share/nginx/html;
    index index.html;
    location /assets/ {
        expires 1y;
        add_header Cache-Control \"public, immutable\";
    }
    location / {
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control \"no-cache, no-store, must-revalidate\";
    }
    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
}" > //etc/nginx/conf.d/default.conf && nginx -s reload'
```

---

### Correção 4 — Empresas0.zip corrompido
**Problema:** Arquivo `data/cnpj/Empresas0.zip` baixado com apenas 9.5KB (corrompido). Causava erro `BadZipFile` e interrompia o pipeline.
**Solução:** Arquivo deletado. Pipeline continua com Empresas1-9.zip normalmente.

```bash
rm ~/Downloads/br-acc-novo/data/cnpj/Empresas0.zip
```

---

## ⚠️ PROBLEMAS CONHECIDOS E PENDENTES

### Problema 1 — Fase 1 do pipeline (CRÍTICO — pendente)
**Descrição:** A Fase 1 do `run_streaming` lê todos os `Estabelecimentos*.zip` para montar o `estab_lookup` (dicionário CNPJ → CNAE, UF, município). O processo morre **silenciosamente** ao ler `Estabelecimentos0.zip` (2GB comprimido).
**Sintomas:**
- Processo para sem mensagem de erro
- Log mostra só `Reading Estabelecimentos0.zip...` e para
- Exit code não é registrado
- Zip não está corrompido (testado)
- Memória não é o problema (17GB disponíveis)
**Causa provável:** Incompatibilidade do Python 3.14 com zipfile em arquivos >2GB, ou OOM killer silencioso do Windows
**Impacto:** Campos `uf`, `municipio`, `cnae_principal` ficam **vazios** em todas as empresas
**Workaround atual:** `--start-phase 2` (pula Fase 1)
**Pendente:** Investigar e corrigir. Possíveis abordagens:
- Testar com Python 3.12 (versão mais estável)
- Descomprimir os zips manualmente antes de rodar
- Aumentar limite de memória virtual do Windows

### Problema 2 — Relacionamentos SOCIO_DE incompletos
**Descrição:** Pipeline reportou gravar 53M de `Partner rels` mas Neo4j tem apenas 18M de `SOCIO_DE`.
**Causa:** O `MERGE` do Neo4j falha silenciosamente quando o nó destino não existe no momento da gravação. Como dados são processados em chunks sequenciais, às vezes o relacionamento é processado antes do nó Company existir.
**Impacto:** Grafo de relações mostra poucas conexões
**Pendente:** Rodar pipeline novamente após todos os dados estarem consolidados

### Problema 3 — Nginx timeout volátil
**Descrição:** A correção do timeout nginx some ao reiniciar containers.
**Pendente:** Incorporar no `frontend/Dockerfile`:
```dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### Problema 4 — Usuários perdidos ao reiniciar
**Descrição:** Usuários criados no frontend são perdidos quando containers reiniciam. A API usa banco SQLite em memória ou sem volume persistente.
**Pendente:** Verificar e adicionar volume persistente para o banco da API no `docker-compose.yml`

### Problema 5 — Fontes bloqueadas
- `blocked_external` — portais do governo fora do ar
- `blocked_credentials` — DOU, RAIS, STF, MiDES precisam de `GOOGLE_APPLICATION_CREDENTIALS` no `.env`
- `failed_download` — ComprasNet, DATASUS — scripts não existem na versão pública

---

## 💡 COMANDOS ÚTEIS

```bash
# ═══════════════════════════════════════
# ROTINA DIÁRIA — rodar ao ligar o PC
# ═══════════════════════════════════════
cd ~/Downloads/br-acc-novo && docker compose up -d

# Verificar containers
docker ps

# Reaplicar nginx timeout (necessário após reiniciar)
docker exec br-acc-novo-frontend-1 sh -c 'echo "server {
    listen 3000; root /usr/share/nginx/html; index index.html;
    location /assets/ { expires 1y; add_header Cache-Control \"public, immutable\"; }
    location / { try_files \$uri \$uri/ /index.html; add_header Cache-Control \"no-cache, no-store, must-revalidate\"; }
    location /api { proxy_pass http://api:8000; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr; proxy_read_timeout 300s; proxy_connect_timeout 300s; proxy_send_timeout 300s; }
}" > //etc/nginx/conf.d/default.conf && nginx -s reload'

# Recriar usuário frontend (necessário após reiniciar)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"teste@bracc.com\",\"password\":\"senha123\",\"invite_code\":\"rolim\"}"

# ═══════════════════════════════════════
# PIPELINE CNPJ
# ═══════════════════════════════════════

# Rodar pipeline streaming (pula Fase 1 — recomendado)
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source cnpj --neo4j-password "changeme" \
  --data-dir ../data --streaming --start-phase 2 2>&1 | tee ../pipeline.log

# Rodar apenas Fase 3 (sócios)
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source cnpj --neo4j-password "changeme" \
  --data-dir ../data --streaming --start-phase 3 2>&1 | tee ../pipeline.log

# Rodar pipeline completo (com Fase 1 — pode travar)
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source cnpj --neo4j-password "changeme" \
  --data-dir ../data --streaming 2>&1 | tee ../pipeline.log

# Monitorar log em tempo real
tail -f ~/Downloads/br-acc-novo/pipeline.log

# ═══════════════════════════════════════
# NEO4J
# ═══════════════════════════════════════

# Ver totais de dados
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Ver relacionamentos
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH ()-[r]->() RETURN type(r) as tipo, count(r) as total ORDER BY total DESC"

# Buscar empresas do AM (quando Fase 1 estiver resolvida)
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (c:Company) WHERE c.uf = 'AM' RETURN c.cnpj, c.razao_social LIMIT 10"

# ═══════════════════════════════════════
# DIAGNÓSTICO
# ═══════════════════════════════════════

# Ver uso de memória dos containers
docker stats --no-stream

# Ver logs da API
docker logs br-acc-novo-api-1 --tail=20

# Ver logs do Neo4j
docker logs bracc-neo4j --tail=20

# Testar se API responde
curl http://localhost:8000/health

# Testar busca via API (sem autenticação)
curl "http://localhost:8000/api/v1/search?q=banco+do+brasil"

# uv não está no PATH? Rodar antes:
source ~/.local/bin/env
```

---

## 🏗️ Arquitetura Planejada

```
FONTES DE DADOS PÚBLICOS
  │
  ├── CNPJ / Receita Federal ✅ (carregado)
  ├── Portal Transparência Federal ⏳
  ├── IBAMA ⏳
  ├── TSE (dados eleitorais) ⏳
  ├── PGFN (devedores) ⏳
  ├── TCE-AM ⏳ (não está no br-acc)
  └── Transparência AM ⏳ (não está no br-acc)
         ↓
    br-acc ETL pipelines
         ↓
  ┌──────────────────────────────────┐
  │  Neo4j (grafos de relações)      │ ✅ funcionando
  │  PostgreSQL (dados estruturados) │ ⏳ pendente
  └──────────────────────────────────┘
         ↓
  ┌──────────────────────────────────┐
  │  BR-ACC Frontend (busca/grafos)  │ ✅ funcionando
  │  Metabase (dashboards/mapas)     │ ⏳ pendente
  └──────────────────────────────────┘
         ↓
  Painel Político do Amazonas
  • Mapa interativo 62 municípios
  • Indicadores por área
  • Registro de problemas
  • Acompanhamento de ações
```

---

## 📋 FASES DO PROJETO

| Fase | Descrição | Status |
|---|---|---|
| 1 | Infraestrutura instalada (Docker, Neo4j, API, Frontend) | ✅ Concluída |
| 2 | Download dos dados CNPJ (~28GB) | ✅ Concluída |
| 3 | Pipeline ETL — Empresas e Sócios no Neo4j | ✅ Parcial (sem UF/município) |
| 4 | Frontend funcionando com busca e grafo | ✅ Concluída |
| 5 | Corrigir Fase 1 (estab_lookup — UF/município/CNAE) | 🔄 Pendente |
| 6 | Corrigir relacionamentos SOCIO_DE incompletos | 🔄 Pendente |
| 7 | Gerar patch de correções + testar em instalação limpa | 🔄 Pendente |
| 8 | Tornar correções nginx/usuários permanentes | 🔄 Pendente |
| 9 | PostgreSQL + tabelas AM (municípios, problemas, indicadores) | ⏳ Não iniciada |
| 10 | Metabase + dashboards | ⏳ Não iniciada |
| 11 | Mapa interativo dos 62 municípios do AM | ⏳ Não iniciada |
| 12 | Outros pipelines br-acc (TSE, IBAMA, Transparência) | ⏳ Não iniciada |

---

## 🔬 PRÓXIMA AÇÃO — Patch de Correções

Alberto propôs a ideia (excelente!) de:
1. Clonar o repositório original limpo
2. Comparar com a versão corrigida usando `git diff`
3. Gerar arquivo `.patch` com todas as correções
4. Testar aplicando em nova instalação
5. Gerar log das alterações para contribuir ao projeto

```bash
# Gerar patch de todas as correções
cd ~/Downloads/br-acc-novo
git diff > correcoes_bracc_2026.patch

# Ver resumo das alterações
git diff --stat
```

---

## 🗃️ Fontes para o Amazonas

### No br-acc (federais)
| Fonte | Status | Observação |
|---|---|---|
| CNPJ | ✅ Carregado | Sem UF/município (Fase 1 pendente) |
| Portal Transparência | ⏳ | Servidor fora do ar |
| IBAMA | ⏳ | Servidor fora do ar |
| TSE | ⏳ | Servidor fora do ar |
| PGFN | ⏳ | Servidor fora do ar |
| DOU/RAIS/STF/MiDES | ⏳ | Precisam de Google Credentials |
| ComprasNet/DATASUS | ❌ | Scripts não existem na versão pública |

### Específicas do AM (não estão no br-acc)
| Fonte | URL | Status |
|---|---|---|
| TCE-AM | https://www.tce.am.gov.br/ | Listado como `not_built` no br-acc |
| Transparência AM | https://www.transparencia.am.gov.br/ | Não listado no br-acc |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] docker compose up -d
[ ] docker ps (confirmar 3 containers rodando)
[ ] Reaplicar nginx timeout
[ ] Recriar usuário frontend se necessário
[ ] Verificar dados no Neo4j
```

---

*Documento master gerado em 24/04/2026 — versão 5*
*Consolida: v1 (20/04), v2 (22/04), v3 (22/04 noite), v4 (24/04)*
