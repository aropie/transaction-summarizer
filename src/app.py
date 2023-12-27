#! /usr/bin/python3


import logging

from src.config import settings
from src.db.db import DBClientError
from src.email_gateway import EmailGatewayError
from src.transaction_seeder import MalformedInputFileError, TransactionSeeder
from src.transaction_summarizer import TransactionSummarizer

summarizer = TransactionSummarizer()
summarizer.send_summary_email(settings.target_email, settings.email_subject)


def handle(event, context):
    logger = logging.getLogger(__name__)
    # TODO: Log level should be setup from env vars for different stages
    logger.setLevel(logging.INFO)
    try:
        file = event["body"].split("\n")
        seeder = TransactionSeeder(logger=logger)
        seeder.parse_file(file)
        logger.info("CSV file parsed correctly")
        summarizer = TransactionSummarizer(logger=logger)
        summarizer.send_summary_email(settings.target_email, settings.email_subject)
        logger.info("Summary email sent successfully")
    except MalformedInputFileError as e:
        return {"statusCode": 400, "message": str(e)}
    except (DBClientError, EmailGatewayError) as e:
        return {"statusCode": 502, "message": str(e)}
    return {"statusCode": 200, "message": "Input processed successfully"}
