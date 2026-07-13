import requests
from bs4 import BeautifulSoup

URL = "https://emasantam.id/harga-emas-antam-harian/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}

def extract():

    response = requests.get(URL, headers=HEADERS, timeout=30)

    print("STATUS :", response.status_code)
    print("URL    :", response.url)
    print("BODY   :")
    print(response.text[:500])

    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")