"""Restart Step 15 fix wave 2, Seat E tests.

Source: the plan (design/DESIGN-PLAN-RESTART.md) Item 3, section
3.6 (the verbatim appendix row fields, and the appendix carrying
a separate named part for unclassified phrasings under AF-2, the
part being the appendix home of the residue items whose phrasings
are unclassified) and section 3.7 (the residue items standing on
the render model as a declared field), and the brief section 5.5
(the residue item shape, and AF-2 at section 5.7), against the
differing form recorded at design/traces/
step-15r-confirm2-trace.md element 26 (A1-F6): render read the
unclassified marking off an attribute that stands in no declared
field list, attached at runtime by validate.

Each test pins the render limb of that form. Expectations come
from the plan and brief at their seals, never from a run of the
tool. The declared carrier the cured render reads is the residue
items list on the model: validate builds one residue item per
untranslatable phrasing per entry carrying it, and a phrasing
stands untranslatable exactly where it stands outside the
vocabulary mapping, the same predicate the removed dynamic
attachment computed.
"""

import unittest
from types import SimpleNamespace

import dqv_harness as h

render = h.import_module("render")
types = h.import_module("types")


def make_row(phrasing, kind="line start", count=1, members=("DQ-001",)):
    return types.VerbatimAppendixRow(
        phrasing=phrasing, occurrence_count=count, kind=kind,
        member_entry_ids=list(members))


def make_residue(phrasing, entry_identifier="DQ-001"):
    return types.ResidueItem(
        phrasing=phrasing, entry_identifier=entry_identifier,
        line_span=types.Span(5, 5))


def make_output(rows, residue_items):
    """A hand built render model at the render model hand off
    seam, carrying its appendix rows in their declared shape
    only, plus the declared residue items field."""
    recon = SimpleNamespace(
        entry_total=None, dq_entry_count=0, unnumbered_entry_count=0,
        headed_span_count=0, orphan_note_segment_count=0,
        h4_sub_heading_count=0, status_occurrences_by_kind={},
        status_occurrence_total=0, canonical_counts={},
        ambiguous_count=0, unparsed_count=0,
        findings_per_severity={}, findings_per_rule={},
        distinct_phrasing_count=None, self_check=None,
        paired_total_declarations=[])
    facts = SimpleNamespace(
        input_name="synthetic.md", byte_count=100, line_count=10,
        digest="0" * 64)
    return SimpleNamespace(
        entries=[], findings=[], census=[], reconciliation=recon,
        file_facts=facts, limits=types.Limits(),
        vocabulary_version="1", output_form_edition="1",
        verbatim_appendix_rows=list(rows),
        per_rule_clearing_forms={}, crosswalk_counts={},
        waiting=0, blocking=0, blocking_list=[], limbo_data={},
        segment_claim_reports=[],
        fastest_item="not derivable from the file",
        supersession_chains=[], residue_items=list(residue_items))


def appendix_section(text):
    start = text.index("Verbatim appendix")
    rest = text[start:]
    end = rest.find("\nResidue list")
    if end >= 0:
        rest = rest[:end]
    return rest


class UnclassifiedMarkingFromDeclaredCarrierTest(unittest.TestCase):
    """A1-F6, render limb: the unclassified marking and the
    separate named appendix part stand on the declared residue
    carrier, not on an undeclared row attribute."""

    def test_declared_shape_row_is_marked_from_the_residue_carrier(self):
        row = make_row("Deferred")
        self.assertFalse(
            hasattr(row, "unclassified"),
            "the hand built row must stand in its declared shape "
            "only, with no dynamic attribute attached")
        output = make_output([row], [make_residue("Deferred")])
        section = appendix_section(render.render_validate(output))
        marked = ("Deferred | line start | 1 occurrence | "
                  "entries: DQ-001 | unclassified")
        self.assertIn(
            marked, section,
            "a row whose phrasing the model residue items carry "
            "stands unmarked in the appendix")
        self.assertIn(
            "Unclassified phrasings, held as unknown:", section,
            "the separate named part for unclassified phrasings "
            "is missing from the appendix")
        self.assertGreaterEqual(
            section.count(marked), 2,
            "the marked line stands once in the appendix body and "
            "again in the separate named part")

    def test_marking_stands_in_the_render_summary_form(self):
        output = make_output([make_row("Deferred")],
                             [make_residue("Deferred")])
        section = appendix_section(render.render_summary(output))
        self.assertIn("Deferred | line start | 1 occurrence | "
                      "entries: DQ-001 | unclassified", section)
        self.assertIn("Unclassified phrasings, held as unknown:",
                      section)

    def test_classified_row_carries_no_marking(self):
        output = make_output([make_row("Banked")],
                             [make_residue("Deferred")])
        section = appendix_section(render.render_validate(output))
        self.assertIn("Banked | line start | 1 occurrence", section)
        self.assertNotIn(" | unclassified", section)
        self.assertNotIn("Unclassified phrasings", section)

    def test_dynamic_attribute_alone_no_longer_marks_a_row(self):
        row = make_row("Banked")
        row.unclassified = True
        output = make_output([row], [])
        section = appendix_section(render.render_validate(output))
        self.assertNotIn(
            " | unclassified", section,
            "render still reads the undeclared row attribute: a "
            "dynamically attached flag alone marked the row")
        self.assertNotIn("Unclassified phrasings", section)

    def test_dynamic_false_does_not_suppress_the_declared_carrier(self):
        row = make_row("Deferred")
        row.unclassified = False
        output = make_output([row], [make_residue("Deferred")])
        section = appendix_section(render.render_validate(output))
        self.assertIn(
            " | unclassified", section,
            "a dynamically attached false flag suppressed the "
            "marking the declared residue carrier charges")


class UnclassifiedBehaviourOnAProductRunTest(unittest.TestCase):
    """The behaviour the removed read served, on a model validate
    itself produces: an unclassified phrasing prints marked in
    the appendix and again in the separate named part. This test
    passes on the collected state only through the dynamic
    attachment, and must still pass once that attachment is
    removed, on the declared residue carrier alone."""

    def test_unclassified_phrasing_marks_on_a_pipeline_run(self):
        data = (
            "# Decision queue\n\nSynthetic queue shaped input.\n\n"
            "### DQ-001: First entry\n\nStatus: Deferred\n\n"
        ).encode()
        _model, output = h.run_pipeline(data)
        self.assertIsNotNone(output)
        rows = h.as_list(h.get(output, "verbatim_appendix_rows",
                               "appendix_rows", "verbatim_appendix"))
        deferred = [row for row in rows
                    if h.text_of(h.get(row, "phrasing")) == "Deferred"]
        self.assertTrue(deferred, "no appendix row for Deferred")
        residue = h.as_list(h.get(output, "residue_items",
                                  "residue_list", "residue"))
        self.assertIn(
            "Deferred",
            [h.text_of(h.get(item, "phrasing")) for item in residue],
            "validate carries no residue item for the unclassified "
            "phrasing, so no declared carrier stands for the "
            "appendix part")
        text = h.render_text(output, "validate")
        section = appendix_section(text)
        self.assertIn(" | unclassified", section)
        self.assertIn("Unclassified phrasings, held as unknown:",
                      section)


if __name__ == "__main__":
    unittest.main()
