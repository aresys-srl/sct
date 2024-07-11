# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_sentinel1_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_sentinel1_product import (
    Sentinel1ChannelManager,
    Sentinel1DopplerPolynomial,
    Sentinel1ProductManager,
)

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

Sentinel1DopplerPolynomialTestCase = create_polynomial_test_case(Sentinel1DopplerPolynomial)

Sentinel1ProductManagerTestCase = create_product_manager_test_case(
    Sentinel1ProductManager, Sentinel1ChannelManager, Sentinel1DopplerPolynomial, "quality_input_from_sentinel1_product"
)

if __name__ == "__main__":
    unittest.main()
