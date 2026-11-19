"""Step 17 fix wave 10, Fix Seat G tests, test first.

Charges CH-257 to CH-263, the strip set family of
round 10 (Cluster G of design/steps/
step-17r-r10-triage-prep.md, ruled TO FIX at section
83 of design/steps/step-17r-record.md, ruling (a)
for the charges as filed and ruling (g) for the
step past forms of CH-262), sourced at round 10
attack seat 2, design/steps/step-17r-r10-seat02.md
(ATK10-2-01 to ATK10-2-06), and round 10 attack
seat 13, design/steps/step-17r-r10-seat13.md
(F-1 to F-5), consolidated as T10-34 to T10-40.
Locus: product/decision_queue_validator/parse.py
only, at _final_line_is_cut_off and
_labelled_value_stands_whole, the sentence close
readings as cured at CH-215 to CH-218.

CH-257 (Low), T10-34, the closing character ring.
A sentence closing on a closing character of the
next neighbour ring outside the cured strip set is
read as cut, in the prose branch and in the
sentence valued labelled branch alike: the left
guillemet (U+00AB), the single left guillemet
(U+2039), the closing white corner bracket
(U+300F), the closing black lenticular bracket
(U+3011), the fullwidth closing bracket (U+FF3D),
the fullwidth closing brace (U+FF5D), the tilde
of a strikethrough span, and the closing angle
bracket (U+27E9). Cure bound: the strip set of
each branch carries exactly those charged
characters beside the standing members; a line
closing on one of them that closes no sentence
stands cut in either branch.

CH-258 (Low), T10-35, the sentence close marks.
A sentence closing on a sentence close mark
outside the CH-218 set is read as cut, in both
branches alike: the ideographic full stop
(U+3002), the fullwidth exclamation mark
(U+FF01), the fullwidth question mark (U+FF1F),
the fullwidth full stop (U+FF0E), the interrobang
(U+203D), the two dot leader (U+2025), and the
midline horizontal ellipsis (U+22EF). Cure bound:
each mark stands as a sentence closing mark on
every sentence close test of both branches, the
standing order test and the probe alike.

CH-259 (Low), T10-36, the titlecase roman tens.
Complete bullet items under titlecase roman
numerals of the sixty to eighty nine family,
Lx. and its dresses and Lxiv., are read as cut.
The titlecase alternatives carry the tens family
in the forms Xc, Xl, Xx, and a bare L, beside the
hundreds and units forms; no titlecase alternative
carries a capital L followed by a lower case x.
Cure bound: the titlecase tens alternatives carry
the Lx family (Lx, Lxx, Lxxx) beside the standing
forms, in every closing form the set reaches,
under the same fragment, joining word, and cut
reference guards the standing markers take.

CH-260 (Low), T10-37, the roman case mixes.
Complete bullet items under roman numeral case
mixes beyond the titlecase form, the marker iV in
its dresses and the marker vI, are read as cut.
Cure bound: each roman alternative set carries a
mixed case form of the standard numeral (each
letter of the numeral in either case) beside the
standing cases, in every closing form the set
reaches, under the same guards. A form that is
no standard numeral in any case (IvX among them)
matches no alternative and stands outside this
cure, as it stood outside CH-216.

CH-261 (Low), T10-38, the group strip behind the
other closing characters. A final line closing on
a balanced bracket group standing behind a
closing character of the cured set other than the
right guillemet, or behind a run and a right
guillemet, is read as cut. The bracket group
reading strips only the standing quote characters
and the right guillemet from the line end. Cure
bound: that strip disregards, in alternation with
a trailing run, exactly the charged members
beside its standing members: the single
guillemet, the asterisk, the underscore, the
backtick, the left double quotation mark, the
fullwidth closing parenthesis, and the closing
corner bracket. No ASCII closing bracket joins
the strip, so a group standing last keeps its own
closing bracket.

CH-262 (Low), T10-39, the step past forms of the
p17 bound, ruled charged at record section 83
ruling (g). A bracket group form one step past
the p17 bound is read as cut: a labelled group
behind an interleaved run and a right guillemet,
the same behind a single guillemet, the p17 shape
itself in the prose branch (a group behind an
interleaved run and a closing double quote), and
seat 2's routed observation form, a labelled
group behind a right guillemet alone. Cure bound:
the labelled branch's bracket group reading takes
a probe on the value as written, disregarding in
alternation a trailing run and the two guillemet
forms alone, and the prose branch's group strip
under CH-261 disregards the run in alternation,
which reaches its charged member. The p17 form
itself (a labelled group behind an interleaved
run and a closing double quote) stands unmoved
at 4, 4 beside its twin at 1, 1, at its section
81 ruling (f) bound, pinned here in both eras:
the probe's strip carries no quote character, so
the form as written takes no probe reading.

CH-263 (Low), T10-40, the single character roman
markers. Complete bullet items under the single
character Unicode roman numeral markers are read
as cut: the capital roman numeral four (U+2163)
in the full stop form, and the small roman
numeral four (U+2173) in the closing parenthesis
form, the attack case bytes governing over the
seat 2 paper's prose, which names the second
marker a three where its bytes carry the four.
Cure bound: the bullet marker set carries the
single character roman numerals (U+2160 to
U+216B and U+2170 to U+217B) in the full stop
form and in the closing parenthesis and bracket
form, under the same guards.

Constructions stand in the attack papers' own
shapes, on the template family of the round 3 to
round 10 papers. Seat 2's constructions stand
byte for byte as its attack case files stand,
each asserted at its recorded byte count and
sha256 head as construction facts. Seat 13's
constructions stand in its paper's shapes on the
same template. An entry stands whole where it
takes no unparsed marker and no rule 12 finding,
and cut where it takes both.

Copyright: J.P. Picard aka Macro-Harder
"""

import hashlib
import unittest

import dqv_harness as h

_HEAD = [
    "# Decision queue", "",
    "### DQ-001: Sample question", "",
    "Status: Banked", "",
    "This question is waiting for a decision.", "",
]
_QUESTION = "Question: Which option should we take first?"
_OPTIONS = "Options: Option A, Option B"
_COST = "Cost of deciding late: Work stays blocked."
_BLOCKS = "Blocks: DQ-002"
_FULL = [_QUESTION, _OPTIONS, _COST, _BLOCKS]

_LEFT_GUILLEMET = "«"
_SINGLE_LEFT_GUILLEMET = "‹"
_WHITE_CORNER_CLOSE = "』"
_LENTICULAR_CLOSE = "】"
_FULLWIDTH_BRACKET_CLOSE = "］"
_FULLWIDTH_BRACE_CLOSE = "｝"
_ANGLE_CLOSE = "⟩"
_IDEOGRAPHIC_STOP = "。"
_FULLWIDTH_EXCLAMATION = "！"
_FULLWIDTH_QUESTION = "？"
_FULLWIDTH_STOP = "．"
_INTERROBANG = "‽"
_TWO_DOT_LEADER = "‥"
_MIDLINE_ELLIPSIS = "⋯"
_SINGLE_GUILLEMET = "›"
_GUILLEMET = "»"
_LEFT_DOUBLE_QUOTE = "“"
_FULLWIDTH_CLOSE = "）"
_CORNER_CLOSE = "」"
_ZWSP = "​"
_CAP_ROMAN_FOUR = "Ⅳ"
_SMALL_ROMAN_FOUR = "ⅳ"

_PROSE = "Work stays blocked until the ruling lands."
_PROSE_NO_CLOSE = "Work stays blocked until the ruling lands"
_COST_VALUE = "Work stays blocked."
_GROUP_LINE = "The note stands (as the appendix records)"
_BULLET_CONTENT = "Option B leaves the note adopted"


def _case(middle, final_line):
    lines = list(_HEAD)
    for line in middle:
        lines += [line, ""]
    lines.append(final_line)
    return "\n".join(lines).encode("utf-8")


def _twin(data):
    return data + b"\n"


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


def _assert_charged(test, data, byte_count, sha_head):
    test.assertEqual(len(data), byte_count)
    test.assertTrue(
        hashlib.sha256(data).hexdigest().startswith(sha_head),
        "construction hash head moved: " + sha_head)


# ---------------------------------------------------------------------
# CH-257: the closing character ring (ATK10-2-01 and F-1, T10-34)
# ---------------------------------------------------------------------

class Step17Fix10GClosingRingTest(unittest.TestCase):
    """CH-257: a sentence closing behind a closing
    character of the charged next neighbour ring
    stands whole, in the prose branch and in the
    sentence valued labelled branch alike. The cut
    side is stated in each branch: a closing
    character of the ring rescues no line that
    closes no sentence."""

    def test_q01_prose_left_guillemet_stands_whole(self):
        data = _case(_FULL, _PROSE + _LEFT_GUILLEMET)
        _assert_charged(self, data, 284, "2a57ae2bd2ab")
        _assert_whole(self, data, "fix10_g_q01.md")
        _assert_whole(self, _twin(data), "fix10_g_q01_twin.md")

    def test_q02_cost_left_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked."
            + _LEFT_GUILLEMET)
        _assert_charged(self, data, 284, "938ecca2c131")
        _assert_whole(self, data, "fix10_g_q02.md")
        _assert_whole(self, _twin(data), "fix10_g_q02_twin.md")

    def test_q03_prose_single_left_guillemet_stands_whole(self):
        data = _case(_FULL, _PROSE + _SINGLE_LEFT_GUILLEMET)
        _assert_charged(self, data, 285, "05f23964d8c6")
        _assert_whole(self, data, "fix10_g_q03.md")
        _assert_whole(self, _twin(data), "fix10_g_q03_twin.md")

    def test_q04_prose_white_corner_bracket_stands_whole(self):
        data = _case(
            _FULL,
            "『" + _PROSE + _WHITE_CORNER_CLOSE)
        _assert_charged(self, data, 288, "d2676656aa8a")
        _assert_whole(self, data, "fix10_g_q04.md")
        _assert_whole(self, _twin(data), "fix10_g_q04_twin.md")

    def test_q05_prose_black_lenticular_stands_whole(self):
        data = _case(
            _FULL,
            "【" + _PROSE + _LENTICULAR_CLOSE)
        _assert_charged(self, data, 288, "adaff6c4ac5d")
        _assert_whole(self, data, "fix10_g_q05.md")
        _assert_whole(self, _twin(data), "fix10_g_q05_twin.md")

    def test_q06_prose_fullwidth_bracket_stands_whole(self):
        data = _case(
            _FULL,
            "［" + _PROSE + _FULLWIDTH_BRACKET_CLOSE)
        _assert_charged(self, data, 288, "1bd7c3df24d2")
        _assert_whole(self, data, "fix10_g_q06.md")
        _assert_whole(self, _twin(data), "fix10_g_q06_twin.md")

    def test_q07_cost_fullwidth_brace_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: ｛Work stays blocked."
            + _FULLWIDTH_BRACE_CLOSE)
        _assert_charged(self, data, 288, "e1306356b880")
        _assert_whole(self, data, "fix10_g_q07.md")
        _assert_whole(self, _twin(data), "fix10_g_q07_twin.md")

    def test_q08_prose_tilde_span_stands_whole(self):
        data = _case(
            _FULL,
            "~~" + _PROSE + "~~")
        _assert_charged(self, data, 286, "a365e5835927")
        _assert_whole(self, data, "fix10_g_q08.md")
        _assert_whole(self, _twin(data), "fix10_g_q08_twin.md")

    def test_q09_question_left_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Question: Which option should we take first?"
            + _LEFT_GUILLEMET)
        _assert_charged(self, data, 286, "15064e5e77fa")
        _assert_whole(self, data, "fix10_g_q09.md")
        _assert_whole(self, _twin(data), "fix10_g_q09_twin.md")

    def test_q10_prose_angle_bracket_stands_whole(self):
        data = _case(
            _FULL,
            "⟨" + _PROSE + _ANGLE_CLOSE)
        _assert_charged(self, data, 288, "bc0496fb0e56")
        _assert_whole(self, data, "fix10_g_q10.md")
        _assert_whole(self, _twin(data), "fix10_g_q10_twin.md")

    def test_s13_cost_white_corner_bracket_stands_whole(self):
        # Seat 13 F-1 case q02, in its paper's shape on
        # this template: the labelled branch member of
        # the white corner bracket pair.
        data = _case(
            _FULL,
            "Cost of deciding late: 『Work stays blocked."
            + _WHITE_CORNER_CLOSE)
        _assert_whole(self, data, "fix10_g_s13_q02.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q02_twin.md")

    def test_s13_cost_fullwidth_bracket_stands_whole(self):
        # Seat 13 F-1 case q05, in its paper's shape:
        # the labelled branch member of the fullwidth
        # bracket pair.
        data = _case(
            _FULL,
            "Cost of deciding late: ［Work stays blocked."
            + _FULLWIDTH_BRACKET_CLOSE)
        _assert_whole(self, data, "fix10_g_s13_q05.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q05_twin.md")

    def test_s13_cost_tilde_span_stands_whole(self):
        # Seat 13 F-1 case q10, in its paper's shape:
        # the labelled branch member of the tilde span.
        data = _case(
            _FULL,
            "Cost of deciding late: ~~Work stays blocked.~~")
        _assert_whole(self, data, "fix10_g_s13_q10.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q10_twin.md")

    def test_q41_prose_left_guillemet_no_close_stands_cut(self):
        # Cut side, seat 2 case q41, prose branch: the
        # line closes on the left guillemet and closes
        # no sentence behind it.
        data = _case(_FULL, _PROSE_NO_CLOSE + _LEFT_GUILLEMET)
        _assert_charged(self, data, 283, "b2f0ea8b1f5c")
        _assert_cut(self, data, "fix10_g_q41.md")

    def test_cost_left_guillemet_no_close_stands_cut(self):
        # Cut side, sentence valued labelled branch.
        _assert_cut(
            self,
            _case(_FULL,
                  "Cost of deciding late: Work stays blocked"
                  + _LEFT_GUILLEMET),
            "fix10_g_cost_guillemet_no_close.md")

    def test_prose_tilde_span_no_close_stands_cut(self):
        # Cut side, prose branch: the tilde span closes
        # and no sentence closes inside it.
        _assert_cut(
            self,
            _case(_FULL,
                  "~~Work stays blocked until the ruling "
                  "lands~~"),
            "fix10_g_tilde_no_close.md")

    def test_cured_single_guillemet_pin_stands_whole(self):
        # Pin: the CH-215 member stands whole in both
        # eras, on the widened set this cure extends.
        data = _case(_FULL, _PROSE + _SINGLE_GUILLEMET)
        _assert_whole(self, data, "fix10_g_pin_sg.md")
        _assert_whole(self, _twin(data), "fix10_g_pin_sg_twin.md")


# ---------------------------------------------------------------------
# CH-258: the sentence close marks (ATK10-2-02, ATK10-2-03, F-2, T10-35)
# ---------------------------------------------------------------------

class Step17Fix10GCloseMarksTest(unittest.TestCase):
    """CH-258: a sentence closing on a sentence close
    mark of the charged sibling set stands whole, in
    the prose branch and in the sentence valued
    labelled branch alike."""

    def test_q11_prose_ideographic_stop_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands"
            + _IDEOGRAPHIC_STOP)
        _assert_charged(self, data, 284, "bc16ed46541b")
        _assert_whole(self, data, "fix10_g_q11.md")
        _assert_whole(self, _twin(data), "fix10_g_q11_twin.md")

    def test_q12_cost_ideographic_stop_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked"
            + _IDEOGRAPHIC_STOP)
        _assert_charged(self, data, 284, "b86e3fd3331f")
        _assert_whole(self, data, "fix10_g_q12.md")
        _assert_whole(self, _twin(data), "fix10_g_q12_twin.md")

    def test_q13_prose_fullwidth_exclamation_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands"
            + _FULLWIDTH_EXCLAMATION)
        _assert_charged(self, data, 284, "7c8322650ff5")
        _assert_whole(self, data, "fix10_g_q13.md")
        _assert_whole(self, _twin(data), "fix10_g_q13_twin.md")

    def test_q14_question_fullwidth_question_stands_whole(self):
        data = _case(
            _FULL,
            "Question: Which option should we take first"
            + _FULLWIDTH_QUESTION)
        _assert_charged(self, data, 286, "6a5c9dc9bbe1")
        _assert_whole(self, data, "fix10_g_q14.md")
        _assert_whole(self, _twin(data), "fix10_g_q14_twin.md")

    def test_q15_prose_fullwidth_stop_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands"
            + _FULLWIDTH_STOP)
        _assert_charged(self, data, 284, "4c003d20ae91")
        _assert_whole(self, data, "fix10_g_q15.md")
        _assert_whole(self, _twin(data), "fix10_g_q15_twin.md")

    def test_q16_question_interrobang_stands_whole(self):
        data = _case(
            _FULL,
            "Question: Which option should we take first"
            + _INTERROBANG)
        _assert_charged(self, data, 286, "1ff40550aca7")
        _assert_whole(self, data, "fix10_g_q16.md")
        _assert_whole(self, _twin(data), "fix10_g_q16_twin.md")

    def test_q17_prose_two_dot_leader_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands"
            + _TWO_DOT_LEADER)
        _assert_charged(self, data, 284, "d33a3eb92f16")
        _assert_whole(self, data, "fix10_g_q17.md")
        _assert_whole(self, _twin(data), "fix10_g_q17_twin.md")

    def test_q18_cost_two_dot_leader_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked"
            + _TWO_DOT_LEADER)
        _assert_charged(self, data, 284, "47552fe45b22")
        _assert_whole(self, data, "fix10_g_q18.md")
        _assert_whole(self, _twin(data), "fix10_g_q18_twin.md")

    def test_q19_prose_midline_ellipsis_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands"
            + _MIDLINE_ELLIPSIS)
        _assert_charged(self, data, 284, "4be06372c743")
        _assert_whole(self, data, "fix10_g_q19.md")
        _assert_whole(self, _twin(data), "fix10_g_q19_twin.md")

    def test_q20_prose_two_dots_control_pin_stands_whole(self):
        # Pin, seat 2 case q20: a sentence closing on
        # two full stops stands whole in both eras.
        data = _case(_FULL, _PROSE + ".")
        _assert_charged(self, data, 283, "3cfe24c52c59")
        _assert_whole(self, data, "fix10_g_q20.md")
        _assert_whole(self, _twin(data), "fix10_g_q20_twin.md")

    def test_prose_ideographic_no_close_stands_cut(self):
        # Cut side: a line carrying the ideographic
        # stop inside it and closing on no mark stands
        # cut; the mark rescues nothing mid line.
        _assert_cut(
            self,
            _case(_FULL,
                  "Work stays blocked" + _IDEOGRAPHIC_STOP
                  + " until the ruling lands"),
            "fix10_g_ideographic_midline.md")

    def test_cost_two_dot_leader_no_close_stands_cut(self):
        # Cut side, labelled branch: a value closing
        # on a word, carrying no close mark, stands cut.
        _assert_cut(
            self,
            _case(_FULL,
                  "Cost of deciding late: Work stays blocked"),
            "fix10_g_cost_no_close.md")


# ---------------------------------------------------------------------
# CH-259: the titlecase roman tens (ATK10-2-05, T10-36)
# ---------------------------------------------------------------------

class Step17Fix10GTitlecaseRomanTensTest(unittest.TestCase):
    """CH-259: complete bullet items under the
    titlecase roman numerals of the sixty to eighty
    nine family stand whole, on colon free content,
    under the standing guards."""

    def test_q29_bullet_Lx_dot_stands_whole(self):
        data = _case(_FULL, "Lx. " + _BULLET_CONTENT)
        _assert_charged(self, data, 276, "f5dee1385fe8")
        _assert_whole(self, data, "fix10_g_q29.md")
        _assert_whole(self, _twin(data), "fix10_g_q29_twin.md")

    def test_q30_bullet_Lx_paren_stands_whole(self):
        data = _case(_FULL, "Lx) " + _BULLET_CONTENT)
        _assert_charged(self, data, 276, "0dcb41515ebb")
        _assert_whole(self, data, "fix10_g_q30.md")
        _assert_whole(self, _twin(data), "fix10_g_q30_twin.md")

    def test_q31_bullet_paren_Lx_stands_whole(self):
        data = _case(_FULL, "(Lx) " + _BULLET_CONTENT)
        _assert_charged(self, data, 277, "4186ae6cce8d")
        _assert_whole(self, data, "fix10_g_q31.md")
        _assert_whole(self, _twin(data), "fix10_g_q31_twin.md")

    def test_q32_bullet_Lxiv_dot_stands_whole(self):
        data = _case(_FULL, "Lxiv. " + _BULLET_CONTENT)
        _assert_charged(self, data, 278, "87b49efe89f6")
        _assert_whole(self, data, "fix10_g_q32.md")
        _assert_whole(self, _twin(data), "fix10_g_q32_twin.md")

    def test_q33_bullet_Lv_dot_pin_stands_whole(self):
        data = _case(_FULL, "Lv. " + _BULLET_CONTENT)
        _assert_charged(self, data, 276, "d391e8a683f8")
        _assert_whole(self, data, "fix10_g_q33.md")

    def test_q34_bullet_LX_dot_pin_stands_whole(self):
        data = _case(_FULL, "LX. " + _BULLET_CONTENT)
        _assert_charged(self, data, 276, "9a9964aebb10")
        _assert_whole(self, data, "fix10_g_q34.md")

    def test_q35_bullet_lx_dot_pin_stands_whole(self):
        data = _case(_FULL, "lx. " + _BULLET_CONTENT)
        _assert_charged(self, data, 276, "2f0ef81965e7")
        _assert_whole(self, data, "fix10_g_q35.md")

    def test_q36_bullet_Mc_dot_pin_stands_whole(self):
        data = _case(_FULL, "Mc. " + _BULLET_CONTENT)
        _assert_charged(self, data, 276, "3b93f5bc1165")
        _assert_whole(self, data, "fix10_g_q36.md")

    def test_q37_bullet_Xl_dot_pin_stands_whole(self):
        data = _case(_FULL, "Xl. " + _BULLET_CONTENT)
        _assert_charged(self, data, 276, "6d5d0f2d1902")
        _assert_whole(self, data, "fix10_g_q37.md")

    def test_q42_bullet_Lx_joining_cut_stands_cut(self):
        # Cut side, seat 2 case q42: an Lx. item ending
        # on a joining word stands cut in both eras.
        data = _case(
            _FULL, "Lx. Option B leaves the note and")
        _assert_charged(self, data, 272, "89c137379ed5")
        _assert_cut(self, data, "fix10_g_q42.md")

    def test_bullet_Lx_fragment_stands_cut(self):
        # Cut side: an Lx. item cut mid word stands cut
        # under the fragment guard in both eras.
        _assert_cut(
            self,
            _case(_FULL,
                  "Lx. Option B leaves the note adop"),
            "fix10_g_Lx_fragment.md")


# ---------------------------------------------------------------------
# CH-260: the roman case mixes (F-3, T10-37)
# ---------------------------------------------------------------------

class Step17Fix10GRomanCaseMixTest(unittest.TestCase):
    """CH-260: complete bullet items under roman
    numeral case mixes beyond the titlecase form
    stand whole, on colon free content, under the
    standing guards. Constructions stand in seat
    13's paper shapes on the standing template."""

    def test_s13_q15_bullet_iV_paren_stands_whole(self):
        data = _case(_FULL, "iV) " + _BULLET_CONTENT)
        _assert_whole(self, data, "fix10_g_s13_q15.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q15_twin.md")

    def test_s13_q16_bullet_iV_dot_stands_whole(self):
        data = _case(_FULL, "iV. " + _BULLET_CONTENT)
        _assert_whole(self, data, "fix10_g_s13_q16.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q16_twin.md")

    def test_s13_q17_bullet_paren_iV_stands_whole(self):
        data = _case(_FULL, "(iV) " + _BULLET_CONTENT)
        _assert_whole(self, data, "fix10_g_s13_q17.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q17_twin.md")

    def test_s13_q18_bullet_iV_bracket_stands_whole(self):
        data = _case(_FULL, "iV] " + _BULLET_CONTENT)
        _assert_whole(self, data, "fix10_g_s13_q18.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q18_twin.md")

    def test_s13_q19_bullet_vI_paren_stands_whole(self):
        data = _case(_FULL, "vI) " + _BULLET_CONTENT)
        _assert_whole(self, data, "fix10_g_s13_q19.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q19_twin.md")

    def test_titlecase_Iv_pin_stands_whole(self):
        # Pin: the CH-216 titlecase member stands whole
        # in both eras beside the mixes this cure adds.
        data = _case(_FULL, "Iv) " + _BULLET_CONTENT)
        _assert_whole(self, data, "fix10_g_pin_Iv.md")
        _assert_whole(self, _twin(data), "fix10_g_pin_Iv_twin.md")

    def test_s13_q28_bullet_iV_fragment_stands_cut(self):
        # Cut side, seat 13 case q28: an iV item whose
        # content stands cut mid word stands cut in
        # both eras.
        _assert_cut(
            self,
            _case(_FULL,
                  "iV) Option B leaves the note adop"),
            "fix10_g_s13_q28.md")

    def test_bullet_iV_joining_stands_cut(self):
        # Cut side: an iV item ending on a joining word
        # stands cut under the joining guard.
        _assert_cut(
            self,
            _case(_FULL,
                  "iV. Option B leaves the note and"),
            "fix10_g_iV_joining.md")


# ---------------------------------------------------------------------
# CH-261: the group strip limb (ATK10-2-04 and F-4, T10-38)
# ---------------------------------------------------------------------

class Step17Fix10GGroupStripTest(unittest.TestCase):
    """CH-261: a final line closing on a balanced
    bracket group standing behind a charged closing
    character, or behind a run and a right guillemet,
    stands whole."""

    def test_q21_group_single_guillemet_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE + _SINGLE_GUILLEMET)
        _assert_charged(self, data, 284, "ac4f1b052cd2")
        _assert_whole(self, data, "fix10_g_q21.md")
        _assert_whole(self, _twin(data), "fix10_g_q21_twin.md")

    def test_q22_group_asterisk_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE + "*")
        _assert_charged(self, data, 282, "8d8e1fa6225a")
        _assert_whole(self, data, "fix10_g_q22.md")
        _assert_whole(self, _twin(data), "fix10_g_q22_twin.md")

    def test_q23_group_underscore_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE + "_")
        _assert_charged(self, data, 282, "9bd169c255ca")
        _assert_whole(self, data, "fix10_g_q23.md")
        _assert_whole(self, _twin(data), "fix10_g_q23_twin.md")

    def test_q24_group_backtick_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE + "`")
        _assert_charged(self, data, 282, "ef68f0ef109f")
        _assert_whole(self, data, "fix10_g_q24.md")
        _assert_whole(self, _twin(data), "fix10_g_q24_twin.md")

    def test_q25_group_left_double_quote_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE + _LEFT_DOUBLE_QUOTE)
        _assert_charged(self, data, 284, "cc7fbefe1836")
        _assert_whole(self, data, "fix10_g_q25.md")
        _assert_whole(self, _twin(data), "fix10_g_q25_twin.md")

    def test_q26_group_fullwidth_paren_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE + _FULLWIDTH_CLOSE)
        _assert_charged(self, data, 284, "462d7a68dc3b")
        _assert_whole(self, data, "fix10_g_q26.md")
        _assert_whole(self, _twin(data), "fix10_g_q26_twin.md")

    def test_q27_group_corner_bracket_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE + _CORNER_CLOSE)
        _assert_charged(self, data, 284, "67d9c6643471")
        _assert_whole(self, data, "fix10_g_q27.md")
        _assert_whole(self, _twin(data), "fix10_g_q27_twin.md")

    def test_q28_group_run_guillemet_stands_whole(self):
        data = _case(
            _FULL, _GROUP_LINE + _ZWSP + _GUILLEMET)
        _assert_charged(self, data, 286, "8a4cd149eb2b")
        _assert_whole(self, data, "fix10_g_q28.md")
        _assert_whole(self, _twin(data), "fix10_g_q28_twin.md")

    def test_group_standing_last_pin_stands_whole(self):
        # Pin: a group standing last stands whole in
        # both eras.
        data = _case(_FULL, _GROUP_LINE)
        _assert_whole(self, data, "fix10_g_pin_group_last.md")

    def test_group_behind_guillemet_pin_stands_whole(self):
        # Pin: the CH-217 member, a group behind a
        # right guillemet alone, stands whole in both
        # eras in the prose branch.
        data = _case(_FULL, _GROUP_LINE + _GUILLEMET)
        _assert_whole(self, data, "fix10_g_pin_group_guil.md")

    def test_group_behind_quote_pin_stands_whole(self):
        # Pin, seat 13 case q30: a group behind a
        # standing quote character stands whole in
        # both eras.
        data = _case(_FULL, _GROUP_LINE + "\"")
        _assert_whole(self, data, "fix10_g_pin_group_quote.md")

    def test_unbalanced_group_single_guillemet_stands_cut(self):
        # Cut side: an unbalanced group behind the
        # single guillemet takes no group reading.
        _assert_cut(
            self,
            _case(_FULL,
                  "The note stands (as the appendix records"
                  + _SINGLE_GUILLEMET),
            "fix10_g_unbalanced_group.md")

    def test_empty_group_asterisk_stands_cut(self):
        # Cut side: an empty group behind an asterisk
        # takes no group reading and closes no sentence.
        _assert_cut(
            self,
            _case(_FULL, "The note stands ()*"),
            "fix10_g_empty_group.md")


# ---------------------------------------------------------------------
# CH-262: the p17 step past forms (F-5, T10-39)
# ---------------------------------------------------------------------

class Step17Fix10GStepPastP17Test(unittest.TestCase):
    """CH-262: the bracket group forms one step past
    the p17 bound stand whole, and the p17 form
    itself stands unmoved at its bound in both
    eras. Constructions stand in seat 13's paper
    shapes on the standing template, beside seat
    2's routed observation case q40 byte for byte."""

    def test_s13_q24_cost_group_run_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _ZWSP + _GUILLEMET)
        _assert_whole(self, data, "fix10_g_s13_q24.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q24_twin.md")

    def test_s13_q25_cost_group_run_single_guillemet_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _ZWSP
            + _SINGLE_GUILLEMET)
        _assert_whole(self, data, "fix10_g_s13_q25.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q25_twin.md")

    def test_s13_q26_prose_group_run_quote_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked (until the ruling lands)"
            + _ZWSP + "\"")
        _assert_whole(self, data, "fix10_g_s13_q26.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q26_twin.md")

    def test_q40_cost_group_guillemet_stands_whole(self):
        # Seat 2's routed observation case q40: a
        # labelled group behind a right guillemet
        # alone, routed into this charge at record
        # section 83 ruling (g).
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _GUILLEMET)
        _assert_charged(self, data, 308, "b667dd393c74")
        _assert_whole(self, data, "fix10_g_q40.md")
        _assert_whole(self, _twin(data), "fix10_g_q40_twin.md")

    def test_p17_cost_group_run_quote_bound_stands_cut(self):
        # Bound pin, in both eras: the p17 form itself
        # (a labelled group behind an interleaved run
        # and a closing double quote) stands at its
        # section 81 ruling (f) bound, cut at 4, 4
        # beside its twin parsed. No charge of this
        # wave widens into it.
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _ZWSP + "\"")
        _assert_cut(self, data, "fix10_g_p17.md")
        _assert_whole(self, _twin(data), "fix10_g_p17_twin.md")

    def test_s13_q29_cost_group_run_only_pin_stands_whole(self):
        # Pin, seat 13 case q29: a labelled group
        # behind a trailing run alone stands whole in
        # both eras, at its twin's exit.
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _ZWSP)
        _assert_whole(self, data, "fix10_g_s13_q29.md")
        _assert_whole(self, _twin(data),
                      "fix10_g_s13_q29_twin.md")


# ---------------------------------------------------------------------
# CH-263: the single character roman markers (ATK10-2-06, T10-40)
# ---------------------------------------------------------------------

class Step17Fix10GSingleCharRomanTest(unittest.TestCase):
    """CH-263: complete bullet items under the
    single character Unicode roman numeral markers
    stand whole, on colon free content, under the
    standing guards."""

    def test_q38_bullet_unicode_cap_roman_stands_whole(self):
        data = _case(
            _FULL, _CAP_ROMAN_FOUR + ". " + _BULLET_CONTENT)
        _assert_charged(self, data, 277, "9bd2e3b1ef17")
        _assert_whole(self, data, "fix10_g_q38.md")
        _assert_whole(self, _twin(data), "fix10_g_q38_twin.md")

    def test_q39_bullet_unicode_low_roman_stands_whole(self):
        data = _case(
            _FULL, _SMALL_ROMAN_FOUR + ") " + _BULLET_CONTENT)
        _assert_charged(self, data, 277, "a106776e3acf")
        _assert_whole(self, data, "fix10_g_q39.md")
        _assert_whole(self, _twin(data), "fix10_g_q39_twin.md")

    def test_bullet_unicode_roman_fragment_stands_cut(self):
        # Cut side: an item under the single character
        # marker cut mid word stands cut in both eras.
        _assert_cut(
            self,
            _case(_FULL,
                  _CAP_ROMAN_FOUR
                  + ". Option B leaves the note adop"),
            "fix10_g_unicode_fragment.md")

    def test_bullet_unicode_roman_joining_stands_cut(self):
        # Cut side: an item under the single character
        # marker ending on a joining word stands cut.
        _assert_cut(
            self,
            _case(_FULL,
                  _SMALL_ROMAN_FOUR
                  + ") Option B leaves the note and"),
            "fix10_g_unicode_joining.md")


if __name__ == "__main__":
    unittest.main()
