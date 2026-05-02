# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v8
> Gerado em 28/04/2026 — consolida v7 + sessão 27/04 noite e 28/04
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
7. **REGRA:** Sempre propor testes rápidos ANTES de rodar pipelines longos
8. **REGRA:** Sempre agrupar múltiplos comandos bash em um único bloco
9. **REGRA:** Nunca rodar download e importação separadamente — baixar tudo primeiro, depois importar
10. **REGRA:** Preferir texto colado em vez de prints/imagens para economizar contexto de sessão
11. **REGRA:** Gerar novo contexto (.md) proativamente quando a conversa estiver longa

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

---

## 🛠️ Infraestrutura

### Containers Docker
| Container | Porta | Status |
|---|---|---|
| bracc-neo4j | 7474/7687 | ✅ |
| br-acc-novo-api-1 | 8000 | ✅ |
| br-acc-novo-frontend-1 | 3000 | ✅ |
| etl | — | profile "etl" |

```bash
# Subir containers:
cd ~/Downloads/br-acc-novo && docker compose up -d
```

### Credenciais
| Sistema | Usuário | Senha |
|---|---|---|
| Neo4j | neo4j | changeme |
| Frontend | teste@bracc.com | senha123 |
| Invite code | — | rolim |

---

## ✅ STATUS ATUAL DOS DADOS (28/04/2026)

### Neo4j
| Tipo | Quantidade | Status |
|---|---|---|
| Company | 40.467.322 | ✅ CNPJs corretos |
| Partner | 17.774.658 | ✅ |
| Person | 1.090.627 | ✅ Candidatos TSE 2024 |
| Election | 16.707 | ✅ |
| SOCIO_DE | 18.783.607 | ⚠️ Incompleto (esperado 26.8M) |
| DOOU | 1.169.752 | ✅ |
| CANDIDATO_EM | 463.604 | ✅ |

### Dados baixados no HD
```
data/cnpj/          ✅ 40M empresas
data/tse/           ✅ candidatos.csv (927k) + doacoes.csv (5.1M) — 2024
data/camara/        ✅ 18/18 anos (2009-2026)
data/senado/        ✅ 14/19 anos (alguns 404 nos anos recentes)
```

### Backup do banco
```
Arquivo: neo4j-backup-20260426.tar.gz
Local:   C:\Users\Rolim\Downloads\
Tamanho: 9.4GB
```

---

## 🔧 CORREÇÕES APLICADAS

### Correção 1 — URLs de download (runner.py)
Mirror Casa dos Dados adicionado como fallback.

### Correção 2 — Bug start_phase Fase 1 (cnpj.py)
`--start-phase` agora funciona corretamente.

### Correção 3 — Filtro ZIP — CAUSA RAIZ (cnpj.py) ✅
```python
files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
```

### Correção 4 — Empresas0.zip corrompido
Arquivo deletado.

### Correção 5 — Nginx timeout (volátil)
Pendente incorporar no Dockerfile.

### Correção 6 — bootstrap_all_contract.yml ✅
28 fontes atualizadas para `script_download`. Aplicado em:
`config/bootstrap_all_contract.yml`

### Correção 7 — venv corrompido (lib64)
```powershell
Remove-Item -Recurse -Force "C:\Users\Rolim\Downloads\br-acc-novo\etl\.venv"
```
```bash
cd ~/Downloads/br-acc-novo/etl && uv sync
```

### Correção 8 — wait_for_api no bootstrap ✅ NOVA (28/04/2026)
**Problema:** `run_bootstrap_all.py` usava `localhost:8000` fixo — travava dentro do Docker.
**Solução:** Adicionado parâmetro `--api-url`.
**Aplicado em:** `scripts/run_bootstrap_all.py`

```bash
# Como aplicar se precisar reaplicar:
cd ~/Downloads/br-acc-novo && \
sed -i 's/def wait_for_api(timeout_sec: int = 300) -> bool:/def wait_for_api(api_url: str = "http:\/\/localhost:8000\/health", timeout_sec: int = 300) -> bool:/' scripts/run_bootstrap_all.py && \
sed -i 's|with urlopen("http://localhost:8000/health", timeout=5) as response:|with urlopen(api_url, timeout=5) as response:|' scripts/run_bootstrap_all.py && \
sed -i 's/    if not wait_for_api():/    if not wait_for_api(api_url=args.api_url):/' scripts/run_bootstrap_all.py && \
sed -i 's/    parser.add_argument("--report-latest"/    parser.add_argument("--api-url", default="http:\/\/localhost:8000\/health", help="API health check URL")\n    parser.add_argument("--report-latest"/' scripts/run_bootstrap_all.py
```

---

## 📄 PATCH COMPLETO (correcoes_bracc_2026.patch)

```diff
diff --git a/etl/src/bracc_etl/pipelines/cnpj.py b/etl/src/bracc_etl/pipelines/cnpj.py
@@ -290,7 +290,7 @@
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
@@ -322,9 +322,9 @@
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
-            files = sorted(cnpj_dir.glob(pattern))
+            files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
@@ -1025,9 +1025,9 @@
-        files = sorted(cnpj_dir.glob(f"extracted/{pattern}"))
+        files = [f for f in sorted(cnpj_dir.glob(f"extracted/{pattern}")) if f.suffix != ".zip"]
-            files = sorted(cnpj_dir.glob(pattern))
+            files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
@@ -1105,7 +1105,9 @@
-        if use_bq:
+        if start_phase > 1:
+            logger.info("Skipping Phase 1 -- start_phase=%d", start_phase)
+        elif use_bq:

diff --git a/etl/src/bracc_etl/runner.py b/etl/src/bracc_etl/runner.py
@@ -227,6 +227,22 @@
+    casadosdados_base = "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/2026-04-12/"
+    try:
+        resp = httpx.head(casadosdados_base, follow_redirects=True, timeout=30)
+        if resp.status_code < 400:
+            return casadosdados_base
+    except httpx.HTTPError:
+        pass
```

---

## ⚠️ PROBLEMA ATUAL — Bootstrap trava após download do Senado

**Sintoma:** O bootstrap baixa o Senado (14/19 anos com sucesso, 5 com 404) mas não continua para a importação.

**Causa provável:** `download_senado.py` retorna exit code 1 quando alguns anos falham com 404, e o bootstrap interpreta isso como falha total — para antes de importar.

**Próxima ação:** Ver o exit code do download do Senado e corrigir para que 404 em anos recentes não seja tratado como erro fatal.

**Comando para testar:**
```bash
cd ~/Downloads/br-acc-novo && python3 scripts/run_bootstrap_all.py \
  --repo-root . \
  --compose-file docker-compose.yml \
  --api-url http://localhost:8000/health \
  --no-reset \
  --sources senado 2>&1 | tee ../bootstrap_test.log
```

---

## 🔍 DESCOBERTAS IMPORTANTES

### API funciona via element_id
```bash
curl "http://localhost:8000/api/v1/entity/29025187000160"  # CNPJ sem formatação
curl "http://localhost:8000/api/v1/entity/by-element-id/4:...:47052943"
curl "http://localhost:8000/api/v1/entity/4:...:28475404/connections"
curl "http://localhost:8000/api/v1/graph/4:...:28475404"  # só Company
```

### Bug do frontend
`/api/v1/graph/{id}` só aceita Company, não Partner. Fix pendente no frontend.

### Caso Adail José Figueiredo Pinheiro
```
CPF: 772.677.962-49
Partner ID: 1eeb9bfb2fa9c3af
Person ID: 4:91a9add5-...:58722149 (após TSE)

Empresas AM:
  DAFIL PARTICIPACOES LTDA (29.025.187/0001-60) — holding — R$150k
  VIEIRALVES EMPREENDIMENTOS LTDA (19.362.619/0001-74) — imóveis — R$180k

Candidato a prefeito: 2016 e 2020 — Itacoatiara/AM (município 0225)
```

### 47 pipelines disponíveis
```
✅ script_download (28): tse, camara, senado, sanctions, transparencia...
⚠️  Google credentials (8): tse_bens, tse_filiados, dou, rais, stf, mides, caged, datajud
⚠️  Sem script (7): pgfn, tcu, ibama, bndes, inep, datasus, transferegov
```

---

## ⚠️ PROBLEMAS CONHECIDOS

| # | Problema | Status |
|---|---|---|
| 1 | SOCIO_DE incompletos (18.7M vs 26.8M) | ⚠️ Pendente |
| 2 | Scripts link_persons.cypher não existem | ⚠️ Pendente |
| 3 | Bug frontend grafo vazio para pessoas | ⚠️ Pendente |
| 4 | sanctions 403 Forbidden | ⚠️ Pendente |
| 5 | Bootstrap para após 404 no Senado | 🔄 Investigando |
| 6 | Nginx timeout volátil | ⚠️ Pendente |
| 7 | Usuários perdidos ao reiniciar | ⚠️ Pendente |
| 8 | Fontes sem script de download | ⚠️ Sem solução pública |

---

## 💡 COMANDOS ÚTEIS

```bash
# ── Rotina diária ─────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo && docker compose up -d

# ── Nginx timeout ─────────────────────────────────────────────────────
docker exec br-acc-novo-frontend-1 sh -c 'echo "server {
    listen 3000; root /usr/share/nginx/html; index index.html;
    location /assets/ { expires 1y; add_header Cache-Control \"public, immutable\"; }
    location / { try_files \$uri \$uri/ /index.html; add_header Cache-Control \"no-cache, no-store, must-revalidate\"; }
    location /api { proxy_pass http://api:8000; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr; proxy_read_timeout 300s; proxy_connect_timeout 300s; proxy_send_timeout 300s; }
}" > //etc/nginx/conf.d/default.conf && nginx -s reload'

# ── Recriar usuário ───────────────────────────────────────────────────
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"teste@bracc.com\",\"password\":\"senha123\",\"invite_code\":\"rolim\"}"

# ── Bootstrap (modo correto) ──────────────────────────────────────────
cd ~/Downloads/br-acc-novo && python3 scripts/run_bootstrap_all.py \
  --repo-root . \
  --compose-file docker-compose.yml \
  --api-url http://localhost:8000/health \
  --no-reset \
  --sources tse,camara,senado 2>&1 | tee ../bootstrap_test.log

# ── Pipeline CNPJ (20h) ───────────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source cnpj --neo4j-password "changeme" \
  --data-dir ../data --streaming 2>&1 | tee ../pipeline.log && \
  echo "✅ Finalizado em: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a ../pipeline.log

# ── Neo4j ─────────────────────────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH ()-[r]->() RETURN type(r) as tipo, count(r) as total ORDER BY total DESC"

# ── Backup (PowerShell) ───────────────────────────────────────────────
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-YYYYMMDD.tar.gz /data

# ── Restaurar backup (PowerShell) ─────────────────────────────────────
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar xzf /backup/neo4j-backup-20260426.tar.gz -C /

# ── Limpar banco ──────────────────────────────────────────────────────
# docker stop bracc-neo4j && docker rm bracc-neo4j && docker volume rm br-acc-novo_neo4j-data
# cd ~/Downloads/br-acc-novo && docker compose up -d neo4j
```

---

## 📋 FASES DO PROJETO

| Fase | Descrição | Status |
|---|---|---|
| 1 | Infraestrutura instalada | ✅ |
| 2 | Download CNPJ (~28GB) | ✅ |
| 3 | Pipeline ETL CNPJ | ✅ CNPJs corretos |
| 4 | Frontend com busca e grafo | ✅ Parcial |
| 5 | Corrigir Fase 1 estab_lookup | ✅ |
| 6 | Bootstrap corrigido (contrato + wait_for_api) | ✅ |
| 7 | TSE 2024 baixado e importado | ✅ |
| 8 | Câmara baixada (18 anos) | ✅ |
| 9 | Senado baixado (14 anos) | ✅ Parcial |
| 10 | Corrigir bootstrap após 404 Senado | 🔄 Investigando |
| 11 | Download demais fontes | 🔄 Pendente |
| 12 | Importação de todas as fontes | 🔄 Pendente |
| 13 | Corrigir bug frontend grafo pessoas | 🔄 Pendente |
| 14 | Corrigir SOCIO_DE incompletos | 🔄 Pendente |
| 15 | Nginx/usuários permanentes | 🔄 Pendente |
| 16 | PostgreSQL + tabelas AM | ⏳ |
| 17 | Metabase + dashboards | ⏳ |
| 18 | Mapa interativo 62 municípios AM | ⏳ |

---

## 📅 HISTÓRICO DE SESSÕES

| Data | O que foi feito |
|---|---|
| 20/04 | Infraestrutura instalada |
| 21/04 | Mirror Casa dos Dados — download CNPJ iniciado |
| 22/04 | Download CNPJ concluído |
| 24/04 | Correções URLs + start_phase |
| 25/04 | Causa raiz ZIP encontrada + patch gerado |
| 26/04 manhã | Pipeline CNPJ completo (~20h) com dados corretos |
| 26/04 tarde | Backup 9.4GB — diagnóstico SOCIO_DE — análise Adail Pinheiro |
| 26/04 noite | 47 pipelines mapeados — venv corrigido — contrato bootstrap corrigido |
| 27/04 manhã | TSE 2024 baixado e importado (1M pessoas, 5M doações) |
| 27/04 noite | Câmara (18 anos) baixada — bootstrap wait_for_api corrigido |
| 28/04 | Senado baixado (14/19 anos) — bootstrap trava após 404 — v8 gerado |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (3 containers rodando)
[ ] Reaplicar nginx timeout
[ ] Recriar usuário frontend se necessário
[ ] Verificar dados Neo4j
[ ] Investigar bootstrap após 404 Senado (próxima prioridade)
```

---

*v8 — 28/04/2026*
*Consolida v1→v7 + sessões 27/04 noite e 28/04*
