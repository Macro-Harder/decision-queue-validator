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


class DeciderLabelCorrectionTest(unittest.TestCase):
    """The carried decider label itself, for the corrected classes.

    Expectations are sourced from the tuple rule of brief section
    5.4 (where the determining element tuple names a decider, that
    decider governs the label, and statement text never outranks
    the tuple) and from the Step 14 correction record (the
    correction figure of 84: 79 Manager grant tuple results at
    disposition Settled, 3 DQ-117 results, 2 DQ-108 results). No
    expectation is sourced from a run of the tool. Each assertion
    reads the carried decider_label on the Validate output entry
    result, never rendered text, and is unconditional.
    """

    def _label(self, fixture_id, entry_id):
        entry = _state(fixture_id, entry_id)
        return entry, h.text_of(h.get(entry, "decider_label", "decider"))

    def test_r8_dq130_carries_the_manager_grant_label(self):
        entry, label = self._label("R8", "DQ-130")
        self.assertEqual(h.entry_state(entry), "Settled")
        self.assertEqual(label, "Settled by the Manager under the grant")

    def test_s18_plain_grant_form_carries_the_manager_grant_label(self):
        entry, label = self._label("S18", "DQ-901")
        self.assertEqual(h.entry_state(entry), "Settled")
        self.assertEqual(label, "Settled by the Manager under the grant")

    def test_r1_dq117_manager_grant_tuple_at_ruled_disposition(self):
        entry, label = self._label("R1", "DQ-117")
        self.assertEqual(h.entry_state(entry), "Ruled")
        self.assertEqual(label, "Settled by the Manager under the grant")

    def test_r1_dq108_captain_jp_tuple_carries_the_ruled_label(self):
        entry, label = self._label("R1", "DQ-108")
        self.assertEqual(h.entry_state(entry), "Ruled")
        self.assertEqual(label, "Ruled by Captain JP")


class CarriedFormDerivationTest(unittest.TestCase):
    """Derivation reads carried forms only, with body lines empty.

    The hand built entries carry the D-1 assessment closure fact
    and the D-2 closing condition fact in their element tuples
    alone. The corpus invariant then strips body lines from every
    pinned fixture model and asserts that no entry state, decider
    label, condition text or remainder text moves.
    """

    def _hand_model(self):
        types = h.import_module("types")
        tuple_type = types.ElementTuple
        element_type = types.StatusBearingElement
        record_type = types.EntryRecord

        def element(kind, verbatim, tup, line):
            return element_type(
                kind=kind, verbatim=verbatim, tuple=tuple_type(*tup),
                line=line, position_in_line=0, occurrence_kind=None,
                statement=verbatim,
                decider_text=None)

        d1 = record_type(
            identifier="DQ-901", heading="DQ-901: Hand built closure",
            heading_level=3, heading_line=1,
            title="Hand built closure",
            status_elements=[
                element("head Status line", "Banked",
                        ("Banked", "Whole", None, None, 2), 2),
                element("closing prose",
                        "Closed as decided under DQ-148.",
                        ("Closed", "Whole", None,
                         "assessment by cross reference", 5), 5)],
            body_lines=[])
        d1.status_elements[1].decider_text = "assessment under DQ-148"
        d2 = record_type(
            identifier="DQ-902", heading="DQ-902: Hand built condition",
            heading_level=3, heading_line=10,
            title="Hand built condition",
            status_elements=[
                element("head Status line", "Banked",
                        ("Banked", "Whole", None, None, 11), 11),
                element("closing prose", "Ruled in full.",
                        ("Ruled", "Whole",
                         "the five landings completing", "Captain JP",
                         14), 14)],
            body_lines=[])
        d2.status_elements[1].decider_text = "Captain JP"
        return h.ParseModelDouble(entries=[d1, d2])

    def test_hand_built_carried_forms_derive_without_body_text(self):
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        output = h.validate_function(validate_module)(
            self._hand_model(), vocabulary)
        d1 = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(d1), "Closed as decided")
        self.assertEqual(
            h.text_of(h.get(d1, "decider_label", "decider")),
            "decided by assessment under DQ-148")
        d2 = h.entry_by_id(output, "DQ-902")
        self.assertEqual(h.entry_state(d2), "Conditional")
        self.assertEqual(
            h.text_of(h.get(d2, "condition_text", "condition")),
            "the five landings completing")

    def _carried_facts(self, output):
        facts = {}
        for entry in h.entries_of(output):
            ident = h.entry_identifier(entry)
            facts[ident] = (
                h.entry_state(entry),
                h.text_of(h.get(entry, "decider_label", "decider")),
                h.text_of(h.get(entry, "condition_text", "condition")),
                h.text_of(h.get(entry, "remainder_text", "remainder")))
        return facts

    def test_corpus_derivation_is_invariant_under_body_line_stripping(self):
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        for fixture_id in h.FIXTURE_IDS:
            with self.subTest(fixture=fixture_id):
                model, output = h.cached_pipeline(fixture_id)
                if h.is_failure_result(model):
                    continue
                stripped = h.deepcopy_value(model)
                for entry in h.entries_of(stripped):
                    entry.body_lines = []
                stripped_output = h.validate_function(
                    validate_module)(stripped, vocabulary)
                self.assertEqual(self._carried_facts(stripped_output),
                                 self._carried_facts(output))

    def test_r1_blast_radius_of_the_parse_repair(self):
        model, output = h.cached_pipeline("R1")
        recon = h.reconciliation_of(output)
        total = h.int_of(h.get(recon, "status_occurrence_total"))
        expected = h.manifest_value(
            h.manifest_entry("R1"), "expected_counts",
            "status_occurrences")
        self.assertEqual(total, expected)
        check3 = [finding for finding in h.findings_for(output, rule=3)
                  if h.finding_entry_id(finding) in (
                      "DQ-053", "DQ-061", "DQ-064", "DQ-067",
                      "DQ-109", "DQ-110")]
        self.assertEqual(check3, [])
        for entry_id in ("DQ-053", "DQ-061", "DQ-064", "DQ-067",
                         "DQ-109", "DQ-110"):
            with self.subTest(entry=entry_id):
                record = h.entry_by_id(model, entry_id)
                elements = h.as_list(
                    h.get(record, "status_elements", "elements"))
                result = h.entry_by_id(output, entry_id)
                summary = h.as_list(
                    h.get(result, "element_summary"))
                self.assertEqual(len(summary), len(elements))
                self.assertIn("closing prose", summary[-1])
                self.assertIn("Closed", summary[-1])


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
