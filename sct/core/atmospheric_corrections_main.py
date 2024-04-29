# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Main entry point for atmospheric corrections
--------------------------------------------
"""
import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from arepyextras.quality.io.quality_input_protocol import TwiceDifferentiable3DCurve
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.configuration.sct_configuration import SCTPointTargetAnalysisConfig
from sct.core.atmospheric_corrections_core import IonosphericInput, TroposphereInput, compute_atmospheric_delays

# syncing with logger
log = logging.getLogger("quality_analysis")


@dataclass
class AtmosphericDelaysAcquisitionInfo:
    """Acquisition information required for computing atmospheric delays"""

    trajectory: TwiceDifferentiable3DCurve
    azimuth_time: PreciseDateTime
    carrier_frequency: float


def run_compute_atmospheric_delays(
    target_coords: np.ndarray,
    acquisition_info: AtmosphericDelaysAcquisitionInfo,
    config: SCTPointTargetAnalysisConfig,
) -> tuple[np.ndarray | None, tuple[np.ndarray, np.ndarray] | None]:
    """Compute atmospheric delays"""
    if config.enable_ionospheric_correction and config.ionospheric_maps_directory is None:
        log.critical("Ionospheric perturbation computation requested but the maps directory is not valid")
        raise RuntimeError("Invalid ionospheric maps directory")

    if config.enable_tropospheric_correction and config.tropospheric_maps_directory is None:
        log.critical("Tropospheric perturbation computation requested but the maps directory is not valid")
        raise RuntimeError("Invalid tropospheric maps directory")

    ionosphere_input = None
    if config.enable_ionospheric_correction:
        assert config.ionospheric_analysis_center is not None
        assert config.ionospheric_maps_directory is not None
        ionosphere_input = IonosphericInput(
            analysis_center=config.ionospheric_analysis_center,
            incidence_angle_method=config.ionospheric_tec_inc_angle_method,
            map_dir=config.ionospheric_maps_directory,
        )

    troposphere_input = None
    if config.enable_tropospheric_correction:
        assert config.tropospheric_maps_directory
        assert config.tropospheric_map_grid_resolution
        troposphere_input = TroposphereInput(
            maps_directory=config.tropospheric_maps_directory, maps_resolution=config.tropospheric_map_grid_resolution
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
