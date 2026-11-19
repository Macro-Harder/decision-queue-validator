"""Step 17 fix wave 9, Fix Seat C tests.

Charge CH-197, as numbered consecutively from CH-191 in
cluster order under ruling (a) of section 81 of
design/steps/step-17r-record.md (Cluster A two charges,
Cluster B four charges, Cluster C next), sourced at
round 9 attack seat 10 finding A9-10-F1 (Medium, T9-12)
with the further members of round 9 attack seat 12
observation O-9-12-4, consolidated in
design/steps/step-17r-r9-triage-prep.md at Cluster C.
The cure stands in
product/decision_queue_validator/validate.py only, at
the charged locus: the Blocks value reading, the
CH-162 cure family.

CH-197 (seat 10 finding A9-10-F1, Medium, T9-12): the
blocking figure counts blocks fields that name no item,
in 15 fresh forms ("0 entries blocked", "blocks not a
single item", "blocks zero items", "none!nothing" on
the exclamation joiner, "free of obstructions",
"hinders nothing", "holds up nothing", "is not
blocking", "no hindrance", "no item is blocked", "no
roadblock", "not a single item blocked", "not one item
is blocked", "nothing blocks", "the way is clear"),
each at Blocking 1 against a hand truth of 0 under
OP-Q12 as corrected, and the scale case b9-combined at
Blocking 2 against a hand truth of 1; with seat 12
observation O-9-12-4 forms named as further members
("blocks no questions", "blocks no decisions", "no
question is blocked", "path is clear", "clear of
blockers", and the mismatched wrapper "(none]"), and
seat 12's nine neighbour forms standing at Blocking 0
named in the tests in the safe direction. Hand truth
under OP-Q12 as corrected: an entry counts only where
its blocks field names at least one item. The D2
blocking narrowing pin and the O4 corpus bound stand
whole.

No construction in this file builds the F1 shape, and
no banked question is named in any construction.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def open_entry(number, blocks_value, label="Blocks"):
    return (
        "### DQ-%03d: Blocks case %d\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "%s: %s\n"
        "\n"
        "A plain context paragraph.\n"
        % (number, number, label, blocks_value))


def blocking_of(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline produced no output")
    _waiting, blocking = h.waiting_and_blocking(output)
    return output, h.int_of(blocking)


class Ch197BlockingRound9Test(unittest.TestCase):
    """CH-197, A9-10-F1 with O-9-12-4 members: the
    blocking figure no item values, round 9 limbs."""

    def test_spelled_zero_forms_do_not_count(self):
        for value in ("0 entries blocked",
                      "blocks zero items"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_hinder_verb_subject_first_forms_do_not_count(self):
        for value in ("hinders nothing",
                      "holds up nothing"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_plural_obstructions_form_does_not_count(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "free of obstructions"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)

    def test_single_item_negation_forms_do_not_count(self):
        for value in ("blocks not a single item",
                      "not a single item blocked",
                      "not one item is blocked",
                      "no item is blocked"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_exclamation_joiner_does_not_count(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "none!nothing"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)

    def test_further_phrase_forms_do_not_count(self):
        for value in ("is not blocking",
                      "no hindrance",
                      "no roadblock",
                      "nothing blocks",
                      "the way is clear"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_seat12_member_forms_do_not_count(self):
        for value in ("blocks no questions",
                      "blocks no decisions",
                      "no question is blocked",
                      "path is clear",
                      "clear of blockers",
                      "(none]"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_combined_figure_foots_to_hand_truth(self):
        values = (
            "blocks no items",
            "hinders nothing",
            "«none»",
            "none&nothing",
            "zero entries blocked",
            "DQ-002",
            "none",
            "nothing at all",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)
        listed = h.as_list(h.get(output, "blocking_list"))
        listed_ids = [h.text_of(h.get(
            item, "entry_id", "identifier")) for item in listed]
        self.assertEqual(listed_ids, ["DQ-006"])

    def test_same_edge_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "hinders nothing",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_d2_part_exactly_nothing_dot_still_names_an_item(self):
        # Pin under the D2 blocking narrowing pin (seat 10
        # observation O1, a governed bound), passing
        # before and after.
        for value in ("Nothing.", "nothing.",
                      "nothing. and none", "none, nothing."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)

    def test_o4_corpus_form_nothing_named_keeps_standing_treatment(self):
        # Pin under the O4 corpus bound (seat 10
        # observation O2, a governed bound), passing
        # before and after.
        text = ("# Decision queue\n\n"
                + open_entry(1, "nothing named."))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_seat12_neighbour_forms_stand_at_blocking_zero(self):
        # Seat 12's nine neighbour forms of O-9-12-4
        # (M05, M06, M10 to M16), standing at Blocking 0
        # in the safe direction, passing before and
        # after, named as pins.
        for value in ("blocks nothing",
                      "no obstacles",
                      "none;none",
                      "none,none",
                      "none and nothing",
                      "«none»",
                      "does not block anything",
                      "not blocking anything",
                      "zero blockers"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_earlier_cured_forms_still_do_not_count(self):
        # Pins, passing before and after: the CH-162,
        # CH-146, CH-105, CH-86, and CH-66 charged forms
        # keep their cured outcome.
        for value in ("blocks no item", "no obstacles",
                      "`none`", "none.nothing",
                      "zero blocked", "zilch", "nada",
                      "no blockage", "unobstructed",
                      "nothing obstructs",
                      "zero entries blocked", "does not block",
                      "all clear", "_none_", "<none>",
                      "none - nothing", "none = nothing",
                      "nothing blocked", "zero blockers",
                      "none | nothing", "[none]",
                      "none recorded", "no blockers",
                      "blocks nothing", "zero items", "0",
                      "(none)", "none/nothing", "n.a.",
                      "nothing at all", "n/a", "not applicable",
                      "no entries", "nil", "empty",
                      "blocks no entries", "no entry is blocked",
                      "zero items blocked", "0 items blocked",
                      "free of hindrances", "free of roadblocks",
                      "not a single blocker", "no blocker",
                      "blocks zero entries",
                      "‹none›", "„none“",
                      "「none」",
                      "none nothing", "none%nothing",
                      "none^nothing", "none$nothing",
                      "none?nothing", "none§nothing"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_real_reference_beside_fresh_forms_still_counts(self):
        # Guard, passing before and after: a real
        # reference beside a no item part counts, on the
        # fresh joiner as on the standing ones.
        for value in ("DQ-002, none", "none/DQ-002",
                      "DQ-002, hinders nothing",
                      "none!DQ-002",
                      "DQ-002, blocks no questions"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)


if __name__ == "__main__":
    unittest.main()
