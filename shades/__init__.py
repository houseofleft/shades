"""
Shades is a python module for generative 2d image creation.

Because of the relatively small level of classes and functions
everything is imported into 'shades' name space to avoid
long import commands for single items.
"""
from .canvas import *  # noqa
from .noise_fields import *  # noqa
from .shades import *  # noqa
from .utils import *  # noqa

__version__ = "3.0.0"
