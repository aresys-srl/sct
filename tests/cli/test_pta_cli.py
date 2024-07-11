# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT PTA CLI unittest
--------------------
"""

import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Generator

from click.testing import CliRunner

from sct.cli.sct_cli import sct_analysis
from sct.configuration.sct_configuration import DefaultConfiguration, SCTConfiguration


@contextmanager
def TemporaryDirectoriesAndConfFile() -> Generator[tuple[Path, Path, Path, Path], Any, None]:
    """Create empty existing dirs and an empty conf.toml file"""
    with (
        TemporaryDirectory() as input_product,
        TemporaryDirectory() as point_target_product,
        TemporaryDirectory() as output_dir,
        TemporaryDirectory() as conf_dir,
    ):
        conf_file = Path(conf_dir).joinpath("conf.toml")
        yield Path(input_product), Path(point_target_product), Path(output_dir), Path(conf_file)


class PointTargetAnalysisCLITestCase(unittest.TestCase):
    """Test point target analysis command line interface"""

    def setUp(self) -> None:
        self.cli_runner = CliRunner()
        self.command = "target-analysis"
        self.test_configuration = SCTConfiguration(general=DefaultConfiguration(save_log=False))

    def test_error_no_args(self):
        """Error when no arguments are provided"""
        result = self.cli_runner.invoke(sct_analysis, [self.command])
        self.assertEqual(result.exit_code, 2)

    def test_display_help(self):
        """Display help"""
        result = self.cli_runner.invoke(sct_analysis, [self.command, "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, point_target, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = (
                f"--config {conf_file} {self.command} -p {product} -pt {point_target} -out {output_dir}".split()
            )
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, point_target, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = (
                f"--config {conf_file} {self.command} -p {product} -pt {point_target} -out {output_dir} -g".split()
            )
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)


if __name__ == "__main__":
    unittest.main()
