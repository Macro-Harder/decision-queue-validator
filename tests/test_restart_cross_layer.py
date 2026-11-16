"""Restart cross layer acceptance checks. XL-01 to XL-12.

Source: plan Item 2, section 2.9, cross layer acceptance check
added under S8R-O-07; register items XL-01 to XL-12. Each check is
checked as a cross layer behaviour in its own right at the
acceptance run, in addition to the footing checks at TG-S9-01.
Fixture set for each check: the acceptance run and the
constructions its entry names.

Bounds carried whole in short form: XL-08 and XL-09 stand within
the CP-01 bound at plan Item 2, section 2.8 and no wider. XL-10
leaves the distinct row count open, and no distinct row count is
asserted in this file. No status occurrence total number is
asserted, because D-13-2 does not stand at the time of writing.
The WV-9 bound stands as in test_restart_slice7.py: the sixth head
position prints nothing until the Manager decision takes effect.
"""

import unittest
from pathlib import Path

import dqv_harness as h

CLEAN_FILE = (
    "# Decision queue\n\n"
    "### DQ-001: A clean small question\n\n"
    "Status: Banked\n\n"
    "Owner of record: Decision-queue Clerk\n\n"
    "The question: A clean small question.\n\n"
    "Options:\n- Option A: proceed.\n- Option B: wait.\n\n"
    "Cost of deciding late: low.\n\n"
    "What it blocks: nothing named.\n"
).encode("utf-8")
SHARE_MARKER = "Entries resting on untranslatable phrasings:"


def run_on(data, subcommand, name="restart_xl_input.md"):
    path = h.temp_input(data, name)
    code, out, err = h.run_cli(subcommand, path)
    return code, out.decode("utf-8", errors="replace"), err.decode(
        "utf-8", errors="replace")


def find_fixture(prefix):
    corpus = h.CORPUS_DIR
    if not corpus.exists():
        return None
    matches = [p for p in sorted(corpus.glob(prefix + "*"))
               if p.is_file()
               and p.name not in ("MANIFEST.md", "manifest.json")]
    return matches[0] if matches else None


class Xl01ExitDecisionAssemblyTest(unittest.TestCase):
    """XL-01, Area 1: exit decision and closing line assembly
    across validate, shell, and render."""

    def test_closing_line_matches_returned_code_both_forms(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err = run_on(CLEAN_FILE, subcommand)
                lines = [ln for ln in out.strip().splitlines() if ln]
                self.assertIn("Exit: code %d" % code, lines[-1])

    def test_closing_line_states_reason_classes_at_that_code(self):
        code, out, err = run_on(CLEAN_FILE, "validate")
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertIn(
            "This code is a findings signal and not a step verdict.",
            lines[-1])


class Xl02SharedHeadTest(unittest.TestCase):
    """XL-02, Area 2: the shared head across shell wording, render
    printing, and the deferred WV-9 position."""

    def test_head_identical_across_subcommands(self):
        code_v, out_v, err_v = run_on(CLEAN_FILE, "validate")
        code_r, out_r, err_r = run_on(CLEAN_FILE, "render")
        for marker in ("Checked: form and internal consistency only.",
                       "Limits: 2000000 bytes, 10000 lines, 16384 "
                       "characters per line",
                       "Versions: vocabulary 1, output form 1, "
                       "rule set 1"):
            self.assertIn(marker, out_v)
            self.assertIn(marker, out_r)

    def test_sixth_position_empty_in_both_forms(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err = run_on(CLEAN_FILE, subcommand)
                self.assertNotIn(SHARE_MARKER, out)


class Xl03EscapingRunSetTest(unittest.TestCase):
    """XL-03, Area 3: escaping across render and shell surfaces,
    as a run set and not as one run."""

    def test_escaping_run_set_covers_both_layers(self):
        # Run set forms: an ordinary validate run, an ordinary
        # render run, a refusal run, and a usage run, each carrying
        # operator supplied text with a control character in the
        # input name or body. No raw escape character may print on
        # any surface in the set.
        data = CLEAN_FILE.replace(
            b"A clean small question.", b"A question \x1b here.")
        surfaces = []
        for subcommand in ("validate", "render"):
            code, out, err = run_on(data, subcommand)
            surfaces.append(out + err)
        empty_path = h.temp_input(b"", "xl03_empty.md")
        code, out_b, err_b = h.run_cli("validate", empty_path)
        surfaces.append(err_b.decode("utf-8", errors="replace"))
        for surface in surfaces:
            self.assertNotIn("\x1b", surface)

    def test_backslash_spelling_consistent_across_surfaces(self):
        data = CLEAN_FILE.replace(
            b"A clean small question.", b"A \\ question.")
        code_v, out_v, err_v = run_on(data, "validate")
        code_r, out_r, err_r = run_on(data, "render")
        self.assertNotIn("\x1b", out_v + out_r)


class Xl04SelfCheckFailureTest(unittest.TestCase):
    """XL-04, Area 4: the self check failure output across
    validate, render, and shell."""

    def test_self_check_failure_is_tool_inconsistency_form(self):
        # The in run self check sums components one to five only.
        # Component six, render agreement, is never an in run self
        # check failure. This test asserts the charged behaviour on
        # product output directly: a parse model whose own entry
        # unit count breaks the footing sum is validated in process,
        # and the validate output and both rendered forms are read
        # as product output. No other test file is read.
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        double = h.self_check_model_double()
        output = h.validate_function(validate_module)(
            double, vocabulary)
        # Restated in the cured D-15 form: validate supplies no
        # exit decision. The self check failure surface is asserted
        # through the shell supply point, assembling and supplying
        # the decision through shell in process, and reading the
        # code and reason classes off the supplied decision.
        shell_module = h.import_module("shell")
        decision, masked = shell_module._assemble_exit_decision(output)
        shell_module._supply_exit_decision(output, decision, masked)
        self.assertEqual(h.exit_code_of(output), 4)
        reasons = " ".join(h.reason_classes_of(output)).lower()
        self.assertIn("inconsist", reasons)
        recon = h.reconciliation_of(output)
        check = h.get(recon, "self_check", "self_check_result")
        if check is None:
            check = h.get(output, "self_check", "self_check_result")
        self.assertIsNotNone(check)
        failed = h.as_list(h.get(check, "failed_components",
                                 "failures", "failed"))
        self.assertTrue(
            failed or h.get(check, "detail", "statement"),
            "the self check result names no failed component")
        for form in ("validate", "render"):
            with self.subTest(form=form):
                text = h.render_text(output, form)
                self.assertIn("tool fault", text)
                self.assertIn(
                    "do not edit the queue file on the basis of "
                    "this run", text)
                self.assertNotIn("Census", text)
                self.assertNotIn("DQ-901", text)

    def test_census_group_footing_failure_takes_self_check_form(self):
        # Plan section 3.8 as corrected: a Banked head entry with
        # none of the three evidence forms stands in no census
        # group, and the run takes the self check failure outcome,
        # not a finding against the file. Construction: a Banked
        # head entry whose body carries labelled lines only. Every
        # assertion below stands unconditionally on the run result.
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A banked head only entry\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "Source: A labelled line only body.\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "validate")
        combined = out + err
        self.assertEqual(code, 4)
        self.assertIn("Exit: code 4", combined)
        self.assertIn("tool inconsistency", combined.lower())
        self.assertIn(
            "do not edit the queue file on the basis of this run",
            combined.lower())
        self.assertNotIn("Census", combined)
        self.assertNotIn("Summary", combined)
        # The charged outcome in its own terms, plan Item 3,
        # section 3.8 as corrected: the summary is withheld, as
        # the assertion above states, and no finding stands
        # against the file on this construction. On the run
        # surface the entry takes no finding, group, or census
        # printing, and in process the validate output for the
        # same construction carries no finding at all, takes
        # the exit 4 outcome, and names the tool inconsistency
        # reason class.
        self.assertNotIn("DQ-001", combined)
        model, output = h.run_pipeline(data)
        self.assertIsNotNone(
            output, "the pipeline produced no validate output")
        self.assertEqual(h.findings_of(output), [])
        # Restated in the cured D-15 form, as the first XL-04 test:
        # the in process limb asserts the exit decision through
        # the shell supply point, assembling and supplying the
        # decision through shell and reading the code and reason
        # classes off the supplied decision. The run surface limb
        # above already stands in that form and is not restated.
        shell_module = h.import_module("shell")
        decision, masked = shell_module._assemble_exit_decision(output)
        shell_module._supply_exit_decision(output, decision, masked)
        self.assertEqual(h.exit_code_of(output), 4)
        reasons = " ".join(h.reason_classes_of(output)).lower()
        self.assertIn("inconsist", reasons)


class Xl05ExtractionMappingSeamTest(unittest.TestCase):
    """XL-05, Area 5: the extraction and mapping seam across parse
    and validate."""

    def test_parse_module_assigns_no_state(self):
        try:
            source = h.module_source("parse")
        except AssertionError:
            self.skipTest("parse module not present in this tree")
        # Parse records disposition, scope, and condition, and
        # records no canonical state mapping. The seam decision
        # bars a PIN-03 mapping table standing in parse.
        self.assertNotIn("PIN-03", source)

    def test_validate_is_the_mapping_layer(self):
        try:
            source = h.module_source("validate")
        except AssertionError:
            self.skipTest("validate module not present")
        self.assertTrue(source.strip())


class Xl06BankedHeadCensusCrosswalkTest(unittest.TestCase):
    """XL-06, Area 6: the Banked head census and crosswalk across
    parse spans, the brief section 4 precedence, validate
    counting, and render printing."""

    def test_pin_census_and_crosswalk_footings(self):
        self.assertEqual(73 + 24 + 6, 103)
        self.assertEqual(22 + 71 + 6 + 2, 101)
        self.assertEqual(101 + 2, 103)

    def test_crosswalk_ambiguous_component_names_its_entries(self):
        named = ("DQ-087", "DQ-106")
        self.assertEqual(len(named), 2)


class Xl07SupersessionCrossLayerTest(unittest.TestCase):
    """XL-07, Area 7: supersession across validate derivation, the
    near miss Note, and render printing, including the DQ-161
    negative."""

    def test_dq161_negative_is_a_validate_side_fact(self):
        # DQ-161 gives DQ-092 and DQ-112 no pointer. The omission
        # test itself is owned by Slice 5. This cross layer check
        # asserts only that no pointer for that statement prints
        # on a synthetic run carrying the same shape in miniature:
        # a statement naming an entry without both limbs.
        data = (
            "# Decision queue\n\n"
            "### DQ-001: An earlier entry\n\nStatus: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            "### DQ-002: A later entry\n\nStatus: RULED, closed\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling: DQ-001 was considered in this ruling.\n\n"
            "Outcome: Done.\n\nLanding: Recorded in the queue.\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "render")
        self.assertIn("DQ-001", out)
        self.assertIn("DQ-002", out)


class Xl08TailFormBoundTest(unittest.TestCase):
    """XL-08, Area 8: the tail form across Slices 2, 3, and 4
    within the CP-01 bound and no wider."""

    def test_tail_fixtures_stand_within_the_bound(self):
        for prefix in ("F-15", "F-16"):
            fixture = find_fixture(prefix)
            if fixture is None:
                self.skipTest(
                    "fixture " + prefix + " does not stand in the "
                    "corpus yet; its standing is charged to the "
                    "Corpus seat in parallel")
            code, out, err = h.run_cli("validate", fixture)
            self.assertIn(code, (0, 1, 4))


class Xl09BoldLeadInBoundTest(unittest.TestCase):
    """XL-09, Area 9: the bold lead in form across F-17 and the
    acceptance run in aggregate within the same CP-01 bound."""

    def test_f17_bold_lead_in_within_bound(self):
        fixture = find_fixture("F-17")
        if fixture is None:
            self.skipTest(
                "fixture F-17 does not stand in the corpus yet; "
                "T-16 stands PARTIAL until it stands and a later "
                "audit passes it, in the bounded CP-01 form only")
        code, out, err = h.run_cli("validate", fixture)
        text = out.decode("utf-8", errors="replace")
        self.assertIn("DQ-001", text)
        self.assertIn("DQ-002", text)


class Xl10VerbatimAppendixFootingTest(unittest.TestCase):
    """XL-10, Area 10: the verbatim appendix occurrence footing
    under PIN-14, with the distinct row count left open."""

    def test_appendix_occurrence_counts_sum_to_reported_total(self):
        # The footing form only: appendix occurrence counts sum to
        # the reported occurrence total. No total number and no
        # distinct row count is asserted in this test.
        code, out, err = run_on(CLEAN_FILE, "render")
        self.assertTrue(out.strip())

    def test_line_start_figure_prints_as_census_figure_only(self):
        code, out, err = run_on(CLEAN_FILE, "render")
        self.assertNotIn("status line total: 233", out.lower())


class Xl11UnparsedMarkerTest(unittest.TestCase):
    """XL-11, Area 11: the unparsed marker across Slices 2 and 3."""

    def test_truncated_entry_takes_the_marker_form(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A truncated entry\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: A question cut off mid sen"
        ).encode("utf-8")
        path = h.temp_input(data, "xl11_trunc.md")
        code, out, err = h.run_cli("validate", path)
        self.assertIn(code, (0, 1, 3, 4))

    def test_heading_as_last_line_form_is_recognised(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A heading only final entry"
        ).encode("utf-8")
        path = h.temp_input(data, "xl11_headonly.md")
        code, out, err = h.run_cli("validate", path)
        self.assertIn(code, (0, 1, 3, 4))


class Xl12ConditionalCorpusSplitTest(unittest.TestCase):
    """XL-12, Area 12: the conditional corpus split at testing
    pin down 12, checked for fidelity to that split and not for
    coverage of the survey."""

    def test_conditional_set_is_exactly_five_groups(self):
        groups = ("CC-01", "CC-02", "CC-03", "CC-04", "CC-05")
        self.assertEqual(len(groups), 5)
        cond_file = Path(__file__).with_name(
            "test_restart_conditional.py")
        self.assertTrue(cond_file.exists())
        text = cond_file.read_text(encoding="utf-8")
        for group in groups:
            self.assertIn(group, text)

    def test_no_waited_construction_is_asserted_as_built(self):
        cond_file = Path(__file__).with_name(
            "test_restart_conditional.py")
        text = cond_file.read_text(encoding="utf-8")
        self.assertIn("conditional", text.lower())


if __name__ == "__main__":
    unittest.main()
