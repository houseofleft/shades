"""
canvas

contains functions/classes relating to Shades' canvas object
"""
from typing import Callable, Tuple, List, Optional
from enum import Enum

from PIL import Image
import numpy as np

class ColorMode(Enum):
    """
    Enum for supported color modes.
    """
    RGB = "RGB"
    HSV = "HSV"
    LAB = "LAB"

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
        color: Tuple[int, ...] = (240, 240, 240),
        mode: ColorMode = ColorMode.RGB,
    ) -> None:
        """
        Initialise a Canvas object
        """
        self.mode = mode
        self.width: int = width
        self.height: int = height
        self.x_center: int = int(self.width/2)
        self.y_center: int = int(self.height/2)
        self.center: Tuple[int, int] = (self.x_center, self.y_center)
        self._image_array: np.ndarray = np.full(
            (height, width, 3),
            color,
            dtype=float,
        )
        self._stack: List[Tuple[Callable, np.ndarray]] = []

    def _render_stack(self):
        for shade, area in self._stack:
            nonzero = np.nonzero(area)
            y = np.min(nonzero[0])
            height = np.max(nonzero[0]) - y
            x = np.min(nonzero[1])
            width = np.max(nonzero[1]) - x
            shaded_area = shade((x, y), width, height)
            shaded_area = np.pad(
                shaded_area,
                (
                    (y, self.height-(height+y)),
                    (x, self.width-(width+x)),
                    (0, 0),
                ),
                constant_values=0,
            )
            shaded_area *= np.repeat(area[:, :, np.newaxis], 3, axis=2)
            mask = np.any(shaded_area != 0, axis=-1)
            self._image_array = np.where(
                mask[:, :, np.newaxis],
                shaded_area,
                self._image_array,
            )
        self._stack = []

    def image(self) -> Image:
        """
        Return PIL image directly
        """
        self._render_stack()
        image = Image.fromarray(
            self._image_array.astype("uint8"),
            mode=self.mode.value,
        )
        return image

    def show(self) -> None:
        """
        """
        self.image().show()

    def save(self, path: str, format: Optional[str] = None, **kwargs) -> None:
        """
        Save image to a given filepath.

        Any additional keyword arguments will be passed to image writer.
        """
        self.image().save(path, format=format, **kwargs)

    def rectangle(self, shade: Callable, xy: Tuple[int, int], width: int, height: int) -> "Canvas":
        """
        Draw a rectangle on the canvas using the given shade.

        xy point corresponds to top left corner of the rectangle.
        """
        x, y = xy
        array: np.ndarray = np.zeros((self.height, self.width))
        array[y:y+height, x:x+width] = 1
        self._stack.append((shade, array))
        return self

    def square(self, shade: Callable, xy: Tuple[int, int], size: int) -> "Canvas":
        """
        Draw a square on the canvas using the given shade.

        xy point corresponts to the top left corner of the square.

        Size relates to the height or width (they are the same).
        """
        return self.rectangle(shade, xy, size, size)

    def line(self, shade: Callable, start: Tuple[int, int], end: Tuple[int, int], weight=1) -> "Canvas":
        """
        Draw a line on the canvas using the given shade.
        """
        array: np.ndarray = np.zeros((self.height, self.width))
        slope = (end[1] - start[1]) / (end[0] - start[0])
        intercept = start[1] - slope * start[0]
        y_start = min(start[1], end[1])
        y_end = max(start[1], end[1])
        for y in range(y_start, y_end):
            x = int(round(slope * y + intercept))
            array[y, x:x+weight] = 1
        self._stack.append((shade, array))
        return self


