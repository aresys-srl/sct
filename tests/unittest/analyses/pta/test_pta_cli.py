# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Point Target Analysis CLI"""

from typer.testing import CliRunner

from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig
from sct.cli.cli import app

cli_runner = CliRunner()
command = "point_target"
test_configuration = SCTPointTargetAnalysisConfig()


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
    point_target = tmp_path / "point_target"
    point_target.touch()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"

    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} -p {input_product} -pt {point_target} -out {output_dir}".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1


def test_invalid_product_graph(tmp_path):
    """Error on invalid product"""
    input_product = tmp_path / "input_product"
    input_product.mkdir()
    point_target = tmp_path / "point_target"
    point_target.touch()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conf_file = tmp_path / "conf.toml"

    test_configuration.to_toml(conf_file)
    command_args = f"--config {conf_file} {command} -p {input_product} -pt {point_target} -out {output_dir} -g".split()
    result = cli_runner.invoke(app, command_args)
    assert result.exit_code == 1
