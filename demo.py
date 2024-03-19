from typing import Tuple
from random import choice

from shades import Canvas, block_color

canvas = Canvas(1000, 1000, color=(242, 229, 212))
palette = [
    (222, 152, 189),
    (255, 255, 255),
    (91, 159, 204),
    (206, 90, 51),
    (245, 221, 51),
]

for x, y in canvas.grid(50):
    color = block_color(choice(palette))
    canvas.rectangle(color, (x, y), 25, 10)

canvas.show()
