from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.orm import Session

from database.connection import engine
from database.models import GoldPrice
from database.models import Base

Base.metadata.create_all(engine)


def save_dataframe(df):

    with Session(engine) as session:

        for _, row in df.iterrows():

            stmt = insert(GoldPrice).values(

                tanggal=row["tanggal"],

                scraped_at=row["scraped_at"],

                source=row["source"],

                wilayah=row["wilayah"],

                butik=row["butik"],

                gram=row["gram"],

                harga=row["harga"],

                stok=str(row["stok"])

            )

            stmt = stmt.on_conflict_do_update(

                constraint="uq_gold",

                set_={

                    "harga": row["harga"],

                    "stok": str(row["stok"]),

                    "scraped_at": row["scraped_at"]

                }

            )

            session.execute(stmt)

        session.commit()