#!/usr/bin/env python3
"""Configuration options for packages-report.

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
import io
import sys
from typing import Any

ACTIONS = ["installed", "upgrades"]
DEFAULT_MAIL_FROM_ADDR = "root@localhost"
DEFAULT_MAIL_TO_ADDRS = ["root@localhost"]
# E-mail content types based on output format.
CONTENT_TYPES = {
    "json": "application/json",
    "text": "text/plain",
}
FORMATS = ["json", "text"]
OUTPUT_DESTINATIONS = ["mail", "stdout"]
SERVICE = "packages-report"
SMTP_TIMEOUT = 30  # seconds


def get_output_destination(output_name: str) -> Any:
    """Return output destination based on lookup.

    NOTE(zstyblik): this used to be simple k->v lookup in const/"global" var.
    However, then it was impossible to capture stdout in pytest. Maybe all I had
    to do was to wrap it inside function like this.

    :raises KeyError: raised on unsupported output
    """
    if output_name == "stdout":
        return sys.stdout
    elif output_name == "mail":
        return io.StringIO()

    raise KeyError("unsupported output '{}'".format(output_name))
