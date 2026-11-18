"""Step 17 fix wave 7, Fix Seat K1 tests, test first.

Charges CH-114 and CH-115, as ruled at section 66 of
design/steps/step-17r-record.md, with the CH-96 scan scope
stated once for both charges at ruling (b) of that
section, and prepared at design/steps/step-17r-triage7-prep.md.

CH-114 (parse, the CH-96 split scan, the recognised
heading limb): seat 1 finding F-7-1-1 (Medium) at
design/steps/step-17r-attack7-1.md and seat 3 finding
A7-3-F1 (Medium) at design/steps/step-17r-attack7-3.md,
one mechanism, one charge. The CH-96 scan splits every
partitioned line on the CH-78 join set and reads each
later part with the heading readers; the heading readers
absorb a leading run, so where a join character stands
inside the leading run of a heading line itself, the part
behind it is the line own heading, already recognised and
raised by the main reading, and the scan signals it a
second time as an unmatched heading. Cure bound, under
ruling (b) of section 66: the scan's ground is a heading
that stands in heading position and is not recognised;
where the line's own heading is recognised and raised,
the scan does not fire, and the charged twin forms of
CH-96 stand whole under their pins in both directions.

CH-115 (parse, the CH-96 split scan, the inert matter
and heading title limb): seat 3 finding A7-3-F2 (Medium).
The scan loops over every partitioned line as written,
with no exclusion for the lines the rest of the parse
blanks as inert, and no exclusion for heading title
matter, so it fires on heading shaped parts standing
inside a fenced code block or an HTML comment, and on
heading shaped text standing inside the title of a
recognised first or second entry heading, where no entry
is lost at all. Cure bound, under the same ruling (b):
where the matter stands inert or inside a recognised
heading's title, the scan does not fire. The title side
is read on the lost entry ground of the CH-96 cure
itself: a heading part standing in a joined line takes
its signal where a second entry body stands in the file
behind the heading line, the deletion the signal names;
heading shaped matter inside a recognised heading's
title with no entry body standing behind it is title
matter and takes no signal. Seat 3 observation O-3, the
heading fragment inside body prose, stands as a design
question under ruling (c) of section 66, no cure charged
on it: its behaviour stands unchanged and is pinned here
in that posture.

Constructions stand in the attack papers own shapes: the
one entry base and the two entry control of round 7
attack seat 3, the twin and differing second bodies of
the fix wave 6 seat K2 pins, and the probe forms of
round 7 attack seat 1.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

LS = " "
PS = " "
NEL = ""
VT = "\x0b"
FF = "\x0c"
CR = "\r"
BOM = "﻿"
LRM = "‎"

_HEAD = "# Decision queue\n\n"
_BODY_ONE = ("Status: Banked\n\n"
             "Question: Which option should we take?\n\n"
             "Options: Option A, Option B\n\n"
             "Cost of deciding late: Work stays blocked.\n\n"
             "Blocks: DQ-002\n\n"
             "This question is waiting for a decision.\n")
BASE = (_HEAD + "### DQ-001: A sample open question\n\n"
        + _BODY_ONE)
TWO = (_HEAD + "### DQ-001: First question\n\n"
       "Status: Banked\n\n"
       "Question: Which option should we take?\n\n"
       "Options: Option A, Option B\n\n"
       "Cost of deciding late: Work stays blocked.\n\n"
       "Blocks: DQ-002\n\n"
       "This question is waiting for a decision.\n\n"
       "### DQ-002: Second question\n\n"
       "Status: Banked\n\n"
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
_SECOND_BODY_DIFFERING = (
    "\n\nStatus: Ruled\n\n"
    "Question: Which other option should we take?\n\n"
    "Options: Option C, Option D\n\n"
    "Cost of deciding late: More work stays blocked.\n\n"
    "Blocks: DQ-001\n\n"
    "This question is also waiting for a decision.\n")


def _pin06(output):
    return [f for f in h.findings_of(output)
            if str(h.get(f, "rule_id")) == "PIN-06"]


def _cli_validate(data):
    path = h.temp_input(data)
    code, out, _err = h.run_cli("validate", path)
    return code, out.decode("utf-8", errors="replace")


def _assert_no_signal(test, data, name, entries):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    test.assertEqual(_pin06(output), [])
    test.assertEqual(int(h.entry_total(output)), entries)


def _assert_signalled(test, data, name, heading_text, count=1):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    found = _pin06(output)
    test.assertEqual(len(found), count)
    test.assertIn(heading_text,
                  h.finding_statement(found[0]) or "")
    test.assertIn("matches no recognised heading form",
                  h.finding_statement(found[0]) or "")


def _heading_join_file(joiner, second_title, second_body):
    body = _HEAD
    body += "### DQ-001: A sample open question" + joiner
    body += "### DQ-002: " + second_title + "\n"
    body += "\n" + _BODY_ONE.rstrip("\n")
    body += second_body
    return body.encode("utf-8")


# ---------------------------------------------------------------------
# CH-114: a join character in the leading run of a heading
# line; the part behind it is the line own heading,
# recognised and raised, and takes no signal
# ---------------------------------------------------------------------

class Step17Fix7K1RecognisedHeadingTest(unittest.TestCase):
    """CH-114, F-7-1-1 and A7-3-F1: the scan does not fire
    on a line whose own heading is recognised and raised,
    where a join character stands in its leading run."""

    def test_leading_join_before_first_heading_no_signal(self):
        # Seat 1 probes p1, p2, p3: a line separator, a
        # next line character, or a paragraph separator at
        # the start of the entry heading line; the entry
        # stands counted in full and no signal stands.
        for joiner in (LS, NEL, PS):
            with self.subTest(joiner=repr(joiner)):
                data = BASE.replace(
                    "### DQ-001", joiner + "### DQ-001"
                    ).encode("utf-8")
                _assert_no_signal(
                    self, data, "fix7_k1_lead_first.md", 1)
                code, _out = _cli_validate(data)
                self.assertEqual(code, 0)

    def test_leading_join_before_second_heading_no_signal(self):
        # Seat 3 fresh instances r10 to r14: a vertical
        # tab, a paragraph separator, a line separator, a
        # next line character, or a form feed before the
        # second entry heading; headed entries 2 of 2.
        for joiner in (VT, PS, LS, NEL, FF):
            with self.subTest(joiner=repr(joiner)):
                data = TWO.replace(
                    "### DQ-002", joiner + "### DQ-002"
                    ).encode("utf-8")
                _assert_no_signal(
                    self, data, "fix7_k1_lead_second.md", 2)
                code, _out = _cli_validate(data)
                self.assertEqual(code, 0)

    def test_leading_run_sandwich_forms_no_signal(self):
        # Seat 3 instances r16 and r19, and verification
        # case m30: a run carrying a join character (byte
        # order mark, join, byte order mark; left to right
        # mark and vertical tab) before the second entry
        # heading; the run is the heading leading run and
        # the heading behind it is the line own heading.
        for run in (BOM + LS + BOM, LRM + VT):
            with self.subTest(run=repr(run)):
                data = TWO.replace(
                    "### DQ-002", run + "### DQ-002"
                    ).encode("utf-8")
                _assert_no_signal(
                    self, data, "fix7_k1_lead_run.md", 2)

    def test_leading_join_open_entry_no_signal(self):
        # Seat 1 fixture e10 and probe p10: a line
        # separator at the start of an Open entry heading
        # line; the entry stands in full with its field
        # findings and no unmatched heading signal stands
        # beside them.
        body = _HEAD
        body += LS + "### DQ-001: A sample open question\n\n"
        body += "Status: Open\n\n"
        body += "This question is waiting for a decision.\n"
        data = body.encode("utf-8")
        model, output = h.run_pipeline(
            data, "fix7_k1_lead_open.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_pin06(output), [])
        self.assertEqual(int(h.entry_total(output)), 1)


# ---------------------------------------------------------------------
# CH-115, inert limb: heading shaped parts standing in
# inert matter take no signal
# ---------------------------------------------------------------------

class Step17Fix7K1InertMatterTest(unittest.TestCase):
    """CH-115, A7-3-F2 inert limb: the scan reads the
    lines as the rest of the parse reads them, with inert
    container matter blanked, so a heading shaped part
    standing inside a fence or a comment is no heading at
    all to the scan."""

    def test_fence_joined_heading_no_signal(self):
        # Seat 3 instance r20: a fenced code block inside
        # the entry carrying example text joined by one
        # line separator to a heading shaped text.
        data = BASE.replace(
            "This question is waiting for a decision.\n",
            "Example:\n\n```\ntext" + LS +
            "### DQ-002: Example heading\n```\n\n"
            "This question is waiting for a decision.\n"
            ).encode("utf-8")
        _assert_no_signal(self, data, "fix7_k1_fence.md", 1)

    def test_comment_joined_heading_no_signal(self):
        # Seat 3 instance r21: the same joined text inside
        # an HTML comment.
        data = BASE.replace(
            "This question is waiting for a decision.\n",
            "<!-- text" + LS +
            "### DQ-002: Example heading -->\n\n"
            "This question is waiting for a decision.\n"
            ).encode("utf-8")
        _assert_no_signal(self, data, "fix7_k1_comment.md", 1)


# ---------------------------------------------------------------------
# CH-115, title limb: heading shaped text standing inside
# a recognised heading's title, with no entry body
# standing behind it, takes no signal
# ---------------------------------------------------------------------

class Step17Fix7K1HeadingTitleTest(unittest.TestCase):
    """CH-115, A7-3-F2 title limb: a heading shaped part
    standing inside the title of a recognised entry
    heading, where no second entry body stands in the
    file, is title matter of that heading, not a second
    heading standing in a joined line."""

    def test_title_join_first_heading_no_signal(self):
        # Seat 3 instance r23: the first entry heading
        # whose own title carries one line separator and
        # then a heading shaped text.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix7_k1_title1.md", 1)
        code, _out = _cli_validate(data)
        self.assertEqual(code, 0)

    def test_title_join_second_heading_no_signal(self):
        # Seat 3 instance r24: the second entry heading of
        # the two entry control whose title carries the
        # same joined fake heading text; headed entries
        # 2 of 2 at the control reading.
        data = TWO.replace(
            "### DQ-002: Second question",
            "### DQ-002: Second" + LS +
            "### DQ-003: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix7_k1_title2.md", 2)
        code, _out = _cli_validate(data)
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------
# The charged twin forms of CH-96 stand whole under their
# pins in both directions (ruling (b) of section 66)
# ---------------------------------------------------------------------

class Step17Fix7K1JoinedHeadingPinTest(unittest.TestCase):
    """The CH-96 signal stands exactly where its charge
    places it: a second entry heading standing in a joined
    line, its entry body standing in the file behind it,
    takes the file level unmatched heading Warning, and no
    entry is raised for it."""

    def test_heading_join_twin_still_signalled(self):
        for joiner in (LS, CR):
            with self.subTest(joiner=repr(joiner)):
                data = _heading_join_file(
                    joiner, "A sample open question",
                    _SECOND_BODY_TWIN)
                _assert_signalled(
                    self, data, "fix7_k1_join_twin.md",
                    "DQ-002: A sample open question")
                self.assertEqual(
                    int(h.entry_total(
                        h.run_pipeline(data, "x.md")[1])), 1)
                code, _out = _cli_validate(data)
                self.assertEqual(code, 1)

    def test_heading_join_differing_still_signalled(self):
        data = _heading_join_file(
            LS, "Second question", _SECOND_BODY_DIFFERING)
        _assert_signalled(
            self, data, "fix7_k1_join_diff.md",
            "DQ-002: Second question")

    def test_status_join_twin_still_signalled(self):
        # The q53 form: the second heading joined to the
        # first entry Status line.
        body = _HEAD
        body += "### DQ-001: A sample open question\n\n"
        body += "Status: Banked" + LS
        body += "### DQ-002: A sample open question\n"
        body += _SECOND_BODY_TWIN
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This question is waiting for a decision.\n"
        data = body.encode("utf-8")
        _assert_signalled(
            self, data, "fix7_k1_sjoin_twin.md",
            "DQ-002: A sample open question")

    def test_heading_status_heading_one_line_still_signalled(self):
        # The q54 form: one joined line carrying the first
        # heading, its Status line, and the second heading;
        # the Status part keeps its CH-78 counting and the
        # heading part takes its signal.
        body = _HEAD
        body += ("### DQ-001: A sample open question" + LS +
                 "Status: Banked" + LS +
                 "### DQ-002: A sample open question\n\n")
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This question is waiting for a decision."
        body += _SECOND_BODY_TWIN
        data = body.encode("utf-8")
        model, output = h.run_pipeline(
            data, "fix7_k1_join_multi.md")
        self.assertFalse(h.is_failure_result(model))
        found = _pin06(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-002: A sample open question",
                      h.finding_statement(found[0]) or "")
        entry = h.entry_by_id(model, "DQ-001")
        kinds = [h.text_of(h.get(el, "kind", "element_kind"))
                 or "" for el in h.as_list(
                     h.get(entry, "status_elements",
                           "elements"))]
        self.assertIn("line start Status line", kinds)

    def test_two_joined_headings_still_two_signals(self):
        # Seat 3 instance r40: one line carrying two joined
        # headings behind the first, each taking its own
        # signal, the second entry body standing behind.
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question" + LS +
            "### DQ-003: A sample open question\n"
            ).encode("utf-8") + _SECOND_BODY_TWIN.encode("utf-8")
        model, output = h.run_pipeline(
            data, "fix7_k1_join_two.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(len(_pin06(output)), 2)

    def test_joined_part_forms_still_signalled(self):
        # Seat 3 held forms r35, r36, r37, r42, r50: a
        # joined part behind one unassigned character
        # before its hashes, a tab separated part, a level
        # 2 part, a part behind one plain space, and the
        # named unnumbered entry form as a joined part,
        # each in twin form with the second body standing.
        parts = {
            "run prefix": "\u0378### DQ-002: A sample open question",
            "tab separated": "###\tDQ-002: A sample open question",
            "level 2": "## DQ-002: A sample open question",
            "space prefix": " ### DQ-002: A sample open question",
            "unnumbered": "### R-7 closure conflict",
        }
        for label, part in parts.items():
            with self.subTest(form=label):
                data = BASE.replace(
                    "### DQ-001: A sample open question\n",
                    "### DQ-001: A sample open question" + LS +
                    part + "\n").encode(
                        "utf-8") + _SECOND_BODY_TWIN.encode(
                            "utf-8")
                model, output = h.run_pipeline(
                    data, "fix7_k1_part_form.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertEqual(len(_pin06(output)), 1)

    def test_prose_joined_heading_still_signalled(self):
        # Seat 3 observation O-3, a design question under
        # ruling (c) of section 66, no cure charged: a body
        # prose line carrying a join and a heading shaped
        # part keeps the behaviour it stands at, pinned
        # here in that posture and decided nowhere.
        data = BASE.replace(
            "This question is waiting for a decision.\n",
            "See the example" + LS +
            "### DQ-002: Example heading\n\n"
            "This question is waiting for a decision.\n"
            ).encode("utf-8")
        _assert_signalled(
            self, data, "fix7_k1_prose.md",
            "DQ-002: Example heading")

    def test_non_entry_part_and_prose_part_pins_stand(self):
        # The fix wave 6 pins beside the charge: a split
        # part opening with a heading in no entry form, and
        # a prose part, each take no signal.
        for tail in ("## Notes on the queue",
                     "Standing note follows"):
            with self.subTest(tail=tail):
                body = _HEAD
                body += ("### DQ-001: A sample open question"
                         + LS + tail + "\n\n")
                body += _BODY_ONE
                data = body.encode("utf-8")
                _assert_no_signal(
                    self, data, "fix7_k1_part_pin.md", 1)

    def test_separator_trailing_heading_pin_stands(self):
        # The CH-78 held form: a separator trailing on the
        # heading line, the Status line on its own line,
        # changes nothing and takes no signal.
        body = _HEAD
        body += "### DQ-001: A sample open question" + LS + "\n\n"
        body += _BODY_ONE
        data = body.encode("utf-8")
        _assert_no_signal(
            self, data, "fix7_k1_trail_pin.md", 1)


if __name__ == "__main__":
    unittest.main()
