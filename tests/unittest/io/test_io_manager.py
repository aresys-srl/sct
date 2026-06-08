"""Testing IO manager"""

from pathlib import Path

import pytest

from sct.io.io_manager import InvalidProductType, product_loader


def test_product_loader_invalid_product():
    with pytest.raises(InvalidProductType):
        product_loader(Path("nonexistent_product_path"))


def test_product_loader_non_existent_path():
    with pytest.raises(InvalidProductType):
        product_loader(Path("C:/does_not_exist.safe"))
