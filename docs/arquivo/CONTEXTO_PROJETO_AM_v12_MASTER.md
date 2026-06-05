# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v12
> Gerado em 29/04/2026 madrugada — consolida v11 + sessão 29/04 madrugada
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
9. **REGRA:** Nunca rodar download e importação da MESMA FONTE simultaneamente — baixar tudo de uma fonte primeiro, depois importar. Fontes diferentes podem rodar em paralelo.
10. **REGRA:** Preferir texto colado em vez de prints/imagens para economizar contexto de sessão
11. **REGRA:** Gerar novo contexto (.md) proativamente quando a conversa estiver longa
12. **REGRA:** Avisar Alberto com antecedência quando a conversa estiver ficando longa
13. **REGRA:** Quando algo demorar mais de 1 minuto sem output, é sinal de travamento — avisar
14. **REGRA:** Usar `grep -E "✅|⚠️" <log> && du -sh data/*` como diagnóstico rápido
15. **REGRA:** Downloads podem rodar em paralelo em terminais separados — organizar assim
16. **REGRA:** Sempre adicionar sinal sonoro ao final dos comandos longos:
    `&& powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"`
17. **REGRA:** Quando todos os terminais terminarem → gerar novo .md de contexto + sugerir backup Neo4j

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

## ✅ STATUS ATUAL DOS DADOS (29/04/2026 madrugada)

### Neo4j (banco atual)
| Tipo | Quantidade | Status |
|---|---|---|
| Company | 40.467.322 | ✅ CNPJs corretos |
| Partner | 17.774.658 | ✅ |
| Person | 1.090.627+ | ✅ TSE 2024 + 2018/2020/2022 importados |
| Election | 16.707+ | ✅ |
| SOCIO_DE | 18.783.607 | ⚠️ Incompleto (esperado 26.8M) |
| DOOU | 1.169.752+ | ✅ 2024 + histórico importado |
| CANDIDATO_EM | 463.604+ | ✅ |
| Transparência | 137.924 | ✅ recém importado |
| TSE histórico | 1.827.050 | ✅ recém importado |

> ⚠️ Números aproximados — fazer query no Neo4j para confirmar totais exatos após todas importações.

### Backup do banco
```
Arquivo: neo4j-backup-20260426.tar.gz
Local:   C:\Users\Rolim\Downloads\
Tamanho: 9.4GB
```
> ⚠️ Backup DESATUALIZADO — fazer novo backup assim que todas as importações terminarem!

### Downloads — Status Detalhado

| Fonte | Tamanho | Status | Observação |
|---|---|---|---|
| cnpj | 28G | ✅ importado | 40M empresas |
| tse 2024 | — | ✅ importado | 1.09M candidatos |
| tse 2018/2020/2022 | 13G+ | ✅ importado | 1.827M registros |
| camara | 1.7G | 🔄 importando (T4) | 18 anos (2009-2026) |
| senado | 71M | 🔄 importando (T2) | 14 anos |
| transparencia 2020/2021/2022 | — | ✅ importado | 137k registros |
| transparencia 2023 | — | ✅ baixado | aguarda importação |
| transparencia 2024 | — | ✅ importado | anterior |
| viagens | 7.7G | 🔄 importando (T3) | 3.9M viagens 2020-2026 |
| leniency | 292K | ✅ baixado | aguarda importação |
| cpgf | 50M | ✅ baixado | aguarda importação |
| tesouro_emendas | 61M | ✅ baixado | aguarda importação |
| siop | 2.4G | ✅ baixado | 4.7M linhas emendas 2020-2024 |
| cvm | 652K | ✅ baixado | aguarda importação |
| cvm_funds | 18M | ✅ baixado | aguarda importação |
| icij | 667M | ✅ baixado | Panama/Pandora Papers |
| ofac | 7.9M | ✅ baixado | aguarda importação |
| un_sanctions | 2.4M | ✅ baixado | aguarda importação |
| opensanctions | 2.6G | ✅ baixado | aguarda importação |
| holdings | 10M | ✅ baixado | aguarda importação |
| renuncias | 510M | ✅ baixado | aguarda importação |
| querido_diario | — | ✅ baixado | aguarda importação |
| senado_cpis | — | ✅ baixado | aguarda importação |
| siconfi | 763M | ✅ baixado | estados + municípios 2020-2024 |
| pncp | — | 🔄 baixando (T1) | ~678/4668 combos |
| sanctions (CGU) | 0 | ❌ | 403 Forbidden |
| cepim | 0 | ❌ | 403 Forbidden |
| ceaf | 0 | ❌ | 403 Forbidden |
| pep_cgu | 0 | ❌ | 403 Forbidden |
| bcb | 0 | ❌ | 400 Bad Request — URL mudou |
| eu_sanctions | 0 | ❌ | 403 Forbidden |
| world_bank | 0 | ❌ | URLs mortas |
| camara_inquiries | — | ❌ | Precisa BigQuery |
| datasus | — | ❌ | Precisa Visual C++ Build Tools |

---

## 🔄 STATUS DOS TERMINAIS (29/04/2026 ~01:22)

| Terminal | Fonte | Status |
|---|---|---|
| T1 | PNCP download | 🔄 rodando |
| T2 | Senado importação | 🔄 rodando |
| T3 | Viagens importação | 🔄 rodando |
| T4 | Câmara importação | 🔄 rodando |

---

## 📋 FILA DE IMPORTAÇÃO (após terminais liberarem)

Ordem sugerida:
1. siop
2. siconfi
3. leniency
4. cpgf
5. tesouro_emendas
6. cvm + cvm_funds
7. ofac + un_sanctions + opensanctions
8. icij
9. holdings
10. renuncias
11. querido_diario
12. senado_cpis
13. pncp (quando download terminar)

---

## 🔧 COMANDOS ÚTEIS

```bash
# ── Importar fonte no Neo4j ───────────────────────────────────────────
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  uv run bracc-etl run --source FONTE --neo4j-password "changeme" \
  --data-dir ../data 2>&1 | tee ../pipeline_FONTE.log && \
  echo "✅ FONTE importado: $(date '+%H:%M:%S')" | tee -a ../pipeline_FONTE.log && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

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

# ── Neo4j — contar nós ────────────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# ── Neo4j — contar relações ───────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH ()-[r]->() RETURN type(r) as tipo, count(r) as total ORDER BY total DESC"

# ── Diagnóstico rápido ────────────────────────────────────────────────
du -sh ~/Downloads/br-acc-novo/data/* | sort -h

# ── Verificar PNCP ────────────────────────────────────────────────────
wc -l ~/Downloads/br-acc-novo/data/pncp/.checkpoint

# ── Backup Neo4j (rodar quando todas importações terminarem!) ─────────
docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup \
  alpine tar czf /backup/neo4j-backup-20260429.tar.gz /data && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1200,500); [console]::beep(1500,1000)"
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

### Análise voto × verba (planejada)
Cruzar votações da Câmara com emendas parlamentares para identificar acordos:
- Deputado votou SIM → recebeu emenda logo depois?
- Emenda para prefeitura → prefeito tem empresa no CNPJ?
- Dados necessários: Câmara ✅ + SIOP ✅ + Transparência ✅

### DATASUS — bloqueado
PySUS precisa compilar `cffi` que requer Microsoft Visual C++ 14.0+.

### PNCP — instável mas funcionando
Script tem checkpoint robusto. Usar `--window-days 5 --request-delay 2.0`.

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
| 8 | Download massivo de fontes | ✅ ~95% |
| 9 | TSE 2018/2020/2022 baixado e importado | ✅ |
| 10 | PNCP baixando | 🔄 ~14% |
| 11 | Transparência 2020/2021/2022/2023 baixada e importada | ✅ |
| 12 | Câmara importando | 🔄 |
| 13 | Senado importando | 🔄 |
| 14 | Viagens importando | 🔄 |
| 15 | **Importar fontes restantes** | ⏳ Próxima etapa |
| 16 | **Backup Neo4j atualizado** | ⏳ Urgente após importações |
| 17 | Corrigir bug frontend grafo | ⏳ |
| 18 | Corrigir SOCIO_DE incompletos | ⏳ |
| 19 | Nginx/usuários permanentes | ⏳ |
| 20 | PostgreSQL + tabelas AM | ⏳ |
| 21 | Metabase + dashboards | ⏳ |
| 22 | Mapa interativo 62 municípios | ⏳ |
| 23 | Análise voto × verba | ⏳ |

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
| 28/04 noite | PNCP retomado — TSE 2018/2020/2022 baixando — Transparência 2023 ✅ |
| 29/04 madrugada | TSE histórico importado (1.8M) — Transparência importada (137k) — Câmara/Senado/Viagens importando |

---

## ⚠️ CHECKLIST AO INICIAR NOVA SESSÃO

```
[ ] cd ~/Downloads/br-acc-novo && docker compose up -d
[ ] docker ps (3 containers rodando)
[ ] Verificar downloads: wc -l data/pncp/.checkpoint && du -sh data/tse/
[ ] Reaplicar nginx timeout se necessário
[ ] Recriar usuário frontend se necessário
[ ] PRÓXIMA ETAPA: importar fontes restantes (siop, siconfi, leniency, cpgf, cvm, icij, ofac, sanctions, holdings, renuncias, pncp)
[ ] URGENTE: fazer backup Neo4j após todas importações terminarem
```

---

*v12 — 29/04/2026 madrugada*
*Consolida v1→v11 + sessão 29/04 madrugada*
*4 terminais rodando: T1=PNCP download, T2=Senado import, T3=Viagens import, T4=Câmara import*
