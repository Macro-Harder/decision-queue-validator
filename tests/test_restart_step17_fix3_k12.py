"""Restart Step 17 fix wave 3, Seat K12 tests.

Charges CH-48 and CH-49, as ruled at section 26 of
design/steps/step-17r-record.md (ruling (m) and FLAG 12
included) and prepared at
design/steps/step-17r-triage3-prep.md.

CH-48 (validate, the Options alias collected lines):
S17-ATK3-17-03 of seat 17 (Low). Where no field recorded
under the exact label Options stands, the alias limb of
_options_value_present returns the truth of its own value
strip and never reaches the collected lines reading, so an
Options alias label standing alone with its dash lines
reads missing, while the exact label in the same shape
collects its dash lines and passes. Cure bound: the alias
limb, on an empty value, reads the following dash lines as
the field value, as the exact label limb does. Pins that
must not break: the CH-22 pins whole, including the alias
boundary forms (digit suffix, gibberish, and underscore
continuation forms taking the missing Warning in the fail
safe direction) and the exact label collected lines pins.

CH-49 (parse, the duplicate heading at level 1): Finding 2
of seat 6 (Low). A duplicate entry heading at heading
level 1 is taken as file structure, counted nowhere, and
named on no surface, with no PIN-06 unmatched heading
Warning, where headings displaced to levels 4 to 6 take
the PIN-06 Warning naming the exact heading. Cure bound,
from ruling (m): a numbered or R-7 entry heading at
level 1 takes the PIN-06 unmatched heading Warning naming
the heading as written, as the levels 4 to 6 forms do, or
stands recognised; the cure names entry heading forms
only, and the queue header at level 1 stands as file
structure and takes no Warning. Pins that must not break:
the CH-20 pins whole and the PIN-06 pins whole, including
the queue header control standing clean.

Constructions are the finding papers own constructions,
rebuilt in the attack papers base forms: the seat 17 two
entry Banked base for CH-48, and the seat 6 Open entry
files for CH-49.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")


def options_queue(first_options_lines):
    """The attack seat 17 base: DQ-001 Banked carrying the
    options lines under test and no other options matter,
    DQ-002 complete with the exact label."""
    parts = [
        "# Decision queue\n\n",
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


def open_entry(heading_line, blocks):
    return (
        heading_line + "\n\n"
        "Status: Open\n\n"
        "Question: Which option should we take?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked.\n\n"
        "Blocks: " + blocks + "\n\n"
        "This entry is waiting for a decision.\n\n")


def dup_queue(level1_heading, with_level3_copy):
    """The attack seat 6 base: the queue header at level 1,
    one entry heading at level 1, then the level 3 entries."""
    parts = ["# Decision queue\n\n"]
    parts.append(open_entry(level1_heading, "DQ-002"))
    if with_level3_copy:
        if level1_heading.startswith("# R-7"):
            parts.append(open_entry("### R-7 closure conflict",
                                    "DQ-002"))
        else:
            parts.append(open_entry("### DQ-001: Alpha", "DQ-002"))
    parts.append(open_entry("### DQ-002: Beta question", "DQ-001"))
    return "".join(parts).encode("utf-8")


def cli_validate(data):
    path = h.temp_input(data)
    code, out, _err = h.run_cli("validate", path)
    return code, out.decode("utf-8", errors="replace")


def run(data):
    _model, output = h.run_pipeline(data)
    if output is None:
        raise AssertionError("pipeline returned a failure")
    return output


def statements(output, entry_id=None):
    found = h.findings_for(output, entry_id=entry_id) \
        if entry_id else h.findings_of(output)
    return [h.finding_statement(f) or "" for f in found]


def missing_options_statements(output):
    return [s for s in statements(output, "DQ-001")
            if "missing its options" in s]


def pin06_findings(output):
    return [f for f in h.findings_of(output)
            if str(h.get(f, "rule_id")) == "PIN-06"]


class Ch48AliasCollectedLinesTest(unittest.TestCase):
    """CH-48: the alias limb, on an empty value, reads the
    following dash lines as the field value."""

    def test_alias_are_alone_with_dash_lines_passes(self):
        data = options_queue(
            ["The options are:", "- Option A", "- Option B"])
        output = run(data)
        self.assertEqual(missing_options_statements(output), [])
        code, _out = cli_validate(data)
        self.assertEqual(code, 0)

    def test_alias_the_options_alone_with_dash_lines_passes(self):
        output = run(options_queue(
            ["The options:", "- Option A", "- Option B"]))
        self.assertEqual(missing_options_statements(output), [])

    def test_alias_three_options_alone_with_dash_lines_passes(self):
        output = run(options_queue(
            ["The three options are:", "- Option A",
             "- Option B", "- Option C"]))
        self.assertEqual(missing_options_statements(output), [])

    def test_alias_collected_lines_unit(self):
        entry = {
            "fields": [{"label": "The options are", "value": ""}],
            "body_lines": [
                (10, "The options are:"),
                (11, ""),
                (12, "- Option A"),
                (13, "- Option B"),
            ],
        }
        self.assertTrue(validate._options_value_present(entry))

    def test_alias_alone_without_dash_lines_still_missing(self):
        # Guard, passing before and after: an alias label alone
        # whose following lines are plain prose collects
        # nothing, as the exact label shape collects dash
        # lines only (seat 17 observation O-8 bound).
        output = run(options_queue(
            ["The options are:", "Option A and Option B"]))
        self.assertEqual(len(missing_options_statements(output)), 1)

    def test_alias_empty_value_no_following_lines_unit(self):
        entry = {
            "fields": [{"label": "The options", "value": ""}],
            "body_lines": [(10, "The options:")],
        }
        self.assertFalse(validate._options_value_present(entry))


class Ch48PinsTest(unittest.TestCase):
    """CH-48 pins: the CH-22 pins whole at this surface."""

    def test_exact_label_alone_with_dash_lines_passes(self):
        # The exact label collected lines pin (the round 2
        # case c23 form), passing before and after.
        output = run(options_queue(
            ["Options:", "- Option A", "- Option B"]))
        self.assertEqual(missing_options_statements(output), [])

    def test_alias_inline_value_still_counts(self):
        output = run(options_queue(
            ["The options are: Option A, Option B"]))
        self.assertEqual(missing_options_statements(output), [])

    def test_digit_suffix_alias_boundary_takes_missing(self):
        # Seat 17 observation O-3 form f10, a CH-22 boundary
        # pin: the digit suffix form counts as no alias and
        # takes the missing Warning in the fail safe direction.
        output = run(options_queue(
            ["The options2: Option A, Option B"]))
        self.assertEqual(len(missing_options_statements(output)), 1)

    def test_gibberish_alias_boundary_takes_missing(self):
        output = run(options_queue(
            ["The optionsXYZ: Option A, Option B"]))
        self.assertEqual(len(missing_options_statements(output)), 1)

    def test_underscore_continuation_boundary_takes_missing(self):
        # Seat 17 observation O-3 form f22.
        output = run(options_queue(
            ["The options_are: Option A, Option B"]))
        self.assertEqual(len(missing_options_statements(output)), 1)


class Ch49Level1EntryHeadingTest(unittest.TestCase):
    """CH-49: a numbered or R-7 entry heading at level 1
    takes the PIN-06 unmatched heading Warning naming the
    heading as written."""

    def test_level1_numbered_duplicate_takes_pin06(self):
        data = dup_queue("# DQ-001: Alpha level one", True)
        output = run(data)
        found = pin06_findings(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha level one",
                      h.finding_statement(found[0]) or "")
        self.assertIn("matches no recognised heading form",
                      h.finding_statement(found[0]) or "")
        code, _out = cli_validate(data)
        self.assertEqual(code, 1)

    def test_level1_numbered_duplicate_counts_no_extra_entry(self):
        output = run(dup_queue("# DQ-001: Alpha level one", True))
        self.assertEqual(int(h.entry_total(output)), 2)
        self.assertFalse(any(
            "used more than once" in s for s in statements(output)))

    def test_level1_r7_heading_takes_pin06(self):
        output = run(dup_queue("# R-7 closure conflict", True))
        found = pin06_findings(output)
        self.assertEqual(len(found), 1)
        self.assertIn("R-7 closure conflict",
                      h.finding_statement(found[0]) or "")

    def test_level1_solo_entry_heading_takes_pin06(self):
        output = run(dup_queue("# DQ-001: Alpha level one", False))
        found = pin06_findings(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha level one",
                      h.finding_statement(found[0]) or "")
        self.assertEqual(int(h.entry_total(output)), 1)

    def test_level1_entry_heading_stands_unmatched_at_parse(self):
        model = h.run_parse(dup_queue("# DQ-001: Alpha level one",
                                      True))
        segments = h.as_list(h.get(model, "orphan_segments"))
        unmatched = [s for s in segments
                     if h.get(s, "unmatched_heading")]
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(h.get(unmatched[0], "heading_text"),
                         "DQ-001: Alpha level one")


class Ch49PinsTest(unittest.TestCase):
    """CH-49 pins: the queue header control and the standing
    PIN-06 forms."""

    def test_queue_header_at_level1_stands_clean(self):
        # The queue header control, passing before and after:
        # the header at level 1 is file structure and takes
        # no Warning, and a plain two entry queue stands clean.
        data = ("# Decision queue\n\n" +
                open_entry("### DQ-001: Alpha", "DQ-002") +
                open_entry("### DQ-002: Beta question", "DQ-001"))
        output = run(data.encode("utf-8"))
        self.assertEqual(pin06_findings(output), [])
        code, _out = cli_validate(data.encode("utf-8"))
        self.assertEqual(code, 0)

    def test_non_entry_level1_heading_takes_no_pin06(self):
        # FLAG 12 bound, passing before and after: the cure
        # names entry heading forms only, so a level 1 heading
        # in no entry form stands as file structure with no
        # PIN-06 Warning.
        data = ("# Decision queue\n\n" +
                open_entry("### DQ-001: Alpha", "DQ-002") +
                open_entry("### DQ-002: Beta question", "DQ-001") +
                "# Appendix notes\n\n"
                "Plain closing prose with no status line.\n")
        output = run(data.encode("utf-8"))
        self.assertEqual(pin06_findings(output), [])

    def test_level4_duplicate_still_takes_pin06(self):
        # The levels 4 to 6 PIN-06 form, passing before and
        # after: the cure reaches level 1 in the same form.
        parts = ["# Decision queue\n\n"]
        parts.append(open_entry("#### DQ-001: Alpha level four",
                                "DQ-002"))
        parts.append(open_entry("### DQ-001: Alpha", "DQ-002"))
        parts.append(open_entry("### DQ-002: Beta question",
                                "DQ-001"))
        output = run("".join(parts).encode("utf-8"))
        found = pin06_findings(output)
        self.assertEqual(len(found), 1)
        self.assertIn("DQ-001: Alpha level four",
                      h.finding_statement(found[0]) or "")


if __name__ == "__main__":
    unittest.main()
