"""
tests for shades.shades module
"""
from shades import shades

def test_block_color_returns_array_of_identical_colors():
    color = shades.block_color((200, 10, 130))
    actual = color((0, 0), 10, 10)
    assert (actual == (200, 10, 130)).all()

def test_gradient_produces_expected_shade():
    gradient = shades.gradient()
    actual = gradient((20, 40), 2, 4)
    assert actual.shape == (4, 2, 3)

def test_custom_shade_allows_any_python_function_over_xy_coords():
    custom = shades.custom_shade(lambda xy: (2, 2, 4))
    actual = custom((0, 0), 4, 4)
    assert (actual == (2, 2, 4)).all()
