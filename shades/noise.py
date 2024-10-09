"""
noise_fields

Functions and classes relating to Shades' NoiseField
"""

import random
import math

from typing import List, Tuple, Union

import numpy as np

from numpy.typing import ArrayLike


class NoiseField:
    """
    An object to calculate and store perlin noise data.

    Initialisation takes float (recommend very low number < 0.1)
    and random seed
    """

    def __init__(self, scale: float = 0.002, seed: int = None) -> None:
        if seed is None:
            self.seed = random.randint(0, 9999)
        else:
            self.seed = seed
        self.scale = scale
        size = 10
        self.x_lin = np.linspace(0, (size * self.scale), size, endpoint=False)
        self.y_lin = np.linspace(0, (size * self.scale), size, endpoint=False)
        self.field = self._perlin_field(self.x_lin, self.y_lin)
        self.x_negative_buffer = 0
        self.y_negative_buffer = 0
        self.buffer_chunks = 500

    def _roundup(self, to_round: float, nearest_n: float) -> float:
        """
        Internal function to round up number to_round to nearest_n
        """
        return int(math.ceil(to_round / nearest_n)) * nearest_n

    def _buffer_field_right(self, to_extend: int) -> None:
        """
        Extends object's noise field right
        """
        # y is just gonna stay the same, but x needs to be picking up
        max_lin = self.x_lin[-1]

        additional_x_lin = np.linspace(
            max_lin + self.scale,
            max_lin + (to_extend * self.scale),
            to_extend,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self.field, self._perlin_field(additional_x_lin, self.y_lin)],
            axis=1,
        )
        self.x_lin = np.concatenate([self.x_lin, additional_x_lin])

    def _buffer_field_bottom(self, to_extend: int) -> None:
        """
        Extends object's noise field downwards
        """
        max_lin = self.y_lin[-1]
        additional_y_lin = np.linspace(
            max_lin + self.scale,
            max_lin + (to_extend * self.scale),
            to_extend,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self.field, self._perlin_field(self.x_lin, additional_y_lin)],
            axis=0,
        )
        self.y_lin = np.concatenate([self.y_lin, additional_y_lin])

    def _buffer_field_left(self, to_extend: int) -> None:
        """
        Extends object's noise field left
        """
        min_lin = self.x_lin[0]
        additional_x_lin = np.linspace(
            min_lin - (to_extend * self.scale),
            min_lin,
            to_extend,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self._perlin_field(additional_x_lin, self.y_lin), self.field],
            axis=1,
        )
        self.x_lin = np.concatenate([additional_x_lin, self.x_lin])
        self.x_negative_buffer += to_extend

    def _buffer_field_top(self, to_extend: int) -> None:
        """
        Extends object's noise field upwards
        """
        min_lin = self.y_lin[0]
        additional_y_lin = np.linspace(
            min_lin - (to_extend * self.scale),
            min_lin,
            to_extend,
            endpoint=False,
        )
        self.field = np.concatenate(
            [self._perlin_field(self.x_lin, additional_y_lin), self.field],
            axis=0,
        )
        self.y_lin = np.concatenate([additional_y_lin, self.y_lin])
        self.y_negative_buffer += to_extend

    def _perlin_field(self, x_lin: List[float], y_lin: List[float]) -> ArrayLike:
        """
        generate field from x and y linear points

        credit to tgirod for stack overflow on numpy perlin noise (most of this code from answer)
        https://stackoverflow.com/questions/42147776/producing-2d-perlin-noise-with-numpy
        """
        # remembering the random state (so we can put it back after)
        initial_random_state = np.random.get_state()
        x_grid, y_grid = np.meshgrid(x_lin, y_lin)
        x_grid %= 512
        y_grid %= 512
        # permutation table
        np.random.seed(self.seed)
        field_256 = np.arange(256, dtype=int)
        np.random.shuffle(field_256)
        field_256 = np.stack([field_256, field_256]).flatten()
        # coordinates of the top-left
        x_i, y_i = x_grid.astype(int), y_grid.astype(int)
        # internal coordinates
        x_f, y_f = x_grid - x_i, y_grid - y_i
        # fade factors
        u_array, v_array = self._fade(x_f), self._fade(y_f)
        # noise components
        n00 = self._gradient(field_256[(field_256[x_i % 512] + y_i) % 512], x_f, y_f)
        n01 = self._gradient(
            field_256[(field_256[x_i % 512] + y_i + 1) % 512], x_f, y_f - 1
        )
        n11 = self._gradient(
            field_256[(field_256[((x_i % 512) + 1) % 512] + y_i + 1) % 512],
            x_f - 1,
            y_f - 1,
        )
        n10 = self._gradient(
            field_256[(field_256[((x_i % 512) + 1) % 512] + y_i) % 512], x_f - 1, y_f
        )
        # combine noises
        x_1 = self._lerp(n00, n10, u_array)
        x_2 = self._lerp(n01, n11, u_array)
        # putting the random state back in place
        np.random.set_state(initial_random_state)
        field = self._lerp(x_1, x_2, v_array)
        field += 0.5
        return field

    def _lerp(
        self, a_array: ArrayLike, b_array: ArrayLike, x_array: ArrayLike
    ) -> ArrayLike:
        "linear interpolation"
        return a_array + x_array * (b_array - a_array)

    def _fade(self, t_array: ArrayLike) -> ArrayLike:
        "6t^5 - 15t^4 + 10t^3"
        return 6 * t_array**5 - 15 * t_array**4 + 10 * t_array**3

    def _gradient(
        self, h_array: ArrayLike, x_array: ArrayLike, y_array: ArrayLike
    ) -> ArrayLike:
        "grad converts h to the right gradient vector and return the dot product with (x,y)"
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        g_array = vectors[h_array % 4]
        return g_array[:, :, 0] * x_array + g_array[:, :, 1] * y_array

    def _noise(self, xy_coords: Tuple[int, int]):
        """
        Returns noise of xy coords
        Also manages noise_field (will dynamically recalcuate as needed)
        """
        if self.scale == 0:
            return 0
        x_coord, y_coord = xy_coords
        x_coord += self.x_negative_buffer
        y_coord += self.y_negative_buffer
        if x_coord < 0:
            # x negative buffer needs to be increased
            x_to_backfill = self._roundup(abs(x_coord), self.buffer_chunks)
            self._buffer_field_left(x_to_backfill)
            x_coord, y_coord = xy_coords
            x_coord += self.x_negative_buffer
            y_coord += self.y_negative_buffer
        if y_coord < 0:
            # y negative buffer needs to be increased
            y_to_backfill = self._roundup(abs(y_coord), self.buffer_chunks)
            self._buffer_field_top(y_to_backfill)
            x_coord, y_coord = xy_coords
            x_coord += self.x_negative_buffer
            y_coord += self.y_negative_buffer
        try:
            return self.field[int(y_coord)][int(x_coord)]
        except IndexError:
            # ran out of generated noise, so need to extend the field
            height, width = self.field.shape
            x_to_extend = x_coord - width + 1
            y_to_extend = y_coord - height + 1
            if x_to_extend > 0:
                x_to_extend = self._roundup(x_to_extend, self.buffer_chunks)
                self._buffer_field_right(x_to_extend)
            if y_to_extend > 0:
                y_to_extend = self._roundup(y_to_extend, self.buffer_chunks)
                self._buffer_field_bottom(y_to_extend)
            return self._noise(xy_coords)

    def noise_range(self, xy: Tuple[int, int], width: int, height: int):
        """
        Return noise values for a given grid (starting at point xy)
        and covering the stated width and height
        """
        xy_coords = xy
        x_coord, y_coord = xy
        x_coord += width
        y_coord += height
        x_coord += self.x_negative_buffer
        y_coord += self.y_negative_buffer
        if x_coord < 0:
            # x negative buffer needs to be increased
            x_to_backfill = self._roundup(abs(x_coord), self.buffer_chunks)
            self._buffer_field_left(x_to_backfill)
            x_coord, y_coord = xy_coords
            x_coord += self.x_negative_buffer
            y_coord += self.y_negative_buffer
        if y_coord < 0:
            # y negative buffer needs to be increased
            y_to_backfill = self._roundup(abs(y_coord), self.buffer_chunks)
            self._buffer_field_top(y_to_backfill)
            x_coord, y_coord = xy_coords
            x_coord += self.x_negative_buffer
            y_coord += self.y_negative_buffer
        try:
            _ = self._noise((xy[0] + width, xy[1] + height))
            return self.field[
                int(xy[1]) : int(xy[1]) + height, int(xy[0]) : int(xy[0]) + width
            ]
        except IndexError:
            # ran out of generated noise, so need to extend the field
            height, width = self.field.shape
            x_to_extend = x_coord - width + 1
            y_to_extend = y_coord - height + 1
            if x_to_extend > 0:
                x_to_extend = self._roundup(x_to_extend, self.buffer_chunks)
                self._buffer_field_right(x_to_extend)
            if y_to_extend > 0:
                y_to_extend = self._roundup(y_to_extend, self.buffer_chunks)
                self._buffer_field_bottom(y_to_extend)
            return self.noise_range(xy, width, height)


def noise_fields(
    scale: Union[List[float], float] = 0.002,
    seed: Union[List[int], int] = None,
    channels: int = 3,
) -> List[NoiseField]:
    """
    Create multiple NoiseField objects in one go.
    This is a quality of life function, rather than adding new behaviour
    shades.noise_fields(scale=0.2, channels=3) rather than
    [shades.NoiseField(scale=0.2) for i in range(3)]
    """

    if not isinstance(scale, list):
        scale = [scale for i in range(channels)]
    if not isinstance(seed, list):
        seed = [seed for i in range(channels)]

    return [NoiseField(scale=scale[i], seed=seed[i]) for i in range(channels)]
