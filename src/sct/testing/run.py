# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Integration Tests - Main
----------------------------
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTConfiguration
from sct.testing import utilities as utils


def test_session_api(params: utils.TestParams, sensor: str, test_name: str, output_dir: Path, graphs: bool) -> bool:
    """Executing SCT single test using API interface.

    Parameters
    ----------
    params : utils.TestParams
        sct input params for the current test
    sensor : str
        sensor name
    test_name : str
        name of the test
    output_dir : Path
        output directory where to save the results
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    bool
        True if passed, else False
    """
    out_dir = output_dir.joinpath(sensor, test_name)
    out_dir.mkdir(exist_ok=True, parents=True)
    config = SCTConfiguration.from_toml(params.config) if params.config is not None else SCTConfiguration()
    try:
        if params.analysis == utils.SCTAnalyses.POINT_TARGET:
            config = config.point_target_analysis if config is not None else None
            results = utils.run_pta_api(params=params, output_dir=out_dir, config=config, graphs=graphs)
            # comparing dataframes differences to specific tolerances
            sct_logger.info("Validating results...")
            utils.compare_pta_df_with_tolerances(ref=pd.read_csv(params.reference_output), current=results.copy())
        elif params.analysis == utils.SCTAnalyses.NESZ:
            config = config.radiometric_analysis if config is not None else None
            nc_results, kpi_results = utils.run_nesz_api(
                params=params, output_dir=out_dir, config=config, graphs=graphs
            )
            # comparing dataframes and netcdf differences to specific tolerances
            sct_logger.info("Validating results...")
            utils.validate_ra_results(
                reference_output=params.reference_output, current_nc_output=nc_results, current_kpi_stats=kpi_results
            )
        elif params.analysis == utils.SCTAnalyses.RAIN_FOREST:
            config = config.radiometric_analysis if config is not None else None
            nc_results, kpi_results = utils.run_rain_forest_api(
                params=params, output_dir=out_dir, config=config, graphs=graphs
            )
            # comparing dataframes and netcdf differences to specific tolerances
            sct_logger.info("Validating results...")
            utils.validate_ra_results(
                reference_output=params.reference_output, current_nc_output=nc_results, current_kpi_stats=kpi_results
            )
        elif params.analysis == utils.SCTAnalyses.INTERFEROMETRY:
            config = config.interferometric_analysis if config is not None else None
            results = utils.run_interferometry_api(params=params, output_dir=out_dir, config=config)
            sct_logger.info("Validating results...")
            for report in params.reference_output:
                result = [r for r in results if report.name == r.name]
                utils.compare_interf_netcdf_with_tolerances(ref=report, current=result[0])
        sct_logger.info("")
        sct_logger.success(f"Test {test_name} - SUCCESS")
        sct_logger.info("")
        return True
    except Exception as err:
        sct_logger.info("")
        sct_logger.fail(f"Test {test_name} - FAIL")
        sct_logger.info("")
        sct_logger.error(err)
        return False


def test_session_cli(params: utils.TestParams, sensor: str, test_name: str, output_dir: Path, graphs: bool) -> bool:
    """Executing SCT single test using CLI interface.

    Parameters
    ----------
    params : utils.TestParams
        sct input params for the current test
    sensor : str
        sensor name
    test_name : str
        name of the test
    output_dir : Path
        output directory where to save the results
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    bool
        True if passed, else False
    """
    out_dir = output_dir.joinpath(sensor, test_name)
    out_dir.mkdir(exist_ok=True, parents=True)
    try:
        match params.analysis:
            case utils.SCTAnalyses.POINT_TARGET:
                results = utils.run_pta_cli(params=params, output_dir=out_dir, config=params.config)
                # comparing dataframes differences to specific tolerances
                sct_logger.info("Validating results...")
                utils.compare_pta_df_with_tolerances(ref=pd.read_csv(params.reference_output), current=results.copy())
            case utils.SCTAnalyses.NESZ:
                nc_results, kpi_results = utils.run_ra_cli(
                    params=params, output_dir=out_dir, config=params.config, analysis="NESZ"
                )
                sct_logger.info("Validating results...")
                utils.validate_ra_results(
                    reference_output=params.reference_output,
                    current_nc_output=nc_results,
                    current_kpi_stats=kpi_results,
                )
            case utils.SCTAnalyses.RAIN_FOREST:
                nc_results, kpi_results = utils.run_ra_cli(
                    params=params, output_dir=out_dir, config=params.config, analysis="RF"
                )
                sct_logger.info("Validating results...")
                utils.validate_ra_results(
                    reference_output=params.reference_output,
                    current_nc_output=nc_results,
                    current_kpi_stats=kpi_results,
                )
            case utils.SCTAnalyses.INTERFEROMETRY:
                nc_results = utils.run_interferometry_cli(params=params, output_dir=out_dir, config=params.config)
                sct_logger.info("Validating results...")
                for report in params.reference_output:
                    result = [r for r in nc_results if report.name == r.name]
                    utils.compare_interf_netcdf_with_tolerances(ref=report, current=result[0])
            case _:
                raise ValueError(f"Unsupported analysis type: {params.analysis}")
        sct_logger.info("")
        sct_logger.success(f"Test {test_name} - SUCCESS")
        sct_logger.info("")
        return True
    except Exception as err:
        sct_logger.info("")
        sct_logger.fail(f"Test {test_name} - FAIL")
        sct_logger.info("")
        sct_logger.error(err)
        return False


def run_tests(registry_path: str | Path, output_dir: str | Path, cli: bool, graphs: bool) -> dict:
    """Running all the SCT Integration Tests from input registry

    Parameters
    ----------
    registry_path : str | Path
        Path to the integration tests registry .json
    output_dir : str | Path
        Path to the output directory where to save results
    cli : bool
        flag to enable cli usage instead of api
    graphs : bool
        flag to enable graphs generation
    """

    registry_path = Path(registry_path)
    output_dir = Path(output_dir)

    sct_logger.info("")
    sct_logger.info(f"Running tests using: {'CLI' if cli else 'API'} interface")
    sct_logger.info("")

    sct_logger.info("Loading tests parameters from registry...")
    with open(registry_path, "r", encoding="UTF-8") as f_in:
        test_config = json.load(f_in)

    results = {}
    for sensor, parameters in test_config.items():
        sct_logger.info("")
        sct_logger.info("")
        sct_logger.info(f"Tests for Sensor {sensor.upper()}")
        sct_logger.info("")
        sct_logger.info("")
        results[sensor] = {}
        for test_name, test_params in parameters.items():
            sct_logger.info(f"Test {test_name.upper()}")
            sct_logger.info("")
            start_time = time.perf_counter()
            params = utils.TestParams.from_dict(test_params)
            if not cli:
                results[sensor][test_name] = test_session_api(
                    params=params, sensor=sensor, test_name=test_name, output_dir=output_dir, graphs=graphs
                )
            else:
                results[sensor][test_name] = test_session_cli(
                    params=params, sensor=sensor, test_name=test_name, output_dir=output_dir, graphs=graphs
                )
            time_spent = time.perf_counter() - start_time
            if time_spent < 60:
                sct_logger.info(f"Elapsed: {np.round(time_spent)} seconds")
            else:
                sct_logger.info(f"Elapsed: {np.round(time_spent / 60, 2)} minutes")
            sct_logger.info("")

    return results


def summary_results(results: dict) -> bool:
    """Summary of tests results.

    Parameters
    ----------
    results : dict
        results coming from run_test function

    Returns
    -------
    bool
        True if all tests are passed, else False
    """

    tests_num = sum([len(c.keys()) for c in results.values()])
    passed_tests = sum([sum(c.values()) for c in results.values()])
    sct_logger.info(f"PASSED: {passed_tests}/{tests_num} tests")
    if passed_tests == tests_num:
        sct_logger.info("No FAILED tests")
        outcome = True
    else:
        sct_logger.critical(f"FAILED: {tests_num - passed_tests}")
        outcome = False
    for sensor_name in results:
        sct_logger.info("")
        print(pd.DataFrame({sensor_name: results[sensor_name]}))

    if outcome:
        sct_logger.success("INTEGRATION TESTS: PASS")
    else:
        sct_logger.fail("INTEGRATION TESTS: FAIL")

    return outcome
