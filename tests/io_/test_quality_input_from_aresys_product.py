# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_aresys_product support"""

import sys
import unittest
from pathlib import Path

from arepyextras.quality.io.quality_input_from_product_folder import DopplerPolynomialWrapper

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case

ARESYSDopplerPolynomialTestCase = create_polynomial_test_case(DopplerPolynomialWrapper)

if __name__ == "__main__":
    unittest.main()
