"""Testing CLI common functions"""

import sys
from unittest import mock

from sct.cli.common import display_title, graceful_exit, log_elapsed_time, logging_to_file


def test_display_title():
    with mock.patch("typer.echo") as mock_echo:
        display_title("SCT")
        assert mock_echo.call_count >= 2


def test_logging_to_file_no_path():
    with logging_to_file(None):
        pass


def test_logging_to_file_with_path(tmp_path):
    log_file = tmp_path / "test.log"
    with logging_to_file(log_file):
        pass
    assert log_file.exists()


def test_log_elapsed_time_under_60s():
    @log_elapsed_time("test_func")
    def dummy():
        return 42

    with mock.patch("sct.cli.common.sct_logger") as mock_logger:
        result = dummy()
        assert result == 42
        mock_logger.info.assert_called_once()
        args, _ = mock_logger.info.call_args
        assert "completed in" in args[0]


def test_graceful_exit_success():
    @graceful_exit("test_func")
    def dummy():
        return "ok"

    result = dummy()
    assert result == "ok"


def test_graceful_exit_with_exception():
    @graceful_exit("test_func")
    def failing():
        raise ValueError("test error")

    with mock.patch.object(sys, "exit") as mock_exit:
        with mock.patch("sct.cli.common.sct_logger") as mock_logger:
            failing()
            mock_exit.assert_called_once_with(1)
            mock_logger.critical.assert_any_call("test_func failed")


def test_graceful_exit_saves_config(tmp_path):
    config_content = {"save_log": True}

    class MockConfig:
        def to_toml(self, out_file):
            with open(out_file, "w") as f:
                import json

                json.dump(config_content, f)

    @graceful_exit("test_func")
    def dummy_with_config(config=None, dump_config=False, output_directory=None):
        return "ok"

    result = dummy_with_config(config=MockConfig(), dump_config=True, output_directory=tmp_path)
    assert result == "ok"
    saved_file = tmp_path / "analysis_config.toml"
    assert saved_file.exists()


def test_log_elapsed_time_over_60s():
    @log_elapsed_time("slow_func")
    def slow():
        return 42

    with mock.patch("sct.cli.common.time.perf_counter", side_effect=[0, 65]):
        with mock.patch("sct.cli.common.sct_logger") as mock_logger:
            result = slow()
            assert result == 42
            args, _ = mock_logger.info.call_args
            assert "1 min" in args[0]
