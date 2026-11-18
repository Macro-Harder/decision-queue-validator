"""Restart Step 17 fix wave 5, Seat K9 tests.

Charge CH-76 (validate, the findings print): seat 5 Finding 1
of round 5 (design/steps/step-17r-attack5-5.md), a cost
finding. One statement line in comma list form naming N ghost
targets takes one PD-R7 Note per ghost, each Note quoting the
whole statement, so the validate output grows with the square
of the target count inside one statement: at N 1700 a 14,575
byte file takes 24,890,799 bytes of validate output, 13.213
CPU seconds, and 272.2 MB peak RSS, measured on the bench by
the attack seat; render shows none of the growth.

The cure stands under record section 52 ruling (d), stated
once there: the PD-R7 Note governed form stands whole (the
Note quotes the line carrying the target reference); where
one statement names more than one ghost target, the Notes
for that statement stand combined into one Note per statement
naming every ghost target it carries and quoting the
statement once; the governed single ghost forms keep their
exact standing form.

The combined Note form these tests state first: one PD-R7
Note at Note grade on the host of the first Note of the
statement, at that Note's span, with the statement's own
line as its evidence quoted once, its statement naming every
ghost target of the statement in statement order in the
form: DQ-100, DQ-101 and DQ-102 are cited, but no headed
entry in the file carries those numbers: the cited numbers
are reported once under PD-R7 only. The combined Note
carries the ghost targets in its named entries. A statement
naming exactly one ghost target takes the standing single
form whole, word for word: DQ-999 is cited, but no headed
entry in the file carries that number: the cited number is
reported once under PD-R7 only.

Cost figures in this file are measurements and bounds on
output size, never pass or fail verdicts on time: the output
bound tests assert the size of the validate print, which is
the charged surface, at a bound the combined form meets by
construction and the fan out form exceeds by an order of
magnitude at the same input.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

_HEADER = "# Decision queue\n\n"

_SINGLE_FORM = (
    "%s is cited, but no headed entry in the file carries "
    "that number: the cited number is reported once under "
    "PD-R7 only.")

_COMBINED_FORM = (
    "%s are cited, but no headed entry in the file carries "
    "those numbers: the cited numbers are reported once "
    "under PD-R7 only.")

_BASIS = "a cited number with no heading, PD-R7"


def _run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline refused the input")
    return output


def _pd_r7(output):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "")
            == "PD-R7"]


def _plain_entry(number):
    return ("### DQ-%03d: Plain entry %d\nStatus: Banked\n"
            "This question is waiting for a decision.\n"
            % (number, number))


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


def _wideghost_text(n, first=100):
    statement = _supersedes_statement(
        list(range(first, first + n)))
    return (_HEADER + _plain_entry(1)
            + _wide_entry(2, [statement]))


def _named(finding):
    return [h.text_of(item) for item in h.as_list(
        h.get(finding, "named_entries", "named_entry_ids"))]


def _join_names(names):
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


class Ch76CombinedNoteTest(unittest.TestCase):
    """The charged constructions: one statement naming more
    than one ghost target takes one combined Note."""

    def test_two_ghost_statement_takes_one_combined_note(self):
        statement = _supersedes_statement([100, 101])
        text = (_HEADER + _plain_entry(1)
                + _wide_entry(2, [statement]))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(h.finding_severity(note), "Note")
        self.assertEqual(
            h.finding_statement(note),
            _COMBINED_FORM % "DQ-100 and DQ-101")
        self.assertEqual(h.finding_evidence_text(note), statement)
        self.assertEqual(_named(note), ["DQ-100", "DQ-101"])
        self.assertEqual(
            h.text_of(h.get(note, "basis")), _BASIS)

    def test_three_ghost_statement_combined_form_single_quote(self):
        statement = _supersedes_statement([100, 101, 102])
        text = (_HEADER + _plain_entry(1)
                + _wide_entry(2, [statement]))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(
            h.finding_statement(note),
            _COMBINED_FORM % "DQ-100, DQ-101 and DQ-102")
        self.assertEqual(h.finding_evidence_text(note), statement)
        self.assertEqual(
            _named(note), ["DQ-100", "DQ-101", "DQ-102"])
        quoted = sum(
            h.finding_evidence_text(f).count(statement)
            for f in h.findings_of(output))
        self.assertEqual(quoted, 1)

    def test_mixed_headed_and_ghost_targets_in_one_statement(self):
        statement = _supersedes_statement([3, 100, 101])
        text = (_HEADER + _plain_entry(1) + _plain_entry(3)
                + _wide_entry(2, [statement]))
        output = _run_text(text)
        entry = h.entry_by_id(output, "DQ-003")
        self.assertIsNotNone(entry)
        pointers = [h.text_of(p) for p in h.as_list(
            h.get(entry, "supersession_pointers"))]
        self.assertEqual(pointers, ["DQ-002"])
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            h.finding_statement(notes[0]),
            _COMBINED_FORM % "DQ-100 and DQ-101")
        self.assertEqual(_named(notes[0]), ["DQ-100", "DQ-101"])

    def test_two_statements_each_take_their_own_combined_note(self):
        first = _supersedes_statement([100, 101])
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
            _COMBINED_FORM % "DQ-100 and DQ-101")
        self.assertEqual(
            h.finding_statement(by_evidence[second]),
            _COMBINED_FORM % "DQ-200, DQ-201 and DQ-202")

    def test_plain_citation_line_naming_many_ghosts_combines(self):
        line = ("The background mentions DQ-100, DQ-101 and "
                "DQ-102 in passing.")
        text = (_HEADER
                + "### DQ-001: Plain entry 1\nStatus: Banked\n"
                + line + "\n")
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            h.finding_statement(notes[0]),
            _COMBINED_FORM % "DQ-100, DQ-101 and DQ-102")
        self.assertEqual(h.finding_evidence_text(notes[0]), line)
        self.assertEqual(
            _named(notes[0]), ["DQ-100", "DQ-101", "DQ-102"])

    def test_ghost_middle_of_headed_list_keeps_single_form(self):
        statement = _supersedes_statement([1, 999, 3])
        text = (_HEADER + _plain_entry(1) + _plain_entry(3)
                + _wide_entry(2, [statement]))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            h.finding_statement(notes[0]), _SINGLE_FORM % "DQ-999")
        self.assertEqual(
            h.finding_evidence_text(notes[0]), statement)


class Ch76GovernedSingleGhostPinsTest(unittest.TestCase):
    """The governed single ghost forms, stated test first
    either way: they pass before the cure and after it, word
    for word as they stand on the uncured tree."""

    def test_single_ghost_supersession_statement_exact_form(self):
        statement = _supersedes_statement([999])
        text = (_HEADER + _plain_entry(1)
                + _wide_entry(2, [statement]))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(h.finding_severity(note), "Note")
        self.assertEqual(
            h.finding_statement(note), _SINGLE_FORM % "DQ-999")
        self.assertEqual(h.finding_evidence_text(note), statement)
        self.assertEqual(
            h.text_of(h.get(note, "basis")), _BASIS)
        self.assertEqual(_named(note), [])

    def test_single_ghost_plain_citation_exact_form(self):
        line = "The background mentions DQ-999 in passing."
        text = (_HEADER
                + "### DQ-001: Plain entry 1\nStatus: Banked\n"
                + line + "\n")
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            h.finding_statement(notes[0]), _SINGLE_FORM % "DQ-999")
        self.assertEqual(h.finding_evidence_text(notes[0]), line)

    def test_single_ghost_decided_entry_subject_exact_form(self):
        # The seat 7 case G3 form, as pinned in the slice
        # files: exactly one PD-R7 Note, in the single form,
        # and no second finding mentioning the ghost.
        text = ("# Decision queue\n\n"
                "### DQ-113: Supersedes a ghost, recognised form\n\n"
                "Status: RULED, closed\n\n"
                "Ruled by: Captain JP\n\n"
                "Ruling: DQ-999 is superseded by this entry and is "
                "displaced by it.\n\n"
                "Outcome: Done.\n\n"
                "Landing: Recorded in the queue.\n")
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            h.finding_statement(notes[0]), _SINGLE_FORM % "DQ-999")
        mentioning = [
            f for f in h.findings_of(output)
            if "DQ-999" in (
                (h.finding_statement(f) or "") + " "
                + h.finding_evidence_text(f))]
        self.assertEqual(len(mentioning), 1)

    def test_two_single_ghost_statements_stay_two_notes(self):
        first = _supersedes_statement([999])
        second = _supersedes_statement([998])
        text = (_HEADER + _plain_entry(1)
                + _wide_entry(2, [first, second]))
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 2)
        statements = sorted(
            h.finding_statement(n) for n in notes)
        self.assertEqual(
            statements,
            sorted([_SINGLE_FORM % "DQ-998",
                    _SINGLE_FORM % "DQ-999"]))


class Ch76OutputBoundTest(unittest.TestCase):
    """The charged surface at the attack seat's own shape:
    the validate findings print on the wideghost fan out.
    The bounds are output size bounds, stated as
    measurements of the print, never as time verdicts."""

    def test_wideghost_250_validate_output_stays_linear(self):
        text = _wideghost_text(250)
        output = _run_text(text)
        notes = _pd_r7(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(len(_named(notes[0])), 250)
        rendered = h.render_text(output, "validate")
        self.assertLess(len(rendered.encode("utf-8")), 30000)
        self.assertEqual(
            rendered.count("This supersedes the ruling at "
                           "DQ-100"), 1)

    def test_wideghost_250_render_output_shows_no_growth(self):
        # A pin, before and after: the render print carries
        # no findings list and shows none of the growth.
        text = _wideghost_text(250)
        output = _run_text(text)
        rendered = h.render_text(output, "render")
        self.assertLess(len(rendered.encode("utf-8")), 30000)

    def test_wideghost_250_cli_validate_output_bound(self):
        text = _wideghost_text(250)
        path = h.temp_input(text.encode("utf-8"))
        try:
            code, stdout, _stderr = h.run_cli("validate", path)
        finally:
            path.unlink()
        self.assertEqual(code, 1)
        self.assertLess(len(stdout), 30000)
        self.assertEqual(
            stdout.count(b"This supersedes the ruling at "
                         b"DQ-100"), 1)


if __name__ == "__main__":
    unittest.main()
