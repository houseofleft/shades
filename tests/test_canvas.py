"""
tests for the shades.canvas module
"""
import numpy as np
import pytest

from shades import canvas
from shades.shades import block_color


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


def test_rectangle_draws_expected_shape(small_canvas, black):
    actual = small_canvas.rectangle(black, (1, 1), 2, 1)._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 1], [0, 0, 0]])).all()


def test_rectangle_outline_draws_expected_shape(small_canvas, black):
    actual = small_canvas.rectangle_outline(black, (1, 1), 2, 1)._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0]])).all()


def test_square_draws_expected_shape(small_canvas, black):
    actual = small_canvas.square(black, (1, 1), 2)._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 1], [0, 1, 1]])).all()


def test_square_outline_draws_expected_shape(small_canvas, black):
    small_canvas.square_outline(black, (1, 1), 2)._compress_stack()
    actual = small_canvas._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 1], [0, 1, 0]])).all()


def test_line_draws_expected_shape(small_canvas, black):
    small_canvas.line(black, (1, 0), (0, 1))._compress_stack()
    actual = small_canvas._stack[0][1]
    assert (actual == np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]])).all()


def test_polygon_draws_expected_shape(small_canvas, black):
    small_canvas.polygon(black, (1, 1), (3, 2), (2, 2))._compress_stack()
    actual = small_canvas._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 0], [0, 0, 1]])).all()


def test_polygon_outline_draws_expected_shape(small_canvas, black):
    actual = small_canvas.polygon_outline(black, (1, 1), (2, 1))._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 1, 1], [0, 0, 0]])).all()


def test_triangle_draws_expected_shape(small_canvas, black):
    actual = small_canvas.triangle(black, (0, 0), (1, 0), (2, 2))._stack[0][1]
    assert (actual == np.array([[1, 1, 0], [1, 1, 0], [0, 0, 1]])).all()


def test_triangle_outline_draws_expected_shape(small_canvas, black):
    actual = small_canvas.triangle_outline(black, (0, 0), (1, 0), (2, 2))._stack[0][1]
    assert (actual == np.array([[1, 1, 0], [0, 0, 0], [0, 0, 0]])).all()


def test_circle_draws_expected_shape(small_canvas, black):
    actual = small_canvas.circle(black, (1, 1), 1)._stack[0][1]
    assert (actual == np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])).all()


def test_circle_outline_draws_expected_shape(small_canvas, black):
    actual = small_canvas.circle_outline(black, (1, 1), 2)._stack[0][1]
    assert (actual == np.array([[0, 0, 0], [0, 0, 0], [0, 0, 1]])).all()
