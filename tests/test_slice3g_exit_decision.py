"""Slice 3, Unit 3g, Exit decision group.

The Exit decision with its set of reason classes, travelling with the
code in the order the causes stand in the precedence: exit 4 for
governing material and for unparsed entries, both classes named on a
combined run, exit 1 for Error and Warning findings, exit 0 where
Note findings alone stand, and the manifest exit code of every
corpus fixture.
"""

import unittest

import dqv_harness as h


def _output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    return output


class ManifestExitCodesTest(unittest.TestCase):

    def test_every_fixture_exit_code_matches_the_manifest(self):
        for fixture_id in h.FIXTURE_IDS:
            with self.subTest(fixture=fixture_id):
                _model, output = h.cached_pipeline(fixture_id)
                if output is None:
                    code, _out, _err = h.cached_run(fixture_id, "validate")
                    self.assertEqual(code, h.expected_exit(fixture_id),
                                     fixture_id)
                else:
                    self.assertEqual(h.exit_code_of(output),
                                     h.expected_exit(fixture_id),
                                     fixture_id)


class ExitFourCausesTest(unittest.TestCase):

    def test_r1_r2_r4_r7_each_carry_a_governing_cause(self):
        for fixture_id in ("R1", "R2", "R4", "R7"):
            with self.subTest(fixture=fixture_id):
                output = _output(fixture_id)
                self.assertEqual(h.exit_code_of(output), 4)
                self.assertTrue(h.reason_classes_of(output))

    def test_s13_names_both_reason_classes(self):
        output = _output("S13")
        self.assertEqual(h.exit_code_of(output), 4)
        reasons = h.reason_classes_of(output)
        self.assertGreaterEqual(len(reasons), 2)
        joined = " ".join(reasons).lower()
        self.assertTrue("unparsed" in joined or "pin 12" in joined)
        self.assertTrue("ambig" in joined or "govern" in joined
                        or "pin 9" in joined or "conditional" in joined)

    def test_s7c_unparsed_cause_alone_exits_four(self):
        output = _output("S7c")
        self.assertEqual(h.exit_code_of(output), 4)
        reasons = " ".join(h.reason_classes_of(output)).lower()
        self.assertIn("unparsed", reasons)

    def test_reason_classes_travel_in_precedence_order(self):
        output = _output("S13")
        reasons = [reason.lower() for reason in
                   h.reason_classes_of(output)]
        pin9_index = next(
            (index for index, reason in enumerate(reasons)
             if "ambig" in reason or "govern" in reason
             or "pin 9" in reason or "conditional" in reason), None)
        pin12_index = next(
            (index for index, reason in enumerate(reasons)
             if "unparsed" in reason or "pin 12" in reason), None)
        self.assertIsNotNone(pin9_index)
        self.assertIsNotNone(pin12_index)
        self.assertLess(pin9_index, pin12_index)


class ExitFourReasonWordingTest(unittest.TestCase):
    """The exit 4 reason classes stand in plain words alone.

    OP-Q11 rules the closing line as stating the exit code and, in
    plain words, every reason class present. The brief's pin numbers
    are the classes' homes in the brief, not words the shipped
    surface defines, so no reason string and no closing line carries
    a pin citation. Expectations are the reason classes in their
    plain words, with no other word changed.
    """

    def test_r1_reason_class_stands_without_a_pin_citation(self):
        output = _output("R1")
        reasons = h.reason_classes_of(output)
        self.assertEqual(
            reasons, ["ambiguous or conditional entries govern "
                      "the exit"])
        code, out, _err = h.cached_run("R1", "validate")
        self.assertEqual(code, 4)
        closing = [line for line in
                   out.decode("utf-8", errors="replace")
                   .strip().splitlines() if line][-1]
        self.assertIn(
            "exit 4: ambiguous or conditional entries govern "
            "the exit;", closing)
        self.assertNotIn("pin", closing)

    def test_s13_both_reason_classes_stand_without_pin_citations(self):
        output = _output("S13")
        reasons = h.reason_classes_of(output)
        self.assertEqual(
            reasons,
            ["ambiguous or conditional entries govern the exit",
             "an unparsed entry stands in the file"])
        code, out, _err = h.cached_run("S13", "validate")
        self.assertEqual(code, 4)
        closing = [line for line in
                   out.decode("utf-8", errors="replace")
                   .strip().splitlines() if line][-1]
        self.assertIn("an unparsed entry stands in the file;",
                      closing)
        self.assertNotIn("pin", closing)


class UnparsedErrorFindingTest(unittest.TestCase):
    """Pin 12: an unparsed entry carries an Error finding.

    Brief pin 12 rules the unparsed entry's finding grade as Error;
    criterion 5 and the shipped corpus manifest state the same
    expectation for fixtures S7c and S13 (one unparsed entry, an
    Error, and exit 4). The finding stands beside the carriage, the
    reconciliation row, and the exit 4 behaviour the other groups
    pin: the head counts and the closing line count it.
    """

    def test_s7c_carries_one_error_finding_on_the_unparsed_entry(self):
        output = _output("S7c")
        findings = h.findings_of(output)
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(h.finding_severity(finding), "Error")
        self.assertEqual(h.finding_entry_id(finding), "DQ-901")
        recon = h.reconciliation_of(output)
        per_severity = h.get(recon, "findings_per_severity")
        counts = {h.text_of(key): h.int_of(value)
                  for key, value in per_severity.items()}
        self.assertEqual(counts.get("Error"), 1)
        self.assertEqual(h.unparsed_count(output), 1)
        self.assertEqual(h.exit_code_of(output), 4)

    def test_s13_carries_one_error_finding_on_the_unparsed_entry(self):
        output = _output("S13")
        errors = [finding for finding in h.findings_of(output)
                  if h.finding_severity(finding) == "Error"]
        self.assertEqual(len(errors), 1)
        self.assertEqual(h.finding_entry_id(errors[0]), "DQ-902")
        self.assertEqual(h.unparsed_count(output), 1)
        self.assertEqual(h.ambiguous_count(output), 1)
        self.assertEqual(h.exit_code_of(output), 4)

    def test_s7c_validate_output_counts_the_error_in_its_closing_line(self):
        code, out, _err = h.cached_run("S7c", "validate")
        self.assertEqual(code, 4)
        text = out.decode("utf-8", errors="replace")
        self.assertNotIn("No findings.", text)
        closing = [line for line in text.strip().splitlines()
                   if line][-1]
        self.assertIn("1 Error", closing)


class ExitOneAndZeroTest(unittest.TestCase):

    def test_warning_only_and_error_runs_exit_one(self):
        for fixture_id in ("S1", "S2", "S4", "S5b", "S6", "S15",
                           "S18", "R3", "R5", "R6", "R9"):
            with self.subTest(fixture=fixture_id):
                output = _output(fixture_id)
                self.assertEqual(h.exit_code_of(output), 1, fixture_id)

    def test_note_findings_alone_leave_exit_zero(self):
        output = _output("S14")
        severities = {h.finding_severity(finding)
                      for finding in h.findings_of(output)}
        self.assertEqual(severities, {"Note"})
        self.assertEqual(h.exit_code_of(output), 0)

    def test_clean_runs_exit_zero(self):
        # R8 stood in this list until the Step 19 R-08 fix: its
        # DQ-130 settlement block records no landing in a recorded
        # form, so the entry now draws the check 5 landing Warning
        # and R8 exits 1, as its derived manifest expectation
        # records.
        for fixture_id in ("S3a", "S3b", "S3c", "S5", "S11", "S12"):
            with self.subTest(fixture=fixture_id):
                output = _output(fixture_id)
                self.assertEqual(h.exit_code_of(output), 0, fixture_id)

    def test_exit_four_masks_exit_one_but_findings_still_stand(self):
        output = _output("R1")
        self.assertEqual(h.exit_code_of(output), 4)
        warnings = [finding for finding in h.findings_of(output)
                    if h.finding_severity(finding) == "Warning"]
        # 53 since the Step 19 R-08 fix: the R1 block settlements
        # that record no landing in a recorded form draw the
        # check 5 landing Warning, as the fix register records.
        self.assertEqual(len(warnings), 53)


class FileLevelExitThreeTest(unittest.TestCase):

    def test_file_level_fixtures_exit_three_at_the_command_line(self):
        for fixture_id in ("S7a", "S7b", "S10"):
            with self.subTest(fixture=fixture_id):
                for subcommand in ("validate", "render"):
                    code, _out, _err = h.cached_run(fixture_id,
                                                    subcommand)
                    self.assertEqual(code, 3, fixture_id + " " +
                                     subcommand)


if __name__ == "__main__":
    unittest.main()
