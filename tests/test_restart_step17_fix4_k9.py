"""Step 17 fix wave 4, Fix Seat K9 tests.

Charges CH-57 and CH-58, as ruled at section 38 of
design/steps/step-17r-record.md, with FLAG 9 and FLAG 12
disposed as charge bounds in that ruling, and prepared at
design/steps/step-17r-triage4-prep.md.

CH-57 (parse, the final line cut off rule, round 4 limbs):
the four Low findings of attack seat 2 at
design/steps/step-17r-attack4-2.md (ATK4-2-01 to
ATK4-2-04, register item 17R-178). One rule in four limbs:
a final line stands whole only where its value is complete
in its own form, read in the form the tool itself reads on
every other line of the file. FLAG 9 bound, express: this
charge cures, discharges, and moves no note (h) form; the
three note (h) forms stand pinned as still cut below, and
the complete bullet pin of ATK2-2-05 stands unbroken. The
bullet marker limb states its cut side test first in this
file: a cut item under a star, plus, or numbered marker
stands cut, so the completeness reading for those markers
does not stand whole over cut items.

CH-58 (parse, the heading separator after the hashes):
Finding 1 of attack seat 6 at
design/steps/step-17r-attack4-6.md (register item
17R-180). A duplicate entry heading separated from its
hashes by a tab is no heading at all to the reader, its
body absorbed into the preceding entry. Cure bound: a
heading line whose hashes stand separated from its text
by a tab takes the unmatched heading treatment its
displaced neighbours take, naming the heading as written,
and its body stands in no entry span. FLAG 12 bound,
express: the cure names displaced entry heading forms
only; the queue header itself stands as file structure
under the CH-49 ruling bound (the first heading standing
as the queue header whatever words it carries) and takes
no Warning and no entry from this cure; the CH-20 and
CH-49 pins stand in view in this file and are re-run at
the cluster close.

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


def _tab_queue(tab_heading, absorbed_status):
    """The attack seat 6 base: DQ-001 Open at level 3, then
    the same identifier under a tab separated heading
    carrying a full second body, then DQ-002."""
    parts = ["# Decision queue\n\n"]
    parts.append(_open_entry("### DQ-001: Alpha", "Open",
                             "DQ-002"))
    extra = ""
    if absorbed_status == "Ruled":
        extra = "Ruling text: take Option A.\n\n"
    parts.append(_open_entry(tab_heading, absorbed_status,
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


class Step17Fix4K9LeadingRunFinalLineTest(unittest.TestCase):
    """CH-57, ATK4-2-01: a final line standing behind a
    leading run character of the format or mark classes is
    read as cut, where its terminated twin is read under
    the one run set."""

    def test_status_behind_format_or_mark_run_stands_whole(self):
        for final_line in (
                "\u200bStatus: Banked",
                "\u0301Status: Banked",
                "\u2060Status: Banked",
                "\u00adStatus: Banked"):
            with self.subTest(final_line=repr(final_line)):
                _assert_whole(self, _file(final_line),
                              "fix4_k9_run_status.md")

    def test_blocks_behind_zero_width_space_stands_whole(self):
        _assert_whole(self, _file("\u200bBlocks: DQ-002"),
                      "fix4_k9_run_blocks.md")

    def test_heading_behind_zero_width_space_stands_whole(self):
        _assert_whole(
            self,
            _plain_file("\u200b#### Ruling by Captain JP"),
            "fix4_k9_run_heading.md")

    def test_in_set_neighbours_stand_whole_before_and_after(self):
        # Pins: the members of the run set the plain strip
        # and the express byte order mark removal already
        # covered on the uncured tree stand whole in both
        # eras.
        for final_line in (
                "\x0bStatus: Banked",
                "\u00a0Status: Banked",
                "\ufeffStatus: Banked"):
            with self.subTest(final_line=repr(final_line)):
                _assert_whole(self, _file(final_line),
                              "fix4_k9_run_pins.md")

    def test_run_before_valueless_status_still_cut(self):
        # Guard: the run reading reaches the Status test,
        # it does not supply a value.
        _assert_cut(self, _file("\u200bStatus:"),
                    "fix4_k9_run_valueless.md")

    def test_run_before_cut_prose_still_cut(self):
        # Guard: a prose line behind a run character that
        # closes no sentence stands cut in both eras.
        _assert_cut(
            self,
            _file("\u200bThis question is waiting for a deci"),
            "fix4_k9_run_prose_cut.md")


class Step17Fix4K9BlocksTrailingTest(unittest.TestCase):
    """CH-57, ATK4-2-02: a final Blocks line carrying a
    trailing zero width space is read as cut, where a
    trailing byte order mark and a trailing no break space
    stand parsed."""

    def test_blocks_trailing_zero_width_space_stands_whole(self):
        _assert_whole(self, _file("Blocks: DQ-002\u200b"),
                      "fix4_k9_blocks_trail_zwsp.md")

    def test_blocks_trailing_neighbours_stand_whole(self):
        # Pins, whole before and after: the trailing forms
        # the neighbouring branches already disregarded.
        for final_line in (
                "Blocks: DQ-002\u00a0",
                "Blocks: DQ-002\t",
                "Blocks: DQ-002\ufeff",
                "Owner of record: Clerk in Charge\u200b"):
            with self.subTest(final_line=repr(final_line)):
                _assert_whole(self, _file(final_line),
                              "fix4_k9_blocks_trail_pins.md")

    def test_blocks_trailing_run_does_not_mask_cut_ref(self):
        # Guard: a genuinely cut reference closing behind a
        # trailing run character stands cut in both eras.
        _assert_cut(self, _file("Blocks: DQ-00\u200b"),
                    "fix4_k9_blocks_trail_cut.md")


class Step17Fix4K9BulletMarkerTest(unittest.TestCase):
    """CH-57, ATK4-2-03: complete bullet items under the
    star, plus, and numbered list markers are read as cut
    prose. The cut side is stated first in this class, per
    FLAG 9: the completeness reading for the new markers
    does not stand whole over cut items the dash limb
    refuses."""

    def test_cut_items_under_new_markers_stand_cut(self):
        for final_line in (
                "* Option B: leave the note unadop",
                "+ Option B: leave the note unadop",
                "1. Option B: leave the note unadop",
                "* Option A, Option B and",
                "+ Option A, Option B and",
                "1. Option A, Option B and"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix4_k9_bullet_cut.md")

    def test_star_item_complete_stands_whole(self):
        _assert_whole(
            self, _file("* Option B: leave the note adopted"),
            "fix4_k9_bullet_star.md")

    def test_plus_item_complete_stands_whole(self):
        _assert_whole(
            self, _file("+ Option B: leave the note adopted"),
            "fix4_k9_bullet_plus.md")

    def test_numbered_item_complete_stands_whole(self):
        _assert_whole(
            self, _file("1. Option B: leave the note adopted"),
            "fix4_k9_bullet_numbered.md")

    def test_dash_complete_pin_stands_unbroken(self):
        # The complete bullet pin of ATK2-2-05, standing as
        # a pin that must not break under FLAG 9.
        for final_line in (
                "- Option B: leave the note adopted",
                "- Option B: leave the note unadopted"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, _file(final_line),
                              "fix4_k9_bullet_dash_pin.md")

    def test_dash_cut_controls_stand_cut(self):
        for final_line in (
                "- Option B: leave the note unadop",
                "- Option A, Option B and"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix4_k9_bullet_dash_cut.md")

    def test_marker_only_lines_stand_cut(self):
        # Bound recorded at the attack paper observation 2,
        # not charged: a marker carrying no content may
        # itself be the whole of a cut longer line.
        for final_line in ("*", "+", "-"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix4_k9_bullet_marker_only.md")


class Step17Fix4K9BlocksLoneCrTest(unittest.TestCase):
    """CH-57, ATK4-2-04: a final Blocks line whose value
    carries a lone carriage return between two references
    is read as cut, where its terminated twin stands parsed
    with the value taken."""

    def test_blocks_lone_cr_between_refs_stands_whole(self):
        _assert_whole(self, _file("Blocks: DQ-002\rDQ-003"),
                      "fix4_k9_blocks_lone_cr.md")

    def test_blocks_lone_cr_does_not_mask_cut_ref(self):
        # Controls, cut in both eras: the carriage return
        # reading takes the same value as the field reading,
        # it does not complete a cut reference on either
        # side of it.
        for final_line in (
                "Blocks: DQ-002\rDQ-00",
                "Blocks: DQ-00\rDQ-003"):
            with self.subTest(final_line=repr(final_line)):
                _assert_cut(self, _file(final_line),
                            "fix4_k9_blocks_cr_cut.md")

    def test_blocks_closing_on_cr_stands_whole(self):
        # Pin: the cured d5 form, a complete Blocks line
        # closing on a carriage return, stands whole in
        # both eras.
        _assert_whole(self, _file("Blocks: DQ-002\r"),
                      "fix4_k9_blocks_cr_close.md")


class Step17Fix4K9NoteHPinsTest(unittest.TestCase):
    """CH-57 under FLAG 9: no note (h) form is cured,
    discharged, or moved by this charge. The three forms
    stand pinned as still cut, in the ruled forms the
    round 2 ruling left them."""

    def test_note_h_forms_stand_pinned_as_still_cut(self):
        for final_line in (
                "Options: Option A, Option B, and Option C",
                "Blocks: none",
                "What it blocks: Item 155 only"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix4_k9_note_h.md")

    def test_options_dangling_and_still_cut(self):
        # CH-34 neighbour pin standing beside this charge:
        # the Options limb cut forms stand cut in both eras.
        _assert_cut(self, _file("Options: Option A, Option B and"),
                    "fix4_k9_options_dangling.md")


class Step17Fix4K9TabHeadingTest(unittest.TestCase):
    """CH-58, seat 6 Finding 1: a duplicate entry heading
    separated from its hashes by a tab takes the unmatched
    heading treatment, naming the heading as written, and
    its body stands in no entry span."""

    def test_tab_duplicate_same_state_takes_pin06(self):
        data = _tab_queue("###\tDQ-001: Alpha tab", "Open")
        _model, output = h.run_pipeline(data, "fix4_k9_tab.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha tab",
                      h.finding_statement(found[0]) or "")
        self.assertIn("matches no recognised heading form",
                      h.finding_statement(found[0]) or "")

    def test_tab_duplicate_counts_no_extra_entry(self):
        data = _tab_queue("###\tDQ-001: Alpha tab", "Open")
        _model, output = h.run_pipeline(data, "fix4_k9_tab.md")
        self.assertEqual(int(h.entry_total(output)), 2)
        self.assertFalse(any(
            "used more than once" in s
            for s in _statements(output)))

    def test_tab_duplicate_body_stands_in_no_entry_span(self):
        data = _tab_queue("###\tDQ-001: Alpha tab", "Open")
        model = h.run_parse(data, "fix4_k9_tab.md")
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

    def test_tab_duplicate_differing_state_host_unmoved(self):
        # The n08b form: the absorbed copy is Ruled, the
        # host as written is Open. After the cure the host
        # keeps its own state and the tab copy is named by
        # its Warning alone.
        data = _tab_queue("###\tDQ-001: Alpha tab", "Ruled")
        _model, output = h.run_pipeline(data, "fix4_k9_tabb.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha tab",
                      h.finding_statement(found[0]) or "")
        host = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(host), "Open")
        code, _out = _cli_validate(data)
        self.assertEqual(code, 1)

    def test_tab_duplicate_same_state_cli_exit_is_warning(self):
        # The n08 form on the uncured tree passes wholly
        # clean at exit 0 with the copy named on no surface.
        data = _tab_queue("###\tDQ-001: Alpha tab", "Open")
        code, _out = _cli_validate(data)
        self.assertEqual(code, 1)

    def test_tab_heading_at_level2_takes_pin06(self):
        data = _tab_queue("##\tDQ-001: Alpha tab", "Open")
        _model, output = h.run_pipeline(data, "fix4_k9_tab2.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha tab",
                      h.finding_statement(found[0]) or "")
        self.assertEqual(int(h.entry_total(output)), 2)

    def test_tab_heading_at_level1_takes_pin06(self):
        data = _tab_queue("#\tDQ-001: Alpha tab", "Open")
        _model, output = h.run_pipeline(data, "fix4_k9_tab1.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha tab",
                      h.finding_statement(found[0]) or "")
        self.assertEqual(int(h.entry_total(output)), 2)


class Step17Fix4K9QueueHeaderBoundTest(unittest.TestCase):
    """CH-58 under FLAG 12: the cure names displaced entry
    heading forms only. The queue header stands as file
    structure under the CH-49 ruling bound and takes no
    Warning and no entry from this cure. The CH-20 and
    CH-49 pins stand in view."""

    def test_tab_queue_header_first_heading_stands_clean(self):
        # The first heading standing as the queue header
        # whatever words it carries, in its tab separated
        # form: no PIN-06 Warning, no entry, exit 0.
        data = ("#\tDecision queue\n\n" +
                _open_entry("### DQ-001: Alpha", "Open",
                            "DQ-002") +
                _open_entry("### DQ-002: Beta question", "Open",
                            "DQ-001"))
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix4_k9_tab_header.md")
        self.assertEqual(_pin06(output), [])
        self.assertEqual(int(h.entry_total(output)), 2)
        code, _out = _cli_validate(data.encode("utf-8"))
        self.assertEqual(code, 0)

    def test_plain_queue_header_stands_clean(self):
        # The CH-49 queue header control, passing before
        # and after.
        data = ("# Decision queue\n\n" +
                _open_entry("### DQ-001: Alpha", "Open",
                            "DQ-002") +
                _open_entry("### DQ-002: Beta question", "Open",
                            "DQ-001"))
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix4_k9_header.md")
        self.assertEqual(_pin06(output), [])
        code, _out = _cli_validate(data.encode("utf-8"))
        self.assertEqual(code, 0)

    def test_level1_space_duplicate_still_takes_pin06(self):
        # The CH-49 pin in view: a numbered entry heading at
        # level 1 in the plain space form takes its PIN-06
        # Warning, before and after this cure.
        parts = ["# Decision queue\n\n"]
        parts.append(_open_entry("# DQ-001: Alpha level one",
                                 "Open", "DQ-002"))
        parts.append(_open_entry("### DQ-001: Alpha", "Open",
                                 "DQ-002"))
        parts.append(_open_entry("### DQ-002: Beta question",
                                 "Open", "DQ-001"))
        _model, output = h.run_pipeline(
            "".join(parts).encode("utf-8"), "fix4_k9_ch49.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha level one",
                      h.finding_statement(found[0]) or "")
        self.assertEqual(int(h.entry_total(output)), 2)

    def test_non_entry_level1_heading_takes_no_pin06(self):
        # FLAG 12 bound, passing before and after: a level 1
        # heading in no entry form stands as file structure
        # with no PIN-06 Warning.
        data = ("# Decision queue\n\n" +
                _open_entry("### DQ-001: Alpha", "Open",
                            "DQ-002") +
                _open_entry("### DQ-002: Beta question", "Open",
                            "DQ-001") +
                "# Appendix notes\n\n"
                "Plain closing prose with no status line.\n")
        _model, output = h.run_pipeline(
            data.encode("utf-8"), "fix4_k9_nonentry.md")
        self.assertEqual(_pin06(output), [])


if __name__ == "__main__":
    unittest.main()
