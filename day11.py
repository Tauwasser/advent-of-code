#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import math

from dataclasses import dataclass, field

from lib import setup

example_input = """125 17
"""


def ilog10_int(number: int) -> int:
    return math.ceil(math.log10(number + 0.1))

def ilog10_str(number: int) -> int:
    return len(str(number))


@dataclass
class Stone:
    number: int
    
    def change(self) -> 'Stone | None':
        
        if (self.number == 0):
            # rule 1: 0 --> 1
            self.number = 1
        elif (0 == (exp := ilog10_int(self.number)) % 2):
            # rule 2: split stones if number even length
            split = int(10 ** (exp / 2))
            lhs = self.number // split
            rhs = self.number % split
            self.number = rhs
            return Stone(lhs)
        else:
            # rule 3: number multiplied bz 2024
            self.number *= 2024
        
        return None

def read_inputs(example=0) -> list[Stone]:
    
    match (example):
        case _ if (example):
            data = example_input
        case _:
            with open('day11_input', 'r', encoding='utf-8') as f:
                data = f.readline()
    
    # parse logic
    return [Stone(int(n)) for n in data.split()]

def print_stones(stones: list[Stone]):
    print(" ".join(str(stone.number) for stone in stones))

def part1(stones: list[Stone], steps: int=1) -> list[Stone]:
    
    # create a copy of stones
    stones = [Stone(stone.number) for stone in stones]
    
    for _ in range(steps):
        ix_off = 0
    
        for ix, stone in enumerate(stones[:]):
            
            extra = stone.change()
            if (extra is not None):
                stones.insert(ix + ix_off, extra)
                ix_off += 1
        
        #print_stones(stones)
    
    return stones

def main(args):
    
    stones = read_inputs(args.example)
    stones = part1(stones, steps=25)
    logging.info(f'Part 1: {len(stones)} stones: '
                 f'{" ".join(str(stone.number) for stone in stones[:25])}')
    stones = part1(stones, steps=75)
    logging.info(f'Part 1: {len(stones)} stones: '
                 f'{" ".join(str(stone.number) for stone in stones[:25])}')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
