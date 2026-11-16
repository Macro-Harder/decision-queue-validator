"""Restart Step 15 fix wave 1, Seat C tests.

Source: the plan (design/DESIGN-PLAN-RESTART.md) Item 3, sections
3.6 to 3.9 and Item 9, sections 9.5 to 9.9, and the brief OP-Q2,
OP-Q3, and OP-Q7, against the differing forms recorded at
design/steps/step-15r-audit1-3.md and
design/steps/step-14r-lead-engineer-shape-review.md section 10.
Each test pins one differing form in the render layer, the shell
layer, the manifest harness, or the shipped README. Expectations
come from the plan and brief at their seals, never from a run of
the tool.
"""

import unittest
from types import SimpleNamespace

import dqv_harness as h

render = h.import_module("render")
shell = h.import_module("shell")
types = h.import_module("types")

UNIT_ID = ("file level unit, kind file header, "
           "beginning at line 1")
LINE_SEPARATOR = chr(0x2028)
PARAGRAPH_SEPARATOR = chr(0x2029)


def make_entry(identifier="DQ-901", state="Open", title="An entry"):
    entry = types.EntryResult(
        identifier=identifier,
        heading="%s: %s" % (identifier, title),
        title=title, effective_state=state, open_fields={})
    return entry


def make_recon(**overrides):
    recon = types.ReconciliationBlock(
        entry_total=types.HeadedEntryCount(1),
        canonical_counts={}, ambiguous_count=0, unparsed_count=0,
        status_occurrence_total=0, paired_total_declarations=[])
    for name, value in overrides.items():
        setattr(recon, name, value)
    return recon


def make_facts(**overrides):
    facts = types.FileFactsData(
        input_name="synthetic.md", byte_count=100, line_count=10,
        digest="0" * 64)
    for name, value in overrides.items():
        setattr(facts, name, value)
    return facts


def make_output(entries=(), findings=(), census=(), recon=None,
                facts=None, **overrides):
    output = types.ValidateOutput(
        entries=list(entries), findings=list(findings),
        census=list(census),
        reconciliation=recon if recon is not None else make_recon(),
        file_facts=facts if facts is not None else make_facts(),
        limits=types.Limits(), vocabulary_version="1",
        output_form_edition="1", waiting=0, blocking=0,
        blocking_list=[], limbo_data={},
        exit_decision=types.ExitDecision(code=0, reason_classes=[]),
        fastest_item="not derivable from the file")
    for name, value in overrides.items():
        setattr(output, name, value)
    return output


def make_ns_output():
    """A render model double carrying no designation, no rule set
    version, no entry groups, and no counting units at all."""
    recon = SimpleNamespace(
        entry_total=None, dq_entry_count=0, unnumbered_entry_count=0,
        headed_span_count=0, orphan_note_segment_count=0,
        h4_sub_heading_count=0, status_occurrences_by_kind={},
        status_occurrence_total=0, canonical_counts={},
        ambiguous_count=0, unparsed_count=0,
        findings_per_severity={}, findings_per_rule={},
        distinct_phrasing_count=None, self_check=None,
        paired_total_declarations=[])
    facts = SimpleNamespace(
        input_name="synthetic.md", byte_count=100, line_count=10,
        digest="0" * 64)
    return SimpleNamespace(
        entries=[], findings=[], census=[], reconciliation=recon,
        file_facts=facts, limits=types.Limits(),
        vocabulary_version="1", output_form_edition="1",
        verbatim_appendix_rows=[], per_rule_clearing_forms={},
        crosswalk_counts={}, waiting=0, blocking=0, blocking_list=[],
        limbo_data={}, segment_claim_reports=[],
        fastest_item="not derivable from the file",
        supersession_chains=[])


def make_finding(identifier, rule=5, severity="Warning", **extra):
    finding = types.Finding(
        rule_id=rule, severity=severity, entry_identifier=identifier,
        line_span=types.Span(1, 1), statement="A synthetic finding.")
    for name, value in extra.items():
        setattr(finding, name, value)
    return finding


class SourceDesignationRenderTest(unittest.TestCase):
    """D-02, render side: render reads the source designation
    from the model and falls back to nothing."""

    def test_no_designation_in_model_never_prints_live(self):
        text = render.render_validate(make_ns_output())
        head = text.splitlines()[:6]
        file_lines = [ln for ln in head if ln.startswith("File:")]
        self.assertTrue(file_lines, "no file facts line in the head")
        self.assertNotIn(
            "live", file_lines[0],
            "render fell back to the word live where the model "
            "carries no source designation")
        self.assertIn("absent", file_lines[0])

    def test_designation_carried_on_the_output_prints(self):
        output = make_ns_output()
        output.source_designation = "pinned"
        text = render.render_validate(output)
        self.assertIn("File: pinned,", text)


class FindingIdentifierRenderTest(unittest.TestCase):
    """D-09, render part: the findings index lists per entry
    findings only, and the claiming line reads the declared
    claiming unit field and no other name."""

    def test_index_lists_per_entry_findings_only(self):
        entry = make_entry("DQ-901")
        per_entry = make_finding("DQ-901", rule=5)
        file_level = make_finding(UNIT_ID, rule=1)
        output = make_output(entries=[entry],
                             findings=[per_entry, file_level])
        text = render.render_validate(output)
        index = text.split("Findings index", 1)[1].split(
            "\nFindings\n", 1)[0]
        self.assertIn("DQ-901", index)
        self.assertNotIn(
            UNIT_ID, index,
            "a file level finding stands in the per entry index")
        body = text.split("\nFindings\n", 1)[1]
        self.assertIn(UNIT_ID, body)

    def test_claiming_line_reads_the_declared_field_only(self):
        entry = make_entry("DQ-901")
        undeclared = make_finding(
            "DQ-901", rule=8, severity="Note",
            claiming_entry="DQ-999 heading text claim")
        output = make_output(entries=[entry], findings=[undeclared])
        text = render.render_validate(output)
        self.assertNotIn(
            "Claiming unit: DQ-999 heading text claim", text,
            "render read the claiming text under an undeclared "
            "attribute name")
        declared = make_finding(
            "DQ-901", rule=8, severity="Note",
            claiming_unit=UNIT_ID)
        output = make_output(entries=[entry], findings=[declared])
        text = render.render_validate(output)
        self.assertIn("Claiming unit: " + UNIT_ID, text)


class CensusRuleRenderTest(unittest.TestCase):
    """D-10, render part: the census rule line reads the
    class_rule_statement field under its contract name."""

    def test_rule_prints_from_class_rule_statement(self):
        row = types.CensusEntry(
            class_name="Open entries", count=1,
            member_entry_ids=["DQ-901"],
            class_rule_statement="Entries whose state is Open.",
            counting_unit="entries")
        text = render.render_validate(make_output(census=[row]))
        self.assertIn("Rule: Entries whose state is Open.", text)

    def test_rule_under_another_name_does_not_print(self):
        row = SimpleNamespace(
            class_name="Open entries", count=1,
            member_entry_ids=[], class_rule="A rule under an "
            "old name.", head_line_count=None)
        text = render.render_validate(make_output(census=[row]))
        self.assertNotIn("A rule under an old name.", text)


class ShellSupplyTest(unittest.TestCase):
    """D-15, shell part: the masked findings summary stands on
    the Exit decision only, and shell supplies the rule set
    version field of the model from its own constant."""

    def test_supply_keeps_masked_summary_off_the_output(self):
        output = SimpleNamespace(findings=[], reconciliation=None)
        decision = types.ExitDecision(code=4, reason_classes=[
            "a total stated under undetermined state"])
        shell._supply_exit_decision(output, decision, (2, 1))
        self.assertEqual(
            decision.masked_findings_summary,
            {"Error": 2, "Warning": 1})
        self.assertFalse(
            hasattr(output, "masked_findings_summary"),
            "shell attached a masked findings summary to the "
            "output object beside the decision field")
        self.assertEqual(output.rule_set_version,
                         shell.RULE_SET_VERSION)

    def test_render_prints_rule_set_version_from_the_model(self):
        text = render.render_validate(make_ns_output())
        head = "\n".join(text.splitlines()[:6])
        self.assertNotIn(
            "rule set 1", head,
            "render supplied the rule set version from a fallback "
            "where the model carries no such field")
        self.assertIn("rule set absent", head)


class RenderRecomputationTest(unittest.TestCase):
    """D-16: render recomputes and rederives nothing. It prints
    what the model carries."""

    def test_no_carried_entry_total_break_is_computed(self):
        entry = make_entry("DQ-901")
        output = make_output(entries=[entry])
        output.header_facts = SimpleNamespace(
            unit_counts={"entry": 5})
        text = render.render_validate(output)
        self.assertNotIn("Tool fault", text)
        self.assertIn("DQ-901", text)

    def test_paired_totals_print_as_carried(self):
        declarations = [
            "Headed entries: 7 = 7 canonical rows + 0 Ambiguous "
            "+ 0 unparsed",
            "Status occurrences: 9 = 9 counted in the verbatim "
            "appendix",
        ]
        recon = make_recon(
            canonical_counts={"Open": 3},
            entry_total=types.HeadedEntryCount(7),
            status_occurrence_total=9,
            paired_total_declarations=declarations)
        text = render.render_validate(make_output(recon=recon))
        for declaration in declarations:
            self.assertIn(declaration, text)
        self.assertNotIn(
            "canonical rows total of 3", text,
            "render summed the canonical counts to compose its "
            "own paired totals text")

    def test_limbo_parts_do_not_recount_entries(self):
        ambiguous = make_entry("DQ-901", state="Ambiguous")
        unparsed = make_entry("DQ-902", state="Open")
        unparsed.unparsed = True
        output = make_output(entries=[ambiguous, unparsed],
                             recon=make_recon())
        text = render.render_validate(output)
        limbo_lines = [ln for ln in text.splitlines()
                       if ln.startswith("Limbo:")]
        self.assertTrue(limbo_lines)
        self.assertNotIn("DQ-901", limbo_lines[0])
        self.assertNotIn("DQ-902", limbo_lines[0])
        self.assertIn("0 Ambiguous", limbo_lines[0])

    def test_entry_groups_come_from_the_model(self):
        entry = make_entry("DQ-901", state="Open")
        output = make_output(entries=[entry])
        output.entry_groups = {"Ruled": [entry]}
        text = render.render_summary(output)
        ruled_at = text.find("Ruled group")
        self.assertGreaterEqual(ruled_at, 0)
        self.assertGreater(text.find("DQ-901"), ruled_at,
                           "the entry did not print under the "
                           "group the model carries for it")


class CountingUnitsRenderTest(unittest.TestCase):
    """D-14, render side: the units key and the figure units
    print from the model, not from render constants."""

    def test_units_key_prints_from_counting_units(self):
        output = make_output()
        output.counting_units = {
            "canonical rows": "headed entries",
            "appendix rows": "verbatim rows",
        }
        text = render.render_validate(output)
        self.assertIn("canonical rows count headed entries", text)
        self.assertIn("appendix rows count verbatim rows", text)

    def test_figure_units_print_as_carried(self):
        output = make_output(
            waiting=SimpleNamespace(value=3, unit="headed entries"),
            blocking=SimpleNamespace(value=2, unit="headed entries"))
        text = render.render_validate(output)
        self.assertIn("Waiting: 3 headed entries.", text)
        self.assertIn("Blocking: 2 headed entries.", text)


class SharedHeadTest(unittest.TestCase):
    """D-18: one shared head construction serves render and
    shell, the SharedHead shape is instantiated by it, and the
    shell not read head carries the file facts line."""

    def test_one_construction_instantiates_shared_head(self):
        render_source = h.module_source("render")
        shell_source = h.module_source("shell")
        self.assertIn("SharedHead(", render_source + shell_source)
        self.assertIn("build_shared_head", render_source)
        self.assertIn("build_shared_head", shell_source)

    def test_not_read_head_carries_the_file_facts_line(self):
        missing = "/tmp/dqv_fix_c_missing_input_zz.md"
        code, out, err = h.run_cli("validate", missing)
        self.assertEqual(code, 2)
        lines = err.decode("utf-8", errors="replace").splitlines()
        self.assertTrue(lines[0].startswith("Checked:"))
        self.assertTrue(lines[1].startswith("Input:"))
        self.assertTrue(
            lines[2].startswith("File:"),
            "the not read head omits the file facts line; its "
            "third line is: " + lines[2])
        self.assertTrue(lines[3].startswith("Limits:"))
        self.assertTrue(lines[4].startswith("Versions:"))


class ManifestHarnessTest(unittest.TestCase):
    """D-17, harness part: the harness checks the manifest
    grammar and its labels over the manifest text, and the
    MANIFEST_MD constant stands used by that check."""

    def test_manifest_entries_come_from_the_checked_text(self):
        entry = h.manifest_entry("F-01")
        self.assertIn("pinned", entry["expected_counts"])
        self.assertEqual(h.expected_exit("F-01"), 1)

    def test_self_check_fails_loudly_on_an_unlabelled_count(self):
        bad = (
            "Fixture: F-99\n"
            "Kind: synthetic\n"
            "Source: synthetic construction\n"
            "Hash: " + "0" * 64 + "\n"
            "Bytes: 10\n"
            "Lines: 2\n"
            "Expected counts: headed entries 1\n"
            "Expected findings: none (pinned)\n"
            "Expected exit: 0 (derived)\n"
        )
        with self.assertRaises(h.ManifestFailure) as caught:
            h.check_manifest_text(bad)
        self.assertIn("F-99", str(caught.exception))

    def test_self_check_fails_loudly_on_field_order(self):
        bad = (
            "Fixture: F-99\n"
            "Source: synthetic construction\n"
            "Kind: synthetic\n"
            "Hash: " + "0" * 64 + "\n"
            "Bytes: 10\n"
            "Lines: 2\n"
            "Expected counts: headed entries 1 (pinned)\n"
            "Expected findings: none (pinned)\n"
            "Expected exit: 0 (derived)\n"
        )
        with self.assertRaises(h.ManifestFailure):
            h.check_manifest_text(bad)

    def test_manifest_md_constant_stands_used(self):
        import inspect
        source = inspect.getsource(h)
        self.assertGreaterEqual(source.count("MANIFEST_MD"), 3)


class FreshFindingsTest(unittest.TestCase):
    """A3-F01 to A3-F04, the fresh findings in this slice."""

    def test_a3_f01_ungrouped_entry_is_never_dropped(self):
        entry = make_entry("DQ-777", state="Banked")
        output = make_output(entries=[entry])
        output.entry_groups = {}
        text = render.render_validate(output)
        self.assertIn("Ungrouped entries", text)
        self.assertIn("DQ-777", text)

    def test_a3_f02_separators_are_escaped(self):
        self.assertEqual(render.escape_text(LINE_SEPARATOR),
                         "\\u2028")
        self.assertEqual(render.escape_text(PARAGRAPH_SEPARATOR),
                         "\\u2029")

    def test_a3_f03_readme_describes_the_shipped_sections(self):
        text = (h.PRODUCT_ROOT / "README.md").read_text(
            encoding="utf-8")
        validate_part = text.split(
            "The validate report carries", 1)[1].split(
            "The render summary carries", 1)[0]
        render_part = text.split(
            "The render summary carries", 1)[1].split(
            "The figures state", 1)[0]
        for part in (validate_part, render_part):
            self.assertIn("verbatim appendix", part.lower())
            self.assertIn("residue list", part.lower())
            self.assertIn("Segment claims", part)
        lowered = validate_part.lower()
        self.assertLess(lowered.find("verbatim appendix"),
                        lowered.find("residue list"))
        self.assertLess(lowered.find("residue list"),
                        lowered.find("segment claims"))

    def test_a3_f04_shell_trusts_the_carried_counts(self):
        output = SimpleNamespace(
            findings=[],
            entries=[SimpleNamespace(
                effective_state="Ambiguous",
                reporting_form="Ambiguous", unparsed=True)],
            reconciliation=SimpleNamespace(
                ambiguous_count=0, unparsed_count=0,
                self_check=None))
        decision, _masked = shell._assemble_exit_decision(output)
        self.assertEqual(
            decision.code, 0,
            "shell recounted the Ambiguous and unparsed entries "
            "where the model carries zero for both counts")


if __name__ == "__main__":
    unittest.main()
