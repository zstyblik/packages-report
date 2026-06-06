#!/usr/bin/env python3
"""Debian's APT support for packages-report.

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
import re
import subprocess
from typing import Set

from .config import SERVICE
from .models import PackageMetadata
from .models import PackageUpgrade

module_logger = logging.getLogger("{:s}.lib.apt".format(SERVICE))


def get_installed_packages() -> Set[PackageMetadata]:
    """Return installed packages as a set."""
    raw_pkgs = run_dpkg()
    pkgs = parse_package_list(raw_pkgs)
    return pkgs


def get_package_upgrades() -> Set[PackageUpgrade]:
    """Return package upgrades as a set."""
    _ = run_apt_get_update()
    raw_upgrades = run_apt_get("upgrade")
    pkg_upgrades = parse_package_upgrades(raw_upgrades)

    raw_upgrades = run_apt_get("dist-upgrade")
    dist_upgrades = parse_package_upgrades(raw_upgrades)
    pkg_upgrades.update(dist_upgrades)

    return pkg_upgrades


def parse_dpkg_line(line: str) -> PackageMetadata:
    """Parse line from dpkg output and return instance of PackageMetadata."""
    name, version, arch = line.split()[1:4]
    # Remove architecture eg. ':amd64' from the package name.
    if ":" in name:
        name = name.split(":")[0]

    package = PackageMetadata(
        state="ii",
        name=name,
        version=version,
        arch=arch,
    )
    return package


def parse_package_list(stdout: str) -> Set[PackageMetadata]:
    """Parse output from % dpkg -l; and return installed packages."""
    re_pkg_installed = re.compile(r"^ii[ \t]+")
    packages = set()
    for line in stdout.splitlines():
        if not re_pkg_installed.search(line):
            continue

        package = parse_dpkg_line(line)
        packages.add(package)

    return packages


def parse_package_upgrade(line: str) -> PackageUpgrade:
    """Parse Conf line and return instance of PackageUpgrade."""
    re_brackets = re.compile(r"[\[\]\(\)]")
    name, details = line.split(" ", 2)[1:3]
    splitted = details.split()
    version = splitted[0][1:]
    origin = " ".join(splitted[1:-1])
    arch = re_brackets.sub("", splitted[-1])
    return PackageUpgrade(
        name=name,
        version=version,
        origin=origin,
        arch=arch,
    )


def parse_package_upgrades(stdout: str) -> Set[PackageUpgrade]:
    """Parse apt-get's output and return packages to upgrade."""
    upgrades = set()
    re_conf = re.compile(r"^Conf[ \t]+")
    for line in stdout.splitlines():
        match = re_conf.search(line)
        if not match:
            continue

        pkg_upgrade = parse_package_upgrade(line)
        upgrades.add(pkg_upgrade)

    return upgrades


def run_apt_get(apt_action: str) -> str:
    """Run apt-get with given action and return its STDOUT.

    :raises ValueError: when unsupported action is given
    :raises ValueError: raised when returncode != 0
    """
    if apt_action not in ["upgrade", "dist-upgrade"]:
        raise ValueError(
            "atp-get action '{}' is not supported".format(apt_action)
        )

    proc_args = ["/usr/bin/apt-get", "-s", apt_action]
    with subprocess.Popen(
        proc_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        (stdout, stderr) = proc.communicate()
        module_logger.debug("apt-get %s STDOUT: '%s'", apt_action, stdout)
        module_logger.debug("apt-get %s STDERR: '%s'", apt_action, stderr)
        module_logger.debug("apt-get %s RC: %s", apt_action, proc.returncode)
        if proc.returncode != 0:
            module_logger.error("apt-get %s STDERR: '%s'", apt_action, stderr)
            module_logger.error(
                "apt-get %s RC: %s", apt_action, proc.returncode
            )
            raise ValueError(
                "apt-get {:s} returncode is '{}', expecting 0".format(
                    apt_action, proc.returncode
                )
            )

        return stdout.decode("utf-8")


def run_apt_get_update() -> bool:
    """Run % apt-get update; and return T/F depending on retcode.

    Logs a WARNING and returns False when RC > 0. RC > 0 can be caused by eg.
    lock or lack of privileges.
    RC = 100 seems to be used for any error, therefore output would have to be
    parsed in order to know what exactly happened.
    """
    proc_args = ["/usr/bin/apt-get", "update"]
    with subprocess.Popen(
        proc_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        stdout, stderr = proc.communicate()
        module_logger.debug("apt-get update STDOUT: '%s'", stdout)
        module_logger.debug("apt-get update STDERR: '%s'", stderr)
        module_logger.debug("apt-get update RC: %s", proc.returncode)
        if proc.returncode != 0:
            module_logger.warning("apt-get update STDERR: '%s'", stderr)
            module_logger.warning("apt-get update RC: %s", proc.returncode)
            return False

        return True


def run_dpkg() -> str:
    """Run % dpkg -l; and return its STDOUT.

    :raises ValueError: raised when returncode != 0
    """
    proc_args = ["/usr/bin/dpkg", "-l", "--no-pager"]
    with subprocess.Popen(
        proc_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        (stdout, stderr) = proc.communicate()
        module_logger.debug("dpkg STDOUT: '%s'", stdout)
        module_logger.debug("dpkg STDERR: '%s'", stderr)
        module_logger.debug("dpkg RC: %s", proc.returncode)
        if proc.returncode != 0:
            module_logger.error("dpkg STDERR: '%s'", stderr.decode("utf-8"))
            module_logger.error("dpkg RC: %s", proc.returncode)
            raise ValueError(
                "dpkg returncode is '{}', expecting 0".format(proc.returncode)
            )

        return stdout.decode("utf-8")
