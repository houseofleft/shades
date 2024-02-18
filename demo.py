from typing import Tuple
from random import random, choice

from shades import Canvas, block_color, gradient

CANVAS = Canvas(1000, 1000, color=(242, 229, 212))
PALETTE = [
    (222, 152, 189),
    (255, 255, 255),
    (91, 159, 204),
    (206, 90, 51),
    (245, 221, 51),
]

def nice_shape(xy: Tuple[int, int], width: int, height: int, depth: int, axis=True) -> None:
    color = block_color(choice(PALETTE))
    x, y = xy
    if depth <= 0:
        return CANVAS.rectangle(
            color,
            (int(x), int(y)),
            int(width),
            int(height),
        )
    divide_by = choice([2, 3, 4])
    if axis:
        draw_on = int(width / divide_by)
        CANVAS.rectangle(
            color,
            (int(x), int(y)),
            int(draw_on),
            int(height),
        )
        return nice_shape((int(x+draw_on), y), int(width-draw_on), height, depth-1, not axis) 
    else:
        draw_on = height / divide_by
        CANVAS.rectangle(
            color,
            (int(x), int(y)),
            int(width),
            int(draw_on),
        )
        return nice_shape((x, y+draw_on), width, height-draw_on, depth-1, not axis) 


total_grid_size = int(CANVAS.width / 2)
padding = int((total_grid_size * 0.2) / 2)
size = int(total_grid_size * 0.8)
depth = 0
for x, y in CANVAS.grid(total_grid_size):
    nice_shape((x+padding, y+padding), size-padding, size-padding, depth)
    CANVAS.square_outline(
        block_color((0, 0, 0)),
          (x+padding, y+padding),
           size-padding-2,
        weight=3,
    )
    depth += 1


CANVAS.show()
