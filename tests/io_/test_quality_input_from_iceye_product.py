# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_iceye_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_iceye_product import ICEYEChannelManager, ICEYEDopplerPolynomial, ICEYEProductManager

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

ICEYEDopplerPolynomialTestCase = create_polynomial_test_case(ICEYEDopplerPolynomial)

ICEYEProductManagerTestCase = create_product_manager_test_case(
    ICEYEProductManager, ICEYEChannelManager, ICEYEDopplerPolynomial, "quality_input_from_iceye_product"
)

if __name__ == "__main__":
    unittest.main()
