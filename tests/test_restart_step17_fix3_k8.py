"""Restart Step 17 fix wave 3, Seat K8 tests.

Charges CH-43 and CH-44, ruled at section 26 of
design/steps/step-17r-record.md (flag ruling (h) especially)
and prepared at design/steps/step-17r-triage3-prep.md. Both
charges stand in product/decision_queue_validator/validate.py
only.

CH-43 (A3-10-F1, seat 10): the blocking figure still counts
Blocks fields that name no item, in the cured values own
neighbouring forms and in further no item phrases: the cured
values with an exclamation mark, values joined by a semicolon,
by or, or by an ampersand, the phrases nothing at all, none at
all, nothing whatsoever, nothing further, no entries, not
applicable, n/a, nil, and empty, and the cured values with a
space before the full stop. The cure bound, from ruling (h):
a Blocks value whose every part, read under the ordinary
sentence punctuation and joiner forms, names no item does not
count; the widening goes around the D2 bound, not through it.
A part that is exactly nothing., case aside, still names an
item under D2, and the corpus form nothing named. still
counts under the Fix C3 bound at observation O2.

CH-44 (A3-10-F2, seat 10): a remainder named with the verbs
remains, stays open, or is still open is not read, in the
statement or in its own paragraph. The cure bound: a
remainder named in words with remains, stays open, or is
still open, in the statement or in its own paragraph, is
extracted as the cured forms are. The PIN-03 pin stands: a
part act naming no remainder stands Ambiguous.
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


class BlockingFigureRound3Test(unittest.TestCase):
    """CH-43, A3-10-F1: the blocking figure no item values,
    round 3 limbs."""

    FRESH_NO_ITEM_VALUES = (
        "None!",
        "nothing else!",
        "no item!",
        "none; nothing else",
        "none or nothing",
        "none & nothing",
        "nothing at all",
        "none at all",
        "nothing whatsoever",
        "nothing further",
        "no entries",
        "not applicable",
        "n/a",
        "nil",
        "empty",
        "none .",
        "nothing .",
    )

    def test_a3_10_f1_each_fresh_no_item_value_does_not_count(self):
        for value in self.FRESH_NO_ITEM_VALUES:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_a3_10_f1_combined_figure(self):
        values = (
            "None!",
            "nothing at all",
            "none; nothing else",
            "none or nothing",
            "not applicable",
            "DQ-002",
            "nothing else.",
            "none",
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

    def test_a3_10_f1_same_edge_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "None!", label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_ch10_charged_no_item_values_still_do_not_count(self):
        # Pin, passing before and after: the CH-10 pins whole
        # in their D2 narrowed form keep their cured outcome.
        for value in ("None.", "nothing else.", "nothing",
                      "no items", "none, nothing else",
                      "Nothing else at all"):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 0)

    def test_d2_part_exactly_nothing_dot_still_names_an_item(self):
        # Pin under ruling (h): a part that is exactly
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
        # Observation O1 of the round 3 seat 10 paper, on the
        # D2 bound own terms: a value carrying the exact part
        # nothing. beside a no item part counts.
        for value in ("nothing. and none", "none, nothing."):
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _output, blocking = blocking_of(text)
                self.assertEqual(blocking, 1)

    def test_o2_corpus_form_nothing_named_keeps_standing_treatment(self):
        # Observation O2 bound, not charged: the corpus form
        # nothing named. stands counted, as the Fix C3 paper
        # bound left it.
        text = ("# Decision queue\n\n"
                + open_entry(1, "nothing named."))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_nothing_double_dot_does_not_count(self):
        # The attack paper V2 form: Nothing.. is not the exact
        # D2 part, and the sentence form reading reads it down
        # to the no item word.
        text = ("# Decision queue\n\n"
                + open_entry(1, "Nothing.."))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)

    def test_real_reference_beside_no_item_part_still_counts(self):
        # Guard, passing before and after: a field naming a
        # real reference beside a no item part names an item.
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002, none"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)


class PartScopeRemainderRound3Test(unittest.TestCase):
    """CH-44, A3-10-F2: part scope remainder reading, round 3
    limbs."""

    STATEMENT_FORMS = (
        (2, "Rest stays open bare",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest stays open."),
        (3, "Rest remains open bare",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest remains open."),
        (4, "Remainder remains open bare",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder remains open."),
        (5, "Remainder remains open named",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The remainder, the second part, "
         "remains open."),
        (6, "Rest remains open named",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, "
         "remains open."),
        (7, "Rest is still open named",
         "Ruled by Captain JP: the first part is ruled, "
         "take Option A. The rest, the second part, "
         "is still open."),
        (9, "Settled rest remains open",
         "Settled by Captain JP: the first part is settled, "
         "take Option A. The rest remains open."),
    )

    def test_a3_10_f2_statement_forms_derive_settled_in_part(self):
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

    def test_a3_10_f2_statement_combined_figures(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control remainder stands open",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stands open."]))
        for number, title, paragraph in self.STATEMENT_FORMS:
            parts.append(taught_entry(number, title, [paragraph]))
        parts.append(taught_entry(
            8, "Control rest stands open named",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest, the second part, "
             "stands open."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 9)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 9)

    def test_a3_10_f2_own_paragraph_forms_derive_settled_in_part(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Next paragraph rest stays open",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest stays open."]))
        parts.append(taught_entry(
            2, "Next paragraph remainder remains",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder remains open."]))
        parts.append(taught_entry(
            3, "Control next paragraph cured",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 3)
        self.assertEqual(counts.get("Ruled"), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 3)

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
