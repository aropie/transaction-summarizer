#! /usr/bin/python3
from datetime import timedelta

from src.models import Transaction
from src.transaction_seeder import TransactionSeeder


class TestTransactionSeeder:
    def test_update_or_insert_transaction(self, seed_db, transactions, db):
        # Given
        seeder = TransactionSeeder()
        transaction = transactions[0]
        new_date = transaction.date + timedelta(days=365)
        new_value = transaction.value + 10

        # When
        seeder._update_or_insert_transaction(transaction.id, new_date, new_value)

        # Then
        with db.session_local() as session:
            transaction_from_db = session.get(Transaction, transaction.id)
            assert transaction_from_db.id == transaction.id
            assert transaction_from_db.date == new_date
            assert transaction_from_db.value == new_value
