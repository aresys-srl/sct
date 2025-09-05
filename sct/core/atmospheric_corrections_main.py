# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Main entry point for atmospheric corrections
--------------------------------------------
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from arepytools.geometry.curve_protocols import TwiceDifferentiable3DCurve
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.configuration.logger import sct_logger
from sct.configuration.point_target_analysis_configuration import SCTPointTargetAnalysisCorrectionsConf
from sct.core.atmospheric_corrections_core import IonosphericInput, TroposphereInput, compute_atmospheric_delays


@dataclass
class AtmosphericDelaysAcquisitionInfo:
    """Acquisition information required for computing atmospheric delays"""

    trajectory: TwiceDifferentiable3DCurve
    azimuth_time: PreciseDateTime
    carrier_frequency: float


def run_compute_atmospheric_delays(
    target_coords: np.ndarray,
    acquisition_info: AtmosphericDelaysAcquisitionInfo,
    config: SCTPointTargetAnalysisCorrectionsConf,
) -> tuple[np.ndarray | None, tuple[np.ndarray, np.ndarray] | None]:
    """Compute atmospheric delays"""
    if config.enable_ionospheric_correction and config.ionosphere is None:
        sct_logger.critical(
            "Ionospheric perturbation computation requested but the ionosphere configuration is missing"
        )
        raise RuntimeError("Invalid ionospheric configuration")

    if config.enable_tropospheric_correction and config.troposphere is None:
        sct_logger.critical(
            "Tropospheric perturbation computation requested but the troposhere configuration is missing"
        )
        raise RuntimeError("Invalid tropospheric configuration")

    ionosphere_input = None
    if config.enable_ionospheric_correction:
        assert config.ionosphere is not None
        ionosphere_input = IonosphericInput(
            analysis_center=config.ionosphere.analysis_center,
            incidence_angle_method=config.ionosphere.tec_incidence_angle_method,
            map_dir=config.ionosphere.maps_directory,
        )

    troposphere_input = None
    if config.enable_tropospheric_correction:
        assert config.troposphere
        troposphere_input = TroposphereInput(
            maps_directory=config.troposphere.maps_directory,
            maps_resolution=config.troposphere.map_grid_resolution,
        )

    # atmospheric delays for each point target
    return compute_atmospheric_delays(
        target_coords=target_coords,
        trajectory=acquisition_info.trajectory,
        az_time=acquisition_info.azimuth_time,
        fc_hz=acquisition_info.carrier_frequency,
        ionosphere_input=ionosphere_input,
        troposphere_input=troposphere_input,
    )


def convert_atmospheric_delays_to_df(
    target_names: pd.Series, delays: tuple[np.ndarray | None, tuple[np.ndarray, np.ndarray] | None]
) -> pd.DataFrame:
    """Converting atmospheric delays in a pandas dataframe correlating each delay to its own point targe id.

    Parameters
    ----------
    target_names : pd.Series
        target ids
    delays : tuple[np.ndarray | None, tuple[np.ndarray, np.ndarray] | None]
        atmospheric delays, ionospheric[0] and tropospheric[1] (both hyd and wet)

    Returns
    -------
    pd.DataFrame
        dataframe of atmospheric delays for each point target
    """
    df = target_names.to_frame()
    if delays[0] is not None:
        df["ionospheric_delay_range_correction_[m]"] = delays[0]
    else:
        df["ionospheric_delay_range_correction_[m]"] = np.nan
    if delays[1] is not None:
        df["tropospheric_delay_hydrostatic_range_correction_[m]"] = delays[1][0]
        df["tropospheric_delay_wet_range_correction_[m]"] = delays[1][1]
    else:
        df["tropospheric_delay_hydrostatic_range_correction_[m]"] = np.nan
        df["tropospheric_delay_wet_range_correction_[m]"] = np.nan

    return df
