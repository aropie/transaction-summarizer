#! /usr/bin/python3


from statistics import mean

from src.transaction_summarizer import TransactionSummarizer


class TestTransactionSummarizer:
    def test_get_transactions_by_year_month(self, seed_db):
        # Given
        summarizer = TransactionSummarizer()
        expected_dict = {
            2021: {1: 2},
            2022: {4: 1, 5: 2},
            2023: {7: 3},
        }

        # When
        transactions_year_month = summarizer.get_transactions_by_year_month()

        # Then
        assert transactions_year_month == expected_dict

    def test_get_total_balance(self, seed_db, transactions) -> None:
        # Given
        summarizer = TransactionSummarizer()
        expected_total = sum((t.value for t in transactions))

        # When
        total_balance = summarizer.get_total_balance()

        # Then
        assert expected_total == total_balance

    def test_get_average_debit(self, transactions, seed_db) -> None:
        # Given
        filtered_transactions = [t.value for t in transactions if t.value < 0]
        expected_avg = mean(filtered_transactions) if filtered_transactions else 0
        summarizer = TransactionSummarizer()

        # When
        avg_debit = summarizer.get_average_debit()

        # Then
        assert expected_avg == avg_debit

    def test_get_average_debit_no_debit_transactions(self, db) -> None:
        # Given
        summarizer = TransactionSummarizer()

        # When
        avg_debit = summarizer.get_average_debit()

        # Then
        assert avg_debit == 0

    def test_get_average_credit(self, transactions, seed_db) -> None:
        # Given
        filtered_transactions = [t.value for t in transactions if t.value > 0]
        expected_avg = mean(filtered_transactions) if filtered_transactions else 0
        summarizer = TransactionSummarizer()

        # When
        avg_credit = summarizer.get_average_credit()

        # Then
        assert expected_avg == avg_credit

    def test_get_average_credit_no_credit_transactions(self, db) -> None:
        # Given
        summarizer = TransactionSummarizer()

        # When
        avg_credit = summarizer.get_average_credit()

        # Then
        assert avg_credit == 0
