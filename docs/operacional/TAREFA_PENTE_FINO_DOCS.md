# TAREFA — PENTE FINO NA DOCUMENTAÇÃO
> Criado em 03/06/2026 — DELETAR após concluir todas as tarefas
> **PARA A PRÓXIMA IA:** continue daqui, marcando cada tarefa conforme conclui

## CONTEXTO
Reorganizamos toda a estrutura de docs. Esta tarefa é fazer pente fino em TODOS
os docs operacionais corrigindo referências antigas, status desatualizados e inconsistências.

## TERMOS ANTIGOS — substituir por novos
| Antigo | Correto |
|---|---|
| `~/Downloads/br-acc-novo/` | `~/bracc/` |
| `ICARUS` / `icarus_etl` | `BRACC` / `bracc_etl` |
| `docs/URLS_CORRETAS.md` | `docs/operacional/DOWNLOADS_STATUS.md` |
| `docs/CORRECOES_SCRIPTS_DOWNLOAD.md` | `docs/operacional/DOWNLOADS_STATUS.md` |
| `docs/data-sources.md` | `docs/referencia/CATALOGO_FONTES.md` |
| `docs/PENDENCIAS_FEATURES.md` | `docs/operacional/PENDENCIAS_FEATURES.md` |
| `docker-compose` (com hífen) | `docker compose` (sem hífen) |

## ARQUIVOS DELETADOS — não referenciar mais
- `docs/URLS_CORRETAS.md` → fundido em DOWNLOADS_STATUS.md
- `docs/CORRECOES_SCRIPTS_DOWNLOAD.md` → fundido em DOWNLOADS_STATUS.md
- `docs/data-sources.md` → renomeado para CATALOGO_FONTES.md
- `docs/pipeline_status.md` → arquivado
- `docs/source_registry_br_v1.csv` → arquivado
- `docs/FONTES_EXTERNAS_REFERENCIA.md` → arquivado

## TAREFAS

### 1. `docs/operacional/ORIENTACOES_IA.md` ✅ CONCLUÍDO 03/06/2026
- Reescrito completamente — caminhos corrigidos, regras atualizadas

### 2. `docs/operacional/CHANGELOG.md` ✅ CONCLUÍDO 03/06/2026
- [ ] Substituir todas ocorrências de `br-acc-novo` por `bracc`
- [ ] Substituir caminhos Windows `C:\Users\Rolim\Downloads` por `/home/rolim`
- [ ] Verificar referências a docs antigos
- [ ] Adicionar entradas das sessões 01-03/06/2026

### 3. `docs/operacional/SETUP_INDICES.md` ✅ CONCLUÍDO 04/06/2026
- [ ] Verificar se índices criados em 01-03/06 estão listados:
  - community_id_person, community_id_partner, community_id_globalpep
  - titulo_eleitor_person
  - declared_asset_id
- [ ] Verificar comandos docker — usar `docker compose` não `docker-compose`
- [ ] Verificar caminhos

### 4. `docs/operacional/ORIENTACOES_PIPELINE.md` ✅ CONCLUÍDO 04/06/2026
- [ ] Verificar caminhos
- [ ] Adicionar orientação sobre orchestrator — todo novo pipeline deve ser registrado
- [ ] Verificar consistência com o que implementamos

### 5. `docs/operacional/BRACC_INSTALLER_ESCOPO.md` ✅ CONCLUÍDO 04/06/2026
- [ ] Verificar referências a docs antigos
- [ ] Verificar prioridades

### 6. `docs/referencia/CATALOGO_FONTES.md` ✅ CONCLUÍDO 05/06/2026
- [ ] Verificar status das fontes — tse_bens importado, etc
- [ ] Verificar referências a arquivos antigos

### 7. `~/bracc/CHANGELOG.md` (raiz) ✅ CONCLUÍDO 05/06/2026
- [ ] Verificar se é duplicata do docs/operacional/CHANGELOG.md
- [ ] Definir qual é o principal

## TAREFAS APÓS PENTE FINO
- [ ] Criar `~/bracc/CLAUDE.md` — doc estático de entrada
- [ ] Criar `~/bracc/docs/operacional/ESTADO_ATUAL.md` — estado dinâmico do banco
- [ ] Deletar este arquivo
- [ ] Commitar tudo
- [ ] Gerar v36 MASTER

## VERIFICAÇÃO RÁPIDA
```bash
grep -rn "br-acc-novo\|Downloads.*bracc\|icarus\|ICARUS\|URLS_CORRETAS\|data-sources\|pipeline_status\|source_registry\|FONTES_EXTERNAS" ~/bracc/docs/operacional/ && echo "OK"
```
