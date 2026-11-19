"""Step 17 (restart) fix wave 8, Fix Seat K1 (second seat)
tests.

Charges CH-158 and CH-184 (parse, the stored form
reading), ruled at record section 77 of
design/steps/step-17r-record.md, against round 8 attack
seat 11 findings F-11R8-02 (Medium) and F-11R8-03 (Low),
paper at design/steps/step-17r-attack8-11.md, findings
T8-08 and T8-31 in the triage consolidation. Charge
CH-154 of this cluster stands cured by the first seat of
the cluster and is not re-cured here; its pin module
stands in the governing set of this seat.

CH-158, the second marker head line limb: the CH-126
stored form reading of an embedded marker element is
conditioned on a line start marker, in the marker
flavour, standing on the same line, so a comment segment
inside the value word of a Status marker standing after
a variant element on the head line itself never takes
the stored form, because the line start element of that
line is the variant element. A sound entry takes the
Ambiguous outcome at exit 4.

CH-184, the variant padding verbatim limb: the CH-127
span reading is refused whole where the variant span
carries any unclosed segment, so a closed segment
standing before an unclosed segment inside the span
leaves its masked spaces standing in the recorded
verbatim, although the stored form of the span credits
nothing past the unclosed opening and the closed segment
stands wholly before it.

Named neighbour forms joined to CH-158 under record
section 77 ruling (i), on ruling R-21: the stated bounds
of the CH-126 act at observation O-11R8-2 of the attack
paper. An embedded marker on a line carrying no line
start marker keeps its masked reading, and a segment
left unclosed in an embedded span keeps the masked
reading of that span whole. Both forms stand bounded
expressly in this file, in the bound pin methods below:
they are not cured by the CH-158 cure and stand as they
stood before it.

Constructions are the attack paper's own forms:
design/steps/step-17r-attack8-11.md, cases b1, b9, b4,
b2, b3, and b10 for CH-158, and cases c1, c2, c5, and
c6 for CH-184, each beside its plain twin in that
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


class Ch158VariantFirstChargedTest(unittest.TestCase):
    """F-11R8-02: the charged construction of the attack
    paper, case b1, failing before the cure for its
    charged reason and standing decided after it."""

    def test_b1_variant_first_marker_second_segment_credits(self):
        model, output = _run(
            "Status unchanged Status: Rul<!-- c -->ed",
            "b1_variant_first_marker_second_segment.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[1], "verbatim"),
                         "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertNotEqual(h.entry_state(_entry(output)),
                            "Ambiguous")
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 2)

    def test_b1_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status unchanged Status: Rul<!-- c -->ed",
                    "b1_variant_first_marker_second_segment.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status unchanged Status: Ruled",
                    "b1_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)


class Ch158ContrastPinsTest(unittest.TestCase):
    """Contrasts of the second marker limb, standing
    before and after: the reading reaches the embedded
    element where the line start element carries the
    marker flavour, at the second and third positions."""

    def test_b9_both_markers_segment_inside_stands_credited(self):
        model, output = _run(
            "Status: Ban<!-- c -->ked Status: Rul<!-- c -->ed",
            "b9_both_markers_segment_inside.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[0], "verbatim"),
                         "Banked")
        self.assertEqual(h.get(elements[1], "verbatim"),
                         "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 2)

    def test_b4_third_marker_segment_inside_stands_credited(self):
        model, output = _run(
            "Status: Banked Status: Open "
            "Status: Rul<!-- c -->ed",
            "b4_third_marker_segment_inside.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"),
                         "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)


class Ch158BoundPinsTest(unittest.TestCase):
    """The stated bounds of the CH-126 act, joined to
    CH-158 as named neighbour forms under ruling (i) on
    R-21 and bounded expressly here: they stand as they
    stood before the cure, in the other direction."""

    def test_b2_embedded_inside_unclosed_after_bound_stands(self):
        # A segment left unclosed in an embedded span
        # keeps the masked reading of that span whole:
        # the second element value stands masked and
        # unclassified, before and after.
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
        # The same bound with the unclosed segment
        # standing adjacent after the embedded value.
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

    def test_b10_embedded_off_head_line_keeps_masked(self):
        # An embedded marker on a line carrying no line
        # start marker keeps its masked reading, before
        # and after: the charge reaches the head line
        # only.
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


class Ch184VariantPaddingChargedTest(unittest.TestCase):
    """F-11R8-03: the charged constructions of the attack
    paper, cases c1 and c2, each failing before the cure
    for its charged reason and standing unpadded after
    it, in the stored form the span carries before its
    unclosed opening."""

    def test_c1_variant_closed_and_unclosed_after_unpadded(self):
        model, output = _run(
            "Status unchanged<!-- c --> <!-- unclosed",
            "c1_variant_closed_and_unclosed_after.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 1)
        element = elements[0]
        self.assertEqual(h.get(element, "kind"),
                         "variant phrasing")
        self.assertEqual(h.get(element, "verbatim"),
                         "Status unchanged ")
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 1)
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Open"), 1)

    def test_c2_variant_closed_unclosed_adjacent_unpadded(self):
        model, output = _run(
            "Status unchanged<!-- c --><!-- unclosed",
            "c2_variant_closed_unclosed_adjacent.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 1)
        element = elements[0]
        self.assertEqual(h.get(element, "kind"),
                         "variant phrasing")
        self.assertEqual(h.get(element, "verbatim"),
                         "Status unchanged")
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 1)

    def test_c1_cli_exit_and_counts_stand_as_its_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status unchanged<!-- c --> <!-- unclosed",
                    "c1_variant_closed_and_unclosed_after.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status unchanged <!-- unclosed",
                    "c1_plain_twin.md", subcommand)
                self.assertEqual(code, twin_code)
                self.assertEqual(code, 0)
                self.assertIn("Canonical Open: 1", combined)


class Ch184ContrastAndBoundPinsTest(unittest.TestCase):
    """Contrasts and bounds of the variant span limb,
    standing before and after."""

    def test_c5_variant_two_closed_after_stands_unpadded(self):
        # With no unclosed segment in the span, the
        # CH-127 reading is taken and both segments are
        # removed, before and after.
        model, output = _run(
            "Status unchanged<!-- a --><!-- b -->",
            "c5_variant_two_closed_after.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 1)
        self.assertEqual(h.get(elements[0], "verbatim"),
                         "Status unchanged")
        self.assertEqual(h.entry_state(_entry(output)), "Open")

    def test_c6_variant_unclosed_only_after_bound_stands(self):
        # A span carrying an unclosed segment alone
        # credits nothing and the masked verbatim stands,
        # in the governed bound form the CH-127 act
        # states, before and after: no closed segment
        # stands in the span for the reading to remove.
        model, output = _run(
            "Status unchanged <!-- unclosed",
            "c6_variant_unclosed_only_after.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 1)
        verbatim = h.get(elements[0], "verbatim")
        self.assertNotEqual(verbatim, "Status unchanged")
        self.assertTrue(verbatim.startswith(
            "Status unchanged"))
        self.assertIn("  ", verbatim)
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 1)


if __name__ == "__main__":
    unittest.main()
