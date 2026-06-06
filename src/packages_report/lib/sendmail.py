#!/usr/bin/env python3
"""E-mail support for packages-report.

Copyright (C) 2026 Zdenek Styblik

This file is part of packages-report.

packages-report is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

packages-report is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with packages-report; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import datetime
import logging
import smtplib
from email.message import EmailMessage
from typing import List

from .config import SERVICE
from .config import SMTP_TIMEOUT

module_logger = logging.getLogger("{:s}.lib.sendmail".format(SERVICE))


def compose_email_message(
    mail_from_addr: str,
    mail_to_addr: str,
    subject: str,
    body: str,
    content_type: str,
) -> EmailMessage:
    """Compose e-mail message."""
    dtime = datetime.datetime.now(datetime.UTC)
    msg = EmailMessage()
    msg["From"] = mail_from_addr
    msg["To"] = mail_to_addr
    msg["Subject"] = subject
    # Date: Sun, 2 Jan 2022 23:45:02 +0000
    msg["Date"] = dtime.strftime("%a, %-d %b %Y %H:%M:%S %z")
    msg.set_payload(body.encode("utf-8"))
    msg["Content-Type"] = "{:s}; charset=utf-8".format(content_type)
    return msg


def sendmail(
    mail_from_addr: str,
    mail_to_addrs: List[str],
    subject: str,
    body: str,
    content_type: str,
    host: str = "localhost",
    port: int = 0,
) -> int:
    """Mailout via SMTP.

    Return RC > 0 and log error, if there was an error.

    :raises ValueError: raised on unsupported content_type
    """
    retval = 0
    if content_type not in ["text/plain", "application/json"]:
        raise ValueError("unsupported content_type '{}'".format(content_type))

    with smtplib.SMTP(host=host, port=port, timeout=SMTP_TIMEOUT) as server:
        server.ehlo()
        for mail_to_addr in mail_to_addrs:
            try:
                msg = compose_email_message(
                    mail_from_addr,
                    mail_to_addr,
                    subject,
                    body,
                    content_type,
                )
                server.send_message(msg)
            except Exception:
                retval = 1
                module_logger.exception(
                    "Exception has occurred while sending mail to '%s'.",
                    mail_to_addr,
                )

    return retval
