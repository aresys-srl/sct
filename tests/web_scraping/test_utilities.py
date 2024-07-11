# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT automatic Unittest module
-----------------------------
"""
import unittest
from tempfile import TemporaryDirectory

from sct.web_scraping._utilities import download_watchdog


class DownloadWatchDogTestCase(unittest.TestCase):

    def test_download_watchdog(self):

        with TemporaryDirectory() as dir:
            result = download_watchdog(dir, n_files=1, timeout=1)
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
