"""Step 17 (restart) fix wave 9, Fix Seat I tests.

Charges CH-219, CH-220, and CH-221, cluster I (the
label joint damage forms), ruled TO FIX at section 81
of design/steps/step-17r-record.md: ruling (a) (all 35
distinct findings TO FIX in fix wave 9, test first, in
the triage preparation clusters A to K, charges
numbered consecutively from CH-191 in cluster order,
one charge per distinct finding on the split as filed,
so cluster I takes the three charges after clusters A
to H) and ruling (e) (the Cluster I joint damage forms
stand TO FIX in their charge, the joint ruled a
distinct construction family outside the bounds as
pinned, the cure stating its bound expressly).
Findings: T9-32 (seat 17 S17-ATK9-17-01), T9-33 (seat
17 S17-ATK9-17-02), and T9-34 (seat 17 S17-ATK9-17-03),
each Low, consolidated in
design/steps/step-17r-r9-triage-prep.md Cluster I,
against round 9 attack seat 17, paper at
design/steps/step-17r-attack9-17.md. Locus: parse.py,
the near marker scan in scan_line_occurrences at the
Status label, the joint ground between CH-185 and
CH-186, and validate.py, the CH-179 heading signal in
_check2 for CH-221.

CH-219 (the run ground case joint limb): a Status
label carrying one run ground character in place of
one label letter together with a letter case damage
takes no signal, where each damage alone takes the
near marker Warning (CH-185 cures the run ground
substitution where the remaining letters stand in the
capitalised form; CH-186 cures the case joint where
the interior damage is of a CH-128 class; the run
ground class is not one of the CH-186 classes).
Cure bound, stated expressly: a label of six
characters whose letters, read without case, stand
one position from the Status word, that one position
an interior position of the word (the second letter
position through the last) carrying a character of
the run ground of record section 52 ruling (a), read
at _in_leading_run in parse.py, and whose remaining
letters, with that character read as the Status
letter, stand in a letter case other than the
capitalised form, at the line start reading and at
the embedded token scan alike. Two such characters in
one label, a joint form at any other label length,
and a character of the ground at the first letter
position stand outside this cure and take their
standing readings as before.

CH-220 (the interior separator joint limb): a Status
label carrying one interior damage together with a
separator damage takes no signal, where each damage
alone takes the near marker Warning (the readings
that name the separator damage read the label word
whole, and the readings that name the interior damage
read the line through its colon separator). Cure
bound, stated expressly: a line opening with a label
of the CH-128 interior damage form (one punctuation,
symbol, or number character, or one letter of a
script other than the ASCII letters, in place of one
letter of the Status word, the remaining letters in
the capitalised form, as _is_label_interior_damage
states it) or of the CH-185 run ground substitution
form (as _is_run_ground_label_substitution states
it), standing before a semicolon in place of the
colon separator, at the near marker reading. A label
carrying a case damage together with its interior
damage before the semicolon (three damages on one
line) stands outside this cure.

CH-221 (the damaged heading marker limb): a Status
heading carrying one interior damage is counted
nowhere, listed nowhere, and takes no signal at all,
where the clean heading forms take the CH-179 heading
signal (the CH-179 reading as landed takes the marker
word whole, and the line start and near marker
readings do not reach a level 4 heading line). Cure
bound, stated expressly: a level 4 heading line in a
CH-179 dress form whose marker word stands six
characters long, one interior position of the word
(the second letter position through the last)
carrying one character of the CH-128 interior classes
or of the run ground categories, its remaining
letters matching the Status word read without case,
takes the heading signal in the same form as the
clean marker. Two interior damages on the marker
word, a marker word of any other length, a damage at
the first letter position, and an ASCII letter
standing in place of a marker letter stand outside
this cure.

Pins standing in this file: the single damage forms
of each joint (the case forms m25 and m26, the run
ground substitution in the capitalised form, the
interior damage with the colon separator standing,
the semicolon separator with the label letters whole,
and the clean heading forms) warn or signal before
and after; and the bound forms at the joints stay in
their standing silent forms (two run ground
substitutions standing with a case damage, the two
character bound extent form of round 9 observation
O-4, the case joint form standing before the
semicolon separator, and the heading marker carrying
two interior damages or an ASCII letter substitution).

Constructions are the attack paper own forms, cases
m02, m03, m04, m14, m15, m17, m18, and m24 of round 9
seat 17, on the round papers two entry base and, for
the heading forms, the open base with one heading line
appended, rebuilt inline in the shapes the attack
paper states.

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


def _heading_body(heading_line):
    body = "# Decision queue\n\n"
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked\n\n"
    body += _BASE_TAIL
    body += "\n" + heading_line + "\n"
    return body


def _run(status_line, name):
    return h.run_pipeline(
        _body(status_line).encode("utf-8"), name)


def _run_embedded(marker_line, name):
    return h.run_pipeline(
        _embedded_body(marker_line).encode("utf-8"), name)


def _run_heading(heading_line, name):
    return h.run_pipeline(
        _heading_body(heading_line).encode("utf-8"), name)


def _run_cli(data, name, subcommand):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / name
        target.write_bytes(data.encode("utf-8"))
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


def _heading_hits(output):
    # The heading line stands appended at the end of the
    # file, inside the second entry body, as the attack
    # paper own constructions stand (the open base with
    # one heading line appended at its end), so the hits
    # are read across the whole output in the CH-179 test
    # form of fix wave 8 seat K6.
    return [finding for finding in h.findings_of(output)
            if "standing as a heading" in
            (h.finding_statement(finding) or "")]


def _assert_near_marker(test_case, status_line, name):
    _model, output = _run(status_line, name)
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


class Ch219RunGroundCaseJointTest(unittest.TestCase):
    """T9-32, S17-ATK9-17-01: one run ground character
    in place of one label letter standing together with
    a letter case damage takes the near marker Warning
    at exit 4, where each damage alone takes it."""

    def test_lowercase_zwsp_substitution_warns(self):
        # Attack case m02: the label in lower case, a
        # zero width space in place of the letter a.
        _assert_near_marker(self, "st\u200btus: Banked",
                            "m02_lower_zwsp.md")

    def test_uppercase_combining_substitution_warns(self):
        # Attack case m03: the label in upper case, a
        # combining acute accent in place of the letter A.
        _assert_near_marker(self, "ST\u0301TUS: Banked",
                            "m03_upper_combining.md")

    def test_lowercase_space_substitution_warns(self):
        # Attack case m04: the label in lower case, a
        # plain space in place of the letter a.
        _assert_near_marker(self, "st tus: Banked",
                            "m04_lower_space.md")

    def test_embedded_only_lowercase_zwsp_warns(self):
        # Attack case m24: the m02 label standing as the
        # entry only marker in closing prose.
        _model, output = _run_embedded(
            "st\u200btus: Banked", "m24_embed_lower.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(
            h.entry_sub_label(_entry(output)), "No element")
        self.assertEqual(len(_rule2(output)), 1)
        self.assertEqual(_occurrence_total(output), 1)

    def test_joint_form_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("st\u200btus: Banked"),
                    "m02_lower_zwsp.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch220InteriorSeparatorJointTest(unittest.TestCase):
    """T9-33, S17-ATK9-17-02: one interior damage
    standing together with a semicolon separator damage
    takes the near marker Warning at exit 4, where each
    damage alone takes it."""

    def test_dot_inside_semicolon_separator_warns(self):
        # Attack case m17: a full stop inside the label
        # and a semicolon standing as the separator.
        _assert_near_marker(self, "St.tus; Banked",
                            "m17_dot_semicolon.md")

    def test_zwsp_inside_semicolon_separator_warns(self):
        # Attack case m18: a zero width space in place of
        # the letter a and a semicolon as the separator.
        _assert_near_marker(self, "St\u200btus; Banked",
                            "m18_zwsp_semicolon.md")

    def test_joint_form_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("St.tus; Banked"),
                    "m17_dot_semicolon.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch221DamagedHeadingMarkerTest(unittest.TestCase):
    """T9-34, S17-ATK9-17-03: a Status heading carrying
    one interior damage takes the CH-179 heading signal,
    where the clean heading forms take it and the
    damaged forms were counted nowhere in silence."""

    def test_italic_dress_dot_inside_takes_signal(self):
        # Attack case m14: the italic dress with a full
        # stop inside the marker word.
        _model, output = _run_heading(
            "#### *St.tus:* RULED, closed", "m14_head_dot.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_heading_hits(output)), 1)

    def test_plain_heading_zwsp_substitution_takes_signal(self):
        # Attack case m15: the plain heading form with a
        # zero width space in place of the letter a.
        _model, output = _run_heading(
            "#### St\u200btus: RULED, closed",
            "m15_head_zwsp.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_heading_hits(output)), 1)

    def test_damaged_heading_cli_exit_one_with_the_signal(self):
        code, combined = _run_cli(
            _heading_body("#### *St.tus:* RULED, closed"),
            "m14_head_dot.md", "validate")
        self.assertEqual(code, 1)
        self.assertIn("standing as a heading", combined)


class SingleDamagePinsTest(unittest.TestCase):
    """Pins in the signal direction, standing before and
    after: each damage of the three joints standing
    alone takes its standing signal."""

    def test_case_damage_alone_still_warns(self):
        # Attack controls m25 and m26: the label in upper
        # case and in lower case, no other damage.
        for status_line, name in (
                ("STATUS: Banked", "m25_upper_alone.md"),
                ("status: Banked", "m26_lower_alone.md")):
            with self.subTest(status_line=status_line):
                _model, output = _run(status_line, name)
                self.assertIsNotNone(output)
                self.assertEqual(
                    h.entry_state(_entry(output)), "Ambiguous")
                self.assertEqual(len(_rule2(output)), 1)

    def test_run_ground_substitution_alone_still_warns(self):
        # The CH-185 charged form in the capitalised
        # label (round 8 case k04) stands warned.
        _assert_near_marker(self, "St\u200btus: Banked",
                            "pin_k04_zwsp_alone.md")

    def test_interior_damage_alone_still_warns(self):
        # The CH-128 charged form with the colon
        # separator standing (round 8 pin form).
        _assert_near_marker(self, "Stat.us: Banked",
                            "pin_dot_colon.md")

    def test_semicolon_separator_alone_still_warns(self):
        # Attack control m31: a semicolon as separator
        # with the label letters whole.
        _assert_near_marker(self, "Status; Banked",
                            "m31_semicolon_alone.md")

    def test_clean_heading_forms_still_take_signal(self):
        # The CH-179 charged and control forms: the
        # italic dress (s01), the bold dress with its
        # colon outside (m30 control), and the plain
        # heading form (m33 control).
        for heading_line, name in (
                ("#### *Status:* RULED, closed",
                 "pin_s01_italic.md"),
                ("#### **Status**: RULED, closed",
                 "pin_m30_bold_outside.md"),
                ("#### Status: RULED, closed",
                 "pin_m33_plain.md")):
            with self.subTest(heading_line=heading_line):
                _model, output = _run_heading(
                    heading_line, name)
                self.assertIsNotNone(output)
                self.assertEqual(
                    len(_heading_hits(output)), 1)


class JointBoundPinsTest(unittest.TestCase):
    """Bound pins, standing before and after in their
    silent forms: the forms the three cure bounds state
    expressly as standing outside the cures."""

    def test_two_run_ground_with_case_damage_stays_silent(self):
        # Two run ground characters in one label stand
        # outside the CH-219 bound of one, as two stand
        # outside the CH-185 bound (round 9 seat 19
        # observation O-4 member, recorded as standing).
        _assert_silent_ambiguous(
            self, "st\u200bt\u200bs: Banked",
            "bound_two_zwsp_case.md")

    def test_two_character_bound_extent_stays_silent(self):
        # Attack case m16, round 9 observation O-4: a
        # full stop in place of the letter a with a
        # combining acute beside it, two damage
        # characters on one label, at a label length of
        # seven, outside the bounds of CH-219 as stated.
        _assert_silent_ambiguous(
            self, "St.tus\u0301: Banked", "bound_m16.md")

    def test_case_joint_before_semicolon_stays_silent(self):
        # One interior damage with a case damage standing
        # before the semicolon separator is three damages
        # on one line, outside the CH-220 bound of one
        # interior damage with the separator damage.
        _assert_silent_ambiguous(
            self, "st.tus; Banked", "bound_case_semicolon.md")

    def test_heading_two_interior_damages_stay_silent(self):
        # Two interior damages on the heading marker word
        # stand outside the CH-221 bound of one.
        _model, output = _run_heading(
            "#### St.tu!: RULED, closed",
            "bound_head_two_damage.md")
        self.assertIsNotNone(output)
        self.assertEqual(_heading_hits(output), [])

    def test_heading_ascii_letter_substitution_stays_silent(self):
        # An ASCII letter standing in place of a marker
        # letter stands outside the CH-221 bound as
        # stated; the letter readings govern letters.
        _model, output = _run_heading(
            "#### Stxtus: RULED, closed",
            "bound_head_ascii_sub.md")
        self.assertIsNotNone(output)
        self.assertEqual(_heading_hits(output), [])


if __name__ == "__main__":
    unittest.main()
