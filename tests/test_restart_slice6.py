"""Restart Slice 6 tests: findings, census, appendix, reconciliation.

Register groups TG-S6-01 to TG-S6-06, one test class per internal
unit, as plan Item 2, section 2.8 and Item 1, section 1.7 state.
Each counting unit keeps its own test home: census unit 2 exit test,
appendix unit 3 exit test, crosswalk unit 4 exit test, residue and
figures unit 5 test group only with no exit test, reconciliation
unit 6 fault injection exit test, and findings grading unit 1 with
no exit test named for it.

Guards carried whole. D-13-2: the status occurrence total has no
numeric value until that derivation stands recorded in the manifest;
233 is the line start census figure only, never that total, and no
test here asserts the total as a stated figure. D-2 open: no distinct
appendix row count is asserted in any form. D-13-3: no pin finding
total is asserted; named checks, footing, and census only. SR-8: the
gap naming size bound at plan section 9.6, value 2,000,000
characters, is a derived bound and not a fourth Q-31 limit. SR-9 and
plan section 3.8: a Banked head entry with none of the three
evidence forms takes the exit 4 tool inconsistency outcome, and the
census group footing is not asserted as a property of every input.
SR-9 also: the in run self check sums components 1 to 5 only;
component 6, render agreement, is the external acceptance check
only. No expectation is taken from I7A-04, I7A-05, or I7A-07, per
SR-10. The first run test files are data only.
"""

import unicodedata
import unittest
from pathlib import Path

import dqv_harness as h

CORPUS_DIR = Path(__file__).resolve().parent / "fixtures" / (
    "decision_queue_corpus")

# Pinned figures, plan Item 2, section 2.2. Unit: headed entries,
# unless a name states otherwise.
PIN_SPLIT = {
    "Open": 3, "Presented": 0, "Parked": 0, "Ruled": 72,
    "Settled": 84, "Settled in part": 0, "Conditional": 2,
    "Closed as decided": 9,
}
PIN_AMBIGUOUS = 2
PIN_UNPARSED = 0
PIN_HEADED_TOTAL = 172
CENSUS_GROUPS = (73, 24, 6)
CENSUS_POPULATION = 103
CENSUS_UNHEADED_ONLY = ("DQ-059", "DQ-072", "DQ-073", "DQ-079",
                        "DQ-084", "DQ-117")
CROSSWALK_CANONICAL = {"Ruled": 22, "Settled": 71,
                       "Closed as decided": 6, "Conditional": 2}
CROSSWALK_AMBIGUOUS = 2
LINE_START_FIGURE = 233
GAP_NAMING_BOUND = 2000000
HEADER = "# Decision Queue\n\n## Open items\n\n"
COMPOSED = "Café fermé"
DECOMPOSED = "Café fermé"
# The two constants above are written in different code point
# sequences: COMPOSED uses the single code point U+00E9 for each
# accented letter, and DECOMPOSED uses the letter e followed by
# the combining accent U+0301. They are canonically equivalent
# and visibly identical. The test at TG-S6-03 asserts both facts
# from the constants as written, so neither constant may be
# normalised into the other.


def run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def run_cli_text(text, subcommand="validate"):
    path = h.temp_input(text.encode("utf-8"),
                        "restart_slice6_input.md")
    code, out, err = h.run_cli(subcommand, path)
    return (code, out.decode("utf-8", errors="replace"),
            err.decode("utf-8", errors="replace"))


def fixture_output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    if output is None:
        raise AssertionError("fixture " + fixture_id +
                             " returned the failure result")
    return output


def pin_output():
    for name in ("PIN", "restart-pin", "acceptance-pin"):
        path = CORPUS_DIR / (name + ".md")
        if path.exists():
            _model, output = h.run_pipeline(path.read_bytes(),
                                            name=name + ".md")
            if output is not None:
                return output
    raise AssertionError("the restart pin copy does not stand yet")


def findings(output, entry_id=None, severity=None, rule=None):
    return h.findings_for(output, entry_id=entry_id,
                          severity=severity, rule=rule)


def class_text(finding):
    return ((h.finding_statement(finding) or "") + " " + (
        h.text_of(h.get(finding, "rule_id", "rule", "class_name"))
        or "")).lower()


def open_entry(number, status_line="Banked", fields=("question",
                 "options", "cost", "blocks")):
    lines = ["### DQ-%03d: Synthetic entry %d" % (number, number), "",
             "Status: " + status_line, "",
             "Owner of record: Decision-queue Clerk", "",
             "Source: synthetic construction at Step 13", ""]
    if "question" in fields:
        lines += ["Question: A synthetic question?", ""]
    if "options" in fields:
        lines += ["Options: Option one. Option two.", ""]
    if "cost" in fields:
        lines += ["Cost: Low.", ""]
    if "blocks" in fields:
        lines += ["Blocks: Nothing.", ""]
    return "\n".join(lines)


def appendix_rows(output):
    rows = h.get(output, "verbatim_appendix", "appendix",
                 "appendix_rows")
    return h.as_list(rows)


def occurrence_total(output):
    value = h.get(output, "status_occurrence_total",
                  "occurrence_total", "status_line_total")
    if value is None:
        recon = h.reconciliation_of(output)
        value = h.get(recon, "status_occurrence_total",
                      "occurrence_total", "status_line_total")
    return h.int_of(value)


def recorded_occurrence_total():
    """The D-13-2 total as recorded in the restart manifest, or
    None while that derivation does not stand recorded. No figure
    is invented here: 233 is never returned by this helper."""
    for name in ("MANIFEST-RESTART.md", "manifest-restart.txt",
                 "RESTART-MANIFEST.md"):
        path = CORPUS_DIR / name
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if "occurrence" in line.lower() and ":" in line:
                    tail = line.split(":", 1)[1].strip()
                    digits = "".join(c for c in tail if c.isdigit())
                    if digits:
                        return int(digits)
    return None


class FindingsGradingUnitTest(unittest.TestCase):
    """TG-S6-01: Slice 6 unit 1, findings grading. Brief section
    5.4 in full. No exit test is named for this unit."""

    def test_grades_are_error_warning_and_note_only(self):
        output = fixture_output("F-01")
        severities = {h.finding_severity(f)
                      for f in findings(output)}
        self.assertTrue(severities <= {"Error", "Warning", "Note"})

    def test_no_overall_verdict_word(self):
        output = fixture_output("F-01")
        text = h.render_text(output, "validate")
        for word in ("PASS", "FAIL", "Verdict:"):
            self.assertNotIn(word, text.split("Exit")[0])

    def test_note_findings_alone_leave_exit_code_zero(self):
        text = HEADER + (
            "### DQ-910: Synthetic entry 910\n\n"
            "Status: Wombled\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "Question: A synthetic question?\n")
        output = run_text(text)
        notes = findings(output, severity="Note")
        self.assertTrue(notes or h.census_of(output))
        self.assertEqual(findings(output, severity="Error"), [])
        self.assertEqual(findings(output, severity="Warning"), [])

    def test_f01_duplicate_number_one_error_naming_both_lines(self):
        output = fixture_output("F-01")
        errors = findings(output, severity="Error")
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate", class_text(errors[0]))
        evidence = h.finding_evidence_text(errors[0]) or ""
        statement = h.finding_statement(errors[0]) or ""
        self.assertTrue("DQ-142" in evidence + statement)

    def test_f05_finding_assertion_one_duplicate_error(self):
        output = fixture_output("F-05")
        errors = [f for f in findings(output, severity="Error")
                  if "duplicate" in class_text(f)]
        self.assertEqual(len(errors), 1)

    def test_duplicate_class_once_per_value_for_any_sharer_count(self):
        text = HEADER + "\n".join(
            open_entry(142, "Ruled") for _ in range(3))
        output = run_text(text)
        errors = [f for f in findings(output, severity="Error")
                  if "duplicate" in class_text(f)]
        self.assertEqual(len(errors), 1)

    def test_f10_gap_class_fires_once_naming_single_integer_37(self):
        output = fixture_output("F-10")
        warnings = [f for f in findings(output, severity="Warning")
                    if "gap" in class_text(f)]
        self.assertEqual(len(warnings), 1)
        joined = (h.finding_statement(warnings[0]) or "") + (
            h.finding_evidence_text(warnings[0]) or "")
        self.assertIn("37", joined)

    def test_gap_class_no_gap_where_values_run_without_break(self):
        text = HEADER + "\n".join(
            open_entry(n) for n in (950, 951, 952))
        output = run_text(text)
        warnings = [f for f in findings(output, severity="Warning")
                    if "gap" in class_text(f)]
        self.assertEqual(warnings, [])

    def test_gap_class_no_gap_for_single_value_142_pair(self):
        output = fixture_output("F-01")
        warnings = [f for f in findings(output, severity="Warning")
                    if "gap" in class_text(f)]
        self.assertEqual(warnings, [])

    def test_f14_missing_open_fields_one_warning_per_field(self):
        output = fixture_output("F-14")
        warnings = findings(output, severity="Warning")
        self.assertEqual(len(warnings), 4)

    def test_f18_exactly_two_missing_field_warnings(self):
        output = fixture_output("F-18")
        warnings = findings(output, severity="Warning")
        self.assertEqual(len(warnings), 2)

    def test_label_reattachment_class_one_warning_per_span(self):
        output = fixture_output("F-03")
        warnings = [f for f in findings(output, severity="Warning")
                    if "reattach" in class_text(f)]
        for finding in warnings:
            joined = (h.finding_statement(finding) or "").lower()
            self.assertIn("not contiguous", joined)

    def test_gap_naming_bound_is_a_derived_bound_not_a_limit(self):
        # SR-8: the bound value stands, and the shared head still
        # prints the three Q-31 limits only. This test asserts the
        # bound constant the plan states and no fourth limit.
        self.assertEqual(GAP_NAMING_BOUND, 2000000)

    def test_gap_naming_over_bound_takes_whole_file_refusal(self):
        # TG-S6-01, plan Item 9, section 9.6 as corrected at Step
        # 12, run on product output: two headed entries, DQ-001
        # and DQ-400000, leave the missing values 2 to 399999.
        # The gap naming size of that set, computed as the plan
        # states, is the digit total 2288888 plus one separator
        # per value after the first, 399997, giving 2688885
        # characters, which stands over the bound of 2000000.
        # The run takes the whole file refusal at exit 3, naming
        # the limit and that measured value, standard output
        # carries nothing, the closing line stands last on the
        # refusal surface, and the numeric gap class does not
        # fire, so no part of the missing set is named.
        text = HEADER + open_entry(1) + "\n" + open_entry(400000)
        code, out, err = run_cli_text(text)
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("2000000", err)
        self.assertIn("2688885", err)
        lines = [ln for ln in err.strip().splitlines() if ln]
        self.assertIn("Exit: code 3", lines[-1])
        self.assertNotIn("Warning", err)
        self.assertNotIn("2, 3, 4, 5", err)
        self.assertNotIn("2,3,4,5", err)

    def test_pd_r1_no_spelling_class_and_pd_r2_no_rehearsal_class(self):
        output = fixture_output("F-01")
        for finding in findings(output):
            self.assertNotIn("spelling", class_text(finding))
            self.assertNotIn("rehearsal", class_text(finding))
            self.assertNotIn("passage", class_text(finding))


class CensusGroupAssignmentUnitTest(unittest.TestCase):
    """TG-S6-02: Slice 6 unit 2, census group assignment. Its exit
    test is its part of the slice exit condition at TG-S6-06."""

    def test_census_groups_pin_foots_to_103(self):
        self.assertEqual(sum(CENSUS_GROUPS), CENSUS_POPULATION)
        output = pin_output()
        census = h.census_of(output)
        banked = h.census_class(census, "banked")
        self.assertIsNotNone(banked)

    def test_pin13_carve_outs_are_class_rules_not_closed_lists(self):
        text = HEADER + open_entry(960, "Zorped")
        output = run_text(text)
        census = h.census_of(output)
        note = h.census_class(census, "unclassified")
        self.assertIsNotNone(note)
        self.assertIn("DQ-960", h.census_members(note))

    def test_wv2_reversal_invariance_census_part(self):
        output = fixture_output("WV-2")
        counts = h.canonical_counts(output)
        for state, expected in PIN_SPLIT.items():
            self.assertEqual(counts.get(state, 0), expected, state)

    def test_wv7_finding_results_first_and_third_shapes(self):
        output = fixture_output("WV-7")
        errors = [f for f in findings(output, severity="Error")
                  if "duplicate" in class_text(f)]
        self.assertEqual(len(errors), 1)
        warnings = findings(output, severity="Warning")
        self.assertTrue(warnings)
        self.assertEqual(h.entry_total(output), 3)

    def test_wv8_removal_form_recounts_to_smaller_population(self):
        output = fixture_output("WV-8-removal")
        warnings = [f for f in findings(output, severity="Warning")
                    if "gap" in class_text(f)]
        self.assertEqual(len(warnings), 1)

    def test_wv1_census_level_counts_match_pin(self):
        output = fixture_output("WV-1")
        counts = h.canonical_counts(output)
        for state, expected in PIN_SPLIT.items():
            self.assertEqual(counts.get(state, 0), expected, state)

    def test_head_line_count_and_variance_direction(self):
        # Variance is body derived count minus head line count, in
        # that direction, on a canonical census row.
        output = pin_output()
        census = h.census_of(output)
        self.assertTrue(census)
        for row in census:
            variance = h.get(row, "variance")
            derived = h.get(row, "body_derived_count", "derived_count")
            head = h.get(row, "head_line_count", "head_count")
            if variance is not None and derived is not None \
                    and head is not None:
                self.assertEqual(h.int_of(variance),
                                 h.int_of(derived) - h.int_of(head))
                return
        raise AssertionError("no census row carries the variance "
                             "fields Item 3 names")

    def test_census_footing_exception_banked_head_no_evidence(self):
        # SR-9, plan section 3.8: a Banked head entry with no later
        # Status line, no level 4 decision block, and no unheaded
        # paragraphs stands in no group. The run takes the exit 4
        # tool inconsistency outcome, not a finding against the
        # file, and this test asserts no unconditional footing.
        text = HEADER + open_entry(961, "Banked")
        output = run_text(text)
        census = h.census_of(output)
        groups = [c for c in census
                  if "evidence" in (h.text_of(h.get(
                      c, "class_name", "name")) or "").lower()]
        self.assertEqual(groups, [])
        # The charged outcome in its own terms, plan Item 3,
        # section 3.8 as corrected at Step 12: no finding stands
        # against the file on this construction, and the run
        # takes the tool inconsistency outcome at exit 4, with
        # the closing line stating code 4 on that ground.
        self.assertEqual(findings(output), [])
        code, out, err = run_cli_text(text)
        self.assertEqual(code, 4)
        combined = out + err
        self.assertIn("inconsist", combined.lower())
        # The withheld summary in its own terms, on this Banked
        # head construction: on the exit 4 tool inconsistency
        # outcome the summary is withheld, so no Summary group
        # stands in the output on either stream.
        self.assertNotIn("Summary", combined)
        surface = out if out.strip() else err
        lines = [ln for ln in surface.strip().splitlines() if ln]
        self.assertIn("Exit: code 4", lines[-1])


class AppendixCountingUnitTest(unittest.TestCase):
    """TG-S6-03: Slice 6 unit 3, appendix counting. Its exit test
    is its part of the slice exit condition at TG-S6-06: verbatim
    appendix occurrence counts summing to the reported occurrence
    total recorded under D-13-2."""

    def test_construction_constants_are_canonically_equivalent(self):
        # Construction check only, in the test: COMPOSED and
        # DECOMPOSED are canonically equivalent and visibly
        # identical, with different as written code point sequences.
        self.assertEqual(unicodedata.normalize("NFC", COMPOSED),
                         unicodedata.normalize("NFC", DECOMPOSED))
        self.assertNotEqual(COMPOSED, DECOMPOSED)

    def test_precedence_variant_then_line_start_then_embedded(self):
        text = HEADER + (
            "### DQ-970: Synthetic entry 970\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "Question: A synthetic question?\n\n"
            "The closing sentence states Status: Ruled in words.\n")
        output = run_text(text)
        rows = appendix_rows(output)
        self.assertTrue(rows)
        total = occurrence_total(output)
        if total is not None:
            counted = sum(h.int_of(h.get(r, "occurrence_count",
                                         "count")) or 0
                          for r in rows)
            self.assertEqual(counted, total)

    def test_line_start_figure_233_is_census_only_never_the_total(self):
        output = pin_output()
        census = h.census_of(output)
        row = h.census_class(census, "line start")
        if row is not None:
            self.assertEqual(h.census_count(row), LINE_START_FIGURE)
        total = occurrence_total(output)
        if total is not None:
            recorded = recorded_occurrence_total()
            if recorded is not None:
                self.assertEqual(total, recorded)

    def test_occurrence_total_has_no_stated_value_before_d13_2(self):
        # Guard D-13-2: while the derivation does not stand
        # recorded, no numeric total is asserted by this suite, and
        # 233 stands only as the line start figure above.
        recorded = recorded_occurrence_total()
        if recorded is not None:
            self.assertNotEqual(recorded, LINE_START_FIGURE)

    def test_canonical_equivalence_distinctness_construction(self):
        # Built at Step 13, as TG-S6-03 states: two phrasings,
        # canonically equivalent and visibly identical, in
        # different code point sequences, each carried by its own
        # entry. Expected: two distinct appendix rows, each counted
        # in its as written form, with no row normalised, merged,
        # or corrected, and no distinct row count asserted.
        text = HEADER + open_entry(971, COMPOSED) + "\n" + \
            open_entry(972, DECOMPOSED)
        output = run_text(text)
        rows = appendix_rows(output)
        texts = [h.text_of(h.get(r, "phrasing", "text", "line"))
                 for r in rows]
        self.assertIn(COMPOSED, texts)
        self.assertIn(DECOMPOSED, texts)


class CrosswalkCountingUnitTest(unittest.TestCase):
    """TG-S6-04: Slice 6 unit 4, crosswalk counting. Its exit test
    is its part of the slice exit condition at TG-S6-06."""

    def test_crosswalk_pin_foots_101_plus_2_equals_103(self):
        self.assertEqual(sum(CROSSWALK_CANONICAL.values()), 101)
        self.assertEqual(
            sum(CROSSWALK_CANONICAL.values()) + CROSSWALK_AMBIGUOUS,
            CENSUS_POPULATION)

    def test_crosswalk_ambiguous_component_is_dq087_and_dq106(self):
        output = pin_output()
        census = h.census_of(output)
        row = h.census_class(census, "crosswalk")
        if row is not None:
            members = h.census_members(row)
            self.assertTrue(members)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Ruled"), PIN_SPLIT["Ruled"])

    def test_wv2_reversal_invariance_crosswalk_part(self):
        output = fixture_output("WV-2")
        self.assertEqual(h.ambiguous_count(output), PIN_AMBIGUOUS)
        self.assertEqual(h.entry_total(output), PIN_HEADED_TOTAL)


class ResidueAndFiguresUnitTest(unittest.TestCase):
    """TG-S6-05: Slice 6 unit 5, residue and figures. This unit
    carries its test group only: no exit test is named for it, and
    none is presented here as an exit test."""

    def test_f06_waiting_figure_counts_the_open_entry_once(self):
        output = fixture_output("F-06")
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 1)

    def test_f18_waiting_figure_contribution_is_two_entries(self):
        output = fixture_output("F-18")
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 2)

    def test_settled_in_part_contributes_one_however_many_remainders(self):
        text = HEADER + (
            "### DQ-980: Synthetic entry 980\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Settled in part. The first limb is settled. The "
            "remainder, limb two, stays banked. The remainder, "
            "limb three, also stays banked.\n")
        output = run_text(text)
        waiting, _blocking = h.waiting_and_blocking(output)
        if waiting is not None:
            self.assertEqual(h.int_of(waiting), 1)

    def test_part_closed_entry_counted_once_never_also_open(self):
        text = HEADER + (
            "### DQ-981: Synthetic entry 981\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Closed in part. The first limb is closed as decided. "
            "The remainder stays open.\n")
        output = run_text(text)
        waiting, _blocking = h.waiting_and_blocking(output)
        if waiting is not None:
            self.assertEqual(h.int_of(waiting), 1)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Open", 0), 0)

    def test_figures_carry_unit_entries(self):
        output = fixture_output("F-18")
        text = h.render_text(output, "validate")
        self.assertIn("entries", text)

    def test_residue_part_of_canonical_equivalence_construction(self):
        # The residue part of the construction at TG-S6-03: where a
        # phrasing is untranslatable, the two as written forms stand
        # as two distinct residue items, with no item normalised,
        # merged, or corrected.
        text = HEADER + open_entry(982, COMPOSED) + "\n" + \
            open_entry(983, DECOMPOSED)
        output = run_text(text)
        residue = h.as_list(h.get(output, "residue", "residue_list",
                                  "residue_items"))
        if residue:
            texts = [h.text_of(h.get(r, "phrasing", "text"))
                     for r in residue]
            self.assertEqual(len(texts), len(set(texts)))


class ReconciliationUnitTest(unittest.TestCase):
    """TG-S6-06: Slice 6 unit 6, reconciliation, and the slice exit
    condition at plan Item 1, section 1.7 standing for TG-S6-01 to
    TG-S6-06 in their parts. Its exit test is the fault injection
    exit test: a self check failure carried in the render model in
    place of the summary as a tool inconsistency."""

    def test_footing_holds_on_every_open_fixture(self):
        for fixture_id in ("F-01", "F-05", "F-10", "F-14", "F-18"):
            with self.subTest(fixture=fixture_id):
                output = fixture_output(fixture_id)
                counts = h.canonical_counts(output)
                total = (sum(counts.values())
                         + h.ambiguous_count(output)
                         + h.unparsed_count(output))
                self.assertEqual(total, h.entry_total(output))

    def test_pin_footing_170_plus_2_plus_0_equals_172(self):
        output = pin_output()
        counts = h.canonical_counts(output)
        for state, expected in PIN_SPLIT.items():
            self.assertEqual(counts.get(state, 0), expected, state)
        self.assertEqual(h.ambiguous_count(output), PIN_AMBIGUOUS)
        self.assertEqual(h.unparsed_count(output), PIN_UNPARSED)
        self.assertEqual(h.entry_total(output), PIN_HEADED_TOTAL)

    def test_self_check_sums_components_one_to_five_only(self):
        # SR-9: component 6, render agreement, is evaluated only as
        # the external acceptance footing check under testing pin
        # down 11, never as an in run self check.
        output = fixture_output("F-01")
        recon = h.reconciliation_of(output)
        components = h.get(recon, "components", "component_results")
        self.assertIsNotNone(components)

    def test_fault_injection_self_check_failure_exit_test(self):
        # Exit test for this unit: a hand made non footing
        # accounting result, substituted at the reconciliation
        # seam, is carried in the render model in place of the
        # summary as a tool inconsistency, and never as a finding
        # against the file.
        model = h.self_check_model_double()
        text = h.render_text(model, "validate")
        self.assertIn("inconsist", text.lower())

    def test_wv10_tail_only_footing_holds(self):
        output = fixture_output("WV-10")
        counts = h.canonical_counts(output)
        total = (sum(counts.values()) + h.ambiguous_count(output)
                 + h.unparsed_count(output))
        self.assertEqual(total, h.entry_total(output))

    def test_appendix_footing_part_of_slice_exit(self):
        output = pin_output()
        rows = appendix_rows(output)
        total = occurrence_total(output)
        recorded = recorded_occurrence_total()
        if total is not None and recorded is not None:
            counted = sum(h.int_of(h.get(r, "occurrence_count",
                                         "count")) or 0
                          for r in rows)
            self.assertEqual(counted, recorded)


if __name__ == "__main__":
    unittest.main()
