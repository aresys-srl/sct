# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Main entry point for geodynamics corrections
--------------------------------------------
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.configuration.sct_configuration import SCTPointTargetAnalysisConfig
from sct.core.geodynamics_corrections_core import PlateTectonicsInput, SolidTidesInput, compute_geodynamics_corrections

# syncing with logger
log = logging.getLogger("quality_analysis")


def run_compute_geodynamics_corrections(
    nominal_target_coords: np.ndarray,
    acquisition_time: PreciseDateTime,
    point_targets_df: pd.DataFrame,
    config: SCTPointTargetAnalysisConfig,
) -> np.ndarray | None:
    """Compute geodynamics corrections"""
    # checking if acquisition time lies within point target data time validity boundaries

    plate_tectonics_input = None
    if config.enable_plate_tectonics_correction:
        try:

            def _to_pdt(date: pd.Series) -> PreciseDateTime:
                return PreciseDateTime.fromisoformat(date.mode()[0].isoformat())

            date_lower_boundary = _to_pdt(point_targets_df["validity_start_date"])
            date_upper_boundary = _to_pdt(point_targets_df["validity_stop_date"])

            if not date_lower_boundary <= acquisition_time <= date_upper_boundary:
                raise RuntimeError(
                    f"Acquisition time {acquisition_time} date is "
                    + f"outside of validity boundaries: [{date_lower_boundary},{date_upper_boundary}]"
                )

            # computing time delta between acquisition time and calibration site measurement campaign date
            time_delta_s = acquisition_time - _to_pdt(point_targets_df["measurement_date"])

        except KeyError as err:
            log.critical("Missing time validity required information in input point targets")
            raise RuntimeError(
                "Cannot apply Plate Tectonics correction: disable this feature from configuration or "
                + "add validity dates to point targets data"
            ) from err

        drift_vel = ["drift_velocity_x_my", "drift_velocity_y_my", "drift_velocity_z_my"]
        drift_velocities = None
        if set(drift_vel).issubset(point_targets_df.columns):
            drift_velocities = point_targets_df[drift_vel].to_numpy()

        plate_tectonics_input = PlateTectonicsInput(
            time_delta_s=time_delta_s, drift_velocities=drift_velocities, plate_ref=point_targets_df.plate[0]
        )

    solid_tides_input = SolidTidesInput(time=acquisition_time) if config.enable_solid_tides_correction else None

    return compute_geodynamics_corrections(
        target_coords=nominal_target_coords,
        solid_tides_input=solid_tides_input,
        plate_tectonics_input=plate_tectonics_input,
    )
