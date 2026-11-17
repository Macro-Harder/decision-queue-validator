"""Slice 3, Unit 3e, census group.

The census as its own type, never a finding: its class rules keyed to
shape and to effective state, its counts and member entry identifiers
for the real fixtures as the corpus manifest records them, and the
same shape on an effectively open entry governed by the open entry
check instead of the census.
"""

import unittest

import dqv_harness as h


def _census(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    return output, h.census_of(output)


class CensusShapeTest(unittest.TestCase):

    def test_census_entries_are_not_findings(self):
        _model, output = h.cached_pipeline("R1")
        findings = h.findings_of(output)
        finding_blobs = set()
        for finding in findings:
            finding_blobs.add(h.finding_statement(finding))
        for item in h.census_of(output):
            self.assertIsNotNone(h.get(item, "class_name", "name"))
            self.assertIsNotNone(h.get(item, "count", "member_count"))
            self.assertIsNotNone(h.get(item, "member_entry_ids",
                                       "members", "member_ids"))
            # A census entry is its own shape and never a finding:
            # it does not stand in the findings list, it carries no
            # finding severity and no finding rule, and its class
            # name is the statement of no finding. A product that
            # emitted a census entry as a finding would fail each of
            # these, where the shape assertions above alone would
            # still pass.
            self.assertNotIn(item, findings)
            self.assertIsNone(h.get(item, "severity", "grade"))
            self.assertIsNone(h.finding_rule_number(item))
            class_name = h.text_of(h.get(item, "class_name", "name"))
            self.assertNotIn(class_name, finding_blobs)

    def test_census_prints_in_both_outputs(self):
        _model, output = h.cached_pipeline("R1")
        for form in ("validate", "render"):
            with self.subTest(form=form):
                text = h.render_text(output, form)
                self.assertIn("census", text.lower())


class R1CensusClassesTest(unittest.TestCase):

    def test_banked_head_class_stands_at_103_with_members(self):
        _output, census = _census("R1")
        banked = h.census_class(census, "banked")
        self.assertIsNotNone(banked)
        self.assertEqual(h.census_count(banked), 103)
        members = h.census_members(banked)
        self.assertEqual(len(members), 103)
        self.assertIn("DQ-050", members)

    def test_derived_class_counts_match_the_manifest_header(self):
        _output, census = _census("R1")
        splits = h.manifest()["corpus_structure_splits"]
        derived = splits["census_classes_R1_beyond_banked_head"]
        checks = (
            (("non", "header"), derived[
                "non_header_status_value_on_decided_entry"]),
            (("options",), derived[
                "missing_options_block_on_decided_entry"]),
            (("date",), derived["missing_ruling_date_on_decided_entry"]),
            (("numeric",), derived[
                "non_numeric_filing_in_ruled_record"]),
            (("owner",), derived["missing_owner_line_in_tail_form_entry"]),
            (("question",), derived[
                "decided_entry_missing_question_label_or_cost_field"]),
            (("open form",), derived[
                "open_form_fields_carried_by_decided_entry_in_ruled_record"]),
            (("unclassified",), derived["unclassified_status_values"]),
        )
        for parts, expected in checks:
            with self.subTest(parts=parts):
                item = h.census_class(census, *parts)
                self.assertIsNotNone(item, parts)
                self.assertEqual(h.census_count(item), expected, parts)
                self.assertEqual(len(h.census_members(item)), expected,
                                 parts)

    def test_member_ids_print_in_file_order(self):
        _model, output = h.cached_pipeline("R1")
        file_order = [h.entry_identifier(entry)
                      for entry in h.entries_of(output)]
        positions = {name: index for index, name in enumerate(file_order)}
        for item in h.census_of(output):
            members = [member for member in h.census_members(item)
                       if member in positions]
            ordered = sorted(members, key=lambda member: positions[member])
            self.assertEqual(members, ordered)


class CensusVersusCheck9Test(unittest.TestCase):

    def test_decided_dq137_shape_is_census_not_a_finding(self):
        _model, output = h.cached_pipeline("R1")
        self.assertEqual(
            h.findings_for(output, entry_id="DQ-137", rule=9), [])
        _output, census = _census("R1")
        item = h.census_class(census, "question")
        self.assertIsNotNone(item)
        self.assertIn("DQ-137", h.census_members(item))

    def test_open_entry_missing_fields_are_findings_not_census(self):
        _model, output = h.cached_pipeline("S5b")
        self.assertEqual(len(h.findings_for(output, rule=9)), 4)
        for item in h.census_of(output):
            members = h.census_members(item)
            self.assertNotIn("DQ-901", members)
            self.assertNotIn("DQ-902", members)


class SmallFixtureCensusTest(unittest.TestCase):

    def test_s3b_unclassified_class_names_its_entry(self):
        _output, census = _census("S3b")
        item = h.census_class(census, "unclassified")
        self.assertIsNotNone(item)
        self.assertEqual(h.census_members(item), ["DQ-001"])

    def test_s5_clean_run_census_classes_are_empty_of_its_entry(self):
        _output, census = _census("S5")
        for item in census:
            self.assertEqual(h.census_count(item),
                             len(h.census_members(item)))


def _taught_entry(number, title, status, blocks="DQ-002",
                  paragraph="This question is waiting for a decision."):
    return (
        "### DQ-%03d: %s\n"
        "\n"
        "Status: %s\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: %s\n"
        "\n"
        "%s\n" % (number, title, status, blocks, paragraph))


class Step17C3CensusTest(unittest.TestCase):
    """Step 17 fix wave 1, cluster C3, census and counting charges.

    Each test pins one charged finding under its own name, in the
    construction its attack paper states. The constructions are
    built here as text, in the README taught form the papers use.
    """

    def test_a3_3_f3_status_occurrence_joined_to_heading_by_lone_cr_is_counted(self):
        # A3-3-F3: a lone carriage return joins the heading line
        # and the Status line into one logical line. The brief
        # invariant is that each status occurrence is counted
        # exactly once: the swallowed Banked occurrence must stand
        # in the verbatim appendix and in the occurrence total.
        text = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: A sample open question\rStatus: Banked\n"
            "\n"
            "Question: Which option should we take?\n"
            "\n"
            "Options: Option A, Option B\n"
            "\n"
            "Cost of deciding late: Work stays blocked.\n"
            "\n"
            "Blocks: DQ-002\n"
            "\n"
            "This question is waiting for a decision.\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        recon = h.reconciliation_of(output)
        total = h.int_of(h.get(recon, "status_occurrence_total",
                               "occurrence_total"))
        self.assertEqual(total, 1)
        rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                               "appendix_rows", "verbatim_appendix"))
        banked = [row for row in rows
                  if h.text_of(h.get(row, "phrasing")) == "Banked"]
        self.assertEqual(len(banked), 1)
        self.assertEqual(
            h.int_of(h.get(banked[0], "occurrence_count", "count")), 1)

    def test_s17_atk7_03_preamble_status_lines_enter_the_appendix_totals(self):
        # S17-ATK7-03: two Status lines standing in the queue
        # preamble before any entry heading are status occurrences
        # in the file. They must be assigned to a unit or listed
        # as unassigned and enter the paired totals: the appendix
        # and the occurrence total count all three line start
        # Status lines of the file.
        text = (
            "# Decision queue\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "Status: Banked\n"
            "\n"
            + _taught_entry(109, "Ordinary banked entry", "Banked"))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        recon = h.reconciliation_of(output)
        total = h.int_of(h.get(recon, "status_occurrence_total",
                               "occurrence_total"))
        self.assertEqual(total, 3)
        rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                               "appendix_rows", "verbatim_appendix"))
        by_phrasing = {}
        for row in rows:
            by_phrasing[h.text_of(h.get(row, "phrasing"))] = h.int_of(
                h.get(row, "occurrence_count", "count"))
        self.assertEqual(by_phrasing.get("RULED, closed"), 1)
        self.assertEqual(by_phrasing.get("Banked"), 2)

    def test_s17_atk7_03_status_line_before_the_heading_is_counted(self):
        # S17-ATK7-03, second construction of the paper: one Status
        # line placed between the header and the entry heading,
        # the entry body carrying no Status line of its own. The
        # displaced line is a status occurrence in the file and
        # must be counted somewhere in the totals.
        text = (
            "# Decision queue\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "### DQ-104: Entry with no status line of its own\n"
            "\n"
            "Question: Which option should we take?\n"
            "\n"
            "Options: Option A, Option B\n"
            "\n"
            "Cost of deciding late: Work stays blocked.\n"
            "\n"
            "Blocks: DQ-002\n"
            "\n"
            "This question is waiting for a decision.\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        recon = h.reconciliation_of(output)
        total = h.int_of(h.get(recon, "status_occurrence_total",
                               "occurrence_total"))
        self.assertEqual(total, 1)

    def test_a10_f4_translated_phrasing_is_not_held_as_residue(self):
        # A10-F4 (merged charge M7, first name): one phrasing holds
        # one classification across the derived state, the census,
        # the appendix, and the residue list. A phrasing the tool
        # translates to a canonical family is not a residue item
        # and is not held as unknown in the appendix.
        for status in ("banked", "BANKED, awaiting Captain JP",
                       "Banked."):
            with self.subTest(status=status):
                text = ("# Decision queue\n\n"
                        + _taught_entry(1, "Translated phrasing entry",
                                        status,
                                        paragraph="A plain context "
                                                  "paragraph."))
                _model, output = h.run_pipeline(text.encode("utf-8"))
                self.assertIsNotNone(output)
                residue = h.as_list(h.get(output, "residue_items",
                                          "residue_list", "residue"))
                self.assertEqual(residue, [])
                _output, census = output, h.census_of(output)
                item = h.census_class(census, "unclassified")
                self.assertIsNotNone(item)
                self.assertEqual(h.census_count(item), 0)
                rendered = h.render_text(output, "validate")
                self.assertNotIn("| unclassified", rendered)

    def test_seat19_f1_value_side_change_is_not_held_as_residue(self):
        # F1 of seat 19 (merged charge M7, second name): a value
        # side whitespace or case change on the F-06 shape must not
        # make one report disagree with itself. The state, the
        # crosswalk, and the census treat the phrasing as
        # classified, so the appendix flag and the residue list
        # must not hold it as unknown.
        base = h.fixture_bytes("F-06")
        for mutated in (
                base.replace(b"Status: Banked", b"Status: banked"),
                base.replace(b"Status: Banked", b"Status:\tBanked")):
            with self.subTest(mutated=mutated[100:140]):
                _model, output = h.run_pipeline(mutated,
                                                name="F-06.md")
                self.assertIsNotNone(output)
                residue = h.as_list(h.get(output, "residue_items",
                                          "residue_list", "residue"))
                self.assertEqual(residue, [])
                item = h.census_class(h.census_of(output),
                                      "unclassified")
                self.assertIsNotNone(item)
                self.assertEqual(h.census_count(item), 0)

    def test_f_8_1_bare_decision_block_heading_takes_no_evidence_credit(self):
        # F-8-1: a level 4 decision block heading with no body
        # carries no census evidence element under PIN-01 form 1.
        # The bare heading must not place its entry in the level 4
        # decision block evidence group, and with no other counted
        # element the Banked head footing must fail, as the README
        # describes for a Banked entry counted in no group.
        text = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: Entry ending in an empty decision block\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "Question: Which option should we take?\n"
            "\n"
            "Options: Option A, Option B\n"
            "\n"
            "Cost of deciding late: Work stays blocked.\n"
            "\n"
            "Blocks: DQ-002\n"
            "\n"
            "#### Ruling by Captain JP\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        census = h.census_of(output)
        group = h.census_class(census, "level 4 decision block")
        members = h.census_members(group) if group is not None else []
        self.assertNotIn("DQ-001", members)
        recon = h.reconciliation_of(output)
        check = h.get(recon, "self_check", "self_check_result")
        agrees = h.get(check, "sums_agree", "ok", "passed", "agrees")
        self.assertEqual(agrees, False)

    def test_f_8_1_block_with_a_body_keeps_its_evidence_credit(self):
        # F-8-1 control, the bound of the charge stated in the
        # triage ruling: the cure removes the credit of a bare
        # heading only, and nothing else. A level 4 block carrying
        # a body keeps its place in the evidence group.
        text = (
            "# Decision queue\n"
            "\n"
            "### DQ-001: Entry with a decision block body\n"
            "\n"
            "Status: Banked\n"
            "\n"
            "Question: Which option should we take?\n"
            "\n"
            "Options: Option A, Option B\n"
            "\n"
            "Cost of deciding late: Work stays blocked.\n"
            "\n"
            "Blocks: DQ-002\n"
            "\n"
            "#### Ruling by Captain JP\n"
            "\n"
            "A filing sentence stands in the block body.\n")
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        group = h.census_class(h.census_of(output),
                               "level 4 decision block")
        self.assertIsNotNone(group)
        self.assertIn("DQ-001", h.census_members(group))

    def test_a21_5_gap_naming_total_over_the_bound_takes_over_bound_treatment(self):
        # A21-5: the 2,000,000 character naming bound applies to
        # the run total naming output, not only per naming. One
        # naming of this missing set stands under the bound, and
        # the validate form prints the naming twice, so the total
        # stands over the bound and the over bound treatment
        # applies: no part of the missing set is named.
        text = (
            "# Decision queue\n"
            "\n"
            + _taught_entry(1, "Entry 1", "Banked",
                            blocks="none",
                            paragraph="Some prose paragraph here.")
            + "\n"
            + _taught_entry(200000, "Entry 200000", "Banked",
                            blocks="none",
                            paragraph="Some prose paragraph here."))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        over = h.get(output, "gap_naming_over_bound", "gap_over_bound")
        self.assertEqual(over, True)
        statements = [h.finding_statement(finding) or ""
                      for finding in h.findings_of(output)]
        self.assertFalse(any("Entry numbers missing" in statement
                             for statement in statements))


if __name__ == "__main__":
    unittest.main()
