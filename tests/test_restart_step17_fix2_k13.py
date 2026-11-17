"""Restart Step 17 fix wave 2, Fix Seat K13 tests.

Seat K13 owns two charges, ruled at section 19 of
design/steps/step-17r-record.md:

CH-30 (S17-ATK2-13-03, Low): the invalid bytes whole file
refusal names no location for the bad byte. The cure binds the
decoder known bad byte offset into the refusal, in parse.py
decode guard, on the ruling ground at flag ruling (e): the
refusal surface own practice names the measured values it knows
exactly. The four constructions are the finding paper own:
byte 0xFF prepended to the control (offset 0), a lone
continuation byte 0x80 inserted at offset 300, a truncated two
byte sequence 0xC3 appended at the end (offset 434), and the
control encoded UTF-16LE with its byte order mark (offset 0),
each run on both subcommands.

CH-28 (S17-ATK2-12-03, Low): the README Installing section
states the tool writes nothing else, and a run writes bytecode
cache files beside the package. Documentation only: the cure
corrects the Installing sentence in product/README.md to match
the measured behaviour, in the round 1 C9 documentation cure
form. The behaviour limb runs the bench construction the
triage supplement names, on a copy: the synced product copy
with its decision_queue_validator/__pycache__ directory
deleted, then one validate run on the control file recreating
the directory with seven bytecode files, one per module.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

README_PATH = h.PRODUCT_ROOT / "README.md"
PACKAGE_DIR = h.PRODUCT_ROOT / "decision_queue_validator"
MODULE_NAMES = (
    "__init__", "__main__", "parse", "render", "shell",
    "types", "validate",
)


def readme_text():
    return README_PATH.read_text(encoding="utf-8")


def section_flat(heading, next_heading):
    """One README section, flattened in the C9 form."""
    text = readme_text()
    start = text.find(heading)
    if start < 0:
        raise AssertionError("section missing: " + heading)
    end = text.find(next_heading, start)
    if end < 0:
        raise AssertionError("section end missing: " + next_heading)
    return " ".join(text[start:end].split())


def installing_flat():
    return section_flat("## Installing it", "## Running it")


_CORE = (
    "# Decision queue\n\n"
    "### DQ-001: A sample open question\n\n"
    "Status: Banked\n\n"
    "This question is waiting for a decision.\n\n")


def _base(length):
    """A valid queue text of exactly length bytes, in ASCII."""
    text = _CORE
    remaining = length - len(text)
    if remaining < 0:
        raise AssertionError("core is longer than the base length")
    if remaining:
        text += "P" * (remaining - 1) + "\n"
    data = text.encode("ascii")
    if len(data) != length:
        raise AssertionError("base construction is off length")
    return data


def _constructions():
    """The four finding paper constructions, with their offsets.

    Returns a list of (name, data, offset) triples. The first
    three offsets are the paper measured values 0, 300, and
    434; the UTF-16 form fails at its first byte, offset 0.
    """
    base431 = _base(431)
    base434 = _base(434)
    start = b"\xff" + base431
    mid = base431[:300] + b"\x80" + base431[300:]
    trunc = base434 + b"\xc3"
    utf16 = b"\xff\xfe" + base431.decode("ascii").encode("utf-16-le")
    return [
        ("badutf-start", start, 0),
        ("badutf-mid", mid, 300),
        ("badutf-trunc", trunc, 434),
        ("utf16", utf16, 0),
    ]


def _run_both(data, name):
    """Run both subcommands on data written to a temp file."""
    path = h.temp_input(data, name + ".md")
    try:
        results = {}
        for subcommand in ("validate", "render"):
            code, out, err = h.run_cli(subcommand, path)
            results[subcommand] = (
                code, out.decode("utf-8", errors="replace"),
                err.decode("utf-8", errors="replace"))
        return results
    finally:
        Path(path).unlink(missing_ok=True)


class InvalidBytesOffsetParseTest(unittest.TestCase):
    """CH-30 at parse level: the failure value carries the
    decoder known offset of the first invalid byte."""

    def _offset_for(self, data, name):
        result = h.run_parse(data, name + ".md")
        self.assertTrue(h.is_failure_result(result))
        kinds = h.get(result, "failure_kinds", "kinds")
        self.assertIn("invalid bytes",
                      [str(kind) for kind in h.as_list(kinds)])
        return h.get(result, "invalid_byte_offset")

    def test_parse_offset_at_start(self):
        name, data, offset = _constructions()[0]
        self.assertEqual(self._offset_for(data, name), offset)

    def test_parse_offset_in_middle(self):
        name, data, offset = _constructions()[1]
        self.assertEqual(self._offset_for(data, name), offset)

    def test_parse_offset_at_truncated_end(self):
        name, data, offset = _constructions()[2]
        self.assertEqual(self._offset_for(data, name), offset)

    def test_parse_offset_for_utf16_form(self):
        name, data, offset = _constructions()[3]
        self.assertEqual(self._offset_for(data, name), offset)


class InvalidBytesOffsetSurfaceTest(unittest.TestCase):
    """CH-30 on the refusal surface: both subcommands name the
    byte offset on the exit 3 refusal, beside the failure kind."""

    def _check_surface(self, data, name, offset):
        for subcommand, (code, out, err) in \
                _run_both(data, name).items():
            with self.subTest(construction=name,
                              subcommand=subcommand):
                self.assertEqual(code, 3, err)
                self.assertEqual(out, "")
                self.assertIn("Failure kind: invalid bytes", err)
                self.assertIn(
                    "Invalid byte offset: %d" % offset, err)

    def test_surface_offset_at_start(self):
        name, data, offset = _constructions()[0]
        self._check_surface(data, name, offset)

    def test_surface_offset_in_middle(self):
        name, data, offset = _constructions()[1]
        self._check_surface(data, name, offset)

    def test_surface_offset_at_truncated_end(self):
        name, data, offset = _constructions()[2]
        self._check_surface(data, name, offset)

    def test_surface_offset_for_utf16_form(self):
        name, data, offset = _constructions()[3]
        self._check_surface(data, name, offset)


class ReadmeInstallingBytecodeTest(unittest.TestCase):
    """CH-28: the Installing section states that a run creates
    bytecode cache files beside the package, and no longer
    states that a run writes nothing else."""

    def test_installing_states_run_creates_bytecode_cache(self):
        text = installing_flat()
        self.assertIn(
            "A run creates bytecode cache files beside the "
            "package", text)

    def test_installing_no_longer_states_writes_nothing_else(self):
        text = installing_flat()
        self.assertNotIn("writes nothing else", text)
        self.assertIn(
            "The tool never edits its input file and writes no "
            "log file and no run record", text)

    def test_installing_states_cache_place_and_bound(self):
        text = installing_flat()
        self.assertIn("__pycache__ directory", text)
        self.assertIn("one bytecode file per module", text)
        self.assertIn(
            "Nothing outside the package directory is written",
            text)

    def test_deleted_pycache_recreated_by_one_validate_run(self):
        text = installing_flat()
        self.assertIn(
            "A run creates bytecode cache files beside the "
            "package", text)
        staging = Path(tempfile.mkdtemp(prefix="dqv_k13_"))
        try:
            copy_root = staging / "product"
            shutil.copytree(PACKAGE_DIR,
                            copy_root / "decision_queue_validator")
            cache = copy_root / "decision_queue_validator" / \
                "__pycache__"
            if cache.exists():
                shutil.rmtree(cache)
            self.assertFalse(cache.exists())
            env = dict(os.environ)
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            env["PYTHONPATH"] = str(copy_root)
            env["PYTHONHASHSEED"] = str(h.SEED_ONE)
            proc = subprocess.run(
                [sys.executable, "-m", "decision_queue_validator",
                 "validate", str(h.corpus_path("WV-9"))],
                cwd=str(copy_root), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(cache.is_dir())
            stems = sorted(
                path.name.split(".")[0]
                for path in cache.glob("*.pyc"))
            self.assertEqual(stems, sorted(MODULE_NAMES))
        finally:
            shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
