"""
General handy function for drawing
"""

from typing import Tuple, Union
from random import randint


def euclidean_distance(point_one: Tuple[int, int], point_two: Tuple[int, int]) -> float:
    """
    Returns the
    (euclidean distance)[https://en.wikipedia.org/wiki/Euclidean_distance]
    between two points.
    """
    return (
        ((point_one[0] - point_two[0]) ** 2) + ((point_one[1] - point_two[1]) ** 2)
    ) ** 0.5


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
        xy_coords[i] + randint(movement_range[i][0], movement_range[i][1])
        for i in range(2)
    ]
    return tuple(shifted_xy)
