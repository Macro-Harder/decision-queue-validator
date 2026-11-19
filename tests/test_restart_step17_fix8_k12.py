"""Restart Step 17 fix wave 8, Seat K12 tests.

Charges CH-187 and CH-188, as ruled at section 77 of
design/steps/step-17r-record.md, under ruling (e) of that
section and the ruling (f) form of record section 66 for
both cost charges: figures stand as measurements, and the
verdicts rest on the constructions behaviour and the
governed pins, never on a cost figure alone. Findings:
seat 21 A8-21-1 (Medium, T8-33) and A8-21-2 (Medium,
T8-34), at design/steps/step-17r-attack8-21.md.

CH-187: one chord edge inside a ring component stands
outside the narrowed CH-152 limb at any file order, so a
2,498 entry ring carrying one chord and two cycles pays
a quadratic descent excess against its pure control. The
locus is _enumerate_components in validate.py. The cure
stands at that locus: where a start is carried by a
recorded cycle and the descent from the start can do
nothing but follow that cycle to its refusal (every
other edge of every entry the descent can reach stands
refused on its face from that start: it leaves the
component, it points at an entry standing earlier in
file order than the start, or it points at an entry
already on the path), the descent is not walked; its
counted examinations are tallied by a reading of the
same edges in the same candidate terms the walk itself
uses, and the tally is added to the work counter in the
walk place, bound check included, so the work figure,
the cycle inventory, the counts, and the refusal figures
stand exactly as counted. A start whose trapped reading
meets an edge that would descend, or an edge back to the
start that would close a cycle, is walked exactly as
before, so the families whose figures stand governed
(the wall, detour, dense, and bipartite forms, the pure
ring, the leaf ring of CH-152, and the small chord form)
stand untouched, as the pins below record.

CH-188: the governed hugebip4 construction (complete
bipartite width 4, identifiers of 15,996 digits) measured
a factor near 2.7 over its round 5 to 7 cost on the wave
7 tree, its inventory and output exact, the profile
placing the cost in scan_line_occurrences in parse.py
and in escape_text and the surrogate safe delivery in
the render path. The scan locus stands cured in this
wave at CH-155 (seat K2); this seat cures the render
path loci: escape_text in render.py and _surrogate_safe
in shell.py, whose per character loops over the composed
output (134,742,025 bytes on the governed form) are
restated as table translations carrying the same
replacement for every code point the loops name, and no
other change. The behaviour pins below record the
escaped forms exactly, character class by character
class, and the scaled hugebip form stands at its exact
inventory and output size.

The bounded tests assert, in the CH-144 and CH-155 test
form, that the charged readings complete inside a stated
bound and return the behaviour the construction carries;
the bound is the test harness timeout on a child process,
not an asserted duration. Cost figures stand as
measurements in the seat paper only.

Copyright: J.P. Picard aka Macro-Harder
"""

import os
import subprocess
import sys
import unittest

import dqv_harness as h

validate = h.import_module("validate")
render = h.import_module("render")
shell = h.import_module("shell")
types = h.import_module("types")

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


def _ring_text(n, chord=None, leaf_target=None, compact=False):
    parts = [_HEADER]
    for i in range(1, n + 1):
        prev = n if i == 1 else i - 1
        stmt = "This supersedes the ruling at DQ-%03d." % prev
        if chord and i == chord[0]:
            stmt += " This supersedes the ruling at DQ-%03d." % chord[1]
        if compact:
            parts.append(
                "### DQ-%03d: Entry %d\nStatus: Banked. %s\n"
                % (i, i, stmt))
        else:
            parts.append(
                "### DQ-%03d: Entry %d\nStatus: Banked\n%s\n\n"
                % (i, i, stmt))
    if leaf_target is not None:
        parts.append(
            "### DQ-%03d: Leaf\nStatus: Banked. "
            "This supersedes the ruling at DQ-%03d.\n"
            % (n + 1, leaf_target))
    return "".join(parts)


def _simple_entry(number, targets):
    stmt = "This supersedes the ruling at " + " and ".join(
        "DQ-%03d" % t for t in targets) + ".\n"
    return ("### DQ-%03d: Entry %d\nStatus: Banked\n%s\n"
            % (number, number, stmt))


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
    parts = [_HEADER]
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
    parts = [_HEADER]
    for i in range(1, tid + 1):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _chord_text():
    edges = {1: [6], 2: [1], 3: [2], 4: [3, 2], 5: [4], 6: [5]}
    parts = [_HEADER]
    for i in range(1, 7):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _hugebip_scaled_text(digits):
    ids = {}
    for i in range(1, 9):
        ids[i] = "DQ-" + "7" * (digits - 1) + str(i)
    odds = [1, 3, 5, 7]
    evens = [2, 4, 6, 8]
    parts = [_HEADER]
    for i in range(1, 9):
        targets = evens if i % 2 == 1 else odds
        stmt = "This supersedes the ruling at " + " and ".join(
            ids[t] for t in targets) + ".\n"
        parts.append("### %s: Entry %d\nStatus: Banked\n%s\n"
                     % (ids[i], i, stmt))
    return "".join(parts)


def _cli_bounded(text, bound, label, filename=None):
    """Run validate on the text in a child process under
    the bound, in the CH-144 test form. Returns the child
    (returncode, stdout, stderr); a run past the bound
    fails the calling test. Where a filename stands
    named, the input stands written under that exact
    name, so the input name line of the output stands as
    the named form carries it."""
    if filename is None:
        path = h.temp_input(text.encode("utf-8"),
                            name="fix8_k12_%s.md" % label)
    else:
        import tempfile
        from pathlib import Path
        directory = tempfile.mkdtemp(prefix="fix8_k12_")
        path = Path(directory) / filename
        path.write_bytes(text.encode("utf-8"))
    try:
        code, out, err = h.run_cli_with_timeout(
            "validate", path, timeout=bound)
        return code, out, err, str(path)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "%s did not complete inside its bound of %s seconds"
            % (label, bound))


def _driver_bounded(source, bound, label):
    """Run a python driver in a child process under the
    bound. Returns its stdout text; a run past the bound
    fails the calling test."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(h.PRODUCT_ROOT)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", source],
            cwd=str(h.PRODUCT_ROOT), env=env,
            capture_output=True, text=True, timeout=bound)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "%s did not complete inside its bound of %s seconds"
            % (label, bound))
    if proc.returncode != 0:
        raise AssertionError(
            "%s driver exited %d: %s"
            % (label, proc.returncode, proc.stderr[-400:]))
    return proc.stdout


class Ch187BoundedCompletionTest(unittest.TestCase):
    """CH-187: the chorded ring readings complete inside
    their bounds and return the exact inventory."""

    def test_chorded_ring_2498_completes(self):
        # The charged form of A8-21-1 in its four line
        # shape: 2,498 entries, one chord to the earliest
        # entry, two cycles. On the uncured tree this run
        # measured 6.90 seconds of child CPU on the bench;
        # its pure control measured 2.24.
        code, out, _err, _path = _cli_bounded(
            _ring_text(2498, chord=(1249, 1)), 5, "ringchord2498")
        self.assertEqual(code, 1)
        self.assertEqual(out.count(b"PIN-10"), 5)

    def test_chorded_ring_4000_compact_completes(self):
        # The same form in the compact two line shape at
        # 4,000 entries: on the uncured tree this run
        # measured 14.92 seconds of child CPU on the bench;
        # its pure control measured 3.94.
        code, out, _err, _path = _cli_bounded(
            _ring_text(4000, chord=(2000, 1), compact=True),
            8, "ringchord4000")
        self.assertEqual(code, 1)
        self.assertEqual(out.count(b"PIN-10"), 5)


class Ch187BehaviourPinsTest(unittest.TestCase):
    """CH-187: the chorded ring inventory and work figure
    stand exactly as counted before the cure, and every
    governed figure of the enumeration stands as counted."""

    def test_chord_to_earliest_work_and_inventory(self):
        n = 800
        output = _run_text(_ring_text(n, chord=(n // 2, 1)))
        self.assertEqual(len(_cycle_warnings(output)), 2)
        self.assertEqual(_work_measured(output), 3 * n // 2 + 2)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_chord_to_later_work_and_inventory(self):
        n = 800
        output = _run_text(_ring_text(n, chord=(n // 2, n - 1)))
        self.assertEqual(len(_cycle_warnings(output)), 2)
        self.assertEqual(_work_measured(output), 3 * n // 2 + 1)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_chord_second_size(self):
        n = 400
        output = _run_text(_ring_text(n, chord=(n // 2, 1)))
        self.assertEqual(len(_cycle_warnings(output)), 2)
        self.assertEqual(_work_measured(output), 3 * n // 2 + 2)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_pure_ring_pin_stands(self):
        n = 800
        output = _run_text(_ring_text(n))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), n)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_leaf_ring_ch152_pin_stands(self):
        n = 800
        output = _run_text(_ring_text(n, leaf_target=n // 2))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), n + 1)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_small_chord_form_stands_walked_and_whole(self):
        # The governed chord form of the fix wave 7 K12
        # pins: the chord target stands inside the
        # component, both cycles stand recorded, and the
        # work figure stands at 10 exactly.
        output = _run_text(_chord_text())
        self.assertEqual(len(_cycle_warnings(output)), 2)
        self.assertEqual(_work_measured(output), 10)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_governed_work_figures_stand(self):
        cases = [
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

    def test_dense8_count_refusal_stands(self):
        output = _run_text(_dense_text(8))
        self.assertEqual(_count_over(output), True)


class Ch188EscapeBehaviourTest(unittest.TestCase):
    """CH-188: the escaped form of every character class
    the render path names stands exactly as before."""

    def test_plain_text_prints_as_itself(self):
        self.assertEqual(render.escape_text("plain text 123"),
                         "plain text 123")
        ident = "DQ-" + "7" * 15996 + "1"
        self.assertEqual(render.escape_text(ident), ident)
        self.assertEqual(render.escape_text(""), "")
        self.assertEqual(render.escape_text(None), "")
        self.assertEqual(render.escape_text(123), "123")

    def test_backslash_and_whitespace_forms(self):
        self.assertEqual(render.escape_text("a\\b"), "a\\\\b")
        self.assertEqual(render.escape_text("a\nb"), "a\\nb")
        self.assertEqual(render.escape_text("a\rb"), "a\\rb")
        self.assertEqual(render.escape_text("a\tb"), "a\\tb")

    def test_control_forms(self):
        self.assertEqual(render.escape_text("\x1b"), "\\x1B")
        self.assertEqual(render.escape_text("\x00"), "\\x00")
        self.assertEqual(render.escape_text("\x0b"), "\\x0B")
        self.assertEqual(render.escape_text("\x1f"), "\\x1F")
        self.assertEqual(render.escape_text("\x7f"), "\\x7F")
        self.assertEqual(render.escape_text("\x80"), "\\x80")
        self.assertEqual(render.escape_text("\x9f"), "\\x9F")

    def test_invisible_forms(self):
        self.assertEqual(render.escape_text("\xad"), "\\u00AD")
        self.assertEqual(render.escape_text("\u200b"), "\\u200B")
        self.assertEqual(render.escape_text("\u202a"), "\\u202A")
        self.assertEqual(render.escape_text("\u2028"), "\\u2028")
        self.assertEqual(render.escape_text("\u2029"), "\\u2029")
        self.assertEqual(render.escape_text("\ufeff"), "\\uFEFF")
        self.assertEqual(render.escape_text("\u061c"), "\\u061C")

    def test_tag_forms(self):
        self.assertEqual(render.escape_text("\U000e0001"),
                         "\\uE0001")
        self.assertEqual(render.escape_text("\U000e0020"),
                         "\\uE0020")
        self.assertEqual(render.escape_text("\U000e007f"),
                         "\\uE007F")

    def test_surrogate_and_astral_forms(self):
        self.assertEqual(render.escape_text("\ud800"), "\\uD800")
        self.assertEqual(render.escape_text("\udfff"), "\\uDFFF")
        self.assertEqual(render.escape_text("\U0001d11e"),
                         "\U0001d11e")
        self.assertEqual(
            render.escape_text("x\ud800y\x00z"),
            "x\\uD800y\\x00z")


class Ch188SurrogateSafeBehaviourTest(unittest.TestCase):
    """CH-188: the surrogate safe delivery form stands
    exactly as before."""

    def test_plain_text_unchanged(self):
        self.assertEqual(shell._surrogate_safe("plain 123"),
                         "plain 123")
        self.assertEqual(shell._surrogate_safe(""), "")

    def test_lone_surrogates_escaped(self):
        self.assertEqual(shell._surrogate_safe("a\ud800b"),
                         "a\\uD800b")
        self.assertEqual(shell._surrogate_safe("\udfff"),
                         "\\uDFFF")
        self.assertEqual(shell._surrogate_safe("\ud800\udc00"),
                         "\\uD800\\uDC00")

    def test_astral_and_controls_unchanged(self):
        self.assertEqual(shell._surrogate_safe("\U0001d11e"),
                         "\U0001d11e")
        self.assertEqual(shell._surrogate_safe("a\x00b\nc"),
                         "a\x00b\nc")


class Ch188BoundedCompletionTest(unittest.TestCase):
    """CH-188: the render path readings complete inside
    their bounds on the charged shapes."""

    def test_escape_of_long_plain_text_completes(self):
        # On the uncured tree the per character loop read
        # 8,000,000 plain characters at 1.63 seconds of
        # process CPU on the bench, beside the child
        # interpreter start.
        source = (
            "from decision_queue_validator import render\n"
            "plain = '9' * 8000000\n"
            "out = render.escape_text(plain)\n"
            "print(len(out), out == plain)\n")
        out = _driver_bounded(source, 1.0, "escape8m")
        self.assertEqual(out.strip(), "8000000 True")

    def test_surrogate_safe_of_long_text_completes(self):
        # On the uncured tree the per character loop read
        # 8,000,000 characters at 0.51 seconds of process
        # CPU on the bench; this form carries twice that
        # length beside the child interpreter start.
        source = (
            "from decision_queue_validator import shell\n"
            "text = ('9' * 999999 + '\\ud800') * 16\n"
            "out = shell._surrogate_safe(text)\n"
            "print(len(out), out.count('\\\\uD800'))\n")
        out = _driver_bounded(source, 0.7, "surrogate16m")
        self.assertEqual(out.strip(), "16000080 16")

    def test_scaled_hugebip_completes_with_exact_output(self):
        # The governed hugebip4 shape at 2,000 digits: on
        # the uncured tree this run measured 9.28 seconds
        # of child CPU on the bench, its output standing
        # at 32,870,624 bytes with 424 cycle Warnings. The
        # output carries the input path as passed on its
        # Input line, so the standing size is stated for
        # the probe path and corrected here by the length
        # of the path this run passes.
        code, out, _err, path = _cli_bounded(
            _hugebip_scaled_text(2000), 6, "hugebipscaled",
            filename="hugebip-scaled.md")
        self.assertEqual(code, 1)
        probe_path = "fix8-k12-stage/cases/hugebip-scaled.md"
        self.assertEqual(
            len(out), 32870624 - len(probe_path) + len(path))
        self.assertEqual(out.count(b"PIN-10"), 849)


if __name__ == "__main__":
    unittest.main()
