# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Interferometric Analysis CLI"""

from typer.testing import CliRunner

from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig
from sct.cli.cli import app

cli_runner = CliRunner()
command = "interferometry"
test_configuration = SCTInterferometricAnalysisConfig()


def test_error_no_args():
    """Error when no arguments are provided"""
    result = cli_runner.invoke(app, [command])
    assert result.exit_code == 2


def test_display_help():
    """Display help"""
    result = cli_runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0


def test_invalid_product(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    second_product = tmp_path / "second_product"
    second_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"

    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} -p {input_product} -out {output_dir}".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_invalid_product_1(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    second_product = tmp_path / "second_product"
    second_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"

    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} -p {input_product} -pp {second_product} -out {output_dir}".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_invalid_product_graph(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    second_product = tmp_path / "second_product"
    second_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"

    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} -p {input_product} -out {output_dir} -g".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1
