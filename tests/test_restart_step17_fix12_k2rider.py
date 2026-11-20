"""Step 17 (restart) fix wave 12, K2 rider seat tests.

Charge: seat 10's observation O-12R10-1, standing put
to the determination in K1 form by
design/steps/step-17r-r12-triage-prep.md and charged
to fix wave 12 as its own unnumbered charge in the K1
family, test first, its cure stating its bound
expressly at the marker positions it cures. It
carries no CH number. The specification is the K1
rider passage of
design/steps/step-17r-r12-triage-prep.md, with the
observation in seat 10's run paper
design/steps/step-17r-r12-seat10-run.md, and the cure
form model is design/steps/step-17r-fix11-k1rider.md.
The parent cure stands at
design/steps/step-17r-fix11-k1rider.md: on the marker
first head line the span guard stands whole at its
stated bound at the second marker position (cases b2
and b3, and case j13), its limbs reach the third
marker position (case h15) and the fifth marker
position (case j5) exactly, and at the fourth marker
position the masked reading of the span stands whole
as it stood (case j4).

The bound question: that bound question transposed
one and two positions further. Seat 10's fresh cases
m01, m02, m03, and m13, marker first head lines with
the closed plus unclosed span form at the sixth
marker position, stand masked at exit 4 while their
twins stand recorded whole at exit 1 (total 6,
unclassified 1 in each case), and seat 10's fresh
case m16 stands in the same divergence at the
seventh marker position (total 7). The variant first
limb carries no such bound (case m10 credited at the
sixth).

The cure this module pins, stated expressly: where
the head line's line start element carries the
marker flavour, an embedded marker stands at the
sixth marker position or at the seventh marker
position on that line, a closed segment stands at or
after the start of the embedded element's value, and
an unclosed segment stands in the same embedded span,
the embedded value is read from the stored form of
the span on the CH-125 and CH-154 terms: the stored
value is credited whole, a trailing space or tab is
stripped, and nothing past the unclosed opening is
credited, so the embedded element stands at its plain
twin's standing. The cure states its bound expressly
at the sixth and seventh marker positions: at the
second marker position the span guard stands whole at
its stated bound, exactly as cases b2 and b3 and case
j13 pin it; at the third marker position the parent
cure's limb stands as it stood, case h15 credited in
full; at the fourth marker position the masked
reading of the span stands whole as it stood, exactly
as case j4 pins it, no limb of this cure reaching it;
at the fifth marker position the fix wave 11 cure's
limb stands as it stood, case j5 credited in full;
case j19's family, the second and third positions
standing together in one span, keeps its masked
reading whole, as do case m08's second and fifth
positions standing together and case m09's fourth and
fifth positions standing together; and at the eighth
marker position the masked reading of the span stands
whole as it stood, no limb of this cure reaching it.
Where no closed segment stands in the span, the limb
is not reached and the standing reading stands, as the
plain twin form itself stands. An embedded marker on
a line carrying no line start element keeps its masked
reading, as case b10 pins it. The variant first limb
of the parent cure stands untouched at its own locus
and bound, its sixth position form (case m10) standing
credited as it stood.

Constructions are seat 10's own m01, m02, m03, m13,
and m16 forms and their written neighbours, each
beside its plain twin, the round 8 bound forms b2, b3,
and b10, the parent cures' h15 and j5 forms, seat 11's
j13, j4, and j19 forms, seat 10's m08, m09, m10, and
m14 forms, and an eighth position bound form.

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


class O12R101MarkerFirstSixthChargedTest(unittest.TestCase):
    """The charged constructions m01, m02, m03, and m13
    at the sixth marker position: each failing before
    the cure for its charged reason and standing at its
    plain twin's standing after it."""

    def test_m01_marker_first_sixth_closed_unclosed_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "m01_marker_sixth_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertEqual(h.get(elements[5], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 6)

    def test_m01_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Open Status: Open Status: Open "
                    "Status: Open Status: Open "
                    "Status: Rul<!-- c -->ed<!-- unclosed",
                    "m01_marker_sixth_closed_unclosed.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status: Open Status: Open Status: Open "
                    "Status: Open Status: Open "
                    "Status: Ruled<!-- unclosed",
                    "m01_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_m03_marker_first_sixth_space_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed <!-- unclosed",
            "m03_marker_sixth_space_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertEqual(h.get(elements[5], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 6)

    def test_m13_marker_first_sixth_tab_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed\t<!-- unclosed",
            "m13_marker_sixth_tab_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertEqual(h.get(elements[5], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 6)

    def test_m02_marker_first_sixth_banked_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Ban<!-- c -->ked<!-- unclosed",
            "m02_marker_sixth_banked.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertEqual(h.get(elements[5], "verbatim"), "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Open"), 1)
        self.assertEqual(_occurrence_total(output), 6)


class O12R101MarkerFirstSeventhChargedTest(unittest.TestCase):
    """The charged construction m16 at the seventh
    marker position and its written neighbours: each
    failing before the cure for its charged reason and
    standing at its plain twin's standing after it."""

    def test_m16_marker_first_seventh_closed_unclosed_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "m16_marker_seventh_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 7)
        self.assertEqual(h.get(elements[6], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 7)

    def test_m16_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Open Status: Open Status: Open "
                    "Status: Open Status: Open Status: Open "
                    "Status: Rul<!-- c -->ed<!-- unclosed",
                    "m16_marker_seventh_closed_unclosed.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status: Open Status: Open Status: Open "
                    "Status: Open Status: Open Status: Open "
                    "Status: Ruled<!-- unclosed",
                    "m16_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_m16_marker_first_seventh_space_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open Status: Open "
            "Status: Rul<!-- c -->ed <!-- unclosed",
            "m16_marker_seventh_space.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 7)
        self.assertEqual(h.get(elements[6], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 7)

    def test_m16_marker_first_seventh_banked_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open Status: Open "
            "Status: Ban<!-- c -->ked<!-- unclosed",
            "m16_marker_seventh_banked.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 7)
        self.assertEqual(h.get(elements[6], "verbatim"), "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Open"), 1)
        self.assertEqual(_occurrence_total(output), 7)


class O12R101MarkerFirstBoundPinsTest(unittest.TestCase):
    """The stated bounds standing before and after in
    every direction this cure does not reach: the second
    marker position keeps the masked reading whole
    (cases b2, b3, and j13), the fourth marker position
    keeps it whole (case j4), case j19's second and third
    positions standing together keep it whole, cases m08
    and m09, whose combined spans are governed by a
    position this cure does not reach, keep it whole,
    case m14's two closed segment form at the sixth
    position credits no disposition, case b10 keeps its
    masked reading off the head line, and the eighth
    marker position keeps the masked reading whole."""

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

    def test_m08_second_and_fifth_both_bound_stands(self):
        model, output = _run(
            "Status: Open Status: Rul<!-- c -->ed<!-- u1 "
            "Status: Open Status: Open "
            "Status: Ban<!-- d -->ked<!-- u2",
            "m08_marker_second_and_fifth_both.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        verbatim = h.get(elements[1], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 2)

    def test_m09_fourth_and_fifth_both_bound_stands(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- u1 "
            "Status: Ban<!-- d -->ked<!-- u2",
            "m09_marker_fourth_and_fifth_both.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 4)
        verbatim = h.get(elements[3], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 4)

    def test_m14_sixth_two_closed_credits_no_disposition(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- d -->x<!-- unclosed",
            "m14_marker_sixth_two_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertNotEqual(h.get(elements[5], "verbatim"),
                            "Ruled")
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 6)

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

    def test_marker_eighth_bound_stands(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open Status: Open "
            "Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "k2rider_marker_eighth_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 8)
        verbatim = h.get(elements[7], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 8)


class O12R101ParentPinsTest(unittest.TestCase):
    """The parent cures' charged constructions standing
    as pins in full: the third marker position (case
    h15, the fix wave 10 K1 rider cure) and the fifth
    marker position (case j5, the fix wave 11 K1 rider
    cure), each credited whole in its adjacent and
    Banked forms, exactly as their papers state them."""

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


class O12R101ControlPinsTest(unittest.TestCase):
    """Controls standing before and after: the span
    guard's no unclosed reading at the sixth marker
    position, the no closed segment twin form itself at
    the sixth marker position, the unfinished stored
    prefix form at the sixth marker position, and the
    variant first sixth position form (case m10)
    standing credited as it stood."""

    def test_marker_first_sixth_no_unclosed_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed",
            "k2rider_marker_first_sixth_no_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertEqual(h.get(elements[5], "verbatim"), "Ruled")
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 6)

    def test_marker_first_sixth_no_closed_segment_form_stands(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Ruled<!-- unclosed",
            "m01_plain_twin_form.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 6)

    def test_marker_first_sixth_unfinished_prefix_stays_ambiguous(self):
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Ban<!-- c -->k<!-- unclosed",
            "k2rider_marker_first_sixth_unfinished_prefix.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertNotEqual(h.get(elements[5], "verbatim"),
                            "Banked")
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")

    def test_m10_variant_first_sixth_form_still_credits(self):
        model, output = _run(
            "Status unchanged Status: Open Status: Open "
            "Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "m10_variant_sixth_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 6)
        self.assertEqual(h.get(elements[5], "verbatim"), "Ruled")
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 6)


if __name__ == "__main__":
    unittest.main()
