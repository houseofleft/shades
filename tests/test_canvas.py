"""
tests for the shades.canvas module
"""
import numpy as np
import pytest

from shades import canvas
from shades.shades import block_color
from shades.noise import noise_fields

@pytest.fixture
def canvas_obj():
    return canvas.Canvas(10, 10, (0, 0, 255))

@pytest.fixture
def small_canvas():
    return canvas.Canvas(3, 3, (0, 0, 255))

@pytest.fixture
def black():
    return block_color((0, 0, 0))

def test_image_returns_expected_pil_image(canvas_obj):
    actual = canvas_obj.image().getpixel((4, 4))
    assert actual == (0, 0, 255)

def test_grid_provides_correctly_spaces_xy_coords(canvas_obj):
    actual = {i for i in canvas_obj.grid(10, 10)}
    assert actual == {(0, 0), (0, 10), (10, 10), (10, 0)}

def test_rotation_manipulates_rectangle_correcly(small_canvas, black):
    actual = small_canvas.rectangle(
        black,
        (1, 1),
        2, 1,
        rotation=90,
        rotate_on=(1, 1)
    )._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0]])).all()

def test_rectangle_draws_expected_sahpe_without_rotation(small_canvas, black):
    actual = small_canvas.rectangle(black, (1, 1), 2, 1)._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 1], [0, 0, 0]])).all()

def test_rectangle_is_changed_by_warping(canvas_obj, black):
    not_expected = canvas_obj.rectangle(black, (1, 1), 20, 10)._stack[0][1]
    actual = canvas_obj.warped_rectangle(black, (1, 1), 20, 10, warp_noise=noise_fields(seed=3, channels=2), shift=100)._stack[1][1]
    assert not (actual != not_expected).all()

