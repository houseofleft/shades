# Shades 2

You're currently looking at the v3 branch, but its actually for v2 (I got confused along the way). Either way it isn't released or ready for use.

There's a pretty major overhaul of how things are working under the hood, which will probably mean at least at first a reduced feature set.

Design changes are:
- An actual canvas object (previously this was just a wrapper for a PIL image)
- The new canvas object manages all state and therefore can make a rudimentary lazy execution plan (i.e. not ask for pixels that are going to be drawn over) and more significantly, allows shades to be numpy vectorised functions.

This gives a pretty big speedup because it means we can completely bypass python's inner loop. For instance, previously coloring a noise gradient over a 1000x1000px image took 5.9 second (boo!) but this process now takes 0.014 seconds (yay) which is an approx 400x speedup.

Its always nice when things are faster, but this should mean a much bigger opportunity for supporting things like higher resolution images, anti-aliasing etc.

There's also a lot more opportunities for further speedups down the line now there's a proper execution planner;

Plan:

- [x] New, lazy evaluated canvas class to hold all state
- [ ] Port over geometry maths from Shade class into canvas
    - [x] Generic polygon function (+ rectangle, square, triangle implementations)
    - [ ] Circle
    - [ ] Perlin noise shifted geometry
    - [ ] New rotation functionality?
- [x] Shades can now be any function taking a numpy array of coordinates + returning corresponding array of colors
- [x] This should give a big speedup to draw operations by vectorizing them, but introduce a shade API for applying a standard x/y function (which will be slow, but helpful for quick sketching and customisation)
- [ ] Some nicer, github hosted docs with pdoc + new readme

