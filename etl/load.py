import os

from database.repository import save_dataframe


def load(df):

    os.makedirs("data/raw", exist_ok=True)

    filename = f"data/raw/gold_price_{df.iloc[0]['tanggal']}.csv"

    df.to_csv(

        filename,

        index=False,

        encoding="utf-8-sig"

    )

    save_dataframe(df)

    print("CSV tersimpan")

    print("Database berhasil diperbarui")