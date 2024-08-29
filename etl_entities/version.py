# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

VERSION_FILE = Path(__file__).parent / "VERSION"

__version__ = VERSION_FILE.read_text().strip()  # noqa: WPS410
