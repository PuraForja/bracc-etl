# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v7
> Gerado em 27/04/2026 — consolida v6 + sessões de 26/04 (noite) e 27/04
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
7. **REGRA:** Sempre propor testes rápidos (amostras pequenas) ANTES de rodar pipelines longos
8. **REGRA:** Sempre agrupar múltiplos comandos bash em um único bloco para copiar de uma vez
9. **REGRA:** Nunca rodar download e importação separadamente — baixar tudo primeiro, depois importar tudo

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
| etl | — | profile "etl" | Container ETL — sobe só quando necessário |

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

---

## ✅ STATUS ATUAL DOS DADOS (27/04/2026)

### Neo4j — dados carregados
| Tipo | Quantidade | Status |
|---|---|---|
| Company (empresas) | 40.453.740 | ✅ CNPJs corretos |
| Partner (sócios CPF mascarado) | 17.774.658 | ✅ |
| SOCIO_DE (relacionamentos) | 18.783.607 | ⚠️ Incompleto (esperado 26.8M) |
| TSE candidatos 2024 | 927.616 | ✅ Baixado e sendo importado |
| TSE doações 2024 | 5.149.602 | ✅ Baixado |
| UF / Município / CNAE | ✅ | Populados corretamente |

### Confirmação de qualidade — CNPJ
```cypher
MATCH (c:Company {cnpj: '05.726.562/0001-30'}) RETURN c
// Retorna: INSTITUTO TIBAGI, uf: PR, municipio: 7535 ✅

MATCH (c:Company) WHERE c.cnpj ENDS WITH '0001-00' RETURN count(c)
// Retorna: 1.317.756 (só 3% — eram 100% antes do fix!)
```

### Caso de uso validado — Adail José Figueiredo Pinheiro
```
CPF: 772.677.962-49
Partner ID: 1eeb9bfb2fa9c3af
Doc mascarado: ***677962**

Empresas no AM:
  - DAFIL PARTICIPACOES LTDA (29.025.187/0001-60) — CNAE 6463800 (holding) — cap. R$150k
  - VIEIRALVES EMPREENDIMENTOS LTDA (19.362.619/0001-74) — CNAE 6810201 (imóveis) — cap. R$180k

Estrutura: ADAIL → DAFIL (holding) → VIEIRALVES (imóveis)
           ADAIL → VIEIRALVES (diretamente, desde 12/05/2023)
Candidato a prefeito: 2016 (CNPJ 25.594.636/0001-30) e 2020 (39.217.920/0001-00)
Município: Itacoatiara (código 0225)
Padrão: blindagem patrimonial via holding em ME
```

### Arquivos baixados no HD
```
data/cnpj/     ✅ 40M empresas (K3241...ESTABELE, EMPRE, SOCIOCSV)
data/tse/      ✅ candidatos.csv (927k) + doacoes.csv (5.1M) — 2024
```

### Backup do banco
```
Arquivo: neo4j-backup-20260426.tar.gz
Local:   C:\Users\Rolim\Downloads\
Tamanho: 9.4GB (36GB descompactado)
Data:    26/04/2026 21:08
```

---

## 🔧 CORREÇÕES APLICADAS NO CÓDIGO

### Correção 1 — URLs de download (runner.py)
Mirror Casa dos Dados adicionado como fallback:
```python
casadosdados_base = "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/2026-04-12/"
```

### Correção 2 — Bug start_phase Fase 1 (cnpj.py)
```python
if start_phase > 1:
    logger.info("Skipping Phase 1 -- start_phase=%d", start_phase)
elif use_bq:
```

### Correção 3 — Filtro ZIP — CAUSA RAIZ (cnpj.py) ✅
```python
# ANTES: files = sorted(cnpj_dir.glob(pattern))
# DEPOIS:
files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
```

### Correção 4 — Empresas0.zip corrompido
```bash
rm ~/Downloads/br-acc-novo/data/cnpj/Empresas0.zip
```

### Correção 5 — Nginx timeout (volátil — some ao reiniciar)
Aumentar timeouts para 300s. Reaplicar com o comando na seção de comandos úteis.
**Pendente:** incorporar no `frontend/Dockerfile`.

### Correção 6 — bootstrap_all_contract.yml ✅ NOVA (27/04/2026)
**Problema:** Quase todas as fontes tinham `"acquisition_mode": "file_manifest"` — o bootstrap ficava esperando os arquivos já existirem sem baixar nada.
**Solução:** 28 fontes atualizadas para `"acquisition_mode": "script_download"` com `download_commands` corretos.
**Arquivo:** `config/bootstrap_all_contract.yml`
**Como aplicar:**
```bash
cp ~/Downloads/bootstrap_all_contract.yml ~/Downloads/br-acc-novo/config/bootstrap_all_contract.yml
```

### Correção 7 — venv corrompido (lib64) ✅ NOVA (27/04/2026)
**Problema:** Symlink `lib64` corrompido no Windows causava erro `Acesso negado` ao rodar `uv run`.
**Solução:** Deletar o `.venv` via PowerShell Admin e recriar:
```powershell
# PowerShell como Administrador:
Remove-Item -Recurse -Force "C:\Users\Rolim\Downloads\br-acc-novo\etl\.venv"
```
```bash
# Git Bash:
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && uv sync
```

---

## 📄 PATCH COMPLETO (correcoes_bracc_2026.patch)

```diff
diff --git a/etl/src/bracc_etl/pipelines/cnpj.py b/etl/src/bracc_etl/pipelines/cnpj.py
index ce9d3e9..5f4285d 100644
--- a/etl/src/bracc_etl/pipelines/cnpj.py
+++ b/etl/src/bracc_etl/pipelines/cnpj.py
@@ -290,7 +290,7 @@ class CNPJPipeline(Pipeline):
         cnpj_dir = Path(self.data_dir) / "cnpj"
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
         if not files:
             return pd.DataFrame()
@@ -322,9 +322,9 @@ class CNPJPipeline(Pipeline):
         cnpj_dir = Path(self.data_dir) / "cnpj"
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
         if not files:
-            files = sorted(cnpj_dir.glob(pattern))
+            files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
@@ -1025,9 +1025,9 @@ class CNPJPipeline(Pipeline):
     def _find_rf_files(self, pattern: str) -> list[Path]:
         cnpj_dir = Path(self.data_dir) / "cnpj"
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
         if not files:
-            files = sorted(cnpj_dir.glob(pattern))
+            files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
@@ -1105,7 +1105,9 @@ class CNPJPipeline(Pipeline):
-        if use_bq:
+        if start_phase > 1:
+            logger.info("Skipping Phase 1 -- start_phase=%d", start_phase)
+        elif use_bq:
diff --git a/etl/src/bracc_etl/runner.py b/etl/src/bracc_etl/runner.py
index 86a2195..38b3f77 100644
--- a/etl/src/bracc_etl/runner.py
+++ b/etl/src/bracc_etl/runner.py
@@ -227,6 +227,22 @@ def _resolve_rf_release_inline(year_month: str | None = None) -> str:
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
```

---

## 🔍 DESCOBERTAS IMPORTANTES

### API funciona via element_id
```bash
# Buscar entidade pelo CNPJ sem formatação (funciona ✅)
curl "http://localhost:8000/api/v1/entity/29025187000160"

# Buscar pelo element_id (funciona ✅)
curl "http://localhost:8000/api/v1/entity/by-element-id/4:91a9add5-04eb-4574-a38d-fd9437d62144:47052943"

# Ver conexões (funciona ✅)
curl "http://localhost:8000/api/v1/entity/4:...:28475404/connections"

# Ver grafo (só funciona com Company, não Partner ⚠️)
curl "http://localhost:8000/api/v1/graph/4:...:28475404"
```

### Bug do frontend identificado
- Busca por CPF no frontend não funciona — RF mascara CPFs, banco não tem CPF completo
- Busca por nome funciona mas grafo não renderiza — frontend usa element_id do Partner mas `/graph` só aceita Company
- **Workaround:** buscar pelo CNPJ da empresa sem formatação (29025187000160)
- **Fix pendente:** frontend deve abrir grafo pelo CNPJ da empresa quando buscar pessoa

### 47 pipelines disponíveis no br-acc
```
✅ Baixados automaticamente (script_download): 28 fontes
⚠️  Precisam Google credentials: tse_bens, tse_filiados, dou, rais, stf, mides, caged, datajud
⚠️  Sem script de download: pgfn, tcu, ibama, bndes, inep, datasus, transferegov
```

### Status dos servidores (27/04/2026)
```
✅ Online:  tse, ibama, camara, senado, ceaf, cepim, cpgf, leniency, viagens,
            tesouro_emendas, renuncias, siconfi, bndes, bcb, tcu, querido_diario,
            comprasnet, sanctions, pncp, cvm, stj, datasus, holdings, caged,
            eu_sanctions, icij, world_bank, rais
❌ Offline: pep_cgu, datajud, inep, transferegov, mides, ofac
```

### sanctions — 403 Forbidden
O script `download_sanctions.py` recebe 403 ao baixar do Portal da Transparência — servidor bloqueando downloads automatizados. Possível solução: adicionar User-Agent de browser no header.

---

## 🆕 NOVOS ARQUIVOS GERADOS

| Arquivo | Local | Descrição |
|---|---|---|
| bootstrap_all_contract.yml | Downloads/ | Contrato corrigido com 28 fontes usando script_download |
| bracc_run.sh | scripts/ | Script completo de download + importação |
| correcoes_bracc_2026.patch | Downloads/ | Patch com todas as correções de código |
| neo4j-backup-20260426.tar.gz | Downloads/ | Backup completo do banco (9.4GB) |

### Como usar o bracc_run.sh
```bash
# Baixar tudo e importar tudo:
bash scripts/bracc_run.sh

# Só baixar:
bash scripts/bracc_run.sh --only-download

# Só importar:
bash scripts/bracc_run.sh --only-import

# Fonte específica:
bash scripts/bracc_run.sh --sources tse,sanctions
```

---

## ⚠️ PROBLEMAS CONHECIDOS E PENDENTES

### Problema 1 — SOCIO_DE incompletos
Pipeline reportou 26.8M mas Neo4j tem 18.7M. Scripts faltantes:
```
scripts/link_partners_probable.cypher  ← NÃO EXISTE
scripts/link_persons.cypher            ← NÃO EXISTE
```
**Status:** ⚠️ Pendente investigação

### Problema 2 — Bug frontend grafo vazio
`/api/v1/graph/{id}` só aceita Company, não Partner. Quando busca pessoa, frontend usa element_id do Partner e recebe "Entity not found".
**Fix:** frontend deve usar CNPJ da empresa para abrir o grafo.
**Status:** ⚠️ Pendente correção no frontend

### Problema 3 — sanctions 403 Forbidden
Portal da Transparência bloqueando downloads automáticos do CEIS/CNEP.
**Fix:** adicionar User-Agent de browser no `download_sanctions.py`.
**Status:** ⚠️ Pendente

### Problema 4 — bootstrap wait_for_api
`run_bootstrap_all.py` usa `localhost:8000` mas dentro do container Docker isso não resolve para o host.
**Fix:** adicionar parâmetro `--api-url` ao script.
**Status:** ⚠️ Pendente — usando `bracc_run.sh` como alternativa

### Problema 5 — Nginx timeout volátil
Some ao reiniciar containers. Pendente incorporar no Dockerfile.

### Problema 6 — Usuários perdidos ao reiniciar
Pendente volume persistente no docker-compose.yml.

### Problema 7 — Fontes sem script de download
pgfn, tcu, ibama, bndes, inep, datasus, transferegov não têm scripts no repositório público.

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

# Recriar usuário frontend
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"teste@bracc.com\",\"password\":\"senha123\",\"invite_code\":\"rolim\"}"

# ═══════════════════════════════════════
# DOWNLOAD + IMPORTAÇÃO
# ═══════════════════════════════════════

# Script completo (recomendado):
cd ~/Downloads/br-acc-novo && bash scripts/bracc_run.sh

# Download individual:
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_tse.py --output-dir ../data/tse \
  --years 2018 2020 2022 2024 --skip-existing

# Importação individual:
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source tse --neo4j-password "changeme" \
  --data-dir ../data 2>&1 | tee ../pipeline_tse.log && \
  echo "✅ Finalizado em: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a ../pipeline_tse.log

# Pipeline CNPJ completo (20h):
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source cnpj --neo4j-password "changeme" \
  --data-dir ../data --streaming 2>&1 | tee ../pipeline.log && \
  echo "✅ Pipeline finalizado em: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a ../pipeline.log

# ═══════════════════════════════════════
# NEO4J — CONSULTAS ÚTEIS
# ═══════════════════════════════════════

# Totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Relacionamentos
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH ()-[r]->() RETURN type(r) as tipo, count(r) as total ORDER BY total DESC"

# Buscar empresa no AM
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (c:Company) WHERE c.uf = 'AM' RETURN c.cnpj, c.razao_social, c.municipio LIMIT 10"

# Buscar pessoa por nome
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (p:Partner) WHERE p.name =~ '(?i).*NOME.*' RETURN p.name, p.doc_raw, p.partner_id"

# Ver empresas de uma pessoa
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (p:Partner {partner_id: 'ID_AQUI'})-[:SOCIO_DE]->(c:Company) RETURN c.cnpj, c.razao_social, c.uf"

# ═══════════════════════════════════════
# BACKUP — rodar no PowerShell
# ═══════════════════════════════════════

# Criar:
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-YYYYMMDD.tar.gz /data

# Restaurar:
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar xzf /backup/neo4j-backup-20260426.tar.gz -C /

# ═══════════════════════════════════════
# LIMPAR BANCO E RECOMEÇAR DO ZERO
# ═══════════════════════════════════════
# docker stop bracc-neo4j && docker rm bracc-neo4j && docker volume rm br-acc-novo_neo4j-data
# cd ~/Downloads/br-acc-novo && docker compose up -d neo4j

# ═══════════════════════════════════════
# DIAGNÓSTICO
# ═══════════════════════════════════════
docker stats --no-stream
docker logs br-acc-novo-api-1 --tail=20
curl http://localhost:8000/health
source ~/.local/bin/env  # se uv não estiver no PATH
```

---

## 📋 FASES DO PROJETO

| Fase | Descrição | Status |
|---|---|---|
| 1 | Infraestrutura instalada | ✅ Concluída |
| 2 | Download CNPJ (~28GB) | ✅ Concluída |
| 3 | Pipeline ETL CNPJ — Empresas e Sócios | ✅ Concluída (CNPJs corretos!) |
| 4 | Frontend funcionando com busca e grafo | ✅ Parcial (bug no grafo de pessoas) |
| 5 | Corrigir Fase 1 (estab_lookup — UF/município/CNAE) | ✅ Concluída (26/04/2026) |
| 6 | Corrigir bootstrap para baixar fontes automaticamente | ✅ Concluída (27/04/2026) |
| 7 | Download e importação TSE 2024 | 🔄 Em andamento |
| 8 | Download e importação demais fontes | 🔄 Próxima prioridade |
| 9 | Corrigir bug frontend (grafo vazio para pessoas) | 🔄 Pendente |
| 10 | Corrigir SOCIO_DE incompletos (scripts .cypher) | 🔄 Pendente |
| 11 | Tornar nginx/usuários permanentes | 🔄 Pendente |
| 12 | Corrigir bootstrap wait_for_api | 🔄 Pendente |
| 13 | PostgreSQL + tabelas AM | ⏳ Não iniciada |
| 14 | Metabase + dashboards | ⏳ Não iniciada |
| 15 | Mapa interativo 62 municípios AM | ⏳ Não iniciada |

---

## 🔬 PRÓXIMA AÇÃO

1. Verificar se importação do TSE concluiu:
```bash
tail -10 ~/Downloads/br-acc-novo/pipeline_tse.log
```

2. Confirmar dados no Neo4j:
```bash
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"
```

3. Rodar `bracc_run.sh` para baixar e importar todas as demais fontes disponíveis.

---

## 📅 HISTÓRICO DE SESSÕES

| Data | O que foi feito |
|---|---|
| 20/04 | Infraestrutura instalada, Docker, Neo4j, Metabase |
| 21/04 | Mirror Casa dos Dados adicionado — download CNPJ iniciado |
| 22/04 | Download CNPJ concluído (~28GB) |
| 22/04 noite | Pipeline ETL primeira tentativa com --start-phase 2 |
| 24/04 | Correções URLs + start_phase — v5 gerado |
| 25/04 | Causa raiz encontrada (filtro ZIP) + correção + patch gerado |
| 26/04 manhã | Pipeline completo concluído (~20h30) com dados corretos |
| 26/04 tarde | Backup Neo4j (9.4GB) — diagnóstico SOCIO_DE — análise Adail Pinheiro |
| 26/04 noite | Diagnóstico 47 pipelines — venv corrompido corrigido — bootstrap_all_contract corrigido |
| 27/04 | TSE 2024 baixado (candidatos 927k + doações 5.1M) — importação em andamento |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (confirmar 3 containers rodando)
[ ] Reaplicar nginx timeout
[ ] Recriar usuário frontend se necessário
[ ] Verificar dados: docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"
```

---

*Documento master gerado em 27/04/2026 — versão 7*
*Consolida: v1→v6 + sessões 26/04 noite e 27/04 manhã*
*Inclui: patch completo + bootstrap corrigido + bracc_run.sh + caso Adail Pinheiro*
