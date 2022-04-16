import shades

canvas = shades.Canvas()
swirl = shades.SwirlOfShades(
           shades=[
                (0.4, 0.6, shades.BlockColor()),
            ],
            swirl_field=shades.NoiseField(scale=0.01),
)

swirl.fill(canvas)

canvas.show()
