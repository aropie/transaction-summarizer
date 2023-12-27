#! /usr/bin/python3
from csv import DictReader
from datetime import date
from typing import List, Optional

from src.db.db import DbAPI
from src.models import Transaction


class MalformedInputFileError(Exception):
    pass


class TransactionSeeder:
    """Class for the object to parse the transactions file into the DB.

    This object's main method, parse_file, will recieve a transactions
    csvfile in its initialization method and will automatically insert
    them into the DB. The input file is treated as a source of truth;
    this means that if an existing transaction is already in the DB,
    identified by its id, then the existing row will be updated.

    """

    def __init__(self, dbapi: Optional[DbAPI] = None):
        self.db = dbapi or DbAPI()

    def parse_file(self, csvfile: List[str]):
        reader = DictReader(csvfile)
        for row in reader:
            try:
                split_date = [int(arg) for arg in row["date"].split("/")]
                year, month, day = split_date
                self._update_or_insert_transaction(
                    id=int(row["id"]),
                    date=date(day=day, month=month, year=year),
                    value=float(row["transaction"]),
                )
            except (ValueError, AttributeError, KeyError) as e:
                raise MalformedInputFileError("The input csv file is invalid") from e

    def _update_or_insert_transaction(self, id: int, date: date, value: float):
        with self.db.session_local() as session:
            transaction = session.get(Transaction, id)
            if transaction:
                transaction.date = date
                transaction.value = value
            else:
                transaction = Transaction(id=id, date=date, value=value)
            session.add(transaction)
