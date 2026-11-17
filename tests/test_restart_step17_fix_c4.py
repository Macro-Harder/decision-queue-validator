"""Restart Step 17 fix wave 1, Seat C4 tests: chain cost.

Charge M2, counted under both names: Finding 2 of seat 5 and
A21-1. The supersession unit cost on a chain grows
superlinearly in chain length, measured at two sizes in the
seat 5 paper (chain 200, 400, 800) and past a 30 second bound
at 1,000 entries in the seat 21 paper, on files inside every
stated limit (2,000,000 bytes, 10,000 lines, 16,384 characters
per line). The cure is charged in validate.py, in
_supersession_unit and the map print size computation in
_map_print_size, and it changes no stated limit.

The cost pin here is a stated timing bound, as the triage
draft charges: a compact chain of 800 entries, inside every
stated limit as the construction facts assert, runs the full
parse and validate pipeline in at most 2.0 seconds of process
time. On the uncured code the same run took 3.83 seconds of
process time on this machine. Process time is used, not wall
time, so a contended shared machine does not move the bound.
"""

import time
import unittest

import dqv_harness as h

validate = h.import_module("validate")

CHAIN_BOUND_SECONDS = 2.0


def chain_bytes(count):
    """A compact supersession chain: each entry after the first
    supersedes the ruling at the previous entry, in the seat 21
    sentence form. Four lines stand per entry."""
    parts = ["# Decision queue\n\n"]
    for number in range(1, count + 1):
        parts.append("### DQ-%03d: Entry %d\n" % (number, number))
        parts.append("Status: Banked\n")
        if number > 1:
            parts.append(
                "This supersedes the ruling at DQ-%03d.\n\n"
                % (number - 1))
        else:
            parts.append("Prose paragraph here.\n\n")
    return "".join(parts).encode("utf-8")


def _pointers(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return [h.text_of(p) for p in h.as_list(
        h.get(entry, "supersession_pointers"))]


class ChainConstructionTest(unittest.TestCase):
    """Construction facts and the guard: a short chain inside
    every stated limit resolves its pointers. This test passes
    before and after the cure."""

    def test_chain_stays_inside_every_stated_limit(self):
        data = chain_bytes(800)
        self.assertLessEqual(len(data), 2000000)
        self.assertLessEqual(data.count(b"\n"), 10000)
        longest = max(len(line) for line in data.split(b"\n"))
        self.assertLessEqual(longest, 16384)

    def test_short_chain_resolves_its_pointers(self):
        _model, output = h.run_pipeline(chain_bytes(10))
        if output is None:
            raise AssertionError("pipeline returned a failure")
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-002"])
        self.assertEqual(_pointers(output, "DQ-009"), ["DQ-010"])
        self.assertEqual(_pointers(output, "DQ-010"), [])


class ChainCostTest(unittest.TestCase):
    """M2, Finding 2 of seat 5 and A21-1: the chain cost pin."""

    def test_chain_800_cost_within_the_stated_bound(self):
        data = chain_bytes(800)
        start = time.process_time()
        _model, output = h.run_pipeline(data)
        elapsed = time.process_time() - start
        if output is None:
            raise AssertionError("pipeline returned a failure")
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-002"])
        self.assertLessEqual(
            elapsed, CHAIN_BOUND_SECONDS,
            "a chain of 800 entries took %.2f seconds of process "
            "time, over the stated bound of %.1f seconds"
            % (elapsed, CHAIN_BOUND_SECONDS))

    def test_map_print_size_of_a_chain_is_not_over_bound(self):
        pointers = {}
        headed = []
        for number in range(1, 801):
            headed.append("DQ-%03d" % number)
            if number > 1:
                pointers["DQ-%03d" % (number - 1)] = [
                    "DQ-%03d" % number]
        size = validate._map_print_size(pointers, headed, [])
        self.assertLessEqual(size, 2000000)


if __name__ == "__main__":
    unittest.main()
