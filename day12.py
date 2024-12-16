#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from lib import setup

example1_input = """AAAA
BBCD
BBCC
EEEC
"""

example2_input = """OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
"""

example3_input = """RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
"""


Position = tuple[int, int]

@dataclass(eq=False)
class Region:
    plant: int = field(repr=False)
    perimeter: int = 0
    plots: list[Position] = field(default_factory=list, repr=False)
    
    @property
    def area(self):
        return len(self.plots)
    
    @property
    def cost(self):
        return self.area * self.perimeter
    
    @property
    def letter(self):
        return chr(ord('A') + self.plant)
    
    def __ior__(self, other: 'Region | Any'):
        if not isinstance(other, Region):
            return NotImplemented
        if (other.plant != self.plant):
            raise RuntimeError(f'Cannot merge unrelated Regions.')
        self.plots += other.plots
        self.perimeter += other.perimeter
        return self
    
    def __contains__(self, item: 'Position | Any'):
        return (item in self.plots)
    
    def __repr__(self):
        return f'{self.__class__.__name__}(letter={self.letter}, area={self.area}, perimeter={self.perimeter})'


@dataclass
class Puzzle:
    height: int
    width: int
    map: list[list[int]] = field(default_factory=list, repr=False)


def read_inputs(example=0) -> Puzzle:
    
    match (example):
        case 1 if (example):
            data = example1_input
        case 2 if (example):
            data = example2_input
        case 3 if (example):
            data = example3_input
        case _:
            with open('day12_input', 'r', encoding='utf-8') as f:
                data = f.read()
    
    data = data.splitlines()
    
    # parse logic
    puzzle = Puzzle(height=len(data), width=len(data[0]))
    for line in data:
        puzzle.map.append([ord(c) - ord('A') for c in line])
    
    return puzzle

def part1(puzzle: Puzzle) -> list[Region]:
    
    regions_by_plant: dict[int, list[Region]] = defaultdict(lambda: [])
    width = puzzle.width
    height = puzzle.height
    
    def _neighbors(x: int, y: int) -> Iterator[Position]:
        
        for dx, dy in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
            
            if not (0 <= x + dx < puzzle.width):
                continue
            if not (0 <= y + dy < puzzle.height):
                continue
            yield (x + dx, y + dy)
    
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            
            # grab plant
            plant = puzzle.map[y][x]
            
            # perimeter cost 4 less plots w/ same plant
            perimeter = 4 - sum(1 if (puzzle.map[ny][nx] == plant) else 0 for nx, ny in _neighbors(x, y))
            
            # find adjacent regions
            adjacent_regions = set(region
                                for pos in _neighbors(x, y)
                                for region in regions_by_plant[plant]
                                if pos in region
                                )
            
            # create/merge regions
            if (len(adjacent_regions) == 0):
                # create new region
                region = Region(plant)
                regions_by_plant[plant].append(region)
            else:
                adjacent_regions = tuple(adjacent_regions)
                region = adjacent_regions[0]
                for other in adjacent_regions[1:]:
                    # merge into current region
                    region |= other
                    # remove region from map
                    regions_by_plant[plant].remove(other)
            
            # add the current plot to the current region
            region.plots.append((x, y))
            # add current perimeter to current region
            region.perimeter += perimeter
    
    # return flat region list
    return [region for regions in regions_by_plant.values() for region in regions]

def part2():
    pass

def main(args):
    
    puzzle = read_inputs(args.example)
    regions = part1(puzzle)
    logging.info(f'Part 1: {sum(region.cost for region in regions)}'
                 f' ({" + ".join(str(region.cost) for region in regions[:25])})')
    part2()
    logging.info(f'Part 2: ')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
