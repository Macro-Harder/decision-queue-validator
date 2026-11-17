"""Restart Step 17 fix wave 2 closing, Defect Repair Seat D2 tests.

Defect: the governed Step 15 pin
test_waiting_and_blocking_carry_their_unit in
product/tests/test_restart_step15_fix_b.py fails on the wave 2
cured tree, the blocking figure reading 0 where the pin expects
1. The moving hunk is the CH-10 cure in validate.py (cluster K7):
its _blocks_names_an_item helper reads a Blocks value in its
ordinary sentence form, case aside with a trailing full stop
stripped from every part, and its no item set gains the bare
word nothing. That reading sweeps in the value Nothing., the
whole value of the Step 15 pin unit, and of the standard taught
open entry form across the restart pins.

The bound that narrows it stands in the wave 1 Fix C3 paper
(design/steps/step-17r-fix1-c3.md, charge 4): the wave 1 cure
set is exactly none and nothing else, case aside, and value
forms standing in the corpus and in the restart pins, such as
"nothing.", keep their standing treatment and are untouched by
that cure. The round 2 charge CH-10, as its preparation entry
states it (design/steps/step-17r-triage2-prep.md, A2-10-F2),
names the cured values with a full stop added, the bare word
nothing, and no items: it does not name the form "nothing."
with its full stop. The narrowing therefore holds one exact
form apart: a part that is exactly the word nothing with its
full stop, in any case, keeps its standing treatment and names
an item, while every charged CH-10 form keeps its cured
outcome. These tests pin both directions at that locus.
"""

import unittest

import dqv_harness as h

HEADER = "# Decision Queue\n\n## Open items\n\n"


def run_text(text):
    model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return model, output


def step15_unit():
    # The Step 15 pin unit, in the pin file's own open_entry
    # form: one Banked entry, Blocks: Nothing.
    return HEADER + (
        "### DQ-001: Synthetic entry 1\n\n"
        "Status: Banked\n\n"
        "A plain paragraph stands in this entry.\n\n"
        "Owner of record: Decision-queue Clerk\n\n"
        "Question: A synthetic question for entry 1?\n\n"
        "Options: Option one. Option two.\n\n"
        "Cost: Low.\n\n"
        "Blocks: Nothing.\n")


def blocks_entry(number, blocks_value, label="Blocks"):
    return (
        "### DQ-%03d: Blocks case %d\n\n"
        "Status: Banked\n\n"
        "Question: Which option?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked.\n\n"
        "%s: %s\n\n"
        "A plain context paragraph.\n"
        % (number, number, label, blocks_value))


def blocking_of(text):
    _model, output = run_text(text)
    _waiting, blocking = h.waiting_and_blocking(output)
    return h.int_of(blocking), output


class Step15PinDirectionTest(unittest.TestCase):
    """The Step 15 pin direction: Nothing. carries its count."""

    def test_step15_unit_carries_waiting_and_blocking_one(self):
        model, output = run_text(step15_unit())
        waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 1)
        self.assertEqual(h.int_of(blocking), 1)
        units = h.get(output, "counting_units")
        self.assertEqual(h.get(units, "waiting"), "entries")
        self.assertEqual(h.get(units, "blocking"), "entries")
        listed = h.as_list(h.get(output, "blocking_list"))
        listed_ids = [h.text_of(h.get(
            item, "entry_id", "identifier")) for item in listed]
        self.assertEqual(listed_ids, ["DQ-001"])

    def test_nothing_sentence_form_under_what_it_blocks_counts(self):
        text = HEADER + blocks_entry(
            1, "Nothing.", label="What it blocks")
        blocking, _output = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_nothing_sentence_form_lower_case_counts(self):
        # The Fix C3 bound names the form in lower case; the
        # standing treatment is case aside, as that cure reads
        # its own set case aside.
        text = HEADER + blocks_entry(1, "nothing.")
        blocking, _output = blocking_of(text)
        self.assertEqual(blocking, 1)


class ChargedDirectionTest(unittest.TestCase):
    """The CH-10 direction: every charged form keeps its cure."""

    CHARGED_NO_ITEM_VALUES = (
        "none",
        "nothing else",
        "NONE",
        "None.",
        "nothing else.",
        "nothing",
        "no items",
        "none, nothing else",
        "Nothing else at all",
    )

    def test_each_charged_no_item_value_does_not_count(self):
        for value in self.CHARGED_NO_ITEM_VALUES:
            with self.subTest(value=value):
                text = HEADER + blocks_entry(1, value)
                blocking, _output = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_charged_edge_under_what_it_blocks_label(self):
        text = (HEADER + blocks_entry(1, "DQ-002")
                + "\n" + blocks_entry(
                    2, "None.", label="What it blocks"))
        blocking, _output = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_attack_combined_figure_stands_at_three(self):
        # The seat 10 round 2 attack construction f2-combined,
        # in the K7 test file's in process form: twelve entries
        # identical except for the Blocks field.
        values = (
            "DQ-002", "none", "nothing else", "None.",
            "nothing else.", "NONE", "nothing", "no items",
            "nothing named.", "none, nothing else",
            "Nothing else at all", "DQ-002, none",
        )
        text = HEADER + "\n".join(
            blocks_entry(number, value)
            for number, value in enumerate(values, start=1))
        blocking, output = blocking_of(text)
        self.assertEqual(blocking, 3)
        listed = h.as_list(h.get(output, "blocking_list"))
        listed_ids = [h.text_of(h.get(
            item, "entry_id", "identifier")) for item in listed]
        self.assertEqual(listed_ids,
                         ["DQ-001", "DQ-009", "DQ-012"])

    def test_mixed_none_beside_a_real_reference_counts(self):
        text = HEADER + blocks_entry(1, "DQ-002, none")
        blocking, _output = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_o4_corpus_form_nothing_named_counts(self):
        text = HEADER + blocks_entry(1, "nothing named.")
        blocking, _output = blocking_of(text)
        self.assertEqual(blocking, 1)


if __name__ == "__main__":
    unittest.main()
