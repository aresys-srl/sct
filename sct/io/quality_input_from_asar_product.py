# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
ASAR format Arepyextras-Quality protocol-compliant wrapper
------------------------------------------------------------
"""

from __future__ import annotations

from itertools import product
from pathlib import Path

import numpy as np
from arepyextras.eo_products.asar.l1_products.reader import open_product, read_channel_data, read_channel_metadata
from arepyextras.quality.core.custom_errors import (
    AzimuthExceedsBoundariesError,
    CoordinatesOutOfBounds,
    RangeExceedsBoundariesError,
)
from arepyextras.quality.core.generic_dataclasses import (
    LocationData,
    SARImageType,
    SAROrbitDirection,
    SARPolarization,
    SARProjection,
    SARRadiometricQuantity,
    SARSamplingFrequencies,
    SARSideLooking,
)
from arepyextras.quality.core.signal_processing import radiometric_correction
from arepytools.constants import LIGHT_SPEED
from arepytools.geometry.geometric_functions import (
    compute_ground_velocity_from_trajectory,
    compute_incidence_angles_from_trajectory,
    compute_look_angles_from_trajectory,
)
from arepytools.geometry.inverse_geocoding_core import inverse_geocoding_monostatic_core
from arepytools.geometry.orbit import Orbit
from arepytools.math.genericpoly import SortedPolyList
from arepytools.timing.precisedatetime import PreciseDateTime
from numpy.typing import ArrayLike
from shapely import Polygon


class ASARDopplerPolynomial:
    """ASAR doppler polynomial wrapper compliant with Arepyextras-quality Coordinate Conversion Function protocol"""

    def __init__(self, sorted_poly: SortedPolyList) -> None:
        self._sorted_poly = sorted_poly

    def evaluate(self, azimuth_time: PreciseDateTime, range_time: float) -> float:
        """Evaluate the Doppler Polynomial at given azimuth and range times.

        Parameters
        ----------
        azimuth_time : PreciseDateTime
            azimuth time at which evaluate the polynomial
        range_time : float
            range time at which evaluate the polynomial

        Returns
        -------
        float
            doppler centroid at that time
        """
        return self._sorted_poly.evaluate((azimuth_time, range_time))


class ASARProductManager:
    """SCTInputProduct protocol compliant ASAR wrapper"""

    def __init__(self, path: str | Path, **kwargs) -> None:
        self._path = Path(path)
        self._name = self._path.name
        self._product = open_product(path)
        region_corners = list(product(self._product.footprint[:2], self._product.footprint[2:]))
        self._footprint = Polygon(region_corners)

    @property
    def path(self) -> Path:
        """Get product path"""
        return self._path

    @property
    def name(self) -> str:
        """Get product name"""
        return self._name

    @property
    def footprint(self) -> Polygon:
        """Get product footprint"""
        return self._footprint

    @property
    def channels_list(self) -> list[str]:
        """Get list of available channels for this product"""
        return self._product.channels_list

    def get_channel_data(self, channel_id: str) -> ASARChannelManager:
        """Gathering all the information that are channel dependent and storing them in a protocol compliant object.

        Parameters
        ----------
        channel_id : int
            selected channel identifier

        Returns
        -------
        ASARChannelManager
            ChannelData-compliant object containing data corresponding to the selected channel
        """
        return ASARChannelManager(product_path=self.path, channel_name=channel_id)


class ASARChannelManager:
    """Arepyextras-quality ChannelData protocol compliant SAOCOM channel wrapper"""

    def __init__(
        self,
        product_path: Path,
        channel_name: str,
    ) -> None:
        """Creating a ChannelManager object compliant with the ChannelData protocol.

        Parameters
        ----------
        channel_files : list[Path]
            files corresponding to the selected channel
        channel_name : str
            name of the current channel
        """

        self._channel_id = channel_name
        self._product_path = product_path
        self._channel = read_channel_metadata(file_path=self._product_path, channel_id=channel_name)

        # translating arepyextras.eo_products enum to arepyextras.quality ones
        self._radiometric_quantity = SARRadiometricQuantity[self._channel.image_radiometric_quantity.name]
        self._polarization = SARPolarization(self._channel.general_info.polarization.value)
        self._projection = SARProjection(self._channel.general_info.projection.value)
        self._orbit_direction = SAROrbitDirection[self._channel.general_info.orbit_direction.name]
        self._acquisition_mode = self._channel.general_info.acquisition_mode_std.name

        self._range_step_m = self._compute_range_step_m()
        self._image_type = self._channel.general_info.product_type
        self._looking_side = SARSideLooking(self._channel.dataset_info.side_looking.value.upper())

        # compute axes
        self._azimuth_axis = self._compute_azimuth_axis()
        self._az_time_half_swath = self._azimuth_axis[self._azimuth_axis.size // 2]
        self._range_axis = (
            np.arange(0, self._channel.raster_info.samples, 1) * self._channel.raster_info.samples_step
            + self._channel.raster_info.samples_start
        )
        self._slant_range_axis = self._compute_slant_range_axis()
        rng_time_half_swath = (
            self._channel.raster_info.samples_start
            + (self._channel.raster_info.samples - 1) * self._channel.raster_info.samples_step / 2
        )
        if self._projection == SARProjection.GROUND_RANGE:
            rng_time_half_swath = self._channel.coordinate_conversions.evaluate_ground_to_slant(
                azimuth_time=self._az_time_half_swath, ground_range=np.floor(rng_time_half_swath)
            )
        self._rng_time_half_swath = rng_time_half_swath

        # computing range_step_m
        self._az_step_s = self._channel.raster_info.lines_step
        self._range_step_m = self._compute_range_step_m()

        # lines per burst array
        if self._channel.burst_info.num > 0:
            self._lines_per_burst_array = np.repeat(
                self._channel.burst_info.lines_per_burst, self._channel.burst_info.num
            )
        else:
            # should be a 1D array
            self._lines_per_burst_array = np.repeat(self._channel.raster_info.lines, 1)

        # lines per burst array
        if self._channel.burst_info.num > 0:
            self._lines_per_burst_array = np.repeat(
                self._channel.burst_info.lines_per_burst, self._channel.burst_info.num
            )
        else:
            # should be a 1D array
            self._lines_per_burst_array = np.repeat(self._channel.raster_info.lines, 1)

        # pulse rate
        if self._channel.pulse is not None:
            self._signal_pulse_rate = self._channel.pulse.bandwidth / self._channel.pulse.pulse_length
        else:
            self._signal_pulse_rate = 1

        # prf
        self._prf = self._channel.swath_info.prf

        # steering rate
        self._steering_rate_poly_coeff = self._channel.swath_info.azimuth_steering_rate_poly

        # generating trajectory from orbit
        self._trajectory_rx = self._channel.orbit
        self._trajectory_tx = None

        # generating doppler centroid wrappers
        self._doppler_centroid_poly = ASARDopplerPolynomial(sorted_poly=self._channel.doppler_centroid_poly)
        self._doppler_rate_poly = ASARDopplerPolynomial(sorted_poly=self._channel.doppler_rate_poly)

        # re-organizing SWST changes
        # TODO: implement acquisition timeline, if needed
        self._swst_changes = [(0, 0)]

        # get burst boundaries
        self._burst_az_boundaries, self._burst_rng_boundaries = self._get_raster_layout()

    def _compute_range_step_m(self) -> float:
        """Computing step along range direction, in meters"""
        if self._projection == SARProjection.GROUND_RANGE:
            return self._channel.raster_info.samples_step

        return self._channel.raster_info.samples_step * LIGHT_SPEED / 2

    def _compute_slant_range_axis(self) -> np.ndarray:
        """Computing slant range full axis.

        Returns
        -------
        np.ndarray
            slant range axis
        """
        slant_rng_axis = self._range_axis
        if self._projection == SARProjection.GROUND_RANGE:
            slant_rng_axis = self._channel.coordinate_conversions.evaluate_ground_to_slant(
                azimuth_time=self._az_time_half_swath, ground_range=self._range_axis
            )

        return slant_rng_axis

    def _compute_azimuth_axis(self) -> np.ndarray:
        """Compute azimuth full axis.

        Returns
        -------
        np.ndarray
            azimuth axis
        """
        az_axis = (
            np.arange(0, self._channel.raster_info.lines, 1) * self._channel.raster_info.lines_step
            + self._channel.raster_info.lines_start
        )
        if self._channel.burst_info.num > 0:
            az_axis = []
            for brst in range(self._channel.burst_info.num):
                az_axis.append(
                    self._channel.burst_info.azimuth_start_times[brst]
                    + np.arange(0, self._channel.burst_info.lines_per_burst, 1) * self._channel.raster_info.lines_step
                )
            az_axis = np.concatenate(az_axis)
        return az_axis

    def _get_raster_layout(self) -> tuple[list[PreciseDateTime], list[float]]:
        """Evaluating raster boundaries taking into account the bursts, if needed.

        Returns
        -------
        tuple[list[list[PreciseDateTime, PreciseDateTime]], list[list[float, float]]]
            azimuth raster boundaries (azimuth start, azimuth stop),
            range raster boundaries (range start, range stop)
        """

        if self._channel.burst_info.num > 0:
            az_times = self._channel.burst_info.azimuth_start_times
            rng_times = np.repeat(self._channel.raster_info.samples_start, az_times.size)
            burst_az_boundaries = []
            for az_time in az_times:
                burst_az_boundaries.append(
                    [az_time, az_time + self._channel.burst_info.lines_per_burst * self._channel.raster_info.lines_step]
                )
            burst_rng_boundaries = []
            for rng_time in rng_times:
                burst_rng_boundaries.append(
                    [rng_time, rng_time + self._channel.raster_info.samples * self._channel.raster_info.samples_step]
                )
        else:
            burst_az_boundaries = [
                [
                    self._channel.raster_info.lines_start,
                    self._channel.raster_info.lines_start
                    + self._channel.raster_info.lines * self._channel.raster_info.lines_step,
                ]
            ]
            burst_rng_boundaries = [
                [
                    self._channel.raster_info.samples_start,
                    self._channel.raster_info.samples_start
                    + self._channel.raster_info.samples * self._channel.raster_info.samples_step,
                ]
            ]

        return burst_az_boundaries, burst_rng_boundaries

    @property
    def swath_name(self) -> str:
        """Name of the swath being analyzed"""
        return self._channel.general_info.swath

    @property
    def channel_id(self) -> str:
        """Identifier of current channel data"""
        return self._channel_id

    @property
    def prf(self) -> float:
        """Sensor Pulse Repetition Frequency (PRF)"""
        return self._prf

    @property
    def range_step_m(self) -> float:
        """Step along range direction, in meters"""
        return self._range_step_m

    @property
    def azimuth_step_s(self) -> float:
        """Step along azimuth direction, in seconds"""
        return self._channel.raster_info.lines_step

    @property
    def projection(self) -> SARProjection:
        """Channel data projection"""
        return self._projection

    @property
    def polarization(self) -> SARPolarization:
        """Channel data polarization"""
        return self._polarization

    @property
    def orbit_direction(self) -> SAROrbitDirection:
        """Channel data orbit direction"""
        return self._orbit_direction

    @property
    def image_type(self) -> SARImageType:
        """Channel raster image type"""
        return self._image_type

    @property
    def sampling_constants(self) -> SARSamplingFrequencies:
        """Channel data signal sampling frequencies"""
        return self._channel.sampling_constants

    @property
    def pulse_rate(self) -> float:
        """Signal pulse rate"""
        return self._signal_pulse_rate

    @property
    def looking_side(self) -> SARSideLooking:
        """Sensor look direction for this channel"""
        return self._looking_side

    @property
    def carrier_frequency(self) -> float:
        """Signal carrier frequency"""
        return self._channel.dataset_info.fc_hz

    @property
    def mid_azimuth_time(self) -> PreciseDateTime:
        """Azimuth time at half swath"""
        return self._az_time_half_swath

    @property
    def trajectory(self) -> Orbit:
        """Channel trajectory rx 3D curve"""
        return self._trajectory_rx

    @property
    def boresight_normal_curve(self) -> None:
        """Channel attitude boresight normal 3D curve"""
        return None

    @property
    def doppler_centroid(self) -> ASARDopplerPolynomial:
        """Channel doppler centroid polynomial wrapper"""
        return self._doppler_centroid_poly

    @property
    def doppler_rate(self) -> ASARDopplerPolynomial:
        """Channel doppler rate polynomial wrapper"""
        return self._doppler_rate_poly

    @property
    def mid_range_time(self) -> float:
        """Range time at half swath"""
        return self._rng_time_half_swath

    @property
    def range_axis(self) -> np.ndarray:
        """Range axis"""
        return self._range_axis

    @property
    def slant_range_axis(self) -> np.ndarray:
        """Range axis"""
        return self._slant_range_axis

    @property
    def azimuth_axis(self) -> np.ndarray:
        """Azimuth axis, PreciseDateTime format"""
        return self._azimuth_axis

    @property
    def lines_per_burst(self) -> np.ndarray:
        """Lines per burst, for each burst in the swath"""
        return self._lines_per_burst_array

    @property
    def radiometric_quantity(self) -> np.ndarray:
        """Product radiometric quantity"""
        return self._radiometric_quantity

    @property
    def pulse_latch_time(self) -> None:
        """Signal pulse latch time"""
        return None

    @property
    def swst_changes(self) -> list[tuple[PreciseDateTime, float]] | None:
        """SWST changes list as tuple of time of change and new SWST value"""
        return self._swst_changes

    def get_mid_burst_times(self, burst: int) -> tuple[PreciseDateTime, float]:
        """Compute mid azimuth and range times for a given burst.

        Returns
        -------
        tuple(PreciseDateTime, float)
            azimuth and range mid burst times
        """
        az_mid_burst = self.mid_azimuth_time
        rng_mid_burst = self.mid_range_time
        if self._channel.burst_info.num > 0:
            az_time_boundaries, rng_time_boundaries = self._get_raster_layout()
            az_mid_burst = (az_time_boundaries[burst][1] - az_time_boundaries[burst][0]) / 2 + az_time_boundaries[
                burst
            ][0]
            rng_mid_burst = (rng_time_boundaries[burst][1] - rng_time_boundaries[burst][0]) / 2 + rng_time_boundaries[
                burst
            ][0]

        return az_mid_burst, rng_mid_burst

    def get_steering_rate(self, azimuth_time: PreciseDateTime, burst: int) -> float:
        """Compute steering rate at a given azimuth time and for a given burst.

        Parameters
        ----------
        azimuth_time : PreciseDateTime
            azimuth time
        burst : int
            burst corresponding to the input time

        Returns
        -------
        float
            azimuth steering rate
        """
        if self._channel.burst_info.num > 0 and burst is not None:
            time_rel = azimuth_time - self._channel.burst_info.azimuth_start_times[burst]
        else:
            time_rel = azimuth_time - self._channel.raster_info.lines_start
        return (
            self._steering_rate_poly_coeff[0]
            + self._steering_rate_poly_coeff[1] * time_rel
            + self._steering_rate_poly_coeff[2] * time_rel**2
        )

    def get_location_data(self, azimuth_time: PreciseDateTime, range_time: float) -> LocationData:
        """Generating a LocationData object containing data and info derived from the current SAOCOMChannelManager
        and declined to the specific azimuth and range times selected.

        Parameters
        ----------
        abs_azimuth_time : PreciseDateTime
            selected absolute azimuth time
        abs_range_time : float
            selected absolute range time

        Returns
        -------
        LocationData
            LocationData instance related to the selected location
        """

        incidence_angle = compute_incidence_angles_from_trajectory(
            trajectory=self.trajectory,
            azimuth_time=azimuth_time,
            range_times=range_time,
            look_direction=self.looking_side.value,
        )
        look_angle = compute_look_angles_from_trajectory(
            trajectory=self.trajectory,
            azimuth_time=azimuth_time,
            range_times=self.mid_range_time,
            look_direction=self.looking_side.value,
        )
        v_ground = compute_ground_velocity_from_trajectory(
            trajectory=self.trajectory, azimuth_time=azimuth_time, look_angles_rad=look_angle
        )
        azimuth_step_m = self.azimuth_step_s * v_ground

        # TODO: this should be a common feature, also: slant_range_step_m, not range_step_m
        if self.projection == SARProjection.SLANT_RANGE:
            ground_range_step_m: float = self.range_step_m / np.sin(incidence_angle)
            range_step_m = self.range_step_m
        elif self.projection == SARProjection.GROUND_RANGE:
            ground_range_step_m: float = self.range_step_m
            range_step_m = self.range_step_m * np.sin(incidence_angle)

        return LocationData(
            abs_azimuth_time=azimuth_time,
            abs_range_time=range_time,
            incidence_angle=incidence_angle,
            look_angle=look_angle,
            ground_velocity=v_ground,
            azimuth_step_m=azimuth_step_m,
            range_step_m=range_step_m,
            ground_range_step_m=ground_range_step_m,
        )

    def pixel_to_times_conversion(
        self, azimuth_index: float, range_index: float, burst: int = None
    ) -> tuple[PreciseDateTime, float]:
        """Converting input raster pixel coordinates (azimuth_index and range index) to corresponding absolute times,
        azimuth and range.

        Parameters
        ----------
        azimuth_index : float
            azimuth pixel index, subpixel precision
        range_index : float
            range pixel index, subpixel precision
        burst : int, optional
            burst index, by default None

        Returns
        -------
        tuple[PreciseDateTime, float]
            azimuth time,
            range time
        """

        start_time_rng = self._channel.raster_info.samples_start
        if self._channel.burst_info.num > 0 and burst is not None:
            start_time_az = self._channel.burst_info.azimuth_start_times[burst]
            az_time = (
                azimuth_index - self._channel.burst_info.lines_per_burst * burst
            ) * self._channel.raster_info.lines_step + start_time_az
        else:
            start_time_az = self._channel.raster_info.lines_start
            az_time = azimuth_index * self._channel.raster_info.lines_step + start_time_az

        rng_time = range_index * self._channel.raster_info.samples_step + start_time_rng

        if self.projection == SARProjection.GROUND_RANGE:
            rng_time = self._channel.coordinate_conversions.evaluate_ground_to_slant(
                azimuth_time=self.mid_azimuth_time, ground_range=rng_time
            )

        return az_time, rng_time

    def times_to_pixel_conversion(
        self, azimuth_time: PreciseDateTime, range_time: float, burst: int = None
    ) -> tuple[float, float]:
        """Converting azimuth and range times to raster image pixels indexes with subpixel precision.

        Parameters
        ----------
        azimuth_time : PreciseDateTime
            azimuth time
        range_time : float
            range time
        burst : int
            burst number corresponding to these times

        Returns
        -------
        tuple[float, float]
            pixel corresponding to azimuth time,
            pixel corresponding to range time
        """

        rng_value = range_time
        if self.projection == SARProjection.GROUND_RANGE:
            # if projection is GROUND RANGE, range info are expressed in meters, so it must be converted
            rng_value = self._channel.coordinate_conversions.evaluate_slant_to_ground(
                azimuth_time=azimuth_time, slant_range=range_time
            )

        rng_idx = (rng_value - self._channel.raster_info.samples_start) / self._channel.raster_info.samples_step
        if self._channel.burst_info.num > 0:
            if burst is None:
                burst = self.times_to_burst_association([azimuth_time])[0]
            azmth_idx = (
                azimuth_time - self._channel.burst_info.azimuth_start_times[burst]
            ) / self._channel.raster_info.lines_step + self._channel.burst_info.lines_per_burst * burst
        else:
            azmth_idx = (azimuth_time - self._channel.raster_info.lines_start) / self._channel.raster_info.lines_step

        return azmth_idx, rng_idx

    def ground_points_to_burst_association(self, coordinates: ArrayLike) -> list[list[int] | None]:
        """Determining the burst (or bursts) where the input coordinates lie. If no association can be found (i.e. the
        point is not visible in the scene), None is returned.

        Parameters
        ----------
        coordinates : ArrayLike
            array of coordinates, in the form (N, 3)

        Returns
        -------
        list[list[int] | None]
            list containing the burst association for each input point, None if no association was found
        """

        coordinates = np.atleast_2d(coordinates)

        t_azmth, t_rng = [], []
        for coord in coordinates:
            try:
                t_azmth_i, t_rng_i = inverse_geocoding_monostatic_core(
                    trajectory=self.trajectory,
                    ground_points=coord,
                    wavelength=1,
                    frequencies_doppler_centroid=0,
                    initial_guesses=self.mid_azimuth_time,
                )
                t_azmth.append(t_azmth_i)
                t_rng.append(t_rng_i)
            except Exception:
                t_azmth.append(np.nan)
                t_rng.append(np.nan)

        t_azmth = np.asarray(t_azmth)
        t_rng = np.asarray(t_rng)

        az_check = [
            (
                [(t < az[1] and t > az[0]) for az in self._burst_az_boundaries]
                if isinstance(t, PreciseDateTime)
                else [False]
            )
            for t in t_azmth
        ]
        rng_check = [
            [(t < rng[1] and t > rng[0]) for rng in self._burst_rng_boundaries] if ~np.isnan(t) else [False]
            for t in t_rng
        ]
        check = [np.logical_and(az_check[c], rng_check[c]) for c in range(len(az_check))]

        bursts = [list(np.where(c)[0]) if c.any() else None for c in check]

        return bursts

    def times_to_burst_association(self, azimuth_times: ArrayLike) -> list[int]:
        """Associate the right burst to a given input time point. This function returns 1 association for each
        input time.
        Associating time only to the first burst containing it.

        Parameters
        ----------
        azimuth_time : ArrayLike
            azimuth time array in PreciseDateTime format

        Returns
        -------
        list[int]
            burst associated with a given time

        Raises
        ------
        CoordinatesOutOfBounds
            if input time exceeds tme boundaries of the swath
        """
        if self._channel.burst_info is None:
            return [0] * len(azimuth_times)

        bursts_start_times = self._channel.burst_info.azimuth_start_times
        last_time = (
            bursts_start_times[0]
            + self._channel.burst_info.num
            * self._channel.burst_info.lines_per_burst
            * self._channel.raster_info.lines_step
        )

        bursts = []
        for time in azimuth_times:
            if time < bursts_start_times[0] or time > last_time:
                raise CoordinatesOutOfBounds(f"{time} is out of the recorded timeline")

            time_diff = time - bursts_start_times
            time_mask = np.ma.masked_less(time_diff.astype("float64"), 0)
            # associating time only to the first burst containing it
            bursts.append(time_mask.argmin())

        return bursts

    def pixel_to_burst_association(self, azimuth_px_indexes: ArrayLike) -> list[int]:
        """Associate the azimuth pixel value to the right burst. This function returns 1 association for each
        input time.

        Parameters
        ----------
        azimuth_px_indexes : ArrayLike
            azimuth pixel indexes array

        Returns
        -------
        list[int]
            burst associated with a given pixel index

        Raises
        ------
        CoordinatesOutOfBounds
            if input time exceeds tme boundaries of the swath
        """
        if self._channel.burst_info is None:
            return [0] * len(azimuth_px_indexes)

        bursts_lines = np.repeat(self._channel.burst_info.lines_per_burst, self._channel.burst_info.num)
        burst_boundaries = np.array([0] + [sum(bursts_lines[: t + 1]) for t, _ in enumerate(bursts_lines)])

        bursts = []
        for coord in azimuth_px_indexes:
            if coord > burst_boundaries[-1]:
                raise CoordinatesOutOfBounds(f"{coord} pixel exceeds swath's bounds")

            px_diff = coord - burst_boundaries
            px_mask = np.ma.masked_less(px_diff, 0)

            bursts.append(px_mask.argmin())

        return bursts

    def read_data(
        self,
        azimuth_index: float,
        range_index: float,
        cropping_size: tuple[int, int] = (150, 150),
        output_radiometric_quantity: SARRadiometricQuantity = SARRadiometricQuantity.BETA_NOUGHT,
        burst: int | None = None,
    ) -> np.ndarray:
        """Extracting the swath portion centered to the provided target position and of size cropping_size by
        cropping_size. Target position is provided via its azimuth and range indexes in the swath array.

        Parameters
        ----------
        azimuth_index : float
            index of azimuth time in swath array
        range_index : float
            index of range time in swath array
        cropping_size : tuple[int, int], optional
            size in pixel of the swath portion to be read (number of samples, number of lines), by default (150, 150)
        output_radiometric_quantity : SARRadiometricQuantity, optional
            selected output radiometric quantity to convert the read data to, if needed,
            by default SARRadiometricQuantity.BETA_NOUGHT
        burst : int, optional
            if burst is provided, the roi extraction gives error if the boundaries exceed the burst boundaries,
            by default None

        Returns
        -------
        np.ndarray
            cropped swath array centered to the input target coordinates, output array is (samples, lines)
            by default the output radiometric quantity is BETA_NOUGHT, unless specified otherwise

        Raises
        ------
        AzimuthExceedsBoundariesError
            azimuth index exceeds swath boundaries
        RangeExceedsBoundariesError
            range index exceeds swath boundaries
        """

        # NOTE: inverting range index starting from the end of the axis due to the fact that the binary is written
        # in the opposite direction along range
        range_index = self._channel.raster_info.samples - range_index
        # creating the target block identifier for partial swath reading
        # [start line, start sample, number of lines, number of samples]
        target_block = [
            azimuth_index - np.floor(cropping_size[1] / 2).astype(int),
            range_index - np.floor(cropping_size[0] / 2).astype(int),
            cropping_size[1],
            cropping_size[0],
        ]

        if target_block[0] > self._channel.raster_info.lines or target_block[0] < 0:
            # starting azimuth line to be read is out of swath boundaries
            raise AzimuthExceedsBoundariesError(f"First ROI line {target_block[0]} is out of azimuth swath boundaries")

        if target_block[1] > self._channel.raster_info.samples or target_block[1] < 0:
            # starting range sample to be read is out of swath boundaries
            raise RangeExceedsBoundariesError(f"First ROI sample {target_block[1]} is out of range swath boundaries")

        if target_block[0] + target_block[2] > self._channel.raster_info.lines:
            # last azimuth line to be read is out of swath boundaries
            raise AzimuthExceedsBoundariesError(
                f"Last ROI line {target_block[0] + target_block[2]} exceeds azimuth swath boundaries"
            )

        if target_block[1] + target_block[3] > self._channel.raster_info.samples:
            # last range sample to be read is out of swath boundaries
            raise RangeExceedsBoundariesError(
                f"Last ROI sample {target_block[1] + target_block[3]} exceeds range swath boundaries"
            )

        # reading data portion and switching to convention (samples, lines) with transpose
        data = read_channel_data(
            raster_file=self._product_path,
            block_to_read=target_block,
            scaling_conversion=self._channel.image_calibration_factor,
        ).T

        # converting to beta nought if radiometric quantity is different
        if self._radiometric_quantity != output_radiometric_quantity:
            azimuth_time, _ = self.pixel_to_times_conversion(azimuth_index=azimuth_index, range_index=range_index)
            incidence_angles = compute_incidence_angles_from_trajectory(
                trajectory=self.trajectory,
                azimuth_time=azimuth_time,
                range_times=self._slant_range_axis[target_block[1] : target_block[1] + target_block[3]],
                look_direction=self.looking_side.value,
            )
            data = radiometric_correction(
                data=data,
                incidence_angle=incidence_angles,
                input_quantity=self._radiometric_quantity,
                output_quantity=output_radiometric_quantity,
            )

        if np.isrealobj(data):
            return data.astype("float64")

        return data
