"""
Function decorators for internal use.
"""
from typing import Callable, Tuple, Optional
import inspect
from functools import wraps

def cast_ints(func: Callable) -> Callable:
    @wraps(func)
    def casted_func(*args, **kwargs):
        kwargs |= dict(zip(inspect.getfullargspec(func).args, args))
        for kwarg, value in kwargs.items():
            kwarg_type = func.__annotations__.get(kwarg)
            if kwarg_type == int:
                kwargs[kwarg] = round(value)
            elif kwarg_type == Optional[int] and value is not None:
                kwargs[kwarg] = round(value)
            elif kwarg_type == Tuple[int, int]:
                kwargs[kwarg] = (round(value[0]), round(value[1]))
            elif kwarg_type == Tuple[int, int, int]:
                kwargs[kwarg] = (round(value[0]), round(value[1]), round(value[2]))
        return func(**kwargs)
    return casted_func
