# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Mock products to test the adapter without the need of disk access to a concrete product"""

from dataclasses import dataclass
from enum import Enum

import numpy as np
from arepytools.math.genericpoly import SortedPolyList
from arepytools.timing.precisedatetime import PreciseDateTime


@dataclass
class MockProduct:
    """Mock product with minimal data and methods"""

    footprint: list
    channels_list: list[str]
    metadata_file = "metadata_file"

    def get_files_from_channel_name(self, channel_name):
        return 3 * [f"file_{channel_name}"]

    def get_raster_files_from_channel_name(self, channel_id):
        return f"file_{channel_id}"

    get_raster_file_from_channel_name = get_raster_files_from_channel_name


class MockEnum(Enum):
    """Mock values for several enums"""

    BETA_NOUGHT = "BETA_NOUGHT"
    HH = "H/H"
    SLANT_RANGE = "SLANT RANGE"
    ASCENDING = "ASCENDING"
    RIGHT_LOOKING = "RIGHT"


class MockProductType(str):
    """Mock product type"""

    @property
    def value(self):
        return str(self)


@dataclass
class MockChannel:
    """Mock channel"""

    image_radiometric_quantity = MockEnum.BETA_NOUGHT

    class MockGeneralInfo:
        polarization = MockEnum.HH
        projection = MockEnum.SLANT_RANGE
        orbit_direction = MockEnum.ASCENDING
        product_level = "SLC"
        product_type = MockProductType("SLC")
        swath = "S1"

    class MockRasterInfo:
        samples = 50
        samples_start = 0.5
        samples_step = 0.1
        lines = 1000
        lines_step = 0.1
        lines_start = PreciseDateTime.from_numeric_datetime(2000)

    class MockDataSetInfo:
        side_looking = MockEnum.RIGHT_LOOKING
        fc_hz = 1000

    class MockBurstInfo:
        num = 1
        azimuth_start_times = np.array([PreciseDateTime.from_numeric_datetime(2000)])
        lines_per_burst = 1000

    class MockPulse:
        bandwidth = 1000
        pulse_length = 30
        length = 30
        tx_pulse_latch_time = None

    class MockSwathInfo:
        azimuth_steering_rate_poly = [0, 0, 0]
        azimuth_steering_rate_pol = [0, 0, 0]

    class MockGSO:
        pass

    class MockATL:
        swst_changes = [0, [0], [0]]

    general_info = MockGeneralInfo()
    raster_info = MockRasterInfo()
    dataset_info = MockDataSetInfo()
    burst_info = MockBurstInfo()
    pulse = MockPulse()
    swath_info = MockSwathInfo()
    general_sar_orbit = MockGSO()
    doppler_centroid_poly = SortedPolyList()
    doppler_rate_poly = SortedPolyList()
    doppler_rate_vector = SortedPolyList()
    acquisition_timeline = MockATL()
    sampling_constants = None
    image_calibration_factor = 1
