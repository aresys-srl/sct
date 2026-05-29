# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Auxiliary Utilities Command Line Interface unit tests"""

from pathlib import Path

from typer.testing import CliRunner

from sct.cli.utilities import utilities_app

cli_runner = CliRunner()


def test_download_vmf3(tmp_path):
    """Download vmf3 files"""
    command = ["tropo-downloader", "-d", "2024-04-20 10:00:00"]
    out_dir = tmp_path
    command.extend(f"-r COARSE -out {out_dir}".split())
    result = cli_runner.invoke(utilities_app, command)
    assert result.exit_code == 0

    files = [Path(line) for line in result.stdout.splitlines() if "VMF3_" in line]
    assert len(files) == 4
    assert files[0].exists()
    assert files[1].exists()
    assert files[2].exists()
    assert files[3].exists()


def test_download_ionex_error_non_existing_email(tmp_path):
    """Error on server side on non existing email"""
    command = ["iono-downloader", "-d", "2024-04-20 10:00:00"]
    out_dir = tmp_path
    command.extend(f"-c JPL -e name@domain.it -out {out_dir}".split())
    result = cli_runner.invoke(utilities_app, command)
    assert result.exit_code == 1


def test_rosamond_converter(tmp_path):
    rosamond_out_1 = """"Corner ID","Latitude (deg)","Longitude (deg)","Height Above Ellipsoid (m)","""
    rosamond_out_2 = """"Azimuth (deg)","Tilt / Elevation angle (deg)","Side Length (m)","""
    rosamond_out = """" "Epoch: 2024-05-24 00:00"
    00,34.79696931,-118.09653087,660.7853,170.50,12.10,2.4384
    01,34.79984857,-118.08698886,661.0342,170.50,8.72,2.4384
    02,34.80523758,-118.08738926,660.7955,170.00,9.30,2.4384"""
    input_csv = tmp_path.joinpath("rosamond.csv")
    input_csv.write_text(rosamond_out_1 + rosamond_out_2 + rosamond_out)
    command = f"rosamond-pt-converter -s {input_csv} -d".split() + ["2024-05-24 00:00:00"]
    result = cli_runner.invoke(utilities_app, command)
    assert result.exit_code == 0
    assert tmp_path.joinpath("rosamond_point_target.csv")
