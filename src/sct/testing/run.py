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
from sct.testing.utilities import (
    SCTAnalyses,
    TestParams,
    compare_interf_netcdf_with_tolerances,
    compare_kpi_stats,
    compare_pta_df_with_tolerances,
    compare_ra_netcdf_with_tolerances,
    run_interferometry_api,
    run_nesz_api,
    run_pta_api,
    run_rain_forest_api,
)


def test_session(params: TestParams, sensor: str, test_name: str, output_dir: Path, graphs: bool) -> bool:
    """Testing sct point target analysis on input product.

    Parameters
    ----------
    params : TestParams
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
        if params.analysis == SCTAnalyses.POINT_TARGET:
            config = config.point_target_analysis if config is not None else None
            results = run_pta_api(params=params, output_dir=out_dir, config=config, graphs=graphs)
            # comparing dataframes differences to specific tolerances
            sct_logger.info("Validating results...")
            compare_pta_df_with_tolerances(ref=pd.read_csv(params.reference_output), current=results.copy())
        elif params.analysis == SCTAnalyses.NESZ:
            config = config.radiometric_analysis if config is not None else None
            nc_results, kpi_results = run_nesz_api(params=params, output_dir=out_dir, config=config, graphs=graphs)
            sct_logger.info("Validating results...")
            if isinstance(params.reference_output, list):
                for report in params.reference_output:
                    if ".nc" in report.name:
                        result = [r for r in nc_results if report.name == r.name]
                        compare_ra_netcdf_with_tolerances(ref=report, current=result[0])
            else:
                compare_ra_netcdf_with_tolerances(ref=params.reference_output, current=results)
            kpi_csv_file = [p for p in params.reference_output if ".csv" in p.name]
            if kpi_csv_file:
                compare_kpi_stats(ref=pd.read_csv(kpi_csv_file[0]), current=pd.read_csv(kpi_results))
        elif params.analysis == SCTAnalyses.RAIN_FOREST:
            config = config.radiometric_analysis if config is not None else None
            nc_results, kpi_results = run_rain_forest_api(
                params=params, output_dir=out_dir, config=config, graphs=graphs
            )
            sct_logger.info("Validating results...")
            if isinstance(params.reference_output, list):
                for report in params.reference_output:
                    if ".nc" in report.name:
                        result = [r for r in nc_results if report.name == r.name]
                        compare_ra_netcdf_with_tolerances(ref=report, current=result[0])
            else:
                compare_ra_netcdf_with_tolerances(ref=params.reference_output, current=nc_results)
            kpi_csv_file = [p for p in params.reference_output if ".csv" in p.name]
            if kpi_csv_file:
                compare_kpi_stats(ref=pd.read_csv(kpi_csv_file[0]), current=pd.read_csv(kpi_results))
        elif params.analysis == SCTAnalyses.INTERFEROMETRY:
            config = config.interferometric_analysis if config is not None else None
            results = run_interferometry_api(params=params, output_dir=out_dir, config=config)
            sct_logger.info("Validating results...")
            for report in params.reference_output:
                result = [r for r in results if report.name == r.name]
                compare_interf_netcdf_with_tolerances(ref=report, current=result[0])
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


def run_tests(registry_path: str | Path, output_dir: str | Path, graphs: bool) -> dict:
    """Running all the SCT Integration Tests from input registry

    Parameters
    ----------
    registry_path : str | Path
        Path to the integration tests registry .json
    output_dir : str | Path
        Path to the output directory where to save results
    graphs : bool
        flag to enable graphs generation
    """

    registry_path = Path(registry_path)
    output_dir = Path(output_dir)

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
            params = TestParams.from_dict(test_params)
            results[sensor][test_name] = test_session(
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
