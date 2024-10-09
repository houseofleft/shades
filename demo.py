from random import choice

from shades import Canvas, block_color

canvas = Canvas(1000, 1000, color=(242, 229, 212))
palette = [
    block_color(i)
    for i in [
        (222, 152, 189),
        (255, 255, 255),
        (91, 159, 204),
        (206, 90, 51),
        (245, 221, 51),
    ]
]

# for x, y in canvas.grid(50):
#    color = block_color(choice(palette))
#    canvas.rectangle_outline(color, (x, y), 40, 20, weight=2)

canvas = canvas.for_grid(50).do(
    lambda c, p: c.rectangle_outline(choice(palette), p, 40, 20, weight=2)
)


canvas.show()
