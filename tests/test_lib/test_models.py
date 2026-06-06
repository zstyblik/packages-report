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

from freezegun import freeze_time

from packages_report.lib import models


def test_package_report_init():
    """Test that PackageReport()."""
    with freeze_time("2026-06-14 22:00:00"):
        dtime = datetime.datetime.now(datetime.UTC)
        expected_datetime = dtime.strftime("%Y-%m-%dT%H:%M:%SZ%z")

    expected_hostname = "pytest"
    expected_report_type = "pytest-report"
    expected_service = "pytest-service"
    expected_payload = set([])
    expected_version = 1

    report = models.PackageReport(
        datetime=expected_datetime,
        hostname=expected_hostname,
        report_type=expected_report_type,
        service=expected_service,
    )
    assert report.datetime == expected_datetime
    assert report.hostname == expected_hostname
    assert report.report_type == expected_report_type
    assert report.service == expected_service
    assert report.payload == expected_payload
    assert report.version == expected_version


def test_package_metadata_init():
    """Test PackageMetadata()."""
    expected_state = "ii"
    expected_name = "pytest-pkg"
    expected_version = "1.2.3"
    expected_arch = "i386"

    pkg_metadata = models.PackageMetadata(
        state=expected_state,
        name=expected_name,
        version=expected_version,
        arch=expected_arch,
    )

    assert pkg_metadata.state == expected_state
    assert pkg_metadata.name == expected_name
    assert pkg_metadata.version == expected_version
    assert pkg_metadata.arch == expected_arch


def test_package_metadata_fmt_text_header():
    """Test that PackageMetadata table header works as expected."""
    expected_header = "| Name       | Version    | Arch       |"
    col_widths = {
        "arch": 10,
        "name": 10,
        "state": 10,
        "version": 10,
    }
    header = models.PackageMetadata.fmt_text_header(col_widths)
    assert header == expected_header


def test_package_metadata_fmt_text_header_separator():
    """Test that PackageMetadata table row separator works as expected."""
    expected_header_sep = "|------------|------------|------------|"
    col_widths = {
        "arch": 10,
        "name": 10,
        "state": 10,
        "version": 10,
    }
    header_sep = models.PackageMetadata.fmt_text_header_separator(col_widths)
    assert header_sep == expected_header_sep


def test_package_metadata_fmt_text_table_row():
    """Test that PackageMetadata text table row formatting works as expected."""
    expected_row = "| pytest-pkg | 1.2.3      | i386       |"
    col_widths = {
        "arch": 10,
        "name": 10,
        "state": 10,
        "version": 10,
    }
    pkg_metadata = models.PackageMetadata(
        state="ii",
        name="pytest-pkg",
        version="1.2.3",
        arch="i386",
    )
    row = pkg_metadata.fmt_text_table_row(col_widths)
    assert row == expected_row


def test_package_metadata_col_widths():
    """Test that PackageMetadata.get_col_widths() work as expected."""
    expected_col_widths = {
        "arch": 4,
        "name": 10,
        "state": 2,
        "version": 5,
    }
    pkg_metadata = models.PackageMetadata(
        state="ii",
        name="pytest-pkg",
        version="1.2.3",
        arch="i386",
    )
    col_widths = pkg_metadata.get_col_widths()
    assert col_widths == expected_col_widths


def test_package_metadata_col_names():
    """Test PackageMetadata() returns expected col names."""
    expected_col_names = [
        "Name",
        "Version",
        "Arch",
    ]
    col_names = models.PackageMetadata.get_header_col_names()
    assert sorted(expected_col_names) == sorted(col_names)


def test_package_upgrade_init():
    """Test PackageUpgrade()."""
    expected_name = "pytest-pkg"
    expected_version = "3.2.1"
    expected_origin = "pytest/origin"
    expected_arch = "amd64"

    pkg_upgrade = models.PackageUpgrade(
        name=expected_name,
        version=expected_version,
        origin=expected_origin,
        arch=expected_arch,
    )

    assert pkg_upgrade.name == expected_name
    assert pkg_upgrade.version == expected_version
    assert pkg_upgrade.origin == expected_origin
    assert pkg_upgrade.arch == expected_arch


def test_package_upgrade_fmt_text_header():
    """Test that PackageUpgrade table header works as expected."""
    expected_header = "| Name       | Version    | Arch       | Origin     |"
    col_widths = {
        "arch": 10,
        "name": 10,
        "origin": 10,
        "version": 10,
    }
    header = models.PackageUpgrade.fmt_text_header(col_widths)
    assert header == expected_header


def test_package_upgrade_fmt_text_header_separator():
    """Test that PackageUpgrade table row separator works as expected."""
    expected_header_sep = (
        "|------------|------------|------------|------------|"
    )
    col_widths = {
        "arch": 10,
        "name": 10,
        "origin": 10,
        "version": 10,
    }
    header_sep = models.PackageUpgrade.fmt_text_header_separator(col_widths)
    assert header_sep == expected_header_sep


def test_package_upgrade_fmt_text_table_row():
    """Test that PackageUpgrade text table row formatting works as expected."""
    expected_row = "| pytest-pkg | 1.2.3      | i386       | pytest/origin |"
    col_widths = {
        "arch": 10,
        "name": 10,
        "origin": 10,
        "version": 10,
    }
    pkg_upgrade = models.PackageUpgrade(
        name="pytest-pkg",
        version="1.2.3",
        origin="pytest/origin",
        arch="i386",
    )
    row = pkg_upgrade.fmt_text_table_row(col_widths)
    assert row == expected_row


def test_package_upgrade_col_widths():
    """Test that PackageMetadata.get_col_widths() work as expected."""
    expected_col_widths = {
        "arch": 4,
        "name": 10,
        "origin": 13,
        "version": 5,
    }
    pkg_upgrade = models.PackageUpgrade(
        name="pytest-pkg",
        version="1.2.3",
        origin="pytest/origin",
        arch="i386",
    )
    col_widths = pkg_upgrade.get_col_widths()
    assert col_widths == expected_col_widths


def test_package_upgrade_col_names():
    """Test PackageUpgrade() returns expected col names."""
    expected_col_names = [
        "Name",
        "Version",
        "Arch",
        "Origin",
    ]
    col_names = models.PackageUpgrade.get_header_col_names()
    assert sorted(expected_col_names) == sorted(col_names)
