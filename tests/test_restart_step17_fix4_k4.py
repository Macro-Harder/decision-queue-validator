"""Step 17 fix wave 4, Fix Seat K4 tests.

Charge CH-69 (parse and validate, the inert pass fence close
and the segment stored form), ruled at section 38 of
design/steps/step-17r-record.md under FLAG 4: the three
findings of round 4 attack seat 11 are cured by one act on
the one stored form decision, with the governed container
forms standing as pins in both directions.

F-11R4-01 (Medium): a closing fence line carrying a comment
segment, before its run or after it, does not close the
fence, and genuine matter after that line is read as
container matter and takes missing field Warnings on the
field surface and missing evidence findings on the presence
surface. Cure bound: the closing fence test reads the line
on the same stored form the opening side reads, comment
segments removed, in both fence characters and in the
segment before, after, and doubled positions.

F-11R4-02 (Medium): a comment segment standing between the
words of a multiword field label defeats the label, segment
removal leaving two spaces where the label as written
carries one word break. Cure bound: the stored form of a
line after segment removal is normalised at the word breaks
a segment stood on, so a label standing genuine in the file
reads as the label it is.

F-11R4-03 (Low): a comment segment standing between a field
label and its colon takes a spurious rule 2 near marker
Warning, segment removal leaving a space before the colon
in the stored form, while the field itself stands credited.
Cure bound: the stored form is normalised at the label
colon position a segment stood on, so a credited field line
takes no near marker Warning.

Pins in both directions, standing in this file: the plain
closing line control; the governed reopening, stray close,
and fence after segment forms standing with their findings;
closing candidates that carry an info string, a shorter
run, a run of the other character, or no run at all standing
with no close, in segment positions as in plain positions;
the segment inside one word contrast standing credited; and
a space before a colon written in the file itself, with no
segment standing on it, standing with its near marker
Warning, so the normalisation reaches segment positions
only and no written form.

The CH-16 and CH-45 pins whole stand in
product/tests/test_step17_fix2_k4.py and
product/tests/test_restart_step17_fix3_k4.py, and the
CH-35, CH-37, and CH-38 pins in
product/tests/test_restart_step17_fix3_k2.py; they are
re-run at this cluster close, not edited here.

Constructions are the attack paper own forms:
design/steps/step-17r-attack4-11.md, cases n1 to n18.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _run(body, name):
    return h.run_pipeline(body.encode("utf-8"), name)


def _fields_body(closing_line, fence_open="````",
                 fence_char_form=None):
    body = h._header_block()
    body += "### DQ-001: Open one\n\nStatus: Presented\n\n"
    body += fence_open + "\njunk line\n"
    body += closing_line + "\n"
    body += "Question: Which option?\n"
    body += "Options: A, B\nCost of deciding late: blocked.\n"
    body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
    return body


def _evidence_body(opening_line, closing_line="````"):
    body = h._header_block()
    body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
    body += opening_line + "\nRuled by: Captain JP\n"
    body += "Ruling text: \"Runs.\"\n"
    body += "Ruling outcome: It runs.\n"
    body += "Where the ruling landed: harbour file.\n"
    body += closing_line + "\n"
    return body


def _rule9(output):
    return h.findings_for(output, entry_id="DQ-001", rule=9,
                          severity="Warning")


def _rule5(output):
    return h.findings_for(output, entry_id="DQ-001", rule=5)


def _rule2(output):
    return h.findings_for(output, entry_id="DQ-001", rule=2)


class Ch69ClosingFenceStoredFormFieldTest(unittest.TestCase):
    """F-11R4-01, field surface: cases n1, n2, n3, n17."""

    def test_n1_segment_before_run_closes_fence(self):
        _model, output = _run(
            _fields_body("<!-- end --> ````"),
            "n1_close_segment_before_run_fields.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])

    def test_n2_segment_after_run_closes_fence(self):
        _model, output = _run(
            _fields_body("```` <!-- end -->"),
            "n2_close_trailing_segment_fields.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])

    def test_n3_two_segments_before_run_close_fence(self):
        _model, output = _run(
            _fields_body("<!-- a --> <!-- b --> ````"),
            "n3_close_two_segments_fields.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])

    def test_n17_tilde_segment_before_run_closes_fence(self):
        _model, output = _run(
            _fields_body("<!-- end --> ~~~~",
                         fence_open="~~~~"),
            "n17_close_segment_tilde_fields.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])

    def test_n4_plain_closing_line_control(self):
        _model, output = _run(
            _fields_body("````"),
            "n4_close_plain_control_fields.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])


class Ch69ClosingFenceStoredFormPresenceTest(unittest.TestCase):
    """F-11R4-01, presence surface: case n16."""

    def test_n16_segment_before_run_credits_evidence_after(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "````\njunk line\n<!-- end --> ````\n"
        body += "Ruled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n"
        _model, output = _run(
            body, "n16_close_segment_evidence_after.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule5(output), [])


class Ch69ClosingCandidateNoClosePinTest(unittest.TestCase):
    """Pins in the other direction: a closing candidate on
    the stored form that carries matter after its run, a
    shorter run, a run of the other character, or no run
    closes no fence, in segment positions as in plain ones.
    The fields after each candidate stand inside the fence
    and take their rule 9 Warnings."""

    def _assert_no_close(self, closing_line, name):
        _model, output = _run(_fields_body(closing_line), name)
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule9(output)), 4)

    def test_segment_before_run_with_info_string_no_close(self):
        self._assert_no_close("<!-- end --> ```` python",
                              "k4_close_info_string.md")

    def test_segment_before_shorter_run_no_close(self):
        self._assert_no_close("<!-- end --> ```",
                              "k4_close_shorter_run.md")

    def test_segment_before_other_character_run_no_close(self):
        self._assert_no_close("<!-- end --> ~~~~",
                              "k4_close_other_character.md")

    def test_segment_line_with_no_run_no_close(self):
        self._assert_no_close("<!-- end --> junk",
                              "k4_close_no_run.md")


class Ch69GovernedContainerFormsPinTest(unittest.TestCase):
    """The governed container forms of the paper, standing
    as pins in both directions: cases n5, n6, n7, n10, n11
    of observation O-11R4-3."""

    def test_n10_two_segments_no_space_run_opens_fence(self):
        _model, output = _run(
            _evidence_body("<!-- a --><!-- b -->````"),
            "n10_two_segments_fence_evidence.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule5(output)), 3)

    def test_n5_open_segment_run_segment_opens_fence(self):
        _model, output = _run(
            _evidence_body("<!-- a --> ```` <!-- b -->"),
            "n5_open_segment_run_segment_evidence.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule5(output)), 3)

    def test_n11_run_after_segment_on_closing_line_opens(self):
        _model, output = _run(
            _evidence_body("<!-- draft\n--> <!-- x --> ````"),
            "n11_fence_after_segment_on_close_line.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule5(output)), 3)

    def test_n6_reopen_on_closing_line_governs_under_it(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!-- draft\n--> <!-- again\n"
        body += "Ruled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n-->\n"
        _model, output = _run(
            body, "n6_reopen_on_closing_line_evidence.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule5(output)), 3)

    def test_n7_stray_close_then_open_governs_fields(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "--> <!-- draft\n"
        body += "Question: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n-->\n\nA waiting paragraph.\n"
        _model, output = _run(
            body, "n7_stray_close_then_open_fields.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule9(output)), 4)


class Ch69SegmentBetweenLabelWordsTest(unittest.TestCase):
    """F-11R4-02: cases n13 and n18, contrast n14."""

    def test_n13_segment_between_ruled_by_words_credits(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "Ruled <!-- c --> by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n"
        _model, output = _run(
            body, "n13_segment_between_ruled_by.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule5(output), [])

    def test_n18_segment_between_cost_words_credits(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "Question: Which option?\nOptions: A, B\n"
        body += "Cost of deciding <!-- c --> late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(
            body, "n18_segment_between_cost_words.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])

    def test_n14_segment_inside_one_word_stands_credited(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "Ques<!-- c -->tion: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(
            body, "n14_segment_inside_question_word.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])


class Ch69SegmentBetweenLabelAndColonTest(unittest.TestCase):
    """F-11R4-03: cases n8, n9, n15. The field stands
    credited and no rule 2 near marker Warning stands."""

    def test_n8_question_label_colon_no_near_warning(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "Question <!-- c -->: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(
            body, "n8_segment_between_label_colon.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])
        self.assertEqual(_rule2(output), [])

    def test_n9_decider_label_colon_no_near_warning(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "Ruled by <!-- c -->: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n"
        _model, output = _run(
            body, "n9_segment_in_decider_label.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule5(output), [])
        self.assertEqual(_rule2(output), [])

    def test_n15_ruling_text_label_colon_no_near_warning(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "Ruled by: Captain JP\n"
        body += "Ruling text <!-- c -->: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n"
        _model, output = _run(
            body, "n15_segment_label_colon_ruling_text.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule5(output), [])
        self.assertEqual(_rule2(output), [])

    def test_written_space_before_colon_keeps_near_warning(self):
        # Pin in the other direction: a space before the
        # colon written in the file itself, with no segment
        # standing on it, is no segment position. The field
        # stands credited in its stripped label form and the
        # line keeps its near marker Warning, as the field
        # recording form states.
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "Question : Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(
            body, "k4_written_space_before_colon.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule9(output), [])
        self.assertEqual(len(_rule2(output)), 1)


if __name__ == "__main__":
    unittest.main()
