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


def _run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def _ruled_entry(number, ruling_line):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: Ruled\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"%s\"\n\n"
        "Ruling outcome: The synthetic outcome stands.\n\n"
        "Where the ruling landed: synthetic record.\n\n"
        % (number, number, ruling_line))


def _plain_ruled(number):
    return _ruled_entry(number, "The synthetic ruling stands.")


_HEADER = "# Decision Queue\n\n## Open items\n\n"


def _by_rule(output, rule_text):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "") == rule_text]


def _mentioning(output, token):
    out = []
    for f in h.findings_of(output):
        blob = (h.finding_evidence_text(f) + " "
                + (h.finding_statement(f) or "") + " "
                + (h.text_of(h.get(f, "rule_id", "rule")) or ""))
        if token in blob:
            out.append(f)
    return out


def _pointers(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return [h.text_of(p) for p in h.as_list(
        h.get(entry, "supersession_pointers"))]


class Step17C4MissingTargetSingleNoteTest(unittest.TestCase):
    """M4, counted under both names: S17-ATK7-02 and Finding 2 of
    seat 9. A missing supersession target takes exactly one
    PD-R7 Note quoting the statement, and that Note is the only
    finding on the supersession ground."""

    def test_recognised_ghost_form_takes_one_pd_r7_note(self):
        # S17-ATK7-02 construction, seat 7 case G3 form.
        text = ("# Decision queue\n\n"
                "### DQ-113: Supersedes a ghost, recognised form\n\n"
                "Status: RULED, closed\n\n"
                "Ruled by: Captain JP\n\n"
                "Ruling: DQ-999 is superseded by this entry and is "
                "displaced by it.\n\n"
                "Outcome: Done.\n\n"
                "Landing: Recorded in the queue.\n")
        output = _run_text(text)
        pd_r7 = _by_rule(output, "PD-R7")
        self.assertEqual(len(pd_r7), 1)
        blob = (h.finding_evidence_text(pd_r7[0]) + " "
                + (h.finding_statement(pd_r7[0]) or ""))
        self.assertIn("DQ-999", blob)
        self.assertEqual(h.finding_severity(pd_r7[0]), "Note")
        self.assertEqual(
            len(_mentioning(output, "DQ-999")), 1,
            "a second finding stands on the supersession ground")

    def test_missing_target_in_citation_frame_takes_one_pd_r7(self):
        # Finding 2 of seat 9 construction, seat 9 case C4 form.
        text = (_HEADER + _plain_ruled(1) + _ruled_entry(
            2,
            "This ruling displaces the ruling at DQ-999 in full; "
            "that earlier ruling no longer stands as governing on "
            "its subject, and DQ-999 is the superseded entry."))
        output = _run_text(text)
        pd_r7 = _by_rule(output, "PD-R7")
        self.assertEqual(len(pd_r7), 1)
        self.assertEqual(
            h.findings_for(output, rule=8, severity="Warning"), [])
        self.assertEqual(
            len(_mentioning(output, "DQ-999")), 1,
            "the same statement is reported twice")


class Step17C4CycleThroughSecondPointerTest(unittest.TestCase):
    """Finding 1 of seat 9, its own charge: the cycle search
    follows every displacement target of each entry."""

    def test_cycle_through_second_pointer_takes_cycle_warning(self):
        # Seat 9 case C10 construction: DQ-001 displaces DQ-002
        # and DQ-003, DQ-003 displaces DQ-001. The cycle stands
        # through the second target only.
        text = (_HEADER
                + _ruled_entry(
                    1,
                    "This ruling displaces the rulings at DQ-002 "
                    "and DQ-003 in full; those earlier rulings no "
                    "longer stand as governing on their subjects, "
                    "and DQ-002 and DQ-003 are the superseded "
                    "entries.")
                + _plain_ruled(2)
                + _ruled_entry(
                    3,
                    "This ruling displaces the ruling at DQ-001 "
                    "in full; that earlier ruling no longer stands "
                    "as governing on its subject, and DQ-001 is "
                    "the superseded entry."))
        output = _run_text(text)
        warnings = [f for f in _by_rule(output, "PIN-10")
                    if h.finding_severity(f) == "Warning"
                    and "cycle" in (h.finding_statement(f) or "")]
        self.assertEqual(len(warnings), 1)
        blob = (h.finding_evidence_text(warnings[0]) + " "
                + (h.finding_statement(warnings[0]) or ""))
        self.assertIn("DQ-001", blob)
        self.assertIn("DQ-003", blob)


class Step17C4NearMissIdentificationTest(unittest.TestCase):
    """M5, counted under all three names: Finding 3 of seat 9,
    F-11-03, and A21-3. A named target the identification
    patterns do not reach takes the PIN-10 near miss Note, and
    the at form of a multi target supersession identifies every
    named target."""

    def test_case_variant_target_takes_near_miss_note(self):
        # Finding 3 of seat 9 construction, seat 9 case C9a form.
        text = (_HEADER + _plain_ruled(1) + _ruled_entry(
            2,
            "This ruling displaces the ruling at dq-001 in full; "
            "that earlier ruling no longer stands as governing on "
            "its subject, and dq-001 is the superseded entry."))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), [])
        notes = [f for f in _by_rule(output, "PIN-10")
                 if h.finding_severity(f) == "Note"
                 and "not recognised" in (h.finding_statement(f)
                                          or "")]
        self.assertEqual(len(notes), 1)
        blob = (h.finding_evidence_text(notes[0]) + " "
                + (h.finding_statement(notes[0]) or ""))
        self.assertIn("DQ-001", blob)

    def test_split_statement_takes_near_miss_note(self):
        # F-11-03 construction, seat 11 case c21 form: the
        # statement is split across two physical lines.
        text = ("# Decision queue\n\n"
                "### DQ-001: Open one\n\n"
                "Status: Banked\n\n"
                "Question: Q?\n\n"
                "Options: A, B\n\n"
                "Cost of deciding late: Late.\n\n"
                "Blocks: DQ-002\n\n"
                "Waiting prose here.\n\n"
                "### DQ-002: Ruled one\n\n"
                "Status: RULED, closed\n\n"
                "Ruled by: Captain JP\n\n"
                "Ruling text: \"Runs.\"\n\n"
                "Ruling outcome: It runs.\n\n"
                "Where the ruling landed: harbour file.\n\n"
                "### DQ-003: Later ruling\n\n"
                "Status: RULED, closed\n\n"
                "Ruled by: Captain JP\n\n"
                "Ruling text: \"This ruling supersedes\n"
                "the ruling at DQ-002.\"\n\n"
                "Ruling outcome: It replaces the earlier ruling.\n\n"
                "Where the ruling landed: harbour file.\n")
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-002"), [])
        notes = [f for f in _by_rule(output, "PIN-10")
                 if h.finding_severity(f) == "Note"
                 and "not recognised" in (h.finding_statement(f)
                                          or "")]
        self.assertEqual(len(notes), 1)
        blob = (h.finding_evidence_text(notes[0]) + " "
                + (h.finding_statement(notes[0]) or ""))
        self.assertIn("DQ-002", blob)

    def test_at_form_multi_target_identifies_every_target(self):
        # A21-3 construction: the at form naming two targets.
        text = ("# Decision queue\n\n"
                "### DQ-001: Entry 1\n\n"
                "Status: Banked\n\n"
                "Prose paragraph.\n\n"
                "### DQ-002: Entry 2\n\n"
                "Status: Banked\n\n"
                "Prose paragraph.\n\n"
                "### DQ-003: Entry 3\n\n"
                "Status: Banked\n\n"
                "Prose paragraph.\n\n"
                "This supersedes the ruling at DQ-001 and DQ-002.\n")
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-003"])
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-003"])
        notes = [f for f in _by_rule(output, "PIN-10")
                 if h.finding_severity(f) == "Note"
                 and "not recognised" in (h.finding_statement(f)
                                          or "")]
        self.assertEqual(notes, [])


def _c2_pd_r7_notes(output):
    return [finding for finding in h.findings_of(output)
            if str(h.get(finding, "rule_id", "rule")) == "PD-R7"]


class Step17C2CitedNumberTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge F-11-05: a cited DQ
    number with no heading, in entry body prose or in the file
    preamble, takes its PD-R7 report at Note grade."""

    _OPEN_ENTRY = (
        "### DQ-001: Open one\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Q?\n"
        "\n"
        "Options: A, B\n"
        "\n"
        "Cost of deciding late: Late.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "Waiting prose here.\n")

    def test_plain_citation_in_entry_prose_takes_pd_r7(self):
        data = ("# Decision queue\n\n" + self._OPEN_ENTRY +
                "\nSee DQ-099 for details.\n").encode("utf-8")
        _model, output = h.run_pipeline(data, "cited.md")
        notes = [note for note in _c2_pd_r7_notes(output)
                 if "DQ-099" in (h.finding_statement(note) or "")]
        self.assertEqual(len(notes), 1)
        self.assertEqual(h.finding_severity(notes[0]), "Note")

    def test_citations_in_the_preamble_take_pd_r7(self):
        data = ("# Decision queue\n"
                "\n"
                "This queue follows DQ-099 and DQ-098, which are "
                "still open.\n"
                "\n" + self._OPEN_ENTRY).encode("utf-8")
        _model, output = h.run_pipeline(data, "preamble.md")
        notes = _c2_pd_r7_notes(output)
        for number in ("DQ-099", "DQ-098"):
            named = [note for note in notes
                     if number in (h.finding_statement(note) or "")]
            self.assertEqual(len(named), 1, number)


class Step17C2StaleClaimPhrasingTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge F-11-06: stale cross
    entry state claims in the paper ordinary phrasings are
    reported as claims under rule 8, never applied."""

    _DATA = (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Open one\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Q?\n"
        "\n"
        "Options: A, B\n"
        "\n"
        "Cost of deciding late: Late.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "DQ-002 is still open.\n"
        "\n"
        "DQ-002 remains banked.\n"
        "\n"
        "The DQ-002 question is still waiting for a decision.\n"
        "\n"
        "Waiting prose here.\n"
        "\n"
        "### DQ-002: Ruled one\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"Runs.\"\n"
        "\n"
        "Ruling outcome: It runs.\n"
        "\n"
        "Where the ruling landed: harbour file.\n"
    ).encode("utf-8")

    def test_all_three_plain_phrasings_are_reported_as_claims(self):
        _model, output = h.run_pipeline(self._DATA, "stale.md")
        notes = h.findings_for(output, entry_id="DQ-001", rule=8,
                               severity="Note")
        claims = [note for note in notes
                  if "claim" in (h.finding_statement(note)
                                 or "").lower()]
        self.assertEqual(len(claims), 3)
        entry = h.entry_by_id(output, "DQ-002")
        self.assertEqual(h.entry_state(entry), "Ruled")


class Step17FixC2SuppQuarantinedHeadingCitationTest(unittest.TestCase):
    """Step 17 fix wave 1, supplementary seat, charge F-2 of
    seat 4, citation limb (cluster C1 with a C2 limb): the
    citation scan does not manufacture a Note grade citation
    from the quarantined heading line of an entry whose
    identifier carries a combining mark or a zero width
    character (seat 4 cases v1 and v2). The quarantined
    heading stands under PIN-06; the heading line itself is
    not a citation of any number."""

    _BODY = (
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-999\n"
        "\n"
        "A plain paragraph of context for this entry.\n")

    def _run(self, quarantined_heading):
        text = ("# Decision queue\n"
                "\n"
                "### DQ-002: Valid companion\n"
                + self._BODY +
                "\n"
                + quarantined_heading + "\n"
                + self._BODY)
        return _run_text(text)

    def _manufactured(self, output, number):
        return [note for note in _c2_pd_r7_notes(output)
                if h.finding_severity(note) == "Note"
                and number in (h.finding_statement(note) or "")]

    def test_zwsp_heading_manufactures_no_dq000_note(self):
        # Seat 4 case v2: DQ-00, zero width space U+200B, 1.
        # No DQ-000 token stands anywhere in the file as
        # written, so no PD-R7 Note may name DQ-000.
        output = self._run(
            "### DQ-00​1: Zero width space in identifier")
        self.assertEqual(self._manufactured(output, "DQ-000"), [])
        self.assertEqual(len(_by_rule(output, "PIN-06")), 1)
        self.assertGreaterEqual(
            len(self._manufactured(output, "DQ-999")), 1)

    def test_combining_heading_manufactures_no_dq001_note(self):
        # Seat 4 case v1: DQ-001 with a combining acute
        # U+0301 inside the identifier, beside valid DQ-002.
        # The only DQ-001 form in the file is the corrupted
        # heading token itself, so no PD-R7 Note may name
        # DQ-001 as cited.
        output = self._run(
            "### DQ-001́: Combining mark in identifier")
        self.assertEqual(self._manufactured(output, "DQ-001"), [])
        self.assertEqual(len(_by_rule(output, "PIN-06")), 1)
        self.assertGreaterEqual(
            len(self._manufactured(output, "DQ-999")), 1)


if __name__ == "__main__":
    unittest.main()
