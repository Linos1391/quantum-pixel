# cspell: ignore stegano, computer-lizing
# pylint: disable=I1101:c-extension-no-member
"""
Do what is needed to be done.
"""

from . import stegano

class Steganography:
    """Encode and decode."""
    @classmethod
    def encode(cls, password: str,
               input_file_path: str,
               output_file_path: str,
               disguised_file_path: str) -> str:
        """
        Encoder.

        Args:
            password (str): Password for the steganography.
            input_file_path (str): The image will be embedded.
            output_file_path (str): Where the output is.
            disguised_file_path (str): The disguised image file data.

        Returns:
            str: Error if there is, will be "" if success. (Use `if` to check!)
        """
        try:
            stegano.encode(password, input_file_path, output_file_path, disguised_file_path)
            return ""
        except OSError as err:
            return str(err)

    @classmethod
    def decode(cls, password: str,
               disguise_image: str,
               output_folder: str) -> str:
        """
        Decoder.

        Args:
            password (str): Password for the steganography.
            disguise_image (str): The image will be decoded.
            output_folder (str): Where the output is (THIS IS FOLDER).
        
        Returns:
            bool: operate successfully.
        """
        try:
            stegano.decode(password, disguise_image, output_folder)
            return ""
        except OSError as err:
            return str(err)
