"""Step 17 fix wave 11, Fix Seat A: Cluster A, the title limb.

Charges CH-274 to CH-281, as determined at record section
108, against round 11 attack seat 1 findings A11-1-F1 to
A11-1-F5 (paper at design/steps/step-17r-r11-seat01-run.md)
and round 11 attack seat 3 findings A11-3-F1 to A11-3-F5
(paper at design/steps/step-17r-r11-seat03-run.md),
consolidated at section 2.1 and Cluster A of the round 11
triage preparation (design/steps/step-17r-r11-triage-prep.md,
findings T11-01 to T11-08). Locus: parse.py, the CH-96 split
scan title limb as cured at CH-226 to CH-233.

CH-274 (Medium, T11-01): the wholly inside condition read
without the ordinal exception, a genuine joined heading
opening with its number's ordinal word deleted (seat 1
case m21; seat 3 cases v01 and v01b). CH-275 (Medium,
T11-02): a genuine joined heading at number distance
three beside two bodies taking no signal (seat 1 cases
m20 and n05; seat 3 case v03). CH-276 (Medium, T11-03):
the title word reading's separator set not reading the
underscore (seat 1 case m04). CH-277 (Medium, T11-04): the
title word reading's edge strip set not stripping quote
marks or parentheses (seat 3 cases v07 and v07b). CH-278
(Medium, T11-05): a silent fake standing as its own joined
segment shielding a genuine part (seat 1 cases m15 and
n03). CH-279 (Medium, T11-06): the measured segment
reading joined to the six word excess bound firing inside
a title (seat 3 case v05). CH-280 (Medium, T11-07): the
two body extension reading the skipped number's standing
on heading lines anywhere in the file (seat 1 cases m10,
m11, and n06). CH-281 (Medium, T11-08): the ordinal
exception reading no part of where a part stands, a part
inside a title firing where no body stands behind it
(seat 3 cases v02 and v02b).

The pin class states the cured controls standing as pins:
u05, u02, k07, u06 and the CH-228 family, u11, u12, u14,
k09, m12, and the round 10 word controls in their cured
standings, beside the bound forms v03c, v04, v06, v08, and
m17 at their recorded readings.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

LS = chr(0x2028)
ZWSP = chr(0x200b)

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
TWO = (_HEAD + "### DQ-001: First question\n\n"
       + _BODY_ONE + "\n"
       "### DQ-002: Second question\n\n"
       + _BODY_TWO)
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
_RICH2 = ("### DQ-002: Second question\n\nStatus: Banked\n\n"
          "Question: Which other option should we take?\n\n"
          "Options: Option C, Option D\n\n"
          "Cost of deciding late: More work stays blocked.\n\n"
          "Blocks: DQ-001\n\n"
          "This question is also waiting for a decision.\n")
_RICH3 = ("### DQ-003: Third question\n\nStatus: Banked\n\n"
          "Question: Which third option should we take?\n\n"
          "Options: Option E, Option F\n\n"
          "Cost of deciding late: Even more work stays blocked.\n\n"
          "Blocks: DQ-001\n\n"
          "This third question is waiting for a decision.\n")


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
# CH-274: the wholly inside condition read without the
# ordinal exception deletes a genuine joined heading
# ---------------------------------------------------------------------

class Step17Fix11A274WhollyInsideOrdinalTest(unittest.TestCase):
    """CH-274, T11-01 (seat 1 A11-1-F5 with seat 3
    A11-3-F1): a genuine joined heading whose title stands
    wholly in its segment's own title terms and opens with
    the ordinal word of its own number takes its signal."""

    def test_m21_subset_genuine_signalled(self):
        # Seat 1 case m21: segment Open question about
        # second matter, part Second matter.
        data = _kjoined(
            "### DQ-001: Open question about second matter",
            "### DQ-002: Second matter", _KBODY)
        _assert_signalled(self, data, "fix11_a_m21.md",
                          "DQ-002: Second matter")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_v01_genuine_inside_ordinal_signalled(self):
        # Seat 3 case v01: segment Question second review,
        # part Second question.
        data = _joined("### DQ-001: Question second review",
                       "### DQ-002: Second question", _BODY_ONE)
        _assert_signalled(self, data, "fix11_a_v01.md",
                          "DQ-002: Second question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_v01b_genuine_inside_ordinal_second_signalled(self):
        # Seat 3 case v01b: the same form on the second
        # heading of the two entry control.
        data = TWO.replace(
            "### DQ-002: Second question\n",
            "### DQ-002: Question third review" + LS +
            "### DQ-003: Third question\n").encode("utf-8")
        _assert_signalled(self, data, "fix11_a_v01b.md",
                          "DQ-003: Third question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-275: a genuine joined heading at number distance
# three beside two standing bodies takes its signal
# ---------------------------------------------------------------------

class Step17Fix11A275DistanceThreeTest(unittest.TestCase):
    """CH-275, T11-02 (seat 1 A11-1-F4 with seat 3
    A11-3-F3): the two body limb at number distance three,
    the skipped entries standing in the file."""

    def test_m20_plus3_two_bodies_signalled(self):
        # Seat 1 case m20: DQ-004 after DQ-001, two bodies,
        # complete DQ-002 and DQ-003 entries standing later.
        data = (_KHEAD + "### DQ-001: First question" + LS +
                "### DQ-004: Fourth question with several "
                "more words in title\n\n" + _RICH1 + "\n" +
                _RICH1B + "\n" + _RICH2 + "\n" +
                _RICH3).encode("utf-8")
        _assert_signalled(
            self, data, "fix11_a_m20.md",
            "DQ-004: Fourth question with several more "
            "words in title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_n05_plus3_one_skipped_later_signalled(self):
        # Seat 1 case n05: DQ-004 after DQ-001, two bodies,
        # the skipped DQ-002 standing later as a complete
        # entry.
        data = (_KHEAD + "### DQ-001: First question" + LS +
                "### DQ-004: Fourth question with several "
                "more words in title\n\n" + _RICH1 + "\n" +
                _RICH1B + "\n" + _RICH2).encode("utf-8")
        _assert_signalled(
            self, data, "fix11_a_n05.md",
            "DQ-004: Fourth question with several more "
            "words in title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_v03_genuine_distance3_signalled(self):
        # Seat 3 case v03: DQ-004 after DQ-001, the first
        # and fourth entries' bodies in the span, complete
        # DQ-002 and DQ-003 entries standing later.
        data = (_HEAD + "### DQ-001: First question" + LS +
                "### DQ-004: Fourth question plus\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE +
                "\n### DQ-002: Second question\n\n" +
                _BODY_TWO +
                "\n### DQ-003: Third question\n\n" +
                _BODY_THREE).encode("utf-8")
        _assert_signalled(self, data, "fix11_a_v03.md",
                          "DQ-004: Fourth question plus")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-276: the separator set does not read the underscore
# ---------------------------------------------------------------------

class Step17Fix11A276UnderscoreSeparatorTest(unittest.TestCase):
    """CH-276, T11-03 (seat 1 A11-1-F1): a genuine joined
    heading whose segment title joins two of its words
    with an underscore takes its signal."""

    def test_m04_underscore_segment_signalled(self):
        # Seat 1 case m04: segment First open_question,
        # part Second open question.
        data = _kjoined("### DQ-001: First open_question",
                        "### DQ-002: Second open question",
                        _KBODY)
        _assert_signalled(self, data, "fix11_a_m04.md",
                          "DQ-002: Second open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-277: the edge strip set does not strip quote marks
# or parentheses at a word's edge
# ---------------------------------------------------------------------

class Step17Fix11A277EdgeStripTest(unittest.TestCase):
    """CH-277, T11-04 (seat 3 A11-3-F5): a genuine joined
    heading whose one shared word with its host segment
    stands under quote marks or in parentheses in the
    segment title takes its signal."""

    def test_v07_quoted_shared_word_signalled(self):
        data = _joined('### DQ-001: "Budget" review',
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix11_a_v07.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_v07b_paren_shared_word_signalled(self):
        data = _joined("### DQ-001: (Budget) review",
                       "### DQ-002: Budget outcome", _BODY_ONE)
        _assert_signalled(self, data, "fix11_a_v07b.md",
                          "DQ-002: Budget outcome")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-278: a silent fake standing as its own joined
# segment shields a genuine part behind it
# ---------------------------------------------------------------------

class Step17Fix11A278FakeSegmentShieldTest(unittest.TestCase):
    """CH-278, T11-05 (seat 1 A11-1-F2): a genuine part
    standing behind a silent fake segment on its line is
    measured against the host segment, not the fake."""

    def test_m15_fake_segment_shields_genuine_signalled(self):
        # Seat 1 case m15: host First question, fake segment
        # DQ-009, genuine part of nine words.
        data = _kjoined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix11_a_m15.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_n03_two_fake_shield_signalled(self):
        # Seat 1 case n03: two silent fake segments standing
        # between the host segment and the genuine part.
        data = _kjoined(
            "### DQ-001: First question" + LS +
            "### DQ-009: Not a real entry at all here" + LS +
            "### DQ-010: Also not a real entry standing "
            "here now",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix11_a_n03.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-279: the measured segment reading joined to the six
# word excess bound fires on a part inside a title
# ---------------------------------------------------------------------

class Step17Fix11A279MeasuredSegmentTitleTest(unittest.TestCase):
    """CH-279, T11-06 (seat 3 A11-3-F4): a heading shaped
    part inside a title, behind a segment whose measured
    title is cut at an embedded fragment, takes no signal
    where the one body in the span is the host's own."""

    def test_v05_fake_measured_segment_cut_no_signal(self):
        # Seat 3 case v05: host Alpha with a space joined
        # fragment inside its title, part of seven words.
        data = _joined(
            "### DQ-001: Alpha ### DQ-009: many fake words "
            "standing here",
            "### DQ-002: Part title with six more words now",
            _BODY_ONE)
        _assert_no_signal(self, data, "fix11_a_v05.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------
# CH-280: the extension reads the skipped number's
# standing on heading lines anywhere in the file
# ---------------------------------------------------------------------

class Step17Fix11A280ExtensionStandingTest(unittest.TestCase):
    """CH-280, T11-07 (seat 1 A11-1-F3): a heading shaped
    fake at the number after next takes no signal where
    the skipped number stands earlier, or stands as a
    heading line alone, neither of them a complete entry
    later in the file."""

    def test_m10_fake_plus2_skipped_earlier_no_pin06(self):
        # Seat 1 case m10: the skipped DQ-003 stands earlier
        # in the file as a complete entry.
        data = (_KHEAD + _RICH3 +
                "\n### DQ-002: First question" + LS +
                "### DQ-004: Not a real entry at all here "
                "now\n\n" + _RICH1 + "\n" +
                _RICH1B).encode("utf-8")
        _assert_no_pin06(self, data, "fix11_a_m10.md")

    def test_m11_fake_plus2_skipped_heading_only_no_pin06(self):
        # Seat 1 case m11: the skipped DQ-002 stands later
        # as a heading line alone, with no body.
        data = (_KHEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Not a real entry at all here "
                "now\n\n" + _RICH1 + "\n" + _RICH1B +
                "\n### DQ-002: Second question\n"
                ).encode("utf-8")
        _assert_no_pin06(self, data, "fix11_a_m11.md")

    def test_n06_fake_plus2_skipped_earlier_heading_no_pin06(self):
        # Seat 1 case n06: the skipped DQ-002 stands earlier
        # as a heading line alone.
        data = (_KHEAD + "### DQ-002: Second question\n" +
                "\n### DQ-001: First question" + LS +
                "### DQ-003: Not a real entry at all here "
                "now\n\n" + _RICH1 + "\n" +
                _RICH1B).encode("utf-8")
        _assert_no_pin06(self, data, "fix11_a_n06.md")


# ---------------------------------------------------------------------
# CH-281: the ordinal exception reads no part of where a
# part stands, and a part inside a title fires
# ---------------------------------------------------------------------

class Step17Fix11A281OrdinalPositionTest(unittest.TestCase):
    """CH-281, T11-08 (seat 3 A11-3-F2): a heading shaped
    part inside a title that opens with the ordinal word
    of its own number takes no signal where no body stands
    behind the part, the one body in the span being the
    host heading's own and the host segment's title
    standing long against the part's."""

    def test_v02_fake_ordinal_opens_no_signal(self):
        # Seat 3 case v02: host title of eight words, part
        # Second thoughts.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Second thoughts").encode("utf-8")
        _assert_no_signal(self, data, "fix11_a_v02.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_v02b_fake_ordinal_one_word_no_signal(self):
        # Seat 3 case v02b: the one word form Second beside
        # the host's full body.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Second").encode("utf-8")
        _assert_no_signal(self, data, "fix11_a_v02b.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------
# Governing pins on this surface, in both directions
# ---------------------------------------------------------------------

class Step17Fix11APinTest(unittest.TestCase):
    """The cured controls of fix wave 10 and the round 10
    and round 11 papers on this surface, standing whole
    beside the charges."""

    def test_u05_genuine_noshare_equal_signalled(self):
        data = _joined("### DQ-001: First question",
                       "### DQ-002: Second entry", _BODY_ONE)
        _assert_signalled(self, data, "fix11_a_u05.md",
                          "DQ-002: Second entry")

    def test_u02_genuine_nonnext_two_bodies_signalled(self):
        data = (_HEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Third question plus\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE +
                "\n### DQ-002: Second question\n\n" +
                _BODY_TWO).encode("utf-8")
        _assert_signalled(self, data, "fix11_a_u02.md",
                          "DQ-003: Third question plus")

    def test_k07_genuine_long_nonnext_two_bodies_signalled(self):
        data = (_KHEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Third question with several "
                "more words in its title here\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE +
                "\n### DQ-002: Second question\n\n" +
                _BODY_TWO).encode("utf-8")
        _assert_signalled(
            self, data, "fix11_a_k07.md",
            "DQ-003: Third question with several more "
            "words in its title here")

    def test_u06_genuine_share_equal_control_signalled(self):
        data = _joined("### DQ-001: First question",
                       "### DQ-002: Second question", _BODY_ONE)
        _assert_signalled(self, data, "fix11_a_u06.md",
                          "DQ-002: Second question")

    def test_k09_inflated_segment_control_signalled(self):
        data = _kjoined(
            "### DQ-001: First question",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix11_a_k09.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")

    def test_k08_inflated_segment_signalled(self):
        data = _kjoined(
            "### DQ-001: First question about ### DQ-009: "
            "Not a real entry at all here",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KBODY)
        _assert_signalled(
            self, data, "fix11_a_k08.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")

    def test_u11_fake_wholly_in_segment_title_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Sample question").encode("utf-8")
        _assert_no_signal(self, data, "fix11_a_u11.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_u12_fake_one_word_full_body_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Notreal").encode("utf-8")
        _assert_no_signal(self, data, "fix11_a_u12.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_u14_fake_two_status_in_host_span_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Not real").encode("utf-8")
        data = data + "\nStatus: Banked\n".encode("utf-8")
        _assert_no_signal(self, data, "fix11_a_u14.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_m12_fake_plus2_skipped_absent_no_pin06(self):
        # Seat 1 control m12: the skipped number stands
        # nowhere in the file.
        data = (_KHEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Not a real entry at all here "
                "now\n\n" + _RICH1 + "\n" +
                _RICH1B).encode("utf-8")
        _assert_no_pin06(self, data, "fix11_a_m12.md")

    def test_v03c_control_distance2_skipped_absent_no_pin06(self):
        # Seat 3 held control v03c: the charged distance of
        # CH-227 with the skipped number standing nowhere.
        data = (_HEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Third question plus\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE).encode("utf-8")
        _assert_no_pin06(self, data, "fix11_a_v03c.md")

    def test_k01_case_share_signalled(self):
        data = _kjoined("### DQ-001: First question",
                        "### DQ-002: Second Question", _KBODY)
        _assert_signalled(self, data, "fix11_a_k01.md",
                          "DQ-002: Second Question")

    def test_k02_punct_share_part_signalled(self):
        data = _kjoined("### DQ-001: First question",
                        "### DQ-002: Second question.", _KBODY)
        _assert_signalled(self, data, "fix11_a_k02.md",
                          "DQ-002: Second question.")

    def test_k03_punct_share_segment_signalled(self):
        data = _kjoined("### DQ-001: First question.",
                        "### DQ-002: Second question", _KBODY)
        _assert_signalled(self, data, "fix11_a_k03.md",
                          "DQ-002: Second question")

    def test_k04_hyphen_share_signalled(self):
        data = _kjoined("### DQ-001: First open-question",
                        "### DQ-002: Second open question",
                        _KBODY)
        _assert_signalled(self, data, "fix11_a_k04.md",
                          "DQ-002: Second open question")

    def test_k11_case_share_second_entry_signalled(self):
        first_entry = ("### DQ-001: A sample open question\n"
                       "\nStatus: BankedX\n\n"
                       "This question is waiting for a "
                       "decision.\n")
        data = (_KHEAD + first_entry +
                "\n### DQ-002: First question" + LS +
                "### DQ-003: Second Question\n" +
                _KBODY).encode("utf-8")
        _assert_signalled(self, data, "fix11_a_k11.md",
                          "DQ-003: Second Question")

    def test_k18_hyphen_control_signalled(self):
        data = _kjoined("### DQ-001: First open question",
                        "### DQ-002: Second open question",
                        _KBODY)
        _assert_signalled(self, data, "fix11_a_k18.md",
                          "DQ-002: Second open question")

    def test_m01_paren_part_signalled(self):
        data = _kjoined("### DQ-001: First question",
                        "### DQ-002: Second (question)", _KBODY)
        _assert_signalled(self, data, "fix11_a_m01.md",
                          "DQ-002: Second (question)")

    def test_m02_paren_segment_signalled(self):
        data = _kjoined("### DQ-001: First (question)",
                        "### DQ-002: Second question", _KBODY)
        _assert_signalled(self, data, "fix11_a_m02.md",
                          "DQ-002: Second question")

    def test_m03_quote_part_signalled(self):
        data = _kjoined("### DQ-001: First question",
                        '### DQ-002: Second "question"', _KBODY)
        _assert_signalled(self, data, "fix11_a_m03.md",
                          'DQ-002: Second "question"')

    def test_m05_apostrophe_part_signalled(self):
        data = _kjoined("### DQ-001: First question",
                        "### DQ-002: Second question's", _KBODY)
        _assert_signalled(self, data, "fix11_a_m05.md",
                          "DQ-002: Second question's")

    def test_m06_slash_part_signalled(self):
        data = _kjoined("### DQ-001: First question",
                        "### DQ-002: Second question/answer",
                        _KBODY)
        _assert_signalled(self, data, "fix11_a_m06.md",
                          "DQ-002: Second question/answer")

    def test_n01_underscore_part_signalled(self):
        data = _kjoined("### DQ-001: First open question",
                        "### DQ-002: Second open_question",
                        _KBODY)
        _assert_signalled(self, data, "fix11_a_n01.md",
                          "DQ-002: Second open_question")

    def test_n04_underscore_both_control_signalled(self):
        data = _kjoined("### DQ-001: First open_question",
                        "### DQ-002: Second open_question",
                        _KBODY)
        _assert_signalled(self, data, "fix11_a_n04.md",
                          "DQ-002: Second open_question")

    def test_u01_genuine_excess_six_one_body_signalled(self):
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question with several more "
            "words in title", _BODY_ONE)
        _assert_signalled(
            self, data, "fix11_a_u01.md",
            "DQ-002: Second question with several more "
            "words in title")

    def test_u15_fake_excess_eight_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry heading at all "
            "in this title").encode("utf-8")
        _assert_no_signal(self, data, "fix11_a_u15.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t05_fake_excess_one_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with "
            "words" + LS +
            "### DQ-002: Not a real entry at all here"
            ).encode("utf-8")
        _assert_no_signal(self, data, "fix11_a_t05.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_v06_genuine_excess_eight_bound_no_signal(self):
        # Seat 3 bound reading v06: eight words of excess
        # beside the one shared body stands as title matter
        # at the cure's stated long title bound.
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question with several more "
            "words in this title today", _BODY_ONE)
        _assert_no_signal(self, data, "fix11_a_v06.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_v08_fake_excess_six_bound_signalled(self):
        # Seat 3 bound reading v08: a part at six words of
        # excess beside the host's own body stands in
        # heading position at the same stated bound.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry heading at all "
            "now").encode("utf-8")
        _assert_signalled(
            self, data, "fix11_a_v08.md",
            "DQ-002: Not a real entry heading at all now")

    def test_v04_residual_noshare_noordinal_no_signal(self):
        # Seat 3 case v04: the recorded CH-229 residual, a
        # genuine part sharing no word and opening with no
        # ordinal word, stands silent at its recorded
        # reading.
        data = _joined("### DQ-001: First question with words",
                       "### DQ-002: Budget review", _BODY_ONE)
        _assert_no_signal(self, data, "fix11_a_v04.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_m17_ordinal_past_twenty_bound_no_signal(self):
        # Seat 1 observation O-11-1-1: numbers past the
        # twentieth carry no ordinal word under the cured
        # reading, at its stated bound.
        data = _kjoined("### DQ-020: Twentieth question",
                        "### DQ-021: Completely unrelated",
                        _KBODY)
        _assert_no_signal(self, data, "fix11_a_m17.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
