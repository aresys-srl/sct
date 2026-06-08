"""Testing testing/utilities/executor.py"""

from pathlib import Path
from unittest import mock

import pytest

from sct.testing.utilities.common import TestParams
from sct.testing.utilities.executor import execute_analysis_test


def _make_handler(has_testing=True):
    handler = mock.Mock()
    handler.testing = mock.Mock() if has_testing else None
    return handler


def test_execute_api_with_config():
    handler = _make_handler()
    registry = {"pta": handler}
    params = mock.Mock(spec=TestParams, analysis="pta", config="config.toml", reference_output=mock.Mock())

    with mock.patch("sct.testing.utilities.executor.ANALYSIS_REGISTRY", registry):
        with mock.patch("sct.testing.utilities.executor.sct_logger"):
            execute_analysis_test(params, Path("/tmp/out"), graphs=False, cli=False)
            handler.config.from_toml.assert_called_once_with("config.toml")
            handler.testing.api_runner.assert_called_once()
            handler.testing.validator.assert_called_once()


def test_execute_api_without_config():
    handler = _make_handler()
    registry = {"pta": handler}
    params = mock.Mock(spec=TestParams, analysis="pta", config=None, reference_output=mock.Mock())

    with mock.patch("sct.testing.utilities.executor.ANALYSIS_REGISTRY", registry):
        with mock.patch("sct.testing.utilities.executor.sct_logger"):
            execute_analysis_test(params, Path("/tmp/out"), graphs=False, cli=False)
            handler.config.assert_called_once()
            handler.testing.api_runner.assert_called_once()
            handler.testing.validator.assert_called_once()


def test_execute_cli():
    handler = _make_handler()
    registry = {"pta": handler}
    params = mock.Mock(spec=TestParams, analysis="pta", config=mock.Mock(), reference_output=mock.Mock())

    with mock.patch("sct.testing.utilities.executor.ANALYSIS_REGISTRY", registry):
        with mock.patch("sct.testing.utilities.executor.sct_logger"):
            execute_analysis_test(params, Path("/tmp/out"), graphs=False, cli=True)
            handler.testing.cli_runner.assert_called_once()
            handler.testing.validator.assert_called_once()


def test_execute_unknown_analysis():
    params = mock.Mock(spec=TestParams, analysis="unknown")

    with mock.patch("sct.testing.utilities.executor.ANALYSIS_REGISTRY", {}):
        with pytest.raises(ValueError, match="Unsupported analysis type: unknown"):
            execute_analysis_test(params, Path("/tmp/out"))


def test_execute_no_testing_handler():
    handler = _make_handler(has_testing=False)
    registry = {"pta": handler}
    params = mock.Mock(spec=TestParams, analysis="pta")

    with mock.patch("sct.testing.utilities.executor.ANALYSIS_REGISTRY", registry):
        with pytest.raises(ValueError, match="Unsupported testing"):
            execute_analysis_test(params, Path("/tmp/out"))
