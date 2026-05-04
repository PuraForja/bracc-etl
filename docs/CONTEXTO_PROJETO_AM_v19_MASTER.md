# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v19
> Gerado em 03/05/2026 ~23h50
> Cole este arquivo ou use o PROMPT_INICIALIZACAO_IA.md no início de qualquer nova sessão.

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
3. Após qualquer alteração de código → atualize o CHANGELOG → commite no GitHub
4. Ao final de cada sessão → gere novo MASTER .md e commite
5. **Sempre inclua data/hora nos comandos de log**
6. **⚠️ Avise quando a sessão estiver no limite — OBRIGATÓRIO**
7. **Nunca reescreva scripts usando `requests` puro — sempre use `_download_utils.py`**
8. **Confirme alterações antes de executar — evita bagunça**

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

## ✅ STATUS NEO4J (03/05/2026 ~23h)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.483.645+ | ✅ |
| Partner | 17.774.658 | ✅ |
| Person | 1.559.007+ | ✅ |
| Expense | 430.000 | ⚠️ só viagens — câmara ainda pendente |
| TaxWaiver | 291.799 | ✅ |
| GovTravel | 260.000 | ✅ |
| GovCardExpense | 131.950 | ✅ |
| Fund | 41.107 | ✅ |
| Contract | 32.259 | ✅ |
| Amendment | 27.943 | ✅ |
| Election | 16.898 | ✅ |
| InternationalSanction | 8.435+ | ✅ |
| Expulsion | 4.074 | ✅ ceaf |
| BarredNGO | 3.572 | ✅ cepim |
| CVMProceeding | 537 | ✅ |
| LeniencyAgreement | 115 | ✅ |
| Inquiry/CPI | 105 | ✅ |
| MunicipalGazetteAct | 10 | ✅ |

**Importados em 02/05:** sanctions ✅ + siconfi ✅ + icij ✅ + senado ✅

**Backup:** neo4j-backup-20260430.tar.gz — 🔴 URGENTE fazer após câmara importar

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
| camara 1.7G | ✅ | ❌ | morrendo no load — problema memória/constraints |
| siconfi 763M | ✅ | ✅ | importado 02/05 |
| icij 667M | ✅ | ✅ | importado 02/05 |
| senado 71M | ✅ | ✅ | importado 02/05 |
| sanctions 62M | ✅ | ✅ | importado 02/05 |
| renuncias 510M | ✅ | ✅ | |
| cpgf 50M | ✅ | ✅ | |
| cvm_funds 18M | ✅ | ✅ | |
| holdings 10M | ✅ | ✅ | |
| ofac 7.9M | ✅ | ✅ | |
| ceaf 4M | ✅ | ✅ | |
| un_sanctions 2.4M | ✅ | ✅ | |
| bcb 2.4M | ✅ | ✅ | API Olinda manual |
| cepim 1.4M | ✅ | ✅ | |
| leniency 560K | ✅ | ✅ | |
| cvm 652K | ✅ | ✅ | |
| senado_cpis 108K | ✅ | ✅ | |
| querido_diario 8K | ✅ | ✅ | |
| pncp parcial | 🔄 ~47% | ⏳ | importar após download |
| eu_sanctions | ❌ | ❌ | IP BR bloqueado — usar OpenSanctions |
| pep_cgu | ❌ | ❌ | autenticação obrigatória — decisão pendente |
| world_bank | ❌ | ❌ | não testado |
| datasus | ❌ | ❌ | precisa Visual C++ |

---

## 🔴 PROBLEMA CRÍTICO — CÂMARA

A câmara (3.35M expenses) morre silenciosamente no load mesmo com batch_size=500.

**Histórico de tentativas:**
| batch_size | Resultado |
|---|---|
| 10.000 (padrão) | ❌ |
| 1.000 | ❌ |
| 500 | ❌ |
| 250 | próximo passo |

**Causa provável (análise arquitetural):**
- Neo4j usando ~26GB deixa só 6GB para Windows + Python → SO mata processo (OOM)
- Falta de CONSTRAINTS força Full Scan em 40M+ nós a cada MERGE

**Solução pendente — 3 passos:**
1. Verificar memória atual do Neo4j:
```bash
docker stats bracc-neo4j --no-stream && \
grep -i "heap\|memory\|Xms\|Xmx" ~/Downloads/br-acc-novo/docker-compose.yml
```
2. Limitar heap Neo4j para 20GB no docker-compose.yml
3. Criar constraints únicas:
```cypher
CREATE CONSTRAINT company_cnpj IF NOT EXISTS FOR (c:Company) REQUIRE c.cnpj IS UNIQUE;
CREATE CONSTRAINT person_cpf IF NOT EXISTS FOR (p:Person) REQUIRE p.cpf IS UNIQUE;
```

**ANTES de implementar:** diagnosticar com o comando acima para confirmar hipótese.

---

## 🔧 ARQUITETURA DOS SCRIPTS DE DOWNLOAD

```
_download_utils.py              ← BASE — nunca reescrever com requests puro
    ├── download_file()         retomada, streaming, User-Agent, httpx
    ├── extract_zip()           proteção ZIP bombs
    ├── validate_csv()          validação de colunas
    └── find_latest_date()      ← NOVO 03/05 — fallback de datas (7 dias)

download_FONTE.py               ← cada fonte tem seu script
    ├── importa _download_utils ← OBRIGATÓRIO
    ├── URL específica
    ├── find_latest_date()      ← usar para fontes com atualização diária
    └── mapeamento de colunas
```

**Scripts já corrigidos com find_latest_date:**
- `download_cepim.py` ✅
- `download_pep_cgu.py` ✅

**Scripts pendentes de correção** (ver CORRECOES_SCRIPTS_DOWNLOAD.md):
- `download_bcb.py` — reescrever para API Olinda
- `download_transparencia.py` — loop de meses para trás
- `download_world_bank.py` — testar URL legada

---

## 🔧 CORREÇÕES NO CÓDIGO — RESUMO

| Data | Correção | Arquivos | Status |
|---|---|---|---|
| 03/05 | `find_latest_date` centralizado | `_download_utils.py` | ✅ commitado |
| 03/05 | fallback 7 dias CEPIM | `download_cepim.py` | ✅ commitado |
| 03/05 | fallback 7 dias PEP | `download_pep_cgu.py` | ✅ commitado |
| 03/05 | restauração scripts outra IA | cepim + pep | ✅ commitado |
| 02/05 | batch_size 1_000→500 | 6 pipelines | ⚠️ não resolve câmara |
| 01/05 | run_query→run_query_with_retry | 12 pipelines | ✅ |
| 30/04 | BCB API Olinda manual | download_bcb.py | ✅ dados OK |

---

## 📁 PASTA docs/analise_outra_ia/

Contém trabalho preservado de outra IA que alterou scripts sem registro:
```
download_cepim_versao_outra_ia.py   — CEPIM reescrito com requests puro (não usar)
download_pep_criado_outra_ia.py     — arquivo vazio
download_pep_versao_outra_ia.py     — cópia antes da restauração
CHANGELOG_outra_ia.md               — proposta de centralização de downloads
diff_completo_outra_ia.txt          — diff completo de tudo que ela alterou
```

**O que a outra IA propôs (registrado no CHANGELOG):**
- Centralizar todos os downloads no `_download_utils.py` — ideia correta
- Implementar constraints no Neo4j — válido, pendente diagnóstico
- Limitar heap Neo4j a 20GB — válido, pendente diagnóstico
- **Execução foi irresponsável** — reescreveu sem testar, abandonou no meio

---

## ⚠️ PROBLEMAS CONHECIDOS

| # | Problema | Prioridade |
|---|---|---|
| 1 | Câmara morrendo no load — memória/constraints | 🔴 URGENTE |
| 2 | Backup desatualizado | 🔴 após câmara importar |
| 3 | SOCIO_DE incompletos 18.7M vs 26.8M | 🟡 |
| 4 | pep_cgu autenticação | 🟡 decisão pendente |
| 5 | world_bank não testado | 🟡 |
| 6 | download_bcb.py reescrita pendente | 🟡 |
| 7 | Bug frontend Person grafo vazio | 🟡 |
| 8 | DATASUS Visual C++ | 🟠 |
| 9 | Nginx timeout volátil | 🟠 |

---

## 💡 COMANDOS ÚTEIS

```bash
# ── Monitoramento ─────────────────────────────────────────────────────
tail -5 ~/Downloads/br-acc-novo/pipeline_imports.log && echo "---" && \
ps aux | grep bracc-etl | grep -v grep

# ── Neo4j totais ──────────────────────────────────────────────────────
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme \
  "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# ── Diagnóstico memória Neo4j ─────────────────────────────────────────
docker stats bracc-neo4j --no-stream && \
grep -i "heap\|memory\|Xms\|Xmx" ~/Downloads/br-acc-novo/docker-compose.yml

# ── Fila de importação (relançar se morreu) ───────────────────────────
echo "▶️ FILA: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ~/Downloads/br-acc-novo/pipeline_imports.log && \
cd ~/Downloads/br-acc-novo/etl && source ~/.local/bin/env && \
  for FONTE in camara transparencia siop opensanctions tse; do
    echo "▶️ $FONTE: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline_imports.log
    uv run bracc-etl run --source $FONTE --neo4j-password "changeme" \
      --data-dir ../data 2>&1 | tee -a ../pipeline_imports.log
    echo "✅ $FONTE: $(date '+%d/%m/%Y %H:%M:%S')" | tee -a ../pipeline_imports.log
    powershell.exe -Command "[console]::beep(1000,300); [console]::beep(1200,300)"
  done

# ── Backup ────────────────────────────────────────────────────────────
docker run --rm -v br-acc-novo_neo4j-data:/data \
  -v C:/Users/Rolim/Downloads:/backup \
  alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && \
  echo "✅ Backup: $(date '+%d/%m/%Y %H:%M:%S')" && \
  powershell.exe -Command "[console]::beep(1000,500); [console]::beep(1500,1000)"

# ── Commitar docs ─────────────────────────────────────────────────────
cd ~/Downloads/br-acc-novo && \
  git add docs/ etl/scripts/ etl/src/ && \
  git status --short && \
  git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && \
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
| 02/05 | batch_size→500. sanctions+siconfi+icij+senado ✅. Câmara travando. |
| 03/05 | Restauração scripts alterados por outra IA. find_latest_date centralizado. CEPIM+PEP com fallback 7 dias. CHANGELOG recuperado e completo. |

---

## ⚠️ CHECKLIST NOVA SESSÃO

```
[ ] Docker Desktop aberto
[ ] docker compose up -d && docker ps
[ ] cat docs/CHANGELOG_TECNICO.md ← OBRIGATÓRIO
[ ] ps aux | grep bracc-etl (fila viva?)
[ ] tail -5 pipeline_imports.log
[ ] PRIMEIRA AÇÃO: diagnosticar memória Neo4j antes de relançar câmara
[ ] Após câmara: BACKUP PRIMEIRO
[ ] Após backup: importar PNCP
```

---

## 📎 ARQUIVOS DE REFERÊNCIA

```
docs/CONTEXTO_PROJETO_AM_v19_MASTER.md  ← este
docs/CHANGELOG_TECNICO.md
docs/CORRECOES_SCRIPTS_DOWNLOAD.md
docs/URLS_CORRETAS.md
docs/ORIENTACOES_IA.md
docs/PROMPT_INICIALIZACAO_IA.md         ← usar no início de cada sessão
docs/analise_outra_ia/                  ← trabalho preservado para análise
```

GitHub: https://github.com/PuraForja/bracc-etl/tree/main/docs

---

*v19 — 03/05/2026 ~23h50*
*Scripts download corrigidos com find_latest_date*
*Câmara pendente — diagnosticar memória antes de relançar*
*⚠️ Backup URGENTE após câmara importar*
