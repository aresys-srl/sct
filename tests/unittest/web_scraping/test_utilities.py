# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Web scraping download utilities unit tests"""

from unittest import mock

from sct.web_scraping._utilities import download_watchdog


def test_download_watchdog_timeout(tmp_path):
    result = download_watchdog(tmp_path, n_files=1, timeout=1)
    assert not result


def test_download_watchdog_success(tmp_path):
    call_count = [0]

    def _mock_sleep(_seconds):
        call_count[0] += 1
        if call_count[0] == 1:
            (tmp_path / "file.txt").write_text("data")

    with mock.patch("sct.web_scraping._utilities.time.sleep", side_effect=_mock_sleep):
        result = download_watchdog(tmp_path, n_files=1, timeout=2)
        assert result is True


def test_download_watchdog_partial_crdownload(tmp_path):
    call_count = [0]

    def _mock_sleep(_seconds):
        call_count[0] += 1
        if call_count[0] == 1:
            (tmp_path / "file.txt.crdownload").write_text("data")

    with mock.patch("sct.web_scraping._utilities.time.sleep", side_effect=_mock_sleep):
        result = download_watchdog(tmp_path, n_files=1, timeout=2)
        assert result is False
