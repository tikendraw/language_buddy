import os
from functools import cache


@cache
def get_env(var:str)-> str|None:
    return os.environ.get(var, None)