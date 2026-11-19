"""Step 17 fix wave 8, Fix Seat K3 tests, test first.

Charges CH-156 and CH-157, as ruled at section 77 of
design/steps/step-17r-record.md, against round 8 attack
seat 3 findings A8-3-F1 and A8-3-F2 (finding T8-06 and
T8-07 in the triage consolidation), paper at
design/steps/step-17r-attack8-3.md. Both charges stand on
the one counting helper of the CH-115 title limb in the
CH-96 split scan, _joined_heading_body_stands in
parse_queue: the helper tested whether a second entry
body stands in the file behind a live entry heading line
by counting Status occurrences in the span running from
that line to the next heading, on the heading line's own
tail parts and on the span's lines, and took the body to
stand at two or more occurrences.

CH-156 (parse, the CH-96 split scan, the title limb
count, genuine joined heading limb): the two occurrence
bound fails in the direction of the original CH-96 harm.
A genuine joined entry heading whose span carries only
one Status occurrence, the one body the joined heading
and its host heading share as the file is written, takes
no signal, and the entry is deleted from every count in
silence, in three instances at a clean exit 0 (attack
cases s01, s03, s04, with s02 and s05 beside them).

CH-157 (parse, the CH-96 split scan, the title limb
count, title tail limb): the count reads the heading
line's own tail parts, so a Status shaped tail standing
inside a heading's own title, behind the heading shaped
part itself, supplies the second occurrence on its own,
and the scan fires on title matter where no second entry
body stands in the file at all, against ruling (b) of
record section 66 (attack cases s10, s11, s13, against
the tail only control s12).

Named neighbour form, under ruling (i) of record
section 77: round 8 seat 3 observation O-3, a joined
heading carrying an unclosed comment opener in its title
(attack case s26, the twin form with two bodies
standing), joins both charges as a named neighbour form
these tests must state, cured or bounded expressly. Its
standing is stated and pinned in the neighbour class
below: the part takes no PIN-06 signal, the file stands
at exit 1 on other findings with headed entries 1, and
no silent deletion is shown, because the comment trouble
the part carries is named by the findings that stand.

The charged twin forms of CH-96 and the ruling (b)
ground of record section 66 stand whole under their pins
in both directions, in the pin class below: the twin and
differing joined headings with two bodies standing take
their signal, the heading Status heading one line form
takes its signal, the round 7 title constructions r23
and r24 take no signal, and the round 8 held form s32
takes no signal.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

LS = " "
PS = " "
VT = "\x0b"

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
_BODY_TWO_DIFF = (
    "Status: Ruled\n\n"
    "Question: Which other option should we take?\n\n"
    "Options: Option C, Option D\n\n"
    "Cost of deciding late: More work stays blocked.\n\n"
    "Blocks: DQ-001\n\n"
    "This question is also waiting for a decision.\n")
_THIRD = ("### DQ-003: Third question\n\n"
          "Status: Banked\n\n"
          "Question: Which third option should we take?\n\n"
          "Options: Option E, Option F\n\n"
          "Cost of deciding late: Even more work stays blocked.\n\n"
          "Blocks: DQ-001\n\n"
          "This question is also waiting for a decision.\n")


def _pin06(output):
    return [f for f in h.findings_of(output)
            if str(h.get(f, "rule_id")) == "PIN-06"]


def _cli(data, subcommand):
    path = h.temp_input(data)
    code, out, _err = h.run_cli(subcommand, path)
    return code, out.decode("utf-8", errors="replace")


def _assert_signalled(test, data, name, heading_text, count=1):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    found = _pin06(output)
    test.assertEqual(len(found), count)
    test.assertIn(heading_text,
                  h.finding_statement(found[0]) or "")
    test.assertIn("matches no recognised heading form",
                  h.finding_statement(found[0]) or "")


def _assert_no_signal(test, data, name, entries):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    test.assertEqual(_pin06(output), [])
    test.assertEqual(int(h.entry_total(output)), entries)


def _twin_single_body():
    return BASE.replace(
        "### DQ-001: A sample open question\n",
        "### DQ-001: A sample open question" + LS +
        "### DQ-002: A sample open question\n").encode("utf-8")


# ---------------------------------------------------------------------
# CH-156: a genuine joined entry heading whose span
# carries only one Status occurrence takes its signal
# ---------------------------------------------------------------------

class Step17Fix8K3GenuineJoinedHeadingTest(unittest.TestCase):
    """CH-156, A8-3-F1: the title limb count takes the
    signal where a genuine joined entry heading stands on
    a live entry heading line and one entry body stands
    in the span behind the heading line, the body the
    joined heading and its host heading share as the file
    is written."""

    def test_s01_twin_single_body_signalled(self):
        # Attack case s01: the first heading joined to a
        # twin second heading, one body following; before
        # the cure headed entries read 1 at a clean exit 0
        # with no signal of any kind.
        data = _twin_single_body()
        _assert_signalled(
            self, data, "fix8_k3_s01.md",
            "DQ-002: A sample open question")
        model, output = h.run_pipeline(data, "fix8_k3_s01.md")
        self.assertEqual(int(h.entry_total(output)), 1)
        for sub in ("validate", "render"):
            code, _out = _cli(data, sub)
            self.assertEqual(code, 1)

    def test_s02_differing_single_body_signalled(self):
        # Attack case s02: the differing form, one body
        # following; before the cure the joined heading
        # took no signal and its body was read as the
        # first entry's body.
        body = _HEAD
        body += ("### DQ-001: First question" + LS +
                 "### DQ-002: Second question\n\n")
        body += _BODY_TWO_DIFF
        data = body.encode("utf-8")
        _assert_signalled(
            self, data, "fix8_k3_s02.md", "DQ-002: Second question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_s03_third_joined_to_second_signalled(self):
        # Attack case s03: the second heading of the two
        # entry control joined to a third heading, the
        # second entry's own body following; before the
        # cure headed entries read 2 at a clean exit 0.
        data = TWO.replace(
            "### DQ-002: Second question\n",
            "### DQ-002: Second question" + LS +
            "### DQ-003: Second question\n").encode("utf-8")
        _assert_signalled(
            self, data, "fix8_k3_s03.md", "DQ-003: Second question")
        model, output = h.run_pipeline(data, "fix8_k3_s03.md")
        self.assertEqual(int(h.entry_total(output)), 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_s04_two_joined_headings_both_signalled(self):
        # Attack case s04: two headings joined to the
        # first on one line, one body following, two
        # headings lost before the cure at a clean exit 0;
        # each joined heading takes its own signal.
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question" + LS +
            "### DQ-003: A sample open question\n").encode("utf-8")
        model, output = h.run_pipeline(data, "fix8_k3_s04.md")
        self.assertFalse(h.is_failure_result(model))
        found = _pin06(output)
        self.assertEqual(len(found), 2)
        statements = [h.finding_statement(f) or "" for f in found]
        self.assertTrue(any("DQ-002" in s for s in statements))
        self.assertTrue(any("DQ-003" in s for s in statements))
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_s05_join_single_body_then_third_entry_signalled(self):
        # Attack case s05: the s01 form with a normal
        # third entry standing later in the file; before
        # the cure the joined DQ-002 was nowhere counted
        # and took no PIN-06 signal.
        data = (_twin_single_body().decode("utf-8") + "\n" +
                _THIRD).encode("utf-8")
        _assert_signalled(
            self, data, "fix8_k3_s05.md",
            "DQ-002: A sample open question")
        model, output = h.run_pipeline(data, "fix8_k3_s05.md")
        self.assertEqual(int(h.entry_total(output)), 2)


# ---------------------------------------------------------------------
# CH-157: a Status shaped tail inside a heading's own
# title supplies no occurrence to the count
# ---------------------------------------------------------------------

class Step17Fix8K3TitleTailTest(unittest.TestCase):
    """CH-157, A8-3-F2: the title limb count reads no
    part of the heading line itself, so a Status shaped
    tail standing inside a recognised heading's title,
    behind the heading shaped part, makes no second
    occurrence, and the scan does not fire on title
    matter where no second entry body stands."""

    def test_s10_marker_tail_in_title_no_signal(self):
        # Attack case s10: the tail part in marker form,
        # the text Status: Banked, inside the title.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry" + LS +
            "Status: Banked").encode("utf-8")
        _assert_no_signal(self, data, "fix8_k3_s10.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_s11_near_marker_tail_in_title_no_signal(self):
        # Attack case s11: the tail part in near marker
        # form, the text Status; Banked, inside the title;
        # the file's Status occurrence total reads 1 and
        # no second entry body stands anywhere in it. The
        # charge is the PIN-06 Warning: no PIN-06 finding
        # stands after the cure. The exit assertion stands
        # narrowed in the open, on the fix wave 7 seat K1
        # narrowing form: the near marker tail part itself
        # takes the near marker report of the CH-78 tail
        # scan, a rule 2 Warning naming the tail line, so
        # the run stands at exit 1 on that finding alone,
        # which is the tail's own correct standing and no
        # part of this charge.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry" + LS +
            "Status; Banked").encode("utf-8")
        _assert_no_signal(self, data, "fix8_k3_s11.md", 1)
        code, out = _cli(data, "validate")
        self.assertEqual(code, 1)
        self.assertNotIn("PIN-06", out)

    def test_s13_variant_tail_in_title_no_signal(self):
        # Attack case s13: the tail part in variant
        # marker form, the text Status unchanged, inside
        # the title.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry" + LS +
            "Status unchanged").encode("utf-8")
        _assert_no_signal(self, data, "fix8_k3_s13.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_s12_tail_only_control_no_signal(self):
        # Attack control s12: the same title construction
        # with the marker tail as the entry's only Status
        # form and no body Status line; no signal stands,
        # as it stood before the cure.
        data = BASE.replace(
            "### DQ-001: A sample open question\n\nStatus: Banked\n",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry" + LS +
            "Status: Banked\n").encode("utf-8")
        _assert_no_signal(self, data, "fix8_k3_s12.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------
# Named neighbour form: ruling (i) of record section 77
# ---------------------------------------------------------------------

class Step17Fix8K3NeighbourFormTest(unittest.TestCase):
    """Seat 3 observation O-3 of round 8, joined to
    CH-156 and CH-157 as a named neighbour form under
    ruling (i) of record section 77, stated and bounded
    expressly here: a joined heading carrying an unclosed
    comment opener in its title (attack case s26, the
    twin form with two bodies standing) takes no PIN-06
    signal. The bound stands in the open: the unclosed
    opener stands inside the joined part's own title, the
    scan reads the line in its inert blanked form under
    the inert limb of CH-115, and the file does not stand
    clean, the comment trouble standing named by the
    findings the run carries at exit 1, with headed
    entries 1; no entry is deleted in silence on this
    form, and no cure is charged on the signal side of
    it in this wave."""

    def test_s26_comment_opener_in_joined_title_bounded(self):
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question <!-- x\n"
            ).encode("utf-8") + _SECOND_BODY_TWIN.encode("utf-8")
        model, output = h.run_pipeline(data, "fix8_k3_s26.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_pin06(output), [])
        self.assertEqual(int(h.entry_total(output)), 1)
        for sub in ("validate", "render"):
            code, _out = _cli(data, sub)
            self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# Governing pins on this surface, in both directions
# ---------------------------------------------------------------------

class Step17Fix8K3PinTest(unittest.TestCase):
    """The charged twin forms of CH-96 stand whole under
    their pins in both directions, and the CH-115 title
    constructions stand at their cured readings, as
    ruling (b) of record section 66 charges."""

    def test_twin_two_bodies_still_signalled(self):
        # Attack control s06 and the fix wave 7 pin form:
        # the twin join with two bodies standing behind
        # the heading line takes its PIN-06 Warning.
        data = _twin_single_body().decode(
            "utf-8") + _SECOND_BODY_TWIN
        data = data.encode("utf-8")
        _assert_signalled(
            self, data, "fix8_k3_s06.md",
            "DQ-002: A sample open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_differing_two_bodies_still_signalled(self):
        body = _HEAD
        body += ("### DQ-001: A sample open question" + LS +
                 "### DQ-002: Second question\n")
        body += "\n" + _BODY_ONE.rstrip("\n")
        body += ("\n\nStatus: Ruled\n\n"
                 "Question: Which other option should we take?\n\n"
                 "Options: Option C, Option D\n\n"
                 "Cost of deciding late: More work stays blocked.\n\n"
                 "Blocks: DQ-001\n\n"
                 "This question is also waiting for a decision.\n")
        data = body.encode("utf-8")
        _assert_signalled(
            self, data, "fix8_k3_diff2.md", "DQ-002: Second question")

    def test_heading_status_heading_one_line_still_signalled(self):
        # The q54 form held at fix wave 7: one joined line
        # carrying the first heading, its Status line, and
        # the second heading; the heading part takes its
        # signal on the body standing behind the line.
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
        _assert_signalled(
            self, data, "fix8_k3_q54.md",
            "DQ-002: A sample open question")

    def test_title_join_first_heading_no_signal(self):
        # Round 7 instance r23, the CH-115 title pin: the
        # first entry heading whose own title carries one
        # line separator and then a heading shaped text.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix8_k3_r23.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_title_join_second_heading_no_signal(self):
        # Round 7 instance r24, the CH-115 title pin: the
        # second entry heading whose title carries the
        # same joined fake heading text.
        data = TWO.replace(
            "### DQ-002: Second question",
            "### DQ-002: Second" + LS +
            "### DQ-003: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix8_k3_r24.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_s32_own_heading_join_title_fake_no_signal(self):
        # Round 8 held form s32: a line carrying its own
        # recognised heading behind a leading join, with a
        # further title fake behind it; headed entries 2
        # of 2 at exit 0 with no signal, as the attack
        # paper records it held.
        data = TWO.replace(
            "### DQ-002: Second question",
            VT + "### DQ-002: Second question" + LS +
            "### DQ-009: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix8_k3_s32.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
