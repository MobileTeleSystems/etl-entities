#  Copyright 2023 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import logging
import sys

etl_entities_log = logging.getLogger("etl_entities")
root_log = logging.getLogger()

HALF_SCREEN_SIZE = 45
BASE_LOG_INDENT = 8
LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(threadName)s: %(message)s"
CLIENT_MODULES = {"hdfs", "paramiko", "ftputil", "minio", "webdav3", "pyspark"}

DISABLED = 9999  # CRITICAL is 50, we need even higher to disable all logs
logging.addLevelName(DISABLED, "DISABLED")

NOTICE = 5  # DEBUG is 10, we need lower value for less verbose logs even on debug level
logging.addLevelName(NOTICE, "NOTICE")


def log_with_indent(
    logger: logging.Logger,
    inp: str,
    *args,
    indent: int = 0,
    level: int = logging.INFO,
    stacklevel: int = 1,
    **kwargs,
) -> None:
    """Log a message with indentation.

    Supports all positional and keyword arguments which ``logging.log`` support.

    Example
    -------

    .. code:: python

        log_with_indent(logger, "message")
        log_with_indent(
            logger,
            "message with additional %s",
            "indent",
            indent=4,
            level=logging.DEBUG,
        )

    .. code-block:: text

        INFO  onetl.module        message
        DEBUG onetl.module            message with additional indent

    """
    _log(logger, "%s" + inp, " " * (BASE_LOG_INDENT + indent), *args, level=level, stacklevel=stacklevel + 1, **kwargs)


def _log(logger: logging.Logger, msg: str, *args, level: int = logging.INFO, stacklevel: int = 1, **kwargs) -> None:
    if sys.version_info >= (3, 8):
        # https://github.com/python/cpython/pull/7424
        logger.log(level, msg, *args, stacklevel=stacklevel + 1, **kwargs)  # noqa: WPS204
    else:
        logger.log(level, msg, *args, **kwargs)
