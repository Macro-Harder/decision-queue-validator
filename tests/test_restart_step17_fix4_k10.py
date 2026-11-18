"""Restart Step 17 fix wave 4, cluster K10 tests.

Charges CH-59 and CH-72, ruled at section 38 of design/steps/
step-17r-record.md and prepared at design/steps/
step-17r-triage4-prep.md.

CH-59 (validate, the repeated and alias field value
selection), register item 17R-180, round 4 attack seat 6
Finding 2: a field label repeated inside one entry, or
standing beside its alias with a contradictory value, is
read under a silent selection rule with no finding at any
grade, and the selection rule differs between the repeated
label (first occurrence governs) and the alias pair (the
naming value governs in both orders). Cure bound: a
repeated or alias paired field carrying two contradictory
values takes a finding naming the conflict, and one stated
selection rule governs both forms. The rule stated once,
here and in the cure: the first occurrence in file order
governs, for a repeated label and for an alias pair alike.
Pins that must not break: the governed single value
readings whole, including the repeated identifier inside
one Blocks list counting its entry once.

CH-72 (validate and parse, the Options alias case and
block bounds), register item 17R-185, round 4 attack seat
17 findings S17-ATK4-17-04 and S17-ATK4-17-05: the Options
alias label counts in letter case forms every sibling
label rejects, including all capitals, and the alias label
alone inside a level 4 decision block collects its dash
lines and satisfies the entry. Cure bounds: the alias
label counts in the case forms the ruling states, no
wider than its siblings stand, test first in the all
capitals, mixed case, title case, and lower case forms
against the exact label controls; and the alias collected
lines scan and the alias presence test skip decision
block lines, as every sibling presence test does. Pins
that must not break: the CH-22 and CH-48 pins whole,
including the taught alias forms counting as they count
and the alias alone forms collecting their dash lines
outside a block.

Constructions are the finding papers own constructions,
rebuilt in the attack papers base forms: the seat 6 Open
entry files for CH-59 and the seat 17 two entry Banked
base for CH-72.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

HEAD = "# Decision queue\n\n"


def open_queue(first_field_paragraphs):
    """The attack seat 6 base: DQ-001 Open carrying the
    field paragraphs under test, DQ-002 complete."""
    parts = [HEAD,
             "### DQ-001: Alpha question\n\n",
             "Status: Open\n\n"]
    for paragraph in first_field_paragraphs:
        parts.append(paragraph + "\n\n")
    parts.extend([
        "This entry is waiting for a decision.\n\n",
        "### DQ-002: Beta question\n\n",
        "Status: Open\n\n",
        "Question: Which other option should we take?\n\n",
        "Options: Option C, Option D\n\n",
        "Cost of deciding late: Other work stays blocked.\n\n",
        "Blocks: DQ-001\n\n",
        "This second entry is waiting for a decision.\n",
    ])
    return "".join(parts).encode("utf-8")


BASE_FIELDS = [
    "Question: Which option should we take?",
    "Options: Option A, Option B",
    "Cost of deciding late: Work stays blocked.",
]


def blocks_queue(blocks_paragraphs):
    return open_queue(BASE_FIELDS + list(blocks_paragraphs))


def options_queue(first_options_lines):
    """The attack seat 17 base: DQ-001 Banked carrying the
    options lines under test and no other options matter,
    DQ-002 complete with the exact label."""
    parts = [
        HEAD,
        "### DQ-001: A sample open question\n\n",
        "Status: Banked\n\n",
        "This question is waiting for a decision.\n\n",
        "Question: Which option should we take?\n\n",
    ]
    if first_options_lines:
        parts.append("\n".join(first_options_lines) + "\n\n")
    parts.extend([
        "Cost of deciding late: Work stays blocked.\n\n",
        "Blocks: DQ-002\n\n",
        "### DQ-002: A second open question\n\n",
        "Status: Banked\n\n",
        "Second entry is waiting for a decision.\n\n",
        "Question: Which path should we take?\n\n",
        "Options: Option C, Option D\n\n",
        "Cost of deciding late: More work stays blocked.\n\n",
        "Blocks: DQ-001\n",
    ])
    return "".join(parts).encode("utf-8")


def run(data):
    _model, output = h.run_pipeline(data)
    if output is None:
        raise AssertionError("pipeline returned a failure")
    return output


def cli_code(data, subcommand="validate"):
    path = h.temp_input(data)
    code, _out, _err = h.run_cli(subcommand, path)
    return code


def statements(output, entry_id=None):
    found = h.findings_for(output, entry_id=entry_id) \
        if entry_id else h.findings_of(output)
    return [h.finding_statement(f) or "" for f in found]


def conflict_statements(output):
    return [s for s in statements(output, "DQ-001")
            if "contradictory values" in s]


def missing_options_statements(output):
    return [s for s in statements(output, "DQ-001")
            if "missing its options" in s]


class Ch59RepeatedBlocksTest(unittest.TestCase):
    """CH-59, the repeated label form: seat 6 cases n10 and
    n10b, first occurrence governing in both orders, each
    taking the conflict finding."""

    def test_first_value_governs_and_conflict_is_named(self):
        data = blocks_queue(["Blocks: DQ-002", "Blocks: none"])
        output = run(data)
        conflicts = conflict_statements(output)
        self.assertEqual(len(conflicts), 1)
        self.assertIn("DQ-002", conflicts[0])
        self.assertIn("none", conflicts[0])
        self.assertIn("first occurrence in file order governs",
                      conflicts[0])
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_code(data), 1)

    def test_reversed_order_first_value_governs(self):
        data = blocks_queue(["Blocks: none", "Blocks: DQ-002"])
        output = run(data)
        self.assertEqual(len(conflict_statements(output)), 1)
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 1)
        self.assertEqual(cli_code(data), 1)

    def test_identical_repeat_takes_no_conflict_finding(self):
        # Pin direction, passing before and after: the same
        # value stated twice under one label is one value
        # stated twice, not a contradiction.
        data = blocks_queue(["Blocks: DQ-002", "Blocks: DQ-002"])
        output = run(data)
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(cli_code(data), 0)

    def test_repeat_inside_one_blocks_list_counts_once(self):
        # The pin the charge names expressly, passing before
        # and after: a repeated identifier inside one Blocks
        # list counts its entry once.
        data = blocks_queue(["Blocks: DQ-002, DQ-002"])
        output = run(data)
        self.assertEqual(conflict_statements(output), [])
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_code(data), 0)


class Ch59AliasBlocksTest(unittest.TestCase):
    """CH-59, the alias pair form: seat 6 cases n11 and
    n11b. Before the cure the naming value governed in both
    orders; under the one stated rule the first occurrence
    in file order governs in both orders alike."""

    def test_alias_pair_none_first_governs(self):
        data = blocks_queue(
            ["Blocks: none", "What it blocks: DQ-002"])
        output = run(data)
        self.assertEqual(len(conflict_statements(output)), 1)
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 1)
        self.assertEqual(cli_code(data), 1)

    def test_alias_pair_naming_first_governs(self):
        data = blocks_queue(
            ["What it blocks: DQ-002", "Blocks: none"])
        output = run(data)
        self.assertEqual(len(conflict_statements(output)), 1)
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_code(data), 1)

    def test_alias_pair_same_value_takes_no_conflict(self):
        # Pin direction, passing before and after: an alias
        # pair carrying one value in both forms states no
        # contradiction.
        data = blocks_queue(
            ["Blocks: none", "What it blocks: none"])
        output = run(data)
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(cli_code(data), 0)


class Ch59OtherFamiliesTest(unittest.TestCase):
    """CH-59 on the other field families the seat 6 paper
    measures in the same silent form: seat 6 cases n13
    (Question) and n28 (Options), and the Cost alias pair."""

    def test_duplicate_question_takes_conflict_finding(self):
        data = open_queue([
            "Question: Which option should we take?",
            "Question: Which completely different question "
            "is this?",
            "Options: Option A, Option B",
            "Cost of deciding late: Work stays blocked.",
            "Blocks: DQ-002",
        ])
        output = run(data)
        conflicts = conflict_statements(output)
        self.assertEqual(len(conflicts), 1)
        self.assertIn("question", conflicts[0])
        self.assertEqual(cli_code(data), 1)

    def test_duplicate_options_takes_conflict_finding(self):
        data = open_queue([
            "Question: Which option should we take?",
            "Options: Option A, Option B",
            "Options: Option C, Option D",
            "Cost of deciding late: Work stays blocked.",
            "Blocks: DQ-002",
        ])
        output = run(data)
        conflicts = conflict_statements(output)
        self.assertEqual(len(conflicts), 1)
        self.assertIn("options", conflicts[0])
        self.assertEqual(cli_code(data), 1)

    def test_options_alias_pair_takes_conflict_finding(self):
        data = open_queue([
            "Question: Which option should we take?",
            "Options: Option A, Option B",
            "The options are: Option C, Option D",
            "Cost of deciding late: Work stays blocked.",
            "Blocks: DQ-002",
        ])
        output = run(data)
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_code(data), 1)

    def test_cost_alias_pair_takes_conflict_finding(self):
        data = open_queue([
            "Question: Which option should we take?",
            "Options: Option A, Option B",
            "Cost of deciding late: Work stays blocked.",
            "Cost: Nothing is delayed at all.",
            "Blocks: DQ-002",
        ])
        output = run(data)
        conflicts = conflict_statements(output)
        self.assertEqual(len(conflicts), 1)
        self.assertIn("cost of deciding late", conflicts[0])
        self.assertEqual(cli_code(data), 1)

    def test_single_value_fields_take_no_conflict_finding(self):
        # Pin direction, passing before and after: the clean
        # base carries one value per field and stands clean.
        data = blocks_queue(["Blocks: DQ-002"])
        output = run(data)
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(cli_code(data), 0)

    def test_governing_value_is_first_in_file_order(self):
        # The one stated selection rule at the helper the
        # blocking figure reads: file order, not label
        # priority, in both orders.
        first = {"fields": [
            {"label": "Blocks", "value": "none"},
            {"label": "What it blocks", "value": "DQ-002"}]}
        second = {"fields": [
            {"label": "What it blocks", "value": "DQ-002"},
            {"label": "Blocks", "value": "none"}]}
        labels = ("What it blocks", "Blocks")
        self.assertEqual(
            validate._first_family_value(first, labels), "none")
        self.assertEqual(
            validate._first_family_value(second, labels),
            "DQ-002")


class Ch72AliasCaseTest(unittest.TestCase):
    """CH-72, the case limb, S17-ATK4-17-04: seat 17 cases
    g21, g22, g24, and g25 take the missing options Warning,
    against the exact label controls g23 and g26."""

    def test_alias_all_capitals_takes_missing_warning(self):
        data = options_queue(
            ["THE OPTIONS ARE: Option A, Option B"])
        output = run(data)
        self.assertEqual(len(missing_options_statements(output)), 1)
        self.assertEqual(cli_code(data), 1)

    def test_alias_mixed_case_takes_missing_warning(self):
        data = options_queue(
            ["ThE OpTiOnS aRe: Option A, Option B"])
        output = run(data)
        self.assertEqual(len(missing_options_statements(output)), 1)
        self.assertEqual(cli_code(data), 1)

    def test_three_options_alias_all_capitals_takes_missing(self):
        data = options_queue(
            ["THE THREE OPTIONS ARE: Option A, Option B"])
        output = run(data)
        self.assertEqual(len(missing_options_statements(output)), 1)
        self.assertEqual(cli_code(data), 1)

    def test_alias_title_case_takes_missing_warning(self):
        data = options_queue(
            ["The Options Are: Option A, Option B"])
        output = run(data)
        self.assertEqual(len(missing_options_statements(output)), 1)
        self.assertEqual(cli_code(data), 1)

    def test_alias_label_case_test_unit(self):
        # The alias test reads the label as written, in its
        # sentence case form alone: a capital first word and
        # every following word in lower case.
        self.assertTrue(validate._options_alias_label(
            "The options are"))
        self.assertTrue(validate._options_alias_label(
            "The three options are"))
        self.assertTrue(validate._options_alias_label(
            "The options stated plainly"))
        self.assertFalse(validate._options_alias_label(
            "THE OPTIONS ARE"))
        self.assertFalse(validate._options_alias_label(
            "ThE OpTiOnS aRe"))
        self.assertFalse(validate._options_alias_label(
            "The Options Are"))
        self.assertFalse(validate._options_alias_label(
            "the options are"))
        self.assertFalse(validate._options_alias_label(
            "The optionsXYZ"))


class Ch72AliasBlockTest(unittest.TestCase):
    """CH-72, the block limb, S17-ATK4-17-05: seat 17 case
    g33, the alias label alone inside a level 4 decision
    block collecting its dash lines."""

    G33 = None

    def _g33(self):
        parts = [
            HEAD,
            "### DQ-001: A sample open question\n\n",
            "Status: Banked\n\n",
            "This question is waiting for a decision.\n\n",
            "Question: Which option should we take?\n\n",
            "#### Decision block\n\n",
            "The options are:\n\n",
            "- Option A\n",
            "- Option B\n\n",
            "Cost of deciding late: Work stays blocked.\n\n",
            "Blocks: DQ-002\n\n",
            "### DQ-002: A second open question\n\n",
            "Status: Banked\n\n",
            "Second entry is waiting for a decision.\n\n",
            "Question: Which path should we take?\n\n",
            "Options: Option C, Option D\n\n",
            "Cost of deciding late: More work stays blocked.\n\n",
            "Blocks: DQ-001\n",
        ]
        return "".join(parts).encode("utf-8")

    def test_alias_alone_in_block_takes_missing_warning(self):
        data = self._g33()
        output = run(data)
        self.assertEqual(len(missing_options_statements(output)), 1)
        self.assertEqual(cli_code(data), 1)

    def test_alias_field_inside_block_counts_for_nothing_unit(self):
        entry = {
            "fields": [{"label": "The options are",
                        "value": "Option A, Option B",
                        "line": 17}],
            "body_lines": [(15, "#### Decision block"),
                           (17, "The options are: Option A, "
                                "Option B")],
            "decision_blocks": [
                {"span": {"start_line": 15, "end_line": 21}}],
        }
        self.assertFalse(validate._has_options_field(entry))
        self.assertFalse(validate._options_value_present(entry))

    def test_exact_field_inside_block_counts_for_nothing_unit(self):
        entry = {
            "fields": [{"label": "Options",
                        "value": "Option A, Option B",
                        "line": 17}],
            "body_lines": [(15, "#### Decision block"),
                           (17, "Options: Option A, Option B")],
            "decision_blocks": [
                {"span": {"start_line": 15, "end_line": 21}}],
        }
        self.assertFalse(validate._has_options_field(entry))
        self.assertFalse(validate._options_value_present(entry))

    def test_collected_dash_lines_inside_block_collect_nothing(self):
        entry = {
            "fields": [{"label": "The options are", "value": "",
                        "line": 10}],
            "body_lines": [
                (10, "The options are:"),
                (11, ""),
                (12, "- Option A"),
                (13, "- Option B"),
            ],
            "decision_blocks": [
                {"span": {"start_line": 12, "end_line": 14}}],
        }
        self.assertFalse(validate._options_value_present(entry))

    def test_collected_dash_lines_outside_block_still_collect(self):
        # Pin direction, passing before and after: the
        # CH-48 collected lines form outside a block.
        entry = {
            "fields": [{"label": "The options are", "value": "",
                        "line": 10}],
            "body_lines": [
                (10, "The options are:"),
                (11, ""),
                (12, "- Option A"),
                (13, "- Option B"),
            ],
            "decision_blocks": [],
        }
        self.assertTrue(validate._options_value_present(entry))


class Ch72PinsTest(unittest.TestCase):
    """CH-72 pins: the CH-22 and CH-48 pins whole at this
    surface. Every test in this class passes before and
    after, save where a class docstring states otherwise."""

    def test_taught_alias_inline_forms_still_count(self):
        for line in ("The options are: Option A, Option B",
                     "The three options are: Option A, Option B, "
                     "Option C",
                     "The options stated plainly: Option A, "
                     "Option B",
                     "The options: Option A, Option B"):
            with self.subTest(line=line):
                output = run(options_queue([line]))
                self.assertEqual(
                    missing_options_statements(output), [])

    def test_alias_alone_outside_block_collects_its_dash_lines(self):
        # The CH-48 pin the charge names: the alias alone
        # forms collecting their dash lines outside a block.
        for lines in (["The options are:", "- Option A",
                       "- Option B"],
                      ["The options:", "- Option A", "- Option B"],
                      ["The three options are:", "- Option A",
                       "- Option B", "- Option C"]):
            with self.subTest(lines=lines):
                data = options_queue(lines)
                output = run(data)
                self.assertEqual(
                    missing_options_statements(output), [])
                self.assertEqual(cli_code(data), 0)

    def test_exact_label_alone_collects_its_dash_lines(self):
        output = run(options_queue(
            ["Options:", "- Option A", "- Option B"]))
        self.assertEqual(missing_options_statements(output), [])

    def test_alias_lower_case_takes_missing_warning(self):
        # Control g26, passing before and after: the alias
        # in all lower case is rejected, as the paper
        # records, because the field recording requires a
        # capital first letter.
        output = run(options_queue(
            ["the options are: Option A, Option B"]))
        self.assertEqual(len(missing_options_statements(output)), 1)

    def test_exact_label_mixed_case_takes_missing_warning(self):
        # Control g23, passing before and after: the exact
        # label in a mixed case form is rejected, as every
        # sibling label is.
        output = run(options_queue(
            ["OpTiOnS: Option A, Option B"]))
        self.assertEqual(len(missing_options_statements(output)), 1)

    def test_gibberish_alias_boundary_takes_missing_warning(self):
        output = run(options_queue(
            ["The optionsXYZ: Option A, Option B"]))
        self.assertEqual(len(missing_options_statements(output)), 1)


if __name__ == "__main__":
    unittest.main()
