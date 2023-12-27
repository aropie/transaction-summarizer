#! /usr/bin/python3


from src.db.db import DBClientError
from src.transaction_seeder import MalformedInputFileError, TransactionSeeder


def handle(event, context):
    try:
        file = event["body"].split("\n")
        seeder = TransactionSeeder()
        seeder.parse_file(file)
    except MalformedInputFileError as e:
        return {"statusCode": 400, "message": str(e)}
    except DBClientError as e:
        return {"statusCode": 502, "message": str(e)}
    return {"statusCode": 200, "message": "Input processed successfully"}
