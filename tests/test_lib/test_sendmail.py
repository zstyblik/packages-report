#!/usr/bin/env python3
"""Unit tests related to packages_report.lib.sendmail.py.

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
import pytest
from freezegun import freeze_time

from packages_report.lib import sendmail


def test_compose_email_message():
    """Test that compose_email_message() works as expected."""
    expected_from = "root+fromaddr@localhost"
    expected_to = "root+toaddr@localhost"
    expected_subject = "pytest subject"
    expected_body = "pytest test e-mail body"
    content_type = "text/plain"
    expected_content_type = 'text/plain; charset="utf-8"'
    expected_date = "Sun, 14 Jun 2026 22:00:00 +0000"

    with freeze_time("2026-06-14 22:00:00"):
        email_message = sendmail.compose_email_message(
            expected_from,
            expected_to,
            expected_subject,
            expected_body,
            content_type,
        )

    assert email_message["From"] == expected_from
    assert email_message["To"] == expected_to
    assert email_message["Subject"] == expected_subject
    assert email_message["Content-Type"] == expected_content_type
    assert email_message["Date"] == expected_date
    email_payload = email_message.get_payload()
    assert email_payload == expected_body


@pytest.mark.parametrize(
    "content_type",
    [
        "text/plain",
        "application/json",
    ],
)
def test_sendmail_happy_path(content_type, smtpserver):
    """Test that sendmail() works as expected."""
    expected_from = "root+mailfrom@localhost"
    expected_to = ["root+mailto1@localhost", "root+mailto2@localhost"]
    expected_subject = "pytest-packages-report"
    body = "pytest test"
    expected_body = "{}\r\n".format(body)
    expected_content_type = '{:s}; charset="utf-8"'.format(content_type)
    expected_date = "Mon, 15 Jun 2026 21:00:00 +0000"

    with freeze_time("2026-06-15 21:00:00"):
        sendmail.sendmail(
            expected_from,
            expected_to,
            expected_subject,
            body,
            content_type,
            host=smtpserver.addr[0],
            port=smtpserver.addr[1],
        )

    assert len(smtpserver.outbox) == 2

    for email in smtpserver.outbox:
        assert email["Subject"] == expected_subject
        assert email["From"] == expected_from
        assert email["To"] in expected_to
        # NOTE(zstyblik): workaround. Better solution next time.
        expected_to.remove(email["To"])

        assert email["Content-Type"] == expected_content_type
        assert email["Date"] == expected_date
        email_payload = email.get_payload()
        assert email_payload == expected_body


@pytest.mark.parametrize(
    "content_type",
    [
        "abcefg",
    ],
)
def test_sendmail_unsuppoted_content_type(content_type, smtpserver):
    """Test that sendmail() raises exception on unsupported content_type."""
    expected_excinfo = "unsupported content_type '{}'".format(content_type)
    with pytest.raises(ValueError) as excinfo:
        sendmail.sendmail(
            "root+mailfrom@localhost",
            ["root+mailto@localhost"],
            "pytest-packages-report",
            "pytest test",
            content_type,
            host=smtpserver.addr[0],
            port=smtpserver.addr[1],
        )

    assert expected_excinfo in str(excinfo)
    assert len(smtpserver.outbox) == 0
