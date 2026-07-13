import os
import requests
from bs4 import BeautifulSoup

URL = "https://emasantam.id/harga-emas-antam-harian/"

def extract():
    api_key = os.getenv("SCRAPERAPI_KEY")
    
    if not api_key:
        print("Peringatan: SCRAPERAPI_KEY tidak ditemukan!")
        return BeautifulSoup("", "html.parser")

    payload = {
        'api_key': api_key,
        'url': URL,
        'render': 'true'
    }
    
    try:
        print("Mengirim request ke ScraperAPI...")
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)
        
        if response.status_code == 200:
            print("Scraping via ScraperAPI Sukses!")
            return BeautifulSoup(response.text, "html.parser")
        else:
            print(f"ScraperAPI gagal. Status Code: {response.status_code}")
            print("Error:", response.text[:500])
            
    except Exception as e:
        print(f"Terjadi error saat request ke ScraperAPI: {e}")
        
    return BeautifulSoup("", "html.parser")