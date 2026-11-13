"""Slice 3, Unit 3d, cross entry check group.

Check 8 in its limited form: citations, state claims and section
introduction counts in their named forms only. A mere mention does
not fire, a claim is reported as a claim and is never imported as
evidence for its target, a claim about an Ambiguous target is
reported as a claim with the target status named and no verdict, and
the amendment governing claim on a note segment is reported as a
claim and never applied. BQ-1, BQ-2 and BQ-3 are decided nowhere:
fixture S21 asserts the interim rule reporting only.
"""

import unittest

import dqv_harness as h


def _output(fixture_id):
    _model, output = h.cached_pipeline(fixture_id)
    return output


class CitationTest(unittest.TestCase):

    def test_r3_citation_of_a_number_with_no_heading_warns(self):
        output = _output("R3")
        warnings = h.findings_for(output, rule=8, severity="Warning")
        self.assertEqual(len(warnings), 1)
        blob = (h.finding_evidence_text(warnings[0]) + " " +
                (h.finding_statement(warnings[0]) or ""))
        self.assertIn("DQ-143", blob)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_r9_citations_warn_for_dq129_and_dq002(self):
        output = _output("R9")
        warnings = h.findings_for(output, rule=8, severity="Warning")
        self.assertEqual(len(warnings), 2)
        self.assertEqual(h.exit_code_of(output), 1)

    def test_r6_check8_dependent_count_is_zero(self):
        output = _output("R6")
        self.assertEqual(h.findings_for(output, rule=8), [])

    def test_r8_check8_citation_count_is_zero(self):
        output = _output("R8")
        self.assertEqual(h.findings_for(output, rule=8), [])
        # The exit is the derived manifest expectation: 1 since
        # the Step 19 R-08 fix, on DQ-130's check 5 landing
        # Warning; the check 8 citation count this test names
        # stands at 0.
        self.assertEqual(h.exit_code_of(output),
                         h.expected_exit("R8"))


class MentionAndClaimTest(unittest.TestCase):

    def test_s14_mere_mention_does_not_fire(self):
        output = _output("S14")
        warnings = h.findings_for(output, rule=8, severity="Warning")
        self.assertEqual(warnings, [])

    def test_s14_state_claim_fires_as_a_note_claim(self):
        output = _output("S14")
        notes = h.findings_for(output, rule=8, severity="Note")
        self.assertEqual(len(notes), 1)
        self.assertEqual(h.finding_entry_id(notes[0]), "DQ-902")
        blob = (h.finding_evidence_text(notes[0]) + " " +
                (h.finding_statement(notes[0]) or ""))
        self.assertIn("DQ-901", blob)
        self.assertIn("claim", blob.lower())
        self.assertEqual(h.exit_code_of(output), 0)

    def test_s14_claim_does_not_change_either_entry_state(self):
        output = _output("S14")
        first = h.entry_by_id(output, "DQ-901")
        second = h.entry_by_id(output, "DQ-902")
        self.assertEqual(h.entry_state(first), "Open")
        self.assertEqual(h.entry_state(second), "Open")


class AmbiguousTargetClaimTest(unittest.TestCase):

    def test_s21_claim_about_an_ambiguous_target(self):
        output = _output("S21")
        notes = h.findings_for(output, rule=8, severity="Note")
        self.assertEqual(len(notes), 1)
        blob = (h.finding_evidence_text(notes[0]) + " " +
                (h.finding_statement(notes[0]) or ""))
        self.assertIn("Ambiguous", blob)
        self.assertIn("claim", blob.lower())
        lowered = blob.lower()
        self.assertNotIn("stale", lowered)
        self.assertNotIn("agree", lowered)

    def test_s21_target_and_claiming_entry_states(self):
        output = _output("S21")
        target = h.entry_by_id(output, "DQ-901")
        claiming = h.entry_by_id(output, "DQ-902")
        self.assertTrue(h.is_ambiguous(target))
        self.assertEqual(h.entry_sub_label(target), "Conflict")
        self.assertEqual(h.entry_state(claiming), "Open")
        self.assertEqual(h.exit_code_of(output), 4)


class SectionIntroductionCountTest(unittest.TestCase):

    def test_r1_section_introduction_disagreement_is_a_warning(self):
        output = _output("R1")
        warnings = h.findings_for(output, rule=8, severity="Warning")
        self.assertEqual(len(warnings), 1)
        blob = (h.finding_evidence_text(warnings[0]) + " " +
                (h.finding_statement(warnings[0]) or ""))
        self.assertIn("6", blob)
        self.assertIn("14", blob)


class SegmentClaimTest(unittest.TestCase):

    def test_r8_amendment_claim_is_reported_and_never_applied(self):
        model, output = h.cached_pipeline("R8")
        orphans = h.as_list(h.get(model, "orphan_segments"))
        self.assertEqual(len(orphans), 3)
        claims = []
        for segment in orphans:
            claims.extend(h.as_list(h.get(segment, "claims",
                                          "named_entries", "entries_named")))
        render = h.render_text(output, "render")
        self.assertIn("claim", render.lower())
        entry = h.entry_by_id(output, "DQ-130")
        self.assertEqual(h.entry_state(entry), "Settled")


class StaleClaimNotesTest(unittest.TestCase):

    def test_r1_stale_claims_are_three_notes(self):
        output = _output("R1")
        notes = h.findings_for(output, rule=8, severity="Note")
        self.assertEqual(len(notes), 3)
        for note in notes:
            blob = (h.finding_evidence_text(note) + " " +
                    (h.finding_statement(note) or ""))
            self.assertIn("claim", blob.lower())


if __name__ == "__main__":
    unittest.main()
