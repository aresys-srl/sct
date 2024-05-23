# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Test provider for different product adapters"""

import unittest
from pathlib import Path
from types import NoneType
from unittest import mock

import numpy as np
from arepyextras.quality.core.generic_dataclasses import (
    SARImageType,
    SAROrbitDirection,
    SARPolarization,
    SARProjection,
    SARSideLooking,
)
from arepyextras.quality.io.quality_input_protocol import ChannelData, QualityInputProduct, SARCoordinatesFunction
from arepytools.geometry.generalsarorbit import GSO3DCurveWrapper
from arepytools.math.genericpoly import GenericPoly, SortedPolyList
from arepytools.timing.precisedatetime import PreciseDateTime
from mock_product import MockChannel, MockProduct
from shapely import Polygon

from sct.io.extended_protocols import SCTInputProduct


def create_polynomial_test_case(custom_polynomial_class):
    """Create test case for polynomial adapter"""
    poly_0 = GenericPoly(
        reference_values=[
            PreciseDateTime.from_utc_string("09-JUL-2006 21:00:0.0"),
            2,
        ],
        coefficients=[
            2.5,
            2.5,
            0.0,
            -1.0,
        ],
        powers=[(0, 2), (1, 0), (1, 0), (0, 2)],
    )

    poly_1 = GenericPoly(
        reference_values=[PreciseDateTime(), 8],
        coefficients=[
            5.5,
            6.0,
            0.0,
            0.0,
            1.0,
            1.0,
        ],
        powers=[(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (0, 5)],
    )

    values_0 = [
        PreciseDateTime.from_utc_string("09-JUL-2006 21:00:3.0"),
        4,
    ]
    result_0 = 13.5

    values_1 = [
        PreciseDateTime.from_utc_string("09-JUL-2006 20:59:7.0"),
        4,
    ]
    result_1 = -1026.5

    class DopplerPolynomialTestCase(unittest.TestCase):
        """Doppler poly test case"""

        def setUp(self) -> None:
            self.sorted_poly_list = SortedPolyList(list_generic_poly=[poly_0, poly_1])

        def test_protocol_compliance(self) -> None:
            """Test protocol-compliance of custom polynomial class"""
            assert isinstance(custom_polynomial_class, SARCoordinatesFunction)

        def test_doppler_polynomial(self):
            """Test proper evaluation"""
            poly = custom_polynomial_class(self.sorted_poly_list)
            self.assertEqual(poly.evaluate(*values_0), result_0)
            self.assertEqual(poly.evaluate(*values_1), result_1)

    return DopplerPolynomialTestCase


def create_product_manager_test_case(
    custom_product_manager_class, custom_channel_class, custom_polynomial_class, module_name: str
):
    """Create test case for given adapter"""
    product = MockProduct(footprint=[-20, 20, 0, 15], channels_list=[0, 1])
    channel = MockChannel()
    raster = np.zeros((2, 2))

    class ProductManagerTestCase(unittest.TestCase):
        """ProductManager test case"""

        def test_product_protocol_compliance_sct(self) -> None:
            """Test SCT protocol-compliance of custom product manager class"""
            assert isinstance(custom_product_manager_class, SCTInputProduct)

        def test_product_protocol_compliance(self) -> None:
            """Test quality protocol-compliance of custom product manager class"""
            assert isinstance(custom_product_manager_class, QualityInputProduct)

        def test_channel_protocol_compliance(self) -> None:
            """Test quality protocol-compliance of custom channel class"""
            assert isinstance(custom_channel_class, ChannelData)

        @mock.patch(f"sct.io.{module_name}.open_product", mock.Mock(return_value=product))
        @mock.patch(f"sct.io.{module_name}.read_channel_data", mock.Mock(return_value=raster))
        @mock.patch(f"sct.io.{module_name}.read_channel_calibration", mock.Mock(return_value=raster), create=True)
        @mock.patch(f"sct.io.{module_name}.read_channel_metadata", mock.Mock(return_value=channel), create=True)
        @mock.patch(f"sct.io.{module_name}.read_product_metadata", mock.Mock(return_value=[channel]), create=True)
        def test_init(self):
            """test init"""
            product_manager = custom_product_manager_class(path=Path("example_product"))
            self.assertEqual(product_manager.channels_list, [0, 1])
            self.assertEqual(product_manager.name, "example_product")
            self.assertEqual(product_manager.footprint, Polygon([(-20, 0), (-20, 15), (20, 0), (20, 15)]))
            self.assertEqual(product_manager.path, Path("example_product"))

            channel_data = product_manager.get_channel_data(0)
            self.assertEqual(channel_data.carrier_frequency, 1000)
            self.assertEqual(channel_data.swath_name, "S1")
            self.assertEqual(channel_data.channel_id, 0)
            self.assertEqual(channel_data.range_step_m, 14989622.9)
            self.assertEqual(channel_data.projection, SARProjection.SLANT_RANGE)
            self.assertEqual(channel_data.polarization, SARPolarization.HH)
            self.assertEqual(channel_data.orbit_direction, SAROrbitDirection.ASCENDING)
            self.assertTrue(channel_data.image_type == "SLC" or channel_data.image_type == SARImageType.SLC)
            self.assertEqual(channel_data.sampling_constants, None)
            self.assertEqual(channel_data.looking_side, SARSideLooking.RIGHT_LOOKING)
            self.assertEqual(
                channel_data.mid_azimuth_time, PreciseDateTime.from_utc_string("01-JAN-2000 00:00:50.000000000000")
            )
            self.assertEqual(type(channel_data.trajectory), GSO3DCurveWrapper)
            self.assertEqual(channel_data.boresight_normal_curve, None)
            self.assertTrue(isinstance(channel_data.doppler_centroid, (custom_polynomial_class, NoneType)))
            self.assertTrue(isinstance(channel_data.doppler_rate, (custom_polynomial_class, NoneType)))
            self.assertEqual(channel_data.mid_range_time, 2.95)
            self.assertEqual(len(channel_data.range_axis), 50)
            self.assertEqual(channel_data.azimuth_step_s, 0.1)
            self.assertEqual(channel_data.pulse_rate, 33.333333333333336)
            self.assertEqual(len(channel_data.slant_range_axis), 50)
            self.assertEqual(len(channel_data.azimuth_axis), 1000)
            self.assertEqual(channel_data.lines_per_burst, 1000)
            self.assertEqual(channel_data.pulse_latch_time, None)
            self.assertEqual(channel_data.swst_changes, [(0, 0)])
            self.assertEqual(
                channel_data.get_mid_burst_times(0),
                (PreciseDateTime.from_utc_string("01-JAN-2000 00:00:50.000000000000"), 3),
            )
            self.assertEqual(
                channel_data.get_steering_rate(azimuth_time=PreciseDateTime.from_numeric_datetime(2000), burst=0), 0.0
            )
            self.assertEqual(
                channel_data.pixel_to_times_conversion(10, 5, 0),
                (PreciseDateTime.from_utc_string("01-JAN-2000 00:00:01.000000000000"), 1.0),
            )
            self.assertEqual(
                channel_data.times_to_pixel_conversion(
                    PreciseDateTime.from_utc_string("01-JAN-2000 00:00:01.000000000000"), 1.0, 0
                ),
                (10, 5),
            )
            self.assertEqual(
                channel_data.times_to_burst_association(
                    [PreciseDateTime.from_utc_string("01-JAN-2000 00:00:01.000000000000")]
                ),
                [0],
            )
            self.assertEqual(
                channel_data.pixel_to_burst_association([5]),
                [0],
            )
            self.assertEqual(channel_data.read_data(50, 10, (2, 2)).shape, (2, 2))

    return ProductManagerTestCase
