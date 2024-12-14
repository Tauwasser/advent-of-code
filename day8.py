#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import math

from collections import defaultdict
from itertools import chain, combinations
from dataclasses import dataclass, field

from lib import setup

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

def part1(puzzle: Puzzle) -> dict[str, list[Antinode]]:
    """Determine list of Antinodes"""
    antinodes : dict[str, list[Antinode]] = defaultdict(lambda: [])
    
    # short-hands for puzzle width/height
    height = puzzle.height
    width = puzzle.width
    
    # for all pairings of antennas of same frequencies
    # determine antinodes (if inside map)
    for frequency, antennas in puzzle.antennas.items():
        for lhs, rhs in combinations(antennas, 2):
            
            delta = rhs.position - lhs.position
            
            # two possible positions per paring of antennas
            positions = (lhs.position - delta, rhs.position + delta)
            
            for position in positions:
                if not(0 <= position.x <= width):
                    continue
                if not (0 <= position.y <= height):
                    continue
                # antinode found in map
                antinodes[frequency].append(Antinode((lhs, rhs), position))
    
    return {**antinodes}

def part2():
    pass

def main(args):
    
    puzzle = read_inputs(args.example)
    antinodes = part1(puzzle)
    unique_positions = set((antinode.x, antinode.y) for antinode in chain(*antinodes.values()))
    logging.info(f'Part 1: {len(unique_positions)}')
    part2()
    logging.info(f'Part 2: ')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
