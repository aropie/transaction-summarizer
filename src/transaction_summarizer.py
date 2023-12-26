#! /usr/bin/python3
from collections import defaultdict
from typing import Any, Optional

from html2text import html2text
from sqlalchemy import func, select

from src.config import settings
from src.db.db import DbAPI
from src.email_gateway import EmailGateway
from src.models import Transaction


class TransactionSummarizer:
    """Class for giving information on the Transactions stored on the DB.

    A TransactionSummarizer object will perform queries on the DB to
    return averages and balances.
    """

    def __init__(self, db_api: Optional[DbAPI] = None):
        self.email_gateway = EmailGateway()
        self.db = db_api or DbAPI()

    def get_transactions_by_year_month(self) -> Any:
        """Returns a dictionary with the number of transactions sorted by year and month.
        For example:
        {
          2022: {
              7: 3
              8: 10
          },
          2023: {
              12: 5
          }
        }

        :returns: A dictionary with the number transactions sorted by year and month

        """

        with self.db.session_local() as session:
            transactions = session.scalars(select(Transaction)).all()
            parsed_transactions = defaultdict(lambda: defaultdict(int))
            for transaction in transactions:
                parsed_transactions[transaction.date.year][transaction.date.month] += 1
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

    def send_summary_email(self) -> None:
        """Sends an email with a summary of the transactions stored in DB.

        :returns: None

        """

        # Importing here to avoid circular imports
        from src.email_composer import EmailComposer

        email_composer = EmailComposer()
        html = email_composer.compose_html_summary()
        text = html2text(html)

        self.email_gateway.send_email(
            settings.target_email, settings.email_subject, text, html
        )
