#Cspell:ignore getbbox
"""Pytest for the `steganography.py`"""

import os
import shutil

import pytest
from PIL import Image, ImageChops

from quantum_pixel import Steganography

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_PATH = os.path.join(PROJECT_ROOT, "assets")
TEST_ASSET_PATH = os.path.join(PROJECT_ROOT, "tests", "assets")

def _same_image(img1: Image.Image, img2: Image.Image):
    return ImageChops.difference(img1, img2).getbbox() is None

def test_encode_overload():
    """Test encoding with unfit disguised image. (too small)"""
    assert Steganography.encode(
        password="",
        input_file_path=os.path.join(ASSET_PATH, "material.png"),
        output_file_path=os.path.join(TEST_ASSET_PATH, "overload.png"),
        disguised_file_path=os.path.join(ASSET_PATH, "intro.png"),
    ).startswith("Capacity Error")

def test_decode_wrong_path():
    """Test decoding wrong path."""
    assert Steganography.decode(
        password="",
        disguise_image=os.path.join("Not", "a", "path.png"),
        output_folder=os.path.join(TEST_ASSET_PATH, "output")
    ) == "Image media is invalid"

def test_decode_normal_file():
    """Test decoding normal file which has no file embedded within."""
    with pytest.raises(BaseException): # Rust Panic.
        Steganography.decode(
            password="",
            disguise_image=os.path.join(ASSET_PATH, "intro.png"),
            output_folder=os.path.join(TEST_ASSET_PATH, "output")
        )

def test_encode_no_password():
    """Test encoding without password."""
    assert Steganography.encode(
        password="",
        input_file_path=os.path.join(ASSET_PATH, "intro.png"),
        output_file_path=os.path.join(TEST_ASSET_PATH, "no_password.png"),
        disguised_file_path=os.path.join(ASSET_PATH, "material.png"),
    ) == ""

def test_decode_no_password():
    """Test decoding without password."""
    assert Steganography.decode(
        password="",
        disguise_image=os.path.join(TEST_ASSET_PATH, "no_password.png"),
        output_folder=os.path.join(TEST_ASSET_PATH, "output")
    ) == ""
    assert _same_image(
        img1=Image.open(os.path.join(ASSET_PATH, "intro.png")),
        img2=Image.open(os.path.join(TEST_ASSET_PATH, "output", "intro.png"))
    )
    shutil.rmtree("tests/assets")

def test_encode_with_password():
    """Test encoding with password."""
    assert Steganography.encode(
        password="supercalifragilisticexpialidocious",
        input_file_path=os.path.join(ASSET_PATH, "intro.png"),
        output_file_path=os.path.join(TEST_ASSET_PATH, "with_password.png"),
        disguised_file_path=os.path.join(ASSET_PATH, "material.png"),
    ) == ""

def test_decode_wrong_password():
    """Test decoding with wrong password."""
    assert Steganography.decode(
        password="serendipitous",
        disguise_image=os.path.join(TEST_ASSET_PATH, "with_password.png"),
        output_folder=os.path.join(TEST_ASSET_PATH, "output")
    ) == "Decryption error"

def test_decode_with_password():
    """Test decoding with password."""
    assert Steganography.decode(
        password="supercalifragilisticexpialidocious",
        disguise_image=os.path.join(TEST_ASSET_PATH, "with_password.png"),
        output_folder=os.path.join(TEST_ASSET_PATH, "output")
    ) == ""
    assert _same_image(
        img1=Image.open(os.path.join(ASSET_PATH, "intro.png")),
        img2=Image.open(os.path.join(TEST_ASSET_PATH, "output", "intro.png"))
    )
    shutil.rmtree(TEST_ASSET_PATH)
