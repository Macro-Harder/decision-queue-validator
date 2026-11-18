"""Step 17 fix wave 7, Fix Seat K2 tests, test first.

Charges CH-116 to CH-120, as ruled at section 66 of
design/steps/step-17r-record.md and sourced at round 7
attack seat 2, design/steps/step-17r-attack7-2.md
(ATK7-2-01 to ATK7-2-05). One rule at five limbs: the
final line rule in parse.py, in _final_line_is_cut_off
and _labelled_value_stands_whole.

CH-116 (parse, the label match limb, ATK7-2-01): the
re-opened limb 4 of CH-95, ruled at section 66 ruling
(a). A valueless labelled final line whose only value
matter is a run of the ruling (a) ground classes
standing directly after the colon, with no space, takes
no label match under _LABEL_RE, whose value group reads
one or more plain spaces after the colon followed by the
value, or nothing after the colon at all, and the line
falls through every labelled branch and stands cut in
the prose branch, where the spaced form of the same line
stands as no value under the CH-95 limb 4 reading. The
tests stand on the original charged constructions of
round 6, k38_blocks_colon_zwsp, k42_ruled_colon_zwsp,
and k58_blocks_colon_combining, byte for byte as the
attack papers record them. Cure bound: the reading
reaches the run only form, a run of the ground classes
standing alone after the colon; a run character standing
before value matter in the unspaced form stands outside
the limb, as the fix wave 6 paper states the bound for
the limb, and stands cut in this file. The Status and
variant members of the valueless family stand in their
own terms at their marker branches above the label
reading and are not reached here.

CH-117 (parse, the quote and bracket order limb,
ATK7-2-02): a run character standing after a closing
quote or closing bracket hides the sentence close, in
the prose branch and in the sentence valued labelled
branch alike: each branch strips the closing characters
from the end of the line first and only then removes a
trailing run, so the run blocks the strip and the
closing character is left standing last. Cure bound:
each branch disregards the trailing run before its
closing character strip, and again after it, so the
sentence close behind the closing character is read;
a run character rescues no line that closes no sentence,
in either branch.

CH-118 (parse, the letter and roman bullet limb,
ATK7-2-03): complete bullet items under the letter and
roman numeral markers are read as cut prose on colon
free content, the bullet marker set reaching the dash,
star, and plus markers, the digits forms, and the
CH-95 limb 6 parenthesised digits and digits and
bracket markers only. Cure bound: the marker set carries
the single letter and full stop form, the single letter
and closing parenthesis form, the parenthesised single
letter form, and the roman numeral and full stop form in
the standard numeral forms, upper or lower case, under
the same fragment, joining word, and cut reference
guards the standing markers take, the cut side stated
for each newly reached marker in this file. An item
whose content carries a colon is read whole as a
labelled line on that colon, as round 6 observation 3
recorded, and stands outside this limb.

CH-119 (parse, the Options adjacent boundary limb,
ATK7-2-04): a final Options line whose value carries
two part boundaries standing adjacent is read as cut,
the Options branch of _labelled_value_stands_whole
refusing a value carrying any empty item, where the
Blocks branch drops the empty part standing between two
adjacent boundaries since CH-95 limb 5. Cure bound: the
Options branch drops the empty item standing between
two adjacent boundaries where that pair is the value's
one join between its two items, as the charged forms
stand; an empty item at any other boundary, a trailing
comma among them, still fails, and the trailing joining
word refusal stands unmoved. A longer list stands as the
branch has always read it: the Oxford comma list form
(Options: Option A, Option B, and Option C) stands
pinned as still cut under design question note (h), by
the round 2 ruling at record section 19, which no
charge of this wave moves, and it is pinned in this file
on that bound.

CH-120 (parse, the table row limb, ATK7-2-05): a
complete table row carrying no leading pipe is read as
cut prose, the table branch requiring the line to open
on its leading pipe as well as close on its final pipe.
Cure bound: the table reading reaches a row closing on
its final pipe and carrying at least one further pipe,
in the form carrying its leading pipe and in the form
carrying none, subject to the same reference
completeness test of ATK5-2-04; a row missing its final
pipe falls through and stands cut.

Constructions stand in the attack papers own shapes,
byte for byte where a charge names a construction, each
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
_NO_OPTIONS = [_QUESTION, _COST, _BLOCKS]
_NO_BLOCKS = [_QUESTION, _OPTIONS, _COST]


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
# CH-116: the label match limb, the re-opened CH-95 limb 4
# (ATK7-2-01)
# ---------------------------------------------------------------------

class Step17Fix7K2RunOnlyValueTest(unittest.TestCase):
    """CH-116, ATK7-2-01: a valueless labelled final line
    whose only value matter is a run of the ground classes
    standing directly after the colon stands as no value,
    as its spaced form and its terminated twin do. The
    tests stand on the original charged constructions of
    round 6, k38, k42, and k58."""

    def test_k38_blocks_colon_zwsp_stands_whole(self):
        data = _case(_NO_OPTIONS, "Blocks:\u200b")
        _assert_charged(self, data, 221, "10ec100e2b26")
        _assert_whole(self, data, "fix7_k2_k38.md")
        _assert_whole(self, _twin(data), "fix7_k2_k38_twin.md")

    def test_k42_ruled_colon_zwsp_stands_whole(self):
        data = _case(_NO_BLOCKS, "Ruled:\u200b")
        _assert_charged(self, data, 233, "036d1e277217")
        _assert_whole(self, data, "fix7_k2_k42.md")
        _assert_whole(self, _twin(data), "fix7_k2_k42_twin.md")

    def test_k58_blocks_colon_combining_stands_whole(self):
        data = _case(_NO_OPTIONS, "Blocks:\u0301")
        _assert_charged(self, data, 220, "8c8359db5933")
        _assert_whole(self, data, "fix7_k2_k58.md")
        _assert_whole(self, _twin(data), "fix7_k2_k58_twin.md")

    def test_lower_case_run_only_value_stands_whole(self):
        # The label reading reads a label in its lower case
        # form as well as its capital form, so the unspaced
        # run only form stands as no value in that reading
        # too, as the spaced lower case form does.
        _assert_whole(self, _case(_NO_OPTIONS, "blocks:\u200b"),
                      "fix7_k2_blocks_lower.md")

    def test_spaced_run_only_value_pin_stands_whole(self):
        # Pin: m61_blocks_mixed_run_value, the spaced form
        # of the charged line, stands whole under limb 4 as
        # landed, in both eras.
        data = _case(_NO_OPTIONS, "Blocks: \u200b ")
        _assert_charged(self, data, 223, "f53d59b42562")
        _assert_whole(self, data, "fix7_k2_m61.md")

    def test_spaced_spaces_only_value_pin_stands_whole(self):
        # Pin: k39_blocks_colon_spaces, a value of plain
        # spaces alone, stands whole in both eras.
        _assert_whole(self, _case(_NO_OPTIONS, "Blocks:   "),
                      "fix7_k2_k39.md")

    def test_run_before_value_matter_unspaced_stands_cut(self):
        # Cut side, the stated bound of the limb: a run
        # character standing before value matter is a value,
        # not no value, and the unspaced form takes no label
        # match on that ground in either era.
        _assert_cut(self,
                    _case(_NO_OPTIONS, "Blocks:\u200bDQ-002"),
                    "fix7_k2_run_before_value.md")


# ---------------------------------------------------------------------
# CH-117: the quote and bracket order limb (ATK7-2-02)
# ---------------------------------------------------------------------

class Step17Fix7K2QuoteBracketOrderTest(unittest.TestCase):
    """CH-117, ATK7-2-02: a run character standing after a
    closing quote or closing bracket hides no sentence
    close, in the prose branch or in the sentence valued
    labelled branch. The cut side is stated in each
    branch: a run rescues no line that closes no
    sentence."""

    def test_m02_prose_quote_run_stands_whole(self):
        data = _case(
            _FULL,
            "\"Work stays blocked until the ruling lands.\""
            "\u200b")
        _assert_charged(self, data, 287, "416f5ddd2bfb")
        _assert_whole(self, data, "fix7_k2_m02.md")
        _assert_whole(self, _twin(data), "fix7_k2_m02_twin.md")

    def test_m03_prose_paren_run_stands_whole(self):
        data = _case(
            _FULL,
            "(Work stays blocked until the ruling lands.)"
            "\u200b")
        _assert_charged(self, data, 287, "0f6e1c92e318")
        _assert_whole(self, data, "fix7_k2_m03.md")
        _assert_whole(self, _twin(data), "fix7_k2_m03_twin.md")

    def test_m07_cost_quote_run_stands_whole(self):
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked.\""
            "\u200b")
        _assert_charged(self, data, 286, "92b607b5b8f5")
        _assert_whole(self, data, "fix7_k2_m07.md")
        _assert_whole(self, _twin(data), "fix7_k2_m07_twin.md")

    def test_m10_question_quote_run_stands_whole(self):
        data = _case(
            _FULL,
            "Question: Which option should we take first?\""
            "\u200b")
        _assert_charged(self, data, 288, "d97cb0431641")
        _assert_whole(self, data, "fix7_k2_m10.md")
        _assert_whole(self, _twin(data), "fix7_k2_m10_twin.md")

    def test_m09_prose_quote_plain_control_stands_whole(self):
        # Control: m09_prose_quote_plain, the m02 line
        # carrying no run character, stands whole in both
        # eras by the quote stripping the branches already
        # take.
        data = _case(
            _FULL,
            "\"Work stays blocked until the ruling lands.\"")
        _assert_charged(self, data, 284, "cee78e5c04f0")
        _assert_whole(self, data, "fix7_k2_m09.md")

    def test_prose_run_after_punctuation_pin_stands_whole(self):
        # Pin: the run standing directly after the sentence
        # closing punctuation stands cured at CH-95 limb 2,
        # verified at k05 in the round 7 verification set.
        _assert_whole(
            self,
            _case(_FULL, "Work stays blocked until the "
                         "ruling lands.\u200b"),
            "fix7_k2_k05_form.md")

    def test_prose_quote_run_no_sentence_close_stands_cut(self):
        # Cut side, prose branch: the quoted line closes no
        # sentence, and the run after its closing quote
        # rescues nothing.
        _assert_cut(
            self,
            _case(_FULL, "\"Work stays blocked until the "
                         "ruling lands\"\u200b"),
            "fix7_k2_quote_no_close.md")

    def test_cost_quote_run_no_sentence_close_stands_cut(self):
        # Cut side, sentence valued labelled branch: the
        # value closes no sentence behind its closing
        # quote, and the run rescues nothing.
        _assert_cut(
            self,
            _case(_FULL, "Cost of deciding late: Work stays "
                         "blocked\"\u200b"),
            "fix7_k2_cost_no_close.md")


# ---------------------------------------------------------------------
# CH-118: the letter and roman bullet limb (ATK7-2-03)
# ---------------------------------------------------------------------

class Step17Fix7K2LetterRomanBulletTest(unittest.TestCase):
    """CH-118, ATK7-2-03: complete bullet items under the
    letter and roman numeral markers stand whole in item
    form, under the standing fragment, joining word, and
    cut reference guards. The cut side is stated for the
    newly reached markers below."""

    def test_m11_bullet_a_dot_stands_whole(self):
        data = _case(_FULL, "a. Option B leaves the note adopted")
        _assert_charged(self, data, 275, "9d70496cb35c")
        _assert_whole(self, data, "fix7_k2_m11.md")
        _assert_whole(self, _twin(data), "fix7_k2_m11_twin.md")

    def test_m12_bullet_a_paren_stands_whole(self):
        data = _case(_FULL, "a) Option B leaves the note adopted")
        _assert_charged(self, data, 275, "49cc66f9913c")
        _assert_whole(self, data, "fix7_k2_m12.md")
        _assert_whole(self, _twin(data), "fix7_k2_m12_twin.md")

    def test_m13_bullet_paren_a_stands_whole(self):
        data = _case(_FULL, "(a) Option B leaves the note adopted")
        _assert_charged(self, data, 276, "622875b39fb2")
        _assert_whole(self, data, "fix7_k2_m13.md")
        _assert_whole(self, _twin(data), "fix7_k2_m13_twin.md")

    def test_m14_bullet_roman_dot_stands_whole(self):
        data = _case(_FULL, "iv. Option B leaves the note adopted")
        _assert_charged(self, data, 276, "9127b8abe807")
        _assert_whole(self, data, "fix7_k2_m14.md")
        _assert_whole(self, _twin(data), "fix7_k2_m14_twin.md")

    def test_m15_bullet_cap_a_dot_stands_whole(self):
        data = _case(_FULL, "A. Option B leaves the note adopted")
        _assert_charged(self, data, 275, "a76458758dab")
        _assert_whole(self, data, "fix7_k2_m15.md")
        _assert_whole(self, _twin(data), "fix7_k2_m15_twin.md")

    def test_m16_bullet_a_dot_period_control_stands_whole(self):
        # Control: m16_bullet_a_dot_period, the m11 item
        # closing on its full stop, stands whole in both
        # eras by the prose sentence close.
        data = _case(_FULL, "a. Option B leaves the note adopted.")
        _assert_charged(self, data, 276, "0eed24eb4e2a")
        _assert_whole(self, data, "fix7_k2_m16.md")

    def test_letter_item_cut_mid_word_stands_cut(self):
        # Cut side, the fragment guard: an item under a
        # letter marker cut mid word stands cut, as an item
        # under a standing marker does.
        _assert_cut(self,
                    _case(_FULL, "a. Option B leaves the note adop"),
                    "fix7_k2_letter_fragment.md")

    def test_roman_item_joining_word_stands_cut(self):
        # Cut side, the joining word guard: an item under a
        # roman marker ending on a joining word stands cut.
        _assert_cut(self,
                    _case(_FULL, "iv. Option B leaves the note and"),
                    "fix7_k2_roman_joining.md")

    def test_paren_letter_item_cut_reference_stands_cut(self):
        # Cut side, the reference completeness guard: an
        # item under a parenthesised letter marker carrying
        # a cut DQ reference stands cut.
        _assert_cut(self,
                    _case(_FULL, "(a) Option B references DQ-00"),
                    "fix7_k2_paren_letter_cut_ref.md")

    def test_colon_content_item_read_as_labelled_pin(self):
        # Bound pin: an item whose content carries a colon
        # is read whole as a labelled line on that colon, in
        # both eras, as round 6 observation 3 recorded for
        # the a) form at k18; it stands outside this limb.
        _assert_whole(
            self,
            _case(_FULL, "a) Option B: leaves the note adopted"),
            "fix7_k2_colon_content.md")


# ---------------------------------------------------------------------
# CH-119: the Options adjacent boundary limb (ATK7-2-04)
# ---------------------------------------------------------------------

class Step17Fix7K2OptionsAdjacentBoundaryTest(unittest.TestCase):
    """CH-119, ATK7-2-04: an Options value carrying two
    part boundaries standing adjacent stands whole, the
    empty item between the boundaries standing as no item,
    as the Blocks branch reads its empty part since CH-95
    limb 5, on the single join bound the charge names. An
    empty item at any other boundary still fails, and the
    Oxford comma list form stands pinned under note (h)."""

    def test_m20_options_double_comma_stands_whole(self):
        data = _case(_NO_OPTIONS, "Options: Option A,, Option B")
        _assert_charged(self, data, 239, "b5852ecdbc0c")
        _assert_whole(self, data, "fix7_k2_m20.md")
        _assert_whole(self, _twin(data), "fix7_k2_m20_twin.md")

    def test_m21_options_comma_and_stands_whole(self):
        data = _case(_NO_OPTIONS, "Options: Option A, and Option B")
        _assert_charged(self, data, 242, "d6b4ae08ef8c")
        _assert_whole(self, data, "fix7_k2_m21.md")
        _assert_whole(self, _twin(data), "fix7_k2_m21_twin.md")

    def test_m25_options_and_comma_stands_whole(self):
        data = _case(_NO_OPTIONS, "Options: Option A and, Option B")
        _assert_charged(self, data, 242, "2ece0b8fd98d")
        _assert_whole(self, data, "fix7_k2_m25.md")
        _assert_whole(self, _twin(data), "fix7_k2_m25_twin.md")

    def test_plain_options_value_pin_stands_whole(self):
        # Pin: the plain two item Options value as a final
        # line stands whole in both eras.
        _assert_whole(self, _case(_NO_OPTIONS, _OPTIONS),
                      "fix7_k2_options_plain.md")

    def test_m22_options_trailing_comma_stands_cut(self):
        # Bound pin, round 7 observation 1, not charged: an
        # empty item at the trailing boundary still fails,
        # as an empty part at any other boundary does; the
        # cure reaches the interior adjacent forms alone.
        data = _case(_NO_OPTIONS, "Options: Option A, Option B,")
        _assert_charged(self, data, 239, "e8eb97a44e1c")
        _assert_cut(self, data, "fix7_k2_m22.md")

    def test_oxford_comma_form_note_h_pin_stands_cut(self):
        # Bound pin: the Oxford comma list form stands
        # pinned as still cut under design question note
        # (h), by the round 2 ruling at record section 19:
        # its completeness turns on a surface form the tool
        # nowhere teaches, no cure is charged on it, and
        # the single join bound of this cure does not reach
        # a list carrying a plain join beside the adjacent
        # pair.
        _assert_cut(
            self,
            _case(_NO_OPTIONS,
                  "Options: Option A, Option B, and Option C"),
            "fix7_k2_oxford_note_h.md")

    def test_options_trailing_joining_word_stands_cut(self):
        # Cut side: a value whose last token is a joining
        # word is refused, as the branch has always refused
        # it.
        _assert_cut(self,
                    _case(_NO_OPTIONS, "Options: Option A and"),
                    "fix7_k2_options_joining.md")


# ---------------------------------------------------------------------
# CH-120: the table row limb (ATK7-2-05)
# ---------------------------------------------------------------------

class Step17Fix7K2TableNoLeadPipeTest(unittest.TestCase):
    """CH-120, ATK7-2-05: a complete table row carrying no
    leading pipe stands whole in its own form, closing on
    its final pipe, under the reference completeness test.
    A row missing its final pipe, and a row carrying a cut
    reference in either form, stands cut."""

    def test_m32_table_no_lead_pipe_stands_whole(self):
        data = _case(_FULL, "DQ-002 | None |")
        _assert_charged(self, data, 255, "a4a4230ead0c")
        _assert_whole(self, data, "fix7_k2_m32.md")
        _assert_whole(self, _twin(data), "fix7_k2_m32_twin.md")

    def test_lead_pipe_trailing_run_pin_stands_whole(self):
        # Pin: the leading pipe form carrying a trailing run
        # stands whole under CH-95 limb 1, verified at k02
        # in the round 7 verification set.
        _assert_whole(self, _case(_FULL, "| DQ-002 | None |\u200b"),
                      "fix7_k2_k02_form.md")

    def test_lead_pipe_cut_reference_pin_stands_cut(self):
        # Pin: k25_table_cut_ref, the leading pipe form
        # carrying a cut reference, stands cut in both eras
        # under the reference completeness test.
        _assert_cut(self, _case(_FULL, "| DQ-00 | None |"),
                    "fix7_k2_k25_form.md")

    def test_no_lead_pipe_cut_reference_stands_cut(self):
        # Cut side: the no leading pipe form carrying a cut
        # reference stands cut on the same test.
        _assert_cut(self, _case(_FULL, "DQ-00 | None |"),
                    "fix7_k2_no_lead_cut_ref.md")

    def test_no_lead_pipe_missing_final_pipe_stands_cut(self):
        # Cut side: a row in the no leading pipe form
        # missing its final pipe falls through and stands
        # cut, as a row in the leading pipe form does.
        _assert_cut(self, _case(_FULL, "DQ-002 | None"),
                    "fix7_k2_no_lead_no_final.md")


if __name__ == "__main__":
    unittest.main()
