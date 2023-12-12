"""
canvas

contains functions/classes relating to Shades' canvas object
"""
from random import randint, shuffle
from typing import List, Callable, Tuple
from enum import Enum

import numpy as np

from PIL import Image

from .utils import color_clamp

def dummy_test_shade(xy: Tuple[int, int], width: int, height: int) -> np.ndarray:
    """
    Just returns a random color based filling out array
    """
    random_color = [random.ranint(0, 255) for i in range(3)]
    return np.full(
        (height, width, 3),
        random_color,
        dtype=float,
    )

class ColorMode(Enum):
    """
    Enum for supported color modes.
    """
    RGB = "RGB"
    HSL = "HSL"

class Canvas:
    """
    Shades central Canvas object.

    Draws image on self (will help of a shade function)
    and contains methods for displaying / saving etc.
    """

    def __init__(
        self,
        width: int = 700,
        height: int = 700,
        color: Tuple[int] = (240, 240, 240),
    ) -> None:
        """
        Initialise a Canvas object
        """
        self._image_array: np.ndarray = np.full(
            (height, width, 3),
            color,
            dtype=float,
        )
        self.width: int = width
        self.height: int = height
        self.x_center: int = int(self.width/2)
        self.y_center: int = int(self.height/2)
        self.center: Tuple[int, int] = (self.x_center, self.y_center)


    def _render_item(fills: np.ndarray, shade: Callable):
        """
        Render single item.
        
        Fills should be height/width shaped array of 0s and 1s.

        1 being "yes shade in", and 0 being "no thanks!"
        """
        raise NotImplementedError

    def _render_stack(list):
        """
        Render all items on the stack
        """
        raise NotImplementedError
