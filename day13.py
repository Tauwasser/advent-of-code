#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import re

from dataclasses import dataclass, field

from lib import setup

example_input = """Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
"""

BUTTON_PATTERN = re.compile(r'Button ([AB]): X([+-]\d+), Y([+-]\d+)')
PRIZE_PATTERN = re.compile(r'Prize: X=(\d+), Y=(\d+)')

@dataclass(frozen=True)
class ClawMachine:
    a:     tuple[int, int]
    b:     tuple[int, int]
    prize: tuple[int, int]
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(A: X{self.a[0]:+d}, Y{self.a[1]:+d}), '
                                          f'B: X{self.b[0]:+d}, Y{self.b[1]:+d}), '
                                          f'Prize: X={self.prize[0]}, Y={self.prize[1]})')

def read_inputs(example=0) -> list[ClawMachine]:
    
    match (example):
        case _ if (example):
            data = example_input
        case _:
            with open('day13_input', 'r', encoding='utf-8') as f:
                data = f.read()
    
    data = data.splitlines()
    
    buttons = {}
    machines = []
    
    for line in data:
        
        # skip empty lines
        if not line.strip():
            continue
        
        # match buttons or prizes
        if (match := BUTTON_PATTERN.match(line)):
            button, x, y = match.groups()
            buttons[button] = (int(x), int(y))
        elif (match := PRIZE_PATTERN.match(line)):
            x, y = match.groups()
            prize = (int(x), int(y))
            machines.append(ClawMachine(a=buttons['A'], b=buttons['B'], prize=prize))
        else:
            raise RuntimeError(f'Unrecognized line: {line}')
        
    return machines

def part1(machines: list[ClawMachine]) -> list[tuple[int, int]]:
    """Calculate the minimum number of Tokens needed to reach the Prize"""
    
    # token cost A=3, B=1
    tokens: list[tuple[int, int]] = []
    
    for m in machines:
        # assume initial position is X=0, Y=0
        # basically we have a matrix
        #  [x0 * Ax + x1 * Bx] = [Px]
        #  [x0 * Ay + x1 * By] = [Py]
        
        # we need to bring this into row echelon form
        # to deduce x0 and x1
        # We can also determine if there is a solution
        # by checking if the determinant:
        # zero:     no unique solution
        # non-zero: unique solution
        
        # det([[Ax, Bx], [Ay, By]]) = Ax * By - Ay * Bx
        det = m.a[0] * m.b[1] - m.a[1] * m.b[0]
        
        if (det != 0):
            # unique solution
            # use Cramer's rule to solve for x0 and x1
            x0 = (m.prize[0] * m.b[1] - m.prize[1] * m.b[0]) // det
            x1 = (m.a[0] * m.prize[1] - m.a[1] * m.prize[0]) // det
            
            # double check the solution, because of truncating division
            if (x0 * m.a[0] + x1 * m.b[0] == m.prize[0] and
                x0 * m.a[1] + x1 * m.b[1] == m.prize[1]):
                # unique solution with positive button presses
                tokens.append((x0, x1))
            else:
                # unique solution requiring negative button presses
                # or no integer solution
                tokens.append((0, 0))
        else:
            # no unique solution, check for at most 100 button pushes (per button)
            # prioritize button B, because it costs less
            found = False
            x1 = min(100, min(m.prize[0] // m.b[0], m.prize[1] // m.b[1]))
            while (not found and x1 >= 0):
                for x0 in range(1, 100):
                    # x coord overflow
                    if (x0 * m.a[0] + x1 * m.b[0] > m.prize[0]):
                        break
                    # y coord overflow
                    if (x0 * m.a[1] + x1 * m.b[1] > m.prize[1]):
                        break
                    if (x0 * m.a[0] + x1 * m.b[0] == m.prize[0] and
                        x0 * m.a[1] + x1 * m.b[1] == m.prize[1]):
                        tokens.append((x0, x1))
                        found = True
                        break
                
                # try one less B button push
                x1 -= 1
            
            if not found:
                # no integer solution
                tokens.append((0, 0))
        
    return tokens

def part2():
    pass

def main(args):
    
    machines = read_inputs(args.example)
    if (logging.DEBUG):
        for machine in machines:
            logging.debug(machine)
    tokens = part1(machines)
    logging.info(f'Part 1: {sum(3 * x0 + x1 for x0, x1 in tokens)} '
                 f'({", ".join(f"A×{x0} + B×{x1}" for x0, x1 in tokens[:25])})')
    part2()
    logging.info(f'Part 2: ')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
