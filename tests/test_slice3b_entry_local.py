"""Slice 3, Unit 3b, entry local checks group.

Checks 2, 3, 4, 5, 7, 9 and 10 as predicates over single entries:
the near marker Warning, the symmetric disagreement Warning and its
census form, the Conditional closure Note, decision evidence presence
with its four independent tests and its Ambiguous bound, the open
entry fields, and the parked form. Expectations are the brief rulings
and the corpus manifest values.
"""

import unittest

import dqv_harness as h


def _output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    return output


class Check2NearMarkerTest(unittest.TestCase):

    def test_s15_near_marker_fires_once_and_state_stays_open(self):
        output = _output("S15")
        entry = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(entry), "Open")
        warnings = h.findings_for(output, rule=2, severity="Warning")
        self.assertEqual(len(warnings), 1)
        self.assertEqual(h.finding_entry_id(warnings[0]), "DQ-901")
        self.assertEqual(len(h.findings_of(output)), 1)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s5_clean_entry_has_no_check2_finding(self):
        output = _output("S5")
        self.assertEqual(h.findings_for(output, rule=2), [])


class Check3DisagreementTest(unittest.TestCase):

    def test_s18_later_settled_governs_with_one_warning(self):
        output = _output("S18")
        entry = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(entry), "Settled")
        warnings = h.findings_for(output, rule=3, severity="Warning")
        self.assertEqual(len(warnings), 1)
        statement = h.finding_statement(warnings[0]) or ""
        self.assertIn("disagree", statement.lower())
        evidence = h.finding_evidence_text(warnings[0])
        self.assertIn("RULED", evidence)
        self.assertIn("SETTLED", evidence)
        self.assertEqual(len(h.findings_of(output)), 1)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s19_disagreement_fires_for_the_earlier_ruled_elements(self):
        output = _output("S19")
        warnings = h.findings_for(output, rule=3, severity="Warning")
        self.assertEqual(len(warnings), 1)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s5_single_element_entry_has_no_disagreement(self):
        output = _output("S5")
        self.assertEqual(h.findings_for(output, rule=3), [])

    def test_r1_banked_head_disagreements_are_census_only(self):
        # The Banked head normal form stays census only: no check 3
        # finding on R1 rests on a Banked head over a decided body.
        # Since the Step 19 R-04 fix, the check 3 Warnings on R1
        # rest on the tail record entries whose last element states
        # what remains open: that element now stands in element
        # order, and the disagreement between the state it denotes
        # and the state its entry derives is a pin 6 Warning where
        # the determining element is unambiguous. One further
        # Warning stands since the Step 19 R-04 limb C fix, on
        # DQ-023, whose last element opening "Closing line for"
        # now stands in element order and states Ruled. The count
        # stands recomputed under those fixes and is recorded in
        # the Step 19 fix register.
        output = _output("R1")
        warnings = h.findings_for(output, rule=3)
        self.assertEqual(len(warnings), 12)
        for warning in warnings:
            self.assertNotIn("Banked",
                             h.finding_evidence_text(warning) or "")
        census = h.census_of(output)
        banked = h.census_class(census, "banked")
        self.assertIsNotNone(banked)
        self.assertEqual(h.census_count(banked), 103)


class Check4ConditionalNoteTest(unittest.TestCase):

    def test_r7_one_note_per_conditional_entry(self):
        output = _output("R7")
        notes = h.findings_for(output, rule=4, severity="Note")
        self.assertEqual(len(notes), 2)
        targets = sorted(h.finding_entry_id(note) for note in notes)
        conditional = sorted(
            h.entry_identifier(entry)
            for entry in h.entries_of(output)
            if h.entry_state(entry) == "Conditional")
        self.assertEqual(targets, conditional)

    def test_s5_open_entry_has_no_check4_note(self):
        output = _output("S5")
        self.assertEqual(h.findings_for(output, rule=4), [])


class Check5EvidencePresenceTest(unittest.TestCase):

    def test_s4_all_four_tests_fire_independently(self):
        output = _output("S4")
        findings = h.findings_for(output, rule=5)
        errors = [item for item in findings
                  if h.finding_severity(item) == "Error"]
        warnings = [item for item in findings
                    if h.finding_severity(item) == "Warning"]
        self.assertEqual(len(errors), 2)
        self.assertEqual(len(warnings), 2)
        self.assertEqual(h.exit_code_of(output), 1)
        entry = h.entry_by_id(output, "DQ-002")
        self.assertEqual(h.entry_state(entry), "Ruled")
        annotation = h.text_of(h.get(entry, "decider_annotation",
                                     "row_annotation"))
        label = h.text_of(h.get(entry, "decider_label"))
        self.assertTrue(annotation == "decider not recorded"
                        or label in (None, "", "decider not recorded"))

    def test_s4b_one_landing_warning_only(self):
        output = _output("S4b")
        findings = h.findings_for(output, rule=5)
        self.assertEqual(len(findings), 1)
        self.assertEqual(h.finding_severity(findings[0]), "Warning")
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s18_full_evidence_is_the_non_firing_side(self):
        output = _output("S18")
        self.assertEqual(h.findings_for(output, rule=5), [])

    def test_r6_three_entries_carry_no_evidence_findings(self):
        output = _output("R6")
        self.assertEqual(h.findings_for(output, rule=5), [])
        self.assertEqual(h.findings_for(output, rule=2), [])
        self.assertEqual(h.findings_for(output, rule=3), [])

    def test_check5_does_not_run_on_ambiguous_entries(self):
        for fixture_id in ("S17", "S20"):
            with self.subTest(fixture=fixture_id):
                output = _output(fixture_id)
                self.assertEqual(h.findings_for(output, rule=5), [])

    def test_s11_settled_part_evidence_is_scoped_to_the_part(self):
        output = _output("S11")
        self.assertEqual(h.findings_for(output, rule=5), [])


class Check5RecordedFormsTest(unittest.TestCase):
    """Check 5's tests are satisfied by the recorded label forms only.

    Pin 8 and brief section 5.5 rule check 5 over the recorded
    label forms of section 5.3. The shipped landing test was also
    satisfied by a body wide search for the word "landed", by any
    later Status line in the entry, and by any field label
    beginning "Decision"; the outcome test likewise by any
    "Decision" field label. The constructed entry below is seat
    2's rf20 shape: a Ruled entry with decider, ruling text and
    outcome in recorded forms, whose only landing-like text is
    the narrative sentence "the change landed somewhere last
    week" inside its ruling text. It must draw the landing
    Warning.
    """

    RF20_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: A ruled entry whose landing stands only in "
        "narrative\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"The change landed somewhere last week, "
        "and the item is closed.\"\n"
        "\n"
        "Ruling outcome: The item stands ruled and closed.\n")

    def test_rf20_draws_the_landing_warning(self):
        _model, output = h.run_pipeline(self.RF20_TEXT.encode())
        findings = h.findings_for(output, rule=5)
        self.assertEqual(len(findings), 1)
        self.assertEqual(h.finding_severity(findings[0]), "Warning")
        self.assertIn("landing",
                      (h.finding_statement(findings[0]) or "").lower())
        self.assertEqual(h.exit_code_of(output), 1)


class Check7UnclassifiedCensusTest(unittest.TestCase):

    def test_s20_unclassified_values_are_census_notes_not_findings(self):
        output = _output("S20")
        self.assertEqual(h.findings_for(output, rule=7), [])
        census = h.census_of(output)
        unclassified = h.census_class(census, "unclassified")
        self.assertIsNotNone(unclassified)
        self.assertEqual(h.census_count(unclassified), 2)

    def test_r1_has_no_unclassified_values(self):
        output = _output("R1")
        census = h.census_of(output)
        unclassified = h.census_class(census, "unclassified")
        if unclassified is not None:
            self.assertEqual(h.census_count(unclassified), 0)


class Check9OpenFieldsTest(unittest.TestCase):

    def test_s5b_one_warning_per_missing_field(self):
        output = _output("S5b")
        first = h.findings_for(output, entry_id="DQ-901", rule=9)
        second = h.findings_for(output, entry_id="DQ-902", rule=9)
        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 3)
        for finding in first + second:
            self.assertEqual(h.finding_severity(finding), "Warning")
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s5_complete_open_entry_does_not_fire(self):
        output = _output("S5")
        self.assertEqual(h.findings_for(output, rule=9), [])

    def test_s3b_complete_open_fields_do_not_fire(self):
        output = _output("S3b")
        self.assertEqual(h.findings_for(output, rule=9), [])


class Check10ParkedFormTest(unittest.TestCase):

    def test_s6_triggerless_entry_carries_the_error(self):
        output = _output("S6")
        errors = h.findings_for(output, rule=10, severity="Error")
        self.assertEqual(len(errors), 1)
        self.assertEqual(h.finding_entry_id(errors[0]), "DQ-002")
        self.assertEqual(h.exit_code_of(output), 1)

    def test_s3a_triggered_entry_carries_no_check10_finding(self):
        output = _output("S3a")
        self.assertEqual(h.findings_for(output, rule=10), [])


if __name__ == "__main__":
    unittest.main()
