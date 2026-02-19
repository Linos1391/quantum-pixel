"""Pytest for the `generator.py`"""

import os
import shutil

import pytest
import numpy as np
from PIL import Image

from quantum_pixel import Generator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

def test_unreadable_file():
    """Test raising error when passing an unreadable file."""
    with pytest.raises(Exception):
        Generator("Not/a/path.png")

def test_init():
    """Test the __init__ function"""
    generator = Generator("assets/material.png")

    assert isinstance(generator.img_data, np.ndarray)

    # pylint: disable=W0212:protected-access
    assert generator._allowance == -1
    assert generator._remain_allowance == -1

def test_preview():
    """Test the `preview` function"""
    generator = Generator("assets/material.png")

    for _ in generator.preview(0.2, "tests/assets/preview.png"):
        pass
    assert Image.open("tests/assets/preview.png")
    shutil.rmtree("tests/assets")
