"""Restart Step 17 fix wave 4, Seat K8 tests.

Charges CH-66 and CH-67, ruled at section 38 of
design/steps/step-17r-record.md (flag ruling (e) at FLAG 7
for CH-66 and the charge bounds there) and prepared at
design/steps/step-17r-triage4-prep.md. Both charges stand
in product/decision_queue_validator/validate.py only.

CH-66 (A4-10-F1, seat 10): the blocking figure still counts
Blocks fields that name no item, in fresh phrase forms (no
blockers, blocks nothing, zero items, the digit 0 alone,
and the further forms the finding names), under joiners
the CH-43 cure does not split on (slash, plus, colon),
inside a wrapper (parentheses), and in a dotted
abbreviation (n.a. for n/a). The cure bound: the no item
reading reaches the charged phrase, joiner, wrapper,
abbreviation, and zero count forms, around the D2 bound
and the O4 corpus bound, not through them. The D2 pins, the
governed Step 15 waiting and blocking pins, and the CH-43
pins whole stand.

CH-67 (A4-10-F2, seat 10): a remainder named with the
verbs is open, remains pending, stays pending, is still
pending, remains unresolved, is unresolved, continues
open, or lies open is not read, in the statement or in its
own paragraph. The cure bound: the remainder reading
carries the eight charged verb forms for both subjects
(the rest and the remainder), in bare and named forms, in
the statement and in the own paragraph shapes alike. The
CH-44 pins whole and the CH-9 pins with their exit form
stand, and the PIN-03 pin stands: a part act naming no
remainder stands Ambiguous.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")


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
    """One Banked head entry in the taught form, with the
    given ruling paragraphs standing after a plain context
    paragraph, in the seat 10 paper construction form."""
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
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry %s in the output" % entry_id)
    return h.entry_state(entry)


def blocking_of(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline produced no output")
    _waiting, blocking = h.waiting_and_blocking(output)
    return output, h.int_of(blocking)


class BlockingFigureRound4Test(unittest.TestCase):
    """CH-66, A4-10-F1: the blocking figure no item values,
    round 4 limbs."""

    FRESH_NO_ITEM_VALUES = (
        "no blockers",
        "no blocking items",
        "blocks nothing",
        "none whatsoever",
        "nothing else whatsoever",
        "no item at all",
        "not a single item",
        "zero items",
        "0",
        "0 items",
        "no one",
        "nothing pending",
        "no blocks",
        "none pending",
        "nothing to block",
        "no further entries",
        "nothing more",
        "none more",
        "no items at all",
        "empty list",
        "blank",
        "void",
        "(none)",
        "none/nothing",
        "none + nothing",
        "none: nothing",
        "n.a.",
        "does not block anything",
        "no",
        "nothing in particular",
    )

    def test_a4_10_f1_each_fresh_no_item_value_does_not_count(self):
        for value in self.FRESH_NO_ITEM_VALUES:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_a4_10_f1_combined_figure(self):
        values = (
            "no blockers",
            "none whatsoever",
            "no item at all",
            "nothing pending",
            "none/nothing",
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

    def test_a4_10_f1_same_edge_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "no blockers",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_ch43_pins_whole_stand(self):
        # Pin, passing before and after: the CH-43 charged
        # forms keep their cured outcome, n/a among them, so
        # the slash reading of this cure cannot re-read the
        # cured abbreviation as two parts naming an item.
        for value in ("nothing at all", "none at all",
                      "nothing whatsoever", "none; nothing else",
                      "none or nothing", "none & nothing",
                      "None!", "n/a", "not applicable",
                      "no entries", "nil", "empty",
                      "Nothing.."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_d2_part_exactly_nothing_dot_still_names_an_item(self):
        # Pin under the D2 bound: a part that is exactly
        # nothing., case aside, names an item and counts, as
        # the governed Step 15 pin
        # test_waiting_and_blocking_carry_their_unit records.
        for value in ("Nothing.", "nothing."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)

    def test_d2_composites_beside_nothing_dot_still_count(self):
        # The D2 bound own terms: a value carrying the exact
        # part nothing. beside a no item part counts.
        for value in ("nothing. and none", "none, nothing."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)

    def test_o4_corpus_form_nothing_named_keeps_standing_treatment(self):
        # The O4 corpus bound, not charged: the corpus form
        # nothing named. stands counted, as the Fix C3 paper
        # bound left it.
        text = ("# Decision queue\n\n"
                + open_entry(1, "nothing named."))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_real_reference_beside_no_item_part_still_counts(self):
        # Guard, passing before and after: a field naming a
        # real reference beside a no item part names an item,
        # under the standing joiners and under the fresh
        # slash joiner alike.
        for value in ("DQ-002, none", "none/DQ-002"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)


class PartScopeRemainderRound4Test(unittest.TestCase):
    """CH-67, A4-10-F2: part scope remainder verb widths,
    round 4 limbs."""

    STATEMENT_FORMS = (
        (2, "Rest bare is open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is open."),
        (3, "Remainder bare is open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder is open."),
        (4, "Rest named is open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, is open."),
        (5, "Remainder named is open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "is open."),
        (6, "Rest bare remains pending",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest remains pending."),
        (7, "Remainder bare remains pending",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder remains pending."),
        (8, "Rest named remains unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, "
         "remains unresolved."),
        (10, "Rest bare is still pending",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest is still pending."),
        (11, "Remainder bare continues open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder continues open."),
        (12, "Rest bare lies open",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest lies open."),
        (13, "Remainder named is unresolved",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "is unresolved."),
        (14, "Settled rest bare is open",
         "Settled by Captain JP: the first part is settled, "
         "take Option A. The rest is open."),
    )

    def test_a4_10_f2_statement_forms_derive_settled_in_part(self):
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
                entry = h.entry_by_id(output, entry_id)
                remainder = h.get(entry, "remainder_text",
                                  "remainder")
                self.assertTrue(remainder)

    def test_a4_10_f2_statement_combined_figures(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control rest stands open named",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "stands open."]))
        for number, title, paragraph in self.STATEMENT_FORMS:
            parts.append(taught_entry(number, title, [paragraph]))
        parts.append(taught_entry(
            9, "Remainder named stays pending",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stays pending."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 14)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 14)

    def test_a4_10_f2_own_paragraph_forms_derive_settled_in_part(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control remainder stands open",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        parts.append(taught_entry(
            2, "Rest bare is open para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest is open."]))
        parts.append(taught_entry(
            3, "Remainder remains pending para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder remains pending."]))
        parts.append(taught_entry(
            4, "Rest remains unresolved para",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest remains unresolved."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 4)
        self.assertEqual(counts.get("Ruled"), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 4)

    def test_named_stays_pending_form_stands(self):
        # Pin inside the charged file, passing before and
        # after: the named remainder with stays pending is
        # read through the standing generic stays pattern,
        # as the round 4 paper records at DQ-009.
        text = ("# Decision queue\n\n" + taught_entry(
            9, "Remainder named stays pending",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stays pending."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-009"),
                         "Settled in part")

    def test_ch44_cured_forms_still_derive_settled_in_part(self):
        # Pin, passing before and after: the CH-44 pins
        # whole, the remains, stays open, and is still open
        # forms of round 3.
        forms = (
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest remains open."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stays open."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "is still open."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest stays open."],
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

    def test_ch9_cured_forms_still_derive_settled_in_part(self):
        # Pin, passing before and after: the CH-9 pins whole,
        # including the round 2 A2-10-F4 forms.
        forms = (
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stands open."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest still stands open."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."],
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
        # PIN-03 pin, passing before and after: a part act
        # naming no remainder stands Ambiguous.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Part no remainder",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ambiguous")
        self.assertEqual(h.ambiguous_count(output), 1)

    def test_whole_ruling_still_derives_ruled(self):
        # Guard, passing before and after: a ruling statement
        # that limits nothing to a part still derives Ruled
        # whole.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Whole ruling entry",
            ["Ruled by Captain JP: this entry is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ruled")


if __name__ == "__main__":
    unittest.main()
