#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging

from collections import defaultdict
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import TypeVar

from lib import setup

example_input = """2333133121414131402
"""


@dataclass
class Entry:
    id: int
    size: int


@dataclass
class Puzzle:
    entries: list[Entry] = field(default_factory=list)


@dataclass
class LLEntry:
    entry: Entry
    prev: 'LLEntry | None' = None
    next: 'LLEntry | None' = None

_T = TypeVar("_T")
class DoubleIterator[_T]:
    
    def __init__(self, sequence: Sequence[_T]):
        """Create a Double Iterator
        
        Args:
            sequence: sequence to be iterated over
        """
        self._begin = 0
        self._end = len(sequence) - 1
        self._sequence = sequence
    
    def get_fwd(self) -> Iterator[_T]:
        """Iterate through available elements in forwards direction."""
        ix = self._begin
        while (ix <= self._end):
            self._begin += 1
            yield self._sequence[ix]
            ix += 1
    
    def get_bwd(self) -> Iterator[_T]:
        """Iterate through available elements in backwards direction."""
        ix = self._end
        while (ix >= self._begin):
            self._end -= 1
            yield self._sequence[ix]
            ix -= 1


def read_inputs(example=0) -> Puzzle:
    
    match (example):
        case _ if (example):
            data = example_input
        case _:
            with open('day9_input', 'r', encoding='utf-8') as f:
                data = f.readline()
    
    data = data.strip()
    
    # parse logic
    puzzle = Puzzle()
    file_id = 0
    
    for file_length, gap_length in zip(data[::2], data[1::2] + '0'):
        # parse file and gap descriptor
        puzzle.entries.append(Entry(file_id, int(file_length)))
        if (gap_length != '0'):
            puzzle.entries.append(Entry(-1, int(gap_length)))
        # increment file ID
        file_id += 1
    
    return puzzle

def compact_memory_fragmented(puzzle: Puzzle) -> list[Entry]:
    """Compact Memory w/ Fragmentation
    
    Args:
        puzzle: Puzzle input
    
    Returns:
        List of compacted memory blocks.
    """
    compacted : list[Entry] = []
    
    # fwd/bwd iterator through entries
    it = DoubleIterator(puzzle.entries)
    
    # current gap/file block properties
    fill_size = 0
    num_gap_blk = 0
    num_file_blk = 0
    
    # go backwards through memory
    for bwd_entry in it.get_bwd():
        
        # skip gaps
        if (bwd_entry.id == -1):
            continue
        
        # store size to compact
        num_file_blk = bwd_entry.size
        
        while (0 < num_file_blk):
        
            if (0 == num_gap_blk):
                # find next gap
                for fwd_entry in it.get_fwd():
                    if (fwd_entry.id == -1):
                        break
                    # direct copy file
                    compacted.append(Entry(fwd_entry.id, fwd_entry.size))
                else:
                    # we hit the current backward entry, which we need to finish
                    compacted.append(Entry(bwd_entry.id, num_file_blk))
                    break
                
                # fill current gap
                num_gap_blk = fwd_entry.size
            
            # determine how many blocks to fill
            fill_size = min(num_gap_blk, num_file_blk)
            
            # copy blocks
            compacted.append(Entry(bwd_entry.id, fill_size))
            
            num_file_blk -= fill_size
            num_gap_blk -= fill_size
    
    return compacted

def calculate_checksum(memory: list[Entry]) -> int:
    """Calculate File System Checksum"""
    address = 0
    checksum = 0
    
    for entry in memory:
        # calculate entry checksum for files only
        if (entry.id != -1):
            for block in range(address, address + entry.size):
                checksum += block * entry.id
        # advance to next address
        address += entry.size
    
    return checksum

def part1(puzzle: Puzzle) -> int:
    """Compact Memory and compute Checksum w/ Fragmentation
    
    Returns:
        File System Checksum
    """
    # compact memory (allow fragmentation)
    compacted = compact_memory_fragmented(puzzle)
    # calculate checksum
    checksum = calculate_checksum(compacted)
    
    return checksum

def convert_memory_llist(entries: list[Entry]) -> tuple[LLEntry | None, LLEntry | None]:
    """Convert Memory descriptors to linked list
    
    Returns:
        Tuple of first and last linked list entry.
    """
    root = LLEntry(Entry(-1, 0))
    prev = root
    current = None
    
    for entry in entries:
        current = LLEntry(entry, prev)
        prev.next = current
        prev = current
    
    if (root.next is not None):
        root.next.prev = None
    
    return root.next, current

def print_llist(llentry: LLEntry):
    
    result = ''
    current = llentry
    while (current is not None):
        
        result += (str(current.entry.id) if (current.entry.id != -1) else '.') * current.entry.size
        current = current.next
    
    print(result)

def compact_memory_defragmented(puzzle: Puzzle) -> list[Entry]:
    """Compact Memory w/o Fragmentation
    
    Args:
        puzzle: Puzzle input
    
    Returns:
        List of compacted memory blocks.
    """
    compacted : list[Entry] = []
    
    # convert to linked list
    llist_begin, llist_end = convert_memory_llist(puzzle.entries)
    assert(llist_begin is not None)
    
    def _llist_remove(llentry: LLEntry):
        
        if (llentry.prev is not None):
            llentry.prev.next = llentry.next
        if (llentry.next is not None):
            llentry.next.prev = llentry.prev
        
        return llentry
    
    def _llist_insert(existing: LLEntry, node: LLEntry):
        """Insert Node to the left of existing entry."""
        
        node.prev = existing.prev
        node.next = existing
        existing.prev = node
        if (node.prev is not None):
            node.prev.next = node
        
        return node
    
    def _llist_find_gap(begin: LLEntry, node: LLEntry) -> LLEntry | None:
        """Find gap that's big enough"""
        current = begin
        size = node.entry.size
        
        # traverse list until we reach end or ourselves
        while (current is not None and current is not node):
            # skip non-gaps / small gaps
            if (current.entry.id != -1 or current.entry.size < size):
                current = current.next
                continue
            return current
        
        return None
    
    # begin at list end
    current = llist_end
    
    while (current is not None):
        
        # short-hand for current entry
        llentry = current
        # process next node in backwards direction
        current = current.prev
        
        # skip existing gaps
        if (llentry.entry.id == -1):
            continue
        
        # print_llist(llist_begin)
        
        # find first matching gap
        gap = _llist_find_gap(llist_begin, llentry)
        if (gap is None):
            continue
        
        # move current entry
        _llist_insert(llentry, LLEntry(Entry(-1, llentry.entry.size)))
        llentry = _llist_remove(llentry)
        llentry = _llist_insert(gap, llentry)
        # adjust existing gap
        gap.entry = Entry(-1, gap.entry.size - llentry.entry.size)
        # remove gap entirely if completely filled
        if (gap.entry.size < 1):
            _llist_remove(gap)
    
    # convert linked list to regular list
    current = llist_begin
    while (current is not None):
        compacted.append(current.entry)
        current = current.next
    
    return compacted

def part2(puzzle: Puzzle) -> int:
    """Compact Memory and compute Checksum w/o Fragmentation
    
    Returns:
        File System Checksum
    """
    # compact memory (disallow fragmentation)
    compacted = compact_memory_defragmented(puzzle)
    # calculate checksum
    checksum = calculate_checksum(compacted)
    
    return checksum


def main(args):
    
    puzzle = read_inputs(args.example)
    checksum = part1(puzzle)
    logging.info(f'Part 1: {checksum}')
    checksum = part2(puzzle)
    logging.info(f'Part 2: {checksum}')

if __name__ == '__main__':
    args = setup()
    sys.exit(main(args))
