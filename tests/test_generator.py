"""Pytest for the `generator.py`"""

import os
import shutil

import pytest
import numpy as np
from PIL import Image

from quantum_pixel import Generator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_unreadable_file():
    """Test raising error when passing an unreadable file."""
    with pytest.raises(Exception):
        Generator(os.path.join("Not", "a", "path.png"))

def test_init():
    """Test the __init__ function"""
    generator = Generator(os.path.join(PROJECT_ROOT, "assets", "material.png"))

    assert isinstance(generator.img_data, np.ndarray)

    # pylint: disable=W0212:protected-access
    assert generator._allowance == -1
    assert generator._remain_allowance == -1

def test_preview():
    """Test the `preview` function"""
    generator = Generator(os.path.join(PROJECT_ROOT, "assets", "material.png"))

    for _ in generator.preview(0.2, os.path.join(PROJECT_ROOT, "tests", "assets", "preview.png")):
        pass
    assert Image.open(os.path.join(PROJECT_ROOT, "tests", "assets", "preview.png"))
    shutil.rmtree(os.path.join(PROJECT_ROOT, "tests", "assets"))
