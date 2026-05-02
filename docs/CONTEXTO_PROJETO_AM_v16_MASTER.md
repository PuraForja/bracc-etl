# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v16
> Gerado em 01/05/2026 ~23h — consolida v15 + sessão 01/05 (correções críticas nos pipelines)
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
8. **REGRA:** Baixar tudo primeiro, depois importar — nunca misturar DA MESMA FONTE simultaneamente
9. **REGRA:** Preferir texto colado em vez de prints/imagens
10. **REGRA:** Downloads podem rodar em paralelo — importações devem ser sequenciais (uma por vez no Neo4j)
11. **REGRA:** Sempre adicionar sinal sonoro ao final de comandos longos E após cada etapa concluída:
    `&& powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"`
12. **REGRA:** Load do Neo4j não escala em paralelo — nunca rodar 2 pipelines de importação ao mesmo tempo
13. **REGRA:** Todo novo problema/solução descoberto deve ser registrado no próximo backup
14. **REGRA:** NUNCA iniciar backup e importação simultaneamente no Neo4j
15. **REGRA:** Sempre verificar se o Docker Desktop está aberto antes de rodar qualquer comando Docker
16. **REGRA:** Terminais podem ter numeração invertida — sempre confirmar qual terminal está fazendo o quê antes de mandar comando
17. **REGRA:** ⚠️ AVISAR QUANDO A SESSÃO ESTIVER PRÓXIMA DO LIMITE — obrigatório gerar novo .md antes de encerrar

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
6. **Análise voto × verba:** cruzar votações da Câmara com emendas parlamentares para identificar acordos políticos

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

## ✅ STATUS ATUAL DOS DADOS (01/05/2026 ~23h)

### Neo4j — último snapshot verificado
| Tipo | Quantidade | Fonte |
|---|---|---|
| Company | 40.483.645 | CNPJ + TSE |
| Partner | 17.774.658 | CNPJ |
| Person | 1.559.007 | CNPJ + TSE + Transparência |
| Expense | 430.000 | viagens ✅ |
| TaxWaiver | 291.799 | renuncias ✅ |
| GovTravel | 260.000 | viagens ✅ |
| GovCardExpense | 131.950 | cpgf ✅ |
| Fund | 41.107 | cvm_funds ✅ |
| Contract | 32.259 | transparencia ✅ |
| Amendment | 27.943 | transparencia ✅ |
| Election | 16.898 | TSE ✅ |
| InternationalSanction | 8.435 | ofac + un_sanctions ✅ |
| Expulsion | 4.074 | ceaf ✅ |
| BarredNGO | 3.572 | cepim ✅ |
| CVMProceeding | 537 | cvm ✅ |
| LeniencyAgreement | 115 | leniency ✅ |
| Inquiry | 105 | senado_cpis ✅ |
| CPI | 105 | senado_cpis ✅ |
| MunicipalGazetteAct | 10 | querido_diario ✅ |

> Banco ocupa **~37GB** no volume Docker.

### Backup atual
```
Arquivo: neo4j-backup-20260430.tar.gz
Local:   C:\Users\Rolim\Downloads\
Data:    30/04/2026 ~17h
Status:  ⚠️ Desatualizado — fazer novo backup após fila terminar
```

---

## 📦 STATUS DE DOWNLOADS E IMPORTAÇÕES

| Fonte | Tamanho | Download | Importação | Observação |
|---|---|---|---|---|
| cnpj | 28G | ✅ | ✅ | 40M empresas |
| viagens | 7.7G | ✅ | ✅ | |
| tse | 43G | ✅ | ⏳ | na fila — último |
| transparencia | 2.7G | ✅ | ⏳ | na fila |
| siop | 2.4G | ✅ | ⏳ | na fila |
| opensanctions | 2.6G | ✅ | ⏳ | na fila |
| camara | 1.7G | ✅ | ⏳ | na fila |
| siconfi | 763M | ✅ | ⏳ | na fila |
| icij | 667M | ✅ | ⏳ | na fila |
| renuncias | 510M | ✅ | ✅ | |
| cpgf | 50M | ✅ | ✅ | |
| sanctions | 62M | ✅ | ⏳ | na fila |
| senado | 71M | ✅ | 🔄 | rodando agora — corrigido |
| cvm_funds | 18M | ✅ | ✅ | |
| holdings | 10M | ✅ | ✅ | |
| ofac | 7.9M | ✅ | ✅ | |
| ceaf | 4M | ✅ | ✅ | |
| un_sanctions | 2.4M | ✅ | ✅ | |
| bcb | 2.4M | ✅ | ✅ | baixado via API Olinda |
| cepim | 1.4M | ✅ | ✅ | 3.572 BarredNGO |
| leniency | 560K | ✅ | ✅ | |
| cvm | 652K | ✅ | ✅ | |
| senado_cpis | 108K | ✅ | ✅ | |
| querido_diario | 8K | ✅ | ✅ | |
| pncp | 109M parcial | 🔄 | ⏳ | T1 ~47% — importar após completar |
| eu_sanctions | 0 | ❌ | ❌ | IP BR bloqueado — substituído OpenSanctions |
| pep_cgu | 0 | ❌ | ❌ | autenticação obrigatória — decisão pendente |
| world_bank | 0 | ❌ | ❌ | não testado ainda |
| datasus | 0 | ❌ | ❌ | precisa Visual C++ Build Tools |

---

## 🔄 STATUS DOS TERMINAIS (01/05/2026 ~23h)

| Terminal | O que está fazendo | Observação |
|---|---|---|
| T1 | PNCP download | 🔄 ~47% (2218/4668) — não interromper |
| T2 | Fila de importação | 🔄 senado rodando agora |

**Fila atual do T2:**
```
sanctions → siconfi → icij → senado → camara → transparencia → siop → opensanctions → tse
```
(sanctions, siconfi, icij são os leves — senado em diante são os pesados corrigidos)

---

## 🔧 CORREÇÕES APLICADAS NO CÓDIGO

### Correção 1-9 — anteriores (ver v15)

### Correção 10 — CEPIM ✅ (30/04 noite)
Causa: script tentava arquivo do dia atual → 403. Solução: `--date D-1`.

### Correção 11 — BCB ✅ (30/04 noite)
URL antiga morreu. Nova API: `olinda.bcb.gov.br`. 16.394 penalidades baixadas manualmente.

### Correção 12 — `run_query` → `run_query_with_retry` ✅ (01/05)
**Problema:** Vários pipelines usavam `loader.run_query()` que mandava TODAS as relações de uma vez pro Neo4j → estourava memória → processo morria silenciosamente.

**Arquivos corrigidos:**
```
etl/src/bracc_etl/pipelines/senado.py
etl/src/bracc_etl/pipelines/camara.py
etl/src/bracc_etl/pipelines/transparencia.py
etl/src/bracc_etl/pipelines/tse.py
etl/src/bracc_etl/pipelines/sanctions.py
etl/src/bracc_etl/pipelines/cvm.py
etl/src/bracc_etl/pipelines/ibama.py
etl/src/bracc_etl/pipelines/inep.py
etl/src/bracc_etl/pipelines/tcu.py
etl/src/bracc_etl/pipelines/tesouro_emendas.py
etl/src/bracc_etl/pipelines/transferegov.py
etl/src/bracc_etl/pipelines/cnpj.py
```
**Comando usado:**
```bash
sed -i 's/loader\.run_query(/loader.run_query_with_retry(/g' ARQUIVO.py
```

### Correção 13 — `batch_size=1_000` nos pipelines grandes ✅ (01/05)
**Problema:** `Neo4jBatchLoader` tem batch_size padrão de 10.000 — muito grande para pipelines com centenas de milhares de nós → estourava memória no load.

**Arquivos corrigidos (batch_size reduzido de 10k para 1k):**
```
etl/src/bracc_etl/pipelines/senado.py
etl/src/bracc_etl/pipelines/camara.py
etl/src/bracc_etl/pipelines/transparencia.py
etl/src/bracc_etl/pipelines/tse.py
etl/src/bracc_etl/pipelines/siop.py
etl/src/bracc_etl/pipelines/opensanctions.py
```
**Comando usado:**
```bash
sed -i 's/loader = Neo4jBatchLoader(self\.driver)/loader = Neo4jBatchLoader(self.driver, batch_size=1_000)/' ARQUIVO.py
```

**Backups criados:** todos os `.py` originais têm cópia `.py.bak` no mesmo diretório.

---

## 💡 DESCOBERTAS IMPORTANTES

### Senado travava silenciosamente no load — causa raiz identificada
O pipeline do senado cria 282.027 relações GASTOU de uma vez + 272k nós Expense com batch de 10k. O Neo4j não aguentava → processo morria sem logar erro. Aconteceu 4+ vezes. Resolvido com batch_size=1_000 + run_query_with_retry.

### Como detectar travamento rápido
```bash
ps aux | grep bracc-etl | grep -v grep
# Se retornar vazio = processo morto
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log
# Se log parou há mais de 10min = travado
```

### Scripts de download vs pipelines de importação — são separados
- Download: `etl/scripts/download_FONTE.py`
- Importação: `etl/src/bracc_etl/pipelines/FONTE.py`
- Runner: `etl/src/bracc_etl/runner.py`

### Load Neo4j não escala em paralelo
Sempre sequencial — um pipeline por vez.

### NUNCA fazer backup e importação ao mesmo tempo

### CEPIM — arquivo gerado no dia anterior (D-1)
Sempre usar `--date $(date -d "yesterday" +%Y%m%d)`

### PEP CGU — autenticação obrigatória
403 em todas as datas. Usar OpenSanctions ou token Gov.br com email descartável.

### EU Sanctions — IP Brasil bloqueado
Timeout total. OpenSanctions substitui.

### BCB — migrou para API Olinda
16.394 penalidades em `../data/bcb/penalidades.csv`.
Pendente: reescrever `download_bcb.py` para usar nova API.

### API funciona via element_id
```bash
curl "http://localhost:8000/api/v1/entity/29025187000160"
curl "http://localhost:8000/api/v1/entity/by-element-id/4:...:47052943"
```

---

## ⚠️ PROBLEMAS CONHECIDOS

| # | Problema | Status |
|---|---|---|
| 1 | SOCIO_DE incompletos (18.7M vs 26.8M esperados) | ⚠️ Pendente |
| 2 | pep_cgu — autenticação obrigatória | ⚠️ Decisão pendente |
| 3 | Bug frontend grafo vazio para pessoas | ⚠️ Pendente |
| 4 | DATASUS precisa Visual C++ Build Tools | ⚠️ Pendente |
| 5 | world_bank — não testado | ⚠️ Pendente |
| 6 | download_bcb.py — precisa reescrita para API Olinda | ⚠️ Dados OK manualmente |
| 7 | download_cepim.py — precisa fallback automático D-1 | ⚠️ Funciona com --date manual |
| 8 | Nginx timeout volátil | ⚠️ Pendente Dockerfile |
| 9 | Usuários perdidos ao reiniciar | ⚠️ Pendente volume |
| 10 | Backup desatualizado — fazer após fila terminar | ⚠️ URGENTE |

---

## 💡 COMANDOS ÚTEIS

```bash
# ── Rotina diária ─────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo && docker compose up -d

# ── Verificar se importação está viva ─────────────────────────────────
ps aux | grep bracc-etl | grep -v grep
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log

# ── Verificar progresso PNCP ──────────────────────────────────────────
tail -3 ~/Downloads/br-acc-novo/download_pncp.log

# ── Fila de importação completa (ordem leve→pesado) ───────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  for FONTE in sanctions siconfi icij senado camara transparencia siop opensanctions tse; do
    echo "▶️ Iniciando $FONTE: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log
    uv run bracc-etl run --source $FONTE --neo4j-password "changeme" \
      --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log
    echo "✅ $FONTE concluído: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log
    powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"
  done && \
  echo "🎉 FILA COMPLETA: $(date '+%H:%M:%S')" | tee -a ../pipeline_imports.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"

# ── Importar fonte individual ─────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source FONTE --neo4j-password "changeme" \
  --data-dir ../data 2>&1 | tee ../pipeline_FONTE.log && \
  echo "✅ FONTE: $(date '+%H:%M:%S')" && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# ── Neo4j totais ──────────────────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# ── Tamanho do banco ──────────────────────────────────────────────────
docker system df -v | grep neo4j-data

# ── CEPIM (sempre D-1) ────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_cepim.py --output-dir ../data/cepim \
  --date $(date -d "yesterday" +%Y%m%d) 2>&1 | tee ../download_cepim.log

# ── BCB download manual (até reescrita do script) ─────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && python3 - <<'EOF'
import urllib.request, json, csv
from pathlib import Path
API_BASE = "https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata"
ENDPOINT = "QuadroGeralProcessoAdministrativoSancionador"
PAGE_SIZE = 500
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
all_records = []
skip = 0
while True:
    url = f"{API_BASE}/{ENDPOINT}?$format=json&$top={PAGE_SIZE}&$skip={skip}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    records = data.get("value", [])
    if not records:
        break
    all_records.extend(records)
    print(f"  Baixados: {len(all_records)} registros...")
    if len(records) < PAGE_SIZE:
        break
    skip += PAGE_SIZE
out = Path("../data/bcb")
out.mkdir(parents=True, exist_ok=True)
csv_path = out / "penalidades.csv"
keys = list(all_records[0].keys())
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=keys, delimiter=";")
    writer.writeheader()
    writer.writerows(all_records)
print(f"✅ BCB: {len(all_records)} penalidades salvas")
EOF

# ── Backup Neo4j (NUNCA simultâneo com importação!) ───────────────────
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup \
  alpine tar czf /backup/neo4j-backup-YYYYMMDD.tar.gz /data && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"

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

# ── PNCP retomar download ─────────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_pncp.py --output-dir ../data/pncp \
  --start-date 2021-01-01 --window-days 5 --request-delay 2.0 \
  --timeout 120 --skip-existing 2>&1 | tee ../download_pncp.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"
```

---

## 📋 FASES DO PROJETO

| Fase | Descrição | Status |
|---|---|---|
| 1-7 | Infraestrutura + CNPJ + TSE 2024 | ✅ |
| 8 | Download massivo de fontes | ✅ 95%+ |
| 9 | Downloads complementares | ✅ parcial |
| 10 | Backup 30/04 | ✅ |
| 11 | Importação sequencial de todas as fontes | 🔄 rodando |
| 12 | PNCP download completo | 🔄 47% |
| 13 | PNCP importação | ⏳ após download |
| 14 | Backup atualizado após fila | ⏳ URGENTE |
| 15 | Corrigir scripts download (bcb, pep, world_bank) | ⏳ mapeado |
| 16 | DATASUS | ⏳ |
| 17 | Corrigir bug frontend grafo pessoas | ⏳ |
| 18 | Corrigir SOCIO_DE incompletos | ⏳ |
| 19 | PostgreSQL + tabelas AM | ⏳ |
| 20 | Metabase + dashboards | ⏳ |
| 21 | Mapa interativo 62 municípios AM | ⏳ |
| 22 | Análise voto × verba | ⏳ |

---

## 📅 HISTÓRICO DE SESSÕES

| Data | O que foi feito |
|---|---|
| 20-25/04 | Infraestrutura + CNPJ + correções + patch |
| 26/04 | Pipeline CNPJ completo + backup 9.4GB |
| 27/04 | TSE 2024 importado + Câmara baixada |
| 28/04 | Downloads massivos — siconfi, siop, viagens, etc. |
| 29/04 manhã | Importação viagens ✅ |
| 29/04 tarde | User-Agent CGU corrigido ✅ |
| 29/04 noite | Câmara+Senado importando |
| 30/04 manhã | Queda de luz — banco OK (37.1GB) |
| 30/04 tarde | Backup feito ✅ — TSE 2016 + Transp baixados — PNCP 35% |
| 30/04 noite | CEPIM ✅ + BCB ✅ resolvidos — EU Sanctions ❌ — PEP ❌ |
| 01/05 | Correção crítica: run_query→run_query_with_retry + batch_size=1_000 em todos os pipelines grandes. Senado travava 4x — causa raiz identificada e resolvida. Fila rodando. |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] Abrir Docker Desktop (barra de tarefas)
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (3 containers rodando)
[ ] ps aux | grep bracc-etl (ver se fila ainda está viva)
[ ] tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log (ver o que terminou)
[ ] tail -3 ~/Downloads/br-acc-novo/download_pncp.log (ver progresso PNCP)
[ ] Se fila morreu: relançar com comando da fila acima
[ ] Após fila terminar: fazer backup ANTES de qualquer outra coisa
[ ] Após backup: importar PNCP quando download terminar
[ ] Decidir pep_cgu: token email descartável ou OpenSanctions
[ ] Investigar world_bank URL
```

---

## 📎 ARQUIVOS DE REFERÊNCIA

Manter sempre os 3 arquivos juntos:
- `CONTEXTO_PROJETO_AM_v16_MASTER.md` — este arquivo
- `CORRECOES_SCRIPTS_DOWNLOAD.md` — correções nos scripts de download
- `URLS_CORRETAS.md` — mapa de URLs corretas por fonte

---

*v16 — 01/05/2026 ~23h*
*Correção crítica: batch_size + run_query_with_retry em todos os pipelines*
*T1=PNCP ~47% | T2=fila rodando (senado→...→tse)*
*Backup URGENTE após fila terminar*
