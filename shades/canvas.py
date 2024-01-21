"""
canvas

contains functions/classes relating to Shades' canvas object
"""
from typing import Callable, Tuple, List, Optional, Generator, DefaultDict
from enum import Enum
from collections import defaultdict

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
        self.x_center: int = int(self.width / 2)
        self.y_center: int = int(self.height / 2)
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
                    (y, self.height - (height + y)),
                    (x, self.width - (width + x)),
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
        """ """
        self.image().show()

    def save(self, path: str, format: Optional[str] = None, **kwargs) -> None:
        """
        Save image to a given filepath.

        Any additional keyword arguments will be passed to image writer.
        """
        self.image().save(path, format=format, **kwargs)

    def rectangle(
        self,
        shade: Callable,
        xy: Tuple[int, int],
        width: int,
        height: int,
        rotation: int = 0,
    ) -> "Canvas":
        """
        Draw a rectangle on the canvas using the given shade.

        xy point corresponds to top left corner of the rectangle.
        """
        x, y = xy
        array: np.ndarray = np.zeros((self.height, self.width))
        array[y : y + height, x : x + width] = 1
        if rotation != 0:
            array = self.rotate(array, xy, rotation)
        self._stack.append((shade, array))
        return self

    def square(
        self, shade: Callable, xy: Tuple[int, int], size: int, rotation: int = 0
    ) -> "Canvas":
        """
        Draw a square on the canvas using the given shade.

        xy point corresponts to the top left corner of the square.

        Size relates to the height or width (they are the same).
        """
        return self.rectangle(shade, xy, size, size, rotation)

    def line(
        self, shade: Callable, start: Tuple[int, int], end: Tuple[int, int], weight=1
    ) -> "Canvas":
        """
        Draw a line on the canvas using the given shade.
        """
        array: np.ndarray = np.zeros((self.height, self.width))
        for x, y in self._points_in_line(start, end):
            array[y, x : x + weight] = 1
        self._stack.append((shade, array))
        return self

    def _points_in_line(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> Generator[Tuple[int, int], None, None]:
        """
        Get the points in a line, iterating across the y axis
        """
        slope = (end[1] - start[1]) / (end[0] - start[0])
        intercept = start[1] - slope * start[0]
        y_start = min(start[1], end[1])
        y_end = max(start[1], end[1])
        for y in range(y_start, y_end):
            x = int(round(slope * y + intercept))
            yield (x, y)

    def polygon(
        self, shade: Callable, *points: Tuple[int, int], rotation: int = 0
    ) -> "Canvas":
        """
        Draw a polygon on canvas with the given shade.

        Uses ray tracing to determin points within shape, based on matching
        between first points, to second, to third (etc) to first.
        """
        pairs = [
            (point, points[(i + 1) % len(points)]) for i, point in enumerate(points)
        ]
        y_to_x_points: DefaultDict[int, List[int]] = defaultdict(lambda: [])
        for pair in pairs:
            for line_point in self._points_in_line(*pair):
                y_to_x_points[line_point[1]].append(line_point[0])
        array: np.ndarray = np.zeros((self.height, self.width))
        for y in y_to_x_points:
            xs = y_to_x_points[y]
            for start_x, end_x in zip(xs[::2], xs[1::2]):
                array[y, start_x:end_x] = 1
        if rotation != 0:
            array = self.rotate(array, points[0], rotation)
        self._stack.append((shade, array))
        return self

    def circle(self, shade: Callable, center: Tuple[int, int], radius: int) -> "Canvas":
        """
        Draw a circle on canvas with the given shade.
        """
        x, y = center
        i, j = np.ogrid[: self.height, : self.width]
        array: np.ndarray = np.zeros((self.height, self.width))
        array[(i - y) ** 2 + (j - x) ** 2 <= radius**2] = 1
        self._stack.append((shade, array))
        return self

    def rotate(
        self, array: np.ndarray, center: Tuple[int, int], degrees: int
    ) -> np.ndarray:
        radians = np.radians(degrees)
        y_center, x_center = center
        y_size, x_size = array.shape
        i, j = np.ogrid[:y_size, :x_size]
        i_rotated = (
            np.cos(radians) * (i - y_center)
            - np.sin(radians) * (j - x_center)
            + y_center
        )
        j_rotated = (
            np.sin(radians) * (i - y_center)
            + np.cos(radians) * (j - x_center)
            + x_center
        )
        i_rotated = np.round(i_rotated).astype(int)
        j_rotated = np.round(j_rotated).astype(int)
        rotated_grid = np.zeros_like(array)
        mask = (
            (i_rotated >= 0)
            & (i_rotated < y_size)
            & (j_rotated >= 0)
            & (j_rotated < x_size)
        )
        rotated_grid[mask] = array[i_rotated[mask], j_rotated[mask]]

        return rotated_grid
