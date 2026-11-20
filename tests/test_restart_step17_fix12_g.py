"""Step 17 fix wave 12, Fix Seat G tests, test first.

Charges CH-342 to CH-346, the strip set family of
round 12 (Cluster G of design/steps/
step-17r-r12-triage-prep.md section 3, T12-30 to
T12-34), sourced at round 12 attack seat 1,
design/steps/step-17r-r12-seat01-run.md
(ATK12-1-01 to ATK12-1-05), and round 12 attack
seat 12, design/steps/step-17r-r12-seat12-run.md
(ATK12-12-01 to ATK12-12-05). Locus:
product/decision_queue_validator/parse.py only,
at _final_line_is_cut_off and
_labelled_value_stands_whole, the sentence close
readings as cured at CH-302 to CH-306.

CH-342 (Low), T12-30, the closing character limb.
A sentence closing on a closing character of the
next ring outside the CH-302 restated strip set
is read as cut, in the prose branch and in the
sentence valued labelled branch alike. Restated
strip set: the standing members, the CH-257
members, and the CH-302 members, plus exactly
these charged members: the mathematical right
white square bracket (U+27E7), the right white
parenthesis (U+2986), the double prime (U+2033),
the low double prime quotation mark (U+301F),
the heavy double comma quotation mark ornament
(U+275E), the medium right parenthesis ornament
(U+2769), the heavy right-pointing angle
quotation mark ornament (U+276F), the
right-pointing angle bracket (U+232A), the right
wiggly fence (U+29D9), the right square bracket
with quill (U+2046), the heavy right-pointing
angle bracket ornament (U+2771), the medium flat
right parenthesis ornament (U+276B), the Tibetan
mark ang khang closing (U+0F3D), the reversed
double prime (U+2036), the small right
parenthesis (U+FE5A), and the small right
tortoise shell bracket (U+FE5E).

CH-343 (Low), T12-31, the sentence close mark
limb. A sentence closing on a sentence close
mark of the next ring outside the CH-303
restated mark set is read as cut, in both
branches alike. Restated close mark set: the
standing marks, the CH-258 marks, and the
CH-303 marks, plus exactly these charged marks:
the Devanagari danda (U+0964), the Devanagari
double danda (U+0965), the Myanmar sign section
(U+104B), the Tibetan mark shad (U+0F0D), the
small question mark (U+FE56), the small
exclamation mark (U+FE57), the Khmer sign khan
(U+17D4), the Myanmar sign little section
(U+104A), the Tibetan mark gter shad (U+0F14),
the Vai full stop (U+A60E), the reversed
question mark (U+2E2E), the Arabic question mark
(U+061F), and the Lisu punctuation full stop
(U+A4FF), on every sentence close test of both
branches, the standing order test and the probe
alike.

CH-344 (Low), T12-32, the final line group limb.
A final line closing on a balanced bracket group
standing behind a closing character that stands
in neither pass of the CH-305 restated group
strip is read as cut. Restated group strip
passes: the first pass stands as CH-217 left it;
the second pass disregards, in alternation with
a trailing run of the ground classes, every
member of the restated sentence close strip set
of CH-342 except the ASCII closing brackets,
whose group the reading seeks, and counts only
where matter stands before the group once the
quote characters and the run are disregarded, as
CH-261's narrowing states. The charged members
stand inside the CH-342 set.

CH-345 (Low), T12-33, the labelled value group
limb. A sentence valued labelled value closing
on a balanced bracket group standing behind a
closing character the CH-306 restated probe
strip does not reach is read as cut. Restated
labelled group probe: the probe on the value as
written disregards, in alternation with a
trailing run of the ground classes, every member
of the restated sentence close strip set of
CH-342 except the standing quote characters (the
double quote, the single quote, and the two
closing curly quotes), so the p17 form (a group
behind an interleaved run and a closing double
quote) takes no probe reading and stands unmoved
at its section 81 ruling (f) bound, pinned here
in both eras. The charged members stand inside
the CH-342 set.

CH-346 (Low), T12-34, the roman numeral bullet
limb. Complete bullet items under the single
character Unicode roman numeral markers of the
archaic range past U+2181 are read as cut prose,
on colon free content. Restated roman numeral
bullet forms: the single character alternatives
carry the capital forms U+2160 to U+216F and the
small forms U+2170 to U+217F, beside the archaic
range U+2180 to U+2188 whole (the one thousand
and five thousand forms of CH-304 beside the ten
thousand form U+2182, the reversed one hundred
forms U+2183 and U+2184, the roman numeral six
late form U+2185, the fifty early form U+2186,
the fifty thousand form U+2187, and the one
hundred thousand form U+2188), in the full stop
form, the closing parenthesis and bracket form,
the parenthesised form, the opening bracket
form, and the braced form, under the same
fragment, joining word, and cut reference guards
the standing markers take.

Constructions stand byte for byte as the round
12 attack case files stand, on the template
family of the earlier rounds, each asserted at
its recorded byte count and sha256 head as a
construction fact. The cured CH-302 to CH-306
forms stand as pins in the last class, and the
p17 bound form stands unmoved as a pin at its
bound in every charge of this cluster.

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

_PROSE = "Work stays blocked until the ruling lands."
_GROUP_LINE = "The note stands (as the appendix records)"
_GUILLEMET = "\u00bb"
_SINGLE_GUILLEMET = "\u203a"
_LEFT_GUILLEMET = "\u00ab"
_ZWSP = "\u200b"


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
# CH342
# ---------------------------------------------------------------------

class Step17Fix12GClosingCharacterTest(unittest.TestCase):
    """CH-342: a sentence closing behind a closing character of the charged ring past the CH-302 strip set stands whole, in the prose branch and in the sentence valued labelled branch alike."""

    def test_ch342_01_t01_prose_math_white_square_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t01_prose_math_white_square
        data = _case(_FULL, '⟦Work stays blocked until the ruling lands.⟧')
        _assert_charged(self, data, 288, "83b409bbcd16")
        _assert_whole(self, data, "fix12_g_t01_prose_math_white_square.md")
        _assert_whole(self, _twin(data), "fix12_g_t01_prose_math_white_square_twin.md")

    def test_ch342_02_t02_prose_right_white_paren_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t02_prose_right_white_paren
        data = _case(_FULL, '⦅Work stays blocked until the ruling lands.⦆')
        _assert_charged(self, data, 288, "ae67dee10994")
        _assert_whole(self, data, "fix12_g_t02_prose_right_white_paren.md")
        _assert_whole(self, _twin(data), "fix12_g_t02_prose_right_white_paren_twin.md")

    def test_ch342_03_t03_cost_double_prime_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t03_cost_double_prime
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked.″')
        _assert_charged(self, data, 285, "acbfe4dad52d")
        _assert_whole(self, data, "fix12_g_t03_cost_double_prime.md")
        _assert_whole(self, _twin(data), "fix12_g_t03_cost_double_prime_twin.md")

    def test_ch342_04_t04_prose_low_double_prime_quote_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t04_prose_low_double_prime_quote
        data = _case(_FULL, 'Work stays blocked until the ruling lands.〟')
        _assert_charged(self, data, 285, "0993a02720da")
        _assert_whole(self, data, "fix12_g_t04_prose_low_double_prime_quote.md")
        _assert_whole(self, _twin(data), "fix12_g_t04_prose_low_double_prime_quote_twin.md")

    def test_ch342_05_t05_prose_heavy_right_quote_orn_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t05_prose_heavy_right_quote_orn
        data = _case(_FULL, 'Work stays blocked until the ruling lands.❞')
        _assert_charged(self, data, 285, "830255257c4b")
        _assert_whole(self, data, "fix12_g_t05_prose_heavy_right_quote_orn.md")
        _assert_whole(self, _twin(data), "fix12_g_t05_prose_heavy_right_quote_orn_twin.md")

    def test_ch342_06_t06_prose_medium_right_paren_orn_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t06_prose_medium_right_paren_orn
        data = _case(_FULL, '❨Work stays blocked until the ruling lands.❩')
        _assert_charged(self, data, 288, "123150950084")
        _assert_whole(self, data, "fix12_g_t06_prose_medium_right_paren_orn.md")
        _assert_whole(self, _twin(data), "fix12_g_t06_prose_medium_right_paren_orn_twin.md")

    def test_ch342_07_t07_question_heavy_right_angle_quote_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t07_question_heavy_right_angle_quote
        data = _case(_FULL, 'Question: Which option should we take first?❯')
        _assert_charged(self, data, 287, "fbe487ea4ac1")
        _assert_whole(self, data, "fix12_g_t07_question_heavy_right_angle_quote.md")
        _assert_whole(self, _twin(data), "fix12_g_t07_question_heavy_right_angle_quote_twin.md")

    def test_ch342_08_t08_prose_right_angle_bracket_232a_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t08_prose_right_angle_bracket_232a
        data = _case(_FULL, '〈Work stays blocked until the ruling lands.〉')
        _assert_charged(self, data, 288, "f983d24b4780")
        _assert_whole(self, data, "fix12_g_t08_prose_right_angle_bracket_232a.md")
        _assert_whole(self, _twin(data), "fix12_g_t08_prose_right_angle_bracket_232a_twin.md")

    def test_ch342_09_t09_cost_wiggly_fence_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t09_cost_wiggly_fence
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked.⧙')
        _assert_charged(self, data, 285, "560008bea39b")
        _assert_whole(self, data, "fix12_g_t09_cost_wiggly_fence.md")
        _assert_whole(self, _twin(data), "fix12_g_t09_cost_wiggly_fence_twin.md")

    def test_ch342_10_t10_prose_right_square_quill_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t10_prose_right_square_quill
        data = _case(_FULL, 'Work stays blocked until the ruling lands.⁆')
        _assert_charged(self, data, 285, "6b4b01af13d3")
        _assert_whole(self, data, "fix12_g_t10_prose_right_square_quill.md")
        _assert_whole(self, _twin(data), "fix12_g_t10_prose_right_square_quill_twin.md")

    def test_ch342_11_t01_prose_heavy_angle_orn_close_stands_whole(self):
        # Source: attack12-12-scratch/cases/t01_prose_heavy_angle_orn_close
        data = _case(_FULL, '❰Work stays blocked until the ruling lands.❱')
        _assert_charged(self, data, 288, "63f89f50d836")
        _assert_whole(self, data, "fix12_g_t01_prose_heavy_angle_orn_close.md")
        _assert_whole(self, _twin(data), "fix12_g_t01_prose_heavy_angle_orn_close_twin.md")

    def test_ch342_12_t02_prose_flat_paren_orn_close_stands_whole(self):
        # Source: attack12-12-scratch/cases/t02_prose_flat_paren_orn_close
        data = _case(_FULL, '❪Work stays blocked until the ruling lands.❫')
        _assert_charged(self, data, 288, "b5a6db0899a9")
        _assert_whole(self, data, "fix12_g_t02_prose_flat_paren_orn_close.md")
        _assert_whole(self, _twin(data), "fix12_g_t02_prose_flat_paren_orn_close_twin.md")

    def test_ch342_13_t03_cost_tibetan_ang_close_stands_whole(self):
        # Source: attack12-12-scratch/cases/t03_cost_tibetan_ang_close
        data = _case(_FULL, 'Cost of deciding late: ༼Work stays blocked.༽')
        _assert_charged(self, data, 288, "d0210ee2aa97")
        _assert_whole(self, data, "fix12_g_t03_cost_tibetan_ang_close.md")
        _assert_whole(self, _twin(data), "fix12_g_t03_cost_tibetan_ang_close_twin.md")

    def test_ch342_14_t05_question_reversed_double_prime_close_stands_whole(self):
        # Source: attack12-12-scratch/cases/t05_question_reversed_double_prime_close
        data = _case(_FULL, 'Question: ‶Which option should we take first?‶')
        _assert_charged(self, data, 290, "0b0933efea08")
        _assert_whole(self, data, "fix12_g_t05_question_reversed_double_prime_close.md")
        _assert_whole(self, _twin(data), "fix12_g_t05_question_reversed_double_prime_close_twin.md")

    def test_ch342_15_t06_prose_small_paren_close_stands_whole(self):
        # Source: attack12-12-scratch/cases/t06_prose_small_paren_close
        data = _case(_FULL, '﹙Work stays blocked until the ruling lands.﹚')
        _assert_charged(self, data, 288, "05d8926944b7")
        _assert_whole(self, data, "fix12_g_t06_prose_small_paren_close.md")
        _assert_whole(self, _twin(data), "fix12_g_t06_prose_small_paren_close_twin.md")

    def test_ch342_16_t07_cost_small_tortoise_close_stands_whole(self):
        # Source: attack12-12-scratch/cases/t07_cost_small_tortoise_close
        data = _case(_FULL, 'Cost of deciding late: ﹛Work stays blocked.﹜')
        _assert_charged(self, data, 288, "08b8bdaa6fce")
        _assert_whole(self, data, "fix12_g_t07_cost_small_tortoise_close.md")
        _assert_whole(self, _twin(data), "fix12_g_t07_cost_small_tortoise_close_twin.md")

# ---------------------------------------------------------------------
# CH343
# ---------------------------------------------------------------------

class Step17Fix12GCloseMarkTest(unittest.TestCase):
    """CH-343: a sentence closing on a sentence close mark of the charged ring past the CH-303 mark set stands whole, in the prose branch and in the sentence valued labelled branch alike."""

    def test_ch343_01_t11_prose_devanagari_danda_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t11_prose_devanagari_danda
        data = _case(_FULL, 'Work stays blocked until the ruling lands।')
        _assert_charged(self, data, 284, "d4d408b7705c")
        _assert_whole(self, data, "fix12_g_t11_prose_devanagari_danda.md")
        _assert_whole(self, _twin(data), "fix12_g_t11_prose_devanagari_danda_twin.md")

    def test_ch343_02_t12_prose_devanagari_double_danda_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t12_prose_devanagari_double_danda
        data = _case(_FULL, 'Work stays blocked until the ruling lands॥')
        _assert_charged(self, data, 284, "008d6d765208")
        _assert_whole(self, data, "fix12_g_t12_prose_devanagari_double_danda.md")
        _assert_whole(self, _twin(data), "fix12_g_t12_prose_devanagari_double_danda_twin.md")

    def test_ch343_03_t13_cost_myanmar_section_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t13_cost_myanmar_section
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked။')
        _assert_charged(self, data, 284, "4cdc93088d7e")
        _assert_whole(self, data, "fix12_g_t13_cost_myanmar_section.md")
        _assert_whole(self, _twin(data), "fix12_g_t13_cost_myanmar_section_twin.md")

    def test_ch343_04_t14_prose_tibetan_shad_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t14_prose_tibetan_shad
        data = _case(_FULL, 'Work stays blocked until the ruling lands།')
        _assert_charged(self, data, 284, "b7faaa5dc218")
        _assert_whole(self, data, "fix12_g_t14_prose_tibetan_shad.md")
        _assert_whole(self, _twin(data), "fix12_g_t14_prose_tibetan_shad_twin.md")

    def test_ch343_05_t15_question_small_question_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t15_question_small_question
        data = _case(_FULL, 'Question: Which option should we take first﹖')
        _assert_charged(self, data, 286, "9fa3f9dd19fc")
        _assert_whole(self, data, "fix12_g_t15_question_small_question.md")
        _assert_whole(self, _twin(data), "fix12_g_t15_question_small_question_twin.md")

    def test_ch343_06_t16_prose_small_exclamation_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t16_prose_small_exclamation
        data = _case(_FULL, 'Work stays blocked until the ruling lands﹗')
        _assert_charged(self, data, 284, "4176d8558e58")
        _assert_whole(self, data, "fix12_g_t16_prose_small_exclamation.md")
        _assert_whole(self, _twin(data), "fix12_g_t16_prose_small_exclamation_twin.md")

    def test_ch343_07_t17_prose_khmer_khan_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t17_prose_khmer_khan
        data = _case(_FULL, 'Work stays blocked until the ruling lands។')
        _assert_charged(self, data, 284, "deac5b43a613")
        _assert_whole(self, data, "fix12_g_t17_prose_khmer_khan.md")
        _assert_whole(self, _twin(data), "fix12_g_t17_prose_khmer_khan_twin.md")

    def test_ch343_08_t08_prose_myanmar_little_section_stands_whole(self):
        # Source: attack12-12-scratch/cases/t08_prose_myanmar_little_section
        data = _case(_FULL, 'Work stays blocked until the ruling lands፣')
        _assert_charged(self, data, 284, "ab3af621aa27")
        _assert_whole(self, data, "fix12_g_t08_prose_myanmar_little_section.md")
        _assert_whole(self, _twin(data), "fix12_g_t08_prose_myanmar_little_section_twin.md")

    def test_ch343_09_t09_prose_tibetan_gter_shad_stands_whole(self):
        # Source: attack12-12-scratch/cases/t09_prose_tibetan_gter_shad
        data = _case(_FULL, 'Work stays blocked until the ruling lands༔')
        _assert_charged(self, data, 284, "84f401868818")
        _assert_whole(self, data, "fix12_g_t09_prose_tibetan_gter_shad.md")
        _assert_whole(self, _twin(data), "fix12_g_t09_prose_tibetan_gter_shad_twin.md")

    def test_ch343_10_t10_cost_vai_full_stop_stands_whole(self):
        # Source: attack12-12-scratch/cases/t10_cost_vai_full_stop
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked꘎')
        _assert_charged(self, data, 284, "8f4767279b78")
        _assert_whole(self, data, "fix12_g_t10_cost_vai_full_stop.md")
        _assert_whole(self, _twin(data), "fix12_g_t10_cost_vai_full_stop_twin.md")

    def test_ch343_11_t11_prose_reversed_question_stands_whole(self):
        # Source: attack12-12-scratch/cases/t11_prose_reversed_question
        data = _case(_FULL, 'Work stays blocked until the ruling lands⸮')
        _assert_charged(self, data, 284, "b881269aa7c0")
        _assert_whole(self, data, "fix12_g_t11_prose_reversed_question.md")
        _assert_whole(self, _twin(data), "fix12_g_t11_prose_reversed_question_twin.md")

    def test_ch343_12_t12_question_arabic_question_stands_whole(self):
        # Source: attack12-12-scratch/cases/t12_question_arabic_question
        data = _case(_FULL, 'Question: Which option should we take first؟')
        _assert_charged(self, data, 285, "6d9cdd9e2379")
        _assert_whole(self, data, "fix12_g_t12_question_arabic_question.md")
        _assert_whole(self, _twin(data), "fix12_g_t12_question_arabic_question_twin.md")

    def test_ch343_13_t13_prose_lisu_full_stop_stands_whole(self):
        # Source: attack12-12-scratch/cases/t13_prose_lisu_full_stop
        data = _case(_FULL, 'Work stays blocked until the ruling lands꓿')
        _assert_charged(self, data, 284, "992d5b5f908a")
        _assert_whole(self, data, "fix12_g_t13_prose_lisu_full_stop.md")
        _assert_whole(self, _twin(data), "fix12_g_t13_prose_lisu_full_stop_twin.md")

# ---------------------------------------------------------------------
# CH344
# ---------------------------------------------------------------------

class Step17Fix12GGroupStripProseTest(unittest.TestCase):
    """CH-344: a final line closing on a balanced bracket group standing behind a charged closing character stands whole in the prose branch, the group strip's second pass disregarding every member of the restated strip set except the ASCII closing brackets."""

    def test_ch344_01_t18_group_math_white_square_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t18_group_math_white_square
        data = _case(_FULL, 'The note stands (as the appendix records)⟧')
        _assert_charged(self, data, 284, "ba9a7fa34f1d")
        _assert_whole(self, data, "fix12_g_t18_group_math_white_square.md")
        _assert_whole(self, _twin(data), "fix12_g_t18_group_math_white_square_twin.md")

    def test_ch344_02_t19_group_right_white_paren_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t19_group_right_white_paren
        data = _case(_FULL, 'The note stands (as the appendix records)⦆')
        _assert_charged(self, data, 284, "7a0e288f08f3")
        _assert_whole(self, data, "fix12_g_t19_group_right_white_paren.md")
        _assert_whole(self, _twin(data), "fix12_g_t19_group_right_white_paren_twin.md")

    def test_ch344_03_t20_group_double_prime_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t20_group_double_prime
        data = _case(_FULL, 'The note stands (as the appendix records)″')
        _assert_charged(self, data, 284, "8b7a6c416f4b")
        _assert_whole(self, data, "fix12_g_t20_group_double_prime.md")
        _assert_whole(self, _twin(data), "fix12_g_t20_group_double_prime_twin.md")

    def test_ch344_04_t21_group_heavy_right_quote_orn_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t21_group_heavy_right_quote_orn
        data = _case(_FULL, 'The note stands (as the appendix records)❞')
        _assert_charged(self, data, 284, "59d46bdc8b0f")
        _assert_whole(self, data, "fix12_g_t21_group_heavy_right_quote_orn.md")
        _assert_whole(self, _twin(data), "fix12_g_t21_group_heavy_right_quote_orn_twin.md")

    def test_ch344_05_t14_prose_group_heavy_angle_orn_stands_whole(self):
        # Source: attack12-12-scratch/cases/t14_prose_group_heavy_angle_orn
        data = _case(_FULL, 'The note stands (as the appendix records)❱')
        _assert_charged(self, data, 284, "227593108566")
        _assert_whole(self, data, "fix12_g_t14_prose_group_heavy_angle_orn.md")
        _assert_whole(self, _twin(data), "fix12_g_t14_prose_group_heavy_angle_orn_twin.md")

    def test_ch344_06_t15_prose_group_tibetan_ang_stands_whole(self):
        # Source: attack12-12-scratch/cases/t15_prose_group_tibetan_ang
        data = _case(_FULL, 'The note stands (as the appendix records)༽')
        _assert_charged(self, data, 284, "bc0f6d42248c")
        _assert_whole(self, data, "fix12_g_t15_prose_group_tibetan_ang.md")
        _assert_whole(self, _twin(data), "fix12_g_t15_prose_group_tibetan_ang_twin.md")

    def test_ch344_07_t16_prose_group_small_paren_stands_whole(self):
        # Source: attack12-12-scratch/cases/t16_prose_group_small_paren
        data = _case(_FULL, 'The note stands (as the appendix records)﹚')
        _assert_charged(self, data, 284, "f964d5ccdb33")
        _assert_whole(self, data, "fix12_g_t16_prose_group_small_paren.md")
        _assert_whole(self, _twin(data), "fix12_g_t16_prose_group_small_paren_twin.md")

# ---------------------------------------------------------------------
# CH345
# ---------------------------------------------------------------------

class Step17Fix12GGroupStripLabelledTest(unittest.TestCase):
    """CH-345: a sentence valued labelled value closing on a balanced bracket group standing behind a charged closing character stands whole in the labelled branch, the p17 bound standing unmoved."""

    def test_ch345_01_t22_cost_group_math_white_square_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t22_cost_group_math_white_square
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)⟧')
        _assert_charged(self, data, 309, "d5638ea3897b")
        _assert_whole(self, data, "fix12_g_t22_cost_group_math_white_square.md")
        _assert_whole(self, _twin(data), "fix12_g_t22_cost_group_math_white_square_twin.md")

    def test_ch345_02_t23_cost_group_medium_right_paren_orn_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t23_cost_group_medium_right_paren_orn
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)❩')
        _assert_charged(self, data, 309, "e79fa7a3ee18")
        _assert_whole(self, data, "fix12_g_t23_cost_group_medium_right_paren_orn.md")
        _assert_whole(self, _twin(data), "fix12_g_t23_cost_group_medium_right_paren_orn_twin.md")

    def test_ch345_03_t24_cost_group_low_double_prime_quote_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t24_cost_group_low_double_prime_quote
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)〟')
        _assert_charged(self, data, 309, "48d2d6f55b7f")
        _assert_whole(self, data, "fix12_g_t24_cost_group_low_double_prime_quote.md")
        _assert_whole(self, _twin(data), "fix12_g_t24_cost_group_low_double_prime_quote_twin.md")

    def test_ch345_04_t25_cost_group_right_square_quill_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t25_cost_group_right_square_quill
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)⁆')
        _assert_charged(self, data, 309, "0e021e33802b")
        _assert_whole(self, data, "fix12_g_t25_cost_group_right_square_quill.md")
        _assert_whole(self, _twin(data), "fix12_g_t25_cost_group_right_square_quill_twin.md")

    def test_ch345_05_t17_cost_group_flat_paren_orn_stands_whole(self):
        # Source: attack12-12-scratch/cases/t17_cost_group_flat_paren_orn
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)❫')
        _assert_charged(self, data, 309, "391be396ab4b")
        _assert_whole(self, data, "fix12_g_t17_cost_group_flat_paren_orn.md")
        _assert_whole(self, _twin(data), "fix12_g_t17_cost_group_flat_paren_orn_twin.md")

    def test_ch345_06_t19_cost_group_small_tortoise_stands_whole(self):
        # Source: attack12-12-scratch/cases/t19_cost_group_small_tortoise
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)﹜')
        _assert_charged(self, data, 309, "eea837118ebc")
        _assert_whole(self, data, "fix12_g_t19_cost_group_small_tortoise.md")
        _assert_whole(self, _twin(data), "fix12_g_t19_cost_group_small_tortoise_twin.md")

# ---------------------------------------------------------------------
# CH346
# ---------------------------------------------------------------------

class Step17Fix12GRomanBulletTest(unittest.TestCase):
    """CH-346: complete bullet items under single character Unicode roman numeral markers of the archaic range past U+2181 stand whole, on colon free content, in every dress the standing markers take."""

    def test_ch346_01_t26_bullet_unicode_ten_thousand_dot_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t26_bullet_unicode_ten_thousand_dot
        data = _case(_FULL, 'ↂ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "7f795f756739")
        _assert_whole(self, data, "fix12_g_t26_bullet_unicode_ten_thousand_dot.md")
        _assert_whole(self, _twin(data), "fix12_g_t26_bullet_unicode_ten_thousand_dot_twin.md")

    def test_ch346_02_t27_bullet_unicode_reversed_100_paren_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t27_bullet_unicode_reversed_100_paren
        data = _case(_FULL, 'Ↄ) Option B leaves the note adopted')
        _assert_charged(self, data, 277, "3788262c8710")
        _assert_whole(self, data, "fix12_g_t27_bullet_unicode_reversed_100_paren.md")
        _assert_whole(self, _twin(data), "fix12_g_t27_bullet_unicode_reversed_100_paren_twin.md")

    def test_ch346_03_t28_bullet_unicode_50000_bracket_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t28_bullet_unicode_50000_bracket
        data = _case(_FULL, 'ↇ] Option B leaves the note adopted')
        _assert_charged(self, data, 277, "74ee5e96d7d3")
        _assert_whole(self, data, "fix12_g_t28_bullet_unicode_50000_bracket.md")
        _assert_whole(self, _twin(data), "fix12_g_t28_bullet_unicode_50000_bracket_twin.md")

    def test_ch346_04_t29_bullet_unicode_100000_parenform_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t29_bullet_unicode_100000_parenform
        data = _case(_FULL, '(ↈ) Option B leaves the note adopted')
        _assert_charged(self, data, 278, "ae2f991e8538")
        _assert_whole(self, data, "fix12_g_t29_bullet_unicode_100000_parenform.md")
        _assert_whole(self, _twin(data), "fix12_g_t29_bullet_unicode_100000_parenform_twin.md")

    def test_ch346_05_t30_bullet_unicode_six_late_brace_stands_whole(self):
        # Source: attack12-01-scratch/fresh/t30_bullet_unicode_six_late_brace
        data = _case(_FULL, '{ↅ} Option B leaves the note adopted')
        _assert_charged(self, data, 278, "e95325430a45")
        _assert_whole(self, data, "fix12_g_t30_bullet_unicode_six_late_brace.md")
        _assert_whole(self, _twin(data), "fix12_g_t30_bullet_unicode_six_late_brace_twin.md")

    def test_ch346_06_t20_bullet_reversed_hundred_dot_stands_whole(self):
        # Source: attack12-12-scratch/cases/t20_bullet_reversed_hundred_dot
        data = _case(_FULL, 'ↄ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "0bfbfd4a6ed7")
        _assert_whole(self, data, "fix12_g_t20_bullet_reversed_hundred_dot.md")
        _assert_whole(self, _twin(data), "fix12_g_t20_bullet_reversed_hundred_dot_twin.md")

    def test_ch346_07_t21_bullet_fifty_early_closeparen_stands_whole(self):
        # Source: attack12-12-scratch/cases/t21_bullet_fifty_early_closeparen
        data = _case(_FULL, 'ↆ) Option B leaves the note adopted')
        _assert_charged(self, data, 277, "2d05fd8cda91")
        _assert_whole(self, data, "fix12_g_t21_bullet_fifty_early_closeparen.md")
        _assert_whole(self, _twin(data), "fix12_g_t21_bullet_fifty_early_closeparen_twin.md")

    def test_ch346_08_t22_bullet_fifty_early_braced_stands_whole(self):
        # Source: attack12-12-scratch/cases/t22_bullet_fifty_early_braced
        data = _case(_FULL, '{ↆ} Option B leaves the note adopted')
        _assert_charged(self, data, 278, "95adeb4d98a2")
        _assert_whole(self, data, "fix12_g_t22_bullet_fifty_early_braced.md")
        _assert_whole(self, _twin(data), "fix12_g_t22_bullet_fifty_early_braced_twin.md")

# ---------------------------------------------------------------------
# Pins and cut sides
# ---------------------------------------------------------------------

class Step17Fix12GPinsAndCutSidesTest(unittest.TestCase):
    """The cured forms of CH-302 to CH-306 stand as
    pins, the p17 bound form stands unmoved at its
    bound, and the cut sides stand: no widened
    character, mark, marker, or group strip rescues
    a line or item that closes nothing complete."""

    def test_pin_ch302_cured_math_double_angle(self):
        # Source: attack12-01-scratch/fresh/t34_prose_math_double_angle_control
        data = _case(_FULL, '⟪Work stays blocked until the ruling lands.⟫')
        _assert_charged(self, data, 288, "98be96a301eb")
        _assert_whole(self, data, "fix12_g_pin_ch302_cured_math_double_angle.md")
        _assert_whole(self, _twin(data), "fix12_g_pin_ch302_cured_math_double_angle_twin.md")

    def test_pin_ch304_cured_five_thousand(self):
        # Source: attack12-01-scratch/fresh/t35_bullet_unicode_5000_dot_control
        data = _case(_FULL, 'ↁ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "e31466c088cf")
        _assert_whole(self, data, "fix12_g_pin_ch304_cured_five_thousand.md")
        _assert_whole(self, _twin(data), "fix12_g_pin_ch304_cured_five_thousand_twin.md")

    def test_pin_ch302_cured_math_angle(self):
        # Source: attack12-12-scratch/cases/t04_prose_math_angle_close
        data = _case(_FULL, '⟨Work stays blocked until the ruling lands.⟩')
        _assert_charged(self, data, 288, "bc0496fb0e56")
        _assert_whole(self, data, "fix12_g_pin_ch302_cured_math_angle.md")
        _assert_whole(self, _twin(data), "fix12_g_pin_ch302_cured_math_angle_twin.md")

    def test_pin_ch306_cured_math_angle_group(self):
        # Source: attack12-12-scratch/cases/t18_cost_group_math_angle
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)⟩')
        _assert_charged(self, data, 309, "2e31ed1cd8b0")
        _assert_whole(self, data, "fix12_g_pin_ch306_cured_math_angle_group.md")
        _assert_whole(self, _twin(data), "fix12_g_pin_ch306_cured_math_angle_group_twin.md")

    def test_pin_ch304_cured_five_thousand_s13form(self):
        # Source: attack12-12-scratch/cases/t23_pin_bullet_five_thousand_dot
        data = _case(_FULL, 'ↁ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "e31466c088cf")
        _assert_whole(self, data, "fix12_g_pin_ch304_cured_five_thousand_s13form.md")
        _assert_whole(self, _twin(data), "fix12_g_pin_ch304_cured_five_thousand_s13form_twin.md")

    def test_pin_ch305_cured_group_tilde(self):
        # Source: attack12-12-scratch/cases/t24_pin_prose_group_tilde
        data = _case(_FULL, 'The note stands (as the appendix records)~')
        _assert_charged(self, data, 282, "b70a9ba26d51")
        _assert_whole(self, data, "fix12_g_pin_ch305_cured_group_tilde.md")
        _assert_whole(self, _twin(data), "fix12_g_pin_ch305_cured_group_tilde_twin.md")

    def test_cut_prose_math_white_square_noclose(self):
        # Source: attack12-01-scratch/fresh/t31_prose_math_white_square_noclose_cut
        data = _case(_FULL, '⟦Work stays blocked until the ruling lands⟧')
        _assert_charged(self, data, 287, "2d4a3d39ff61")
        _assert_cut(self, data, "fix12_g_cut_prose_math_white_square_noclose.md")
        _assert_whole(self, _twin(data), "fix12_g_cut_prose_math_white_square_noclose_twin.md")

    def test_cut_bullet_ten_thousand_joining(self):
        # Source: attack12-01-scratch/fresh/t32_bullet_unicode_ten_thousand_joining_cut
        data = _case(_FULL, 'ↂ. Option B leaves the note and')
        _assert_charged(self, data, 273, "d40662a6797b")
        _assert_cut(self, data, "fix12_g_cut_bullet_ten_thousand_joining.md")
        _assert_whole(self, _twin(data), "fix12_g_cut_bullet_ten_thousand_joining_twin.md")

    def test_cut_prose_empty_group_double_prime(self):
        # Source: attack12-01-scratch/fresh/t33_prose_empty_group_double_prime_cut
        data = _case(_FULL, 'The note stands ()″')
        _assert_charged(self, data, 261, "bb837bce282e")
        _assert_cut(self, data, "fix12_g_cut_prose_empty_group_double_prime.md")
        _assert_whole(self, _twin(data), "fix12_g_cut_prose_empty_group_double_prime_twin.md")

    def test_cut_prose_heavy_angle_orn_noclose(self):
        # Source: attack12-12-scratch/cases/t25_ctrl_prose_noclose_heavy_angle_orn
        data = _case(_FULL, '❰Work stays blocked until the ruling lands❱')
        _assert_charged(self, data, 287, "0340641934e9")
        _assert_cut(self, data, "fix12_g_cut_prose_heavy_angle_orn_noclose.md")
        _assert_whole(self, _twin(data), "fix12_g_cut_prose_heavy_angle_orn_noclose_twin.md")

    def test_cut_bullet_reversed_hundred_fragment(self):
        # Source: attack12-12-scratch/cases/t26_ctrl_bullet_reversed_hundred_fragment
        data = _case(_FULL, 'ↄ. Option B leaves the note adop')
        _assert_charged(self, data, 274, "6bf473f40686")
        _assert_cut(self, data, "fix12_g_cut_bullet_reversed_hundred_fragment.md")
        _assert_whole(self, _twin(data), "fix12_g_cut_bullet_reversed_hundred_fragment_twin.md")

    def test_pin_p17_bound_form_stands_cut(self):
        # The p17 form itself: a labelled group behind
        # an interleaved run and a closing double
        # quote, standing at its section 81 ruling (f)
        # bound in both eras, beside its parsed twin.
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _ZWSP + "\"")
        _assert_cut(self, data, "fix12_g_pin_p17.md")
        _assert_whole(self, _twin(data),
                      "fix12_g_pin_p17_twin.md")
