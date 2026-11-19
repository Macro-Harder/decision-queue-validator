"""Step 17 fix wave 10, Fix Seat A: Cluster A, the title family.

Charges CH-226 to CH-233, as ruled at section 83 of
design/steps/step-17r-record.md under ruling (a), against
round 10 attack seat 1 findings A10-1-F1 to A10-1-F5
(paper at design/steps/step-17r-r10-seat01.md) and round
10 attack seat 3 findings A10-3-F1 to A10-3-F5 (paper at
design/steps/step-17r-r10-seat03.md), consolidated at
section 2.1 and Cluster A of the round 10 triage
preparation (design/steps/step-17r-r10-triage-prep.md).
Locus: parse.py, the CH-96 split scan title limb as cured
at CH-191 and CH-192, the helper
_joined_part_is_title_matter and the body count helper
beside it.

CH-226 (Medium): a genuine joined heading whose title
exceeds its host segment's by six words beside the one
shared body is suppressed at clean exit 0 (seat 3 cases
u01 and u01b; seat 1 case k05, the bound contact of seat
1 observation O-10-1-1, charged by ruling (a) of section
83, its cure stating the title bound expressly per limb).
CH-227 (Medium): a genuine joined heading whose number
is not the next number is suppressed beside two standing
bodies, the skipped entry standing later (seat 1 case
k07, seat 3 case u02). CH-228 (Medium): the shared word
condition read on split tokens suppresses a genuine
joined heading whose title stands in its host segment's
own title terms under any other reading (seat 1 cases
k01 to k04 and k11). CH-229 (Medium): a genuine joined
heading sharing no word with its host segment's title is
read as title matter by the single shared body limb
(seat 3 cases u05 and u05b). CH-230 (Medium): a measured
segment title inflated by an embedded space joined fake
suppresses a genuine joined heading (seat 1 case k08,
control k09). CH-231 (Medium): a heading shaped part
inside a title fires where no body stands behind it, one
step past the limb's conditions (seat 1 cases k12 and
k13; seat 3 cases u11, u12, and u14). CH-232 (Medium):
the long title limb fires on a heading shaped part inside
a title at eight words of excess beside the host's own
body (seat 3 case u15). CH-233 (Low): a near marker line
inside the host's own body raises the span body count to
two and the title part fires (seat 1 case k14).

The pin class states the governed readings the cures must
hold: the CH-191 and CH-192 charged forms and controls at
their cured readings (t01 to t07, t16 standing in the fix
wave 9 module run whole beside this one), the CH-192
title parts t04, t06, and t17 silent, the CH-156 pin s02
and the twin form s01 signalled, the held chain forms
t08 to t11, the CH-115 title pins r23 and r24, the held
form s32, the s26 neighbour bound, the seat 1 neighbour
forms j09 to j11 signalled, and the seat 1 stated bound
forms k15 and k16 firing, k17 silent, k06 and k10 at
their recorded readings.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

LS = " "
ZWSP = "​"

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
_NEAR = ("Status: BankedX\n\n"
         "This question is waiting for a decision.\n")
_KHEAD = "# Decision queue\n\n"


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


def _kjoined(first, joined, body):
    text = _KHEAD + first + LS + joined + "\n" + body
    return text.encode("utf-8")


_KNEAR_BODY = ("\nStatus: BankedX\n\n"
               "This question is waiting for a decision.\n")


# ---------------------------------------------------------------------
# CH-226: a genuine joined heading at six words of excess
# beside the one shared body takes its signal
# ---------------------------------------------------------------------

class Step17Fix10A226ExcessSixTest(unittest.TestCase):
    """CH-226, T10-01 (seat 3 A10-3-F1 with seat 1 case
    k05): the long title limb's bound, stated expressly
    per limb by the cure, stands at six words of excess
    beside the one shared body."""

    def test_u01_genuine_excess_six_one_body_signalled(self):
        # Seat 3 case u01: host First question, two words,
        # joined title eight words, one shared body; before
        # the cure headed entries read 1 at clean exit 0.
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question with several more "
            "words in title", _BODY_ONE)
        _assert_signalled(
            self, data, "fix10_a_u01.md",
            "DQ-002: Second question with several more "
            "words in title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_u01b_genuine_excess_six_second_heading_signalled(self):
        # Seat 3 case u01b: the same excess standing on the
        # second heading line of the two entry control.
        data = TWO.replace(
            "### DQ-002: Second question\n",
            "### DQ-002: Second question" + LS +
            "### DQ-003: Third question with several more "
            "words in title\n").encode("utf-8")
        _assert_signalled(
            self, data, "fix10_a_u01b.md",
            "DQ-003: Third question with several more "
            "words in title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_k05_genuine_excess_six_near_body_signalled(self):
        # Seat 1 case k05: host title Short, one word,
        # joined title seven words, the near marker body
        # standing behind the line; the bound contact of
        # observation O-10-1-1, charged at CH-226.
        data = _kjoined(
            "### DQ-001: Short",
            "### DQ-002: A much longer second open "
            "question title", _KNEAR_BODY)
        _assert_signalled(
            self, data, "fix10_a_k05.md",
            "DQ-002: A much longer second open question "
            "title")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-227: a genuine joined heading whose number is not
# the next number, beside two standing bodies, the
# skipped entry standing later, takes its signal
# ---------------------------------------------------------------------

class Step17Fix10A227NotNextTwoBodiesTest(unittest.TestCase):
    """CH-227, T10-02 (seat 1 A10-1-F3 with seat 3
    A10-3-F3): the two body limb at the number after
    next, where the skipped number stands as a complete
    entry later in the file."""

    def test_u02_genuine_nonnext_two_bodies_signalled(self):
        # Seat 3 case u02: host DQ-001 joined to DQ-003,
        # two bodies standing, a complete DQ-002 entry
        # standing after them; before the cure no PIN-06
        # stood anywhere in the report.
        data = (_HEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Third question plus\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE +
                "\n### DQ-002: Second question\n\n" +
                _BODY_TWO).encode("utf-8")
        _assert_signalled(
            self, data, "fix10_a_u02.md",
            "DQ-003: Third question plus")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_k07_genuine_long_nonnext_two_bodies_signalled(self):
        # Seat 1 case k07: the same joint with a ten word
        # joined title; before the cure the run stood at
        # exit 1 on rule 9 findings only, no PIN-06.
        data = (_KHEAD + "### DQ-001: First question" + LS +
                "### DQ-003: Third question with several "
                "more words in its title here\n\n" +
                _BODY_ONE + "\n" + _BODY_THREE +
                "\n### DQ-002: Second question\n\n" +
                _BODY_TWO).encode("utf-8")
        _assert_signalled(
            self, data, "fix10_a_k07.md",
            "DQ-003: Third question with several more "
            "words in its title here")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-228: the shared word condition read as titles are
# read, not on split tokens
# ---------------------------------------------------------------------

class Step17Fix10A228SharedWordReadingTest(unittest.TestCase):
    """CH-228, T10-03 (seat 1 A10-1-F1): a genuine joined
    heading whose title stands in its host segment's own
    title terms under the reading the heading readers
    take, on letter case, on sentence punctuation, and on
    hyphenation, takes its signal."""

    def test_k01_case_share_signalled(self):
        data = _kjoined(
            "### DQ-001: First question",
            "### DQ-002: Second Question", _KNEAR_BODY)
        _assert_signalled(self, data, "fix10_a_k01.md",
                          "DQ-002: Second Question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_k02_punct_share_part_signalled(self):
        data = _kjoined(
            "### DQ-001: First question",
            "### DQ-002: Second question.", _KNEAR_BODY)
        _assert_signalled(self, data, "fix10_a_k02.md",
                          "DQ-002: Second question.")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_k03_punct_share_segment_signalled(self):
        data = _kjoined(
            "### DQ-001: First question.",
            "### DQ-002: Second question", _KNEAR_BODY)
        _assert_signalled(self, data, "fix10_a_k03.md",
                          "DQ-002: Second question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_k04_hyphen_share_signalled(self):
        data = _kjoined(
            "### DQ-001: First open-question",
            "### DQ-002: Second open question", _KNEAR_BODY)
        _assert_signalled(self, data, "fix10_a_k04.md",
                          "DQ-002: Second open question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_k11_case_share_second_entry_signalled(self):
        # Seat 1 case k11: the k01 form standing at the
        # second entry position of the file.
        first_entry = ("### DQ-001: A sample open question\n"
                       "\nStatus: BankedX\n\n"
                       "This question is waiting for a "
                       "decision.\n")
        data = (_KHEAD + first_entry +
                "\n### DQ-002: First question" + LS +
                "### DQ-003: Second Question\n" +
                _KNEAR_BODY).encode("utf-8")
        _assert_signalled(self, data, "fix10_a_k11.md",
                          "DQ-003: Second Question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-229: a genuine joined heading sharing no word with
# its host segment's title takes its signal
# ---------------------------------------------------------------------

class Step17Fix10A229NoSharedWordTest(unittest.TestCase):
    """CH-229, T10-04 (seat 3 A10-3-F2): the single
    shared body limb reads no genuine joined heading as
    title matter on the charged constructions, whose
    titles open with the ordinal word of their own
    number."""

    def test_u05_genuine_noshare_equal_signalled(self):
        # Seat 3 case u05: host First question, joined
        # Second entry, two words against two, no word
        # shared, one shared body; before the cure the
        # entry stood deleted at clean exit 0.
        data = _joined("### DQ-001: First question",
                       "### DQ-002: Second entry", _BODY_ONE)
        _assert_signalled(self, data, "fix10_a_u05.md",
                          "DQ-002: Second entry")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_u05b_genuine_noshare_longer_host_signalled(self):
        # Seat 3 case u05b: four words against four, no
        # word shared, one shared body.
        data = _joined(
            "### DQ-001: First question with words",
            "### DQ-002: Second entry here now", _BODY_ONE)
        _assert_signalled(self, data, "fix10_a_u05b.md",
                          "DQ-002: Second entry here now")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-230: the segment the test measures is read without
# the space joined fake embedded in its title
# ---------------------------------------------------------------------

class Step17Fix10A230InflatedSegmentTest(unittest.TestCase):
    """CH-230, T10-05 (seat 1 A10-1-F2): a genuine joined
    heading standing behind a segment whose own title
    carries a space joined heading shaped fake takes the
    signal it takes against the host heading as written,
    as the control k09 states."""

    def test_k08_inflated_segment_signalled(self):
        data = _kjoined(
            "### DQ-001: First question about ### DQ-009: "
            "Not a real entry at all here",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KNEAR_BODY)
        _assert_signalled(
            self, data, "fix10_a_k08.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_k09_inflated_segment_control_signalled(self):
        # Seat 1 control k09: the same genuine part joined
        # to the host heading as written without the
        # embedded fragment; the PIN-06 signal stands, as
        # before the cure.
        data = _kjoined(
            "### DQ-001: First question",
            "### DQ-002: Second open matter waiting for "
            "decision under review today", _KNEAR_BODY)
        _assert_signalled(
            self, data, "fix10_a_k09.md",
            "DQ-002: Second open matter waiting for "
            "decision under review today")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# CH-231: a heading shaped part inside a title, one step
# past the single shared body limb's conditions, takes
# no signal
# ---------------------------------------------------------------------

class Step17Fix10A231FalseFireStepPastTest(unittest.TestCase):
    """CH-231, T10-06 (seat 1 A10-1-F4 with seat 3
    A10-3-F4): the scan fires on no title part on the
    charged forms, at the shared word condition read as
    titles are read, at the two word condition read as
    titles are read, and at the span body count standing
    at two on the host entry's own occurrences."""

    def test_u11_fake_wholly_in_segment_title_no_signal(self):
        # Seat 3 case u11: the part Sample question, every
        # word of its title standing in the host segment's
        # own title terms, the one body the host's own.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Sample question").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_u11.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_u12_fake_one_word_full_body_no_signal(self):
        # Seat 3 case u12: the part Notreal, one word as
        # written, beside the host heading's own full
        # body standing in the span.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Notreal").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_u12.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_u14_fake_two_status_in_host_span_no_signal(self):
        # Seat 3 case u14: the part Not real meeting every
        # condition of the limb, with two Status
        # occurrences standing in the host entry's own
        # span, the second at the span's end.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Not real").encode("utf-8")
        data = data + "\nStatus: Banked\n".encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_u14.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_k12_hyphen_fake_no_signal(self):
        # Seat 1 case k12: the part Not-real, its two
        # words joined by a hyphen, against a segment of
        # eight words, the near marker body standing.
        data = _kjoined(
            "### DQ-001: A sample open question with many "
            "more words",
            "### DQ-002: Not-real", _KNEAR_BODY)
        _assert_no_signal(self, data, "fix10_a_k12.md", 1)

    def test_k13_zwsp_fake_no_signal(self):
        # Seat 1 case k13: the part Not real with a zero
        # width space standing between its two words.
        data = _kjoined(
            "### DQ-001: A sample open question with many "
            "more words",
            "### DQ-002: Not" + ZWSP + "real", _KNEAR_BODY)
        _assert_no_signal(self, data, "fix10_a_k13.md", 1)


# ---------------------------------------------------------------------
# CH-232: the long title limb at eight words of excess
# beside the host's own body fires on no title part
# ---------------------------------------------------------------------

class Step17Fix10A232ExcessEightTest(unittest.TestCase):
    """CH-232, T10-07 (seat 3 A10-3-F5): the long title
    limb's bound, stated expressly per limb by the cure,
    stands at six or seven words of excess beside the
    one shared body; at eight words of excess the part
    stands as title matter."""

    def test_u15_fake_excess_eight_no_signal(self):
        # Seat 3 case u15: host segment A sample, two
        # words, the part's title ten words, the one body
        # in the span the host heading's own; before the
        # cure the run exited 1 on the PIN-06 Warning.
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry heading at all "
            "in this title").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_u15.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------
# CH-233: a near marker line inside the host's own body
# raises no body count against the title limb
# ---------------------------------------------------------------------

class Step17Fix10A233NearMarkerBodyCountTest(unittest.TestCase):
    """CH-233, T10-24 (seat 1 A10-1-F5): a title part
    meeting every other condition of the single shared
    body limb takes no signal where the span's second
    occurrence is a near marker line standing at the
    span's end inside the host entry's own body; the
    file's rule 2 finding on that line stands."""

    def test_k14_fake_two_bodies_near_marker_no_signal(self):
        data = _kjoined(
            "### DQ-001: A sample open question with many "
            "more words",
            "### DQ-002: Not real",
            _KNEAR_BODY + "\nStatus : BankedX\n")
        _assert_no_signal(self, data, "fix10_a_k14.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------
# Governing pins on this surface, in both directions
# ---------------------------------------------------------------------

class Step17Fix10APinTest(unittest.TestCase):
    """The cured readings of fix waves 8 and 9 on this
    surface and the stated bound forms of the round 10
    papers, standing whole beside the charges."""

    def test_t02_genuine_excess_seven_signalled(self):
        # The CH-191 charged form at the long title limb's
        # own figure: excess seven beside the one body.
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question with several more "
            "words in its title", _BODY_ONE)
        _assert_signalled(
            self, data, "fix10_a_t02.md",
            "DQ-002: Second question with several more "
            "words in its title")

    def test_t05_fake_excess_one_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with "
            "words" + LS +
            "### DQ-002: Not a real entry at all here"
            ).encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_t05.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t04_fake_short_title_long_host_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample open question with many "
            "more words" + LS +
            "### DQ-002: Not real").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_t04.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t06_fake_equal_titles_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not real").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_t06.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t17_fake_short_title_second_heading_no_signal(self):
        data = TWO.replace(
            "### DQ-002: Second question",
            "### DQ-002: Second question with many more "
            "words" + LS +
            "### DQ-003: Not real").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_t17.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_s02_differing_single_body_signalled(self):
        # The governing CH-156 pin: a genuine differing
        # joined heading on one shared body whose title
        # stands in the host segment's own title terms.
        data = _joined("### DQ-001: First question",
                       "### DQ-002: Second question", _BODY_ONE)
        _assert_signalled(self, data, "fix10_a_s02.md",
                          "DQ-002: Second question")

    def test_u06_genuine_share_equal_control_signalled(self):
        data = _joined("### DQ-001: First question",
                       "### DQ-002: Second question", _BODY_ONE)
        _assert_signalled(self, data, "fix10_a_u06.md",
                          "DQ-002: Second question")
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 1)

    def test_j09_short_host_long_join_signalled(self):
        data = _joined(
            "### DQ-001: Short",
            "### DQ-002: A much longer second open "
            "question title here",
            "Status: BankedX\n\n"
            "This question is waiting for a decision.\n")
        _assert_signalled(
            self, data, "fix10_a_j09.md",
            "DQ-002: A much longer second open question "
            "title here")

    def test_j10_long_host_short_join_signalled(self):
        data = _joined(
            "### DQ-001: A much longer first open question "
            "title here",
            "### DQ-002: Short",
            "Status: BankedX\n\n"
            "This question is waiting for a decision.\n")
        _assert_signalled(self, data, "fix10_a_j10.md",
                          "DQ-002: Short")

    def test_j11_equal_titles_join_signalled(self):
        data = _joined(
            "### DQ-001: A sample open question",
            "### DQ-002: A sample open question",
            "Status: BankedX\n\n"
            "This question is waiting for a decision.\n")
        _assert_signalled(
            self, data, "fix10_a_j11.md",
            "DQ-002: A sample open question")

    def test_t01_genuine_long_title_two_bodies_signalled(self):
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question with several more "
            "words in its title",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(
            self, data, "fix10_a_t01.md",
            "DQ-002: Second question with several more "
            "words in its title")

    def test_t03_genuine_equal_titles_two_bodies_signalled(self):
        data = _joined("### DQ-001: First question",
                       "### DQ-002: Second question",
                       _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix10_a_t03.md",
                          "DQ-002: Second question")

    def test_t07_genuine_short_title_two_bodies_signalled(self):
        data = _joined(
            "### DQ-001: First question with words",
            "### DQ-002: Second",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix10_a_t07.md",
                          "DQ-002: Second")

    def test_t08_chain_fake_then_genuine_held(self):
        data = _joined(
            "### DQ-001: First question",
            "### DQ-009: Not a real entry with a long "
            "title here" + LS + "### DQ-002: Second question",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix10_a_t08.md",
                          "DQ-002: Second question")

    def test_t09_chain_genuine_then_fake_held(self):
        data = _joined(
            "### DQ-001: First question",
            "### DQ-002: Second question" + LS +
            "### DQ-009: Not a real entry with a long "
            "title here",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix10_a_t09.md",
                          "DQ-002: Second question")

    def test_t10_plain_part_then_fake_held(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "some plain words" + LS +
            "### DQ-002: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_t10.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_t11_plain_part_then_genuine_held(self):
        data = _joined(
            "### DQ-001: First question with many words",
            "some plain words" + LS + "### DQ-002: Second",
            _BODY_ONE + "\n" + _BODY_THREE)
        _assert_signalled(self, data, "fix10_a_t11.md",
                          "DQ-002: Second")

    def test_r23_title_join_first_heading_no_signal(self):
        data = BASE.replace(
            "### DQ-001: A sample open question",
            "### DQ-001: A sample" + LS +
            "### DQ-002: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_r23.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_r24_title_join_second_heading_no_signal(self):
        data = TWO.replace(
            "### DQ-002: Second question",
            "### DQ-002: Second" + LS +
            "### DQ-003: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_r24.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_s32_own_heading_join_title_fake_no_signal(self):
        data = TWO.replace(
            "### DQ-002: Second question",
            "\x0b### DQ-002: Second question" + LS +
            "### DQ-009: Not a real entry").encode("utf-8")
        _assert_no_signal(self, data, "fix10_a_s32.md", 2)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_s01_twin_single_body_signalled(self):
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question\n").encode(
                "utf-8")
        _assert_signalled(
            self, data, "fix10_a_s01.md",
            "DQ-002: A sample open question")

    def test_s26_comment_opener_in_joined_title_bounded(self):
        # Bounded expressly as the fix wave 8 K3 module
        # states it: no PIN-06 signal, the file at exit 1
        # on other findings with headed entries 1.
        data = BASE.replace(
            "### DQ-001: A sample open question\n",
            "### DQ-001: A sample open question" + LS +
            "### DQ-002: A sample open question <!-- x\n"
            ).encode("utf-8")
        data = data + ("\n\nStatus: Banked\n\n"
                       "Question: Which option should we "
                       "take?\n\n"
                       "Options: Option A, Option B\n\n"
                       "Cost of deciding late: Work stays "
                       "blocked.\n\n"
                       "Blocks: DQ-002\n\n"
                       "This question is waiting for a "
                       "decision.\n").encode("utf-8")
        model, output = h.run_pipeline(data, "fix10_a_s26.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_pin06(output), [])
        self.assertEqual(int(h.entry_total(output)), 1)
        for sub in ("validate", "render"):
            code, _out = _cli(data, sub)
            self.assertEqual(code, 1)

    def test_k15_fake_shared_word_bound_fires(self):
        # Seat 1 observation O-10-1-2, the stated bound
        # form: a fake sharing a word with its segment, its
        # title not standing wholly in the segment's own
        # title terms, fires, as the cured test states.
        data = _kjoined(
            "### DQ-001: A sample open question",
            "### DQ-002: Second question", _KNEAR_BODY)
        _assert_signalled(self, data, "fix10_a_k15.md",
                          "DQ-002: Second question")

    def test_k16_fake_one_word_bound_fires(self):
        # Seat 1 observation O-10-1-2, the stated bound
        # form: a one word fake beside a near marker body
        # fires, as the cured test states.
        data = _kjoined(
            "### DQ-001: A sample open question with many "
            "more words",
            "### DQ-002: Scope", _KNEAR_BODY)
        _assert_signalled(self, data, "fix10_a_k16.md",
                          "DQ-002: Scope")

    def test_k17_fake_case_differs_no_signal(self):
        # Seat 1 case k17: a title fake written in lower
        # case against a capitalised segment title stays
        # silent, the cured CH-192 direction holding.
        data = _kjoined(
            "### DQ-001: A sample open question",
            "### DQ-002: not real", _KNEAR_BODY)
        _assert_no_signal(self, data, "fix10_a_k17.md", 1)
        code, _out = _cli(data, "validate")
        self.assertEqual(code, 0)

    def test_k18_hyphen_control_signalled(self):
        data = _kjoined(
            "### DQ-001: First open question",
            "### DQ-002: Second open question", _KNEAR_BODY)
        _assert_signalled(self, data, "fix10_a_k18.md",
                          "DQ-002: Second open question")

    def test_k06_long_nonnext_one_body_signalled(self):
        # Seat 1 control k06: a genuine part at seven
        # words of excess beside one body signals even
        # where its number is not the next number, the
        # long title limb carrying no number condition.
        data = _kjoined(
            "### DQ-001: First question",
            "### DQ-003: Second question with several more "
            "words in its title", _KNEAR_BODY)
        _assert_signalled(
            self, data, "fix10_a_k06.md",
            "DQ-003: Second question with several more "
            "words in its title")

    def test_k10_unnumbered_segment_genuine_signalled(self):
        # Seat 1 observation O-10-1-3 at its recorded
        # reading: the genuine part behind an unnumbered
        # segment takes its signal against the host
        # segment before it.
        data = (_KHEAD +
                "### DQ-001: A sample open question" + LS +
                "### Interlude" + LS +
                "### DQ-002: Second open question here\n" +
                _KNEAR_BODY).encode("utf-8")
        _assert_signalled(
            self, data, "fix10_a_k10.md",
            "DQ-002: Second open question here")


if __name__ == "__main__":
    unittest.main()
