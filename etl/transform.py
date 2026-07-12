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

    for table in tables:

        headers = table.find_all("tr")

        wilayah = headers[1].get_text(" ", strip=True)

        butik_list = [
            th.get_text(" ", strip=True)
            for th in headers[3].find_all("th")
        ]

        rows = table.find("tbody").find_all("tr")

        for row in rows:

            cols = row.find_all("td")

            gram = float(cols[0].text.strip())

            for butik, cell in zip(butik_list, cols[1:]):

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

    df = pd.DataFrame(data)

    return df