# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_saocom_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_saocom_product import SAOCOMChannelManager, SAOCOMDopplerPolynomial, SAOCOMProductManager

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

SAOCOMDopplerPolynomialTestCase = create_polynomial_test_case(SAOCOMDopplerPolynomial)

SAOCOMProductManagerTestCase = create_product_manager_test_case(
    SAOCOMProductManager, SAOCOMChannelManager, SAOCOMDopplerPolynomial, "quality_input_from_saocom_product"
)

if __name__ == "__main__":
    unittest.main()
