#!/usr/bin/env python3
"""Report either on installed packages or pending package upgrades.

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
import argparse
import datetime
import logging
import socket
import sys

from .lib import apt
from .lib import config
from .lib import formatters
from .lib import sendmail
from .lib.models import PackageMetadata
from .lib.models import PackageReport
from .lib.models import PackageUpgrade


def calc_log_level(count: int) -> int:
    """Return logging log level as int based on count."""
    log_lvl = 40 - max(count, 0) * 10
    log_lvl = max(log_lvl, 10)
    return log_lvl


def get_hostname(hostname: str) -> str:
    """Either return hostname given as an arg or try to determine one."""
    if not hostname:
        hostname = socket.getfqdn()

    return hostname


def get_report_payload(action: str):
    """Return information about packages based on action.

    :raises ValueError: raised when unsupported action is given
    """
    if action == "installed":
        return apt.get_installed_packages()
    elif action == "upgrades":
        return apt.get_package_upgrades()

    raise ValueError("action '{}' is not supported".format(action))


def get_heading_cls(action: str) -> PackageMetadata | PackageUpgrade:
    """Determine which class should be used to format report's heading.

    :raises ValueError: raised when unsupported action is given
    """
    if action == "installed":
        return PackageMetadata
    elif action == "upgrades":
        return PackageUpgrade

    raise ValueError("action '{}' is not supported".format(action))


def main() -> None:
    """Parse args, init logging, gather information and generate report."""
    args = parse_args()
    logging.basicConfig(level=args.log_level, stream=sys.stderr)
    logger = logging.getLogger(config.SERVICE)
    logger.setLevel(args.log_level)

    hostname = get_hostname(args.hostname)
    action = args.action
    dtime = datetime.datetime.now(datetime.UTC)
    package_report = PackageReport(
        datetime=dtime.strftime("%Y-%m-%dT%H:%M:%SZ%z"),
        hostname=hostname,
        report_type=action,
        service=config.SERVICE,
    )
    if action not in config.ACTIONS:
        logger.error("Action '%s' is not supported.", action)
        sys.exit(1)

    package_report.payload = get_report_payload(action)
    if not package_report.payload:
        logger.info("Nothing to report.")
        sys.exit(0)

    output_name = args.output_name
    output_dest = config.get_output_destination(output_name)
    fmt = args.fmt
    if fmt == "json":
        formatters.fmt_json(package_report, output_dest)
    elif fmt == "text":
        heading_cls = get_heading_cls(action)
        formatters.fmt_text(package_report, heading_cls, output_dest)
    else:
        logger.error("Format '%s' is not supported.", fmt)
        sys.exit(1)

    retcode = 255
    if output_name == "stdout":
        retcode = 0
    elif output_name == "mail":
        output_dest.seek(0)
        body = "".join(output_dest)
        subject = "Packages report for {:s} (Linux)".format(
            package_report.hostname
        )
        content_type = config.CONTENT_TYPES.get(fmt, "text/plain")
        retcode = sendmail.sendmail(
            args.mail_from_addr,
            args.mail_to_addrs,
            subject,
            body,
            content_type,
        )
    else:
        logger.error("Output '%s' is not supported.", output_name)
        retcode = 1

    sys.exit(retcode)


def parse_args() -> argparse.Namespace:
    """Return parsed CLI args."""
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=(
            "Generate report either on installed packages"
            " or pending package upgrades."
        ),
        epilog="{:s}, Copyright (C) 2026 Zdenek Styblik".format(config.SERVICE),
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="text",
        choices=config.FORMATS,
        help="Output format. Defaults to '%(default)s'.",
    )
    parser.add_argument(
        "--hostname",
        type=str,
        default=None,
        help="Override reported hostname.",
    )
    parser.add_argument(
        "--mail-from",
        dest="mail_from_addr",
        default=config.DEFAULT_MAIL_FROM_ADDR,
        type=str,
        help="Mail from address. Defaults to '%(default)s'.",
    )
    parser.add_argument(
        "--mail-to",
        action="append",
        dest="mail_to_addrs",
        type=str,
        help="Mail report to given address(can be given multiple times).",
    )
    parser.add_argument(
        "--output",
        default="stdout",
        dest="output_name",
        choices=config.OUTPUT_DESTINATIONS,
        help="Output where report will be written. Defaults to '%(default)s'.",
    )
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--installed",
        dest="action",
        action="store_const",
        const="installed",
        help="Create report on installed packages.",
    )
    action_group.add_argument(
        "--upgrades",
        dest="action",
        action="store_const",
        const="upgrades",
        help="Create report on available package upgrades.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log level verbosity. Can be passed multiple times.",
    )
    args = parser.parse_args()
    args.log_level = calc_log_level(args.verbose)
    if not args.mail_to_addrs:
        args.mail_to_addrs = config.DEFAULT_MAIL_TO_ADDRS

    return args


if __name__ == "__main__":
    main()
