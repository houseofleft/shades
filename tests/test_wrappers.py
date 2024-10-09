from typing import Tuple
from shades import _wrappers

def test_cast_int_converts_floats_based_on_type_hints():
    @_wrappers.cast_ints
    def some_function(a: int):
        assert isinstance(a, int)
    some_function(1.1)

def test_cast_int_leaves_not_int_hinted_things_alone():
    @_wrappers.cast_ints
    def some_function(a: float, b):
        return (a, b)
    actual, also_actual = some_function(1.2, "cool")
    assert not isinstance(actual, int)
    assert not isinstance(also_actual, int)

def test_case_int_works_also_on_tuple_of_ints_of_two_or_three_length():
    @_wrappers.cast_ints
    def some_function(a: Tuple[int, int]):
        one, two = a
        assert isinstance(one, int)
        assert isinstance(two, int)
    some_function((3.4, 3.1))
    @_wrappers.cast_ints
    def some_function(a: Tuple[int, int, int]):
        one, two, three = a
        assert isinstance(one, int)
        assert isinstance(two, int)
        assert isinstance(three, int)
    some_function((3.4, 3.1, 1.1))
