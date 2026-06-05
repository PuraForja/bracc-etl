# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v6
> Gerado em 26/04/2026 — consolida todas as versões anteriores (v1 a v5) + patch completo
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
7. **REGRA NOVA:** Sempre propor testes rápidos (amostras pequenas) ANTES de rodar pipelines longos — nunca rodar 10h+ sem validar primeiro
8. **REGRA NOVA:** Sempre agrupar múltiplos comandos bash em um único bloco para o usuário copiar de uma vez

---

## 🎭 COMO O CLAUDE DEVE OPERAR

### Modo Arquiteto (Execução)
- Definir arquitetura de sistemas
- Sugerir tecnologias (banco de dados, APIs, ferramentas BI)
- Criar estruturas prontas (modelos de banco, fluxos de dados, dashboards)

### Modo Professor (Didático)
- Explicar passo a passo de forma clara
- Ensinar como implementar cada parte
- Permitir evolução para nível avançado

### Estrutura das respostas
1. Contexto e objetivo
2. Arquitetura da solução
3. Como coletar os dados
4. Estrutura do banco de dados
5. Como implementar (passo a passo)
6. Dashboards sugeridos
7. Gestão de problemas aplicada
8. Possíveis evoluções

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
| bracc-neo4j | 7474/7687 | ✅ | Neo4j 5-community com APOC |
| br-acc-novo-api-1 | 8000 | ✅ | API FastAPI do br-acc |
| br-acc-novo-frontend-1 | 3000 | ✅ | Frontend React/Nginx |

> ⚠️ **Containers não sobem automaticamente.** Sempre rodar ao ligar o PC:
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

## ✅ STATUS ATUAL DOS DADOS (26/04/2026)

### Neo4j — dados carregados
| Tipo | Quantidade | Status |
|---|---|---|
| Company (empresas) | 40.453.740 | ✅ Completo — CNPJs corretos! |
| Partner (sócios c/ CPF mascarado) | 17.774.658 | ✅ Carregado |
| SOCIO_DE (relacionamentos) | 18.783.607 | ⚠️ Incompleto (pipeline reportou 26.8M) |
| Person (CPF válido) | 0 | ⚠️ RF mascara maioria dos CPFs |
| UF / Município / CNAE | ✅ | Populados corretamente após fix Fase 1 |

### Confirmação de qualidade dos dados
```cypher
// CNPJ correto confirmado:
MATCH (c:Company {cnpj: '05.726.562/0001-30'}) RETURN c
// Retorna: INSTITUTO TIBAGI, uf: PR, municipio: 7535 ✅

// Companies com CNPJ no formato fallback:
MATCH (c:Company) WHERE c.cnpj ENDS WITH '0001-00' RETURN count(c)
// Retorna: 1.317.756 (só 3% — eram 100% antes do fix!)
```

### Frontend — funcionando
- ✅ Login: `http://localhost:3000`
- ✅ Busca por nome/CNPJ funcionando
- ✅ Grafo de relações carregando
- ⚠️ Grafo mostra poucas conexões (SOCIO_DE incompletos)

### Backup do banco
```
Arquivo: neo4j-backup-20260426.tar.gz
Local:   C:\Users\Rolim\Downloads\
Tamanho: 9.4GB (36GB descompactado)
Data:    26/04/2026 21:08
```

### Restaurar backup (no PowerShell):
```powershell
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar xzf /backup/neo4j-backup-20260426.tar.gz -C /
```

### Dados de arquivo no HD
```
C:\Users\Rolim\Downloads\br-acc-novo\data\cnpj\
├── K3241...EMPRE    (10 arquivos RF originais extraídos) ✅
├── K3241...ESTABELE (10 arquivos RF originais extraídos) ✅
├── K3241...SOCIOCSV (10 arquivos RF originais extraídos) ✅
├── Empresas1-9.zip       (~75-95MB cada) ✅
├── Estabelecimentos0-9.zip (~320MB-2GB cada) ✅
├── Socios0-9.zip         (~217-329MB cada) ✅
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
**Problema:** O parâmetro `--start-phase` era ignorado na Fase 1.

```python
# ANTES (com bug):
if use_bq:
    logger.info("Phase 1: Building estab_lookup...")

# DEPOIS (corrigido):
if start_phase > 1:
    logger.info("Skipping Phase 1 -- start_phase=%d", start_phase)
elif use_bq:
    logger.info("Phase 1: Building estab_lookup...")
```

---

### Correção 3 — Filtro de arquivos ZIP ✅ NOVA (26/04/2026) — CAUSA RAIZ
**Arquivo:** `etl/src/bracc_etl/pipelines/cnpj.py` (3 lugares)
**Problema:** `_find_rf_files` retornava arquivos `.zip` misturados com arquivos extraídos. Como `E` vem antes de `K` na ordenação alfabética, os `Estabelecimentos*.zip` eram encontrados antes dos `K3241...ESTABELE`. O código tentava ler ZIPs como CSV puro — travava silenciosamente. Resultado: `estab_lookup` vazio → CNPJs todos gerados como `basico + 000100` (fallback) → **100% das 40M Companies com CNPJs falsos** → todos os `MATCH (Company)` falhavam → zero `SOCIO_DE` criados corretamente.

```python
# ANTES (com bug):
files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
if not files:
    files = sorted(cnpj_dir.glob(pattern))

# DEPOIS (corrigido):
files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
if not files:
    files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
```

**Como aplicar manualmente:**
```bash
cd ~/Downloads/br-acc-novo && sed -i 's/files = sorted(cnpj_dir.glob(f"extracted\/{pattern}"))/files = [f for f in sorted(cnpj_dir.glob(f"extracted\/{pattern}")) if f.suffix != ".zip"]/' etl/src/bracc_etl/pipelines/cnpj.py && sed -i 's/files = sorted(cnpj_dir.glob(pattern))/files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]/' etl/src/bracc_etl/pipelines/cnpj.py
```

---

### Correção 4 — Empresas0.zip corrompido
**Arquivo:** `data/cnpj/Empresas0.zip`
**Problema:** Arquivo baixado com apenas 9.5KB (corrompido). Causava erro `BadZipFile` e interrompia o pipeline.
**Solução:** Arquivo deletado. Pipeline continua com Empresas1-9.zip normalmente.

```bash
rm ~/Downloads/br-acc-novo/data/cnpj/Empresas0.zip
```

---

### Correção 5 — Nginx timeout
**Arquivo:** `/etc/nginx/conf.d/default.conf` dentro do container `br-acc-novo-frontend-1`
**Problema:** Nginx com timeout padrão de 60s. Queries no Neo4j com 40M+ nós demoram mais. Resultado: erro 504 Gateway Timeout.
**Solução:** Aumentar timeouts para 300s.

> ⚠️ **Esta correção é VOLÁTIL** — some toda vez que o container reinicia. Reaplicar com o comando na seção de comandos úteis.
> **Pendente:** incorporar no `frontend/Dockerfile` para ser permanente.

---

## 📄 PATCH COMPLETO (correcoes_bracc_2026.patch)

```diff
diff --git a/etl/src/bracc_etl/pipelines/cnpj.py b/etl/src/bracc_etl/pipelines/cnpj.py
index ce9d3e9..5f4285d 100644
--- a/etl/src/bracc_etl/pipelines/cnpj.py
+++ b/etl/src/bracc_etl/pipelines/cnpj.py
@@ -290,7 +290,7 @@ class CNPJPipeline(Pipeline):
         renames columns to match the RF schema used by transform().
         """
         cnpj_dir = Path(self.data_dir) / "cnpj"
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
         if not files:
             return pd.DataFrame()
 
@@ -322,9 +322,9 @@ class CNPJPipeline(Pipeline):
         """Read Receita Federal headerless CSVs with chunking for memory efficiency."""
         cnpj_dir = Path(self.data_dir) / "cnpj"
         # Search both extracted/ subdirectory and cnpj/ root
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
         if not files:
-            files = sorted(cnpj_dir.glob(pattern))
+            files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
         if not files:
             return pd.DataFrame(columns=columns)
 
@@ -1025,9 +1025,9 @@ class CNPJPipeline(Pipeline):
     def _find_rf_files(self, pattern: str) -> list[Path]:
         """Find RF-format data files, checking extracted/ then cnpj/ root."""
         cnpj_dir = Path(self.data_dir) / "cnpj"
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
         if not files:
-            files = sorted(cnpj_dir.glob(pattern))
+            files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
         return files
 
     def _find_bq_files(self, pattern: str) -> list[Path]:
@@ -1105,7 +1105,9 @@ class CNPJPipeline(Pipeline):
             bq_estab = bq_emp = bq_socio = []
 
         # Phase 1: Build estab_lookup
-        if use_bq:
+        if start_phase > 1:
+            logger.info("Skipping Phase 1 -- start_phase=%d", start_phase)
+        elif use_bq:
             logger.info("Phase 1: Building estab_lookup from %d BQ files", len(bq_estab))
             for f in bq_estab:
                 logger.info("  Reading %s...", f.name)
diff --git a/etl/src/bracc_etl/runner.py b/etl/src/bracc_etl/runner.py
index 86a2195..38b3f77 100644
--- a/etl/src/bracc_etl/runner.py
+++ b/etl/src/bracc_etl/runner.py
@@ -227,6 +227,22 @@ def _resolve_rf_release_inline(year_month: str | None = None) -> str:
         except httpx.HTTPError:
             pass
 
+    # --- Mirror Casa dos Dados (adicionada 2026) ---
+    casadosdados_base = "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/2026-04-12/"
+    try:
+        resp = httpx.head(casadosdados_base, follow_redirects=True, timeout=30)
+        if resp.status_code < 400:
+            return casadosdados_base
+    except httpx.HTTPError:
+        pass
+    # --- Nova URL dados.gov.br (adicionada 2026) ---
+    dados_gov_base = "https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj"
+    try:
+        resp = httpx.head(dados_gov_base, follow_redirects=True, timeout=30)
+        if resp.status_code < 400:
+            return dados_gov_base
+    except httpx.HTTPError:
+        pass
     # --- Legacy dadosabertos (fallback) ---
     new_base = "https://dadosabertos.rfb.gov.br/CNPJ/dados_abertos_cnpj/{ym}/"
     legacy_url = "https://dadosabertos.rfb.gov.br/CNPJ/"
```

**Como aplicar o patch em instalação nova:**
```bash
cd ~/Downloads/br-acc-novo && git apply ~/Downloads/correcoes_bracc_2026.patch
```

---

## ⚠️ PROBLEMAS CONHECIDOS E PENDENTES

### Problema 1 — SOCIO_DE incompletos
**Descrição:** Pipeline reportou gravar 26.8M de `Partner rels` mas Neo4j tem apenas 18.7M de `SOCIO_DE`.
**Causa provável:** Scripts de pós-carga ausentes. O pipeline loga WARNING ao final:
```
WARNING Post-load linking script missing (skipped): scripts\link_partners_probable.cypher
WARNING Post-load linking script missing (skipped): scripts\link_persons.cypher
```
**Status:** ⚠️ Próxima prioridade — esses scripts não existem no repositório público do br-acc.

### Problema 2 — 1.3M Companies com CNPJ no formato fallback
**Descrição:** Após correção da Fase 1, ainda existem 1.317.756 companies com CNPJ terminando em `0001-00`.
**Causa provável:** Empresas que genuinamente têm esse formato, ou estabelecimentos não encontrados no estab_lookup.
**Status:** ⚠️ Baixa prioridade — pode ser dado legítimo.

### Problema 3 — Nginx timeout volátil
**Descrição:** A correção do timeout nginx some ao reiniciar containers.
**Pendente:** Incorporar no `frontend/Dockerfile`:
```dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### Problema 4 — Usuários perdidos ao reiniciar
**Descrição:** Usuários do frontend são perdidos quando containers reiniciam.
**Pendente:** Adicionar volume persistente no `docker-compose.yml`.

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

# Rodar pipeline completo (recomendado — com Fase 1 corrigida)
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source cnpj --neo4j-password "changeme" \
  --data-dir ../data --streaming 2>&1 | tee ../pipeline.log && \
  echo "✅ Pipeline finalizado em: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a ../pipeline.log

# Rodar apenas Fase 3 (sócios) — se Fase 1 e 2 já concluídas e Companies no banco
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source cnpj --neo4j-password "changeme" \
  --data-dir ../data --streaming --start-phase 3 2>&1 | tee ../pipeline.log && \
  echo "✅ Pipeline finalizado em: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a ../pipeline.log

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

# Buscar empresas do AM
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (c:Company) WHERE c.uf = 'AM' RETURN c.cnpj, c.razao_social, c.municipio LIMIT 10"

# Verificar qualidade dos CNPJs
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (c:Company) WHERE c.cnpj ENDS WITH '0001-00' RETURN count(c)"

# ═══════════════════════════════════════
# BACKUP DO NEO4J — rodar no PowerShell
# ═══════════════════════════════════════

# Criar backup:
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-YYYYMMDD.tar.gz /data

# Restaurar backup:
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar xzf /backup/neo4j-backup-20260426.tar.gz -C /

# ═══════════════════════════════════════
# LIMPAR BANCO E RECOMEÇAR DO ZERO
# ═══════════════════════════════════════
# docker stop bracc-neo4j && docker rm bracc-neo4j && docker volume rm br-acc-novo_neo4j-data
# cd ~/Downloads/br-acc-novo && docker compose up -d neo4j
# Confirmar vazio: docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN count(n)"

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

# Testar busca via API
curl "http://localhost:8000/api/v1/search?q=banco+do+brasil"

# uv não está no PATH? Rodar antes:
source ~/.local/bin/env
```

---

## 🏗️ Arquitetura Planejada

```
FONTES DE DADOS PÚBLICOS
  │
  ├── CNPJ / Receita Federal ✅ (carregado — CNPJs corretos)
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
| 3 | Pipeline ETL — Empresas e Sócios no Neo4j | ✅ Concluída (CNPJs corretos!) |
| 4 | Frontend funcionando com busca e grafo | ✅ Concluída |
| 5 | Corrigir Fase 1 (estab_lookup — UF/município/CNAE) | ✅ Concluída (26/04/2026) |
| 6 | Corrigir relacionamentos SOCIO_DE incompletos | 🔄 Parcial (18.7M de 26.8M esperados) |
| 7 | Investigar scripts link_partners_probable.cypher e link_persons.cypher | 🔄 Próxima prioridade |
| 8 | Tornar correções nginx/usuários permanentes | 🔄 Pendente |
| 9 | Gerar patch de correções + testar em instalação limpa | 🔄 Patch gerado, teste pendente |
| 10 | PostgreSQL + tabelas AM (municípios, problemas, indicadores) | ⏳ Não iniciada |
| 11 | Metabase + dashboards | ⏳ Não iniciada |
| 12 | Mapa interativo dos 62 municípios do AM | ⏳ Não iniciada |
| 13 | Outros pipelines br-acc (TSE, IBAMA, Transparência) | ⏳ Não iniciada |

---

## 🔬 PRÓXIMA AÇÃO — Investigar SOCIO_DE incompletos

Pipeline reportou 26.8M de `Partner rels` mas Neo4j tem só 18.7M de `SOCIO_DE`.

Os scripts de pós-carga que criariam os relacionamentos faltantes não existem no repositório público:
```
scripts/link_partners_probable.cypher  ← NÃO EXISTE
scripts/link_persons.cypher            ← NÃO EXISTE
```

**Opções a investigar:**
1. Escrever os scripts `.cypher` manualmente baseado na estrutura dos dados
2. Entender por que o `MERGE` do Neo4j está falhando para ~8M de registros
3. Verificar índices no Neo4j

---

## 🗃️ Fontes para o Amazonas

### No br-acc (federais)
| Fonte | Status | Observação |
|---|---|---|
| CNPJ | ✅ Carregado | CNPJs corretos, UF/município populados |
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

## 📅 HISTÓRICO DE SESSÕES

| Data | O que foi feito |
|---|---|
| 20/04 | Infraestrutura instalada, Docker, Neo4j, Metabase, PostgreSQL |
| 21/04 | Investigação URLs Receita Federal — mirror Casa dos Dados adicionado |
| 22/04 | Download dos dados CNPJ (~28GB) concluído |
| 22/04 noite | Pipeline ETL primeira tentativa — Fases 2 e 3 com --start-phase 2 |
| 24/04 | Correções URLs + start_phase — v5 gerado |
| 25/04 | Descoberta causa raiz (filtro ZIP) + correção — patch gerado |
| 26/04 | Pipeline completo concluído (~20h30) com dados corretos + backup 9.4GB |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (confirmar 3 containers rodando)
[ ] Reaplicar nginx timeout
[ ] Recriar usuário frontend se necessário
[ ] Verificar dados no Neo4j
```

---

*Documento master gerado em 26/04/2026 — versão 6*
*Consolida: v1 (20/04), v2 (22/04), v3 (22/04 noite), v4 (24/04), v5 (24/04)*
*Inclui patch completo correcoes_bracc_2026.patch*
