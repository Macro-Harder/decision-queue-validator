"""Step 17 (restart) fix wave 12, Fix Seat H tests.

Charges CH-347 and CH-348, cluster H (the joint
damage family of round 12), consolidated in
design/steps/step-17r-r12-triage-prep.md at section
2.6 and Cluster H of section 3, from round 12 attack
seat 16, paper at
design/steps/step-17r-r12-seat16-run.md, findings
S17-ATK12-16-01 and S17-ATK12-16-02, each Low, and
round 12 attack seat 18, paper at
design/steps/step-17r-r12-seat18-run.md, finding F-1,
Low. Seat 16 finding S17-ATK12-16-01 and seat 18
finding F-1 are the one insertion case spaced colon
construction, consolidated at T12-35 and charged at
CH-347, their members counted once in that charge.
Locus: parse.py, the label exactness readings as
cured at CH-307 to CH-309 (paper
design/steps/step-17r-fix11-h.md), whose pins stand
in product/tests/test_restart_step17_fix11_h.py and
stand unmoved by this wave.

CH-347 (T12-35, S17-ATK12-16-01 with seat 18 F-1):
a Status label carrying one run ground character
inserted beside its whole letters together with a
letter case damage and a space or tab standing
before the colon takes no signal, where every pair
of those damages takes the near marker Warning, and
its decided member validates clean. Charged
members: seat 16 cases q01 (a plain space before
the colon), q02 (a tab before the colon), and q21
(the decided member at a plain space), and seat 18
cases y01 (a plain space) and y02 (a tab), the seat
18 members standing in the same shapes as q01 and
q02. Cure bound, stated expressly: the label before
a space or tab run and its colon stands in the
CH-265 run ground insertion case joint form as
_is_run_ground_insertion_case_joint_label_damage
states it (seven characters, exactly one run ground
character at an interior position of the label, not
before the first letter and not after the last
letter, the remaining letters the whole Status word
in a letter case other than the capitalised form),
standing before a space or tab run and a colon. The
CH-265 narrowing stands alike at this separator: an
insertion at the first or last position of the
label stands outside this taking (seat 16 case q23
stays pinned silent at the spaced colon; case q24,
the first position member, keeps its standing
signal through the CH-266 spaced taking).

CH-348 (T12-36, S17-ATK12-16-02): the CH-265
insertion joint form standing as the entry only
marker in closing prose before a colon takes no
signal, where its line start twin (cured at CH-265)
and the embedded colon form of the interior joint
(seat 16 case q20) take the near marker Warning.
Charged member: seat 16 case q03 (the q01 label
standing as the entry only marker in closing prose,
its token closed by a colon). Cure bound, stated
expressly, naming the embedded only position: at
the embedded only position, a whole token standing
before a colon takes the near marker report where
its label stands in the CH-265 run ground insertion
case joint form, on the bound stated at
_is_run_ground_insertion_case_joint_label_damage.
The neighbouring narrowings stand: a case damage
alone at the embedded colon position (round 11
case p17, the round 11 paper's control) stays
silent, and a case damage alone before a semicolon
at the embedded position (case p05) stays silent.

Pins standing in this file: the cured CH-265 form
(seat 16 case q17) signalling; the cured CH-308
forms (cases p07 and p08 of round 11 seat 17)
signalling, with their tab members of this round
(seat 16 cases q05 and q06) signalling; the cured
CH-309 form (case p11) signalling; the embedded
interior joint through a colon (seat 16 case q20)
signalling; the first position spaced member (case
q24) signalling through its standing reading; and
the bound forms standing silent: the insertion
after the last label letter at the spaced colon
(case q23), the insertion after the last letter
before a semicolon (case q10), the embedded
insertion token closed by a letter after its
semicolon (case q12), the insertion form with a
space standing before a semicolon (case q11), a
case damage alone at the embedded colon and
semicolon positions (cases p17 and p05), and
separator damage alone at the embedded position
(case n34).

Constructions are the attack papers own forms,
cases q01, q02, q03, and q21 of round 12 seat 16
and cases y01 and y02 of round 12 seat 18, on the
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


class Ch347InsertionCaseSpacedColonTest(unittest.TestCase):
    """T12-35, S17-ATK12-16-01 with seat 18 F-1: one
    run ground character inserted beside the whole
    label letters, standing with a letter case
    damage, takes the near marker Warning before a
    space or tab run and a colon."""

    def test_insertion_case_space_before_colon_warns(self):
        # Attack case q01 of seat 16, and case y01 of
        # seat 18 in the same shape: the label in
        # lower case, a zero width space inserted
        # inside it, a plain space before the colon.
        _assert_near_marker(self, "st\u200batus : Banked",
                            "q01_insert_case_space_colon.md")

    def test_insertion_case_tab_before_colon_warns(self):
        # Attack case q02 of seat 16, and case y02 of
        # seat 18 in the same shape: the same label
        # standing before a tab and a colon.
        _assert_near_marker(self, "st\u200batus\t: Banked",
                            "q02_insert_case_tab_colon.md")

    def test_insertion_case_spaced_colon_decided_warns(self):
        # Attack case q21 of seat 16: the same label
        # at a plain space before the colon, as the
        # Status line of the decided base, which
        # validated clean before this cure.
        _model, output = _run_decided(
            "st\u200batus : RULED, closed", "q21_decided.md")
        self.assertIsNotNone(output)
        self.assertEqual(len(_rule2(output)), 1)

    def test_insertion_case_spaced_colon_cli(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _body("st\u200batus : Banked"),
                    "q01_insert_case_space_colon.md",
                    subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class Ch348EmbeddedInsertionColonTest(unittest.TestCase):
    """T12-36, S17-ATK12-16-02: the CH-265 insertion
    joint form standing as the entry only marker in
    closing prose before a colon takes the near
    marker Warning."""

    def test_embedded_insertion_case_colon_warns(self):
        # Attack case q03: the q01 label standing as
        # the entry only marker in closing prose, its
        # token closed by a colon.
        _assert_embedded_near_marker(
            self, "st\u200batus: Banked",
            "q03_embedded_insert_case_colon.md")

    def test_embedded_insertion_colon_cli(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    _embedded_body("st\u200batus: Banked"),
                    "q03_embedded_insert_case_colon.md",
                    subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element",
                                  combined)


class CuredNeighbourPinsTest(unittest.TestCase):
    """The cured forms of the neighbouring charges
    standing as pins, in the standings the round 12
    papers record."""

    def test_pin_ch265_insertion_colon_still_warns(self):
        # Seat 16 case q17: the insertion joint at
        # the plain colon, cured at CH-265.
        _assert_near_marker(self, "st\u200batus: Banked",
                            "pin_q17.md")

    def test_pin_ch308_forms_still_warn(self):
        _assert_near_marker(self, "st.tus : Banked",
                            "pin_p07.md")
        _assert_near_marker(self, "st\u200btus : Banked",
                            "pin_p08.md")

    def test_pin_ch308_tab_members_still_warn(self):
        # Seat 16 cases q05 and q06: the CH-308 reach
        # at the tab separator, recorded at O-3.
        _assert_near_marker(self, "st.tus\t: Banked",
                            "pin_q05.md")
        _assert_near_marker(self, "st\u200btus\t: Banked",
                            "pin_q06.md")

    def test_pin_ch309_embedded_insertion_still_warns(self):
        _assert_embedded_near_marker(
            self, "st\u200batus; Banked", "pin_p11.md")

    def test_pin_embedded_interior_colon_still_warns(self):
        # Seat 16 case q20: the interior plus case
        # joint at the embedded only position through
        # a colon, the contrast member of CH-348.
        _assert_embedded_near_marker(
            self, "st.tus: Banked", "pin_q20.md")

    def test_pin_first_position_spaced_still_warns(self):
        # Seat 16 case q24: a run ground insertion
        # before the first label letter, with a case
        # damage, before a space and a colon, taking
        # its standing signal through the CH-266
        # spaced taking.
        _assert_near_marker(self, "\u200bstatus : Banked",
                            "pin_q24.md")


class JointBoundPinsTest(unittest.TestCase):
    """Bound forms standing silent, before and after,
    in the standings the round 12 papers record at
    seat 16 observation O-2 and the earlier rounds
    record."""

    def test_pin_insertion_last_spaced_colon_silent(self):
        # Seat 16 case q23: a run ground insertion
        # after the last label letter standing with a
        # case damage before a space and a colon, the
        # CH-265 narrowing form at the spaced colon.
        _assert_silent_ambiguous(
            self, "status\u200b : Banked", "pin_q23.md")

    def test_pin_insertion_last_semicolon_silent(self):
        # Seat 16 case q10: the same narrowing at the
        # semicolon, outside the CH-307 taking.
        _assert_silent_ambiguous(
            self, "status\u200b; Banked", "pin_q10.md")

    def test_pin_embedded_letter_closed_silent(self):
        # Seat 16 case q12: an embedded insertion
        # token whose semicolon is closed by a
        # letter, outside the CH-309 taking by its
        # closure narrowing.
        _assert_embedded_silent(
            self, "st\u200batus;Banked", "pin_q12.md")

    def test_pin_insertion_space_semicolon_silent(self):
        # Seat 16 case q11: the insertion form with
        # a case damage and a plain space standing
        # before a semicolon, an extent recorded at
        # O-2 and not charged.
        _assert_silent_ambiguous(
            self, "st\u200batus ; Banked", "pin_q11.md")

    def test_pin_embedded_case_alone_colon_silent(self):
        # Round 11 case p17: a case damage alone at
        # the embedded colon position, the control
        # on which CH-348 is bounded.
        _assert_embedded_silent(
            self, "status: Banked", "pin_p17.md")

    def test_pin_embedded_case_alone_semicolon_silent(self):
        # Round 11 case p05: a case damage alone
        # before a semicolon at the embedded only
        # position, outside the CH-268 takings.
        _assert_embedded_silent(
            self, "status; Banked", "pin_p05.md")

    def test_pin_embedded_clean_semicolon_silent(self):
        # Round 10 case n34: separator damage alone
        # at the embedded position.
        _assert_embedded_silent(
            self, "Status; Banked", "pin_n34.md")


if __name__ == "__main__":
    unittest.main()
