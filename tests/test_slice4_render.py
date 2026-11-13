"""Slice 4, render group.

Both output forms from the Validate output only: the shared head and
its file facts forms, the banner at its ruled placement, the render
section order, the findings form with its index and rule list, the
groups and the docket, the counts section with its glossary, the
verbatim appendix, the Project Manager figures, absence shown as
absence, and the foot and closing lines. No output carries a verdict
word for the file or language inviting gate use.
"""

import re
import unittest

import dqv_harness as h


def _cli(fixture_id, subcommand):
    code, out, _err = h.cached_run(fixture_id, subcommand)
    return code, out.decode("utf-8", errors="replace")


def _validate_text(fixture_id):
    _code, text = _cli(fixture_id, "validate")
    return text


def _render_text(fixture_id):
    _code, text = _cli(fixture_id, "render")
    return text


class SharedHeadTest(unittest.TestCase):

    def test_head_carries_scope_limits_vocabulary_edition_and_facts(self):
        text = _validate_text("S5")
        self.assertIn("form and internal consistency", text)
        self.assertIn("may not be cited as a pass or fail condition",
                      text)
        self.assertIn("2,000,000", text.replace("2000000", "2,000,000"))
        self.assertIn("16,384", text.replace("16384", "16,384"))
        self.assertIn("S5.md", text)
        self.assertIn("vocabulary", text.lower())
        digest_fragment = h.sha256_hex(h.fixture_bytes("S5"))[:12]
        self.assertIn(digest_fragment, text)

    def test_both_subcommand_heads_share_the_file_facts_line(self):
        validate_text = _validate_text("R5")
        render_text = _render_text("R5")
        digest_fragment = h.sha256_hex(h.fixture_bytes("R5"))[:12]
        self.assertIn(digest_fragment, validate_text)
        self.assertIn(digest_fragment, render_text)

    def test_no_verdict_word_or_gate_language_in_any_output(self):
        banned = ("verdict: pass", "verdict: fail", "the queue is valid",
                  "the queue is invalid", "gate approved", "approved for "
                  "release")
        for fixture_id in ("R1", "S5", "S13", "S4"):
            for subcommand in ("validate", "render"):
                with self.subTest(fixture=fixture_id,
                                  subcommand=subcommand):
                    _code, text = _cli(fixture_id, subcommand)
                    lowered = text.lower()
                    for phrase in banned:
                        self.assertNotIn(phrase, lowered)


class BannerPlacementTest(unittest.TestCase):

    def test_r1_banner_present_in_both_outputs_under_the_head(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                _code, text = _cli("R1", subcommand)
                lowered = text.lower()
                # The banner stands under the shared head, after the
                # file facts line that names the input, and before
                # every later section: the CA-3 placement of brief
                # section 5.5, directly under the scope head.
                head_at = text.find("R1.md")
                self.assertGreaterEqual(head_at, 0)
                banner_at = lowered.find("reported under that "
                                         "condition")
                self.assertGreater(banner_at, head_at)
                census_at = lowered.find("census")
                self.assertGreater(census_at, banner_at)
                under_head = text[head_at:census_at]
                self.assertIn("Ambiguous", under_head)
                self.assertIn("Conditional", under_head)
                self.assertIn("totals", under_head.lower())

    def test_s5_banner_absent_in_both_outputs(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                _code, text = _cli("S5", subcommand)
                self.assertNotIn("reported under that condition", text)
                self.assertNotIn("governing uncertainty", text.lower())

    def test_s13_banner_present_with_a_pin9_cause_beside_pin12(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                _code, text = _cli("S13", subcommand)
                self.assertIn("Ambiguous", text)

    def test_s7c_unparsed_only_run_carries_no_banner(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                _code, text = _cli("S7c", subcommand)
                self.assertNotIn("reported under that condition", text)


class RenderOrderTest(unittest.TestCase):

    def test_r1_render_section_order(self):
        text = _render_text("R1")
        markers = [
            "this summary is not a presentation list",
            "different units",
            "Reconciliation",
            "Census",
            "Ambiguous",
            "Counts",
            "appendix",
            "stand outside both",
            "exit 4",
        ]
        # Each marker is searched for from the end of the section
        # before it, so a marker names the section this order claims
        # and not an earlier mention of the same word: the first
        # Ambiguous in the output stands in the banner and in the
        # presentation set statement, before the reconciliation
        # block, and does not identify the open groups position.
        positions = []
        start = 0
        for marker in markers:
            position = text.find(marker, start)
            if position < 0:
                position = text.lower().find(marker.lower(), start)
            self.assertGreaterEqual(position, 0, marker)
            positions.append(position)
            start = position + len(marker)
        self.assertEqual(positions, sorted(positions))

    def test_r1_render_closing_line_names_warnings_with_counts(self):
        text = _render_text("R1")
        last_lines = [line for line in text.strip().splitlines() if line]
        self.assertTrue(last_lines)
        closing = last_lines[-1]
        self.assertIn("4", closing)
        self.assertIn("Warning", closing)
        self.assertIn("3", closing)

    def test_r1_ambiguous_group_carries_sub_label_marker_and_elements(self):
        text = _render_text("R1")
        self.assertIn("Conflict", text)
        self.assertIn("no action available to the reader", text)
        self.assertIn("awaiting ruling on BQ-2", text)
        self.assertIn("DQ-087", text)
        self.assertIn("DQ-106", text)


class ValidateOutputFormTest(unittest.TestCase):

    def test_findings_carry_their_full_shape(self):
        _model, output = h.cached_pipeline("S4")
        findings = h.findings_of(output)
        self.assertEqual(len(findings), 4)
        for finding in findings:
            self.assertIsNotNone(h.finding_rule_number(finding))
            self.assertIsNotNone(h.finding_severity(finding))
            self.assertIsNotNone(h.finding_entry_id(finding))
            start, _end = h.span_of(finding)
            self.assertGreaterEqual(start, 0)
            self.assertTrue(h.finding_statement(finding))
            basis = h.get(finding, "basis")
            self.assertIsNotNone(basis)

    def test_index_precedes_findings_and_carries_per_entry_lines_only(self):
        text = _validate_text("R1")
        lowered = text.lower()
        index_at = lowered.find("index")
        self.assertGreaterEqual(index_at, 0)
        # The findings list itself opens with the OP-Q16 form only
        # reminder at its head, so the index stands before that line.
        findings_head_at = lowered.find(
            "form and internal consistency only")
        self.assertGreater(findings_head_at, index_at)
        index_section = text[index_at:findings_head_at]
        index_lines = [line for line in index_section.splitlines()
                       if line.strip()]
        # The index carries lines: at least one index line names a
        # per entry finding by its entry identifier, and no index
        # line is a FILE line, the index being per entry only under
        # OP-Q2 and OQ-7.
        self.assertTrue(any("DQ-" in line for line in index_lines))
        self.assertFalse(any(line.strip().startswith("FILE")
                             for line in index_lines))

    def test_terminal_order_rule_list_then_census_then_closing(self):
        text = _validate_text("R1")
        lowered = text.lower()
        census_at = lowered.rfind("census")
        closing_at = lowered.rfind("exit 4")
        self.assertGreater(census_at, 0)
        self.assertGreater(closing_at, census_at)

    def test_form_only_reminder_stands_at_the_findings_head(self):
        text = _validate_text("S4")
        self.assertIn("form and internal consistency only", text)

    def test_rule_list_orders_rules_ascending(self):
        # The OP-Q3 rule list order is read, never sorted into
        # existence by the test: the numbers are taken in the order
        # the clearing forms stand in the Validate output and in the
        # order they print in the validate text, and both orders
        # must already be ascending and must name exactly the rules
        # that fired on R1, from the manifest per rule totals.
        _model, output = h.cached_pipeline("R1")
        forms = h.get(output, "per_rule_clearing_forms", "clearing_forms",
                      "rule_list")
        self.assertIsNotNone(forms)
        if isinstance(forms, dict):
            keys = list(forms)
        else:
            keys = h.as_list(forms)
        numbers = []
        for key in keys:
            if isinstance(key, dict):
                numbers.append(h.finding_rule_number(key))
            else:
                numbers.append(
                    h.finding_rule_number({"rule_id": key}))
        self.assertTrue(numbers)
        self.assertEqual(numbers, sorted(numbers))
        per_rule = h.manifest()["corpus_structure_splits"][
            "finding_totals"]["R1"]["per_rule"]
        expected = sorted(int(name.split()[1])
                          for name, grades in per_rule.items()
                          if grades)
        self.assertEqual(numbers, expected)
        text = _validate_text("R1")
        lowered = text.lower()
        list_at = lowered.find("rule list")
        self.assertGreaterEqual(list_at, 0)
        census_at = lowered.find("census", list_at)
        self.assertGreater(census_at, list_at)
        section = text[list_at:census_at]
        printed = [int(match) for match in
                   re.findall(r"check\s+(\d+)", section.lower())]
        self.assertEqual(printed, expected)

    def test_file_finding_is_citable_with_the_file_identifier(self):
        # The assertion is unconditional: it stands on a run that
        # carries a FILE finding by construction, the generated
        # unmatched heading case, whose one FILE finding keys at
        # rule 5 under amendment 3 beside OQ-7, instead of passing
        # without asserting anything on a run that carries none.
        data, _facts = h.unmatched_heading_input("h5")
        _model, output = h.run_pipeline(data, "unmatched.md")
        warnings = [finding for finding in h.findings_of(output)
                    if h.finding_entry_id(finding) == "FILE"]
        self.assertEqual(len(warnings), 1)
        finding = warnings[0]
        citation = (h.finding_entry_id(finding),
                    h.finding_rule_number(finding),
                    h.span_of(finding))
        self.assertEqual(citation[0], "FILE")
        self.assertEqual(citation[1], 5)
        self.assertGreaterEqual(citation[2][0], 0)

    def test_index_carries_no_file_finding_line(self):
        # Only the index section is scanned: OQ-7 bounds FILE
        # findings out of the index only, and a FILE group line in
        # the full findings list after it is no failure of this
        # test. The index section runs from its head to the head of
        # the findings list, marked by the OP-Q16 reminder line.
        text = _validate_text("R1")
        lowered = text.lower()
        index_at = lowered.find("index")
        self.assertGreaterEqual(index_at, 0)
        findings_head_at = lowered.find(
            "form and internal consistency only", index_at)
        self.assertGreater(findings_head_at, index_at)
        index_lines = text[index_at:findings_head_at].splitlines()
        file_lines = [line for line in index_lines
                      if line.strip().startswith("FILE")]
        self.assertEqual(file_lines, [])


class GroupsAndDocketTest(unittest.TestCase):

    def test_open_items_stand_before_decided_groups(self):
        # Fixture S8 carries one entry of each kind, which S14
        # cannot show, both of its entries being Open: DQ-902 is
        # Open and DQ-901 is Ruled by its reattached addition. The
        # group rows carry the entry titles, which stand nowhere
        # before the groups, so the title order is the group order.
        text = _render_text("S8")
        open_at = text.find("A neighbouring open question")
        decided_at = text.find("A question closed by a later "
                               "addition")
        self.assertGreaterEqual(open_at, 0)
        self.assertGreaterEqual(decided_at, 0)
        self.assertLess(open_at, decided_at)

    def test_docket_covers_the_ambiguous_entries_of_r1(self):
        text = _render_text("R1")
        lowered = text.lower()
        self.assertIn("docket", lowered)
        docket_at = lowered.find("docket")
        tail = text[docket_at:]
        self.assertIn("DQ-087", tail)
        self.assertIn("DQ-106", tail)

    def test_decided_rows_carry_status_and_determining_element(self):
        text = _render_text("R3")
        self.assertIn("Settled", text)
        self.assertIn("settled under DQ-143", text)

    def test_s12_row_carries_label_and_remainder_verbatim(self):
        text = _render_text("S12")
        self.assertIn("Ruled by Captain JP", text)
        self.assertIn("the estate default anchor set stays banked",
                      text)
        self.assertIn("Settled in part", text)


class CountsAndFiguresTest(unittest.TestCase):

    def test_counts_section_carries_the_glossary_line_set(self):
        text = _render_text("R1")
        lowered = text.lower()
        self.assertIn("canonical", lowered)
        self.assertIn("phrasing", lowered)
        self.assertIn("headed", lowered)

    def test_appendix_carries_its_units_line_and_kind_markers(self):
        text = _render_text("R1")
        self.assertIn("rows count Status occurrences as written", text)
        self.assertIn("line start", text)
        self.assertIn("embedded", text)
        self.assertIn("variant", text)

    def test_appendix_marks_unclassified_phrasings_on_s3b(self):
        text = _render_text("S3b")
        self.assertIn("Deferred", text)
        self.assertIn("unclassified", text.lower())

    def test_project_manager_figures_carry_formula_rule_line_and_limbo(self):
        text = _render_text("R1")
        self.assertIn("effective Open entries plus Settled in part "
                      "remainders", text)
        self.assertIn("these figures measure the queue and its "
                      "questions; they are not a measure of any person",
                      text)
        self.assertIn("stand outside both", text)
        self.assertIn("not derivable from the file", text)

    def test_blocking_list_gathers_the_s5_blocking_entry(self):
        text = _render_text("S5")
        self.assertIn("DQ-001", text)
        self.assertIn("the Step 13 manifest act", text)

    def test_absence_shows_as_absence(self):
        text = _render_text("R1")
        self.assertIn("no date recorded", text)

    def test_ordering_reason_prints_verbatim_under_its_claim_label(self):
        text = _render_text("S5")
        self.assertIn("it blocks the current step, so it sits early",
                      text)


class RenderModulePurityTest(unittest.TestCase):

    def test_render_module_is_pure(self):
        banned = ("open(", "print(", "input(", "os.environ", "getenv",
                  "socket", "urllib", "requests", "random.", "time.time",
                  "datetime.now", "date.today")
        source = h.module_source("render")
        for token in banned:
            self.assertNotIn(token, source, "render uses " + token)


class FootAndClosingTest(unittest.TestCase):

    def test_each_output_ends_with_a_closing_exit_line(self):
        for fixture_id, expected in (("S5", "0"), ("S1", "1"),
                                     ("R1", "4")):
            for subcommand in ("validate", "render"):
                with self.subTest(fixture=fixture_id,
                                  subcommand=subcommand):
                    _code, text = _cli(fixture_id, subcommand)
                    lines = [line for line in text.strip().splitlines()
                             if line]
                    self.assertTrue(lines)
                    self.assertIn("exit " + expected, lines[-1])
                    self.assertIn("not a step verdict", lines[-1])

    def test_penultimate_line_names_the_other_subcommand(self):
        for subcommand, other in (("validate", "render"),
                                  ("render", "validate")):
            with self.subTest(subcommand=subcommand):
                _code, text = _cli("S5", subcommand)
                lines = [line for line in text.strip().splitlines()
                         if line]
                self.assertGreaterEqual(len(lines), 2)
                self.assertIn(other, lines[-2])


if __name__ == "__main__":
    unittest.main()
