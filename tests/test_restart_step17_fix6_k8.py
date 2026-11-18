"""Restart Step 17 fix wave 6, Seat K8 tests.

Charges CH-98 and CH-99 (validate), seat 5 findings A6-5-1
(High) and A6-5-2 (Medium) of round 6 (design/steps/
step-17r-attack6-5.md), both cost findings, as ruled at
record section 58 ruling (f) and prepared at design/steps/
step-17r-triage6-prep.md headed question 6.

CH-98: the PIN-09 claim fan out in a file level note section.
One line holding N state claims takes one PIN-09 Note per
claim, each Note carrying the whole claim line as its
evidence, so the validate output grows with the square of
the claim count inside one line: at N 900 a 15,411 byte file
takes 28,014,619 bytes of validate output, 8.535 CPU seconds
and 304.4 MB peak RSS, and render takes 13,914,462 bytes at
the same shape, measured by the attack seat. Ruling (f) limb
one: the combining ground of ruling (d) of section 52
reaches the claim print: where one line names more than one
claim target, its claim Notes stand combined into one Note
per line naming every claim target it carries and quoting
the line once; the governed single claim form (a line
carrying one claim) keeps its exact standing form.

The combined Note form these tests state first: one PIN-09
Note at Note grade, standing where the line's first claim
Note stood, on that Note's host and span, with the claim
line as its evidence, its basis and its claiming unit
unchanged, its statement naming every claim target of the
line in line order and quoting the line once, in the form:
A file level note section records claims about DQ-100,
DQ-101 and DQ-102: "<the line>" The claims are reported as
claims and are never applied. The combined Note carries the
claim targets in its named entries. A line carrying exactly
one claim keeps the standing single form whole, word for
word: A file level note section records a claim about
DQ-999: "DQ-999 is Ruled" The claim is reported as a claim
and is never applied.

CH-99: the ghost citation reading cost inside one entry.
Many wide ghost statements in one entry pay a reading cost
growing near quadratically in the statements per entry, on
both subcommands, while the findings output of the same
files stands linear: validate CPU 0.457 s, 1.366 s, 3.112 s,
9.523 s and 20.059 s at 4, 10, 20, 40 and 60 lines of 900
ghosts per statement line in one entry, measured by the
attack seat. Ruling (f) limb two: the reading is restated so
the per statement cost of one entry stands independent of
the number of wide ghost statements the entry already
carries, the total growing linearly, the findings standing
exact on every construction. The CH-99 tests below pin the
governed forms object for object, before the cure and after
it: they are the fail before anchor of the charge, and the
cost itself stands measured in the seat paper, never tested
as a verdict. No test in this file pins a time or a byte
count as a verdict; the output bound tests assert the size
of the charged prints, the surface CH-98 charges, at a bound
the combined form meets by construction and the fan out form
exceeds by two orders of magnitude at the same input.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

_HEADER = "# Decision queue\n\n"

_SINGLE_FORM = (
    "A file level note section records a claim about %s: "
    "\"%s\" The claim is reported as a claim and is never "
    "applied.")

_COMBINED_FORM = (
    "A file level note section records claims about %s: "
    "\"%s\" The claims are reported as claims and are never "
    "applied.")

_BASIS = ("a governing or state claim by a file "
          "level note section, PIN-09")

_PD_R7_COMBINED_FORM = (
    "%s are cited, but no headed entry in the file carries "
    "those numbers: the cited numbers are reported once "
    "under PD-R7 only.")


def _run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline refused the input")
    return output


def _pin09(output):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "")
            == "PIN-09"]


def _pd_r7(output):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "")
            == "PD-R7"]


def _plain_entry(number):
    return ("### DQ-%03d: Plain entry %d\nStatus: Banked\n"
            "This question is waiting for a decision.\n"
            % (number, number))


def _notes_text(lines):
    parts = [_HEADER, _plain_entry(1), "\n## Notes\n\n"]
    for line in lines:
        parts.append(line + "\n")
    return "".join(parts)


def _claim_line(pairs):
    return ", ".join("DQ-%03d is %s" % pair for pair in pairs) + "."


def _named(finding):
    return [h.text_of(item) for item in h.as_list(
        h.get(finding, "named_entries", "named_entry_ids"))]


def _join_names(names):
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _wide_entry(number, statements):
    parts = ["### DQ-%03d: Wide ghost entry\nStatus: Banked\n"
             % number]
    for statement in statements:
        parts.append(statement + "\n")
    parts.append("\n")
    return "".join(parts)


def _supersedes_statement(numbers):
    return ("This supersedes the ruling at "
            + ", ".join("DQ-%03d" % n for n in numbers) + ".")


class Ch98CombinedClaimNoteTest(unittest.TestCase):
    """The charged constructions: one claim line naming more
    than one claim target takes one combined PIN-09 Note."""

    def test_two_claim_line_takes_one_combined_note(self):
        line = _claim_line([(100, "Ruled"), (101, "Ruled")])
        output = _run_text(_notes_text([line]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(h.finding_severity(note), "Note")
        self.assertEqual(
            h.finding_statement(note),
            _COMBINED_FORM % ("DQ-100 and DQ-101", line))
        self.assertEqual(h.finding_evidence_text(note), line)
        self.assertEqual(_named(note), ["DQ-100", "DQ-101"])
        self.assertEqual(h.text_of(h.get(note, "basis")), _BASIS)

    def test_three_claim_line_combined_form_single_quote(self):
        line = _claim_line(
            [(100, "Ruled"), (101, "Ruled"), (102, "Ruled")])
        output = _run_text(_notes_text([line]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(
            h.finding_statement(note),
            _COMBINED_FORM % ("DQ-100, DQ-101 and DQ-102", line))
        self.assertEqual(h.finding_evidence_text(note), line)
        self.assertEqual(
            _named(note), ["DQ-100", "DQ-101", "DQ-102"])
        quoted = sum(
            h.finding_evidence_text(f).count(line)
            for f in h.findings_of(output))
        self.assertEqual(quoted, 1)

    def test_mixed_state_words_on_one_line_combine(self):
        line = _claim_line(
            [(100, "Ruled"), (101, "Settled"), (102, "Banked")])
        output = _run_text(_notes_text([line]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            h.finding_statement(notes[0]),
            _COMBINED_FORM % ("DQ-100, DQ-101 and DQ-102", line))
        self.assertEqual(
            _named(notes[0]), ["DQ-100", "DQ-101", "DQ-102"])

    def test_two_claim_lines_each_take_their_own_combined_note(self):
        first = _claim_line([(100, "Ruled"), (101, "Ruled")])
        second = _claim_line(
            [(200, "Ruled"), (201, "Ruled"), (202, "Ruled")])
        output = _run_text(_notes_text([first, second]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 2)
        by_evidence = {
            h.finding_evidence_text(n): n for n in notes}
        self.assertEqual(set(by_evidence), {first, second})
        self.assertEqual(
            h.finding_statement(by_evidence[first]),
            _COMBINED_FORM % ("DQ-100 and DQ-101", first))
        self.assertEqual(
            h.finding_statement(by_evidence[second]),
            _COMBINED_FORM % ("DQ-200, DQ-201 and DQ-202", second))

    def test_repeated_target_on_second_line_stays_deduped(self):
        # The standing per segment claim dedup stands in front
        # of the combining: a target claimed on a first line
        # takes no second Note on a later line, and the later
        # line combines only the targets it first carries.
        first = _claim_line([(100, "Ruled"), (101, "Ruled")])
        second = _claim_line([(100, "Settled"), (102, "Ruled")])
        output = _run_text(_notes_text([first, second]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 2)
        by_evidence = {
            h.finding_evidence_text(n): n for n in notes}
        self.assertEqual(set(by_evidence), {first, second})
        self.assertEqual(
            h.finding_statement(by_evidence[first]),
            _COMBINED_FORM % ("DQ-100 and DQ-101", first))
        self.assertEqual(
            h.finding_statement(by_evidence[second]),
            _SINGLE_FORM % ("DQ-102", "DQ-102 is Ruled"))
        self.assertEqual(_named(by_evidence[second]), ["DQ-102"])

    def test_combined_note_keeps_first_note_host_and_unit(self):
        line = _claim_line([(100, "Ruled"), (101, "Ruled")])
        combined_output = _run_text(_notes_text([line]))
        single_output = _run_text(
            _notes_text([_claim_line([(999, "Ruled")])]))
        combined = _pin09(combined_output)
        single = _pin09(single_output)
        self.assertEqual(len(combined), 1)
        self.assertEqual(len(single), 1)
        self.assertEqual(
            h.finding_entry_id(combined[0]),
            h.finding_entry_id(single[0]))
        self.assertEqual(
            h.text_of(h.get(combined[0], "claiming_unit")),
            h.text_of(h.get(single[0], "claiming_unit")))
        span = h.get(combined[0], "line_span", "span")
        single_span = h.get(single[0], "line_span", "span")
        self.assertEqual(
            h.get(span, "start_line"),
            h.get(single_span, "start_line"))
        self.assertEqual(
            h.get(span, "end_line"), h.get(span, "start_line"))


class Ch98GovernedSingleClaimPinsTest(unittest.TestCase):
    """The governed single claim forms, stated test first
    either way: they pass before the cure and after it, word
    for word as they stand on the uncured tree."""

    def test_single_claim_line_exact_standing_form(self):
        line = _claim_line([(999, "Ruled")])
        output = _run_text(_notes_text([line]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(h.finding_severity(note), "Note")
        self.assertEqual(
            h.finding_statement(note),
            _SINGLE_FORM % ("DQ-999", "DQ-999 is Ruled"))
        self.assertEqual(h.finding_evidence_text(note), line)
        self.assertEqual(_named(note), ["DQ-999"])
        self.assertEqual(h.text_of(h.get(note, "basis")), _BASIS)

    def test_two_single_claim_lines_stay_two_single_notes(self):
        first = _claim_line([(100, "Ruled")])
        second = _claim_line([(101, "Settled")])
        output = _run_text(_notes_text([first, second]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 2)
        statements = sorted(
            h.finding_statement(n) for n in notes)
        self.assertEqual(
            statements,
            sorted([
                _SINGLE_FORM % ("DQ-100", "DQ-100 is Ruled"),
                _SINGLE_FORM % ("DQ-101", "DQ-101 is Settled")]))

    def test_governing_claim_form_keeps_its_standing_form(self):
        # The recorded governing claim of a note section (the
        # claims list form, not the fallback scan) stands as
        # it stood: one Note, its statement the governing line
        # carried whole, its named entries the governed set.
        line = "This section governs DQ-100 and DQ-101."
        output = _run_text(_notes_text([line]))
        notes = _pin09(output)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(
            h.finding_statement(note),
            "A file level note section records a claim: %s "
            "The claim is reported as a claim and is never "
            "applied." % line)
        self.assertEqual(h.finding_evidence_text(note), line)
        self.assertEqual(_named(note), ["DQ-100", "DQ-101"])

    def test_claim_line_inside_an_entry_body_takes_no_pin09(self):
        # The claim print stands on file level note sections
        # only: a claim line standing in an entry body takes
        # no PIN-09 Note (the attack paper observation O4
        # scope control).
        text = (_HEADER
                + "### DQ-001: Plain entry 1\nStatus: Banked\n"
                + _claim_line([(100, "Ruled")]) + "\n")
        output = _run_text(text)
        self.assertEqual(_pin09(output), [])


class Ch98OutputBoundTest(unittest.TestCase):
    """The charged surface at the attack seat's own shape:
    the claim fan out print on validate and on render. The
    bounds are output size bounds, stated as measurements of
    the prints, never as time verdicts."""

    def _claims_text(self, n):
        line = _claim_line(
            [(i, "Ruled") for i in range(100, 100 + n)])
        return _notes_text([line]), line

    def test_claims_250_validate_output_stays_linear(self):
        text, line = self._claims_text(250)
        output = _run_text(text)
        notes = _pin09(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(len(_named(notes[0])), 250)
        self.assertEqual(h.finding_evidence_text(notes[0]), line)
        rendered = h.render_text(output, "validate")
        self.assertLess(len(rendered.encode("utf-8")), 30000)

    def test_claims_250_cli_validate_output_bound(self):
        text, _line = self._claims_text(250)
        path = h.temp_input(text.encode("utf-8"))
        try:
            code, stdout, _stderr = h.run_cli("validate", path)
        finally:
            path.unlink()
        self.assertEqual(code, 1)
        self.assertLess(len(stdout), 30000)

    def test_claims_250_cli_render_output_bound(self):
        text, _line = self._claims_text(250)
        path = h.temp_input(text.encode("utf-8"))
        try:
            code, stdout, _stderr = h.run_cli("render", path)
        finally:
            path.unlink()
        self.assertEqual(code, 1)
        self.assertLess(len(stdout), 30000)


class Ch99GhostReadingFormsTest(unittest.TestCase):
    """The governed ghost reading forms on the CH-99 ground,
    pinned object for object before the cure and after it:
    the multi statement entry, the distinct entries form, and
    the headed control. The reading cost itself stands
    measured in the seat paper, never tested here."""

    def test_two_wide_lines_in_one_entry_forms_exact(self):
        first = _supersedes_statement([100, 101, 102])
        second = _supersedes_statement([200, 201, 202])
        text = (_HEADER + _plain_entry(1)
                + _wide_entry(2, [first, second]))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 2)
        by_evidence = {
            h.finding_evidence_text(n): n for n in notes}
        self.assertEqual(set(by_evidence), {first, second})
        self.assertEqual(
            h.finding_statement(by_evidence[first]),
            _PD_R7_COMBINED_FORM % "DQ-100, DQ-101 and DQ-102")
        self.assertEqual(
            _named(by_evidence[first]),
            ["DQ-100", "DQ-101", "DQ-102"])
        self.assertEqual(
            h.finding_statement(by_evidence[second]),
            _PD_R7_COMBINED_FORM % "DQ-200, DQ-201 and DQ-202")
        self.assertEqual(
            _named(by_evidence[second]),
            ["DQ-200", "DQ-201", "DQ-202"])

    def test_twenty_wide_lines_in_one_entry_forms_exact(self):
        statements = []
        expected = {}
        nxt = 100
        for _ in range(20):
            numbers = list(range(nxt, nxt + 30))
            statement = _supersedes_statement(numbers)
            statements.append(statement)
            expected[statement] = ["DQ-%03d" % n for n in numbers]
            nxt += 30
        text = (_HEADER + _plain_entry(1)
                + _wide_entry(2, statements))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 20)
        for note in notes:
            evidence = h.finding_evidence_text(note)
            self.assertIn(evidence, expected)
            self.assertEqual(_named(note), expected[evidence])
            self.assertEqual(
                h.finding_statement(note),
                _PD_R7_COMBINED_FORM % _join_names(
                    expected[evidence]))

    def test_distinct_entries_form_stands_exact(self):
        statements = {}
        parts = [_HEADER, _plain_entry(1)]
        for entry_number, first in ((2, 100), (3, 200), (4, 300)):
            statement = _supersedes_statement(
                [first, first + 1, first + 2])
            statements[statement] = [
                "DQ-%03d" % n for n in (first, first + 1, first + 2)]
            parts.append(_wide_entry(entry_number, [statement]))
        output = _run_text("".join(parts))
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 3)
        for note in notes:
            evidence = h.finding_evidence_text(note)
            self.assertIn(evidence, statements)
            self.assertEqual(_named(note), statements[evidence])

    def test_headed_control_pointers_stand_exact(self):
        first = _supersedes_statement([3])
        second = _supersedes_statement([4])
        text = (_HEADER + _plain_entry(1) + _plain_entry(3)
                + _plain_entry(4)
                + _wide_entry(2, [first, second]))
        output = _run_text(text)
        self.assertEqual(_pd_r7(output), [])
        for target in ("DQ-003", "DQ-004"):
            entry = h.entry_by_id(output, target)
            self.assertIsNotNone(entry)
            pointers = [h.text_of(p) for p in h.as_list(
                h.get(entry, "supersession_pointers"))]
            self.assertEqual(pointers, ["DQ-002"])

    def test_single_wide_line_in_one_entry_form_exact(self):
        statement = _supersedes_statement([100, 101, 102])
        text = (_HEADER + _plain_entry(1)
                + _wide_entry(2, [statement]))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            h.finding_statement(notes[0]),
            _PD_R7_COMBINED_FORM % "DQ-100, DQ-101 and DQ-102")
        self.assertEqual(
            _named(notes[0]), ["DQ-100", "DQ-101", "DQ-102"])


if __name__ == "__main__":
    unittest.main()
