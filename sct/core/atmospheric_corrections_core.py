# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Atmospheric corrections core functions
--------------------------------------
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from arepyextras.perturbations.atmospheric import ionosphere, troposphere
from arepytools.geometry.curve_protocols import TwiceDifferentiable3DCurve
from arepytools.geometry.inverse_geocoding_core import inverse_geocoding_monostatic_core
from arepytools.timing.precisedatetime import PreciseDateTime

# syncing with logger
log = logging.getLogger("quality_analysis")


@dataclass
class IonosphericInput:
    """Input for ionospheric delay computation"""

    analysis_center: ionosphere.IonosphericAnalysisCenters
    """ionospheric maps analysis center"""

    incidence_angle_method: ionosphere.TECMappingFunctionIncidenceAngleMethod
    """pierce point incidence angle computing method"""

    map_dir: Path
    """path to ionospheric maps directory"""


@dataclass
class TroposphereInput:
    """Input for tropospheric delay computation"""

    maps_resolution: troposphere.TroposphericGRIDResolution
    """tropospheric maps resolution"""

    maps_directory: Path
    """path to tropospheric maps directory"""


def compute_atmospheric_delays(
    target_coords: np.ndarray,
    trajectory: TwiceDifferentiable3DCurve,
    az_time: PreciseDateTime,
    fc_hz: float,
    ionosphere_input: IonosphericInput | None,
    troposphere_input: TroposphereInput | None,
) -> tuple[np.ndarray | None, tuple[np.ndarray, np.ndarray] | None]:
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
    ionosphere_input: IonosphericInput | None
        trigger ionospheric delay computation if provided
    troposphere_input: TroposphereInput | None
        trigger tropospheric delay computation if provided

    Returns
    -------
    tuple[np.ndarray | None, tuple[np.ndarray, np.ndarray] | None]
        ionospheric delay,
        tropospheric hydrostatic and wet delays
    """
    if not ionosphere_input and not troposphere_input:
        return None, None

    assert ionosphere_input or troposphere_input

    # computing sensor position at which the ground point targets are seen
    az_times, _ = inverse_geocoding_monostatic_core(
        trajectory=trajectory,
        ground_points=target_coords,
        initial_guesses=az_time,
        frequencies_doppler_centroid=0,
        wavelength=1,
    )
    sat_pos = trajectory.evaluate(az_times)

    ionospheric_delay: np.ndarray | None = None
    if ionosphere_input:
        ionospheric_delay = ionosphere.compute_delay(
            acq_time=az_time,
            targets_xyz_coords=target_coords,
            sat_xyz_coords=sat_pos,
            analysis_center=ionosphere_input.analysis_center,
            fc_hz=fc_hz,
            map_folder=ionosphere_input.map_dir,
            tec_mapping_method=ionosphere_input.incidence_angle_method,
        )

    tropospheric_delay: tuple[np.ndarray, np.ndarray] | None = None
    if troposphere_input:
        tropospheric_delay = troposphere.compute_delay(
            acq_time=az_time,
            targets_xyz_coords=target_coords,
            sat_xyz_coords=sat_pos,
            map_folder=troposphere_input.maps_directory,
            map_resolution=troposphere_input.maps_resolution,
        )

    return ionospheric_delay, tropospheric_delay
