# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_radarsat2_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_radarsat2_product import (
    RADARSAT2ChannelManager,
    RADARSAT2DopplerPolynomial,
    RADARSAT2ProductManager,
)

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

RADARSATDopplerPolynomialTestCase = create_polynomial_test_case(RADARSAT2DopplerPolynomial)

RADARSATProductManagerTestCase = create_product_manager_test_case(
    RADARSAT2ProductManager, RADARSAT2ChannelManager, RADARSAT2DopplerPolynomial, "quality_input_from_radarsat2_product"
)

if __name__ == "__main__":
    unittest.main()
