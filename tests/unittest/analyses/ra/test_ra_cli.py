# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Radiometric Analysis CLI"""

import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Generator

from typer.testing import CliRunner

from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig
from sct.cli.cli import app


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
        self.command = "radiometry"
        self.test_configuration = SCTRadiometricAnalysisConfig()

    def test_help_on_no_args(self):
        """Display help when no arguments are provided"""
        result = self.cli_runner.invoke(app, ["--debug", self.command])
        self.assertEqual(result.exit_code, 2)

    def test_display_help(self):
        """Display help"""
        result = self.cli_runner.invoke(app, [self.command, "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_help_elevation_profile(self):
        """Display help elevation profile"""
        result = self.cli_runner.invoke(app, [self.command, "elevation-profiles", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_help_rain_forest(self):
        """Display help rain forest profile"""
        result = self.cli_runner.invoke(app, [self.command, "rain-forest", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_help_nesz(self):
        """Display help nesz"""
        result = self.cli_runner.invoke(app, [self.command, "nesz", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_help_scalloping(self):
        """Display help scalloping"""
        result = self.cli_runner.invoke(app, [self.command, "scalloping", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_elevation_profile_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = (
                f"--config {conf_file} {self.command} elevation-profiles -p {product} -out {output_dir} -r gamma"
            ).split()
            result = self.cli_runner.invoke(
                app,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_rain_forest_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} rain-forest -p {product} -out {output_dir}".split()
            result = self.cli_runner.invoke(
                app,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_nesz_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} nesz -p {product} -out {output_dir}".split()
            result = self.cli_runner.invoke(
                app,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_scalloping_invalid_product(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} scalloping -p {product} -out {output_dir}".split()
            result = self.cli_runner.invoke(
                app,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_elevation_profile_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = (
                f"--config {conf_file} {self.command} elevation-profiles -p {product}"
                + f" -out {output_dir} "
                + "-r gamma -g"
            )
            result = self.cli_runner.invoke(
                app,
                command_args.split(),
            )
            self.assertEqual(result.exit_code, 1)

    def test_rain_forest_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} rain-forest -p {product} -out {output_dir} -g".split()
            result = self.cli_runner.invoke(
                app,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_nesz_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} nesz -p {product} -out {output_dir} -g".split()
            result = self.cli_runner.invoke(
                app,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_scalloping_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} scalloping -p {product} -out {output_dir} -g".split()
            result = self.cli_runner.invoke(
                app,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)


if __name__ == "__main__":
    unittest.main()
