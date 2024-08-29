# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_cosmo_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_cosmo_product import COSMOChannelManager, COSMODopplerPolynomial, COSMOProductManager

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

COSMODopplerPolynomialTestCase = create_polynomial_test_case(COSMODopplerPolynomial)

COSMOProductManagerTestCase = create_product_manager_test_case(
    COSMOProductManager, COSMOChannelManager, COSMODopplerPolynomial, "quality_input_from_cosmo_product"
)

if __name__ == "__main__":
    unittest.main()
