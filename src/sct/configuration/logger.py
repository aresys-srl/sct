# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Logger"""

import logging
import sys
from enum import Enum
from pathlib import Path


# This function was inspired by the answers to Stack Overflow post
# http://stackoverflow.com/q/2183233/2988730, especially
# http://stackoverflow.com/a/13638084/2988730
def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `level_name` becomes an attribute of the `logging` module with the value
    `levelNum`. `method_name` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `method_name` is not specified, `level_name.lower()` is
    used.

    To avoid accidental clobbering of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel("TRACE", logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace("that worked")
    >>> logging.trace("so did this")
    >>> logging.TRACE
    5

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError(f"{level_name} already defined in logging module")
    if hasattr(logging, method_name):
        raise AttributeError(f"{method_name} already defined in logging module")
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError(f"{method_name} already defined in logger class")

    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


sct_logger = logging.getLogger("sct-log")
add_logging_level(level_name="FAIL", level_num=21)
add_logging_level(level_name="SUCCESS", level_num=22)


class AnsiColors(Enum):
    """Ansi escape color strings for Logging Formatter"""

    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    HIGHLIGHT_YELLOW = "\033[48;5;226m"
    GREEN = "\x1b[1;32m"
    HIGHLIGHT_GREEN = "\033[48;5;40m"
    RED = "\x1b[31;20m"
    HIGHLIGHT_RED = "\033[48;5;196m"
    BOLD_RED = "\x1b[31;1m"
    PURPLE = "\x1b[1;35m"
    BLUE = "\x1b[1;34m"
    LIGHT_BLUE = "\x1b[1;36m"
    BOLD = "\x1b[1m"
    UNDERLINE = "\x1b[4m"
    RESET = "\x1b[0m"


class ConsoleFormatter(logging.Formatter):
    """Custom logger formatter with colors"""

    # message formatting layout
    fmt = "| %(levelname)-9s @ %(module)s| %(asctime)s | %(message)s"

    FORMATS = {
        logging.DEBUG: AnsiColors.GREY.value + fmt + AnsiColors.RESET.value,
        logging.INFO: AnsiColors.GREY.value + fmt + AnsiColors.RESET.value,
        logging.WARNING: AnsiColors.YELLOW.value + fmt + AnsiColors.RESET.value,
        logging.ERROR: AnsiColors.RED.value + fmt + AnsiColors.RESET.value,
        logging.CRITICAL: AnsiColors.BOLD_RED.value + fmt + AnsiColors.RESET.value,
        logging.FAIL: AnsiColors.BOLD.value + AnsiColors.HIGHLIGHT_RED.value + fmt + AnsiColors.RESET.value,
        logging.SUCCESS: AnsiColors.BOLD.value + AnsiColors.HIGHLIGHT_GREEN.value + fmt + AnsiColors.RESET.value,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)


class FileFormatter(logging.Formatter):
    """Custom logger formatter with colors"""

    # message formatting layout
    fmt = "| %(levelname)-9s @ %(module)s| %(asctime)s | %(message)s"

    FORMATS = {
        logging.DEBUG: fmt,
        logging.INFO: fmt,
        logging.WARNING: fmt,
        logging.ERROR: fmt,
        logging.CRITICAL: fmt,
        logging.FAIL: fmt,
        logging.SUCCESS: fmt,
    }

    def __init__(self):
        super().__init__()
        self._fmt = self.fmt

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)


class ConsoleHandler(logging.StreamHandler):
    """Custom logging stream handler to centralize logging"""

    def __init__(self):
        super().__init__(stream=sys.stdout)
        self.setFormatter(ConsoleFormatter())


class SCTFileHandler(logging.FileHandler):
    """Custom logging file handler to centralize logging"""

    def __init__(self, filename: Path):
        """File handler to write log to disk.

        Parameters
        ----------
        filename : Path
            log filename
        """
        super().__init__(filename=filename)
        self.setFormatter(FileFormatter())


def enable_quality_logger(file_handler: logging.Handler | None = None):
    """Enabling quality logger with the same handler of the sct common logger.

    Parameters
    ----------
    file_handler : logging.FileHandler | None, optional
        if provided, a file handler is added to the logger, by default None
    """
    log = logging.getLogger("perseo-quality")
    log.setLevel("INFO")

    # Avoid adding duplicate console handlers
    if not any(isinstance(h, ConsoleHandler) for h in log.handlers):
        log.addHandler(ConsoleHandler())

    if file_handler is not None:
        log.addHandler(file_handler)


sct_logger.addHandler(logging.NullHandler())
sct_logger.setLevel(logging.DEBUG)
