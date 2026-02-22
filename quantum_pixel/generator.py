# cspell:ignore setdiff, fromarray
"""
Generating layers from an image file.
"""

import logging
import os
from collections.abc import Generator as gen
from random import shuffle, randint

import numpy as np
from PIL import Image

class Generator:
    """
    The generator.
    """
    def __init__(self, input_path: str):
        try: # convert to RGB to remove the only way AI can learn to solve.
            self.img_data = np.array(Image.open(input_path).convert("RGB"))
        except Exception as e:
            logging.error("Error opening image: %s", e)
            raise e
        self._allowance: int = -1
        self._remain_allowance: int = -1

    def receive_current_progress(self):
        """This print out the percentage of completion. Dont know if really need."""
        return int(100*(1-self._remain_allowance/self._allowance))

    def preview(self, intensity: float, output_path: str) -> None:
        """
        Generate the preview layer AND DO NOT STREAM.
        ```
        Generator("Path/to/image.png").preview(0.5, "Path/to/output/image.png"):
        ```

        Args:
            intensity (float): the amount of pixel being taken (0-1). The smaller it is, the \
                faster to process, the harder to visualize. (AI may have the stroke, and so \
                human's eyes)
            output_path (str): Where the file should be saved at.
        """
        assert 0 <= intensity <= 1, "Invalid intensity"

        # [[i, j] for i in range(img_data.shape[0]) for j in range(img_data.shape[1])]
        available_location = np.stack(np.meshgrid(np.arange(self.img_data.shape[0]),
            np.arange(self.img_data.shape[1])), axis=-1).reshape(-1, 2).tolist()
        shuffle(available_location)

        # do the shit.
        self._allowance = int(int(np.sum(self.img_data) * intensity))
        self._remain_allowance = self._allowance

        layer: np.ndarray = np.zeros_like(self.img_data)
        while self._remain_allowance > 0:
            try:
                location = tuple(available_location.pop())
            except IndexError:
                break
            for current_value in range(3): # RGBA channels
                value=min(randint(0, self.img_data[location][current_value]),self._remain_allowance)
                layer[location][current_value] = value
                self._remain_allowance -= value
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        Image.fromarray(layer.astype(np.uint8), "RGB").save(output_path, optimize=True)

    def preview_streaming(self, intensity: float, output_path: str) -> gen[int]:
        """
        Generate the preview layer AND STREAM PROGRESS OUT.
        ```
        generator = Generator("Path/to/image.png")
        for progress in generator.preview_streaming(0.5, "Path/to/output/image.png"):
            print(progress)
        ```


        Args:
            intensity (float): the amount of pixel being taken (0-1). The smaller it is, the \
                faster to process, the harder to visualize. (AI may have the stroke, and so \
                human's eyes)
            output_path (str): Where the file should be saved at.

        Returns:
            collections.abc.Generator[int]: The percentage of completion.
        """
        assert 0 <= intensity <= 1, "Invalid intensity"

        # [[i, j] for i in range(img_data.shape[0]) for j in range(img_data.shape[1])]
        available_location = np.stack(np.meshgrid(np.arange(self.img_data.shape[0]),
            np.arange(self.img_data.shape[1])), axis=-1).reshape(-1, 2).tolist()
        shuffle(available_location)

        # do the shit.
        self._allowance = int(int(np.sum(self.img_data) * intensity))
        self._remain_allowance = self._allowance

        layer: np.ndarray = np.zeros_like(self.img_data)
        while self._remain_allowance > 0:
            try:
                location = tuple(available_location.pop())
            except IndexError:
                break
            for current_value in range(3): # RGBA channels
                value=min(randint(0, self.img_data[location][current_value]),self._remain_allowance)
                layer[location][current_value] = value
                self._remain_allowance -= value
                yield int(100*(1-self._remain_allowance/self._allowance))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        Image.fromarray(layer.astype(np.uint8), "RGB").save(output_path, optimize=True)

if __name__ == "__main__":
    generator = Generator("assets/material.png")
    for progress in generator.preview_streaming(0.5, "assets/preview.png"):
        print(progress)
