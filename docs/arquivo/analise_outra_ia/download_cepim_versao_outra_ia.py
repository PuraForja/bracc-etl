import requests
from datetime import datetime, timedelta
import os
from pathlib import Path

def download_cepim():
    output_dir = Path("../data/transparencia/cepim")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Tenta hoje, se falhar tenta ontem (Fallback D-1)
    for i in range(5):
        target_date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
        url = f"https://portaldatransparencia.gov.br/download-de-dados/cepim/{target_date}"
        file_path = output_dir / f"{target_date}_cepim.zip"
        
        print(f"▶️ Tentando baixar CEPIM data {target_date}...")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Sucesso! Arquivo salvo em: {file_path}")
            return
        else:
            print(f"⚠️ Data {target_date} não disponível (Erro {response.status_code}).")

    print("❌ Falha crítica: Nenhuma data disponível para o CEPIM nos últimos 2 dias.")

if __name__ == "__main__":
    download_cepim()
