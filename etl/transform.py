import re
from datetime import datetime

import pandas as pd


SOURCE = "https://emasantam.id/harga-emas-antam-harian/"


def clean_price(text):

    match = re.search(r"Rp\s*([\d\.]+)", text)

    if match:
        return int(match.group(1).replace(".", ""))

    return None


def clean_stock(text):

    if "Sold Out" in text:
        return "Sold Out"

    match = re.search(r"Stock:\s*(\d+)", text)

    if match:
        return int(match.group(1))

    return None


def transform(soup):
    tables = soup.find_all("table")
    data = []
    today = datetime.now().date()
    scraped_at = datetime.now()

    if not tables:
        print("Tidak ditemukan tabel di HTML.")
        return pd.DataFrame()

    for table in tables:
        all_rows = table.find_all("tr")
        
        if len(all_rows) < 4: 
            continue

        wilayah = all_rows[1].get_text(" ", strip=True)

        butik_list = [
            th.get_text(" ", strip=True)
            for th in all_rows[3].find_all("th")
        ]
        
        data_rows = all_rows[4:]

        for row in data_rows:
            cols = row.find_all("td")
            
            if not cols:
                continue

            try:
                gram_text = re.sub(r"[^\d\.]", "", cols[0].text.strip())
                gram = float(gram_text) if gram_text else None
                
                if gram is None:
                    continue

                for i, butik in enumerate(butik_list):
                    if (i + 1) < len(cols):
                        cell = cols[i + 1]
                        text = cell.get_text(" ", strip=True)

                        data.append({
                            "tanggal": today,
                            "scraped_at": scraped_at,
                            "source": SOURCE,
                            "wilayah": wilayah,
                            "butik": butik,
                            "gram": gram,
                            "harga": clean_price(text),
                            "stok": clean_stock(text)
                        })
            except Exception as e:
                print(f"Gagal memproses baris: {e}")
                continue

    df = pd.DataFrame(data)
    
    if df.empty:
        df = pd.DataFrame(columns=["tanggal", "scraped_at", "source", "wilayah", "butik", "gram", "harga", "stok"])
        
    return df