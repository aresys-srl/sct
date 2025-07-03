# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Integration test script to test the whole application using reference well known data"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from arepyextras.test import DataRepository, Environment, TestSession, skip_if
from netCDF4 import Dataset

from sct.analyses.automatic_analyses import sct_automatic_analysis
from sct.configuration.sct_configuration import SCTConfiguration

PYTHON_INTERPRETER = sys.executable
ABSOLUTE_TOLERANCE = 1e-6
ABSOLUTE_TOLERANCE_ISLR = 5e-1
ABSOLUTE_TOLERANCE_LOC = 1e-4
ABSOLUTE_TOLERANCE_DEG = 5e-4
ABSOLUTE_TOLERANCE_RA = 1e-2
ABSOLUTE_TOLERANCE_OTHER = 1e-3

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


def _compare_pta_df_with_tolerances(ref: pd.DataFrame, current: pd.DataFrame) -> None:
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
    pd.testing.assert_frame_equal(islr_df_ref, islr_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_ISLR, rtol=0)

    other_df_ref = ref[OTHER_VAR_LIST].copy()
    other_report = current[OTHER_VAR_LIST].copy()
    pd.testing.assert_frame_equal(other_df_ref, other_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_OTHER, rtol=0)

    # TODO: remove this with next integration test dataset update
    skip_vars = ["rcs_theoretical_[dB]"]

    # checking goodness of results
    pd.testing.assert_frame_equal(
        ref.drop(LOC_VAR_LIST + DEG_VAR_LIST + ISLR_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR + skip_vars, axis=1),
        current.drop(LOC_VAR_LIST + DEG_VAR_LIST + ISLR_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR + skip_vars, axis=1),
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )


def _compare_ra_netcdf_with_tolerances(ref: Path, current: Path) -> None:
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
        ref_dataset.range_block_centers, current_dataset.range_block_centers, atol=ABSOLUTE_TOLERANCE, rtol=0
    )

    np.testing.assert_allclose(
        ref_dataset["look_angles"][:], current_dataset["look_angles"][:], atol=ABSOLUTE_TOLERANCE, rtol=0
    )
    np.testing.assert_allclose(
        ref_dataset["radiometric_profiles"][:],
        current_dataset["radiometric_profiles"][:],
        atol=ABSOLUTE_TOLERANCE_RA,
        rtol=0,
    )

    ref_dataset.close()
    current_dataset.close()


def _compare_interf_netcdf_with_tolerances(ref: Path, current: Path) -> None:
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
        ref_dataset["coherence_bins"][:], current_dataset["coherence_bins"][:], atol=ABSOLUTE_TOLERANCE, rtol=0
    )
    np.testing.assert_allclose(
        ref_dataset["azimuth_histogram"][:],
        current_dataset["azimuth_histogram"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )
    np.testing.assert_allclose(
        ref_dataset["range_histogram"][:], current_dataset["range_histogram"][:], atol=ABSOLUTE_TOLERANCE, rtol=0
    )

    ref_dataset.close()
    current_dataset.close()


def _run_cli_tool_pta(
    session: TestSession, env: Environment, config: Path, product: Path, targets: Path, ext_orbit: Path | None = None
) -> pd.DataFrame:
    """Running SCT Point Target Analysis from CLI tool forwarding the inputs.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    config : Path
        path to the toml config file
    product : Path
        path to the product to be analyzed
    targets : Path
        path to the point target file
    ext_orbit : Path | None, optional
        path to the external orbit file, by default None

    Returns
    -------
    pd.DataFrame
        results dataframe
    """
    out_file = env.root.joinpath("point_target_analysis_results.csv")

    # analysis
    result = env.run("sct", "--config", config, "target-analysis", "-p", product, "-out", env.root, "-pt", targets)
    # checking successful run
    if result.returncode != 0:
        print(result.stderr.read_text())
    session.expect_run_successful(result)
    assert out_file.is_file()

    return pd.read_csv(out_file)


def _run_cli_tool_ra(session: TestSession, env: Environment, config: Path, product: Path, analysis: str):
    """Running SCT Radiometric Analysis from CLI tool forwarding the inputs.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    config : Path
        path to the toml config file
    product : Path
        path to the product to be analyzed
    analysis : str
        analysis to be performed, [NESZ, RF]
    """

    # analysis
    if analysis == "RF":
        result = env.run(
            "sct",
            "--config",
            config,
            "radiometric-analysis",
            "elevation_profile",
            "-p",
            product,
            "-out",
            env.root,
            "-r",
            "gamma",
        )
    elif analysis == "NESZ":
        result = env.run("sct", "--config", config, "radiometric-analysis", "nesz", "-p", product, "-out", env.root)
    # checking successful run
    if result.returncode != 0:
        print(result.stderr.read_text())
    session.expect_run_successful(result)


def _run_cli_tool_interf(session: TestSession, env: Environment, config: Path, product: Path | list[Path]):
    """Running SCT Interferometric Analysis from CLI tool forwarding the inputs.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    config : Path
        path to the toml config file
    product : Path | list[Path]
        path or list of paths to the product(s) to be analyzed
    """

    # analysis
    if isinstance(product, list):
        result = env.run(
            "sct", "--config", config, "interferometric-analysis", "-p", product[0], "-pp", product[1], "-out", env.root
        )
    else:
        result = env.run("sct", "--config", config, "interferometric-analysis", "-p", product, "-out", env.root)
    # checking successful run
    if result.returncode != 0:
        print(result.stderr.read_text())
    session.expect_run_successful(result)


def test_pta_novasar1_slc(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on NovaSAR-1 SLC product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/novasar1/config")
    product_folder = data.pull("input/novasar1/SLC")
    point_target = data.pull("input/novasar1/SuratBasinDataCSV")
    report = data.pull("output/novasar1/SLC")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_novasar1_grd(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on NovaSAR-1 GRD product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/novasar1/config")
    product_folder = data.pull("input/novasar1/GRD")
    point_target = data.pull("input/novasar1/SuratBasinDataCSV")
    report = data.pull("output/novasar1/GRD")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_novasar1_scd(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on NovaSAR-1 SCD product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/novasar1/config")
    product_folder = data.pull("input/novasar1/SCD")
    point_target = data.pull("input/novasar1/SuratBasinDataCSV")
    report = data.pull("output/novasar1/SCD")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_rain_forest_novasar1_scd(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct average radiometric profiles (gamma) on NovaSAR-1 SCD product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    product_folder = data.pull("input/novasar1/SCD_RF")
    ref = data.pull("output/novasar1/SCD_RF")
    out_file = env.root.joinpath("AVERAGE_GAMMA_NOUGHT_profiles_S_VV.nc")
    # TODO: check these results for proper radiometric quantity (input is beta now)

    config_file = env.root.joinpath("new_config.toml")
    config = SCTConfiguration()
    config.radiometric_analysis.base_config.profile_extraction_parameters.outlier_removal = False
    config.radiometric_analysis.base_config.profile_extraction_parameters.smoothening_filter = False
    config.dump_to_toml(out_file=config_file)
    assert config_file.is_file()

    # running analysis using CLI
    _run_cli_tool_ra(env=env, session=session, config=config_file, product=product_folder, analysis="RF")

    # comparing netcdf differences to specific tolerances
    _compare_ra_netcdf_with_tolerances(ref=ref, current=out_file)


def test_nesz_novasar1_grd(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct average radiometric profiles (gamma) on NovaSAR-1 SCD product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    product_folder = data.pull("input/novasar1/GRD_NESZ")
    ref = data.pull("output/novasar1/GRD_NESZ")
    out_file = env.root.joinpath("NESZ_profiles_S1_HH.nc")
    # TODO: check these results for proper radiometric quantity (input is beta now)

    config_file = env.root.joinpath("new_config.toml")
    config = SCTConfiguration()
    config.dump_to_toml(out_file=config_file)
    assert config_file.is_file()

    # running analysis using CLI
    _run_cli_tool_ra(env=env, session=session, config=config_file, product=product_folder, analysis="NESZ")

    # comparing netcdf differences to specific tolerances
    _compare_ra_netcdf_with_tolerances(ref=ref, current=out_file)


def test_pta_iceye_stripmap(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on ICEYE stripmap product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/iceye/config")
    product_folder = data.pull("input/iceye/SM")
    point_target = data.pull("input/iceye/RosamondCSV")
    report = data.pull("output/iceye/SM")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_z_pta_iceye_stripmap_automatic(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on ICEYE stripmap product via automatic sct analysis detection.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/iceye/config")
    product_folder = data.pull("input/iceye/SM")
    point_target = data.pull("input/iceye/RosamondCSV")
    report = data.pull("output/iceye/SM")
    expected_report = pd.read_csv(report)

    # creating json calibration sites registry
    registry_json = env.root.joinpath("registry.json")
    cal_sites_registry = {
        "regions": {
            "rosamond": {
                "description": "Rosamond Corner Reflector Array, Rosamond Dry Lakebed, California, USA",
                "latitude_boundaries_deg": [34, 35],
                "longitude_boundaries_deg": [-119, -117],
                "supported_analyses": ["point_target_analysis"],
                "reference_dataset": str(point_target),
            }
        }
    }
    with open(registry_json, "w", encoding="utf-8") as f_out:
        json.dump(cal_sites_registry, f_out)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )
    sct_automatic_analysis(
        product_path=product_folder,
        output_dir=env.root,
        calibration_sites_registry=registry_json,
        graphs=False,
        config=SCTConfiguration.from_toml(config),
    )
    current_df = pd.read_csv(env.root.joinpath("point_target_analysis_results.csv"))

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_iceye_spotlight(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on ICEYE spotlight product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/iceye/config")
    product_folder = data.pull("input/iceye/SLH")
    point_target = data.pull("input/iceye/RosamondCSV")
    report = data.pull("output/iceye/SLH")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_iceye_topsar(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on ICEYE topsar product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/iceye/config")
    product_folder = data.pull("input/iceye/SC")
    point_target = data.pull("input/iceye/RosamondCSV")
    report = data.pull("output/iceye/SC")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_saocom_slc(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on SAOCOM stripmap SLC product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/saocom/config")
    product_folder = data.pull("input/saocom/L1A_SLC_SM")
    point_target = data.pull("input/saocom/SaocomCSV")
    report = data.pull("output/saocom/L1A_SLC_SM")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_saocom_grd(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on SAOCOM stripmap GRD product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/saocom/config")
    product_folder = data.pull("input/saocom/L1B_RGC_SM")
    point_target = data.pull("input/saocom/SaocomCSV")
    report = data.pull("output/saocom/L1B_RGC_SM")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_s1_slc_etad(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on Sentinel-1 SLC 23 product with its etad product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/s1/config_etad")
    product_folder = data.pull("input/s1/SLC_23")
    point_target = data.pull("input/s1/SuratBasinDataCSV")
    etad_product = data.pull("input/s1/ETAD")
    report = data.pull("output/s1/SLC_23_ETAD")
    expected_report = pd.read_csv(report)

    # preparing config
    edited_config = SCTConfiguration.from_toml(config)
    edited_config.point_target_analysis.etad_product_path = etad_product
    new_config = env.root.joinpath("new_config.toml")
    edited_config.dump_to_toml(out_file=new_config)
    assert new_config.is_file()

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env,
        session=session,
        config=new_config,
        product=product_folder,
        targets=point_target,
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_s1_slc_perturb(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on Sentinel-1 SLC 19 product with all perturbations enabled.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/s1/config_perturbations")
    product_folder = data.pull("input/s1/SLC_19")
    point_target = data.pull("input/s1/SuratBasinDataCSV")
    iono_maps = data.pull("input/s1/ionosphere_maps")
    tropo_maps = data.pull("input/s1/troposphere_maps")
    report = data.pull("output/s1/SLC_19_PERT")
    expected_report = pd.read_csv(report)

    # preparing config
    edited_config = SCTConfiguration.from_toml(config)
    edited_config.point_target_analysis.ionospheric_maps_directory = iono_maps
    edited_config.point_target_analysis.tropospheric_maps_directory = tropo_maps
    new_config = env.root.joinpath("new_config.toml")
    edited_config.dump_to_toml(out_file=new_config)
    assert new_config.is_file()

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=new_config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_s1_slc_perturb_ext_orbit(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on Sentinel-1 SLC 19 product with all perturbations enabled with ext orbit.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/s1/config_perturbations")
    product_folder = data.pull("input/s1/SLC_19")
    point_target = data.pull("input/s1/SuratBasinDataCSV")
    ext_orbit = data.pull("input/s1/ext_orbit")
    iono_maps = data.pull("input/s1/ionosphere_maps")
    tropo_maps = data.pull("input/s1/troposphere_maps")
    report = data.pull("output/s1/SLC_19_PERT_EXT_ORBIT")
    expected_report = pd.read_csv(report)

    # preparing config
    edited_config = SCTConfiguration.from_toml(config)
    edited_config.point_target_analysis.ionospheric_maps_directory = iono_maps
    edited_config.point_target_analysis.tropospheric_maps_directory = tropo_maps
    new_config = env.root.joinpath("new_config.toml")
    edited_config.dump_to_toml(out_file=new_config)
    assert new_config.is_file()

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=new_config, product=product_folder, targets=point_target, ext_orbit=ext_orbit
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_s1_grd_perturb(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on Sentinel-1 GRD 19 product with all perturbations enabled.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/s1/config_perturbations")
    product_folder = data.pull("input/s1/GRD_19")
    point_target = data.pull("input/s1/SuratBasinDataCSV")
    iono_maps = data.pull("input/s1/ionosphere_maps")
    tropo_maps = data.pull("input/s1/troposphere_maps")
    report = data.pull("output/s1/GRD_19_PERT")
    expected_report = pd.read_csv(report)

    # preparing config
    edited_config = SCTConfiguration.from_toml(config)
    edited_config.point_target_analysis.ionospheric_maps_directory = iono_maps
    edited_config.point_target_analysis.tropospheric_maps_directory = tropo_maps
    new_config = env.root.joinpath("new_config.toml")
    edited_config.dump_to_toml(out_file=new_config)
    assert new_config.is_file()

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env,
        session=session,
        config=new_config,
        product=product_folder,
        targets=point_target,
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_cosmo_grd(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on COSMO SkyMed scansar GRD product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/cosmo/config")
    product_folder = data.pull("input/cosmo/DGM_SCANSAR")
    point_target = data.pull("input/cosmo/NeusterlitzCSV")
    report = data.pull("output/cosmo/DGM_SCANSAR")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


def test_pta_asar_slc(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on Envisat ASAR slc product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/asar/config")
    product_folder = data.pull("input/asar/ASA_IMS_SLC")
    point_target = data.pull("input/asar/ASAR_transponders")
    report = data.pull("output/asar/ASA_IMS_SLC")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


# TODO: check these results
def test_pta_asar_grd(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct point target analysis on Envisat ASAR slc product.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    config = data.pull("input/asar/config")
    product_folder = data.pull("input/asar/ASA_WSM_GRD")
    point_target = data.pull("input/asar/ASAR_transponders")
    report = data.pull("output/asar/ASA_WSM_GRD")
    expected_report = pd.read_csv(report)

    # running analysis using CLI
    current_df = _run_cli_tool_pta(
        env=env, session=session, config=config, product=product_folder, targets=point_target
    )

    # comparing dataframes differences to specific tolerances
    _compare_pta_df_with_tolerances(ref=expected_report.copy(), current=current_df.copy())


@skip_if(sys.platform.startswith("linux"))
def test_interferometry_pf_co_registered(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct interferometric analysis on two co-registered PF products.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    pf_1 = data.pull("input/pf/INT_PROD_1")
    pf_2 = data.pull("input/pf/INT_PROD_2")
    ref_outputs = {f.name: f for f in data.pull("output/pf/co_registered").iterdir()}
    out_files = [
        env.root.joinpath("coherence_histograms_IW1_b0_VH.nc"),
        env.root.joinpath("coherence_histograms_IW1_b1_VH.nc"),
        env.root.joinpath("coherence_histograms_IW1_b0_VV.nc"),
        env.root.joinpath("coherence_histograms_IW1_b1_VV.nc"),
    ]

    config_file = env.root.joinpath("new_config.toml")
    config = SCTConfiguration()
    config.interferometric_analysis.base_config.enable_coherence_computation = True
    config.dump_to_toml(out_file=config_file)
    assert config_file.is_file()

    # running analysis using CLI
    _run_cli_tool_interf(env=env, session=session, config=config_file, product=[pf_1, pf_2])

    # comparing netcdf differences to specific tolerances
    for file in out_files:
        _compare_interf_netcdf_with_tolerances(ref=ref_outputs[file.name], current=file)


def test_interferometry_pf_interferogram(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct interferometric analysis on interferogram PF.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    pf = data.pull("input/pf/INT_PROD")
    ref_outputs = {f.name: f for f in data.pull("output/pf/interferogram").iterdir()}
    out_files = [
        env.root.joinpath("coherence_histograms_IW1_b0_VH.nc"),
        env.root.joinpath("coherence_histograms_IW1_b1_VH.nc"),
        env.root.joinpath("coherence_histograms_IW1_b0_VV.nc"),
        env.root.joinpath("coherence_histograms_IW1_b1_VV.nc"),
    ]

    config_file = env.root.joinpath("new_config.toml")
    config = SCTConfiguration()
    config.interferometric_analysis.base_config.enable_coherence_computation = True
    config.interferometric_analysis.base_config.coherence_kernel = [5, 5]
    config.dump_to_toml(out_file=config_file)
    assert config_file.is_file()

    # running analysis using CLI
    _run_cli_tool_interf(env=env, session=session, config=config_file, product=pf)

    # comparing netcdf differences to specific tolerances
    for file in out_files:
        _compare_interf_netcdf_with_tolerances(ref=ref_outputs[file.name], current=file)


def test_interferometry_pf_coherence_map(session: TestSession, env: Environment, data: DataRepository):
    """Testing sct interferometric analysis on coherence map PF.

    Parameters
    ----------
    session : TestSession
        sct test session
    env : Environment
        sct test environment
    data : DataRepository
        sct dataset repository manager
    """
    pf = data.pull("input/pf/INT_PROD_CM")
    ref_outputs = {f.name: f for f in data.pull("output/pf/coherence_map").iterdir()}
    out_files = [
        env.root.joinpath("coherence_histograms_IW1_b0_VH.nc"),
        env.root.joinpath("coherence_histograms_IW1_b1_VH.nc"),
        env.root.joinpath("coherence_histograms_IW1_b0_VV.nc"),
        env.root.joinpath("coherence_histograms_IW1_b1_VV.nc"),
    ]

    config_file = env.root.joinpath("new_config.toml")
    config = SCTConfiguration()
    config.dump_to_toml(out_file=config_file)
    assert config_file.is_file()

    # running analysis using CLI
    _run_cli_tool_interf(env=env, session=session, config=config_file, product=pf)

    # comparing netcdf differences to specific tolerances
    for file in out_files:
        _compare_interf_netcdf_with_tolerances(ref=ref_outputs[file.name], current=file)
