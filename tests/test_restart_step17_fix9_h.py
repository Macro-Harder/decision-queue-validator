"""Step 17 fix wave 9, Fix Seat H tests, test first.

Charges CH-215, CH-216, CH-217, and CH-218, the
truncation neighbours, as numbered consecutively from
CH-191 in cluster order under ruling (a) of section 81
of design/steps/step-17r-record.md (Cluster A two
charges, Cluster B four, Cluster C one, Cluster D one,
Cluster E seven, Cluster F seven, Cluster G two, so
Cluster H takes the next four), sourced at round 9
attack seat 2, design/steps/step-17r-attack9-2.md
(ATK9-2-01 to ATK9-2-04), consolidated as T9-18 to
T9-21 in design/steps/step-17r-r9-triage-prep.md at
Cluster H. Locus: product/decision_queue_validator/
parse.py only, at _final_line_is_cut_off and the
sentence close probe of _labelled_value_stands_whole,
the strip set as CH-174 widened it, and the bullet
item reading, the fix wave 8 K9 family (CH-173 to
CH-175).

CH-215 (Low), T9-18, ATK9-2-01, the closing character
neighbours. A sentence closing on a closing character
outside the widened strip set is read as cut, in the
prose branch and in the sentence valued labelled
branch alike, where the terminated twins stand parsed:
the single guillemet (U+203A), the underscore emphasis
close, the double underscore close, the backtick span
close, the left double quotation mark (U+201C, the
closing mark of the low high quote pair), the fullwidth
closing parenthesis (U+FF09), and the closing corner
bracket (U+300D). Cure bound: the strip set of each
branch carries exactly those charged characters beside
the standing members, so a sentence closing behind one
of them is read; a line closing on one of them that
closes no sentence stands cut, in either branch.

CH-216 (Low), T9-19, ATK9-2-02, the mixed case roman
numeral bullet forms. Complete bullet items under the
mixed case (titlecase) roman numeral forms Iv) and
Iv. and (Iv) and Iv] are read as cut prose, on colon
free content. The roman alternatives of the marker set
read the numeral in its all capital form or its all
lower case form only. Cure bound: each roman
alternative carries the titlecase form of the numeral
(one capital letter followed by lower case letters in
the standard numeral order) beside the two standing
cases, under the same fragment, joining word, and cut
reference guards the standing markers take. Case mixes
beyond the titlecase form stand outside this cure. An
item whose content carries a colon is read whole as a
labelled line on that colon, as round 6 observation 3
recorded, and stands outside this limb.

CH-217 (Low), T9-20, ATK9-2-03, the bracket group
behind a right guillemet. A final line closing on a
balanced bracket group standing behind a right
guillemet is read as cut, where its terminated twin
stands parsed. The bracket group reading of the prose
branch strips only the standing quote characters from
the line end (the double and single quotes and the
curly closing quotes); the right guillemet is not among
them, so the group takes no reading. Cure bound: that
strip carries the right guillemet beside its standing
members, and nothing else; the group member standing
behind an interleaved run and a closing quote (seat
2's p17 form) stands at the fix wave 8 K9 paper's
stated bound, recorded as standing under ruling (f)
of record section 81, no charge, and no construction
in this file widens into it.

CH-218 (Low), T9-21, ATK9-2-04, the single character
ellipsis close. A sentence closing on the single
character horizontal ellipsis (U+2026) is read as cut,
in the prose branch and in the sentence valued
labelled branch alike, where the terminated twins
stand parsed. The sentence close test of both branches
reads the line end against the full stop, the question
mark, and the exclamation mark only. Cure bound: the
ellipsis character stands as a fourth sentence closing
mark in both branches, on the standing order's own
test and on the labelled branch's probe alike; the
three dot spelling of the same close stands whole in
both eras, pinned here.

Constructions stand in the attack paper own shapes,
byte for byte where a charge names a construction,
each asserted at its recorded byte count and sha256
head as construction facts. An entry stands whole
where it takes no unparsed marker and no rule 12
finding, and cut where it takes both.

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

_SINGLE_GUILLEMET = "›"
_LEFT_DOUBLE_QUOTE = "“"
_FULLWIDTH_CLOSE = "）"
_CORNER_CLOSE = "」"
_GUILLEMET = "»"
_ELLIPSIS = "…"
_ZWSP = "​"


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
# CH-215: the closing character neighbours (ATK9-2-01, T9-18)
# ---------------------------------------------------------------------

class Step17Fix9HClosingCharacterNeighboursTest(unittest.TestCase):
    """CH-215, ATK9-2-01: a sentence closing behind a
    closing character of the charged neighbour set stands
    whole, in the prose branch and in the sentence valued
    labelled branch alike. The cut side is stated in each
    branch: a closing character of the set rescues no
    line that closes no sentence."""

    def test_p01_prose_single_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands."
            + _SINGLE_GUILLEMET)
        _assert_charged(self, data, 285, "06f91eacbacf")
        _assert_whole(self, data, "fix9_h_p01.md")
        _assert_whole(self, _twin(data), "fix9_h_p01_twin.md")

    def test_p02_cost_single_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked."
            + _SINGLE_GUILLEMET)
        _assert_charged(self, data, 285, "b09ada5f8f48")
        _assert_whole(self, data, "fix9_h_p02.md")
        _assert_whole(self, _twin(data), "fix9_h_p02_twin.md")

    def test_p24_question_single_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Question: Which option should we take first?"
            + _SINGLE_GUILLEMET)
        _assert_charged(self, data, 287, "c079145b2171")
        _assert_whole(self, data, "fix9_h_p24.md")
        _assert_whole(self, _twin(data), "fix9_h_p24_twin.md")

    def test_p03_prose_underscore_emphasis_stands_whole(self):
        data = _case(
            _FULL,
            "_Work stays blocked until the ruling lands._")
        _assert_charged(self, data, 284, "2a5f158757e8")
        _assert_whole(self, data, "fix9_h_p03.md")
        _assert_whole(self, _twin(data), "fix9_h_p03_twin.md")

    def test_p04_prose_double_underscore_stands_whole(self):
        data = _case(
            _FULL,
            "__Work stays blocked until the ruling lands.__")
        _assert_charged(self, data, 286, "e99e5362a7c8")
        _assert_whole(self, data, "fix9_h_p04.md")
        _assert_whole(self, _twin(data), "fix9_h_p04_twin.md")

    def test_p05_cost_underscore_emphasis_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: _Work stays blocked._")
        _assert_charged(self, data, 284, "3fbdd5f38cce")
        _assert_whole(self, data, "fix9_h_p05.md")
        _assert_whole(self, _twin(data), "fix9_h_p05_twin.md")

    def test_p06_prose_backtick_span_stands_whole(self):
        data = _case(
            _FULL,
            "`Work stays blocked until the ruling lands.`")
        _assert_charged(self, data, 284, "d45c3df440f0")
        _assert_whole(self, data, "fix9_h_p06.md")
        _assert_whole(self, _twin(data), "fix9_h_p06_twin.md")

    def test_p07_question_backtick_span_stands_whole(self):
        data = _case(
            _FULL,
            "Question: `Which option should we take first?`")
        _assert_charged(self, data, 286, "de0c9dcbcef8")
        _assert_whole(self, data, "fix9_h_p07.md")
        _assert_whole(self, _twin(data), "fix9_h_p07_twin.md")

    def test_p08_prose_left_double_quote_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands."
            + _LEFT_DOUBLE_QUOTE)
        _assert_charged(self, data, 285, "9604c357ea29")
        _assert_whole(self, data, "fix9_h_p08.md")
        _assert_whole(self, _twin(data), "fix9_h_p08_twin.md")

    def test_p09_prose_fullwidth_paren_stands_whole(self):
        data = _case(
            _FULL,
            "（Work stays blocked until the ruling lands."
            + _FULLWIDTH_CLOSE)
        _assert_charged(self, data, 288, "cab9b50d223d")
        _assert_whole(self, data, "fix9_h_p09.md")
        _assert_whole(self, _twin(data), "fix9_h_p09_twin.md")

    def test_p10_prose_cjk_bracket_stands_whole(self):
        data = _case(
            _FULL,
            "「Work stays blocked until the ruling lands."
            + _CORNER_CLOSE)
        _assert_charged(self, data, 288, "405d0a5b9505")
        _assert_whole(self, data, "fix9_h_p10.md")
        _assert_whole(self, _twin(data), "fix9_h_p10_twin.md")

    def test_p20_prose_paren_run_guillemet_pin_stands_whole(self):
        # Pin: the CH-173 alternation on the widened set of
        # CH-174 reaches this fresh neighbour in both eras.
        data = _case(
            _FULL,
            "(Work stays blocked until the ruling lands.)"
            + _ZWSP + _GUILLEMET)
        _assert_charged(self, data, 289, "c1b0b34eaaa8")
        _assert_whole(self, data, "fix9_h_p20.md")
        _assert_whole(self, _twin(data), "fix9_h_p20_twin.md")

    def test_p21_prose_bold_run_quote_pin_stands_whole(self):
        # Pin: a run standing between the closing asterisks
        # of a bold span and a closing double quote stands
        # whole in both eras.
        data = _case(
            _FULL,
            "**Work stays blocked until the ruling lands.**"
            + _ZWSP + "\"")
        _assert_charged(self, data, 290, "3f8112aace45")
        _assert_whole(self, data, "fix9_h_p21.md")
        _assert_whole(self, _twin(data), "fix9_h_p21_twin.md")

    def test_p23_prose_run_guillemet_pin_stands_whole(self):
        # Pin: a run standing between the full stop and a
        # right guillemet stands whole in both eras.
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands."
            + _ZWSP + _GUILLEMET)
        _assert_charged(self, data, 287, "68840b703551")
        _assert_whole(self, data, "fix9_h_p23.md")
        _assert_whole(self, _twin(data), "fix9_h_p23_twin.md")

    def test_prose_single_guillemet_no_close_stands_cut(self):
        # Cut side, prose branch: the line closes on the
        # single guillemet and closes no sentence behind it.
        _assert_cut(
            self,
            _case(_FULL,
                  "Work stays blocked until the ruling lands"
                  + _SINGLE_GUILLEMET),
            "fix9_h_guillemet_no_close.md")

    def test_cost_single_guillemet_no_close_stands_cut(self):
        # Cut side, sentence valued labelled branch: the
        # value closes on the single guillemet and closes
        # no sentence behind it.
        _assert_cut(
            self,
            _case(_FULL,
                  "Cost of deciding late: Work stays blocked"
                  + _SINGLE_GUILLEMET),
            "fix9_h_cost_guillemet_no_close.md")

    def test_prose_underscore_no_close_stands_cut(self):
        # Cut side, prose branch: the underscore span closes
        # and no sentence closes inside it.
        _assert_cut(
            self,
            _case(_FULL,
                  "_Work stays blocked until the ruling lands_"),
            "fix9_h_underscore_no_close.md")

    def test_question_backtick_no_close_stands_cut(self):
        # Cut side, sentence valued labelled branch: the
        # backtick span closes and no sentence closes
        # inside it.
        _assert_cut(
            self,
            _case(_FULL,
                  "Question: `Which option should we take "
                  "first`"),
            "fix9_h_question_backtick_no_close.md")

    def test_prose_fullwidth_no_close_stands_cut(self):
        # Cut side, prose branch: the fullwidth parenthesis
        # closes and no sentence closes inside it.
        _assert_cut(
            self,
            _case(_FULL,
                  "（Work stays blocked until the ruling lands"
                  + _FULLWIDTH_CLOSE),
            "fix9_h_fullwidth_no_close.md")


# ---------------------------------------------------------------------
# CH-216: the mixed case roman numeral bullet forms (ATK9-2-02, T9-19)
# ---------------------------------------------------------------------

class Step17Fix9HMixedRomanBulletTest(unittest.TestCase):
    """CH-216, ATK9-2-02: complete bullet items under the
    titlecase roman numeral forms stand whole in item
    form, under the standing fragment, joining word, and
    cut reference guards. The uniform case forms stand
    whole in both eras, pinned here, and the cut side is
    stated for the newly reached markers below."""

    def test_p11_bullet_mixed_roman_paren_stands_whole(self):
        data = _case(_FULL, "Iv) Option B leaves the note adopted")
        _assert_charged(self, data, 276, "0f960747de54")
        _assert_whole(self, data, "fix9_h_p11.md")
        _assert_whole(self, _twin(data), "fix9_h_p11_twin.md")

    def test_p12_bullet_mixed_roman_dot_stands_whole(self):
        data = _case(_FULL, "Iv. Option B leaves the note adopted")
        _assert_charged(self, data, 276, "9a16553e4f05")
        _assert_whole(self, data, "fix9_h_p12.md")
        _assert_whole(self, _twin(data), "fix9_h_p12_twin.md")

    def test_p13_bullet_paren_mixed_roman_stands_whole(self):
        data = _case(_FULL, "(Iv) Option B leaves the note adopted")
        _assert_charged(self, data, 277, "48cb12d7e0de")
        _assert_whole(self, data, "fix9_h_p13.md")
        _assert_whole(self, _twin(data), "fix9_h_p13_twin.md")

    def test_p14_bullet_mixed_roman_bracket_stands_whole(self):
        data = _case(_FULL, "Iv] Option B leaves the note adopted")
        _assert_charged(self, data, 276, "9181cfdc56bc")
        _assert_whole(self, data, "fix9_h_p14.md")
        _assert_whole(self, _twin(data), "fix9_h_p14_twin.md")

    def test_cap_roman_paren_pin_stands_whole(self):
        # Pin: the capital roman parenthesis form stands
        # whole inside the cured set of CH-175, in both eras.
        data = _case(_FULL, "IV) Option B leaves the note adopted")
        _assert_charged(self, data, 276, "aae24d98db69")
        _assert_whole(self, data, "fix9_h_cap_paren.md")
        _assert_whole(self, _twin(data), "fix9_h_cap_paren_twin.md")

    def test_cap_roman_dot_pin_stands_whole(self):
        # Pin: the capital roman full stop form stands whole
        # inside the cured set of CH-118, in both eras.
        data = _case(_FULL, "IV. Option B leaves the note adopted")
        _assert_charged(self, data, 276, "52854e2fb9a3")
        _assert_whole(self, data, "fix9_h_cap_dot.md")
        _assert_whole(self, _twin(data), "fix9_h_cap_dot_twin.md")

    def test_lower_roman_paren_pin_stands_whole(self):
        # Pin: the lower case roman parenthesis form stands
        # whole inside the cured set of CH-175, in both eras.
        data = _case(_FULL, "iv) Option B leaves the note adopted")
        _assert_charged(self, data, 276, "5e0392d46449")
        _assert_whole(self, data, "fix9_h_lower_paren.md")
        _assert_whole(self, _twin(data), "fix9_h_lower_paren_twin.md")

    def test_lower_paren_roman_pin_stands_whole(self):
        # Pin: the parenthesised lower case roman form
        # stands whole inside the cured set of CH-175, in
        # both eras.
        data = _case(_FULL, "(iv) Option B leaves the note adopted")
        _assert_charged(self, data, 277, "1d1756dedee8")
        _assert_whole(self, data, "fix9_h_lower_paren2.md")
        _assert_whole(self, _twin(data), "fix9_h_lower_paren2_twin.md")

    def test_mixed_roman_item_cut_mid_word_stands_cut(self):
        # Cut side, the fragment guard: an item under a
        # titlecase roman parenthesis marker cut mid word
        # stands cut, as an item under a standing marker does.
        _assert_cut(self,
                    _case(_FULL, "Iv) Option B leaves the note adop"),
                    "fix9_h_mixed_roman_fragment.md")

    def test_mixed_roman_item_joining_word_stands_cut(self):
        # Cut side, the joining word guard: an item under a
        # titlecase roman full stop marker ending on a
        # joining word stands cut.
        _assert_cut(self,
                    _case(_FULL, "Iv. Option B leaves the note and"),
                    "fix9_h_mixed_roman_joining.md")

    def test_paren_mixed_roman_item_cut_reference_stands_cut(self):
        # Cut side, the reference completeness guard: an
        # item under a parenthesised titlecase roman marker
        # carrying a cut DQ reference stands cut.
        _assert_cut(self,
                    _case(_FULL, "(Iv) Option B references DQ-00"),
                    "fix9_h_paren_mixed_cut_ref.md")

    def test_colon_content_item_read_as_labelled_pin(self):
        # Bound pin: an item whose content carries a colon
        # is read whole as a labelled line on that colon, in
        # both eras, as round 6 observation 3 recorded; it
        # stands outside this limb, on a newly reached
        # marker as on a standing one.
        _assert_whole(
            self,
            _case(_FULL, "Iv) Option B: leaves the note adopted"),
            "fix9_h_colon_content.md")


# ---------------------------------------------------------------------
# CH-217: the bracket group behind a right guillemet (ATK9-2-03, T9-20)
# ---------------------------------------------------------------------

class Step17Fix9HGroupGuillemetTest(unittest.TestCase):
    """CH-217, ATK9-2-03: a final line closing on a
    balanced bracket group standing behind a right
    guillemet stands whole on the bracket group reading.
    The group standing last and the group behind a
    standing quote character stand whole in both eras,
    pinned here; an unbalanced or empty group behind the
    guillemet stands cut."""

    def test_p16_prose_group_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "The note stands (as the appendix records)"
            + _GUILLEMET)
        _assert_charged(self, data, 283, "e3cb125edef5")
        _assert_whole(self, data, "fix9_h_p16.md")
        _assert_whole(self, _twin(data), "fix9_h_p16_twin.md")

    def test_group_standing_last_pin_stands_whole(self):
        # Pin: a group closing on its bracket standing last
        # stands whole on the same reading, in both eras.
        _assert_whole(
            self,
            _case(_FULL,
                  "The note stands (as the appendix records)"),
            "fix9_h_group_last.md")

    def test_group_behind_quote_pin_stands_whole(self):
        # Pin: a group standing behind a closing double
        # quote, a member of the standing strip, stands
        # whole in both eras.
        _assert_whole(
            self,
            _case(_FULL,
                  "The note stands (as the appendix records)\""),
            "fix9_h_group_quote.md")

    def test_unbalanced_group_guillemet_stands_cut(self):
        # Cut side: an unbalanced group behind the
        # guillemet takes no bracket group reading and
        # closes no sentence.
        _assert_cut(
            self,
            _case(_FULL,
                  "The note stands (as the appendix records"
                  + _GUILLEMET),
            "fix9_h_group_unbalanced.md")

    def test_empty_group_guillemet_stands_cut(self):
        # Cut side: an empty group behind the guillemet
        # carries no bracket form and closes no sentence.
        _assert_cut(
            self,
            _case(_FULL,
                  "The note stands ()" + _GUILLEMET),
            "fix9_h_group_empty.md")


# ---------------------------------------------------------------------
# CH-218: the single character ellipsis close (ATK9-2-04, T9-21)
# ---------------------------------------------------------------------

class Step17Fix9HEllipsisCloseTest(unittest.TestCase):
    """CH-218, ATK9-2-04: a sentence closing on the single
    character ellipsis stands whole, in the prose branch
    and in the sentence valued labelled branch alike. The
    three dot spelling stands whole in both eras, pinned
    here; the ellipsis character rescues no form that
    stands cut on its own reading, as the cut side below
    states."""

    def test_p18_prose_ellipsis_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands"
            + _ELLIPSIS)
        _assert_charged(self, data, 284, "b54533c1e693")
        _assert_whole(self, data, "fix9_h_p18.md")
        _assert_whole(self, _twin(data), "fix9_h_p18_twin.md")

    def test_p19_cost_ellipsis_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked"
            + _ELLIPSIS)
        _assert_charged(self, data, 284, "d14804c2f8a2")
        _assert_whole(self, data, "fix9_h_p19.md")
        _assert_whole(self, _twin(data), "fix9_h_p19_twin.md")

    def test_prose_three_dot_pin_stands_whole(self):
        # Pin: the three dot spelling of the same close
        # ends on a full stop and stands whole on the
        # standing test, in both eras.
        _assert_whole(
            self,
            _case(_FULL,
                  "Work stays blocked until the ruling lands..."),
            "fix9_h_three_dot.md")

    def test_cost_three_dot_pin_stands_whole(self):
        # Pin: the three dot spelling inside the sentence
        # valued labelled branch, in both eras.
        _assert_whole(
            self,
            _case(_FULL,
                  "Cost of deciding late: Work stays blocked..."),
            "fix9_h_cost_three_dot.md")

    def test_bullet_fragment_ellipsis_stands_cut(self):
        # Cut side: an item under a standing marker cut mid
        # word and closing on the ellipsis character stands
        # cut on the fragment guard, in both eras; the
        # ellipsis rescues no cut form.
        _assert_cut(self,
                    _case(_FULL,
                          "- Option B leaves the note adop"
                          + _ELLIPSIS),
                    "fix9_h_bullet_fragment_ellipsis.md")

    def test_bullet_joining_word_ellipsis_stands_cut(self):
        # Cut side: an item under a standing marker ending
        # on a joining word and closing on the ellipsis
        # character stands cut on the joining word guard,
        # in both eras; the ellipsis rescues no cut form.
        _assert_cut(self,
                    _case(_FULL,
                          "- Option B leaves the note and"
                          + _ELLIPSIS),
                    "fix9_h_bullet_joining_ellipsis.md")


if __name__ == "__main__":
    unittest.main()
