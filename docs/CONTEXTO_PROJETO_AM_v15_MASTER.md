# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v15
> Gerado em 30/04/2026 ~19h30 — consolida v14 + sessão 30/04 noite (downloads corrigidos)
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
   - Deputado votou SIM → recebeu emenda logo depois?
   - Emenda para prefeitura → prefeito tem empresa no CNPJ?

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

## ✅ STATUS ATUAL DOS DADOS (30/04/2026 ~19h30)

### Neo4j — snapshot após backup 30/04
| Tipo | Quantidade | Fonte |
|---|---|---|
| Company | 40.483.324 | CNPJ + TSE |
| Partner | 17.774.658 | CNPJ |
| Person | 1.559.007 | CNPJ + TSE + Transparência |
| TaxWaiver | 291.799 | renuncias ✅ |
| GovTravel | 260.000 | viagens ✅ |
| Expense | 430.000 | viagens ✅ |
| GovCardExpense | 131.950 | cpgf ✅ |
| Fund | 41.107 | cvm_funds ✅ |
| Contract | 32.259 | transparencia ✅ |
| Amendment | 27.943 | transparencia ✅ |
| Election | 16.898 | TSE ✅ |
| InternationalSanction | 8.435 | ofac + un_sanctions ✅ |
| CVMProceeding | 537 | cvm ✅ |
| LeniencyAgreement | 115 | leniency ✅ |
| Inquiry | 105 | senado_cpis ✅ |
| CPI | 105 | senado_cpis ✅ |
| MunicipalGazetteAct | 10 | querido_diario ✅ |
| SOCIO_DE | 18.783.607 | CNPJ ⚠️ incompleto |
| DOOU | 1.706.319 | TSE ✅ |
| CANDIDATO_EM | 492.706 | TSE ✅ |
| HOLDING_DE | 158.902 | holdings ✅ |
| RECEBEU_RENUNCIA | 18.472 | renuncias ✅ |

> Banco ocupa **37.1GB** no volume Docker.

### Backup atual
```
Arquivo: neo4j-backup-20260430.tar.gz
Local:   C:\Users\Rolim\Downloads\
Data:    30/04/2026 ~17h
Status:  ✅ ATUAL — feito hoje
```

---

## 📦 STATUS DE DOWNLOADS E IMPORTAÇÕES

| Fonte | Tamanho | Download | Importação | Observação |
|---|---|---|---|---|
| cnpj | 28G | ✅ | ✅ | 40M empresas |
| tse 2024 | — | ✅ | ✅ | |
| tse 2016 | — | ✅ | ⏳ | baixado hoje |
| tse 2018/2020/2022 | 33G | ✅ | ⏳ | na fila |
| camara | 1.7G | ✅ | 🔄 | importando (T2) — 3.35M expenses, 1773 deputados |
| senado | 71M | ✅ | ⏳ | na fila após câmara |
| transparencia 2018/2019 | — | ✅ | ⏳ | baixado hoje |
| transparencia 2020/2021/2022/2023/2024 | 1.8G | ✅ | ⏳ | na fila |
| viagens | 7.7G | ✅ | ✅ | |
| renuncias | 510M | ✅ | ✅ | 291k waivers |
| cpgf | 50M | ✅ | ✅ | |
| leniency | 292K | ✅ | ✅ | |
| cvm | 652K | ✅ | ✅ | |
| cvm_funds | 18M | ✅ | ✅ | |
| holdings | 10M | ✅ | ✅ | |
| ofac | 7.9M | ✅ | ✅ | |
| un_sanctions | 2.4M | ✅ | ✅ | |
| opensanctions | 2.6G | ✅ | ⏳ | na fila |
| icij | 667M | ✅ | ⏳ | na fila |
| siop | 2.4G | ✅ | ⏳ | na fila |
| siconfi | 763M | ✅ | ⏳ | na fila |
| sanctions (CEIS+CNEP) | — | ✅ | ⏳ | na fila |
| ceaf | — | ✅ | ⏳ | 4.074 expulsões |
| senado_cpis | 108K | ✅ | ✅ | |
| querido_diario | 8K | ✅ | ✅ | |
| pncp | 103M+ | 🔄 | ⏳ | T1 — 1637/4668 (~35%) |
| **cepim** | 0.1MB | **✅ RESOLVIDO** | ⏳ | 3.572 registros — usar `--date 20260429` |
| **bcb** | ~5MB | **✅ RESOLVIDO** | ⏳ | 16.394 penalidades — nova API Olinda |
| **eu_sanctions** | — | ❌ bloqueado BR | ❌ | Timeout — IP Brasil bloqueado. Usar OpenSanctions |
| **pep_cgu** | — | ❌ bloqueado | ❌ | 403 em todas as datas — requer token ou OpenSanctions |
| **world_bank** | — | ⏳ investigar | ❌ | URLs legadas — ver CORRECOES_SCRIPTS_DOWNLOAD.md |
| datasus | 0 | ❌ | ❌ | precisa Visual C++ Build Tools |
| camara_inquiries | — | ❌ | ❌ | precisa BigQuery |
| tse_bens | — | ❌ | ❌ | precisa Google credentials |
| tse_filiados | — | ❌ | ❌ | precisa Google credentials |

---

## 🔄 STATUS DOS TERMINAIS (30/04/2026 ~19h30)

| Terminal | Fonte | Fase | Observação |
|---|---|---|---|
| T1 | PNCP download | 🔄 1637/4668 | ~4-5h restantes |
| T2 | Câmara importação | 🔄 load | 3.35M linhas — em andamento |
| T3/T4 | Livres | — | Disponíveis |

---

## 📋 FILA DE IMPORTAÇÃO (T2 — sequencial após câmara)

Já configurada e rodando no T2:
```
camara → senado → tse → transparencia → siconfi → icij → siop → opensanctions
```

Fontes que ainda precisam entrar na fila quando a acima terminar:
```
sanctions → ceaf → tse 2016 → cepim → bcb
```

Comando completo já rodando no T2 — não interromper!

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
Função atualizada para aceitar `api_url` como parâmetro.

### Correção 9 — User-Agent CGU ✅
Permite baixar sanctions, ceaf, leniency. cepim e pep_cgu tinham cliente HTTP próprio — resolvidos separadamente.

### Correção 10 — CEPIM ✅ (sessão 30/04 noite)
**Causa:** Script tentava arquivo do dia atual (não gerado ainda) → 403.
**Solução:** Passar `--date 20260429` (D-1). Sem alteração de código necessária.
**Comando:**
```bash
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_cepim.py --output-dir ../data/cepim \
  --date 20260429 2>&1 | tee ../download_cepim.log && \
  powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"
```
**Resultado:** 3.572 registros ✅

### Correção 11 — BCB Penalidades ✅ (sessão 30/04 noite)
**Causa:** URL antiga `https://www3.bcb.gov.br/rdrweb/rest/ext/ranking/arquivo?tipo=2` morreu (400).
**Solução:** BCB migrou para API Olinda. Download manual com paginação funcionou.
**URL nova:** `https://olinda.bcb.gov.br/olinda/servico/Gepad_QuadroPenalidades/versao/v1/odata/QuadroGeralProcessoAdministrativoSancionador?$format=json`
**Resultado:** 16.394 penalidades salvas em `../data/bcb/penalidades.csv` ✅
**Pendente:** Reescrever `download_bcb.py` para usar nova API permanentemente (ver CORRECOES_SCRIPTS_DOWNLOAD.md)

---

## 💡 DESCOBERTAS IMPORTANTES

### Load Neo4j não escala em paralelo
Rodar múltiplos pipelines de importação simultaneamente trava o Neo4j. Sempre rodar um por vez sequencialmente.

### NUNCA fazer backup e importação ao mesmo tempo
São operações conflitantes no Neo4j — esperar backup terminar antes de importar.

### Docker Desktop deve estar aberto
Antes de qualquer comando Docker, verificar se o Docker Desktop está rodando na barra de tarefas.

### Viagens — transformação lenta
3.9M registros = ~1h de transformação + load longo. Normal — não é travamento.

### CEPIM — arquivo gerado no dia anterior (D-1)
O arquivo de hoje nunca está disponível — sempre usar data de ontem.
Arquivo fica em: `dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/cepim/YYYYMMDD_CEPIM.zip`

### PEP CGU — autenticação obrigatória
Testado 60 dias para trás — 403 em todas as datas. Não é problema de data.
Requer token da CGU (cadastro em portaldatransparencia.gov.br/api-de-dados/cadastrar-email com Gov.br nível Prata/Ouro).
Alternativa: usar OpenSanctions (já importado) que agrega PEP brasileiro.

### EU Sanctions — IP Brasil bloqueado
Timeout de conexão — servidor da Europa inacessível a partir do Brasil.
OpenSanctions substitui (já baixado e importado).

### BCB — migrou para API Olinda
Dados ricos: CNPJ, nome, tipo de penalidade, valor da multa, situação, 1ª e 2ª instância.
16.394 penalidades — útil para cruzar com contratos públicos e doações.

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
| 1 | SOCIO_DE incompletos (18.7M vs 26.8M esperados) | ⚠️ Pendente |
| 2 | pep_cgu 403 — requer token CGU ou usar OpenSanctions | ⚠️ Decisão pendente |
| 3 | Bug frontend grafo vazio para pessoas | ⚠️ Pendente |
| 4 | DATASUS precisa Visual C++ Build Tools | ⚠️ Pendente |
| 5 | eu_sanctions — IP BR bloqueado — usar OpenSanctions | ⚠️ Substituído |
| 6 | world_bank — investigar nova URL | ⚠️ Pendente |
| 7 | camara_inquiries precisa BigQuery | ⚠️ Pendente |
| 8 | Nginx timeout volátil | ⚠️ Pendente Dockerfile |
| 9 | Usuários perdidos ao reiniciar | ⚠️ Pendente volume |
| 10 | Scripts link_persons.cypher não existem | ⚠️ Pendente |
| 11 | download_bcb.py — precisa reescrita para API Olinda | ⚠️ Dados já baixados manualmente |
| 12 | download_cepim.py — precisa fallback automático D-1 | ⚠️ Funciona com --date manual |

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

docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH ()-[r]->() RETURN type(r) as tipo, count(r) as total ORDER BY total DESC"

# ── Tamanho do banco ──────────────────────────────────────────────────
docker system df -v | grep neo4j-data

# ── Diagnóstico rápido ────────────────────────────────────────────────
du -sh ~/Downloads/br-acc-novo/data/* | sort -h
grep -E "✅|⚠️|FALHOU" ~/Downloads/br-acc-novo/pipeline_imports.log | tail -20

# ── Ver progresso importação ──────────────────────────────────────────
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log

# ── Ver progresso PNCP ────────────────────────────────────────────────
tail -3 ~/Downloads/br-acc-novo/download_pncp.log

# ── PNCP retomar ──────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_pncp.py --output-dir ../data/pncp \
  --start-date 2021-01-01 --window-days 5 --request-delay 2.0 \
  --timeout 120 --skip-existing 2>&1 | tee ../download_pncp.log && \
  echo "✅ PNCP: $(date '+%H:%M:%S')" | tee -a ../download_pncp.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# ── CEPIM (usar sempre D-1) ───────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run python scripts/download_cepim.py --output-dir ../data/cepim \
  --date $(date -d "yesterday" +%Y%m%d) 2>&1 | tee ../download_cepim.log && \
  powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"

# ── BCB (download manual via API Olinda — até reescrita do script) ────
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
if all_records:
    keys = list(all_records[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter=";")
        writer.writeheader()
        writer.writerows(all_records)
    print(f"✅ BCB: {len(all_records)} penalidades salvas em {csv_path}")
EOF

# ── Backup Neo4j (PowerShell — NUNCA simultaneo com importação!) ──────
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup \
  alpine tar czf /backup/neo4j-backup-YYYYMMDD.tar.gz /data && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"

# ── Importar fonte individual ─────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source FONTE --neo4j-password "changeme" \
  --data-dir ../data 2>&1 | tee ../pipeline_FONTE.log && \
  echo "✅ FONTE: $(date '+%H:%M:%S')" | tee -a ../pipeline_FONTE.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"
```

---

## 📋 FASES DO PROJETO

| Fase | Descrição | Status |
|---|---|---|
| 1-7 | Infraestrutura + CNPJ + TSE 2024 | ✅ |
| 8 | Download massivo de fontes | ✅ 95%+ |
| 9 | Downloads complementares | ✅ parcial |
| 10 | Backup atualizado | ✅ 30/04 feito |
| 11 | Importação sequencial de todas as fontes | 🔄 câmara rodando |
| 12 | PNCP download completo | 🔄 35% |
| 13 | PNCP importação | ⏳ após download |
| 14 | Corrigir scripts download (bcb, pep, world_bank) | ⏳ mapeado |
| 15 | DATASUS (Visual C++ Build Tools) | ⏳ |
| 16 | Corrigir bug frontend grafo pessoas | ⏳ |
| 17 | Corrigir SOCIO_DE incompletos | ⏳ |
| 18 | PostgreSQL + tabelas AM | ⏳ |
| 19 | Metabase + dashboards | ⏳ |
| 20 | Mapa interativo 62 municípios AM | ⏳ |
| 21 | Análise voto × verba | ⏳ |

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
| 30/04 manhã | Queda de luz — câmara não terminou — banco OK (37.1GB) |
| 30/04 tarde | Docker restart — backup 30/04 feito ✅ — TSE 2016 + Transp 2018/2019 baixados — câmara reimportando — PNCP 35% |
| 30/04 noite | CEPIM ✅ resolvido (3.572 reg, D-1) — BCB ✅ 16.394 penalidades via API Olinda — EU Sanctions ❌ IP BR bloqueado — PEP CGU ❌ autenticação obrigatória — Mapa correções criado |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] Abrir Docker Desktop primeiro (barra de tarefas)
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (3 containers rodando)
[ ] tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log (ver o que terminou)
[ ] tail -3 ~/Downloads/br-acc-novo/download_pncp.log (ver progresso PNCP)
[ ] Reaplicar nginx timeout se necessário
[ ] Recriar usuário frontend se necessário
[ ] PRÓXIMA AÇÃO: aguardar fila de importação terminar → importar sanctions + ceaf + tse 2016 + cepim + bcb → aguardar PNCP → importar PNCP → backup final
[ ] CORREÇÕES PENDENTES: reescrever download_bcb.py + download_cepim.py (fallback D-1) + investigar world_bank + decidir pep_cgu (token ou OpenSanctions)
```

---

## 📎 ARQUIVOS DE REFERÊNCIA

Manter sempre os 3 arquivos juntos:
- `CONTEXTO_PROJETO_AM_v15_MASTER.md` — este arquivo (contexto geral)
- `CORRECOES_SCRIPTS_DOWNLOAD.md` — correções pendentes nos scripts de download
- `URLS_CORRETAS.md` — mapa de URLs corretas por fonte

---

*v15 — 30/04/2026 ~19h30*
*Consolida v14 + sessão 30/04 noite*
*T1=PNCP download (35%), T2=Câmara importando (fila longa configurada)*
*Novidade: CEPIM ✅ + BCB ✅ resolvidos | EU Sanctions + PEP CGU bloqueados*
