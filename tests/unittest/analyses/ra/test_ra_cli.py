# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Radiometric Analysis CLI"""

from typer.testing import CliRunner

from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig
from sct.cli.cli import app

cli_runner = CliRunner()
command = "radiometry"
test_configuration = SCTRadiometricAnalysisConfig()


def test_help_on_no_args():
    """Display help when no arguments are provided"""
    result = cli_runner.invoke(app, ["--debug", command])
    assert result.exit_code == 2


def test_display_help():
    """Display help"""
    result = cli_runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0


def test_display_help_elevation_profile():
    """Display help elevation profile"""
    result = cli_runner.invoke(app, [command, "elevation-profiles", "--help"])
    assert result.exit_code == 0


def test_display_help_rain_forest():
    """Display help rain forest profile"""
    result = cli_runner.invoke(app, [command, "rain-forest", "--help"])
    assert result.exit_code == 0


def test_display_help_nesz():
    """Display help nesz"""
    result = cli_runner.invoke(app, [command, "nesz", "--help"])
    assert result.exit_code == 0


def test_display_help_scalloping():
    """Display help scalloping"""
    result = cli_runner.invoke(app, [command, "scalloping", "--help"])
    assert result.exit_code == 0


def test_elevation_profile_invalid_product(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = (
        f"--config {conf_file} {command} elevation-profiles -p {input_product} -out {output_dir} -r gamma"
    ).split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_rain_forest_invalid_product(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} rain-forest -p {input_product} -out {output_dir}".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_nesz_invalid_product(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} nesz -p {input_product} -out {output_dir}".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_scalloping_invalid_product(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} scalloping -p {input_product} -out {output_dir}".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_elevation_profile_invalid_product_graph(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = (
        f"--config {conf_file} {command} elevation-profiles -p {input_product}" + f" -out {output_dir} " + "-r gamma -g"
    )
    result = cli_runner.invoke(app, command_args.split())
    assert result.exit_code == 1


def test_rain_forest_invalid_product_graph(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} rain-forest -p {input_product} -out {output_dir} -g".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_nesz_invalid_product_graph(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} nesz -p {input_product} -out {output_dir} -g".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_scalloping_invalid_product_graph(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"
    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} scalloping -p {input_product} -out {output_dir} -g".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1
