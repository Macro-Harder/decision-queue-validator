"""Step 17 (restart) fix wave 8, Fix Seat K11 tests.

Charges CH-185 and CH-186 (parse, the near marker and
label reading), as ruled TO FIX at section 77 of
design/steps/step-17r-record.md and prepared at
design/steps/step-17r-r8-triage-prep.md (findings T8-32
and T8-35), against round 8 attack seat 17 findings
S17-ATK8-17-01 and S17-ATK8-17-02 (Low each), paper at
design/steps/step-17r-attack8-17.md. Both charges stand
at the CH-128 locus, the reading where the letter
readings, the CH-79 cleaning, the CH-111 limb, and the
CH-128 limb meet.

CH-185 (the run ground substitution limb): a Status
label carrying one run ground character in place of one
label letter, at an interior position of the word (the
second letter position through the last), reaches
Ambiguous at exit 4 with no finding at all. The run
ground is the ground of record section 52 ruling (a),
read at _in_leading_run: the mark categories Mn, Mc,
and Me, the format, control, unassigned, and private
use categories Cf, Cc, Cn, and Co, and the space
separator category Zs, together with the line and
paragraph separator categories and the name limb. The
CH-128 helper reads one character inside the word only
where its category opens with P, S, or N, or where it
is a letter of a script other than the ASCII letters;
the CH-111 helper reads its own charged set alone; and
the CH-79 cleaning rescues the same characters only
where the whole letters of the word still stand, so in
place of one letter the cleaned label is the five
letters that remain and the cleaning is silent. Cure
bound: one character of that ground, substituted for
one letter of the Status word at the second letter
position through the last, at the line start reading
and at the embedded token scan alike. The first letter
position stands apart, as the attack paper bounds it:
a combining acute standing there takes the Warning
already, through the leading run reading and the one
edit reading, and stands pinned below in that standing.

CH-186 (the combined damage joint limb): a Status
label carrying one interior damage of a cured class
together with a letter case damage takes no signal,
where each damage alone takes the near marker Warning.
The case reading and the one edit reading read a run of
ASCII letters only, so the interior character breaks
their match before case is ever compared; and the
interior damage helpers compare the label letter by
letter against the capitalised word and take their
charge only where exactly one position differs, so a
label whose remaining letters stand in another case
differs at five positions and stands outside both
helpers. No cure text states a bound on the case joint.
Cure bound: a label of six characters whose letters,
read without case, stand one position from the Status
word, that one position carrying a character of the
CH-128 interior classes (a punctuation, symbol, or
number character, or a letter of a script other than
the ASCII letters, the CH-111 charged set standing
inside those classes), and whose remaining letters
stand in a letter case other than the capitalised
form, at the line start reading and at the embedded
token scan alike.

Joined bound forms, stated expressly under ruling (i)
of section 77, item R-21: the CH-128 bound forms of
round 8 attack seat 19 observation O-4, at the entry
surface, each at exit 4, the distinction visible only
in the presence or absence of the Warning. Two charged
characters standing beside the whole letters inside
the word, one hyphen after the complete word, and one
underscore after the complete word stand BOUNDED
SILENT in this file: each takes no Warning under this
wave, exactly as the CH-128 helper text states its
bound and as the CH-111 bound guards stand pinned. One
ASCII letter substituted inside the word and one
letter after the complete word stand SIGNALLED in this
file, through the letter readings, as seat 19 measured
them. The round 8 seat 17 bound guards of observation
O-1 stand in the same bounded silent form: two
punctuation characters in place of two label letters,
two combining marks in place of two label letters, and
two punctuation characters beside the whole letters.

Constructions are the attack papers own forms, cases
k01 to k11, k18, k32 to k34, and k36 of round 8 seat 17
and the bound forms of round 8 seat 19, on the round
papers two entry base, copied from
product/attack8-17-scratch/cases.

Copyright: J.P. Picard aka Macro-Harder
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

_BASE_TAIL = (
    "This question is waiting for a decision.\n\n"
    "Question: Which option should we take?\n\n"
    "Options: Option A, Option B\n\n"
    "Cost of deciding late: Work stays blocked.\n\n"
    "Blocks: DQ-002\n\n"
    "### DQ-002: A second open question\n\n"
    "Status: Banked\n\n"
    "Second entry is waiting for a decision.\n\n"
    "Question: Which path should we take?\n\n"
    "Options: Option C, Option D\n\n"
    "Cost of deciding late: More work stays blocked.\n\n"
    "Blocks: DQ-001\n")


def _body(status_line):
    body = "# Decision queue\n\n"
    body += "### DQ-001: A sample open question\n\n"
    body += status_line + "\n\n"
    body += _BASE_TAIL
    return body


def _embedded_body(marker_line):
    body = "# Decision queue\n\n"
    body += "### DQ-001: A sample open question\n\n"
    body += "Some closing text. " + marker_line + "\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "### DQ-002: A second open question\n\n"
    body += "Status: Banked\n\n"
    body += "Second entry is waiting for a decision.\n\n"
    body += "Question: Which path should we take?\n\n"
    body += "Options: Option C, Option D\n\n"
    body += "Cost of deciding late: More work stays blocked.\n\n"
    body += "Blocks: DQ-001\n"
    return body


def _run(status_line, name):
    return h.run_pipeline(
        _body(status_line).encode("utf-8"), name)


def _run_embedded(marker_line, name):
    return h.run_pipeline(
        _embedded_body(marker_line).encode("utf-8"), name)


def _run_cli(status_line, name, subcommand):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / name
        target.write_bytes(_body(status_line).encode("utf-8"))
        code, out, err = h.run_cli(subcommand, target)
    return code, (out + err).decode("utf-8", errors="replace")


def _rule2(output):
    return h.findings_for(output, entry_id="DQ-001", rule=2)


def _entry(output):
    return h.entry_by_id(output, "DQ-001")


def _occurrence_total(output):
    recon = h.reconciliation_of(output)
    return h.int_of(h.get(recon, "status_occurrence_total",
                          "occurrence_total"))


def _assert_near_marker(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)),
                          "Ambiguous")
    test_case.assertEqual(h.entry_sub_label(_entry(output)),
                          "No element")
    test_case.assertEqual(len(_rule2(output)), 1)
    test_case.assertEqual(_occurrence_total(output), 1)


def _assert_warns(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)),
                          "Ambiguous")
    test_case.assertEqual(h.entry_sub_label(_entry(output)),
                          "No element")
    test_case.assertEqual(len(_rule2(output)), 1)


def _assert_embedded_near_marker(test_case, marker_line, name):
    _model, output = _run_embedded(marker_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)),
                          "Ambiguous")
    test_case.assertEqual(h.entry_sub_label(_entry(output)),
                          "No element")
    test_case.assertEqual(len(_rule2(output)), 1)
    test_case.assertEqual(_occurrence_total(output), 1)


def _assert_silent_ambiguous(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)),
                          "Ambiguous")
    test_case.assertEqual(h.entry_sub_label(_entry(output)),
                          "No element")
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(
        [finding for finding in h.findings_for(output)
         if h.finding_severity(finding) != "Note"], [])
    test_case.assertEqual(_occurrence_total(output), 1)


class Ch185RunGroundMarkSubstitutionTest(unittest.TestCase):
    """S17-ATK8-17-01, the mark members: one character of
    the mark categories Mn, Mc, or Me standing in place
    of the second letter of the Status word takes the
    near marker Warning at exit 4."""

    def test_mark_characters_substituted_warn(self):
        # Attack cases k01, k02, k03, and k09: a combining
        # acute accent (Mn), a spacing mark (Mc), a
        # combining enclosing circle (Me), and a variation
        # selector (Mn), each in place of the label a.
        for status_line, name in (
                ("St\u0301tus: Banked", "k01_combining.md"),
                ("St\u093etus: Banked", "k02_mc_mark.md"),
                ("St\u20ddtus: Banked", "k03_me_mark.md"),
                ("St\ufe0ftus: Banked", "k09_variation.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)


class Ch185RunGroundOtherClassesTest(unittest.TestCase):
    """S17-ATK8-17-01, the remaining ground members: one
    character of the format, space separator, control,
    private use, or unassigned categories standing in
    place of one label letter takes the Warning."""

    def test_format_space_and_control_substituted_warn(self):
        # Attack cases k04, k07, and k08: a zero width
        # space (Cf), a plain space (Zs), and a bell
        # control character (Cc), each in place of the
        # label a.
        for status_line, name in (
                ("St\u200btus: Banked", "k04_zwsp.md"),
                ("St tus: Banked", "k07_space.md"),
                ("St\u0007tus: Banked", "k08_bell.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_private_use_and_unassigned_substituted_warn(self):
        # Attack cases k05 and k06: a private use
        # character (Co) and an unassigned character (Cn),
        # each in place of the label a.
        for status_line, name in (
                ("St\ue000tus: Banked", "k05_private_use.md"),
                ("St\u0378tus: Banked", "k06_unassigned.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_final_letter_substitution_warns(self):
        # Attack case k34: a zero width space standing in
        # place of the final letter of the word, the last
        # position of the charged interior bound.
        _assert_near_marker(self, "Statu\u200b: Banked",
                            "k34_zwsp_final.md")

    def test_embedded_only_run_ground_substitutions_warn(self):
        # Attack cases k10 and k11: the entry carries no
        # head Status line and its only marker, carrying
        # the k01 or the k04 label, stands in the closing
        # prose of its first paragraph.
        _assert_embedded_near_marker(
            self, "St\u0301tus: Banked", "k10_embed_comb.md")
        _assert_embedded_near_marker(
            self, "St\u200btus: Banked", "k11_embed_zwsp.md")

    def test_charged_forms_cli_exit_four_with_the_warning(self):
        # The CLI standing of one mark form and one format
        # form, on both subcommands: exit 4, the entry
        # Ambiguous, and the near marker statement standing
        # on the validate surface.
        for status_line, name in (
                ("St\u0301tus: Banked", "k01_combining.md"),
                ("St\u200btus: Banked", "k04_zwsp.md")):
            for subcommand in ("validate", "render"):
                with self.subTest(status_line=status_line,
                                  subcommand=subcommand):
                    code, combined = _run_cli(
                        status_line, name, subcommand)
                    self.assertEqual(code, 4)
                    self.assertIn("Ambiguous", combined)
                    if subcommand == "validate":
                        self.assertIn("carries no element",
                                      combined)


class Ch186CombinedDamageJointTest(unittest.TestCase):
    """S17-ATK8-17-02: one interior damage of a cured
    class standing together with a letter case damage on
    one label takes the near marker Warning at exit 4,
    where each damage alone takes it and the joint took
    nothing."""

    def test_lowercase_dot_inside_warns(self):
        # Attack case k18: the label in lower case with a
        # full stop inside it.
        _assert_near_marker(self, "st.tus: Banked",
                            "k18_lower_dot.md")

    def test_uppercase_dot_inside_warns(self):
        # Attack case k32: the label in upper case with a
        # full stop inside it.
        _assert_near_marker(self, "ST.TUS: Banked",
                            "k32_upper_dot.md")

    def test_lowercase_cyrillic_inside_warns(self):
        # Attack case k33: the label in lower case with
        # one Cyrillic small letter a inside it.
        _assert_near_marker(self, "st\u0430tus: Banked",
                            "k33_lower_cyrillic.md")

    def test_embedded_only_lowercase_dot_warns(self):
        # Attack case k36: the k18 label standing as the
        # entry only marker in closing prose.
        _assert_embedded_near_marker(
            self, "st.tus: Banked", "k36_embed_lower_dot.md")

    def test_joint_form_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "st.tus: Banked", "k18_lower_dot.md",
                    subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class NeighbourReachPinsTest(unittest.TestCase):
    """Pins in the warning direction, standing before and
    after: the CH-128 charged forms, the cure reach forms
    of round 8 seat 17 observation O-2, the case form, and
    the plain control."""

    def test_ch128_charged_forms_still_warn(self):
        for status_line, name in (
                ("Stat.us: Banked", "pin_dot_inside.md"),
                ("St\u0430tus: Banked", "pin_cyrillic_in.md"),
                ("Status!: Banked", "pin_exclaim_suffix.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_reach_forms_still_warn(self):
        # Round 8 seat 17 observation O-2, passing before
        # and after: a combining acute beside the whole
        # letters (k12) and after the complete word (k13),
        # through the CH-79 cleaning; an Arabic Indic
        # digit in place of the label a (k14), through
        # CH-128; one letter after the complete word
        # (k16), through the one edit reading; and a
        # combining acute in place of the first label
        # letter (k35), through the leading run reading,
        # the position the CH-185 bound stands apart from.
        for status_line, name in (
                ("Sta\u0301tus: Banked", "k12_insertion.md"),
                ("Status\u0301: Banked", "k13_suffix.md"),
                ("St\u0661tus: Banked", "k14_arabic_digit.md"),
                ("Statusa: Banked", "k16_letter_suffix.md"),
                ("\u0301tatus: Banked", "k35_first_sub.md")):
            with self.subTest(status_line=status_line):
                _assert_warns(self, status_line, name)

    def test_case_only_form_still_warns(self):
        # The case member of the CH-186 joint standing
        # alone: the label in lower case with no interior
        # damage takes the Warning through the case form
        # of the near marker reading, before and after.
        _assert_warns(self, "status: Banked",
                      "pin_case_only.md")

    def test_plain_status_control_stands_credited(self):
        _model, output = _run("Status: Banked",
                              "k11_plain_control.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Open")
        self.assertEqual(_rule2(output), [])
        self.assertEqual(_occurrence_total(output), 2)


class JoinedBoundFormsTest(unittest.TestCase):
    """The joined bound forms of ruling (i) of section
    77, item R-21, stated expressly: the CH-128 bound
    forms of round 8 seat 19 observation O-4 at the entry
    surface, each at exit 4, and the round 8 seat 17
    observation O-1 bound guards. The silent members
    stand bounded silent under this wave; the letter
    members stand signalled through the letter readings.
    No member of this class is a charged form of CH-185
    or CH-186, and no cure of this wave moves any of
    them."""

    def test_two_charged_characters_beside_letters_stay_silent(self):
        # Seat 19 bound form: two star characters standing
        # beside the whole letters inside the word.
        _assert_silent_ambiguous(self, "St**tus: Banked",
                                 "r21_two_star_beside.md")

    def test_hyphen_after_complete_word_stays_silent(self):
        # Seat 19 bound form, and the CH-111 bound guard:
        # one hyphen standing after the complete word.
        _assert_silent_ambiguous(self, "Status-: Banked",
                                 "r21_hyphen_after.md")

    def test_underscore_after_complete_word_stays_silent(self):
        # Seat 19 bound form, and the CH-111 bound guard:
        # one underscore standing after the complete word.
        _assert_silent_ambiguous(self, "Status_: Banked",
                                 "r21_underscore_after.md")

    def test_ascii_letter_substituted_inside_warns(self):
        # Seat 19 bound form on the signalled side: one
        # ASCII letter substituted inside the word takes
        # the Warning through the one edit reading.
        _assert_warns(self, "Stxtus: Banked",
                      "r21_ascii_sub.md")

    def test_letter_after_complete_word_warns(self):
        # Seat 19 bound form on the signalled side: one
        # letter standing after the complete word takes
        # the Warning through the one edit reading.
        _assert_warns(self, "Statusx: Banked",
                      "r21_letter_after.md")

    def test_two_punctuation_substitutions_stay_silent(self):
        # Round 8 seat 17 case k15, observation O-1: two
        # punctuation characters standing in place of two
        # label letters.
        _assert_silent_ambiguous(self, "St.tu!: Banked",
                                 "k15_two_punct_sub.md")

    def test_two_combining_substitutions_stay_silent(self):
        # Round 8 seat 17 case k17, observation O-1: two
        # combining marks standing in place of two label
        # letters. Two run ground characters in one label
        # stand outside the CH-185 charge, which takes
        # one, exactly as the CH-128 bound states its own.
        _assert_silent_ambiguous(
            self, "St\u0301t\u0301s: Banked",
            "k17_two_combining_sub.md")

    def test_two_punctuation_beside_letters_stay_silent(self):
        # Round 8 seat 17 case k19, observation O-1: two
        # punctuation characters standing beside the whole
        # label letters.
        _assert_silent_ambiguous(self, "Sta..tus: Banked",
                                 "k19_two_punct_beside.md")


if __name__ == "__main__":
    unittest.main()
