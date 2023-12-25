#! /usr/bin/python3
from datetime import date

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.db.db import DbAPI


class Base(DeclarativeBase):
    ...


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date]
    value: Mapped[float]


Base.metadata.create_all(bind=DbAPI().engine)
