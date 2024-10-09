"""
Shades is a python module for generative 2d image creation.

Because of the relatively small level of classes and functions
everything is imported into 'shades' name space to avoid
long import commands for single items.
"""

from shades.canvas import Canvas  # noqa
from shades.noise import noise_fields  # noqa
from shades.shades import block_color, gradient  # noqa

__version__ = "2.0.0a"
