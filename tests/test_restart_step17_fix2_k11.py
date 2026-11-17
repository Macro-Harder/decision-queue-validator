"""Restart Step 17 fix wave 2, Seat K11 tests.

Charges CH-17 (supersession, cycle search and near miss width)
and CH-18 (the gap naming bound made one measure in validate
and shell), as ruled at section 19 of the step record and
prepared in the round 2 triage preparation.

CH-17 carries three findings. Finding 1 of seat 9 (High): a
cycle that shares an entry with an earlier walked branch takes
no cycle Warning for that cycle, and validate and render
disagree on the cycle inventory (the diamond and shared tail
constructions). Finding 2 of seat 9 (Low): a statement that
both identifies its target and names it again in a case variant
takes a not recognised Note that denies the pointer the same
report prints. F-11R2-03 of seat 11 (Low): a supersession
statement split across a paragraph break takes no near miss
Note and derives no pointer, where the same statement split
across lines of one paragraph takes the Note.

CH-18 carries Finding 1 of seat 18 (High): validate suppresses
the gap class and sets the gap_over_bound flag on the total
measure (the single naming size multiplied by the number of
printings), shell ignores that flag and recomputes on the
single naming measure, and the interval from 1,000,001 to
2,000,000 falls between the two measures and reports nothing.
The cure makes the two measures one measure, the total measure
validate already uses, so the gap Warning and the refusal agree
at every size. The controls from the seat 18 paper hold: the
Warning fires at sizes up to exactly 1,000,000, and the refusal
fires at 2,000,001 with the exact measured size stated.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")
shell = h.import_module("shell")

_HEADER = "# Decision Queue\n\n## Open items\n\n"


def _ruled_entry(number, ruling_line):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: Ruled\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"%s\"\n\n"
        "Ruling outcome: The synthetic outcome stands.\n\n"
        "Where the ruling landed: synthetic record.\n\n"
        % (number, number, ruling_line))


def _plain_ruled(number):
    return _ruled_entry(number, "The synthetic ruling stands.")


def _displaces(number, targets_sentence):
    return _ruled_entry(number, targets_sentence)


def _statement(target_phrase):
    return (
        "This ruling displaces %s in full; that earlier ruling "
        "no longer stands as governing on its subject, and %s "
        "is the superseded entry." % (target_phrase[0],
                                      target_phrase[1]))


def _run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def _by_rule(output, rule_text):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "")
            == rule_text]


def _pointers(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return [h.text_of(p) for p in h.as_list(
        h.get(entry, "supersession_pointers"))]


def _cycle_warnings(output):
    return [f for f in _by_rule(output, "PIN-10")
            if h.finding_severity(f) == "Warning"
            and "cycle" in (h.finding_statement(f) or "")]


def _cycle_sets(output):
    sets = []
    for finding in _cycle_warnings(output):
        named = h.get(finding, "named_entries")
        if named:
            sets.append(tuple(h.text_of(item) for item in
                              h.as_list(named)))
        else:
            statement = h.finding_statement(finding) or ""
            sets.append(tuple(part.strip() for part in
                              statement.split("among", 1)[1]
                              .split(":", 1)[0].split(",")))
    return sets


def _not_recognised_notes(output):
    return [f for f in _by_rule(output, "PIN-10")
            if h.finding_severity(f) == "Note"
            and "not recognised" in (h.finding_statement(f) or "")]


class Ch17DiamondCycleTest(unittest.TestCase):
    """Finding 1 of seat 9, first construction (case A1)."""

    def _diamond(self):
        return (_HEADER
                + _displaces(1, _statement((
                    "the rulings at DQ-002 and DQ-003",
                    "DQ-002 and DQ-003 are the superseded "
                    "entries")))
                + _displaces(2, _statement((
                    "the ruling at DQ-004", "DQ-004")))
                + _displaces(3, _statement((
                    "the ruling at DQ-004", "DQ-004")))
                + _displaces(4, _statement((
                    "the ruling at DQ-001", "DQ-001"))))

    def test_diamond_takes_two_cycle_warnings(self):
        output = _run_text(self._diamond())
        sets = _cycle_sets(output)
        self.assertEqual(len(sets), 2)
        self.assertIn(("DQ-001", "DQ-002", "DQ-004"),
                      [tuple(sorted(s)) and s for s in sets])
        named_sets = sorted(tuple(sorted(s)) for s in sets)
        self.assertEqual(named_sets, [
            ("DQ-001", "DQ-002", "DQ-004"),
            ("DQ-001", "DQ-003", "DQ-004")])

    def test_diamond_validate_and_render_agree_on_cycles(self):
        output = _run_text(self._diamond())
        rendered = h.render_text(output, "render")
        self.assertIn(
            "DQ-001 -> DQ-004 -> DQ-002 -> DQ-001 (cycle)",
            rendered)
        self.assertIn(
            "DQ-001 -> DQ-004 -> DQ-003 -> DQ-001 (cycle)",
            rendered)
        self.assertEqual(len(_cycle_warnings(output)), 2)


class Ch17SharedTailCycleTest(unittest.TestCase):
    """Finding 1 of seat 9, second construction (case A4)."""

    def _shared_tail(self):
        return (_HEADER
                + _displaces(1, _statement((
                    "the ruling at DQ-002", "DQ-002")))
                + _displaces(2, _statement((
                    "the rulings at DQ-003 and DQ-004",
                    "DQ-003 and DQ-004 are the superseded "
                    "entries")))
                + _displaces(3, _statement((
                    "the ruling at DQ-005", "DQ-005")))
                + _displaces(4, _statement((
                    "the ruling at DQ-005", "DQ-005")))
                + _displaces(5, _statement((
                    "the ruling at DQ-002", "DQ-002"))))

    def test_shared_tail_takes_two_cycle_warnings(self):
        output = _run_text(self._shared_tail())
        named_sets = sorted(tuple(sorted(s))
                            for s in _cycle_sets(output))
        self.assertEqual(named_sets, [
            ("DQ-002", "DQ-003", "DQ-005"),
            ("DQ-002", "DQ-004", "DQ-005")])

    def test_shared_tail_render_prints_both_cycles(self):
        output = _run_text(self._shared_tail())
        rendered = h.render_text(output, "render")
        self.assertIn(
            "DQ-002 -> DQ-005 -> DQ-003 -> DQ-002 (cycle)",
            rendered)
        self.assertIn(
            "DQ-002 -> DQ-005 -> DQ-004 -> DQ-002 (cycle)",
            rendered)
        self.assertEqual(len(_cycle_warnings(output)), 2)


class Ch17CycleCliExitTest(unittest.TestCase):
    """The cycle constructions at the CLI surface the seat 9
    paper measured: both subcommands exit 1, the exit the
    warned cycles carry."""

    def test_diamond_and_shared_tail_exit_1_on_both(self):
        texts = (
            Ch17DiamondCycleTest()._diamond(),
            Ch17SharedTailCycleTest()._shared_tail())
        for text in texts:
            path = h.temp_input(text.encode("utf-8"))
            for subcommand in ("validate", "render"):
                with self.subTest(subcommand=subcommand):
                    code, _out, _err = h.run_cli(
                        subcommand, path)
                    self.assertEqual(code, 1)


class Ch17CycleControlsTest(unittest.TestCase):
    """Controls from the seat 9 paper: the figure eight and the
    disjoint cycles already take one Warning per cycle. These
    pass before and after the cure."""

    def test_figure_eight_takes_two_cycle_warnings(self):
        text = (_HEADER
                + _displaces(1, _statement((
                    "the rulings at DQ-002 and DQ-003",
                    "DQ-002 and DQ-003 are the superseded "
                    "entries")))
                + _displaces(2, _statement((
                    "the ruling at DQ-001", "DQ-001")))
                + _displaces(3, _statement((
                    "the ruling at DQ-001", "DQ-001"))))
        output = _run_text(text)
        self.assertEqual(len(_cycle_warnings(output)), 2)

    def test_two_disjoint_cycles_take_two_warnings(self):
        text = (_HEADER
                + _displaces(1, _statement((
                    "the ruling at DQ-002", "DQ-002")))
                + _displaces(2, _statement((
                    "the ruling at DQ-001", "DQ-001")))
                + _displaces(3, _statement((
                    "the ruling at DQ-004", "DQ-004")))
                + _displaces(4, _statement((
                    "the ruling at DQ-003", "DQ-003"))))
        output = _run_text(text)
        self.assertEqual(len(_cycle_warnings(output)), 2)


class Ch17IdentifiedPlusVariantTest(unittest.TestCase):
    """Finding 2 of seat 9 (case C1): the identified target
    named again in a case variant in the same statement."""

    def test_no_not_recognised_note_for_the_identified_target(self):
        text = (_HEADER + _plain_ruled(1) + _ruled_entry(
            2,
            "This ruling displaces the ruling at DQ-001 in "
            "full; that earlier ruling no longer stands as "
            "governing on its subject, and dq-001 is the "
            "superseded entry."))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-002"])
        self.assertEqual(_not_recognised_notes(output), [])


class Ch17ParagraphSplitNearMissTest(unittest.TestCase):
    """F-11R2-03 of seat 11 (case a10e): a supersession
    statement split across a paragraph break inside its quoted
    ruling text takes the near miss Note and no pointer."""

    _TEXT = (
        "# Decision queue\n\n"
        "### DQ-001: Open one\n\n"
        "Status: Banked\n\n"
        "Question: Which option should we take?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked.\n\n"
        "Blocks: DQ-002\n\n"
        "This question is waiting for a decision.\n\n"
        "### DQ-002: Ruled one\n\n"
        "Status: RULED, closed\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"The ferry runs.\"\n\n"
        "Ruling outcome: The ferry runs daily.\n\n"
        "Where the ruling landed: the harbour file.\n\n"
        "### DQ-003: Ruled two\n\n"
        "Status: RULED, closed\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"This ruling supersedes\n\n"
        "the ruling at DQ-002.\"\n\n"
        "Ruling outcome: It runs.\n\n"
        "Where the ruling landed: harbour file.\n")

    def test_paragraph_split_statement_takes_one_note(self):
        output = _run_text(self._TEXT)
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        blob = (h.finding_evidence_text(notes[0]) + " "
                + (h.finding_statement(notes[0]) or ""))
        self.assertIn("DQ-002", blob)
        self.assertEqual(_pointers(output, "DQ-002"), [])


def _gap_entry(number, title):
    return (
        "### DQ-%d: %s\n\n"
        "Status: Banked\n\n"
        "This question is waiting for a decision.\n\n"
        "Question: Which option should we take?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked.\n\n"
        "Blocks: DQ-999\n\n" % (number, title))


def _gap_text(low, high):
    return ("# Decision queue\n\n"
            + _gap_entry(low, "Gap low")
            + _gap_entry(high, "Gap high"))


# The seat 18 constructions, by present numbers, with the
# single naming size each stands at.
_GAP_CASES = (
    (857144, 1000002, 1000000),
    (857145, 1000003, 1000001),
    (714287, 1000002, 1999999),
    (714288, 1000003, 2000000),
    (714289, 1000004, 2000001),
)


class Ch18ConstructionTest(unittest.TestCase):
    """Construction facts: the present number pairs stand at
    the single naming sizes the seat 18 paper states. This
    passes before and after the cure."""

    def test_construction_sizes(self):
        for low, high, size in _GAP_CASES:
            with self.subTest(size=size):
                self.assertEqual(
                    validate._gap_naming_size([low, high]), size)


class Ch18ValidateMeasureTest(unittest.TestCase):
    """The validate side of the one measure: the gap class
    fires where the total measure stands at or under the
    bound, and the over bound flag stands where it does not.
    These pass before the cure on the validate side; the
    disagreement the finding charges is on the shell side."""

    def test_warning_and_flag_at_exactly_one_million(self):
        output = _run_text(_gap_text(857144, 1000002))
        over = h.get(output, "gap_naming_over_bound",
                     "gap_over_bound")
        self.assertEqual(over, False)
        statements = [h.finding_statement(f) or ""
                      for f in h.findings_of(output)]
        self.assertTrue(any("Entry numbers missing" in s
                            for s in statements))

    def test_flag_and_no_gap_finding_above_one_million(self):
        output = _run_text(_gap_text(857145, 1000003))
        over = h.get(output, "gap_naming_over_bound",
                     "gap_over_bound")
        self.assertEqual(over, True)
        statements = [h.finding_statement(f) or ""
                      for f in h.findings_of(output)]
        self.assertFalse(any("Entry numbers missing" in s
                             for s in statements))


class Ch18ShellAgreementTest(unittest.TestCase):
    """The shell side of the one measure, run through the CLI
    on both subcommands: the refusal follows the same total
    measure as the validate suppression, so no size in the
    interval reports nothing."""

    def _run(self, low, high, subcommand):
        path = h.temp_input(
            _gap_text(low, high).encode("utf-8"))
        code, out, err = h.run_cli(subcommand, path)
        return code, out.decode("utf-8", "replace"), \
            err.decode("utf-8", "replace")

    def test_warning_fires_at_exactly_one_million(self):
        # The validate form prints the gap naming; the render
        # form does not print the naming, and its agreement
        # surface is the exit code and the rule 1 finding count
        # in its reconciliation.
        code, out, _err = self._run(857144, 1000002, "validate")
        self.assertEqual(code, 1)
        self.assertIn("Entry numbers missing", out)
        code, out, _err = self._run(857144, 1000002, "render")
        self.assertEqual(code, 1)
        self.assertIn("Findings per rule: 1: 1", out)

    def test_interval_sizes_take_the_refusal(self):
        for low, high, size in _GAP_CASES[1:4]:
            for subcommand in ("validate", "render"):
                with self.subTest(size=size,
                                  subcommand=subcommand):
                    code, out, err = self._run(
                        low, high, subcommand)
                    self.assertEqual(code, 3)
                    self.assertEqual(out, "")
                    self.assertIn("Gap naming size limit", err)
                    self.assertIn(str(size), err)
                    self.assertIn(str(size * 2), err)

    def test_refusal_at_two_million_and_one_exact_size(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err = self._run(
                    714289, 1000004, subcommand)
                self.assertEqual(code, 3)
                self.assertEqual(out, "")
                self.assertIn("Gap naming size limit", err)
                self.assertIn("2000001", err)


if __name__ == "__main__":
    unittest.main()
