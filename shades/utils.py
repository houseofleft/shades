"""
utils

contains general purpose functions for use within or outside module
"""
from typing import Tuple, Union
from random import randint


def color_clamp(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Ensures a three part iterable is a properly formatted color
    (i.e. all numbers between 0 and 255)
    """
    clamped_color = [max(min(int(i), 255), 0) for i in color]
    return tuple(clamped_color)


def distance_between_points(xy1: Tuple[int, int], xy2: Tuple[int, int]) -> float:
    """
    Returns the euclidean distance between two points.
    https://en.wikipedia.org/wiki/Euclidean_distance
    """
    return (((xy1[0] - xy2[0]) ** 2) + ((xy1[1] - xy2[1]) ** 2)) ** 0.5


def randomly_shift_point(
        xy_coords: Tuple[int, int],
        movement_range: Union[Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]],
    ) -> Tuple[int, int]:
    """
    Randomly shifts a point within defined range

    movement range of form:
    (min amount, max amount)

    you can give two movement ranges for:
    [(min amount on x axis, max amount on x axis),
    (min amount on y axis, max amount on y axis)]
    or just one, if you want equal ranges
    """
    if type(movement_range[0]) not in [list, tuple]:
        movement_range = [movement_range, movement_range]

    shifted_xy = [
        xy_coords[i] +
        randint(movement_range[i][0], movement_range[i][1])
        for i in range(2)
    ]
    return tuple(shifted_xy)
