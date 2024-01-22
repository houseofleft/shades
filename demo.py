from shades import Canvas, block_color, ColorMode, gradient, noise_fields

if __name__ == "__main__":
    cool = Canvas(mode=ColorMode.RGB)
    one = block_color((20, 20, 240))
    two = gradient((150, 150, 150))
    (
        Canvas()
        .square(one, (30, 40), 300, rotation=324)
        .line(two, (0, 0), (500, 500), 10)
        .warped_line(one, (0, 0), (500, 500), noise_fields(channels=2), shift=100)
        .show()
    )
