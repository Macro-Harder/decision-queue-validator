"""Restart Step 17 fix wave 2, Seat K7 tests.

Charges CH-9, CH-10, and CH-19, ruled at section 19 of
design/steps/step-17r-record.md and prepared at
design/steps/step-17r-triage2-prep.md. All three charges stand
in product/decision_queue_validator/validate.py only.

CH-9 (A2-10-F4, seat 10): the validate side part scope reading
added by Fix C2 read scope as Part only where a remainder was
first extracted from the same statement in the cured forms.
Three part constructions still derived Ruled whole: a remainder
named as the rest, a remainder standing in the next paragraph,
and a part act with no remainder named, which PIN-03 reports
as Ambiguous in the Status line form of the same shape.

CH-10 (A2-10-F2, seat 10): the blocking figure still counted
Blocks fields that name no item, beyond the two cured strings:
the cured values with a full stop added, nothing, no items,
a mixed none beside a real reference is not in that family
(it names an item and counts), and the same edge under the
What it blocks label. Observation O4 of the same paper stands
untouched: the corpus form nothing named. keeps the standing
treatment the Fix C3 paper bound states, and a guard test
below pins that it still counts.

CH-19 (F2-8-1 Medium and F2-8-2 Low, seat 8, taken in one act
as the preparation collisions note records, both standing in
_banked_evidence_groups): a non content body line still
credited the level 4 group, and a heading shaped line with
one prefix character counted as an unheaded paragraph and
footed its entry through group 3. The F1 treatment itself
(carry H-01) is fenced and is cured in neither direction by
these tests or by the cure they pin.
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

validate = h.import_module("validate")


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


def banked_block_entry(body_line):
    """One Banked head entry whose only evidence form is a
    level 4 decision block carrying the given single body
    line, in the seat 8 paper construction form."""
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Test entry\n"
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
        "#### Ruling by Captain JP\n"
        "\n"
        + body_line + "\n")


def banked_plain_entry(body_line):
    """One Banked head entry with no level 4 block and no
    later Status line, whose only body line after the taught
    fields is the given line, in the seat 8 group 3 form."""
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Test entry\n"
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
        + body_line + "\n")


def group_members(output, *name_parts):
    group = h.census_class(h.census_of(output), *name_parts)
    if group is None:
        return []
    return h.census_members(group)


def sums_agree(output):
    recon = h.reconciliation_of(output)
    check = h.get(recon, "self_check", "self_check_result")
    return h.get(check, "sums_agree", "ok", "passed", "agrees")


def state_of(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry %s in the output" % entry_id)
    return h.entry_state(entry)


class PartScopeReadingTest(unittest.TestCase):
    """CH-9, A2-10-F4: part scope reading in validate."""

    def test_a2_10_f4_rest_remainder_derives_settled_in_part(self):
        text = ("# Decision queue\n\n" + taught_entry(
            2, "Remainder the rest",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest still stands open."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-002"),
                         "Settled in part")
        entry = h.entry_by_id(output, "DQ-002")
        remainder = h.get(entry, "remainder_text", "remainder")
        self.assertTrue(remainder)

    def test_a2_10_f4_next_paragraph_remainder_derives_settled_in_part(self):
        text = ("# Decision queue\n\n" + taught_entry(
            5, "Remainder separate paragraph",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-005"),
                         "Settled in part")
        entry = h.entry_by_id(output, "DQ-005")
        remainder = h.get(entry, "remainder_text", "remainder")
        self.assertTrue(remainder)

    def test_a2_10_f4_part_act_with_no_remainder_is_ambiguous(self):
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Part no remainder solo",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ambiguous")
        self.assertEqual(h.ambiguous_count(output), 1)

    def test_a2_10_f4_combined_figures(self):
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Remainder stands open no still",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stands open."]))
        parts.append(taught_entry(
            2, "Remainder the rest",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest still stands open."]))
        parts.append(taught_entry(
            3, "Second part ruled",
            ["Ruled by Captain JP: the second part is ruled, "
             "take Option B. The remainder, the first part, "
             "still stands open."]))
        parts.append(taught_entry(
            4, "A part of this entry",
            ["Ruled by Captain JP: a part of this entry is "
             "ruled, take Option A. The remainder, the second "
             "part, still stands open."]))
        parts.append(taught_entry(
            5, "Remainder separate paragraph",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        parts.append(taught_entry(
            6, "Settled by part",
            ["Settled by Captain JP: the first part is settled, "
             "take Option A. The remainder, the second part, "
             "still stands open."]))
        parts.append(taught_entry(
            7, "Part no remainder",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A."]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Ruled"), 0)
        self.assertEqual(counts.get("Settled in part"), 6)
        self.assertEqual(h.ambiguous_count(output), 1)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 6)

    def test_part_scope_cured_forms_still_derive_settled_in_part(self):
        # Guard, passing before and after: the forms the Fix C2
        # cure already reached keep their part derivation.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Remainder stands open no still",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder, the second part, "
             "stands open."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"),
                         "Settled in part")

    def test_whole_ruling_still_derives_ruled(self):
        # Guard, passing before and after: a ruling statement
        # that limits nothing to a part still derives Ruled
        # whole, so the widened scope reading takes no whole
        # act into the part rows.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Whole ruling entry",
            ["Ruled by Captain JP: this entry is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ruled")


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


class BlockingFigureNoItemTest(unittest.TestCase):
    """CH-10, A2-10-F2: the blocking figure no item values."""

    CHARGED_NO_ITEM_VALUES = (
        "None.",
        "nothing else.",
        "nothing",
        "no items",
        "none, nothing else",
        "Nothing else at all",
    )

    def test_a2_10_f2_each_charged_no_item_value_does_not_count(self):
        for value in self.CHARGED_NO_ITEM_VALUES:
            with self.subTest(value=value):
                text = ("# Decision queue\n\n"
                        + open_entry(1, value))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                _waiting, blocking = h.waiting_and_blocking(output)
                self.assertEqual(h.int_of(blocking), 0)

    def test_a2_10_f2_same_edge_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "None.", label="What it blocks"))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(blocking), 1)

    def test_a2_10_f2_combined_figure(self):
        values = (
            "DQ-002", "none", "nothing else", "None.",
            "nothing else.", "NONE", "nothing", "no items",
            "nothing named.", "none, nothing else",
            "Nothing else at all", "DQ-002, none",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        _waiting, blocking = h.waiting_and_blocking(output)
        # Hand truth on the charged forms is 2 (DQ-001 and
        # DQ-012). DQ-009, nothing named., stands counted under
        # the Fix C3 bound recorded at observation O4 of the
        # seat 10 paper, which this charge does not move, so
        # the figure on the whole file is 3.
        self.assertEqual(h.int_of(blocking), 3)
        listed = h.as_list(h.get(output, "blocking_list"))
        listed_ids = [h.text_of(h.get(
            item, "entry_id", "identifier")) for item in listed]
        self.assertEqual(listed_ids,
                         ["DQ-001", "DQ-009", "DQ-012"])

    def test_a2_10_f2_mixed_none_beside_a_real_reference_counts(self):
        # Guard on the charged construction DQ-012: a field
        # naming a real reference beside the word none names
        # an item and counts, before and after the cure.
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002, none"))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(blocking), 1)

    def test_o4_corpus_form_nothing_named_keeps_standing_treatment(self):
        # Observation O4 bound, not charged: the corpus form
        # nothing named. stands as the Fix C3 paper bound left
        # it, counted in the blocking figure.
        text = ("# Decision queue\n\n"
                + open_entry(1, "nothing named."))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(blocking), 1)


class BankedHeadEvidenceGroupsTest(unittest.TestCase):
    """CH-19, F2-8-1 and F2-8-2: the Banked head evidence
    groups in _banked_evidence_groups, taken in one act."""

    NON_CONTENT_BODY_LINES = (
        "\u200b",
        "\u200e",
        ".",
        "---",
        "x",
        "Question: A repeated question line inside the block.",
    )

    def test_f2_8_1_each_non_content_body_line_takes_no_group(self):
        for line in self.NON_CONTENT_BODY_LINES:
            with self.subTest(line=line):
                text = banked_block_entry(line)
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertNotIn(
                    "DQ-001", group_members(
                        output, "level 4 decision block"))
                self.assertNotIn(
                    "DQ-001", group_members(
                        output, "unheaded paragraphs"))
                self.assertNotIn(
                    "DQ-001", group_members(
                        output, "later Status line"))
                self.assertEqual(sums_agree(output), False)

    def test_f2_8_1_non_content_body_line_withholds_the_run(self):
        text = banked_block_entry("\u200b")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "n1.md"
            target.write_bytes(text.encode("utf-8"))
            code, out, err = h.run_cli("validate", target)
        combined = (out + err).decode("utf-8", errors="replace")
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_f2_8_1_genuine_block_body_keeps_group_2_credit(self):
        # Control C2 of the seat 8 paper, passing before and
        # after: a filing sentence in the block body foots
        # the entry through group 2 and the sums agree.
        text = banked_block_entry(
            "A filing sentence stands in the block body.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "level 4 decision block"))
        self.assertEqual(sums_agree(output), True)

    def test_f2_8_2_prefixed_heading_line_takes_no_group(self):
        for line in ("> #### Ruling by Captain JP",
                     "- #### Ruling by Captain JP"):
            with self.subTest(line=line):
                text = banked_plain_entry(line)
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertNotIn(
                    "DQ-001", group_members(
                        output, "unheaded paragraphs"))
                self.assertNotIn(
                    "DQ-001", group_members(
                        output, "level 4 decision block"))
                self.assertEqual(sums_agree(output), False)

    def test_f2_8_2_prefixed_heading_line_withholds_the_run(self):
        text = banked_plain_entry("> #### Ruling by Captain JP")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "h10.md"
            target.write_bytes(text.encode("utf-8"))
            code, out, err = h.run_cli("validate", target)
        combined = (out + err).decode("utf-8", errors="replace")
        self.assertEqual(code, 4)
        self.assertIn("Banked head evidence groups sum to 0",
                      combined)

    def test_f2_8_2_quoted_genuine_paragraph_keeps_group_3_credit(self):
        # Control G2 of the seat 8 paper, passing before and
        # after, and the bound of the charge: a quoted genuine
        # prose paragraph is a paragraph and keeps its group 3
        # credit. Only the heading shaped line is charged.
        text = banked_plain_entry(
            "> An unheaded paragraph stands here.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))
        self.assertEqual(sums_agree(output), True)

    def test_f2_8_2_plain_unheaded_paragraph_keeps_group_3_credit(self):
        # Guard, passing before and after: an ordinary unheaded
        # paragraph keeps its group 3 credit.
        text = banked_plain_entry(
            "An unheaded paragraph stands here.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))
        self.assertEqual(sums_agree(output), True)


if __name__ == "__main__":
    unittest.main()
