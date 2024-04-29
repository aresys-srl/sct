# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Geodynamics corrections core functions
--------------------------------------
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from arepyextras.perturbations.geodynamics import plate_tectonics, solid_tides
from arepytools.timing.precisedatetime import PreciseDateTime

SECONDS_IN_A_YEAR = 3.154e7

# syncing with logger
log = logging.getLogger("quality_analysis")


@dataclass
class SolidTidesInput:
    """Inputs to compute solid tides displacement"""

    time: PreciseDateTime
    """acquisition time at which compute the displacement"""


@dataclass
class PlateTectonicsInput:
    """Inputs to compute plate tectonics displacement"""

    time_delta_s: float
    """elapsed time [seconds] since input target positions were measured"""

    drift_velocities: np.ndarray | None
    """drift velocities for x, y and z, same shape as target_coords"""

    plate_ref: str | plate_tectonics.ITRF2014PlatesRotationPoles
    """reference plate for input coordinates"""


def compute_geodynamics_corrections(
    target_coords: np.ndarray,
    solid_tides_input: SolidTidesInput | None,
    plate_tectonics_input: PlateTectonicsInput | None,
) -> np.ndarray | None:
    """Geophysics corrections management: computing solid tides and/or plate tectonic displacements of input coordinates.

    Parameters
    ----------
    target_coords : np.ndarray
        input coordinates xyz, in the form (3,) or (N, 3)
    solid_tides_input : SolidTidesInput, optional
        information required to compute solid tides displacement. Displacements are computed only if provided.
    plate_tectonics_input : PlateTectonicsInput, optional
        information required to plate tectonics displacement. Displacements are computed only if provided.

    Returns
    -------
    np.ndarray | None
        overall coordinates displacement array or None if both displacements were not required
    """
    if not solid_tides_input and not plate_tectonics_input:
        return None

    tides_displacement = None
    if solid_tides_input:
        log.info("Computing Solid Tides displacement correction for calibration site coordinates")
        tides_displacement = solid_tides.compute_displacement(
            target_xyz_coords=target_coords,
            acquisition_time=solid_tides_input.time,
        )

    tectonics_displacement = None
    if plate_tectonics_input:
        log.info("Computing Plate Tectonics displacement correction for calibration site coordinates")

        # velocities are expressed in meters per year, so the time_delta should be computed in terms of years
        time_delta_y = plate_tectonics_input.time_delta_s / SECONDS_IN_A_YEAR

        # if drift velocities are provided for the calibration targets in use, those must be used to
        # compute the displacement due to plate tectonics movements
        drift_velocities_available = (
            plate_tectonics_input.drift_velocities is not None
            and not np.isnan(plate_tectonics_input.drift_velocities).all()
        )
        if drift_velocities_available:
            drift_velocities = plate_tectonics_input.drift_velocities
        else:
            log.info("Drift velocities not provided for the selected calibration site")
            log.info("Computing Plate Tectonics displacement correction using average plate drift velocities")
            drift_velocities = None

        tectonics_displacement = plate_tectonics.compute_displacement(
            xyz_coords=target_coords,
            plate_ref=plate_tectonics_input.plate_ref,
            time_delta=time_delta_y,
            drift_vel=drift_velocities,
        )

    total_displacement = tides_displacement if tides_displacement is not None else 0.0
    total_displacement += tectonics_displacement if tectonics_displacement is not None else 0.0
    assert isinstance(total_displacement, np.ndarray)
    return total_displacement
