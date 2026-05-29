# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT main function unit tests"""

import pytest

from sct import __main__ as main_module


def test_main(monkeypatch):
    """Call the main function"""
    monkeypatch.setattr("sys.stdout", None)
    monkeypatch.setattr("sys.argv", ["--help"])
    try:
        main_module.main()
    except SystemExit as system_exit:
        assert system_exit.code == 2
    else:
        pytest.fail("SystemExit not raised")
