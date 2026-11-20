"""Step 17 fix wave 11, Fix Seat G tests, test first.

Charges CH-302 to CH-306, the strip set family of
round 11 (Cluster G of design/steps/
step-17r-r11-triage-prep.md, adopted whole at
section 108 of design/steps/step-17r-record.md),
sourced at round 11 attack seat 2, design/steps/
step-17r-r11-seat02-run.md (ATK11-2-01 to
ATK11-2-05), and round 11 attack seat 13,
design/steps/step-17r-r11-seat13-run.md (F-1 to
F-10), consolidated as T11-30 to T11-34. Locus:
product/decision_queue_validator/parse.py only,
at _final_line_is_cut_off and
_labelled_value_stands_whole, the sentence close
readings as cured at CH-257 to CH-263.

CH-302 (Low), T11-30, the closing character limb.
A sentence closing on a closing character outside
the cured strip set is read as cut, in the prose
branch and in the sentence valued labelled branch
alike. Restated strip set: the standing members
and the CH-257 members, plus exactly these
charged members: the right tortoise shell bracket
(U+3015), the right double angle bracket
(U+300B), the right angle bracket (U+3009), the
halfwidth right corner bracket (U+FF63), the
right white square bracket (U+301B), the medium
right curly bracket ornament (U+2775), the right
white lenticular bracket (U+3017), the
mathematical right double angle bracket
(U+27EB), the double high reversed 9 quotation
mark (U+201F), the prime (U+2032), the right
white tortoise shell bracket (U+3019), the
fullwidth right white parenthesis (U+FF60), and
the double prime quotation mark (U+301E).

CH-303 (Low), T11-31, the sentence close mark
limb. A sentence closing on a sentence close mark
outside the cured set is read as cut, in both
branches alike. Restated close mark set: the
standing marks and the CH-258 marks, plus exactly
these charged marks: the double exclamation mark
(U+203C), the exclamation question mark (U+2049),
the one dot leader (U+2024), the vertical
ellipsis (U+22EE), the halfwidth ideographic full
stop (U+FF61), the small full stop (U+FE52), the
double question mark (U+2047), the inverted
interrobang (U+2E18), the question exclamation
mark (U+2048), the Armenian full stop (U+0589),
and the Ethiopic full stop (U+1362), on every
sentence close test of both branches, the
standing order test and the probe alike.

CH-304 (Low), T11-32, the roman numeral bullet
limb. Complete bullet items under single
character Unicode roman numeral markers past the
CH-263 forms are read as cut prose, on colon free
content. Restated roman numeral bullet forms: the
single character alternatives carry the capital
forms U+2160 to U+216F and the small forms U+2170
to U+217F, plus the roman numeral one thousand
(U+2180) and five thousand (U+2181), in the full
stop form and in the closing parenthesis and
bracket form as CH-263 left them, and further in
the parenthesised form, the opening bracket form,
and the braced form the charges name, under the
same fragment, joining word, and cut reference
guards the standing markers take.

CH-305 (Low), T11-33, the group strip limb, prose
and final line forms. A final line closing on a
balanced bracket group standing behind a closing
character the group strip does not carry is read
as cut. Restated group strip passes: the first
pass stands as CH-217 left it; the second pass
disregards, in alternation with a trailing run of
the ground classes, every member of the restated
sentence close strip set of CH-302 except the
ASCII closing brackets, whose group the reading
seeks, and counts only where matter stands before
the group once the quote characters and the run
are disregarded, as CH-261's narrowing states.

CH-306 (Low), T11-34, the group strip limb,
labelled value forms. A sentence valued labelled
value closing on a balanced bracket group standing
behind a closing character other than the two
guillemets is read as cut. Restated labelled group
probe: the probe on the value as written
disregards, in alternation with a trailing run of
the ground classes, every member of the restated
sentence close strip set of CH-302 except the
standing quote characters (the double quote, the
single quote, and the two closing curly quotes),
so the p17 form (a group behind an interleaved
run and a closing double quote) takes no probe
reading and stands unmoved at its section 81
ruling (f) bound, pinned here in both eras.

Constructions stand byte for byte as the round 11
attack case files stand, on the template family
of the earlier rounds, each asserted at its
recorded byte count and sha256 head as a
construction fact; where the two seats' staged
bytes stand identical, the construction stands
once with both sources named. The cured CH-257
to CH-263 forms stand as pins in the last class,
and the p17 bound form stands unmoved as a pin at
its bound in every charge of this cluster.

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
# CH302
# ---------------------------------------------------------------------

class Step17Fix11GClosingCharacterTest(unittest.TestCase):
    """CH-302: a sentence closing behind a closing character of the charged ring past the CH-257 strip set stands whole, in the prose branch and in the sentence valued labelled branch alike."""

    def test_ch302_01_r01_prose_white_lenticular_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r01_prose_white_lenticular; attack11-13-scratch/cases/r04_prose_tortoise_close
        data = _case(_FULL, '〔Work stays blocked until the ruling lands.〕')
        _assert_charged(self, data, 288, "1df6b41a86cc")
        _assert_whole(self, data, "fix11_g_r01_prose_white_lenticular.md")
        _assert_whole(self, _twin(data), "fix11_g_r01_prose_white_lenticular_twin.md")

    def test_ch302_02_r02_prose_double_angle_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r02_prose_double_angle; attack11-13-scratch/cases/r01_prose_double_angle_close
        data = _case(_FULL, '《Work stays blocked until the ruling lands.》')
        _assert_charged(self, data, 288, "ebc4c92f75c2")
        _assert_whole(self, data, "fix11_g_r02_prose_double_angle.md")
        _assert_whole(self, _twin(data), "fix11_g_r02_prose_double_angle_twin.md")

    def test_ch302_03_r03_cost_angle_cjk_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r03_cost_angle_cjk
        data = _case(_FULL, 'Cost of deciding late: 〈Work stays blocked.〉')
        _assert_charged(self, data, 288, "b88dea4085fe")
        _assert_whole(self, data, "fix11_g_r03_cost_angle_cjk.md")
        _assert_whole(self, _twin(data), "fix11_g_r03_cost_angle_cjk_twin.md")

    def test_ch302_04_r04_prose_halfwidth_corner_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r04_prose_halfwidth_corner
        data = _case(_FULL, '｢Work stays blocked until the ruling lands.｣')
        _assert_charged(self, data, 288, "ab31fcee6c20")
        _assert_whole(self, data, "fix11_g_r04_prose_halfwidth_corner.md")
        _assert_whole(self, _twin(data), "fix11_g_r04_prose_halfwidth_corner_twin.md")

    def test_ch302_05_r05_prose_white_square_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r05_prose_white_square
        data = _case(_FULL, '〚Work stays blocked until the ruling lands.〛')
        _assert_charged(self, data, 288, "f8f5af0b27d4")
        _assert_whole(self, data, "fix11_g_r05_prose_white_square.md")
        _assert_whole(self, _twin(data), "fix11_g_r05_prose_white_square_twin.md")

    def test_ch302_06_r06_prose_ornate_paren_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r06_prose_ornate_paren
        data = _case(_FULL, '❴Work stays blocked until the ruling lands.❵')
        _assert_charged(self, data, 288, "ee7a43b7f38e")
        _assert_whole(self, data, "fix11_g_r06_prose_ornate_paren.md")
        _assert_whole(self, _twin(data), "fix11_g_r06_prose_ornate_paren_twin.md")

    def test_ch302_07_r07_question_white_lenticular_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r07_question_white_lenticular
        data = _case(_FULL, 'Question: Which option should we take first?〕')
        _assert_charged(self, data, 287, "b68486086fdf")
        _assert_whole(self, data, "fix11_g_r07_question_white_lenticular.md")
        _assert_whole(self, _twin(data), "fix11_g_r07_question_white_lenticular_twin.md")

    def test_ch302_08_r08_prose_white_lenticular_bracket_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r08_prose_white_lenticular_bracket; attack11-13-scratch/cases/r03_prose_white_lenticular_close
        data = _case(_FULL, '〖Work stays blocked until the ruling lands.〗')
        _assert_charged(self, data, 288, "42950ec5c2d0")
        _assert_whole(self, data, "fix11_g_r08_prose_white_lenticular_bracket.md")
        _assert_whole(self, _twin(data), "fix11_g_r08_prose_white_lenticular_bracket_twin.md")

    def test_ch302_09_s01_prose_math_double_angle_stands_whole(self):
        # Sources: attack11-2-scratch/fresh2/s01_prose_math_double_angle; attack11-13-scratch/cases/r06_prose_math_double_angle_close
        data = _case(_FULL, '⟪Work stays blocked until the ruling lands.⟫')
        _assert_charged(self, data, 288, "98be96a301eb")
        _assert_whole(self, data, "fix11_g_s01_prose_math_double_angle.md")
        _assert_whole(self, _twin(data), "fix11_g_s01_prose_math_double_angle_twin.md")

    def test_ch302_10_r02_cost_double_angle_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r02_cost_double_angle_close
        data = _case(_FULL, 'Cost of deciding late: 《Work stays blocked.》')
        _assert_charged(self, data, 288, "e1f2176293b5")
        _assert_whole(self, data, "fix11_g_r02_cost_double_angle_close.md")
        _assert_whole(self, _twin(data), "fix11_g_r02_cost_double_angle_close_twin.md")

    def test_ch302_11_r05_cost_tortoise_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r05_cost_tortoise_close
        data = _case(_FULL, 'Cost of deciding late: 〔Work stays blocked.〕')
        _assert_charged(self, data, 288, "1b28018120d9")
        _assert_whole(self, data, "fix11_g_r05_cost_tortoise_close.md")
        _assert_whole(self, _twin(data), "fix11_g_r05_cost_tortoise_close_twin.md")

    def test_ch302_12_r07_question_double_angle_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r07_question_double_angle_close
        data = _case(_FULL, 'Question: 《Which option should we take first?》')
        _assert_charged(self, data, 290, "2e44f9dcfad5")
        _assert_whole(self, data, "fix11_g_r07_question_double_angle_close.md")
        _assert_whole(self, _twin(data), "fix11_g_r07_question_double_angle_close_twin.md")

    def test_ch302_13_r08_prose_reversed_double_quote_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r08_prose_reversed_double_quote
        data = _case(_FULL, '‟Work stays blocked until the ruling lands.‟')
        _assert_charged(self, data, 288, "c5ecb18aac7c")
        _assert_whole(self, data, "fix11_g_r08_prose_reversed_double_quote.md")
        _assert_whole(self, _twin(data), "fix11_g_r08_prose_reversed_double_quote_twin.md")

    def test_ch302_14_r09_prose_prime_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r09_prose_prime_close
        data = _case(_FULL, '′Work stays blocked until the ruling lands.′')
        _assert_charged(self, data, 288, "a2eaf1a4c5cf")
        _assert_whole(self, data, "fix11_g_r09_prose_prime_close.md")
        _assert_whole(self, _twin(data), "fix11_g_r09_prose_prime_close_twin.md")

    def test_ch302_15_s01_prose_white_tortoise_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s01_prose_white_tortoise_close
        data = _case(_FULL, '〘Work stays blocked until the ruling lands.〙')
        _assert_charged(self, data, 288, "8a58226d5830")
        _assert_whole(self, data, "fix11_g_s01_prose_white_tortoise_close.md")
        _assert_whole(self, _twin(data), "fix11_g_s01_prose_white_tortoise_close_twin.md")

    def test_ch302_16_s02_cost_fullwidth_white_paren_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s02_cost_fullwidth_white_paren_close
        data = _case(_FULL, 'Cost of deciding late: ｟Work stays blocked.｠')
        _assert_charged(self, data, 288, "0446b473170e")
        _assert_whole(self, data, "fix11_g_s02_cost_fullwidth_white_paren_close.md")
        _assert_whole(self, _twin(data), "fix11_g_s02_cost_fullwidth_white_paren_close_twin.md")

    def test_ch302_17_s03_prose_double_prime_quote_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s03_prose_double_prime_quote_close
        data = _case(_FULL, '〝Work stays blocked until the ruling lands.〞')
        _assert_charged(self, data, 288, "b3addd527c8d")
        _assert_whole(self, data, "fix11_g_s03_prose_double_prime_quote_close.md")
        _assert_whole(self, _twin(data), "fix11_g_s03_prose_double_prime_quote_close_twin.md")

# ---------------------------------------------------------------------
# CH303
# ---------------------------------------------------------------------

class Step17Fix11GCloseMarkTest(unittest.TestCase):
    """CH-303: a sentence closing on a sentence close mark of the charged ring past the CH-258 set stands whole, in both branches alike, on the standing order test and on the probe alike."""

    def test_ch303_01_r09_prose_double_exclamation_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r09_prose_double_exclamation; attack11-13-scratch/cases/r10_prose_double_exclamation
        data = _case(_FULL, 'Work stays blocked until the ruling lands‼')
        _assert_charged(self, data, 284, "46bfe8f7e7ae")
        _assert_whole(self, data, "fix11_g_r09_prose_double_exclamation.md")
        _assert_whole(self, _twin(data), "fix11_g_r09_prose_double_exclamation_twin.md")

    def test_ch303_02_r10_question_excl_question_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r10_question_excl_question
        data = _case(_FULL, 'Question: Which option should we take first⁉')
        _assert_charged(self, data, 286, "ee2d312b70bf")
        _assert_whole(self, data, "fix11_g_r10_question_excl_question.md")
        _assert_whole(self, _twin(data), "fix11_g_r10_question_excl_question_twin.md")

    def test_ch303_03_r11_prose_one_dot_leader_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r11_prose_one_dot_leader; attack11-13-scratch/cases/r15_prose_one_dot_leader
        data = _case(_FULL, 'Work stays blocked until the ruling lands․')
        _assert_charged(self, data, 284, "321b623c61ab")
        _assert_whole(self, data, "fix11_g_r11_prose_one_dot_leader.md")
        _assert_whole(self, _twin(data), "fix11_g_r11_prose_one_dot_leader_twin.md")

    def test_ch303_04_r12_prose_vertical_ellipsis_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r12_prose_vertical_ellipsis
        data = _case(_FULL, 'Work stays blocked until the ruling lands⋮')
        _assert_charged(self, data, 284, "67e4b19d2566")
        _assert_whole(self, data, "fix11_g_r12_prose_vertical_ellipsis.md")
        _assert_whole(self, _twin(data), "fix11_g_r12_prose_vertical_ellipsis_twin.md")

    def test_ch303_05_r13_cost_halfwidth_stop_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r13_cost_halfwidth_stop
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked｡')
        _assert_charged(self, data, 284, "c930c832658c")
        _assert_whole(self, data, "fix11_g_r13_cost_halfwidth_stop.md")
        _assert_whole(self, _twin(data), "fix11_g_r13_cost_halfwidth_stop_twin.md")

    def test_ch303_06_r14_prose_small_stop_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r14_prose_small_stop
        data = _case(_FULL, 'Work stays blocked until the ruling lands﹒')
        _assert_charged(self, data, 284, "7242c38cb4ba")
        _assert_whole(self, data, "fix11_g_r14_prose_small_stop.md")
        _assert_whole(self, _twin(data), "fix11_g_r14_prose_small_stop_twin.md")

    def test_ch303_07_r15_question_double_question_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r15_question_double_question
        data = _case(_FULL, 'Question: Which option should we take first⁇')
        _assert_charged(self, data, 286, "7e36c3cd1d79")
        _assert_whole(self, data, "fix11_g_r15_question_double_question.md")
        _assert_whole(self, _twin(data), "fix11_g_r15_question_double_question_twin.md")

    def test_ch303_08_s02_question_inverted_interrobang_stands_whole(self):
        # Sources: attack11-2-scratch/fresh2/s02_question_inverted_interrobang
        data = _case(_FULL, 'Question: Which option should we take first⸘')
        _assert_charged(self, data, 286, "2d6cc0d39cf8")
        _assert_whole(self, data, "fix11_g_s02_question_inverted_interrobang.md")
        _assert_whole(self, _twin(data), "fix11_g_s02_question_inverted_interrobang_twin.md")

    def test_ch303_09_s08_cost_question_exclamation_stands_whole(self):
        # Sources: attack11-2-scratch/fresh2/s08_cost_question_exclamation
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked⁈')
        _assert_charged(self, data, 284, "20f9f5030f77")
        _assert_whole(self, data, "fix11_g_s08_cost_question_exclamation.md")
        _assert_whole(self, _twin(data), "fix11_g_s08_cost_question_exclamation_twin.md")

    def test_ch303_10_r11_cost_double_exclamation_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r11_cost_double_exclamation
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked‼')
        _assert_charged(self, data, 284, "5932ccc68f4b")
        _assert_whole(self, data, "fix11_g_r11_cost_double_exclamation.md")
        _assert_whole(self, _twin(data), "fix11_g_r11_cost_double_exclamation_twin.md")

    def test_ch303_11_r12_prose_double_question_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r12_prose_double_question
        data = _case(_FULL, 'Work stays blocked until the ruling lands⁇')
        _assert_charged(self, data, 284, "cac5f6f0d9ce")
        _assert_whole(self, data, "fix11_g_r12_prose_double_question.md")
        _assert_whole(self, _twin(data), "fix11_g_r12_prose_double_question_twin.md")

    def test_ch303_12_r13_prose_question_exclamation_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r13_prose_question_exclamation
        data = _case(_FULL, 'Work stays blocked until the ruling lands⁉')
        _assert_charged(self, data, 284, "d28bd4111840")
        _assert_whole(self, data, "fix11_g_r13_prose_question_exclamation.md")
        _assert_whole(self, _twin(data), "fix11_g_r13_prose_question_exclamation_twin.md")

    def test_ch303_13_r14_prose_halfwidth_ideographic_stop_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r14_prose_halfwidth_ideographic_stop
        data = _case(_FULL, 'Work stays blocked until the ruling lands｡')
        _assert_charged(self, data, 284, "1cd08cde88db")
        _assert_whole(self, data, "fix11_g_r14_prose_halfwidth_ideographic_stop.md")
        _assert_whole(self, _twin(data), "fix11_g_r14_prose_halfwidth_ideographic_stop_twin.md")

    def test_ch303_14_s04_prose_exclamation_question_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s04_prose_exclamation_question
        data = _case(_FULL, 'Work stays blocked until the ruling lands⁈')
        _assert_charged(self, data, 284, "e9d531ae0276")
        _assert_whole(self, data, "fix11_g_s04_prose_exclamation_question.md")
        _assert_whole(self, _twin(data), "fix11_g_s04_prose_exclamation_question_twin.md")

    def test_ch303_15_s05_prose_armenian_full_stop_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s05_prose_armenian_full_stop
        data = _case(_FULL, 'Work stays blocked until the ruling lands։')
        _assert_charged(self, data, 283, "7b44e34acdfa")
        _assert_whole(self, data, "fix11_g_s05_prose_armenian_full_stop.md")
        _assert_whole(self, _twin(data), "fix11_g_s05_prose_armenian_full_stop_twin.md")

    def test_ch303_16_s06_cost_ethiopic_full_stop_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s06_cost_ethiopic_full_stop
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked።')
        _assert_charged(self, data, 284, "9cac76a52992")
        _assert_whole(self, data, "fix11_g_s06_cost_ethiopic_full_stop.md")
        _assert_whole(self, _twin(data), "fix11_g_s06_cost_ethiopic_full_stop_twin.md")

# ---------------------------------------------------------------------
# CH304
# ---------------------------------------------------------------------

class Step17Fix11GRomanBulletTest(unittest.TestCase):
    """CH-304: a complete bullet item under a single character roman numeral marker past the CH-263 forms stands whole, on colon free content, under the standing guards."""

    def test_ch304_01_r27_bullet_unicode_cap_L_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r27_bullet_unicode_cap_L
        data = _case(_FULL, 'Ⅼ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "790ba0a8a0ad")
        _assert_whole(self, data, "fix11_g_r27_bullet_unicode_cap_L.md")
        _assert_whole(self, _twin(data), "fix11_g_r27_bullet_unicode_cap_L_twin.md")

    def test_ch304_02_r28_bullet_unicode_cap_C_paren_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r28_bullet_unicode_cap_C_paren
        data = _case(_FULL, 'Ⅽ) Option B leaves the note adopted')
        _assert_charged(self, data, 277, "7a615af5b6bd")
        _assert_whole(self, data, "fix11_g_r28_bullet_unicode_cap_C_paren.md")
        _assert_whole(self, _twin(data), "fix11_g_r28_bullet_unicode_cap_C_paren_twin.md")

    def test_ch304_03_r29_bullet_unicode_low_l_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r29_bullet_unicode_low_l
        data = _case(_FULL, 'ⅼ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "147114a8e102")
        _assert_whole(self, data, "fix11_g_r29_bullet_unicode_low_l.md")
        _assert_whole(self, _twin(data), "fix11_g_r29_bullet_unicode_low_l_twin.md")

    def test_ch304_04_r30_bullet_unicode_low_m_bracket_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r30_bullet_unicode_low_m_bracket
        data = _case(_FULL, 'ⅿ] Option B leaves the note adopted')
        _assert_charged(self, data, 277, "85b0291f4c13")
        _assert_whole(self, data, "fix11_g_r30_bullet_unicode_low_m_bracket.md")
        _assert_whole(self, _twin(data), "fix11_g_r30_bullet_unicode_low_m_bracket_twin.md")

    def test_ch304_05_s05_bullet_unicode_low_d_stands_whole(self):
        # Sources: attack11-2-scratch/fresh2/s05_bullet_unicode_low_d
        data = _case(_FULL, 'ⅾ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "eed67c2ec9d6")
        _assert_whole(self, data, "fix11_g_s05_bullet_unicode_low_d.md")
        _assert_whole(self, _twin(data), "fix11_g_s05_bullet_unicode_low_d_twin.md")

    def test_ch304_06_r16_bullet_paren_single_char_roman_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r16_bullet_paren_single_char_roman
        data = _case(_FULL, '(Ⅳ) Option B leaves the note adopted')
        _assert_charged(self, data, 278, "bebb001ef45a")
        _assert_whole(self, data, "fix11_g_r16_bullet_paren_single_char_roman.md")
        _assert_whole(self, _twin(data), "fix11_g_r16_bullet_paren_single_char_roman_twin.md")

    def test_ch304_07_r17_bullet_bracket_single_char_roman_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r17_bullet_bracket_single_char_roman
        data = _case(_FULL, '[Ⅳ] Option B leaves the note adopted')
        _assert_charged(self, data, 278, "e3db6d0c2a74")
        _assert_whole(self, data, "fix11_g_r17_bullet_bracket_single_char_roman.md")
        _assert_whole(self, _twin(data), "fix11_g_r17_bullet_bracket_single_char_roman_twin.md")

    def test_ch304_08_r18_bullet_paren_small_single_char_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r18_bullet_paren_small_single_char
        data = _case(_FULL, '(ⅳ) Option B leaves the note adopted')
        _assert_charged(self, data, 278, "674d9123b691")
        _assert_whole(self, data, "fix11_g_r18_bullet_paren_small_single_char.md")
        _assert_whole(self, _twin(data), "fix11_g_r18_bullet_paren_small_single_char_twin.md")

    def test_ch304_09_r19_bullet_thousand_single_char_dot_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r19_bullet_thousand_single_char_dot
        data = _case(_FULL, 'ↀ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "c4fb9a73972c")
        _assert_whole(self, data, "fix11_g_r19_bullet_thousand_single_char_dot.md")
        _assert_whole(self, _twin(data), "fix11_g_r19_bullet_thousand_single_char_dot_twin.md")

    def test_ch304_10_s07_bullet_brace_single_char_roman_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s07_bullet_brace_single_char_roman
        data = _case(_FULL, '{Ⅳ} Option B leaves the note adopted')
        _assert_charged(self, data, 278, "a8a183817cfe")
        _assert_whole(self, data, "fix11_g_s07_bullet_brace_single_char_roman.md")
        _assert_whole(self, _twin(data), "fix11_g_s07_bullet_brace_single_char_roman_twin.md")

    def test_ch304_11_s08_bullet_five_thousand_dot_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s08_bullet_five_thousand_dot
        data = _case(_FULL, 'ↁ. Option B leaves the note adopted')
        _assert_charged(self, data, 277, "e31466c088cf")
        _assert_whole(self, data, "fix11_g_s08_bullet_five_thousand_dot.md")
        _assert_whole(self, _twin(data), "fix11_g_s08_bullet_five_thousand_dot_twin.md")

# ---------------------------------------------------------------------
# CH305
# ---------------------------------------------------------------------

class Step17Fix11GGroupStripProseTest(unittest.TestCase):
    """CH-305: a final line closing on a balanced bracket group standing behind a charged character of the widened strip set stands whole in the prose branch, under the CH-261 narrowing."""

    def test_ch305_01_r16_group_left_guillemet_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r16_group_left_guillemet; attack11-13-scratch/cases/r20_prose_group_left_guillemet
        data = _case(_FULL, 'The note stands (as the appendix records)«')
        _assert_charged(self, data, 283, "10d711494696")
        _assert_whole(self, data, "fix11_g_r16_group_left_guillemet.md")
        _assert_whole(self, _twin(data), "fix11_g_r16_group_left_guillemet_twin.md")

    def test_ch305_02_r17_group_tilde_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r17_group_tilde; attack11-13-scratch/cases/r24_prose_group_tilde
        data = _case(_FULL, 'The note stands (as the appendix records)~')
        _assert_charged(self, data, 282, "b70a9ba26d51")
        _assert_whole(self, data, "fix11_g_r17_group_tilde.md")
        _assert_whole(self, _twin(data), "fix11_g_r17_group_tilde_twin.md")

    def test_ch305_03_r18_group_fullwidth_brace_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r18_group_fullwidth_brace; attack11-13-scratch/cases-own/s11_prose_group_fullwidth_brace
        data = _case(_FULL, 'The note stands (as the appendix records)｝')
        _assert_charged(self, data, 284, "6a02bab13982")
        _assert_whole(self, data, "fix11_g_r18_group_fullwidth_brace.md")
        _assert_whole(self, _twin(data), "fix11_g_r18_group_fullwidth_brace_twin.md")

    def test_ch305_04_r19_group_angle_bracket_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r19_group_angle_bracket; attack11-13-scratch/cases/r25_prose_group_angle_bracket
        data = _case(_FULL, 'The note stands (as the appendix records)⟩')
        _assert_charged(self, data, 284, "2ff81aeef2c5")
        _assert_whole(self, data, "fix11_g_r19_group_angle_bracket.md")
        _assert_whole(self, _twin(data), "fix11_g_r19_group_angle_bracket_twin.md")

    def test_ch305_05_r20_group_run_left_guillemet_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r20_group_run_left_guillemet; attack11-13-scratch/cases/r27_prose_group_run_left_guillemet
        data = _case(_FULL, 'The note stands (as the appendix records)\u200b«')
        _assert_charged(self, data, 286, "7d6e33ecb8fc")
        _assert_whole(self, data, "fix11_g_r20_group_run_left_guillemet.md")
        _assert_whole(self, _twin(data), "fix11_g_r20_group_run_left_guillemet_twin.md")

    def test_ch305_06_r21_group_white_corner_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r21_group_white_corner; attack11-13-scratch/cases/r22_prose_group_white_corner
        data = _case(_FULL, 'The note stands (as the appendix records)』')
        _assert_charged(self, data, 284, "96d54b95968a")
        _assert_whole(self, data, "fix11_g_r21_group_white_corner.md")
        _assert_whole(self, _twin(data), "fix11_g_r21_group_white_corner_twin.md")

    def test_ch305_07_s03_group_black_lenticular_stands_whole(self):
        # Sources: attack11-2-scratch/fresh2/s03_group_black_lenticular; attack11-13-scratch/cases/r23_prose_group_black_lenticular
        data = _case(_FULL, 'The note stands (as the appendix records)】')
        _assert_charged(self, data, 284, "00755c345bc5")
        _assert_whole(self, data, "fix11_g_s03_group_black_lenticular.md")
        _assert_whole(self, _twin(data), "fix11_g_s03_group_black_lenticular_twin.md")

    def test_ch305_08_r21_prose_group_single_left_guillemet_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r21_prose_group_single_left_guillemet
        data = _case(_FULL, 'The note stands (as the appendix records)‹')
        _assert_charged(self, data, 284, "7e27a26dfdb0")
        _assert_whole(self, data, "fix11_g_r21_prose_group_single_left_guillemet.md")
        _assert_whole(self, _twin(data), "fix11_g_r21_prose_group_single_left_guillemet_twin.md")

    def test_ch305_09_r26_prose_group_fullwidth_bracket_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r26_prose_group_fullwidth_bracket
        data = _case(_FULL, 'The note stands (as the appendix records)］')
        _assert_charged(self, data, 284, "970fe1794348")
        _assert_whole(self, data, "fix11_g_r26_prose_group_fullwidth_bracket.md")
        _assert_whole(self, _twin(data), "fix11_g_r26_prose_group_fullwidth_bracket_twin.md")

    def test_ch305_10_s10_prose_group_double_angle_close_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s10_prose_group_double_angle_close
        data = _case(_FULL, 'The note stands (as the appendix records)》')
        _assert_charged(self, data, 284, "dc0295a117c7")
        _assert_whole(self, data, "fix11_g_s10_prose_group_double_angle_close.md")
        _assert_whole(self, _twin(data), "fix11_g_s10_prose_group_double_angle_close_twin.md")

# ---------------------------------------------------------------------
# CH306
# ---------------------------------------------------------------------

class Step17Fix11GGroupStripLabelledTest(unittest.TestCase):
    """CH-306: a sentence valued labelled value closing on a balanced bracket group standing behind a charged character stands whole in the labelled branch, the p17 bound standing unmoved."""

    def test_ch306_01_r22_cost_group_asterisk_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r22_cost_group_asterisk; attack11-13-scratch/cases/r28_cost_group_asterisk
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)*')
        _assert_charged(self, data, 307, "d74275505e18")
        _assert_whole(self, data, "fix11_g_r22_cost_group_asterisk.md")
        _assert_whole(self, _twin(data), "fix11_g_r22_cost_group_asterisk_twin.md")

    def test_ch306_02_r23_cost_group_backtick_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r23_cost_group_backtick; attack11-13-scratch/cases/r29_cost_group_backtick
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)`')
        _assert_charged(self, data, 307, "984da431be27")
        _assert_whole(self, data, "fix11_g_r23_cost_group_backtick.md")
        _assert_whole(self, _twin(data), "fix11_g_r23_cost_group_backtick_twin.md")

    def test_ch306_03_r24_cost_group_left_double_quote_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r24_cost_group_left_double_quote; attack11-13-scratch/cases/r30_cost_group_left_double_quote
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)“')
        _assert_charged(self, data, 309, "00cda52a84c9")
        _assert_whole(self, data, "fix11_g_r24_cost_group_left_double_quote.md")
        _assert_whole(self, _twin(data), "fix11_g_r24_cost_group_left_double_quote_twin.md")

    def test_ch306_04_r25_cost_group_run_asterisk_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r25_cost_group_run_asterisk; attack11-13-scratch/cases/r32_cost_group_run_asterisk
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)\u200b*')
        _assert_charged(self, data, 310, "8febf28d7233")
        _assert_whole(self, data, "fix11_g_r25_cost_group_run_asterisk.md")
        _assert_whole(self, _twin(data), "fix11_g_r25_cost_group_run_asterisk_twin.md")

    def test_ch306_05_r26_cost_group_fullwidth_paren_stands_whole(self):
        # Sources: attack11-2-scratch/cases/r26_cost_group_fullwidth_paren
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)）')
        _assert_charged(self, data, 309, "4fc7dcf8aab4")
        _assert_whole(self, data, "fix11_g_r26_cost_group_fullwidth_paren.md")
        _assert_whole(self, _twin(data), "fix11_g_r26_cost_group_fullwidth_paren_twin.md")

    def test_ch306_06_s04_cost_group_underscore_stands_whole(self):
        # Sources: attack11-2-scratch/fresh2/s04_cost_group_underscore
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)_')
        _assert_charged(self, data, 307, "32966bab2cce")
        _assert_whole(self, data, "fix11_g_s04_cost_group_underscore.md")
        _assert_whole(self, _twin(data), "fix11_g_s04_cost_group_underscore_twin.md")

    def test_ch306_07_r31_cost_group_corner_bracket_stands_whole(self):
        # Sources: attack11-13-scratch/cases/r31_cost_group_corner_bracket
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)」')
        _assert_charged(self, data, 309, "93dc2fc4a752")
        _assert_whole(self, data, "fix11_g_r31_cost_group_corner_bracket.md")
        _assert_whole(self, _twin(data), "fix11_g_r31_cost_group_corner_bracket_twin.md")

    def test_ch306_08_s12_cost_group_tilde_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s12_cost_group_tilde
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)~')
        _assert_charged(self, data, 307, "384999b264dc")
        _assert_whole(self, data, "fix11_g_s12_cost_group_tilde.md")
        _assert_whole(self, _twin(data), "fix11_g_s12_cost_group_tilde_twin.md")

    def test_ch306_09_s13_cost_group_white_corner_stands_whole(self):
        # Sources: attack11-13-scratch/cases-own/s13_cost_group_white_corner
        data = _case(_FULL, 'Cost of deciding late: Work stays blocked (until the ruling lands)』')
        _assert_charged(self, data, 309, "9af7c3ded998")
        _assert_whole(self, data, "fix11_g_s13_cost_group_white_corner.md")
        _assert_whole(self, _twin(data), "fix11_g_s13_cost_group_white_corner_twin.md")

# ---------------------------------------------------------------------
# Pins and cut sides: the cured CH-257 to CH-263 forms standing
# ---------------------------------------------------------------------

class Step17Fix11GPinsAndCutSidesTest(unittest.TestCase):
    """The cured forms of CH-257 to CH-263 stand as
    pins, the p17 bound form stands unmoved at its
    bound, and the cut sides stand: no widened
    character, mark, marker, or group strip rescues
    a line or item that closes nothing complete."""

    def test_pin_ch257_prose_left_guillemet_stands_whole(self):
        data = _case(_FULL, _PROSE + _LEFT_GUILLEMET)
        _assert_whole(self, data, "fix11_g_pin_ch257.md")
        _assert_whole(self, _twin(data),
                      "fix11_g_pin_ch257_twin.md")

    def test_pin_ch263_single_char_dot_stands_whole(self):
        # Seat 13 pin r34, byte for byte.
        data = _case(
            _FULL,
            "\u2163. Option B leaves the note adopted")
        _assert_charged(self, data, 277, "9bd2e3b1ef17")
        _assert_whole(self, data, "fix11_g_pin_ch263.md")
        _assert_whole(self, _twin(data),
                      "fix11_g_pin_ch263_twin.md")

    def test_pin_ch263_single_char_closeparen_stands_whole(self):
        # Seat 13 own pin s09, byte for byte.
        data = _case(
            _FULL,
            "\u2163) Option B leaves the note adopted")
        _assert_charged(self, data, 277, "b54ddcf486c1")
        _assert_whole(self, data, "fix11_g_pin_ch263cp.md")
        _assert_whole(self, _twin(data),
                      "fix11_g_pin_ch263cp_twin.md")

    def test_pin_ch261_group_single_guillemet_stands_whole(self):
        # Seat 2 control r31 and seat 13 pin r35, byte
        # for byte (the one construction).
        data = _case(_FULL, _GROUP_LINE + _SINGLE_GUILLEMET)
        _assert_charged(self, data, 284, "ac4f1b052cd2")
        _assert_whole(self, data, "fix11_g_pin_ch261.md")
        _assert_whole(self, _twin(data),
                      "fix11_g_pin_ch261_twin.md")

    def test_pin_ch262_cost_group_guillemet_stands_whole(self):
        # Seat 13 pin r33, byte for byte.
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _GUILLEMET)
        _assert_charged(self, data, 308, "b667dd393c74")
        _assert_whole(self, data, "fix11_g_pin_ch262.md")
        _assert_whole(self, _twin(data),
                      "fix11_g_pin_ch262_twin.md")

    def test_pin_group_standing_last_stands_whole(self):
        data = _case(_FULL, _GROUP_LINE)
        _assert_whole(self, data, "fix11_g_pin_group_last.md")

    def test_pin_p17_bound_form_stands_cut(self):
        # The p17 form itself: a labelled group behind
        # an interleaved run and a closing double
        # quote, standing at its section 81 ruling (f)
        # bound in both eras, beside its parsed twin.
        data = _case(
            _FULL,
            "Cost of deciding late: Work stays blocked "
            "(until the ruling lands)" + _ZWSP + "\"")
        _assert_cut(self, data, "fix11_g_pin_p17.md")
        _assert_whole(self, _twin(data),
                      "fix11_g_pin_p17_twin.md")

    def test_cut_prose_tortoise_noclose_stands_cut(self):
        # Seat 2 cut side r32, byte for byte: a line
        # closing on a charged closing character that
        # closes no sentence stands cut.
        data = _case(
            _FULL,
            "\u3014Work stays blocked until the ruling "
            "lands\u3015")
        _assert_charged(self, data, 287, "5ccab9657576")
        _assert_cut(self, data, "fix11_g_cut_r32.md")

    def test_cut_prose_double_angle_noclose_stands_cut(self):
        # Seat 13 control r36, byte for byte.
        data = _case(
            _FULL,
            "\u300aWork stays blocked until the ruling "
            "lands\u300b")
        _assert_charged(self, data, 287, "b0078ad856fb")
        _assert_cut(self, data, "fix11_g_cut_r36.md")

    def test_cut_prose_white_tortoise_noclose_stands_cut(self):
        # Seat 13 own control s14, byte for byte.
        data = _case(
            _FULL,
            "\u3018Work stays blocked until the ruling "
            "lands\u3019")
        _assert_charged(self, data, 287, "180f8e02bfa8")
        _assert_cut(self, data, "fix11_g_cut_s14.md")

    def test_cut_bullet_extended_joining_stands_cut(self):
        # Seat 2 cut side r33, byte for byte: an item
        # under a charged marker ending on a joining
        # word stands cut under the standing guards.
        data = _case(
            _FULL,
            "\u216c. Option B leaves the note and")
        _assert_charged(self, data, 273, "421f9a66ffa6")
        _assert_cut(self, data, "fix11_g_cut_r33.md")

    def test_cut_bullet_paren_fragment_stands_cut(self):
        # Seat 13 control r37, byte for byte: an item
        # under a charged marker whose content stands
        # cut mid word stands cut.
        data = _case(
            _FULL,
            "(\u2163) Option B leaves the note adop")
        _assert_charged(self, data, 275, "16ee3b809284")
        _assert_cut(self, data, "fix11_g_cut_r37.md")

    def test_cut_empty_group_asterisk_stands_cut(self):
        # Seat 2 cut side r34, byte for byte: an empty
        # group behind a charged character takes no
        # group reading.
        data = _case(_FULL, "The note stands ()*")
        _assert_charged(self, data, 259, "fbafcc08022b")
        _assert_cut(self, data, "fix11_g_cut_r34.md")


if __name__ == "__main__":
    unittest.main()
