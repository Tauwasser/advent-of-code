#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import operator

from enum import IntEnum
from functools import reduce
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from lib import setup

example1_input = """8A004A801A8002F478
"""

example2_input = """620080001611562C8802118E34
"""

example3_input = """C0015000016115A2E0802F182340
"""

example4_input = """A0016C880162017C3686B18A3D4780
"""

class PacketType(IntEnum):
    SUM =     0
    PROD =    1
    MIN =     2
    MAX =     3
    LITERAL = 4
    GT =      5
    LT =      6
    EQ =      7

@dataclass
class Packet:
    version: int
    type: PacketType

@dataclass
class Literal(Packet):
    value: int

@dataclass
class Operator(Packet):
    packets: List[Packet] = field(default_factory=list)

class BitReader:
    
    def __init__(self, data: bytes):
        self._data = data
        self._off = 0
        self._byte = 0
        self._bits = 0
        self._bit_cnt = 0
    
    def read(self, bits: int):
        
        result = 0
        
        while (bits):
            
            # reload byte
            if (0 == self._bits):
                self._byte = self._data[self._off]
                self._off += 1
                self._bits = 8
            
            shift = min(bits, self._bits)
            self._byte <<= shift
            result <<= shift
            result |= (self._byte >> 8)
            self._byte &= 0xFF
            bits -= shift
            self._bits -= shift
            self._bit_cnt += shift
        
        return result
    
    @property
    def bit_count(self):
        return self._bit_cnt

def parse_packet(br: BitReader) -> Packet:
    
    # parse version
    # parse type
    version = br.read(3)
    type = br.read(3)
    
    if (type == PacketType.LITERAL):
        
        value = 0
        data = br.read(5)
        
        while (data & 0b10000):
            value |= data & 0b01111
            value <<= 4
            data = br.read(5)
        
        value |= data & 0b01111
        return Literal(version, type, value)
    
    else:
        
        length_type = br.read(1)
        
        if (length_type == 1):
            
            # number of packets
            num_packets = br.read(11)
            packets = []
            for _ in range(num_packets):
                packets.append(parse_packet(br))
            
        else:
            
            # number of bits
            bit_count = br.read(15)
            bit_count_beg = br.bit_count
            packets = []
            while (br.bit_count - bit_count_beg < bit_count):
                packets.append(parse_packet(br))
        
        return Operator(version, type, packets)

def _calc_packet(packet: Packet) -> int:
    
    if (PacketType.LITERAL == packet.type):
        return packet.value
    
    values = [_calc_packet(p) for p in packet.packets]
    
    if (PacketType.SUM == packet.type):
        return sum(values)
    elif (PacketType.PROD == packet.type):
        return reduce(operator.mul, values)
    elif (PacketType.MIN == packet.type):
        return min(values)
    elif (PacketType.MAX == packet.type):
        return max(values)
    elif (PacketType.LT == packet.type):
        return 1 if (values[0] < min(values[1:])) else 0
    elif (PacketType.GT == packet.type):
        return 1 if (values[0] > max(values[1:])) else 0
    elif (PacketType.EQ == packet.type):
        return 1 if all(values[0] == x for x in values[1:]) else 0
    else:
        raise RuntimeError(f'Unimplemented Packet Type {packet.type}')

def read_inputs(example=0):
    
    if (1 == example):
        data = example1_input
    elif (2 == example):
        data = example2_input
    elif (3 == example):
        data = example3_input
    elif (example):
        data = example4_input
    else:
        with open('day16_input', 'r', encoding='utf-8') as f:
            data = f.read()
    
    br = BitReader(bytes.fromhex(data))
    return parse_packet(br)

def part1(packet: Packet) -> int:

    result = 0
    
    def _visit_packet(packet: Packet):
        nonlocal result
        result += packet.version
        if (packet.type != PacketType.LITERAL):
            for subpacket in packet.packets:
                _visit_packet(subpacket)
    
    _visit_packet(packet)
    return result

def part2(packet: Packet) -> int:
    return _calc_packet(packet)

def main(args):
    
    packet = read_inputs(args.example)
    sum_versions = part1(packet)
    logging.info(f'Part 1: sum of version numbers = {sum_versions}')
    result = part2(packet)
    logging.info(f'Part 2: result of packet = {result}')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))