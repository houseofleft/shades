# Sh🕶️des


## About

Shades is a python module for generative 2d image creation.

[Latest version is available via pip install](https://pypi.org/project/shades/)

[Full reference documentation is available here!](https://shades.readthedocs.io/en/latest/) 🥳

It might be helpful to read the below guide first as an intro.


## Handy Guide

The shades module is based around a few key objects:
* Canvas (basically just a PIL image, with a couple of additions)
* Shade (determine color based on rules, have methods to draw on canvas)
* NoiseField (calculates Perlin noise based on xy coords)


### Canvas

The *Canvas* object is just a wrapper for a PIL image object (with some minor functionalities added in like Canvas.random_point() and Canvas.center).
The idea is that you don't have to import two libraries all the time, but if you'd prefer, you can switch out the *Canvas* call for a PIL image one. This is useful to know as well if you'd like to work between the two modules, or import images/photos to draw on or use with **Shades**.

Here's a simple example using just the *Canvas* object:
```python
import shades

canvas = shades.Canvas(width=100, height=100, color=(200, 0, 0))

canvas.save('exciting_red_square.png')
canvas.show()
```

This script will save, and bring up the following image:

![Red square](https://github.com/benrutter/Shades/blob/main/images/red_canvas.png)

Not too exciting, right? We created a monotone red image that is 100 by 100 pixels. Color is worth taking note, as throughout **Shades** colors are treated and expected to be tuples of the Red, Green and Blue color values (on a scale of 0 to 255). So (200, 0, 0) gives us a red tone.

There's not much else you can do with *Canvas*, the idea is just to give us an image *on which we can draw stuff*.


### NoiseField

*NoiseField* is a pretty handy concept here. A lot of the time with images, we might want an element of randomness, but with a gentler transition. *NoiseField* is the answer to this, as it gives us random gradients between numbers. [There's more resources online about Perlin noise itself if you're interested- t's a really cool topic](https://en.wikipedia.org/wiki/Perlin_noise)

Here's an example of a simple *NoiseField* use:

```python
import shades

noise_field = shades.NoiseField(scale=0.002, seed=8)
random_number = noise_field.noise((24, 100))
```

In this, *random_number* is the return of the 'noise' call, which takes in coordinates (in the form of an (x, y) tuple) and spits out a float between 0 and 1. The important thing about *NoiseField* vs purely random number generation, is that if we get the return of a nearby point, say (25, 101), then the float between 0 and 1 will be close to our first call. The further away from the point we get, the further away the noise value is likely to be.

When creating a *NoiseField*, the two arguments we can put in are *scale* (which affected how quickly generated numbers will change between points, and 'seed' which is used for generating the semi-random numbers)

**Shades** uses numpy to calculate perlin noise, and tries to strike a balance between frontloading noise-fields (so they can be batch calculated with vectorisation) and calculating as it goes (so that you're not waiting ages for something that'll never be used).

One quality of life feature that's worth mentioning is the *noise_fields* function that works as follows:

```python
import shades
noise_fields = shades.noise_fields(seed=[4, 4, 9], scale=[0.04, 0.2, 0.002], channels=3)
more_fields = shades.noise_fields(scale=0.002, channels=2)
```

This doesn't introduce new functionality, but in a lot of cases (like with working with color, or x/y coordinates) you'll want multiple noise fields (and might want to specify seeds or scales, or leave them blank for defaults), so this is a handy way of doing that without lots of repetitive calls.


### Shade

The *Shade* object as you'd guess in a module called **Shades** does pretty much all the work. You can think of them as like code-pencils - they have properties that affect what color stuff will be, and a bunch of methods to let us draw stuff.

Here's a simple example using a *BlockColor* shade, that'll always produce the same color:
```python
import shades

canvas = shades.Canvas(200, 200)
cyan = shades.BlockColor((0, 255, 255))
cyan.rectangle(canvas, (50, 50), width=100, height=150)

canvas.show()
```

This script does a few things:
- Creates a *Canvas* to draw on
- Creates a *BlockColor* shade to draw with
- Draws a rectangle with the *BlockColor* object on coordinates (50, 50) of the *Canvas*
- Displays the canvas

This is what the picture will look like:

![A cyan rectangle](https://github.com/benrutter/Shades/blob/main/images/cyan_rectangle.png)

A lot of *Shade* objects use *NoiseField*, for example, the *NoiseGradient* object which chooses color based on noise responses to (x,y) coordinates. Which we can see here:
```python
import shades

canvas = shades.Canvas(200, 200)
gradient = shades.NoiseGradient(
  color=(200, 200, 200),
  noise_fields=shades.noise_fields(scale=0.02, channels=3),
)
gradient.circle(
  canvas,
  canvas.center,
  radius=50,
)

canvas.show()
```
(There are three *NoiseField* objects taken by the *noise_field* parameter, one for red, green and blue, using the same *NoiseField* seed for each would create a gradient that changes how light/dark the color is without affecting the overall tone)

![A gradient circle](https://github.com/benrutter/Shades/blob/main/images/gradient_circle.png)

Also, all *Shade* objects can be called with 'warp_noise' that will use noise to affect the location of points:
```python
import shades

canvas = shades.Canvas(200, 200)

warped_shade = shades.BlockColor(
  color=(100, 200, 100),
  warp_size=50,
  warp_noise=shades.noise_fields(scale=0.01, channels=3)
)

warped_shade.line(canvas,(0, 0), (canvas.width, canvas.height))

canvas.show()
```
(the line's location is affected by the two *NoiseField* relating to x and y warping, giving us a wavy green line)

![A wavy green line](https://github.com/benrutter/Shades/blob/main/images/squiggly_line.png)


### Hacking Shades

One of the goals of the *Shade* object, is to make something that's easily extensible. You can create your own *Shade* and already have access to the drawing methods and location warping that are present in the abstract base class of the *Shade*.

The only requirement of creating a *Shade* is to include a method *determine_shade*, taking only (x,y) coordinates as an argument, and returning a color.

Here's an example of creating a shade that returns a completely random shade of grey each time:
```python
import shades
from random import randint

class RandomGrey(shades.Shade):
  def determine_shade(self, xy):
    mono = randint(0, 255)
    return (mono, mono, mono)

canvas = shades.Canvas(300,300)
my_shade = RandomGrey()

my_shade.triangle(canvas, (0, 0), (0, 300), (300, 150))

canvas.show()
```
![A triangle with varying shades of grey](https://github.com/benrutter/Shades/blob/main/images/grey_triangle.png)


### Examples

Here's a few examples of some short scripts and the images they create.

**Using SwirlOfShades which will choose another shade based on NoiseField returns**
```python
import shades

canvas = shades.Canvas()
shade = shades.SwirlOfShades(
  noise_field=shades.NoiseField(scale=0.005),
  shades=([
    (0.4, 0.6, shades.BlockColor((63, 151, 197)))
  ]),
)

shade.fill(canvas)
canvas.show()
```
![Ripples](https://github.com/benrutter/Shades/blob/main/images/ripple.png)


**Drawing a circle using a DomainWarpGradient object**
```python
import shades

canvas = shades.Canvas()

shade = shades.DomainWarpGradient(
    color=(200,200,200),
    color_variance=70,
    noise_fields=shades.noise_fields(scale=0.01, channels=3),
    depth=2,
)

shade.circle(canvas, canvas.center, canvas.width/3)

canvas.show()
```
![Domain warped circle](https://github.com/benrutter/Shades/blob/main/images/domain_circle.png)


**Integrating with Scipy's Delaunay function, to make a triangular grid**
```python
import shades
from random import randint
from scipy.spatial import Delaunay

canvas = shades.Canvas(1000, 800)
ink = shades.NoiseGradient(
    noise_fields=[shades.NoiseField(scale=0.002) for i in range(3)]
)

points = [(randint(0, canvas.width), randint(0, canvas.height)) for i in range(90)]
# plus some edge points to make sure the whole canvas is coloured
points.append((0, 0))
points.append((0, canvas.height))
points.append((canvas.width, 0))
points.append((canvas.width, canvas.height))
points.append((0, canvas.height/2))
points.append((canvas.width, canvas.height/2))
points.append((canvas.width/2, 0))
points.append((canvas.width/2, canvas.height))

# drawing triangles between points
for tri in Delaunay(points).simplices:
    ink.color = [randint(180, 255) for i in range(3)]
    ink.triangle(
        canvas,
        points[tri[0]],
        points[tri[1]],
        points[tri[2]],
    )

canvas.show()
```
![Delaunay grid](https://github.com/benrutter/Shades/blob/main/images/delaunay.png)


Happy hacking! 🕶️
