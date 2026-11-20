"""Step 17 (restart) fix wave 11, Fix Seat H tests.

Charges CH-307 to CH-309, cluster H (the joint damage
family of round 11), consolidated in
design/steps/step-17r-r11-triage-prep.md at Cluster H
from round 11 attack seat 17, paper at
design/steps/step-17r-r11-seat17-run.md, findings
S17-ATK11-17-01 to S17-ATK11-17-03, each Low. Locus:
parse.py, the label exactness readings as cured at
CH-264 to CH-268 (paper
design/steps/step-17r-fix10-h.md), whose pins stand
in product/tests/test_restart_step17_fix10_h.py and
stand unmoved by this wave.

CH-307 (T11-35, S17-ATK11-17-01): a Status label
carrying one run ground character inserted beside
its whole letters together with a letter case damage
takes no signal before a semicolon separator, where
the same insertion joint at the colon (CH-265) and
the substitution member of the same triple at the
semicolon (CH-264) each take the near marker
Warning. Charged member: case p03 (the label in
lower case, a zero width space inserted inside it,
a semicolon as separator, at line start). Cure
bound, stated expressly: the label before the
semicolon stands in the CH-265 run ground insertion
case joint form as
_is_run_ground_insertion_case_joint_label_damage
states it (seven characters, exactly one run ground
character at an interior position of the label, not
before the first letter and not after the last
letter, the remaining letters the whole Status word
in a letter case other than the capitalised form),
standing before a semicolon separator. The stated
narrowing of CH-265 stands: an insertion at the
first or last position of the label (cases p01 and
p02 of round 11 seat 17) stands outside this cure;
p02 stays silent, and p01 keeps its standing signal
through its standing reading.

CH-308 (T11-36, S17-ATK11-17-02): a Status label
carrying one interior damage together with a letter
case damage and a space standing before the colon
takes no signal, on the full stop member and on the
run ground member, where every pair of those damages
takes the Warning. Charged members: case p07 (a
full stop inside the label, the label in lower
case, a plain space before the colon) and case p08
(a zero width space in place of the letter a, the
label in lower case, a plain space before the
colon). Cure bound, stated expressly: the label
before a space or tab run and its colon stands in
the CH-186 case joint form as
_is_case_joint_label_damage states it (the full
stop member: one interior damage of the CH-128
classes standing with a letter case damage), or in
the CH-219 run ground case joint form as
_is_run_ground_case_joint_label_damage states it
(the run ground member: one run ground character in
place of one label letter at an interior position,
standing with a letter case damage), each on the
bounds those helpers state. The charge stands on
its two named members only.

CH-309 (T11-37, S17-ATK11-17-03): the CH-265
insertion joint form standing as the entry only
marker in closing prose before a semicolon takes no
signal, where its line start twin is charged at
CH-307 and the embedded semicolon forms of the
substitution classes (CH-268) take the Warning.
Charged member: case p11 (the p03 label standing as
the entry only marker in closing prose). Cure
bound, stated expressly, naming the embedded only
position: at the embedded only position, a whole
token closed by the end of the line or by a space
or a tab, carrying a semicolon at its end, takes
the near marker report where the label before the
semicolon stands in the CH-265 run ground insertion
case joint form, on the bound stated at
_is_run_ground_insertion_case_joint_label_damage.
The CH-268 narrowings stand: a case damage alone
before a semicolon at the embedded position (case
p05) stays silent, a token whose semicolon is
closed by a letter (case p09) stays silent, and
separator damage alone at the embedded position
(case n34) stays silent.

Pins standing in this file: the cured CH-264 to
CH-268 forms (cases n03, n05, n08, n09, n10, n11,
n12, n14, n29, n35 of round 10 seat 17) signalling;
the bound forms of round 11 seat 17 observation
O-2 (case p02 silent, case p05 silent, case p09
silent, case p14 silent, case p10 silent as the
embedded member of the pinned n04 family); the
pinned case plus interior plus semicolon triple
(case n04) silent; two interior damages before a
semicolon (case n27) silent; separator damage alone
at the embedded position (case n34) silent; and the
CH-267 contrast member (case n07) signalling.

Constructions are the attack papers own forms,
cases p03, p07, p08, and p11 of round 11 seat 17
and the round 10 forms named in the pins, on the
round papers two entry base and on the embedded
only form of that base, rebuilt inline in the
shapes the attack papers state.

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


def _assert_embedded_silent(test_case, marker_line, name):
    _model, output = _run_embedded(marker_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(
        [finding for finding in h.findings_for(output)
         if h.finding_severity(finding) != "Note"], [])


class Ch307InsertionCaseSemicolonTest(unittest.TestCase):
    """T11-35, S17-ATK11-17-01: one run ground character
    inserted beside the whole label letters, standing
    with a letter case damage, takes the near marker
    Warning before a semicolon separator."""

    def test_insertion_case_semicolon_warns(self):
        # Attack case p03: the label in lower case, a
        # zero width space inserted inside it, a
        # semicolon standing as the separator.
        _assert_near_marker(self, "st\u200batus; Banked",
                            "p03_insert_case_semicolon.md")

    def test_insertion_case_semicolon_cli(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("st\u200batus; Banked"),
                    "p03_insert_case_semicolon.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch308InteriorCaseSpaceColonTest(unittest.TestCase):
    """T11-36, S17-ATK11-17-02: one interior damage
    standing together with a letter case damage and a
    space before the colon takes the near marker
    Warning, on the full stop member and on the run
    ground member."""

    def test_full_stop_case_space_before_colon_warns(self):
        # Attack case p07: a full stop inside the
        # label, the label in lower case, a plain
        # space standing before the colon.
        _assert_near_marker(self, "st.tus : Banked",
                            "p07_dot_space_case.md")

    def test_run_ground_case_space_before_colon_warns(self):
        # Attack case p08: a zero width space in place
        # of the letter a, the label in lower case, a
        # plain space standing before the colon.
        _assert_near_marker(self, "st\u200btus : Banked",
                            "p08_rg_space_case.md")

    def test_space_joint_cli(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("st.tus : Banked"),
                    "p07_dot_space_case.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch309EmbeddedInsertionSemicolonTest(unittest.TestCase):
    """T11-37, S17-ATK11-17-03: the CH-265 insertion
    joint form standing as the entry only marker in
    closing prose before a semicolon takes the near
    marker Warning."""

    def test_embedded_insertion_case_semicolon_warns(self):
        # Attack case p11: the p03 label standing as
        # the entry only marker in closing prose.
        _assert_embedded_near_marker(
            self, "st\u200batus; Banked",
            "p11_embedded_insert_case_semicolon.md")

    def test_embedded_insertion_cli(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _embedded_body("st\u200batus; Banked"),
                    "p11_embedded_insert_case_semicolon.md",
                    subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class CuredWave10PinsTest(unittest.TestCase):
    """The cured CH-264 to CH-268 forms standing as
    pins, in the standings the fix wave 10 module
    records."""

    def test_pin_ch264_forms_still_warn(self):
        _assert_near_marker(self, "st\u200btus; Banked",
                            "pin_n03.md")
        _assert_embedded_near_marker(
            self, "st\u200btus; Banked", "pin_n12.md")
        _model, output = _run_decided(
            "st\u200btus; RULED, closed", "pin_n14.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule2(output)), 1)

    def test_pin_ch265_form_still_warns(self):
        _assert_near_marker(self, "st\u200batus: Banked",
                            "pin_n05.md")

    def test_pin_ch266_forms_still_warn(self):
        _assert_near_marker(self, "status; Banked",
                            "pin_n10.md")
        _assert_near_marker(self, "status : Banked",
                            "pin_n09.md")

    def test_pin_ch267_forms_still_warn(self):
        _assert_near_marker(self, "St\u200btus : Banked",
                            "pin_n08.md")
        _assert_near_marker(self, "St.tus\t: Banked",
                            "pin_n29.md")
        _assert_near_marker(self, "St.tus : Banked",
                            "pin_n07.md")

    def test_pin_ch268_forms_still_warn(self):
        _assert_embedded_near_marker(
            self, "St\u200btus; Banked", "pin_n35.md")
        _assert_embedded_near_marker(
            self, "St.tus; Banked", "pin_n11.md")


class JointBoundPinsTest(unittest.TestCase):
    """Bound forms standing silent, before and after,
    in the standings round 11 seat 17 records at its
    observation O-2 and the fix wave 10 pins record."""

    def test_pin_insertion_last_position_stays_silent(self):
        # Attack case p02: a run ground insertion after
        # the last label letter standing with a case
        # damage, outside the CH-265 limb by its stated
        # narrowing at the last position.
        _assert_silent_ambiguous(
            self, "status\u200b: Banked", "pin_p02.md")

    def test_pin_embedded_case_alone_stays_silent(self):
        # Attack case p05: a case damage alone before a
        # semicolon at the embedded only position,
        # outside the CH-268 takings by its stated
        # narrowing.
        _assert_embedded_silent(
            self, "status; Banked", "pin_p05.md")

    def test_pin_embedded_letter_closed_stays_silent(self):
        # Attack case p09: an embedded interior token
        # whose semicolon is closed by a letter, outside
        # the CH-268 taking by its closure narrowing.
        _model, output = _run_embedded(
            "St.tus;Banked", "pin_p09.md")
        self.assertIsNotNone(output)
        self.assertEqual(_rule2(output), [])

    def test_pin_two_run_ground_semicolon_stays_silent(self):
        # Attack case p14: two run ground characters
        # standing with a case damage before a
        # semicolon, past the bound of one.
        _assert_silent_ambiguous(
            self, "s\u200b\u200btus; Banked", "pin_p14.md")

    def test_pin_embedded_triple_stays_silent(self):
        # Attack case p10: the case plus interior plus
        # semicolon triple at the embedded only
        # position, the embedded member of the pinned
        # n04 family.
        _assert_embedded_silent(
            self, "st.tus; Banked", "pin_p10.md")

    def test_pin_case_interior_semicolon_triple_silent(self):
        _assert_silent_ambiguous(
            self, "st.tus; Banked", "pin_n04.md")

    def test_pin_two_interior_semicolon_stays_silent(self):
        _assert_silent_ambiguous(
            self, "St.t!s; Banked", "pin_n27.md")

    def test_pin_embedded_clean_semicolon_stays_silent(self):
        _assert_embedded_silent(
            self, "Status; Banked", "pin_n34.md")


if __name__ == "__main__":
    unittest.main()
