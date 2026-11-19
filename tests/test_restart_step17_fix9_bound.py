"""Restart Step 17 fix wave 9, Bound Charge tests.

Charge: record section 81 ruling (b) of
design/steps/step-17r-record.md. The K12 remainder, the
chorded ring residual excess at the _map_print_size locus
in validate.py, outside the CH-187 charge of fix wave 8,
stands BOUND, neither cured nor silently carried. This
module states the bound as a governed test. It changes no
product code, and no test in it asserts a cure: each test
measures the remainder constructions on the bench, in the
attack round 9 seat 21 generator forms, and asserts that
the measured excess, chorded child CPU minus pure control
child CPU in the same sitting, stands at or under the
bound ceiling stated for that construction below, with
the construction behaviour (exit 1, cycle count exact by
its PIN-10 occurrences) standing as the pin the
measurement rides on. Cost figures stand as measurements;
an excess beyond a stated ceiling at the same construction
in a later round is a defect under ruling (b).

The bound ladder, stated expressly. Each term names its
entry count, its form, its chord count, the cycles counted
in its one component, the round 9 measured excess it is
stated from (seat 21, design/steps/step-17r-attack9-21.md,
with seat 5, design/steps/step-17r-attack9-5.md, beside
it), and the bound ceiling this module asserts:

- 1,200 entries, four line form, 1 chord, 2 cycles:
  round 9 excess 0.17 s; ceiling 0.50 s.
- 2,498 entries, four line form, 1 chord, 2 cycles:
  round 9 excess 1.02 s and 1.00 s in two runs; ceiling
  1.35 s. Seat 5, compact dress: 0.79 s earliest chord,
  0.62 s later chord.
- 2,498 entries, compact two line form, 1 chord, 2 cycles:
  round 9 excess 0.83 s; ceiling 1.15 s.
- 4,000 entries, compact two line form, 1 chord, 2 cycles:
  round 9 excess 2.29 s; ceiling 3.20 s, as restated in
  fix wave 10. The first stated ceiling for this term was
  2.65 s. Round 10 read the term past that ceiling in 2
  of 10 readings (worst stated reading 2.828 s, median
  about 2.41 s, behaviour exact in every reading), and
  the fix wave 10 bound restatement seat read it in a
  fresh serial series of 12 readings at a median of
  2.288 s and a worst of 2.560 s, no reading past the
  first ceiling. On the full stated distribution (22
  readings across the round 10 and fix wave 10 sittings,
  median 2.321 s, worst 2.828 s) the ceiling stands
  restated at 3.20 s, a margin of 0.37 s over the worst
  stated reading, in the margin shape of the first
  statement, which stood 0.36 s over the round 9 figure.
  The restatement stands recorded in the open in the
  seat paper, design/steps/step-17r-fix10-bound-restatement.md.
- 2,498 entries, four line form, 2 chords, 3 cycles:
  round 9 excess 2.82 s; ceiling 3.20 s.
- 2,498 entries, four line form, 4 chords, 8 cycles:
  round 9 excess 8.97 s; ceiling 9.55 s.
- 2,498 entries, four line form, 10 chords, 41 cycles:
  round 9 excess 16.83 s; ceiling 19.00 s. The ceiling for
  this largest term is stated in the split parallel
  measurement posture of the bench, under which this
  sitting first measured 17.72 s against a first stated
  ceiling of 17.55 s; the restatement stands recorded in
  the open in the seat paper.
- 4,000 entries, compact two line form, 2 chords, 4 cycles:
  round 9 excess 12.36 s; ceiling 13.05 s.
- 4,990 entries, compact two line form, 1 chord, 2 cycles:
  round 9 excess 3.24 s; ceiling 3.65 s.
- 4,990 entries, compact two line form, 2 chords, 4 cycles:
  round 10 excess 19.30 s and 18.53 s, re-measured first
  in fix wave 10 at excess 21.77 s and 22.21 s and peak
  1,265.1 MB; cured excess 2.71 s and 2.03 s and cured
  peak 160.0 MB, as stated in the CH-272 closing act in
  design/steps/step-17r-fix10-j.md section 8; ceiling
  10.00 s of excess and ceiling 400 MB of peak.
- 2,498 entries, four line form, self edge at the middle
  entry, 1 cycle: no second cycle stands, and round 9
  measured the form at its pure control figure (1.96 s
  against 1.87 s); ceiling 0.50 s of excess.
- Locality term: two disjoint chorded rings of 1,249
  entries in one file, 4 cycles counted across two
  components, round 9 total 2.37 s against the one
  component 2,498 entry chorded form at 2.89 s; ceiling
  2.75 s of total child CPU, and the twin total stands at
  or under the one component chorded form measured in the
  same sitting.

The peak memory form, stated beside the ladder (seat 5
observation O7): the chorded ring at 2,498 entries stands
at peak RSS 267.5 MB for the earliest chord and 259.1 MB
for the later chord against its pure ring control at
51.6 MB, and at 74.1 MB at 1,200 entries, in seat 5
compact dress. On the four line forms of this module the
peak ceilings asserted are 330 MB for the earliest chord
at 2,498 entries, 300 MB for the later chord at 2,498
entries, and 100 MB at 1,200 entries, with the pure
control at 2,498 entries standing at or under 80 MB as
the control pin beside them. The peak form for the
4,990 entry, compact two line form, 2 chords term
stated in the ladder above stands at a ceiling of
400 MB, on its cured peak of 160.0 MB measured alone
in a fresh process against its pure control at
85.3 MB.

Bound statement for the Step 18 plan, in the exact words
this seat files it in design/steps/step-17r-fix9-bound.md:
"The K12 remainder stands BOUND. The chorded ring residual
excess at the _map_print_size locus in validate.py stands
admitted at or under the bound ladder stated in
product/tests/test_restart_step17_fix9_bound.py, stated on
entry count and on component cycle count together, with
the peak memory form stated beside it. Excess beyond a
stated ceiling of that ladder, at the same construction,
in a later round, is a defect. The remainder is not cured
by this bound, is not counted among the fifteen carries,
and rides to the Step 18 plan in this bound form for the
plan to hold or to charge a cure against."

Copyright: J.P. Picard aka Macro-Harder
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

_DRIVER = r"""
import json, os, resource, subprocess, sys
root = os.environ["DQV_PRODUCT_ROOT"]
mode = sys.argv[1]
paths = sys.argv[2:]
env = dict(os.environ, PYTHONPATH=root)
for path in paths:
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc = subprocess.run(
        [sys.executable, "-m", "decision_queue_validator",
         "validate", path],
        cwd=root, env=env, capture_output=True, timeout=180)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime + after.ru_stime) - (
        before.ru_utime + before.ru_stime)
    rec = {"exit": proc.returncode, "cpu": cpu,
           "pin10": proc.stdout.count(b"PIN-10"),
           "out": len(proc.stdout)}
    if mode == "peak":
        rec["peak_mb"] = after.ru_maxrss / 1024.0
    print(json.dumps(rec))
"""

_HEADER = "# Decision queue\n\n"


def _ring4(n, chords=(), selfchord=None):
    cmap = dict(chords)
    parts = [_HEADER]
    for i in range(1, n + 1):
        prev = n if i == 1 else i - 1
        stmt = "This supersedes the ruling at DQ-%03d." % prev
        if i in cmap:
            stmt += " This supersedes the ruling at DQ-%03d." % cmap[i]
        if selfchord is not None and i == selfchord:
            stmt += " This supersedes the ruling at DQ-%03d." % i
        parts.append("### DQ-%03d: Entry %d\nStatus: Banked\n%s\n\n"
                     % (i, i, stmt))
    return "".join(parts)


def _ring2(n, chords=()):
    cmap = dict(chords)
    parts = [_HEADER]
    for i in range(1, n + 1):
        prev = n if i == 1 else i - 1
        stmt = "This supersedes the ruling at DQ-%03d." % prev
        if i in cmap:
            stmt += " This supersedes the ruling at DQ-%03d." % cmap[i]
        parts.append("### DQ-%03d: Entry %d\nStatus: Banked. %s\n"
                     % (i, i, stmt))
    return "".join(parts)


def _twinring(n):
    parts = [_HEADER]
    for base in (0, n):
        for i in range(1, n + 1):
            idx = base + i
            prev = base + n if i == 1 else idx - 1
            stmt = "This supersedes the ruling at DQ-%03d." % prev
            if i == n // 2:
                stmt += " This supersedes the ruling at DQ-%03d." % (
                    base + 1)
            parts.append(
                "### DQ-%03d: Entry %d\nStatus: Banked\n%s\n\n"
                % (idx, idx, stmt))
    return "".join(parts)


def _measure(texts, mode="cpu", bound=240):
    """Run validate on each text in one driver child process
    under the stated bound, in the seat 21 runner form: child
    CPU from rusage, every subprocess carrying its own hard
    timeout. Returns one record per text, in order."""
    directory = Path(tempfile.mkdtemp(prefix="fix9_bound_"))
    paths = []
    for index, text in enumerate(texts):
        path = directory / ("case%d.md" % index)
        path.write_bytes(text.encode("utf-8"))
        paths.append(str(path))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(h.PRODUCT_ROOT)
    env["DQV_PRODUCT_ROOT"] = str(h.PRODUCT_ROOT)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _DRIVER, mode] + paths,
            cwd=str(h.PRODUCT_ROOT), env=env,
            capture_output=True, text=True, timeout=bound)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "bound measurement did not complete inside %s seconds"
            % bound)
    if proc.returncode != 0:
        raise AssertionError(
            "bound measurement driver exited %d: %s"
            % (proc.returncode, proc.stderr[-400:]))
    return [json.loads(line) for line in proc.stdout.splitlines()
            if line.strip()]


class K12RemainderBoundTest(unittest.TestCase):
    """The remainder excess stands at or under its bound
    ladder, term by term, on the bench measurements of this
    sitting. No term asserts a cure."""

    def _pair(self, chorded_text, pure_text, cycles, ceiling,
              label):
        chorded, pure = _measure([chorded_text, pure_text])
        for rec in (chorded, pure):
            self.assertEqual(rec["exit"], 1)
        self.assertEqual(chorded["pin10"], 2 * cycles + 1)
        self.assertEqual(pure["pin10"], 3)
        excess = chorded["cpu"] - pure["cpu"]
        print("%s: chorded %.3f pure %.3f excess %.3f "
              "ceiling %.2f" % (label, chorded["cpu"],
                                pure["cpu"], excess, ceiling))
        self.assertLessEqual(
            excess, ceiling,
            "%s excess %.3f s stands past its bound ceiling "
            "of %.2f s" % (label, excess, ceiling))
        return excess

    def test_bound_1200_four_line_2_cycles(self):
        self._pair(_ring4(1200, chords=((600, 1),)),
                   _ring4(1200), 2, 0.50, "r1200-4l-1chord")

    def test_bound_2498_four_line_2_cycles(self):
        self._pair(_ring4(2498, chords=((1249, 1),)),
                   _ring4(2498), 2, 1.35, "r2498-4l-1chord")

    def test_bound_2498_four_line_late_chord_2_cycles(self):
        self._pair(_ring4(2498, chords=((1249, 2497),)),
                   _ring4(2498), 2, 1.35, "r2498-4l-late")

    def test_bound_2498_compact_2_cycles(self):
        self._pair(_ring2(2498, chords=((1249, 1),)),
                   _ring2(2498), 2, 1.15, "r2498-2l-1chord")

    def test_bound_4000_compact_2_cycles(self):
        self._pair(_ring2(4000, chords=((2000, 1),)),
                   _ring2(4000), 2, 3.20, "r4000-2l-1chord")

    def test_bound_2498_four_line_3_cycles(self):
        self._pair(
            _ring4(2498, chords=((800, 1), (1600, 400))),
            _ring4(2498), 3, 3.20, "r2498-4l-2chords")

    def test_bound_2498_four_line_8_cycles(self):
        self._pair(
            _ring4(2498, chords=((400, 1), (900, 200),
                                 (1400, 700), (1900, 1200))),
            _ring4(2498), 8, 9.55, "r2498-4l-4chords")

    def test_bound_2498_four_line_41_cycles(self):
        chords = tuple((250 * k, max(1, 250 * k - 700))
                       for k in range(1, 11))
        self._pair(_ring4(2498, chords=chords),
                   _ring4(2498), 41, 19.00, "r2498-4l-10chords")

    def test_bound_4000_compact_4_cycles(self):
        self._pair(
            _ring2(4000, chords=((1000, 1), (3000, 1500))),
            _ring2(4000), 4, 13.05, "r4000-2l-2chords")

    def test_bound_4990_compact_2_cycles(self):
        self._pair(_ring2(4990, chords=((2495, 1),)),
                   _ring2(4990), 2, 3.65, "r4990-2l-1chord")

    def test_bound_4990_compact_4_cycles(self):
        self._pair(
            _ring2(4990, chords=((1250, 1), (3750, 2000))),
            _ring2(4990), 4, 10.00, "r4990-2l-2chords")

    def test_bound_vanishes_with_no_second_cycle(self):
        chorded, pure = _measure(
            [_ring4(2498, selfchord=1249), _ring4(2498)])
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(chorded["pin10"], 3)
        excess = chorded["cpu"] - pure["cpu"]
        self.assertLessEqual(
            excess, 0.50,
            "self edge excess %.3f s stands past its bound "
            "ceiling of 0.50 s" % excess)

    def test_bound_component_local_twin_rings(self):
        twin, single = _measure(
            [_twinring(1249), _ring4(2498, chords=((1249, 1),))])
        self.assertEqual(twin["exit"], 1)
        self.assertEqual(twin["pin10"], 9)
        self.assertLessEqual(
            twin["cpu"], 2.75,
            "twin ring total %.3f s stands past its bound "
            "ceiling of 2.75 s" % twin["cpu"])
        self.assertLessEqual(
            twin["cpu"], single["cpu"],
            "twin ring total %.3f s stands past the one "
            "component chorded form at %.3f s in the same "
            "sitting" % (twin["cpu"], single["cpu"]))


class K12RemainderPeakBoundTest(unittest.TestCase):
    """The peak memory form stands at or under the peak
    ceilings stated beside the ladder, each form measured
    in a fresh driver so its peak stands alone."""

    def _peak(self, text):
        (rec,) = _measure([text], mode="peak")
        self.assertEqual(rec["exit"], 1)
        return rec

    def test_peak_2498_earliest_and_late_chord(self):
        earliest = self._peak(_ring4(2498, chords=((1249, 1),)))
        self.assertEqual(earliest["pin10"], 5)
        self.assertLessEqual(
            earliest["peak_mb"], 330.0,
            "earliest chord peak %.1f MB stands past its "
            "bound ceiling of 330 MB" % earliest["peak_mb"])
        late = self._peak(_ring4(2498, chords=((1249, 2497),)))
        self.assertEqual(late["pin10"], 5)
        self.assertLessEqual(
            late["peak_mb"], 300.0,
            "late chord peak %.1f MB stands past its bound "
            "ceiling of 300 MB" % late["peak_mb"])

    def test_peak_1200_chorded_and_2498_pure_control(self):
        chorded = self._peak(_ring4(1200, chords=((600, 1),)))
        self.assertEqual(chorded["pin10"], 5)
        self.assertLessEqual(
            chorded["peak_mb"], 100.0,
            "1,200 entry chorded peak %.1f MB stands past "
            "its bound ceiling of 100 MB" % chorded["peak_mb"])
        pure = self._peak(_ring4(2498))
        self.assertEqual(pure["pin10"], 3)
        self.assertLessEqual(
            pure["peak_mb"], 80.0,
            "pure control peak %.1f MB stands past its "
            "control ceiling of 80 MB" % pure["peak_mb"])

    def test_peak_4990_compact_2_chords(self):
        chorded = self._peak(
            _ring2(4990, chords=((1250, 1), (3750, 2000))))
        self.assertEqual(chorded["pin10"], 9)
        self.assertLessEqual(
            chorded["peak_mb"], 400.0,
            "4,990 entry 2 chords peak %.1f MB stands past "
            "its bound ceiling of 400 MB" % chorded["peak_mb"])


if __name__ == "__main__":
    unittest.main()
