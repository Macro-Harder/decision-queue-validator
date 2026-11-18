"""Restart Step 17 fix wave 4, Seat K1 tests.

Charges CH-52, CH-64, and CH-65, as ruled at section 38 of
design/steps/step-17r-record.md (rulings (b), (c), (f), and
(g), with FLAG 10 and FLAG 11) and prepared in
design/steps/step-17r-triage4-prep.md. The three charges
stand in one function territory in validate, the
supersession and cycle reading, and are taken with all
three in view.

CH-52 (rulings (b) and (c), merged): the CH-32 cycle bound
counts cycles found, not paths explored, so the funnel
family (round 4 seat 5 Finding 1: refusal only after
10.457 CPU seconds at 5,006 bytes, no completion in 25
seconds at 5,695 bytes) and the wall family (round 4 seat
21 A4-21-1: correct refusal only after 62.56 seconds
validate at L 12 in a 192,695 byte file) pay exponential
dead path cost before the bound trips. The ruled cure: the
enumeration gains a work counter, paths explored in the
descent, beside the found cycle count; on the work bound
tripping, refusal at exit 3 in the CH-32 form naming the
work limit. No cure truncates an inventory below the ruled
count bound; the complete inventory duty below the count
bound stands unmoved. The work bound figure is set on
bench evidence at the strict side and stands in validate
as _CYCLE_WORK_BOUND; these tests read the figure from the
product and pin the behaviour around it, and the K1 paper
records the figure and the measurements behind it.

CH-64 (ruling (f)): round 4 seat 9 Finding 1. A comma
separated supersession target list of four or more
silently drops every target between the first and the
last two: no pointer, no Note, no map entry, and the
cycle inventory undercounts the stated graph (26 cycle
Warnings against 180 cycles on the five entry complete
digraph). The cure: the target list reading takes every
listed target, at every list length.

CH-65: round 4 seat 9 Findings 2 and 3. Finding 2: a real
pointer derived from hypothetical, reported, and
withdrawn draft statements; the cure is that a conditional
frame and a reported claim the same text withdraws derive
no pointer. Finding 3: four identifier forms (DQ001,
DQ_001, DQ 001, non-ASCII digits) silently dropped with
no near miss Note; under FLAG 11 data readings read ASCII
digits only and that stands, so the cure is the near miss
Note on the silent forms, not a widened digit reading.
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


class Ch52WorkBoundTest(unittest.TestCase):
    """CH-52: the enumeration work bound. The funnel and the
    wall refuse promptly at exit 3 in the CH-32 form naming
    the work limit, and every governed below count bound
    construction completes or refuses exactly as before."""

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

    def test_funnel20_refuses_work_on_both_subcommands(self):
        text = _funnel_text(20)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_work_refusal(text, subcommand)

    def test_funnel24_refuses_work_on_validate(self):
        self._assert_work_refusal(
            _funnel_text(24), "validate", timeout=30)

    def test_wall8_refuses_work_on_both_subcommands(self):
        text = _wall_text(200, 8)
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                self._assert_work_refusal(text, subcommand)

    def test_wall10_refuses_work_on_validate(self):
        self._assert_work_refusal(
            _wall_text(200, 10), "validate", timeout=30)

    def test_pipeline_carries_the_work_over_bound_flag(self):
        output = _run_text(_funnel_text(20))
        self.assertEqual(_work_over(output), True)
        self.assertEqual(_cycle_warnings(output), [])
        below = _run_text(_dense_text(5))
        self.assertEqual(_work_over(below), False)

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

    def test_count_refusals_stand_exactly_as_before(self):
        # The global across components proof: three disjoint
        # dense6 components carry 1,227 cycles in total and
        # refuse on the count bound, in the count form.
        for subcommand in ("validate", "render"):
            with self.subTest(case="threedense6",
                              subcommand=subcommand):
                self._assert_count_refusal(
                    _multi_dense_text(3), subcommand)
        for subcommand in ("validate", "render"):
            with self.subTest(case="dense7", subcommand=subcommand):
                self._assert_count_refusal(
                    _dense_text(7), subcommand)


class Ch64TargetListTest(unittest.TestCase):
    """CH-64: every listed target in a comma separated list
    takes its pointer, at every list length, in acyclic and
    cyclic forms."""

    def _list_file(self, claiming_number, targets):
        total = max([claiming_number] + list(targets))
        parts = [_HEADER]
        for i in range(1, total + 1):
            if i == claiming_number:
                parts.append(_ruled_entry(
                    i, _comma_statement(list(targets))))
            else:
                parts.append(_ruled_entry(
                    i, "The harbour ruling stands."))
        return "".join(parts)

    def test_four_target_comma_list_takes_all_pointers(self):
        output = _run_text(self._list_file(5, [1, 2, 3, 4]))
        for target in (1, 2, 3, 4):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])
        self.assertEqual(_not_recognised_notes(output), [])

    def test_five_target_comma_list_takes_all_pointers(self):
        output = _run_text(self._list_file(6, [1, 2, 3, 4, 5]))
        for target in (1, 2, 3, 4, 5):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-006"])

    def test_four_target_comma_list_permuted_takes_all(self):
        output = _run_text(self._list_file(5, [3, 1, 4, 2]))
        for target in (1, 2, 3, 4):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])

    def test_six_target_comma_list_takes_all_pointers(self):
        output = _run_text(self._list_file(7, [1, 2, 3, 4, 5, 6]))
        for target in (1, 2, 3, 4, 5, 6):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-007"])

    def test_comma_list_ghost_middle_target_takes_pd_r7(self):
        parts = [_HEADER]
        for i in range(1, 5):
            parts.append(_ruled_entry(
                i, "The harbour ruling stands."))
        parts.append(_ruled_entry(
            5, _comma_statement([1, 999, 2, 3])))
        output = _run_text("".join(parts))
        for target in (1, 2, 3):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])
        self.assertEqual(len(_pd_r7_notes(output)), 1)

    def test_complete5_comma_graph_takes_84_cycles(self):
        # The seat 9 paper states a hand count of 180 cycles
        # for this graph. The product inventory definition
        # counts each distinct simple cycle once, from its
        # earliest entry in file order, and the governed
        # dense5 pin for the identical complete digraph on
        # five entries stands at 84 cycle Warnings (fix wave
        # 3 K1 file, CH-32 completeness). The cured comma
        # graph therefore takes 84, matching the governed
        # inventory of the same graph exactly, with all 20
        # pointers standing; the 180 figure is named in the
        # K1 paper as a figure that does not stand against
        # the governed pin, not absorbed into this test.
        parts = [_HEADER]
        for i in range(1, 6):
            targets = [t for t in range(1, 6) if t != i]
            parts.append(_ruled_entry(i, _comma_statement(targets)))
        output = _run_text("".join(parts))
        self.assertEqual(len(_cycle_warnings(output)), 84)
        for target in range(1, 6):
            self.assertEqual(
                len(_pointers(output, "DQ-%03d" % target)), 4)

    def test_three_target_comma_list_control(self):
        output = _run_text(self._list_file(4, [1, 2, 3]))
        for target in (1, 2, 3):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-004"])

    def test_four_target_and_form_control(self):
        parts = [_HEADER]
        for i in range(1, 5):
            parts.append(_ruled_entry(
                i, "The harbour ruling stands."))
        parts.append(_ruled_entry(5, _full_statement([1, 2, 3, 4])))
        output = _run_text("".join(parts))
        for target in (1, 2, 3, 4):
            self.assertEqual(
                _pointers(output, "DQ-%03d" % target), ["DQ-005"])


_HYPOTHETICAL = (
    "If a later ruling displaces the ruling at DQ-001 in "
    "full, that earlier ruling would no longer stand as "
    "governing on its subject, and DQ-001 would be the "
    "superseded entry.")

_REPORTED_DRAFT = (
    "An earlier draft claimed this ruling displaces the "
    "ruling at DQ-001 in full; that earlier ruling no "
    "longer stands as governing on its subject, and DQ-001 "
    "is the superseded entry. The draft was withdrawn and "
    "this ruling makes no displacement.")

_NEGATION = (
    "This ruling does not displace the ruling at DQ-001 in "
    "full; that earlier ruling still stands as governing on "
    "its subject, and DQ-001 is not the superseded entry.")


def _two_entry_file(claiming_line):
    return (
        _HEADER
        + _ruled_entry(1, "The harbour ruling stands.")
        + _ruled_entry(2, claiming_line))


class Ch65AssertionTest(unittest.TestCase):
    """CH-65 Finding 2: a conditional frame and a reported
    claim the same text withdraws derive no pointer."""

    def test_hypothetical_derives_no_pointer(self):
        output = _run_text(_two_entry_file(_HYPOTHETICAL))
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(len(_not_recognised_notes(output)), 1)

    def test_reported_withdrawn_draft_derives_no_pointer(self):
        output = _run_text(_two_entry_file(_REPORTED_DRAFT))
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(len(_not_recognised_notes(output)), 1)

    def test_plain_assertion_control_derives_pointer(self):
        output = _run_text(_two_entry_file(_full_statement([1])))
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-002"])
        self.assertEqual(_not_recognised_notes(output), [])

    def test_negation_control_stands(self):
        output = _run_text(_two_entry_file(_NEGATION))
        self.assertEqual(_pointers(output, "DQ-001"), [])
        self.assertEqual(len(_not_recognised_notes(output)), 1)


def _target_form_statement(target_text):
    return (
        "This ruling displaces the ruling at %s in full; "
        "that earlier ruling no longer stands as governing "
        "on its subject, and %s is the superseded entry."
        % (target_text, target_text))


class Ch65NearMissTest(unittest.TestCase):
    """CH-65 Finding 3: the four charged identifier forms
    take the near miss Note, so a missed pointer stands
    told from an absent one. The data reading itself stays
    on ASCII digits under FLAG 11: no pointer derives."""

    def _assert_near_miss(self, target_text):
        output = _run_text(_two_entry_file(
            _target_form_statement(target_text)))
        self.assertEqual(_pointers(output, "DQ-001"), [])
        notes = _not_recognised_notes(output)
        self.assertEqual(len(notes), 1)

    def test_no_dash_form_takes_note(self):
        self._assert_near_miss("DQ001")

    def test_underscore_form_takes_note(self):
        self._assert_near_miss("DQ_001")

    def test_space_form_takes_note(self):
        self._assert_near_miss("DQ 001")

    def test_non_ascii_digit_form_takes_note(self):
        self._assert_near_miss("DQ-٠٠١")

    def test_case_variant_control_takes_note(self):
        self._assert_near_miss("dq-001")

    def test_standard_form_control_derives_pointer(self):
        output = _run_text(_two_entry_file(
            _target_form_statement("DQ-001")))
        self.assertEqual(_pointers(output, "DQ-001"), ["DQ-002"])
        self.assertEqual(_not_recognised_notes(output), [])


if __name__ == "__main__":
    unittest.main()
