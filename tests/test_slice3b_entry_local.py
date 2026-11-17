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


class Step17FixC1ContainerTest(unittest.TestCase):
    """Merger M6: F-11-01 and F-11-02, container awareness in parse.

    Matter inside an HTML comment satisfies no presence test, and
    fields inside a code fence satisfy no field test. Both names
    are pinned here, one charge at the shared parse root.
    """

    def test_f11_01_comment_matter_satisfies_no_presence_test(self):
        # The seat 11 minimal reproduction: a decided entry whose
        # only decider, ruling text, outcome, and landing record
        # stand inside an HTML comment.
        body = h._header_block()
        body += "### DQ-001: Ruled one\n\nStatus: RULED, closed\n\n"
        body += "<!--\nRuled by: Captain JP\n"
        body += "Ruling text: \"Runs.\"\n"
        body += "Ruling outcome: It runs.\n"
        body += "Where the ruling landed: harbour file.\n-->\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "comment_evidence.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=5))

    def test_f11_02_fenced_fields_satisfy_no_field_test(self):
        body = h._header_block()
        body += "### DQ-001: A sample open question\n\nStatus: Banked\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += "```\nQuestion: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n```\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "fenced_fields.md")
        self.assertTrue(h.findings_for(output, entry_id="DQ-001",
                                       rule=9, severity="Warning"))


def _c2_open_entry(heading, options_line="Options: Option A, Option B",
                   question_line="Question: Which option should we take?",
                   cost_line="Cost of deciding late: Work stays blocked.",
                   blocks_line="Blocks: DQ-002"):
    return (
        "### %s\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "This question is waiting for a decision.\n"
        "\n"
        "%s\n"
        "\n"
        "%s\n"
        "\n"
        "%s\n"
        "\n"
        "%s\n" % (heading, question_line, options_line, cost_line,
                  blocks_line))


def _c2_queue(*entries):
    return ("# Decision queue\n\n" + "\n".join(entries)).encode("utf-8")


def _c2_pd_r7_notes(output):
    return [finding for finding in h.findings_of(output)
            if str(h.get(finding, "rule_id", "rule")) == "PD-R7"]


class Step17C2Check1R7DuplicateTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, Finding 1 of seat 6: check 1
    covers the recognised unnumbered identifier R-7 as it covers
    DQ numbers, so a duplicated R-7 heading takes the duplicate
    entry number Error."""

    def test_duplicate_r7_heading_takes_a_rule1_error(self):
        body = _c2_open_entry("R-7 closure conflict")
        data = _c2_queue(body, body,
                         _c2_open_entry("DQ-002: Second question"))
        _model, output = h.run_pipeline(data, "r7_dup.md")
        errors = h.findings_for(output, rule=1, severity="Error")
        self.assertEqual(len(errors), 1)
        blob = (h.finding_evidence_text(errors[0]) + " " +
                (h.finding_statement(errors[0]) or ""))
        self.assertIn("R-7", blob)


class Step17C2Check5GhostEvidenceTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge S17-ATK7-01: decision
    evidence that names a different entry with no heading is not
    accepted as the host entry own evidence in silence; the
    cited ghost number takes its PD-R7 Note."""

    def test_ruling_text_naming_a_ghost_entry_takes_pd_r7(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-106: Ruling text names another entry\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            "Ruled by: Captain JP\n"
            "\n"
            "Ruling text: \"Settle DQ-999 as follows.\"\n"
            "\n"
            "Ruling outcome: DQ-999 is decided and closed.\n"
            "\n"
            "Where the ruling landed: NOWHERE.md, sample rule.\n"
            "\n"
            "#### Ruling by Captain JP\n"
            "\n"
            "Ruled: DQ-999 is closed by this ruling. Closed.\n"
        ).encode("utf-8")
        _model, output = h.run_pipeline(data, "ghost_ruling.md")
        notes = _c2_pd_r7_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(h.finding_severity(notes[0]), "Note")
        self.assertIn("DQ-999", h.finding_statement(notes[0]) or "")

    def test_settlement_block_naming_a_ghost_entry_takes_pd_r7(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-112: Settlement block for another entry\n"
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
            "This question is waiting for a decision.\n"
            "\n"
            "#### Settlement under Captain JP's pass 2 grant: DQ-999\n"
            "\n"
            "Settled by: The Manager, under the pass 2 grant.\n"
            "\n"
            "Settlement: DQ-999 is settled in full. "
            "This item is settled.\n"
            "\n"
            "Status: SETTLED by the Manager under the pass 2 grant. "
            "This item is settled.\n"
        ).encode("utf-8")
        _model, output = h.run_pipeline(data, "ghost_settlement.md")
        notes = _c2_pd_r7_notes(output)
        self.assertGreaterEqual(len(notes), 1)
        joined = " ".join(h.finding_statement(note) or ""
                          for note in notes)
        self.assertIn("DQ-999", joined)


class Step17C2UnclassifiedNoteTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge S17-ATK7-05, on its
    own construction only: a lone entry whose only status value
    is unclassified takes the Note finding brief section 5.4
    lists for an unclassified status value. This charge does
    not cure, restate, or extend A12-F5, which stands CONFIRMED
    ONLY on its own multi entry construction."""

    def test_lone_unclassified_value_takes_a_note(self):
        data = _c2_queue(_c2_open_entry(
            "DQ-105: Undefined state name two").replace(
                "Status: Banked", "Status: Done"))
        _model, output = h.run_pipeline(data, "undefined.md")
        notes = [finding for finding in h.findings_for(
            output, entry_id="DQ-105", severity="Note")
            if "unclassified" in (h.finding_statement(finding)
                                  or "").lower()]
        self.assertEqual(len(notes), 1)


class Step17C2Check9EmptyFieldValueTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge F-17-02: an open
    entry field presence test reads the value, not the label
    alone, so a field label carrying an empty value takes the
    rule 9 missing field Warning for that field."""

    def _warnings_for(self, **kwargs):
        data = _c2_queue(_c2_open_entry("DQ-001: One question",
                                        **kwargs))
        _model, output = h.run_pipeline(data, "empty_field.md")
        return h.findings_for(output, entry_id="DQ-001", rule=9,
                              severity="Warning")

    def test_empty_question_value_is_missing(self):
        warnings = self._warnings_for(question_line="Question:")
        self.assertEqual(len(warnings), 1)
        self.assertIn("question",
                      (h.finding_statement(warnings[0]) or "").lower())

    def test_empty_options_value_is_missing(self):
        warnings = self._warnings_for(options_line="Options:")
        self.assertEqual(len(warnings), 1)
        self.assertIn("options",
                      (h.finding_statement(warnings[0]) or "").lower())

    def test_empty_cost_value_is_missing(self):
        warnings = self._warnings_for(
            cost_line="Cost of deciding late:")
        self.assertEqual(len(warnings), 1)
        self.assertIn("cost of deciding late",
                      (h.finding_statement(warnings[0]) or "").lower())

    def test_empty_blocks_value_is_missing(self):
        warnings = self._warnings_for(blocks_line="Blocks:")
        self.assertEqual(len(warnings), 1)
        self.assertIn("blocks",
                      (h.finding_statement(warnings[0]) or "").lower())


class Step17C2OptionsExactnessTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge F-17-07: the Options
    presence test stands at the same exactness as its sibling
    field tests, with no stripped line fallback, so the leading
    space, tab separator, and no space forms that every sibling
    label rejects are rejected for Options too."""

    def _options_warnings(self, options_line):
        data = _c2_queue(_c2_open_entry("DQ-001: One question",
                                        options_line=options_line))
        _model, output = h.run_pipeline(data, "options_form.md")
        return [finding for finding in h.findings_for(
            output, entry_id="DQ-001", rule=9, severity="Warning")
            if "options" in (h.finding_statement(finding)
                             or "").lower()]

    def test_leading_space_options_line_is_missing(self):
        warnings = self._options_warnings(
            " Options: Option A, Option B")
        self.assertEqual(len(warnings), 1)

    def test_tab_separator_options_line_is_missing(self):
        warnings = self._options_warnings(
            "Options:\tOption A, Option B")
        self.assertEqual(len(warnings), 1)

    def test_no_space_options_line_is_missing(self):
        warnings = self._options_warnings("Options:Option A, Option B")
        self.assertEqual(len(warnings), 1)

    def test_taught_options_line_still_satisfies(self):
        warnings = self._options_warnings("Options: Option A, Option B")
        self.assertEqual(warnings, [])


class Step17Fix1bD1ProseOptionsTest(unittest.TestCase):
    """Step 17 fix wave 1 supplementary repair, seat D1: the
    corpus prose options form, the line "The options, stated
    plainly:" with its option lines following, counts as
    options present, as it did before fix wave 1. Fix C2
    charges 11 and 12 removed the stripped body line fallback
    that also served this form, although the charges named
    only the leading space, tab separator, and no space forms
    of the Options label, and the empty value ground. This
    pin stands beside those charges: the prose form reads
    present, and no charged form is reopened by it."""

    def _options_warnings(self, options_block):
        data = _c2_queue(_c2_open_entry("DQ-001: One question",
                                        options_line=options_block))
        _model, output = h.run_pipeline(data, "prose_options.md")
        return [finding for finding in h.findings_for(
            output, entry_id="DQ-001", rule=9, severity="Warning")
            if "options" in (h.finding_statement(finding)
                             or "").lower()]

    def test_prose_options_form_reads_present(self):
        warnings = self._options_warnings(
            "The options, stated plainly:\n"
            "\n"
            "- Option A: adopt the note as written.\n"
            "- Option B: leave the note unadopted.")
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
