#!/usr/bin/env python3
"""Unit tests related to packages_report.cli.py.

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
import json
import logging
import os
import sys
from unittest.mock import ANY
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from packages_report import cli
from packages_report.lib import models

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


@patch("packages_report.cli.socket.getfqdn")
def test_get_hostname(mock_getfqdn):
    """Test that get_hostname() does not call socket.getfqdn()."""
    expected = "pytest-host1"
    result = cli.get_hostname(expected)
    assert result == expected
    mock_getfqdn.assert_not_called()


@pytest.mark.parametrize(
    "input_hostname",
    [
        "",
        None,
    ],
)
@patch("packages_report.cli.socket.getfqdn")
def test_get_hostname_not_set(mock_getfqdn, input_hostname):
    """Test that get_hostname() calls socket.getfqdn() when hostname not set."""
    expected = "pytest-host2"
    mock_getfqdn.return_value = expected
    result = cli.get_hostname(input_hostname)
    assert result == expected
    mock_getfqdn.assert_called_once()


@pytest.mark.parametrize(
    "action,expected",
    [
        ("installed", "installed pkgs"),
        ("upgrades", "pkg upgrades"),
    ],
)
@patch("packages_report.lib.apt.get_installed_packages")
@patch("packages_report.lib.apt.get_package_upgrades")
def test_get_report_payload(
    mock_pkg_upgrades,
    mock_installed_pkgs,
    action,
    expected,
):
    """Test that get_report_payload() works as expected."""
    mock_installed_pkgs.return_value = "installed pkgs"
    mock_pkg_upgrades.return_value = "pkg upgrades"
    result = cli.get_report_payload(action)
    assert result == expected


@pytest.mark.parametrize(
    "action",
    [
        "",
        None,
        1234,
        "whatever",
        "i",
        "ugprades",
        "instaled",
        "upgrade",
        "install",
    ],
)
@patch("packages_report.lib.apt.get_installed_packages")
@patch("packages_report.lib.apt.get_package_upgrades")
def test_get_report_payload_exception(
    mock_pkg_upgrades,
    mock_installed_pkgs,
    action,
):
    """Test that get_report_payload_exception() raises exception as expected."""
    expected_msg = "action '{}' is not supported".format(action)
    with pytest.raises(ValueError) as exc_info:
        cli.get_report_payload(action)

    mock_installed_pkgs.assert_not_called()
    mock_pkg_upgrades.assert_not_called()
    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == expected_msg


@pytest.mark.parametrize(
    "action,expected",
    [
        ("installed", models.PackageMetadata),
        ("upgrades", models.PackageUpgrade),
    ],
)
def test_get_heading_cls(action, expected):
    """Test that get_heading_cls() returns expected class."""
    result = cli.get_heading_cls(action)
    assert result == expected


@pytest.mark.parametrize(
    "action",
    [
        "",
        None,
        1234,
        "whatever",
        "i",
        "ugprades",
        "instaled",
        "upgrade",
        "install",
    ],
)
def test_get_heading_cls_exception(action):
    """Test that get_heading_cls() raises exception on unsupported action."""
    expected_msg = "action '{}' is not supported".format(action)
    with pytest.raises(ValueError) as exc_info:
        cli.get_heading_cls(action)

    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == expected_msg


@pytest.mark.parametrize(
    "action,fmt,payload,report_fname",
    [
        (
            "installed",
            "text",
            [
                models.PackageMetadata(
                    state="ii",
                    name="adduser",
                    version="3.152",
                    arch="all",
                ),
            ],
            "report_installed_stdout_01.txt",
        ),
        (
            "upgrades",
            "text",
            [
                models.PackageUpgrade(
                    name="libngtcp2-16",
                    version="1.11.0-1+deb13u1",
                    origin="Debian-Security:13/stable-security",
                    arch="amd64",
                ),
            ],
            "report_upgrades_stdout_01.txt",
        ),
    ],
)
@freeze_time("2026-07-04 12:01:02")
@patch("packages_report.cli.get_report_payload")
def test_main_output_stdout_text(
    mock_get_payload, action, fmt, payload, report_fname, capsys
):
    """Test that TEXT format on STDOUT works as expected."""
    expected_report_fpath = os.path.join(SCRIPT_PATH, "files", report_fname)
    mock_get_payload.return_value = payload
    args = [
        "packages_report",
        "--{:s}".format(action),
        "--hostname",
        "pytest-host",
        "--format",
        "{:s}".format(fmt),
        "--output",
        "stdout",
    ]
    exception = None
    with patch.object(sys, "argv", args):
        try:
            cli.main()
        except SystemExit as exc:
            exception = exc

    assert isinstance(exception, SystemExit) is True
    assert exception.code == 0
    mock_get_payload.assert_called_once_with(action)

    with open(expected_report_fpath, "r", encoding="utf-8") as fhandle:
        expected_report = fhandle.readlines()

    out, err = capsys.readouterr()
    assert out == "".join(expected_report)
    assert err == ""


@pytest.mark.parametrize(
    "action,fmt,payload,report_fname",
    [
        (
            "installed",
            "json",
            [
                models.PackageMetadata(
                    state="ii",
                    name="adduser",
                    version="3.152",
                    arch="all",
                ),
            ],
            "report_installed_stdout_01.json",
        ),
        (
            "upgrades",
            "json",
            [
                models.PackageUpgrade(
                    name="libngtcp2-16",
                    version="1.11.0-1+deb13u1",
                    origin="Debian-Security:13/stable-security",
                    arch="amd64",
                ),
            ],
            "report_upgrades_stdout_01.json",
        ),
    ],
)
@freeze_time("2026-07-04 12:01:02")
@patch("packages_report.cli.get_report_payload")
def test_main_output_stdout_json(
    mock_get_payload, action, fmt, payload, report_fname, capsys
):
    """Test that JSON format on STDOUT works as expected.

    Because payload is a list, therefore inconsistent, these have to be two
    separate tests.
    """
    expected_report_fpath = os.path.join(SCRIPT_PATH, "files", report_fname)
    mock_get_payload.return_value = payload
    args = [
        "packages_report",
        "--{:s}".format(action),
        "--hostname",
        "pytest-host",
        "--format",
        "{:s}".format(fmt),
        "--output",
        "stdout",
    ]
    exception = None
    with patch.object(sys, "argv", args):
        try:
            cli.main()
        except SystemExit as exc:
            exception = exc

    assert isinstance(exception, SystemExit) is True
    assert exception.code == 0
    mock_get_payload.assert_called_once_with(action)

    out, err = capsys.readouterr()
    assert err == ""

    with open(expected_report_fpath, "r", encoding="utf-8") as fhandle:
        expected_report = json.load(fhandle)

    result = json.loads(out)
    # NOTE(zstyblik): payload is a list, test would be flaky.
    result["payload"].sort(key=lambda x: x["name"])
    expected_report["payload"].sort(key=lambda x: x["name"])
    assert result == expected_report


@pytest.mark.parametrize(
    "action,fmt,payload,report_fname",
    [
        (
            "installed",
            "text",
            [
                models.PackageMetadata(
                    state="ii",
                    name="adduser",
                    version="3.152",
                    arch="all",
                ),
            ],
            "report_installed_stdout_01.txt",
        ),
        (
            "upgrades",
            "text",
            [
                models.PackageUpgrade(
                    name="libngtcp2-16",
                    version="1.11.0-1+deb13u1",
                    origin="Debian-Security:13/stable-security",
                    arch="amd64",
                ),
            ],
            "report_upgrades_stdout_01.txt",
        ),
    ],
)
@freeze_time("2026-07-04 12:01:02")
@patch("packages_report.cli.get_report_payload")
@patch("packages_report.lib.sendmail.sendmail")
def test_main_output_mail_text(
    mock_sendmail, mock_get_payload, action, fmt, payload, report_fname, capsys
):
    """Test that TEXT format with MAIL out works as expected."""
    expected_report_fpath = os.path.join(SCRIPT_PATH, "files", report_fname)
    mock_get_payload.return_value = payload
    mock_sendmail.return_value = 0
    args = [
        "packages_report",
        "--{:s}".format(action),
        "--hostname",
        "pytest-host",
        "--format",
        "{:s}".format(fmt),
        "--output",
        "mail",
    ]
    exception = None
    with patch.object(sys, "argv", args):
        try:
            cli.main()
        except SystemExit as exc:
            exception = exc

    assert isinstance(exception, SystemExit) is True
    assert exception.code == 0
    mock_get_payload.assert_called_once_with(action)

    with open(expected_report_fpath, "r", encoding="utf-8") as fhandle:
        expected_report = fhandle.readlines()

    mock_sendmail.assert_called_once_with(
        "root@localhost",
        ["root@localhost"],
        "Packages report for pytest-host (Linux)",
        "".join(expected_report),
        "text/plain",
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


@pytest.mark.parametrize(
    "action,fmt,payload,report_fname",
    [
        (
            "installed",
            "json",
            [
                models.PackageMetadata(
                    state="ii",
                    name="adduser",
                    version="3.152",
                    arch="all",
                ),
            ],
            "report_installed_stdout_01.json",
        ),
        (
            "upgrades",
            "json",
            [
                models.PackageUpgrade(
                    name="libngtcp2-16",
                    version="1.11.0-1+deb13u1",
                    origin="Debian-Security:13/stable-security",
                    arch="amd64",
                ),
            ],
            "report_upgrades_stdout_01.json",
        ),
    ],
)
@freeze_time("2026-07-04 12:01:02")
@patch("packages_report.cli.get_report_payload")
@patch("packages_report.lib.sendmail.sendmail")
def test_main_output_mail_json(
    mock_sendmail, mock_get_payload, action, fmt, payload, report_fname, capsys
):
    """Test that JSON format with MAIL works as expected.

    Because payload is a list, therefore inconsistent, these have to be two
    separate tests.
    """
    expected_report_fpath = os.path.join(SCRIPT_PATH, "files", report_fname)
    mock_get_payload.return_value = payload
    mock_sendmail.return_value = 0
    args = [
        "packages_report",
        "--{:s}".format(action),
        "--hostname",
        "pytest-host",
        "--format",
        "{:s}".format(fmt),
        "--output",
        "mail",
    ]
    exception = None
    with patch.object(sys, "argv", args):
        try:
            cli.main()
        except SystemExit as exc:
            exception = exc

    assert isinstance(exception, SystemExit) is True
    assert exception.code == 0
    mock_get_payload.assert_called_once_with(action)

    with open(expected_report_fpath, "r", encoding="utf-8") as fhandle:
        expected_report = json.load(fhandle)

    mock_sendmail.assert_called_once_with(
        "root@localhost",
        ["root@localhost"],
        "Packages report for pytest-host (Linux)",
        ANY,
        "application/json",
    )
    body = mock_sendmail.call_args[0][3]
    result = json.loads(body)
    # NOTE(zstyblik): payload is a list, test would be flaky.
    result["payload"].sort(key=lambda x: x["name"])
    expected_report["payload"].sort(key=lambda x: x["name"])
    assert result == expected_report

    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


@pytest.mark.parametrize(
    "action,fmt,output",
    [
        ("installed", "text", "stdout"),
        ("upgrades", "text", "stdout"),
        ("installed", "json", "stdout"),
        ("upgrades", "json", "stdout"),
        ("installed", "text", "mail"),
        ("upgrades", "text", "mail"),
        ("installed", "json", "mail"),
        ("upgrades", "json", "mail"),
    ],
)
@patch("packages_report.cli.get_report_payload")
def test_main_no_payload(mock_get_payload, action, fmt, output, capsys, caplog):
    """Test that main() exists as expected when there is no payload."""
    expected_log_records = [
        (
            "packages-report",
            20,
            "Nothing to report.",
        ),
    ]
    mock_get_payload.return_value = []
    args = [
        "packages_report",
        "--{:s}".format(action),
        "--hostname",
        "pytest-host",
        "--format",
        "{:s}".format(fmt),
        "--output",
        "{:s}".format(output),
        "-vvv",
    ]
    exception = None
    with patch.object(sys, "argv", args):
        with caplog.at_level(logging.INFO):
            try:
                cli.main()
            except SystemExit as exc:
                exception = exc

    assert isinstance(exception, SystemExit) is True
    assert exception.code == 0
    mock_get_payload.assert_called_once_with(action)

    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert caplog.record_tuples == expected_log_records
