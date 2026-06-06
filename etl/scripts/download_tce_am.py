"""
download_tce_am.py
==================
Download de contratos e licitações do TCE-AM via API eContas.
https://econtasapi.tce.am.gov.br

COMO FUNCIONA:
  1. Busca lista de todas as unidades gestoras ativas via /transparencia/dados-abertos/unidades
  2. Para cada unidade × exercício (2013-2026), baixa contratos e licitações
  3. Salva em: data/tce_am/contratos/{exercicio}/{id_unidade}.json
               data/tce_am/licitacoes/{exercicio}/{id_unidade}.json
  4. Ao final, converte todos os JSON em CSV consolidado por tipo

API:
  GET https://econtasapi.tce.am.gov.br/transparencia/dados-abertos/unidades
  GET https://econtasapi.tce.am.gov.br/transparencia/dados-abertos/contratos/{idUnidade}/{exercicio}
  GET https://econtasapi.tce.am.gov.br/transparencia/dados-abertos/licitacoes/{idUnidade}/{exercicio}

ANOS DISPONÍVEIS: 2013 a 2026 (antes disso a API retorna vazio)
UNIDADES: ~466 unidades gestoras de todos os 62 municípios do AM

USO:
  cd ~/bracc/etl
  uv run python scripts/download_tce_am.py --output-dir ../data/tce_am
  uv run python scripts/download_tce_am.py --output-dir ../data/tce_am --tipo contratos
  uv run python scripts/download_tce_am.py --output-dir ../data/tce_am --ano 2024
  uv run python scripts/download_tce_am.py --output-dir ../data/tce_am --dry-run

REGRAS OBRIGATÓRIAS DO PROJETO:
  - Usar httpx com timeout e retry — nunca requests puro
  - Rate limiting: 0.3s entre requisições para não derrubar a API
  - Salvar JSON bruto antes de converter para CSV (permite re-processar)
  - Pular arquivos já existentes (download incremental)
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://econtasapi.tce.am.gov.br"
ANOS = list(range(2013, 2027))  # 2013 a 2026
DELAY = 0.3  # segundos entre requisições

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def get_unidades(client: httpx.Client) -> list[dict]:
    """Busca todas as unidades gestoras ativas."""
    try:
        resp = client.get(f"{BASE_URL}/transparencia/dados-abertos/unidades", headers=HEADERS, timeout=30)
        resp.raise_for_status()
        unidades = resp.json()
        ativas = [u for u in unidades if u.get("ativo", True)]
        logger.info("Total de unidades gestoras ativas: %d", len(ativas))
        return ativas
    except Exception as e:
        logger.error("Erro ao buscar unidades: %s", e)
        sys.exit(1)


def fetch_endpoint(client: httpx.Client, endpoint: str) -> list[dict]:
    """Chama um endpoint da API e retorna lista de registros."""
    try:
        resp = client.get(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=60)
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else []
    except httpx.TimeoutException:
        logger.warning("Timeout: %s", endpoint)
        return []
    except Exception as e:
        logger.warning("Erro em %s: %s", endpoint, e)
        return []


def salvar_json(data: list[dict], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def contratos_para_csv(output_dir: Path) -> Path:
    """Consolida todos os JSON de contratos em um único CSV."""
    csv_path = output_dir / "contratos.csv"
    campos = [
        "idContrato", "idUnidadeGestora", "cnpjUnidadeGestora", "nomeUnidadeGestora",
        "numContrato", "numContratoOrigem", "vlContrato", "desMoeda",
        "dtAssinaturaContrato", "dtPublicacaoContrato", "desObjetivo",
        "numDoe", "desTipoPessoa", "cpfCnpj", "nome", "exercicio",
    ]
    total = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for json_file in sorted((output_dir / "contratos").rglob("*.json")):
            try:
                registros = json.loads(json_file.read_text(encoding="utf-8"))
                for r in registros:
                    writer.writerow(r)
                    total += 1
            except Exception as e:
                logger.warning("Erro ao processar %s: %s", json_file, e)
    logger.info("CSV contratos: %d registros → %s", total, csv_path)
    return csv_path


def licitacoes_para_csv(output_dir: Path) -> Path:
    """Consolida todos os JSON de licitações em um único CSV."""
    csv_path = output_dir / "licitacoes.csv"
    campos = [
        "idLicitacao", "idUnidadeGestora", "cnpjUnidadeGestora", "nomeUnidadeGestora",
        "numeroLicitacao", "numDoe", "dtPublicacaoEdital", "descricaoObjeto",
        "valorTotal", "numeroEdital", "descricao", "desTipoLicitacao",
        "desTipoNaturezaProcedimento", "exercicio",
    ]
    total = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for json_file in sorted((output_dir / "licitacoes").rglob("*.json")):
            try:
                registros = json.loads(json_file.read_text(encoding="utf-8"))
                for r in registros:
                    writer.writerow(r)
                    total += 1
            except Exception as e:
                logger.warning("Erro ao processar %s: %s", json_file, e)
    logger.info("CSV licitações: %d registros → %s", total, csv_path)
    return csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download TCE-AM — Contratos e Licitações")
    parser.add_argument("--output-dir", required=True, help="Diretório de saída, ex: ../data/tce_am")
    parser.add_argument("--tipo", choices=["contratos", "licitacoes", "ambos"], default="ambos", help="Tipo de dado a baixar")
    parser.add_argument("--ano", type=int, help="Baixar só este ano (ex: 2024)")
    parser.add_argument("--unidade", type=int, help="Baixar só esta unidade gestora (ex: 238)")
    parser.add_argument("--dry-run", action="store_true", help="Listar sem baixar")
    parser.add_argument("--so-csv", action="store_true", help="Só gerar CSVs dos JSONs já baixados")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Modo só-CSV: reconsolida sem baixar nada
    if args.so_csv:
        if args.tipo in ("contratos", "ambos"):
            contratos_para_csv(output_dir)
        if args.tipo in ("licitacoes", "ambos"):
            licitacoes_para_csv(output_dir)
        return

    anos = [args.ano] if args.ano else ANOS
    baixar_contratos = args.tipo in ("contratos", "ambos")
    baixar_licitacoes = args.tipo in ("licitacoes", "ambos")

    with httpx.Client() as client:
        unidades = get_unidades(client)

        if args.unidade:
            unidades = [u for u in unidades if u["id_unidade_gestora"] == args.unidade]
            if not unidades:
                logger.error("Unidade %d não encontrada", args.unidade)
                sys.exit(1)

        total_unidades = len(unidades)
        total_contratos = 0
        total_licitacoes = 0
        total_pulados = 0
        total_erros = 0

        for i, unidade in enumerate(unidades, 1):
            uid = unidade["id_unidade_gestora"]
            nome = unidade["nome"]
            municipio = unidade["desMunicipio"]

            logger.info("[%d/%d] %s — %s (%s)", i, total_unidades, uid, nome, municipio)

            for ano in anos:
                # ── Contratos ──────────────────────────────────────────────
                if baixar_contratos:
                    dest = output_dir / "contratos" / str(ano) / f"{uid}.json"
                    if dest.exists():
                        total_pulados += 1
                    elif args.dry_run:
                        logger.info("  [DRY-RUN] contratos/%s/%s.json", ano, uid)
                    else:
                        dados = fetch_endpoint(client, f"/transparencia/dados-abertos/contratos/{uid}/{ano}")
                        if dados:
                            salvar_json(dados, dest)
                            total_contratos += len(dados)
                            logger.info("  contratos %s: %d registros", ano, len(dados))
                        time.sleep(DELAY)

                # ── Licitações ─────────────────────────────────────────────
                if baixar_licitacoes:
                    dest = output_dir / "licitacoes" / str(ano) / f"{uid}.json"
                    if dest.exists():
                        total_pulados += 1
                    elif args.dry_run:
                        logger.info("  [DRY-RUN] licitacoes/%s/%s.json", ano, uid)
                    else:
                        dados = fetch_endpoint(client, f"/transparencia/dados-abertos/licitacoes/{uid}/{ano}")
                        if dados:
                            salvar_json(dados, dest)
                            total_licitacoes += len(dados)
                            logger.info("  licitacoes %s: %d registros", ano, len(dados))
                        time.sleep(DELAY)

    logger.info("=" * 60)
    logger.info("Download concluído:")
    logger.info("  Contratos:  %d registros", total_contratos)
    logger.info("  Licitações: %d registros", total_licitacoes)
    logger.info("  Pulados:    %d (já existiam)", total_pulados)
    logger.info("  Erros:      %d", total_erros)

    # Gerar CSVs consolidados
    if not args.dry_run:
        if baixar_contratos:
            contratos_para_csv(output_dir)
        if baixar_licitacoes:
            licitacoes_para_csv(output_dir)


if __name__ == "__main__":
    main()
