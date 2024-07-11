# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing quality_input_from_eos04_product support"""

import sys
import unittest
from pathlib import Path

from sct.io.quality_input_from_eos04_product import EOS04ChannelManager, EOS04DopplerPolynomial, EOS04ProductManager

sys.path.append(str(Path(__file__).parent))
from adapters_tester import create_polynomial_test_case, create_product_manager_test_case

EOS04DopplerPolynomialTestCase = create_polynomial_test_case(EOS04DopplerPolynomial)

EOS04ProductManagerTestCase = create_product_manager_test_case(
    EOS04ProductManager, EOS04ChannelManager, EOS04DopplerPolynomial, "quality_input_from_eos04_product"
)

if __name__ == "__main__":
    unittest.main()
