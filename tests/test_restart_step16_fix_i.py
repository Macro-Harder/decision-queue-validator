"""Restart Step 16 fix wave 2, Fix seat I tests.

Seat I owns product/decision_queue_validator/render.py for one
item only. Each test pins the charged cure, written before the
cure:

A2-3-1 (Low, Auditor 3 of confirmation round 2,
design/steps/step-16r-audit2-3.md section 8): the docstring of
the census member list wrapping helper, _wrapped_member_lines,
claims that no printed line stands over 72 characters. That
claim fails for a member identifier longer than the width
allows, which prints whole and unsplit on a longer line. No
member is lost, duplicated, reordered, or split in that case,
and never splitting an identifier is the right behaviour. The
defect is the docstring overstatement only. The cure corrects
the docstring to state the bound truly: member lists wrap at
72 characters, and a single identifier longer than the width
prints whole on its own line.

The behaviour pins below pass before and after the cure, by
design: they guard the correct behaviour the cure must not
change. The docstring pins fail before the cure and pass
after it, in the form the test can reach, which is the helper
docstring itself read in process.
"""

import unittest

import dqv_harness as h

render = h.import_module("render")
types = h.import_module("types")

LONG_103 = "DQ-" + "9" * 100
LONG_93 = "DQ-" + "8" * 90


def make_recon():
    return types.ReconciliationBlock(
        entry_total=types.HeadedEntryCount(3),
        canonical_counts={}, ambiguous_count=0, unparsed_count=0,
        status_occurrence_total=0, paired_total_declarations=[])


def make_facts():
    return types.FileFactsData(
        input_name="synthetic.md", byte_count=100, line_count=10,
        digest="0" * 64)


def make_output(census=()):
    return types.ValidateOutput(
        entries=[], findings=[], census=list(census),
        reconciliation=make_recon(), file_facts=make_facts(),
        limits=types.Limits(), vocabulary_version="1",
        output_form_edition="1", waiting=0, blocking=0,
        blocking_list=[], limbo_data={},
        exit_decision=types.ExitDecision(code=0, reason_classes=[]),
        fastest_item="not derivable from the file")


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


def docstring_flat():
    """The helper docstring with all whitespace runs collapsed
    to one space, so a phrase stands or falls as written,
    wherever the docstring lines wrap."""
    doc = render._wrapped_member_lines.__doc__ or ""
    return " ".join(doc.split())


class LongIdentifierBehaviourTest(unittest.TestCase):
    """A2-3-1 behaviour: an identifier longer than the width
    prints whole and unsplit. This behaviour is correct and
    must not change under the docstring cure."""

    def test_long_identifier_fixture_lengths(self):
        self.assertEqual(len(LONG_103), 103)
        self.assertEqual(len(LONG_93), 93)

    def test_single_long_identifier_prints_whole_via_helper(self):
        lines = render._wrapped_member_lines([LONG_103])
        self.assertEqual(lines, ["Members:", " " * 9 + LONG_103])
        self.assertEqual(len(lines[1]), 112)
        self.assertGreater(len(lines[1]), 72)
        carriers = [line for line in lines if LONG_103 in line]
        self.assertEqual(len(carriers), 1)

    def test_single_long_identifier_prints_whole_in_validate(self):
        row = types.CensusEntry(
            class_name="Open entries", count=1,
            member_entry_ids=[LONG_103], counting_unit="entries")
        text = render.render_validate(make_output(census=[row]))
        block = members_block(text)
        self.assertEqual(block, ["Members:", " " * 9 + LONG_103])
        self.assertEqual(len(block[1]), 112)
        carriers = [line for line in block if LONG_103 in line]
        self.assertEqual(len(carriers), 1)

    def test_single_long_identifier_prints_whole_in_summary(self):
        row = types.CensusEntry(
            class_name="Open entries", count=1,
            member_entry_ids=[LONG_103], counting_unit="entries")
        text = render.render_summary(make_output(census=[row]))
        block = members_block(text)
        self.assertEqual(block, ["Members:", " " * 9 + LONG_103])

    def test_mixed_list_long_identifier_whole_and_in_order(self):
        members = ["DQ-001", LONG_93, "DQ-002"]
        row = types.CensusEntry(
            class_name="Open entries", count=3,
            member_entry_ids=members, counting_unit="entries")
        text = render.render_validate(make_output(census=[row]))
        block = members_block(text)
        carriers = [line for line in block if LONG_93 in line]
        self.assertEqual(len(carriers), 1)
        self.assertIn(LONG_93, carriers[0])
        self.assertGreater(len(carriers[0].rstrip(",")), 72)
        joined = " ".join(line.strip() for line in block)
        tokens = joined[len("Members:"):].strip()
        printed = [item.strip() for item in tokens.split(",")]
        printed = [item for item in printed if item]
        self.assertEqual(printed, members)

    def test_fitting_members_still_wrap_within_72(self):
        members = ["DQ-%04d" % number for number in range(1, 31)]
        lines = render._wrapped_member_lines(members)
        self.assertGreater(len(lines), 1)
        for line in lines:
            self.assertLessEqual(len(line), 72)


class WrappingDocstringTest(unittest.TestCase):
    """A2-3-1 cure: the helper docstring states the bound
    truly, and no longer claims that no printed line stands
    over 72 characters."""

    def test_docstring_no_longer_claims_no_line_over_72(self):
        self.assertNotIn(
            "no printed line stands over 72 characters",
            docstring_flat())

    def test_docstring_states_member_lists_wrap_at_72(self):
        self.assertIn(
            "Member lists wrap at 72 characters",
            docstring_flat())

    def test_docstring_states_long_identifier_prints_whole(self):
        self.assertIn(
            "A single identifier longer than the width prints "
            "whole on its own line", docstring_flat())

    def test_docstring_still_states_no_identifier_is_split(self):
        self.assertIn(
            "no identifier is split across lines",
            docstring_flat())


if __name__ == "__main__":
    unittest.main()
