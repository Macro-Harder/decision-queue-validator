"""Restart Step 17 fix wave 11, Fix Seat J tests.

Charge CH-312, Cluster J, the cost family of round 11,
carrying seat 21 finding A11-21-1 (Medium, T11-21): four
chords at the compact maximum of 4,990 entries measure an
excess of 30.78 s and 29.71 s of child CPU on this VM at
8 cycles against its pure control, one step past the
staged three chord form on the chord axis, with no stated
bound term covering the construction. The charge's first
step was an independent re-measurement in the posture of
the charge (this VM under the local guard, seat 21's own
measurement form), which reproduced the growth at excess
36.10 s and 32.74 s. Test first: the tests below were
written before any cure edit and failed on the charged
construction's excess only, its behaviour pins whole.

The charged construction stands below in the seat 21
genown ring2 form: 4,990 compact entries, chords at
entries 1000, 2000, 3000, and 4000 (targets 1, 1, 1500,
and 2500), 8 cycles counted by 17 PIN-10 occurrences,
output 7,180,462 bytes in this module's driver form,
against its pure control at 3 PIN-10 occurrences and
6,018,320 bytes in the same form. (The runner form
figures of seat 21's paper, 7,180,473 and 6,018,323
bytes, differ by the case path length the output
prints, and by nothing else.) The bound test
states the cured construction's terms in the governed
bound ladder's form: the excess, chorded child CPU minus
pure control child CPU in the same sitting, stands at or
under 15.00 s, and the chorded peak, measured alone in a
fresh driver, stands at or under 400 MB, with the
construction's behaviour standing as the pin the
measurement rides on. The neighbouring CH-272
construction (4,990 compact entries, 2 chords, 4 cycles)
stands as a behaviour pin only: the CH-272 confirmation
stands CONFIRMED and apart from this charge in both
directions, and no part of this module re-opens it or
rests on it.

Cost figures in this module stand as measurements under
TS-1's bounded form, taken in a serial pass; no figure
here is a logic verdict, except where this module asserts
its bound ceiling, which is the bound's own form.

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


_CHORD4 = ((1000, 1), (2000, 1), (3000, 1500), (4000, 2500))
_CHORD2 = ((1250, 1), (3750, 2000))


def _measure(texts, mode="cpu", bound=360):
    directory = Path(tempfile.mkdtemp(prefix="fix11_j_"))
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


class Ch312Chord4990BehaviourPinTest(unittest.TestCase):
    """The charged construction's behaviour stands exact,
    before and after any cure: the cure moves cost only."""

    def test_chord4_4990_behaviour(self):
        chorded, pure = _measure([
            _ring2(4990, chords=_CHORD4), _ring2(4990)])
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(pure["exit"], 1)
        self.assertEqual(chorded["pin10"], 17)
        self.assertEqual(pure["pin10"], 3)
        self.assertEqual(chorded["out"], 7180462)
        self.assertEqual(pure["out"], 6018320)


class Ch312Chord4990BoundTest(unittest.TestCase):
    """The charged CH-312 construction, in the governed
    bound ladder's form, on the cured figures."""

    def test_chord4_4990_excess_bound(self):
        chorded, pure = _measure([
            _ring2(4990, chords=_CHORD4), _ring2(4990)])
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(pure["exit"], 1)
        self.assertEqual(chorded["pin10"], 17)
        self.assertEqual(pure["pin10"], 3)
        excess = chorded["cpu"] - pure["cpu"]
        print("r4990-2l-4chords: chorded %.3f pure %.3f "
              "excess %.3f ceiling 15.00"
              % (chorded["cpu"], pure["cpu"], excess))
        self.assertLessEqual(
            excess, 15.00,
            "r4990-2l-4chords excess %.3f s stands past "
            "its bound ceiling of 15.00 s" % excess)

    def test_chord4_4990_peak_bound(self):
        (chorded,) = _measure(
            [_ring2(4990, chords=_CHORD4)], mode="peak")
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(chorded["pin10"], 17)
        print("r4990-2l-4chords peak %.1f MB ceiling 400"
              % chorded["peak_mb"])
        self.assertLessEqual(
            chorded["peak_mb"], 400.0,
            "r4990-2l-4chords peak %.1f MB stands past its "
            "bound ceiling of 400 MB" % chorded["peak_mb"])


class Ch312NeighbourBehaviourPinTest(unittest.TestCase):
    """The neighbouring CH-272 construction at 4,990
    compact entries, 2 chords, 4 cycles: its behaviour
    stands whole, before and after any cure at the
    charged construction. Its confirmation stands apart
    from this charge in both directions."""

    def test_ch272_4990_compact_2chords_behaviour(self):
        chorded, pure = _measure([
            _ring2(4990, chords=_CHORD2), _ring2(4990)])
        self.assertEqual(chorded["exit"], 1)
        self.assertEqual(pure["exit"], 1)
        self.assertEqual(chorded["pin10"], 9)
        self.assertEqual(pure["pin10"], 3)


if __name__ == "__main__":
    unittest.main()
