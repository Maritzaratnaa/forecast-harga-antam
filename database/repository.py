import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from database.connection import engine
from database.models import GoldPrice


def save_dataframe(df):

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

            session.commit()

        except Exception:

            session.rollback()
            raise