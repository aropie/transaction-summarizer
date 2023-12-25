#! /usr/bin/python3

from datetime import date
from typing import List

from pytest import fixture
from src.db.db import DbAPI
from src.models import Base, Transaction


@fixture
def db():
    db = DbAPI()
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(db.engine)
    return db


@fixture
def transactions():
    transactions = [
        Transaction(id=1, date=date(2021, 1, 1), value=10),
        Transaction(id=2, date=date(2021, 1, 5), value=-20),
        Transaction(id=3, date=date(2022, 4, 19), value=30),
        Transaction(id=4, date=date(2022, 5, 20), value=-40),
        Transaction(id=5, date=date(2022, 5, 21), value=50),
        Transaction(id=6, date=date(2023, 7, 1), value=-60),
        Transaction(id=7, date=date(2023, 7, 2), value=70),
        Transaction(id=8, date=date(2023, 7, 3), value=-80),
    ]
    return transactions


@fixture
def seed_db(db: DbAPI, transactions: List[Transaction]):
    with db.session_local() as session:
        session.expire_on_commit = False
        session.add_all(transactions)
        session.commit()
