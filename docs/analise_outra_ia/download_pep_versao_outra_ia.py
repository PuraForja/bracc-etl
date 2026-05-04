import requests
from pathlib import Path

def download_pep():
    output_dir = Path("../data/transparencia/pep")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # --- CONFIGURAÇÃO DE FONTES ---
    # OPÇÃO OFICIAL (CGU): Requer login manual via Gov.br (bloqueia automação direta)
    # url_oficial = "https://portaldatransparencia.gov.br/download-de-dados/pep"
    
    # OPÇÃO ALTERNATIVA (OpenSanctions): Espelho público, não requer senha/login.
    url = "https://data.opensanctions.org/datasets/latest/br_pep/entities.ftm.json"
    # ------------------------------

    file_path = output_dir / "pep_brasil.json"
    print(f"▶️ Baixando PEP Brasil via OpenSanctions (Fonte aberta)...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Sucesso! Arquivo salvo em: {file_path}")
    else:
        print(f"❌ Erro no download: Status {response.status_code}")

if __name__ == "__main__":
    download_pep()
