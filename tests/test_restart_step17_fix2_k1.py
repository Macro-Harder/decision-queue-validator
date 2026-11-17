"""Restart Step 17 fix wave 2, Fix Seat K1 tests (charge CH-1).

CH-1 is the final line cut off rule in parse.py, the functions
_final_line_is_cut_off and _labelled_value_stands_whole. The
findings pinned here are seat 2 findings ATK2-2-01 to
ATK2-2-05 and seat 3 finding A2-3-F7, at the dispositions
ruled at section 19 of design/steps/step-17r-record.md:
ATK2-2-01, ATK2-2-03, ATK2-2-04, ATK2-2-05, and A2-3-F7 cured
in full; ATK2-2-02 cured in part only (the four digit Blocks
reference and the short Options items in the taught list
form), its Oxford comma list form, lower case none form, and
phrase under the Blocks label form standing carried to
design question note (h), pinned here as still cut so the
split stands in the open.

Every construction is one taught form entry (heading, Status
line, an unheaded paragraph, and the labelled fields) whose
final line stands without its terminating newline, in the
seat 2 papers own shapes. An entry stands whole where it
takes no unparsed marker and no rule 12 finding, and cut
where it takes both.
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


def _assert_whole(test, final_line):
    model, output = h.run_pipeline(_file(final_line),
                                   "fix2_k1_whole.md")
    test.assertFalse(h.is_failure_result(model))
    entry = h.entry_by_id(model, "DQ-001")
    test.assertFalse(bool(h.get(entry, "unparsed",
                                "unparsed_flag")))
    test.assertEqual(h.findings_for(output, rule=12), [])


def _assert_cut(test, final_line):
    model, output = h.run_pipeline(_file(final_line),
                                   "fix2_k1_cut.md")
    test.assertFalse(h.is_failure_result(model))
    entry = h.entry_by_id(model, "DQ-001")
    test.assertTrue(bool(h.get(entry, "unparsed",
                               "unparsed_flag")))
    test.assertTrue(h.findings_for(output, rule=12))


class Step17Fix2K1FinalLineTest(unittest.TestCase):
    """Step 17 fix wave 2, seat K1, charge CH-1, test first."""

    def test_atk2_2_01_complete_name_and_source_values_whole(self):
        for final_line in (
                "Owner of record: Clerk in Charge",
                "Owner of record: Leonardo di Caprio",
                "Owner of record: Émile Zola",
                "Source: the clerk",
                "Ruled: Option A is taken"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, final_line)

    def test_atk2_2_02_cured_part_whole(self):
        for final_line in (
                "Blocks: DQ-1000",
                "Options: A, B"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, final_line)

    def test_atk2_2_02_uncured_part_stands_cut(self):
        # The part of ATK2-2-02 carried to design question
        # note (h) at record section 19 flag ruling (b): no
        # cure is charged on these three forms and none is
        # landed here.
        for final_line in (
                "Options: Option A, Option B, and Option C",
                "Blocks: none",
                "What it blocks: Item 155 only"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, final_line)

    def test_atk2_2_03_capitalised_fragment_cut(self):
        _assert_cut(self, "Owner of record: Decision-queue Cler")
        _assert_whole(self,
                      "Owner of record: Decision-queue Clerk")

    def test_atk2_2_04_lower_case_label_whole(self):
        _assert_whole(self, "blocks: DQ-002")

    def test_atk2_2_05_parenthetical_and_bullet_forms_whole(self):
        for final_line in (
                "(See the appendix)",
                "- Option B: leave the note unadopted",
                "Cost of deciding late: Work stays blocked "
                "(for now)"):
            with self.subTest(final_line=final_line):
                _assert_whole(self, final_line)

    def test_a2_3_f7_trailing_byte_order_mark_whole(self):
        # A byte order mark standing alone as the final line,
        # no terminator: the mark is inert and the entry
        # stands whole.
        data = _file("This question is waiting for a decision.")
        data += "\n\ufeff".encode("utf-8")
        model, output = h.run_pipeline(data, "fix2_k1_bom.md")
        self.assertFalse(h.is_failure_result(model))
        entry = h.entry_by_id(model, "DQ-001")
        self.assertFalse(bool(h.get(entry, "unparsed",
                                    "unparsed_flag")))
        self.assertEqual(h.findings_for(output, rule=12), [])
        # A byte order mark appended to a complete final line,
        # no terminator: the same whole standing.
        _assert_whole(
            self, "This question is waiting for a decision."
            "\ufeff")
        # The limiting control from the finding paper: a
        # trailing letter in the same position stands cut.
        _assert_cut(
            self, "This question is waiting for a decision.x")

    def test_cut_controls_stand(self):
        for final_line in (
                "The question: Should the harbour note be ado",
                "Blocks: DQ-00",
                "Options: Option C, Optio",
                "This question is waiting for a decision"):
            with self.subTest(final_line=final_line):
                _assert_cut(self, final_line)


if __name__ == "__main__":
    unittest.main()
