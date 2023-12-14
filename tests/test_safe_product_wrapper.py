# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SAFE quality input protocol-compliant product wrapper"""

import unittest

from arepyextras.quality.io.quality_input_protocol import (
    ChannelData,
    DopplerPolynomial,
    QualityInputProduct,
)

from sct.io.quality_input_from_safe_product import (
    S1DopplerPolynomial,
    SafeChannelManager,
    SafeProductManager,
)


class SAFEProductWrapperTest(unittest.TestCase):
    """Testing quality_input_from_safe_product.py functionalities"""

    def test_product_protocol_compliancy(self) -> None:
        """Test protocol-compliancy of SafeProductManager"""
        assert isinstance(SafeProductManager, QualityInputProduct)

    def test_channel_protocol_compliancy(self) -> None:
        """Test protocol-compliancy of SafeChannelManager"""
        assert isinstance(SafeChannelManager, ChannelData)

    def test_poly_protocol_compliancy(self) -> None:
        """Test protocol-compliancy of S1DopplerPolynomial"""
        assert isinstance(S1DopplerPolynomial, DopplerPolynomial)


if __name__ == "__main__":
    unittest.main()
