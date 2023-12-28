#! /usr/bin/python3
import logging

from requests_toolbelt.multipart import decoder

from src.config import settings
from src.db.db import DBClientError
from src.email_gateway import EmailGatewayError
from src.transaction_seeder import MalformedInputFileError, TransactionSeeder
from src.transaction_summarizer import TransactionSummarizer


class BadRequestError(Exception):
    ...


BAD_REQUEST_MESSAGE = (
    "A csv file needs to be sent. The request needs to be "
    "of multipart/form-data content type."
)


def handle(event, context):
    logger = logging.getLogger(__name__)
    # TODO: Log level should be setup from env vars for different stages
    logger.setLevel(logging.INFO)
    try:
        logger.debug(f"File received: {event['body']}")

        event_body = event.get("body")
        if not event_body:
            raise BadRequestError(BAD_REQUEST_MESSAGE)
        multipart_data = decoder.MultipartDecoder(
            content=event_body.encode(),
            content_type=event["headers"].get("Content-Type"),
        )
        file = None
        for part in multipart_data.parts:
            content_type = part.headers.get("Content-Type".encode())
            if content_type and content_type.decode() == "text/csv":
                file = part.text
        if not file:
            raise BadRequestError(BAD_REQUEST_MESSAGE)
        file = file.split("\n")
        seeder = TransactionSeeder(logger=logger)
        seeder.parse_file(file)
        logger.info("CSV file parsed correctly")
        summarizer = TransactionSummarizer(logger=logger)
        summarizer.send_summary_email(settings.target_email, settings.email_subject)
        logger.info("Summary email sent successfully")
    except (BadRequestError, MalformedInputFileError) as e:
        logger.error(str(e))
        status_code = 400
        body = str(e)
    except (DBClientError, EmailGatewayError) as e:
        status_code = 502
        body = str(e)
        logger.error(str(e))
    except Exception as e:
        logger.error(str(e))
        status_code = 500
        body = str(e)
    else:
        status_code = 200
        body = "Input processed successfully"
    finally:
        return {"statusCode": status_code, "body": body}
