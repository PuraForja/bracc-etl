# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v12
> Gerado em 29/04/2026 — consolida v11 + sessão 29/04
> Cole este arquivo no início de QUALQUER nova conversa para restaurar contexto completo.

---

## 🧠 INSTRUÇÃO OBRIGATÓRIA PARA O CLAUDE

Você está num projeto longo e técnico com Alberto (Rolim). Sua janela de contexto é limitada.

**Obrigações:**
1. Opere sempre em dois modos: **Arquiteto** (propõe soluções) + **Professor** (explica passo a passo)
2. Monitore o tamanho da conversa. Após 30-40 trocas, avise e gere novo `.md`
3. Sempre conectar: **Dados → Diagnóstico → Problema → Ação → Monitoramento**
4. Nível técnico: intermediário — já programou, já usou Linux/Bash, absorve rápido mas precisa de orientação passo a passo
5. Sempre usar dados e exemplos do Amazonas quando possível
6. **REGRA:** Sempre propor testes rápidos ANTES de rodar pipelines longos
7. **REGRA:** Sempre agrupar múltiplos comandos bash em um único bloco
8. **REGRA:** Baixar tudo primeiro, depois importar — nunca misturar
9. **REGRA:** Preferir texto colado em vez de prints/imagens
10. **REGRA:** Downloads podem rodar em paralelo — importações devem ser sequenciais (uma por vez)
11. **REGRA:** Sempre adicionar sinal sonoro ao final de comandos longos:
    `&& powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"`
12. **REGRA:** Load do Neo4j não escala em paralelo — nunca rodar 2 pipelines de importação ao mesmo tempo
13. **REGRA:** Todo novo problema/solução descoberto deve ser registrado no próximo backup

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
1. Coleta e visualização de dados públicos
2. Mapa interativo dos 62 municípios do AM
3. Sistema de registro e acompanhamento de problemas por município
4. Dashboards para tomada de decisão política
5. Cruzamento de dados: CPF/CNPJ de políticos e empresas

---

## 🛠️ Infraestrutura

### Containers Docker
| Container | Porta | Status |
|---|---|---|
| bracc-neo4j | 7474/7687 | ✅ |
| br-acc-novo-api-1 | 8000 | ✅ |
| br-acc-novo-frontend-1 | 3000 | ✅ |

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

## ✅ STATUS ATUAL DOS DADOS (29/04/2026 ~19h)

### Neo4j — dados importados
| Tipo | Quantidade | Fonte |
|---|---|---|
| Company | 40.474.277 | CNPJ + TSE |
| Partner | 17.774.658 | CNPJ |
| Person | 1.559.007 | CNPJ + TSE + Transparência |
| GovTravel | 260.000 | Viagens ✅ |
| Expense | 430.000 | Viagens ✅ |
| Contract | 32.259 | Transparência ✅ |
| Amendment | 27.943 | Transparência ✅ |
| Election | 16.898 | TSE ✅ |
| SOCIO_DE | 18.783.607 | CNPJ ⚠️ incompleto |
| DOOU | 1.169.752 | TSE ✅ |
| CANDIDATO_EM | 463.604 | TSE ✅ |

### Importações em andamento
```
Câmara → Senado (sequencial) — rodando agora
```

### Downloads no HD
| Fonte | Tamanho | Status |
|---|---|---|
| cnpj | 28G | ✅ importado |
| tse | 33G+ | ✅ 2024 importado — 2018/2020 baixados — 2022 pendente |
| camara | 1.7G | ✅ baixado — importando agora |
| senado | 71M | ✅ baixado — na fila |
| transparencia | 1.8G | ✅ 2024 importado — 2020/2021/2022/2023 baixados |
| viagens | 7.7G | ✅ importado |
| siop | 2.4G | ✅ baixado |
| opensanctions | 2.6G | ✅ baixado |
| icij | 667M | ✅ baixado |
| siconfi | 763M | ✅ baixado |
| renuncias | 510M | ✅ baixado |
| cpgf | 50M | ✅ baixado |
| cvm_funds | 18M | ✅ baixado |
| holdings | 10M | ✅ baixado |
| ofac | 7.9M | ✅ baixado |
| un_sanctions | 2.4M | ✅ baixado |
| leniency | 292K | ✅ baixado (atualizado) |
| cvm | 652K | ✅ baixado |
| senado_cpis | 108K | ✅ baixado |
| querido_diario | 8K | ✅ importado |
| sanctions | — | ✅ baixado (CEIS 22k + CNEP 1.6k) |
| ceaf | — | ✅ baixado (4.074 expulsões) |
| pncp | 103M | 🔄 1371/4668 — pausado |
| cepim | 0 | ❌ 403 mesmo com User-Agent |
| pep_cgu | 0 | ❌ 403 mesmo com User-Agent |
| bcb | 0 | ❌ URL mudou (400) |
| eu_sanctions | 0 | ❌ 403 |
| world_bank | 0 | ❌ URLs mortas |
| datasus | 0 | ❌ precisa Visual C++ Build Tools |
| camara_inquiries | — | ❌ precisa BigQuery |
| tse_bens | — | ❌ precisa Google credentials |
| tse_filiados | — | ❌ precisa Google credentials |

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

### Correção 7 — venv corrompido (lib64)
```powershell
Remove-Item -Recurse -Force "C:\Users\Rolim\Downloads\br-acc-novo\etl\.venv"
```
```bash
cd ~/Downloads/br-acc-novo/etl && uv sync
```

### Correção 8 — wait_for_api no bootstrap ✅
```bash
cd ~/Downloads/br-acc-novo && \
sed -i 's/def wait_for_api(timeout_sec: int = 300) -> bool:/def wait_for_api(api_url: str = "http:\/\/localhost:8000\/health", timeout_sec: int = 300) -> bool:/' scripts/run_bootstrap_all.py && \
sed -i 's|with urlopen("http://localhost:8000/health", timeout=5) as response:|with urlopen(api_url, timeout=5) as response:|' scripts/run_bootstrap_all.py && \
sed -i 's/    if not wait_for_api():/    if not wait_for_api(api_url=args.api_url):/' scripts/run_bootstrap_all.py && \
sed -i 's/    parser.add_argument("--report-latest"/    parser.add_argument("--api-url", default="http:\/\/localhost:8000\/health", help="API health check URL")\n    parser.add_argument("--report-latest"/' scripts/run_bootstrap_all.py
```

### Correção 9 — User-Agent CGU ✅ NOVA (29/04/2026)
**Problema:** Downloads da CGU retornavam 403 Forbidden — servidor bloqueava scripts automáticos.
**Solução:** Adicionado User-Agent de browser no `_download_utils.py`:
```bash
sed -i 's/headers = {}/headers = {"User-Agent": "Mozilla\/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/120.0.0.0 Safari\/537.36"}/' etl/scripts/_download_utils.py
```
**Resultado:** sanctions ✅, ceaf ✅, leniency ✅ — cepim e pep_cgu ainda falham (usam cliente HTTP diferente)

**Pendente:** corrigir cepim e pep_cgu que têm cliente HTTP próprio sem usar `_download_utils.py`:
```bash
grep -n "httpx\|headers\|User-Agent" etl/scripts/download_cepim.py
grep -n "httpx\|headers\|User-Agent" etl/scripts/download_pep_cgu.py
```

---

## 🔍 DESCOBERTAS IMPORTANTES

### Load Neo4j não escala em paralelo
Rodar múltiplos pipelines de importação simultaneamente trava o Neo4j. Sempre rodar um por vez sequencialmente.

### Viagens — transformação lenta
3.9M registros = ~1h de transformação + ~15h de load. Normal — não é travamento.

### API funciona via element_id
```bash
curl "http://localhost:8000/api/v1/entity/29025187000160"  # CNPJ sem formatação ✅
curl "http://localhost:8000/api/v1/entity/by-element-id/4:...:47052943"  # ✅
curl "http://localhost:8000/api/v1/entity/4:...:28475404/connections"  # ✅
```

### Bug do frontend
`/api/v1/graph/{id}` só aceita Company, não Partner. Fix pendente.

### Caso Adail José Figueiredo Pinheiro
```
CPF: 772.677.962-49
Empresas AM: DAFIL PARTICIPACOES LTDA + VIEIRALVES EMPREENDIMENTOS LTDA
Candidato prefeito: 2016 e 2020 — Itacoatiara/AM
```

---

## ⚠️ PROBLEMAS CONHECIDOS

| # | Problema | Status |
|---|---|---|
| 1 | SOCIO_DE incompletos (18.7M vs 26.8M) | ⚠️ Pendente |
| 2 | cepim 403 — cliente HTTP próprio sem User-Agent | 🔄 Investigando |
| 3 | pep_cgu 403 — cliente HTTP próprio sem User-Agent | 🔄 Investigando |
| 4 | Bug frontend grafo vazio para pessoas | ⚠️ Pendente |
| 5 | DATASUS precisa Visual C++ Build Tools | ⚠️ Pendente |
| 6 | bcb URL mudou (400) | ⚠️ Pendente |
| 7 | eu_sanctions 403 | ⚠️ Pendente |
| 8 | world_bank URLs mortas | ⚠️ Pendente |
| 9 | camara_inquiries precisa BigQuery | ⚠️ Pendente |
| 10 | Nginx timeout volátil | ⚠️ Pendente Dockerfile |
| 11 | Usuários perdidos ao reiniciar | ⚠️ Pendente volume |

---

## 📋 ORDEM DE IMPORTAÇÃO (menor ao maior)

Após Câmara+Senado terminarem, importar nesta ordem:

```bash
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source sanctions --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ sanctions: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source ceaf --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ ceaf: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source leniency --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ leniency: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source cvm --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ cvm: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source un_sanctions --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ un_sanctions: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source ofac --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ ofac: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source holdings --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ holdings: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source cvm_funds --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ cvm_funds: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source cpgf --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ cpgf: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source senado_cpis --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ senado_cpis: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source renuncias --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ renuncias: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source icij --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ icij: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source siconfi --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ siconfi: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source tse --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ tse: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source transparencia --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ transparencia: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source siop --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ siop: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  uv run bracc-etl run --source opensanctions --neo4j-password "changeme" --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log && echo "✅ opensanctions: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  echo "🎉 TODAS IMPORTAÇÕES CONCLUÍDAS: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a ../pipeline_imports.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"
```

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

# ── Neo4j totais ──────────────────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# ── Diagnóstico rápido ────────────────────────────────────────────────
du -sh ~/Downloads/br-acc-novo/data/* | sort -h
grep -E "✅|⚠️|FALHOU" ~/Downloads/br-acc-novo/pipeline_imports.log | tail -20

# ── Ver progresso importação ──────────────────────────────────────────
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log
tail -5 ~/Downloads/br-acc-novo/pipeline_camara.log

# ── PNCP retomar ──────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_pncp.py --output-dir ../data/pncp \
  --start-date 2021-01-01 --window-days 5 --request-delay 2.0 \
  --timeout 120 --skip-existing 2>&1 | tee ../download_pncp.log && \
  echo "✅ PNCP: $(date '+%H:%M:%S')" | tee -a ../download_pncp.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# ── TSE 2022 ─────────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_tse.py --output-dir ../data/tse \
  --years 2022 --skip-existing 2>&1 | tee ../download_tse2022.log && \
  echo "✅ TSE 2022: $(date '+%H:%M:%S')" | tee -a ../download_tse2022.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# ── Backup (PowerShell) ───────────────────────────────────────────────
# docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-YYYYMMDD.tar.gz /data
```

---

## 📋 FASES DO PROJETO

| Fase | Descrição | Status |
|---|---|---|
| 1-7 | Infraestrutura + CNPJ + TSE 2024 | ✅ |
| 8 | Download massivo de fontes | ✅ ~95% |
| 9 | TSE 2022 | 🔄 pendente download |
| 10 | Importação sequencial de todas as fontes | 🔄 Câmara+Senado agora |
| 11 | Corrigir cepim/pep_cgu (User-Agent próprio) | 🔄 Investigando |
| 12 | DATASUS (Visual C++ Build Tools) | ⏳ |
| 13 | Fazer backup Neo4j atualizado | ⏳ após importações |
| 14 | Corrigir bug frontend grafo pessoas | ⏳ |
| 15 | Corrigir SOCIO_DE incompletos | ⏳ |
| 16 | PostgreSQL + tabelas AM | ⏳ |
| 17 | Metabase + dashboards | ⏳ |
| 18 | Mapa interativo 62 municípios AM | ⏳ |

---

## 📅 HISTÓRICO DE SESSÕES

| Data | O que foi feito |
|---|---|
| 20-25/04 | Infraestrutura + CNPJ + correções + patch |
| 26/04 | Pipeline CNPJ completo + backup 9.4GB |
| 27/04 | TSE 2024 importado + Câmara baixada |
| 28/04 | Downloads massivos — siconfi, siop, viagens, etc. |
| 29/04 manhã | Importação viagens (~15h load) ✅ |
| 29/04 tarde | User-Agent CGU corrigido — sanctions/ceaf/leniency ✅ |
| 29/04 noite | Câmara+Senado importando — ordem importação definida |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (3 containers rodando)
[ ] tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log
[ ] Reaplicar nginx timeout se necessário
[ ] PRÓXIMA AÇÃO: após Câmara+Senado, rodar ordem de importação completa
[ ] Investigar cepim/pep_cgu User-Agent próprio
[ ] TSE 2022 ainda não baixado
```

---

*v12 — 29/04/2026 ~19h*
*Consolida v1→v11 + sessão 29/04*
