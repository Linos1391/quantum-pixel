# cspell:ignore setdiff, fromarray
"""
Generating layers from an image file.
"""

import logging
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

    def _generate(self, image_data: np.ndarray, remove_interacted_data: bool):
        assert self._allowance > 0, "Allowance not set."

        layer: np.ndarray = np.zeros_like(self.img_data)

        # [[i, j] for i in range(img_data.shape[0]) for j in range(img_data.shape[1])]
        available_location = np.stack(np.meshgrid(np.arange(self.img_data.shape[0]),
            np.arange(self.img_data.shape[1])), axis=-1).reshape(-1, 2).tolist()
        shuffle(available_location)

        # do the shit.
        self._remain_allowance = self._allowance

        while self._remain_allowance > 0:
            try:
                location = tuple(available_location.pop())
            except IndexError:
                break
            for current_value in range(3): # RGBA channels
                value = min(randint(0, image_data[location][current_value]), self._remain_allowance)
                if remove_interacted_data:
                    image_data[location][current_value] -= value
                layer[location][current_value] = value
                self._remain_allowance -= value
        return Image.fromarray(layer.astype(np.uint8), "RGB")

    def preview(self, intensity: float) -> Image.Image:
        """
        Generate the preview layer.
        ```
        generator = Generator("Path/to/image.png")
        generator.preview(0.5).show()
        ```


        Args:
            intensity (float): the amount of pixel being taken (0-1). The smaller it is, the \
                faster to process, the harder to visualize. (AI may have the stroke, and so \
                human's eyes)

            
        Returns:
            Image.Image: the preview layer.
        """
        assert 0 <= intensity <= 1, "Invalid intensity"

        self._allowance = int(int(np.sum(self.img_data) * intensity))
        return self._generate(self.img_data, False)

if __name__ == "__main__":
    generator = Generator("assets/material.png")
    generator.preview(0.5).save("assets/mask.png", optimize=True)
