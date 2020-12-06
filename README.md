# Sh🕶️des

## About

Shades is a python module for generative 2d image creation.

The main abstract object is a 'shade' which will determine color based on rules, and contains methods for drawing on images.

The majority of these implement simplex noise fields to determine color resulting in images that will appear different each time they are generated.

Current existing shades are:

* BlockColor
* HorizontalGradient
* VerticalGradient
* PointGradients
* NoiseGradient
* DomainWarpGradient
* SwirlOfShades

All shades have inherit internal methods that can be used for drawing on images.

Current existing methods are:

* rectangle
* triangle
* shape
* circle
* pizza_slice
* fill

## Using Shades

Shades is designed to help make image creation easier. Here's an example:

```python
# First shades is imported along with any required modules
import shades
import random

# The shades.Canvas() function will return a blank PIL image
canvas = shades.Canvas()

# A shade is defined like so the below creates a simplex noise gradent:
shade = shades.NoiseGradient(
    color = (200,200,200),
    noise_fields = [shades.NoiseField(scale=0.02) for i in range(3)],
    warp_size = 50
    warp_noise = (shades.NoiseField(scale=0.005),shades.NoiseField(scale=0.005))
)

# The below for loops draw a grid across the 'canvas' image
for x in range(-50, canvas.width+50, 10):
    shade.line(canvas, (x,-50), (x,canvas.height+50))

for y in range(-50, canvas.height+50, 10):
    shade.line(canvas, (-50,y), (canvas.height+50,y))

# Then normal PIL Image methods like "show" and "save" can be used on the image
canvas.show()
canvas.save('picture.png')
```

# Installing Shades

Shades is pip installable with *python -m pip install shades*
