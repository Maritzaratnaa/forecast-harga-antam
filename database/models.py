from datetime import date, datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import UniqueConstraint


class Base(DeclarativeBase):
    pass


class GoldPrice(Base):

    __tablename__ = "harga_antam_harian"

    id: Mapped[int] = mapped_column(primary_key=True)

    tanggal: Mapped[date] = mapped_column(Date)

    scraped_at: Mapped[datetime] = mapped_column(DateTime)

    source: Mapped[str] = mapped_column(String(255))

    wilayah: Mapped[str] = mapped_column(String(100))

    butik: Mapped[str] = mapped_column(String(100))

    gram: Mapped[float] = mapped_column(Float)

    harga: Mapped[int] = mapped_column(Integer)

    stok: Mapped[str] = mapped_column(String(30))

    __table_args__ = (
        UniqueConstraint(
            "tanggal",
            "wilayah",
            "butik",
            "gram",
            name="uq_gold",
        ),
    )