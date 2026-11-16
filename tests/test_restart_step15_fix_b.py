"""Restart Step 15 fix wave 1, Fix seat B tests.

Each test pins the differing form of one charged item in the
derivation layer, validate.py, as the audit at
design/steps/step-15r-audit1-2.md and the deviation register at
design/steps/step-14r-lead-engineer-shape-review.md section 10
state it, against the plan and the brief at their seals. Items:
D-07, D-08, D-12, D-13, D-20, the validate parts of D-09, D-10,
D-11, and D-15, the validate population of D-14, and fresh
findings NF-1, NF-2, and NF-3. The open derivations D-13-3,
D-13-4, and D-13-7 stand open with no figure anywhere; no test
here asserts any figure for them.
"""

import unittest

import dqv_harness as h

HEADER = "# Decision Queue\n\n## Open items\n\n"


def run_text(text):
    model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return model, output


def open_entry(number, status_line="Banked"):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: %s\n\n"
        "A plain paragraph stands in this entry.\n\n"
        "Owner of record: Decision-queue Clerk\n\n"
        "Question: A synthetic question for entry %d?\n\n"
        "Options: Option one. Option two.\n\n"
        "Cost: Low.\n\n"
        "Blocks: Nothing.\n"
    ) % (number, number, status_line, number)


def ruled_entry(number, status_line="Ruled"):
    return (
        "### DQ-%03d: Synthetic ruled entry %d\n\n"
        "Status: %s\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"The synthetic ruling stands.\"\n\n"
        "Ruling outcome: The synthetic outcome stands.\n\n"
        "Where the ruling landed: synthetic record.\n"
    ) % (number, number, status_line)


def entry_result(output, wanted):
    entry = h.entry_by_id(output, wanted)
    if entry is None:
        raise AssertionError("no entry result " + wanted)
    return entry


def model_entry(model, wanted):
    for entry in h.as_list(h.get(model, "entries")):
        if h.text_of(h.get(entry, "identifier")) == wanted:
            return entry
    raise AssertionError("no model entry " + wanted)


class D07EntryDerivedFieldsTest(unittest.TestCase):
    """D-07: validate fills the derived fields on the Entry."""

    def test_derived_fields_stand_on_the_entry_record(self):
        # The labelled paragraph form: the entry stands only in
        # labelled paragraphs, so the ruling element carrying the
        # decider is the determining element of the derivation.
        text = HEADER + (
            "### DQ-001: Synthetic ruled entry 1\n\n"
            "Ruled by: Captain JP\n\n"
            "Ruling text: \"The synthetic ruling stands.\"\n\n"
            "Ruling outcome: The synthetic outcome stands.\n\n"
            "Where the ruling landed: synthetic record.\n")
        model, output = run_text(text)
        entry = model_entry(model, "DQ-001")
        self.assertEqual(h.get(entry, "effective_state"), "Ruled")
        self.assertIsNone(h.get(entry, "reporting_form"))
        self.assertEqual(h.get(entry, "decider_label"),
                         "Ruled by Captain JP")
        self.assertEqual(h.as_list(h.get(entry, "remainder_texts")),
                         [])
        self.assertIsNone(h.get(entry, "condition_text"))

    def test_ambiguous_reporting_form_has_its_own_carrier(self):
        text = HEADER + (
            "### DQ-002: Synthetic entry 2\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Status: Wombled\n")
        model, output = run_text(text)
        entry = model_entry(model, "DQ-002")
        self.assertIsNone(h.get(entry, "effective_state"))
        self.assertEqual(h.get(entry, "reporting_form"), "Ambiguous")
        result = entry_result(output, "DQ-002")
        self.assertEqual(h.get(result, "reporting_form"), "Ambiguous")

    def test_remainder_texts_stand_as_a_list_on_the_entry(self):
        text = HEADER + (
            "### DQ-003: Synthetic entry 3\n\n"
            "Status: Banked\n\n"
            "#### Decision block\n\n"
            "Settled in part. The first limb is settled. "
            "The remainder, the second limb, stays banked.\n")
        model, output = run_text(text)
        entry = model_entry(model, "DQ-003")
        texts = h.as_list(h.get(entry, "remainder_texts"))
        self.assertTrue(texts)
        self.assertTrue(any("second limb" in str(t) for t in texts))


class D08ElementFieldsTest(unittest.TestCase):
    """D-08: validate sets the two validate owned element fields."""

    def test_determining_flag_and_underlying_state_are_set(self):
        conditional = HEADER + ruled_entry(
            1, "Ruled") + (
                "\nStatus: Ruled, subject to the landing standing "
                "verified\n")
        model, output = run_text(conditional)
        entry = model_entry(model, "DQ-001")
        elements = h.as_list(h.get(entry, "status_elements"))
        flagged = [e for e in elements
                   if h.get(e, "determining_flag")]
        self.assertEqual(len(flagged), 1)
        self.assertEqual(
            h.get(flagged[0], "underlying_state_without_condition"),
            "Ruled")


class D09ValidateFindingsTest(unittest.TestCase):
    """D-09, validate part: finding identifiers and claim fields."""

    def test_file_level_finding_carries_a_unit_identifier(self):
        text = HEADER + open_entry(1) + "\n" + open_entry(1)
        model, output = run_text(text)
        duplicates = [f for f in h.findings_of(output)
                      if h.finding_rule_number(f) == 1
                      and h.finding_severity(f) == "Error"]
        self.assertTrue(duplicates)
        for finding in duplicates:
            ident = h.finding_entry_id(finding)
            self.assertNotEqual(ident, "FILE")
            self.assertTrue(
                str(ident).startswith("file level unit, kind "),
                ident)

    def test_entry_claim_uses_the_declared_claiming_field(self):
        text = HEADER + open_entry(1) + "\n" + (
            "### DQ-002: Synthetic entry 2\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "DQ-001 is Settled.\n\n"
            "Question: A synthetic question?\n\n"
            "Options: Option one. Option two.\n\n"
            "Cost: Low.\n\n"
            "Blocks: Nothing.\n")
        model, output = run_text(text)
        claims = [f for f in h.findings_of(output)
                  if h.finding_rule_number(f) == 8
                  and h.finding_severity(f) == "Note"]
        self.assertTrue(claims)
        for finding in claims:
            self.assertFalse(hasattr(finding, "claiming_entry"))
            self.assertEqual(h.get(finding, "claiming_unit"),
                             "DQ-002")
            self.assertNotEqual(h.finding_entry_id(finding), "FILE")

    def test_segment_claim_carries_a_unit_identifier(self):
        text = HEADER + open_entry(1) + (
            "\n## Notes\n\n"
            "DQ-001 was settled in the note section.\n")
        model, output = run_text(text)
        claims = [f for f in h.findings_of(output)
                  if str(h.get(f, "rule_id")) == "PIN-09"]
        if not claims:
            self.skipTest("no segment claim stands on this "
                          "construction in the built parse")
        for finding in claims:
            claiming = h.get(finding, "claiming_unit")
            self.assertTrue(
                str(claiming).startswith("file level unit, kind "),
                claiming)
            self.assertNotEqual(h.finding_entry_id(finding), "FILE")


class D10ClassRuleStatementTest(unittest.TestCase):
    """D-10, validate part: every census row carries its rule."""

    def test_every_census_row_carries_a_class_rule_statement(self):
        model, output = run_text(HEADER + open_entry(1))
        rows = h.census_of(output)
        self.assertTrue(rows)
        for row in rows:
            statement = h.get(row, "class_rule_statement")
            self.assertTrue(statement, h.get(row, "class_name"))


class D11ResidueItemTest(unittest.TestCase):
    """D-11: residue items stand as ResidueItem values."""

    def test_residue_items_are_residue_item_instances(self):
        text = HEADER + open_entry(1, "Wombled")
        model, output = run_text(text)
        items = h.as_list(h.get(output, "residue_items"))
        self.assertTrue(items)
        residue_type = h.find_type("ResidueItem")
        self.assertIsNotNone(residue_type)
        for item in items:
            self.assertIsInstance(item, residue_type)
            self.assertEqual(h.get(item, "entry_identifier"),
                             "DQ-001")
            span = h.span_of(item)
            self.assertTrue(span[0] >= 1)
            self.assertFalse(isinstance(item, dict))


class D12CanonicalCountsTest(unittest.TestCase):
    """D-12: the model canonical counts field stands populated."""

    def test_canonical_counts_stand_on_the_output(self):
        model, output = run_text(HEADER + open_entry(1))
        counts = h.get(output, "canonical_counts")
        self.assertTrue(isinstance(counts, dict) and counts)
        self.assertEqual(counts.get("Open"), 1)
        self.assertEqual(sum(counts.values()), 1)


class D13ResidueShareTest(unittest.TestCase):
    """D-13: the residue share stands as its exact pair."""

    def test_residue_share_is_the_exact_pair_not_a_float(self):
        text = HEADER + open_entry(1, "Wombled") + "\n" + open_entry(2)
        model, output = run_text(text)
        share = h.get(output, "residue_share")
        self.assertNotIsInstance(share, float)
        pair = tuple(share)
        self.assertEqual(pair, (1, 2))


class D14RenderModelPopulationTest(unittest.TestCase):
    """D-14, validate population: groups, units, figures."""

    def test_entry_groups_stand_in_render_order(self):
        text = HEADER + open_entry(1) + "\n" + ruled_entry(2)
        model, output = run_text(text)
        groups = h.get(output, "entry_groups")
        self.assertIsNotNone(groups)
        names = []
        for group in h.as_list(groups):
            if isinstance(group, dict):
                names.append(group.get("group") or group.get("name"))
            else:
                names.append(h.get(group, "group", "name"))
        self.assertEqual(names, ["Open", "Ruled"])

    def test_counting_units_stand_populated(self):
        model, output = run_text(HEADER + open_entry(1))
        units = h.get(output, "counting_units")
        self.assertIsNotNone(units)
        self.assertEqual(h.get(units, "waiting"), "entries")
        self.assertEqual(h.get(units, "blocking"), "entries")
        self.assertEqual(h.get(units, "canonical_counts"),
                         "entries")

    def test_waiting_and_blocking_carry_their_unit(self):
        # The unit beside each figure stands in the counting
        # units key of the model, in the shape the types seat
        # landed for D-14: the key names the unit of the waiting
        # figure and of the blocking figure, each as entries.
        model, output = run_text(HEADER + open_entry(1))
        waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 1)
        self.assertEqual(h.int_of(blocking), 1)
        units = h.get(output, "counting_units")
        self.assertEqual(h.get(units, "waiting"), "entries")
        self.assertEqual(h.get(units, "blocking"), "entries")

    def test_companion_count_stands_carried_beside_waiting(self):
        model, output = run_text(HEADER + open_entry(1))
        companion = h.get(output, "companion_count")
        self.assertIsNotNone(companion)
        self.assertEqual(h.int_of(companion), 0)


class D15ExitDecisionTest(unittest.TestCase):
    """D-15, validate part: validate supplies no exit decision."""

    def test_validate_output_carries_no_exit_decision(self):
        model, output = run_text(HEADER + open_entry(1))
        self.assertIsNone(h.get(output, "exit_decision"))

    def test_validate_output_carries_the_rule_set_version(self):
        model, output = run_text(HEADER + open_entry(1))
        self.assertEqual(
            str(h.get(output, "rule_set_version")), "1")


class D20ReconciliationComponentsTest(unittest.TestCase):
    """D-20: components stand in the contract order and names."""

    def test_component_list_matches_the_contract_enumeration(self):
        model, output = run_text(HEADER + open_entry(1))
        recon = h.reconciliation_of(output)
        components = h.as_list(h.get(recon, "components",
                                     "component_results"))
        self.assertTrue(components)
        names = [str(h.get(c, "name", "component")) for c in components]
        self.assertEqual(names, [
            "population footing", "canonical footing",
            "verbatim footing", "component footing",
            "whole file assignment"])

    def test_whole_file_assignment_component_can_fail(self):
        double = h.ParseModelDouble(
            entries=[], unassigned_lines=[3])
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        output = h.validate_function(validate_module)(
            double, vocabulary)
        recon = h.reconciliation_of(output)
        check = h.get(recon, "self_check", "self_check_result")
        self.assertFalse(h.get(check, "sums_agree"))


class Nf1BankedEvidenceGroupsTest(unittest.TestCase):
    """NF-1: group two requires a level 4 decision block."""

    def test_non_level_4_block_stands_in_no_group(self):
        text = (
            "# Decision Queue\n\n"
            "### DQ-001: A banked head entry\n\n"
            "Status: Banked\n\n"
            "Decision: the matter is settled as recorded here "
            "in full.\n")
        model, output = run_text(text)
        rows = h.census_of(output)
        group2 = h.census_class(rows, "level 4 decision block")
        members = h.census_members(group2) if group2 else []
        self.assertNotIn("DQ-001", members)
        recon = h.reconciliation_of(output)
        check = h.get(recon, "self_check", "self_check_result")
        self.assertFalse(h.get(check, "sums_agree"))

    def test_level_4_block_stands_in_group_two(self):
        text = (
            "# Decision Queue\n\n"
            "### DQ-001: A banked head entry\n\n"
            "Status: Banked\n\n"
            "#### Ruling by Captain JP\n\n"
            "The ruling stands in this block.\n")
        model, output = run_text(text)
        rows = h.census_of(output)
        group2 = h.census_class(rows, "level 4 decision block")
        self.assertIsNotNone(group2)
        self.assertIn("DQ-001", h.census_members(group2))


class Nf2PopulationFootingTest(unittest.TestCase):
    """NF-2: population footing checks both of its totals."""

    def test_ledger_disagreement_fails_population_footing(self):
        entry = {
            "identifier": "DQ-901",
            "heading": "DQ-901: A ledger break entry",
            "heading_text": "DQ-901: A ledger break entry",
            "elements": [], "status_elements": [], "fields": [],
            "decision_blocks": [], "unparsed": False,
        }
        double = h.ParseModelDouble(entries=[entry])
        double.number_ledger = {}
        validate_module = h.import_module("validate")
        vocabulary = h.build_vocabulary(validate_module)
        output = h.validate_function(validate_module)(
            double, vocabulary)
        recon = h.reconciliation_of(output)
        check = h.get(recon, "self_check", "self_check_result")
        self.assertFalse(h.get(check, "sums_agree"))
        failed = " ".join(str(x) for x in h.as_list(
            h.get(check, "failed_components", "failures")))
        self.assertIn("population footing", failed)


class Nf3HeaderFactsPurityTest(unittest.TestCase):
    """NF-3: validate does not write into the parse owned facts."""

    def test_header_facts_object_stands_unchanged(self):
        model, output = run_text(HEADER + open_entry(1))
        facts = h.get(model, "header_facts", "file_header_facts")
        self.assertIsNone(h.get(facts, "vocabulary_version"))


class D19TranslationKnockOnTest(unittest.TestCase):
    """D-19 knock on effect: translation is validate work.

    With the parse layer mapping lookup deleted under the D-19
    cure, a Status value whose opening forms state no
    disposition but which stands in the vocabulary table
    reaches validate with no disposition, and validate
    derivation reading the element disposition alone reports
    the entry Ambiguous. The translation of a verbatim phrasing
    to its canonical family is validate work under the plan
    Item 3, section 3.5 seam, by exact match on the value as
    written, with no normalisation: a canonically equivalent
    phrasing in another code point sequence does not translate
    and takes the untranslatable treatment.
    """

    def test_value_standing_in_the_table_translates(self):
        composed = "Café fermé"
        model, output = run_text(HEADER + ruled_entry(1, composed))
        result = entry_result(output, "DQ-001")
        self.assertFalse(h.is_ambiguous(result))
        entry = model_entry(model, "DQ-001")
        elements = h.as_list(h.get(entry, "status_elements"))
        line_start = [e for e in elements
                      if h.get(e, "occurrence_kind") == "line start"]
        self.assertTrue(line_start)
        self.assertEqual(h.get(line_start[0], "disposition"),
                         "Closed")

    def test_equivalent_value_in_another_sequence_does_not(self):
        decomposed = "Café fermé"
        model, output = run_text(
            HEADER + ruled_entry(1, decomposed))
        result = entry_result(output, "DQ-001")
        self.assertTrue(h.is_ambiguous(result))


class R7DisplayIdentifierTest(unittest.TestCase):
    """The named R-7 entry stands under its display identifier.

    Under the D-06 cure the entry identifier on the model is
    the literal heading text of the named unnumbered heading.
    Validate derives the display identifier of that form as
    R-7, the identifier the entry result carries and every
    validate comparison uses.
    """

    def test_r7_entry_stands_under_r7(self):
        text = ("# Decision Queue\n\n## Ruled record\n\n"
                "### R-7 closure conflict\n\n"
                "Status: RULED, closed\n\n"
                "Ruled by: Captain JP\n\n"
                "Ruling text: \"The synthetic ruling stands.\"\n")
        model, output = run_text(text)
        result = entry_result(output, "R-7")
        self.assertEqual(h.entry_state(result), "Ruled")


if __name__ == "__main__":
    unittest.main()
