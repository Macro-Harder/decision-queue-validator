"""Slice 3, Unit 3a, derivation group.

Effective state derivation under the tuple mapping with its named
exceptions: the part state in both decider forms, the unclassifiable
value shapes, the triggerless Parked reading, the combined tuple
shapes with no part State row, the BQ-2 interim reporting rule, the
unparsed precedence, and the canonical counts of the real fixtures as
the corpus manifest records them. BQ-1, BQ-2 and BQ-3 are decided
nowhere in this group: the pair shaped fixtures assert the interim
rule reporting only.
"""

import unittest

import dqv_harness as h


def _state(fixture_id, entry_id):
    _model, output = h.cached_pipeline(fixture_id)
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id + " on " + fixture_id)
    return entry


class PartStateTest(unittest.TestCase):

    def test_s11_manager_part_settlement_is_settled_in_part(self):
        entry = _state("S11", "DQ-901")
        self.assertEqual(h.entry_state(entry), "Settled in part")
        remainder = h.text_of(h.get(entry, "remainder_text", "remainder"))
        self.assertIn("the estate default anchor set stays banked",
                      remainder or "")
        _model, output = h.cached_pipeline("S11")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 1)
        self.assertEqual(counts.get("Closed as decided", 0), 0)
        self.assertEqual(h.findings_of(output), [])
        self.assertEqual(h.exit_code_of(output), 0)

    def test_s12_captain_jp_part_ruling_keeps_its_decider_label(self):
        entry = _state("S12", "DQ-901")
        self.assertEqual(h.entry_state(entry), "Settled in part")
        label = h.text_of(h.get(entry, "decider_label", "decider"))
        self.assertEqual(label, "Ruled by Captain JP")
        remainder = h.text_of(h.get(entry, "remainder_text", "remainder"))
        self.assertIn("the estate default anchor set stays banked",
                      remainder or "")
        _model, output = h.cached_pipeline("S12")
        self.assertEqual(h.findings_of(output), [])
        self.assertEqual(h.exit_code_of(output), 0)


class UnclassifiableValueTest(unittest.TestCase):

    def test_s3b_shape_a_assigns_open_by_the_exception_row(self):
        entry = _state("S3b", "DQ-001")
        self.assertEqual(h.entry_state(entry), "Open")
        _model, output = h.cached_pipeline("S3b")
        self.assertEqual(h.exit_code_of(output), 0)
        census = h.census_of(output)
        unclassified = None
        for item in census:
            name = (h.text_of(h.get(item, "class_name", "name")) or "")
            if "unclassified" in name.lower():
                unclassified = item
        self.assertIsNotNone(unclassified)
        self.assertIn("DQ-001", h.census_members(unclassified))

    def test_s20_shape_b_both_limbs_report_ambiguous(self):
        for entry_id in ("DQ-901", "DQ-902"):
            with self.subTest(entry=entry_id):
                entry = _state("S20", entry_id)
                self.assertTrue(h.is_ambiguous(entry))
                self.assertEqual(h.entry_sub_label(entry),
                                 "Single element")
        _model, output = h.cached_pipeline("S20")
        self.assertEqual(h.exit_code_of(output), 4)
        errors = [finding for finding in h.findings_of(output)
                  if h.finding_severity(finding) == "Error"]
        self.assertEqual(errors, [])
        census = h.census_of(output)
        unclassified = None
        for item in census:
            name = (h.text_of(h.get(item, "class_name", "name")) or "")
            if "unclassified" in name.lower():
                unclassified = item
        self.assertIsNotNone(unclassified)
        self.assertEqual(h.census_count(unclassified), 2)
        members = h.census_members(unclassified)
        self.assertIn("DQ-901", members)
        self.assertIn("DQ-902", members)


class ParkedAndPresentedTest(unittest.TestCase):

    def test_s3a_triggered_parked_is_parked_with_no_error(self):
        entry = _state("S3a", "DQ-001")
        self.assertEqual(h.entry_state(entry), "Parked")
        _model, output = h.cached_pipeline("S3a")
        self.assertEqual(h.findings_of(output), [])
        self.assertEqual(h.exit_code_of(output), 0)

    def test_s3c_presented_is_assigned_on_verbatim_evidence(self):
        entry = _state("S3c", "DQ-001")
        self.assertEqual(h.entry_state(entry), "Presented")
        _model, output = h.cached_pipeline("S3c")
        self.assertEqual(h.exit_code_of(output), 0)

    def test_s6_pair_both_parked_and_triggerless_is_not_ambiguous(self):
        first = _state("S6", "DQ-001")
        second = _state("S6", "DQ-002")
        self.assertEqual(h.entry_state(first), "Parked")
        self.assertEqual(h.entry_state(second), "Parked")
        self.assertFalse(h.is_ambiguous(second))


class CombinedTupleShapeTest(unittest.TestCase):

    def test_s17_part_scope_shapes_report_ambiguous_single_element(self):
        for entry_id in ("DQ-901", "DQ-902"):
            with self.subTest(entry=entry_id):
                entry = _state("S17", entry_id)
                self.assertTrue(h.is_ambiguous(entry))
                self.assertEqual(h.entry_sub_label(entry),
                                 "Single element")
                competing = h.as_list(h.get(
                    entry, "competing_elements", "determining_element",
                    "elements_quoted"))
                self.assertTrue(competing)
        _model, output = h.cached_pipeline("S17")
        self.assertEqual(h.exit_code_of(output), 4)


class Bq2InterimReportingTest(unittest.TestCase):

    def test_r4_pair_reports_ambiguous_conflict_and_closed_nowhere(self):
        for entry_id in ("DQ-087", "DQ-106"):
            with self.subTest(entry=entry_id):
                entry = _state("R4", entry_id)
                self.assertTrue(h.is_ambiguous(entry))
                self.assertEqual(h.entry_sub_label(entry), "Conflict")
                banked = h.text_of(h.get(entry, "banked_question",
                                         "banked_question_id"))
                self.assertEqual(banked, "BQ-2")
        _model, output = h.cached_pipeline("R4")
        counts = h.canonical_counts(output)
        decided_total = sum(counts.get(name, 0) for name in
                            ("Ruled", "Settled", "Settled in part",
                             "Closed as decided"))
        self.assertEqual(decided_total, 0)
        self.assertEqual(h.ambiguous_count(output), 2)
        check3 = h.findings_for(output, rule=3)
        self.assertEqual(check3, [])
        errors = [finding for finding in h.findings_of(output)
                  if h.finding_severity(finding) == "Error"]
        self.assertEqual(errors, [])

    def test_r1_pair_carries_the_same_interim_reporting(self):
        for entry_id in ("DQ-087", "DQ-106"):
            with self.subTest(entry=entry_id):
                entry = _state("R1", entry_id)
                self.assertTrue(h.is_ambiguous(entry))
                self.assertEqual(h.entry_sub_label(entry), "Conflict")


class UnparsedPrecedenceTest(unittest.TestCase):

    def test_s7c_unparsed_entry_is_not_derived(self):
        _model, output = h.cached_pipeline("S7c")
        entry = h.entry_by_id(output, "DQ-901")
        self.assertIsNotNone(entry)
        self.assertTrue(bool(h.get(entry, "unparsed", "unparsed_flag")))
        counts = h.canonical_counts(output)
        total = sum(counts.values())
        self.assertEqual(total, 0)
        self.assertEqual(h.unparsed_count(output), 1)

    def test_s13_unparsed_entry_stands_beside_the_ambiguous_entry(self):
        _model, output = h.cached_pipeline("S13")
        self.assertEqual(h.unparsed_count(output), 1)
        self.assertEqual(h.ambiguous_count(output), 1)


class ReattachedEntryStateTest(unittest.TestCase):

    def test_s8_states_ruled_by_addition_and_open_beside_it(self):
        first = _state("S8", "DQ-901")
        second = _state("S8", "DQ-902")
        self.assertEqual(h.entry_state(first), "Ruled")
        self.assertEqual(h.entry_state(second), "Open")


class CanonicalCountsRealFixturesTest(unittest.TestCase):

    def test_r1_canonical_counts_match_the_manifest(self):
        _model, output = h.cached_pipeline("R1")
        counts = h.canonical_counts(output)
        split = h.manifest()["corpus_structure_splits"][
            "canonical_split_R1"]
        for state in ("Open", "Presented", "Parked", "Ruled", "Settled",
                      "Settled in part", "Closed as decided",
                      "Conditional"):
            self.assertEqual(counts.get(state), split[state], state)
        self.assertEqual(h.ambiguous_count(output), 2)
        self.assertEqual(h.unparsed_count(output), 0)
        self.assertEqual(h.int_of(h.entry_total(output)), 157)

    def test_r2_canonical_counts_match_the_manifest(self):
        _model, output = h.cached_pipeline("R2")
        counts = h.canonical_counts(output)
        expected = h.manifest_entry("R2")["expected_counts"][
            "canonical_split"]
        for state in ("Open", "Presented", "Parked", "Ruled", "Settled",
                      "Settled in part", "Closed as decided",
                      "Conditional"):
            self.assertEqual(counts.get(state), expected[state], state)
        self.assertEqual(h.ambiguous_count(output), 2)
        self.assertEqual(h.int_of(h.entry_total(output)), 156)

    def test_r7_states_ruled_four_conditional_two(self):
        _model, output = h.cached_pipeline("R7")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Ruled"), 4)
        self.assertEqual(counts.get("Conditional"), 2)

    def test_r3_settled_with_the_dq143_decider_label(self):
        entry = _state("R3", "DQ-050")
        self.assertEqual(h.entry_state(entry), "Settled")
        label = h.text_of(h.get(entry, "decider_label", "decider"))
        self.assertEqual(label, "settled under DQ-143")

    def test_r9_dq099_is_settled(self):
        entry = _state("R9", "DQ-099")
        self.assertEqual(h.entry_state(entry), "Settled")

    def test_every_parsed_entry_gets_exactly_one_state(self):
        for fixture_id in ("R1", "R5", "S5", "S14", "S20"):
            with self.subTest(fixture=fixture_id):
                _model, output = h.cached_pipeline(fixture_id)
                for entry in h.entries_of(output):
                    if h.get(entry, "unparsed", "unparsed_flag"):
                        continue
                    state = h.entry_state(entry)
                    self.assertTrue(
                        state in ("Open", "Presented", "Parked", "Ruled",
                                  "Settled", "Settled in part",
                                  "Closed as decided", "Conditional")
                        or h.is_ambiguous(entry),
                        fixture_id + " entry without one state")


if __name__ == "__main__":
    unittest.main()
