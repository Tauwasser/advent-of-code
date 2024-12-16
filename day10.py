#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging

from collections.abc import Iterator
from dataclasses import dataclass, field

from lib import setup
from lib.util import unique

example_input = """89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
"""


Position = tuple[int, int]

@dataclass
class Peak:
    x: int
    y: int
    elevation: int


@dataclass
class Trailhead:
    x: int
    y: int
    peaks: list[Peak] = field(default_factory=list, repr=False)


@dataclass
class Puzzle:
    height: int
    width: int
    map: list[list[int]] = field(default_factory=list, repr=False)

def read_inputs(example=0) -> Puzzle:
    
    match (example):
        case _ if (example):
            data = example_input
        case _:
            with open('day10_input', 'r', encoding='utf-8') as f:
                data = f.read()
    
    data = data.splitlines()
    
    # parse logic
    puzzle = Puzzle(height=len(data), width=len(data[0]))
    for line in data:
        puzzle.map.append([int(c) for c in line])
    
    return puzzle

def part1(puzzle: Puzzle, distinct: bool=False) -> list[Trailhead]:
    """Find Trailheads"""
    
    def _neighbors(x: int, y: int) -> Iterator[Position]:
        
        for dx, dy in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
            
            if not (0 <= x + dx < puzzle.width):
                continue
            if not (0 <= y + dy < puzzle.height):
                continue
            yield (x + dx, y + dy)
    
    trailheads : list[Trailhead] = []
    elevation_map : dict[int, dict[Position, list[Peak]]] = {e: {} for e in range(1, 10)}
    
    # find all 0s (trailheads) and 9s (peaks)
    # map all points at elevation (W * H)
    for y in range(puzzle.height):
        for x in range(puzzle.width):
            pos = (x, y)
            match (puzzle.map[y][x]):
                case 9:
                    elevation_map[9][pos] = [Peak(x, y, 9)]
                case 0:
                    trailheads.append(Trailhead(x, y))
                case elevation:
                    elevation_map[elevation][pos] = []
    
    # traverse paths along gradient (downward slope)
    for elevation in range(8, 0, -1):
        for (x, y), paths in elevation_map[elevation].items():
            for neighbor in _neighbors(x, y):
                paths += elevation_map[elevation + 1].get(neighbor, [])
    
    # find all peaks reachable for each trailhead
    for trailhead in trailheads:
        for neighbor in _neighbors(trailhead.x, trailhead.y):
            trailhead.peaks += elevation_map[1].get(neighbor, [])
        if not distinct:
            # make sure peaks are unique
            trailhead.peaks = unique(trailhead.peaks, key=lambda peak: (peak.x, peak.y))
    
    # return trailheads only
    return trailheads

def part2(puzzle: Puzzle) -> list[Trailhead]:
    return part1(puzzle, distinct=True)

def main(args):
    
    puzzle = read_inputs(args.example)
    trailheads = part1(puzzle)
    logging.info(f'Part 1: {sum(len(trailhead.peaks) for trailhead in trailheads)}'
                 f' ({" + ".join(str(len(trailhead.peaks)) for trailhead in trailheads[:15])})'
    )
    trailheads = part2(puzzle)
    logging.info(f'Part 1: {sum(len(trailhead.peaks) for trailhead in trailheads)}'
                 f' ({" + ".join(str(len(trailhead.peaks)) for trailhead in trailheads[:15])})'
    )
    logging.info(f'Part 2: ')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
