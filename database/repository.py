import pandas as pd
from sqlalchemy import text
from datetime import datetime

def save_dataframe(df, session):
    tanggal_hari_ini = str(df["tanggal"].iloc[0])
    
    try:
        query_stok = text("""
            INSERT INTO stok_antam_butik (tanggal, wilayah, butik, gram, stok, harga, scraped_at)
            VALUES (:tanggal, :wilayah, :butik, :gram, :stok, :harga, :scraped_at)
            ON CONFLICT (tanggal, butik, gram) DO UPDATE 
            SET stok = EXCLUDED.stok,
                harga = EXCLUDED.harga,
                scraped_at = EXCLUDED.scraped_at;
        """)
        
        for _, row in df.iterrows():
            raw_stok = str(row["stok"]).strip() if not pd.isna(row["stok"]) else ""
            stok_final = 0 if raw_stok in ["Sold Out", ""] else int(raw_stok)
            
            session.execute(query_stok, {
                "tanggal": row["tanggal"],
                "wilayah": row["wilayah"],
                "butik": row["butik"],
                "gram": row["gram"],
                "stok": stok_final,
                "harga": row["harga"],
                "scraped_at": row["scraped_at"]
            })

        df_agregat = df.groupby(["tanggal", "gram"])["harga"].mean().reset_index()
        
        query_harga_harian = text("""
            INSERT INTO harga_antam_harian (tanggal, gram, harga, scraped_at)
            VALUES (:tanggal, :gram, :harga, :scraped_at)
            ON CONFLICT (tanggal, gram) DO UPDATE
            SET harga = EXCLUDED.harga,
                scraped_at = EXCLUDED.scraped_at;
        """)
        
        for _, row in df_agregat.iterrows():
            session.execute(query_harga_harian, {
                "tanggal": row["tanggal"],
                "gram": row["gram"],
                "harga": int(row["harga"]),
                "scraped_at": datetime.now()
            })

        query_migrasi = text("""
            INSERT INTO historis_harga_antam (tanggal, gram, harga_antam)
            SELECT tanggal, gram, harga
            FROM harga_antam_harian
            WHERE tanggal = :tanggal
            ON CONFLICT (tanggal, gram) DO UPDATE 
            SET harga_antam = EXCLUDED.harga_antam;
        """)
        
        session.execute(query_migrasi, {"inverse_tanggal": tanggal_hari_ini})
        
        session.commit()
        print(f"Sukses memproses data untuk tanggal {tanggal_hari_ini} ke tabel Stok, Harian, dan Historis!")
        
    except Exception as e:
        session.rollback()
        print(f"Gagal, database di-rollback. Error: {str(e)}")
        raise e