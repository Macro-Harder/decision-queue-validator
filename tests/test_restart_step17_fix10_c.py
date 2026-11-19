"""Step 17 fix wave 10, Fix Seat C tests.

Charges CH-239, CH-240, and CH-241, the blocking family
of round 10 in the three charge form ruled at ruling
(b) of section 83 of design/steps/step-17r-record.md,
sourced at round 10 attack seat 10 finding A10-10-F1,
round 10 attack seat 12 findings F-10-12-1, F-10-12-2,
and F-10-12-3, and round 10 attack seat 20 findings
F-20-10-5 and F-20-10-6, consolidated in
design/steps/step-17r-r10-triage-prep.md at Cluster C
(distinct findings T10-11, T10-12, and T10-13). The cure
stands in product/decision_queue_validator/validate.py
only, at the charged locus: the Blocks value reading,
the CH-197 cure family.

CH-239 (T10-11, Medium), the phrase limb: the blocking
figure counts blocks fields that name no item, in the
24 fresh phrase forms of seat 10, the 24 phrase probes
N01 to N24 of seat 12, and the 14 phrase wordings cb01
to cb27 of seat 20, shared members counted once, each
at Blocking 1 against a hand truth of 0 under OP-Q12 as
corrected, with the seat 10 scale case b10-combined at
Blocking 5 against a hand truth of 1, the seat 12
combined file C01 at Blocking 8 against a hand truth
of 0, and the same edge under the What it blocks label.

CH-240 (T10-12, Medium), the joiner limb: the blocking
figure counts blocks fields whose parts are joined by
the 10 fresh joiner forms of seat 10 (the apostrophe,
less than sign, greater than sign, pound sign, euro
sign, degree sign, pilcrow, dagger, middle dot, and
copyright sign standing between the two cured no item
words) and the 5 joiner probes J01 to J04 and J06 of
seat 12 (the asterisk, backtick, apostrophe,
parenthesis, and inverted exclamation joiners), each
at Blocking 1 against a hand truth of 0.

CH-241 (T10-13, Medium), the wrapper limb: the blocking
figure counts blocks fields standing inside the 7 fresh
wrapper forms of seat 10, the 10 wrapper probes W01 to
W08, W10, and W12 of seat 12, and the 4 mismatched
wrapper pairs cb22 to cb25 of seat 20, shared members
counted once, each at Blocking 1 against a hand truth
of 0.

Hand truth under OP-Q12 as corrected: an entry counts
only where its blocks field names at least one item.
The D2 blocking narrowing pin and the O4 corpus bound
stand whole, pinned in both directions in this file,
and a real reference beside a no item part stands as a
confinement pin on the fresh forms as on the standing
ones.

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


def check_values(case, values, expected):
    for value in values:
        with case.subTest(value=value):
            text = ("# Decision queue\n\n"
                    + open_entry(1, value))
            _output, blocking = blocking_of(text)
            case.assertEqual(blocking, expected)


class Ch239BlockingPhrasesRound10Test(unittest.TestCase):
    """CH-239, T10-11: the phrase limb of round 10."""

    def test_seat10_zero_and_noun_phrases_do_not_count(self):
        check_values(self, (
            "blocks zero questions",
            "zero questions blocked",
            "zero decisions blocked",
            "blocks zero decisions",
            "zero items are blocked",
            "zero questions are blocked",
            "blocks 0 items",
            "blocks nil items",
        ), 0)

    def test_seat10_question_ruling_verb_phrases(self):
        check_values(self, (
            "no question blocked",
            "blocks no rulings",
            "no ruling is blocked",
            "no decisions blocked",
            "not a single question blocked",
            "blocks not a single question",
            "nothing is obstructed",
            "obstructs nothing at all",
            "is not obstructing",
        ), 0)

    def test_seat10_barrier_and_path_phrases(self):
        check_values(self, (
            "holds up no item",
            "holds nothing up",
            "no barrier",
            "no barriers",
            "free of barriers",
            "the path is clear",
            "way is clear",
        ), 0)

    def test_seat12_phrases_do_not_count(self):
        check_values(self, (
            "blocks no blockers",
            "blocks zero blockers",
            "0 blockers blocked",
            "no questions blocked",
            "no decisions blocked",
            "no question blocked",
            "not one question is blocked",
            "not a single question blocked",
            "blocks not a single question",
            "blocks zero questions",
            "0 questions blocked",
            "zero questions blocked",
            "hinders no item",
            "obstructs no item",
            "holds up no item",
            "the road is clear",
            "the path is clear",
            "free of hindrance",
            "no obstruction at all",
            "blocks nothing at all",
            "holds no item",
            "impedes no item",
            "no item blocks anything",
            "zero entries are blocked",
        ), 0)

    def test_seat20_phrases_do_not_count(self):
        check_values(self, (
            "blocks no item at all",
            "blocks nothing at all",
            "no question blocked",
            "the path is clear",
            "way is clear",
            "clear of obstacles",
            "not blocking any item",
            "zero items are blocked",
            "0 questions blocked",
            "blocks zero questions",
            "no decision is blocked",
            "hinders no item",
            "holds up no item",
            "blocks no items at all",
        ), 0)

    def test_phrase_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "blocks no blockers",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)


class Ch240BlockingJoinersRound10Test(unittest.TestCase):
    """CH-240, T10-12: the joiner limb of round 10."""

    def test_seat10_joiners_do_not_count(self):
        check_values(self, (
            "none'nothing",
            "none<nothing",
            "none>nothing",
            "none\u00a3nothing",
            "none\u20acnothing",
            "none\u00b0nothing",
            "none\u00b6nothing",
            "none\u2020nothing",
            "none\u00b7nothing",
            "none\u00a9nothing",
        ), 0)

    def test_seat12_joiners_do_not_count(self):
        check_values(self, (
            "none*none",
            "none`nothing",
            "none'none",
            "none(nothing)",
            "none\u00a1nothing",
        ), 0)

    def test_real_reference_beside_fresh_joiner_counts(self):
        # Confinement pin, passing before and after: a
        # real reference beside a no item part counts, on
        # the fresh joiners as on the standing ones (the
        # seat 12 observation form J07 stands first).
        check_values(self, (
            "none*DQ-099",
            "none<DQ-002",
            "DQ-002'none",
            "none\u00a1DQ-002",
        ), 1)


class Ch241BlockingWrappersRound10Test(unittest.TestCase):
    """CH-241, T10-13: the wrapper limb of round 10."""

    def test_seat10_wrappers_do_not_count(self):
        check_values(self, (
            "[none)",
            "{none)",
            "[none}",
            "\u00abnone)",
            "<none]",
            "\uff08none\uff09",
            "\u300enone\u300f",
        ), 0)

    def test_seat12_wrappers_do_not_count(self):
        check_values(self, (
            "[none)",
            "(none}",
            "{none]",
            "[none}",
            "{none)",
            "(none>",
            "\"none'",
            "'none\"",
            "((none]",
            "[[none)",
        ), 0)

    def test_seat20_wrappers_do_not_count(self):
        check_values(self, (
            "[none)",
            "(none}",
            "{none]",
            "\u00abnone]",
        ), 0)


class BlockingScaleRound10Test(unittest.TestCase):
    """The scale cases of the three papers, spanning the
    limbs as the papers file them."""

    def test_seat10_combined_foots_to_hand_truth(self):
        values = (
            "blocks zero questions",
            "the path is clear",
            "none\u00a3nothing",
            "[none)",
            "nothing blocks",
            "DQ-002",
            "none",
            "(none]",
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

    def test_seat12_combined_foots_to_zero(self):
        values = (
            "blocks no blockers",
            "no questions blocked",
            "blocks zero questions",
            "[none)",
            "none*none",
            "the road is clear",
            "hinders no item",
            "no question blocked",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)

    def test_seat10_whatblocks_fresh_foots(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002",
                             label="What it blocks")
                + "\n"
                + open_entry(2, "blocks zero questions",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)


class BlockingPinsRound10Test(unittest.TestCase):
    """The governed pins of the locus, passing before
    and after in both directions."""

    def test_d2_part_exactly_nothing_dot_still_names(self):
        # Pin under the D2 blocking narrowing pin (seat
        # 10 observation O1, a governed bound).
        check_values(self, (
            "Nothing.",
            "nothing.",
            "nothing. and none",
            "none, nothing.",
        ), 1)

    def test_o4_corpus_form_nothing_named_stands(self):
        # Pin under the O4 corpus bound (seat 10
        # observation O2, a governed bound).
        check_values(self, ("nothing named.",), 1)

    def test_seat20_safe_direction_controls_stand(self):
        # The seat 20 group CB controls (cb02, cb03,
        # cb09, cb11, cb18 to cb21, cb26), guarded in the
        # safe direction at observation O-10-20-3.
        check_values(self, (
            "no items are blocked",
            "nothing is blocked",
            "free of blockers",
            "does not block any item",
            "nothing hinders",
            "no obstruction",
            "none~nothing",
            "none#nothing",
            "none!!nothing",
        ), 0)

    def test_earlier_cured_forms_still_do_not_count(self):
        # Pins, passing before and after: the CH-197,
        # CH-162, CH-146, CH-105, CH-86, and CH-66
        # charged forms keep their cured outcome.
        check_values(self, (
            "blocks no questions",
            "blocks no decisions",
            "no question is blocked",
            "path is clear",
            "clear of blockers",
            "(none]",
            "none!nothing",
            "blocks no item", "no obstacles",
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
            "\u2039none\u203a", "\u201enone\u201c",
            "\u300cnone\u300d",
            "none nothing", "none%nothing",
            "none^nothing", "none$nothing",
            "none?nothing", "none\u00a7nothing",
        ), 0)

    def test_real_reference_beside_fresh_phrase_counts(self):
        # Confinement pin, passing before and after: the
        # seat 20 confinement case cb28 form, a real
        # reference beside a fresh no item phrase counts
        # on its own ground.
        check_values(self, (
            "DQ-002, blocks no item at all",
            "DQ-002, blocks zero questions",
        ), 1)


if __name__ == "__main__":
    unittest.main()
