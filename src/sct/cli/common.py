# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI common.
-----------
"""

import functools
import time
from pathlib import Path

import art
import click

from sct.configuration.logger import SCTFileHandler, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration

# creating a decorator to pass a SCTConfiguration dataclass object between commands
share_config = click.make_pass_decorator(SCTConfiguration)

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
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
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


def add_logging_file(log_file: Path) -> SCTFileHandler:
    """Add a file handler to sct logger"""
    file_handler = SCTFileHandler(filename=log_file)
    sct_logger.addHandler(file_handler)
    return file_handler


def display_title(title: str) -> None:
    """Display a title in the CLI."""
    click.echo("\n")
    txt = art.text2art(title, font="doom")
    assert isinstance(txt, str)
    click.echo(txt + "\n")


def log_elapsed_time(logged_name: str):
    """Decorate function to log elapsed time with the given name."""

    def decorator(func):
        @functools.wraps(func)
        def decorated_func(*args, **kwargs):
            start_time = time.perf_counter()
            outputs = func(*args, **kwargs)
            stop_time = time.perf_counter()
            elapsed_time = stop_time - start_time
            sct_logger.info(f"{logged_name} completed in {elapsed_time:.2f} s")
            return outputs

        return decorated_func

    return decorator
