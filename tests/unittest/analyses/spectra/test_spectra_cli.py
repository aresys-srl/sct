# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Spectral Analysis CLI"""

import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any, Generator

from click.testing import CliRunner

from sct.analyses.spectra.config import SCTSpectralAnalysisConfig
from sct.cli.cli import sct_analysis


@contextmanager
def TemporaryDirectoriesAndConfFile() -> Generator[tuple[Path, Path, Path, Path], Any, None]:
    """Create empty existing dirs and an empty conf.toml file"""
    with (
        TemporaryDirectory() as input_product,
        NamedTemporaryFile() as point_targets,
        TemporaryDirectory() as output_dir,
        TemporaryDirectory() as conf_dir,
    ):
        conf_file = Path(conf_dir).joinpath("conf.toml")
        yield Path(input_product), Path(point_targets.name), Path(output_dir), Path(conf_file)


class SpectralAnalysisCLITestCase(unittest.TestCase):
    """Test spectral analysis command line interface"""

    def setUp(self) -> None:
        self.cli_runner = CliRunner()
        self.command = "spectral-analysis"
        self.test_configuration = SCTSpectralAnalysisConfig()

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
        with TemporaryDirectoriesAndConfFile() as (product, point_targets, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} -p {product} -out {output_dir}".split()
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_invalid_product_1(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, point_targets, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = (
                f"--config {conf_file} {self.command} -p {product} -pt {point_targets} -out {output_dir}".split()
            )
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)

    def test_invalid_product_graph(self):
        """Error on invalid product"""
        with TemporaryDirectoriesAndConfFile() as (product, point_targets, output_dir, conf_file):
            self.test_configuration.to_toml(conf_file)
            command_args = f"--config {conf_file} {self.command} -p {product} -out {output_dir} -g".split()
            result = self.cli_runner.invoke(
                sct_analysis,
                command_args,
            )
            self.assertEqual(result.exit_code, 1)


if __name__ == "__main__":
    unittest.main()
