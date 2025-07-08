# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Integration Tests - Main
-----------------------------
"""

import json
import logging
import sys
import time
from itertools import compress
from pathlib import Path

import arepyextras.quality.core.custom_logger as clg
import art
import numpy as np
import pandas as pd
from integration_tests.suite.utilities import (
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

from sct.configuration.sct_configuration import SCTConfiguration

log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())


def test_session(params: TestParams, test_name: str, output_dir: Path) -> bool:
    """Testing sct point target analysis on input product.

    Parameters
    ----------
    params : TestParams
        sct input params for the current test
    test_name : str
        name of the test
    output_dir : Path
        output directory where to save the results
    """
    out_dir = output_dir.joinpath(test_name)
    out_dir.mkdir(exist_ok=True)
    config = SCTConfiguration.from_toml(params.config) if params.config is not None else None
    try:
        if params.analysis == SCTAnalyses.POINT_TARGET:
            config = config.point_target_analysis if config is not None else None
            results = run_pta_api(params=params, output_dir=out_dir, config=config)
            # comparing dataframes differences to specific tolerances
            compare_pta_df_with_tolerances(ref=pd.read_csv(params.report), current=results.copy())
        elif params.analysis == SCTAnalyses.NESZ:
            config = config.radiometric_analysis if config is not None else None
            results = run_nesz_api(params=params, output_dir=out_dir, config=config)
            if isinstance(params.report, list):
                for report in params.report:
                    result = [r for r in results if report.name == r.name]
                    compare_ra_netcdf_with_tolerances(ref=report, current=result[0])
            else:
                compare_ra_netcdf_with_tolerances(ref=params.report, current=results)
        elif params.analysis == SCTAnalyses.RAIN_FOREST:
            config = config.radiometric_analysis if config is not None else None
            results = run_rain_forest_api(params=params, output_dir=out_dir, config=config)
            if isinstance(params.report, list):
                for report in params.report:
                    result = [r for r in results if report.name == r.name]
                    compare_ra_netcdf_with_tolerances(ref=report, current=result[0])
            else:
                compare_ra_netcdf_with_tolerances(ref=params.report, current=results)
        elif params.analysis == SCTAnalyses.INTERFEROMETRY:
            config = config.interferometric_analysis if config is not None else None
            results = run_interferometry_api(params=params, output_dir=out_dir, config=config)
            for report in params.report:
                result = [r for r in results if report.name == r.name]
                compare_interf_netcdf_with_tolerances(ref=report, current=result[0])
        log.info(f"Test {test_name} successfully completed")
        return True
    except Exception as err:
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
    results = []
    for sensor, parameters in test_config.items():
        log.info(f"Launching test for sensor: {sensor.upper()}")
        for test_name, test_params in parameters.items():
            start_time = time.perf_counter()
            params = TestParams.from_dict(test_params)
            results.append(test_session(params=params, test_name=test_name, output_dir=output_dir))
            time_spent = time.perf_counter() - start_time
            if time_spent < 60:
                log.info(f"Elapsed: {np.round(time_spent)} seconds")
            else:
                log.info(f"Elapsed: {np.round(time_spent / 60, 2)} minutes")

    log.info()
    print(art.text2art("Integration Tests Summary", font="doom"))
    log.info()
    log.info(f"PASSED: {sum(results)}/{len(results)} tests")
    if sum(results) != len(results):
        failed_tests = list(compress(test_config.keys(), [not r for r in results]))
        log.critical(f"FAILED: {len(failed_tests)}")
        log.info("List of failed tests:")
        for t in failed_tests:
            log.error(t)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--registry")
    parser.add_argument("-out", "--output_dir")
    args = parser.parse_args()

    run(registry_path=args.registry, output_dir=args.output_dir)
