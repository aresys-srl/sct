# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Integration test script to test the whole application using reference well known data"""

import sys

import pandas as pd
from arepyextras.test import DataRepository, Environment, TestSession

from sct.analyses import point_target_analysis as pta
from sct.configuration.sct_default_configuration import SCTConfiguration

PYTHON_INTERPRETER = sys.executable
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


def _compare_df_with_tolerances(ref: pd.DataFrame, current: pd.DataFrame) -> None:
    """Comparing reference dataframe and current one, column by column to assess differences in values.
    Some values are grouped by theme ad compared with specific tolerances.

    Parameters
    ----------
    ref : pd.DataFrame
        reference dataframe
    current : pd.DataFrame
        current evaluated dataframe
    """
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
    pd.testing.assert_frame_equal(other_df_ref, other_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_RA, rtol=0)

    # checking goodness of results
    pd.testing.assert_frame_equal(
        ref.drop(LOC_VAR_LIST + DEG_VAR_LIST + ISLR_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR, axis=1),
        current.drop(LOC_VAR_LIST + DEG_VAR_LIST + ISLR_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR, axis=1),
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )


def test_point_target_analysis_novasar1_slc(session: TestSession, env: Environment, data: DataRepository):
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
    config_ = data.pull("input/novasar1/config")
    product_folder = data.pull("input/novasar1/SLC")
    point_target = data.pull("input/novasar1/PointTargetsXML")
    report_ = data.pull("output/novasar1/SLC")

    # preparing config
    config = SCTConfiguration.from_toml(config_)

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_novasar1_grd(session: TestSession, env: Environment, data: DataRepository):
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
    config_ = data.pull("input/novasar1/config")
    product_folder = data.pull("input/novasar1/GRD")
    point_target = data.pull("input/novasar1/PointTargetsXML")
    report_ = data.pull("output/novasar1/GRD")

    # preparing config
    config = SCTConfiguration.from_toml(config_)

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_novasar1_scd(session: TestSession, env: Environment, data: DataRepository):
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
    config_ = data.pull("input/novasar1/config")
    product_folder = data.pull("input/novasar1/SCD")
    point_target = data.pull("input/novasar1/PointTargetsXML")
    report_ = data.pull("output/novasar1/SCD")

    # preparing config
    config = SCTConfiguration.from_toml(config_)

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_sentinel1_slc_perturbations(
    session: TestSession, env: Environment, data: DataRepository
):
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
    config_ = data.pull("input/sentinel1/config_perturbations")
    product_folder = data.pull("input/sentinel1/SLC_19")
    point_target = data.pull("input/sentinel1/PointTargetsBinarySurat")
    iono_maps = data.pull("input/sentinel1/ionosphere_maps")
    tropo_maps = data.pull("input/sentinel1/troposphere_maps")
    report_ = data.pull("output/sentinel1/SLC_19_PERT")

    # preparing config
    config = SCTConfiguration.from_toml(config_)
    config.point_target_analysis.ionospheric_maps_directory = iono_maps
    config.point_target_analysis.tropospheric_maps_directory = tropo_maps

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_sentinel1_slc_perturbations_ext_orbit(
    session: TestSession, env: Environment, data: DataRepository
):
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
    config_ = data.pull("input/sentinel1/config_perturbations")
    product_folder = data.pull("input/sentinel1/SLC_19")
    point_target = data.pull("input/sentinel1/PointTargetsBinarySurat")
    ext_orbit = data.pull("input/sentinel1/ext_orbit")
    iono_maps = data.pull("input/sentinel1/ionosphere_maps")
    tropo_maps = data.pull("input/sentinel1/troposphere_maps")
    report_ = data.pull("output/sentinel1/SLC_19_PERT_EXT_ORBIT")

    # preparing config
    config = SCTConfiguration.from_toml(config_)
    config.point_target_analysis.ionospheric_maps_directory = iono_maps
    config.point_target_analysis.tropospheric_maps_directory = tropo_maps

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_orbit_path=ext_orbit,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_sentinel1_slc_etad(session: TestSession, env: Environment, data: DataRepository):
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
    config_ = data.pull("input/sentinel1/config_etad")
    product_folder = data.pull("input/sentinel1/SLC_23")
    etad_product = data.pull("input/sentinel1/ETAD")
    report_ = data.pull("output/sentinel1/SLC_23_ETAD")
    point_target = data.pull("input/sentinel1/SuratBasinDataCSV")

    # preparing config
    config = SCTConfiguration.from_toml(config_)
    config.point_target_analysis.etad_product_path = etad_product

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_sentinel1_grd_perturbations(
    session: TestSession, env: Environment, data: DataRepository
):
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
    config_ = data.pull("input/sentinel1/config_perturbations")
    product_folder = data.pull("input/sentinel1/GRD_19")
    point_target = data.pull("input/sentinel1/PointTargetsBinarySurat")
    iono_maps = data.pull("input/sentinel1/ionosphere_maps")
    tropo_maps = data.pull("input/sentinel1/troposphere_maps")
    report_ = data.pull("output/sentinel1/GRD_19_PERT")

    # preparing config
    config = SCTConfiguration.from_toml(config_)
    config.point_target_analysis.ionospheric_maps_directory = iono_maps
    config.point_target_analysis.tropospheric_maps_directory = tropo_maps

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_iceye_stripmap(session: TestSession, env: Environment, data: DataRepository):
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
    config_ = data.pull("input/iceye/config")
    product_folder = data.pull("input/iceye/SM")
    point_target = data.pull("input/iceye/PointTargetsBinaryRosamond")
    report_ = data.pull("output/iceye/SM")

    # preparing config
    config = SCTConfiguration.from_toml(config_)

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_iceye_spotlight(session: TestSession, env: Environment, data: DataRepository):
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
    config_ = data.pull("input/iceye/config")
    product_folder = data.pull("input/iceye/SLH")
    point_target = data.pull("input/iceye/PointTargetsBinaryRosamond")
    report_ = data.pull("output/iceye/SLH")

    # preparing config
    config = SCTConfiguration.from_toml(config_)

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())


def test_point_target_analysis_iceye_topsar(session: TestSession, env: Environment, data: DataRepository):
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
    config_ = data.pull("input/iceye/config")
    product_folder = data.pull("input/iceye/SC")
    point_target = data.pull("input/iceye/PointTargetsBinaryRosamond")
    report_ = data.pull("output/iceye/SC")

    # preparing config
    config = SCTConfiguration.from_toml(config_)

    # preparing report
    expected_report = pd.read_csv(report_)
    out_file = env.root.joinpath("sct_report.csv")

    # analysis
    results_df, _ = pta.main(
        product_path=product_folder,
        external_target_source=point_target,
        config=config.point_target_analysis,
    )
    results_df.to_csv(out_file, index=False)
    loaded_df = pd.read_csv(out_file)

    # filtering only valid rows
    loaded_df = loaded_df.loc[~loaded_df["incidence_angle_[deg]"].isna()]
    loaded_df.reset_index(drop=True, inplace=True)
    expected_report = expected_report.loc[~expected_report["incidence_angle_[deg]"].isna()]
    expected_report.reset_index(drop=True, inplace=True)

    # comparing dataframes differences to specific tolerances
    _compare_df_with_tolerances(ref=expected_report.copy(), current=loaded_df.copy())
