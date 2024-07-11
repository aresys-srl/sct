# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_novasar1_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_novasar1_product import (
    NovaSAR1ChannelManager,
    NovaSAR1DopplerPolynomial,
    NovaSAR1ProductManager,
)

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

NOVASARDopplerPolynomialTestCase = create_polynomial_test_case(NovaSAR1DopplerPolynomial)

NOVASARProductManagerTestCase = create_product_manager_test_case(
    NovaSAR1ProductManager, NovaSAR1ChannelManager, NovaSAR1DopplerPolynomial, "quality_input_from_novasar1_product"
)

if __name__ == "__main__":
    unittest.main()
