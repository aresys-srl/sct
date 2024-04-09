# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality input protocol-compliance of every product wrapper"""

import unittest

from arepyextras.quality.io.quality_input_protocol import ChannelData, QualityInputProduct, SARCoordinatesFunction

from sct.io.extended_protocols import SCTInputProduct
from sct.io.quality_input_from_iceye_product import ICEYEChannelManager, ICEYEDopplerPolynomial, ICEYEProductManager
from sct.io.quality_input_from_novasar1_product import (
    NovaSAR1ChannelManager,
    NovaSAR1DopplerPolynomial,
    NovaSAR1ProductManager,
)
from sct.io.quality_input_from_sentinel1_product import (
    Sentinel1ChannelManager,
    Sentinel1DopplerPolynomial,
    Sentinel1ProductManager,
)


class SENTINEL1ProductWrapperTest(unittest.TestCase):
    """Testing quality_input_from_safe_product.py functionalities"""

    def test_product_protocol_compliance_sct(self) -> None:
        """Test SCT protocol-compliance of Sentinel1ProductManager"""
        assert isinstance(Sentinel1ProductManager, SCTInputProduct)

    def test_product_protocol_compliance(self) -> None:
        """Test protocol-compliance of Sentinel1ProductManager"""
        assert isinstance(Sentinel1ProductManager, QualityInputProduct)

    def test_channel_protocol_compliance(self) -> None:
        """Test protocol-compliance of Sentinel1ChannelManager"""
        assert isinstance(Sentinel1ChannelManager, ChannelData)

    def test_poly_protocol_compliance(self) -> None:
        """Test protocol-compliance of Sentinel1DopplerPolynomial"""
        assert isinstance(Sentinel1DopplerPolynomial, SARCoordinatesFunction)


class NOVASAR1ProductWrapperTest(unittest.TestCase):
    """Testing quality_input_from_novasar_product.py functionalities"""

    def test_product_protocol_compliance_sct(self) -> None:
        """Test SCT protocol-compliance of NovaSAR1ProductManager"""
        assert isinstance(NovaSAR1ProductManager, SCTInputProduct)

    def test_product_protocol_compliance(self) -> None:
        """Test protocol-compliance of NovaSAR1ProductManager"""
        assert isinstance(NovaSAR1ProductManager, QualityInputProduct)

    def test_channel_protocol_compliance(self) -> None:
        """Test protocol-compliance of NovaSAR1ChannelManager"""
        assert isinstance(NovaSAR1ChannelManager, ChannelData)

    def test_poly_protocol_compliance(self) -> None:
        """Test protocol-compliance of NovaSAR1DopplerPolynomial"""
        assert isinstance(NovaSAR1DopplerPolynomial, SARCoordinatesFunction)


class ICEYEProductWrapperTest(unittest.TestCase):
    """Testing quality_input_from_iceye_product.py functionalities"""

    def test_product_protocol_compliance_sct(self) -> None:
        """Test SCT protocol-compliance of ICEYEProductManager"""
        assert isinstance(ICEYEProductManager, SCTInputProduct)

    def test_product_protocol_compliance(self) -> None:
        """Test protocol-compliance of ICEYEProductManager"""
        assert isinstance(ICEYEProductManager, QualityInputProduct)

    def test_channel_protocol_compliance(self) -> None:
        """Test protocol-compliance of ICEYEChannelManager"""
        assert isinstance(ICEYEChannelManager, ChannelData)

    def test_poly_protocol_compliance(self) -> None:
        """Test protocol-compliance of ICEYEDopplerPolynomial"""
        assert isinstance(ICEYEDopplerPolynomial, SARCoordinatesFunction)


if __name__ == "__main__":
    unittest.main()
