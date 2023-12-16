from shades import Canvas, block_color, ColorMode, noise_gradient

if __name__ == "__main__":
    """
    cool = Canvas(mode=ColorMode.RGB)
    one = block_color((20, 20, 240))
    two = noise_gradient((150, 150, 150))
    (Canvas()
        .rectangle(one, cool.center, 200, 200)
        .rectangle(two, (0, 0), 100, 300)
        .rectangle(one, (10, 10), 10, 400)
        .square(one, (30, 40), 300)
        .rectangle(two, (600, 400), 100, 100)
        .show()
    )
    """
    import time
    start = time.perf_counter()
    tone = noise_gradient()
    (Canvas(1000, 1000)
        .rectangle(tone, (0, 0), 1000, 1000)
    )
    end = time.perf_counter()
    elapsed = end - start
    print(f"Time: {elapsed:.6f} seconds")

    
