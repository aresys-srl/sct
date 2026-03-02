# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI common functions
--------------------
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Callable

import art
import click

from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import enable_quality_logger, sct_logger

# creating a decorator to pass a GeneralConfiguration dataclass object between commands
share_config = click.make_pass_decorator(GeneralConfiguration)

input_product_option = click.option(
    "--product",
    "-p",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the product to be analyzed",
)

input_point_target_option = click.option(
    "--point-target-source",
    "-pt",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help="Path to the external point target source",
)

output_directory_option = click.option(
    "--output_directory",
    "-out",
    required=True,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the folder where to save output data",
)

generate_graph_option = click.option(
    "--graphs",
    "-g",
    default=False,
    is_flag=True,
    type=bool,
    help="Flag to generate graphical output at the end of the analysis",
)


@contextmanager
def logging_to_file(path: Path | None):
    """Context manager to safely add a file handler to sct logger.

    Parameters
    ----------
    path : Path | None
        path to log file to be used, if None, no file handler is added
    """

    if path is None:
        yield
        return

    handler = logging.FileHandler(path)

    # Get both loggers
    sct_log = logging.getLogger("sct")
    quality_log = logging.getLogger("perseo-quality")

    # Attach
    sct_log.addHandler(handler)
    enable_quality_logger(handler)

    try:
        yield

    finally:
        # Remove from both loggers
        for logger in (sct_log, quality_log):
            if handler in logger.handlers:
                logger.removeHandler(handler)

        handler.flush()
        handler.close()


def display_title(title: str) -> None:
    """Display a title in the CLI."""
    click.echo("\n")
    txt = art.text2art(title, font="doom")
    assert isinstance(txt, str)
    click.echo(txt + "\n")


def log_elapsed_time(logged_name: str):
    """Decorate function to log elapsed time with the given name."""

    def decorator(func: Callable):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            start_time = time.perf_counter()
            outputs = func(*args, **kwargs)
            stop_time = time.perf_counter()
            elapsed_time = stop_time - start_time
            if elapsed_time < 60:
                sct_logger.info(f"{logged_name} completed in {round(elapsed_time)} s")
            else:
                minutes, seconds = divmod(int(elapsed_time), 60)
                sct_logger.info(f"{logged_name} completed in {minutes} min {seconds} s")
            return outputs

        return decorated_func

    return decorator


def graceful_exit(name: str):
    """Decorate function to gracefully log and exit in case of errors."""

    # TODO: check this part
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract config & output_directory if present
            analysis_config = kwargs.get("config", None)
            dump_config = kwargs.get("dump_config", False)
            output_directory: Path | None = kwargs.get("output_directory", None)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                sct_logger.critical(f"{name} failed")
                sct_logger.critical(e)
                sys.exit(1)
            finally:
                # Save config copy if applicable
                if output_directory is not None:
                    if dump_config:
                        analysis_config.to_toml(
                            out_file=output_directory.joinpath("analysis_config.toml"),
                        )

        return wrapper

    return decorator
