# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v14
> Gerado em 30/04/2026 ~18h — consolida v13 + sessão 30/04 tarde
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

## ✅ STATUS ATUAL DOS DADOS (30/04/2026 ~18h)

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
| camara | 1.7G | ✅ | 🔄 | importando agora (T2) |
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
| cepim | 0 | ❌ | ❌ | 403 — cliente HTTP próprio |
| pep_cgu | 0 | ❌ | ❌ | 403 — cliente HTTP próprio |
| bcb | 0 | ❌ | ❌ | 400 — URL mudou |
| eu_sanctions | 0 | ❌ | ❌ | 403 |
| world_bank | 0 | ❌ | ❌ | URLs mortas |
| datasus | 0 | ❌ | ❌ | precisa Visual C++ Build Tools |
| camara_inquiries | — | ❌ | ❌ | precisa BigQuery |
| tse_bens | — | ❌ | ❌ | precisa Google credentials |
| tse_filiados | — | ❌ | ❌ | precisa Google credentials |

---

## 🔄 STATUS DOS TERMINAIS (30/04/2026 ~18h)

| Terminal | Fonte | Fase | Observação |
|---|---|---|---|
| T1 | PNCP download | 🔄 1637/4668 | ~4-5h restantes |
| T2 | Câmara importação | 🔄 load | 3.5M linhas — pode levar horas |

T3 e T4 livres para usar se necessário.

---

## 📋 FILA DE IMPORTAÇÃO (T2 — sequencial após câmara)

Já configurada e rodando no T2:
```
camara → senado → tse → transparencia → siconfi → icij → siop → opensanctions
```

Fontes que ainda precisam entrar na fila quando a acima terminar:
```
sanctions → ceaf → tse 2016
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
Permite baixar sanctions, ceaf, leniency. cepim e pep_cgu têm cliente HTTP próprio — ainda bloqueados.

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
| 2 | cepim 403 — cliente HTTP próprio sem User-Agent | ⚠️ Pendente |
| 3 | pep_cgu 403 — cliente HTTP próprio sem User-Agent | ⚠️ Pendente |
| 4 | Bug frontend grafo vazio para pessoas | ⚠️ Pendente |
| 5 | DATASUS precisa Visual C++ Build Tools | ⚠️ Pendente |
| 6 | bcb URL mudou (400) | ⚠️ Pendente |
| 7 | eu_sanctions 403 | ⚠️ Pendente |
| 8 | world_bank URLs mortas | ⚠️ Pendente |
| 9 | camara_inquiries precisa BigQuery | ⚠️ Pendente |
| 10 | Nginx timeout volátil | ⚠️ Pendente Dockerfile |
| 11 | Usuários perdidos ao reiniciar | ⚠️ Pendente volume |
| 12 | BCB — URL API mudou (400 Bad Request) | ⚠️ Pendente investigar nova URL |
| 13 | Scripts link_persons.cypher não existem | ⚠️ Pendente |

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
| 9 | Downloads complementares (TSE 2016, Transparência 2018/2019, BCB, EU) | ✅ parcial |
| 10 | Backup atualizado | ✅ 30/04 feito |
| 11 | Importação sequencial de todas as fontes | 🔄 câmara rodando |
| 12 | PNCP download completo | 🔄 35% |
| 13 | PNCP importação | ⏳ após download |
| 14 | Corrigir cepim/pep_cgu | ⏳ |
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
[ ] PRÓXIMA AÇÃO: aguardar fila de importação terminar → importar sanctions + ceaf + tse 2016 → aguardar PNCP → importar PNCP → backup final
```

---

*v14 — 30/04/2026 ~18h*
*Consolida v1→v13 + sessão 30/04 tarde*
*T1=PNCP download (35%), T2=Câmara importando (fila longa configurada)*
