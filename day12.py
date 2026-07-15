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
    plots: set[Position] = field(default_factory=set, repr=False)
    _tl: Position = field(default=(0, 0), init=False, repr=False)
    """Bounding Box Top Left"""
    _br: Position = field(default=(0, 0), init=False, repr=False)
    """Bounding Box Bottom Right"""

    @property
    def area(self):
        return len(self.plots)
    
    @property
    def cost(self):
        return self.area * self.perimeter
    
    @property
    def perimeter(self):
        """Calculate Perimeter of the Region"""
        perimeter = 0
        for plot in self.plots:
            # check neighbors
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                neighbor = (plot[0] + dx, plot[1] + dy)
                if neighbor not in self.plots:
                    perimeter += 1
        return perimeter
    
    @property
    def letter(self):
        return chr(ord('A') + self.plant)
    
    def __iadd__(self, other: 'Position | Any'):
        if not isinstance(other, Position.__base__):
            return NotImplemented
        # add plot
        self.plots.add(other)
        # update bounding boxes
        self._tl = (min(self._tl[0], other[0]), min(self._tl[1], other[1]))
        self._br = (max(self._br[0], other[0]), max(self._br[1], other[1]))
        return self
    
    def halo(self) -> 'Region':
        """Return the Halo of the Region
        
        Line of pixels around the edge of the Region, not including the Region itself.
        """
        # dilate by one plot in each direction
        dilated = set((plot[0] + dx, plot[1] + dy)
                      for plot in self.plots
                      for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
                     )
        # cut out self-intersections
        dilated -= self.plots
        return Region(plant=self.plant, plots=dilated)
    
    def __and__(self, other: 'Region | Any') -> bool:
        """Check if Regions intersect"""
        if not isinstance(other, Region):
            return NotImplemented
        # let's see if bounding boxes intersect first
        lhs_minx, lhs_miny = self._tl
        rhs_minx, rhs_miny = other._tl
        lhs_maxx, lhs_maxy = self._br
        rhs_maxx, rhs_maxy = other._br

        # bounding boxes don't intersect --> no intersection
        if (lhs_maxx < rhs_minx or rhs_maxx < lhs_minx or
            lhs_maxy < rhs_miny or rhs_maxy < lhs_miny):
            return False
        
        # actually check if any plots intersect
        if self.plots & other.plots:
            return True
        
        # no plot intersections
        return False

    def __ior__(self, other: 'Region | Any'):
        if not isinstance(other, Region):
            return NotImplemented
        if (other.plant != self.plant):
            raise RuntimeError(f'Cannot merge unrelated Regions.')
        self.plots |= other.plots
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
            
            # create new region
            current = Region(puzzle.map[y][x])
            # add the current plot to the current region
            current += (x, y)
            
            # find adjacent regions
            adjacent_regions = tuple(region
                                for region in regions_by_plant[current.plant]
                                if current.halo() & region
                                )
            
            # merge existing regions (if any)
            for region in adjacent_regions:
                # merge into current region
                current |= region
                # remove region from map
                regions_by_plant[region.plant].remove(region)
            
            # store new region
            regions_by_plant[current.plant].append(current)
    
    # return flat region list
    return [region for regions in regions_by_plant.values() for region in regions]

def part2():
    pass

def main(args):
    
    puzzle = read_inputs(args.example)
    regions = part1(puzzle)
    if (logging.DEBUG):
        for region in regions:
            logging.debug(region)
    logging.info(f'Part 1: {sum(region.cost for region in regions)}'
                 f' ({" + ".join(str(region.cost) for region in regions[:25])})')
    part2()
    logging.info(f'Part 2: ')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
