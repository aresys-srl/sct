# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT main file Unittest module
-----------------------------
"""

import unittest
from unittest import mock

from sct import __main__ as main_module


class MainTestCase(unittest.TestCase):
    """Testing main module"""

    @mock.patch("sys.stdout", new=None)
    @mock.patch("sys.argv", new=["--help"])
    def test_main(self):
        """Call the main function"""
        try:
            main_module.main()
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 2)
        else:
            raise AssertionError("SystemExit not raised")


if __name__ == "__main__":
    unittest.main()
