"""Slice 2, parse group.

Covers the line partition under the decided terminator rule, heading
recognition, span cutting with label reattachment, the element
inventory in element order, the file level failure result and its per
kind line count rules, the unparsed entry carriage at parse level, and
the parse owned counts. Expectations are the brief forms and the
corpus manifest values.
"""

import unittest

import dqv_harness as h


def _failure_for(data, name="generated.md"):
    result = h.run_parse(data, name)
    return result


def _failure_line_count(result):
    return h.get(result, "line_count", "lines")


def _failure_kinds(result):
    kinds = h.get(result, "failure_kinds", "kinds", "failure_kind")
    texts = []
    for kind in h.as_list(kinds):
        texts.append((h.text_of(kind) or "").lower())
    return " ".join(texts)


class LinePartitionTest(unittest.TestCase):

    def test_r1_line_count_and_header_measurements(self):
        model, _output = h.cached_pipeline("R1")
        facts = h.get(model, "header_facts", "file_header_facts")
        self.assertEqual(h.int_of(h.get(facts, "line_count")), 4554)
        self.assertEqual(h.int_of(h.get(facts, "byte_count")), 379560)

    def test_line_feed_and_crlf_count_as_terminators(self):
        model = h.run_parse(b"one\ntwo\r\nthree\n", "lines.md")
        self.assertFalse(h.is_failure_result(model))
        facts = h.get(model, "header_facts", "file_header_facts")
        self.assertEqual(h.int_of(h.get(facts, "line_count")), 3)

    def test_final_line_without_terminator_counts(self):
        model = h.run_parse(b"one\ntwo", "lines.md")
        facts = h.get(model, "header_facts", "file_header_facts")
        self.assertEqual(h.int_of(h.get(facts, "line_count")), 2)

    def test_trailing_terminator_adds_no_line_but_two_add_a_blank(self):
        data, _facts = h.terminator_lines_input(4)
        model = h.run_parse(data, "term.md")
        facts = h.get(model, "header_facts", "file_header_facts")
        self.assertEqual(h.int_of(h.get(facts, "line_count")), 4)
        data2 = data + b"\n"
        model2 = h.run_parse(data2, "term.md")
        facts2 = h.get(model2, "header_facts", "file_header_facts")
        self.assertEqual(h.int_of(h.get(facts2, "line_count")), 5)

    def test_exactly_10000_terminated_lines_does_not_breach(self):
        data, facts = h.terminator_lines_input(10000)
        self.assertEqual(facts["lines"], 10000)
        result = h.run_parse(data, "term10000.md")
        self.assertFalse(h.is_failure_result(result))

    def test_one_further_terminator_breaches_at_10001_lines(self):
        data, _facts = h.terminator_lines_input(10000)
        data = data + b"\n"
        self.assertEqual(h.count_lines_formula(data), 10001)
        result = h.run_parse(data, "term10001.md")
        self.assertTrue(h.is_failure_result(result))
        self.assertIn("line", _failure_kinds(result))
        self.assertEqual(h.int_of(_failure_line_count(result)), 10001)

    def test_lone_carriage_return_variant(self):
        data, facts = h.lone_carriage_return_input()
        self.assertEqual(facts["lines"], 6)
        model = h.run_parse(data, "lone_cr.md")
        self.assertFalse(h.is_failure_result(model))
        model_facts = h.get(model, "header_facts", "file_header_facts")
        self.assertEqual(h.int_of(h.get(model_facts, "line_count")), 6)
        lines = h.get(model, "lines", "model_lines", "line_texts")
        texts = []
        for line in h.as_list(lines):
            if isinstance(line, str):
                texts.append(line)
            else:
                texts.append(h.text_of(h.get(line, "text", "line_text",
                                             "content")))
        # The six line texts bind in every path: a model whose lines
        # cannot be read as texts fails here instead of passing on
        # the span presence assertions alone.
        self.assertEqual(len(texts), 6)
        self.assertEqual(texts, facts["expected_texts"])
        entry = h.entry_by_id(model, "DQ-901")
        self.assertIsNotNone(entry)
        spans = h.as_list(h.get(entry, "spans", "span"))
        self.assertTrue(spans)

    def test_lone_carriage_return_counts_as_a_character_not_a_line(self):
        data, _facts = h.lone_carriage_return_input()
        model = h.run_parse(data, "lone_cr.md")
        facts = h.get(model, "header_facts", "file_header_facts")
        longest = h.get(facts, "longest_line_length",
                        "longest_line_length_in_characters")
        expected = max(len(text) for text in
                       h.lone_carriage_return_input()[1]["expected_texts"])
        self.assertEqual(h.int_of(longest), expected)


class LimitBreachTest(unittest.TestCase):

    def test_byte_limit_breach_is_a_file_level_failure(self):
        data, facts = h.limit_bytes_input()
        self.assertGreater(facts["bytes"], h.MAX_BYTES)
        result = _failure_for(data)
        self.assertTrue(h.is_failure_result(result))
        self.assertIn("byte", _failure_kinds(result))
        breached = h.get(result, "breached_limit", "limit")
        measured = h.get(result, "measured_value", "measured")
        if breached is not None:
            self.assertIn("byte", (h.text_of(breached) or "").lower())
        if measured is not None:
            self.assertEqual(h.int_of(measured), facts["bytes"])

    def test_byte_limit_breach_line_count_is_absent(self):
        data, _facts = h.limit_bytes_input()
        result = _failure_for(data)
        self.assertIsNone(_failure_line_count(result))

    def test_line_limit_breach_line_count_is_present(self):
        data, facts = h.limit_lines_input()
        self.assertEqual(facts["lines"], 10001)
        result = _failure_for(data)
        self.assertTrue(h.is_failure_result(result))
        self.assertEqual(h.int_of(_failure_line_count(result)), 10001)

    def test_per_line_limit_breach_line_count_is_present(self):
        data, _facts = h.limit_chars_input()
        result = _failure_for(data)
        self.assertTrue(h.is_failure_result(result))
        self.assertIn("line", _failure_kinds(result))
        self.assertIsNotNone(_failure_line_count(result))

    def test_invalid_bytes_line_count_is_absent(self):
        data = b"# Decision queue\n\n### DQ-901: Bad bytes\n\n\xff\xfe\n"
        result = _failure_for(data)
        self.assertTrue(h.is_failure_result(result))
        self.assertIn("invalid", _failure_kinds(result))
        self.assertIsNone(_failure_line_count(result))


class HeadingRecognitionTest(unittest.TestCase):

    def test_r1_headed_and_dq_entry_counts(self):
        model, _output = h.cached_pipeline("R1")
        entries = h.entries_of(model)
        self.assertEqual(len(entries), 157)
        numbered = [entry for entry in entries
                    if h.entry_identifier(entry)
                    and h.entry_identifier(entry).startswith("DQ-")]
        self.assertEqual(len(numbered), 156)

    def test_h4_heading_naming_dq_numbers_creates_no_entry(self):
        model, _output = h.cached_pipeline("R1")
        identifiers = [h.entry_identifier(entry)
                       for entry in h.entries_of(model)]
        self.assertEqual(identifiers.count("DQ-145"), 1)
        self.assertEqual(len(identifiers), 157)
        self.assertEqual(h.int_of(h.get(model, "h4_sub_heading_count")),
                         113)

    def test_r2_contrast_run_dq156_absent(self):
        model, _output = h.cached_pipeline("R2")
        identifiers = [h.entry_identifier(entry)
                       for entry in h.entries_of(model)]
        self.assertEqual(len(identifiers), 156)
        self.assertNotIn("DQ-156", identifiers)

    def test_unnumbered_r7_entry_is_an_entry_with_null_identifier(self):
        model, _output = h.cached_pipeline("R1")
        unnumbered = [
            entry for entry in h.entries_of(model)
            if not (h.entry_identifier(entry) or "").startswith("DQ-")]
        self.assertEqual(len(unnumbered), 1)
        heading = h.text_of(h.get(unnumbered[0], "heading",
                                  "heading_text")) or ""
        self.assertIn("R-7", heading)

    def test_heading_borne_evidence_orders_before_body_elements(self):
        model, _output = h.cached_pipeline("R1")
        entry = h.entry_by_id(model, "DQ-156")
        self.assertIsNotNone(entry)
        elements = h.as_list(h.get(entry, "status_elements", "elements"))
        self.assertTrue(elements)
        kinds = [(h.text_of(h.get(el, "kind", "element_kind")) or "")
                 for el in elements]
        self.assertTrue(any("heading" in kind.lower()
                            for kind in kinds))
        heading_index = next(i for i, kind in enumerate(kinds)
                             if "heading" in kind.lower())
        self.assertEqual(heading_index, 0)

    def test_origin_line_without_status_matter_is_a_field_only(self):
        model, _output = h.cached_pipeline("R1")
        entry = h.entry_by_id(model, "DQ-153")
        self.assertIsNotNone(entry)
        fields = h.as_list(h.get(entry, "fields", "field_list"))
        labels = [(h.text_of(h.get(field, "label")) or "")
                  for field in fields]
        self.assertTrue(any("Origin" in label for label in labels))
        elements = h.as_list(h.get(entry, "status_elements", "elements"))
        kinds = [(h.text_of(h.get(el, "kind", "element_kind")) or "")
                 for el in elements]
        self.assertFalse(any("origin" in kind.lower() for kind in kinds))

    def test_unmatched_heading_variants(self):
        for variant in ("second_h1", "h5", "h6"):
            with self.subTest(variant=variant):
                data, _facts = h.unmatched_heading_input(variant)
                model, output = h.run_pipeline(data, "unmatched.md")
                self.assertFalse(h.is_failure_result(model))
                entries = h.entries_of(model)
                self.assertEqual(len(entries), 1)
                warnings = [finding for finding in h.findings_of(output)
                            if h.finding_rule_number(finding) == 5
                            and h.finding_severity(finding) == "Warning"]
                self.assertEqual(len(warnings), 1)
                self.assertEqual(
                    h.finding_entry_id(warnings[0]), "FILE")
                orphans = h.as_list(h.get(model, "orphan_segments"))
                self.assertTrue(orphans)
                self.assertEqual(
                    h.as_list(h.get(model, "unassigned_lines")), [])
                self.assertEqual(h.exit_code_of(output), 1)

    def test_bare_token_heading_without_title_is_unmatched(self):
        data = (h._header_block() +
                "### DQ-901\n\nProse under a bare token heading.\n"
                ).encode("utf-8")
        model, output = h.run_pipeline(data, "bare.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(h.entries_of(model), [])
        warnings = [finding for finding in h.findings_of(output)
                    if h.finding_rule_number(finding) == 5]
        self.assertEqual(len(warnings), 1)


class SpanAndElementOrderTest(unittest.TestCase):

    def test_s8_reattachment_flags_span_non_contiguous(self):
        model, _output = h.cached_pipeline("S8")
        entry = h.entry_by_id(model, "DQ-901")
        self.assertIsNotNone(entry)
        spans = h.as_list(h.get(entry, "spans", "span"))
        flags = [h.get(span, "non_contiguous", "noncontiguous")
                 for span in spans]
        self.assertTrue(any(flags))
        notes = h.as_list(h.get(model, "parse_notes", "notes"))
        entry_notes = h.as_list(h.get(entry, "parse_notes", "notes"))
        self.assertTrue(notes or entry_notes)

    def test_s19_segment_elements_order_by_their_own_lines(self):
        model, _output = h.cached_pipeline("S19")
        entry = h.entry_by_id(model, "DQ-901")
        elements = h.as_list(h.get(entry, "status_elements", "elements"))
        lines = [h.span_of(element)[0] for element in elements]
        self.assertEqual(lines, sorted(lines))
        dispositions = []
        for element in elements:
            tup = h.get(element, "tuple", "element_tuple", "core_tuple")
            if tup is not None:
                dispositions.append(h.text_of(tuple(tup)[0]))
            else:
                dispositions.append(h.text_of(
                    h.get(element, "disposition")))
        self.assertIn("Ruled", dispositions)
        self.assertEqual(dispositions[-1], "Settled")

    def test_coincident_elements_order_by_position_within_the_line(self):
        data, _facts = h.coincident_input()
        model = h.run_parse(data, "coincident.md")
        entry = h.entry_by_id(model, "DQ-901")
        self.assertIsNotNone(entry)
        elements = h.as_list(h.get(entry, "status_elements", "elements"))
        self.assertGreaterEqual(len(elements), 2)
        keys = []
        for element in elements:
            line = h.span_of(element)[0]
            position = h.get(element, "position_in_line",
                             "value_position", "position",
                             "position_within_line")
            keys.append((line, h.int_of(position)))
        self.assertEqual(keys, sorted(keys))
        same_line = [key for key in keys if key[0] == keys[-1][0]]
        self.assertGreaterEqual(len(same_line), 1)
        last = elements[-1]
        tup = h.get(last, "tuple", "element_tuple", "core_tuple")
        disposition = h.text_of(tuple(tup)[0]) if tup is not None else \
            h.text_of(h.get(last, "disposition"))
        self.assertEqual(disposition, "Ruled")

    def test_r9_post_closing_addition_stays_inside_its_entry(self):
        model, _output = h.cached_pipeline("R9")
        entries = h.entries_of(model)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        spans = h.as_list(h.get(entry, "spans", "span"))
        ends = [h.span_of(span)[1] for span in spans
                if not isinstance(span, dict) or True]
        self.assertTrue(ends)
        flag = h.get(entry, "post_status_blocks", "post_status_flag",
                     "has_post_status_blocks")
        self.assertTrue(bool(flag))

    def test_r8_orphan_segments_and_assignment(self):
        model, _output = h.cached_pipeline("R8")
        orphans = h.as_list(h.get(model, "orphan_segments"))
        self.assertEqual(len(orphans), 3)
        self.assertEqual(h.as_list(h.get(model, "unassigned_lines")), [])
        self.assertEqual(
            h.as_list(h.get(model, "double_assigned_lines",
                            "double_assigned")), [])

    def test_s7c_span_is_carried_as_unparsed_at_parse(self):
        model, _output = h.cached_pipeline("S7c")
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-901")
        self.assertIsNotNone(entry)
        self.assertTrue(bool(h.get(entry, "unparsed", "unparsed_flag")))

    def test_parse_records_a_note_for_an_unrecognised_label_lead_in(self):
        body = h._header_block()
        body += "### DQ-901: An entry with an unknown label form\n\n"
        body += "Status: Banked\n\n"
        body += "Verdictish: this label form is not a named form.\n\n"
        body += "The question: A question.\n\nOptions:\n- A\n- B\n\n"
        body += "Cost of deciding late: low.\n\nWhat it blocks: a note.\n"
        model = h.run_parse(body.encode("utf-8"), "unknown_label.md")
        self.assertFalse(h.is_failure_result(model))
        notes = h.as_list(h.get(model, "parse_notes", "notes"))
        entry = h.entry_by_id(model, "DQ-901")
        entry_notes = h.as_list(h.get(entry, "parse_notes", "notes")) \
            if entry is not None else []
        self.assertTrue(notes or entry_notes)


class ElementTupleShapeTest(unittest.TestCase):

    def test_element_tuple_has_five_components_and_positions(self):
        model, _output = h.cached_pipeline("S5")
        entry = h.entry_by_id(model, "DQ-001")
        self.assertIsNotNone(entry)
        elements = h.as_list(h.get(entry, "status_elements", "elements"))
        self.assertTrue(elements)
        element = elements[0]
        tup = h.get(element, "tuple", "element_tuple", "core_tuple")
        self.assertIsNotNone(tup)
        self.assertEqual(len(tuple(tup)), 5)
        line = h.get(element, "line", "line_number")
        self.assertIsNotNone(line)
        position = h.get(element, "position_in_line", "value_position",
                         "position", "position_within_line")
        self.assertIsNotNone(position)


class ParseModulePurityTest(unittest.TestCase):

    def test_parse_module_is_pure(self):
        banned = ("open(", "print(", "input(", "os.environ", "getenv",
                  "socket", "urllib", "requests", "random.", "time.time",
                  "datetime.now", "date.today")
        source = h.module_source("parse")
        for token in banned:
            self.assertNotIn(token, source, "parse uses " + token)


class FileLevelFailureParseTest(unittest.TestCase):

    def test_empty_file_failure_carries_line_count_zero(self):
        result = _failure_for(h.fixture_bytes("S7a"), "S7a.md")
        self.assertTrue(h.is_failure_result(result))
        self.assertEqual(h.int_of(_failure_line_count(result)), 0)
        decision = h.get(result, "exit_decision")
        self.assertEqual(h.int_of(h.get(decision, "code", "exit_code")),
                         3)

    def test_header_only_failure_carries_a_line_count(self):
        result = _failure_for(h.fixture_bytes("S7b"), "S7b.md")
        self.assertTrue(h.is_failure_result(result))
        self.assertIsNotNone(_failure_line_count(result))
        self.assertIn("header", _failure_kinds(result))

    def test_no_structure_failure_names_what_is_missing(self):
        result = _failure_for(h.fixture_bytes("S10"), "S10.md")
        self.assertTrue(h.is_failure_result(result))
        self.assertIsNotNone(_failure_line_count(result))
        statement = h.get(result, "missing_structure",
                          "structure_statement", "statement")
        self.assertIsNotNone(statement)


if __name__ == "__main__":
    unittest.main()
