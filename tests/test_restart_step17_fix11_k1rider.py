"""Step 17 (restart) fix wave 11, K1 rider seat tests.

Charge: seat 11 observation O-11R11-1, standing
determined at record section 108 in its second form
as its own unnumbered charge in the K1 family, test
first, its cure stating its bound expressly at the
fifth marker position. It carries no CH number. The
specification is the K1 rider passage of
design/steps/step-17r-r11-triage-prep.md, with the
observation in seat 11's run paper
design/steps/step-17r-r11-seat11-run.md, and the cure
form model is design/steps/step-17r-fix10-k1rider.md.
The parent cure stands at
design/steps/step-17r-fix10-k1rider.md: on the marker
first head line the span guard stands whole at its
stated bound at the second marker position (cases b2
and b3), its limb reaches the third marker position
exactly (case h15, exit 1 on both subcommands in both
forms, figures identical case to twin), and at the
fourth marker position the masked reading of the span
stands whole as it stood.

The bound question: that bound question transposed
one position further. Seat 11's fresh case j5, a
marker first head line with the closed plus unclosed
span form at the fifth marker position, stands masked
at exit 4 while its twin stands recorded whole at
exit 1 (total 5, unclassified 1 in the case). The
second (case j13), third (case h15, and case j19's
family), and fourth (case j4) positions bind in the
twins and stand masked in the cases, on the cases as
seat 11's paper states them, the third position
standing cured by the parent cure in its own form.

The cure this module pins, stated expressly: where
the head line's line start element carries the
marker flavour, an embedded marker stands at the
fifth marker position on that line, a closed segment
stands at or after the start of the embedded
element's value, and an unclosed segment stands in
the same embedded span, the embedded value is read
from the stored form of the span on the CH-125 and
CH-154 terms: the stored value is credited whole, a
trailing space or tab is stripped, and nothing past
the unclosed opening is credited, so the embedded
element stands at its plain twin's standing. The
cure states its bound expressly at the fifth marker
position: at the second marker position the span
guard stands whole at its stated bound, exactly as
cases b2 and b3 and case j13 pin it; at the third
marker position the parent cure's limb stands as it
stood, case h15 credited in full; at the fourth
marker position the masked reading of the span
stands whole as it stood, exactly as case j4 pins
it, no limb of this cure reaching it; and case
j19's family, the second and third positions
standing together in one span, keeps its masked
reading whole. Where no closed segment stands in
the span, the limb is not reached and the standing
reading stands, as the plain twin form itself
stands. An embedded marker on a line carrying no
line start element keeps its masked reading, as
case b10 pins it. The variant first limb of the
parent cure stands untouched at its own locus and
bound, its fifth position form (case j15) standing
credited as it stood.

Constructions are seat 11's own j5 form and its
written neighbours, each beside its plain twin, the
round 8 bound forms b2, b3, and b10, the parent
cure's h15 form in full, and seat 11's j13, j4, j15,
and j19 forms.

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


def _elements(model):
    entry = h.entry_by_id(model, "DQ-001")
    return h.get(entry, "status_elements") or []


class O11R111MarkerFirstFifthChargedTest(unittest.TestCase):
    """The charged construction j5 and its written
    neighbours: each failing before the cure for its
    charged reason and standing at its plain twin's
    standing after it."""

    def test_j5_marker_first_fifth_closed_unclosed_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Rul<!-- c -->ed<!-- unclosed",
            "j5_marker_fifth_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 5)
        self.assertEqual(h.get(elements[4], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 5)

    def test_j5_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Open Status: Open Status: Open "
                    "Status: Open Status: Rul<!-- c -->ed"
                    "<!-- unclosed",
                    "j5_marker_fifth_closed_unclosed.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status: Open Status: Open Status: Open "
                    "Status: Open Status: Ruled<!-- unclosed",
                    "j5_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_j5_marker_first_fifth_space_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Rul<!-- c -->ed <!-- unclosed",
            "j5_marker_fifth_space.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 5)
        self.assertEqual(h.get(elements[4], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 5)

    def test_j5_marker_first_fifth_banked_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Ban<!-- c -->ked<!-- unclosed",
            "j5_marker_fifth_banked.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 5)
        self.assertEqual(h.get(elements[4], "verbatim"), "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Open"), 1)
        self.assertEqual(_occurrence_total(output), 5)


class O11R111MarkerFirstBoundPinsTest(unittest.TestCase):
    """The stated bounds standing before and after in
    every direction this cure does not reach: the
    second marker position keeps the masked reading
    whole (cases b2, b3, and j13), the fourth marker
    position keeps it whole (case j4), case j19's
    second and third positions standing together keep
    it whole, and case b10 keeps its masked reading
    off the head line."""

    def test_j13_marker_second_bound_stands(self):
        model, output = _run(
            "Status: Open Status: Rul<!-- c -->ed<!-- unclosed",
            "j13_marker_second_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        verbatim = h.get(elements[1], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 2)

    def test_b2_embedded_inside_unclosed_after_bound_stands(self):
        model, output = _run(
            "Status: Banked Status: Rul<!-- c -->ed "
            "<!-- unclosed",
            "b2_embedded_inside_unclosed_after.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        verbatim = h.get(elements[1], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")

    def test_b3_embedded_inside_unclosed_adjacent_bound_stands(self):
        model, output = _run(
            "Status: Banked Status: Rul<!-- c -->ed"
            "<!-- unclosed",
            "b3_embedded_inside_unclosed_adjacent.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        verbatim = h.get(elements[1], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")

    def test_j4_marker_fourth_bound_stands(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "j4_marker_fourth_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 4)
        verbatim = h.get(elements[3], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 4)

    def test_j19_second_and_third_both_bound_stands(self):
        model, output = _run(
            "Status: Open Status: Rul<!-- c -->ed<!-- u1 "
            "Status: Ban<!-- d -->ked<!-- u2",
            "j19_marker_second_and_third_both.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        verbatim = h.get(elements[1], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")

    def test_b10_embedded_off_head_line_keeps_masked(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "Question: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\n"
        body += "A note Status: Rul<!-- c -->ed today.\n"
        model, output = h.run_pipeline(
            body.encode("utf-8"),
            "b10_embedded_off_head_line_segment.md")
        self.assertIsNotNone(output)
        verbatims = [h.get(element, "verbatim")
                     for element in _elements(model)]
        self.assertTrue(any(
            verbatim is not None and "Rul" in verbatim
            and "  " in verbatim
            and not verbatim.startswith("Ruled")
            for verbatim in verbatims))


class O11R111H15ParentPinTest(unittest.TestCase):
    """The parent cure's charged construction h15
    standing as a pin in full: the third marker
    position on the marker first head line, credited
    whole in its adjacent, space, and Banked forms and
    on the CLI against its plain twin, exactly as the
    fix wave 10 paper states it."""

    def test_h15_marker_first_third_closed_unclosed_credits(self):
        model, output = _run(
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "h15_marker_first_third_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)

    def test_h15_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Open Status: Open "
                    "Status: Rul<!-- c -->ed<!-- unclosed",
                    "h15_marker_first_third_closed_unclosed.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status: Open Status: Open "
                    "Status: Ruled<!-- unclosed",
                    "h15_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_h15_marker_first_third_space_credits(self):
        model, output = _run(
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed <!-- unclosed",
            "h15_marker_first_third_space.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)

    def test_h15_marker_first_third_banked_credits(self):
        model, output = _run(
            "Status: Open Status: Open "
            "Status: Ban<!-- c -->ked<!-- unclosed",
            "h15_marker_first_third_banked.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"), "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Open"), 1)
        self.assertEqual(_occurrence_total(output), 3)


class O11R111ControlPinsTest(unittest.TestCase):
    """Controls standing before and after: the span
    guard's no unclosed reading at the fifth marker
    position, the no closed segment twin form itself,
    the unfinished stored prefix form at the fifth
    marker position, and the parent cure's variant
    first fifth position form standing untouched."""

    def test_marker_first_fifth_no_unclosed_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Rul<!-- c -->ed",
            "k1rider_marker_first_fifth_no_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 5)
        self.assertEqual(h.get(elements[4], "verbatim"), "Ruled")
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 5)

    def test_marker_first_fifth_no_closed_segment_form_stands(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Ruled<!-- unclosed",
            "j5_plain_twin_form.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 5)
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 5)

    def test_marker_first_fifth_unfinished_prefix_stays_ambiguous(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Ban<!-- c -->k<!-- unclosed",
            "k1rider_marker_first_fifth_unfinished_prefix.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 5)
        self.assertNotEqual(h.get(elements[4], "verbatim"),
                            "Banked")
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")

    def test_variant_first_fifth_form_still_credits(self):
        model, output = _run(
            "Status unchanged Status: Open Status: Open "
            "Status: Open Status: Rul<!-- c -->ed<!-- unclosed",
            "j15_variant_fifth_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 5)
        self.assertEqual(h.get(elements[4], "verbatim"), "Ruled")
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 5)


if __name__ == "__main__":
    unittest.main()
