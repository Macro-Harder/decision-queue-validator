"""Step 17 fix wave 8, Fix Seat K9 tests, test first.

Charges CH-173 to CH-175, as ruled at section 77 of
design/steps/step-17r-record.md and sourced at round 8
attack seat 2, design/steps/step-17r-attack8-2.md
(ATK8-2-01 to ATK8-2-03). One rule at three limbs: the
final line rule in parse.py, in _final_line_is_cut_off
and _labelled_value_stands_whole.

CH-173 (parse, the interleaved run limb, ATK8-2-01,
T8-20): a run character standing between two closing
characters hides the sentence close, in the prose branch
and in the sentence valued labelled branch alike. The
CH-117 order disregards a trailing run before the
closing characters are stripped and again after them,
but it takes the closing characters in one strip: where
a run stands between two closing characters, the strip
takes the outer character, stops at the run, the second
run pass takes the run, and the inner closing character
is left standing last, with the sentence close behind it
invisible. Cure bound: each branch reads its closing
characters and its trailing run in alternation until the
end of the line stands stable, so no interleaving of the
two hides the close; a run or a closing character
rescues no line that closes no sentence, in either
branch. The mirror orders stand whole in both eras and
are pinned here: a run standing between a closing quote
and a closing bracket, with the bracket standing last,
and a run standing after both closing characters.

CH-174 (parse, the closing character set limb,
ATK8-2-02, T8-21): a sentence closing on a closing
character outside the strip set is read as cut, in the
prose branch and in the sentence valued labelled branch
alike. The charged members outside the set are the right
guillemet, the closing quote mark of the guillemet pair,
standing alone and standing with a run character behind
it, and the closing asterisks of a bold span. Cure
bound: the strip set of each branch carries the right
guillemet and the asterisk beside the standing members
(the double and single quotes, the closing parenthesis,
bracket, and brace, and the curly closing quotes), so a
sentence closing behind one of them is read; a line
closing on one of them that closes no sentence stands
cut, in either branch.

CH-175 (parse, the bullet marker limb, ATK8-2-03,
T8-22): complete bullet items under the roman numeral
parenthesis and bracket forms and the letter bracket
form are read as cut prose, on colon free content. The
bullet marker set as CH-118 left it carries the roman
numeral in the full stop form only, the single letter in
the full stop, closing parenthesis, and parenthesised
forms, and the digits in the bracket form. Cure bound:
the marker set carries the roman numeral and closing
parenthesis form, the parenthesised roman form, and the
bracket form for a letter or a roman numeral, in the
standard numeral forms in either case, under the same
fragment, joining word, and cut reference guards the
standing markers take, the cut side stated for each
newly reached marker in this file. An item whose content
carries a colon is read whole as a labelled line on that
colon, as round 6 observation 3 recorded, and stands
outside this limb.

The two observations of the attack paper stand recorded
as standing at their stated bounds under ruling (j) of
record section 77, no charge: the Options forms beyond
the single join bound of CH-119 as narrowed, and a run
character standing before value matter. No construction
in this file widens into either.

Constructions stand in the attack paper own shapes, byte
for byte where a charge names a construction, each
asserted at its recorded byte count and sha256 head as
construction facts. An entry stands whole where it takes
no unparsed marker and no rule 12 finding, and cut where
it takes both.

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

_ZWSP = "​"
_GUILLEMET = "»"


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
# CH-173: the interleaved run limb (ATK8-2-01, T8-20)
# ---------------------------------------------------------------------

class Step17Fix8K9InterleavedRunTest(unittest.TestCase):
    """CH-173, ATK8-2-01: a run character standing between
    a closing bracket and a closing quote hides no
    sentence close, in the prose branch or in the sentence
    valued labelled branch. The mirror orders stand whole
    in both eras, pinned here, and the cut side is stated
    in each branch: an interleaving rescues no line that
    closes no sentence."""

    def test_n02_prose_paren_run_quote_stands_whole(self):
        data = _case(
            _FULL,
            "\"(Work stays blocked until the ruling lands.)"
            + _ZWSP + "\"")
        _assert_charged(self, data, 289, "40633ec78eb2")
        _assert_whole(self, data, "fix8_k9_n02.md")
        _assert_whole(self, _twin(data), "fix8_k9_n02_twin.md")

    def test_n04_question_paren_run_quote_stands_whole(self):
        data = _case(
            _FULL,
            "Question: (Which option should we take first?)"
            + _ZWSP + "\"")
        _assert_charged(self, data, 290, "231b54a1ad16")
        _assert_whole(self, data, "fix8_k9_n04.md")
        _assert_whole(self, _twin(data), "fix8_k9_n04_twin.md")

    def test_double_interleave_prose_stands_whole(self):
        # A run standing between the closing characters and
        # a further run standing after the outer character:
        # the alternation reads both interleavings.
        _assert_whole(
            self,
            _case(_FULL,
                  "\"(Work stays blocked until the ruling "
                  "lands.)" + _ZWSP + "\"" + _ZWSP),
            "fix8_k9_double_interleave.md")

    def test_n01_prose_quote_run_paren_pin_stands_whole(self):
        # Pin, the mirror order: a run standing between a
        # closing quote and a closing bracket, with the
        # bracket standing last, stands whole in both eras
        # by the bracket group reading.
        data = _case(
            _FULL,
            "(\"Work stays blocked until the ruling lands.\""
            + _ZWSP + ")")
        _assert_charged(self, data, 289, "ab34bcf1340c")
        _assert_whole(self, data, "fix8_k9_n01.md")
        _assert_whole(self, _twin(data), "fix8_k9_n01_twin.md")

    def test_n06_prose_quote_run_bracket_pin_stands_whole(self):
        # Pin, the mirror order on the bracket form.
        data = _case(
            _FULL,
            "[\"Work stays blocked until the ruling lands.\""
            + _ZWSP + "]")
        _assert_charged(self, data, 289, "352201786b35")
        _assert_whole(self, data, "fix8_k9_n06.md")

    def test_n03_cost_bracket_run_paren_pin_stands_whole(self):
        # Pin, the mirror order inside the labelled branch:
        # the bracket group reading stands before the
        # sentence test there.
        data = _case(
            _FULL,
            "Cost of deciding late: (Work stays blocked.\""
            + _ZWSP + ")")
        _assert_charged(self, data, 288, "2a28cda68565")
        _assert_whole(self, data, "fix8_k9_n03.md")
        _assert_whole(self, _twin(data), "fix8_k9_n03_twin.md")

    def test_n05_prose_both_close_run_pin_stands_whole(self):
        # Pin: a run standing after both closing characters
        # stands cured at CH-117, in both eras here.
        data = _case(
            _FULL,
            "(\"Work stays blocked until the ruling lands.\")"
            + _ZWSP)
        _assert_charged(self, data, 289, "d8b88a75bb34")
        _assert_whole(self, data, "fix8_k9_n05.md")

    def test_prose_interleave_no_sentence_close_stands_cut(self):
        # Cut side, prose branch: the interleaved line
        # closes no sentence behind its closing characters,
        # and the interleaving rescues nothing.
        _assert_cut(
            self,
            _case(_FULL,
                  "\"(Work stays blocked until the ruling "
                  "lands)" + _ZWSP + "\""),
            "fix8_k9_interleave_no_close.md")

    def test_question_interleave_no_close_stands_cut(self):
        # Cut side, sentence valued labelled branch: the
        # value closes no sentence behind its interleaved
        # closing characters.
        _assert_cut(
            self,
            _case(_FULL,
                  "Question: (Which option should we take "
                  "first)" + _ZWSP + "\""),
            "fix8_k9_question_interleave_no_close.md")


# ---------------------------------------------------------------------
# CH-174: the closing character set limb (ATK8-2-02, T8-21)
# ---------------------------------------------------------------------

class Step17Fix8K9ClosingCharacterSetTest(unittest.TestCase):
    """CH-174, ATK8-2-02: a sentence closing on the right
    guillemet or on the closing asterisks of a bold span
    stands whole, in the prose branch and in the sentence
    valued labelled branch alike. The cut side is stated
    in each branch: a closing character of the widened set
    rescues no line that closes no sentence."""

    def test_n07_prose_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands."
            + _GUILLEMET)
        _assert_charged(self, data, 284, "e6b34b647c71")
        _assert_whole(self, data, "fix8_k9_n07.md")
        _assert_whole(self, _twin(data), "fix8_k9_n07_twin.md")

    def test_n08_prose_guillemet_zwsp_stands_whole(self):
        data = _case(
            _FULL,
            "Work stays blocked until the ruling lands."
            + _GUILLEMET + _ZWSP)
        _assert_charged(self, data, 287, "86d8f2975823")
        _assert_whole(self, data, "fix8_k9_n08.md")
        _assert_whole(self, _twin(data), "fix8_k9_n08_twin.md")

    def test_n10_cost_guillemet_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked."
            + _GUILLEMET)
        _assert_charged(self, data, 284, "32995a98404a")
        _assert_whole(self, data, "fix8_k9_n10.md")
        _assert_whole(self, _twin(data), "fix8_k9_n10_twin.md")

    def test_n09_prose_bold_close_stands_whole(self):
        data = _case(
            _FULL,
            "**Work stays blocked until the ruling lands.**")
        _assert_charged(self, data, 286, "5e9d21ac2ee2")
        _assert_whole(self, data, "fix8_k9_n09.md")
        _assert_whole(self, _twin(data), "fix8_k9_n09_twin.md")

    def test_cost_bold_close_stands_whole(self):
        # The bold member inside the sentence valued
        # labelled branch, on the same set parity.
        _assert_whole(
            self,
            _case(_FULL,
                  "Cost of deciding late: **Work stays "
                  "blocked.**"),
            "fix8_k9_cost_bold.md")

    def test_m09_prose_quote_plain_pin_stands_whole(self):
        # Pin: a plain member of the standing set, the
        # closing double quote with no run character,
        # stands whole in both eras.
        data = _case(
            _FULL,
            "\"Work stays blocked until the ruling lands.\"")
        _assert_charged(self, data, 284, "cee78e5c04f0")
        _assert_whole(self, data, "fix8_k9_m09.md")

    def test_prose_guillemet_no_sentence_close_stands_cut(self):
        # Cut side, prose branch: the line closes on the
        # guillemet and closes no sentence behind it.
        _assert_cut(
            self,
            _case(_FULL,
                  "Work stays blocked until the ruling lands"
                  + _GUILLEMET),
            "fix8_k9_guillemet_no_close.md")

    def test_prose_bold_no_sentence_close_stands_cut(self):
        # Cut side, prose branch: the bold span closes and
        # no sentence closes inside it.
        _assert_cut(
            self,
            _case(_FULL,
                  "**Work stays blocked until the ruling "
                  "lands**"),
            "fix8_k9_bold_no_close.md")

    def test_cost_guillemet_no_sentence_close_stands_cut(self):
        # Cut side, sentence valued labelled branch: the
        # value closes on the guillemet and closes no
        # sentence behind it.
        _assert_cut(
            self,
            _case(_FULL,
                  "Cost of deciding late: Work stays blocked"
                  + _GUILLEMET),
            "fix8_k9_cost_guillemet_no_close.md")


# ---------------------------------------------------------------------
# CH-175: the bullet marker limb (ATK8-2-03, T8-22)
# ---------------------------------------------------------------------

class Step17Fix8K9BulletMarkerTest(unittest.TestCase):
    """CH-175, ATK8-2-03: complete bullet items under the
    roman numeral parenthesis and bracket forms and the
    letter bracket form stand whole in item form, under
    the standing fragment, joining word, and cut reference
    guards. The cut side is stated for the newly reached
    markers below."""

    def test_n11_bullet_roman_paren_stands_whole(self):
        data = _case(_FULL, "iv) Option B leaves the note adopted")
        _assert_charged(self, data, 276, "5e0392d46449")
        _assert_whole(self, data, "fix8_k9_n11.md")
        _assert_whole(self, _twin(data), "fix8_k9_n11_twin.md")

    def test_n12_bullet_paren_roman_stands_whole(self):
        data = _case(_FULL, "(iv) Option B leaves the note adopted")
        _assert_charged(self, data, 277, "1d1756dedee8")
        _assert_whole(self, data, "fix8_k9_n12.md")
        _assert_whole(self, _twin(data), "fix8_k9_n12_twin.md")

    def test_n13_bullet_letter_bracket_stands_whole(self):
        data = _case(_FULL, "a] Option B leaves the note adopted")
        _assert_charged(self, data, 275, "f74c82eeb134")
        _assert_whole(self, data, "fix8_k9_n13.md")
        _assert_whole(self, _twin(data), "fix8_k9_n13_twin.md")

    def test_n14_bullet_roman_bracket_stands_whole(self):
        data = _case(_FULL, "iv] Option B leaves the note adopted")
        _assert_charged(self, data, 276, "cf2f42dc252d")
        _assert_whole(self, data, "fix8_k9_n14.md")
        _assert_whole(self, _twin(data), "fix8_k9_n14_twin.md")

    def test_n15_bullet_cap_roman_paren_stands_whole(self):
        data = _case(_FULL, "IV) Option B leaves the note adopted")
        _assert_charged(self, data, 276, "aae24d98db69")
        _assert_whole(self, data, "fix8_k9_n15.md")
        _assert_whole(self, _twin(data), "fix8_k9_n15_twin.md")

    def test_paren_cap_roman_stands_whole(self):
        # The parenthesised roman form in its capital case,
        # the case pair of the n12 form.
        _assert_whole(
            self,
            _case(_FULL, "(IV) Option B leaves the note adopted"),
            "fix8_k9_paren_cap_roman.md")

    def test_n16_bullet_cap_roman_dot_control_stands_whole(self):
        # Control: n16_bullet_cap_roman_dot, the capital
        # roman numeral and full stop form, stands whole
        # inside the cured set of CH-118, in both eras.
        data = _case(_FULL, "IV. Option B leaves the note adopted")
        _assert_charged(self, data, 276, "52854e2fb9a3")
        _assert_whole(self, data, "fix8_k9_n16.md")
        _assert_whole(self, _twin(data), "fix8_k9_n16_twin.md")

    def test_roman_paren_item_cut_mid_word_stands_cut(self):
        # Cut side, the fragment guard: an item under a
        # roman parenthesis marker cut mid word stands cut,
        # as an item under a standing marker does.
        _assert_cut(self,
                    _case(_FULL, "iv) Option B leaves the note adop"),
                    "fix8_k9_roman_paren_fragment.md")

    def test_paren_roman_item_joining_word_stands_cut(self):
        # Cut side, the joining word guard: an item under a
        # parenthesised roman marker ending on a joining
        # word stands cut.
        _assert_cut(self,
                    _case(_FULL, "(iv) Option B leaves the note and"),
                    "fix8_k9_paren_roman_joining.md")

    def test_letter_bracket_item_cut_reference_stands_cut(self):
        # Cut side, the reference completeness guard: an
        # item under a letter bracket marker carrying a cut
        # DQ reference stands cut.
        _assert_cut(self,
                    _case(_FULL, "a] Option B references DQ-00"),
                    "fix8_k9_letter_bracket_cut_ref.md")

    def test_colon_content_item_read_as_labelled_pin(self):
        # Bound pin: an item whose content carries a colon
        # is read whole as a labelled line on that colon, in
        # both eras, as round 6 observation 3 recorded; it
        # stands outside this limb, on a newly reached
        # marker as on a standing one.
        _assert_whole(
            self,
            _case(_FULL, "iv) Option B: leaves the note adopted"),
            "fix8_k9_colon_content.md")


if __name__ == "__main__":
    unittest.main()
