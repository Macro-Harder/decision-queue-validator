"""Slice 3, Unit 3f, reconciliation and crosswalk group.

The reconciliation block computed once with its self check, the
paired total declarations, the verbatim appendix rows and their sum
to the Status occurrence total, the crosswalk counts at their single
handoff carriage, the decider subtotals, the distinct phrasing count
at its single home, and the waiting and blocking figures with their
limbo sentence data. The self check failure double stands in this
group at the validate self check seam.
"""

import unittest

import dqv_harness as h


def _output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    return output


class ReconciliationSumsTest(unittest.TestCase):

    def test_r1_entry_total_sums_from_its_rows(self):
        output = _output("R1")
        counts = h.canonical_counts(output)
        total = sum(counts.values()) + h.ambiguous_count(output) + \
            h.unparsed_count(output)
        self.assertEqual(total, 157)
        self.assertEqual(h.int_of(h.entry_total(output)), 157)

    def test_r1_findings_views_sum_to_the_findings_list(self):
        output = _output("R1")
        findings = h.findings_of(output)
        self.assertEqual(len(findings), 8)
        per_severity = {}
        per_rule = {}
        for finding in findings:
            severity = h.finding_severity(finding)
            per_severity[severity] = per_severity.get(severity, 0) + 1
            rule = h.finding_rule_number(finding)
            per_rule[rule] = per_rule.get(rule, 0) + 1
        self.assertEqual(per_severity,
                         {"Error": 0, "Warning": 3, "Note": 5}
                         if per_severity.get("Error") else
                         {"Warning": 3, "Note": 5})
        recon = h.reconciliation_of(output)
        by_severity = h.get(recon, "findings_per_severity",
                            "findings_by_severity")
        if isinstance(by_severity, dict):
            stated = {h.text_of(key): h.int_of(value)
                      for key, value in by_severity.items()}
            self.assertEqual(sum(stated.values()), 8)
            self.assertEqual(stated.get("Warning"), 3)
            self.assertEqual(stated.get("Note"), 5)
        by_rule = h.get(recon, "findings_per_rule",
                        "findings_by_rule")
        if isinstance(by_rule, dict):
            stated_rules = {}
            for key, value in by_rule.items():
                if isinstance(value, dict):
                    stated_rules[h.finding_rule_number({"rule_id": key})] = \
                        sum(h.int_of(item) for item in value.values())
                else:
                    stated_rules[h.finding_rule_number({"rule_id": key})] = \
                        h.int_of(value)
            self.assertEqual(sum(stated_rules.values()), 8)
            self.assertEqual(stated_rules.get(4), 2)
            self.assertEqual(stated_rules.get(6), 2)
            self.assertEqual(stated_rules.get(8), 4)

    def test_derived_finding_totals_for_r2_r6_and_r9(self):
        r2 = _output("R2")
        self.assertEqual(len(h.findings_of(r2)), 6)
        severities = [h.finding_severity(finding)
                      for finding in h.findings_of(r2)]
        self.assertEqual(severities.count("Warning"), 1)
        self.assertEqual(severities.count("Note"), 5)
        r6 = _output("R6")
        self.assertEqual(len(h.findings_of(r6)), 2)
        r9 = _output("R9")
        self.assertEqual(len(h.findings_of(r9)), 2)

    def test_r1_self_check_reports_sums_agree(self):
        output = _output("R1")
        recon = h.reconciliation_of(output)
        check = h.get(recon, "self_check", "self_check_result")
        if check is None:
            check = h.get(output, "self_check", "self_check_result")
        self.assertIsNotNone(check)
        ok = h.get(check, "ok", "passed", "sums_agree", "agrees")
        if isinstance(check, str):
            self.assertIn("agree", check.lower())
        else:
            self.assertTrue(bool(ok))

    def test_paired_total_declarations_stand_in_the_block(self):
        output = _output("R1")
        text = h.render_text(output, "render")
        self.assertIn("157", text)
        self.assertIn("238", text)


class VerbatimAppendixTest(unittest.TestCase):

    def test_r1_appendix_rows_sum_to_the_occurrence_total(self):
        output = _output("R1")
        rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                               "appendix_rows", "verbatim_appendix"))
        self.assertTrue(rows)
        total = 0
        kinds = {}
        for row in rows:
            count = h.int_of(h.get(row, "occurrence_count", "count",
                                   "occurrences"))
            total += count
            kind = h.text_of(h.get(row, "kind", "kind_marker"))
            kinds[kind] = kinds.get(kind, 0) + count
        self.assertEqual(total, 238)
        self.assertEqual(kinds.get("line start"), 233)
        self.assertEqual(kinds.get("embedded"), 3)
        self.assertEqual(kinds.get("variant"), 2)

    def test_appendix_rows_carry_member_entries(self):
        output = _output("R1")
        rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                               "appendix_rows", "verbatim_appendix"))
        for row in rows:
            members = h.get(row, "member_entry_ids", "members",
                            "entry_ids", "entries")
            self.assertIsNotNone(members)
            self.assertTrue(h.as_list(members))

    def test_appendix_rows_order_by_first_occurrence(self):
        # The appendix row shape of brief section 5.5 carries the
        # phrasing verbatim, its occurrence count, its kind marker,
        # its member entry identifiers and the unclassified mark, and
        # no first occurrence line field, so the order is verified
        # from the stated fields alone: each row first occurrence is
        # located in the fixture bytes by its own phrasing under its
        # own kind, under the forms of brief section 5.3, and the
        # rows must stand in that order. A row whose phrasing cannot
        # be located fails here instead of passing on a substitute.
        output = _output("R1")
        rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                               "appendix_rows", "verbatim_appendix"))
        self.assertTrue(rows)
        fixture_lines = h.fixture_bytes("R1").decode(
            "utf-8").split("\n")
        fixture_lines = [line[:-1] if line.endswith("\r") else line
                         for line in fixture_lines]

        def first_occurrence(phrasing, kind):
            for index, line in enumerate(fixture_lines):
                if kind == "line start":
                    if line.startswith("Status:"):
                        value = line[len("Status:"):].lstrip(" ")
                        if value == phrasing:
                            return (index + 1,
                                    line.index("Status:"))
                elif kind == "embedded":
                    at = line.find("Status:", 1)
                    if at > 0 and \
                            line[at + len("Status:"):].lstrip(
                                " ").startswith(phrasing):
                        return (index + 1, at)
                elif kind == "variant":
                    at = line.find(phrasing)
                    if at >= 0 and "Status unchanged" in line:
                        return (index + 1, at)
            return None

        keys = []
        for row in rows:
            phrasing = h.text_of(h.get(row, "phrasing",
                                       "status_phrasing",
                                       "verbatim_phrasing", "value"))
            kind = h.text_of(h.get(row, "kind", "kind_marker"))
            self.assertIsNotNone(phrasing)
            self.assertIsNotNone(kind)
            found = first_occurrence(phrasing, kind)
            self.assertIsNotNone(
                found, "no occurrence of " + str(phrasing) +
                " under kind " + str(kind))
            keys.append(found)
        self.assertEqual(keys, sorted(keys))


class SingleCarriageCountsTest(unittest.TestCase):

    def test_distinct_phrasing_count_is_its_own_type_at_its_home(self):
        type_cls = h.find_type("DistinctPhrasingCount")
        self.assertIsNotNone(type_cls)
        _model, output = h.cached_pipeline("R1")
        recon = h.reconciliation_of(output)
        value = h.get(recon, "distinct_phrasing_count",
                      "DistinctPhrasingCount", "distinct_status_phrasings")
        self.assertIsNotNone(value)
        self.assertIs(type(value), type_cls)
        self.assertEqual(h.int_of(value), 29)
        facts = h.get(output, "file_facts", "file_facts_data")
        other = h.get(facts, "distinct_phrasing_count")
        self.assertIsNone(other)

    def test_h4_count_has_a_single_carriage(self):
        model, output = h.cached_pipeline("R1")
        model_value = h.get(model, "h4_sub_heading_count")
        self.assertEqual(h.int_of(model_value), 113)
        header_facts = h.get(model, "header_facts", "file_header_facts")
        self.assertIsNone(h.get(header_facts, "h4_sub_heading_count"))
        recon = h.reconciliation_of(output)
        recon_value = h.get(recon, "h4_sub_heading_count")
        self.assertEqual(h.int_of(recon_value), 113)
        facts = h.get(output, "file_facts", "file_facts_data")
        self.assertIsNone(h.get(facts, "h4_sub_heading_count"))


class ValidateModulePurityTest(unittest.TestCase):

    def test_validate_module_is_pure(self):
        banned = ("open(", "print(", "input(", "os.environ", "getenv",
                  "socket", "urllib", "requests", "random.", "time.time",
                  "datetime.now", "date.today")
        source = h.module_source("validate")
        for token in banned:
            self.assertNotIn(token, source, "validate uses " + token)


class CrosswalkTest(unittest.TestCase):

    def test_crosswalk_travels_inside_the_validate_output(self):
        output = _output("R1")
        crosswalk = h.get(output, "crosswalk", "crosswalk_counts")
        self.assertIsNotNone(crosswalk)

    def test_banked_row_prints_always_in_the_crosswalk(self):
        output = _output("R1")
        text = h.render_text(output, "render")
        self.assertIn("Banked", text)
        crosswalk = h.get(output, "crosswalk", "crosswalk_counts")
        rows = crosswalk if isinstance(crosswalk, dict) else {}
        if rows:
            self.assertIn("Banked", rows)
            banked = rows["Banked"]
            if isinstance(banked, dict):
                total = sum(h.int_of(value) for value in banked.values())
            else:
                total = h.int_of(h.get(banked, "total", "count"))
            self.assertGreater(total, 0)

    def test_crosswalk_counts_entries_carrying_the_head_phrasing(self):
        output = _output("R1")
        crosswalk = h.get(output, "crosswalk", "crosswalk_counts")
        if isinstance(crosswalk, dict) and "Banked" in crosswalk:
            banked = crosswalk["Banked"]
            if isinstance(banked, dict):
                counts = {h.text_of(key): h.int_of(value)
                          for key, value in banked.items()}
                decided = sum(counts.get(name, 0) for name in
                              ("Ruled", "Settled", "Settled in part",
                               "Closed as decided", "Conditional"))
                self.assertGreater(decided, 0)
                self.assertEqual(counts.get("Ambiguous", 0), 2)


class DeciderSubtotalsTest(unittest.TestCase):

    def test_subtotals_count_labelled_rows_only(self):
        output = _output("R1")
        subtotals = h.get(output, "decider_subtotals", "decider_counts")
        self.assertIsNotNone(subtotals)
        if isinstance(subtotals, dict):
            counts = {h.text_of(key): h.int_of(value)
                      for key, value in subtotals.items()}
            self.assertIn("Ruled by Captain JP", counts)
            self.assertGreater(counts["Ruled by Captain JP"], 0)
            self.assertIn("settled under DQ-143", counts)
            labelled_total = sum(counts.values())
            counts_all = h.canonical_counts(output)
            decided = sum(counts_all.get(name, 0) for name in
                          ("Ruled", "Settled", "Settled in part",
                           "Closed as decided", "Conditional"))
            self.assertLessEqual(labelled_total, decided)


class WaitingBlockingTest(unittest.TestCase):

    def test_s5_waiting_and_blocking_figures(self):
        output = _output("S5")
        waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 1)
        self.assertEqual(h.int_of(blocking), 1)

    def test_limbo_sentence_data_covers_the_three_classes(self):
        output = _output("R1")
        limbo = h.get(output, "limbo", "limbo_sentence_data",
                      "limbo_data")
        if limbo is None:
            text = h.render_text(output, "render")
            self.assertIn("stand outside both", text)
            return
        conditional = h.get(limbo, "conditional_count", "conditional")
        ambiguous = h.get(limbo, "ambiguous_count", "ambiguous")
        unparsed = h.get(limbo, "unparsed_count", "unparsed")
        self.assertEqual(h.int_of(conditional), 2)
        self.assertEqual(h.int_of(ambiguous), 2)
        self.assertEqual(h.int_of(unparsed), 0)

    def test_effort_coverage_counts_stand_on_an_open_fixture(self):
        output = _output("S5")
        effort = h.get(output, "effort_coverage", "effort_counts")
        if effort is None:
            text = h.render_text(output, "render")
            self.assertIn("not derivable from the file", text)
            return
        with_signal = h.get(effort, "with_effort_signal",
                            "with_signal", "carrying")
        without_signal = h.get(effort, "without_effort_signal",
                               "without_signal", "carrying_none")
        self.assertEqual(h.int_of(with_signal) +
                         h.int_of(without_signal), 1)


class SelfCheckFailureDoubleTest(unittest.TestCase):

    def test_broken_sum_double_takes_the_tool_fault_run_form(self):
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        double = h.self_check_model_double()
        output = h.validate_function(validate_module)(double, vocabulary)
        self.assertEqual(h.exit_code_of(output), 4)
        reasons = " ".join(h.reason_classes_of(output)).lower()
        self.assertIn("inconsist", reasons)
        recon = h.reconciliation_of(output)
        check = h.get(recon, "self_check", "self_check_result")
        if check is None:
            check = h.get(output, "self_check", "self_check_result")
        self.assertIsNotNone(check)
        ok = h.get(check, "ok", "passed", "sums_agree", "agrees")
        if isinstance(check, str):
            self.assertNotIn("agree", check.lower().replace(
                "do not agree", "").replace("not agree", ""))
        else:
            self.assertFalse(bool(ok))
        failed = h.get(check, "failed_components", "failures",
                       "failed")
        self.assertTrue(h.as_list(failed) or
                        h.get(check, "detail", "statement"))

    def test_self_check_failure_render_withholds_the_summary(self):
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        double = h.self_check_model_double()
        output = h.validate_function(validate_module)(double, vocabulary)
        for form in ("validate", "render"):
            with self.subTest(form=form):
                text = h.render_text(output, form)
                self.assertIn("tool fault", text)
                self.assertIn(
                    "do not edit the queue file on the basis of this run",
                    text)
                self.assertNotIn("Census", text.split("tool fault")[0]
                                 if "tool fault" in text else text)


if __name__ == "__main__":
    unittest.main()
