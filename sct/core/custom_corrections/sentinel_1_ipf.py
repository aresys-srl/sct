# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Custom Corrections: Sentinel-1 IPF range and azimuth corrections
----------------------------------------------------------------
"""

import numpy as np
import pandas as pd
from arepytools.timing.precisedatetime import PreciseDateTime

import sct.io.safe_computing_utilities as s1_corrections
from sct.io.extended_protocols import SCTInputProduct


def _detect_mid_swath_channel(subswaths: list[str]) -> str:
    """Detecting the mid swath channel name. For Sentinel-1, only IW and EW
    acquisition modes have multiple sub-swaths. For them, the middle sub-swaths
    are IW2 and EW3, respectively. All other modes have a single swath.

    Parameters
    ----------
    times : list[str]
        list with values being the sub-swath names

    Returns
    -------
    str
        mid-swath name
    """
    swath_names = sorted(subswaths)
    if swath_names == ["IW1", "IW2", "IW3"]:
        return "IW2"
    if swath_names == ["EW1", "EW2", "EW3", "EW4", "EW5"]:
        return "EW3"
    assert len(swath_names) == 1
    return swath_names[0]


def _get_rid_of_pol_dependency(arg: dict[str, dict[str, tuple[PreciseDateTime, float]]]) -> dict[str, PreciseDateTime]:
    """Removing polarization dependency from the input dictionary by selecting only the minimum start time.

    Parameters
    ----------
    arg : dict[str, dict[str, tuple[PreciseDateTime, float]]]
        dictionary with keys being the swath id and values being dictionaries of polarizations as keys and azimuth
        and range mid burst times as values

    Returns
    -------
    dict[str, PreciseDateTime]
        dictionary of swath id as keys and azimuth start times as values, one value for each key
    """
    arg = arg.copy()
    for key, val in arg.items():
        vals = list(val.values())
        arg[key] = vals[np.argmin([v[0] for v in val.values()])]

    return arg


def compute_range_corrections(
    product: SCTInputProduct,
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Computing Sentinel-1 specific range corrections for ALE measurements.
    In this case, the only range correction is Doppler Shift.

    Parameters
    ----------
    product : SCTInputProduct
        product
    data : pd.DataFrame
        point target analysis data

    Returns
    -------
    pd.DataFrame
        dataframe with doppler shift range correction
    """
    # retrieving pulse rates for each channel
    pulse_rates = dict.fromkeys(product.channels_list)
    for ch_id in product.channels_list:
        channel_data = product.get_channel_data(channel_id=ch_id)
        pulse_rates[ch_id] = channel_data.pulse_rate

    # computing range corrections
    rng_corr = []
    for _, row in data.iterrows():
        rng_corr.append(
            (
                row["id"],
                s1_corrections.compute_doppler_shift_correction(
                    pulse_rate=pulse_rates[row["channel"]], squint_frequency=row["total_doppler_frequency_[Hz]"]
                ),
            )
        )

    return pd.DataFrame(rng_corr, columns=["id", "doppler_shift_range_correction_[m]"])


def compute_azimuth_corrections(
    product: SCTInputProduct,
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Computing Sentinel-1 specific azimuth corrections for ALE measurements.
    FM rate shift, instrument timing and bistatic delay corrections are computed.

    Parameters
    ----------
    product : SCTInputProduct
        product
    data : pd.DataFrame
        point target analysis data

    Returns
    -------
    pd.DataFrame
        dataframe with fm rate shift, instrument timing and bistatic delay correction
    """

    swst_changes = dict.fromkeys(product.channels_list)
    pulse_latch_times = swst_changes.copy()
    subswath_mid_first_burst_times = {}
    burst_start_times = swst_changes.copy()

    # retrieving swst changes for each channel and detecting the mid swath for the current product
    for ch_id in product.channels_list:
        channel_data = product.get_channel_data(channel_id=ch_id)
        swst_changes[ch_id] = channel_data.swst_changes
        pulse_latch_times[ch_id] = channel_data.pulse_latch_time
        if channel_data._channel.burst_info.num > 0:
            burst_start_times[ch_id] = channel_data._channel.burst_info.range_start_times
        else:
            burst_start_times[ch_id] = channel_data._channel.raster_info.samples_start
        if channel_data.swath_name not in subswath_mid_first_burst_times:
            subswath_mid_first_burst_times[channel_data.swath_name] = {}
        if channel_data.polarization.value not in subswath_mid_first_burst_times[channel_data.swath_name]:
            subswath_mid_first_burst_times[channel_data.swath_name][channel_data.polarization.value] = (
                channel_data.get_mid_burst_times(0)
            )

    subswath_mid_first_burst_times = _get_rid_of_pol_dependency(subswath_mid_first_burst_times)
    mid_swath_channel_id = _detect_mid_swath_channel(subswaths=list(subswath_mid_first_burst_times.keys()))
    bistatic_delay_applied = subswath_mid_first_burst_times[mid_swath_channel_id][1] / 2

    # computing azimuth corrections
    fm_rate_shift = []
    instrument_timing = []
    bistatic_delay = []
    for _, row in data.iterrows():
        try:
            fm_rate_shift.append(
                (
                    row["id"],
                    s1_corrections.compute_fmrate_shift_correction(
                        ground_velocity=row["ground_velocity_[ms]"],
                        doppler_frequency=row["total_doppler_frequency_[Hz]"],
                        doppler_rate_processor=row["doppler_rate_real_[Hzs]"],
                        doppler_rate_geometry=row["doppler_rate_theoretical_[Hzs]"],
                    ),
                )
            )

        except (ValueError, TypeError):
            fm_rate_shift.append((row["id"], np.nan))

        try:
            instrument_timing.append(
                (
                    row["id"],
                    s1_corrections.compute_instrument_timing_correction(
                        ground_velocity=row["ground_velocity_[ms]"],
                        azimuth_time=row["peak_azimuth_time_[UTC]"],
                        pulse_latch_time=pulse_latch_times[row["channel"]],
                        swst_changes=swst_changes[row["channel"]],
                    ),
                )
            )

        except (ValueError, TypeError):
            instrument_timing.append((row["id"], np.nan))

        try:
            bistatic_delay.append(
                (
                    row["id"],
                    s1_corrections.compute_real_bistatic_delay_correction(
                        ground_velocity=row["ground_velocity_[ms]"],
                        range_time=row["peak_range_time_[s]"],
                        bistatic_delay_applied=bistatic_delay_applied,
                        burst_start_time=burst_start_times[row["channel"]][row["burst"]],
                    ),
                )
            )

        except (ValueError, TypeError):
            bistatic_delay.append((row["id"], np.nan))

    # converting output to dataframe
    fm_rate_shift = pd.DataFrame(fm_rate_shift, columns=["id", "fm_rate_shift_azimuth_correction_[m]"])
    instrument_timing = pd.DataFrame(instrument_timing, columns=["id", "instrument_timing_azimuth_correction_[m]"])
    bistatic_delay = pd.DataFrame(bistatic_delay, columns=["id", "bistatic_delay_azimuth_correction_[m]"])
    az_corrections = fm_rate_shift.merge(instrument_timing, on="id").merge(bistatic_delay, on="id")

    return az_corrections
