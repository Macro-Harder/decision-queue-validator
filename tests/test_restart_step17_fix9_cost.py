"""Restart Step 17 fix wave 9, Cost Charge seat tests.

Charge A9-21-1, as ruled at section 81 ruling (c) of
design/steps/step-17r-record.md: the governed wall family
measures about twice its round 8 cost on the wave 8 cured
tree (finding A9-21-1 of design/steps/step-17r-attack9-21.md:
wall6 at 5.07 s and 4.90 s of child CPU against 2.44 s in
round 8, twowall6 at 5.56 s in both runs against 2.29 s,
every exit, refusal, count, and output byte exact, and the
work pin unmoved). The cure terms are stated on
constructions, and verdicts never on figures alone: the
bounded tests below assert, in the CH-144 and CH-155 test
form, that the charged constructions complete inside a
stated bound and return the behaviour the construction
carries; the bound is the test harness timeout on a child
process, not an asserted duration. Cost figures stand as
measurements in the seat paper only.

The behaviour pins record the wall pair exactly: wall6
completes at exit 1 carrying 443 cycle Warnings (887
PIN-10 occurrences), output of 2,463,925 bytes, and the
governed work figure 604,492 standing unmoved; twowall6
takes the work refusal at exit 3 with a refusal of 900
bytes on standard error. The neighbouring pins record the
families the cure must not move: the CH-187 chorded ring
forms and their work figures, the pure and leaf rings,
detour6, dense6, dense8, and bip4, at the figures the
fix wave 8 K12 module pins.

Copyright: J.P. Picard aka Macro-Harder
"""

import subprocess
import unittest

import dqv_harness as h

_HEADER = "# Decision queue\n\n"


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


def _work_measured(output):
    return h.get(output, "cycle_work_measured",
                 "supersession_cycle_work_measured")


def _work_over(output):
    return h.get(output, "cycle_work_over_bound",
                 "supersession_cycle_work_over_bound")


def _count_over(output):
    return h.get(output, "cycle_over_bound",
                 "supersession_cycle_over_bound")


def _simple_entry(number, targets):
    stmt = "This supersedes the ruling at " + " and ".join(
        "DQ-%03d" % t for t in targets) + ".\n"
    return ("### DQ-%03d: Entry %d\nStatus: Banked\n%s\n"
            % (number, number, stmt))


def _wall_edges(w, layers, base=0):
    per = w + 3

    def sp(lay, k):
        return base + (lay - 1) * per + k

    def bush(lay, j):
        return base + (lay - 1) * per + w + j

    sid = base + layers * per + 1
    tid = base + layers * per + 2
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
    return edges, tid


def _wall_text(w, layers, base=0):
    edges, tid = _wall_edges(w, layers, base)
    parts = [_HEADER] if base == 0 else []
    for i in range(base + 1, tid + 1):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _twowall_text(w, layers):
    first, tid = _wall_edges(w, layers, 0)
    parts = [_HEADER]
    for i in range(1, tid + 1):
        parts.append(_simple_entry(i, first[i]))
    parts.append(_wall_text(w, layers, base=tid))
    return "".join(parts)


def _ring_text(n, chord=None, leaf_target=None):
    parts = [_HEADER]
    for i in range(1, n + 1):
        prev = n if i == 1 else i - 1
        stmt = "This supersedes the ruling at DQ-%03d." % prev
        if chord and i == chord[0]:
            stmt += " This supersedes the ruling at DQ-%03d." % chord[1]
        parts.append(
            "### DQ-%03d: Entry %d\nStatus: Banked\n%s\n\n"
            % (i, i, stmt))
    if leaf_target is not None:
        parts.append(
            "### DQ-%03d: Leaf\nStatus: Banked. "
            "This supersedes the ruling at DQ-%03d.\n"
            % (n + 1, leaf_target))
    return "".join(parts)


def _dense_text(n, base=0):
    parts = [_HEADER]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            base + i,
            [base + t for t in range(1, n + 1) if t != i]))
    return "".join(parts)


def _bip_text(width):
    parts = [_HEADER]
    n = 2 * width
    odds = [i for i in range(1, n + 1) if i % 2 == 1]
    evens = [i for i in range(1, n + 1) if i % 2 == 0]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            i, evens if i % 2 == 1 else odds))
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
    parts = [_HEADER]
    for i in range(1, tid + 1):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _cli_bounded(text, bound, label):
    """Run validate on the text in a child process under
    the bound, in the CH-144 test form. Returns the child
    (returncode, stdout, stderr); a run past the bound
    fails the calling test."""
    path = h.temp_input(text.encode("utf-8"),
                        name="fix9_cost_%s.md" % label)
    try:
        code, out, err = h.run_cli_with_timeout(
            "validate", path, timeout=bound)
        return code, out, err
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "%s did not complete inside its bound of %s seconds"
            % (label, bound))


class A921WallBoundedCompletionTest(unittest.TestCase):
    """A9-21-1: the governed wall pair completes inside
    its bound and returns its exact behaviour. On the
    tree at the charge, wall6 measured 4.73 s to 5.07 s
    of child CPU and twowall6 5.33 s to 5.56 s in the
    re-measurement and attack runs, against round 8
    figures of 2.44 s and 2.29 s; both stand outside the
    4 second bound below on that tree."""

    def test_wall6_completes_inside_bound(self):
        # The output and refusal byte totals of the pair
        # stand recorded in the seat paper at the attack
        # constructions own paths (2,463,925 bytes of
        # output on wall6, a refusal of 900 bytes on
        # twowall6), since the output carries the input
        # name line and a harness path would move the
        # total; this test pins the exit, the inventory
        # count, and the empty error stream.
        code, out, err = _cli_bounded(
            _wall_text(200, 6), 4, "wall6")
        self.assertEqual(code, 1)
        self.assertEqual(out.count(b"PIN-10"), 887)
        self.assertEqual(err, b"")

    def test_twowall6_refuses_inside_bound(self):
        code, out, err = _cli_bounded(
            _twowall_text(200, 6), 4, "twowall6")
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        self.assertTrue(len(err) > 0)


class A921WallBehaviourPinsTest(unittest.TestCase):
    """A9-21-1: the wall pair behaviour and the governed
    work figures stand exactly as counted, before and
    after any cure."""

    def test_wall6_work_and_inventory(self):
        output = _run_text(_wall_text(200, 6))
        self.assertEqual(len(_cycle_warnings(output)), 443)
        self.assertEqual(_work_measured(output), 604492)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_twowall6_work_refusal_stands(self):
        output = _run_text(_twowall_text(200, 6))
        self.assertEqual(_work_over(output), True)


class A921NeighbourPinsTest(unittest.TestCase):
    """The neighbouring governed families stand at their
    fix wave 8 figures, before and after any cure at the
    wall locus."""

    def test_chorded_ring_work_and_inventory(self):
        n = 800
        output = _run_text(_ring_text(n, chord=(n // 2, 1)))
        self.assertEqual(len(_cycle_warnings(output)), 2)
        self.assertEqual(_work_measured(output), 3 * n // 2 + 2)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_pure_and_leaf_ring_pins(self):
        n = 800
        output = _run_text(_ring_text(n))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), n)
        output = _run_text(_ring_text(n, leaf_target=n // 2))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), n + 1)

    def test_detour_and_dense_work_figures(self):
        cases = [
            ("dense6", _dense_text(6), 409, 1866),
            ("bip4", _bip_text(4), 424, 2690),
            ("detour6", _detour_text(6), 987, 171535),
        ]
        for name, text, cycles, work in cases:
            with self.subTest(name=name):
                output = _run_text(text)
                self.assertEqual(
                    len(_cycle_warnings(output)), cycles)
                self.assertEqual(_work_measured(output), work)
                self.assertEqual(_work_over(output), False)
                self.assertEqual(_count_over(output), False)

    def test_dense8_count_refusal_stands(self):
        output = _run_text(_dense_text(8))
        self.assertEqual(_count_over(output), True)


if __name__ == "__main__":
    unittest.main()
