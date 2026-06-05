# SISTEMA DE INTELIGÊNCIA POLÍTICA — AMAZONAS
## Documento Master Consolidado v30
> Gerado em 17/05/2026 ~17h00
> Cole este arquivo no início de qualquer nova sessão.

---

## INSTRUÇÕES PARA A IA — LEIA ISTO PRIMEIRO

1. Leia o CHANGELOG antes de qualquer correção de código
2. Leia o ORIENTACOES_IA.md para regras de comportamento
3. Após qualquer alteração de código: atualize o CHANGELOG e commite
4. Ao final de cada sessão: gere novo MASTER e commite
5. Sempre inclua data/hora nos logs
6. Avise quando a sessão estiver no limite — OBRIGATÓRIO
7. Nunca reescrever scripts com requests puro — sempre usar _download_utils.py
8. Confirmar alterações antes de executar
9. Abrir arquivos grandes no Notepad — heredoc trava no Git Bash do Windows
10. Comandos longos na vertical travam o Git Bash — mandar em linha única
11. Todo comando deve terminar com && echo "OK" para confirmar execução
12. NUNCA usar curl para sobrescrever loader.py do GitHub

---

## ⚠️ ORIENTAÇÃO OBRIGATÓRIA — SESSÃO ÚNICA NO LOADER

```python
# CORRETO
with loader.open_session() as session:
    loader.load_nodes("Label", rows, key_field="id", session=session)
    loader.load_relationships(..., session=session)
```

**Pipelines pendentes do fix:**
senado_cpis, cnpj, camara_inquiries, mides, transferegov, transparencia, tse, senado, tcu, datajud, ibama, icij, tse_filiados

---

## PASSO A PASSO PARA IDENTIFICAR ONDE PAROU

```bash
docker ps | grep neo4j && echo "OK"
cd ~/Downloads/br-acc-novo && docker compose up -d && echo "OK"
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC" && echo "OK"
ps aux | grep pncp | grep -v grep && echo "OK"
tail -3 ~/Downloads/br-acc-novo/download_pncp.log && echo "OK"
```

---

## PERFIL

| Campo | Valor |
|---|---|
| Nome | Alberto (Rolim) |
| Contexto | Oposição política no Amazonas |
| Hardware | Xeon 2680 v4, 32GB RAM, HD 2TB |
| SO | Windows 11 / Git Bash |
| GitHub | https://github.com/PuraForja/bracc-etl |

---

## INFRAESTRUTURA

| Sistema | Acesso | Credencial |
|---|---|---|
| Neo4j | localhost:7474 | neo4j / changeme |
| API | localhost:8000 | — |
| Frontend | localhost:3000 | teste@bracc.com / senha123 / invite: rolim |

---

## STATUS NEO4J (17/05/2026 ~17h00)

| Tipo | Qtd | Status |
|---|---|---|
| Company | 40.671.726 | OK |
| Partner | 17.774.658 | OK |
| GovEmployee | 10.269.641 | OK — transparencia_am completo |
| Expense | 3.836.389 | OK |
| MunicipalFinance | 3.469.721 | OK |
| Person | 2.780.851 | OK |
| Health | 612.561 | OK |
| TaxWaiver | 291.799 | OK |
| GovTravel | 260.000 | OK |
| GovCardExpense | 131.950 | OK |
| GlobalPEP | 117.910 | OK |
| Amendment | 101.801 | OK |
| Contract | 64.121 | OK |
| Fund | 41.107 | OK |
| Payment | 40.000 | OK |
| Election | 33.602 | OK |
| Sanction | 24.077 | OK |
| InternationalSanction | 9.707 | OK |
| **TOTAL** | **~80M** | OK |

---

## ENTITY RESOLUTION AM — ESTADO ATUAL

**Problema:** GovEmployee (servidores AM) não tem CPF — 152.856 únicos sem identificador

**Fontes testadas para CPF:**
| Fonte | Resultado |
|---|---|
| Portal Transparência Federal servidores | 403 em todos os meses |
| API CGU | Requer CPF via Gov.br — risco político |
| Brasil.io | Requer autenticação |
| Base dos Dados | Requer GCP |
| CAGED FTP | Acessível mas SEM CPF individual nos arquivos |

**O que já temos no banco com CPF:**
- TSE — candidatos/filiados — 6.6% match por nome
- CNPJ/QSA — sócios (CPF parcial)
- BCB, CEAF, Sanctions — CPF completo

**Próximo passo:** query Cypher de match por nome normalizado entre GovEmployee e Person — cobre ~18-25%

**Estrutura da relação:**
```cypher
(p:Person)-[:POSSIVEL_MESMO_INDIVIDUO {
    score: 0.95,
    metodo: 'nome_exato_tse',
    validado: false
}]->(e:GovEmployee)
```

---

## STATUS DOWNLOADS (17/05/2026)

| Fonte | Download | Importação |
|---|---|---|
| todos nacionais | OK | OK |
| transparencia_am | 6857 CSVs | OK — 10.269.641 GovEmployee |
| pncp | ~90%+ | AGUARDAR 100% |
| servidores_federais | 403 persistente | — |

---

## FERRAMENTAS INSTALADAS

- **7-Zip:** `C:/Program Files/7-Zip/7z.exe`
- Usar como: `"/c/Program Files/7-Zip/7z.exe" e arquivo.7z -o"C:/destino/" -y`

---

## ORQUESTRADOR

```bash
bash ~/Downloads/br-acc-novo/orchestrator.sh
bash ~/Downloads/br-acc-novo/orchestrator.sh --amazonas
bash ~/Downloads/br-acc-novo/orchestrator.sh --force transparencia_am
MODO_TESTE=Y bash ~/Downloads/br-acc-novo/orchestrator.sh --amazonas
```

---

## PNCP — RELANÇAR SE MORREU

```bash
cd ~/Downloads/br-acc-novo && while true; do cd etl && source ~/.local/bin/env && uv run python scripts/download_pncp.py --output-dir ../data/pncp && cd ..; sleep 30; done >> download_pncp.log 2>&1 & echo "OK"
```

---

## COMANDOS ÚTEIS

```bash
# Neo4j totais
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "MATCH (n) RETURN labels(n)[0] as tipo, count(n) as total ORDER BY total DESC"

# Backup
MSYS_NO_PATHCONV=1 docker run --rm -v br-acc-novo_neo4j-data:/data -v C:/Users/Rolim/Downloads:/backup alpine tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data && echo "OK"

# Commitar
cd ~/Downloads/br-acc-novo && git add docs/ etl/scripts/ etl/src/ orchestrator.sh && git commit -m "sync $(date '+%Y-%m-%d %H:%M')" && git push origin main && echo "OK"

# Transações presas
docker exec bracc-neo4j cypher-shell -u neo4j -p changeme "SHOW TRANSACTIONS"
```

---

## PENDENTES TÉCNICOS

```
[ ] Entity Resolution AM — query Cypher match por nome normalizado
[ ] PNCP — aguardar 100% e importar
[ ] Fix sessão única — pipelines pendentes
[ ] Scripts faltando: bndes ibama inep pgfn tcu comprasnet transferegov
[ ] Bug frontend — grafo vazio para Person nodes
[ ] SOCIO_DE incompletos — 18.7M vs 26.8M
[ ] BigQuery (rais, dou, stf, mides) — após credencial GCP
```

---

## HISTÓRICO

| Data | O que foi feito |
|---|---|
| 08-09/05 | camara 3.836M expenses + loader sessão única 1800x |
| 12-13/05 | transparencia_am download 6857 CSVs + catálogo v5 |
| 15-16/05 | transparencia_am.py streaming + fix loader consume |
| 17/05 | transparencia_am 10.269M GovEmployee + entity resolution pesquisa + backup |

---

## CHECKLIST NOVA SESSÃO

```
[ ] Ler CHANGELOG.md
[ ] docker ps | grep neo4j
[ ] Verificar PNCP rodando
[ ] Neo4j totais
[ ] Implementar query entity resolution AM
[ ] Gerar v31 ao final
```

---

v30 — 17/05/2026 ~17h00
transparencia_am: COMPLETO 10.269.641 GovEmployee
Entity Resolution: pesquisa concluída — próximo query Cypher por nome
PNCP: ~90% baixando
Backup: em andamento
