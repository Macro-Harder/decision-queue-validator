"""Restart Step 17 fix wave 2, Seat K5 tests.

Charges CH-4 and CH-5, ruled at section 19 of
design/steps/step-17r-record.md, prepared at
design/steps/step-17r-triage2-prep.md. Both charges stand in
product/decision_queue_validator/validate.py only.

CH-4 (validate, preamble and out of unit status occurrences):
seat 3 findings A2-3-F3 and A2-3-F4 and seat 7 finding
S17-ATK2-7-03, all in _preamble_status_occurrences. A2-3-F3:
a variant Status line in the preamble is counted under a
phrasing that stands nowhere in the file (colon, space, Ruled)
and at the wrong kind. A2-3-F4 and S17-ATK2-7-03: a Status line
standing outside the file header unit and outside any entry
(a section introduction, a note segment between entries, the
preamble under a level 2 heading, a trailing section) is
counted nowhere. The preparation collisions note records that
the variant marker parsing and the reading scope stand in the
one function, so they are taken in one act.

CH-5 (validate, the census Unclassified class test): seat 10
finding A2-10-F3 merged with seat 15 finding F-15-2-2, one
mechanism. The census class test counts any element with no
disposition, so a heading borne evidence element, which
carries no status occurrence, places its entry in the
Unclassified status values class on files where no
unclassified value stands: on this machine through ordinary
one word titles (A2-10-F3), and on the bench runtime through
a Todhri title, whose codepoints are alphabetic only under
that runtime Unicode data (F-15-2-2). The class rule reads:
an entry carrying a status element whose value the vocabulary
does not classify.
"""

import types
import unittest

import dqv_harness as h

validate = h.import_module("validate")

TODHRI_TITLE = "𐗀𐗁𐗂"


def _taught_entry(number, title, status, blocks="DQ-002",
                  paragraph="This question is waiting for a decision."):
    return (
        "### DQ-%03d: %s\n"
        "\n"
        "Status: %s\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: %s\n"
        "\n"
        "%s\n" % (number, title, status, blocks, paragraph))


def _total(output):
    recon = h.reconciliation_of(output)
    return h.int_of(h.get(recon, "status_occurrence_total",
                          "occurrence_total"))


def _rows(output):
    rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                           "appendix_rows", "verbatim_appendix"))
    found = []
    for row in rows:
        found.append((
            h.text_of(h.get(row, "phrasing")),
            h.text_of(h.get(row, "kind", "occurrence_kind")),
            h.int_of(h.get(row, "occurrence_count", "count")),
            [h.text_of(m) for m in h.as_list(
                h.get(row, "member_entry_ids", "members"))],
        ))
    return found


def _unclassified(output):
    item = h.census_class(h.census_of(output), "unclassified")
    if item is None:
        raise AssertionError("no Unclassified census class stands")
    return h.census_count(item), h.census_members(item)


def _run(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned a failure")
    return output


class OutOfUnitStatusOccurrenceTest(unittest.TestCase):
    """CH-4: A2-3-F3, A2-3-F4, and S17-ATK2-7-03."""

    def test_a2_3_f3_variant_status_line_in_preamble_counts_as_written(self):
        # A2-3-F3 (case k54): the line Status unchanged: Ruled
        # standing in the preamble. Inside an entry the same form
        # is counted under its full phrasing, Status unchanged:
        # Banked, at kind variant. The preamble row must read the
        # same: full phrasing, kind variant, member FILE.
        output = _run(
            "# Decision queue\n"
            "\n"
            "Status unchanged: Ruled\n"
            "\n"
            + _taught_entry(1, "A sample open question", "Banked"))
        self.assertEqual(_total(output), 2)
        rows = _rows(output)
        self.assertIn(("Status unchanged: Ruled", "variant", 1,
                       ["FILE"]), rows)
        self.assertNotIn(": Ruled", [row[0] for row in rows])

    def test_a2_3_f4_status_line_in_section_introduction_is_counted(self):
        # A2-3-F4 (case k55): a section heading, then the line
        # Status: Ruled, then the entry with its own Banked line.
        # The identical line in the preamble is counted under
        # FILE; the section introduction line must count too.
        output = _run(
            "# Decision queue\n"
            "\n"
            "## Section one\n"
            "\n"
            "Status: Ruled\n"
            "\n"
            + _taught_entry(1, "A sample open question", "Banked"))
        self.assertEqual(_total(output), 2)
        self.assertIn(("Ruled", "line start", 1, ["FILE"]),
                      _rows(output))

    def test_s17_atk2_7_03_status_line_between_entries_is_counted(self):
        # S17-ATK2-7-03, first position (case n14b): a Status
        # line standing in a note segment between two entries,
        # outside the file header unit and outside any entry.
        output = _run(
            "# Decision queue\n"
            "\n"
            + _taught_entry(218, "Ordinary banked entry", "Banked")
            + "\n"
            "## Notes between entries\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            + _taught_entry(219, "Second ordinary banked entry",
                            "Banked"))
        self.assertEqual(_total(output), 3)
        self.assertIn(("RULED, closed", "line start", 1, ["FILE"]),
                      _rows(output))

    def test_s17_atk2_7_03_status_line_under_preamble_subheading_is_counted(self):
        # S17-ATK2-7-03, second position (case n31): a Status
        # line standing in the preamble under a level 2 heading.
        output = _run(
            "# Decision queue\n"
            "\n"
            "## Open items\n"
            "\n"
            "Status: RULED, closed\n"
            "\n"
            + _taught_entry(240, "Ordinary banked entry", "Banked"))
        self.assertEqual(_total(output), 2)
        self.assertIn(("RULED, closed", "line start", 1, ["FILE"]),
                      _rows(output))

    def test_s17_atk2_7_03_status_line_under_trailing_heading_is_counted(self):
        # S17-ATK2-7-03, third position (case n14): a Status
        # line standing under a trailing section heading after
        # the last entry.
        output = _run(
            "# Decision queue\n"
            "\n"
            + _taught_entry(217, "Ordinary banked entry", "Banked")
            + "\n"
            "## Trailing notes\n"
            "\n"
            "Status: RULED, closed\n")
        self.assertEqual(_total(output), 2)
        self.assertIn(("RULED, closed", "line start", 1, ["FILE"]),
                      _rows(output))

    def test_preamble_plain_status_line_still_counted_once_under_file(self):
        # Guard, passes before and after: case k34, one plain
        # Status line in the preamble, counted once under FILE.
        output = _run(
            "# Decision queue\n"
            "\n"
            "Status: Ruled\n"
            "\n"
            + _taught_entry(1, "A sample open question", "Banked"))
        self.assertEqual(_total(output), 2)
        self.assertIn(("Ruled", "line start", 1, ["FILE"]),
                      _rows(output))

    def test_preamble_two_markers_on_one_line_count_once_each(self):
        # Guard, passes before and after: case k37, two markers
        # on one preamble line count as one line start and one
        # embedded occurrence.
        output = _run(
            "# Decision queue\n"
            "\n"
            "Status: Banked Status: Ruled\n"
            "\n"
            + _taught_entry(1, "A sample open question", "Banked"))
        self.assertEqual(_total(output), 3)
        rows = _rows(output)
        # Rows merge on phrasing and kind across members: the
        # preamble Banked occurrence stands in the one Banked
        # line start row beside the entry own occurrence.
        banked = [row for row in rows
                  if row[0] == "Banked" and row[1] == "line start"]
        self.assertEqual(len(banked), 1)
        self.assertEqual(banked[0][2], 2)
        self.assertIn("FILE", banked[0][3])
        self.assertIn("DQ-001", banked[0][3])
        self.assertIn(("Ruled", "embedded", 1, ["FILE"]), rows)

    def test_preamble_empty_status_value_counted_nowhere(self):
        # Guard, passes before and after: case k40, an empty
        # preamble Status value counts nowhere; the total is the
        # entry own Banked occurrence alone.
        output = _run(
            "# Decision queue\n"
            "\n"
            "Status:\n"
            "\n"
            + _taught_entry(1, "A sample open question", "Banked"))
        self.assertEqual(_total(output), 1)


class UnclassifiedClassTest(unittest.TestCase):
    """CH-5: A2-10-F3 merged with F-15-2-2, one mechanism."""

    def test_a2_10_f3_one_word_title_is_not_unclassified(self):
        # A2-10-F3 minimal (case u1-solo-oneword): one entry
        # titled Alpha, its single Status value Banked, which
        # the vocabulary classifies. No unclassified value
        # stands in the file, so the class must read 0.
        output = _run(
            "# Decision queue\n"
            "\n"
            + _taught_entry(1, "Alpha", "Banked",
                            paragraph="A plain context paragraph."))
        self.assertEqual(_unclassified(output), (0, []))

    def test_a2_10_f3_three_one_word_titles_are_not_unclassified(self):
        # A2-10-F3 at scale (case u2-three-oneword): three one
        # word titled entries, values Banked, Banked, and Ruled,
        # all classified. The class must read 0, not 3.
        text = "# Decision queue\n\n"
        for number, title, status in ((1, "Alpha", "Banked"),
                                      (2, "Beta", "Banked"),
                                      (3, "Gamma", "Ruled")):
            text += _taught_entry(
                number, title, status,
                paragraph="A plain context paragraph.") + "\n"
        output = _run(text)
        self.assertEqual(_unclassified(output), (0, []))

    def test_f15_2_2_heading_borne_element_alone_is_not_unclassified(self):
        # F-15-2-2, the class test limb, pinned at the census
        # function itself so it stands on every runtime: the
        # bench form of the Todhri construction, an entry whose
        # only disposition free element is the heading borne
        # element parse raises on the bench (disposition None,
        # occurrence kind None, verbatim the whole heading).
        # That element carries no status occurrence and states
        # no status value, so the entry stands in no Unclassified
        # class. On the uncured test this entry counts 1.
        element = types.SimpleNamespace(
            kind="heading borne evidence",
            verbatim="### DQ-001: " + TODHRI_TITLE,
            disposition=None, occurrence_kind=None,
            line=3, position_in_line=12, decider=None,
            statement="### DQ-001: " + TODHRI_TITLE,
            own_text="### DQ-001: " + TODHRI_TITLE)
        entry = types.SimpleNamespace(
            identifier="DQ-001",
            heading="### DQ-001: " + TODHRI_TITLE,
            heading_text="### DQ-001: " + TODHRI_TITLE,
            status_elements=[element], fields=[], section="",
            date_text=None)
        rows = validate._census(
            [entry], [{"state": "Open", "unparsed": False}])
        found = [row for row in rows
                 if row.class_name == "Unclassified status values"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].count, 0)
        self.assertEqual(found[0].member_entry_ids, [])

    def test_f15_2_2_todhri_title_pipeline_counts_no_unclassified(self):
        # F-15-2-2 end to end (case u1-todhri-title, the bench
        # paper construction byte for byte in its title and its
        # Status value): the Unclassified line must read 0
        # entries. On this machine (Unicode 15.0.0) the Todhri
        # title raises no heading borne element, so this test
        # passes before and after here; on the bench runtime
        # (Unicode 16.0.0) it fails before the cure and passes
        # after. The mechanism test above fails before the cure
        # on both.
        output = _run(
            "# Decision queue\n"
            "\n"
            + _taught_entry(1, TODHRI_TITLE, "Open",
                            paragraph="This question is waiting "
                                      "for a decision, recorded "
                                      "2026-11-17."))
        self.assertEqual(_unclassified(output), (0, []))

    def test_genuine_unclassified_status_value_still_counts(self):
        # Guard, passes before and after: case v14-solo-invented,
        # a Status value the vocabulary does not classify,
        # carried by a line start Status element. The entry
        # stands in the class, exactly as the class rule states.
        output = _run(
            "# Decision queue\n"
            "\n"
            + _taught_entry(1, "Solo invented value",
                            "Deferred for now",
                            paragraph="A plain context paragraph."))
        self.assertEqual(_unclassified(output), (1, ["DQ-001"]))

    def test_two_word_title_control_is_not_unclassified(self):
        # Guard, passes before and after: the A2-10-F3 control
        # form (case u3-twoword-control, first entry): a two word
        # title raises no heading borne element and the class
        # reads 0.
        output = _run(
            "# Decision queue\n"
            "\n"
            + _taught_entry(1, "Alpha beta", "Banked",
                            paragraph="A plain context paragraph."))
        self.assertEqual(_unclassified(output), (0, []))


if __name__ == "__main__":
    unittest.main()
