# Shades 3

You're currently looking at the v.3 branch, which isn't released or ready for use.

Plan:

- [x] New, lazy evaluated canvas class to hold all state
- [ ] Port over geometry maths from Shade class into canvas
- [x] Shades can now be any function taking a numpy array of coordinates + returning corresponding array of colors
- [ ] This should give a big speedup to draw operations by vectorizing them, but introduce a shade API for applying a standard x/y function (which will be slow, but helpful for quick sketching and customisation)
- [ ] Some nicer, github hosted docs with pdoc + new readme
