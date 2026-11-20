"""Step 17 fix wave 12, Fix Seat A: Cluster A, the title limb.

Charges CH-313 to CH-321, as proposed at Cluster A of the
round 12 triage preparation (design/steps/
step-17r-r12-triage-prep.md, section 3), against round 12
attack seat 2 findings A12-2-F1 to A12-2-F5 (paper at
design/steps/step-17r-r12-seat02-run.md) and round 12
attack seat 21 findings A12-21-F1 to A12-21-F4 (paper at
design/steps/step-17r-r12-seat21-run.md), distinct
findings T12-01 to T12-09. Locus: parse.py, the CH-96
split scan title limb as cured at CH-274 to CH-281.

CH-313 (Medium, T12-01): the edge strip set does not
strip square brackets, braces, asterisks, or guillemets
at a word's edge (seat 2 cases w01, w01b, w01c, w01d).
CH-314 (Medium, T12-02): the separator set does not read
the slash, the en dash, or the full stop as a word
separator (seat 2 cases w02, w02b, w02c). CH-315
(Medium, T12-03): a genuine joined heading at number
distance four beside two bodies taking no signal (seat 2
case w03). CH-316 (Medium, T12-04): the ordinal
exception's four word excess bound leaving a genuine
joined heading deleted at five words of excess (seat 2
case w04). CH-317 (Medium, T12-05): the measured segment
reading cutting only at the exact level three fragment
form, a part inside a title behind a level four or level
two fragment firing (seat 2 cases w05, w05b). CH-318
(Medium, T12-06): the shield bound's ordinal opening
condition narrower than the long title limb it re-applies
(seat 21 case p01, control q01). CH-319 (Medium,
T12-07): the shield bound's next number condition
narrower on the same footing (seat 21 case p02, control
q02). CH-320 (Medium, T12-08): a shield chain of three
silent fake segments, the genuine part behind the chain
taking no signal and the third fake taking a PIN-06 of
its own (seat 21 case p03). CH-321 (Medium, T12-09): the
separator set not reading the zero width joiner, the
word joiner, the soft hyphen, an internal comma, or the
pipe (seat 21 cases p05 to p09).

The pin class states the cured controls standing as
pins: the fix wave 11 charged forms m04, m15, n03, v01,
v05, and v07, the bound forms v02, v06, w04b, and the
shield excess eight form, the held controls m12 and
v03c, and the word reading controls m06, n01, and p15
whose part side separator forms stand signalled.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

LS = chr(0x2028)
ZWJ = chr(0x200d)
WJ = chr(0x2060)
SHY = chr(0x00ad)

_HEAD = "# Decision queue\n\n"
_BODY_ONE = ("Status: Banked\n\n"
             "Question: Which option should we take?\n\n"
             "Options: Option A, Option B\n\n"
             "Cost of deciding late: Work stays blocked.\n\n"
             "Blocks: DQ-002\n\n"
             "This question is waiting for a decision.\n")
_BODY_TWO = ("Status: Banked\n\n"
             "Question: Which other option should we take?\n\n"
             "Options: Option C, Option D\n\n"
             "Cost of deciding late: More work stays blocked.\n\n"
             "Blocks: DQ-001\n\n"
             "This question is also waiting for a decision.\n")
_BODY_THREE = ("Status: Banked\n\n"
               "Question: Which third option should we take?\n\n"
               "Options: Option E, Option F\n\n"
               "Cost of deciding late: Even more work stays blocked.\n\n"
               "Blocks: DQ-001\n\n"
               "This third question is waiting for a decision.\n")
BASE = (_HEAD + "### DQ-001: A sample open question\n\n"
        + _BODY_ONE)
_KHEAD = "# Decision queue\n\n"
_KBODY = ("\nStatus: BankedX\n\n"
          "This question is waiting for a decision.\n")
_RICH1 = ("Status: Banked\n\n"
          "Question: Which option should we take?\n\n"
          "Options: Option A, Option B\n\n"
          "Cost of deciding late: Work stays blocked.\n\n"
          "Blocks: DQ-002\n\n"
          "This question is waiting for a decision.\n")
_RICH1B = _RICH1.replace("Which option", "Which other option")


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


def _assert_no_pin06(test, data, name):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    test.assertEqual(_pin06(output), [])


def _joined(first, joined, bodies):
    text = _HEAD + first + LS + joined + "\n\n" + bodies
    return text.encode("utf-8")


def _kjoined(first, joined, body):
    text = _KHEAD + first + LS + joined + "\n" + body
    return text.encode("utf-8")


# ---------------------------------------------------------------------
# CH-313: the edge strip set does not strip square
# brackets, braces, asterisks, or guillemets
# ---------------------------------------------------------------------

class Step17Fix12A313EdgeStripTest(unittest.TestCase):
    """CH-313, T12-01 (seat 2 A12-2-F1): a genuine joined
    heading whose one shared word with its host segment
    stands under square brackets, braces, asterisks, or
    guillemets in the segment title takes its signal."""

    def test_w01_bracket_shared_word_signalled(self):
        data = _joined("### DQ-001: [Budget] review",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w01.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_w01b_brace_shared_word_signalled(self):
        data = _joined("### DQ-001: {Budget} review",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w01b.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_w01c_asterisk_shared_word_signalled(self):
        data = _joined("### DQ-001: *Budget* review",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w01c.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_w01d_guillemet_shared_word_signalled(self):
        data = _joined("### DQ-001: \u00abBudget\u00bb review",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w01d.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-314: the separator set does not read the slash, the
# en dash, or the full stop
# ---------------------------------------------------------------------

class Step17Fix12A314SeparatorTest(unittest.TestCase):
    """CH-314, T12-02 (seat 2 A12-2-F2): a genuine joined
    heading whose host segment's title joins two of its
    words with a slash, an en dash, or a full stop takes
    its signal."""

    def test_w02_slash_segment_signalled(self):
        data = _joined("### DQ-001: Budget/review notes",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w02.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_w02b_endash_segment_signalled(self):
        data = _joined("### DQ-001: Budget\u2013review notes",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w02b.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_w02c_fullstop_segment_signalled(self):
        data = _joined("### DQ-001: Budget.review notes",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w02c.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-315: a genuine joined heading at number distance
# four beside two standing bodies takes its signal
# ---------------------------------------------------------------------

class Step17Fix12A315DistanceFourTest(unittest.TestCase):
    """CH-315, T12-03 (seat 2 A12-2-F3): the two body
    limb at number distance four, every skipped number
    standing later as a complete entry."""

    def test_w03_distance4_two_bodies_signalled(self):
        # Seat 2 case w03: DQ-005 after DQ-001, the first
        # and fifth entries' bodies in the span, complete
        # DQ-002, DQ-003, and DQ-004 entries standing later.
        data = (_HEAD + "### DQ-001: First question" + LS +
                "### DQ-005: Fifth question plus\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE +
                "\n### DQ-002: Second question\n\n" +
                _BODY_TWO +
                "\n### DQ-003: Third question\n\n" +
                _BODY_THREE +
                "\n### DQ-004: Fourth question\n\n" +
                _BODY_TWO).encode("utf-8")
        _assert_signalled(self, data, "fix12_a_w03.md",
                          "DQ-005: Fifth question plus")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-316: the ordinal exception at five words of segment
# excess leaves a genuine joined heading deleted
# ---------------------------------------------------------------------

class Step17Fix12A316OrdinalExcessFiveTest(unittest.TestCase):
    """CH-316, T12-04 (seat 2 A12-2-F4): a genuine joined
    heading whose title stands wholly in its host
    segment's title terms and opens with the ordinal word
    of its own number takes its signal at five words of
    segment excess."""

    def test_w04_genuine_inside_ordinal_excess5_signalled(self):
        # Seat 2 case w04: segment Question second review
        # with extra words here, seven words, part Second
        # question, wholly inside the segment's terms.
        data = _joined(
            "### DQ-001: Question second review with extra "
            "words here",
            "### DQ-002: Second question", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_w04.md",
                          "DQ-002: Second question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-317: the measured segment reading cuts only at the
# exact level three fragment form
# ---------------------------------------------------------------------

class Step17Fix12A317FragmentLevelTest(unittest.TestCase):
    """CH-317, T12-05 (seat 2 A12-2-F5): a heading shaped
    part inside a title, behind a segment carrying a
    level four or level two fragment inside its title,
    takes no signal where the one body in the span is the
    host heading's own."""

    def test_w05_fragment_level4_no_signal(self):
        data = _joined(
            "### DQ-001: Alpha #### DQ-009: many fake words "
            "standing here",
            "### DQ-002: Part title with six more words now",
            _BODY_ONE)
        _assert_no_signal(self, data, "fix12_a_w05.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_w05b_fragment_level2_no_signal(self):
        data = _joined(
            "### DQ-001: Alpha ## DQ-009: many fake words "
            "standing here",
            "### DQ-002: Part title with six more words now",
            _BODY_ONE)
        _assert_no_signal(self, data, "fix12_a_w05b.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------
# CH-318: the shield bound's ordinal opening condition
# ---------------------------------------------------------------------

class Step17Fix12A318ShieldOrdinalTest(unittest.TestCase):
    """CH-318, T12-06 (seat 21 A12-21-F1): a genuine
    joined heading behind a silent fake segment, carrying
    the host segment's next entry number and exceeding
    its title by seven words, takes its signal although
    its title does not open with the ordinal word of its
    own number, as the same heading joined directly to
    its host signals (seat 21 control q01, in the pins)."""

    def test_p01_shield_no_ordinal_signalled(self):
        data = _kjoined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here",
            "### DQ-002: Open matter waiting for decision "
            "under review today now", _KBODY)
        _assert_signalled(
            self, data, "fix12_a_p01.md",
            "DQ-002: Open matter waiting for decision "
            "under review today now")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-319: the shield bound's next number condition
# ---------------------------------------------------------------------

class Step17Fix12A319ShieldDistanceTest(unittest.TestCase):
    """CH-319, T12-07 (seat 21 A12-21-F2): a genuine
    joined heading behind a silent fake segment, carrying
    the number two places after its host segment's and
    opening with the ordinal word of its own number,
    takes its signal, as the same heading joined directly
    to its host signals (seat 21 control q02, in the
    pins)."""

    def test_p02_shield_distance2_signalled(self):
        data = _kjoined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here",
            "### DQ-003: Third open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix12_a_p02.md",
            "DQ-003: Third open matter waiting for "
            "decision under review today")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-320: a shield chain of three silent fake segments
# ---------------------------------------------------------------------

class Step17Fix12A320ShieldChainThreeTest(unittest.TestCase):
    """CH-320, T12-08 (seat 21 A12-21-F3): at a shield
    chain of three silent fake segments the genuine part
    behind the chain takes its signal, and no fake
    segment of the chain takes a signal of its own: the
    file carries exactly one PIN-06, naming the genuine
    part."""

    def test_p03_shield_three_fakes_signalled(self):
        data = _kjoined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here" + LS +
            "### DQ-010: Also not a real entry standing "
            "here now" + LS +
            "### DQ-011: Still not a real entry standing "
            "here either",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix12_a_p03.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-321: the separator set does not read the zero width
# joiner, the word joiner, the soft hyphen, an internal
# comma, or the pipe
# ---------------------------------------------------------------------

class Step17Fix12A321SeparatorInvisibleTest(unittest.TestCase):
    """CH-321, T12-09 (seat 21 A12-21-F4): a genuine
    joined heading whose segment title joins two of its
    words with a zero width joiner, a word joiner, a soft
    hyphen, an internal comma, or a pipe takes its
    signal."""

    def test_p05_sep_zwj_segment_signalled(self):
        data = _kjoined(
            "### DQ-001: First open" + ZWJ + "question",
            "### DQ-002: Second open question", _KBODY)
        _assert_signalled(self, data, "fix12_a_p05.md",
                          "DQ-002: Second open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_p06_sep_wj_segment_signalled(self):
        data = _kjoined(
            "### DQ-001: First open" + WJ + "question",
            "### DQ-002: Second open question", _KBODY)
        _assert_signalled(self, data, "fix12_a_p06.md",
                          "DQ-002: Second open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_p07_sep_shy_segment_signalled(self):
        data = _kjoined(
            "### DQ-001: First open" + SHY + "question",
            "### DQ-002: Second open question", _KBODY)
        _assert_signalled(self, data, "fix12_a_p07.md",
                          "DQ-002: Second open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_p08_sep_comma_segment_signalled(self):
        data = _kjoined("### DQ-001: First open,question",
                        "### DQ-002: Second open question",
                        _KBODY)
        _assert_signalled(self, data, "fix12_a_p08.md",
                          "DQ-002: Second open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_p09_sep_pipe_segment_signalled(self):
        data = _kjoined("### DQ-001: First open|question",
                        "### DQ-002: Second open question",
                        _KBODY)
        _assert_signalled(self, data, "fix12_a_p09.md",
                          "DQ-002: Second open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# Governing pins on this surface, in both directions
# ---------------------------------------------------------------------

class Step17Fix12APinTest(unittest.TestCase):
    """The cured controls of fix wave 11 and the bound
    forms of the round 12 papers on this surface, standing
    whole beside the charges."""

    def test_m04_underscore_segment_signalled(self):
        data = _kjoined("### DQ-001: First open_question",
                        "### DQ-002: Second open question",
                        _KBODY)
        _assert_signalled(self, data, "fix12_a_m04.md",
                          "DQ-002: Second open question")

    def test_m06_slash_part_signalled(self):
        # The part side slash form of the round 11 papers:
        # the part Second question/answer, opening with its
        # number's ordinal word and sharing a word with its
        # segment, stands signalled beside the cure of
        # CH-314, whose separator reading now splits the
        # part's title at the slash.
        data = _kjoined("### DQ-001: First question",
                        "### DQ-002: Second question/answer",
                        _KBODY)
        _assert_signalled(self, data, "fix12_a_m06.md",
                          "DQ-002: Second question/answer")

    def test_n01_underscore_part_signalled(self):
        data = _kjoined("### DQ-001: First open question",
                        "### DQ-002: Second open_question",
                        _KBODY)
        _assert_signalled(self, data, "fix12_a_n01.md",
                          "DQ-002: Second open_question")

    def test_p15_slash_part_signalled(self):
        # Seat 21 case p15: the part's words joined by a
        # slash on the part side, signalled in round 12.
        data = _kjoined("### DQ-001: First budget review",
                        "### DQ-002: Second budget/outcome",
                        _KBODY)
        _assert_signalled(self, data, "fix12_a_p15.md",
                          "DQ-002: Second budget/outcome")

    def test_v07_quoted_shared_word_signalled(self):
        data = _joined('### DQ-001: "Budget" review',
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_v07.md",
                          "DQ-002: Budget outcome")

    def test_v01_genuine_inside_ordinal_signalled(self):
        data = _joined("### DQ-001: Question second review",
                       "### DQ-002: Second question", _BODY_ONE)
        _assert_signalled(self, data, "fix12_a_v01.md",
                          "DQ-002: Second question")

    def test_m15_fake_segment_shields_genuine_signalled(self):
        data = _kjoined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix12_a_m15.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")

    def test_n03_two_fake_shield_signalled(self):
        data = _kjoined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here" + LS +
            "### DQ-010: Also not a real entry standing "
            "here now",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix12_a_n03.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")

    def test_q01_no_ordinal_direct_signalled(self):
        # Seat 21 control q01: the CH-318 part joined
        # directly to its host, signalled in round 12.
        data = _kjoined(
            "### DQ-001: First question",
            "### DQ-002: Open matter waiting for decision "
            "under review today now", _KBODY)
        _assert_signalled(
            self, data, "fix12_a_q01.md",
            "DQ-002: Open matter waiting for decision "
            "under review today now")

    def test_q02_distance2_direct_signalled(self):
        # Seat 21 control q02: the CH-319 part joined
        # directly to its host, signalled in round 12.
        data = _kjoined(
            "### DQ-001: First question",
            "### DQ-003: Third open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix12_a_q02.md",
            "DQ-003: Third open matter waiting for "
            "decision under review today")

    def test_v05_fake_measured_segment_cut_no_signal(self):
        data = _joined(
            "### DQ-001: Alpha ### DQ-009: many fake words "
            "standing here",
            "### DQ-002: Part title with six more words now",
            _BODY_ONE)
        _assert_no_signal(self, data, "fix12_a_v05.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_v02_fake_ordinal_opens_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Second thoughts").encode("utf-8")
        _assert_no_signal(self, data, "fix12_a_v02.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_w04b_fake_ordinal_excess5_no_signal(self):
        # Seat 2 bound reading w04b: a heading shaped part
        # inside a title opening with the ordinal word of
        # its own number at five words of segment excess,
        # its title not standing wholly in the segment's
        # terms, stands silent beside the cure of CH-316.
        data = _joined(
            "### DQ-001: A sample open question with many "
            "more words",
            "### DQ-002: Second thoughts now", _BODY_ONE)
        _assert_no_signal(self, data, "fix12_a_w04b.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_shield_excess8_bound_no_signal(self):
        # Seat 2 bound reading w06 and seat 21 observation
        # p16: a genuine part behind one shield segment at
        # eight words of excess over its host stands at
        # the shield bound's stated far edge.
        data = _joined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here",
            "### DQ-002: Second open matter waiting for "
            "decision under review today now", _BODY_ONE)
        _assert_no_signal(self, data, "fix12_a_w06.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_m12_fake_plus2_skipped_absent_no_pin06(self):
        data = (_KHEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Not a real entry at all here "
                "now\n\n" + _RICH1 + "\n" +
                _RICH1B).encode("utf-8")
        _assert_no_pin06(self, data, "fix12_a_m12.md")

    def test_v03c_control_distance2_skipped_absent_no_pin06(self):
        data = (_HEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Third question plus\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE).encode("utf-8")
        _assert_no_pin06(self, data, "fix12_a_v03c.md")

    def test_u15_fake_excess_eight_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry heading at all "
            "in this title").encode("utf-8")
        _assert_no_signal(self, data, "fix12_a_u15.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_v06_genuine_excess_eight_bound_no_signal(self):
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question with several more "
            "words in this title today", _BODY_ONE)
        _assert_no_signal(self, data, "fix12_a_v06.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
