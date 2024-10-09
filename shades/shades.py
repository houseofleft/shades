"""
shades

functions to be used for pixel level color generation with Canvas object
"""

from typing import Tuple, Callable
from functools import cache

import numpy as np

from shades.noise import noise_fields, NoiseField


def block_color(color: Tuple[int, int, int]) -> Callable:
    """
    Creates a shade that shades everything with a block color
    """

    def shade(xy: Tuple[int, int], width: int, height: int) -> np.ndarray:
        """
        shade everything a single block color
        """
        return np.full(
            (height, width, 3),
            color,
            dtype=float,
        )

    return shade


def gradient(
    color: Tuple[int, int, int] = (200, 200, 200),
    color_variance: int = 70,
    color_fields: Tuple[NoiseField, NoiseField, NoiseField] = noise_fields(channels=3),
) -> Callable:
    """
    Creates a shade where colors vary based on noise fields

    color variance relate the amount a color will vary at the maximum
    noise point. color_variance of 100, means that noise will vary the
    tone of each channel (as in RGB) by up to 100.
    """

    def shade(xy: Tuple[int, int], width: int, height: int) -> np.ndarray:
        """
        shade varying based on noise fields
        """
        noise_ranges = np.array(
            [i.noise_range(xy, width, height) for i in color_fields]
        )
        noise_ranges = np.transpose(noise_ranges, (1, 2, 0))
        noise_ranges -= 0.5
        noise_ranges *= color_variance * 2
        colors = np.full((height, width, 3), color, dtype=float)
        # TODO: clamp these colors to 0.1 - 255 range
        return colors + noise_ranges

    return shade


def custom_shade(
    custom_function: Callable[Tuple[int, int], Tuple[int, int, int]],
) -> Callable:
    """
    Convenience function to register a standard (x,y) coord to color function
    as a shade that can be used with the Canvas object.

    N.B. This support literally any python code, but means that
    the code itself won't be vectorized, so involves an inner loop
    that will slow things down a lot.

    Where possible, simply writing a shade to return an np.array will
    provide a big speed-up over this method.
    """

    def shade(xy: Tuple[int, int], width: int, height: int) -> np.ndarray:
        """
        Custom defined shade
        """
        colors = np.array()
        for x in range(xy[0], xy[0] + height):
            row = np.array()
            for y in range(xy[1]):
                np.append(row, custom_function((x, y)))
            np.append(colors, row)
        return colors

    return shade
