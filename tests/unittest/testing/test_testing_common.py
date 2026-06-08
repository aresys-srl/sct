"""Testing test utilities common"""

from pathlib import Path
from unittest import mock

from sct.testing.utilities.common import ReferenceOutput, TestOutput, TestParams, cli_launcher


def test_test_output_defaults():
    out = TestOutput()
    assert out.csv_results is None
    assert out.netcdf_results is None


def test_reference_output_defaults():
    ref = ReferenceOutput()
    assert ref.csv_reference is None
    assert ref.netcdf_reference is None


def test_test_params_defaults():
    params = TestParams()
    assert params.analysis is None


def test_test_params_from_dict_analysis():
    params = TestParams.from_dict({"analysis": "pta"})
    assert params.analysis == "pta"
    assert params.product is None


def test_test_params_from_dict_product():
    params = TestParams.from_dict({"product": "/path/to/product.safe"})
    assert params.product == Path("/path/to/product.safe")


def test_test_params_from_dict_product_list():
    params = TestParams.from_dict({"product": ["/p1.safe", "/p2.safe"]})
    assert isinstance(params.product, list)
    assert len(params.product) == 2


def test_test_params_from_dict_reference_output_csv():
    params = TestParams.from_dict({"reference_output": ["/ref.csv"]})
    assert params.reference_output is not None
    assert params.reference_output.csv_reference == "/ref.csv"
    assert params.reference_output.netcdf_reference is None


def test_test_params_from_dict_reference_output_nc():
    params = TestParams.from_dict({"reference_output": ["/ref.nc"]})
    assert params.reference_output.netcdf_reference == "/ref.nc"


def test_test_params_from_dict_reference_output_both():
    params = TestParams.from_dict({"reference_output": ["/ref.csv", "/ref.nc"]})
    assert params.reference_output.csv_reference == "/ref.csv"
    assert params.reference_output.netcdf_reference == "/ref.nc"


def test_test_params_from_dict_empty_string():
    params = TestParams.from_dict({"product": ""})
    assert params.product is None


def test_cli_launcher_success():
    with mock.patch("sct.testing.utilities.common.runner") as mock_runner:
        mock_runner.invoke.return_value.exit_code = 0
        cli_launcher(["--help"])
        mock_runner.invoke.assert_called_once()
