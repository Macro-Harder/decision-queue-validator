"""Step 17 fix wave 7, Fix Seat K10 tests.

Charges CH-146 and CH-147, as ruled at section 66 of
design/steps/step-17r-record.md, sourced at round 7 attack
seat 10, design/steps/step-17r-attack7-10.md. Every cure
stands in product/decision_queue_validator/validate.py only.

CH-146 (seat 10 finding A7-10-F1, Medium): the blocking
figure still counts blocks fields that name no item, in
fresh phrase forms (further no item phrases in ordinary
words), in the cured word none inside wrappers the cure
does not read (backtick, guillemet, curly quote), and in
the cured words joined by characters no split in the
reading covers (full stop, underscore, em dash, en dash,
bullet mark). Hand truth under OP-Q12 as corrected: an
entry counts only where its blocks field names at least
one item. The D2 blocking narrowing pin and the O4 corpus
bound stand whole, and the excluded forms at observation
O3 of the attack paper stand at their measured standing,
outside the charge.

CH-147 (seat 10 finding A7-10-F2, Medium): a remainder
named with a fresh verb form (stays unresolved, stands
outstanding, is still undecided, is awaiting a decision,
awaits a ruling, has not been decided, is not decided, is
left pending, is left unresolved, remains on hold, is
deferred, continues unresolved, still remains open, lies
unresolved, is in abeyance) is not read, in the statement
or in its own paragraph. Hand truth under PIN-01 and
PIN-03: every entry in the constructions names its
remainder in words, so Settled in part for each. The
balance subject forms at observation O8 of the attack
paper stand outside the charge and keep their standing.

No construction in this file builds the F1 shape, and no
banked question is named in any construction.

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


def taught_entry(number, title, ruling_paragraphs):
    text = (
        "### DQ-%03d: %s\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "A plain context paragraph.\n" % (number, title))
    for paragraph in ruling_paragraphs:
        text += "\n" + paragraph + "\n"
    return text


def state_of(output, entry_id):
    found = h.entry_by_id(output, entry_id)
    if found is None:
        raise AssertionError("no entry %s in the output" % entry_id)
    return h.entry_state(found)


def blocking_of(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline produced no output")
    _waiting, blocking = h.waiting_and_blocking(output)
    return output, h.int_of(blocking)


class Ch146BlockingRound7Test(unittest.TestCase):
    """CH-146, A7-10-F1: the blocking figure no item
    values, round 7 limbs."""

    FRESH_PHRASES = (
        "blocks no item",
        "blocks no items",
        "no item blocked",
        "no items blocked",
        "does not block any item",
        "not blocking anything",
        "no obstacles",
        "free of obstacles",
        "unimpeded",
        "nothing stands in the way",
        "no roadblocks",
        "no hindrances",
        "zero blocked",
        "0 blocked",
        "not a single entry",
        "nothing holds",
        "no holds",
        "does not impede",
        "empty set",
    )

    FRESH_WRAPPERS = (
        "`none`",
        "\u00abnone\u00bb",
        "\u201cnone\u201d",
    )

    FRESH_JOINS = (
        "none.nothing",
        "none_nothing",
        "none\u2014nothing",
        "none\u2013nothing",
        "none\u2022nothing",
    )

    def test_fresh_phrase_forms_do_not_count(self):
        for value in self.FRESH_PHRASES:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_fresh_wrapper_forms_do_not_count(self):
        for value in self.FRESH_WRAPPERS:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_fresh_joiner_forms_do_not_count(self):
        for value in self.FRESH_JOINS:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_combined_figure_foots_to_hand_truth(self):
        values = (
            "blocks no item",
            "no obstacles",
            "`none`",
            "none.nothing",
            "zero blocked",
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
                + open_entry(2, "blocks no item",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_d2_part_exactly_nothing_dot_still_names_an_item(self):
        # Pin under the D2 blocking narrowing pin,
        # passing before and after.
        for value in ("Nothing.", "nothing.",
                      "nothing. and none", "none, nothing."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)

    def test_o4_corpus_form_nothing_named_keeps_standing_treatment(self):
        # Pin under the O4 corpus bound, passing before
        # and after.
        text = ("# Decision queue\n\n"
                + open_entry(1, "nothing named."))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_o3_excluded_forms_stand_excluded(self):
        # Observation O3 forms, passing before and after,
        # outside the charge.
        for value in ("none-nothing", "none=nothing",
                      "~none~", "__none__", "none&nothing"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_earlier_cured_forms_still_do_not_count(self):
        # Pins, passing before and after: the CH-105,
        # CH-86, and CH-66 charged forms keep their
        # cured outcome.
        for value in ("zilch", "nada", "no blockage",
                      "unobstructed", "nothing obstructs",
                      "zero entries blocked", "does not block",
                      "all clear", "_none_", "<none>",
                      "none - nothing", "none = nothing",
                      "nothing blocked", "zero blockers",
                      "none | nothing", "[none]",
                      "none recorded", "no blockers",
                      "blocks nothing", "zero items", "0",
                      "(none)", "none/nothing", "n.a.",
                      "nothing at all", "n/a", "not applicable",
                      "no entries", "nil", "empty"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_real_reference_beside_fresh_forms_still_counts(self):
        # Guard, passing before and after in its standing
        # forms; the fresh joiner forms of it stand with
        # the cure.
        for value in ("DQ-002, none", "none/DQ-002",
                      "DQ-002, blocks no item",
                      "none.DQ-002", "none\u2014DQ-002"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)


class Ch147RemainderRound7Test(unittest.TestCase):
    """CH-147, A7-10-F2: part scope remainder verb widths,
    round 7 limbs, in the statement and in the own
    paragraph shapes alike."""

    STATEMENT_FORMS = (
        (2, "Rest stays unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest stays unresolved."),
        (3, "Remainder named stands outstanding",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "stands outstanding."),
        (4, "Remainder is still undecided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder is still undecided."),
        (5, "Rest named is awaiting a decision",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, "
         "is awaiting a decision."),
        (6, "Remainder awaits a ruling",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder awaits a ruling."),
        (7, "Rest has not been decided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest has not been decided."),
        (8, "Remainder is not decided",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder is not decided."),
        (9, "Rest named is left pending",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, "
         "is left pending."),
        (10, "Remainder is left unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder is left unresolved."),
        (11, "Rest remains on hold",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest remains on hold."),
        (12, "Remainder named is deferred",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "is deferred."),
        (13, "Rest continues unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest continues unresolved."),
        (14, "Remainder still remains open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder still remains open."),
        (16, "Remainder lies unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder lies unresolved."),
        (17, "Rest is in abeyance",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is in abeyance."),
        (18, "Settled rest stays unresolved mirror",
         "Settled by Captain JP: the first part is settled, "
         "take Option A. The rest stays unresolved."),
    )

    def test_statement_forms_derive_settled_in_part(self):
        for number, title, paragraph in self.STATEMENT_FORMS:
            with self.subTest(title=title):
                text = ("# Decision queue\n\n" + taught_entry(
                    number, title, [paragraph]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                entry_id = "DQ-%03d" % number
                self.assertEqual(state_of(output, entry_id),
                                 "Settled in part")
                found = h.entry_by_id(output, entry_id)
                remainder = h.get(found, "remainder_text",
                                  "remainder")
                self.assertTrue(remainder)

    def test_statement_combined_figures(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control rest stands open named",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "stands open."]))
        for number, title, paragraph in self.STATEMENT_FORMS:
            parts.append(taught_entry(number, title, [paragraph]))
        parts.append(taught_entry(
            15, "Rest named is pending decision",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "is pending decision."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 18)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 18)

    def test_own_paragraph_forms_derive_settled_in_part(self):
        forms = (
            (2, "Rest stays unresolved para",
             "The rest stays unresolved."),
            (3, "Remainder stands outstanding para",
             "The remainder stands outstanding."),
            (4, "Remainder is awaiting a decision para",
             "The remainder is awaiting a decision."),
            (5, "Remainder has not been decided para",
             "The remainder has not been decided."),
            (6, "Rest remains on hold para",
             "The rest remains on hold."),
        )
        for number, title, remainder_line in forms:
            with self.subTest(title=title):
                text = ("# Decision queue\n\n" + taught_entry(
                    number, title,
                    ["Ruled by Captain JP: the first part is "
                     "ruled, take Option A.",
                     remainder_line]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                entry_id = "DQ-%03d" % number
                self.assertEqual(state_of(output, entry_id),
                                 "Settled in part")

    def test_own_paragraph_combined_figures(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control remainder stands open",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        forms = (
            (2, "Rest stays unresolved para",
             "The rest stays unresolved."),
            (3, "Remainder stands outstanding para",
             "The remainder stands outstanding."),
            (4, "Remainder is awaiting a decision para",
             "The remainder is awaiting a decision."),
            (5, "Remainder has not been decided para",
             "The remainder has not been decided."),
            (6, "Rest remains on hold para",
             "The rest remains on hold."),
        )
        for number, title, remainder_line in forms:
            parts.append(taught_entry(
                number, title,
                ["Ruled by Captain JP: the first part is "
                 "ruled, take Option A.",
                 remainder_line]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 6)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 6)

    def test_ch106_and_ch87_cured_forms_still_derive(self):
        # Pin, passing before and after: the CH-106 and
        # CH-87 pins whole, in the statement and own
        # paragraph shapes.
        forms = (
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest is pending."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder awaits a decision."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder stands undecided."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest is still unresolved."],
        )
        for paragraphs in forms:
            with self.subTest(paragraphs=paragraphs):
                text = ("# Decision queue\n\n" + taught_entry(
                    1, "Cured form", paragraphs))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertEqual(state_of(output, "DQ-001"),
                                 "Settled in part")

    def test_pin03_part_act_with_no_remainder_is_ambiguous(self):
        # PIN-03 pin, passing before and after.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Part no remainder",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ambiguous")
        self.assertEqual(h.ambiguous_count(output), 1)

    def test_balance_subject_stands_outside_the_charge(self):
        # Observation O8 of the attack paper, passing
        # before and after: no governing text names a
        # third subject, and the balance forms keep
        # their standing.
        for paragraph in (
                "Ruled by Captain JP: the first part is "
                "ruled, take Option A. The balance, the "
                "second part, stands open.",
                "Ruled by Captain JP: the first part is "
                "ruled, take Option A. The balance stands "
                "open."):
            with self.subTest(paragraph=paragraph):
                text = ("# Decision queue\n\n" + taught_entry(
                    1, "Balance subject", [paragraph]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertEqual(state_of(output, "DQ-001"),
                                 "Ambiguous")


if __name__ == "__main__":
    unittest.main()
