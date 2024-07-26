"""
tests for shades.utils module
"""
from shades import utils

def test_euclidean_distance_returns_expected_values():
    actual = utils.euclidean_distance((-32, 10), (31, 34))
    assert 67.4166 < actual < 67.4167

def test_randomly_shift_point_produces_new_point():
    points = [(3, 4), (-3, -25), (34, -24444)]
    actual = [utils.randomly_shift_point(i, (10, 10)) for i in points]
    assert not all([i==j for i, j in zip(points, actual)])
