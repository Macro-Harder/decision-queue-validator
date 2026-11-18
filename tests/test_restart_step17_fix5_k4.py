"""Step 17 fix wave 5, Fix Seat K4 tests.

Charges CH-80 and CH-81, as ruled at section 52 of
design/steps/step-17r-record.md, with rulings (a) and (h)
disposed as charge bounds in that ruling, and prepared at
design/steps/step-17r-triage5-prep.md.

CH-80 (parse, the heading separator after the hashes past
the tab form): Finding 1 of round 5 attack seat 6 at
design/steps/step-17r-attack5-6.md. A duplicate entry
heading separated from its hashes by a separator character
other than the plain space or the tab is no heading at all
to the reader, its body absorbed into the preceding entry,
and in the same state case the file passes wholly clean
with the copy named on no surface. Cure bound, under
ruling (h): heading recognition takes a copy heading
separated by a character of the separator ground of ruling
(a), the run ground, stated once for every surface: a
character presenting no visible glyph, the categories Cn,
Co, Cf, Cc (the governed terminators excepted), Zs, Zl,
Zp, Mn, Mc, and Me, together with any character, in any
category, whose Unicode name carries BLANK, FILLER, FILL,
or REPLACEMENT. The no heading side stands stated and
tested in this file: prose lines opening with hashes that
are not headings keep their standing readings, a separator
form the ruling does not name makes no heading, and a
separator heading in no entry form takes no Warning.

CH-81 (parse, the final line cut off rule, round 5 limbs):
the six Low findings of round 5 attack seat 2 at
design/steps/step-17r-attack5-2.md (ATK5-2-01 to
ATK5-2-06). One rule in six limbs: complete final lines in
structural forms stand whole in their own closing forms,
with the cut side stated test first for those forms; a
final line standing inside a code fence is read as fence
content; the bullet completeness reading reaches the
parenthesis numbered marker, the K9 stated bound of the
digits and full stop form extended by this one form as
charged; a cut DQ reference closing a heading or bullet
final line stands cut, the heading limb reaching the
level 4 heading text the attack paper charges and not the
entry heading form; a final Blocks line with two lone
carriage returns takes the same value as its terminated
twin; and valueless labelled final lines stand whole, the
valueless Status member excluded as the rule docstring
states it. Governing pins stand whole in this file: the
CH-58 pins, the K9 final line and tab bounds as charged,
the note (h) forms standing pinned as still cut, and the
fence opener forms standing as round 4 left them.

Constructions stand in the attack papers own shapes. An
entry stands whole where it takes no unparsed marker and
no rule 12 finding, and cut where it takes both.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _file(final_line):
    body = h._header_block()
    body += "### DQ-001: Sample question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take first?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += final_line
    return body.encode("utf-8")


def _plain_file(final_line):
    body = "# Decision queue\n\n"
    body += "### DQ-001: Sample question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take first?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += final_line
    return body.encode("utf-8")


def _assert_whole(test, data, name):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    entry = h.entry_by_id(model, "DQ-001")
    test.assertFalse(bool(h.get(entry, "unparsed",
                                "unparsed_flag")))
    test.assertEqual(h.findings_for(output, rule=12), [])


def _assert_cut(test, data, name):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    entry = h.entry_by_id(model, "DQ-001")
    test.assertTrue(bool(h.get(entry, "unparsed",
                               "unparsed_flag")))
    test.assertTrue(h.findings_for(output, rule=12))


def _open_entry(heading_line, status, blocks, extra=""):
    return (
        heading_line + "\n\n"
        "Status: " + status + "\n\n"
        "Question: Which option should we take?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked.\n\n"
        "Blocks: " + blocks + "\n\n"
        "This entry is waiting for a decision.\n\n" + extra)


def _sep_queue(sep_heading, absorbed_status):
    """The attack seat 6 base: DQ-001 Open at level 3, then
    the same identifier under a separator separated heading
    carrying a full second body, then DQ-002."""
    parts = ["# Decision queue\n\n"]
    parts.append(_open_entry("### DQ-001: Alpha", "Open",
                             "DQ-002"))
    extra = ""
    if absorbed_status == "Ruled":
        extra = "Ruling text: take Option A.\n\n"
    parts.append(_open_entry(sep_heading, absorbed_status,
                             "DQ-002", extra))
    parts.append(_open_entry("### DQ-002: Beta question",
                             "Open", "DQ-001"))
    return "".join(parts).encode("utf-8")


def _pin06(output):
    return [f for f in h.findings_of(output)
            if str(h.get(f, "rule_id")) == "PIN-06"]


def _statements(output):
    return [h.finding_statement(f) or ""
            for f in h.findings_of(output)]


def _cli_validate(data):
    path = h.temp_input(data)
    code, out, _err = h.run_cli("validate", path)
    return code, out.decode("utf-8", errors="replace")


# The eight separators measured at attack seat 6 Finding 1:
# the no break space, the vertical tab, the form feed, the
# em space, the ideographic space, the ogham space mark,
# the narrow no break space, and the zero width space.
_MEASURED_SEPARATORS = (
    "\u00a0", "\x0b", "\x0c", "\u2003",
    "\u3000", "\u1680", "\u202f", "\u200b")


class Step17Fix5K4SeparatorHeadingTest(unittest.TestCase):
    """CH-80, seat 6 Finding 1: a duplicate entry heading
    separated from its hashes by a separator character of
    the ruling (a) ground takes the unmatched heading
    treatment the tab form takes, naming the heading as
    written, and its body stands in no entry span."""

    def test_measured_separators_same_state_take_pin06(self):
        for sep in _MEASURED_SEPARATORS:
            with self.subTest(sep=repr(sep)):
                data = _sep_queue(
                    "###" + sep + "DQ-001: Alpha tab", "Open")
                _model, output = h.run_pipeline(
                    data, "fix5_k4_sep.md")
                found = _pin06(output)
                self.assertEqual(len(found), 1)
                self.assertIn(
                    "DQ-001: Alpha tab",
                    h.finding_statement(found[0]) or "")
                self.assertIn(
                    "matches no recognised heading form",
                    h.finding_statement(found[0]) or "")
                self.assertEqual(int(h.entry_total(output)), 2)
                self.assertFalse(any(
                    "used more than once" in s
                    for s in _statements(output)))

    def test_measured_separators_same_state_cli_exit(self):
        for sep in _MEASURED_SEPARATORS:
            with self.subTest(sep=repr(sep)):
                data = _sep_queue(
                    "###" + sep + "DQ-001: Alpha tab", "Open")
                code, _out = _cli_validate(data)
                self.assertEqual(code, 1)

    def test_ruling_ground_neighbours_take_pin06(self):
        # The ruling (a) ground beyond the measured eight:
        # an unassigned character (Cn), a private use
        # character (Co), and a character whose name carries
        # BLANK (the braille pattern blank, category So).
        for sep in ("\u0378", "\ue000", "\u2800"):
            with self.subTest(sep=repr(sep)):
                data = _sep_queue(
                    "###" + sep + "DQ-001: Alpha tab", "Open")
                _model, output = h.run_pipeline(
                    data, "fix5_k4_sep_ground.md")
                found = _pin06(output)
                self.assertEqual(len(found), 1)
                self.assertIn(
                    "DQ-001: Alpha tab",
                    h.finding_statement(found[0]) or "")
                self.assertEqual(int(h.entry_total(output)), 2)

    def test_separator_duplicate_body_in_no_entry_span(self):
        data = _sep_queue("###\u00a0DQ-001: Alpha tab", "Open")
        model = h.run_parse(data, "fix5_k4_sep_span.md")
        self.assertFalse(h.is_failure_result(model))
        segments = h.as_list(h.get(model, "orphan_segments"))
        unmatched = [s for s in segments
                     if h.get(s, "unmatched_heading")]
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(h.get(unmatched[0], "heading_text"),
                         "DQ-001: Alpha tab")
        entries = h.entries_of(model)
        copies = [e for e in entries
                  if h.entry_identifier(e) == "DQ-001"]
        self.assertEqual(len(copies), 1)

    def test_separator_duplicate_differing_state_host(self):
        # The ruled body companion form: the absorbed copy
        # is Ruled, the host as written is Open. After the
        # cure the host keeps its own state and the copy is
        # named by its Warning alone.
        data = _sep_queue("###\u00a0DQ-001: Alpha tab", "Ruled")
        _model, output = h.run_pipeline(data, "fix5_k4_sepb.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha tab",
                      h.finding_statement(found[0]) or "")
        host = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(host), "Open")
        code, _out = _cli_validate(data)
        self.assertEqual(code, 1)

    def test_separator_heading_at_levels_take_pin06(self):
        for hashes in ("##", "#", "####"):
            with self.subTest(hashes=hashes):
                data = _sep_queue(
                    hashes + "\u00a0DQ-001: Alpha tab", "Open")
                _model, output = h.run_pipeline(
                    data, "fix5_k4_sep_level.md")
                found = _pin06(output)
                self.assertEqual(len(found), 1)
                self.assertIn(
                    "DQ-001: Alpha tab",
                    h.finding_statement(found[0]) or "")
                self.assertEqual(int(h.entry_total(output)), 2)

    def test_separator_named_r7_heading_takes_pin06(self):
        parts = ["# Decision queue\n\n"]
        parts.append(_open_entry("### R-7 closure conflict",
                                 "Open", "DQ-002"))
        parts.append(_open_entry(
            "###\u00a0R-7 closure conflict", "Open", "DQ-002"))
        parts.append(_open_entry("### DQ-002: Beta question",
                                 "Open", "DQ-001"))
        _model, output = h.run_pipeline(
            "".join(parts).encode("utf-8"), "fix5_k4_sep_r7.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("R-7 closure conflict",
                      h.finding_statement(found[0]) or "")
        self.assertEqual(int(h.entry_total(output)), 2)


class Step17Fix5K4SeparatorBoundTest(unittest.TestCase):
    """CH-80 under ruling (h): the no heading side stands
    stated and tested. A separator form the ruling does not
    name makes no heading, a separator heading in no entry
    form takes no Warning, and the queue header bound of
    CH-58 stands for the separator forms as for the tab."""

    def test_unruled_separator_makes_no_heading(self):
        # A visible separator character stands outside the
        # ruling (a) ground: the line is no heading at all,
        # takes no PIN-06 Warning, and raises no entry, in
        # both eras. The copy body is absorbed, as the
        # standing reading of such a line has it.
        for sep in (".", "x"):
            with self.subTest(sep=sep):
                data = _sep_queue(
                    "###" + sep + "DQ-001: Alpha tab", "Open")
                _model, output = h.run_pipeline(
                    data, "fix5_k4_sep_unruled.md")
                self.assertEqual(_pin06(output), [])
                self.assertEqual(int(h.entry_total(output)), 2)

    def test_separator_heading_in_no_entry_form_no_pin06(self):
        # The FLAG 12 bound form, as the K9 file states it:
        # a level 1 heading in no entry form stands as file
        # structure with no PIN-06 Warning, in the separator
        # form as in the plain form.
        data = ("# Decision queue\n\n" +
                _open_entry("### DQ-001: Alpha", "Open",
                            "DQ-002") +
                _open_entry("### DQ-002: Beta question", "Open",
                            "DQ-001") +
                "#\u00a0Appendix notes\n\n"
                "Plain closing prose with no status line.\n")
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix5_k4_sep_nonentry.md")
        self.assertEqual(_pin06(output), [])

    def test_separator_queue_header_first_stands_clean(self):
        data = ("#\u00a0Decision queue\n\n" +
                _open_entry("### DQ-001: Alpha", "Open",
                            "DQ-002") +
                _open_entry("### DQ-002: Beta question", "Open",
                            "DQ-001"))
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix5_k4_sep_header.md")
        self.assertEqual(_pin06(output), [])
        self.assertEqual(int(h.entry_total(output)), 2)
        code, _out = _cli_validate(data.encode("utf-8"))
        self.assertEqual(code, 0)

    def test_tab_pin06_pin_stands_whole(self):
        # The CH-58 pin in view, passing before and after:
        # the tab separated duplicate takes its Warning.
        data = _sep_queue("###\tDQ-001: Alpha tab", "Open")
        _model, output = h.run_pipeline(data, "fix5_k4_tab.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha tab",
                      h.finding_statement(found[0]) or "")
        self.assertEqual(int(h.entry_total(output)), 2)

    def test_space_duplicate_error_pin_stands_whole(self):
        # The space control in view, passing before and
        # after: the plain space duplicate takes the
        # duplicate Error, copies counted per entry.
        data = _sep_queue("### DQ-001: Alpha tab", "Open")
        _model, output = h.run_pipeline(
            data, "fix5_k4_space.md")
        self.assertTrue(any(
            "used more than once" in s
            for s in _statements(output)))
        self.assertEqual(int(h.entry_total(output)), 3)


class Step17Fix5K4StructuralFinalLineTest(unittest.TestCase):
    """CH-81, ATK5-2-01: complete final lines in structural
    forms the tool itself reads elsewhere stand whole in
    their own closing forms. The cut side is stated first
    in this class: a cut member of a newly reached form
    does not stand whole by the cure."""

    def test_cut_members_of_structural_forms_stand_cut(self):
        for final_line in (
                "<!-- Standing note closed here",
                "| DQ-002 | None",
                "> Work stays blocked until the",
                "[ref]: DQ-00 standing reference",
                "[^1]: Work stays blocked until the"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix5_k4_struct_cut.md")

    def test_comment_complete_stands_whole(self):
        _assert_whole(
            self, _file("<!-- Standing note closed here -->"),
            "fix5_k4_comment.md")

    def test_table_row_complete_stands_whole(self):
        _assert_whole(self, _file("| DQ-002 | None |"),
                      "fix5_k4_table.md")

    def test_blockquote_complete_stands_whole(self):
        _assert_whole(
            self,
            _file("> Work stays blocked until the ruling lands"),
            "fix5_k4_blockquote.md")

    def test_setext_underline_stands_whole(self):
        _assert_whole(self, _file("Standing note\n==="),
                      "fix5_k4_setext.md")

    def test_link_ref_def_stands_whole(self):
        _assert_whole(
            self, _file("[ref]: DQ-002 standing reference"),
            "fix5_k4_linkref.md")

    def test_footnote_def_stands_whole(self):
        _assert_whole(self, _file("[^1]: Work stays blocked"),
                      "fix5_k4_footnote.md")


class Step17Fix5K4FenceContentFinalLineTest(unittest.TestCase):
    """CH-81, ATK5-2-02: a final line standing inside a code
    fence is read as fence content, as the parser reads it
    on every other line, not as entry prose."""

    def test_fence_content_final_line_stands_whole(self):
        _assert_whole(
            self,
            _plain_file("```\nDQ-002 stands noted inside the fence"),
            "fix5_k4_fence_content.md")

    def test_fence_content_sentence_pin_stands_whole(self):
        # The control in view, whole in both eras by the
        # prose sentence close.
        _assert_whole(
            self,
            _plain_file("```\nDQ-002 stands noted inside the fence."),
            "fix5_k4_fence_sentence.md")

    def test_fence_opener_final_line_stands_cut(self):
        # Bound in view, as round 4 left it: an opener
        # standing as the final line opens a block that
        # never closes in the file, and the fence content
        # limb does not reach it.
        _assert_cut(self, _plain_file("```python"),
                    "fix5_k4_fence_opener.md")


class Step17Fix5K4ParenBulletTest(unittest.TestCase):
    """CH-81, ATK5-2-03: a complete bullet item under the
    parenthesis numbered marker stands whole, the K9
    stated bound of the digits and full stop form extended
    by this one form as charged. The cut side is stated
    first in this class."""

    def test_cut_items_under_paren_marker_stand_cut(self):
        for final_line in (
                "1) Option B: leave the note unadop",
                "1) Option A, Option B and"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix5_k4_paren_cut.md")

    def test_paren_numbered_item_complete_stands_whole(self):
        _assert_whole(
            self, _file("1) Option B: leave the note adopted"),
            "fix5_k4_paren.md")

    def test_digits_full_stop_pin_stands_whole(self):
        # The K9 pin in view, passing before and after.
        _assert_whole(
            self, _file("1. Option B: leave the note adopted"),
            "fix5_k4_numbered_pin.md")


class Step17Fix5K4CutReferenceFinalLineTest(unittest.TestCase):
    """CH-81, ATK5-2-04: a cut DQ reference closing a
    heading or bullet final line stands cut, where the
    labelled branch and the Blocks branch already test a
    DQ token for reference completeness. The heading limb
    reaches the level 4 heading text the attack paper
    charges; the entry heading form stands on the heading
    recognition surface and is not reached."""

    def test_heading_cut_ref_stands_cut(self):
        _assert_cut(
            self,
            _file("#### Ruling by Captain JP on DQ-00"),
            "fix5_k4_heading_cutref.md")

    def test_bullet_cut_ref_stands_cut(self):
        _assert_cut(self, _file("- See DQ-00"),
                    "fix5_k4_bullet_cutref.md")

    def test_star_bullet_cut_ref_stands_cut(self):
        _assert_cut(self, _file("* See DQ-00"),
                    "fix5_k4_star_cutref.md")

    def test_full_ref_controls_stand_whole(self):
        for final_line in (
                "- See DQ-002",
                "#### Ruling by Captain JP on DQ-002"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, _file(final_line),
                              "fix5_k4_fullref.md")


class Step17Fix5K4BlocksDoubleCrTest(unittest.TestCase):
    """CH-81, ATK5-2-05: a final Blocks line whose value
    carries two lone carriage returns takes the same value
    as its terminated twin, the empty part between two
    boundaries standing as the field reading takes it."""

    def test_blocks_double_cr_stands_whole(self):
        _assert_whole(self, _file("Blocks: DQ-002\r\rDQ-003"),
                      "fix5_k4_blocks_double_cr.md")

    def test_blocks_double_cr_does_not_mask_cut_ref(self):
        for final_line in (
                "Blocks: DQ-002\r\rDQ-00",
                "Blocks: DQ-00\r\rDQ-003"):
            with self.subTest(final_line=repr(final_line)):
                _assert_cut(self, _file(final_line),
                            "fix5_k4_blocks_double_cr_cut.md")

    def test_blocks_single_cr_pin_stands_whole(self):
        # The K9 pin in view, passing before and after.
        _assert_whole(self, _file("Blocks: DQ-002\rDQ-003"),
                      "fix5_k4_blocks_single_cr.md")


class Step17Fix5K4ValuelessLabelledTest(unittest.TestCase):
    """CH-81, ATK5-2-06: a valueless labelled final line
    stands whole, bounded to the labelled family the rule
    docstring does not name. The valueless Status member
    stands excluded, as the docstring states it, and is
    pinned as still cut in this class."""

    def test_blocks_colon_only_stands_whole(self):
        _assert_whole(self, _file("Blocks:"),
                      "fix5_k4_blocks_colon.md")

    def test_ruled_colon_only_stands_whole(self):
        _assert_whole(self, _file("Ruled:"),
                      "fix5_k4_ruled_colon.md")

    def test_owner_colon_only_stands_whole(self):
        _assert_whole(self, _file("Owner of record:"),
                      "fix5_k4_owner_colon.md")

    def test_status_colon_only_pin_stands_cut(self):
        # The excluded member, pinned as the rule docstring
        # states it: a Status line carrying no value stands
        # cut off in its own terms, in both eras.
        _assert_cut(self, _file("Status:"),
                    "fix5_k4_status_colon.md")


class Step17Fix5K4GoverningPinsTest(unittest.TestCase):
    """CH-81 governing pins in view: the note (h) forms
    stand pinned as still cut, and the K9 final line
    bounds stand as charged."""

    def test_note_h_forms_stand_pinned_as_still_cut(self):
        for final_line in (
                "Options: Option A, Option B, and Option C",
                "Blocks: none",
                "What it blocks: Item 155 only"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix5_k4_note_h.md")

    def test_labelled_cut_ref_pin_stands_cut(self):
        # The labelled branch cut reference pin in view:
        # a generic labelled line closing on a cut reference
        # stands cut in both eras.
        _assert_cut(self, _file("Source: DQ-00"),
                    "fix5_k4_labelled_cutref.md")


if __name__ == "__main__":
    unittest.main()
