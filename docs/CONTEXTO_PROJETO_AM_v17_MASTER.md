# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v17
> Gerado em 02/05/2026 ~12h45
> Cole este arquivo + rode `cat docs/CHANGELOG_TECNICO.md` no início de qualquer nova conversa.

---

## 🤖 INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO

Você está num projeto técnico longo com Alberto (Rolim). Siga obrigatoriamente:

1. **Leia o CHANGELOG antes de qualquer correção de código:**
   ```bash
   cat ~/Downloads/br-acc-novo/docs/CHANGELOG_TECNICO.md
   ```
2. **Leia o ORIENTACOES_IA.md para regras de comportamento:**
   ```bash
   cat ~/Downloads/br-acc-novo/docs/ORIENTACOES_IA.md
   ```
3. Após qualquer alteração de código → atualize o CHANGELOG
4. Ao final de cada sessão → gere novo MASTER .md e commite no GitHub
5. **Sempre inclua data/hora nos comandos de log**
6. **⚠️ Avise quando a sessão estiver no limite — OBRIGATÓRIO**

---

## 👤 Perfil

| Campo | Valor |
|---|---|
| Nome | Alberto (Rolim) |
| Contexto | Oposição política no Amazonas |
| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |
| SO | Windows 11 / Git Bash |
| uv | `~/.local/bin/uv` |
| GitHub | https://github.com/PuraForja/bracc-etl |

---

## 🛠️ Infraestrutura

```bash
cd ~/Downloads/br-acc-novo && docker compose up -d
```

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |

---

## ✅ STATUS NEO4J (02/05/2026 ~12h — antes da fila atual)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.483.645 | ✅ |
| Partner | 17.774.658 | ✅ |
| Person | 1.559.007 | ✅ |
| Expense | 430.000 | ✅ viagens apenas — senado/câmara pendentes |
| TaxWaiver | 291.799 | ✅ |
| GovTravel | 260.000 | ✅ |
| GovCardExpense | 131.950 | ✅ |
| Fund | 41.107 | ✅ |
| Contract | 32.259 | ✅ |
| Amendment | 27.943 | ✅ |
| Election | 16.898 | ✅ |
| InternationalSanction | 8.435 | ✅ |
| Expulsion | 4.074 | ✅ ceaf |
| BarredNGO | 3.572 | ✅ cepim |
| CVMProceeding | 537 | ✅ |
| LeniencyAgreement | 115 | ✅ |
| Inquiry/CPI | 105 | ✅ |
| MunicipalGazetteAct | 10 | ✅ |

**Backup:** neo4j-backup-20260430.tar.gz — ⚠️ DESATUALIZADO — fazer após fila terminar

---

## 📦 STATUS DOWNLOADS E IMPORTAÇÕES

| Fonte | Download | Importação | Obs |
|---|---|---|---|
| cnpj 28G | ✅ | ✅ | |
| viagens 7.7G | ✅ | ✅ | |
| tse 43G | ✅ | ⏳ | fila — último |
| transparencia 2.7G | ✅ | ⏳ | fila |
| siop 2.4G | ✅ | ⏳ | fila |
| opensanctions 2.6G | ✅ | ⏳ | fila |
| camara 1.7G | ✅ | ⏳ | fila — corrigido batch=500 |
| siconfi 763M | ✅ | ⏳ | fila |
| icij 667M | ✅ | ⏳ | fila |
| senado 71M | ✅ | ⏳ | fila — corrigido batch=500 |
| sanctions 62M | ✅ | ⏳ | fila |
| renuncias 510M | ✅ | ✅ | |
| cpgf 50M | ✅ | ✅ | |
| cvm_funds 18M | ✅ | ✅ | |
| holdings 10M | ✅ | ✅ | |
| ofac 7.9M | ✅ | ✅ | |
| ceaf 4M | ✅ | ✅ | |
| un_sanctions 2.4M | ✅ | ✅ | |
| bcb 2.4M | ✅ | ✅ | API Olinda manual |
| cepim 1.4M | ✅ | ✅ | 3.572 BarredNGO |
| leniency 560K | ✅ | ✅ | |
| cvm 652K | ✅ | ✅ | |
| senado_cpis 108K | ✅ | ✅ | |
| querido_diario 8K | ✅ | ✅ | |
| pncp parcial | 🔄 ~47% | ⏳ | importar após download |
| eu_sanctions | ❌ | ❌ | IP BR bloqueado |
| pep_cgu | ❌ | ❌ | autenticação — decisão pendente |
| world_bank | ❌ | ❌ | não testado |
| datasus | ❌ | ❌ | precisa Visual C++ |

---

## 🔄 FILA ATUAL (T2) — relançada 02/05 ~12h45

```bash
echo "▶️ FILA INICIADA: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ~/Downloads/br-acc-novo/pipeline_imports.log && \
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  for FONTE in sanctions siconfi icij senado camara transparencia siop opensanctions tse; do
    echo "▶️ Iniciando $FONTE: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline_imports.log
    uv run bracc-etl run --source $FONTE --neo4j-password "changeme" \
      --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log
    echo "✅ $FONTE concluído: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline_imports.log
    powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"
  done && \
  echo "🎉 FILA COMPLETA: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline_imports.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"
```

**Se ainda travar:** reduzir batch_size para 250 nos pipelines que travaram.

---

## 🔧 CORREÇÕES NO CÓDIGO — RESUMO

| Data | Correção | Arquivos | Status |
|---|---|---|---|
| 02/05 | batch_size 1_000→500 | 6 pipelines grandes | ✅ |
| 01/05 | run_query→run_query_with_retry | 12 pipelines | ✅ |
| 01/05 | batch_size 10k→1_000 | 6 pipelines grandes | ✅ (depois →500) |
| 30/04 | CEPIM --date D-1 | download_cepim.py | ✅ workaround |
| 30/04 | BCB API Olinda manual | download_bcb.py | ✅ dados OK |

> Ver CHANGELOG_TECNICO.md para detalhes completos.

---

## ⚠️ PROBLEMAS CONHECIDOS

| # | Problema | Prioridade |
|---|---|---|
| 1 | Backup desatualizado | 🔴 URGENTE após fila |
| 2 | Se batch=500 ainda travar → reduzir para 250 | 🔴 monitorar |
| 3 | SOCIO_DE incompletos 18.7M vs 26.8M | 🟡 |
| 4 | pep_cgu autenticação | 🟡 decisão pendente |
| 5 | world_bank não testado | 🟡 |
| 6 | download_bcb.py reescrita pendente | 🟡 |
| 7 | download_cepim.py fallback D-1 | 🟡 |
| 8 | Bug frontend Person grafo vazio | 🟡 |
| 9 | DATASUS Visual C++ | 🟠 |
| 10 | Nginx timeout volátil | 🟠 |

---

## 💡 COMANDOS ÚTEIS

```bash
# ── Monitoramento padrão ──────────────────────────────────────────────
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log && echo "---" && \
tail -3 ~/Downloads/br-acc-novo/download_pncp.log && echo "---" && \
ps aux | grep bracc-etl | grep -v grep

# ── Neo4j totais ──────────────────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# ── Backup (NUNCA com importação rodando!) ────────────────────────────
docker run --rm -v br-acc-novo_neo4j-data:/data \
  -v C:/Users/Rolim/Downloads:/backup \
  alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && \
  echo "✅ Backup: $(date '+%d/%m/%Y %H:%M:%S')" && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# ── Subir containers ──────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo && docker compose up -d

# ── Nginx timeout ─────────────────────────────────────────────────────
docker exec br-acc-novo-frontend-1 sh -c 'echo "server {
    listen 3000; root /usr/share/nginx/html; index index.html;
    location /assets/ { expires 1y; add_header Cache-Control \"public, immutable\"; }
    location / { try_files \$uri \$uri/ /index.html; add_header Cache-Control \"no-cache, no-store, must-revalidate\"; }
    location /api { proxy_pass http://api:8000; proxy_set_header Host \$host;
      proxy_read_timeout 300s; proxy_connect_timeout 300s; proxy_send_timeout 300s; }
}" > //etc/nginx/conf.d/default.conf && nginx -s reload'

# ── Recriar usuário ───────────────────────────────────────────────────
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"teste@bracc.com\",\"password\":\"senha123\",\"invite_code\":\"rolim\"}"

# ── Verificar correções ───────────────────────────────────────────────
grep -r "batch_size=500" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak" | grep "Neo4jBatchLoader"
grep -r "loader\.run_query(" ~/Downloads/br-acc-novo/etl/src/bracc_etl/pipelines/ | grep -v ".bak" | grep -v "run_query_with_retry"

# ── PNCP retomar ─────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_pncp.py --output-dir ../data/pncp \
  --start-date 2021-01-01 --window-days 5 --request-delay 2.0 \
  --timeout 120 --skip-existing 2>&1 | tee ../download_pncp.log && \
  echo "✅ PNCP: $(date '+%d/%m/%Y %H:%M:%S')" && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# ── Commitar docs no GitHub ───────────────────────────────────────────
cd ~/Downloads/br-acc-novo && \
  git add docs/ && \
  git status --short && \
  git commit -m "docs: v17 + changelog 02/05 $(date '+%Y-%m-%d')" && \
  git push origin main
```

---

## 📅 HISTÓRICO

| Data | O que foi feito |
|---|---|
| 20-25/04 | Infraestrutura + CNPJ + patches |
| 26/04 | CNPJ completo + backup |
| 27/04 | TSE 2024 + Câmara baixada |
| 28/04 | Downloads massivos |
| 29/04 | Viagens ✅ + User-Agent CGU ✅ |
| 30/04 | Backup ✅ + CEPIM ✅ + BCB ✅ |
| 01/05 | run_query_with_retry + batch_size=1_000 em 12 pipelines |
| 02/05 | batch_size 1_000→500 — câmara e senado travavam. Fila relançada. GitHub sincronizado. ORIENTACOES_IA.md criado. |

---

## ⚠️ CHECKLIST NOVA SESSÃO

```
[ ] Docker Desktop aberto
[ ] docker compose up -d && docker ps
[ ] cat docs/CHANGELOG_TECNICO.md
[ ] ps aux | grep bracc-etl (fila viva?)
[ ] tail -5 pipeline_imports.log
[ ] tail -3 download_pncp.log
[ ] Se fila morreu: relançar
[ ] Se batch=500 travou: reduzir para 250
[ ] Após fila: BACKUP PRIMEIRO
[ ] Após backup: importar PNCP
```

---

## 📎 5 ARQUIVOS DE REFERÊNCIA

```
docs/CONTEXTO_PROJETO_AM_v17_MASTER.md  ← este
docs/CHANGELOG_TECNICO.md
docs/CORRECOES_SCRIPTS_DOWNLOAD.md
docs/URLS_CORRETAS.md
docs/ORIENTACOES_IA.md
```

GitHub: https://github.com/PuraForja/bracc-etl/tree/main/docs

---

*v17 — 02/05/2026 ~12h45*
*batch_size=500 aplicado — fila rodando*
*⚠️ Backup URGENTE após fila terminar*
