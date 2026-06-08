"""Testing testing/cli.py"""

from unittest import mock

from sct.testing.cli import integration_testing


def test_integration_testing_success(tmp_path):
    registry_file = tmp_path / "registry.json"
    registry_file.write_text("{}")
    output_dir = tmp_path / "output"

    with mock.patch("sct.testing.cli.run_tests", return_value={"S1A": {"test1": True}}):
        with mock.patch("sct.testing.cli.summary_results", return_value=True):
            with mock.patch("sct.testing.cli.common.display_title"):
                with mock.patch("sct.testing.cli.typer.echo"):
                    with mock.patch("sct.testing.cli.sys.exit") as mock_exit:
                        integration_testing(registry_file, output_dir)
                        mock_exit.assert_called_once_with(0)


def test_integration_testing_failure(tmp_path):
    registry_file = tmp_path / "registry.json"
    registry_file.write_text("{}")
    output_dir = tmp_path / "output"

    with mock.patch("sct.testing.cli.run_tests", return_value={"S1A": {"test1": False}}):
        with mock.patch("sct.testing.cli.summary_results", return_value=False):
            with mock.patch("sct.testing.cli.common.display_title"):
                with mock.patch("sct.testing.cli.typer.echo"):
                    with mock.patch("sct.testing.cli.sys.exit") as mock_exit:
                        integration_testing(registry_file, output_dir)
                        mock_exit.assert_called_once_with(1)


def test_integration_testing_creates_output_dir(tmp_path):
    registry_file = tmp_path / "registry.json"
    registry_file.write_text("{}")
    output_dir = tmp_path / "nonexistent_output"

    assert not output_dir.exists()

    with mock.patch("sct.testing.cli.run_tests", return_value={}):
        with mock.patch("sct.testing.cli.summary_results", return_value=True):
            with mock.patch("sct.testing.cli.common.display_title"):
                with mock.patch("sct.testing.cli.typer.echo"):
                    with mock.patch("sct.testing.cli.sys.exit"):
                        integration_testing(registry_file, output_dir)
                        assert output_dir.exists()
