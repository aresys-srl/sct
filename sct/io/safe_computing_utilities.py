# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SAFE product computing support"""

from typing import Union

import numpy as np
from arepyextras.eo_products.safe.l1_products.utilities import S1AcquisitionMode
from arepytools.constants import LIGHT_SPEED
from arepytools.timing.precisedatetime import PreciseDateTime


def compute_doppler_shift_correction(
    pulse_rate: Union[float, np.ndarray], squint_frequency: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Compute doppler shift correction that affects ALE along range direction.

    Parameters
    ----------
    pulse_rate : Union[float, np.ndarray]
        signal pulse rate as signal bandwidth divided by pulse length, float or array
    squint_frequency : float
        squint frequency in Hz, float or array

    Returns
    -------
    float
        doppler shift correction in meters
    """

    # compute range corrections: doppler shift correction
    doppler_shift = squint_frequency / pulse_rate
    doppler_shift_correction = doppler_shift * LIGHT_SPEED / 2

    return doppler_shift_correction


def compute_fmrate_shift_correction(
    ground_velocity: float, doppler_frequency: float, doppler_rate: np.ndarray, doppler_rate_th: np.ndarray
) -> float:
    """Compute FM rate shift correction.

    Parameters
    ----------
    ground_velocity : float
        sensor ground velocity
    doppler_frequency : float
        doppler frequency in Hz
    doppler_rate : np.ndarray
        doppler rate
    doppler_rate_th : np.ndarray
        doppler rate theoretical

    Returns
    -------
    float
        FM rate shift correction in meters
    """

    fmrate_shift = -doppler_frequency * (-1 / doppler_rate + 1 / doppler_rate_th)
    return fmrate_shift * ground_velocity


def compute_instrument_timing_correction(
    ground_velocity: float, azimuth_time: PreciseDateTime, swst_changes: list, pulse_latch_time: float
) -> float:
    """Compute instrument timing correction.

    Parameters
    ----------
    ground_velocity : float
        sensor ground velocity
    azimuth_time : PreciseDateTime
        azimuth time when to compute the timing correction
    swst_changes : list
        swst changes list
    pulse_latch_time : float
        tx pulse latch time

    Returns
    -------
    float
        instrument timing correction in meters
    """
    swst_times = np.array([t[0] for t in swst_changes])
    swst_values = [t[1] for t in swst_changes]
    # taking the change time that is closest to the input azimuth time and that is before that time
    selected_change_time_idx = np.ma.masked_less(np.abs(azimuth_time - swst_times).astype(float), 0).argmin()

    instrument_timing = swst_values[selected_change_time_idx] + pulse_latch_time
    return instrument_timing * ground_velocity


def compute_mid_swath_index(acquisition_mode: S1AcquisitionMode) -> int:
    """Compute mid-swath index from acquisition mode.

    Parameters
    ----------
    acquisition_mode : S1AcquisitionMode
        sensor acquisition mode

    Returns
    -------
    int
        mid-swath index
    """
    if acquisition_mode == S1AcquisitionMode.IW:
        return 1
    if acquisition_mode == S1AcquisitionMode.EW:
        return 2
    if acquisition_mode in (S1AcquisitionMode.SM, S1AcquisitionMode.WV):
        # for SM and WV the mid-swath index is the current swath
        return -1


def compute_real_bistatic_delay_correction(
    ground_velocity: float, range_time: float, bistatic_delay_applied: float, burst_start_time: float
) -> float:
    """Compute the correct bistatic delay for the current point.
    Processor computed bistatic delay (bistatic_delay_applied) is removed and the properly evaluated delay is then
    added. Delay is computed as:

    .. math::

        \\frac{\\tau_0 - \\Delta \\tau}{2}

    Parameters
    ----------
    ground_velocity : float
        ground velocity
    range_time : float
        range time of the point of interest
    bistatic_delay_applied : float
        bistatic delay already applied by the processor, to be removed and substituted with correct one
    burst_start_time : float
        start time of the burst where the point of interest belongs to

    Returns
    -------
    float
        bistatic delay correction in meters
    """
    delta_tau = range_time - burst_start_time
    bistatic_delay = -bistatic_delay_applied + (burst_start_time - delta_tau) / 2
    return -bistatic_delay * ground_velocity
