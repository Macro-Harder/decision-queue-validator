"""Restart Step 16 fix wave, Seat A tests.

Seat A owns product/decision_queue_validator/render.py. Each test
pins one charged cure in the render layer, written before the
cure:

D-16 (register item 16R-02, Auditor 10 shape): where a model
carries no entry groups field, or an empty one, sectioning
derives no group for any entry; every entry prints under
Ungrouped entries. The populated path, where the model carries
entry groups, prints exactly the grouping it carries.

A12-1 (Auditor 12, Medium): the census printing reads the
counting unit validate sets on the row, so the line start row,
whose count stands in Status lines and whose members are fewer
entries, prints its own unit and not the word entries.

F7 wrapping cure (Auditor 9, Low, brief OP-Q10): census member
identifiers print as a wrapped list under their row. The brief
names no wrap width; this seat fixes the width at 72 characters,
with continuation lines indented to stand under the first
identifier, and no identifier ever split across lines.
"""

import unittest
from types import SimpleNamespace

import dqv_harness as h

render = h.import_module("render")
types = h.import_module("types")

GROUP_HEADING_LINES = (
    "Open group", "Settled in part group", "Presented group",
    "Parked group", "Conditional group", "Ambiguous group",
    "Ruled group", "Settled group", "Closed as decided group",
    "Banked group", "Unparsed entries",
)


def make_entry(identifier, state="Open", reporting_form=None):
    entry = types.EntryResult(
        identifier=identifier,
        heading="%s: An entry" % identifier,
        title="An entry", effective_state=state, open_fields={})
    if reporting_form is not None:
        entry.reporting_form = reporting_form
    return entry


def probe_entries():
    """The Auditor 10 probe entries: DQ-101 state Open; DQ-102
    state Open with reporting form Ambiguous, the two carriers
    the plan keeps apart; DQ-103 state Banked, a name outside
    the render group order."""
    return [
        make_entry("DQ-101", state="Open"),
        make_entry("DQ-102", state="Open",
                   reporting_form="Ambiguous"),
        make_entry("DQ-103", state="Banked"),
    ]


def make_recon():
    return types.ReconciliationBlock(
        entry_total=types.HeadedEntryCount(3),
        canonical_counts={}, ambiguous_count=0, unparsed_count=0,
        status_occurrence_total=0, paired_total_declarations=[])


def make_facts():
    return types.FileFactsData(
        input_name="synthetic.md", byte_count=100, line_count=10,
        digest="0" * 64)


def make_output(entries=(), census=(), **overrides):
    output = types.ValidateOutput(
        entries=list(entries), findings=[], census=list(census),
        reconciliation=make_recon(), file_facts=make_facts(),
        limits=types.Limits(), vocabulary_version="1",
        output_form_edition="1", waiting=0, blocking=0,
        blocking_list=[], limbo_data={},
        exit_decision=types.ExitDecision(code=0, reason_classes=[]),
        fastest_item="not derivable from the file")
    for name, value in overrides.items():
        setattr(output, name, value)
    return output


def make_ns_output(entries=(), census=()):
    """A hand built model carrying entries and no entry groups
    attribute at all, in the seam double form."""
    recon = SimpleNamespace(
        entry_total=None, dq_entry_count=0, unnumbered_entry_count=0,
        headed_span_count=0, orphan_note_segment_count=0,
        h4_sub_heading_count=0, status_occurrences_by_kind={},
        status_occurrence_total=0, canonical_counts={},
        ambiguous_count=0, unparsed_count=0,
        findings_per_severity={}, findings_per_rule={},
        distinct_phrasing_count=None, self_check=None,
        paired_total_declarations=[])
    facts = SimpleNamespace(
        input_name="synthetic.md", byte_count=100, line_count=10,
        digest="0" * 64)
    return SimpleNamespace(
        entries=list(entries), findings=[], census=list(census),
        reconciliation=recon, file_facts=facts,
        limits=types.Limits(), vocabulary_version="1",
        output_form_edition="1", verbatim_appendix_rows=[],
        per_rule_clearing_forms={}, crosswalk_counts={}, waiting=0,
        blocking=0, blocking_list=[], limbo_data={},
        segment_claim_reports=[],
        fastest_item="not derivable from the file",
        supersession_chains=[])


def assert_all_under_ungrouped(case, text, identifiers):
    lines = text.splitlines()
    for heading in GROUP_HEADING_LINES:
        case.assertNotIn(
            heading, lines,
            "a group heading stands in the fallback output: "
            + heading)
    case.assertIn("Ungrouped entries", lines)
    ungrouped_at = text.find("\nUngrouped entries\n")
    case.assertGreaterEqual(ungrouped_at, 0)
    for identifier in identifiers:
        case.assertGreater(
            text.find(identifier), ungrouped_at,
            identifier + " does not stand under Ungrouped entries")


class D16NoGroupsFieldTest(unittest.TestCase):
    """D-16: a model with no entry groups field prints every
    entry under Ungrouped entries and none scattered by the
    state each entry itself carries."""

    def test_mapping_with_no_entry_groups_key_validate(self):
        entries = [
            {"identifier": "DQ-101", "effective_state": "Open",
             "title": "An entry"},
            {"identifier": "DQ-102", "effective_state": "Open",
             "reporting_form": "Ambiguous", "title": "An entry"},
            {"identifier": "DQ-103", "effective_state": "Banked",
             "title": "An entry"},
        ]
        model = {"entries": entries}
        text = render.render_validate(model)
        assert_all_under_ungrouped(
            self, text, ["DQ-101", "DQ-102", "DQ-103"])

    def test_namespace_with_no_entry_groups_attribute(self):
        text = render.render_validate(
            make_ns_output(entries=probe_entries()))
        assert_all_under_ungrouped(
            self, text, ["DQ-101", "DQ-102", "DQ-103"])

    def test_no_entry_groups_field_summary_form(self):
        text = render.render_summary(
            make_ns_output(entries=probe_entries()))
        assert_all_under_ungrouped(
            self, text, ["DQ-101", "DQ-102", "DQ-103"])


class D16EmptyGroupsFieldTest(unittest.TestCase):
    """D-16, second trigger: a model whose entry groups field
    stands empty, the declared default form of ValidateOutput."""

    def test_empty_entry_groups_validate(self):
        output = make_output(entries=probe_entries(),
                             entry_groups=[])
        text = render.render_validate(output)
        assert_all_under_ungrouped(
            self, text, ["DQ-101", "DQ-102", "DQ-103"])

    def test_empty_entry_groups_summary(self):
        output = make_output(entries=probe_entries(),
                             entry_groups=[])
        text = render.render_summary(output)
        assert_all_under_ungrouped(
            self, text, ["DQ-101", "DQ-102", "DQ-103"])


class D16PopulatedGroupsGuardTest(unittest.TestCase):
    """D-16 guard: the populated path must not change. A model
    carrying entry groups prints exactly that grouping, in
    carried order, including a carried name outside the render
    group order. This test passes before and after the cure."""

    def test_populated_grouping_prints_as_carried(self):
        entries = probe_entries()
        output = make_output(
            entries=entries,
            entry_groups=[
                {"group": "Open", "name": "Open",
                 "entries": [entries[0], entries[1]]},
                {"group": "Banked", "name": "Banked",
                 "entries": [entries[2]]},
            ])
        text = render.render_validate(output)
        lines = text.splitlines()
        self.assertIn("Open group", lines)
        self.assertIn("Banked group", lines)
        self.assertNotIn("Ungrouped entries", lines)
        open_at = text.find("\nOpen group\n")
        banked_at = text.find("\nBanked group\n")
        self.assertGreater(text.find("DQ-101"), open_at)
        self.assertLess(text.find("DQ-101"), banked_at)
        self.assertGreater(text.find("DQ-102"), open_at)
        self.assertLess(text.find("DQ-102"), banked_at)
        self.assertGreater(text.find("DQ-103"), banked_at)


class A12CensusUnitTest(unittest.TestCase):
    """A12-1: the census count line reads the counting unit the
    row carries, as validate sets it."""

    def test_line_start_row_prints_status_lines_not_entries(self):
        members = ["DQ-%03d" % number for number in range(1, 154)]
        row = types.CensusEntry(
            class_name="Status occurrences at line start (file "
                       "level census figure)",
            count=233, member_entry_ids=members,
            class_rule_statement="Status occurrences whose "
                                 "occurrence kind is line start.",
            counting_unit="Status lines")
        text = render.render_validate(make_output(census=[row]))
        self.assertIn("233 Status lines", text)
        self.assertNotIn("233 entries", text)

    def test_singular_form_of_a_carried_unit(self):
        row = types.CensusEntry(
            class_name="Status occurrences at line start (file "
                       "level census figure)",
            count=1, member_entry_ids=["DQ-001"],
            counting_unit="Status lines")
        text = render.render_validate(make_output(census=[row]))
        self.assertIn("1 Status line", text)
        self.assertNotIn("1 Status lines", text)

    def test_entries_unit_rows_print_as_before(self):
        row = types.CensusEntry(
            class_name="Open entries", count=3,
            member_entry_ids=["DQ-001", "DQ-002", "DQ-003"],
            counting_unit="entries")
        text = render.render_validate(make_output(census=[row]))
        self.assertIn("3 entries", text)
        single = types.CensusEntry(
            class_name="Open entries", count=1,
            member_entry_ids=["DQ-001"], counting_unit="entries")
        text = render.render_validate(make_output(census=[single]))
        self.assertIn("1 entry", text)
        self.assertNotIn("1 entries", text)


def members_block(text):
    """The printed lines of the first census members list: the
    Members line and every indented continuation line after it."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("Members:"):
            block = [line]
            follow = index + 1
            while follow < len(lines) and \
                    lines[follow].startswith(" "):
                block.append(lines[follow])
                follow += 1
            return block
    return []


class F7CensusWrapTest(unittest.TestCase):
    """F7, OP-Q10: a long census member list prints as a wrapped
    list under its row, at the width this seat fixes, 72."""

    def test_long_member_list_wraps(self):
        members = ["DQ-%04d" % number for number in range(1, 31)]
        row = types.CensusEntry(
            class_name="Banked head over a decided body",
            count=30, member_entry_ids=members,
            counting_unit="entries")
        text = render.render_validate(make_output(census=[row]))
        block = members_block(text)
        self.assertGreater(
            len(block), 1,
            "the member list printed as a single unwrapped line")
        for line in block:
            self.assertLessEqual(
                len(line), 72,
                "a wrapped member line exceeds the fixed width: "
                + line)
        for line in block[1:]:
            self.assertTrue(
                line.startswith(" "),
                "a continuation line does not stand indented "
                "under the row: " + line)
        joined = " ".join(line.strip() for line in block)
        for identifier in members:
            self.assertIn(identifier, joined)
        positions = [joined.find(identifier)
                     for identifier in members]
        self.assertEqual(positions, sorted(positions),
                         "the wrapped list reorders its members")

    def test_short_member_list_stays_on_one_line(self):
        row = types.CensusEntry(
            class_name="Open entries", count=2,
            member_entry_ids=["DQ-001", "DQ-002"],
            counting_unit="entries")
        text = render.render_validate(make_output(census=[row]))
        self.assertIn("Members: DQ-001, DQ-002", text.splitlines())


if __name__ == "__main__":
    unittest.main()
