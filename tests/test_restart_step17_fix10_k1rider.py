"""Step 17 (restart) fix wave 10, K1 rider seat tests.

Charge: seat 11 observation O-11R10-1, ruled TO FIX as
its own unnumbered charge in the K1 family at section
83 ruling (d) of design/steps/step-17r-record.md, in
the route of its parent O-11R9-3 under ruling (d) of
section 81, against round 10 attack seat 11 paper
design/steps/step-17r-r10-seat11.md. The parent cure
stands at design/steps/step-17r-fix9-o11.md.

The bound question: the O-11R9-3 bound question
transposed to the marker first flavour at the third
marker position. Where an unclosed segment stands in
an embedded marker's span, the masked reading of that
span stands whole, bounded expressly at CH-158 on
cases b2 and b3 of round 8 (the embedded marker at
the second position on a line whose line start
element carries the marker flavour), restated by the
fix wave 9 paper for the marker first form, and the
parent module's pins hold that bound in that form.
The round 10 fresh case h15 carries the same span
form at the third marker position on a marker first
head line whose line start element states Open. On
that form the bound's run level outcome differs from
its second position form: the h15 run withholds in
the Ambiguous form at exit 4 where its plain twin
completes at exit 1 with the third element recorded
whole as Ruled, the entry deriving Ruled, and
Unclassified status values at 0.

The cure this module pins, stated expressly: where
the head line's line start element carries the
marker flavour, an embedded marker stands at the
third marker position on that line, a closed segment
stands at or after the start of the embedded
element's value, and an unclosed segment stands in
the same embedded span, the embedded value is read
from the stored form of the span on the CH-125 and
CH-154 terms: the stored value is credited whole, a
trailing space or tab is stripped, and nothing past
the unclosed opening is credited, so the embedded
element stands at its plain twin's standing. The
cure is narrowed in the open to the third marker
position exactly: at the second marker position the
span guard stands whole at its stated bound, exactly
as cases b2 and b3 pin it, and at the fourth marker
position the masked reading of the span stands whole
as it stood, no limb of this cure reaching it. Where
no closed segment stands in the span, the limb is
not reached and the standing reading stands, as the
plain twin form itself stands. An embedded marker on
a line carrying no line start element keeps its
masked reading, as case b10 pins it. The variant
first limb of the parent cure stands untouched at
its own locus and bound.

Constructions are the round 10 attack paper's own
h15 form and its neighbours, each beside its plain
twin, the round 8 bound forms b2, b3, and b10, and
the parent module's g12 control form.

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


class O11R101MarkerFirstThirdChargedTest(unittest.TestCase):
    """The charged construction h15 and its written
    neighbours: each failing before the cure for its
    charged reason and standing at its plain twin's
    standing after it."""

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


class O11R101MarkerFirstBoundPinsTest(unittest.TestCase):
    """The stated bound of the span guard standing
    before and after in every direction this cure does
    not reach: cases b2 and b3 at the second marker
    position keep the masked reading of the embedded
    span whole, the fourth marker position keeps it
    whole under the narrowing recorded in this
    module's head, and case b10 keeps its masked
    reading off the head line."""

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

    def test_marker_first_fourth_position_bound_stands(self):
        # The narrowing, pinned in the open: this cure
        # reaches the third marker position exactly, so
        # the same span form at the fourth marker
        # position on a marker first head line keeps the
        # masked reading of the span whole, as it stood
        # before the cure.
        model, output = _run(
            "Status: Open Status: Open Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "k1rider_marker_first_fourth_closed_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 4)
        verbatim = h.get(elements[3], "verbatim")
        self.assertNotEqual(verbatim, "Ruled")
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 4)

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


class O11R101ControlPinsTest(unittest.TestCase):
    """Controls standing before and after: the span
    guard's no unclosed reading at the third marker
    position, the no closed segment twin form itself,
    the unfinished stored prefix form at the third
    marker position, and the parent cure's variant
    first third position form standing untouched."""

    def test_marker_first_third_no_unclosed_credits(self):
        model, output = _run(
            "Status: Open Status: Open Status: Rul<!-- c -->ed",
            "k1rider_marker_first_third_no_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"), "Ruled")
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)

    def test_marker_first_third_no_closed_segment_form_stands(self):
        # The plain twin form itself: no closed segment
        # stands in the span, so the limb is not reached
        # and the standing reading credits the value, as
        # it stood before the cure.
        model, output = _run(
            "Status: Open Status: Open Status: Ruled<!-- unclosed",
            "h15_plain_twin_form.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)

    def test_marker_first_third_unfinished_prefix_stays_ambiguous(self):
        # A closed segment inside the value word with the
        # unclosed opening standing inside the word after
        # it, at the third marker position on a marker
        # first line: the stored prefix the opening leaves
        # stands unfinished and takes no credit, before
        # and after.
        model, output = _run(
            "Status: Open Status: Open "
            "Status: Ban<!-- c -->k<!-- unclosed",
            "k1rider_marker_first_third_unfinished_prefix.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertNotEqual(h.get(elements[2], "verbatim"),
                            "Banked")
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")

    def test_variant_first_third_form_still_credits(self):
        # The parent cure's own third position form, on
        # the variant first head line, standing as the
        # fix wave 9 paper states it, untouched by this
        # cure.
        model, output = _run(
            "Status unchanged Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "g12_embedded_third_after_variant.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"), "Ruled")
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)


if __name__ == "__main__":
    unittest.main()
