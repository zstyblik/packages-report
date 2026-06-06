#!/usr/bin/env python3
"""Unit tests for packages_report.lib.apt.py.

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
import logging
import os
from unittest.mock import ANY
from unittest.mock import call
from unittest.mock import Mock  # noqa: I100
from unittest.mock import patch

import pytest

from packages_report.lib import apt
from packages_report.lib import models

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


@patch("packages_report.lib.apt.run_dpkg")
def test_get_installed_packages(mock_run_dpkg):
    """Test that get_installed_packages() works as expected."""
    expected = set(
        [
            models.PackageMetadata(
                state="ii",
                name="adduser",
                version="3.152",
                arch="all",
            ),
        ]
    )
    mock_run_dpkg.return_value = "ii  adduser 3.152 all add"
    result = apt.get_installed_packages()

    mock_run_dpkg.assert_called_once_with()
    assert result == expected


@patch("packages_report.lib.apt.run_apt_get")
def test_get_package_upgrades(mock_run_apt_get):
    """Test that get_package_upgrades() works as expected."""
    expected_calls = [call("upgrade"), call("dist-upgrade")]
    expected = set(
        [
            models.PackageUpgrade(
                name="libngtcp2-16",
                version="1.11.0-1+deb13u1",
                origin="Debian-Security:13/stable-security",
                arch="amd64",
            ),
        ]
    )
    mock_run_apt_get.return_value = (
        "Conf libngtcp2-16 (1.11.0-1+deb13u1 "
        "Debian-Security:13/stable-security [amd64])"
    )
    result = apt.get_package_upgrades()

    assert mock_run_apt_get.call_count == 2
    mock_run_apt_get.assert_has_calls(expected_calls)
    assert result == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            "ii  adduser 3.152 all add and remove users and groups",
            models.PackageMetadata(
                state="ii",
                name="adduser",
                version="3.152",
                arch="all",
            ),
        ),
        (
            (
                "ii  libbpf1:amd64 1:1.5.0-3 amd64  eBPF helper library "
                "   (shared library)"
            ),
            models.PackageMetadata(
                state="ii",
                name="libbpf1",
                version="1:1.5.0-3",
                arch="amd64",
            ),
        ),
    ],
)
def test_parse_dpkg_line(input_data, expected):
    """Test that parse_dpkg_line() works as expected."""
    result = apt.parse_dpkg_line(input_data)
    assert result == expected


@pytest.mark.parametrize(
    "fixture_fname,expected",
    [
        (
            "fixture_dpkg_01.txt",
            {
                models.PackageMetadata(
                    state="ii",
                    name="apparmor",
                    version="4.1.0-1",
                    arch="amd64",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="cloud-initramfs-growroot",
                    version="0.18.debian14",
                    arch="all",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="apt",
                    version="3.0.3",
                    arch="amd64",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="augeas-lenses",
                    version="1.14.1-1.1~deb13u1",
                    arch="all",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="base-files",
                    version="13.8+deb13u4",
                    arch="amd64",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="bsd-mailx",
                    version="8.1.2-0.20220412cvs-1.1",
                    arch="amd64",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="ca-certificates",
                    version="20250419",
                    arch="all",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="libbpf1",
                    version="1:1.5.0-3",
                    arch="amd64",
                ),
                models.PackageMetadata(
                    state="ii",
                    name="adduser",
                    version="3.152",
                    arch="all",
                ),
            },
        ),
    ],
)
def test_parse_package_list(fixture_fname, expected):
    """Test that parse_package_list() works as expected."""
    fname = os.path.join(SCRIPT_PATH, "files", fixture_fname)
    with open(fname, "r", encoding="utf-8") as fhandle:
        test_data = fhandle.readlines()

    test_data = "".join(test_data)
    result = apt.parse_package_list(test_data)
    assert result == expected


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (
            (
                "Conf libngtcp2-16 (1.11.0-1+deb13u1"
                " Debian-Security:13/stable-security [amd64])"
            ),
            models.PackageUpgrade(
                name="libngtcp2-16",
                version="1.11.0-1+deb13u1",
                origin="Debian-Security:13/stable-security",
                arch="amd64",
            ),
        ),
    ],
)
def test_parse_package_upgrade(input_data, expected):
    """Test that parse_package_upgrade() works as expected."""
    result = apt.parse_package_upgrade(input_data)
    assert result == expected


@pytest.mark.parametrize(
    "fixture_fname,expected",
    [
        (
            "fixture_apt_upgrades_01.txt",
            {
                models.PackageUpgrade(
                    name="libngtcp2-16",
                    version="1.11.0-1+deb13u1",
                    origin="Debian-Security:13/stable-security",
                    arch="amd64",
                ),
                models.PackageUpgrade(
                    name="libngtcp2-crypto-gnutls8",
                    version="1.11.0-1+deb13u1",
                    origin="Debian-Security:13/stable-security",
                    arch="amd64",
                ),
            },
        ),
    ],
)
def test_parse_package_upgrades(fixture_fname, expected):
    """Test that parse_package_upgrades() works as expected."""
    fname = os.path.join(SCRIPT_PATH, "files", fixture_fname)
    with open(fname, "r", encoding="utf-8") as fhandle:
        test_data = fhandle.readlines()

    test_data = "".join(test_data)
    result = apt.parse_package_upgrades(test_data)
    assert result == expected


@pytest.mark.parametrize(
    "input_data",
    [
        "abc",
        "",
        None,
        1234,
    ],
)
def test_run_apt_get_input_check(input_data):
    """Check that ValueError is raised on unsupported action."""
    expected = "atp-get action '{}' is not supported".format(input_data)
    with pytest.raises(ValueError) as exc_info:
        apt.run_apt_get(input_data)

    assert expected in str(exc_info.value)


@pytest.mark.parametrize(
    "action",
    [
        "dist-upgrade",
        "upgrade",
    ],
)
@patch("packages_report.lib.apt.subprocess")
def test_run_apt_get(mock_subprocess, action, caplog):
    """Test that run_apt_get() works as expected."""
    expected_log_records = [
        (
            "packages-report.lib.apt",
            10,
            "apt-get {:s} STDOUT: 'b'stdout''".format(action),
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get {:s} STDERR: 'b'stderr''".format(action),
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get {:s} RC: 0".format(action),
        ),
    ]

    mock_popen = Mock()
    mock_popen.communicate.return_value = (b"stdout", b"stderr")
    mock_popen.returncode = 0
    mock_subprocess.Popen.return_value.__enter__.return_value = mock_popen
    with caplog.at_level(logging.DEBUG, logger="packages-report.lib.apt"):
        result = apt.run_apt_get(action)

    assert result == "stdout"
    assert caplog.record_tuples == expected_log_records
    mock_subprocess.Popen.assert_called_once_with(
        ["/usr/bin/apt-get", "-s", action],
        stdout=ANY,
        stderr=ANY,
    )
    mock_popen.communicate.assert_called_once_with()


@pytest.mark.parametrize(
    "action",
    [
        "dist-upgrade",
        "upgrade",
    ],
)
@patch("packages_report.lib.apt.subprocess")
def test_run_apt_get_exception(mock_subprocess, action, caplog):
    """Test that run_apt_get() handles RC != 0 as expected."""
    expected = "apt-get {} returncode is '{}', expecting 0".format(action, 1)
    expected_log_records = [
        (
            "packages-report.lib.apt",
            10,
            "apt-get {} STDOUT: 'b'stdout''".format(action),
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get {} STDERR: 'b'stderr''".format(action),
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get {} RC: 1".format(action),
        ),
        (
            "packages-report.lib.apt",
            40,
            "apt-get {} STDERR: 'b'stderr''".format(action),
        ),
        (
            "packages-report.lib.apt",
            40,
            "apt-get {} RC: 1".format(action),
        ),
    ]

    mock_popen = Mock()
    mock_popen.communicate.return_value = (b"stdout", b"stderr")
    mock_popen.returncode = 1
    mock_subprocess.Popen.return_value.__enter__.return_value = mock_popen
    with caplog.at_level(logging.DEBUG, logger="packages-report.lib.apt"):
        with pytest.raises(ValueError) as exc_info:
            apt.run_apt_get(action)

    assert expected in str(exc_info.value)
    assert caplog.record_tuples == expected_log_records
    mock_subprocess.Popen.assert_called_once_with(
        ["/usr/bin/apt-get", "-s", action],
        stdout=ANY,
        stderr=ANY,
    )
    mock_popen.communicate.assert_called_once_with()


@patch("packages_report.lib.apt.subprocess")
def test_run_apt_get_update(mock_subprocess, caplog):
    """Test that run_apt_get_update() works as expected."""
    expected_log_records = [
        (
            "packages-report.lib.apt",
            10,
            "apt-get update STDOUT: 'b'stdout''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get update STDERR: 'b'stderr''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get update RC: 0",
        ),
    ]

    mock_popen = Mock()
    mock_popen.communicate.return_value = (b"stdout", b"stderr")
    mock_popen.returncode = 0
    mock_subprocess.Popen.return_value.__enter__.return_value = mock_popen
    with caplog.at_level(logging.DEBUG, logger="packages-report.lib.apt"):
        result = apt.run_apt_get_update()

    assert result is True
    assert caplog.record_tuples == expected_log_records
    mock_subprocess.Popen.assert_called_once_with(
        ["/usr/bin/apt-get", "update"],
        stdout=ANY,
        stderr=ANY,
    )
    mock_popen.communicate.assert_called_once_with()


@patch("packages_report.lib.apt.subprocess")
def test_run_apt_get_update_exception(mock_subprocess, caplog):
    """Test that run_apt_get_update() handles RC != 0 as expected."""
    expected_log_records = [
        (
            "packages-report.lib.apt",
            10,
            "apt-get update STDOUT: 'b'stdout''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get update STDERR: 'b'stderr''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "apt-get update RC: 1",
        ),
        (
            "packages-report.lib.apt",
            30,
            "apt-get update STDERR: 'b'stderr''",
        ),
        (
            "packages-report.lib.apt",
            30,
            "apt-get update RC: 1",
        ),
    ]

    mock_popen = Mock()
    mock_popen.communicate.return_value = (b"stdout", b"stderr")
    mock_popen.returncode = 1
    mock_subprocess.Popen.return_value.__enter__.return_value = mock_popen
    with caplog.at_level(logging.DEBUG, logger="packages-report.lib.apt"):
        result = apt.run_apt_get_update()

    assert result is False
    assert caplog.record_tuples == expected_log_records
    mock_subprocess.Popen.assert_called_once_with(
        ["/usr/bin/apt-get", "update"],
        stdout=ANY,
        stderr=ANY,
    )
    mock_popen.communicate.assert_called_once_with()


@patch("packages_report.lib.apt.subprocess")
def test_run_dpkg(mock_subprocess, caplog):
    """Test that run_dpkg() works as expected."""
    expected_log_records = [
        (
            "packages-report.lib.apt",
            10,
            "dpkg STDOUT: 'b'stdout''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "dpkg STDERR: 'b'stderr''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "dpkg RC: 0",
        ),
    ]

    mock_popen = Mock()
    mock_popen.communicate.return_value = (b"stdout", b"stderr")
    mock_popen.returncode = 0
    mock_subprocess.Popen.return_value.__enter__.return_value = mock_popen
    with caplog.at_level(logging.DEBUG, logger="packages-report.lib.apt"):
        result = apt.run_dpkg()

    assert result == "stdout"
    assert caplog.record_tuples == expected_log_records
    mock_subprocess.Popen.assert_called_once_with(
        ["/usr/bin/dpkg", "-l", "--no-pager"],
        stdout=ANY,
        stderr=ANY,
    )
    mock_popen.communicate.assert_called_once_with()


@patch("packages_report.lib.apt.subprocess")
def test_run_dpkg_exception(mock_subprocess, caplog):
    """Test that run_dpkg() raises exception when RC != 0."""
    expected = "dpkg returncode is '{}', expecting 0".format(1)
    expected_log_records = [
        (
            "packages-report.lib.apt",
            10,
            "dpkg STDOUT: 'b'stdout''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "dpkg STDERR: 'b'stderr''",
        ),
        (
            "packages-report.lib.apt",
            10,
            "dpkg RC: 1",
        ),
        (
            "packages-report.lib.apt",
            40,
            "dpkg STDERR: 'stderr'",
        ),
        (
            "packages-report.lib.apt",
            40,
            "dpkg RC: 1",
        ),
    ]

    mock_popen = Mock()
    mock_popen.communicate.return_value = (b"stdout", b"stderr")
    mock_popen.returncode = 1
    mock_subprocess.Popen.return_value.__enter__.return_value = mock_popen
    with caplog.at_level(logging.DEBUG, logger="packages-report.lib.apt"):
        with pytest.raises(ValueError) as exc_info:
            apt.run_dpkg()

    assert expected in str(exc_info.value)
    assert caplog.record_tuples == expected_log_records
    mock_subprocess.Popen.assert_called_once_with(
        ["/usr/bin/dpkg", "-l", "--no-pager"],
        stdout=ANY,
        stderr=ANY,
    )
    mock_popen.communicate.assert_called_once_with()
