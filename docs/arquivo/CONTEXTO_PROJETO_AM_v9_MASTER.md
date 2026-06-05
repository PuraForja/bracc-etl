# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v9
> Gerado em 28/04/2026 — consolida v8 + sessão 28/04 noite
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
12. **REGRA NOVA:** Avisar Alberto com antecedência quando a conversa estiver ficando longa, ANTES de bloquear — ele precisa copiar o contexto antes de encerrar a sessão

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
| Python | `/c/Python314/python.exe` (v3.14.4) — uv usa este por padrão |
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

## ✅ STATUS ATUAL DOS DADOS (28/04/2026 — noite)

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

### Backup do banco
```
Arquivo: neo4j-backup-20260426.tar.gz
Local:   C:\Users\Rolim\Downloads\
Tamanho: 9.4GB
```

### Downloads no HD — Status Detalhado

| Fonte | Status | Observação |
|---|---|---|
| cnpj | ✅ | 40M empresas, 28GB |
| tse | ✅ | candidatos 927k + doações 5.1M (2024), 13GB |
| camara | ✅ | 18/18 anos (2009-2026), 1.7GB |
| senado | ✅ | 14/19 anos (2008-2021), 71MB — 2022-2026 retornam 404 |
| transparencia | ✅ | contratos 39k + emendas 857k (2024) — servidores 403 |
| leniency | ✅ | 146 acordos |
| cpgf | ✅ | 15/16 meses (202511 com 403) |
| viagens | ✅ | 3.9M viagens (2020-2026), 7.7GB |
| tesouro_emendas | ✅ | 61MB |
| cvm | ✅ | 2 arquivos |
| cvm_funds | ✅ | cad_fi.csv 17.9MB |
| icij | ✅ | Panama/Pandora Papers, 667MB |
| ofac | ✅ | sdn.csv + add.csv + alt.csv |
| un_sanctions | ✅ | 1005 entidades XML→JSON |
| opensanctions | ✅ | 4.1M entidades, 2.7GB |
| holdings | ✅ | holding.csv.gz 10.4MB |
| renuncias | ✅ | 2020-2024 (5 anos) |
| siconfi | 🔄 | **RODANDO AGORA** — estados OK (2020-2024), municípios em andamento (~8-10h) |
| sanctions (CGU) | ❌ | 403 Forbidden — bloqueio CGU |
| cepim | ❌ | 403 Forbidden — bloqueio CGU |
| ceaf | ❌ | 403 Forbidden — bloqueio CGU |
| pep_cgu | ❌ | 403 Forbidden — bloqueio CGU |
| bcb | ❌ | 400 Bad Request — URL da API mudou |
| eu_sanctions | ❌ | 403 Forbidden |
| world_bank | ❌ | URLs mortas |
| pncp | ⛔ | Cancelado — 2340 combos com timeout, retorna tudo 204 vazio |
| siop | 🔄 | Pendente (após siconfi) |
| querido_diario | 🔄 | Pendente |
| senado_cpis | 🔄 | Pendente |
| camara_inquiries | 🔄 | Pendente |

### O que ainda falta rodar (após siconfi terminar):
```bash
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
uv run python scripts/download_siop.py --output-dir ../data/siop --skip-existing 2>&1 | tee ~/Downloads/bracc_logs/download_siop.log && echo "✅ siop" && \
uv run python scripts/download_querido_diario.py --output-dir ../data/querido_diario --skip-existing 2>&1 | tee ~/Downloads/bracc_logs/download_querido_diario.log && echo "✅ querido_diario" && \
uv run python scripts/download_senado_cpis.py --output-dir ../data/senado_cpis --skip-existing 2>&1 | tee ~/Downloads/bracc_logs/download_senado_cpis.log && echo "✅ senado_cpis" && \
uv run python scripts/download_camara_inquiries.py --output-dir ../data/camara_inquiries --skip-existing 2>&1 | tee ~/Downloads/bracc_logs/download_camara_inquiries.log && echo "✅ camara_inquiries"
echo "🎉 Finalizado: $(date '+%H:%M:%S')"
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
28 fontes atualizadas para `script_download`.

### Correção 7 — venv corrompido (lib64) ✅
```powershell
Remove-Item -Recurse -Force "C:\Users\Rolim\Downloads\br-acc-novo\etl\.venv"
```
```bash
cd ~/Downloads/br-acc-novo/etl && uv sync
```
**Nota:** uv usa Python 3.14.4 do sistema (C:\Python314). Funciona normalmente.

### Correção 8 — wait_for_api no bootstrap ✅
Parâmetro `--api-url` adicionado em `scripts/run_bootstrap_all.py`.

### Correção 9 — renuncias e siconfi não aceitam --skip-existing ✅
Rodar sem esse argumento:
```bash
uv run python scripts/download_renuncias.py --output-dir ../data/renuncias
uv run python scripts/download_siconfi.py --output-dir ../data/siconfi
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

### Fontes com 403 CGU — padrão identificado
Todas as fontes que falham com 403 são do mesmo servidor `dadosabertos-download.cgu.gov.br`.
Provavelmente bloqueio por IP ou user-agent automático. Workaround futuro: adicionar headers de browser ou usar VPN/proxy.
Fontes afetadas: sanctions (CEIS/CNEP), cepim, ceaf, pep_cgu, servidores (transparencia), cpgf nov/2025.

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
| 4 | sanctions/cepim/ceaf/pep_cgu 403 CGU | ⚠️ Bloqueio servidor CGU |
| 5 | Senado 2022-2026 retornam 404 | ⚠️ Dados não disponíveis no formato antigo |
| 6 | Nginx timeout volátil | ⚠️ Pendente |
| 7 | Usuários perdidos ao reiniciar | ⚠️ Pendente |
| 8 | Fontes sem script de download | ⚠️ Sem solução pública |
| 9 | bcb URL API mudou (400) | ⚠️ Pendente investigar nova URL |
| 10 | world_bank URLs mortas | ⚠️ Pendente nova URL |
| 11 | pncp — 2340 combos, API retorna 204 | ⛔ Descartado por ora |

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

# ── Ver logs de download ──────────────────────────────────────────────
ls ~/Downloads/bracc_logs/
grep -l 'FALHOU\|Error\|error' ~/Downloads/bracc_logs/*.log

# ── Verificar espaço por fonte ────────────────────────────────────────
du -sh ~/Downloads/br-acc-novo/data/* | sort -h
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
| 10 | Download de todas as fontes disponíveis | 🔄 ~80% concluído |
| 11 | siconfi rodando (8-10h municípios) | 🔄 Em andamento |
| 12 | siop, querido_diario, senado_cpis, camara_inquiries | ⏳ Após siconfi |
| 13 | Importação de todas as fontes no Neo4j | ⏳ Próxima grande etapa |
| 14 | Corrigir bootstrap após 404 Senado | ⏳ |
| 15 | Corrigir bug frontend grafo pessoas | ⏳ |
| 16 | Corrigir SOCIO_DE incompletos | ⏳ |
| 17 | Nginx/usuários permanentes | ⏳ |
| 18 | PostgreSQL + tabelas AM | ⏳ |
| 19 | Metabase + dashboards | ⏳ |
| 20 | Mapa interativo 62 municípios AM | ⏳ |

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
| 28/04 manhã | Senado baixado (14/19 anos) — bootstrap trava após 404 |
| 28/04 noite | **Download massivo iniciado** — venv recriado — 20+ fontes baixadas — siconfi rodando |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (3 containers rodando)
[ ] Reaplicar nginx timeout se necessário
[ ] Recriar usuário frontend se necessário
[ ] Verificar se siconfi terminou: ls -lh ~/Downloads/br-acc-novo/data/siconfi/
[ ] Se siconfi OK: rodar siop, querido_diario, senado_cpis, camara_inquiries
[ ] Verificar dados Neo4j
[ ] PRÓXIMA GRANDE ETAPA: importar todas as fontes baixadas no Neo4j via bootstrap
```

---

## 🗺️ PRÓXIMA SESSÃO — O QUE FAZER

1. **Verificar siconfi:** `ls -lh ~/Downloads/br-acc-novo/data/siconfi/` — deve ter arquivos `dca_states_YYYY.csv` e `dca_mun_YYYY.csv`
2. **Rodar os 4 pendentes** (siop, querido_diario, senado_cpis, camara_inquiries) — bloco de comando já pronto acima
3. **Fazer backup do Neo4j** (antes de qualquer importação)
4. **Iniciar importação** das fontes baixadas via bootstrap ou pipeline direto
5. **Prioridade de importação:** transparencia → renuncias → viagens → cpgf → leniency → sanctions (se resolver 403)

---

*v9 — 28/04/2026*
*Consolida v1→v8 + sessão 28/04 noite (download massivo)*
