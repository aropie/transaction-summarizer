#! /usr/bin/python3
import logging
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import Logger
from smtplib import SMTP_SSL, SMTPException
from typing import Optional

from src.config import settings


class EmailGatewayError(Exception):
    pass


class EmailGateway:
    def __init__(self, logger: Optional[Logger] = None) -> None:
        self.log = logger or logging.getLogger(__name__)
        self.smtp_server = settings.smtp_server
        self.port = settings.smtp_port
        self.email = settings.sender_email_address
        self.password = settings.sender_email_password
        self._context = ssl.create_default_context()

    def send_email(self, target_email, subject, plaintext, html) -> None:
        # "alternative" subtype is being used to also send a plain text
        # version since not all email clients support HTML and some
        # people might choose to only receive plain-text emails
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.email
        message["To"] = target_email

        part1 = MIMEText(plaintext, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)
        with SMTP_SSL(self.smtp_server, self.port, context=self._context) as server:
            try:
                self.log.debug("Attempting to connect to SMTP server")
                server.login(self.email, self.password)
                self.log.debug("Connection to SMTP server successfull")
                self.log.debug("Attempting to send email")
                server.sendmail(self.email, target_email, message.as_string())
                self.log.debug("Email succesfully sent")
            except SMTPException as e:
                raise EmailGatewayError("There was a problem sending the email") from e
