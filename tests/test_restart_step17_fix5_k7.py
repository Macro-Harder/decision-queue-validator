"""Step 17 (restart) fix wave 5, Fix Seat K7 tests.

Charge CH-89 (parse and validate, the Status element reading
on the stored form), prepared at
design/steps/step-17r-triage5-prep.md, against round 5 attack
seat 11 finding F-11R5-01 (Medium), paper at
design/steps/step-17r-attack5-11.md.

F-11R5-01: a comment segment standing at a word break of the
Status label, between that label and its colon, or inside
its one word defeats the head Status element itself. The
Status element reading and its near marker scan read the
line as written, segment and all, and never take the stored
form act landed at CH-69 (the _stored_form act in parse.py),
which every other label reader takes: comment segments are
removed and the parts of the line are joined at the segment
boundaries, normalised at those boundaries alone. A sound
Banked entry therefore derives Ambiguous, sub label No
element, at exit 4, with a spurious rule 2 near marker
Warning, a Status occurrence total of 0, no Banked head
census row, and a waiting figure of 0.

Cure bound: the Status element reading and its near marker
scan take the stored form reading on the charged segment
positions, and no further. The bound of CH-69 stands whole:
normalisation reaches segment boundaries only, and a space
before a colon written in the file itself, with no segment
standing on it, stands exactly as the CH-69 bound pins it,
in the Ambiguous form with its near marker Warning.

Pins in both directions, standing in this file: the segment
standing after the colon, before the label, and in the no
space colon form, each credited before and after; the plain
Status line control; a marker standing wholly inside a
comment segment counting as no occurrence; an unclosed
segment standing in the label crediting nothing; and a one
edit typo label standing in its near marker form.

The CH-69 pins whole stand in
product/tests/test_restart_step17_fix4_k4.py, and the
CH-15 and CH-16 pins, the CH-45 pins, and the CH-35, CH-37,
and CH-38 pins in their own files; they are re-run at this
cluster close, not edited here.

Constructions are the attack paper own forms:
design/steps/step-17r-attack5-11.md, cases c08, s1 to s6.

Copyright: J.P. Picard aka Macro-Harder
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h


def _body(status_line):
    body = h._header_block()
    body += "### DQ-001: Open one\n\n"
    body += status_line + "\n\n"
    body += "Question: Which option?\n"
    body += "Options: A, B\nCost of deciding late: blocked.\n"
    body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
    return body


def _run(status_line, name):
    return h.run_pipeline(_body(status_line).encode("utf-8"), name)


def _run_cli(status_line, name, subcommand):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / name
        target.write_bytes(_body(status_line).encode("utf-8"))
        code, out, err = h.run_cli(subcommand, target)
    return code, (out + err).decode("utf-8", errors="replace")


def _rule2(output):
    return h.findings_for(output, entry_id="DQ-001", rule=2)


def _entry(output):
    return h.entry_by_id(output, "DQ-001")


def _occurrence_total(output):
    recon = h.reconciliation_of(output)
    return h.int_of(h.get(recon, "status_occurrence_total",
                          "occurrence_total"))


def _group_members(output, *name_parts):
    group = h.census_class(h.census_of(output), *name_parts)
    if group is None:
        return []
    return h.census_members(group)


def _assert_credited(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)), "Open")
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(_occurrence_total(output), 1)
    test_case.assertIn("DQ-001", _group_members(
        output, "unheaded paragraphs"))
    waiting, _blocking = h.waiting_and_blocking(output)
    test_case.assertEqual(h.int_of(waiting), 1)


class Ch89ChargedSegmentPositionsTest(unittest.TestCase):
    """F-11R5-01: the charged constructions, cases c08, s6,
    and s3 of the attack paper, each failing before the cure
    in the Ambiguous form at exit 4 and standing credited
    after it."""

    def test_c08_segment_between_label_and_colon_credits(self):
        _assert_credited(self, "Status <!-- c -->: Banked",
                         "c08_segment_label_colon_status.md")

    def test_c08_head_element_is_a_line_start_status_line(self):
        model, _output = _run("Status <!-- c -->: Banked",
                              "c08_segment_label_colon_status.md")
        entry = h.entry_by_id(model, "DQ-001")
        elements = h.get(entry, "status_elements") or []
        self.assertEqual(len(elements), 1)
        element = elements[0]
        self.assertEqual(h.get(element, "kind"),
                         "line start Status line")
        self.assertEqual(h.get(element, "verbatim"), "Banked")
        self.assertEqual(h.get(element, "occurrence_kind"),
                         "line start")
        self.assertEqual(h.get(entry, "near_marker_occurrences")
                         or [], [])

    def test_c08_cli_exits_zero_on_both_subcommands(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status <!-- c -->: Banked",
                    "c08_segment_label_colon_status.md", subcommand)
                self.assertEqual(code, 0)
                self.assertNotIn("Ambiguous sub label", combined)
                self.assertNotIn("carries no element", combined)
                self.assertIn("Ambiguous reporting count: 0",
                              combined)

    def test_s6_segment_with_a_space_on_each_side_credits(self):
        _assert_credited(self, "Status <!-- c --> : Banked",
                         "s6_status_segment_two_spaces.md")

    def test_s3_segment_inside_the_status_word_credits(self):
        _assert_credited(self, "Stat<!-- c -->us: Banked",
                         "s3_status_segment_inside_word.md")

    def test_two_segments_inside_the_status_word_credit(self):
        _assert_credited(self, "St<!-- a -->at<!-- b -->us: Banked",
                         "k7_two_segments_inside_word.md")

    def test_segment_at_the_variant_label_word_break_credits(self):
        # The variant label is two words: a segment standing
        # at its word break is the word break position of the
        # charge on the Status label family. The stored form
        # joins the parts at the one word break the line as
        # written carries, and the variant element stands.
        model, output = _run("Status <!-- c --> unchanged",
                             "k7_segment_variant_word_break.md")
        self.assertIsNotNone(output)
        entry = h.entry_by_id(model, "DQ-001")
        elements = h.get(entry, "status_elements") or []
        self.assertEqual(len(elements), 1)
        self.assertEqual(h.get(elements[0], "kind"),
                         "variant phrasing")
        self.assertEqual(h.get(elements[0], "occurrence_kind"),
                         "variant")
        self.assertEqual(_rule2(output), [])
        self.assertEqual(_occurrence_total(output), 1)


class Ch89ContrastCreditedPinsTest(unittest.TestCase):
    """Contrasts of the attack paper standing credited
    before and after: cases s2, s4, and s5, and the plain
    control. The defect turns on the segment standing inside
    the label, and on nothing else."""

    def test_s2_segment_after_the_colon_stands_credited(self):
        _assert_credited(self, "Status: <!-- c --> Banked",
                         "s2_status_segment_after_colon.md")

    def test_s4_segment_before_the_label_stands_credited(self):
        _assert_credited(self, "<!-- c --> Status: Banked",
                         "s4_status_segment_before_label.md")

    def test_s5_segment_in_the_no_space_colon_form_credits(self):
        _assert_credited(self, "Status:<!-- c --> Banked",
                         "s5_status_segment_colon_nospace.md")

    def test_plain_status_line_control_stands_credited(self):
        _assert_credited(self, "Status: Banked",
                         "k7_plain_status_control.md")


class Ch89WrittenFormBoundPinsTest(unittest.TestCase):
    """Pins in the other direction, standing before and
    after: the CH-69 bound reaches segment boundaries only,
    and no written form is normalised by this cure."""

    def test_s1_written_space_before_colon_stays_ambiguous(self):
        _model, output = _run("Status : Banked",
                              "s1_status_space_colon.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(h.entry_sub_label(_entry(output)),
                         "No element")
        self.assertEqual(len(_rule2(output)), 1)
        self.assertEqual(_occurrence_total(output), 0)

    def test_s1_cli_exits_four_on_both_subcommands(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status : Banked", "s1_status_space_colon.md",
                    subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    # The near marker statement stands on the
                    # findings surface, which render does not
                    # print; the Ambiguous form stands on both.
                    self.assertIn("carries no element", combined)

    def test_written_space_with_a_segment_before_the_label(self):
        # A segment standing before the label does not cure a
        # space before the colon written in the file: the
        # written form stands, with its near marker Warning.
        _model, output = _run("<!-- c --> Status : Banked",
                              "k7_segment_before_written_space.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(len(_rule2(output)), 1)
        self.assertEqual(_occurrence_total(output), 0)

    def test_marker_wholly_inside_a_segment_counts_nothing(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "<!-- Status: Ruled -->\n\n"
        body += "Question: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = h.run_pipeline(
            body.encode("utf-8"), "k7_marker_inside_segment.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 1)
        self.assertEqual(_rule2(output), [])

    def test_unclosed_segment_in_the_label_credits_nothing(self):
        # A segment left unclosed on the Status line leaves
        # the comment open over the rest of the line, as an
        # unclosed segment stands everywhere else in the
        # pass: no element stands on the line.
        _model, output = _run("Status <!-- c : Banked",
                              "k7_unclosed_segment_in_label.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 0)
        self.assertEqual(_rule2(output), [])

    def test_one_edit_typo_label_keeps_its_near_marker_form(self):
        _model, output = _run("Staus: Banked",
                              "k7_typo_label_control.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(len(_rule2(output)), 1)
        self.assertEqual(_occurrence_total(output), 0)


if __name__ == "__main__":
    unittest.main()
