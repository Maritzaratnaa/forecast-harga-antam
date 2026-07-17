import re
import pandas as pd


def clean_price(text):

    angka = re.sub(
        r"[^\d]",
        "",
        text
    )

    if angka == "":
        return None

    return int(angka)



def transform_history(soup, tanggal):

    table = soup.find(
        "table",
        class_=re.compile(
            "HistoricalPricesTable_table"
        )
    )


    if table is None:
        return pd.DataFrame()


    tbody = table.find("tbody")


    if tbody is None:
        return pd.DataFrame()


    data = []


    for row in tbody.find_all("tr"):

        cols = row.find_all("td")


        if len(cols) < 3:
            continue


        try:

            gram = float(
                cols[0]
                .get_text(strip=True)
            )


            harga_antam = clean_price(
                cols[1]
                .get_text(
                    " ",
                    strip=True
                )
            )


            data.append({

                "tanggal": tanggal,

                "gram": gram,

                "harga_antam": harga_antam
            })


        except Exception:

            continue


    return pd.DataFrame(data)