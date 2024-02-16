# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Global corrections: Geodynamics, Atmospheric and ETAD
-----------------------------------------------------
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from arepyextras.perturbations.atmospheric import ionosphere, troposphere
from arepyextras.perturbations.geodynamics import plate_tectonics, solid_tides
from arepytools.geometry.curve_protocols import TwiceDifferentiable3DCurve
from arepytools.geometry.inverse_geocoding_core import inverse_geocoding_monostatic_core
from arepytools.timing.precisedatetime import PreciseDateTime
from s1etad import ECorrectionType, Sentinel1Etad, Sentinel1EtadBurst
from scipy.interpolate import interp2d
from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import Point

SECONDS_IN_A_YEAR = 3.154e7

# syncing with logger
log = logging.getLogger("quality_analysis")

# due to s1etad use of deprecated shapely function
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)


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

        if isinstance(plate_ref, str):
            plate_ref = plate_tectonics.ITRF2014PlatesRotationPoles[plate_ref.upper()]

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
    These corrections are to be applied only in range direction.

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
    if delays[0] is not None:
        df["ionospheric_delay_range_correction_[m]"] = delays[0]
    else:
        df["ionospheric_delay_range_correction_[m]"] = np.nan
    if delays[1] is not None:
        df["tropospheric_delay_hydrostatic_range_correction_[m]"] = -delays[1][0]
        df["tropospheric_delay_wet_range_correction_[m]"] = -delays[1][1]
    else:
        df["tropospheric_delay_hydrostatic_range_correction_[m]"] = np.nan
        df["tropospheric_delay_wet_range_correction_[m]"] = np.nan

    return df


def get_etad_corrections(etad_product_path: Union[str, Path], target_df: pd.DataFrame) -> pd.DataFrame:
    """Retrieving range ALE correction from ETAD product for all point targets.

    Parameters
    ----------
    etad_product_path : Union[str, Path]
        path to the ETAD product
    target_df : pd.DataFrame
        point target dataframe

    Returns
    -------
    pd.DataFrame
        corrections dataframe
    """

    # opening ETAD product
    etad = Sentinel1Etad(etad_product_path)

    corrections = []
    for _, row in target_df.iterrows():
        # creating a Point instance for the current cor
        cr_point = Point(row["longitude_deg"], row["latitude_deg"], row["altitude_m"])
        cr_burst_location = etad.query_burst(geometry=cr_point)
        if cr_burst_location.empty:
            continue

        total_rng_correction, total_az_correction = _extract_etad_correction(
            burst=next(etad.iter_bursts(cr_burst_location)), location=cr_point
        )

        corrections.append(
            {
                "target_name": row["target_name"],
                "etad_range_correction_[m]": total_rng_correction,
                "etad_azimuth_correction_[m]": total_az_correction,
            }
        )

    return pd.DataFrame(corrections)


def _extract_etad_correction(burst: Sentinel1EtadBurst, location: Point) -> tuple[float, float]:
    """Extracting ALE range correction from ETAD product for a given point target location.

    Parameters
    ----------
    burst : Sentinel1EtadBurst
        burst where the target lies
    location : Point
        location of the target

    Returns
    -------
    float
        range ALE correction in meters
    """
    # get SAR times at which it is seen in the scene
    tau0, t0 = burst.geodetic_to_radar(location.y, location.x, location.z)
    # retrieving sum of all corrections along range direction
    correction = burst.get_correction(ECorrectionType.SUM, meter=True)
    rng_corrections = correction["x"]
    az_corrections = correction["y"]

    # interpolating values at given target time coordinates
    azimuth_time, range_time = burst.get_burst_grid()
    interpolator_rng = interp2d(range_time, azimuth_time, rng_corrections)
    interpolator_az = interp2d(range_time, azimuth_time, az_corrections)

    return interpolator_rng(tau0, t0)[0], interpolator_az(tau0, t0)[0]
