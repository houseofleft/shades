"""
tests for shades.noise module
"""
from shades import noise

import pytest

@pytest.fixture
def field():
    return noise.NoiseField()

def test_noise_range_returns_expected_size_object(field):
    actual = field.noise_range((0, 0), 10, 20)
    assert actual.shape == (20, 10)

def test_noise_range_is_different_based_on_start_point(field):
    actual = field.noise_range((0, 0), 10, 20)
    also_actual = field.noise_range((10, 10), 10, 20)
    assert not (actual == also_actual).all()

def test_noise_fields_function_returns_list_of_requested_noise_fields():
    actual = noise.noise_fields(0.002, 2, 4)
    assert len(actual) == 4

def test_noise_fields_can_take_list_of_scale():
    actual = noise.noise_fields([1, 2, 3], channels=3)
    assert {i.scale for i in actual} == {1, 2, 3}

def test_noise_fields_can_take_list_of_seeds():
    actual = noise.noise_fields(seed=[1, 2, 3], channels=3)
    assert {i.seed for i in actual} == {1, 2, 3}
    
