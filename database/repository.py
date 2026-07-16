import pandas as pd
from sqlalchemy import text  
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from database.connection import engine
from database.models import GoldPrice


def save_dataframe(df):
    if df.empty:
        print("Dataframe kosong, tidak ada data yang disimpan.")
        return

    with Session(engine) as session:
        try:

            for _, row in df.iterrows():
                stok = None if pd.isna(row["stok"]) else str(row["stok"])

                stmt = insert(GoldPrice).values(
                    tanggal=row["tanggal"],
                    scraped_at=row["scraped_at"],
                    source=row["source"],
                    wilayah=row["wilayah"],
                    butik=row["butik"],
                    gram=row["gram"],
                    harga=row["harga"],
                    stok=stok
                )

                stmt = stmt.on_conflict_do_update(
                    constraint="uq_gold",
                    set_={
                        "harga": row["harga"],
                        "stok": stok,
                        "scraped_at": row["scraped_at"]
                    }
                )

                session.execute(stmt)
            
            print(f"Berhasil memproses {len(df)} baris data ke tabel harian.")

            tanggal_hari_ini = str(df.iloc[0]['tanggal'])
            
            query_migrasi = text("""
                INSERT INTO historis_harga_antam (tanggal, gram, harga_antam)
                SELECT DISTINCT tanggal, gram, harga
                FROM harga_antam_harian
                WHERE tanggal = :tanggal
                ON CONFLICT (tanggal, gram) DO UPDATE 
                SET harga_antam = EXCLUDED.harga_antam;
            """)
            
            session.execute(query_migrasi, {"tanggal": tanggal_hari_ini})

            session.commit()

        except Exception as e:
            session.rollback()
            print(f"Gagal, database di-rollback. Error: {e}")
            raise