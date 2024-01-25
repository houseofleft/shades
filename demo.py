from random import random

from shades import Canvas, block_color, ColorMode, gradient, noise_fields

if __name__ == "__main__":
    cool = Canvas(mode=ColorMode.RGB)
    shade = gradient((150, 150, 150))
    canvas = Canvas()
    grid_size = 20
    for x in range(0, canvas.width, grid_size):
        for y in range(0, canvas.height, grid_size):
            if random() > 0.5:
                canvas.line(shade, (x, y), (x+grid_size, y+grid_size), weight=2)
            else:
                canvas.line(shade, (x, y+grid_size), (x+grid_size, y), weight=2)
    canvas.save("nice.png")
    canvas.show()
