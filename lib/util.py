#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections.abc import Callable, Hashable, Iterable
from typing import TypeVar

_T = TypeVar("_T")
def unique(iterable: Iterable[_T], /, *, key: Callable[[_T], Hashable]) -> list[_T]:
    """Return a new list containing all unique items from the iterable.
    
    Args:
        key: key function that transforms elements into hashable keys.
    """
    tmp = {key(elem): elem for elem in iterable}
    return [v for v in tmp.values()]
