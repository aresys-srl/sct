# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing IO support"""

import unittest

from sct.io.io_support import convert_camel2snake


class Camel2Snake(unittest.TestCase):
    """Camel2Snake tests"""

    def test_convert_camel2snake(self):
        """Basic test"""
        self.assertEqual(convert_camel2snake("CamelCase"), "camel_case")
        self.assertEqual(convert_camel2snake("AnotherTest"), "another_test")
        self.assertEqual(convert_camel2snake("Example"), "example")


if __name__ == "__main__":
    unittest.main()
