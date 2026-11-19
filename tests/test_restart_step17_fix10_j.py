"""Restart Step 17 fix wave 10, Fix Seat J tests.

Charges CH-271 and CH-272, Cluster J, the cost family of
round 10, ruled TO FIX at section 83 rulings (c) and (f) of
design/steps/step-17r-record.md, test first, each charge's
first step an independent re-measurement on the bench.

CH-271 (seat 18 finding F10-18-1, Medium): repeated long
lines each closed by a colon pay a constant factor of
about 3.4 times the colon free cost at the same byte size.
The charged constructions stand below in the seat 18
probe10 form: lines of 16,383 letter characters closed by
a colon, 30 lines at 491,782 bytes and 122 lines at
1,999,202 bytes, against colon free lines of 16,384 letter
characters at the same line counts and byte sizes. The
cost tests state their terms on the constructions: the
122 line form completes inside a 4 second harness bound
(the bound stands as the test harness timeout, not as an
asserted duration), and the 30 line form's median cost
stands at or under 1.60 times its colon free twin's median
in the same sitting, each median of three in process runs
in the seat 18 probe form. The behaviour pin stands
beside them: every colon form and colon free form carries
exactly the one PD-R7 Note of the base file, before and
after any cure.

CH-272 (seat 21 finding A10-21-1, Medium): the uncovered
construction 4,990 compact entries, 2 chords, 4 cycles,
measured in round 10 at an excess of 19.30 s and 18.53 s
of child CPU against its pure control and a peak of
1,264.3 MB against the control peak of 84.6 MB, one step
past the governed bound ladder of
product/tests/test_restart_step17_fix9_bound.py on the
entry axis. The bound tests below state the cured
construction's terms in that ladder's form: the excess,
chorded child CPU minus pure control child CPU in the
same sitting, stands at or under 10.00 s, and the chorded
peak, measured alone in a fresh driver, stands at or
under 400 MB, with the construction's behaviour (exit 1,
4 cycles counted by 9 PIN-10 occurrences, the pure
control at 3) standing as the pin the measurement rides
on. The neighbouring ladder term at 4,000 compact
entries, 2 chords, 4 cycles stands as a behaviour pin,
its governed ceiling standing in the bound module itself.

Cost figures in this module stand as measurements, taken
in a serial pass; no figure here is a logic verdict.

Copyright: J.P. Picard aka Macro-Harder
"""

import hashlib
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import dqv_harness as h

_HEADER = "# Decision queue\n\n"

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
        cwd=root, env=env, capture_output=True, timeout=300)
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

_PIPE_DRIVER = r"""
import hashlib, json, os, sys
sys.path.insert(0, os.environ["DQV_PRODUCT_ROOT"])
sys.path.insert(
    0, os.path.join(os.environ["DQV_PRODUCT_ROOT"], "tests"))
import dqv_harness as h
with open(sys.argv[1], "rb") as f:
    data = f.read()
_m, out = h.run_pipeline(data)
rows = []
for f in h.findings_of(out):
    rows.append((h.text_of(h.get(f, "rule_id", "rule")),
                 h.finding_severity(f), h.finding_statement(f)))
print(json.dumps({
    "ok": out is not None,
    "digest": hashlib.sha256(
        repr(rows).encode("utf-8")).hexdigest()}))
"""

_BASE = _HEADER + (
    "### DQ-1: Sample question\n\nStatus: Banked\n\n"
    "This question is waiting for a decision.\n\n"
    "Question: Which option should we take?\n\n"
    "Options: Option A, Option B\n\n"
    "Cost of deciding late: Work stays blocked.\n\n"
    "Blocks: DQ-999\n") + "\n"

_PIN_DIGEST = ("9deb2723c2d3a043ff2cd32afab201a234fbd58f0"
               "d4d294d10d5f6b437cd856e")


def _colon_form(lines, closed):
    if closed:
        return "".join([_BASE] + ["x" * 16383 + ":\n"] * lines)
    return "".join([_BASE] + ["x" * 16384 + "\n"] * lines)


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


def _measure(texts, mode="cpu", bound=360):
    directory = Path(tempfile.mkdtemp(prefix="fix10_j_"))
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
            "measurement did not complete inside %s seconds"
            % bound)
    if proc.returncode != 0:
        raise AssertionError(
            "measurement driver exited %d: %s"
            % (proc.returncode, proc.stderr[-400:]))
    return [json.loads(line) for line in proc.stdout.splitlines()
            if line.strip()]


def _findings_digest(text):
    _m, out = h.run_pipeline(text.encode("utf-8"))
    if out is None:
        raise AssertionError("pipeline returned the failure result")
    rows = []
    for f in h.findings_of(out):
        rows.append((h.text_of(h.get(f, "rule_id", "rule")),
                     h.finding_severity(f),
                     h.finding_statement(f)))
    return hashlib.sha256(repr(rows).encode("utf-8")).hexdigest()


class Ch271ColonClosedBehaviourPinTest(unittest.TestCase):
    """The colon closed forms and their colon free twins
    carry the base file's one PD-R7 Note, before and after
    any cure: the cure moves cost only."""

    def test_colon_forms_findings_standing(self):
        for lines in (30, 122):
            for closed in (True, False):
                self.assertEqual(
                    _findings_digest(_colon_form(lines, closed)),
                    _PIN_DIGEST,
                    "findings standing moved on the %s form at "
                    "%d lines" % ("colon closed" if closed
                                  else "colon free", lines))


class Ch271ColonClosedCostTest(unittest.TestCase):
    """The charged CH-271 constructions, as measurements."""

    def test_colon_closed_factor_at_30_lines(self):
        def median(text):
            dts = []
            for _ in range(3):
                t0 = time.time()
                _m, out = h.run_pipeline(text.encode("utf-8"))
                dts.append(time.time() - t0)
                self.assertIsNotNone(out)
            return statistics.median(dts)
        closed = median(_colon_form(30, True))
        free = median(_colon_form(30, False))
        print("colon closed 30 lines median %.3f s, colon "
              "free %.3f s, factor %.2f"
              % (closed, free, closed / free))
        self.assertLessEqual(
            closed, 1.60 * free,
            "colon closed median %.3f s stands past 1.60 "
            "times the colon free median %.3f s"
            % (closed, free))

    def test_colon_closed_122_lines_inside_bound(self):
        directory = Path(tempfile.mkdtemp(prefix="fix10_j_"))
        path = directory / "colon122.md"
        path.write_bytes(_colon_form(122, True).encode("utf-8"))
        env = dict(os.environ)
        env["PYTHONPATH"] = str(h.PRODUCT_ROOT)
        env["DQV_PRODUCT_ROOT"] = str(h.PRODUCT_ROOT)
        try:
            proc = subprocess.run(
                [sys.executable, "-c", _PIPE_DRIVER, str(path)],
                cwd=str(h.PRODUCT_ROOT), env=env,
                capture_output=True, text=True, timeout=4)
        except subprocess.TimeoutExpired:
            raise AssertionError(
                "the 122 line colon closed form did not "
                "complete inside the 4 second bound")
        if proc.returncode != 0:
            raise AssertionError(
                "pipeline driver exited %d: %s"
                % (proc.returncode, proc.stderr[-400:]))
        rec = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["digest"], _PIN_DIGEST)


class Ch272Chord4990BoundTest(unittest.TestCase):
    """The charged CH-272 construction, in the governed
    bound ladder's form, on the cured figures."""

    def test_chord2_4990_excess_bound(self):
        chorded, pure = _measure([
            _ring2(4990, chords=((1250, 1), (3750, 2000))),
            _ring2(4990)])
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(pure["exit"], 1)
        self.assertEqual(chorded["pin10"], 9)
        self.assertEqual(pure["pin10"], 3)
        excess = chorded["cpu"] - pure["cpu"]
        print("r4990-2l-2chords: chorded %.3f pure %.3f "
              "excess %.3f ceiling 10.00"
              % (chorded["cpu"], pure["cpu"], excess))
        self.assertLessEqual(
            excess, 10.00,
            "r4990-2l-2chords excess %.3f s stands past "
            "its bound ceiling of 10.00 s" % excess)

    def test_chord2_4990_peak_bound(self):
        (chorded,) = _measure(
            [_ring2(4990, chords=((1250, 1), (3750, 2000)))],
            mode="peak")
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(chorded["pin10"], 9)
        print("r4990-2l-2chords peak %.1f MB ceiling 400"
              % chorded["peak_mb"])
        self.assertLessEqual(
            chorded["peak_mb"], 400.0,
            "r4990-2l-2chords peak %.1f MB stands past its "
            "bound ceiling of 400 MB" % chorded["peak_mb"])


class Ch272NeighbourBehaviourPinTest(unittest.TestCase):
    """The neighbouring governed ladder term at 4,000
    compact entries, 2 chords, 4 cycles: its behaviour
    stands whole, before and after any cure at the
    charged construction."""

    def test_ladder_4000_compact_2chords_behaviour(self):
        chorded, pure = _measure([
            _ring2(4000, chords=((1000, 1), (3000, 1500))),
            _ring2(4000)])
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(pure["exit"], 1)
        self.assertEqual(chorded["pin10"], 9)
        self.assertEqual(pure["pin10"], 3)


if __name__ == "__main__":
    unittest.main()
