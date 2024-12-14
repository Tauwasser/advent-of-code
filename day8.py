#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import math

from collections import defaultdict
from collections.abc import Callable, Generator
from itertools import chain, combinations
from dataclasses import dataclass, field

from lib import setup
from lib.util import unique

example_input = """............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
"""


@dataclass
class IntVector2D:
    x: int
    y: int
    
    def __add__(self, other):
        if not isinstance(other, IntVector2D):
            return NotImplemented
        return IntVector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        if not isinstance(other, IntVector2D):
            return NotImplemented
        return IntVector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        return IntVector2D(self.x * other, self.y * other)
    
    def __floordiv__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        return IntVector2D(self.x // other, self.y // other)
    
    def __rmul__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        return IntVector2D(other * self.x, other * self.y)
    
    def __iadd__(self, other):
        if not isinstance(other, IntVector2D):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self
    
    def __isub__(self, other):
        if not isinstance(other, IntVector2D):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __imul__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        self.x *= other
        self.y *= other
        return self
    
    def __neg__(self):
        return IntVector2D(-self.x, -self.y)
    
    def __pos__(self):
        return IntVector2D(+self.x, +self.y)
    
    def __abs__(self):
        return math.sqrt(self.x * self.x + self.y * self.y)


@dataclass
class Antenna:
    frequency: str
    position:  IntVector2D
    
    @property
    def x(self) -> int:
        return self.position.x
    
    @property
    def y(self) -> int:
        return self.position.y
    
    def __repr__(self):
        return f'{self.__class__.__name__}(x={self.x},y={self.y},frequency={self.frequency})'


@dataclass
class Antinode:
    antenna: tuple[Antenna, Antenna]
    position: IntVector2D
    
    @property
    def x(self) -> int:
        return self.position.x
    
    @property
    def y(self) -> int:
        return self.position.y
    
    def __repr__(self):
        return f'{self.__class__.__name__}(x={self.x},y={self.y},frequency={self.antenna[0].frequency})'

@dataclass
class Puzzle:
    width: int
    height: int
    antennas: dict[str, list[Antenna]] = field(default_factory=dict)


def read_inputs(example=0):
    
    match (example):
        case _ if (example):
            data = example_input
        case _:
            with open('day8_input', 'r', encoding='utf-8') as f:
                data = f.read()
    
    data = data.splitlines()
    
    # parse data
    antennas = defaultdict(lambda: [])
    for y, line in enumerate(data):
        for x, char in enumerate(line):
            if ('.' == char):
                continue
            antennas[char].append(Antenna(char, IntVector2D(x, y)))
    
    return Puzzle(antennas={**antennas}, width=x, height=y)

def in_map_fn_factory(puzzle: Puzzle) -> Callable[[IntVector2D], bool]:
    
    def _in_map(position: IntVector2D):
        if not(0 <= position.x <= puzzle.width):
            return False
        if not (0 <= position.y <= puzzle.height):
            return False
        return True
    
    return _in_map

def part1(puzzle: Puzzle) -> list[Antinode]:
    """Determine list of Antinodes"""
    antinodes : dict[str, list[Antinode]] = defaultdict(lambda: [])
    
    in_map = in_map_fn_factory(puzzle)
    
    # for all pairings of antennas of same frequencies
    # determine antinodes (if inside map)
    for frequency, antennas in puzzle.antennas.items():
        for lhs, rhs in combinations(antennas, 2):
            
            delta = rhs.position - lhs.position
            
            # two possible positions per paring of antennas
            positions = (lhs.position - delta, rhs.position + delta)
            
            for position in positions:
                if not in_map(position):
                    continue
                # antinode found in map
                antinodes[frequency].append(Antinode((lhs, rhs), position))
    
    # restrict to unique antinode locations
    unique_antinodes = unique(chain(*antinodes.values()),
                              key=lambda antinode: (antinode.position.x, antinode.position.y)
                              )
    
    return unique_antinodes

def part2(puzzle: Puzzle) -> list[Antinode]:
    """Determine list of Antinodes including resonance"""
    antinodes : dict[str, list[Antinode]] = defaultdict(lambda: [])
    
    in_map = in_map_fn_factory(puzzle)
    
    def _antinode_iter(begin: IntVector2D, delta: IntVector2D) -> Generator[IntVector2D]:
        
        # yield position of resonant antenna as well
        position = begin
        
        while (in_map(position)):
            yield position
            position = position + delta
        
    
    # for all pairings of antennas of same frequencies
    # determine antinodes (if inside map)
    for frequency, antennas in puzzle.antennas.items():
        for lhs, rhs in combinations(antennas, 2):
            
            delta = rhs.position - lhs.position
            
            # iterate through all possible positions
            for position in chain(_antinode_iter(lhs.position, -delta), _antinode_iter(rhs.position, +delta)):
                # antinode found in map
                antinodes[frequency].append(Antinode((lhs, rhs), position))
    
    # restrict to unique antinode locations
    unique_antinodes = unique(chain(*antinodes.values()),
                              key=lambda antinode: (antinode.position.x, antinode.position.y)
                              )
    
    return unique_antinodes

def main(args):
    
    puzzle = read_inputs(args.example)
    unique_antinodes = part1(puzzle)
    logging.info(f'Part 1: {len(unique_antinodes)}')
    unique_antinodes = part2(puzzle)
    logging.info(f'Part 2: {len(unique_antinodes)}')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
