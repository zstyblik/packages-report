#!/usr/bin/env python3
"""Data models for packages-report.

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
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import List


@dataclass
class PackageReport:
    """Class represents report on Linux packages."""

    datetime: str
    hostname: str
    report_type: str
    service: str
    payload: set = field(default_factory=set)
    version: int = 1


@dataclass(frozen=True)
class PackageMetadata:
    """Class represents package and related information."""

    state: str
    name: str
    version: str
    arch: str

    @staticmethod
    def fmt_text_header(col_widths: Dict[str, int]) -> str:
        """Return formatted table header."""
        return "| {:s} | {:s} | {:s} |".format(
            "Name".ljust(col_widths["name"]),
            "Version".ljust(col_widths["version"]),
            "Arch".ljust(col_widths["arch"]),
        )

    @staticmethod
    def fmt_text_header_separator(col_widths: Dict[str, int]) -> str:
        """Return formatted table header separator."""
        return "|{:s}|{:s}|{:s}|".format(
            "".ljust(col_widths["name"] + 2, "-"),
            "".ljust(col_widths["version"] + 2, "-"),
            "".ljust(col_widths["arch"] + 2, "-"),
        )

    def fmt_text_table_row(self, col_widths: Dict[str, int]):
        """Return formatted table row with package metadata info."""
        return "| {:s} | {:s} | {:s} |".format(
            self.name.ljust(col_widths["name"]),
            self.version.ljust(col_widths["version"]),
            self.arch.ljust(col_widths["arch"]),
        )

    def get_col_widths(self) -> Dict[str, int]:
        """Return column widths of each attribute as key-value."""
        return {
            "state": len(self.state),
            "name": len(self.name),
            "version": len(self.version),
            "arch": len(self.arch),
        }

    @staticmethod
    def get_header_col_names() -> List[str]:
        """Return names of header cols."""
        return [
            "Name",
            "Version",
            "Arch",
        ]


@dataclass(frozen=True)
class PackageUpgrade:
    """Class represents available upgrade and related information."""

    name: str
    version: str
    origin: str
    arch: str

    @staticmethod
    def fmt_text_header(col_widths: Dict[str, int]) -> str:
        """Return formatted table header."""
        return "| {:s} | {:s} | {:s} | {:s} |".format(
            "Name".ljust(col_widths["name"]),
            "Version".ljust(col_widths["version"]),
            "Arch".ljust(col_widths["arch"]),
            "Origin".ljust(col_widths["origin"]),
        )

    @staticmethod
    def fmt_text_header_separator(col_widths: Dict[str, int]) -> str:
        """Return formatted table header separator."""
        return "|{:s}|{:s}|{:s}|{:s}|".format(
            "".ljust(col_widths["name"] + 2, "-"),
            "".ljust(col_widths["version"] + 2, "-"),
            "".ljust(col_widths["arch"] + 2, "-"),
            "".ljust(col_widths["origin"] + 2, "-"),
        )

    def fmt_text_table_row(self, col_widths: Dict[str, int]):
        """Return formatted table row with package metadata info."""
        return "| {:s} | {:s} | {:s} | {:s} |".format(
            self.name.ljust(col_widths["name"]),
            self.version.ljust(col_widths["version"]),
            self.arch.ljust(col_widths["arch"]),
            self.origin.ljust(col_widths["origin"]),
        )

    def get_col_widths(self) -> Dict[str, int]:
        """Return column widths of each attribute as key-value."""
        return {
            "name": len(self.name),
            "version": len(self.version),
            "arch": len(self.arch),
            "origin": len(self.origin),
        }

    @staticmethod
    def get_header_col_names() -> List[str]:
        """Return names of header cols."""
        return [
            "Name",
            "Version",
            "Arch",
            "Origin",
        ]
