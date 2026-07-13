from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://emasantam.id/harga-emas-antam-harian/"


def extract():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )

        page.goto(
            URL,
            wait_until="networkidle",
            timeout=60000
        )
        
        html = page.content()
        
        print("--- INTIP ISI HTML ---")
        print(html[:2000])
        print("----------------------")

        browser.close()

    return BeautifulSoup(html, "html.parser")