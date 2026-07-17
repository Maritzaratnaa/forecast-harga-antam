import os
import pandas as pd
from etl.extract import extract
from etl.transform import transform
from etl.load import load
from etl.validation import validate
from forecast.predict import generate_forecast_all_grams

from database.connection import SessionLocal

def main():
    soup = extract()
    
    if not soup or soup.find('body') is None:
        print("SCRAPING GAGAL.")
        return

    df = transform(soup)
    
    if df is None or df.empty:
        print("TRANSFORM GAGAL: Dataframe kosong setelah dibersihkan.")
        return
        
    print(df.head())
    print("TOTAL DATA DATA HARI INI:", len(df))

    df = validate(df)

    session = SessionLocal() 
    try:
        load(df, session)
        print("LOAD DATA HARIAN SUCCESS")
    except Exception as e:
        print(f"LOAD DATA HARIAN GAGAL: {e}")
        return
    finally:
        session.close()
    
    try:
        generate_forecast_all_grams()
        print("FORECASTING & UPDATE METRIK SUCCESS")
    except Exception as e:
        print(f"FORECASTING GAGAL: Terjadi error pada AI core: {e}")
    
    print("ALL PIPELINE PROCESS COMPLETED")
    
if __name__ == "__main__":
    main()