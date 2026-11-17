"""Restart Step 17 fix wave 1, Fix seat C9 tests.

Seat C9 owns product/README.md only. Each test pins one charged
README cure, written before the cure, in the Step 16 README cure
form of product/tests/test_restart_step16_fix_c.py and
product/tests/test_restart_step16_fix_g.py:

Finding 1 of seat 12 (Medium): the README exit code table states
that code 1 is also the code the Python interpreter itself
issues when the module cannot be found and the run never took
place, so the table no longer defines 1 only as a completed run
with findings. The cure states the collision without presenting
the interpreter code as a code the tool issues or can change:
the tool does not run in that event.

Finding 5 of seat 12 (Low): the README Installing section states
that a relative input path resolves against the working
directory, the rule the README already states for finding the
module.
"""

import os
import subprocess
import sys
import unittest

import dqv_harness as h

README_PATH = h.PRODUCT_ROOT / "README.md"


def readme_text():
    return README_PATH.read_text(encoding="utf-8")


def readme_flat():
    """The README text with all whitespace runs collapsed to one
    space, so a phrase stands or falls as written, wherever the
    printed lines wrap."""
    return " ".join(readme_text().split())


def section_flat(heading, next_heading):
    """One README section, flattened in the same form."""
    text = readme_text()
    start = text.find(heading)
    if start < 0:
        raise AssertionError("section missing: " + heading)
    end = text.find(next_heading, start)
    if end < 0:
        raise AssertionError("section end missing: " + next_heading)
    return " ".join(text[start:end].split())


def exit_codes_flat():
    return section_flat("## Exit codes",
                        "### If a run is withheld")


def installing_flat():
    return section_flat("## Installing it", "## Running it")


class InterpreterCodeOneCollisionTest(unittest.TestCase):
    """Finding 1 of seat 12: the exit code table names the code 1
    collision with the Python interpreter, in its bound."""

    def test_exit_code_table_states_the_collision(self):
        text = exit_codes_flat()
        self.assertIn(
            "Code 1 is also the code the Python interpreter "
            "itself issues when it cannot find the module", text)
        self.assertIn("the run never took place", text)
        self.assertIn(
            "1: the run completed and reported Error or Warning "
            "findings", text)
        self.assertIn(
            "2: the run did not take place", text)

    def test_collision_stated_without_tool_issuing_the_code(self):
        text = exit_codes_flat()
        self.assertIn(
            "That code 1 is issued by the interpreter, not by "
            "the tool", text)
        self.assertIn("the tool does not run in that event",
                      text)
        self.assertIn("the tool cannot change it", text)

    def test_module_not_found_event_exits_1_before_the_tool(self):
        text = exit_codes_flat()
        self.assertIn(
            "Code 1 is also the code the Python interpreter "
            "itself issues when it cannot find the module", text)
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", h.PACKAGE, "validate",
             str(h.corpus_path("WV-9"))],
            cwd=str(h.CORPUS_DIR), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, b"")
        self.assertIn(
            b"No module named decision_queue_validator",
            proc.stderr)


class RelativeInputPathTest(unittest.TestCase):
    """Finding 5 of seat 12: the Installing section states the
    working directory rule for a relative input path."""

    def test_installing_states_relative_path_resolution(self):
        text = installing_flat()
        self.assertIn(
            "A relative input path resolves against your "
            "current working directory", text)

    def test_installing_ties_the_rule_to_the_module_rule(self):
        text = installing_flat()
        self.assertIn(
            "the same working directory rule the README states "
            "above for finding the module", text)

    def test_relative_path_resolves_against_the_working_directory(self):
        text = installing_flat()
        self.assertIn(
            "A relative input path resolves against your "
            "current working directory", text)
        code, out, err = h.run_cli(
            "validate", "WV-9.md", cwd=h.CORPUS_DIR)
        self.assertEqual(code, 0, err)
        code, out, err = h.run_cli(
            "validate", "WV-9.md", cwd=h.PRODUCT_ROOT)
        self.assertEqual(code, 2)
        self.assertIn(b"it is missing", err)


if __name__ == "__main__":
    unittest.main()
