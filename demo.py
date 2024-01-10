from shades import Canvas, block_color, ColorMode, gradient

if __name__ == "__main__":
    cool = Canvas(mode=ColorMode.RGB)
    one = block_color((20, 20, 240))
    two = gradient((150, 150, 150))
    (Canvas()
        .rectangle(one, cool.center, 200, 200)
        .rectangle(two, (0, 0), 100, 300)
        .rectangle(one, (10, 10), 10, 400)
        .square(one, (30, 40), 300)
        .rectangle(two, (600, 400), 100, 100)
        .line(one, (0, 0), (500, 500), 10)
        .polygon(two, (40, 50), (234, 35), (400, 400))
        .show()
    )
    
