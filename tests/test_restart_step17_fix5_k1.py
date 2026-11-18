"""Restart Step 17 fix wave 5, Seat K1 tests.

Charges CH-74, CH-75, and CH-93, as ruled at section 52 of
design/steps/step-17r-record.md (rulings (b), (e), and (i))
and prepared in design/steps/step-17r-triage5-prep.md. The
three charges stand in one function territory in validate,
the supersession and cycle reading.

CH-74 (ruling (b)): the CH-52 work accounting charges a
simple cycle once per start entry of its component, so a
ring of n entries pays the sum of its suffix lengths and
the governed ring of 2,400 entries, carrying exactly one
distinct cycle, takes the work refusal at exit 3 where
rounds 2 to 4 record it completing at exit 1. The ruled
cure restates the accounting so a simple cycle is charged
for its distinct cycle once: work spent re-traversing a
cycle the enumeration has already recorded, from a later
start, is charged to that recorded cycle and not counted
again, while dead path work, paths that follow no recorded
cycle, is counted per examination as before. The complete
inventory duty below the count bound stands unmoved, the
named funnel and wall families of the fix wave 4 K1 tables
keep refusing at their bounds, and PIN-10 cycle counts
stand untouched.

CH-75 (ruling (e)): the supersession target list reading
in _identifications is quadratic in the number of distinct
targets one statement names: the two list first patterns
match at every suffix of a long list with full
backtracking, and the collected identifications are
deduplicated by list membership. The cure reads the list
standing before each list first tail once, scanning
backwards from the tail in time standing in the length of
the list, and deduplicates by a set. The identifications
returned stand exact. The F1 shaped limb of the finding
stands FLAG under ruling (e): no test here builds that
form, and the cost tests stand on the exit 1 prose target
forms. Cost figures in these tests are measurements with
wide bounds, never verdicts on a figure: the bounds stand
at a small multiple of the cured measurements and a small
fraction of the uncured ones, as the K1 paper records.

CH-93 (ruling (i)): a semicolon separated target list
derives pointers for its first and last targets only, and
the middle targets are dropped silently. The cure is
signal only: the middle targets take the not recognised
signal, a headed middle target in the not recognised Note
and a ghost middle target under PD-R7, on the standing
forms. The CH-64 joiner set stands unmoved and no
derivation widens.
"""

import time
import unittest

import dqv_harness as h

validate = h.import_module("validate")
shell = h.import_module("shell")

_HEADER = "# Decision Queue\n\n## Open items\n\n"
_SIMPLE_HEADER = "# Decision queue\n\n"

WORK_BOUND = getattr(validate, "_CYCLE_WORK_BOUND", None)
COUNT_BOUND = 1000


def _ruled_entry(number, ruling_line):
    return (
        "### DQ-%03d: Synthetic entry %d\n\n"
        "Status: Ruled\n\n"
        "Ruled by: Captain JP\n\n"
        "Ruling text: \"%s\"\n\n"
        "Ruling outcome: The synthetic outcome stands.\n\n"
        "Where the ruling landed: synthetic record.\n\n"
        % (number, number, ruling_line))


def _and_join(names):
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


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


def _comma_statement(targets):
    names = ["DQ-%03d" % t for t in targets]
    joined = _and_join(names)
    if len(names) == 1:
        return (
            "This ruling displaces the ruling at %s in full; "
            "that earlier ruling no longer stands as governing "
            "on its subject, and %s is the superseded entry."
            % (joined, joined))
    return (
        "This ruling displaces the rulings at %s in full; "
        "those earlier rulings no longer stand as governing "
        "on their subjects, and %s are the superseded entries."
        % (joined, joined))


def _semicolon_statement(targets):
    names = "; ".join("DQ-%03d" % t for t in targets)
    return (
        "This ruling displaces the rulings at %s in full; "
        "those earlier rulings no longer stand as governing "
        "on their subjects, and %s are the superseded entries."
        % (names, names))


def _simple_entry(number, targets):
    stmt = "This supersedes the ruling at " + " and ".join(
        "DQ-%03d" % t for t in targets) + ".\n"
    return ("### DQ-%03d: Entry %d\nStatus: Banked\n%s\n"
            % (number, number, stmt))


def _dense_text(n, base=0):
    parts = [_SIMPLE_HEADER]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            base + i,
            [base + t for t in range(1, n + 1) if t != i]))
    return "".join(parts)


def _multi_dense_text(k):
    parts = [_SIMPLE_HEADER]
    for c in range(k):
        for i in range(1, 7):
            n = c * 100 + i
            parts.append(_simple_entry(
                n, [c * 100 + t for t in range(1, 7) if t != i]))
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


def _layered_cycle_text(layers):
    total = 1 + 2 * layers
    targets = {1: [2, 3]}
    for layer in range(layers):
        first = 2 + 2 * layer
        second = first + 1
        nxt = [1] if layer == layers - 1 else [first + 2, first + 3]
        targets[first] = list(nxt)
        targets[second] = list(nxt)
    parts = [_HEADER]
    for i in range(1, total + 1):
        parts.append(_ruled_entry(i, _full_statement(targets[i])))
    return "".join(parts)


def _funnel_text(m):
    edges = {1: [2], 2: [1, 3]}
    for k in range(1, m + 1):
        num = k + 2
        edges[num] = [j + 2 for j in range(k + 1, m + 1)] + [2]
    parts = [_SIMPLE_HEADER]
    for i in range(1, m + 3):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _wall_text(w, layers):
    per = w + 3

    def sp(lay, k):
        return (lay - 1) * per + k

    def bush(lay, j):
        return (lay - 1) * per + w + j

    sid = layers * per + 1
    tid = layers * per + 2
    edges = {}
    for lay in range(1, layers + 1):
        for k in range(1, w + 1):
            edges[sp(lay, k)] = (
                [sp(lay + 1, k)] if lay < layers else [tid])
        nxt = ([bush(lay + 1, j) for j in (1, 2, 3)]
               if lay < layers else [tid])
        for j in (1, 2, 3):
            edges[bush(lay, j)] = list(nxt)
    edges[tid] = [sid]
    edges[sid] = [bush(1, 1)] + [sp(1, k) for k in range(1, w + 1)]
    parts = [_SIMPLE_HEADER]
    for i in range(1, tid + 1):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _detour_text(layers):
    def nid(lay, k):
        return (lay - 1) * 5 + k + 1

    sid = layers * 5 + 1
    tid = layers * 5 + 2
    edges = {}
    for lay in range(1, layers + 1):
        a, b, c, d, e = (nid(lay, k) for k in range(5))
        if lay < layers:
            na, nb, nc, nd, ne = (nid(lay + 1, k) for k in range(5))
            edges[a] = [na]
            edges[b] = [na, nb, nc]
            edges[c] = [na, nb, nc, nd, ne]
            edges[d] = [nb, nc, nd, ne]
            edges[e] = [nb, nc, nd, ne]
        else:
            for node in (a, b, c, d, e):
                edges[node] = [tid]
    edges[tid] = [sid]
    edges[sid] = [nid(1, 2), nid(1, 0), nid(1, 1)]
    parts = [_SIMPLE_HEADER]
    for i in range(1, tid + 1):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _ring_text(n):
    parts = [_SIMPLE_HEADER]
    for i in range(1, n + 1):
        parts.append(_simple_entry(i, [i - 1 if i > 1 else n]))
    return "".join(parts)


def _prose_fan_text(target_count, fan_count):
    parts = [_SIMPLE_HEADER]
    for i in range(1, target_count + 1):
        parts.append(
            "### DQ-%03d: Entry %d\nStatus: Banked\n"
            "This entry asks whether the queue should adopt "
            "option %d for the shared record, with two named "
            "options and a stated cost of deciding late, and "
            "it blocks nothing.\n\n" % (i, i, i))
    stmt = "This supersedes " + ", ".join(
        "DQ-%03d" % i for i in range(1, target_count + 1)) + ".\n"
    for f in range(1, fan_count + 1):
        parts.append("### DQ-%03d: Fan %d\nStatus: Banked\n%s\n"
                     % (target_count + f, f, stmt))
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


def _pd_r7_notes(output):
    return _by_rule(output, "PD-R7")


def _named_entries(finding):
    return [h.text_of(x) for x in h.as_list(
        h.get(finding, "named_entries", "named_entry_ids"))]


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


def _work_over(output):
    return h.get(output, "cycle_work_over_bound",
                 "supersession_cycle_work_over_bound")


def _count_over(output):
    return h.get(output, "cycle_over_bound",
                 "supersession_cycle_over_bound")


def _work_measured(output):
    return h.get(output, "cycle_work_measured",
                 "supersession_cycle_work_measured")


class Ch74CycleAccountingTest(unittest.TestCase):
    """CH-74: a simple cycle is charged for its distinct
    cycle once. The governed ring completes with its one
    cycle, the named funnel and wall families keep refusing
    at their bounds, and every governed inventory and count
    refusal stands exactly as before."""

    def _assert_work_refusal(self, text, subcommand, timeout=60):
        self.assertIsNotNone(WORK_BOUND)
        code, out, err = _cli(text, subcommand, timeout=timeout)
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("work limit", err.lower())
        self.assertIn(str(WORK_BOUND), err)
        self.assertIn("Exit: code 3", err)

    def _assert_count_refusal(self, text, subcommand):
        code, out, err = _cli(text, subcommand)
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("cycle count limit", err.lower())
        self.assertIn(str(COUNT_BOUND), err)
        self.assertNotIn("work limit", err.lower())
        self.assertIn("Exit: code 3", err)

    def test_ring_2400_completes_with_its_one_cycle(self):
        output = _run_text(_ring_text(2400))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_ring_cycle_is_charged_once_for_its_cycle(self):
        # The accounting test of the charge: the work the
        # enumeration charges for a ring of n entries
        # carrying exactly one distinct cycle is the length
        # of that cycle, charged once, not the sum of the
        # suffix lengths over every start.
        for n in (1200, 1300, 2400):
            with self.subTest(n=n):
                output = _run_text(_ring_text(n))
                self.assertEqual(len(_cycle_warnings(output)), 1)
                self.assertEqual(_work_measured(output), n)

    def test_ring_2400_cli_completes_on_both_subcommands(self):
        text = _ring_text(2400)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err = _cli(text, subcommand, timeout=60)
                self.assertEqual(code, 1)
                self.assertNotIn("work limit", err.lower())
                self.assertNotIn("cycle count limit", err.lower())

    def test_named_family_work_refusals_stand(self):
        text = _funnel_text(20)
        for subcommand in ("validate", "render"):
            with self.subTest(case="funnel20",
                              subcommand=subcommand):
                self._assert_work_refusal(text, subcommand)
        text = _wall_text(200, 8)
        for subcommand in ("validate", "render"):
            with self.subTest(case="wall8", subcommand=subcommand):
                self._assert_work_refusal(text, subcommand)
        self._assert_work_refusal(
            _funnel_text(24), "validate", timeout=30)
        self._assert_work_refusal(
            _wall_text(200, 10), "validate", timeout=30)

    def test_governed_inventories_complete_exactly(self):
        cases = [
            ("dense5", _dense_text(5), 84),
            ("dense6", _dense_text(6), 409),
            ("bip4", _bip_text(4), 424),
            ("layered8", _layered_cycle_text(8), 256),
            ("twodense6", _multi_dense_text(2), 818),
            ("detour5", _detour_text(5), 291),
            ("detour6", _detour_text(6), 987),
            ("wall6", _wall_text(200, 6), 443),
            ("funnel9", _funnel_text(9), 257),
            ("funnel6", _funnel_text(6), 33),
        ]
        for name, text, expected in cases:
            with self.subTest(name=name):
                output = _run_text(text)
                self.assertEqual(
                    len(_cycle_warnings(output)), expected)
                self.assertEqual(_work_over(output), False)

    def test_wall6_work_figure_stands_below_the_bound(self):
        output = _run_text(_wall_text(200, 6))
        self.assertEqual(len(_cycle_warnings(output)), 443)
        self.assertLess(_work_measured(output), WORK_BOUND)

    def test_count_refusals_stand_exactly_as_before(self):
        for subcommand in ("validate", "render"):
            with self.subTest(case="threedense6",
                              subcommand=subcommand):
                self._assert_count_refusal(
                    _multi_dense_text(3), subcommand)
        for subcommand in ("validate", "render"):
            with self.subTest(case="dense7", subcommand=subcommand):
                self._assert_count_refusal(
                    _dense_text(7), subcommand)

    def test_detour7_keeps_both_signals_and_the_count_form(self):
        output = _run_text(_detour_text(7))
        self.assertEqual(_count_over(output), True)
        self.assertEqual(_work_over(output), True)
        self._assert_count_refusal(_detour_text(7), "validate")

    def test_wall7_work_refusal_stands_as_named(self):
        # The wall L 7 consequence the fix wave 4 K1 paper
        # names in the open stands unmoved under ruling (b):
        # it is not cured, and it is not charged here as a
        # defect; the test pins that the restated accounting
        # does not silently move it in either direction.
        output = _run_text(_wall_text(200, 7))
        self.assertEqual(_work_over(output), True)
        self.assertEqual(_count_over(output), False)


class Ch75TargetListCostTest(unittest.TestCase):
    """CH-75: the target list reading takes time near
    linear in the targets named, and the identifications
    returned stand exact at every size. Time figures are
    measurements: each bound stands far above the cured
    measurement and far below the uncured one, as the K1
    paper records."""

    def _fan_sentence(self, n):
        return "This supersedes " + ", ".join(
            "DQ-%03d" % i for i in range(1, n + 1)) + "."

    def _two_clause_sentence(self, n):
        lst = ", ".join(
            "DQ-%03d" % i for i in range(1, n)) + \
            " and DQ-%03d" % n
        return (
            "This ruling displaces the rulings at " + lst +
            " in full; those earlier rulings no longer stand "
            "as governing on their subjects, and " + lst +
            " are the superseded entries.")

    def test_identifications_exact_and_near_linear_supersedes(
            self):
        sentence = self._fan_sentence(4200)
        start = time.process_time()
        found = validate._identifications(sentence)
        elapsed = time.process_time() - start
        self.assertEqual(
            found, ["DQ-%03d" % i for i in range(1, 4201)])
        self.assertLess(elapsed, 4.0)

    def test_identifications_exact_and_near_linear_two_clause(
            self):
        sentence = self._two_clause_sentence(4200)
        start = time.process_time()
        found = validate._identifications(sentence)
        elapsed = time.process_time() - start
        self.assertEqual(
            found, ["DQ-%03d" % i for i in range(1, 4201)])
        self.assertLess(elapsed, 4.0)

    def test_identifications_ladder_growth_is_near_linear(self):
        figures = {}
        for n in (1000, 2000, 4000):
            sentence = self._fan_sentence(n)
            start = time.process_time()
            found = validate._identifications(sentence)
            figures[n] = time.process_time() - start
            self.assertEqual(len(found), n)
        # A quadratic reading grows by a factor near 4 per
        # doubling; the cured reading stands near 2. The
        # bound stands between the two growth forms, as a
        # measurement, with the absolute figures recorded
        # in the K1 paper.
        self.assertLess(figures[4000], figures[1000] * 9 + 0.5)

    def test_prose_fan_pipeline_names_every_target(self):
        text = _prose_fan_text(1000, 5)
        start = time.process_time()
        output = _run_text(text)
        elapsed = time.process_time() - start
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 5)
        for note in notes:
            self.assertEqual(len(_named_entries(note)), 1000)
        self.assertLess(elapsed, 5.0)

    def test_identification_forms_stand_exact(self):
        cases = [
            ("This supersedes DQ-007.", ["DQ-007"]),
            ("This ruling displaces the ruling at DQ-007 "
             "in full.", ["DQ-007"]),
            ("This ruling displaces DQ-007 in full.",
             ["DQ-007"]),
            ("DQ-007 is the superseded entry.", ["DQ-007"]),
            ("DQ-007 and DQ-009 are the superseded entries.",
             ["DQ-007", "DQ-009"]),
            ("DQ-007, DQ-009 are the superseded entries.",
             ["DQ-007", "DQ-009"]),
            ("DQ-007 DQ-009 are the superseded entries.",
             ["DQ-009"]),
            ("DQ-007 is the entry it stands in place of.",
             ["DQ-007"]),
            ("It replaces DQ-007 as the governing text.",
             ["DQ-007"]),
            ("This supersedes the ruling at DQ-007 in full.",
             ["DQ-007"]),
            ("The entries DQ-009, DQ-007 and DQ-011 are the "
             "superseded entries.",
             ["DQ-009", "DQ-007", "DQ-011"]),
            ("DQ-007, DQ-009, and DQ-011 are the superseded "
             "entries.", ["DQ-007", "DQ-009", "DQ-011"]),
            ("This supersedes DQ-007, DQ-007 and DQ-009.",
             ["DQ-007", "DQ-009"]),
        ]
        for sentence, expected in cases:
            with self.subTest(sentence=sentence):
                self.assertEqual(
                    validate._identifications(sentence), expected)


class Ch93SemicolonSignalTest(unittest.TestCase):
    """CH-93: a semicolon separated target list takes the
    near miss signal for its middle targets. Signal only:
    the first and last targets keep the pointers the
    standing reading derives, the middle targets take no
    pointer, and the CH-64 joiner set stands unmoved."""

    def _list_file(self, claiming_number, statement, headed):
        total = max([claiming_number] + list(headed))
        parts = [_HEADER]
        for i in range(1, total + 1):
            if i == claiming_number:
                parts.append(_ruled_entry(i, statement))
            else:
                parts.append(_ruled_entry(
                    i, "The harbour ruling stands."))
        return "".join(parts)

    def test_semicolon_list_middle_targets_take_the_signal(
            self):
        text = self._list_file(
            5, _semicolon_statement([1, 2, 3, 4]), [1, 2, 3, 4])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]), ["DQ-002", "DQ-003"])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_semicolon_list_cli_exits_zero_on_both(self):
        text = self._list_file(
            5, _semicolon_statement([1, 2, 3, 4]), [1, 2, 3, 4])
        code, out, err = _cli(text, "validate")
        self.assertEqual(code, 0)
        self.assertIn("not recognised", out)
        self.assertIn("DQ-002", out)
        self.assertIn("DQ-003", out)
        # The render surface carries its findings as counts,
        # in the standing form: the one Note stands there as
        # the one PIN-10 finding, at the same exit.
        code, out, err = _cli(text, "render")
        self.assertEqual(code, 0)
        self.assertIn("Findings per rule: PIN-10: 1", out)

    def test_semicolon_single_clause_signals_unread_targets(
            self):
        statement = (
            "This ruling displaces the rulings at "
            "DQ-001; DQ-002; DQ-003 in full; those earlier "
            "rulings no longer stand as governing on their "
            "subjects.")
        text = self._list_file(5, statement, [1, 2, 3])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]), ["DQ-002", "DQ-003"])

    def test_semicolon_ghost_middle_takes_pd_r7(self):
        text = self._list_file(
            5, _semicolon_statement([1, 999, 2, 3]), [1, 2, 3])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(len(_pd_r7_notes(output)), 1)
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-002"])

    def test_comma_list_control_takes_no_signal(self):
        text = self._list_file(
            5, _comma_statement([1, 2, 3, 4]), [1, 2, 3, 4])
        output = _run_text(text)
        for target in (1, 2, 3, 4):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_clause_semicolon_control_takes_no_signal(self):
        # Semicolons standing between the clauses of a
        # statement, with no two targets joined by one, are
        # the standing prose form: every target derives its
        # pointer and no signal stands.
        text = self._list_file(
            5, _full_statement([1, 2]), [1, 2])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])


if __name__ == "__main__":
    unittest.main()
