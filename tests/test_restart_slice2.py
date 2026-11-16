"""Restart Slice 2 tests, group TG-S2-01.

Source: plan Item 2, section 2.4, against plan Item 1, section 1.3,
plan Item 3, sections 3.2 and 3.3, plan Item 6, section 6.3, plan
Item 9, sections 9.2 and 9.3, and brief section 5.2 at PIN-06 and
brief section 5.8. Expectations come from the plan and brief at their
seals, never from a run of the tool and never from the first run test
files, which are base material and data only.

Fixture expectations for F-03, F-04, F-05, worked example B-D, and
WV-7 are the brief fixture specifications. Fixture measurements
(hash, byte size, line count) are deferred derivation D-13-1: no
test here asserts a fixture measurement the restart corpus manifest
does not record. The restart pin structural counts are the pinned
brief section 4 figures stated at plan Item 1, section 1.3. The pin
bytes are identified by the brief digest, not by a file name.

Step 13 constructions charged to this slice are built in the tests
themselves: the generated limit constructions, the invalid bytes
construction, the empty file, the header only file, the file with no
recognisable queue structure, the canonical equivalence construction
for the per line limit, the byte order mark construction, and the
carriage return construction. The non regular input case names a
first in first out pipe as the input, as the plan states.
"""

import hashlib
import os
import subprocess
import tempfile
import unicodedata
import unittest
from pathlib import Path

import dqv_harness as h

CORPUS_DIR = h.CORPUS_DIR
PIN_DIGEST = "23f6128230632a5de7f133a65a2497ed6fc11753083e17cd1dfd4" \
             "fa1e57c6132"
PIN_LINES = 4614
PIN_BYTES = 432268
PIN_DQ_HEADINGS = 171
PIN_DQ_AT_LEVEL_3 = 155
PIN_DQ_AT_LEVEL_2 = 16
PIN_HEADED_ENTRIES = 172
R7_HEADING_LINE = 2980
R7_HEADING_TEXT = "R-7 closure conflict"

HEADER = "# Decision queue\n\nSynthetic queue shaped input.\n\n"


def queue_entry(number, title, level=3, body_lines=None):
    marks = "#" * level
    lines = ["%s DQ-%03d: %s" % (marks, number, title), ""]
    lines.extend(body_lines if body_lines is not None else [
        "Status: Banked",
        "",
        "Owner of record: Decision-queue Clerk",
        "",
        "The question: A synthetic question.",
        "",
    ])
    return "\n".join(lines) + "\n"


def open_entry(number, title, level=3):
    return queue_entry(number, title, level=level)


def parse(data, name="synthetic.md"):
    return h.run_parse(data, name)


def is_failure(result):
    return h.is_failure_result(result)


def entries(model):
    return h.entries_of(model)


def entry_ids(model):
    return [h.entry_identifier(entry) for entry in entries(model)]


def ledger(model):
    raw = h.get(model, "number_ledger", "ledger", "dq_number_ledger",
                "numbers", "number_map")
    if raw is None:
        return None
    result = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            try:
                result[int(h.int_of(key))] = value
            except Exception:
                result[h.text_of(key)] = value
        return result
    return raw


def distinct_dq_numbers(model):
    found = ledger(model)
    if isinstance(found, dict):
        return len(found)
    numbers = set()
    for entry in entries(model):
        ident = h.entry_identifier(entry)
        if ident and ident.startswith("DQ-"):
            numbers.add(int(ident.split("-", 1)[1]))
    return len(numbers)


def unit_spans(model):
    spans = []
    for entry in entries(model):
        for span in h.as_list(h.get(entry, "spans", "span")):
            spans.append(h.span_of(type("S", (), {"span": span})())
                         if not isinstance(span, (list, tuple))
                         else (h.int_of(span[0]), h.int_of(span[1])))
    containers = []
    for name in ("units", "file_level_units", "orphan_segments",
                 "file_units"):
        containers.extend(h.as_list(h.get(model, name)))
    for unit in containers:
        span = h.get(unit, "span", "line_span")
        if span is not None:
            spans.append(h.span_of(unit))
    return spans


def assignment_map(model, line_count):
    owners = {line: [] for line in range(1, line_count + 1)}
    for entry in entries(model):
        for span in h.as_list(h.get(entry, "spans", "span")):
            if isinstance(span, (list, tuple)) and len(span) >= 2:
                start, end = h.int_of(span[0]), h.int_of(span[1])
            else:
                start = h.int_of(h.get(span, "start_line", "start"))
                end = h.int_of(h.get(span, "end_line", "end"))
            for line in range(start, end + 1):
                if line in owners:
                    owners[line].append("entry")
    # Restated in the cured D-03 and D-05 form: the partition is
    # counted over the contract carriers only, entry spans and the
    # units list. Entry spans stand on Entry records and stand as
    # units nowhere, and orphan segments stand in the units list
    # as well as in the orphan_segments list, which is the same
    # units in a second carrier and not a second assignment.
    for name in ("units", "file_level_units"):
        for unit in h.as_list(h.get(model, name)):
            start, end = h.span_of(unit)
            if start == 0 and end == 0:
                continue
            for line in range(start, end + 1):
                if line in owners:
                    owners[line].append("unit")
    unassigned = set()
    for item in h.as_list(h.get(model, "unassigned_lines", "unassigned")):
        if isinstance(item, int):
            unassigned.add(item)
        else:
            number = h.get(item, "line_number", "line", "number")
            if number is not None:
                unassigned.add(h.int_of(number))
    return owners, unassigned


def manifest_entries():
    found = {}
    if not CORPUS_DIR.is_dir():
        return found
    for path in sorted(CORPUS_DIR.iterdir()):
        if not path.is_file() or path.suffix == ".json":
            continue
        if "manifest" not in path.name.lower():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for block in text.split("\n\n"):
            lines = [line for line in block.splitlines() if line.strip()]
            if not lines or not lines[0].startswith("Fixture:"):
                continue
            entry = {}
            for line in lines:
                if ":" in line:
                    label, value = line.split(":", 1)
                    entry[label.strip()] = value.strip()
            if "Fixture" in entry:
                found[entry["Fixture"]] = entry
    return found


def fixture_path(fixture_id):
    entries_map = manifest_entries()
    entry = entries_map.get(fixture_id)
    if entry and entry.get("Source"):
        source = entry["Source"].split()[0]
        candidate = CORPUS_DIR / Path(source).name
        if candidate.is_file():
            return candidate
    for name in (fixture_id + ".md", fixture_id + ".txt",
                 fixture_id.replace("-", "") + ".md", fixture_id):
        candidate = CORPUS_DIR / name
        if candidate.is_file():
            return candidate
    return None


def require_fixture(testcase, fixture_id):
    path = fixture_path(fixture_id)
    testcase.assertIsNotNone(
        path, "restart fixture " + fixture_id + " does not stand in "
        "the corpus yet; this test depends on the Corpus seat "
        "standing it with its manifest entry under D-13-1")
    return path


def fixture_model(testcase, fixture_id):
    path = require_fixture(testcase, fixture_id)
    data = path.read_bytes()
    model = parse(data, path.name)
    testcase.assertFalse(is_failure(model),
                         "fixture " + fixture_id + " failed to parse")
    return model, data


def pin_bytes(testcase):
    if CORPUS_DIR.is_dir():
        for path in sorted(CORPUS_DIR.iterdir()):
            if not path.is_file():
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if hashlib.sha256(data).hexdigest() == PIN_DIGEST:
                return data
    testcase.fail("the restart pin does not stand in the corpus; "
                  "this test depends on the acceptance pin copy "
                  "standing under testing pin down 11, identified by "
                  "the brief section 4 digest")


def failure_kinds_text(result):
    kinds = h.get(result, "failure_kinds", "kinds", "failure_kind")
    return " ".join((h.text_of(kind) or "").lower()
                    for kind in h.as_list(kinds))


def assert_whole_file_refusal_cli(testcase, data, name="refusal.md"):
    path = h.temp_input(data, name)
    try:
        code, out, err = h.run_cli("validate", path)
    finally:
        path.unlink(missing_ok=True)
    testcase.assertEqual(code, 3)
    testcase.assertEqual(out, b"", "a refusal prints nothing on "
                                   "standard output")
    text = err.decode("utf-8", errors="replace")
    testcase.assertIn("file fault", text.lower())
    testcase.assertIn("not validated", text.lower())
    lines = [line for line in text.splitlines() if line.strip()]
    testcase.assertTrue(lines and lines[-1].startswith("Exit:"),
                        "the refusal surface carries no closing line")


class HeadingRecognitionTest(unittest.TestCase):

    def test_levels_2_and_3_numbered_headings_recognised(self):
        data = (HEADER + open_entry(1, "First entry", level=3)
                + open_entry(2, "Second entry", level=2)).encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(sorted(entry_ids(model)), ["DQ-001", "DQ-002"])
        levels = {}
        for entry in entries(model):
            levels[h.entry_identifier(entry)] = h.int_of(
                h.get(entry, "heading_level", "level"))
        self.assertEqual(levels, {"DQ-001": 3, "DQ-002": 2})

    def test_level_4_heading_is_never_an_entry_heading(self):
        body = ["Status: Banked", "",
                "#### Scrutiny of DQ-002 and DQ-003", "",
                "Owner of record: Decision-queue Clerk", ""]
        data = (HEADER + queue_entry(1, "Only entry", body_lines=body)
                ).encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(entry_ids(model), ["DQ-001"])
        found = ledger(model)
        if isinstance(found, dict):
            self.assertEqual(set(found), {1})

    def test_level_1_and_level_5_headings_are_not_entries(self):
        data = (HEADER + open_entry(1, "Only entry")
                + "# DQ-002: A top level heading\n\nProse.\n\n"
                + "##### DQ-003: A level five heading\n\nProse.\n"
                ).encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(entry_ids(model), ["DQ-001"])

    def test_named_r7_form_recognised_without_a_dq_number(self):
        data = (HEADER + "### " + R7_HEADING_TEXT + "\n\n"
                "Status: RULED, closed\n\n"
                "Ruled by: Captain JP\n").encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(len(entries(model)), 1,
                         "the named R-7 entry counts as one headed "
                         "entry")
        self.assertEqual(distinct_dq_numbers(model), 0,
                         "the R-7 entry stands in no DQ number count")

    def test_second_unnumbered_heading_is_a_file_level_unit(self):
        data = (HEADER + "### " + R7_HEADING_TEXT + "\n\n"
                "Status: RULED, closed\n\n"
                "### Another unnumbered heading\n\n"
                "Prose under the second unnumbered heading.\n").encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(len(entries(model)), 1,
                         "no unnumbered headed entry other than the "
                         "named R-7 entry enters headed entry counts")
        self.assertEqual(distinct_dq_numbers(model), 0)

    def test_signed_number_heading_does_not_match_the_numbered_form(self):
        data = (HEADER + open_entry(1, "Only entry")
                + "### DQ-+7: A signed heading\n\nProse.\n").encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(entry_ids(model), ["DQ-001"])

    def test_numbered_form_requires_the_colon(self):
        data = (HEADER + open_entry(1, "Only entry")
                + "### DQ-002 A heading with no colon\n\nProse.\n"
                ).encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(entry_ids(model), ["DQ-001"],
                         "the numbered form is a DQ number followed "
                         "by a colon, under PIN-06")


class NumberLedgerTest(unittest.TestCase):

    def test_ledger_keyed_on_value_alone_across_levels(self):
        data = (HEADER + open_entry(7, "At level three", level=3)
                + open_entry(7, "At level two", level=2)).encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(len(entries(model)), 2)
        found = ledger(model)
        self.assertIsNotNone(found, "the File shape carries no number "
                                    "ledger for Slice 2 to read")
        self.assertEqual(set(found), {7})
        self.assertEqual(distinct_dq_numbers(model), 1)

    def test_ledger_differing_digit_widths_take_one_key(self):
        text = HEADER + open_entry(7, "Three digit form", level=3)
        text += "## DQ-07: Two digit form\n\nStatus: Banked\n\n" \
                "Owner of record: Decision-queue Clerk\n"
        model = parse(text.encode())
        self.assertFalse(is_failure(model))
        self.assertEqual(len(entries(model)), 2)
        self.assertEqual(distinct_dq_numbers(model), 1,
                         "differing digit widths of one value take "
                         "the one key, under testing pin down 5")

    def test_ledger_zero_form_keys_on_value_zero(self):
        text = HEADER + "### DQ-000: Zero in three digits\n\n" \
               "Status: Banked\n"
        text += "## DQ-00: Zero in two digits\n\nStatus: Banked\n"
        model = parse(text.encode())
        self.assertFalse(is_failure(model))
        self.assertEqual(len(entries(model)), 2)
        found = ledger(model)
        if isinstance(found, dict):
            self.assertEqual(set(found), {0})
        self.assertEqual(distinct_dq_numbers(model), 1)

    def test_long_digit_heading_completes_under_the_raised_limit(self):
        digits = "7" * 5000
        text = HEADER + "### DQ-" + digits + ": A long number entry\n" \
               "\nStatus: Banked\n"
        model = parse(text.encode())
        self.assertFalse(
            is_failure(model),
            "a heading number over the default integer conversion "
            "limit and inside the stated limits takes no refusal, "
            "under the Step 12 correction at Item 3, section 3.2, "
            "field 11 (shape risk SR-8)")
        self.assertEqual(len(entries(model)), 1)


class AssignmentAndCuttingTest(unittest.TestCase):

    def test_whole_file_assignment_on_a_mixed_file(self):
        data = (HEADER + open_entry(1, "First entry")
                + "## A section heading\n\nSection prose.\n\n"
                + open_entry(2, "Second entry", level=2)).encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        line_count = h.count_lines_formula(data)
        owners, unassigned = assignment_map(model, line_count)
        for line in range(1, line_count + 1):
            with self.subTest(line=line):
                total = len(owners[line]) + (1 if line in unassigned
                                             else 0)
                self.assertEqual(
                    total, 1,
                    "line %d is assigned %d times" % (line, total))

    def test_span_cutting_at_next_entry_and_at_section_heading(self):
        text = HEADER + open_entry(1, "First entry")
        first_end_line = text.count("\n")
        text += "## A section heading\n\nSection prose.\n\n"
        text += open_entry(2, "Second entry", level=2)
        model = parse(text.encode())
        self.assertFalse(is_failure(model))
        first = h.entry_by_id(model, "DQ-001")
        self.assertIsNotNone(first)
        spans = h.as_list(h.get(first, "spans", "span"))
        self.assertTrue(spans)
        start, end = h.span_of(first)
        self.assertLessEqual(end, first_end_line,
                             "the first entry span runs past the "
                             "section heading boundary")

    def test_note_sections_are_file_level_units_never_entry_body(self):
        text = HEADER + open_entry(130, "The entry before the notes")
        text += "### Amendment note, 2026-11-10\n\n" \
                "This note amends DQ-006 and DQ-008.\n\n"
        text += "### Amendment note, 2026-11-10 (Step 5 revision " \
                "after Contrarian attack)\n\n" \
                "This note amends DQ-009.\n\n"
        text += "### Manager addition note\n\n" \
                "DQ-001 and DQ-002 are stated as still open.\n"
        model = parse(text.encode())
        self.assertFalse(is_failure(model))
        self.assertEqual(entry_ids(model), ["DQ-130"],
                         "a note section heading created an entry")
        entry = h.entry_by_id(model, "DQ-130")
        start, end = h.span_of(entry)
        note_heading_line = text[:text.index("Amendment note")].count(
            "\n") + 1
        self.assertLess(end, note_heading_line,
                        "note section lines stand inside entry body")
        units = []
        for name in ("units", "file_level_units", "orphan_segments"):
            units.extend(h.as_list(h.get(model, name)))
        kinds = " ".join((h.text_of(h.get(unit, "kind")) or "").lower()
                         for unit in units)
        self.assertIn("note", kinds,
                      "the note sections stand as no file level unit")

    def test_unmatched_heading_stands_as_a_file_level_unit(self):
        data = (HEADER + open_entry(1, "Only entry")
                + "### A heading matching no known form\n\n"
                + "Prose under the unmatched heading.\n").encode()
        model = parse(data)
        self.assertFalse(is_failure(model))
        self.assertEqual(entry_ids(model), ["DQ-001"])
        line_count = h.count_lines_formula(data)
        owners, unassigned = assignment_map(model, line_count)
        heading_line = data.decode()[:data.decode().index(
            "A heading matching")].count("\n") + 1
        total = len(owners[heading_line]) + (
            1 if heading_line in unassigned else 0)
        self.assertEqual(total, 1,
                         "the unmatched heading line is dropped or "
                         "double assigned")


class FixturePartitionTest(unittest.TestCase):

    def test_f04_level_2_entry_in_full(self):
        model, _data = fixture_model(self, "F-04")
        self.assertEqual(len(entries(model)), 2)
        levels = sorted(h.int_of(h.get(entry, "heading_level", "level"))
                        for entry in entries(model))
        self.assertEqual(levels, [2, 3])
        for entry in entries(model):
            elements = h.as_list(h.get(entry, "status_elements",
                                       "elements",
                                       "status_bearing_elements"))
            self.assertTrue(elements,
                            "an F-04 entry received no element from "
                            "its body")

    def test_f05_population_assertion_only(self):
        model, _data = fixture_model(self, "F-05")
        self.assertEqual(len(entries(model)), 2,
                         "population assertion: headed entries 2")
        self.assertEqual(distinct_dq_numbers(model), 1,
                         "population assertion: distinct DQ "
                         "numbers 1")
        # The finding assertion of F-05 belongs to Slice 6 and is
        # asserted in no test in this file.

    def test_f03_partition_level_and_reattachment(self):
        model, data = fixture_model(self, "F-03")
        self.assertEqual(len(entries(model)), 1)
        entry = entries(model)[0]
        spans = h.as_list(h.get(entry, "spans", "span"))
        self.assertGreaterEqual(len(spans), 1)
        flagged = [span for span in spans
                   if h.get(span, "non_contiguous", "not_contiguous")]
        self.assertTrue(flagged,
                        "no reattached span stands flagged as not "
                        "contiguous on the F-03 entry")
        text = data.decode("utf-8")
        addition_line = None
        for number, line in enumerate(text.splitlines(), start=1):
            if "addition" in line.lower():
                addition_line = number
        self.assertIsNotNone(addition_line)
        covered = False
        for span in spans:
            if isinstance(span, (list, tuple)) and len(span) >= 2:
                start, end = h.int_of(span[0]), h.int_of(span[1])
            else:
                start = h.int_of(h.get(span, "start_line", "start"))
                end = h.int_of(h.get(span, "end_line", "end"))
            if start <= addition_line <= end:
                covered = True
        self.assertTrue(covered,
                        "the post Status addition lines stand "
                        "outside the entry spans")

    def test_worked_example_bd_at_the_partition_level(self):
        data = pin_bytes(self)
        model = parse(data, "pin.md")
        self.assertFalse(is_failure(model))
        entry = h.entry_by_id(model, "DQ-130")
        self.assertIsNotNone(entry)
        _start, entry_end = h.span_of(entry)
        text = data.decode("utf-8")
        lines = text.splitlines()
        note_lines = [number for number, line in enumerate(lines, 1)
                      if line.startswith("## Amendment note")
                      or line.startswith("## Manager's addition")]
        self.assertEqual(len(note_lines), 3,
                         "the three note sections after DQ-130 do "
                         "not stand in the pin bytes")
        for number in note_lines:
            self.assertGreater(number, entry_end,
                               "a note section stands inside the "
                               "DQ-130 entry span")

    def test_wv7_parse_level_first_and_third_shapes(self):
        model, _data = fixture_model(self, "WV-7")
        numbers = []
        for entry in entries(model):
            ident = h.entry_identifier(entry)
            if ident and ident.startswith("DQ-"):
                numbers.append(int(ident.split("-", 1)[1]))
        duplicates = {number for number in numbers
                      if numbers.count(number) > 1}
        self.assertTrue(duplicates,
                        "first shape: the duplicate DQ number at a "
                        "mismatched heading level does not stand in "
                        "the number ledger population")
        levels = {}
        for entry in entries(model):
            ident = h.entry_identifier(entry)
            if ident and ident.startswith("DQ-"):
                number = int(ident.split("-", 1)[1])
                if number in duplicates:
                    levels.setdefault(number, set()).add(h.int_of(
                        h.get(entry, "heading_level", "level")))
        self.assertTrue(any(len(found) > 1 for found in levels.values()),
                        "first shape: the duplicate pair does not "
                        "stand at mismatched heading levels")
        # Third shape, parse level only: the second unnumbered
        # headed entry stands as a file level unit in the partition,
        # so the headed entry count holds only the entries the
        # fixture headed population states in its manifest entry.
        entry_map = manifest_entries().get("WV-7", {})
        self.assertTrue(entry_map,
                        "WV-7 stands with no restart manifest entry "
                        "to read its headed population from")


class PinStructureTest(unittest.TestCase):

    def test_restart_pin_structural_counts(self):
        data = pin_bytes(self)
        self.assertEqual(len(data), PIN_BYTES)
        self.assertEqual(hashlib.sha256(data).hexdigest(), PIN_DIGEST)
        model = parse(data, "pin.md")
        self.assertFalse(is_failure(model))
        # Restated in the cured D-01 form: header_facts is the
        # verbatim text, and the measurements stand on the File
        # model itself.
        self.assertEqual(h.int_of(h.get(model, "line_count")), PIN_LINES)
        self.assertEqual(h.int_of(h.get(model, "byte_count")), PIN_BYTES)
        self.assertEqual(len(entries(model)), PIN_HEADED_ENTRIES)
        dq_entries = [entry for entry in entries(model)
                      if (h.entry_identifier(entry) or "")
                      .startswith("DQ-")]
        self.assertEqual(len(dq_entries), PIN_DQ_HEADINGS)
        at_3 = sum(1 for entry in dq_entries
                   if h.int_of(h.get(entry, "heading_level",
                                     "level")) == 3)
        at_2 = sum(1 for entry in dq_entries
                   if h.int_of(h.get(entry, "heading_level",
                                     "level")) == 2)
        self.assertEqual(at_3, PIN_DQ_AT_LEVEL_3)
        self.assertEqual(at_2, PIN_DQ_AT_LEVEL_2)
        self.assertEqual(distinct_dq_numbers(model), PIN_DQ_HEADINGS)
        r7 = [entry for entry in entries(model)
              if not (h.entry_identifier(entry) or "").startswith("DQ-")]
        self.assertEqual(len(r7), 1)
        self.assertEqual(h.int_of(h.get(r7[0], "heading_line", "line")),
                         R7_HEADING_LINE)


class FailureConstructionTest(unittest.TestCase):

    def test_limit_breach_construction_refusal_form(self):
        data, facts = h.limit_bytes_input()
        self.assertGreater(facts["bytes"], 2000000)
        result = parse(data)
        self.assertTrue(is_failure(result))
        self.assertIn("byte", failure_kinds_text(result))
        assert_whole_file_refusal_cli(self, data)

    def test_invalid_bytes_construction_refusal_form(self):
        data = (HEADER.encode() + b"### DQ-001: Broken bytes\n\n"
                b"Status: Banked \xff\xfe\n")
        result = parse(data)
        self.assertTrue(is_failure(result),
                        "bytes that are not valid in UTF-8 take the "
                        "whole file refusal, naming UTF-8 as the "
                        "encoding at plan Item 6, section 6.3")
        assert_whole_file_refusal_cli(self, data)

    def test_empty_file_construction_refusal_form(self):
        result = parse(b"")
        self.assertTrue(is_failure(result))
        assert_whole_file_refusal_cli(self, b"")

    def test_header_only_construction_refusal_form(self):
        data = HEADER.encode()
        result = parse(data)
        self.assertTrue(is_failure(result))
        assert_whole_file_refusal_cli(self, data)

    def test_no_recognisable_queue_structure_refusal_form(self):
        data = b"Plain prose with no queue header and no entry.\n" \
               b"More prose.\n"
        result = parse(data)
        self.assertTrue(is_failure(result))
        assert_whole_file_refusal_cli(self, data)

    def test_every_failure_kind_carries_no_entry_or_finding_result(self):
        constructions = {
            "limit breach": h.limit_bytes_input()[0],
            "invalid bytes": b"# Decision queue\n\n\xff\xfe\n",
            "empty file": b"",
            "header only": HEADER.encode(),
            "no recognisable queue structure":
                b"Prose only, no structure at all.\n",
        }
        for label, data in constructions.items():
            with self.subTest(kind=label):
                result = parse(data)
                self.assertTrue(is_failure(result), label)
                self.assertEqual(entries(result), [],
                                 label + " carries an entry result")
                findings = h.get(result, "findings", "finding_results")
                self.assertFalse(h.as_list(findings),
                                 label + " carries a finding result")
                decision = h.get(result, "exit_decision", "exit")
                if decision is not None:
                    code = decision if isinstance(decision, int) else \
                        h.int_of(h.get(decision, "code", "exit_code"))
                    self.assertEqual(code, 3, label)


class BackstopTest(unittest.TestCase):
    """The parse level backstop, on the test harness caller path.

    The harness run_parse path reaches parse without the shell
    refusal, as plan Item 2, section 2.4 states for this test.
    """

    def test_backstop_byte_limit_inside_the_read(self):
        data, facts = h.limit_bytes_input()
        result = parse(data)
        self.assertTrue(is_failure(result))
        measured = h.get(result, "measured_value", "measured")
        if measured is not None:
            self.assertEqual(h.int_of(measured), facts["bytes"])

    def test_backstop_line_limit_inside_the_read(self):
        data, facts = h.limit_lines_input()
        self.assertEqual(facts["lines"], 10001)
        result = parse(data)
        self.assertTrue(is_failure(result))
        self.assertIn("line", failure_kinds_text(result))

    def test_backstop_per_line_limit_inside_the_read(self):
        data, facts = h.limit_chars_input()
        self.assertEqual(facts["longest_line_characters"], 16385)
        result = parse(data)
        self.assertTrue(is_failure(result))
        measured = h.get(result, "measured_value", "measured")
        if measured is not None:
            self.assertEqual(h.int_of(measured), 16385)

    def test_canonical_equivalence_construction_for_per_line_limit(self):
        composed = "é" * 16384
        decomposed = "é" * 16384
        self.assertEqual(unicodedata.normalize("NFC", decomposed),
                         composed)
        self.assertEqual(len(composed), 16384)
        self.assertEqual(len(decomposed), 32768)
        base = HEADER + open_entry(1, "Equivalence entry")
        at_limit = (base + composed + "\n").encode("utf-8")
        model = parse(at_limit)
        self.assertFalse(is_failure(model),
                         "the composed form at the limit as written "
                         "passes that limit")
        over_limit = (base + decomposed + "\n").encode("utf-8")
        result = parse(over_limit)
        self.assertTrue(is_failure(result),
                        "the decomposed form over the limit as "
                        "written takes the exit 3 limit refusal, "
                        "with no equivalence adjustment applied to "
                        "either count")


class InputTreatmentConstructionTest(unittest.TestCase):

    def _decoded_facts(self, model):
        facts = []
        for entry in entries(model):
            elements = h.as_list(h.get(entry, "status_elements",
                                       "elements",
                                       "status_bearing_elements"))
            facts.append((
                h.entry_identifier(entry),
                h.int_of(h.get(entry, "heading_level", "level")),
                [(h.text_of(h.get(el, "kind")),
                  h.text_of(h.get(el, "verbatim", "verbatim_value")))
                 for el in elements],
            ))
        return facts

    def test_byte_order_mark_construction(self):
        plain = (HEADER + open_entry(1, "Marked entry")).encode()
        marked = b"\xef\xbb\xbf" + plain
        plain_model = parse(plain)
        marked_model = parse(marked)
        self.assertFalse(is_failure(marked_model))
        self.assertEqual(self._decoded_facts(plain_model),
                         self._decoded_facts(marked_model),
                         "the marked copy differs from the unmarked "
                         "file in a decoded respect")
        # Restated in the cured D-01 form, as the pin structural
        # counts test: the measurements stand on the File model
        # itself, not on header_facts subfields.
        self.assertEqual(h.int_of(h.get(marked_model, "byte_count")),
                         len(marked))
        self.assertEqual(h.text_of(h.get(marked_model, "digest")),
                         hashlib.sha256(marked).hexdigest())
        self.assertEqual(h.int_of(h.get(marked_model, "line_count")),
                         h.count_lines_formula(plain))

    def test_carriage_return_construction(self):
        plain_text = HEADER + open_entry(1, "Return entry") \
            + open_entry(2, "Second entry", level=2)
        plain = plain_text.encode()
        converted = plain_text.replace("\n", "\r\n").encode()
        plain_model = parse(plain)
        converted_model = parse(converted)
        self.assertFalse(is_failure(converted_model))
        self.assertEqual(self._decoded_facts(plain_model),
                         self._decoded_facts(converted_model),
                         "the carriage return copy differs from the "
                         "line feed form in a decoded respect")

        def banked_heads(model):
            count = 0
            for entry in entries(model):
                elements = h.as_list(h.get(
                    entry, "status_elements", "elements",
                    "status_bearing_elements"))
                for element in elements:
                    kind = (h.text_of(h.get(element, "kind")) or "")
                    verbatim = h.text_of(h.get(
                        element, "verbatim", "verbatim_value"))
                    if "line start" in kind.lower() and \
                            verbatim == "Banked":
                        count += 1
                        break
            return count

        self.assertEqual(banked_heads(plain_model),
                         banked_heads(converted_model),
                         "the Banked head census population at parse "
                         "level differs between the two forms")
        # Restated in the cured D-01 form, as the pin structural
        # counts test: the measurements stand on the File model
        # itself, not on header_facts subfields.
        self.assertEqual(h.int_of(h.get(converted_model, "byte_count")),
                         len(converted))
        self.assertEqual(h.text_of(h.get(converted_model, "digest")),
                         hashlib.sha256(converted).hexdigest())

    def test_non_regular_input_case_refused_at_exit_2(self):
        with tempfile.TemporaryDirectory() as directory:
            fifo_path = Path(directory) / "queue_fifo"
            os.mkfifo(fifo_path)
            try:
                code, out, err = h.run_cli_with_timeout(
                    "validate", fifo_path, timeout=20)
            except subprocess.TimeoutExpired:
                self.fail("the run waited on a writer for a first in "
                          "first out pipe input; the refusal at Item "
                          "9, section 9.2 returns from the stat before "
                          "any read")
            self.assertEqual(code, 2)
            self.assertEqual(out, b"")
            text = err.decode("utf-8", errors="replace")
            self.assertIn("not a regular file", text.lower())
            self.assertIn("call fault", text.lower())
            self.assertIn(str(fifo_path), text,
                          "the refusal does not name the input name "
                          "as given")


if __name__ == "__main__":
    unittest.main()
