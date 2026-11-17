"""Restart Step 16 fix wave 2, Fix seat H tests.

Seat H owns two side rulings from Auditor 7 of confirmation
round 2 (design/steps/step-16r-audit2-7.md, rows 7 and 10),
triaged at design/steps/step-16r-record.md section 10. Each
test pins the ruled behaviour, written before any cure.

Item 1, the Segment claims item (Medium, row 10). Ruled
against the brief first hand: the brief at PIN-09 in section
5.3 specifies that a governing or state claim made by a file
level note section is reported as a claim and never applied,
with no restriction to any one wording of the claim, and the
plan carries the segment claim reports as a field of the
validate output (the field the Segment claims section of both
outputs prints from). The product recognises a hand drafted
plain prose claim (DQ-001 is settled, stated in a level 2 Note
section) as a PIN-09 claim in its findings, through the
fallback scan in validate, but builds the segment claim
reports from the parse level claims alone, which cover only
the governs form and the Manager addition bullet form. The
reports therefore miss every claim the fallback scan
recognises, no Segment claims section stands in either
output, and the render output, which prints no findings list,
drops the claim entirely. Corpus shaped claims (fixture R8)
receive the section in both outputs. Ruled a product side
defect in validate, the owning layer for note section claim
reporting under the brief layer map at section 5.1. The
adjacency check stands in the open in the seat paper: the
WV-9 printing decision (S8R-O-34) governs only whether the
residue share prints in the shared head, a different component
at a different position, so this defect stands outside that
decision ground and is cured here, test first, in validate.py.

Item 2, the F2 refusal facts product limb (part of a Medium,
row 7). Ruled in three parts. The designation part stands with
the D-02 design question and takes no cure: the tests below
pin only that the designation position stands on the refusal
surfaces, in its current absent form, so a later D-02 ruling
moves it in one place. The invalid bytes line count part is
ruled no defect: the brief defines the line count on the
decoded text (the File shape at section 5.5 and the line
partition on decoded lines), a file whose bytes do not decode
has no decoded text and therefore no line count the tool can
state, and the byte count and digest it prints are facts of
the bytes read, which stand before decoding. The shell byte
limit part is ruled no defect on the same ground in its own
form: the brief at Q-31 checks the byte limit from the file
size before the file is read, so no digest of bytes read and
no line count of a decoded text stand for that refusal; its
locus in shell.py also stands outside this seat ownership in
any case, and it is left untouched. The two no defect parts
are pinned as they stand, so a later change to either form is
a visible change against a pin.
"""

import unittest
from pathlib import Path

import dqv_harness as h


HAND_NOTE = (
    "# Decision queue\n"
    "\n"
    "### DQ-001: A sample question\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "A plain paragraph about this question.\n"
    "\n"
    "## Note\n"
    "\n"
    "DQ-001 is settled.\n"
).encode("utf-8")

HAND_AMENDMENT = (
    "# Decision queue\n"
    "\n"
    "### DQ-001: A sample question\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "A plain paragraph about this question.\n"
    "\n"
    "## Amendment note\n"
    "\n"
    "DQ-001 is settled.\n"
).encode("utf-8")

INVALID_BYTES = b"# Decision queue\n\n\xff\xfe invalid \x80 bytes\n"


def run_file(subcommand, data, name="queue.md"):
    path = h.temp_input(data, name)
    try:
        code, out, err = h.run_cli(subcommand, path)
    finally:
        Path(path).unlink(missing_ok=True)
    return (code, out.decode("utf-8", errors="replace"),
            err.decode("utf-8", errors="replace"))


def facts_line(output):
    for line in output.splitlines():
        if line.startswith("File:"):
            return line
    raise AssertionError("no File line in output: " + output)


class HandNoteSegmentClaimsTest(unittest.TestCase):
    """Item 1: a hand drafted Note section claim stands in the
    Segment claims section of both outputs, reported as a claim
    and never applied."""

    def test_pin09_finding_stands_for_the_hand_claim(self):
        _model, output = h.run_pipeline(HAND_NOTE)
        pin09 = [finding for finding in h.findings_of(output)
                 if h.get(finding, "rule_id") == "PIN-09"]
        self.assertEqual(len(pin09), 1)

    def test_segment_claim_reports_carry_the_hand_claim(self):
        _model, output = h.run_pipeline(HAND_NOTE)
        reports = h.get(output, "segment_claim_reports") or []
        self.assertEqual(len(reports), 1)
        report = reports[0]
        self.assertIn("DQ-001 is settled",
                      h.get(report, "statement") or "")
        self.assertEqual(
            list(h.get(report, "named_entries") or []), ["DQ-001"])

    def test_validate_output_carries_the_section(self):
        _model, output = h.run_pipeline(HAND_NOTE)
        text = h.render_text(output, "validate")
        self.assertIn("Segment claims", text)
        self.assertIn("DQ-001 is settled", text)

    def test_render_output_carries_the_section_and_the_claim(self):
        _model, output = h.run_pipeline(HAND_NOTE)
        text = h.render_text(output, "render")
        self.assertIn("Segment claims", text)
        self.assertIn("DQ-001 is settled", text)
        self.assertIn("Entries named in the claim: DQ-001", text)

    def test_section_stands_before_the_figures(self):
        _model, output = h.run_pipeline(HAND_NOTE)
        for form in ("validate", "render"):
            text = h.render_text(output, form)
            self.assertLess(text.index("Segment claims"),
                            text.index("Figures"), form)

    def test_claim_is_never_applied_to_the_named_entry(self):
        _model, output = h.run_pipeline(HAND_NOTE)
        entry = h.entry_by_id(output, "DQ-001")
        self.assertIsNotNone(entry)
        self.assertNotEqual(h.entry_state(entry), "Settled")

    def test_amendment_note_shape_behaves_the_same_way(self):
        _model, output = h.run_pipeline(HAND_AMENDMENT)
        reports = h.get(output, "segment_claim_reports") or []
        self.assertEqual(len(reports), 1)
        text = h.render_text(output, "render")
        self.assertIn("Segment claims", text)
        self.assertIn("DQ-001 is settled", text)


class CorpusSegmentClaimsGuardTest(unittest.TestCase):
    """Item 1 guard: the corpus shaped claims of fixture R8
    keep the section in both outputs, unchanged in count."""

    def test_r8_reports_stand(self):
        _model, output = h.cached_pipeline("R8")
        reports = h.get(output, "segment_claim_reports") or []
        self.assertTrue(reports)

    def test_r8_section_in_both_outputs(self):
        _model, output = h.cached_pipeline("R8")
        self.assertIn("Segment claims",
                      h.render_text(output, "validate"))
        self.assertIn("Segment claims",
                      h.render_text(output, "render"))


class RefusalFactsRuledFormsTest(unittest.TestCase):
    """Item 2: the refusal facts forms as ruled. The designation
    position stands in its absent form under the D-02 design
    question, the invalid bytes refusal prints no line count
    because no decoded line count exists for it, and the shell
    byte limit refusal prints the byte count only because that
    refusal stands before any read."""

    def test_invalid_bytes_refusal_facts_as_ruled(self):
        code, out, err = run_file("validate", INVALID_BYTES)
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: absent, "), line)
        self.assertIn("bytes", line)
        self.assertIn("digest", line)
        self.assertNotIn("lines", line)

    def test_invalid_bytes_failure_carries_no_line_count(self):
        failure, output = h.run_pipeline(INVALID_BYTES)
        self.assertIsNone(output)
        self.assertIsNone(h.get(failure, "line_count"))
        self.assertEqual(h.get(failure, "byte_count"),
                         len(INVALID_BYTES))
        self.assertTrue(h.get(failure, "digest"))

    def test_byte_limit_refusal_facts_as_ruled(self):
        data, _facts = h.limit_bytes_input()
        code, out, err = run_file("validate", data)
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertEqual(line, "File: absent, %d bytes" % len(data))

    def test_empty_file_refusal_facts_stand_full_but_designation(self):
        code, out, err = run_file("validate", b"", "empty.md")
        self.assertEqual(code, 3)
        line = facts_line(err)
        self.assertTrue(line.startswith("File: absent, "), line)
        self.assertIn("0 lines", line)
        self.assertIn("0 bytes", line)
        self.assertIn("digest", line)


if __name__ == "__main__":
    unittest.main()
