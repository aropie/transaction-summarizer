#! /usr/bin/python3


from src.config import settings
from src.db.db import DBClientError
from src.email_gateway import EmailGatewayError
from src.transaction_seeder import MalformedInputFileError, TransactionSeeder
from src.transaction_summarizer import TransactionSummarizer

summarizer = TransactionSummarizer()
summarizer.send_summary_email(settings.target_email, settings.email_subject)


def handle(event, context):
    try:
        file = event["body"].split("\n")
        seeder = TransactionSeeder()
        seeder.parse_file(file)
        summarizer = TransactionSummarizer()
        summarizer.send_summary_email(settings.target_email, settings.email_subject)
    except MalformedInputFileError as e:
        return {"statusCode": 400, "message": str(e)}
    except (DBClientError, EmailGatewayError) as e:
        return {"statusCode": 502, "message": str(e)}
    return {"statusCode": 200, "message": "Input processed successfully"}
