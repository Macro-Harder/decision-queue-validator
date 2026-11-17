"""Step 17 fix wave 2, cluster K2 charges, test first.

Charges: CH-2 (A2-3-F1, heading recognition prefixes), CH-3
(A2-3-F2 and A2-3-F6, the carriage return tail scan), CH-20
(seat 6 Finding 1, the unnumbered heading at level 2), and CH-25
(seat 4 F-2, the corrupted identifier refusal kind). Every test
in this file was written before its cure and confirmed failing
on the uncured code for the charged reason.
"""

import unittest

import dqv_harness as h


def _failure_kinds(result):
    kinds = h.get(result, "failure_kinds", "kinds", "failure_kind")
    texts = []
    for kind in h.as_list(kinds):
        texts.append((h.text_of(kind) or "").lower())
    return " ".join(texts)


def _elements(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "status_elements", "elements"))


def _kinds(model, entry_id="DQ-001"):
    return [(h.text_of(h.get(el, "kind", "element_kind")) or "")
            for el in _elements(model, entry_id)]


def _dispositions(model, entry_id="DQ-001"):
    out = []
    for el in _elements(model, entry_id):
        tup = h.get(el, "tuple", "element_tuple", "core_tuple")
        out.append(h.text_of(tuple(tup)[0]) if tup is not None
                   else h.text_of(h.get(el, "disposition")))
    return out


def _occurrence_kinds(model, entry_id="DQ-001"):
    return [(h.text_of(h.get(el, "occurrence_kind")) or "")
            for el in _elements(model, entry_id)]


def _near_texts(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    near = h.as_list(h.get(entry, "near_marker_occurrences"))
    return [(h.text_of(h.get(item, "text")) or "") for item in near]


def _two_entry_file(prefix):
    body = h._header_block()
    body += "### DQ-001: First question\n\nStatus: Banked\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += prefix + "### DQ-002: Second question\n\n"
    body += "Status: Banked\n\n"
    body += "Question: Which other option should we take?\n\n"
    body += "Options: Option C, Option D\n\n"
    body += "Cost of deciding late: More work stays blocked.\n\n"
    body += "Blocks: DQ-001\n\n"
    body += "This question is also waiting for a decision.\n"
    return body.encode("utf-8")


def _cr_tail_file(tail_parts):
    body = h._header_block()
    body += "### DQ-001: A sample open question"
    for part in tail_parts:
        body += "\r" + part
    body += "\n\nQuestion: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n"
    return body.encode("utf-8")


def _sole_heading_file(heading_text):
    body = h._header_block()
    body += "### " + heading_text + "\n\nStatus: Banked\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-999\n\n"
    body += "A plain paragraph of context for this entry.\n"
    return body.encode("utf-8")


class Step17FixK2HeadingPrefixTest(unittest.TestCase):
    """CH-2, A2-3-F1: a prefix before an entry heading."""

    def test_ch2_bom_then_space_before_entry_heading_keeps_entry(self):
        model = h.run_parse(_two_entry_file("﻿ "),
                            "bom_space_heading.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-002"))
        self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch2_space_then_bom_before_entry_heading_keeps_entry(self):
        model = h.run_parse(_two_entry_file(" ﻿"),
                            "space_bom_heading.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-002"))
        self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch2_bom_then_tab_before_entry_heading_keeps_entry(self):
        model = h.run_parse(_two_entry_file("﻿\t"),
                            "bom_tab_heading.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-002"))
        self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch2_one_space_before_entry_heading_keeps_entry(self):
        model = h.run_parse(_two_entry_file(" "),
                            "space_heading.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-002"))
        self.assertEqual(len(h.entries_of(model)), 2)


class Step17FixK2CarriageReturnTailTest(unittest.TestCase):
    """CH-3, A2-3-F2 and A2-3-F6: the heading tail scan."""

    def test_ch3_second_marked_tail_part_is_counted(self):
        model = h.run_parse(
            _cr_tail_file(["Status: Banked", "Status: Ruled"]),
            "cr_two_tails.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        self.assertIn("later Status line", _kinds(model))

    def test_ch3_marked_tail_behind_a_bom_is_counted(self):
        model = h.run_parse(
            _cr_tail_file(["﻿Status: Banked"]),
            "cr_bom_tail.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertIn("line start Status line", _kinds(model))
        self.assertIn("line start", _occurrence_kinds(model))

    def test_ch3_near_marker_tail_takes_a_signal(self):
        model, output = h.run_pipeline(
            _cr_tail_file(["Statuz: Banked"]), "cr_near_tail.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(any("Statuz" in text
                            for text in _near_texts(model)))
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_ch3_lowercase_marker_tail_takes_a_signal(self):
        model, output = h.run_pipeline(
            _cr_tail_file(["status: Banked"]), "cr_lower_tail.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(any("status" in text
                            for text in _near_texts(model)))
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))


class Step17FixK2UnnumberedLevel2Test(unittest.TestCase):
    """CH-20, seat 6 Finding 1: the unnumbered form at level 2."""

    def _level2_file(self):
        body = h._header_block()
        body += "### R-7 closure conflict\n\nStatus: Open\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This entry is waiting for a decision.\n\n"
        body += "## R-7 closure conflict\n\nStatus: Open\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "This entry is waiting for a decision.\n\n"
        body += "### DQ-002: Beta question\n\nStatus: Open\n\n"
        body += "Question: Which other option should we take?\n\n"
        body += "Options: Option C, Option D\n\n"
        body += "Cost of deciding late: Other work stays blocked.\n\n"
        body += "Blocks: DQ-001\n\n"
        body += "This second entry is waiting for a decision.\n"
        return body.encode("utf-8")

    def test_ch20_level2_unnumbered_copy_is_an_entry(self):
        model = h.run_parse(self._level2_file(), "r7_level2.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(len(h.entries_of(model)), 3)
        r7 = [entry for entry in h.entries_of(model)
              if (h.entry_identifier(entry) or "") == "R-7"
              or "R-7 closure conflict" in
              (h.entry_identifier(entry) or "")]
        self.assertEqual(len(r7), 2)

    def test_ch20_level2_unnumbered_copy_takes_duplicate_error(self):
        _model, output = h.run_pipeline(self._level2_file(),
                                        "r7_level2_dup.md")
        errors = h.findings_for(output, rule=1, severity="Error")
        self.assertTrue(any("R-7" in h.finding_statement(item)
                            for item in errors))


class Step17FixK2CorruptedIdentifierTest(unittest.TestCase):
    """CH-25, seat 4 F-2: the corrupted identifier refusal kind."""

    def _assert_corrupted_kind(self, heading_text, name):
        result = h.run_parse(_sole_heading_file(heading_text), name)
        self.assertTrue(h.is_failure_result(result))
        self.assertIn("no recognisable queue structure",
                      _failure_kinds(result))
        self.assertNotIn("header only", _failure_kinds(result))
        statement = h.get(result, "missing_structure",
                          "structure_statement", "statement")
        self.assertIsNotNone(statement)
        self.assertIn("identifier carries characters",
                      h.text_of(statement) or "")

    def test_ch25_arabic_indic_digits_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-٠٠١: A sample open question",
            "arabic_sole.md")

    def test_ch25_fullwidth_digits_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-００１: A sample open question",
            "fullwidth_sole.md")

    def test_ch25_mixed_digit_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-0٠1: A sample open question",
            "mixed_digit_sole.md")

    def test_ch25_soft_hyphen_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-00­1: A sample open question",
            "soft_hyphen_sole.md")

    def test_ch25_hebrew_point_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-00ְ1: A sample open question",
            "hebrew_point_sole.md")

    def test_ch25_combining_20d0_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-00⃐1: A sample open question",
            "combining_20d0_sole.md")

    def test_ch25_zwsp_plus_arabic_digits_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-٠​٠١: A sample open question",
            "zwsp_arabic_sole.md")

    def test_ch25_arabic_letter_mark_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-00؜1: A sample open question",
            "alm_sole.md")

    def test_ch25_persian_digit_sole_heading(self):
        self._assert_corrupted_kind(
            "DQ-00۱: A sample open question",
            "persian_sole.md")

    def test_ch25_plain_section_file_stays_header_only(self):
        body = h._header_block()
        body += "## Section one\n\nPlain prose under a section.\n"
        result = h.run_parse(body.encode("utf-8"),
                             "plain_section.md")
        self.assertTrue(h.is_failure_result(result))
        self.assertIn("header only", _failure_kinds(result))

    def test_ch25_letter_token_heading_stays_header_only(self):
        result = h.run_parse(
            _sole_heading_file("DQ-ABC: A sample open question"),
            "letter_token_sole.md")
        self.assertTrue(h.is_failure_result(result))
        self.assertIn("header only", _failure_kinds(result))
        self.assertNotIn("no recognisable queue structure",
                         _failure_kinds(result))


if __name__ == "__main__":
    unittest.main()
