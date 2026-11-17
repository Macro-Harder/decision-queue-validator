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


class EffectiveElementsExceptionTest(unittest.TestCase):
    """Derivation sets no element aside beyond the named exceptions.

    Brief section 5.4 states the determining element is the last
    element in element order subject to the exceptions named in
    that sentence and nowhere else (pin 16, pin 2 shape A, and the
    unparsed entry precedence), and that no other exception exists.
    The constructed entry below is the rf17 shape: a settled entry
    whose last element states what remains open. Under the mapping
    table that last element, in an entry carrying decision
    evidence, reaches the totality row and reports Ambiguous. The
    shipped derivation set the element aside and reported Settled
    with no findings at exit 0.
    """

    RF17_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: A question with a limb still open\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Owner of record: Decision-queue Clerk\n"
        "\n"
        "The question: Should the whole item be settled now?\n"
        "\n"
        "Options:\n"
        "- Option A: settle the whole item.\n"
        "- Option B: settle part of it.\n"
        "\n"
        "Cost of deciding late: moderate.\n"
        "\n"
        "What it blocks: the closing note.\n"
        "\n"
        "#### Settlement by the Manager\n"
        "\n"
        "Settled by: The Manager (Muse), under the grant.\n"
        "\n"
        "Ruling text: \"The main limb is settled.\"\n"
        "\n"
        "Decision: The main limb is settled and takes effect at "
        "once.\n"
        "\n"
        "Landing: the closing note.\n"
        "\n"
        "Status: SETTLED by the Manager under the grant. The item "
        "is settled.\n"
        "\n"
        "What remains open: the budget limb of this item stays "
        "undecided.\n")

    def test_rf17_last_element_stating_what_remains_open_is_ambiguous(self):
        _model, output = h.run_pipeline(self.RF17_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertIsNotNone(entry)
        self.assertTrue(h.is_ambiguous(entry))
        self.assertEqual(h.ambiguous_count(output), 1)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled"), 0)
        self.assertEqual(h.exit_code_of(output), 4)


class ClosingLineForDeterminationTest(unittest.TestCase):
    """An element opening "Closing line for" determines the state.

    Brief section 5.4 states the determining element is the last
    element in element order subject to the exceptions named in
    that sentence and nowhere else, and that no other exception
    exists. The constructed entry below is a settled entry whose
    last element is a paragraph opening "Closing line for" that
    states a ruling in full. That paragraph is in form a ruling
    paragraph, and under the mapping table the entry derives
    Ruled on it. The shipped derivation set the element aside
    under its opening words alone and reported Settled. This is
    register item R-04 limb C, reopened by the Step 19 re-audit
    of the first fix performance: no brief pinned expectation
    rests on the set aside, and every expectation it moves is
    labelled derived.
    """

    CLOSING_LINE_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: A settled entry whose last element is a "
        "ruling paragraph\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Owner of record: Decision-queue Clerk\n"
        "\n"
        "The question: Should the whole item be settled now?\n"
        "\n"
        "Options:\n"
        "- Option A: settle the whole item.\n"
        "- Option B: settle part of it.\n"
        "\n"
        "Cost of deciding late: moderate.\n"
        "\n"
        "What it blocks: the closing note.\n"
        "\n"
        "#### Settlement by the Manager\n"
        "\n"
        "Settled by: The Manager (Muse), under the grant.\n"
        "\n"
        "Ruling text: \"The main limb is settled.\"\n"
        "\n"
        "Decision: The main limb is settled and takes effect at "
        "once.\n"
        "\n"
        "Landing: the closing note.\n"
        "\n"
        "Status: SETTLED by the Manager under the grant. The item "
        "is settled.\n"
        "\n"
        "Closing line for the held bundle: the last held item is "
        "RULED by Captain JP and closed. Her answer: \"No, only "
        "the failing one.\" Outcome: the estate wide drop is "
        "declined.\n")

    def test_closing_line_paragraph_is_the_determining_element(self):
        _model, output = h.run_pipeline(
            self.CLOSING_LINE_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertIsNotNone(entry)
        self.assertEqual(h.entry_state(entry), "Ruled")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Ruled"), 1)
        self.assertEqual(counts.get("Settled"), 0)


class StaysBankedDeterminationTest(unittest.TestCase):
    """An element noting another question stays banked determines.

    Brief section 5.4 states the determining element is the last
    element in element order subject to the exceptions named in
    that sentence and nowhere else, and that no other exception
    exists. The constructed entry below is a ruled entry whose
    last status bearing element is its ruling outcome paragraph,
    which records that another entry's question stays banked and
    is not decided by this ruling. That paragraph carries the
    Banked disposition on its own statement, and under the
    mapping table an entry carrying decision evidence whose last
    element stands undecided reaches the totality row and
    reports Ambiguous. The shipped derivation set the element
    aside for containing "stays banked" with a not decided
    clause, and reported Ruled. This is register item R-04
    limb D, reopened by the Step 19 re-audit of the first fix
    performance: no brief pinned expectation rests on the set
    aside, and every expectation it moves is labelled derived.
    The shape mirrors fixture R1's DQ-138 entry in form.
    """

    STAYS_BANKED_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: A ruled entry whose outcome notes another "
        "question stays banked\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Owner of record: Decision-queue Clerk\n"
        "\n"
        "Ruling text: \"Yes, the gate always wins.\"\n"
        "\n"
        "Source: a banked run. The run recorded one open "
        "principle at DQ-070.\n"
        "\n"
        "The question that was open: Which governs?\n"
        "\n"
        "Ruling outcome: The corpus gate governs. This settles "
        "the open principle recorded at DQ-070; DQ-070's own "
        "question stays banked and is not decided by this "
        "ruling.\n"
        "\n"
        "Where the ruling landed:\n"
        "\n"
        "- This queue: this entry is the record of the ruling.\n")

    def test_stays_banked_outcome_element_is_the_determining_element(self):
        _model, output = h.run_pipeline(
            self.STAYS_BANKED_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertIsNotNone(entry)
        self.assertTrue(h.is_ambiguous(entry))
        self.assertEqual(h.ambiguous_count(output), 1)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Ruled"), 0)
        self.assertEqual(h.exit_code_of(output), 4)


class DeciderLabelNoFallbackTest(unittest.TestCase):
    """A decider label comes from the determining element alone.

    Brief section 5.4 rules a row whose determining element names
    no decider carries no label and counts in no decider subtotal,
    with "decider not recorded" in its place; brief section 7.3
    rules the render preserves that distinction. The constructed
    entry is the rf19c shape: a head Status line naming Captain JP
    and a determining element, a later Status line reading
    "SETTLED, closed.", naming no decider. The shipped derivation
    fell back to the head line and printed the label "Ruled by
    Captain JP" on a Settled row, counting it in that subtotal.
    """

    RF19C_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: A question settled with no decider on its "
        "determining element\n"
        "\n"
        "Status: Ruled by Captain JP\n"
        "\n"
        "Owner of record: Decision-queue Clerk\n"
        "\n"
        "The question: Should the item be settled now?\n"
        "\n"
        "Options:\n"
        "- Option A: settle it now.\n"
        "- Option B: wait.\n"
        "\n"
        "Cost of deciding late: moderate.\n"
        "\n"
        "What it blocks: the closing note.\n"
        "\n"
        "Status: SETTLED, closed.\n")

    def test_rf19c_row_carries_no_label_and_counts_in_no_subtotal(self):
        _model, output = h.run_pipeline(self.RF19C_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertIsNotNone(entry)
        self.assertEqual(h.entry_state(entry), "Settled")
        self.assertIsNone(
            h.text_of(h.get(entry, "decider_label", "decider")))
        annotation = h.text_of(h.get(
            entry, "decider_annotation", "annotation"))
        self.assertEqual(annotation, "decider not recorded")
        subtotals = h.get(output, "decider_subtotals",
                          "decider_counts")
        counts = {h.text_of(key): h.int_of(value)
                  for key, value in subtotals.items()}
        self.assertEqual(counts.get("Ruled by Captain JP", 0), 0)


class CompletedByStaysClosedTest(unittest.TestCase):
    """A completion form is a decider label on a Closed row, not a settlement.

    The mapping table's Closed row is complete on this shape:
    disposition Closed without a ruling or settlement form, scope
    Whole, condition None, maps to Closed as decided, and brief
    section 5.4's decider label list already provides "completion
    under DQ-145" as a label carried on Closed rows. The shipped
    _derive read a determining element of disposition Closed as
    Settled where its statement contains "Completed by", so seat
    2's rf18 shape rendered in the Settled group. Limb (a) of the
    same register item, the closing prose re-reading, is a design
    question (DQ-R8) and is not touched here.
    """

    RF18_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: An item closed by a completion form\n"
        "\n"
        "Status: Closed. Completed by the Manager under DQ-145.\n")

    def test_rf18_completion_form_derives_closed_as_decided(self):
        _model, output = h.run_pipeline(self.RF18_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(entry), "Closed as decided")
        self.assertEqual(
            h.text_of(h.get(entry, "decider_label")),
            "completion under DQ-145")
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled"), 0)
        self.assertEqual(counts.get("Closed as decided"), 1)


class ConditionOnUnclassifiableTest(unittest.TestCase):
    """A Condition line never converts an unclassifiable element.

    Pin 2 governs an unclassifiable value: it is never assigned a
    disposition, shape B (the only Status line of an entry carrying
    decision evidence, or the last element after classifiable
    elements) reports as Ambiguous, and pin 8 bars check 5 on an
    Ambiguous entry. A Condition label line attaches to the tuple
    of the disposition None element, and the shipped derivation
    tested the condition before the disposition None branch, so
    the entry reported Conditional and collected check 5 Errors.
    Classifiable dispositions carrying a Condition line keep
    reporting Conditional under the mapping table row, which the
    two control tests pin.
    """

    EVIDENCE_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: An entry with decision evidence and one "
        "unclassifiable Status line\n"
        "\n"
        "Owner of record: Decision-queue Clerk\n"
        "\n"
        "The question: What does derivation do when the only "
        "Status line is unclassifiable and decision evidence "
        "stands in a block?\n"
        "\n"
        "#### Assessment and settlement record\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"The block records a ruling on this "
        "item.\"\n"
        "\n"
        "Status: To be classified\n"
        "\n"
        "Condition: the budget is approved\n")

    LITERAL_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: An entry whose only Status line is "
        "unclassifiable\n"
        "\n"
        "Status: To be classified\n"
        "\n"
        "Condition: the budget is approved\n")

    BANKED_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: A banked entry carrying a Condition line\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "The question: Should this item wait on the budget?\n"
        "\n"
        "Options:\n"
        "- Option A: wait.\n"
        "- Option B: proceed.\n"
        "\n"
        "Cost of deciding late: low.\n"
        "\n"
        "What it blocks: the closing note.\n"
        "\n"
        "Condition: the budget is approved\n")

    PARKED_TEXT = (
        "# Decision queue\n"
        "\n"
        "### DQ-901: A parked entry carrying a Condition line\n"
        "\n"
        "Status: Parked\n"
        "\n"
        "Reopening trigger: the budget round opens.\n"
        "\n"
        "Condition: the budget is approved\n")

    def test_evidence_shape_reports_ambiguous_with_no_check5(self):
        _model, output = h.run_pipeline(self.EVIDENCE_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(entry), "Ambiguous")
        self.assertEqual(h.findings_for(output, rule=5), [])
        self.assertEqual(h.exit_code_of(output), 4)

    def test_literal_shape_reports_open_not_conditional(self):
        _model, output = h.run_pipeline(self.LITERAL_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(entry), "Open")
        self.assertEqual(h.findings_for(output, rule=5), [])

    def test_banked_with_condition_stays_conditional(self):
        _model, output = h.run_pipeline(self.BANKED_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(entry), "Conditional")

    def test_parked_with_condition_stays_conditional(self):
        _model, output = h.run_pipeline(self.PARKED_TEXT.encode())
        entry = h.entry_by_id(output, "DQ-901")
        self.assertEqual(h.entry_state(entry), "Conditional")


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

    def test_r5_status_line_deciders_carry_no_label(self):
        # Brief section 5.4 rules the label off the determining
        # element alone. In fixture R5 the entries DQ-149 to DQ-152
        # name their decider only in their head Status line, which
        # reads "Ruled by Captain JP"; their determining elements
        # name no decider. The entries therefore carry no label and
        # the "decider not recorded" annotation stands. An earlier
        # form of this test pinned the fallback to the Status line;
        # that fallback was defect R-05, removed at Step 19, and
        # this expectation now follows the brief text.
        for entry_id in ("DQ-149", "DQ-150", "DQ-151", "DQ-152"):
            with self.subTest(entry=entry_id):
                entry, label = self._label("R5", entry_id)
                self.assertEqual(h.entry_state(entry), "Ruled")
                self.assertIsNone(label)
                annotation = h.text_of(h.get(
                    entry, "decider_annotation", "annotation"))
                self.assertEqual(annotation, "decider not recorded")

    def test_r5_entries_with_no_decider_form_stay_unlabelled(self):
        # DQ-154 and DQ-155 in R5 name no decider in any section 5.3
        # form: their Origin lines pass no decider form. They stay
        # unlabelled with the annotation standing.
        for entry_id in ("DQ-154", "DQ-155"):
            with self.subTest(entry=entry_id):
                entry, label = self._label("R5", entry_id)
                self.assertIsNone(label)
                annotation = h.text_of(h.get(
                    entry, "decider_annotation", "annotation"))
                self.assertEqual(annotation, "decider not recorded")

    def test_r5_decider_subtotal_counts_the_status_line_deciders(self):
        # Derived from the R5 fixture text under the brief section
        # 5.4 rule as cured at Step 19 (defect R-05): DQ-149 to
        # DQ-152 name Captain JP only in the Status line and count
        # in no subtotal (0), DQ-153 carries the label through its
        # determining closing prose (1), DQ-156 through its
        # determining heading (1), and DQ-154 and DQ-155 name no
        # decider (0). Total 2.
        _model, output = h.cached_pipeline("R5")
        subtotals = h.get(output, "decider_subtotals", "decider_counts")
        counts = {h.text_of(key): h.int_of(value)
                  for key, value in subtotals.items()}
        self.assertEqual(counts["Ruled by Captain JP"], 2)

    def test_r1_status_line_deciders_carry_no_label(self):
        # Register D-09's dialect on R1: DQ-147 and DQ-148 name
        # their decider only in the head Status line, in the same
        # form as the R5 entries above. Under the brief section 5.4
        # rule as cured at Step 19 (defect R-05) they carry no
        # label and the annotation stands.
        for entry_id in ("DQ-147", "DQ-148"):
            with self.subTest(entry=entry_id):
                entry, label = self._label("R1", entry_id)
                self.assertEqual(h.entry_state(entry), "Ruled")
                self.assertIsNone(label)
                annotation = h.text_of(h.get(
                    entry, "decider_annotation", "annotation"))
                self.assertEqual(annotation, "decider not recorded")


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
        # 5 since the Step 19 R-04 limb D fix: DQ-138, DQ-141, and
        # DQ-145 report Ambiguous, as the fix register records.
        self.assertEqual(h.ambiguous_count(output), 5)
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
        # 5 since the Step 19 R-04 limb D fix, on the same entries
        # as R1, as the fix register records.
        self.assertEqual(h.ambiguous_count(output), 5)
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


class ManifestCanonicalSplitSumsTest(unittest.TestCase):
    """Step 19 Wave 29 records fix: the JSON canonical splits sum.

    Each split in manifest.json must sum to its headed entries:
    the eight canonical states plus its Ambiguous count plus its
    unparsed count equals headed_entries. The R-04 limb D fix
    moved DQ-138, DQ-141, and DQ-145 to Ambiguous (5 in both R1
    and R2), and the splits must carry that count, as MANIFEST.md
    already states, so the splits sum.
    """

    _STATES = ("Open", "Presented", "Parked", "Ruled", "Settled",
               "Settled in part", "Closed as decided", "Conditional")

    def _assert_split_sums(self, split):
        total = sum(split[state] for state in self._STATES)
        total += split["Ambiguous"] + split["unparsed"]
        self.assertEqual(total, split["headed_entries"])

    def test_canonical_split_r1_sums_and_counts_five_ambiguous(self):
        split = h.manifest()["corpus_structure_splits"][
            "canonical_split_R1"]
        self.assertEqual(split["Ambiguous"], 5)
        self._assert_split_sums(split)

    def test_canonical_split_r2_sums_and_counts_five_ambiguous(self):
        split = h.manifest_entry("R2")["expected_counts"][
            "canonical_split"]
        self.assertEqual(split["Ambiguous"], 5)
        self._assert_split_sums(split)


class Step17FixC1DerivationTest(unittest.TestCase):
    """F-17-01 derivation surface: an empty Status value is not a
    phrasing, so the Shape A exception does not derive Open."""

    def test_f17_01_empty_status_value_does_not_derive_open(self):
        body = h._header_block()
        body += "### DQ-001: A sample open question\n\nStatus:\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n"
        _model, output = h.run_pipeline(body.encode("utf-8"),
                                        "empty_status_derivation.md")
        entry = h.entry_by_id(output, "DQ-001")
        self.assertIsNotNone(entry)
        self.assertNotEqual(h.entry_state(entry), "Open")


class Step17C2ClosingProseClaimTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge S17-ATK7-04, bounded
    to closing prose the tool itself treats as a status bearing
    element: closing prose named as the determining element,
    stating in words that the entry was ruled and closed, does
    not derive Open in silence; it takes the status elements
    disagree treatment."""

    def test_ruled_and_closed_closing_prose_does_not_derive_open(self):
        data = (
            "# Decision queue\n"
            "\n"
            "### DQ-102: Banked head, closed body\n"
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
            "This entry was ruled by Captain JP yesterday and is "
            "now closed. Nothing remains open on it.\n"
        ).encode("utf-8")
        _model, output = h.run_pipeline(data, "contradict_body.md")
        entry = h.entry_by_id(output, "DQ-102")
        self.assertEqual(h.entry_state(entry), "Ambiguous")


class Step17C2BareClosingSentenceTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge A10-F1: under the
    PIN-11 concordance rule a bare closing sentence at the end
    of an entry paragraph confirms a tail heading denoting
    Ruled and denotes no separate Closed state, while the same
    sentence under a heading denoting no decided disposition
    keeps its own Closed state."""

    _DATA = (
        "# Decision queue\n"
        "\n"
        "## DQ-001: the harbour light rota. "
        "RULED by Captain JP 2026-11-15\n"
        "\n"
        "The harbour light rota was drawn up by the Clerk from "
        "the winter watch list, and the rota names the keeper "
        "for each night of the week in a single table at the "
        "end of the note. Closed.\n"
        "\n"
        "## DQ-002: the ferry crew rota. BANKED 2026-11-15\n"
        "\n"
        "The ferry crew rota was drawn up by the Clerk from "
        "the winter sailing list, and the rota names the crew "
        "for each sailing of the week in a single table at the "
        "end of the note. Closed.\n"
    ).encode("utf-8")

    def test_closing_sentence_confirms_the_ruled_heading(self):
        _model, output = h.run_pipeline(self._DATA, "tail.md")
        entry = h.entry_by_id(output, "DQ-001")
        self.assertEqual(h.entry_state(entry), "Ruled")

    def test_closing_sentence_under_a_banked_heading_stays_closed(self):
        _model, output = h.run_pipeline(self._DATA, "tail.md")
        entry = h.entry_by_id(output, "DQ-002")
        self.assertEqual(h.entry_state(entry), "Closed as decided")


class Step17C2PartScopeExtractionTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge A10-F5: part scope
    is extracted from a recognised Ruled by paragraph whose
    statement limits the act to a named part, and its named
    remainder is counted, so the entry derives Settled in
    part under PIN-03."""

    _PARAGRAPH = (
        "Ruled by Captain JP: the first part is ruled, take "
        "Option A. The remainder, the second part, still "
        "stands open.\n")

    def _entry(self, number, title):
        return (
            "### DQ-%03d: %s\n"
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
            "A plain context paragraph.\n"
            "\n"
            "%s" % (number, title, self._PARAGRAPH))

    def test_ruled_by_paragraph_part_scope_derives_settled_in_part(self):
        data = ("# Decision queue\n\n" + self._entry(
            2, "One remainder one entry")).encode("utf-8")
        _model, output = h.run_pipeline(data, "part_scope.md")
        entry = h.entry_by_id(output, "DQ-002")
        self.assertEqual(h.entry_state(entry), "Settled in part")
        remainder = h.get(entry, "remainder_text", "remainder")
        self.assertIn("second part", remainder or "")

    def test_validate_scope_extraction_from_the_statement_itself(self):
        # The charge locus is validate: an element whose recorded
        # scope stands Whole, but whose statement in words limits
        # the ruling to a named part and names its remainder in
        # the stands open form, takes the part scope and the
        # remainder in validate derivation.
        import types as _types
        validate_module = h.import_module("validate")

        def element(kind, disposition, statement, line):
            return _types.SimpleNamespace(
                kind=kind, disposition=disposition, scope="Whole",
                condition=None, remainder_text=None, decider=None,
                decider_text=None, statement=statement,
                verbatim=statement, line=line, occurrence_kind=None)

        head = element("line start Status line", "Banked",
                       "Banked", 5)
        head.occurrence_kind = "line start"
        ruling = element(
            "closing prose", "Ruled",
            "Ruled by Captain JP: the first part is ruled, take "
            "Option A. The remainder, the second part, still "
            "stands open.", 17)
        ruling.decider = "Captain JP"
        entry = _types.SimpleNamespace(
            identifier="DQ-002", heading="DQ-002: One remainder",
            heading_text="DQ-002: One remainder", unparsed=False,
            status_elements=[head, ruling], body_lines=[],
            fields=[])
        derived = validate_module._derive(entry)
        self.assertEqual(derived["state"], "Settled in part")
        self.assertIn("second part", derived["remainder"] or "")


class Step17C2StatusConditionTest(unittest.TestCase):
    """Step 17 fix wave 1, seat C2, charge F-11-04: a
    conditional clause inside the Status value produces its
    Conditional element, as the subject to form on the
    neighbouring entry already does, instead of being dropped
    while the entry derives as plain Ruled."""

    _DATA = (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Conditional one\n"
        "\n"
        "Status: Ruled if the ferry runs\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"Runs.\"\n"
        "\n"
        "### DQ-002: Conditional two\n"
        "\n"
        "Status: RULED, closed, subject to the winter timetable\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"Runs.\"\n"
    ).encode("utf-8")

    def test_if_clause_in_status_value_takes_conditional_treatment(self):
        _model, output = h.run_pipeline(self._DATA, "conditional.md")
        warnings = h.findings_for(output, entry_id="DQ-001", rule=3,
                                  severity="Warning")
        joined = " ".join(h.finding_statement(warning) or ""
                          for warning in warnings)
        self.assertIn("Conditional", joined)

    def test_subject_to_control_entry_keeps_conditional_treatment(self):
        _model, output = h.run_pipeline(self._DATA, "conditional.md")
        warnings = h.findings_for(output, entry_id="DQ-002", rule=3,
                                  severity="Warning")
        joined = " ".join(h.finding_statement(warning) or ""
                          for warning in warnings)
        self.assertIn("Conditional", joined)


if __name__ == "__main__":
    unittest.main()
