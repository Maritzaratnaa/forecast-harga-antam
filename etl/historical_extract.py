import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def extract_history(date):

    """
    date = datetime.date
    """

    bulan = {

        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"

    }

    url = (
        f"https://harga-emas.org/history-harga/"
        f"{date.year}/"
        f"{bulan[date.month]}/"
        f"{date.day:02d}"
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

    except requests.exceptions.RequestException as e:

        print(
            "Request gagal:",
            e
        )

        return None

    if response.status_code != 200:
        return None

    return BeautifulSoup(response.text, "lxml")