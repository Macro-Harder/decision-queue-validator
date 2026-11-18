"""Restart Step 17 fix wave 3, Fix Seat K9 tests.

Charges: CH-34 (parse, the final line cut off rule, round 3
limbs; findings ATK3-2-01, ATK3-2-02, and ATK3-2-03, all Low)
and CH-36 (parse, the carriage return tail selection; finding
A3-3-F2, Medium), as ruled at section 26 of
design/steps/step-17r-record.md, flag rulings (b) and (j)
especially, and prepared at
design/steps/step-17r-triage3-prep.md.

CH-34 bounds. The Options branch tests each item whole, as
the Blocks branch does, and refuses a value whose last token
is a joining word, as the generic branch does. The bullet
item content is read under the same fragment and joining
word guards the labelled forms take, with the complete
bullet pin of ATK2-2-05 standing unbroken. A final line
complete in a structural form the tool itself teaches (a
heading, a fence delimiter) stands whole. Ruling (j),
express: no note (h) form is cured, discharged, or moved by
this file; the three note (h) forms stand pinned as still
cut below.

CH-36 bound. A tail part whose marker stands behind one
space is selected and counted as the same text on an
ordinary body line is counted, or takes the damaged marker
signal; counted nowhere in silence is the defect. The CH-3
pins stand in this file in their attack paper forms and must
not break.

Every construction stands in the attack papers own shapes
(design/steps/step-17r-attack3-2.md and
step-17r-attack3-3.md). An entry stands whole where it takes
no unparsed marker and no rule 12 finding, and cut where it
takes both.
"""

import unittest

import dqv_harness as h


def _file(final_line):
    body = h._header_block()
    body += "### DQ-001: Sample question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take first?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += final_line
    return body.encode("utf-8")


def _plain_file(final_line):
    body = "# Decision queue\n\n"
    body += "### DQ-001: Sample question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take first?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += final_line
    return body.encode("utf-8")


def _assert_whole(test, data, name):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    entry = h.entry_by_id(model, "DQ-001")
    test.assertFalse(bool(h.get(entry, "unparsed",
                                "unparsed_flag")))
    test.assertEqual(h.findings_for(output, rule=12), [])


def _assert_cut(test, data, name):
    model, output = h.run_pipeline(data, name)
    test.assertFalse(h.is_failure_result(model))
    entry = h.entry_by_id(model, "DQ-001")
    test.assertTrue(bool(h.get(entry, "unparsed",
                               "unparsed_flag")))
    test.assertTrue(h.findings_for(output, rule=12))


def _elements(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "status_elements", "elements"))


def _occurrence_only(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "occurrence_only_elements",
                           "occurrence_only"))


def _total_occurrences(model, entry_id="DQ-001"):
    return len(_elements(model, entry_id)) + \
        len(_occurrence_only(model, entry_id))


def _dispositions(model, entry_id="DQ-001"):
    out = []
    for el in _elements(model, entry_id):
        tup = h.get(el, "tuple", "element_tuple", "core_tuple")
        out.append(h.text_of(tuple(tup)[0]) if tup is not None
                   else h.text_of(h.get(el, "disposition")))
    return out


def _kinds(model, entry_id="DQ-001"):
    return [(h.text_of(h.get(el, "kind", "element_kind")) or "")
            for el in _elements(model, entry_id)]


def _near_texts(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    near = h.as_list(h.get(entry, "near_marker_occurrences"))
    return [(h.text_of(h.get(item, "text")) or "") for item in near]


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


class Step17Fix3K9OptionsWholeItemTest(unittest.TestCase):
    """CH-34, ATK3-2-01: the Options item test is whole."""

    def test_options_list_cut_after_joining_word_is_cut(self):
        _assert_cut(self, _file("Options: Option A, Option B and"),
                    "fix3_k9_opt_dangling_and.md")

    def test_options_single_item_cut_after_joining_word_is_cut(self):
        _assert_cut(self, _file("Options: Option A and"),
                    "fix3_k9_opt_dangling_and_single.md")

    def test_options_item_with_trailing_extra_word_is_cut(self):
        _assert_cut(self,
                    _file("Options: Option A, Option B extra"),
                    "fix3_k9_opt_item_extra_word.md")

    def test_options_complete_forms_stand_whole(self):
        # Pins: the CH-1 complete Options list forms, in the
        # K1 pin shapes and in the and joined form without the
        # Oxford comma that round 3 observation 1 records
        # standing whole.
        for final_line in (
                "Options: Option A, Option B",
                "Options: A, B",
                "Options: Option A, Option B and Option C"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, _file(final_line),
                              "fix3_k9_opt_complete.md")

    def test_options_neighbour_controls_stand_cut(self):
        # Pins from the attack paper neighbouring set: the
        # Blocks twins of the charged forms, the trailing
        # comma form, and the bare and first form.
        for final_line in (
                "Blocks: DQ-002 and",
                "Blocks: DQ-002 extra",
                "Options: Option A, Option B,",
                "Options: and Option A",
                "Options: A, B, Optio"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix3_k9_opt_controls.md")

    def test_note_h_forms_stand_pinned_as_still_cut(self):
        # Ruling (j): the note (h) forms are not cured,
        # discharged, or moved by this charge. The ruled split
        # of ATK2-2-02 and its note (h) part stand pinned as
        # still cut, in the K1 pin shapes.
        for final_line in (
                "Options: Option A, Option B, and Option C",
                "Blocks: none",
                "What it blocks: Item 155 only"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, _file(final_line),
                            "fix3_k9_note_h.md")


class Step17Fix3K9BulletContentTest(unittest.TestCase):
    """CH-34, ATK3-2-02: the bullet content completeness test."""

    def test_bullet_item_cut_mid_word_is_cut(self):
        _assert_cut(
            self,
            _file("- Option B: leave the note unadop"),
            "fix3_k9_bullet_fragment.md")

    def test_bullet_item_ending_on_joining_word_is_cut(self):
        _assert_cut(self, _file("- Option A, Option B and"),
                    "fix3_k9_bullet_dangling_and.md")

    def test_bullet_complete_item_stands_whole(self):
        # The complete bullet pin of ATK2-2-05, standing as a
        # pin that must not break, in both complete shapes the
        # attack papers carry.
        for final_line in (
                "- Option B: leave the note unadopted",
                "- Option B: leave the note adopted"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, _file(final_line),
                              "fix3_k9_bullet_complete.md")


class Step17Fix3K9StructuralFinalLineTest(unittest.TestCase):
    """CH-34, ATK3-2-03: complete structural final lines."""

    def test_level4_heading_final_line_stands_whole(self):
        _assert_whole(self,
                      _plain_file("#### Ruling by Captain JP"),
                      "fix3_k9_h4_complete.md")

    def test_fence_closer_final_line_stands_whole(self):
        body = "# Decision queue\n\n"
        body += "### DQ-001: Sample question\n\n"
        body += "Status: Banked\n\n"
        body += "This question is waiting for a decision.\n\n"
        body += "Question: Which option should we take first?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n\n"
        body += "```\nDQ-002 stands noted.\nBlocks: DQ-002\n\n```"
        _assert_whole(self, body.encode("utf-8"),
                      "fix3_k9_fence_close.md")

    def test_heading_cut_mid_word_stands_unparsed(self):
        # Pin: the round 2 construction of a heading cut mid
        # word (c6 in attack2-2-scratch) stands correctly
        # unparsed. Its final line is an entry heading standing
        # as the last line, cut in its title word.
        model, output = h.run_pipeline(
            _file("### DQ-002: Second samp"),
            "fix3_k9_heading_cut.md")
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-002")
        self.assertIsNotNone(entry)
        self.assertTrue(bool(h.get(entry, "unparsed",
                                   "unparsed_flag")))
        self.assertTrue(h.findings_for(output, rule=12))

    def test_complete_entry_heading_final_line_no_delta(self):
        # Pin from round 3 observation 6: the entry heading
        # form as a final line stands unparsed in both its
        # unterminated and terminated forms, so no delta
        # stands on that form and the structural cure does
        # not reach it.
        model, output = h.run_pipeline(
            _file("### DQ-002: Second sample question"),
            "fix3_k9_heading_complete.md")
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-002")
        self.assertIsNotNone(entry)
        self.assertTrue(bool(h.get(entry, "unparsed",
                                   "unparsed_flag")))
        self.assertTrue(h.findings_for(output, rule=12))


class Step17Fix3K9CrTailSpaceTest(unittest.TestCase):
    """CH-36, A3-3-F2: the tail part behind one space."""

    def test_tail_behind_one_space_is_counted(self):
        model = h.run_parse(
            _cr_tail_file([" Status: Banked"]),
            "fix3_k9_cr_space_tail.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertIn("line start Status line", _kinds(model))
        self.assertEqual(_total_occurrences(model), 1)

    def test_variant_tail_behind_one_space_is_counted(self):
        model = h.run_parse(
            _cr_tail_file([" Status unchanged: Ruled"]),
            "fix3_k9_cr_space_variant.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_total_occurrences(model), 1)
        self.assertIn("variant phrasing", _kinds(model))

    def test_near_marker_tail_behind_one_space_takes_signal(self):
        model, output = h.run_pipeline(
            _cr_tail_file([" Statuz: Banked"]),
            "fix3_k9_cr_space_near.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(any("Statuz" in text
                            for text in _near_texts(model)))
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_lowercase_tail_behind_one_space_takes_signal(self):
        model, output = h.run_pipeline(
            _cr_tail_file([" status: Banked"]),
            "fix3_k9_cr_space_lower.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(any("status" in text
                            for text in _near_texts(model)))
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))


class Step17Fix3K9CrTailPinsTest(unittest.TestCase):
    """CH-36 pins: the CH-3 pins whole, in attack paper forms."""

    def test_ch3_three_marked_parts_counted_three(self):
        model = h.run_parse(
            _cr_tail_file(["Status: Banked", "Status: Ruled",
                           "Status: Settled"]),
            "fix3_k9_cr_three.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_total_occurrences(model), 3)

    def test_ch3_near_second_part_takes_rule2_warning(self):
        model, output = h.run_pipeline(
            _cr_tail_file(["Status: Banked", "Statuz: Ruled"]),
            "fix3_k9_cr_exact_near.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertTrue(any("Statuz" in text
                            for text in _near_texts(model)))
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_ch3_lowercase_second_part_takes_rule2_warning(self):
        model, output = h.run_pipeline(
            _cr_tail_file(["Status: Banked", "status: Ruled"]),
            "fix3_k9_cr_exact_lower.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertTrue(any("status" in text
                            for text in _near_texts(model)))
        self.assertTrue(h.findings_for(output, rule=2,
                                       severity="Warning"))

    def test_ch3_variant_and_exact_parts_counted_together(self):
        model = h.run_parse(
            _cr_tail_file(["Status unchanged: Ruled",
                           "Status: Banked"]),
            "fix3_k9_cr_variant_exact.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_total_occurrences(model), 2)
        self.assertIn("Banked", _dispositions(model))

    def test_ch3_empty_value_part_is_counted(self):
        model = h.run_parse(
            _cr_tail_file(["Status: Banked", "Status:"]),
            "fix3_k9_cr_empty_second.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(_total_occurrences(model), 2)
        self.assertIn("Banked", _dispositions(model))

    def test_ch3_bare_and_mark_behind_tails_counted(self):
        # Controls: the bare tail (round 2 k25 form) and the
        # tail behind two byte order marks (round 3 n18 form)
        # each counted once at line start.
        for parts in (["Status: Banked"],
                      ["\ufeff\ufeffStatus: Banked"]):
            with self.subTest(parts=parts):
                model = h.run_parse(
                    _cr_tail_file(parts), "fix3_k9_cr_controls.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn("Banked", _dispositions(model))
                self.assertIn("line start Status line",
                              _kinds(model))
                self.assertEqual(_total_occurrences(model), 1)


if __name__ == "__main__":
    unittest.main()
