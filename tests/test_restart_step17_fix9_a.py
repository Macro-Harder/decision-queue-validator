"""Step 17 fix wave 9, Cluster A: the title matter test.

Charges CH-191 and CH-192, as ruled at section 81 of
design/steps/step-17r-record.md, against round 9 attack
seat 3 findings A9-3-F1 and A9-3-F2 (findings T9-01 and
T9-02 in the round 9 triage preparation, paper at
design/steps/step-17r-r9-triage-prep.md, Cluster A), paper
at design/steps/step-17r-attack9-3.md. Locus: parse.py,
the CH-96 split scan as narrowed by the fix wave 8 K3
cure (CH-156 and CH-157), the title matter word count
test at its hunk 3, the helper
_joined_part_is_title_matter.

CH-191 (Medium, suppression): the narrowed test reads a
part as title matter wherever the heading segment before
it carries fewer title words than the part, so a genuine
joined entry heading whose title carries more words than
its host segment's title is suppressed beside a standing
body and deleted with no PIN-06 signal, in one instance
at a clean exit 0 (attack cases t01, t02, and t16, with
controls t03 and t07 signalling).

CH-192 (Medium, false fire): the same test reads a
heading shaped part inside a heading's own title as
standing in heading position wherever its title carries
no more words than the segment before it, so the scan
fires on title matter where no entry body stands behind
the part at all (attack cases t04, t06, and t17, with
control t05 standing silent).

Seat 1 cases j09, j10, and j11 (paper at
design/steps/step-17r-attack9-1.md, observation O-9-1-1)
stand as named neighbour forms in the CH-191 class, in
the posture of section 2.2 of the triage preparation:
j09 stands with the CH-191 constructions (a genuine
joined heading behind a one word host title, suppressed
at a clean exit 0 before the cure), and j10 and j11
stand at their signalled readings.

The CH-115 pins the narrowing was landed to hold stand
stated in the pin class: the round 7 title constructions
r23 and r24 take no signal, the round 8 held form s32
takes no signal, the twin and differing joined headings
with two bodies standing take their signal, the heading
Status heading one line form takes its signal, and the
twin single body form s01 takes its signal. The joined
neighbour form of ruling (i) of record section 77, seat
3 observation O-3 (attack case s26, a joined heading
carrying an unclosed comment opener in its title),
stands bounded expressly in the pin class, as the fix
wave 8 K3 module states it. The chain and plain part
held forms of the round 9 seat 3 paper (cases t08 to
t11) stand stated in the held class at their recorded
readings.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

LS = " "

_HEAD = "# Decision queue\n\n"
_BODY_ONE = ("Status: Banked\n\n"
             "Question: Which option should we take?\n\n"
             "Options: Option A, Option B\n\n"
             "Cost of deciding late: Work stays blocked.\n\n"
             "Blocks: DQ-002\n\n"
             "This question is waiting for a decision.\n")
_BODY_THREE = ("Status: Banked\n\n"
               "Question: Which third option should we take?\n\n"
               "Options: Option E, Option F\n\n"
               "Cost of deciding late: Even more work stays blocked.\n\n"
               "Blocks: DQ-001\n\n"
               "This third question is waiting for a decision.\n")
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
_NEAR_BODY = ("Status: BankedX\n\n"
              "This question is waiting for a decision.\n")
_LONG_JOINED = ("### DQ-002: Second question with several "
                "more words in its title")


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


def _joined(first, joined, bodies):
    text = _HEAD + first + LS + joined + "\n\n" + bodies
    return text.encode("utf-8")


# ---------------------------------------------------------------------
# CH-191: a genuine joined entry heading whose title
# carries more words than the heading segment before it
# takes its signal beside a standing body
# ---------------------------------------------------------------------

class Step17Fix9A191SuppressionTest(unittest.TestCase):
    """CH-191, A9-3-F1: the title matter test suppresses
    no genuine joined entry heading on the charged
    constructions, and the controls of the same shape
    stand signalled, as before."""

    def test_t01_genuine_long_title_two_bodies_signalled(self):
        # Attack case t01: the first heading joined to a
        # twin second heading whose title carries nine
        # words against the host segment's two, two bodies
        # standing behind the heading line; before the
        # cure headed entries read 1 with no PIN-06.
        data = _joined("### DQ-001: First question", _LONG_JOINED,
                       _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(
            self, data, "fix9_a_t01.md",
            "DQ-002: Second question with several more "
            "words in its title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_t02_genuine_long_title_one_body_signalled(self):
        # Attack case t02: the same join with one body
        # standing, the body the joined heading and its
        # host heading share; before the cure the run
        # stood at a clean exit 0 with no signal of any
        # kind naming the lost heading.
        data = _joined("### DQ-001: First question", _LONG_JOINED,
                       _BODY_ONE)
        _assert_signalled(
            self, data, "fix9_a_t02.md",
            "DQ-002: Second question with several more "
            "words in its title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_t16_genuine_long_title_on_second_signalled(self):
        # Attack case t16: the join standing on the second
        # heading line of the two entry control, the host
        # title Second question joined to a third heading
        # whose title carries nine words, with the second
        # and third bodies standing behind the line;
        # before the cure headed entries read 2 of 3 with
        # no PIN-06.
        data = TWO.replace(
            "### DQ-002: Second question\n",
            "### DQ-002: Second question" + LS +
            "### DQ-003: Third question with several more "
            "words in its title\n").encode("utf-8")
        data = data + ("\n" + _BODY_THREE).encode("utf-8")
        _assert_signalled(
            self, data, "fix9_a_t16.md",
            "DQ-003: Third question with several more "
            "words in its title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_t03_genuine_equal_titles_control_signalled(self):
        # Attack control t03: the joined title Second
        # question, two words, standing equal to the host
        # segment's two words, two bodies behind; the
        # PIN-06 Warning stands, as before the cure.
        data = _joined("### DQ-001: First question",
                       "### DQ-002: Second question",
                       _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix9_a_t03.md",
                          "DQ-002: Second question")

    def test_t07_genuine_short_title_control_signalled(self):
        # Attack control t07: the joined title Second, one
        # word, against a host segment title of five words,
        # two bodies behind; the PIN-06 Warning stands, as
        # before the cure.
        data = _joined("### DQ-001: First question with words",
                       "### DQ-002: Second",
                       _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix9_a_t07.md",
                          "DQ-002: Second")

    def test_j09_short_host_long_join_signalled(self):
        # Seat 1 neighbour case j09: a genuine joined
        # heading whose title carries eight words behind
        # a one word host title, one shared body behind
        # the line in the near marker form; before the
        # cure the part took no signal at exit 0.
        data = _joined("### DQ-001: Short",
                       "### DQ-002: A much longer second open "
                       "question title here",
                       _NEAR_BODY)
        _assert_signalled(
            self, data, "fix9_a_j09.md",
            "DQ-002: A much longer second open question "
            "title here")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_j10_long_host_short_join_signalled(self):
        # Seat 1 neighbour case j10: the host title
        # carrying eight words and the joined part one
        # word, one shared body behind the line; the part
        # takes its signal at exit 1, as recorded.
        data = _joined(
            "### DQ-001: A much longer first open question "
            "title here",
            "### DQ-002: Short", _NEAR_BODY)
        _assert_signalled(self, data, "fix9_a_j10.md",
                          "DQ-002: Short")

    def test_j11_equal_titles_join_signalled(self):
        # Seat 1 neighbour case j11: the joined title
        # standing equal to the host segment's title, one
        # shared body behind the line; the part takes its
        # signal at exit 1, as recorded.
        data = _joined("### DQ-001: A sample open question",
                       "### DQ-002: A sample open question",
                       _NEAR_BODY)
        _assert_signalled(
            self, data, "fix9_a_j11.md",
            "DQ-002: A sample open question")


# ---------------------------------------------------------------------
# CH-192: a heading shaped part inside a heading's own
# title takes no signal where no entry body stands
# behind the part
# ---------------------------------------------------------------------

class Step17Fix9A192FalseFireTest(unittest.TestCase):
    """CH-192, A9-3-F2: the title matter test reads the
    charged title parts as title matter, so the scan
    fires no PIN-06 Warning on title matter with no entry
    body behind the part, and the control stands silent,
    as before."""

    def test_t04_fake_short_title_long_host_no_signal(self):
        # Attack case t04: the host segment title A sample
        # open question with many more words, seven words,
        # and the part DQ-002: Not real, whose title
        # carries two words, on the first heading; the one
        # body in the span is the host heading's own.
        # Before the cure the run exited 1 on one PIN-06
        # Warning naming the title text.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Not real").encode("utf-8")
        _assert_no_signal(self, data, "fix9_a_t04.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t06_fake_equal_titles_no_signal(self):
        # Attack case t06: the host segment title A
        # sample, two words, and the part DQ-002: Not
        # real, two words, standing equal; the one body in
        # the span is the host heading's own. Before the
        # cure the run exited 1 on the PIN-06 Warning.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not real").encode("utf-8")
        _assert_no_signal(self, data, "fix9_a_t06.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t17_fake_short_title_second_heading_no_signal(self):
        # Attack case t17: the same short part form
        # standing in the second heading's title of the
        # two entry control, the host segment title Second
        # question with many more words and the part
        # DQ-003: Not real; the two bodies in the file are
        # the two host entries' own. Before the cure the
        # run exited 1 on the PIN-06 Warning.
        data = TWO.replace(
            "### DQ-002: Second question",
            "### DQ-002: Second question with many more "
            "words" + LS +
            "### DQ-003: Not real").encode("utf-8")
        _assert_no_signal(self, data, "fix9_a_t17.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t05_fake_long_title_control_no_signal(self):
        # Attack control t05: the same title construction
        # with the part's title carrying more words than
        # the segment before it, seven words against six;
        # no signal at exit 0, as before the cure.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with "
            "words" + LS +
            "### DQ-002: Not a real entry at all here"
            ).encode("utf-8")
        _assert_no_signal(self, data, "fix9_a_t05.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------
# Governing pins on this surface, in both directions
# ---------------------------------------------------------------------

class Step17Fix9APinTest(unittest.TestCase):
    """The CH-115 pins the narrowing was landed to hold,
    the charged twin forms of CH-96, and the s26
    neighbour bound, standing whole beside the charges."""

    def test_title_join_first_heading_no_signal(self):
        # Round 7 instance r23, the CH-115 title pin: the
        # first entry heading whose own title carries one
        # line separator and then a heading shaped text.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix9_a_r23.md", 1)
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
        _assert_no_signal(self, data, "fix9_a_r24.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_s32_own_heading_join_title_fake_no_signal(self):
        # Round 8 held form s32: a line carrying its own
        # recognised heading behind a leading join, with a
        # further title fake behind it; headed entries 2
        # of 2 at exit 0 with no signal.
        data = TWO.replace(
            "### DQ-002: Second question",
            "\x0b### DQ-002: Second question" + LS +
            "### DQ-009: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix9_a_s32.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_twin_two_bodies_still_signalled(self):
        # The twin join with two bodies standing behind
        # the heading line takes its PIN-06 Warning.
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question\n").encode(
                "utf-8")
        data = data.decode("utf-8") + _SECOND_BODY_TWIN
        data = data.encode("utf-8")
        _assert_signalled(
            self, data, "fix9_a_twin2.md",
            "DQ-002: A sample open question")

    def test_differing_two_bodies_still_signalled(self):
        # The differing join with two bodies standing
        # behind the heading line takes its PIN-06
        # Warning.
        body = _HEAD
        body += ("### DQ-001: A sample open question" + LS +
                 "### DQ-002: Second question\n")
        body += "\n" + _BODY_ONE.rstrip("\n")
        body += ("\n\nStatus: Ruled\n\n"
                 "Question: Which other option should we "
                 "take?\n\n"
                 "Options: Option C, Option D\n\n"
                 "Cost of deciding late: More work stays "
                 "blocked.\n\n"
                 "Blocks: DQ-001\n\n"
                 "This question is also waiting for a "
                 "decision.\n")
        data = body.encode("utf-8")
        _assert_signalled(self, data, "fix9_a_diff2.md",
                          "DQ-002: Second question")

    def test_heading_status_heading_one_line_still_signalled(self):
        # The q54 form: one joined line carrying the first
        # heading, its Status line, and the second heading;
        # the heading part takes its signal on the body
        # standing behind the line.
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
            self, data, "fix9_a_q54.md",
            "DQ-002: A sample open question")

    def test_s01_twin_single_body_still_signalled(self):
        # Attack case s01 of round 8, the CH-156 pin: the
        # first heading joined to a twin second heading,
        # one body following; the joined heading takes its
        # signal.
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question\n").encode(
                "utf-8")
        _assert_signalled(
            self, data, "fix9_a_s01.md",
            "DQ-002: A sample open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_s26_comment_opener_in_joined_title_bounded(self):
        # The named neighbour form of ruling (i) of record
        # section 77, bounded expressly as the fix wave 8
        # K3 module states it: the part takes no PIN-06
        # signal, the file stands at exit 1 on other
        # findings with headed entries 1, and no silent
        # deletion is shown, because the comment trouble
        # the part carries is named by the findings that
        # stand.
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question <!-- x\n"
            ).encode("utf-8")
        data = data + _SECOND_BODY_TWIN.encode("utf-8")
        model, output = h.run_pipeline(data, "fix9_a_s26.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_pin06(output), [])
        self.assertEqual(int(h.entry_total(output)), 1)
        for sub in ("validate", "render"):
            code, _out = _cli(data, sub)
            self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# Held forms of the round 9 seat 3 paper: the back
# scan's walk on chains and across a plain part
# ---------------------------------------------------------------------

class Step17Fix9AHeldChainTest(unittest.TestCase):
    """Cases t08 to t11 of the round 9 seat 3 paper,
    recorded there as held: the one PIN-06 Warning names
    the genuine part in each chain, and the plain part
    forms stand at their recorded readings."""

    def test_t08_chain_fake_then_genuine_held(self):
        # Case t08: a title fake before a genuine part on
        # one line; the one PIN-06 Warning names the
        # genuine part, DQ-002: Second question, and the
        # title fake before it takes no signal.
        data = _joined(
            "### DQ-001: First question",
            "### DQ-009: Not a real entry with a long "
            "title here" + LS + "### DQ-002: Second question",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix9_a_t08.md",
                          "DQ-002: Second question")

    def test_t09_chain_genuine_then_fake_held(self):
        # Case t09: a genuine part before a title fake on
        # one line; the one PIN-06 Warning names DQ-002:
        # Second question, and the fake behind the genuine
        # part takes no signal.
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question" + LS +
            "### DQ-009: Not a real entry with a long "
            "title here",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix9_a_t09.md",
                          "DQ-002: Second question")

    def test_t10_plain_part_then_fake_held(self):
        # Case t10: a plain words part standing between
        # the host segment and a long title fake leaves
        # the fake suppressed at exit 0.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "some plain words" + LS +
            "### DQ-002: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix9_a_t10.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t11_plain_part_then_genuine_held(self):
        # Case t11: the same plain part standing between
        # a long titled host segment and a short titled
        # genuine part leaves the genuine part signalled
        # at exit 1.
        data = _joined(
            "### DQ-001: First question with many words",
            "some plain words" + LS + "### DQ-002: Second",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix9_a_t11.md",
                          "DQ-002: Second")


if __name__ == "__main__":
    unittest.main()
