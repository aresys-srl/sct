# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_asar_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_asar_product import ASARChannelManager, ASARDopplerPolynomial, ASARProductManager

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

ASARDopplerPolynomialTestCase = create_polynomial_test_case(ASARDopplerPolynomial)

ASARProductManagerTestCase = create_product_manager_test_case(
    ASARProductManager, ASARChannelManager, ASARDopplerPolynomial, "quality_input_from_asar_product"
)

if __name__ == "__main__":
    unittest.main()
