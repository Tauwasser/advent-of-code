#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import functools
import logging
import math

from dataclasses import dataclass, field

from lib import setup

example_input = """125 17
"""


def ilog10(number: int) -> int:
    return math.ceil(math.log10(number + 1))


@functools.cache
def blink(number: int, steps: int) -> int:
    
    # decrement steps
    steps -= 1
    
    if (number == 0):
        # rule 1: 0 --> 1
        return blink(1, steps) if (steps > 0) else 1
    elif (0 == (exp := ilog10(number)) % 2):
        # rule 2: split stones if number even length
        split = int(10 ** (exp / 2))
        lhs = number // split
        rhs = number % split
        return (blink(lhs, steps) + blink(rhs, steps)) if (steps > 0) else 2
    else:
        # rule 3: number multiplied bz 2024
        return blink(number * 2024, steps) if (steps > 0) else 1

def read_inputs(example=0) -> list[int]:
    
    match (example):
        case _ if (example):
            data = example_input
        case _:
            with open('day11_input', 'r', encoding='utf-8') as f:
                data = f.readline()
    
    # parse logic
    return [int(n) for n in data.split()]

def part1(stones: list[int], steps: int=1) -> int:
    """Calculate number of stones after N steps"""
    num_stones = 0
    
    for stone in stones:
        num_stones += blink(stone, steps)
    
    return num_stones

def main(args):
    
    stones = read_inputs(args.example)
    num_stones = part1(stones, steps=25)
    logging.info(f'Part 1: {num_stones} stones after 25 steps.')
    num_stones = part1(stones, steps=75)
    logging.info(f'Part 1: {num_stones} stones after 75 steps.')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
