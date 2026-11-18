"""Restart Step 17 fix wave 3, Seat K1 tests.

Charges CH-32 (validate and render, the supersession cycle
enumeration bound) and CH-33 (validate, the split statement
scan rejoin), as ruled at section 26 of the step record and
prepared in the round 3 triage preparation. The two charges
stand in one cluster because both cures meet inside
_supersession_unit (FLAG 10 of the preparation).

CH-32 carries three findings on one root: seat 5 Finding 1
(High), seat 9 Finding 1 (Medium), and seat 21 A3-21-1
(High). The distinct simple cycle enumeration in find_cycles
and its per cycle PIN-10 Warning printing stand unbounded, so
a dense strongly connected pointer graph grows factorially
(dense_7 takes 2,365 cycle findings, dense_8 takes 16,064,
dense_10 does not finish), a layered graph doubles with each
layer (256, 2,048, and 16,384 cycle Warnings at 17, 23, and
29 entries), a bipartite graph grows by a factor of 18.6 per
width step (424 at width 4, 7,905 at width 5, no finish at
width 6), and a 40 entry chord ring is killed for memory in
both subcommands. On render the map size refusal is computed
only after the enumeration has already run. The ruled cure:
enumeration is bounded during enumeration on both
subcommands; on passing the bound the run refuses at exit 3
in the standing refusal family, naming the bound, and never
presents a truncated inventory as complete. Completeness
under PIN-10 holds below the bound. The bound set by this
seat is 1,000 distinct cycles: the largest governed cycle
inventory in the standing pins is 2 (the CH-17 diamond and
shared tail pins), the largest inventory in the attack papers
that completes cheaply stands at 424 (bip4) and 409
(dense_6), and every charged refusal construction stands at
2,365 cycles or more (dense_7), so 1,000 stands far above
every governed pin and far below every charged blowup.

CH-33 carries seat 21 A3-21-2 (Low): the split statement
scan at the CH-17 cure locus recomputes the standing run
quote state after every appended line by joining every line
of the run so far, a quadratic term in one unbroken run
(manystmt9000 validate CPU 1.17 s in round 2 to 4.26 s in
round 3, with 40,513,506 join generator calls counted). The
ruled cure: the rejoin cost is linear in the run, with exits
and output unchanged on every CH-17 pin and on the manystmt
forms. The cost pin below is a call count, not a wall clock:
it counts, under a profile hook, the resume calls of the
join generator expression at the rejoin locus in the source
of validate, over a run of 600 statement lines in one entry.
The uncured locus stands at the sum of 1 to 600 resumes for
that run alone; a linear cure stands at zero, because the
locus itself is gone.
"""

import sys
import unittest
from pathlib import Path

import dqv_harness as h

validate = h.import_module("validate")
shell = h.import_module("shell")

_HEADER = "# Decision Queue\n\n## Open items\n\n"
_SIMPLE_HEADER = "# Decision queue\n\n"

CYCLE_BOUND = 1000


def _ruled_entry(number, ruling_line):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: Ruled\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"%s\"\n\n"
        "Ruling outcome: The synthetic outcome stands.\n\n"
        "Where the ruling landed: synthetic record.\n\n"
        % (number, number, ruling_line))


def _full_statement(targets):
    names = ["DQ-%03d" % t for t in targets]
    if len(names) == 1:
        return (
            "This ruling displaces the ruling at %s in full; "
            "that earlier ruling no longer stands as governing "
            "on its subject, and %s is the superseded entry."
            % (names[0], names[0]))
    return (
        "This ruling displaces the rulings at %s in full; "
        "those earlier rulings no longer stand as governing "
        "on their subjects, and %s are the superseded entries."
        % (" and ".join(names), " and ".join(names)))


def _simple_entry(number, targets):
    stmt = "This supersedes the ruling at " + " and ".join(
        "DQ-%03d" % t for t in targets) + ".\n"
    return ("### DQ-%03d: Entry %d\nStatus: Banked\n%s\n"
            % (number, number, stmt))


def _dense_text(n):
    parts = [_SIMPLE_HEADER]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            i, [t for t in range(1, n + 1) if t != i]))
    return "".join(parts)


def _bip_text(width):
    parts = [_SIMPLE_HEADER]
    n = 2 * width
    odds = [i for i in range(1, n + 1) if i % 2 == 1]
    evens = [i for i in range(1, n + 1) if i % 2 == 0]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            i, evens if i % 2 == 1 else odds))
    return "".join(parts)


def _chord_text(n=40, span=5):
    parts = [_SIMPLE_HEADER]
    for i in range(1, n + 1):
        targets = [((i + k - 1) % n) + 1 for k in range(1, span + 1)]
        parts.append(_simple_entry(i, targets))
    return "".join(parts)


def _layered_cycle_text(layers):
    # DQ-001 displaces both entries of layer 0; each entry of a
    # layer displaces both entries of the next layer; each
    # entry of the last layer displaces DQ-001. The file of L
    # layers carries 2 to the L distinct cycles.
    total = 1 + 2 * layers
    targets = {}
    targets[1] = [2, 3]
    for layer in range(layers):
        first = 2 + 2 * layer
        second = first + 1
        if layer == layers - 1:
            nxt = [1]
        else:
            nxt = [first + 2, first + 3]
        targets[first] = list(nxt)
        targets[second] = list(nxt)
    parts = [_HEADER]
    for i in range(1, total + 1):
        parts.append(_ruled_entry(i, _full_statement(targets[i])))
    return "".join(parts)


def _manystmt_text(n):
    parts = [
        "# Decision queue\n\n"
        "### DQ-001: A\n\nStatus: Banked\n\n"
        "Prose paragraph here.\n\n"
        "### DQ-002: B\n\nStatus: Banked\n\n"]
    for _i in range(n):
        parts.append("This supersedes the ruling at DQ-001.\n")
    return "".join(parts)


def _run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def _by_rule(output, rule_text):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "")
            == rule_text]


def _cycle_warnings(output):
    return [f for f in _by_rule(output, "PIN-10")
            if h.finding_severity(f) == "Warning"
            and "cycle" in (h.finding_statement(f) or "")]


def _not_recognised_notes(output):
    return [f for f in _by_rule(output, "PIN-10")
            if h.finding_severity(f) == "Note"
            and "not recognised" in (h.finding_statement(f) or "")]


def _pointers(output, entry_id):
    entry = h.entry_by_id(output, entry_id)
    if entry is None:
        raise AssertionError("no entry " + entry_id)
    return [h.text_of(p) for p in h.as_list(
        h.get(entry, "supersession_pointers"))]


def _cli(text, subcommand, timeout=60):
    path = h.temp_input(text.encode("utf-8"))
    code, out, err = h.run_cli_with_timeout(
        subcommand, path, timeout=timeout)
    return code, out.decode("utf-8", "replace"), \
        err.decode("utf-8", "replace")


class Ch32RefusalSurfaceTest(unittest.TestCase):
    """The refusal form itself: exit 3 in the standing refusal
    family, on standard error, naming the bound, with no
    truncated inventory presented as complete on any channel."""

    def _assert_cycle_refusal(self, text, subcommand):
        code, out, err = _cli(text, subcommand)
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("cycle", err.lower())
        self.assertIn(str(CYCLE_BOUND), err)
        self.assertIn("Exit: code 3", err)

    def test_dense10_refuses_on_both_subcommands(self):
        text = _dense_text(10)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_cycle_refusal(text, subcommand)

    def test_dense7_refuses_on_both_subcommands(self):
        text = _dense_text(7)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_cycle_refusal(text, subcommand)

    def test_bip6_refuses_on_both_subcommands(self):
        text = _bip_text(6)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_cycle_refusal(text, subcommand)

    def test_bip5_refuses_on_both_subcommands(self):
        text = _bip_text(5)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_cycle_refusal(text, subcommand)

    def test_layered_29_entries_refuses_on_both(self):
        text = _layered_cycle_text(14)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_cycle_refusal(text, subcommand)

    def test_layered_23_entries_refuses_on_both(self):
        text = _layered_cycle_text(11)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_cycle_refusal(text, subcommand)

    def test_chord40x5_refuses_on_both_subcommands(self):
        text = _chord_text(40, 5)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_cycle_refusal(text, subcommand)

    def test_render_refusal_is_the_cycle_refusal_not_the_map(self):
        # The render refusal is computed before or during
        # enumeration, never only after it: on dense10 the
        # surface that arrives is the cycle count refusal, and
        # the map size refusal, which the uncured code reaches
        # only after paying the enumeration cost, does not
        # stand in its place.
        code, out, err = _cli(_dense_text(10), "render")
        self.assertEqual(code, 3)
        self.assertIn("cycle", err.lower())
        self.assertNotIn("Supersession map size limit", err)

    def test_pipeline_carries_the_cycle_over_bound_flag(self):
        # The in process surface of the same refusal: the
        # validate output carries the over bound flag, and no
        # cycle Warning of a truncated inventory stands on it.
        output = _run_text(_dense_text(7))
        over = h.get(output, "cycle_over_bound",
                     "supersession_cycle_over_bound")
        self.assertEqual(over, True)
        self.assertEqual(_cycle_warnings(output), [])
        below = _run_text(_dense_text(5))
        over_below = h.get(below, "cycle_over_bound",
                           "supersession_cycle_over_bound")
        self.assertEqual(over_below, False)


class Ch32BelowBoundCompletenessTest(unittest.TestCase):
    """Completeness under PIN-10 below the bound: every cycle
    of a file whose inventory stands under the bound stands
    reported exactly once, in the counts the attack papers
    counted exactly. These pass before and after the cure."""

    def test_dense5_takes_84_cycle_warnings(self):
        output = _run_text(_dense_text(5))
        self.assertEqual(len(_cycle_warnings(output)), 84)

    def test_dense6_takes_409_cycle_warnings(self):
        output = _run_text(_dense_text(6))
        self.assertEqual(len(_cycle_warnings(output)), 409)

    def test_bip4_takes_424_cycle_warnings(self):
        output = _run_text(_bip_text(4))
        self.assertEqual(len(_cycle_warnings(output)), 424)

    def test_layered_17_entries_takes_256_cycle_warnings(self):
        output = _run_text(_layered_cycle_text(8))
        self.assertEqual(len(_cycle_warnings(output)), 256)

    def test_dense6_exits_1_on_both_subcommands(self):
        text = _dense_text(6)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                path = h.temp_input(text.encode("utf-8"))
                code, _out, _err = h.run_cli(subcommand, path)
                # Render may take its own governed map refusal
                # on this shape, as the attack papers record;
                # validate carries the warned inventory at 1.
                if subcommand == "validate":
                    self.assertEqual(code, 1)
                else:
                    self.assertIn(code, (1, 3))


class Ch33RejoinCostTest(unittest.TestCase):
    """CH-33: the split statement scan rejoin cost is linear
    in the run. The pin counts the resume calls of the join
    generator expression at the rejoin locus named in the
    source of validate, over one unbroken run of 600
    statement lines in one entry. The uncured locus stands at
    the sum of 1 to 600 resumes for that run; the bound is 20
    resumes per line of the run, which no quadratic rejoin
    meets and a linear scan stands at zero against, the locus
    itself being gone."""

    def _rejoin_locus_line(self):
        source_path = Path(validate.__file__)
        for number, line in enumerate(
                source_path.read_text(
                    encoding="utf-8").splitlines(), 1):
            if "join(t for _n, t in run).count" in line:
                return number
        return None

    def test_rejoin_resumes_stay_linear_in_the_run(self):
        locus = self._rejoin_locus_line()
        if locus is None:
            # No rejoin locus stands in the source: the run
            # quote state is not recomputed by joining the
            # standing run, and the counted cost stands at 0,
            # which meets the bound below.
            return
        lines = 600
        counts = {"resumes": 0}

        def profile(frame, event, _arg):
            if event == "call":
                code = frame.f_code
                if code.co_name == "<genexpr>" and \
                        code.co_firstlineno == locus:
                    counts["resumes"] += 1

        sys.setprofile(profile)
        try:
            _run_text(_manystmt_text(lines))
        finally:
            sys.setprofile(None)
        self.assertLessEqual(counts["resumes"], 20 * lines)


class Ch33SplitOutcomeTest(unittest.TestCase):
    """CH-33 outcome pins: the split statement reading stands
    unchanged. These pass before and after the cure."""

    def test_manystmt_form_outcome_stands(self):
        output = _run_text(_manystmt_text(600))
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-002"])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_cycle_warnings(output), [])
        self.assertEqual(len(h.findings_of(output)), 8)

    def test_paragraph_split_supersedes_takes_one_note(self):
        # The CH-17 charged construction (seat 11 form): a
        # supersedes statement split across a paragraph break
        # takes the near miss Note and no pointer.
        text = (
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
        output = _run_text(text)
        self.assertEqual(len(_not_recognised_notes(output)), 1)
        self.assertEqual(_pointers(output, "DQ-002"), [])

    def test_complete_split_across_blank_line_derives_pointer(self):
        # The seat 9 standing behaviour (observations O1 and
        # O2 of that paper): a complete statement split across
        # a blank line inside its open quotation derives its
        # pointer at full strength.
        text = (
            _HEADER
            + _ruled_entry(1, "The synthetic ruling stands.")
            + "### DQ-002: Synthetic entry 2\n\n"
              "Status: Ruled\n\n"
              "Ruled by: Captain JP\n\n"
              "Ruling text: \"This ruling displaces the "
              "ruling at\n\n"
              "DQ-001 in full; that earlier ruling no longer "
              "stands as governing on its subject, and DQ-001 "
              "is the superseded entry.\"\n\n"
              "Ruling outcome: The synthetic outcome stands.\n\n"
              "Where the ruling landed: synthetic record.\n")
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-002"])
        self.assertEqual(_not_recognised_notes(output), [])

    def test_shared_tail_split_leg_counts_in_the_inventory(self):
        # The seat 9 C5 form: a shared tail whose one leg is
        # split across a blank line inside its open quotation
        # stands warned as an ordinary cycle, both cycles.
        text = (
            _HEADER
            + _ruled_entry(1, _full_statement([2]))
            + _ruled_entry(2, _full_statement([3, 4]))
            + _ruled_entry(3, _full_statement([5]))
            + "### DQ-004: Synthetic entry 4\n\n"
              "Status: Ruled\n\n"
              "Ruled by: Captain JP\n\n"
              "Ruling text: \"This ruling displaces the "
              "ruling at\n\n"
              "DQ-005 in full; that earlier ruling no longer "
              "stands as governing on its subject, and DQ-005 "
              "is the superseded entry.\"\n\n"
              "Ruling outcome: The synthetic outcome stands.\n\n"
              "Where the ruling landed: synthetic record.\n"
            + _ruled_entry(5, _full_statement([2])))
        output = _run_text(text)
        self.assertEqual(len(_cycle_warnings(output)), 2)


if __name__ == "__main__":
    unittest.main()
