import pandas as pd


def validate(df: pd.DataFrame):
    
    print("Kolom yang tersedia saat ini:", df.columns.tolist())

    if df.isnull().sum().sum() > 0:
        print("Ada data NULL")

    if (df["gram"] <= 0).any():
        raise ValueError("Gram tidak valid")

    if (df["harga"] <= 0).any():
        raise ValueError("Harga tidak valid")

    return df