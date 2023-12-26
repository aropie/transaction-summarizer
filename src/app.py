#! /usr/bin/python3
import os


def handle(event, context):
    print(os.environ.get("MESSAGE", "No message found in env vars!"))
    return "Yahoooooooo this works!"
