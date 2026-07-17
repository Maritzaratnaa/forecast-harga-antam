from historical_extract import extract_history
from historical_transform import transform_history
from historical_load import load_history

import pandas as pd

from datetime import date

tanggal_list = pd.date_range(

    start="2026-07-11",
    end="2026-07-11"

)

for tanggal in tanggal_list:

    print(tanggal.date())

    soup = extract_history(

        tanggal.date()

    )

    if soup is None:

        continue

    df = transform_history(

        soup,

        tanggal.date()

    )

    if len(df):

        load_history(df)
        print("Scrape selesai")