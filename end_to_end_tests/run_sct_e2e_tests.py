# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT End to End Tests
--------------------
"""

from __future__ import annotations

import json
import time
import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

import numpy as np
import pandas as pd
from arepyextras.quality.core.generic_dataclasses import SARRadiometricQuantity
from arepyextras.quality.interferometric_analysis.support import (
    coherence_histograms_to_netcdf,
)
from arepyextras.quality.radiometric_analysis.support import (
    radiometric_profiles_to_netcdf,
)
from netCDF4 import Dataset
from sct.analyses.interferometric_analysis import interferometric_coherence_analysis
from sct.analyses.point_target_analysis import point_target_analysis_with_corrections
from sct.analyses.radiometric_analysis import (
    average_elevation_profile_analysis,
    nesz_analysis,
)
from sct.configuration.sct_configuration import SCTConfiguration

BASE_DIR = Path(__file__).parent.resolve()
TEST_CONFIG_PATH = BASE_DIR.joinpath("test_registry.json")
BASE_OUTPUT_DIRECTORY = BASE_DIR.joinpath("output")
DEFAULT_REPORT_NAME = "point_target_analysis_results.csv"

ABSOLUTE_TOLERANCE = 1e-6
ABSOLUTE_TOLERANCE_ISLR = 5e-1
ABSOLUTE_TOLERANCE_LOC = 1e-4
ABSOLUTE_TOLERANCE_DEG = 5e-4
ABSOLUTE_TOLERANCE_RA = 1e-3

LOC_VAR_LIST = [
    "range_resolution_[m]",
    "azimuth_resolution_[m]",
    "slant_range_localization_error_[m]",
    "azimuth_localization_error_[m]",
    "ground_range_localization_error_[m]",
    "revised_ale_range_[m]",
    "revised_ale_azimuth_[m]",
]
DEG_VAR_LIST = ["peak_phase_error_[deg]", "incidence_angle_[deg]"]
ISLR_VAR_LIST = ["range_islr_[dB]", "azimuth_islr_[dB]", "islr_2d_[dB]"]
OTHER_VAR_LIST = [
    "ground_velocity_[ms]",
    "doppler_rate_theoretical_[Hzs]",
    "doppler_rate_real_[Hzs]",
    "doppler_frequency_[Hz]",
]
AZ_TIME_VAR = ["peak_azimuth_time_[UTC]"]


class SCTAnalyses(Enum):
    """Supported analyses"""

    POINT_TARGET = "pta"
    NESZ = "nesz"
    RAIN_FOREST = "rf"
    INTERFEROMETRY = "interf"


@dataclass
class TestParams:
    """Tests input parameters setup"""

    product: Path | list[Path] | None = None
    config: Path | None = None
    analysis: SCTAnalyses | None = None
    targets: Path | None = None
    external_orbit: Path | None = None
    report: Path | None = None
    etad_product: Path | None = None
    ionospheric_maps: Path | None = None
    tropospheric_maps: Path | None = None

    @classmethod
    def from_dict(cls, arg: dict) -> TestParams:
        """Composing TestParams dataclass from config dict.

        Parameters
        ----------
        arg : dict
            input dictionary

        Returns
        -------
        TestParams
            dataclass
        """
        out = cls()
        for key, val in arg.items():
            if key == "analysis":
                setattr(out, key, SCTAnalyses(val))
            else:
                if isinstance(val, list):
                    setattr(out, key, [BASE_DIR.joinpath(v) for v in val])
                elif val != "":
                    setattr(out, key, BASE_DIR.joinpath(val))
        return out


def compare_pta_df_with_tolerances(ref: pd.DataFrame, current: pd.DataFrame) -> None:
    """Comparing reference dataframe and current one, column by column to assess differences in values.
    Some values are grouped by theme ad compared with specific tolerances.

    Parameters
    ----------
    ref : pd.DataFrame
        reference dataframe
    current : pd.DataFrame
        current evaluated dataframe
    """

    # filtering only valid rows
    current = current.loc[~current["incidence_angle_[deg]"].isna()]
    current.reset_index(drop=True, inplace=True)
    ref = ref.loc[~ref["incidence_angle_[deg]"].isna()]
    ref.reset_index(drop=True, inplace=True)

    # splitting dataframes to check different values with specific tolerances
    loc_df_ref = ref[LOC_VAR_LIST].copy()
    loc_report = current[LOC_VAR_LIST].copy()
    pd.testing.assert_frame_equal(loc_df_ref, loc_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_LOC, rtol=0)

    deg_df_ref = ref[DEG_VAR_LIST].copy()
    deg_report = current[DEG_VAR_LIST].copy()
    pd.testing.assert_frame_equal(deg_df_ref, deg_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_DEG, rtol=0)

    islr_df_ref = ref[ISLR_VAR_LIST].copy()
    islr_report = current[ISLR_VAR_LIST].copy()
    pd.testing.assert_frame_equal(
        islr_df_ref,
        islr_report,
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE_ISLR,
        rtol=0,
    )

    other_df_ref = ref[OTHER_VAR_LIST].copy()
    other_report = current[OTHER_VAR_LIST].copy()
    pd.testing.assert_frame_equal(
        other_df_ref,
        other_report,
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE_RA,
        rtol=0,
    )

    # checking goodness of results
    pd.testing.assert_frame_equal(
        ref.drop(
            LOC_VAR_LIST + DEG_VAR_LIST + ISLR_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR,
            axis=1,
        ),
        current.drop(
            LOC_VAR_LIST + DEG_VAR_LIST + ISLR_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR,
            axis=1,
        ),
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )


def compare_ra_netcdf_with_tolerances(ref: Path, current: Path) -> None:
    """Compare radiometric netCDF output results with tolerances.

    Parameters
    ----------
    ref : Path
        Path to the reference netCDF4 file
    current : Path
        Path to the current run netCDF4 file
    """

    ref_dataset = Dataset(ref, "r", format="NETCDF4")
    current_dataset = Dataset(current, "r", format="NETCDF4")

    assert ref_dataset.swath == current_dataset.swath
    assert ref_dataset.channel == current_dataset.channel
    assert ref_dataset.polarization == current_dataset.polarization
    assert ref_dataset.direction == current_dataset.direction
    assert ref_dataset.output_radiometric_quantity == current_dataset.output_radiometric_quantity
    assert ref_dataset.azimuth_blocks_num == current_dataset.azimuth_blocks_num
    assert ref_dataset.azimuth_block_centers == current_dataset.azimuth_block_centers

    np.testing.assert_allclose(
        ref_dataset.range_block_centers,
        current_dataset.range_block_centers,
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )

    np.testing.assert_allclose(
        ref_dataset["look_angles"][:],
        current_dataset["look_angles"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )
    np.testing.assert_allclose(
        ref_dataset["radiometric_profiles"][:],
        current_dataset["radiometric_profiles"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )

    ref_dataset.close()
    current_dataset.close()


def compare_interf_netcdf_with_tolerances(ref: Path, current: Path) -> None:
    """Compare interferometric netCDF output results with tolerances.

    Parameters
    ----------
    ref : Path
        Path to the reference netCDF4 file
    current : Path
        Path to the current run netCDF4 file
    """

    ref_dataset = Dataset(ref, "r", format="NETCDF4")
    current_dataset = Dataset(current, "r", format="NETCDF4")

    assert ref_dataset.swath == current_dataset.swath
    assert ref_dataset.channel == current_dataset.channel
    assert ref_dataset.polarization == current_dataset.polarization
    assert ref_dataset.burst == current_dataset.burst

    np.testing.assert_allclose(
        ref_dataset["coherence_bins"][:],
        current_dataset["coherence_bins"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )
    np.testing.assert_allclose(
        ref_dataset["azimuth_histogram"][:],
        current_dataset["azimuth_histogram"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )
    np.testing.assert_allclose(
        ref_dataset["range_histogram"][:],
        current_dataset["range_histogram"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )

    ref_dataset.close()
    current_dataset.close()


def run_pta_api(params: TestParams, output_dir: Path, config: SCTConfiguration | None) -> pd.DataFrame:
    """Running SCT Point Target Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration

    Returns
    -------
    pd.DataFrame
        results dataframe
    """

    config = SCTConfiguration.from_toml(params.config)
    if params.etad_product is not None:
        config.point_target_analysis.enable_etad_corrections = True
        config.point_target_analysis.etad_product_path = params.etad_product
    if params.ionospheric_maps is not None:
        config.point_target_analysis.enable_ionospheric_correction = True
        config.point_target_analysis.ionospheric_maps_directory = params.ionospheric_maps
    if params.tropospheric_maps is not None:
        config.point_target_analysis.enable_tropospheric_correction = True
        config.point_target_analysis.tropospheric_maps_directory = params.tropospheric_maps
    results_df, _ = point_target_analysis_with_corrections(
        product_path=params.product,
        external_target_source=params.targets,
        external_orbit_path=params.external_orbit,
        config=config.point_target_analysis,
    )
    out_file = output_dir.joinpath(DEFAULT_REPORT_NAME)
    results_df.to_csv(out_file, index=False)
    return pd.read_csv(out_file)


def run_nesz_api(params: TestParams, output_dir: Path, config: SCTConfiguration | None) -> Path:
    """Running SCT NESZ Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration

    Returns
    -------
    Path
        path to output netcdf file
    """

    profiles = nesz_analysis(product_path=params.product, config=config)
    tag = "NESZ"
    for item in profiles:
        radiometric_profiles_to_netcdf(data=item, out_path=output_dir, tag=tag)
    if isinstance(params.report, list):
        return [output_dir.joinpath(p.name) for p in params.report]
    return output_dir.joinpath(params.report.name)


def run_rain_forest_api(params: TestParams, output_dir: Path, config: SCTConfiguration | None) -> Path:
    """Running SCT Average Radiometric Profiles Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration

    Returns
    -------
    Path
        path to output netcdf file
    """

    profiles = average_elevation_profile_analysis(
        product_path=params.product,
        output_quantity=SARRadiometricQuantity.GAMMA_NOUGHT,
        config=config,
    )
    tag = "RAIN_FOREST"
    for item in profiles:
        radiometric_profiles_to_netcdf(data=item, out_path=output_dir, tag=tag)
    if isinstance(params.report, list):
        return [output_dir.joinpath(p.name) for p in params.report]
    return output_dir.joinpath(params.report.name)


def run_interferometry_api(params: TestParams, output_dir: Path, config: SCTConfiguration | None) -> Path:
    """Running SCT Interferometric Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration

    Returns
    -------
    Path
        path to output netcdf file
    """

    first_prod = params.product if isinstance(params.product, Path) else params.product[0]
    second_prod = params.product[1] if isinstance(params.product, list) else None
    coherence_res = interferometric_coherence_analysis(
        product_path=first_prod, second_product_path=second_prod, config=config
    )
    for res in coherence_res:
        # saving 2D histograms to netcdf
        coherence_histograms_to_netcdf(data=res, output_dir=output_dir)
    return [output_dir.joinpath(p.name) for p in params.report]


def test_session(params: TestParams, test_name: str) -> bool:
    """Testing sct point target analysis on input product.

    Parameters
    ----------
    params : TestParams
        sct input params for the current test
    test_name : str
        name of the test
    """
    out_dir = BASE_OUTPUT_DIRECTORY.joinpath(test_name)
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
        print(f"\nTest {test_name} successfully completed\n")
        return True
    except Exception as err:
        print(f"\nTest {test_name} ERROR\n")
        print(err)
        return False


def run() -> None:
    """Running all the SCT E2E tests in the dataset"""

    with open(TEST_CONFIG_PATH, "r", encoding="UTF-8") as f_in:
        test_config = json.load(f_in)

    print("SCT End to End Testing")
    results = []
    for test_name, parameters in test_config.items():
        print(f"\nLaunching test: {test_name}\n")
        start_time = time.perf_counter()
        params = TestParams.from_dict(parameters)
        results.append(test_session(params=params, test_name=test_name))
        print(f"Elapsed: {np.round((time.perf_counter() - start_time) / 60, 2)} minutes\n")

    print("SCT E2E Summary:")
    print(f"{sum(results)}/{len(results)} tests passed")
    if sum(results) != len(results):
        failed_tests = test_config.keys()[not results]
        print("Tests failed:")
        for t in failed_tests:
            print(t)


if __name__ == "__main__":

    run()
