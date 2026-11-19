"""Step 17 (restart) fix wave 9, Fix Seat O-11R9-3 tests.

Charge: seat 11 observation O-11R9-3, ruled TO FIX as
its own charge in the K1 family cluster at section 81
ruling (d) of design/steps/step-17r-record.md, against
round 9 attack seat 11 paper
design/steps/step-17r-attack9-11.md.

The bound question: where an unclosed segment stands
in an embedded marker's span, the masked reading of
that span stands whole, bounded expressly at CH-158
on cases b2 and b3 of round 8 (an embedded marker on a
line whose line start element carries the marker
flavour), and the K1 second seat's pins hold that
bound in that form. The round 9 fresh cases g3, g4,
g12, and g13 carry the same span form on head lines
whose line start element is the variant element, the
position CH-158 cured for spans carrying no unclosed
segment (case b1, and fresh cases g16 and g17 standing
exact). On the variant first form the bound's run
level outcome differs from its marker first form: the
g3, g4, g12, and g13 runs withhold in the Ambiguous
form at exit 4 where their plain twins complete at
exit 1 with the embedded element credited.

The cure this module pins, stated expressly: where the
head line's line start element is the variant element
and an embedded marker's span carries a closed segment
at or after the start of its value and an unclosed
segment in the same span, the embedded value is read
from the stored form of the span on the CH-125 and
CH-154 terms (the stored value credited whole, nothing
past the unclosed opening credited). Where the line
start element carries the marker flavour, the span
guard stands whole as bounded at cases b2 and b3.
Where no closed segment stands in the span, the limb
is not reached and the standing reading stands.

Constructions are the round 9 attack paper's own
forms: cases g3, g4, g12, and g13, each beside its
plain twin, the controls g16 and g17, and the round 8
bound forms b2, b3, and b10.

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


class O11R93VariantFirstChargedTest(unittest.TestCase):
    """The charged constructions g3, g4, g12, and g13:
    each failing before the cure for its charged reason
    and standing at its plain twin's standing after it."""

    def test_g3_embedded_after_variant_adjacent_credits(self):
        model, output = _run(
            "Status unchanged Status: Rul<!-- c -->ed<!-- unclosed",
            "g3_embedded_after_variant_adjacent.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[1], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 2)

    def test_g3_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status unchanged Status: Rul<!-- c -->ed"
                    "<!-- unclosed",
                    "g3_embedded_after_variant_adjacent.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status unchanged Status: Ruled<!-- unclosed",
                    "g3_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_g4_embedded_after_variant_space_credits(self):
        model, output = _run(
            "Status unchanged Status: Rul<!-- c -->ed <!-- unclosed",
            "g4_embedded_after_variant_space.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[1], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 2)

    def test_g12_embedded_third_after_variant_credits(self):
        model, output = _run(
            "Status unchanged Status: Open "
            "Status: Rul<!-- c -->ed<!-- unclosed",
            "g12_embedded_third_after_variant.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)

    def test_g13_embedded_banked_after_variant_credits(self):
        model, output = _run(
            "Status unchanged Status: Ban<!-- c -->ked<!-- unclosed",
            "g13_embedded_banked_after_variant_adjacent.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[1], "verbatim"), "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 2)

    def test_g13_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, _combined = _run_cli(
                    "Status unchanged Status: Ban<!-- c -->ked"
                    "<!-- unclosed",
                    "g13_embedded_banked_after_variant_adjacent.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status unchanged Status: Banked<!-- unclosed",
                    "g13_plain_twin.md", subcommand)
                self.assertEqual(twin_code, 1)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)


class O11R93MarkerFirstBoundPinsTest(unittest.TestCase):
    """The stated bound of the span guard on its marker
    first forms, standing before and after: cases b2 and
    b3 keep the masked reading of the embedded span
    whole, and case b10 keeps its masked reading off the
    head line."""

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


class O11R93ControlPinsTest(unittest.TestCase):
    """Controls standing before and after: the CH-158
    reach on the variant first line with no unclosed
    segment in the span, the no closed segment twin form
    itself, and the unfinished stored prefix form on the
    variant first line."""

    def test_g16_embedded_banked_after_variant_no_unclosed(self):
        model, output = _run(
            "Status unchanged Status: Ban<!-- c -->ked",
            "g16_embedded_banked_after_variant_no_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[1], "verbatim"), "Banked")
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 2)

    def test_g17_embedded_third_after_variant_no_unclosed(self):
        model, output = _run(
            "Status unchanged Status: Open Status: Rul<!-- c -->ed",
            "g17_embedded_third_after_variant_no_unclosed.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 3)
        self.assertEqual(h.get(elements[2], "verbatim"), "Ruled")
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 3)

    def test_variant_first_no_closed_segment_form_stands(self):
        # The plain twin form itself: no closed segment
        # stands in the span, so the limb is not reached
        # and the standing reading credits the value, as
        # it stood before the cure.
        model, output = _run(
            "Status unchanged Status: Ruled<!-- unclosed",
            "g3_plain_twin_form.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.entry_state(_entry(output)), "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 2)

    def test_variant_first_unfinished_prefix_stays_ambiguous(self):
        # A closed segment inside the value word with the
        # unclosed opening standing inside the word after
        # it, on the variant first line: the stored prefix
        # the opening leaves stands unfinished and takes
        # no credit, before and after.
        model, output = _run(
            "Status unchanged Status: Ban<!-- c -->k<!-- unclosed",
            "o11_unfinished_stored_prefix.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertNotEqual(h.get(elements[1], "verbatim"),
                            "Banked")
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")


if __name__ == "__main__":
    unittest.main()
