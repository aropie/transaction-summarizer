#! /usr/bin/python3
from collections import defaultdict
from typing import Any, Optional

from sqlalchemy import func, select

from src.db.db import DbAPI
from src.models import Transaction


class TransactionSummarizer:
    """Class for giving information on the Transactions stored on the DB.

    A TransactionSummarizer object will perform queries on the DB to return
    averages and balances.
    """

    def __init__(self, db_api: Optional[DbAPI] = None):
        self.db = db_api or DbAPI()

    def get_transactions_by_year_month(self) -> Any:
        """Returns a dictionary with the transactions sorted by year and month.
        For example:
        {
          2022: {
              7: [Transaction, Transaction]
              8: [Transaction]
          },
          2023: {
              12: [Transaction, Transaction, Transaction]
          }
        }

        :returns: A dictionary with transactions sorted by year and month

        """

        with self.db.session_local() as session:
            transactions = session.scalars(select(Transaction)).all()
            parsed_transactions = defaultdict(lambda: defaultdict(list))
            for transaction in transactions:
                parsed_transactions[transaction.date.year][
                    transaction.date.month
                ].append(transaction)
            return parsed_transactions

    def get_total_balance(self) -> float:
        """Returns the total balance of all transactions within the DB

        :returns: a float of the total balance of all transactions

        """
        with self.db.session_local() as session:
            total_balance = session.scalars(select(func.sum(Transaction.value))).one()
            return total_balance

    def get_average_debit(self) -> float:
        """Returns the average value of all debit transactions.
        Debit transactions are defined as those whose value is negative.

        :returns: a float of the average of negative-valued transactions

        """
        with self.db.session_local() as session:
            average_debit = (
                session.scalars(
                    select(func.avg(Transaction.value)).where(Transaction.value < 0)
                ).one()
                or 0  # if there are no transactions with value < 0, then return 0 as the avg
            )
            return average_debit

    def get_average_credit(self) -> float:
        """Returns the average value of all credit transactions.
        Credit transactions are defined as those whose value is positive.

        :returns: a float of the average of positive-valued transactions

        """
        with self.db.session_local() as session:
            average_credit = (
                session.scalars(
                    select(func.avg(Transaction.value)).where(Transaction.value > 0)
                ).one()
                or 0  # if there are no transactions with value > 0, then return 0 as the avg
            )
            return average_credit
