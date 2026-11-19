"""Step 17 (restart) fix wave 8, Fix Seat K1 tests.

Charge CH-154 (parse, the stored form reading), ruled at
record section 77 of design/steps/step-17r-record.md,
against round 8 attack seat 11 finding F-11R8-01 (High),
paper at design/steps/step-17r-attack8-11.md, finding
T8-04 in the triage consolidation.

CH-154 carries F-11R8-01, a CH-125 cure defect: the
CH-125 termination test (the stored value stands
terminated before the end of the stored form, by a
following marker or by the written break that stood
before the unclosed opening) misses a complete value
whose unclosed opening stands adjacent to it, with no
written break and no following marker, so a closed
segment inside the value word loses its credit on that
form. A decided entry derives Open in silence at exit 0,
a Banked entry loses its Banked head standing, and the
recorded form of the multiword and after value forms
stands mangled or padded against its plain twin. A tab
written before the unclosed opening fails the same test
in the same way, because the test reads a trailing plain
space alone.

Pins in both directions stand in this file: the governed
CH-108 bound form (a segment left unclosed inside the
value word itself credits nothing, its fragment standing
unclassified, in both its round 7 case u4 form and its
fix wave 6 pin form), the unfinished stored prefix form
(a closed segment inside the value word with the
unclosed opening standing inside the word after it, its
stored prefix standing unclassified and no Banked head
evidence group standing), the plain value comparator (a
plain value standing before an unclosed opening
credited, as it stood before), and the CH-125 written
break contrast (a closed segment inside the value word
and one after it, a written space before the unclosed
segment, credited whole, as charged at CH-125).

Constructions are the attack paper's own forms:
design/steps/step-17r-attack8-11.md, cases a1, a2, a6,
e3, a3, and a4, each beside its plain twin in that
paper's twin set.

Copyright: J.P. Picard aka Macro-Harder
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h


def _body(status_line):
    body = h._header_block()
    body += "### DQ-001: Open one\n\n"
    body += status_line + "\n\n"
    body += "Question: Which option?\n"
    body += "Options: A, B\nCost of deciding late: blocked.\n"
    body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
    return body


def _run(status_line, name):
    return h.run_pipeline(_body(status_line).encode("utf-8"), name)


def _run_cli(status_line, name, subcommand):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / name
        target.write_bytes(_body(status_line).encode("utf-8"))
        code, out, err = h.run_cli(subcommand, target)
    return code, (out + err).decode("utf-8", errors="replace")


def _rule2(output):
    return h.findings_for(output, entry_id="DQ-001", rule=2)


def _entry(output):
    return h.entry_by_id(output, "DQ-001")


def _unclassified_notes(output):
    return [finding for finding in h.findings_for(
        output, entry_id="DQ-001")
        if "unclassified status value" in
        (h.finding_statement(finding) or "")]


def _occurrence_total(output):
    recon = h.reconciliation_of(output)
    return h.int_of(h.get(recon, "status_occurrence_total",
                          "occurrence_total"))


def _group_members(output, *name_parts):
    group = h.census_class(h.census_of(output), *name_parts)
    if group is None:
        return []
    return h.census_members(group)


def _elements(model):
    entry = h.entry_by_id(model, "DQ-001")
    return h.get(entry, "status_elements") or []


def _head_element(model):
    elements = _elements(model)
    test_case = unittest.TestCase()
    test_case.assertEqual(len(elements), 1)
    return elements[0]


class Ch154AdjacentUnclosedChargedTest(unittest.TestCase):
    """F-11R8-01: the charged constructions of the attack
    paper, cases a1, a2, a6, and e3, each failing before
    the cure for its charged reason and standing credited
    after it, beside the recorded form constructions a3
    and a4."""

    def test_a1_ruled_inside_unclosed_adjacent_credits(self):
        model, output = _run(
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "a1_ruled_inside_unclosed_adjacent.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_rule2(output), [])
        self.assertEqual(_occurrence_total(output), 1)
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(canonical.get("Open"), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 0)

    def test_a1_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Rul<!-- c -->ed<!-- unclosed",
                    "a1_ruled_inside_unclosed_adjacent.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status: Ruled<!-- unclosed",
                    "a1_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_a2_banked_inside_unclosed_adjacent_credits(self):
        model, output = _run(
            "Status: Ban<!-- c -->ked<!-- unclosed",
            "a2_banked_inside_unclosed_adjacent.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Banked")
        self.assertEqual(h.get(element, "disposition"),
                         "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_occurrence_total(output), 1)
        self.assertEqual(
            _group_members(output, "unclassified"), [])
        # The cured standing beside the CH-125 space form
        # comparator on the same body (case u3 of round 7,
        # standing at the Banked head footing form in the
        # fix wave 7 K4 paper): the entry state and the
        # evidence group standing match that comparator
        # exactly.
        _cmodel, comparator = _run(
            "Status: Ban<!-- c -->ked <!-- unclosed",
            "a2_space_form_comparator.md")
        self.assertEqual(h.entry_state(_entry(output)),
                         h.entry_state(_entry(comparator)))
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"),
            _group_members(comparator, "unheaded paragraphs"))

    def test_a2_cli_matches_the_space_form_comparator(self):
        # The CLI standing of the cured form is the
        # standing of the CH-125 space form on the same
        # body: the Banked head footing form at exit 4,
        # as cases u3 and u5 stand in the fix wave 7 K4
        # paper, the value credit standing in full.
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Ban<!-- c -->ked<!-- unclosed",
                    "a2_banked_inside_unclosed_adjacent.md",
                    subcommand)
                comparator_code, _comparator = _run_cli(
                    "Status: Ban<!-- c -->ked <!-- unclosed",
                    "a2_space_form_comparator.md", subcommand)
                self.assertEqual(code, comparator_code)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_a6_banked_inside_tab_before_unclosed_credits(self):
        model, output = _run(
            "Status: Ban<!-- c -->ked\t<!-- unclosed",
            "a6_banked_inside_tab_before_unclosed.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Banked")
        self.assertEqual(h.get(element, "disposition"),
                         "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_occurrence_total(output), 1)
        # The cured standing beside the CH-125 space form
        # comparator on the same body, as at case a2.
        _cmodel, comparator = _run(
            "Status: Ban<!-- c -->ked <!-- unclosed",
            "a6_space_form_comparator.md")
        self.assertEqual(h.entry_state(_entry(output)),
                         h.entry_state(_entry(comparator)))
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"),
            _group_members(comparator, "unheaded paragraphs"))

    def test_a6_cli_matches_the_space_form_comparator(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Ban<!-- c -->ked\t<!-- unclosed",
                    "a6_banked_inside_tab_before_unclosed.md",
                    subcommand)
                comparator_code, _comparator = _run_cli(
                    "Status: Ban<!-- c -->ked <!-- unclosed",
                    "a6_space_form_comparator.md", subcommand)
                self.assertEqual(code, comparator_code)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_e3_open_inside_unclosed_adjacent_credits(self):
        model, output = _run(
            "Status: Op<!-- c -->en<!-- unclosed",
            "e3_open_inside_unclosed_adjacent.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Open")
        self.assertEqual(h.get(element, "disposition"),
                         "Open")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_occurrence_total(output), 1)

    def test_a3_multiword_unclosed_adjacent_recorded_whole(self):
        model, output = _run(
            "Status: Closed as deci<!-- c -->ded<!-- unclosed",
            "a3_multiword_unclosed_adjacent.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"),
                         "Closed as decided")
        _twin_model, twin = _run(
            "Status: Closed as decided<!-- unclosed",
            "a3_plain_twin.md")
        self.assertEqual(h.entry_state(_entry(output)),
                         h.entry_state(_entry(twin)))
        self.assertEqual(h.canonical_counts(output),
                         h.canonical_counts(twin))

    def test_a4_segment_after_value_unclosed_adjacent_unpadded(self):
        model, output = _run(
            "Status: Ruled<!-- c --><!-- unclosed",
            "a4_ruled_segment_after_unclosed_adjacent.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        # The charged expectation is the clean recorded
        # form asserted above: the plain twin's own
        # verbatim carries the unclosed segment's masked
        # padding, as the attack paper records, so no
        # twin verbatim equality is asserted here.


class Ch154BoundPinsTest(unittest.TestCase):
    """The governed bound in the other direction, standing
    before and after: a segment left unclosed credits
    nothing past its opening, and the standing CH-125
    terminations stand as they stood."""

    def test_u4_unclosed_inside_value_credits_nothing(self):
        _model, output = _run("Status: Ban<!-- c ked",
                              "u4_unclosed_inside_value.md")
        self.assertIsNotNone(output)
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"), [])
        self.assertEqual(len(_unclassified_notes(output)), 1)

    def test_unclosed_opening_inside_value_no_closed_segment(self):
        _model, output = _run(
            "Status: Ban<!-- c",
            "k1_unclosed_opening_inside_value.md")
        self.assertIsNotNone(output)
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"), [])
        self.assertEqual(len(_unclassified_notes(output)), 1)

    def test_unfinished_stored_prefix_stays_unclassified(self):
        # A closed segment inside the value word with the
        # unclosed opening standing inside the word after
        # it: the stored prefix the opening leaves stands
        # unfinished, takes no credit, and no Banked head
        # evidence group stands, before and after.
        _model, output = _run(
            "Status: Ban<!-- c -->k<!-- unclosed",
            "k1_unfinished_stored_prefix.md")
        self.assertIsNotNone(output)
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"), [])
        self.assertEqual(len(_unclassified_notes(output)), 1)

    def test_u2_plain_value_unclosed_after_stands_credited(self):
        model, output = _run("Status: Banked <!-- unclosed",
                             "u2_plain_value_unclosed_after.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "disposition"),
                         "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_occurrence_total(output), 1)

    def test_e1_written_break_before_unclosed_stands_credited(self):
        model, output = _run(
            "Status: Rul<!-- c -->ed<!-- d --> <!-- unclosed",
            "e1_inside_and_after_closed_unclosed_space.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)


if __name__ == "__main__":
    unittest.main()
