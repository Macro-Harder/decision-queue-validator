"""Step 17 (restart) fix wave 7, Fix Seat K5 tests.

Charge CH-128 (parse, the near marker and label reading,
the label interior character limb), as ruled at record
section 66 of design/steps/step-17r-record.md, prepared at
design/steps/step-17r-triage7-prep.md, against round 7
attack seat 17 findings S17-ATK7-17-01 and S17-ATK7-17-02
(Low each), paper at design/steps/step-17r-attack7-17.md.
One charge at the reading where the two bounds meet.

S17-ATK7-17-01: a Status label carrying one punctuation
or symbol character inside the label word, or one such
character standing after the complete label word, reaches
Ambiguous at exit 4 with no finding at all. The near
marker net reads its letter forms on ASCII letters only,
the CH-79 label cleaning removes the run ground
characters only, and the CH-111 limb at
_is_charged_label_damage takes one charged character
inside the word (an ASCII digit, an underscore, a hyphen,
or a braille dot pattern character) or one ASCII digit
after the complete word. A full stop, a slash, a plus, an
at sign, a tilde, an equals sign, and an emoji stand in
none of those readings; a superscript two is a digit to
the Unicode reading but not an ASCII digit; and an
exclamation mark, a full stop, and a braille dot pattern
standing after the complete word stand outside the
suffix limb, which takes a digit alone there.

S17-ATK7-17-02: a Status label carrying one non ASCII
letter inside the label word (a Cyrillic small letter a,
a small letter a with acute, a fullwidth capital letter
S, a Greek small letter alpha) reaches Ambiguous at
exit 4 with no finding at all. The letter readings govern
letters, but their match admits ASCII letters alone, so
the two bounds meet and leave the form in silence.

Cure bound. The near marker reading takes these forms at
the same joint: one punctuation, symbol, or number
character, or one non ASCII letter, standing inside the
label word in place of one of its letters or beside its
whole letters, and one punctuation, symbol, or number
character standing after the complete label word. The
CH-111 bound guards stand unmoved: two charged characters
in one label, two digits after the complete word, and a
hyphen or an underscore standing after the complete word
each stay silent, exactly as the fix wave 6 seat K4 pins
record them and as round 7 observation O-1 re-measured
them. The CH-111 charged forms and the cleaned neighbour
forms keep their near marker Warning.

Constructions are the attack paper's own forms, cases
j01 to j07, j09 to j14, j19, j20, j32, and j33 for the
charged forms and j15 to j18 for the bound guards, on the
attack paper's two entry base, copied from
product/attack7-17-scratch/cases.

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
    # Silence on the label, in the fix wave 6 seat K4
    # pin form: no rule 2 finding, and no finding above
    # Note grade, stands on the run.
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(
        [finding for finding in h.findings_for(output)
         if h.finding_severity(finding) != "Note"], [])
    test_case.assertEqual(_occurrence_total(output), 1)


class Ch128PunctuationSymbolInsideTest(unittest.TestCase):
    """S17-ATK7-17-01, the inside limb: one punctuation or
    symbol character inside the label word, in place of
    one of its letters or beside its whole letters, takes
    the near marker Warning at exit 4."""

    def test_punctuation_inside_the_label_warns(self):
        # Attack cases j01, j02, j03, j04, j09, and j10:
        # a full stop, a slash, a plus, an at sign, a
        # tilde, and an equals sign inside the label.
        for status_line, name in (
                ("Stat.us: Banked", "j01_dot_inside.md"),
                ("Stat/us: Banked", "j02_slash_inside.md"),
                ("Stat+us: Banked", "j03_plus_inside.md"),
                ("Stat@us: Banked", "j04_at_inside.md"),
                ("Stat~us: Banked", "j09_tilde_inside.md"),
                ("Stat=us: Banked", "j10_equals_inside.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_emoji_inside_the_label_warns(self):
        # Attack case j07: U+1F642 inside the label.
        _assert_near_marker(self, "Stat\U0001F642us: Banked",
                            "j07_emoji_inside.md")

    def test_superscript_digit_inside_the_label_warns(self):
        # Attack case j32: a superscript two, a digit to
        # the Unicode reading but not an ASCII digit, in
        # place of the final label letter.
        _assert_near_marker(self, "Statu\u00b2: Banked",
                            "j32_superscript_inside.md")

    def test_embedded_only_dot_inside_warns(self):
        # Attack case j19: the entry carries no head
        # Status line and its only marker stands in the
        # closing prose of its first paragraph.
        _assert_embedded_near_marker(
            self, "Stat.us: Banked", "j19_embedded_dot.md")


class Ch128PunctuationSymbolSuffixTest(unittest.TestCase):
    """S17-ATK7-17-01, the suffix limb: one punctuation or
    symbol character standing after the complete label
    word takes the near marker Warning at exit 4."""

    def test_punctuation_and_symbol_suffix_warns(self):
        # Attack cases j05, j06, and j33: an exclamation
        # mark, a full stop, and a braille dot pattern
        # after the complete label word.
        for status_line, name in (
                ("Status!: Banked", "j05_exclaim_suffix.md"),
                ("Status.: Banked", "j06_dot_suffix.md"),
                ("Status\u2801: Banked",
                 "j33_braille_suffix.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_charged_forms_cli_exit_four_with_the_warning(self):
        # The CLI standing of one inside form and one
        # suffix form, on both subcommands: exit 4, the
        # entry Ambiguous, and the near marker statement
        # standing on the validate surface.
        for status_line, name in (
                ("Stat.us: Banked", "j01_dot_inside.md"),
                ("Status!: Banked", "j05_exclaim_suffix.md")):
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


class Ch128NonAsciiLetterInsideTest(unittest.TestCase):
    """S17-ATK7-17-02: one non ASCII letter inside the
    label word, in place of one of its letters, takes the
    near marker Warning at exit 4, at the joint where the
    ASCII letter readings and the CH-111 letter bound
    meet."""

    def test_non_ascii_letter_inside_the_label_warns(self):
        # Attack cases j11, j12, j13, and j14: a Cyrillic
        # small letter a, a small letter a with acute, a
        # fullwidth capital letter S, and a Greek small
        # letter alpha inside the label.
        for status_line, name in (
                ("St\u0430tus: Banked", "j11_cyrillic_a.md"),
                ("St\u00e1tus: Banked", "j12_accented_a.md"),
                ("\uff33tatus: Banked", "j13_fullwidth_s.md"),
                ("St\u03b1tus: Banked", "j14_greek_alpha.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_embedded_only_cyrillic_inside_warns(self):
        # Attack case j20: the j11 label standing as the
        # entry's only marker, in closing prose.
        _assert_embedded_near_marker(
            self, "St\u0430tus: Banked",
            "j20_embedded_cyrillic.md")

    def test_non_ascii_letter_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "St\u0430tus: Banked",
                    "j11_cyrillic_a.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch128NeighbourPinsTest(unittest.TestCase):
    """Pins in the warning direction, standing before and
    after: the CH-111 charged forms, the cleaned neighbour
    forms of CH-79, and the plain control."""

    def test_ch111_charged_forms_still_warn(self):
        for status_line, name in (
                ("Statu5: Banked", "pin_digit_inside.md"),
                ("Stat_us: Banked", "pin_underscore_in.md"),
                ("Stat-us: Banked", "pin_hyphen_inside.md"),
                ("Stat\u2801us: Banked",
                 "pin_braille_inside.md"),
                ("Status1: Banked", "pin_digit_suffix.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_cleaned_neighbour_forms_still_warn(self):
        # The CH-79 cleaned neighbours (a combining acute
        # and a replacement character inside the label)
        # and the space inside the label form of round 7
        # case j08, recorded at observation O-2 of the
        # attack paper as cure reach in the signal
        # direction.
        for status_line, name in (
                ("Stat\u0301us: Banked",
                 "pin_combining_acute.md"),
                ("Stat\ufffdus: Banked",
                 "pin_replacement_char.md"),
                ("Stat us: Banked", "pin_space_inside.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_plain_status_control_stands_credited(self):
        _model, output = _run("Status: Banked",
                              "k5_plain_status_control.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Open")
        self.assertEqual(_rule2(output), [])
        self.assertEqual(_occurrence_total(output), 2)


class Ch111BoundGuardPinsTest(unittest.TestCase):
    """Pins in the silent direction, standing before and
    after, as the fix wave 6 seat K4 paper pins them and
    round 7 observation O-1 re-measured them on fresh twin
    constructions: the cure takes one character inside the
    label word, or one character after the complete word
    on its charged classes, and nothing wider."""

    def test_two_digits_inside_one_label_stay_silent(self):
        # Attack case j15: two digits standing for two
        # label letters.
        _assert_silent_ambiguous(self, "St4tu5: Banked",
                                 "j15_two_digits_inside.md")

    def test_two_digits_after_the_complete_word_stay_silent(self):
        # Attack case j16.
        _assert_silent_ambiguous(self, "Status12: Banked",
                                 "j16_two_digits_suffix.md")

    def test_hyphen_after_the_complete_word_stays_silent(self):
        # Attack case j17.
        _assert_silent_ambiguous(self, "Status-: Banked",
                                 "j17_hyphen_suffix.md")

    def test_underscore_after_the_complete_word_stays_silent(self):
        # Attack case j18.
        _assert_silent_ambiguous(self, "Status_: Banked",
                                 "j18_underscore_suffix.md")


if __name__ == "__main__":
    unittest.main()
