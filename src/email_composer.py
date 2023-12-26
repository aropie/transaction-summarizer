#! /usr/bin/python3
from calendar import month_name

from src.email_gateway import EmailGateway
from src.transaction_summarizer import TransactionSummarizer


class EmailComposer:
    def __init__(self):
        self.email_gateway = EmailGateway()
        self.summarizer = TransactionSummarizer()

    def compose_html_summary(self) -> str:
        html = """\
        <html>
        <body>
        """
        html += self._create_greeting()
        html += self._create_transactions_table()
        html += self._create_balance_and_averages()
        html += self._create_footer()
        html += """
        </body>
        </html>
        """

        return html

    def _create_greeting(self) -> str:
        html = """\
        <p>Hi!</p>
        <p>This is your automated transaction summary. Here it is:</p>
        """
        return html

    def _create_transactions_table(self) -> str:
        html = "<p>"
        transactions_year_month = self.summarizer.get_transactions_by_year_month()
        for year, transactions_by_month in transactions_year_month.items():
            transactions_in_year = sum(
                t_in_month for t_in_month in transactions_by_month.values()
            )
            html += f"<p><strong>Number of transactions in {year}: </strong>{transactions_in_year}"
            html += """\
            <table border="1" cellpadding="0" cellspacing="0" style="width:500px">
            <thead>
            <tr>
            <th scope="col">Month</th>
            <th scope="col">Number of transactions</th>
            </tr>
            </thead>
            <tbody>
            """
            for month, transactions in transactions_by_month.items():
                html += f"""\
                <tr>
                <td style="text-align:center">{month_name[month]}</td>
                <td style="text-align:center">{transactions}</td>
                </tr>
                """
            html += "</tbody></table>"
        html += "</p>"
        return html

    def _create_balance_and_averages(self):
        html = f"""
        <ul>
	<li><strong>Average credit amount: </strong>{self.summarizer.get_average_credit()}</li>
	<li><strong>Average debit amount: </strong>{self.summarizer.get_average_debit()}</li>
	<li><strong>Total Balance: </strong>{self.summarizer.get_total_balance()}</li>
        </ul>
        """
        return html

    def _create_footer(self) -> str:
        html = """
        <br><br>
        <p>Summarizer Bot&nbsp;<span style="font-size:18px">&nbsp;🤖</span></p>
        <p><a href="https://www.storicard.com/" target="_blank"><img alt="Stori" src="https://s4-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/560/600/original/logo_stori_1_(1).png" style="height:70px; width:100px" /></a></p>
        """
        return html
