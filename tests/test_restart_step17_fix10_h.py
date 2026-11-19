"""Step 17 (restart) fix wave 10, Fix Seat H tests.

Charges CH-264 to CH-268, cluster H (the joint damage
family of round 10), consolidated in
design/steps/step-17r-r10-triage-prep.md at Cluster H
from round 10 attack seat 17, paper at
design/steps/step-17r-r10-seat17.md, findings
S17-ATK10-17-01 to S17-ATK10-17-05, each Low. Locus:
parse.py, the near marker reading at _is_near_marker
and the embedded token scan in scan_line_occurrences,
at the Status label, one step past the Cluster I
bounds of fix wave 9 (charges CH-219, CH-220, and
CH-221, paper design/steps/step-17r-fix9-i.md), whose
pins stand in product/tests/test_restart_step17_fix9_i.py
and stand unmoved by this wave.

CH-264 (T10-41, S17-ATK10-17-01): a Status label
carrying one run ground character in place of one
label letter together with a letter case damage and
a semicolon separator damage takes no signal, where
every pair of those damages takes the near marker
Warning. Charged members: case n03 (the label in
lower case, a zero width space in place of the
letter a, a semicolon as separator, at line start),
case n12 (the n03 label standing as the entry only
marker in closing prose), and case n14 (the n03
label standing as the Status line of the decided
base, escaping at a clean exit 0 pre cure). Cure
bound, stated expressly: the label before the
semicolon, or the embedded token before the
semicolon, stands in the CH-219 run ground case
joint form as _is_run_ground_case_joint_label_damage
states it (six characters, one run ground character
at an interior position, the remaining letters in a
letter case other than the capitalised form). The
pinned member of the neighbouring triple, a case
damage with a CH-128 interior damage before the
semicolon (case n04), stands outside this cure and
stays silent as pinned.

CH-265 (T10-42, S17-ATK10-17-02): a Status label
carrying one run ground character inserted beside
its whole letters together with a letter case damage
takes no signal, where the insertion alone and the
case damage alone each take the Warning. Charged
member: case n05 (the label in lower case, a zero
width space inserted inside it, at the colon
separator). Cure bound, stated expressly: a label of
seven characters carrying exactly one run ground
character at an interior position of the label (not
before the first letter and not after the last
letter), whose remaining letters are the whole
Status word in a letter case other than the
capitalised form. The capitalised twin (case n31)
takes the Warning through the standing cleaning
reading and stands as a pin.

CH-266 (T10-43, S17-ATK10-17-03): a Status label
carrying a letter case damage together with a
separator damage takes no signal, where each damage
alone takes the Warning. Charged members: case n10
(the label in lower case with a semicolon standing
as the separator) and case n09 (the label in lower
case with a plain space standing before the colon).
Cure bound, stated expressly: the label word whole,
read without case as the Status word and standing
in a letter case other than the capitalised form,
standing before a semicolon separator, or standing
before a space or tab run and a colon.

CH-267 (T10-44, S17-ATK10-17-04): a Status label
carrying one interior damage together with a space
or tab standing before the colon takes no signal on
its two charged members, where each damage alone
takes the Warning. Charged members: case n08 (a zero
width space in place of the letter a, a plain space
before the colon) and case n29 (a full stop inside
the label, a tab before the colon). The signalling
contrast member n07 (a full stop inside the label, a
plain space before the colon) stands as a pin and
expressly outside the charge. Cure bound, stated
expressly: the label before the space or tab run
stands in the CH-128 interior damage form or in the
CH-185 run ground substitution form, each with its
remaining letters in the capitalised form, on the
bounds those helpers state.

CH-268 (T10-45, S17-ATK10-17-05): the CH-220 joint
forms standing as the entry only marker in closing
prose take no signal, where their line start twins
and the embedded colon forms of the same damage
classes take the Warning. Charged members: case n35
(a zero width space in place of the letter a with a
semicolon separator, embedded only) and case n11 (a
full stop inside the label with a semicolon
separator, embedded only). Cure bound, stated
expressly, naming the embedded only position: at the
embedded only position, a token standing before a
semicolon takes the near marker report where its
label stands in the CH-128 interior damage form or
in the CH-185 run ground substitution form (the
CH-220 forms), or in the CH-219 run ground case
joint form (the CH-264 embedded member n12), each on
the bounds those helpers state. The embedded only
semicolon joint form of round 10 seat 19 observation
O-3 (one full stop inside the Status word before a
semicolon separator inside an embedded token in
entry body matter) is the n11 construction on its
own base and rides inside this bound statement: it
takes the same report under this cure, and it
carries no charge of its own. Separator damage alone
at the embedded position (case n34, the clean label
before a semicolon, embedded only) stands outside
this cure and stays silent as a pin.

Pins standing in this file: the bound forms of seat
17 observation O-1 on this surface (case n04, the
case plus interior plus semicolon triple, pinned
silent; case n27, two interior damages before a
semicolon, silent), the CH-267 contrast member n07
signalling, the embedded clean semicolon form n34
silent, the single damage forms of each joint
signalling (case damage alone, semicolon separator
alone, space before the colon alone, run ground
substitution alone, interior damage alone), the
CH-219 and CH-220 charged forms signalling (m02,
m17, m18, and the embedded m24), the capitalised
insertion form n31 signalling, the decided CH-220
form n13 signalling, and the two run ground with
case damage form of the fix wave 9 pins silent.

Constructions are the attack paper own forms, cases
n03 to n35 of round 10 seat 17 as named in each test,
on the round papers two entry base, on the embedded
only form of that base, and, for the decided members,
on the single entry decided base of cases n13 and
n14, rebuilt inline in the shapes the attack paper
states.

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


def _decided_body(status_line):
    body = "# Decision queue\n\n"
    body += "### DQ-001: A decided sample\n\n"
    body += status_line + "\n\n"
    body += "Ruled by: Captain JP, option A stands.\n\n"
    body += "Ruling text: Option A stands.\n\n"
    body += "Ruling outcome: Option A adopted.\n\n"
    body += "Where the ruling landed: DQ-001 record.\n"
    return body


def _run(status_line, name):
    return h.run_pipeline(
        _body(status_line).encode("utf-8"), name)


def _run_embedded(marker_line, name):
    return h.run_pipeline(
        _embedded_body(marker_line).encode("utf-8"), name)


def _run_decided(status_line, name):
    return h.run_pipeline(
        _decided_body(status_line).encode("utf-8"), name)


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
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(
        [finding for finding in h.findings_for(output)
         if h.finding_severity(finding) != "Note"], [])
    test_case.assertEqual(_occurrence_total(output), 1)


class Ch264RunGroundCaseSemicolonTripleTest(unittest.TestCase):
    """T10-41, S17-ATK10-17-01: one run ground character
    in place of one label letter, standing with a letter
    case damage and a semicolon separator damage, takes
    the near marker Warning, where every pair of those
    damages takes it."""

    def test_line_start_form_warns(self):
        # Attack case n03: the label in lower case, a
        # zero width space in place of the letter a, a
        # semicolon standing as the separator.
        _assert_near_marker(self, "st\u200btus; Banked",
                            "n03_rg_case_semicolon.md")

    def test_embedded_only_form_warns(self):
        # Attack case n12: the n03 label standing as the
        # entry only marker in closing prose.
        _assert_embedded_near_marker(
            self, "st\u200btus; Banked",
            "n12_embedded_rg_case_semicolon.md")

    def test_decided_base_form_warns(self):
        # Attack case n14: the n03 label standing as the
        # Status line of the decided base, at a clean
        # exit 0 with no findings pre cure.
        _model, output = _run_decided(
            "st\u200btus; RULED, closed",
            "n14_decided_rg_case_semicolon.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule2(output)), 1)


class Ch265RunGroundInsertionCaseTest(unittest.TestCase):
    """T10-42, S17-ATK10-17-02: one run ground character
    inserted beside the whole label letters, standing
    with a letter case damage, takes the near marker
    Warning, where the insertion alone and the case
    damage alone each take it."""

    def test_insertion_with_case_damage_warns(self):
        # Attack case n05: the label in lower case, a
        # zero width space inserted inside it, standing
        # before the colon separator.
        _assert_near_marker(self, "st\u200batus: Banked",
                            "n05_rg_beside_case.md")

    def test_insertion_form_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("st\u200batus: Banked"),
                    "n05_rg_beside_case.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch266CaseSeparatorJointTest(unittest.TestCase):
    """T10-43, S17-ATK10-17-03: a letter case damage
    standing together with a separator damage takes the
    near marker Warning, where each damage alone takes
    it."""

    def test_case_damage_semicolon_separator_warns(self):
        # Attack case n10: the label in lower case with
        # a semicolon standing as the separator.
        _assert_near_marker(self, "status; Banked",
                            "n10_case_semicolon.md")

    def test_case_damage_space_before_colon_warns(self):
        # Attack case n09: the label in lower case with
        # a plain space standing before the colon.
        _assert_near_marker(self, "status : Banked",
                            "n09_case_space_colon.md")

    def test_case_semicolon_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("status; Banked"),
                    "n10_case_semicolon.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch267InteriorSpaceTabJointTest(unittest.TestCase):
    """T10-44, S17-ATK10-17-04: one interior damage
    standing together with a space or tab before the
    colon takes the near marker Warning on its two
    charged members, where each damage alone takes it."""

    def test_run_ground_space_before_colon_warns(self):
        # Attack case n08: a zero width space in place
        # of the letter a, a plain space before the
        # colon.
        _assert_near_marker(self, "St\u200btus : Banked",
                            "n08_zwsp_space_colon.md")

    def test_interior_tab_before_colon_warns(self):
        # Attack case n29: a full stop inside the label,
        # a tab standing before the colon.
        _assert_near_marker(self, "St.tus\t: Banked",
                            "n29_dot_tab_colon.md")

    def test_space_joint_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("St\u200btus : Banked"),
                    "n08_zwsp_space_colon.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch268EmbeddedSemicolonJointTest(unittest.TestCase):
    """T10-45, S17-ATK10-17-05: the CH-220 joint forms
    standing as the entry only marker in closing prose
    take the near marker Warning, where their line start
    twins and the embedded colon forms of the same
    damage classes take it."""

    def test_embedded_run_ground_semicolon_warns(self):
        # Attack case n35: a zero width space in place
        # of the letter a with a semicolon separator,
        # standing as the entry only marker.
        _assert_embedded_near_marker(
            self, "St\u200btus; Banked",
            "n35_embedded_zwsp_semicolon.md")

    def test_embedded_interior_semicolon_warns(self):
        # Attack case n11: a full stop inside the label
        # with a semicolon separator, standing as the
        # entry only marker. Round 10 seat 19
        # observation O-3 records this same construction
        # on its own base, riding inside the bound
        # statement of this charge.
        _assert_embedded_near_marker(
            self, "St.tus; Banked",
            "n11_embedded_dot_semicolon.md")

    def test_embedded_joint_cli_exit_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _embedded_body("St.tus; Banked"),
                    "n11_embedded_dot_semicolon.md",
                    subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class JointBoundAndSignalPinsTest(unittest.TestCase):
    """Pins in both directions, standing before and
    after: the bound forms of the Cluster I and Cluster
    H joints stay in their silent forms, and the single
    damage and cured neighbour forms keep their
    signals."""

    def test_pin_case_interior_semicolon_triple_stays_silent(self):
        # Attack case n04, seat 17 observation O-1: a
        # case damage with a CH-128 interior damage
        # before the semicolon, three damages on one
        # line, pinned silent in the fix wave 9 module.
        _assert_silent_ambiguous(
            self, "st.tus; Banked", "pin_n04_triple.md")

    def test_pin_two_interior_semicolon_stays_silent(self):
        # Attack case n27, seat 17 observation O-1: two
        # interior damages before the semicolon, outside
        # the bound of one.
        _assert_silent_ambiguous(
            self, "St.t!s; Banked", "pin_n27_two_interior.md")

    def test_pin_embedded_clean_semicolon_stays_silent(self):
        # Attack case n34: separator damage alone at the
        # embedded position, the clean label before a
        # semicolon standing as the entry only marker,
        # outside CH-268 as its bound states.
        _model, output = _run_embedded(
            "Status; Banked", "pin_n34_embedded_clean.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_rule2(output), [])
        self.assertEqual(
            [finding for finding in h.findings_for(output)
             if h.finding_severity(finding) != "Note"], [])

    def test_pin_two_run_ground_with_case_stays_silent(self):
        # The fix wave 9 bound pin: two run ground
        # characters in one label standing with a case
        # damage, outside the bound of one.
        _assert_silent_ambiguous(
            self, "st\u200bt\u200bs: Banked",
            "pin_two_zwsp_case.md")

    def test_pin_contrast_dot_space_before_colon_still_warns(self):
        # Attack case n07, the CH-267 signalling
        # contrast member, expressly outside the charge:
        # a full stop inside the label with a plain
        # space before the colon already warns.
        _assert_near_marker(self, "St.tus : Banked",
                            "pin_n07_contrast.md")

    def test_pin_single_damage_forms_still_warn(self):
        # Each damage of the charged joints standing
        # alone takes its standing signal: the case
        # damage alone, the semicolon separator alone,
        # the space before the colon alone, the run
        # ground substitution alone, and the interior
        # damage alone.
        for status_line, name in (
                ("status: Banked", "pin_case_alone.md"),
                ("Status; Banked", "pin_semicolon_alone.md"),
                ("Status : Banked", "pin_space_alone.md"),
                ("St\u200btus: Banked", "pin_zwsp_alone.md"),
                ("St.tus: Banked", "pin_dot_alone.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)

    def test_pin_ch219_and_ch220_forms_still_warn(self):
        # The fix wave 9 charged forms on this surface:
        # m02 (CH-219), m17 and m18 (CH-220), each at
        # line start, and m24 (CH-219) embedded only.
        for status_line, name in (
                ("st\u200btus: Banked", "pin_m02.md"),
                ("St.tus; Banked", "pin_m17.md"),
                ("St\u200btus; Banked", "pin_m18.md")):
            with self.subTest(status_line=status_line):
                _assert_near_marker(self, status_line, name)
        _assert_embedded_near_marker(
            self, "st\u200btus: Banked", "pin_m24.md")

    def test_pin_capitalised_insertion_still_warns(self):
        # Attack case n31: the n05 insertion with the
        # remaining letters in the capitalised form,
        # warned through the standing cleaning reading.
        _assert_near_marker(self, "St\u200batus: Banked",
                            "pin_n31_insertion_cap.md")

    def test_pin_decided_dot_semicolon_still_warns(self):
        # Attack case n13: the CH-220 form standing as
        # the Status line of the decided base, warned at
        # exit 1 on the attack paper measurement.
        _model, output = _run_decided(
            "St.tus; RULED, closed", "pin_n13_decided.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule2(output)), 1)


if __name__ == "__main__":
    unittest.main()
