"""Restart Step 17 fix wave 6, Seat K1 tests.

Charges CH-104 and CH-113, as ruled at section 58 of
design/steps/step-17r-record.md (rulings (h) and (a)) and
prepared in design/steps/step-17r-triage6-prep.md. The two
charges stand in one function territory in validate, the
supersession reading beside _supersession_unit and the
cycle enumeration.

CH-104 (ruling (h), seat 9 Findings 1 and 2, both Low):
Finding 2, the signal condition limb. The CH-93 near miss
signal stands only for a middle target for which no
pointer stands in the same run from the same entry, in
either statement order; the charged semicolon form with no
other derivation keeps its signal whole. Finding 1, the
joiner signal limb, cured by signal only: the near miss
signal extends to the target lists joined by slash, pipe,
ampersand, and fullwidth semicolon U+FF1B, which today
derive pointers for head and tail only and drop the
middles silently; no pointer is derived for a charged
joiner list, and the CH-64 joiner set stands unmoved. The
condition limb governs every signal the charge produces,
in either limb.

CH-113 (ruling (a), seat 21 A6-21-1, High, a cost charge):
the CH-74 cure restated the charge for re-traversing a
recorded cycle but not the walk, so a simple cycle still
pays the sum of its suffix lengths in descent steps. The
enumeration is restated so a recorded cycle is not
re-walked from each of its starts, bounding the walk
itself, with the inventory, the counts, the refusal
figures, the named funnel and wall family refusals, and
the PIN-10 counts standing exactly as the fix wave 5 K1
paper pins them. Cost and time figures are measurements,
never pass or fail verdicts; no test here pins a time. The
cost failure before the cure and the cost standing after
it are stated as bench measurements in the seat paper.
"""

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


def _joined_statement(targets, joiner):
    names = joiner.join("DQ-%03d" % t for t in targets)
    return (
        "This ruling displaces the rulings at %s in full; "
        "those earlier rulings no longer stand as governing "
        "on their subjects, and %s are the superseded entries."
        % (names, names))


def _semicolon_statement(targets):
    return _joined_statement(targets, "; ")


_JOINERS = {
    "slash": " / ",
    "pipe": " | ",
    "ampersand": " & ",
    "fullwidth_semicolon": "； ",
}


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


def _bip_text(width):
    parts = [_SIMPLE_HEADER]
    n = 2 * width
    odds = [i for i in range(1, n + 1) if i % 2 == 1]
    evens = [i for i in range(1, n + 1) if i % 2 == 0]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            i, evens if i % 2 == 1 else odds))
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


def _compact_ring_text(n):
    # The compact two line form of the round 6 seat 21
    # paper: a heading line and one line carrying the Status
    # and the supersession statement, so the largest ring
    # stands inside the line limit.
    parts = [_SIMPLE_HEADER]
    for i in range(1, n + 1):
        target = i - 1 if i > 1 else n
        parts.append(
            "### DQ-%03d: Entry %d\n"
            "Status: Banked. This supersedes the ruling at "
            "DQ-%03d.\n" % (i, i, target))
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


def _list_file(claiming_number, statement, headed, extra=None,
               second_claiming=None, second_statement=None):
    total = max([claiming_number] + list(headed)
                + ([second_claiming] if second_claiming else []))
    parts = [_HEADER]
    for i in range(1, total + 1):
        if i == claiming_number:
            entry = _ruled_entry(i, statement)
            if extra is not None:
                entry += extra + "\n\n"
            parts.append(entry)
        elif second_claiming is not None and i == second_claiming:
            parts.append(_ruled_entry(i, second_statement))
        else:
            parts.append(_ruled_entry(
                i, "The harbour ruling stands."))
    return "".join(parts)


class Ch104SignalConditionTest(unittest.TestCase):
    """CH-104, the signal condition limb: the CH-93 signal
    stands only for a middle target for which no pointer
    stands in the same run from the same entry, in either
    statement order."""

    def test_semicolon_first_comma_second_takes_no_signal(self):
        text = _list_file(
            5, _semicolon_statement([1, 2, 3, 4]), [1, 2, 3, 4],
            extra=_comma_statement([2, 3]))
        output = _run_text(text)
        for target in (1, 2, 3, 4):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_comma_first_semicolon_second_takes_no_signal(self):
        text = _list_file(
            5, _comma_statement([2, 3]), [1, 2, 3, 4],
            extra=_semicolon_statement([1, 2, 3, 4]))
        output = _run_text(text)
        for target in (1, 2, 3, 4):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_signal_names_only_the_underived_middle(self):
        text = _list_file(
            5, _semicolon_statement([1, 2, 3, 4]), [1, 2, 3, 4],
            extra=_comma_statement([2]))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        self.assertEqual(_pointers(output, "DQ-004"), ["DQ-005"])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-003"])

    def test_charged_semicolon_form_keeps_its_signal_whole(self):
        text = _list_file(
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

    def test_signal_not_suppressed_by_another_entrys_pointer(self):
        # The condition reads on pointers from the same entry:
        # a pointer another entry derives for a middle target
        # does not answer this entry statement, and this entry
        # signal stands.
        text = _list_file(
            5, _semicolon_statement([1, 2, 3, 4]), [1, 2, 3, 4],
            second_claiming=6,
            second_statement=_comma_statement([2, 3]))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-006"])
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-006"])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]), ["DQ-002", "DQ-003"])


class Ch104JoinerSignalTest(unittest.TestCase):
    """CH-104, the joiner signal limb: a target list joined
    by slash, pipe, ampersand, or fullwidth semicolon takes
    the near miss signal for its middle targets, by signal
    only. No pointer derives for a charged joiner list and
    the CH-64 joiner set stands unmoved."""

    def test_joiner_lists_take_the_signal(self):
        for name, joiner in sorted(_JOINERS.items()):
            with self.subTest(joiner=name):
                text = _list_file(
                    5, _joined_statement([1, 2, 3, 4], joiner),
                    [1, 2, 3, 4])
                output = _run_text(text)
                self.assertEqual(
                    _pointers(output, "DQ-001"), ["DQ-005"])
                self.assertEqual(
                    _pointers(output, "DQ-004"), ["DQ-005"])
                self.assertEqual(_pointers(output, "DQ-002"), [])
                self.assertEqual(_pointers(output, "DQ-003"), [])
                notes = _not_recognised_notes(output)
                self.assertEqual(len(notes), 1)
                self.assertEqual(
                    _named_entries(notes[0]), ["DQ-002", "DQ-003"])
                self.assertEqual(_pd_r7_notes(output), [])

    def test_joiner_ghost_middle_takes_pd_r7(self):
        for name in ("slash", "fullwidth_semicolon"):
            with self.subTest(joiner=name):
                text = _list_file(
                    5,
                    _joined_statement(
                        [1, 999, 2, 3], _JOINERS[name]),
                    [1, 2, 3])
                output = _run_text(text)
                self.assertEqual(
                    _pointers(output, "DQ-001"), ["DQ-005"])
                self.assertEqual(
                    _pointers(output, "DQ-003"), ["DQ-005"])
                self.assertEqual(_pointers(output, "DQ-002"), [])
                self.assertEqual(len(_pd_r7_notes(output)), 1)
                notes = _not_recognised_notes(output)
                self.assertEqual(len(notes), 1)
                self.assertEqual(
                    _named_entries(notes[0]), ["DQ-002"])

    def test_joiner_signal_obeys_the_condition_limb(self):
        # The condition limb governs the joiner signals too:
        # where the same entry derives one middle by a comma
        # statement, the joiner signal names only the middle
        # no pointer stands for.
        text = _list_file(
            5, _joined_statement([1, 2, 3, 4], _JOINERS["slash"]),
            [1, 2, 3, 4], extra=_comma_statement([3]))
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-003"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(_named_entries(notes[0]), ["DQ-002"])

    def test_joiner_two_target_list_takes_no_signal(self):
        text = _list_file(
            5, _joined_statement([1, 2], _JOINERS["pipe"]), [1, 2])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])
        self.assertEqual(_pd_r7_notes(output), [])

    def test_joiner_single_clause_signals_unread_targets(self):
        statement = (
            "This ruling displaces the rulings at "
            "DQ-001 / DQ-002 / DQ-003 in full; those earlier "
            "rulings no longer stand as governing on their "
            "subjects.")
        text = _list_file(5, statement, [1, 2, 3])
        output = _run_text(text)
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-005"])
        self.assertEqual(_pointers(output, "DQ-002"), [])
        self.assertEqual(_pointers(output, "DQ-003"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(
            _named_entries(notes[0]), ["DQ-002", "DQ-003"])


class Ch113WalkCostTest(unittest.TestCase):
    """CH-113: the enumeration is restated so a recorded
    cycle is not re-walked from each of its starts. The
    inventory, the counts, the refusal figures, the named
    funnel and wall family refusals, and the PIN-10 counts
    stand exactly as the fix wave 5 K1 paper pins them.
    These tests pin the figures and the completions; the
    walk cost itself stands as bench measurements in the
    seat paper, never as a timed verdict here."""

    def _assert_work_refusal(self, text, subcommand, timeout=60):
        self.assertIsNotNone(WORK_BOUND)
        code, out, err = _cli(text, subcommand, timeout=timeout)
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("work limit", err.lower())
        self.assertIn(str(WORK_BOUND), err)
        self.assertIn("Exit: code 3", err)

    def test_ring_work_and_inventory_stand_at_governed_sizes(self):
        for n in (1200, 2400):
            with self.subTest(n=n):
                output = _run_text(_ring_text(n))
                self.assertEqual(len(_cycle_warnings(output)), 1)
                self.assertEqual(_work_measured(output), n)
                self.assertEqual(_work_over(output), False)
                self.assertEqual(_count_over(output), False)

    def test_ring_3600_compact_completes_exactly(self):
        output = _run_text(_compact_ring_text(3600))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), 3600)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_ring_4990_compact_completes_exactly(self):
        output = _run_text(_compact_ring_text(4990))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), 4990)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_pin10_counts_and_work_figures_stand(self):
        cases = [
            ("dense5", _dense_text(5), 84, 300),
            ("dense6", _dense_text(6), 409, 1866),
            ("bip4", _bip_text(4), 424, 2690),
            ("detour6", _detour_text(6), 987, 171535),
            ("wall6", _wall_text(200, 6), 443, 604492),
        ]
        for name, text, cycles, work in cases:
            with self.subTest(name=name):
                output = _run_text(text)
                self.assertEqual(
                    len(_cycle_warnings(output)), cycles)
                self.assertEqual(_work_measured(output), work)
                self.assertEqual(_work_over(output), False)
                self.assertEqual(_count_over(output), False)

    def test_named_family_refusals_stand(self):
        self._assert_work_refusal(
            _funnel_text(20), "validate", timeout=30)
        self._assert_work_refusal(
            _funnel_text(24), "validate", timeout=30)
        self._assert_work_refusal(
            _wall_text(200, 8), "validate", timeout=30)
        self._assert_work_refusal(
            _wall_text(200, 10), "validate", timeout=30)
        self._assert_work_refusal(
            _wall_text(200, 12), "validate", timeout=60)

    def test_wall7_and_detour7_consequences_stand(self):
        output = _run_text(_wall_text(200, 7))
        self.assertEqual(_work_over(output), True)
        self.assertEqual(_count_over(output), False)
        self.assertEqual(_work_measured(output), WORK_BOUND + 1)
        output = _run_text(_detour_text(7))
        self.assertEqual(_count_over(output), True)
        self.assertEqual(_work_over(output), True)


if __name__ == "__main__":
    unittest.main()
