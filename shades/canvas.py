"""
Functions/Classes relating to Shades' canvas object.

The Canvas class is responsible for most of the actual "drawing" work in shades.
I.e. it works out where a circle should go, and stores information on the
color and shade etc.
"""
from typing import Callable, Tuple, List, Optional, Generator, DefaultDict
from enum import Enum
from collections import defaultdict

from PIL import Image
import numpy as np

from shades.noise import NoiseField
from shades._wrappers import cast_ints


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

    def _compress_and_render_stack(self) -> None:
        """
        Internal method, collapses stack for optimisation and
        then evaluates into image array.

        (the Canvas class is lazily evaluated, so won't calculate
        the image array until it needs to)
        """
        self._compress_stack()
        self._render_stack()

    def _compress_stack(self) -> None:
        """
        Performs optimisation on the stack to allow more efficient
        rendering. Will collapse adjacent and matching shades into
        each other to avoid unecessary draw operations.
        """
        if len(self._stack) == 0:
            return  # nothing to do
        compressed: List[Tuple[Callable, np.ndarray]] = []
        last_index = 0
        for i, item in enumerate(self._stack):
            if item[0] != self._stack[last_index][0]:
                compressed.append(
                    (
                        self._stack[last_index][0],
                        np.maximum.reduce(
                            [i[1] for i in self._stack[last_index : i + 1]]
                        ),
                    )
                )
                last_index = i
        compressed.append(
            (
                self._stack[last_index][0],
                np.maximum.reduce([i[1] for i in self._stack[last_index : i + 1]]),
            )
        )
        self._stack = compressed

    def _render_stack(self) -> None:
        """
        Evalaute stack of shade and shape-fill arrays before emptying internal
        _stack variable.

        This is the method that actually does the final work of converting
        the collected "stack" into a list.
        """
        for shade, area in self._stack:
            nonzero = np.nonzero(area)
            if len(nonzero[0]) == 0:
                continue
            y = np.min(nonzero[0])
            height = np.max(nonzero[0]) - y
            x = np.min(nonzero[1])
            width = np.max(nonzero[1]) - x
            shaded_area = shade((x, y), width, height)
            shaded_area = np.clip(shaded_area, 1, 255)
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
        self._compress_and_render_stack()
        image = Image.fromarray(
            self._image_array.astype("uint8"),
            mode=self.mode.value,
        )
        return image

    def show(self) -> None:
        """
        Show image (using default image show).

        Renders internal image as PIL and shows using ```Image.show()``` method.
        See PIL documentation for more details.
        """
        self.image().show()

    def save(self, path: str, format: Optional[str] = None, **kwargs) -> None:
        """
        Save image to a given filepath.

        Any additional keyword arguments will be passed to image writer.
        """
        self.image().save(path, format=format, **kwargs)

    def _shift_array_points(
        self, array: np.array, warp_noise: Tuple[NoiseField, NoiseField], shift: int
    ) -> np.ndarray:
        """
        Move points in array based on x and y noise fields.

        Shift determines relation between a noise output of "1"
        and movement accross the canvas

        This is, at least currently, implemented as a very slow operation,
        iterating over all non-zero points, and moving them. It'll also
        potentially leave "gaps" - so use carefully, ideally on outlines
        of shapes rather than no the final shape.
        """
        new_array: np.ndarray = np.zeros((self.height, self.width))
        height, width = array.shape
        warp_noise = [i.noise_range((0, 0), height, width) for i in warp_noise]
        warp_noise = [(i - 0.5) * 2 * shift for i in warp_noise]
        y_noise, x_noise = warp_noise
        y_i, x_i = np.indices(array.shape)
        y_noise = y_noise.astype(int) + y_i
        x_noise = x_noise.astype(int) + x_i
        new_locs = np.stack((y_noise, x_noise))
        to_move = np.argwhere(array == 1)
        for y, x in to_move:
            new_x = new_locs[0][y][x]
            new_y = new_locs[1][y][x]
            new_array[new_y][new_x] = 1
        return new_array

    def _points_in_line(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> Generator[Tuple[int, int], None, None]:
        """
        Get the points in a line, iterating across the y axis
        """
        if end[1] == start[1] and end[0] == start[0]:  # point is 0 length
            yield end
            return
        if end[1] == start[1]:  # point only moves over x axis
            x_dir = 1 if start[0] < end[0] else -1
            for x in range(start[0], end[0] + 1, x_dir):
                yield (x, start[1])
            return
        if end[0] == start[0]:  # point only moves over y axis
            y_dir = 1 if start[1] < end[1] else -1
            for y in range(start[1], end[1] + 1, y_dir):
                yield (start[0], y)
            return
        slope = (end[1] - start[1]) / (end[0] - start[0])
        intercept = start[1] - slope * start[0]
        y_start = min(start[1], end[1])
        y_end = max(start[1], end[1])
        y_dir = 1 if y_start < y_end else -1
        for y in range(y_start, y_end + 1, y_dir):
            x = int(round(slope * y + intercept))
            yield (x, y)

    def _rotate(
        self, array: np.ndarray, center: Tuple[int, int], degrees: int
    ) -> np.ndarray:
        """
        Rotate array by degrees around center
        """
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

    @cast_ints
    def grid(
        self,
        x_size: int,
        y_size: Optional[int] = None,
        x_first: bool = True,
    ) -> Generator[Tuple[int, int], None, None]:
        """
        Generator to return x and y coordinates for a grid. Convenience to
        saves either double nested loops or lots of "list(range(canvas.width))"
        type expressions.

        If y_size is None, then will assume to be the same as x_size.

        Leave x_first as true to iterate first through xs, then ys,
        i.e. as if the loops was:
        ```python
        for x in xs:
          for y in ys:
            ...
        ```
        otherwise, making False would be the equivalent of swapping those
        two lines around.

        Here's an example for use to print out the coordinates in a square grid:
        ```python
        for x, y in canvas.grid(10):
            print(x, y)
        ```
        would print (0, 0), (0, 10), (0, 20) etc. . .

        Returned coordinates will always be (x, y) regardless of `x_first`.
        """
        y_size = y_size or x_size
        first, second = (
            (self.width, self.height) if x_first else (self.height, self.width)
        )
        first_i, second_i = (x_size, y_size) if x_first else (y_size, x_size)
        for i in range(0, first + 1, first_i):
            for j in range(0, second + 1, second_i):
                if x_first:
                    yield (i, j)
                else:
                    yield (j, i)

    @cast_ints
    def rectangle(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        height: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a rectangle on the canvas using the given shade.

        corner point corresponds to top left corner of the rectangle.
        """
        x, y = corner
        array: np.ndarray = np.zeros((self.height, self.width))
        array[y : y + height, x : x + width] = 1
        if rotation != 0:
            rotate_on = rotate_on or corner
            array = self._rotate(array, rotate_on, rotation)
        self._stack.append((shade, array))
        return self

    @cast_ints
    def warped_rectangle(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        height: int,
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a rectangle warped by noise fields on the canvas using the given shade.

        Corner point corresponds to top left corner of the rectangle.
        """
        x, y = corner
        return self.warped_polygon(
            shade,
            (x, y),
            (x, y + height),
            (x + width, y + height),
            (x + width, y),
            warp_noise=warp_noise,
            shift=shift,
            rotation=rotation,
            rotate_on=rotate_on,
        )

    @cast_ints
    def rectangle_outline(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        height: int,
        rotation: int = 0,
        weight: int = 1,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a rectangle outline on the canvas using the given shade.

        corner point corresponds to top left corner of the rectangle.
        """
        x, y = corner
        self.line(
            shade,
            corner,
            (x, y + height),
            weight=weight,
            rotation=rotation,
            rotate_on=rotate_on,
        )
        self.line(
            shade,
            corner,
            (x + width, y),
            weight=weight,
            rotation=rotation,
            rotate_on=rotate_on,
        )
        self.line(
            shade,
            (x, y + height),
            (x + width, y + height),
            weight=weight,
            rotation=rotation,
            rotate_on=rotate_on,
        )
        self.line(
            shade,
            (x + width, y),
            (x + width, y + height),
            weight=weight,
            rotation=rotation,
            rotate_on=rotate_on,
        )
        return self

    @cast_ints
    def warped_rectangle_outline(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        height: int,
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
        weight: int = 1,
    ) -> "Canvas":
        """
        Draw a rectangle outline, warped by noise fields, on the canvas using the given shade.

        corner point corresponds to top left corner of the rectangle.
        """
        x, y = corner
        return self.warped_polygon_outline(
            shade,
            (x, y),
            (x, y + height),
            (x + width, y + height),
            (x + width, y),
            warp_noise=warp_noise,
            shift=shift,
            rotation=rotation,
            rotate_on=rotate_on,
            weight=weight,
        )

    @cast_ints
    def square(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a square on the canvas using the given shade.

        corver point corresponts to the top left corner of the square.

        Size relates to the height or width (they are the same).
        """
        return self.rectangle(shade, corner, width, width, rotation, rotate_on)

    @cast_ints
    def warped_square(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a square, warped by noise on the canvas using the given shade.

        corver point corresponts to the top left corner of the square.

        Size relates to the height or width (they are the same).
        """
        return self.warped_rectangle(
            shade=shade,
            corner=corner,
            width=width,
            height=width,
            warp_noise=warp_noise,
            shift=shift,
            rotation=rotation,
            rotate_on=rotate_on,
        )

    @cast_ints
    def square_outline(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        rotation: int = 0,
        weight: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a rectangle outline on the canvas using the given shade.

        corner point corresponds to top left corner of the rectangle.
        """
        return self.rectangle_outline(
            shade=shade,
            corner=corner,
            width=width,
            height=width,
            rotation=rotation,
            weight=weight,
            rotate_on=rotate_on,
        )

    @cast_ints
    def warped_square_outline(
        self,
        shade: Callable,
        corner: Tuple[int, int],
        width: int,
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        weight: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a rectangle outline on the canvas using the given shade.

        corner point corresponds to top left corner of the rectangle.
        """
        return self.warped_rectangle_outline(
            shade=shade,
            corner=corner,
            width=width,
            height=width,
            warp_noise=warp_noise,
            shift=shift,
            rotation=rotation,
            weight=weight,
            rotate_on=rotate_on,
        )

    @cast_ints
    def line(
        self,
        shade: Callable,
        start: Tuple[int, int],
        end: Tuple[int, int],
        weight: int = 1,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a line on the canvas using the given shade.
        """
        array: np.ndarray = np.zeros((self.height, self.width))
        for x, y in self._points_in_line(start, end):
            array[y : y + weight, x : x + weight] = 1
        if rotation != 0:
            rotate_on = rotate_on or start
            array = self._rotate(array, rotate_on, rotation)
        self._stack.append((shade, array))
        return self

    @cast_ints
    def warped_line(
        self,
        shade: Callable,
        start: Tuple[int, int],
        end: Tuple[int, int],
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        weight: int = 1,
    ) -> "Canvas":
        """
        Draw a line, warped by noise fields, on the canvas using the
        given shade.
        """
        array: np.ndarray = np.zeros((self.height, self.width))
        for x, y in self._points_in_line(start, end):
            array[y, x : x + weight] = 1
        array = self._shift_array_points(array, warp_noise, shift)
        self._stack.append((shade, array))
        return self

    def polygon(
        self,
        shade: Callable,
        *points: Tuple[int, int],
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a polygon on canvas with the given shade.

        Uses ray tracing to determine points within shape, based on matching
        between first points, to second, to third (etc) to first.
        """
        # casting ints
        points = [int(i) for i in points]
        rotation = int(rotation)
        if rotate_on:
            rotate_on = (int(rotate_on[0]), int(rotate_on[1]))
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
            rotate_on = rotate_on or points[0]
            array = self._rotate(array, rotate_on, rotation)
        self._stack.append((shade, array))
        return self

    def warped_polygon(
        self,
        shade: Callable,
        *points: Tuple[int, int],
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        """
        Draw a polygon, warped by noise, on canvas with the given shade.

        Uses ray tracing to determine points within shape, based on matching
        between first points, to second, to third (etc) to first.
        """
        # casting ints
        points = [int(i) for i in points]
        rotation = int(rotation)
        if rotate_on:
            rotate_on = (int(rotate_on[0]), int(rotate_on[1]))
        pairs = [
            (point, points[(i + 1) % len(points)]) for i, point in enumerate(points)
        ]
        new_points: List[Tuple[int, int]] = []
        for pair in pairs:
            for point in self._points_in_line(*pair):
                new_points.append(point)
        return self.polygon(shade, *new_points, warp_noise, shift, rotation, rotate_on)


    def polygon_outline(
        self,
        shade: Callable,
        *points: Tuple[int, int],
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
        weight: int = 1,
    ) -> "Canvas":
        """
        Draw a polygon outline on canvas with the given shade.

        Uses ray tracing to determine points within shape, based on matching
        between first points, to second, to third (etc) to first.
        """
        # casting ints
        points = [int(i) for i in points]
        rotation = int(rotation)
        if rotate_on:
            rotate_on = (int(rotate_on[0]), int(rotate_on[1]))
        weight = int(weight)
        pairs = [
            (point, points[(i + 1) % len(points)]) for i, point in enumerate(points)
        ]
        rotate_on = rotate_on or points[0]
        for point_one, point_two in pairs:
            self.line(
                shade,
                start=point_one,
                end=point_two,
                weight=weight,
                rotation=rotation,
                rotate_on=rotate_on,
            )
        return self

    def warped_polygon_outline(
        self,
        shade: Callable,
        *points: Tuple[int, int],
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
        weight: int = 1,
    ) -> "Canvas":
        """
        Draw a polygon outline, warped by noise, on canvas with the given shade.

        Uses ray tracing to determine points within shape, based on matching
        between first points, to second, to third (etc) to first.
        """
        # casting ints
        points = [int(i) for i in points]
        rotation = int(rotation)
        if rotate_on:
            rotate_on = (int(rotate_on[0]), int(rotate_on[1]))
        weight = int(weight)
        pairs = [
            (point, points[(i + 1) % len(points)]) for i, point in enumerate(points)
        ]
        rotate_on = rotate_on or points[0]
        for point_one, point_two in pairs:
            self.warped_line(
                shade,
                start=point_one,
                end=point_two,
                weight=weight,
                rotation=rotation,
                rotate_on=rotate_on,
                warp_noise=warp_noise,
                shift=shift,
            )
        return self

    @cast_ints
    def triangle(
        self,
        shade: Callable,
        point_one: Tuple[int, int],
        point_two: Tuple[int, int],
        point_three: Tuple[int, int],
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        return self.polygon(
            shade,
            point_one,
            point_two,
            point_three,
            rotation=rotation,
            rotate_on=rotate_on,
        )

    @cast_ints
    def warped_triangle(
        self,
        shade: Callable,
        point_one: Tuple[int, int],
        point_two: Tuple[int, int],
        point_three: Tuple[int, int],
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
    ) -> "Canvas":
        return self.warped_polyon(
            shade,
            point_one,
            point_two,
            point_three,
            warp_noise=warp_noise,
            shift=shift,
            rotation=rotation,
            rotate_on=rotate_on,
        )

    @cast_ints
    def triangle_outline(
        self,
        shade: Callable,
        point_one: Tuple[int, int],
        point_two: Tuple[int, int],
        point_three: Tuple[int, int],
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
        weight: int = 1,
    ) -> "Canvas":
        return self.polyon_outline(
            shade, point_one, point_two, point_three, rotation=rotation, weight=weight,
        )

    @cast_ints
    def warped_triangle_outline(
        self,
        shade: Callable,
        point_one: Tuple[int, int],
        point_two: Tuple[int, int],
        point_three: Tuple[int, int],
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        rotation: int = 0,
        rotate_on: Optional[Tuple[int, int]] = None,
        weight: int = 1,
    ) -> "Canvas":
        return self.warped_polyon_outline(
            shade,
            point_one,
            point_two,
            point_three,
            warp_noise=warp_noise,
            shift=shift,
            rotation=rotation,
            rotate_on=rotate_on,
            weight=weight,
        )

    @cast_ints
    def circle(
        self,
        shade: Callable,
        center: Tuple[int, int],
        radius: int,
    ) -> "Canvas":
        """
        Draw a circle on canvas with the given shade.
        """
        x, y = center
        i, j = np.ogrid[: self.height, : self.width]
        array: np.ndarray = np.zeros((self.height, self.width))
        array[(i - y) ** 2 + (j - x) ** 2 <= radius**2] = 1
        self._stack.append((shade, array))
        return self

    def _circle_edge_points(self, center: Tuple[int, int], radius: int):
        circumference = radius*2
        return [
            (
                center[0] + radius * np.cos(2*np.pi*i/circumference),
                center[1] + radius * np.sin(2*np.pi*i/circumference)
            ) for i in range(circumference)
        ]


    @cast_ints
    def warped_circle(
        self,
        shade: Callable,
        center: Tuple[int, int],
        radius: int,
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
    ) -> "Canvas":
        outline_points = self._circle_edge_points(center, radius)
        return self.warped_polygon(shade, *outline_points, warp_noise=warp_noise, shift=shift)

    @cast_ints
    def circle_outline(
        self,
        shade: Callable,
        center: Tuple[int, int],
        radius: int,
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        weight: int = 1,
    ) -> "Canvas":
        """
        Draw a circle on canvas with the given shade.
        """
        outline_points = self._circle_edge_points(center, radius)
        return self.polygon_outline(shade, *outline_points, weight=weight)

    @cast_ints
    def warped_circle_outline(
        self,
        shade: Callable,
        center: Tuple[int, int],
        radius: int,
        warp_noise: Tuple[NoiseField, NoiseField],
        shift: int,
        weight: int = 1,
    ) -> "Canvas":
        outline_points = self._circle_edge_points(center, radius)
        return self.warped_polygon_outline(shade, *outline_points, warp_noise=warp_noise, shift=shift, weight=weight)
