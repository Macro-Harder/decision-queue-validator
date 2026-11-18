"""Restart Step 17 fix wave 3, Seat K6 tests.

Charge CH-42, ruled at section 26 of design/steps/
step-17r-record.md, ruling (g) and FLAG 6 of design/steps/
step-17r-triage3-prep.md, prepared against design/steps/
step-17r-attack3-8.md. Findings F3-8-1 (Medium), F3-8-2
(Medium), F3-8-3 (Low), and F3-8-4 (Low), one census function
in four limbs, all standing in product/decision_queue_validator/
validate.py, in _banked_evidence_groups and its helpers
_line_carries_content, _is_heading_shaped_line, and
_is_open_field_labelled_line.

F3-8-1: the CH-19 content test credits a line of two single
characters, or of one bare number, so a Banked entry carrying
no counted element foots in silence. The cure stops crediting
contentless lines without refusing genuine short words: the
control of two CJK characters forming one word passing as a
genuine short word stands as governing behaviour and as a pin.

F3-8-2: a lower case labelled field line credits group 3,
though labelled field paragraphs count toward none of the
three groups. The cure bound is that a labelled field line
takes no group credit in any case form, on any surface of
the census.

F3-8-3 and F3-8-4: a heading shaped line behind one invisible
character, and a heading shaped line behind a list marker
the heading test does not read, take group credit. The cure
takes that credit away without refusing genuine prose
paragraphs: the round 2 quoted prose control stands as a pin.

Pins that must not break: the CH-19 pins whole, including
the F2-8-1 non content forms and the genuine prose credit
controls. The whole charge stands on the Banked head footing
surface beside F1; no test here decides, drafts, or advances
the F1 shape outcome, which stands fenced at carry H-01.
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

validate = h.import_module("validate")


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


def assert_in_no_group(test_case, output):
    for name in ("level 4 decision block", "unheaded paragraphs",
                 "later Status line"):
        test_case.assertNotIn("DQ-001", group_members(output, name))
    test_case.assertEqual(sums_agree(output), False)


def assert_withheld(test_case, text):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "case.md"
        target.write_bytes(text.encode("utf-8"))
        code, out, err = h.run_cli("validate", target)
    combined = (out + err).decode("utf-8", errors="replace")
    test_case.assertEqual(code, 4)
    test_case.assertIn("Banked head evidence groups sum to 0",
                       combined)


class ContentlessLineCreditTest(unittest.TestCase):
    """F3-8-1: two single characters, or one bare number,
    take no group credit, in a block or standing plain."""

    BLOCK_FORMS = ("a b", "1 2", "42", "e.g.", "a_b")
    PLAIN_FORMS = ("a b", "1 2", "42", "e.g.", "a_b")

    def test_f3_8_1_block_forms_take_no_group(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_f3_8_1_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_f3_8_1_content_test_reads_the_charged_lines_empty(self):
        for line in self.BLOCK_FORMS:
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), False)

    def test_f3_8_1_one_number_withholds_the_run(self):
        assert_withheld(self, banked_block_entry("42"))

    def test_f3_8_1_two_single_letters_withhold_the_run(self):
        assert_withheld(self, banked_plain_entry("a b"))


class GenuineShortWordPinTest(unittest.TestCase):
    """F3-8-1 pins: genuine short words keep their credit,
    so the tightened threshold refuses contentless lines
    only, never genuine short words."""

    def test_two_cjk_characters_forming_one_word_keep_group_2(self):
        # The governing control of the attack paper, its
        # observation 1 case F18: two CJK characters forming
        # one word of two letters pass as a genuine short
        # word does. Passing before and after.
        text = banked_block_entry("\u4e2d\u6587")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "level 4 decision block"))
        self.assertEqual(sums_agree(output), True)

    def test_one_cjk_character_takes_no_group(self):
        # The neighbouring observation form F17, passing
        # before and after: one single character, of any
        # script, is no word of two letters.
        text = banked_block_entry("\u4e2d")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_genuine_short_word_line_keeps_group_2(self):
        text = banked_block_entry("Settled.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "level 4 decision block"))
        self.assertEqual(sums_agree(output), True)

    def test_content_test_reads_genuine_short_words_as_content(self):
        for line in ("\u4e2d\u6587", "Settled.", "Go ahead.",
                     "A filing sentence stands in the block body."):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._line_carries_content(line), True)

    def test_genuine_filing_sentence_keeps_group_2(self):
        # Control C2 of the round 2 seat 8 paper, a CH-19
        # pin, passing before and after.
        text = banked_block_entry(
            "A filing sentence stands in the block body.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "level 4 decision block"))
        self.assertEqual(sums_agree(output), True)


class LabelledFieldCaseTest(unittest.TestCase):
    """F3-8-2: a labelled field line takes no group credit
    in any case form, on any surface of the census."""

    PLAIN_FORMS = (
        "question: A repeated question line stands here.",
        "options: Option A, Option B",
        "QUESTION: A repeated question line stands here.",
        "Options: Option A, Option B",
        "the question: A repeated question line stands here.",
        "cost: Work stays blocked.",
        "blocks: DQ-002",
    )

    def test_f3_8_2_labelled_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_f3_8_2_lower_options_inside_block_takes_no_group(self):
        text = banked_block_entry("options: Option A, Option B")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_f3_8_2_lower_question_withholds_the_run(self):
        assert_withheld(self, banked_plain_entry(
            "question: A repeated question line stands here."))

    def test_capitalised_labelled_line_takes_no_group(self):
        # Control G15 of the attack paper, a standing form,
        # passing before and after.
        text = banked_plain_entry(
            "Question: A repeated question line stands here.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)


class InvisiblePrefixHeadingTest(unittest.TestCase):
    """F3-8-3: a heading shaped line behind one invisible
    character takes no group credit, in group 3 and inside
    a block."""

    PLAIN_FORMS = (
        "\u200b#### Ruling by Captain JP",
        "\ufeff#### Ruling by Captain JP",
    )

    def test_f3_8_3_invisible_heading_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_f3_8_3_invisible_heading_inside_block_takes_no_group(self):
        text = banked_block_entry("\u200b#### Ruling by Captain JP")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        assert_in_no_group(self, output)

    def test_f3_8_3_heading_test_sees_behind_the_invisible_character(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=repr(line)):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)

    def test_f3_8_3_zwsp_heading_withholds_the_run(self):
        assert_withheld(self, banked_plain_entry(
            "\u200b#### Ruling by Captain JP"))


class UnenumeratedMarkerHeadingTest(unittest.TestCase):
    """F3-8-4: a heading shaped line behind a list marker
    the heading test does not read takes no group credit."""

    PLAIN_FORMS = (
        "1234. #### Ruling by Captain JP",
        "a) #### Ruling by Captain JP",
        "iv. #### Ruling by Captain JP",
        "\u2022 #### Ruling by Captain JP",
        "\u2013 #### Ruling by Captain JP",
        "**#### Ruling by Captain JP**",
    )

    def test_f3_8_4_marker_heading_plain_forms_take_no_group(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_f3_8_4_heading_test_reads_the_unenumerated_markers(self):
        for line in self.PLAIN_FORMS:
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), True)

    def test_f3_8_4_four_digit_marker_heading_withholds_the_run(self):
        assert_withheld(self, banked_plain_entry(
            "1234. #### Ruling by Captain JP"))


class Ch19PinsTest(unittest.TestCase):
    """The CH-19 pins whole, re-run on this charge: the
    F2-8-1 non content forms, the F2-8-2 prefixed heading
    forms, and the genuine prose credit controls. Every
    test in this class passes before and after the cure."""

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
            with self.subTest(line=repr(line)):
                _model, output = h.run_pipeline(
                    banked_block_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_f2_8_2_prefixed_heading_line_takes_no_group(self):
        for line in ("> #### Ruling by Captain JP",
                     "- #### Ruling by Captain JP"):
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                assert_in_no_group(self, output)

    def test_f2_8_2_quoted_genuine_paragraph_keeps_group_3_credit(self):
        # Control G2 of the round 2 seat 8 paper, the bound
        # of F3-8-3 and F3-8-4 as well: a quoted genuine prose
        # paragraph is a paragraph and keeps its credit.
        text = banked_plain_entry(
            "> An unheaded paragraph stands here.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))
        self.assertEqual(sums_agree(output), True)

    def test_plain_unheaded_paragraph_keeps_group_3_credit(self):
        text = banked_plain_entry(
            "An unheaded paragraph stands here.")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertIn("DQ-001", group_members(
            output, "unheaded paragraphs"))
        self.assertEqual(sums_agree(output), True)

    def test_genuine_prose_behind_unenumerated_markers_keeps_credit(self):
        # The F3-8-4 bound in the other direction: genuine
        # prose paragraphs standing behind the newly read
        # markers, or wrapped in bold marks, are paragraphs
        # and keep their group 3 credit.
        for line in (
                "1234. An unheaded paragraph stands here.",
                "a) An unheaded paragraph stands here.",
                "iv. An unheaded paragraph stands here.",
                "\u2022 An unheaded paragraph stands here.",
                "**An unheaded paragraph stands here.**"):
            with self.subTest(line=line):
                _model, output = h.run_pipeline(
                    banked_plain_entry(line).encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertIn("DQ-001", group_members(
                    output, "unheaded paragraphs"))
                self.assertEqual(sums_agree(output), True)

    def test_heading_test_reads_genuine_prose_as_no_heading(self):
        for line in ("An unheaded paragraph stands here.",
                     "> An unheaded paragraph stands here.",
                     "1234. An unheaded paragraph stands here.",
                     "**An unheaded paragraph stands here.**"):
            with self.subTest(line=line):
                self.assertEqual(
                    validate._is_heading_shaped_line(line), False)


if __name__ == "__main__":
    unittest.main()
