"""Testing testing/run.py"""

from pathlib import Path
from unittest import mock

from sct.testing.run import print_dict_as_table, status_to_color, summary_results


def test_status_to_color_true():
    assert "PASS" in status_to_color(True)


def test_status_to_color_false():
    assert "FAIL" in status_to_color(False)


def test_summary_results_all_pass():
    results = {"S1A": {"test1": True, "test2": True}}
    with mock.patch("sct.testing.run.sct_logger") as mock_logger:
        with mock.patch("sct.testing.run.print_dict_as_table"):
            outcome = summary_results(results)
            assert outcome is True
            mock_logger.success.assert_any_call("INTEGRATION TESTS: PASS")


def test_summary_results_some_fail():
    results = {"S1A": {"test1": True, "test2": False}}
    with mock.patch("sct.testing.run.sct_logger") as mock_logger:
        with mock.patch("sct.testing.run.print_dict_as_table"):
            outcome = summary_results(results)
            assert outcome is False
            mock_logger.fail.assert_any_call("INTEGRATION TESTS: FAIL")


def test_summary_results_print_fallback():
    results = {"S1A": {"test1": True, "test2": False}}
    with mock.patch("sct.testing.run.sct_logger"):
        with mock.patch("sct.testing.run.print_dict_as_table", side_effect=Exception("fail")):
            with mock.patch("builtins.print") as mock_print:
                outcome = summary_results(results)
                assert outcome is False
                mock_print.assert_any_call("Sensor: S1A\n")


def test_test_session_success():
    from sct.testing.run import test_session

    params = mock.Mock()
    with mock.patch("sct.testing.run.execute_analysis_test"):
        with mock.patch("sct.testing.run.sct_logger"):
            result = test_session(params, "S1A", "test1", Path("/tmp/out"), graphs=False, cli=False)
            assert result is True


def test_test_session_failure():
    from sct.testing.run import test_session

    params = mock.Mock()
    with mock.patch("sct.testing.run.execute_analysis_test", side_effect=ValueError("test error")):
        with mock.patch("sct.testing.run.sct_logger"):
            result = test_session(params, "S1A", "test1", Path("/tmp/out"), graphs=False, cli=False)
            assert result is False


def test_print_dict_as_table():
    data = {"test1": True, "test2": False}
    with mock.patch("sct.testing.run.console") as mock_console:
        print_dict_as_table(data, title="TestTitle")
        mock_console.print.assert_called()


def test_run_tests(tmp_path):
    import json

    from sct.testing.run import run_tests

    registry_file = tmp_path / "registry.json"
    registry_file.write_text(json.dumps({"S1A": {"test1": {"analysis": "pta"}}}))
    output_dir = tmp_path / "output"

    with mock.patch("sct.testing.run.test_session", return_value=True) as mock_ts:
        with mock.patch("sct.testing.run.sct_logger"):
            with mock.patch("sct.testing.run.time.perf_counter", side_effect=[0, 1]):
                results = run_tests(registry_file, output_dir)
                assert results == {"S1A": {"test1": True}}
                mock_ts.assert_called_once()


def test_run_tests_multiple_sensors(tmp_path):
    import json

    from sct.testing.run import run_tests

    registry_file = tmp_path / "registry.json"
    registry_data = {
        "S1A": {"test_a": {"analysis": "pta"}, "test_b": {"analysis": "interf"}},
        "S2A": {"test_c": {"analysis": "pta"}},
    }
    registry_file.write_text(json.dumps(registry_data))
    output_dir = tmp_path / "output"

    with mock.patch("sct.testing.run.test_session", return_value=True) as mock_ts:
        with mock.patch("sct.testing.run.sct_logger"):
            with mock.patch("sct.testing.run.time.perf_counter", side_effect=[0, 1, 0, 1, 0, 1]):
                results = run_tests(registry_file, output_dir)
                assert results == {
                    "S1A": {"test_a": True, "test_b": True},
                    "S2A": {"test_c": True},
                }
                assert mock_ts.call_count == 3


def test_run_tests_elapsed_minutes(tmp_path):
    import json

    from sct.testing.run import run_tests

    registry_file = tmp_path / "registry.json"
    registry_file.write_text(json.dumps({"S1A": {"test1": {"analysis": "pta"}}}))
    output_dir = tmp_path / "output"

    with mock.patch("sct.testing.run.test_session", return_value=True):
        with mock.patch("sct.testing.run.sct_logger") as mock_logger:
            with mock.patch("sct.testing.run.time.perf_counter", side_effect=[0, 120]):
                run_tests(registry_file, output_dir)
                call_args = [c[0][0] for c in mock_logger.info.call_args_list if "minutes" in str(c)]
                assert any("minutes" in str(a) for a in call_args)
