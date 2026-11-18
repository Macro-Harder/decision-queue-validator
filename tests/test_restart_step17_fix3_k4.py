"""Step 17 fix wave 3, Fix Seat K4 tests.

Charge CH-45 (parse, the inert pass fence and segment
position), ruled at section 26 of
design/steps/step-17r-record.md under flag ruling (e): the
two limbs are one charge cured by one act, as round 2 CH-16
stood. The fence test position and the genuine matter
reading are decided together on the blanked line stored
form.

Limb one, F-11R3-01 (High): a fence run standing as the
genuine matter of a line, after any closed comment segment
on that line, is tested as a fence delimiter on the same
terms as a run at the line start and as a run on a comment
closing line. A decided entry whose only evidence stands
inside such a fence must no longer pass clean, and fields
inside such a fence must take their missing field
Warnings.

Limb two, F-11R3-02 (Low): genuine matter after a closed
comment segment on a line opening outside any container is
read on the same terms as the same matter on a comment
closing line, with separating space or without. Fields and
evidence standing after a segment, with a space between
the segment and the matter, must be recorded.

Pins held in this file: the paper contrast forms (no space
after the segment standing credited; a Status line after a
segment standing credited as the line start Status line; a
comment segment inside a field value standing harmless;
genuine matter on a comment closing line standing
credited). The CH-16 and CH-15 pins whole stand in
product/tests/test_step17_fix2_k4.py and are re-run at this
cluster close, not edited here.

Constructions are the attack paper own forms:
design/steps/step-17r-attack3-11.md, cases b1 to b7, d5,
d6, e4, f1, g1, and g2.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _run(body, name):
    return h.run_pipeline(body.encode("utf-8"), name)


class Ch45FenceAfterSegmentPresenceTest(unittest.TestCase):
    """Limb one, presence surface: case b4 and case g2."""

    def test_b4_fence_after_segment_evidence_takes_rule5(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!-- note --> ````\nRuled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n````\n"
        _model, output = _run(body, "b4_fence_after_segment.md")
        self.assertIsNotNone(output)
        findings = h.findings_for(output, entry_id="DQ-001", rule=5)
        self.assertTrue(findings)
        self.assertEqual(len(findings), 3)

    def test_g2_fence_after_segment_no_space_takes_rule5(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!--note-->````\nRuled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n````\n"
        _model, output = _run(body, "g2_fence_no_space.md")
        self.assertIsNotNone(output)
        findings = h.findings_for(output, entry_id="DQ-001", rule=5)
        self.assertTrue(findings)
        self.assertEqual(len(findings), 3)


class Ch45FenceAfterSegmentFieldTest(unittest.TestCase):
    """Limb one, field surface: cases b6 and b7."""

    def test_b6_backtick_fence_after_segment_fields_take_rule9(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Presented\n\n"
        body += "<!-- note --> ````\nQuestion: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n````\n\nA waiting paragraph.\n"
        _model, output = _run(body, "b6_fence_fields.md")
        self.assertIsNotNone(output)
        findings = h.findings_for(output, entry_id="DQ-001",
                                  rule=9, severity="Warning")
        self.assertEqual(len(findings), 4)

    def test_b7_tilde_fence_after_segment_fields_take_rule9(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Presented\n\n"
        body += "<!-- note --> ~~~~\nQuestion: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n~~~~\n\nA waiting paragraph.\n"
        _model, output = _run(body, "b7_tilde_fields.md")
        self.assertIsNotNone(output)
        findings = h.findings_for(output, entry_id="DQ-001",
                                  rule=9, severity="Warning")
        self.assertEqual(len(findings), 4)


class Ch45FenceContrastTest(unittest.TestCase):
    """Contrast pin: the same fence on a comment closing
    line already governs, before and after this cure."""

    def test_b5_fence_on_multiline_close_takes_rule5(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!-- note\n--> ````\nRuled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n````\n"
        _model, output = _run(body, "b5_multiline_close.md")
        self.assertIsNotNone(output)
        findings = h.findings_for(output, entry_id="DQ-001", rule=5)
        self.assertEqual(len(findings), 3)


class Ch45MatterAfterSegmentFieldTest(unittest.TestCase):
    """Limb two, field surface: cases b1 and b3."""

    def test_b1_all_fields_after_segment_are_recorded(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "<!-- draft --> Question: Which option?\n"
        body += "<!-- draft --> Options: A, B\n"
        body += "<!-- draft --> Cost of deciding late: blocked.\n"
        body += "<!-- draft --> Blocks: DQ-002\n"
        body += "\nA waiting paragraph.\n"
        _model, output = _run(body, "b1_prefix_fields.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])

    def test_b3_field_between_two_segments_is_recorded(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "<!-- a --> Question: Which option? <!-- b -->\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(body, "b3_between_segments.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])


class Ch45MatterAfterSegmentPresenceTest(unittest.TestCase):
    """Limb two, presence surface: case b2."""

    def test_b2_all_evidence_after_segment_is_recorded(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!-- draft --> Ruled by: Captain JP\n"
        body += "<!-- draft --> Ruling text: \"Runs.\"\n"
        body += "<!-- draft --> Ruling outcome: It runs.\n"
        body += "<!-- draft --> Where the ruling landed: harbour file.\n"
        _model, output = _run(body, "b2_prefix_evidence.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=5), [])


class Ch45ContrastFormsTest(unittest.TestCase):
    """The paper contrast forms, pinned as standing
    credited before and after this cure."""

    def test_g1_field_no_space_after_segment_credited(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "<!--draft-->Question: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(body, "g1_no_space_field.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])

    def test_e4_status_after_segment_credited_as_line_start(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\n"
        body += "<!-- note --> Status: Banked\n\n"
        body += "Question: Which option?\nOptions: A, B\n"
        body += "Cost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(body, "e4_status_after_segment.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])
        result = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(result), "Open")

    def test_f1_segment_inside_field_value_harmless(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "Question: Which <!-- draft --> option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(body, "f1_value_segment.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])

    def test_d5_field_on_multiline_close_credited(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "<!-- draft\nstill drafting --> Question: Which option?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = _run(body, "d5_close_field.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=9), [])

    def test_d6_evidence_on_multiline_close_credited(self):
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!-- draft\nstill drafting --> Ruled by: Captain JP\n\n"
        body += "Ruling text: \"Runs.\"\n\n"
        body += "Ruling outcome: It runs.\n\n"
        body += "Where the ruling landed: harbour file.\n"
        _model, output = _run(body, "d6_close_evidence.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.findings_for(output, entry_id="DQ-001",
                                        rule=5), [])


if __name__ == "__main__":
    unittest.main()
