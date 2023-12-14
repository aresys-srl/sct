# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Global corrections: Geodynamics and Atmospheric
-----------------------------------------------
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from arepyextras.perturbations.atmospheric import ionosphere, troposphere
from arepyextras.perturbations.geodynamics import plate_tectonics, solid_tides
from arepytools.geometry.curve_protocols import TwiceDifferentiable3DCurve
from arepytools.geometry.inverse_geocoding_core import inverse_geocoding_monostatic_core
from arepytools.timing.precisedatetime import PreciseDateTime

SECONDS_IN_A_YEAR = 3.154e7

# syncing with logger
log = logging.getLogger("quality_analysis")


def compute_geodynamics_corrections(
    target_coords: np.ndarray,
    drift_velocities: np.ndarray | None,
    acq_time: PreciseDateTime,
    time_delta_s: float,
    plate_ref: Union[str, plate_tectonics.ITRF2014PlatesRotationPoles],
    tides_flag: bool,
    tectonics_flag: bool,
) -> Union[np.ndarray, None]:
    """Geophysics corrections management: computing solid tides and plate tectonic displacements of input coordinates.

    Parameters
    ----------
    target_coords : np.ndarray
        input coordinates xyz, in the form (3,) or (N, 3)
    drift_velocities : np.ndarray | None
        drift velocities for x, y and z, same shape as target_coords
    acq_time : PreciseDateTime
        acquisition time at which compute the displacement (solid tides)
    time_delta_s : float
        time interval in seconds from which compute the displacement (plate tectonics)
    plate_ref : Union[str, plate_tectonics.ITRF2014PlatesRotationPoles]
        reference plate for input coordinates
    tides_flag : bool
        enabling flag to perform solid tides displacement computation
    tectonics_flag : bool
        enabling flag to perform plate tectonics displacement computation

    Returns
    -------
    Union[np.ndarray, None]
        overall coordinates displacement array, None if both flags where False
    """

    if isinstance(plate_ref, str):
        plate_ref = plate_tectonics.ITRF2014PlatesRotationPoles[plate_ref.upper()]

    coords_displacements = []
    if tides_flag:
        # computing solid tides corrections
        log.info("Computing Solid Tides displacement correction for calibration site coordinates")
        coords_displacements.append(
            solid_tides.compute_displacement(
                target_xyz_coords=target_coords,
                acquisition_time=acq_time,
            )
        )

    if tectonics_flag:
        # computing plate tectonics corrections
        log.info("Computing Plate Tectonics displacement correction for calibration site coordinates")

        # velocities are expressed in meters per year, so the time_delta should be computed in terms of years
        time_delta_y = time_delta_s / SECONDS_IN_A_YEAR

        # if drift velocities are provided for the calibration targets in use, those must be used to
        # compute the displacement due to plate tectonics movements
        if drift_velocities is not None:
            if np.isnan(drift_velocities).all():
                log.info("Drift velocities not provided for the selected calibration site")
                log.info("Computing Plate Tectonics displacement correction using average plate drift velocities")
                drift_velocities = None

        coords_displacements.append(
            plate_tectonics.compute_displacement(
                xyz_coords=target_coords,
                plate_ref=plate_ref,
                time_delta=time_delta_y,
                drift_vel=drift_velocities,
            )
        )

    # summing computed displacements arrays
    if coords_displacements:
        return sum(coords_displacements)

    return None


def compute_atmospheric_delays(
    target_coords: np.ndarray,
    trajectory: TwiceDifferentiable3DCurve,
    az_time: PreciseDateTime,
    fc_hz: float,
    analysis_center: ionosphere.IonosphericAnalysisCenters,
    ionosphere_incidence_angle_method: ionosphere.TECMappingFunctionIncidenceAngleMethod,
    troposphere_map_resolution: troposphere.TroposphericGRIDResolution,
    ionosphere_flag: bool,
    ionosphere_map_dir: Path,
    troposphere_flag: bool,
    troposphere_map_dir: Path,
) -> list[Union[np.ndarray, None]]:
    """Atmospheric corrections management: computing ionospheric and tropospheric delays displacements from maps.

    Parameters
    ----------
    target_coords : np.ndarray
        input coordinates xyz, in the form (3,) or (N, 3)
    trajectory : TwiceDifferentiable3DCurve
        sensor trajectory
    az_time : PreciseDateTime
        azimuth time corresponding to the product acquisition time
    fc_hz : float
        signal carrier frequency
    analysis_center : ionosphere.IonosphericAnalysisCenters
        ionospheric maps analysis center
    ionosphere_incidence_angle_method : ionosphere.TECMappingFunctionIncidenceAngleMethod
        pierce point incidence angle computing method
    troposphere_map_resolution : troposphere.TroposphericGRIDResolution
        tropospheric maps resolution
    ionosphere_flag : bool
        enabling flag for computing ionosphere corrections
    ionosphere_map_dir : Path
        path to ionospheric maps directory
    troposphere_flag : bool
        enabling flag for computing tropospheric corrections
    troposphere_map_dir : Path
        path to tropospheric maps directory

    Returns
    -------
    list[Union[np.ndarray, None]]
        ionospheric delay,
        tropospheric hydrostatic and wet delays
    """
    delays = [None, None]

    if ionosphere_flag or troposphere_flag:
        # computing sensor position at which the ground point targets are seen
        az_times, _ = inverse_geocoding_monostatic_core(
            trajectory=trajectory,
            ground_points=target_coords,
            initial_guesses=az_time,
            frequencies_doppler_centroid=0,
            wavelength=1,
        )
        sat_pos = trajectory.evaluate(az_times)

    if ionosphere_flag:
        # estimating ionospheric delay corrections
        delays[0] = ionosphere.compute_delay(
            acq_time=az_time,
            targets_xyz_coords=target_coords,
            sat_xyz_coords=sat_pos,
            analysis_center=analysis_center,
            fc_hz=fc_hz,
            map_folder=ionosphere_map_dir,
            tec_mapping_method=ionosphere_incidence_angle_method,
        )
        delays[0] *= -1

    if troposphere_flag:
        # estimating tropospheric delay corrections
        delays[1] = troposphere.compute_delay(
            acq_time=az_time,
            targets_xyz_coords=target_coords,
            sat_xyz_coords=sat_pos,
            map_folder=troposphere_map_dir,
            map_resolution=troposphere_map_resolution,
        )

    return delays


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
    df["ionospheric_delay_[m]"] = delays[0]
    if delays[1] is not None:
        df["tropospheric_delay_hydrostatic_[m]"] = -delays[1][0]
        df["tropospheric_delay_wet_[m]"] = -delays[1][1]
    else:
        df["tropospheric_delay_hydrostatic_[m]"] = None
        df["tropospheric_delay_wet_[m]"] = None

    return df
