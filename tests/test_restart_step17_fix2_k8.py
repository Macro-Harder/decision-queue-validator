"""Restart Step 17 fix wave 2, Seat K8 tests: the two cost loci.

Charges CH-11 and CH-12, ruled at section 19 of
design/steps/step-17r-record.md, prepared at
design/steps/step-17r-triage2-prep.md under seat 5 Finding 1
(one finding standing as both charges, one per locus, counted
once) and seat 21 findings A2-21-1 (at CH-11) and A2-21-2 (at
CH-12). Both charges stand in product/decision_queue_validator/
validate.py only, and neither cure may change any output.

CH-11: validate_model rebuilt the headed number set from every
entry in the file on every iteration of its per entry loop, so
one run paid one full set build per entry. The cost pin here is
a call count, not a wall clock: a counting wrapper around
validate._entry_number records every call one pipeline run
makes. On a plain file of N entries the uncured code calls it
N squared times from the rebuild alone (measured 41,000 calls
in total at N of 200, of which 40,000 stand in the rebuild).
The cured code builds the set once, so the total stands linear
in N: the bound below allows 20 calls per entry, which covers
the one build and the fixed handful of other per entry uses
the run makes of the same helper.

CH-12: _map_print_size computed and stored a full downstream
reach closure per entry through its reach_set helper, so a
chain paid one suffix walk per entry. The cost pin here is a
pointer step count in a stated form: the pointers mapping is
handed to _map_print_size as a dict subclass that counts its
own get calls, and every walk the computation makes reads its
next pointers through that method. On a chain of N entries the
uncured code pays about N squared over two get calls (measured
125,750 at N of 500). The cured code reads the graph a fixed
number of times, so the total stands linear in N under the
same 20 per entry bound.

The guard tests pin the outputs the two loci feed, on shapes
chosen so a cure that changed behaviour would move them: the
ghost number Note the headed number set governs, and the map
print sizes of chain, cycle, branch, and shared cycle shapes.
The guard tests pass before and after the cures.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

CALLS_PER_ENTRY_BOUND = 20


def plain_bytes(count):
    """A plain file: a queue header plus count minimal entries,
    each a heading line and one Status line, in the seat 21
    A2-21-1 construction form."""
    parts = ["# Decision queue\n\n"]
    for number in range(1, count + 1):
        parts.append("### DQ-%03d: Entry %d\n" % (number, number))
        parts.append("Status: Banked\n\n")
    return "".join(parts).encode("utf-8")


def chain_pointers(count):
    """The pointers and headed identifiers of a supersession
    chain of count entries: each entry is superseded by the
    next, in the seat 21 A2-21-2 construction form."""
    pointers = {}
    headed = []
    for number in range(1, count + 1):
        headed.append("DQ-%03d" % number)
        if number > 1:
            pointers["DQ-%03d" % (number - 1)] = [
                "DQ-%03d" % number]
    return pointers, headed


class CountingPointers(dict):
    """A pointers mapping that counts its own get calls: one
    count per pointer step the computation under test reads."""

    def __init__(self, *args):
        super().__init__(*args)
        self.get_calls = 0

    def get(self, key, default=None):
        self.get_calls += 1
        return super().get(key, default)


class HeadedNumberSetCostTest(unittest.TestCase):
    """CH-11, seat 5 Finding 1 limb two and A2-21-1: the per
    entry headed number set rebuild in validate_model."""

    def test_entry_number_calls_stay_linear_in_entry_count(self):
        count = 200
        original = validate._entry_number
        calls = [0]

        def counting(entry):
            calls[0] += 1
            return original(entry)

        validate._entry_number = counting
        try:
            _model, output = h.run_pipeline(plain_bytes(count))
        finally:
            validate._entry_number = original
        if output is None:
            raise AssertionError("pipeline returned a failure")
        self.assertEqual(h.int_of(h.entry_total(output)), count)
        self.assertLessEqual(
            calls[0], CALLS_PER_ENTRY_BOUND * count,
            "one run over %d entries called _entry_number %d "
            "times, over the linear bound of %d: the headed "
            "number set is still being rebuilt per entry"
            % (count, calls[0], CALLS_PER_ENTRY_BOUND * count))

    def test_ghost_note_reads_the_headed_set_as_before(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: First entry\n\n"
            "Status: Ruled\n\n"
            "Ruled by Captain JP on 2026-01-01.\n\n"
            "Ruling text: DQ-999 is ruled. DQ-002 is ruled.\n\n"
            "Ruling outcome: Done.\n\n"
            "Where it landed: In the record.\n\n"
            "### DQ-002: Second entry\n\n"
            "Status: Banked\n\n"
            "Prose paragraph here.\n"
        ).encode("utf-8")
        _model, output = h.run_pipeline(data)
        if output is None:
            raise AssertionError("pipeline returned a failure")
        ghost = [finding for finding in h.findings_of(output)
                 if h.text_of(h.get(finding, "rule_id")) == "PD-R7"]
        self.assertEqual(len(ghost), 1)
        self.assertIn("DQ-999", h.finding_statement(ghost[0]))
        self.assertEqual(len(h.findings_of(output)), 5)


class MapPrintSizeCostTest(unittest.TestCase):
    """CH-12, seat 5 Finding 1 limb one and A2-21-2: the per
    entry reach set recomputation in _map_print_size."""

    def test_pointer_steps_stay_linear_in_chain_length(self):
        count = 500
        pointers, headed = chain_pointers(count)
        counted = CountingPointers(pointers)
        size = validate._map_print_size(counted, headed, [])
        self.assertEqual(size, 5118)
        self.assertLessEqual(
            counted.get_calls, CALLS_PER_ENTRY_BOUND * count,
            "the map print size of a chain of %d entries read "
            "pointers %d times, over the linear bound of %d: "
            "a full reach closure is still being computed per "
            "entry" % (count, counted.get_calls,
                        CALLS_PER_ENTRY_BOUND * count))

    def test_map_print_sizes_of_the_guard_shapes_stand(self):
        cases = []

        pointers, headed = chain_pointers(10)
        cases.append(("chain10", pointers, headed, [], 218))

        cases.append((
            "ring4",
            {"DQ-001": ["DQ-002"], "DQ-002": ["DQ-003"],
             "DQ-003": ["DQ-004"], "DQ-004": ["DQ-001"]},
            ["DQ-001", "DQ-002", "DQ-003", "DQ-004"],
            [["DQ-001", "DQ-002", "DQ-003", "DQ-004"]], 176))

        cases.append((
            "diamond",
            {"DQ-001": ["DQ-002", "DQ-003"],
             "DQ-002": ["DQ-004"], "DQ-003": ["DQ-004"]},
            ["DQ-001", "DQ-002", "DQ-003", "DQ-004"], [], 175))

        cases.append((
            "cyclebranch",
            {"DQ-001": ["DQ-002"],
             "DQ-002": ["DQ-001", "DQ-003"], "DQ-003": []},
            ["DQ-001", "DQ-002", "DQ-003"],
            [["DQ-001", "DQ-002"]], 183))

        cases.append((
            "twocycles",
            {"DQ-001": ["DQ-002"],
             "DQ-002": ["DQ-001", "DQ-003"],
             "DQ-003": ["DQ-002"]},
            ["DQ-001", "DQ-002", "DQ-003"],
            [["DQ-001", "DQ-002"], ["DQ-002", "DQ-003"]], 271))

        cases.append((
            "selfloop",
            {"DQ-001": ["DQ-001"]}, ["DQ-001"], [["DQ-001"]], 146))

        cases.append(("empty", {}, [], [], 121))

        cases.append((
            "rho",
            {"DQ-001": ["DQ-002"], "DQ-002": ["DQ-003"],
             "DQ-003": ["DQ-004"], "DQ-004": ["DQ-003"]},
            ["DQ-001", "DQ-002", "DQ-003", "DQ-004"],
            [["DQ-003", "DQ-004"]], 176))

        for name, pointers, headed, cycles, expected in cases:
            with self.subTest(shape=name):
                self.assertEqual(
                    validate._map_print_size(pointers, headed,
                                             cycles),
                    expected)


if __name__ == "__main__":
    unittest.main()
