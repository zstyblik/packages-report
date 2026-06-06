#!/usr/bin/env python3
"""Unit tests related to packages_report.lib.models.py.

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
import io
import json
import os

import pytest
from freezegun import freeze_time

from packages_report.lib import formatters
from packages_report.lib import models

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.parametrize(
    "heading_cls,packages,expected",
    [
        (
            models.PackageMetadata,
            {
                models.PackageMetadata(
                    state="ii",
                    name="pytest-pkg1",
                    version="1.2.3",
                    arch="amd64",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="pytest-some-pkg1",
                    version="1",
                    arch="i386",
                ),
            },
            {
                "arch": 5,
                "name": 16,
                "version": 7,
            },
        ),
        (
            models.PackageUpgrade,
            {
                models.PackageUpgrade(
                    name="pytest-pkg1",
                    version="1.2.3",
                    origin="pytest/origin/security",
                    arch="amd64",
                ),
                models.PackageUpgrade(
                    name="pytest-some-pkg1",
                    version="1",
                    origin="pytest/origin/supersec",
                    arch="i586",
                ),
            },
            {
                "arch": 5,
                "name": 16,
                "origin": 22,
                "version": 7,
            },
        ),
    ],
)
def test_determine_col_widths(heading_cls, packages, expected):
    """Test that determine_col_widths() works as expected."""
    result = formatters.determine_col_widths(heading_cls, packages)
    assert result == expected


def test_fmt_json():
    """Test that fmt_json() works as expected."""
    expected = {
        "datetime": "2026-06-19T23:30:00Z+0000",
        "hostname": "pytest-localhost",
        "payload": [
            {
                "arch": "amd64",
                "name": "pytest-pkg1",
                "state": "ii",
                "version": "1.2.3",
            },
            {
                "arch": "amd64",
                "name": "pytest-pkg2",
                "origin": "pytest/origin/security",
                "version": "1.2.4",
            },
        ],
        "report_type": "installed",
        "service": "pytest-test",
        "version": 1,
    }
    buff = io.StringIO()
    with freeze_time("2026-06-19 23:30:00"):
        dtime = datetime.datetime.now(datetime.UTC)

    package_report = models.PackageReport(
        datetime=dtime.strftime("%Y-%m-%dT%H:%M:%SZ%z"),
        hostname="pytest-localhost",
        report_type="installed",
        service="pytest-test",
    )
    # NOTE(zstyblik): this is a mixed payload which wouldn't happen, but I'm
    # being a bit lazy regarding tests.
    payload = [
        models.PackageMetadata(
            state="ii",
            name="pytest-pkg1",
            version="1.2.3",
            arch="amd64",
        ),
        models.PackageUpgrade(
            name="pytest-pkg2",
            version="1.2.4",
            origin="pytest/origin/security",
            arch="amd64",
        ),
    ]
    package_report.payload = set(payload)
    formatters.fmt_json(package_report, buff)

    buff.seek(0)
    result = json.load(buff)
    assert "payload" in result
    # NOTE(zstyblik): payload is a list, test would be flaky.
    result["payload"].sort(key=lambda x: x["name"])
    expected["payload"].sort(key=lambda x: x["name"])
    assert result == expected


@pytest.mark.parametrize(
    "heading_cls,report_type,payload,expected_report_fname",
    [
        (
            models.PackageMetadata,
            "installed",
            [
                models.PackageMetadata(
                    state="ii",
                    name="pytest-pkg1",
                    version="1.2.3",
                    arch="amd64",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="pytest-some-pkg1",
                    version="1",
                    arch="i386",
                ),
            ],
            "report_installed_01.txt",
        ),
        (
            models.PackageUpgrade,
            "upgrades",
            [
                models.PackageUpgrade(
                    name="pytest-pkg1",
                    version="1.2.3",
                    origin="pytest/origin/security",
                    arch="amd64",
                ),
                models.PackageUpgrade(
                    name="pytest-some-pkg1",
                    version="2.41-12+deb13u3",
                    origin="pytest/origin/supersec",
                    arch="i586",
                ),
            ],
            "report_upgrades_01.txt",
        ),
    ],
)
def test_fmt_text(heading_cls, report_type, payload, expected_report_fname):
    """Test that fmt_text() works as expected."""
    buff = io.StringIO()
    with freeze_time("2026-06-19 23:30:00"):
        dtime = datetime.datetime.now(datetime.UTC)

    package_report = models.PackageReport(
        datetime=dtime.strftime("%Y-%m-%dT%H:%M:%SZ%z"),
        hostname="pytest-localhost",
        report_type=report_type,
        service="pytest-test",
    )
    package_report.payload = set(payload)
    formatters.fmt_text(
        package_report,
        heading_cls,
        buff,
    )

    fixture_fpath = os.path.join(SCRIPT_PATH, "files", expected_report_fname)
    with open(fixture_fpath, "r", encoding="utf-8") as fhandle:
        fixture_data = fhandle.readlines()

    expected = "".join(fixture_data)
    buff.seek(0)
    result = "".join(buff)
    assert result == expected
