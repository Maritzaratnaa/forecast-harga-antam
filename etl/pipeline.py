from etl.extract import extract
from etl.transform import transform
from etl.load import load
from etl.validation import validate

def main():
        
    print("START SCRAPING")

    soup = extract()
        
    print("SCRAPING SUCCESS")

    df = transform(soup)

    df = validate(df)
        
    print(df.head())
    print("TOTAL DATA:", len(df))

    load(df)

    print("LOAD SUCCESS")