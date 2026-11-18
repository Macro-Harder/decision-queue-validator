"""Step 17 fix wave 6, Fix Seat K2 tests, test first.

Charges CH-95, CH-96, and CH-100, as ruled at section 58
of design/steps/step-17r-record.md, ruling (e) of that
section for CH-96, and prepared at
design/steps/step-17r-triage6-prep.md.

CH-95 (parse, the final line cut off rule, round 6 limbs
past CH-81): the seven Low findings of round 6 attack
seat 2 at design/steps/step-17r-attack6-2.md (ATK6-2-01
to ATK6-2-07). One rule at seven limbs: a trailing run
character of the ruling (a) ground of section 52 standing
after a structural closing mark, and after sentence
closing punctuation in the prose branch; a final line
standing inside an HTML comment, read as comment matter
as the fence content limb reads fence matter; a valueless
labelled final line whose only value matter is a run
character, standing as no value for the CH-81 limb 6
reading; a final Blocks line whose value carries two part
boundaries standing adjacent, the empty part between two
boundaries standing as the field reading takes it; bullet
items under the parenthesised marker (1) and the bracket
marker 1] standing whole in item form under the standing
guards; a dash setext underline standing in underline
position and an underscore thematic break standing whole
in their own closing forms. The cut side of each newly
reached form is stated test first in its class. The
characters read are the run ground of section 52 ruling
(a): a character presenting no visible glyph, the
categories Cn, Co, Cf, Cc (the governed terminators
excepted), Zs, Zl, Zp, Mn, Mc, and Me, together with any
character, in any category, whose Unicode name carries
BLANK, FILLER, FILL, or REPLACEMENT.

CH-96 (parse, the joined line heading selection at the
tail scan): Finding A6-3-F1 (High) of round 6 attack
seat 3 at design/steps/step-17r-attack6-3.md. A second
entry heading standing inside a joined line, behind a
separator character (U+2028) or a lone carriage return,
is selected by nothing in the CH-78 tail scan, which
selects a split part only where it opens with a marker,
a variant marker, or a near marker, and the entry is
deleted from every count, at a clean exit 0 in the
identical twin forms. Cure bound, under ruling (e) of
section 58: the cure stands at the tail scan selection
in parse_queue; a split part opening with an entry
heading is signalled at file level in the README form,
the unmatched heading Warning naming the heading as
written, at either charged join character; the brief
partition rule at _partition_lines stands unmoved and
every CH-78 pin stands whole.

CH-100 (parse, the heading separator empty text form):
Finding 1 (Low) of round 6 attack seat 6 at
design/steps/step-17r-attack6-6.md. A heading line whose
hashes stand separated from an empty text by a separator
character of the ruling (a) ground is no heading at all
to the reader and is named on no surface, where the
identical line separated by a plain space takes the
unmatched heading Warning. Cure bound: the separator
heading reading at _separator_heading_info takes the
empty text form, so the line takes the same unmatched
heading treatment the plain space form takes, naming the
heading as written; the no heading side stands stated
and tested in this file, as CH-80 stated it: a separator
character outside the ruling (a) ground makes no heading,
and bare hashes with no separator at all make no heading.

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


def _pin06(output):
    return [f for f in h.findings_of(output)
            if str(h.get(f, "rule_id")) == "PIN-06"]


def _cli_validate(data):
    path = h.temp_input(data)
    code, out, _err = h.run_cli("validate", path)
    return code, out.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------
# CH-95, limb 1: a trailing run character after a structural
# closing mark (ATK6-2-01)
# ---------------------------------------------------------------------

class Step17Fix6K2StructuralTrailingRunTest(unittest.TestCase):
    """CH-95, ATK6-2-01: the structural branches of the
    final line rule disregard a trailing run of the ruling
    (a) ground classes after the closing mark, as the
    labelled branches do. The cut side is stated first: a
    line cut inside its closing mark stands cut."""

    def test_cut_inside_closing_mark_stands_cut(self):
        for final_line in (
                "<!-- Standing note closed here --\u200b",
                "| DQ-002 | None\u200b",
                "Standing note\n== =\u200b"):
            with self.subTest(final_line=repr(final_line)):
                _assert_cut(self, _file(final_line),
                            "fix6_k2_struct_cut.md")

    def test_comment_trailing_run_stands_whole(self):
        for char in ("\u200b", "\u0301", "\u2060"):
            with self.subTest(char=repr(char)):
                _assert_whole(
                    self,
                    _file("<!-- Standing note closed here -->"
                          + char),
                    "fix6_k2_comment_trail.md")

    def test_table_trailing_run_stands_whole(self):
        _assert_whole(self, _file("| DQ-002 | None |\u200b"),
                      "fix6_k2_table_trail.md")

    def test_setext_trailing_run_stands_whole(self):
        _assert_whole(self, _file("Standing note\n===\u200b"),
                      "fix6_k2_setext_trail.md")


class Step17Fix6K2ProseTrailingRunTest(unittest.TestCase):
    """CH-95, ATK6-2-02: the prose branch disregards a
    trailing run of the ground classes standing after the
    sentence closing punctuation, before its sentence
    close test. The no break space control stands parsed
    whole in both eras, covered by the plain strip."""

    def test_prose_sentence_trailing_run_stands_whole(self):
        for char in ("\u200b", "\u0301", "\u2060"):
            with self.subTest(char=repr(char)):
                _assert_whole(
                    self,
                    _file("Work stays blocked until the ruling "
                          "lands." + char),
                    "fix6_k2_prose_trail.md")

    def test_prose_sentence_nbsp_control_pin_stands_whole(self):
        _assert_whole(
            self,
            _file("Work stays blocked until the ruling lands.\u00a0"),
            "fix6_k2_prose_nbsp.md")

    def test_prose_trailing_run_no_sentence_close_cut(self):
        # Cut side: a trailing run character rescues no line
        # that closes no sentence.
        _assert_cut(
            self,
            _file("Work stays blocked until the ruling\u200b"),
            "fix6_k2_prose_trail_cut.md")


class Step17Fix6K2CommentContainerTest(unittest.TestCase):
    """CH-95, ATK6-2-03: the final line test reads a line
    standing inside an HTML comment container as comment
    matter, as the parser reads it on every other line,
    on the posture of the CH-81 limb 2 fence content limb."""

    def test_comment_content_final_line_stands_whole(self):
        _assert_whole(
            self,
            _plain_file("<!--\nStanding note inside the comment"),
            "fix6_k2_comment_content.md")

    def test_comment_closing_final_line_stands_whole(self):
        _assert_whole(
            self,
            _plain_file("<!--\nStanding note opens here\n"
                        "Standing note ends here -->"),
            "fix6_k2_comment_close.md")

    def test_comment_content_sentence_control_pin(self):
        # The paper control, whole in both eras by the prose
        # sentence close alone.
        _assert_whole(
            self,
            _plain_file("<!--\nStanding note inside the comment."),
            "fix6_k2_comment_sentence.md")

    def test_comment_opener_final_line_pin_stands_cut(self):
        # Bound in view, as the fence opener bound stands:
        # an opener standing as the final line itself has no
        # comment open before it and keeps its standing
        # reading.
        _assert_cut(self, _plain_file("<!-- Standing note opens"),
                    "fix6_k2_comment_opener.md")


class Step17Fix6K2ValuelessRunLabelledTest(unittest.TestCase):
    """CH-95, ATK6-2-04: a value carrying nothing but
    characters of the ground classes stands as no value
    for the CH-81 limb 6 reading. The Status member of the
    family stands uncharged, pinned as still cut."""

    def test_blocks_colon_run_only_value_stands_whole(self):
        for final_line in ("Blocks: \u200b", "Blocks: \u0301"):
            with self.subTest(final_line=repr(final_line)):
                _assert_whole(self, _file(final_line),
                              "fix6_k2_blocks_runonly.md")

    def test_ruled_colon_run_only_value_stands_whole(self):
        _assert_whole(self, _file("Ruled: \u200b"),
                      "fix6_k2_ruled_runonly.md")

    def test_valueless_plain_pins_stand_whole(self):
        for final_line in ("Blocks:", "Ruled:"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, _file(final_line),
                              "fix6_k2_valueless_pin.md")

    def test_run_before_cut_reference_stands_cut(self):
        # Cut side: a run character standing before a cut
        # reference is a value, not no value.
        _assert_cut(self, _file("Blocks: \u200bDQ-00"),
                    "fix6_k2_run_cutref.md")

    def test_status_colon_only_pin_stands_cut(self):
        _assert_cut(self, _file("Status:"),
                    "fix6_k2_status_colon.md")


class Step17Fix6K2BlocksAdjacentBoundaryTest(unittest.TestCase):
    """CH-95, ATK6-2-05: the final line Blocks reading and
    the field reading take the same value on the same
    bytes on the adjacent boundary form: the empty part
    between two boundaries stands as the field reading
    takes it. An empty part at any other boundary, a
    trailing joining word among them, still fails."""

    def test_adjacent_boundary_forms_stand_whole(self):
        for final_line in (
                "Blocks: DQ-002,\rDQ-003",
                "Blocks: DQ-002,\r\rDQ-003",
                "Blocks: DQ-002\r\r,DQ-003",
                "Blocks: DQ-002 and\rDQ-003"):
            with self.subTest(final_line=repr(final_line)):
                _assert_whole(self, _file(final_line),
                              "fix6_k2_blocks_adjacent.md")

    def test_single_boundary_pins_stand_whole(self):
        for final_line in (
                "Blocks: DQ-002\rDQ-003",
                "Blocks: DQ-002\r\rDQ-003"):
            with self.subTest(final_line=repr(final_line)):
                _assert_whole(self, _file(final_line),
                              "fix6_k2_blocks_single.md")

    def test_adjacent_boundary_cut_sides_stand_cut(self):
        for final_line in (
                "Blocks: DQ-002 and",
                "Blocks: DQ-002,\rDQ-00",
                "Blocks: DQ-00,\rDQ-003"):
            with self.subTest(final_line=repr(final_line)):
                _assert_cut(self, _file(final_line),
                            "fix6_k2_blocks_adj_cut.md")


class Step17Fix6K2BulletMarkerFormsTest(unittest.TestCase):
    """CH-95, ATK6-2-06: complete bullet items under the
    parenthesised marker (1) and the bracket marker 1]
    stand whole in item form, under the standing fragment,
    joining word, and cut reference guards. The cut side
    is stated first for each newly reached marker."""

    def test_cut_items_under_new_markers_stand_cut(self):
        for final_line in (
                "(1) Option B: leave the note unadop",
                "(1) Option A, Option B and",
                "1] Option B: leave the note unadop",
                "1] See DQ-00"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix6_k2_bullet_new_cut.md")

    def test_paren_both_marker_item_stands_whole(self):
        _assert_whole(
            self, _file("(1) Option B: leave the note adopted"),
            "fix6_k2_bullet_paren_both.md")

    def test_bracket_marker_item_stands_whole(self):
        _assert_whole(
            self, _file("1] Option B: leave the note adopted"),
            "fix6_k2_bullet_bracket.md")

    def test_paren_close_marker_pin_stands_whole(self):
        # The CH-81 limb 3 pin in view, whole in both eras.
        _assert_whole(
            self, _file("1) Option B: leave the note adopted"),
            "fix6_k2_bullet_paren_pin.md")


class Step17Fix6K2SetextDashAndBreakTest(unittest.TestCase):
    """CH-95, ATK6-2-07: the completeness reading reaches
    the dash underline in underline position and the
    underscore thematic break in their own closing forms.
    The cut side is stated test first: a cut underline, a
    dash run standing in break position after a blank
    line, and the star break form stand cut, as round 4
    left the break forms."""

    def test_dash_underline_in_position_stands_whole(self):
        _assert_whole(self, _file("Standing note\n---"),
                      "fix6_k2_setext_dash.md")

    def test_underscore_break_stands_whole(self):
        _assert_whole(self, _file("___"),
                      "fix6_k2_hr_underscore.md")

    def test_cut_underline_stands_cut(self):
        for final_line in ("Standing note\n---x",
                           "Standing note\n___x"):
            with self.subTest(final_line=repr(final_line)):
                _assert_cut(self, _file(final_line),
                            "fix6_k2_underline_cut.md")

    def test_dash_run_after_blank_pin_stands_cut(self):
        # The round 4 form in view (g75): a dash run whose
        # preceding line stands blank is in break position,
        # not underline position, and stands cut in both
        # eras.
        _assert_cut(self, _file("---"), "fix6_k2_hr_dash.md")

    def test_star_run_after_blank_pin_stands_cut(self):
        # The round 4 form in view (g76), uncharged here:
        # the star break stands as round 4 left it.
        _assert_cut(self, _file("***"), "fix6_k2_hr_stars.md")

    def test_short_underscore_run_pin_stands_cut(self):
        # Bound in view: the break form is a run of three
        # or more underscores; two underscores close no
        # sentence and stand cut in both eras.
        _assert_cut(self, _file("__"), "fix6_k2_hr_short.md")


# ---------------------------------------------------------------------
# CH-96: a split part opening with an entry heading takes the
# file level signal (A6-3-F1)
# ---------------------------------------------------------------------

_BASE_HEAD = "# Decision queue\n\n"
_ENTRY_ONE = ("### DQ-001: A sample open question\n\n"
              "Status: Banked\n\n"
              "Question: Which option should we take?\n\n"
              "Options: Option A, Option B\n\n"
              "Cost of deciding late: Work stays blocked.\n\n"
              "Blocks: DQ-002\n\n"
              "This question is waiting for a decision.\n")
_SECOND_BODY_DIFFERING = (
    "\n\nStatus: Ruled\n\n"
    "Question: Which other option should we take?\n\n"
    "Options: Option C, Option D\n\n"
    "Cost of deciding late: More work stays blocked.\n\n"
    "Blocks: DQ-001\n\n"
    "This question is also waiting for a decision.\n")
_SECOND_BODY_TWIN = (
    "\n\nStatus: Banked\n\n"
    "Question: Which option should we take?\n\n"
    "Options: Option A, Option B\n\n"
    "Cost of deciding late: Work stays blocked.\n\n"
    "Blocks: DQ-002\n\n"
    "This question is waiting for a decision.\n")


def _heading_join_file(joiner, second_title, second_body):
    body = _BASE_HEAD
    body += "### DQ-001: A sample open question" + joiner
    body += "### DQ-002: " + second_title + "\n"
    body += "\nStatus: Banked\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision."
    body += second_body
    return body.encode("utf-8")


def _status_join_file(joiner, second_title, second_body):
    body = _BASE_HEAD
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked" + joiner
    body += "### DQ-002: " + second_title + "\n"
    body += second_body
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n"
    return body.encode("utf-8")


def _assert_heading_signalled(test, data, name, heading_text):
    _model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(_model))
    found = _pin06(output)
    test.assertEqual(len(found), 1)
    test.assertIn(heading_text,
                  h.finding_statement(found[0]) or "")
    test.assertIn("matches no recognised heading form",
                  h.finding_statement(found[0]) or "")
    test.assertEqual(int(h.entry_total(output)), 1)


class Step17Fix6K2JoinedHeadingSignalTest(unittest.TestCase):
    """CH-96, A6-3-F1: a split part opening with an entry
    heading, at either charged join character, takes the
    file level unmatched heading Warning in the README
    form, naming the heading as written, and no second
    entry stands deleted from every count in silence. The
    signal form is the cure form ruling (e) allows beside
    recognition: no entry is raised for the joined
    heading, and its standing in the count is unchanged."""

    def test_heading_join_line_separator_differing(self):
        data = _heading_join_file(
            "\u2028", "Second question", _SECOND_BODY_DIFFERING)
        _assert_heading_signalled(
            self, data, "fix6_k2_join_ls_diff.md",
            "DQ-002: Second question")

    def test_heading_join_carriage_return_differing(self):
        data = _heading_join_file(
            "\r", "Second question", _SECOND_BODY_DIFFERING)
        _assert_heading_signalled(
            self, data, "fix6_k2_join_cr_diff.md",
            "DQ-002: Second question")

    def test_heading_join_line_separator_twin(self):
        data = _heading_join_file(
            "\u2028", "A sample open question", _SECOND_BODY_TWIN)
        _assert_heading_signalled(
            self, data, "fix6_k2_join_ls_twin.md",
            "DQ-002: A sample open question")
        code, _out = _cli_validate(data)
        self.assertEqual(code, 1)

    def test_heading_join_carriage_return_twin(self):
        data = _heading_join_file(
            "\r", "A sample open question", _SECOND_BODY_TWIN)
        _assert_heading_signalled(
            self, data, "fix6_k2_join_cr_twin.md",
            "DQ-002: A sample open question")
        code, _out = _cli_validate(data)
        self.assertEqual(code, 1)

    def test_status_join_line_separator_differing(self):
        data = _status_join_file(
            "\u2028", "Second question", _SECOND_BODY_DIFFERING)
        _assert_heading_signalled(
            self, data, "fix6_k2_sjoin_ls_diff.md",
            "DQ-002: Second question")

    def test_status_join_line_separator_twin(self):
        data = _status_join_file(
            "\u2028", "A sample open question", _SECOND_BODY_TWIN)
        _assert_heading_signalled(
            self, data, "fix6_k2_sjoin_ls_twin.md",
            "DQ-002: A sample open question")
        code, _out = _cli_validate(data)
        self.assertEqual(code, 1)

    def test_status_join_carriage_return_twin(self):
        data = _status_join_file(
            "\r", "A sample open question", _SECOND_BODY_TWIN)
        _assert_heading_signalled(
            self, data, "fix6_k2_sjoin_cr_twin.md",
            "DQ-002: A sample open question")
        code, _out = _cli_validate(data)
        self.assertEqual(code, 1)

    def test_heading_status_heading_one_line_twin(self):
        # The q54 form: one joined line carrying the first
        # heading, its Status line, and the second heading.
        # The Status part keeps its CH-78 counting and the
        # heading part takes its signal.
        body = _BASE_HEAD
        body += ("### DQ-001: A sample open question\u2028"
                 "Status: Banked\u2028"
                 "### DQ-002: A sample open question\n\n")
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This question is waiting for a decision."
        body += _SECOND_BODY_TWIN
        data = body.encode("utf-8")
        _model, output = h.run_pipeline(
            data, "fix6_k2_join_multi.md")
        self.assertFalse(h.is_failure_result(_model))
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-002: A sample open question",
                      h.finding_statement(found[0]) or "")
        entry = h.entry_by_id(_model, "DQ-001")
        kinds = [h.text_of(h.get(el, "kind", "element_kind"))
                 or "" for el in h.as_list(
                     h.get(entry, "status_elements",
                           "elements"))]
        self.assertIn("line start Status line", kinds)


class Step17Fix6K2JoinedHeadingPinTest(unittest.TestCase):
    """CH-96 governing pins: the CH-78 selection stands
    whole. A split part opening with a marker is selected
    and counted exactly as before, and a split part
    opening with no heading form takes no signal."""

    def test_ch78_status_join_counted_no_signal(self):
        for joiner in ("\u2028", "\r"):
            with self.subTest(joiner=repr(joiner)):
                body = h._header_block()
                body += ("### DQ-001: A sample open question"
                         + joiner + "Status: Banked\n\n")
                body += "Question: Which option should we take?\n\n"
                body += "Options: Option A, Option B\n\n"
                body += ("Cost of deciding late: Work stays "
                         "blocked.\n\n")
                body += "Blocks: DQ-002\n\n"
                body += "This question is waiting for a decision.\n"
                model, output = h.run_pipeline(
                    body.encode("utf-8"), "fix6_k2_ch78_pin.md")
                self.assertFalse(h.is_failure_result(model))
                entry = h.entry_by_id(model, "DQ-001")
                kinds = [
                    h.text_of(h.get(el, "kind", "element_kind"))
                    or "" for el in h.as_list(
                        h.get(entry, "status_elements",
                              "elements"))]
                self.assertIn("line start Status line", kinds)
                self.assertEqual(_pin06(output), [])

    def test_separator_trailing_heading_pin_no_signal(self):
        # The CH-78 held form: a separator trailing on the
        # heading line, the Status line on its own line,
        # changes nothing and takes no signal.
        body = h._header_block()
        body += "### DQ-001: A sample open question\u2028\n\n"
        body += "Status: Banked\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n"
        model, output = h.run_pipeline(
            body.encode("utf-8"), "fix6_k2_ch78_trail_pin.md")
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-001")
        kinds = [h.text_of(h.get(el, "kind", "element_kind"))
                 or "" for el in h.as_list(
                     h.get(entry, "status_elements",
                           "elements"))]
        self.assertIn("line start Status line", kinds)
        self.assertEqual(_pin06(output), [])

    def test_non_entry_heading_part_takes_no_signal(self):
        # Bound in view: a split part opening with a heading
        # in no entry form is not an entry heading part; it
        # takes no signal and the heading reading stands as
        # it stood.
        body = h._header_block()
        body += ("### DQ-001: A sample open question\u2028"
                 "## Notes on the queue\n\n")
        body += "Status: Banked\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This question is waiting for a decision.\n"
        model, output = h.run_pipeline(
            body.encode("utf-8"), "fix6_k2_join_nonentry.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-001"))
        self.assertEqual(_pin06(output), [])

    def test_prose_part_takes_no_signal(self):
        body = h._header_block()
        body += ("### DQ-001: A sample open question\u2028"
                 "Standing note follows\n\n")
        body += "Status: Banked\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This question is waiting for a decision.\n"
        model, output = h.run_pipeline(
            body.encode("utf-8"), "fix6_k2_join_prose.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-001"))
        self.assertEqual(_pin06(output), [])


# ---------------------------------------------------------------------
# CH-100: the heading separator empty text form (seat 6 Finding 1)
# ---------------------------------------------------------------------

def _open_entry(heading_line, status, blocks, extra=""):
    return (
        heading_line + "\n\n"
        "Status: " + status + "\n\n"
        "Question: Which option should we take?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked.\n\n"
        "Blocks: " + blocks + "\n\n"
        "This entry is waiting for a decision.\n\n" + extra)


def _empty_heading_file(heading_line):
    parts = ["# Decision queue\n\n"]
    parts.append(_open_entry("### DQ-001: Alpha", "Open",
                             "DQ-002"))
    parts.append(heading_line + "\n\n")
    parts.append(_open_entry("### DQ-002: Beta question",
                             "Open", "DQ-001"))
    return "".join(parts).encode("utf-8")


def _sep_queue(sep_heading, absorbed_status):
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


class Step17Fix6K2SeparatorEmptyTextTest(unittest.TestCase):
    """CH-100, seat 6 Finding 1: a heading line separated
    from an empty text by a separator character of the
    ruling (a) ground takes the same unmatched heading
    treatment the plain space form takes, naming the
    heading as written. The no heading side stands stated
    and tested below, as CH-80 stated it."""

    def test_separator_empty_heading_takes_pin06(self):
        for sep in ("\u00a0", "\t", "\u00a0 "):
            with self.subTest(sep=repr(sep)):
                data = _empty_heading_file("###" + sep)
                _model, output = h.run_pipeline(
                    data, "fix6_k2_sep_empty.md")
                found = _pin06(output)
                self.assertEqual(len(found), 1)
                self.assertIn(
                    "matches no recognised heading form",
                    h.finding_statement(found[0]) or "")
                self.assertEqual(int(h.entry_total(output)), 2)
                code, _out = _cli_validate(data)
                self.assertEqual(code, 1)

    def test_plain_space_empty_heading_pin_takes_pin06(self):
        # The controls in view (s93 and s98), taking their
        # Warning in both eras.
        for line in ("### ", "### \t"):
            with self.subTest(line=repr(line)):
                data = _empty_heading_file(line)
                _model, output = h.run_pipeline(
                    data, "fix6_k2_space_empty.md")
                found = _pin06(output)
                self.assertEqual(len(found), 1)
                self.assertIn(
                    "matches no recognised heading form",
                    h.finding_statement(found[0]) or "")
                self.assertEqual(int(h.entry_total(output)), 2)

    def test_bare_hashes_pin_makes_no_heading(self):
        # The s94 control in view: hashes with no separator
        # character at all are no heading in both eras, at
        # exit 0 in silence.
        data = _empty_heading_file("###")
        _model, output = h.run_pipeline(
            data, "fix6_k2_bare_hashes.md")
        self.assertEqual(_pin06(output), [])
        self.assertEqual(int(h.entry_total(output)), 2)
        code, _out = _cli_validate(data)
        self.assertEqual(code, 0)

    def test_no_heading_side_visible_separator(self):
        # The no heading side, as CH-80 stated it: a
        # separator character outside the ruling (a) ground,
        # a visible character among them, makes no heading,
        # with an empty text as with a carried text.
        for line in ("###.", "###x"):
            with self.subTest(line=line):
                data = _empty_heading_file(line)
                _model, output = h.run_pipeline(
                    data, "fix6_k2_sep_visible.md")
                self.assertEqual(_pin06(output), [])
                self.assertEqual(int(h.entry_total(output)), 2)

    def test_separator_heading_with_text_pin_stands_whole(self):
        # The CH-80 pin in view, passing before and after:
        # a separator separated heading carrying its text
        # takes its Warning naming the heading as written.
        data = _sep_queue("###\u00a0DQ-001: Alpha tab", "Open")
        _model, output = h.run_pipeline(
            data, "fix6_k2_sep_text_pin.md")
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha tab",
                      h.finding_statement(found[0]) or "")
        self.assertEqual(int(h.entry_total(output)), 2)


if __name__ == "__main__":
    unittest.main()
