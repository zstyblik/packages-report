#!/usr/bin/env python3
"""Formatters for packages-report.

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
import dataclasses
import json
import logging
from typing import Any
from typing import Dict
from typing import IO
from typing import Set

from .config import SERVICE
from .models import PackageMetadata
from .models import PackageReport
from .models import PackageUpgrade


module_logger = logging.getLogger("{:s}.lib.formatters".format(SERVICE))


class ReportJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder in order to serialize Reports's data."""

    def default(self, o: Any) -> Any:
        """Return a serializable object for `o` or call base implementation."""
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        if isinstance(o, set):
            return list(o)

        return super().default(o)


def determine_col_widths(
    heading_cls: PackageMetadata | PackageUpgrade,
    packages: Set[PackageMetadata | PackageUpgrade],
) -> Dict[str, int]:
    """Determine maximum widths of columns for text formatting."""
    # NOTE(zstyblik): Use heading cols as a baseline.
    col_widths = {
        col_name.lower(): len(col_name)
        for col_name in heading_cls.get_header_col_names()
    }
    for pkg in packages:
        widths = pkg.get_col_widths()
        for col_name in col_widths:
            col_width = widths.get(col_name, 0)
            col_widths[col_name] = max(
                col_widths[col_name],
                col_width,
            )

    return col_widths


def fmt_json(
    package_report: PackageReport,
    output_dest: IO,
) -> None:
    """Format packages report as JSON and write it into output destination."""
    # NOTE(zstyblik): no JSON-pretty output, because:
    # 1. it was 1km long for installed packages
    # 2. machine is expected on the other side
    # 3. there is jq/python/... you can pretty-format, if needed
    json.dump(
        package_report,
        output_dest,
        sort_keys=True,
        cls=ReportJSONEncoder,
    )


def fmt_text(
    package_report: PackageReport,
    heading_cls: PackageMetadata | PackageUpgrade,
    output_dest: IO,
) -> None:
    """Format packages report as a text and write it into output destination."""
    # Header
    print("# Packages report", file=output_dest)
    print("", file=output_dest)
    print("Date: {:s}".format(package_report.datetime), file=output_dest)
    print(
        "Hostname: {:s}".format(package_report.hostname),
        file=output_dest,
    )
    print(
        "Report type: {:s}".format(package_report.report_type),
        file=output_dest,
    )
    print("", file=output_dest)
    # Body - table with a list of packages
    print("## Packages", file=output_dest)
    print("", file=output_dest)

    col_widths = determine_col_widths(heading_cls, package_report.payload)
    module_logger.debug("Column widths: %s", col_widths)
    header = heading_cls.fmt_text_header(col_widths)
    print(header, file=output_dest)
    header_sep = heading_cls.fmt_text_header_separator(col_widths)
    print(header_sep, file=output_dest)
    for pkg in sorted(package_report.payload, key=lambda x: x.name):
        print(
            "{:s}".format(pkg.fmt_text_table_row(col_widths)),
            file=output_dest,
        )
    # Footer
    print("", file=output_dest)
    print("-- End of packages report", file=output_dest)
