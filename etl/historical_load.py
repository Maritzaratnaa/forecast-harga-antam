import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(
    dotenv_path=env_path
)


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

engine = create_engine(
    DATABASE_URL
)

def load_history(df):

    if df.empty:
        return


    query = """
    INSERT INTO historis_harga_antam
    (
        tanggal,
        gram,
        harga_antam,
        source
    )
    VALUES
    (
        :tanggal,
        :gram,
        :harga_antam,
        :source
    )
    ON CONFLICT (tanggal, gram)
    DO UPDATE SET

        harga_antam = EXCLUDED.harga_antam,

        source = EXCLUDED.source;
    """


    with engine.begin() as conn:

        for row in df.to_dict(
            orient="records"
        ):

            conn.execute(
                text(query),
                row
            )


    print(
        f"{len(df)} data berhasil dimasukkan"
    )