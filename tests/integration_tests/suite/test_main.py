# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Integration Tests - Main
-----------------------------
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import arepyextras.quality.core.custom_logger as clg
import art
import numpy as np
import pandas as pd

from sct.configuration.sct_configuration import SCTConfiguration

current_dir_name = os.path.dirname((os.path.realpath(__file__)))
sys.path.append(current_dir_name)

from utilities import (  # noqa: E402
    SCTAnalyses,
    TestParams,
    compare_interf_netcdf_with_tolerances,
    compare_pta_df_with_tolerances,
    compare_ra_netcdf_with_tolerances,
    run_interferometry_api,
    run_nesz_api,
    run_pta_api,
    run_rain_forest_api,
)

log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())


def test_session(params: TestParams, sensor: str, test_name: str, output_dir: Path) -> bool:
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
    """
    out_dir = output_dir.joinpath(sensor, test_name)
    out_dir.mkdir(exist_ok=True, parents=True)
    config = SCTConfiguration.from_toml(params.config) if params.config is not None else None
    try:
        if params.analysis == SCTAnalyses.POINT_TARGET:
            config = config.point_target_analysis if config is not None else None
            results = run_pta_api(params=params, output_dir=out_dir, config=config)
            # comparing dataframes differences to specific tolerances
            log.info("Validating results...")
            compare_pta_df_with_tolerances(ref=pd.read_csv(params.reference_output), current=results.copy())
        elif params.analysis == SCTAnalyses.NESZ:
            config = config.radiometric_analysis if config is not None else None
            results = run_nesz_api(params=params, output_dir=out_dir, config=config)
            log.info("Validating results...")
            if isinstance(params.reference_output, list):
                for report in params.reference_output:
                    result = [r for r in results if report.name == r.name]
                    compare_ra_netcdf_with_tolerances(ref=report, current=result[0])
            else:
                compare_ra_netcdf_with_tolerances(ref=params.reference_output, current=results)
        elif params.analysis == SCTAnalyses.RAIN_FOREST:
            config = config.radiometric_analysis if config is not None else None
            results = run_rain_forest_api(params=params, output_dir=out_dir, config=config)
            log.info("Validating results...")
            if isinstance(params.reference_output, list):
                for report in params.reference_output:
                    result = [r for r in results if report.name == r.name]
                    compare_ra_netcdf_with_tolerances(ref=report, current=result[0])
            else:
                compare_ra_netcdf_with_tolerances(ref=params.reference_output, current=results)
        elif params.analysis == SCTAnalyses.INTERFEROMETRY:
            config = config.interferometric_analysis if config is not None else None
            results = run_interferometry_api(params=params, output_dir=out_dir, config=config)
            log.info("Validating results...")
            for report in params.reference_output:
                result = [r for r in results if report.name == r.name]
                compare_interf_netcdf_with_tolerances(ref=report, current=result[0])
        log.info("")
        log.info(f"Test {test_name} - SUCCESS")
        log.info("")
        return True
    except Exception as err:
        log.info("")
        log.critical(f"Test {test_name} ERROR")
        print(err)
        return False


def run(registry_path: str, output_dir: str) -> None:
    """Running all the SCT Integration Tests from input registry

    Parameters
    ----------
    registry_path : str
        Path to the integration tests registry .json
    output_dir : str
        Path to the output directory where to save results
    """

    registry_path = Path(registry_path)
    output_dir = Path(output_dir)

    with open(registry_path, "r", encoding="UTF-8") as f_in:
        test_config = json.load(f_in)
    print("")
    print(art.text2art("SCT Integration Tests", font="doom"))
    print("")
    results = {}
    for sensor, parameters in test_config.items():
        print(f"\nTests for Sensor {sensor.upper()}\n")
        results[sensor] = {}
        for test_name, test_params in parameters.items():
            print(f"\nTest {test_name.upper()}\n")
            start_time = time.perf_counter()
            params = TestParams.from_dict(test_params)
            results[sensor][test_name] = test_session(
                params=params, sensor=sensor, test_name=test_name, output_dir=output_dir
            )
            time_spent = time.perf_counter() - start_time
            if time_spent < 60:
                log.info(f"Elapsed: {np.round(time_spent)} seconds")
            else:
                log.info(f"Elapsed: {np.round(time_spent / 60, 2)} minutes")

    print("\n\n\n")
    print(art.text2art("Summary", font="doom"))
    print("")
    tests_num = sum([len(c.keys()) for c in results.values()])
    passed_tests = sum([sum(c.values()) for c in results.values()])
    log.info(f"PASSED: {passed_tests}/{tests_num} tests")
    if passed_tests == tests_num:
        log.info("No FAILED tests")
    else:
        log.critical(f"FAILED: {tests_num - passed_tests}")
    for sensor_name in results:
        print("")
        print(pd.DataFrame({sensor_name: results[sensor_name]}))
    else:
        sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--registry")
    parser.add_argument("-out", "--output_dir")
    args = parser.parse_args()
    registry = args.registry
    out_dir = args.output_dir

    run(registry_path=registry, output_dir=out_dir)
