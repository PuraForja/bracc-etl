# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v11
> Gerado em 28/04/2026 noite — consolida v10 + sessão 28/04 noite
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
12. **REGRA:** Avisar Alberto com antecedência quando a conversa estiver ficando longa
13. **REGRA:** Quando algo demorar mais de 1 minuto sem output, é sinal de travamento — avisar
14. **REGRA:** Usar `grep -E "✅|⚠️" <log> && du -sh data/*` como diagnóstico rápido
15. **REGRA:** Downloads podem rodar em paralelo em terminais separados — organizar assim
16. **REGRA:** Sempre adicionar sinal sonoro ao final dos comandos longos:
    `&& powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"`

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
cd ~/Downloads/br-acc-novo && docker compose up -d
```

### Credenciais
| Sistema | Usuário | Senha |
|---|---|---|
| Neo4j | neo4j | changeme |
| Frontend | teste@bracc.com | senha123 |
| Invite code | — | rolim |

---

## ✅ STATUS ATUAL DOS DADOS (28/04/2026 noite)

### Neo4j (banco atual)
| Tipo | Quantidade | Status |
|---|---|---|
| Company | 40.467.322 | ✅ CNPJs corretos |
| Partner | 17.774.658 | ✅ |
| Person | 1.090.627 | ✅ Candidatos TSE 2024 |
| Election | 16.707 | ✅ |
| SOCIO_DE | 18.783.607 | ⚠️ Incompleto (esperado 26.8M) |
| DOOU | 1.169.752 | ✅ |
| CANDIDATO_EM | 463.604 | ✅ |

> ⚠️ Neo4j tem só TSE 2024 importado. TSE 2018/2020/2022 ainda não importados.

### Backup do banco
```
Arquivo: neo4j-backup-20260426.tar.gz
Local:   C:\Users\Rolim\Downloads\
Tamanho: 9.4GB
```
> ⚠️ Backup desatualizado — fazer novo backup após concluir todos os downloads e importações.

### Downloads no HD — Status Detalhado

| Fonte | Tamanho | Status | Observação |
|---|---|---|---|
| cnpj | 28G | ✅ importado | 40M empresas |
| tse | 13G+ | ✅/🔄 | 2024 importado — 2018/2020/2022 baixando agora |
| camara | 1.7G | ✅ | 18/18 anos (2009-2026) |
| senado | 71M | ✅ | 14/19 anos (2022-2026 retornam 404) |
| transparencia | 396M+ | ✅/🔄 | 2024 importado — 2023 baixado agora (40k contratos + 857k emendas) |
| leniency | 292K | ✅ | 146 acordos |
| cpgf | 50M | ✅ | 15/16 meses |
| viagens | 7.7G | ✅ | 3.9M viagens (2020-2026) |
| tesouro_emendas | 61M | ✅ | emendas_tesouro.csv |
| siop | 2.4G | ✅ | 4.7M linhas — emendas 2020-2024 |
| cvm | 652K | ✅ | processo_sancionador + acusado |
| cvm_funds | 18M | ✅ | cad_fi.csv |
| icij | 667M | ✅ | Panama/Pandora Papers |
| ofac | 7.9M | ✅ | sdn + add + alt |
| un_sanctions | 2.4M | ✅ | 1005 entidades |
| opensanctions | 2.6G | ✅ | 4.1M entidades |
| holdings | 10M | ✅ | holding.csv.gz |
| renuncias | 510M | ✅ | 2020-2024 |
| querido_diario | — | ✅ | acts.jsonl |
| senado_cpis | — | ✅ | |
| siconfi | 763M | ✅ | estados + municípios 2020-2024 |
| pncp | 43M | 🔄 | 672/4668 combos (~14%) — rodando agora |
| sanctions (CGU) | 0 | ❌ | 403 Forbidden |
| cepim | 0 | ❌ | 403 Forbidden |
| ceaf | 0 | ❌ | 403 Forbidden |
| pep_cgu | 0 | ❌ | 403 Forbidden |
| bcb | 0 | ❌ | 400 Bad Request — URL mudou |
| eu_sanctions | 0 | ❌ | 403 Forbidden |
| world_bank | 0 | ❌ | URLs mortas |
| camara_inquiries | — | ❌ | Precisa BigQuery |
| datasus | — | ❌ | Precisa Visual C++ Build Tools para instalar pysus |
| comprasnet | — | N/A | Pipeline Neo4j — usa dados do PNCP |

---

## 🔄 DOWNLOADS RODANDO AGORA (28/04/2026 noite)

| Terminal | Fonte | Status |
|---|---|---|
| T1 | PNCP | 672/4668 combos — ~6h restantes |
| T2 | TSE 2018 | Baixando doações (310MB) |
| T3 | Transparência 2023 | ✅ Concluído |

**Após TSE 2018 terminar, roda automaticamente 2020 e 2022.**

**Comandos para retomar se parar:**
```bash
# PNCP (Terminal 1):
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_pncp.py --output-dir ../data/pncp \
  --start-date 2021-01-01 --window-days 5 --request-delay 2.0 \
  --timeout 120 --skip-existing 2>&1 | tee ../download_pncp.log && \
  echo "✅ PNCP: $(date '+%H:%M:%S')" | tee -a ../download_pncp.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"

# TSE histórico (Terminal 2):
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_tse.py --output-dir ../data/tse --years 2018 --skip-existing 2>&1 | tee ../download_tse_hist.log && \
  uv run python scripts/download_tse.py --output-dir ../data/tse --years 2020 --skip-existing 2>&1 | tee -a ../download_tse_hist.log && \
  uv run python scripts/download_tse.py --output-dir ../data/tse --years 2022 --skip-existing 2>&1 | tee -a ../download_tse_hist.log && \
  echo "✅ TSE histórico: $(date '+%H:%M:%S')" | tee -a ../download_tse_hist.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"

# Transparência anos anteriores (Terminal 3):
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_transparencia.py --output-dir ../data/transparencia --year 2022 --skip-existing 2>&1 | tee ../download_transp2022.log && \
  uv run python scripts/download_transparencia.py --output-dir ../data/transparencia --year 2021 --skip-existing 2>&1 | tee -a ../download_transp2022.log && \
  echo "✅ Transparência 2021-2022: $(date '+%H:%M:%S')" | tee -a ../download_transp2022.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"
```

---

## 🔧 CORREÇÕES APLICADAS NO CÓDIGO

### Correção 1 — URLs de download (runner.py)
Mirror Casa dos Dados adicionado.

### Correção 2 — Bug start_phase Fase 1 (cnpj.py)
`--start-phase` funciona corretamente.

### Correção 3 — Filtro ZIP — CAUSA RAIZ (cnpj.py) ✅
```python
files = [f for f in sorted(cnpj_dir.glob(pattern)) if f.suffix != ".zip"]
```

### Correção 4 — Empresas0.zip corrompido
Arquivo deletado.

### Correção 5 — Nginx timeout (volátil)
Pendente incorporar no Dockerfile.

### Correção 6 — bootstrap_all_contract.yml ✅
28 fontes atualizadas para `script_download`.
```bash
# Aplicado em:
config/bootstrap_all_contract.yml
```

### Correção 7 — venv corrompido (lib64)
```powershell
Remove-Item -Recurse -Force "C:\Users\Rolim\Downloads\br-acc-novo\etl\.venv"
```
```bash
cd ~/Downloads/br-acc-novo/etl && uv sync
```

### Correção 8 — wait_for_api no bootstrap ✅
Adicionado parâmetro `--api-url`.
```bash
# Reaplicar se necessário:
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
@@ -227,6 +227,16 @@
+    casadosdados_base = "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/2026-04-12/"
+    try:
+        resp = httpx.head(casadosdados_base, follow_redirects=True, timeout=30)
+        if resp.status_code < 400:
+            return casadosdados_base
+    except httpx.HTTPError:
+        pass
```

---

## 🔍 DESCOBERTAS IMPORTANTES

### API funciona via element_id
```bash
curl "http://localhost:8000/api/v1/entity/29025187000160"  # CNPJ sem formatação ✅
curl "http://localhost:8000/api/v1/entity/by-element-id/4:...:47052943"  # element_id ✅
curl "http://localhost:8000/api/v1/entity/4:...:28475404/connections"  # conexões ✅
curl "http://localhost:8000/api/v1/graph/4:...:28475404"  # grafo — só Company ⚠️
```

### Bug do frontend
`/api/v1/graph/{id}` só aceita Company, não Partner. Fix pendente.

### Caso Adail José Figueiredo Pinheiro
```
CPF: 772.677.962-49 — Partner ID: 1eeb9bfb2fa9c3af
Empresas AM:
  DAFIL PARTICIPACOES LTDA (29.025.187/0001-60) — holding — R$150k
  VIEIRALVES EMPREENDIMENTOS LTDA (19.362.619/0001-74) — imóveis — R$180k
Candidato a prefeito: 2016 e 2020 — Itacoatiara/AM (município 0225)
```

### DATASUS — bloqueado por falta de Visual C++ Build Tools
PySUS precisa compilar `cffi` que requer Microsoft Visual C++ 14.0+.
Solução alternativa: baixar arquivos DBC do FTP do DATASUS manualmente ou instalar Build Tools (~5GB).

### PNCP — instável mas funcionando
Script tem checkpoint robusto. Usar `--window-days 5 --request-delay 2.0` para reduzir erros.
672/4668 combos concluídos (14%). Estimativa: ~6h para completar.

### Transparência CGU — 403 em servidores
Compras e emendas funcionam. Servidores retornam 403 em todos os meses.

---

## ⚠️ PROBLEMAS CONHECIDOS

| # | Problema | Status |
|---|---|---|
| 1 | SOCIO_DE incompletos (18.7M vs 26.8M) | ⚠️ Pendente |
| 2 | Scripts link_persons.cypher não existem | ⚠️ Pendente |
| 3 | Bug frontend grafo vazio para pessoas | ⚠️ Pendente |
| 4 | CGU 403 (sanctions, cepim, ceaf, pep_cgu) | ⚠️ Sem solução automática |
| 5 | DATASUS precisa Visual C++ Build Tools | ⚠️ Pendente |
| 6 | bcb URL mudou (400) | ⚠️ Pendente investigar |
| 7 | eu_sanctions 403 | ⚠️ Pendente |
| 8 | world_bank URLs mortas | ⚠️ Pendente |
| 9 | camara_inquiries precisa BigQuery | ⚠️ Pendente |
| 10 | Nginx timeout volátil | ⚠️ Pendente Dockerfile |
| 11 | Usuários perdidos ao reiniciar | ⚠️ Pendente volume |

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

# ── Bootstrap ─────────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo && python3 scripts/run_bootstrap_all.py \
  --repo-root . --compose-file docker-compose.yml \
  --api-url http://localhost:8000/health --no-reset \
  --sources tse,camara,senado 2>&1 | tee ../bootstrap_test.log

# ── Neo4j ─────────────────────────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH ()-[r]->() RETURN type(r) as tipo, count(r) as total ORDER BY total DESC"

# ── Diagnóstico rápido ────────────────────────────────────────────────
du -sh ~/Downloads/br-acc-novo/data/* | sort -h

# ── Verificar PNCP ────────────────────────────────────────────────────
wc -l ~/Downloads/br-acc-novo/data/pncp/.checkpoint

# ── Backup (PowerShell) ───────────────────────────────────────────────
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-YYYYMMDD.tar.gz /data

# ── Importar fonte no Neo4j ───────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source FONTE --neo4j-password "changeme" \
  --data-dir ../data 2>&1 | tee ../pipeline_FONTE.log && \
  echo "✅ FONTE importado: $(date '+%H:%M:%S')" | tee -a ../pipeline_FONTE.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"
```

---

## 📋 FASES DO PROJETO

| Fase | Descrição | Status |
|---|---|---|
| 1 | Infraestrutura instalada | ✅ |
| 2 | Download CNPJ (~28GB) | ✅ |
| 3 | Pipeline ETL CNPJ | ✅ |
| 4 | Frontend com busca e grafo | ✅ Parcial |
| 5 | Corrigir Fase 1 estab_lookup | ✅ |
| 6 | Bootstrap corrigido | ✅ |
| 7 | TSE 2024 baixado e importado | ✅ |
| 8 | Download massivo de fontes | 🔄 ~90% |
| 9 | TSE 2018/2020/2022 baixando | 🔄 |
| 10 | PNCP baixando (672/4668) | 🔄 ~6h |
| 11 | Transparência 2021/2022/2023 | 🔄 2023 ✅ |
| 12 | DATASUS (precisa Build Tools) | ⏳ |
| 13 | CGU 403 (solução manual) | ⏳ |
| 14 | **Importação de todas as fontes** | ⏳ Próxima grande etapa |
| 15 | Fazer backup Neo4j atualizado | ⏳ |
| 16 | Corrigir bug frontend grafo | ⏳ |
| 17 | Corrigir SOCIO_DE incompletos | ⏳ |
| 18 | Nginx/usuários permanentes | ⏳ |
| 19 | PostgreSQL + tabelas AM | ⏳ |
| 20 | Metabase + dashboards | ⏳ |
| 21 | Mapa interativo 62 municípios | ⏳ |

---

## 📅 HISTÓRICO DE SESSÕES

| Data | O que foi feito |
|---|---|
| 20/04 | Infraestrutura instalada |
| 21/04 | Mirror Casa dos Dados — download CNPJ iniciado |
| 22/04 | Download CNPJ concluído |
| 24/04 | Correções URLs + start_phase |
| 25/04 | Causa raiz ZIP + patch gerado |
| 26/04 manhã | Pipeline CNPJ completo (~20h) |
| 26/04 tarde | Backup 9.4GB — análise Adail Pinheiro |
| 26/04 noite | 47 pipelines mapeados — bootstrap corrigido |
| 27/04 manhã | TSE 2024 baixado e importado |
| 27/04 noite | Câmara baixada — bootstrap wait_for_api corrigido |
| 28/04 manhã | Senado — bootstrap trava após 404 |
| 28/04 tarde | Download massivo — siconfi completo — datasus criado |
| 28/04 noite | PNCP retomado (672/4668) — TSE 2018/2020/2022 baixando — Transparência 2023 ✅ |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (3 containers rodando)
[ ] Verificar downloads: wc -l data/pncp/.checkpoint && du -sh data/tse/
[ ] Reaplicar nginx timeout se necessário
[ ] Recriar usuário frontend se necessário
[ ] PRÓXIMA GRANDE ETAPA: importar todas as fontes no Neo4j
[ ] Fazer backup Neo4j antes de importar
```

---

*v11 — 28/04/2026 noite*
*Consolida v1→v10 + sessão 28/04 noite*
*Downloads em andamento: PNCP (672/4668) + TSE 2018/2020/2022 + Transparência*
