"""Pytest for the `generator.py`"""

import os
import shutil

import pytest
import numpy as np
from PIL import Image

from quantum_pixel import Generator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_PATH = os.path.join(PROJECT_ROOT, "assets")
TEST_ASSET_PATH = os.path.join(PROJECT_ROOT, "tests", "assets")

def test_unreadable_file():
    """Test raising error when passing an unreadable file."""
    with pytest.raises(Exception):
        Generator(os.path.join("Not", "a", "path.png"))

def test_init():
    """Test the __init__ function"""
    generator = Generator(os.path.join(ASSET_PATH, "material.png"))

    assert isinstance(generator.img_data, np.ndarray)

    # pylint: disable=W0212:protected-access
    assert generator._allowance == -1
    assert generator._remain_allowance == -1

def test_preview():
    """Test the `preview` function"""
    generator = Generator(os.path.join(ASSET_PATH, "material.png"))
    generator.preview(0.2, os.path.join(TEST_ASSET_PATH, "preview.png"))

    assert Image.open(os.path.join(TEST_ASSET_PATH, "preview.png"))
    shutil.rmtree(TEST_ASSET_PATH)
