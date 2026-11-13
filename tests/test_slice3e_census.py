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


if __name__ == "__main__":
    unittest.main()
