# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Web scraping download utilities unit tests"""

from sct.web_scraping._utilities import download_watchdog


def test_download_watchdog(tmp_path):
    result = download_watchdog(tmp_path, n_files=1, timeout=1)
    assert not result
