"""Step 17 (restart) fix wave 7, Fix Seat K4 tests.

Charges CH-125, CH-126, and CH-127 (parse, the stored form
reading), ruled at record section 66 of
design/steps/step-17r-record.md, against round 7 attack
seat 11 findings F-11R7-01 (High), F-11R7-02 (Medium), and
F-11R7-03 (Low), paper at
design/steps/step-17r-attack7-11.md.

CH-125, the guard scope limb: the CH-108 stored form value
reading is refused whole where any segment on the line
stands unclosed, so a closed segment inside the value word
loses its credit where an unclosed segment stands after
the complete value. A decided entry derives Open in
silence at exit 0 and a Banked entry loses its Banked head
standing. The bound the CH-108 act states is narrower: a
segment left unclosed credits nothing past its opening.
Where the complete value stands before that opening, with
a closed segment inside it, crediting the value credits
nothing past the opening.

CH-126, the second marker limb: the CH-108 reading reaches
line start elements only, so a segment inside the value
word of a second Status marker standing on the head line
itself never takes the stored form, and a sound entry
takes the Ambiguous outcome at exit 4.

CH-127, the variant padding limb: a segment standing
after the variant phrasing on a variant head line leaves
the masked spaces standing in the recorded verbatim,
because neither the CH-89 gate nor the CH-108 reading
reaches the variant flavour.

Pins in both directions stand in this file: the governed
CH-108 bound form (a segment left unclosed inside the
value word itself credits nothing, its fragment standing
unclassified), the plain value comparator (a plain value
standing before an unclosed opening credited, as it stood
before), the first marker contrast of the second marker
finding (a segment inside the first element on the same
line credited, as it stood before), the later Status line
form standing as its plain twin stands, the embedded
marker bound (a segment inside an embedded value on a
line carrying no line start marker keeps its masked
reading, the charge reaching the head line only), and the
variant contrast (a segment inside the variant word with
one after the phrasing credited whole, as it stood
before).

Constructions are the attack paper's own forms:
design/steps/step-17r-attack7-11.md, cases u1, u2, u3,
u4, u5, d1, d2, d3, vt1, vt2, and vt3.

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


def _assert_banked_credited(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)), "Open")
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(_unclassified_notes(output), [])
    test_case.assertEqual(_occurrence_total(output), 1)
    test_case.assertIn("DQ-001", _group_members(
        output, "unheaded paragraphs"))
    test_case.assertEqual(
        _group_members(output, "unclassified"), [])
    waiting, _blocking = h.waiting_and_blocking(output)
    test_case.assertEqual(h.int_of(waiting), 1)


class Ch125GuardScopeChargedTest(unittest.TestCase):
    """F-11R7-01: the charged constructions of the attack
    paper, cases u1, u3, and u5, each failing before the
    cure for its charged reason and standing credited
    after it."""

    def test_u1_closed_inside_unclosed_after_ruled_credits(self):
        model, output = _run(
            "Status: Rul<!-- c -->ed <!-- unclosed",
            "u1_closed_inside_unclosed_after_ruled.md")
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

    def test_u1_cli_matches_the_plain_value_comparator(self):
        # The plain value comparator of the attack paper (a
        # plain Ruled value with the same unclosed segment
        # after it) stands credited on this tree; the
        # charged form takes the same standing after the
        # cure, on both subcommands.
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Rul<!-- c -->ed <!-- unclosed",
                    "u1_closed_inside_unclosed_after_ruled.md",
                    subcommand)
                plain_code, _plain = _run_cli(
                    "Status: Ruled <!-- unclosed",
                    "u1_plain_value_comparator.md", subcommand)
                self.assertEqual(code, plain_code)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_u3_closed_inside_unclosed_after_banked_credits(self):
        # The charged credit is the value credit: the
        # attack paper's loss on this construction is the
        # value standing unclassified and, with it, the
        # Banked head standing the value carries. The
        # Banked head evidence group itself cannot stand
        # on this body after the cure, for a reason outside
        # the charge: the unclosed segment leaves the
        # comment open over the entry's remaining lines, so
        # its evidence paragraph stands inside the comment
        # as written, exactly as the plain value comparator
        # u2 stands on the same body. The assertion is
        # therefore the value credit in full, beside the
        # comparator's own standing on the same body.
        model, output = _run(
            "Status: Ban<!-- c -->ked <!-- unclosed",
            "u3_closed_inside_unclosed_after_banked.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Banked")
        self.assertEqual(h.get(element, "disposition"),
                         "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_occurrence_total(output), 1)
        _cmodel, comparator = _run(
            "Status: Banked <!-- unclosed",
            "u3_plain_value_comparator.md")
        self.assertEqual(h.entry_state(_entry(output)),
                         h.entry_state(_entry(comparator)))
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"),
            _group_members(comparator, "unheaded paragraphs"))

    def test_u5_sep_closed_inside_closed_unclosed_after(self):
        # Construction 3 of the finding: a closed segment
        # in the separator and a closed segment inside the
        # word earn the reading together, on the same
        # comparator bound as construction 2.
        model, output = _run(
            "Status: <!-- a -->Ban<!-- c -->ked <!-- x",
            "u5_sep_closed_inside_closed_unclosed_after.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Banked")
        self.assertEqual(h.get(element, "disposition"),
                         "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_occurrence_total(output), 1)
        _cmodel, comparator = _run(
            "Status: Banked <!-- unclosed",
            "u5_plain_value_comparator.md")
        self.assertEqual(h.entry_state(_entry(output)),
                         h.entry_state(_entry(comparator)))


class Ch125BoundPinsTest(unittest.TestCase):
    """The governed bound in the other direction, standing
    before and after: a segment left unclosed credits
    nothing past its opening."""

    def test_u4_unclosed_inside_value_credits_nothing(self):
        # Case u4: the segment inside the value word itself
        # stands unclosed, so the word never forms; the
        # recorded value stands unclassified and no Banked
        # head evidence group stands, exactly as the CH-108
        # bound guard pin holds it.
        _model, output = _run("Status: Ban<!-- c ked",
                              "u4_unclosed_inside_value.md")
        self.assertIsNotNone(output)
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"), [])
        self.assertEqual(len(_unclassified_notes(output)), 1)

    def test_unclosed_opening_inside_value_no_closed_segment(self):
        _model, output = _run("Status: Ban<!-- c",
                              "k4_unclosed_opening_inside_value.md")
        self.assertIsNotNone(output)
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"), [])
        self.assertEqual(len(_unclassified_notes(output)), 1)

    def test_u2_plain_value_unclosed_after_stands_credited(self):
        # The isolation comparator of the finding: a plain
        # Banked value standing before an unclosed opening
        # is credited on this tree, before and after. The
        # credit claimed is the value credit itself: the
        # attack paper records the value whole as Banked
        # beside the rule 9 Warnings the open comment state
        # prints against the lines under it, and the Banked
        # head evidence group is not part of that claim, the
        # unclosed segment leaving the comment open over the
        # entry's remaining lines.
        model, output = _run("Status: Banked <!-- unclosed",
                             "u2_plain_value_unclosed_after.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "disposition"),
                         "Banked")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_occurrence_total(output), 1)


class Ch126SecondMarkerChargedTest(unittest.TestCase):
    """F-11R7-02: the charged construction of the attack
    paper, case d1, failing before the cure for its
    charged reason and standing decided after it."""

    def test_d1_second_marker_segment_inside_credits(self):
        model, output = _run(
            "Status: Banked Status: Rul<!-- c -->ed",
            "d1_two_markers_second_segment_inside.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[1], "verbatim"),
                         "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertNotEqual(h.entry_state(_entry(output)),
                            "Ambiguous")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(_occurrence_total(output), 2)

    def test_d1_cli_matches_its_plain_twin(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Banked Status: Rul<!-- c -->ed",
                    "d1_two_markers_second_segment_inside.md",
                    subcommand)
                twin_code, _twin = _run_cli(
                    "Status: Banked Status: Ruled",
                    "d1_plain_twin.md", subcommand)
                self.assertEqual(code, twin_code)
                self.assertNotEqual(code, 4)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)


class Ch126ContrastAndBoundPinsTest(unittest.TestCase):
    """Contrasts and bounds of the second marker limb,
    standing before and after."""

    def test_d2_first_marker_segment_inside_stands_credited(self):
        # The contrast of the finding: a segment inside the
        # first element on the same line is reached by the
        # CH-108 reading, and the plain second element
        # stands credited, before and after.
        model, output = _run(
            "Status: Ban<!-- c -->ked Status: Ruled",
            "d2_two_markers_first_segment_inside.md")
        self.assertIsNotNone(output)
        elements = _elements(model)
        self.assertEqual(len(elements), 2)
        self.assertEqual(h.get(elements[0], "verbatim"),
                         "Banked")
        self.assertEqual(h.get(elements[1], "verbatim"),
                         "Ruled")
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)

    def test_d3_later_status_line_stands_as_its_twin(self):
        # Case d3: a later Status line in the entry carrying
        # a segment inside its Ruled value stands exactly as
        # its plain twin stands, before and after.
        def _later_body(status_line):
            body = h._header_block()
            body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
            body += "Question: Which option?\n"
            body += "Options: A, B\n"
            body += "Cost of deciding late: blocked.\n"
            body += "Blocks: DQ-002\n\n"
            body += status_line + "\n\nA waiting paragraph.\n"
            return body

        _model, output = h.run_pipeline(
            _later_body("Status: Rul<!-- c -->ed").encode(
                "utf-8"),
            "d3_later_status_line_segment_inside.md")
        _twin_model, twin = h.run_pipeline(
            _later_body("Status: Ruled").encode("utf-8"),
            "d3_later_status_line_plain_twin.md")
        self.assertIsNotNone(output)
        self.assertIsNotNone(twin)
        self.assertEqual(h.entry_state(_entry(output)),
                         h.entry_state(_entry(twin)))
        self.assertEqual(h.canonical_counts(output),
                         h.canonical_counts(twin))
        self.assertEqual(_occurrence_total(output),
                         _occurrence_total(twin))

    def test_embedded_marker_off_the_head_line_keeps_masked(self):
        # The charge reaches the head line only: an embedded
        # marker on a line carrying no line start marker
        # keeps its masked reading, before and after.
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "Question: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\n"
        body += "A note Status: Rul<!-- c -->ed today.\n"
        model, output = h.run_pipeline(
            body.encode("utf-8"),
            "k4_embedded_marker_off_head_line.md")
        self.assertIsNotNone(output)
        verbatims = [h.get(element, "verbatim")
                     for element in _elements(model)]
        self.assertTrue(any(
            verbatim is not None and "Rul" in verbatim
            and "  " in verbatim
            and not verbatim.startswith("Ruled")
            for verbatim in verbatims))


class Ch127VariantPaddingChargedTest(unittest.TestCase):
    """F-11R7-03: the charged constructions of the attack
    paper, cases vt1 and vt2, each failing before the cure
    for its charged reason and standing unpadded after
    it."""

    def test_vt1_variant_segment_after_phrase_unpadded(self):
        model, output = _run("Status unchanged<!-- c -->",
                             "vt1_variant_segment_after_phrase.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "kind"),
                         "variant phrasing")
        self.assertEqual(h.get(element, "verbatim"),
                         "Status unchanged")
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 1)

    def test_vt2_variant_segment_after_phrase_space_unpadded(self):
        model, _output = _run(
            "Status unchanged <!-- c -->",
            "vt2_variant_segment_after_phrase_space.md")
        element = _head_element(model)
        twin_model, _twin_output = _run(
            "Status unchanged ",
            "vt2_variant_plain_twin.md")
        twin_element = _head_element(twin_model)
        self.assertEqual(h.get(element, "verbatim"),
                         h.get(twin_element, "verbatim"))
        self.assertEqual(h.get(element, "verbatim"),
                         "Status unchanged ")


class Ch127ContrastPinsTest(unittest.TestCase):
    """Contrasts of the variant limb, standing before and
    after."""

    def test_vt3_variant_segment_inside_and_after_credits(self):
        # The contrast of the finding: where a segment also
        # stands inside the word, the CH-89 gate is met and
        # the stored form is taken whole, before and after.
        model, output = _run(
            "Status un<!-- c -->changed<!-- d -->",
            "vt3_variant_segment_inside_and_after.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"),
                         "Status unchanged")
        self.assertEqual(h.entry_state(_entry(output)), "Open")

    def test_plain_variant_line_control(self):
        model, output = _run("Status unchanged",
                             "k4_plain_variant_control.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"),
                         "Status unchanged")
        self.assertEqual(h.entry_state(_entry(output)), "Open")


if __name__ == "__main__":
    unittest.main()
