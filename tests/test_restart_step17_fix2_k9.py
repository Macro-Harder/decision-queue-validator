"""Restart Step 17 fix wave 2, Fix Seat K9 tests.

Charges CH-22 and CH-24, ruled at section 19 of
design/steps/step-17r-record.md and prepared at
design/steps/step-17r-triage2-prep.md.

CH-22 (validate, Options presence surfaces): seat 17 findings
S17-ATK2-17-03 and S17-ATK2-17-04. The Options alias prefix in
_has_options_field and _options_value_present has no word
boundary, so a nonsense label opening with the words the
options counts as the Options field; and the restored prose
options form inside a level 4 decision block satisfies the
open entry through _prose_options_line_index, the one scan
the F-17-09 cure did not reach.

CH-24 (validate, digit reading in citations): seat 4 finding
F-3. Digit aliasing survives the F-1 cure on the citation
surfaces: _DQ_TOKEN_RE and _CITATION_PATTERNS read any Unicode
decimal digit and convert with int(), so non ASCII digit
citations are silently read as ASCII numbers in both
directions. The cure pins digit reading in validate.py to
ASCII, and it reaches the introduction count pattern
_INTRODUCTION_PATTERN at the F-15-2-1 locus as well (flag
ruling (h) at record section 19): a section introduction
count written in non ASCII digits is read on no runtime
after the cure, where before the cure a count written in
Arabic Indic digits is read on this runtime and a count
written in Garay digits (U+10D43) is read on a Unicode 16
runtime.

Constructions are the finding papers own constructions,
rebuilt in the attack papers base form.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

ARABIC_888 = "DQ-" + "٨٨٨"
FULLWIDTH_888 = "DQ-" + "８８８"
MIXED_888 = "DQ-" + "8٨8"
DEVANAGARI_888 = "DQ-" + "८८८"
PERSIAN_888 = "DQ-" + "۸۸۸"
ARABIC_002 = "DQ-" + "٠٠٢"
ARABIC_THREE = "٣"
GARAY_THREE = "\U00010d43"


def two_entry_queue(first_body_lines):
    """The attack seat 17 base: DQ-001 carrying the lines under
    test and no other options matter, DQ-002 complete."""
    parts = [
        "# Decision queue\n\n",
        "### DQ-001: A sample open question\n\n",
        "Status: Banked\n\n",
        "This question is waiting for a decision.\n\n",
    ]
    for line in first_body_lines:
        parts.append(line + "\n\n")
    parts.extend([
        "Question: Which option should we take?\n\n",
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


def quarantined_segment_queue(citation_sentence):
    """The attack seat 4 base: a valid DQ-002 entry, then a
    quarantined segment (a zero width space inside its heading
    number) whose body carries the citation sentence."""
    parts = [
        "# Decision queue\n\n",
        "### DQ-002: A sample open question\n\n",
        "Status: Banked\n\n",
        "Question: Which option should we take?\n\n",
        "Options: Option A, Option B\n\n",
        "Cost of deciding late: Work stays blocked.\n\n",
        "Blocks: DQ-999\n\n",
        "A plain paragraph of context for this entry.\n\n",
        "### DQ-00\u200b1: A sample open question\n\n",
        "Status: Banked\n\n",
        "Question: Which option should we take?\n\n",
        "Options: Option A, Option B\n\n",
        "Cost of deciding late: Work stays blocked.\n\n",
        "Blocks: DQ-999\n\n",
        "A plain paragraph of context for this entry.\n\n",
        citation_sentence + "\n",
    ]
    return "".join(parts).encode("utf-8")


def introduction_queue(count_token):
    """The attack seat 15 u2 base: a section introduction
    stating a count of entries, holding one entry."""
    text = (
        "# Decision queue\n\n"
        "## Holding section\n\n"
        "This section holds " + count_token + " entries.\n\n"
        "### DQ-001: The harbour question\n\n"
        "Status: Open\n\n"
        "Question: Which option should we take?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked while this "
        "waits.\n\n"
        "Blocks: DQ-002\n\n"
        "This question is waiting for a decision, recorded "
        "2026-11-17.\n"
    )
    return text.encode("utf-8")


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
            if "options" in s.lower()]


class OptionsAliasBoundaryTest(unittest.TestCase):
    """CH-22, S17-ATK2-17-03: the alias prefix takes a word
    boundary after the prefix."""

    def test_gibberish_label_counts_as_no_options_field(self):
        output = run(two_entry_queue(
            ["The optionsXYZ: Option A, Option B"]))
        self.assertTrue(
            missing_options_statements(output),
            "a label opening with the options and continuing "
            "the word satisfied the Options presence tests")

    def test_gibberish_label_unit_level(self):
        entry = {"fields": [{"label": "The optionsXYZ",
                             "value": "Option A, Option B"}],
                 "body_lines": [], "decision_blocks": []}
        self.assertFalse(validate._has_options_field(entry))
        self.assertFalse(validate._options_value_present(entry))

    def test_options_are_alias_still_counts(self):
        output = run(two_entry_queue(
            ["The options are: Option A, Option B"]))
        self.assertEqual(missing_options_statements(output), [])

    def test_three_options_are_alias_still_counts(self):
        output = run(two_entry_queue(
            ["The three options are: Option A, Option B, "
             "Option C"]))
        self.assertEqual(missing_options_statements(output), [])

    def test_options_stated_plainly_alias_still_counts(self):
        output = run(two_entry_queue(
            ["The options stated plainly: Option A, Option B"]))
        self.assertEqual(missing_options_statements(output), [])


class ProseOptionsInBlockTest(unittest.TestCase):
    """CH-22, S17-ATK2-17-04: the prose options form inside a
    level 4 decision block satisfies nothing."""

    def test_prose_form_inside_h4_block_reads_missing(self):
        data = two_entry_queue([
            "#### Decision block\n\n"
            "The options, stated plainly:\n\n"
            "- Option A: adopt.\n"
            "- Option B: leave."])
        output = run(data)
        self.assertTrue(
            missing_options_statements(output),
            "the prose options form inside a decision block "
            "satisfied the open entry")

    def test_prose_form_inside_block_unit_level(self):
        entry = {
            "fields": [],
            "body_lines": [
                (15, "#### Decision block"),
                (17, "The options, stated plainly:"),
                (19, "- Option A: adopt."),
                (20, "- Option B: leave."),
            ],
            "decision_blocks": [
                {"span": {"start_line": 15, "end_line": 21}}],
        }
        self.assertIsNone(validate._prose_options_line_index(entry))
        self.assertFalse(validate._has_options_field(entry))
        self.assertFalse(validate._options_value_present(entry))

    def test_prose_form_outside_block_still_counts(self):
        data = two_entry_queue([
            "The options, stated plainly:\n\n"
            "- Option A: adopt.\n"
            "- Option B: leave."])
        output = run(data)
        self.assertEqual(missing_options_statements(output), [])


class CitationDigitReadingTest(unittest.TestCase):
    """CH-24, seat 4 F-3: non ASCII digit citations are not
    read as ASCII numbers."""

    def test_token_pattern_reads_ascii_only(self):
        self.assertIsNone(validate._DQ_TOKEN_RE.search(ARABIC_888))
        self.assertIsNone(validate._DQ_TOKEN_RE.search(FULLWIDTH_888))
        self.assertIsNone(validate._DQ_TOKEN_RE.search(MIXED_888))
        self.assertIsNone(validate._DQ_TOKEN_RE.search(ARABIC_002))
        self.assertIsNotNone(validate._DQ_TOKEN_RE.search("DQ-888"))

    def test_citation_patterns_read_ascii_only(self):
        for token in (ARABIC_888, FULLWIDTH_888, DEVANAGARI_888,
                      PERSIAN_888):
            for pattern in validate._CITATION_PATTERNS:
                self.assertIsNone(
                    pattern.search("See the note at " + token),
                    "a citation pattern read " + token)

    def test_ghost_citation_in_segment_is_not_manufactured(self):
        for token in (ARABIC_888, FULLWIDTH_888, MIXED_888,
                      DEVANAGARI_888, PERSIAN_888):
            with self.subTest(token=token):
                output = run(quarantined_segment_queue(
                    "See the note at " + token + " for context."))
                named = [s for s in statements(output)
                         if "DQ-888" in s]
                self.assertEqual(named, [])
                partial = [s for s in statements(output)
                           if "DQ-008" in s]
                self.assertEqual(
                    partial, [],
                    "a mixed script token was read in part as "
                    "an ASCII number")

    def test_ghost_citation_in_headed_entry_is_not_manufactured(self):
        parts = [
            "# Decision queue\n\n",
            "### DQ-001: A sample open question\n\n",
            "Status: Banked\n\n",
            "Question: Which option should we take?\n\n",
            "Options: Option A, Option B\n\n",
            "Cost of deciding late: Work stays blocked.\n\n",
            "Blocks: DQ-999\n\n",
            "A plain paragraph of context for this entry.\n\n",
            "See " + ARABIC_888 + " for the earlier ruling.\n",
        ]
        output = run("".join(parts).encode("utf-8"))
        named = [s for s in statements(output) if "DQ-888" in s]
        self.assertEqual(named, [])

    def test_ascii_citation_still_reports(self):
        output = run(quarantined_segment_queue(
            "See the note at DQ-888 for context."))
        named = [s for s in statements(output) if "DQ-888" in s]
        self.assertTrue(named)


class IntroductionDigitReadingTest(unittest.TestCase):
    """CH-24 at the F-15-2-1 locus: the introduction count
    pattern reads ASCII digits only."""

    def test_introduction_pattern_reads_ascii_only(self):
        self.assertIsNone(validate._INTRODUCTION_PATTERN.search(
            "holds " + ARABIC_THREE + " entries"))
        self.assertIsNone(validate._INTRODUCTION_PATTERN.search(
            "holds " + GARAY_THREE + " entries"))
        self.assertIsNotNone(validate._INTRODUCTION_PATTERN.search(
            "holds 3 entries"))

    def test_arabic_indic_count_takes_no_check8_warning(self):
        output = run(introduction_queue(ARABIC_THREE))
        named = [s for s in statements(output)
                 if "section introduction states" in s]
        self.assertEqual(named, [])

    def test_garay_count_takes_no_check8_warning(self):
        output = run(introduction_queue(GARAY_THREE))
        named = [s for s in statements(output)
                 if "section introduction states" in s]
        self.assertEqual(named, [])

    def test_ascii_count_still_warns_on_mismatch(self):
        output = run(introduction_queue("3"))
        named = [s for s in statements(output)
                 if "section introduction states 3 entries; 1" in s]
        self.assertTrue(named)


if __name__ == "__main__":
    unittest.main()
