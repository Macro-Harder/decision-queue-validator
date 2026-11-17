"""Slice 3, Unit 3c, whole file checks group.

Checks 1 and 6 as predicates over the whole file model: the number
ledger with its duplicate Error and its gap Warning grouped per run
of missing integers, the whole file assignment with its headline
Error, the label reattachment Warnings, the FILE finding position and
order in the full findings list, and the combined defects case that
proves no recoverable defect suppresses another.
"""

import re
import unittest

import dqv_harness as h


def _output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    return output


def _file_key(finding, model_entries):
    """The five key order for FILE findings, as decided.

    Keys: the producing rule number; the line span start, a gap
    finding carrying the span of the entry heading before its gap, or
    start 0 before the first heading; the line span end; the verbatim
    evidence compared byte wise; the printed statement compared byte
    wise.
    """
    rule = h.finding_rule_number(finding)
    start, end = h.span_of(finding)
    evidence = h.finding_evidence_text(finding)
    statement = h.finding_statement(finding) or ""
    return (rule, start, end, evidence.encode("utf-8"),
            statement.encode("utf-8"))


class Check1NumberLedgerTest(unittest.TestCase):

    def test_s1_duplicate_error_names_both_heading_lines(self):
        output = _output("S1")
        errors = h.findings_for(output, rule=1, severity="Error")
        self.assertEqual(len(errors), 1)
        evidence = h.finding_evidence_text(errors[0]) + \
            (h.finding_statement(errors[0]) or "")
        # The duplicate pair in fixture S1 stands at fixture lines 3
        # and 17, both headed DQ-142. The Error must name both heading
        # lines as standalone numbers: a substring scan would be met
        # by the digits inside the entry token itself, so each line
        # number is required on a digit boundary of its own.
        for line_number in ("3", "17"):
            self.assertIsNotNone(
                re.search(r"(?<!\d)" + line_number + r"(?!\d)",
                          evidence),
                "heading line " + line_number + " is not named")
        start, end = h.span_of(errors[0])
        self.assertGreaterEqual(start, 1)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s2_gap_warning_names_the_missing_set(self):
        output = _output("S2")
        warnings = h.findings_for(output, rule=1, severity="Warning")
        self.assertEqual(len(warnings), 1)
        blob = (h.finding_evidence_text(warnings[0]) + " " +
                (h.finding_statement(warnings[0]) or ""))
        self.assertIn("37", blob)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_r6_gap_findings_group_missing_integers_per_run(self):
        output = _output("R6")
        warnings = h.findings_for(output, rule=1, severity="Warning")
        self.assertEqual(len(warnings), 2)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_r4_gap_is_one_finding_for_one_run(self):
        output = _output("R4")
        warnings = h.findings_for(output, rule=1, severity="Warning")
        self.assertEqual(len(warnings), 1)

    def test_r1_number_ledger_is_clean(self):
        output = _output("R1")
        self.assertEqual(h.findings_for(output, rule=1), [])


class Check6AssignmentTest(unittest.TestCase):

    def test_model_double_fires_the_headline_error_naming_both_lines(self):
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        double = h.check6_model_double()
        output = h.validate_function(validate_module)(double, vocabulary)
        errors = h.findings_for(output, rule=6, severity="Error")
        self.assertEqual(len(errors), 1)
        blob = (h.finding_evidence_text(errors[0]) + " " +
                (h.finding_statement(errors[0]) or ""))
        self.assertIn("7", blob)
        self.assertIn("9", blob)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_r8_is_the_non_firing_side(self):
        output = _output("R8")
        self.assertEqual(h.findings_for(output, rule=6), [])
        self.assertEqual(h.exit_code_of(output),
                         h.expected_exit("R8"))

    def test_r5_headed_entries_eight(self):
        model, _output = h.cached_pipeline("R5")
        self.assertEqual(len(h.entries_of(model)), 8)

    def test_r5_two_reattachment_warnings(self):
        output = _output("R5")
        warnings = h.findings_for(output, rule=6, severity="Warning")
        self.assertEqual(len(warnings), 2)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s8_one_reattachment_warning(self):
        output = _output("S8")
        warnings = h.findings_for(output, rule=6, severity="Warning")
        self.assertEqual(len(warnings), 1)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_r2_reattachment_warnings_are_absent(self):
        output = _output("R2")
        self.assertEqual(h.findings_for(output, rule=6), [])


class FileGroupOrderTest(unittest.TestCase):

    def test_combined_defects_file_group_order(self):
        data, _facts = h.combined_defects_input()
        _model, output = h.run_pipeline(data, "combined.md")
        findings = h.findings_of(output)
        file_findings = [finding for finding in findings
                         if h.finding_entry_id(finding) == "FILE"]
        self.assertTrue(file_findings)
        first_entry_index = next(
            index for index, finding in enumerate(findings)
            if h.finding_entry_id(finding) != "FILE")
        file_indices = [index for index, finding in enumerate(findings)
                        if h.finding_entry_id(finding) == "FILE"]
        self.assertLess(max(file_indices), first_entry_index)
        keys = [_file_key(finding, None) for finding in file_findings]
        self.assertEqual(keys, sorted(keys))
        rules = [key[0] for key in keys]
        self.assertIn(1, rules)
        self.assertIn(5, rules)

    def test_pin5_unmatched_heading_keys_at_five(self):
        data, _facts = h.unmatched_heading_input("h5")
        _model, output = h.run_pipeline(data, "unmatched.md")
        file_findings = [finding for finding in h.findings_of(output)
                         if h.finding_entry_id(finding) == "FILE"]
        self.assertEqual(len(file_findings), 1)
        self.assertEqual(h.finding_rule_number(file_findings[0]), 5)

    def test_file_findings_stand_before_entry_findings_on_r1(self):
        output = _output("R1")
        findings = h.findings_of(output)
        file_indices = [index for index, finding in enumerate(findings)
                        if h.finding_entry_id(finding) == "FILE"]
        entry_indices = [index for index, finding in enumerate(findings)
                         if h.finding_entry_id(finding) != "FILE"]
        if file_indices and entry_indices:
            self.assertLess(max(file_indices), min(entry_indices))
        data, _facts = h.combined_defects_input()
        _model, combined = h.run_pipeline(data, "combined.md")
        combined_findings = h.findings_of(combined)
        file_indices = [index for index, finding
                        in enumerate(combined_findings)
                        if h.finding_entry_id(finding) == "FILE"]
        entry_indices = [index for index, finding
                         in enumerate(combined_findings)
                         if h.finding_entry_id(finding) != "FILE"]
        self.assertTrue(file_indices)
        self.assertTrue(entry_indices)
        self.assertLess(max(file_indices), min(entry_indices))


class CombinedDefectsTest(unittest.TestCase):

    def test_all_four_defects_fire_in_one_run(self):
        data, _facts = h.combined_defects_input()
        _model, output = h.run_pipeline(data, "combined.md")
        duplicates = [finding for finding in h.findings_of(output)
                      if h.finding_rule_number(finding) == 1
                      and h.finding_severity(finding) == "Error"]
        gaps = [finding for finding in h.findings_of(output)
                if h.finding_rule_number(finding) == 1
                and h.finding_severity(finding) == "Warning"]
        near_markers = h.findings_for(output, rule=2,
                                      severity="Warning")
        unmatched = [finding for finding in h.findings_of(output)
                     if h.finding_rule_number(finding) == 5
                     and h.finding_severity(finding) == "Warning"]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(len(near_markers), 1)
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_combined_defects_gap_names_902(self):
        data, _facts = h.combined_defects_input()
        _model, output = h.run_pipeline(data, "combined.md")
        gaps = [finding for finding in h.findings_of(output)
                if h.finding_rule_number(finding) == 1
                and h.finding_severity(finding) == "Warning"]
        blob = (h.finding_evidence_text(gaps[0]) + " " +
                (h.finding_statement(gaps[0]) or ""))
        self.assertIn("902", blob)


class Step17C2UnparsedStatementTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge T-2: the rule 12
    statement printed for an unparsed entry must be true of
    that entry. An entry cut off in its final line carries a
    body in the file, so a statement that its heading stands
    with no body is false for it, and the advice built on that
    statement points the wrong way."""

    _CUT_OFF = (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Cut off entry\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "This question is waiting for a decision.\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "Partial prose frag")

    _HEADING_ONLY = (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Heading only entry\n")

    def test_cut_off_entry_with_a_body_takes_no_no_body_statement(self):
        _model, output = h.run_pipeline(
            self._CUT_OFF.encode("utf-8"), "cut_off.md")
        errors = h.findings_for(output, entry_id="DQ-001", rule=12,
                                severity="Error")
        self.assertEqual(len(errors), 1)
        statement = h.finding_statement(errors[0]) or ""
        self.assertNotIn("stands with no body", statement)
        self.assertIn("body", statement)

    def test_heading_only_entry_keeps_the_no_body_statement(self):
        _model, output = h.run_pipeline(
            self._HEADING_ONLY.encode("utf-8"), "heading_only.md")
        errors = h.findings_for(output, entry_id="DQ-001", rule=12,
                                severity="Error")
        self.assertEqual(len(errors), 1)
        statement = h.finding_statement(errors[0]) or ""
        self.assertIn("no body", statement)


if __name__ == "__main__":
    unittest.main()
