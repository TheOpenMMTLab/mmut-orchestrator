# fixtures
import os
import pytest
from pathlib import Path
from unittest import mock


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture()
def data_dir():
    yield Path(TEST_DIR) / "data"



