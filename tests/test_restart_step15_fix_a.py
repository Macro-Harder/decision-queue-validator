"""Restart Step 15 fix wave 1, Seat A tests.

Source: the plan (design/DESIGN-PLAN-RESTART.md) Item 3, sections
3.2 to 3.7 and 3.9, and the brief PIN-02 and PIN-06, against the
differing forms recorded at design/steps/step-15r-audit1-1.md and
design/steps/step-14r-lead-engineer-shape-review.md section 10.
Each test pins one differing form in the capture layer, types.py
and parse.py. Expectations come from the plan and brief at their
seals, never from a run of the tool.
"""

import dataclasses
import unittest

import dqv_harness as h

HEADER = "# Decision queue\n\nSynthetic queue shaped input.\n\n"

CONTRACT_UNIT_KINDS = {
    "file header", "section introduction", "note section",
    "other file level segment",
}


def parse(data, name="synthetic.md"):
    return h.run_parse(data, name)


def entry(number, title, level=3, body=None):
    marks = "#" * level
    lines = ["%s DQ-%03d: %s" % (marks, number, title), ""]
    lines.extend(body if body is not None else ["Status: Banked", ""])
    return "\n".join(lines) + "\n"


def units_of(model):
    return h.as_list(h.get(model, "units", "file_level_units"))


def unit_kinds(model):
    return [h.text_of(h.get(unit, "kind")) for unit in units_of(model)]


class HeaderFactsFormTest(unittest.TestCase):
    """D-01: header facts are one verbatim text field."""

    def test_header_facts_is_verbatim_text_with_no_subfields(self):
        model = parse((HEADER + entry(1, "First entry")).encode())
        self.assertFalse(h.is_failure_result(model))
        facts = h.get(model, "header_facts", "file_header_facts")
        self.assertIsInstance(
            facts, str,
            "header facts stand as a subfield structure, not as "
            "one verbatim text field")
        self.assertEqual(facts, "# Decision queue")
        for subfield in ("stated_vocabulary", "unit_counts",
                         "longest_line_length", "byte_count",
                         "line_count", "digest", "limits",
                         "vocabulary_version", "input_name"):
            self.assertIsNone(
                getattr(facts, subfield, None),
                "header facts carry the subfield " + subfield)

    def test_header_facts_come_from_the_first_header_only(self):
        text = HEADER + entry(1, "First entry")
        text += "# A later queue header\n\nProse.\n"
        model = parse(text.encode())
        facts = h.get(model, "header_facts", "file_header_facts")
        self.assertEqual(facts, "# Decision queue")


class SourceDesignationTest(unittest.TestCase):
    """D-02, capture side: the file facts shape carries the
    source designation, and parse assigns it on the File shape."""

    def test_file_facts_shape_carries_source_designation(self):
        types = h.import_module("types")
        cls = types.FileFactsData
        names = [item.name for item in dataclasses.fields(cls)]
        self.assertIn("source_designation", names)

    def test_parse_assigns_source_designation_on_the_file(self):
        model = parse((HEADER + entry(1, "First entry")).encode())
        self.assertEqual(
            h.text_of(h.get(model, "source_designation")), "live")


class UnitKindTest(unittest.TestCase):
    """D-03 and D-05: unit kinds and the units list membership."""

    def test_unit_kinds_are_the_contract_kinds_only(self):
        text = HEADER + entry(130, "The entry before the notes")
        text += "### Amendment note, 2026-11-10\n\n" \
                "This note amends DQ-006.\n\n"
        text += "### A heading matching no known form\n\nProse.\n"
        model = parse(text.encode())
        self.assertFalse(h.is_failure_result(model))
        kinds = unit_kinds(model)
        for kind in kinds:
            self.assertIn(kind, CONTRACT_UNIT_KINDS,
                          "unit kind outside the contract list: "
                          + str(kind))
        self.assertIn("note section", kinds,
                      "the note section stands under no Unit kind")

    def test_second_queue_header_stands_as_file_header_unit(self):
        text = HEADER + entry(1, "First entry")
        text += "# Decision queue\n\nRepeated header prose.\n"
        model = parse(text.encode())
        headers = [unit for unit in units_of(model)
                   if h.text_of(h.get(unit, "kind")) == "file header"]
        self.assertEqual(len(headers), 2,
                         "a later queue header stands as no file "
                         "header unit in the units list")

    def test_orphan_units_stand_in_the_units_list(self):
        text = HEADER + entry(1, "First entry")
        text += "### Amendment note, 2026-11-10\n\n" \
                "This note amends DQ-006.\n"
        model = parse(text.encode())
        kinds = unit_kinds(model)
        self.assertIn("note section", kinds,
                      "the note section unit is filtered out of "
                      "the units list")


class EntryIdentifierTest(unittest.TestCase):
    """D-06: the identifier is the numeric value, or the literal
    heading text for the named R-7 entry."""

    def test_numbered_identifier_is_the_numeric_value(self):
        model = parse((HEADER + entry(7, "Seven")).encode())
        record = h.entries_of(model)[0]
        ident = h.get(record, "identifier")
        self.assertIsInstance(ident, int,
                              "the identifier is not the numeric "
                              "value the heading digits denote")
        self.assertNotIsInstance(ident, str)
        self.assertEqual(int(ident), 7)

    def test_r7_identifier_is_the_literal_heading_text(self):
        text = HEADER + "### R-7 closure conflict\n\n" \
               "Status: RULED, closed\n"
        model = parse(text.encode())
        record = h.entries_of(model)[0]
        self.assertEqual(h.get(record, "identifier"),
                         "R-7 closure conflict")


class ParseVocabularyLookupTest(unittest.TestCase):
    """D-19 and A1-F5: parse holds no vocabulary mapping lookup
    and imports no validate layer shapes."""

    def test_parse_records_no_disposition_from_the_mapping(self):
        text = HEADER + entry(1, "One", body=["Status: Café fermé", ""])
        model = parse(text.encode())
        record = h.entries_of(model)[0]
        elements = h.as_list(h.get(record, "status_elements"))
        self.assertTrue(elements)
        self.assertIsNone(
            elements[0].disposition,
            "parse derived a disposition through the shipped "
            "vocabulary mapping for a value whose opening forms "
            "state none")

    def test_parse_module_carries_no_mapping_or_validate_shapes(self):
        parse_module = h.import_module("parse")
        for name in ("_SHIPPED_VOCABULARY_MAPPING", "CensusEntry",
                     "DistinctPhrasingCount", "Finding",
                     "HeadedEntryCount", "ReconciliationBlock",
                     "ValidateOutput", "VerbatimAppendixRow"):
            self.assertFalse(
                hasattr(parse_module, name),
                "parse carries the unused or barred name " + name)


class TypesPartsTest(unittest.TestCase):
    """The types parts of D-11 and D-17, and D-14, and A1-F6."""

    def test_residue_item_fields_are_the_contract_fields(self):
        types = h.import_module("types")
        names = [item.name for item in
                 dataclasses.fields(types.ResidueItem)]
        self.assertEqual(
            names, ["phrasing", "entry_identifier", "line_span"])

    def test_manifest_entry_carries_a_label_per_expected_count(self):
        types = h.import_module("types")
        cls = types.CorpusManifestEntry
        names = [item.name for item in dataclasses.fields(cls)]
        self.assertEqual(
            names[:9],
            ["fixture", "kind", "source", "hash", "bytes_count",
             "lines_count", "expected_counts", "expected_findings",
             "expected_exit"])
        self.assertIn("expected_count_labels", names)
        value = cls(fixture="F-01",
                    expected_counts={"headed entries": 2},
                    expected_count_labels={"headed entries": "pinned"})
        self.assertEqual(
            value.expected_count_labels["headed entries"], "pinned")

    def test_validate_output_carries_entry_groups_and_units_key(self):
        types = h.import_module("types")
        cls = types.ValidateOutput
        names = [item.name for item in dataclasses.fields(cls)]
        self.assertIn("entry_groups", names)
        self.assertIn("counting_units", names)
        key_cls = getattr(types, "CountingUnitsKey", None)
        self.assertIsNotNone(
            key_cls, "no counting units shape stands on the model")
        key = key_cls()
        self.assertEqual(key.canonical_counts, "entries")
        self.assertEqual(key.headed_entry_count, "headed entries")

    def test_file_facts_and_model_carry_designation_and_groups(self):
        output = h.import_module("types").ValidateOutput()
        self.assertEqual(output.entry_groups, [])

    def test_appendix_row_carries_no_unclassified_flag(self):
        types = h.import_module("types")
        names = [item.name for item in
                 dataclasses.fields(types.VerbatimAppendixRow)]
        self.assertNotIn("unclassified", names)


class UnnumberedHeadingTest(unittest.TestCase):
    """A1-F1: no unnumbered headed entry other than the named
    R-7 entry stands as an entry."""

    def test_other_r_number_headings_are_not_entries(self):
        for heading in ("R-8 Another thing", "R-12 whatever",
                        "R-7 other title"):
            text = HEADER + entry(1, "First entry")
            text += "### " + heading + "\n\nProse.\n"
            model = parse(text.encode())
            self.assertEqual(len(h.entries_of(model)), 1,
                             heading + " stood as a headed entry")
            kinds = unit_kinds(model)
            self.assertIn("other file level segment", kinds,
                          heading + " stands as no file level unit")


class AssembledOrderTest(unittest.TestCase):
    """A1-F2: elements stand in assembled order under PIN-02."""

    def test_reattached_element_stands_last_in_assembled_order(self):
        lines = [
            "# Decision queue", "",
            "### DQ-001: First entry", "",
            "Status: Banked", "",
            "Addition to DQ-002: a later note",
            "Status: Parked", "",
            "### DQ-002: Second entry", "",
            "Status: Open", "",
        ]
        model = parse(("\n".join(lines) + "\n").encode())
        records = {int(h.get(r, "identifier")): r
                   for r in h.entries_of(model)}
        elements = h.as_list(
            h.get(records[2], "status_elements"))
        self.assertTrue(elements)
        self.assertEqual(elements[-1].disposition, "Parked",
                         "the last element in the list is not the "
                         "reattached element, so last in the list "
                         "is not last in assembled order")
        self.assertEqual(elements[-1].line, 8)
        self.assertEqual(elements[0].line, 12)


class UnmatchedBeforeFirstEntryTest(unittest.TestCase):
    """A1-F3: a level 2 heading before the first entry, matching
    no known form, is never silently folded into the file header."""

    def test_random_heading_before_first_entry_stands_as_a_unit(self):
        lines = [
            "# Decision queue", "",
            "## Random Heading", "",
            "Prose under the random heading.", "",
            "## DQ-001: First entry", "",
            "Status: Banked", "",
        ]
        model = parse(("\n".join(lines) + "\n").encode())
        self.assertFalse(h.is_failure_result(model))
        matches = [unit for unit in units_of(model)
                   if h.text_of(h.get(unit, "heading_text"))
                   == "Random Heading"]
        self.assertEqual(len(matches), 1,
                         "the random heading stands in no unit")
        self.assertEqual(h.text_of(h.get(matches[0], "kind")),
                         "other file level segment")
        header_units = [unit for unit in units_of(model)
                        if h.text_of(h.get(unit, "kind"))
                        == "file header"]
        start, end = h.span_of(header_units[0])
        self.assertLess(end, 3,
                        "the file header unit covers the random "
                        "heading span")


class NoteSectionHeuristicTest(unittest.TestCase):
    """A1-F4: a heading is a note section only in a recorded
    form, never because the word note stands anywhere in it."""

    def test_progress_note_heading_is_no_note_section(self):
        lines = [
            "# Decision queue", "",
            "### DQ-001: First entry", "",
            "Status: Banked", "",
            "## Progress Note on DQ-001", "",
            "Prose about the entry.", "",
        ]
        model = parse(("\n".join(lines) + "\n").encode())
        matches = [unit for unit in units_of(model)
                   if h.text_of(h.get(unit, "heading_text"))
                   == "Progress Note on DQ-001"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(h.text_of(h.get(matches[0], "kind")),
                         "other file level segment",
                         "the heading was silently classified as "
                         "a note section")

    def test_recorded_note_forms_still_stand_as_note_sections(self):
        text = HEADER + entry(130, "The entry before the notes")
        text += "## Manager's addition note\n\n" \
                "DQ-001 and DQ-002 are stated as still open.\n"
        model = parse(text.encode())
        self.assertIn("note section", unit_kinds(model))


if __name__ == "__main__":
    unittest.main()
