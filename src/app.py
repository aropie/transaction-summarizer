#! /usr/bin/python3
import logging
import re

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

        # Postman (among other clients) does not enforce HTTP/2
        # which says that header field names MUST be lowercase
        # so we iterate over the headers to make sure that we
        # find the one we need
        content_key = None
        for key in event["headers"]:
            if key.lower() == "content-type":
                content_key = key
                break

        multipart_data = decoder.MultipartDecoder(
            content=event_body.encode(),
            content_type=event["headers"].get(content_key),
        )
        file = None

        # Once the Multipart request has been decoded we need
        # to iterate over its parts to find the relevant item
        for part in multipart_data.parts:
            # MultipartDecoder transforms each of its parts' headers
            # into bytes. We transform it back into strings for easier
            # handling
            clean_headers = {
                k.decode(): v.decode()
                for k, v in part.headers.items()
                if isinstance(k, bytes)
            }
            part_found = re.findall('name="file"', clean_headers["Content-Disposition"])
            if part_found:
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
        logger.error(str(e))
        status_code = 502
        body = str(e)
    except Exception as e:
        logger.error(str(e))
        status_code = 500
        body = str(e)
    else:
        status_code = 200
        body = "Input processed successfully"
    finally:
        return {"statusCode": status_code, "body": body}
