# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Radiometric analysis CLI unittest
-------------------------------------
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
def TemporaryDirectoriesAndConfFile() -> Generator[tuple[Path, Path, Path], Any, None]:
    """Create empty existing dirs and an empty conf.toml file"""
    with (
        TemporaryDirectory() as input_product,
        TemporaryDirectory() as output_dir,
        TemporaryDirectory() as conf_dir,
    ):
        conf_file = Path(conf_dir).joinpath("conf.toml")
        yield Path(input_product), Path(output_dir), Path(conf_file)


class RadiometricAnalysisCLITestCase(unittest.TestCase):
    """Test command line interface"""

    def setUp(self) -> None:
        self.cli_runner = CliRunner()
        self.command = "radiometric-analysis"
        self.test_configuration = SCTConfiguration(general=DefaultConfiguration(save_log=False))

    def test_help_on_no_args(self):
        """Display help when no arguments are provided"""
        result = self.cli_runner.invoke(sct_analysis, [self.command])
        self.assertEqual(result.exit_code, 0)

    def test_display_help(self):
        """Display help"""
        result = self.cli_runner.invoke(sct_analysis, [self.command, "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_help_elevation_profile(self):
        """Display help elevation profile"""
        result = self.cli_runner.invoke(sct_analysis, [self.command, "elevation_profile", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_help_nesz(self):
        """Display help nesz"""
        result = self.cli_runner.invoke(sct_analysis, [self.command, "nesz", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_help_scalloping(self):
        """Display help scalloping"""
        result = self.cli_runner.invoke(sct_analysis, [self.command, "scalloping", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_elevation_profile_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = (
                f"--config {conf_file} {self.command} elevation_profile -p {product} -out {output_dir} -r gamma".split()
            )
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_nesz_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} nesz -p {product} -out {output_dir}".split()
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_scalloping_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} scalloping -p {product} -out {output_dir}".split()
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_elevation_profile_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} elevation_profile -p {product} -out {output_dir} -r gamma -g".split()
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_nesz_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} nesz -p {product} -out {output_dir} -g".split()
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_scalloping_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.dump_to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} scalloping -p {product} -out {output_dir} -g".split()
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)


if __name__ == "__main__":
    unittest.main()
