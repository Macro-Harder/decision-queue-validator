"""Step 17 fix wave 2, Fix Seat K4 tests.

Charges CH-15 (parse, the output reuse disposition guard) and
CH-16 (parse, the inert container pass), ruled at section 19 of
design/steps/step-17r-record.md under flag ruling (g).

CH-15: the disposition guard must recognise the count row by
its meaning across the measured decorated and respaced forms
(both spellings, the census spelling and the reconciliation
spelling, and the rendered group heading lines), and the
guard effect must be confined to the row itself, line segment
aware, so a genuine ruling standing later on the same line
still counts. Both directions are pinned.

CH-16: the inert pass blanking granularity is the container
segment, not the line. Container matter (a fence line that
cannot close its fence, a comment reopened on the same line,
a single line HTML comment) must not satisfy presence or
field tests or denote dispositions, and a genuine field line
that opens a comment on the same line must not be blanked
whole.

Constructions are the finding papers own forms:
design/steps/step-17r-attack2-20.md (F-20-2-1 to F-20-2-5) and
design/steps/step-17r-attack2-11.md (F-11R2-01, F-11R2-02,
F-11R2-04).

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _k4_entry(extra_body=""):
    """The seat 20 control base: one Banked entry, DQ-001."""
    body = h._header_block()
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: none\n"
    body += extra_body
    return body.encode("utf-8")


def _k4_elements(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "status_elements", "elements"))


def _k4_dispositions(model, entry_id="DQ-001"):
    out = []
    for el in _k4_elements(model, entry_id):
        tup = h.get(el, "tuple", "element_tuple", "core_tuple")
        out.append(h.text_of(tuple(tup)[0]) if tup is not None
                   else h.text_of(h.get(el, "disposition")))
    return out


def _k4_state(extra_body, name="k4_case.md"):
    model, output = h.run_pipeline(_k4_entry(extra_body), name)
    result = h.entry_by_id(output, "DQ-001")
    return model, h.entry_state(result)


class Step17Fix2K4CountRowGuardTest(unittest.TestCase):
    """CH-15, F-20-2-1: the census spelling of the count row."""

    def test_f20_2_1_census_rows_denote_no_disposition(self):
        for row in ("Canonical state: Ruled: 0 entries",
                    "Canonical state: Settled: 0 entries",
                    "Canonical state: Ruled: 2 entries",
                    "Canonical state: Ruled: 1 entry"):
            with self.subTest(row=row):
                model, state = _k4_state("\n" + row + "\n")
                self.assertNotIn("Ruled", _k4_dispositions(model))
                self.assertNotIn("Settled", _k4_dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix2K4GroupHeadingTest(unittest.TestCase):
    """CH-15, F-20-2-2: rendered group heading lines."""

    def test_f20_2_2_group_headings_denote_no_disposition(self):
        for heading in ("Ruled group", "Settled group",
                        "Closed as decided group", "Parked group",
                        "Presented group", "Settled in part group"):
            with self.subTest(heading=heading):
                model, state = _k4_state("\n" + heading + "\n")
                self.assertEqual(state, "Open")
                self.assertNotIn("Ruled", _k4_dispositions(model))
                self.assertNotIn("Settled", _k4_dispositions(model))
                self.assertNotIn("Closed", _k4_dispositions(model))
                self.assertNotIn("Parked", _k4_dispositions(model))
                self.assertNotIn("Presented",
                                 _k4_dispositions(model))

    def test_f20_2_2_appended_render_extract_flips_no_entry(self):
        # The whole appended render form of case e1, in extract:
        # a clean second entry whose span carries rendered lines,
        # the group heading among them, stays Open.
        body = h._header_block()
        body += "### DQ-001: First question\n\nStatus: Banked\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: none\n\n"
        body += "### DQ-002: Second question\n\nStatus: Banked\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: none\n\n"
        body += "Closed as decided group\n\n"
        body += "Canonical Closed as decided: 0 entries\n\n"
        body += "Canonical state: Ruled: 0 entries\n"
        model, output = h.run_pipeline(body.encode("utf-8"),
                                       "appended_render.md")
        self.assertFalse(h.is_failure_result(model))
        for entry_id in ("DQ-001", "DQ-002"):
            result = h.entry_by_id(output, entry_id)
            self.assertEqual(h.entry_state(result), "Open")


class Step17Fix2K4DecoratedRowTest(unittest.TestCase):
    """CH-15, F-20-2-3: decorated and respaced count rows."""

    def test_f20_2_3_decorated_rows_denote_no_disposition(self):
        rows = (
            "- Canonical Ruled: 0 entries",
            "- Canonical Settled: 0 entries",
            "> Canonical Ruled: 0 entries",
            "Canonical Ruled:  0 entries",
            "Canonical Ruled:\t0 entries",
            "canonical Ruled: 0 entries",
            "Report line: Canonical Ruled: 0 entries",
            "Copied from the report. Canonical Ruled: 0 entries.",
            "**Canonical Ruled: 0 entries**",
            "| Canonical Ruled: 0 entries |",
            "Canonical\tRuled: 0 entries",
            "Canonical  Ruled: 0 entries",
            "CANONICAL Ruled: 0 entries",
        )
        for row in rows:
            with self.subTest(row=row):
                model, state = _k4_state("\n" + row + "\n")
                self.assertNotIn("Ruled", _k4_dispositions(model))
                self.assertNotIn("Settled", _k4_dispositions(model))
                self.assertEqual(state, "Open")


class Step17Fix2K4SuppressionTest(unittest.TestCase):
    """CH-15, F-20-2-5: the guard is confined to the row itself.

    A genuine ruling standing later on the same line as a count
    row still counts, in both spellings of the row.
    """

    def test_f20_2_5_ruling_after_reconciliation_row_counts(self):
        model, state = _k4_state(
            "\nCanonical Ruled: 0 entries. Ruled by Captain JP: "
            "take Option A.\n")
        self.assertIn("Ruled", _k4_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_f20_2_5_ruling_after_row_second_form_counts(self):
        model, state = _k4_state(
            "\nCanonical Settled: 0 entries. Captain JP ruled the "
            "entry, take Option A.\n")
        self.assertIn("Ruled", _k4_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_f20_2_5_ruling_after_census_row_counts(self):
        # The Settled census row and the Ruled ruling on one
        # line: the row must not denote Settled, and the ruling
        # must still count, so the entry stands Ruled only.
        model, state = _k4_state(
            "\nCanonical state: Settled: 0 entries. Ruled by "
            "Captain JP: take Option A.\n")
        self.assertNotIn("Settled", _k4_dispositions(model))
        self.assertIn("Ruled", _k4_dispositions(model))
        self.assertEqual(state, "Ruled")

    def test_k4_control_genuine_ruling_alone_still_counts(self):
        model, state = _k4_state(
            "\nRuled by Captain JP: take Option A.\n")
        self.assertIn("Ruled", _k4_dispositions(model))
        self.assertEqual(state, "Ruled")


class Step17Fix2K4FenceDelimiterTest(unittest.TestCase):
    """CH-16, F-11R2-01: a fence line that cannot close the
    fence ends no inert span."""

    def test_f11r2_01_short_line_inside_long_fence_presence(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "````\n```\nRuled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n````\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "long_fence_evidence.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=5))

    def test_f11r2_01_short_line_inside_long_fence_fields(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Presented\n\n"
        body += "````\n```\nQuestion: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n````\n\nA waiting paragraph.\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "long_fence_fields.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=9, severity="Warning"))

    def test_f11r2_01_cross_character_line_closes_no_fence(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Presented\n\n"
        body += "~~~\n```\nQuestion: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n~~~\n\nA waiting paragraph.\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "cross_fence_fields.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=9, severity="Warning"))

    def test_f11r2_01_info_string_line_closes_no_fence(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Presented\n\n"
        body += "```\n``` python\nQuestion: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n```\n\nA waiting paragraph.\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "info_fence_fields.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=9, severity="Warning"))

    def test_k4_control_longer_closing_fence_still_closes(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "```\nsome code\n````\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This question is waiting for a decision.\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "long_close.md")
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])


class Step17Fix2K4CommentReopenTest(unittest.TestCase):
    """CH-16, F-11R2-02: a comment reopened on the same line."""

    def test_f11r2_02_reopened_comment_presence(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!-- note --> <!-- draft\nRuled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "reopen_evidence.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=5))

    def test_f11r2_02_reopened_comment_fields(self):
        # The seat 11 field construction, reshaped out of the
        # F1 form as that paper reshaped its charged
        # constructions: a genuine unheaded paragraph stands
        # before the comment, so the entry foots on genuine
        # matter and the field surface is what is measured.
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += "<!-- note --> <!-- draft\nQuestion: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "reopen_fields.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=9, severity="Warning"))


class Step17Fix2K4SingleLineCommentTest(unittest.TestCase):
    """CH-16 with CH-15, F-20-2-4: a single line HTML comment
    denotes no disposition, for output rows and rulings alike."""

    def test_f20_2_4_count_row_in_single_line_comment(self):
        model, state = _k4_state(
            "\n<!-- Canonical Ruled: 0 entries -->\n")
        self.assertNotIn("Ruled", _k4_dispositions(model))
        self.assertEqual(state, "Open")

    def test_f20_2_4_ruling_in_single_line_comment(self):
        model, state = _k4_state(
            "\n<!-- Ruled by Captain JP: take Option A. -->\n")
        self.assertNotIn("Ruled", _k4_dispositions(model))
        self.assertEqual(state, "Open")


class Step17Fix2K4FieldLineCommentTest(unittest.TestCase):
    """CH-16, F-11R2-04: a genuine field line that opens a
    comment on the same line is not blanked whole."""

    def test_f11r2_04_field_line_opening_comment_is_recorded(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += ("Question: Which option should we take? "
                 "<!-- draft note\nstill drafting -->\n\n")
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This question is waiting for a decision.\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "field_opens_comment.md")
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])


class Step17Fix2K4ExtractionBoundTest(unittest.TestCase):
    """The D3 bound stands: a disposition element inside a
    fence is still extracted. This cure moves no part of it."""

    def test_k4_control_fenced_element_still_extracted(self):
        data = _k4_entry(
            "\n```\nRuled: the checker note takes the short "
            "form.\n```\n")
        model, output = h.run_pipeline(data, "fenced_element.md")
        self.assertIn("Ruled", _k4_dispositions(model))
        result = h.entry_by_id(output, "DQ-001")
        self.assertNotEqual(h.entry_state(result), "Open")


if __name__ == "__main__":
    unittest.main()
