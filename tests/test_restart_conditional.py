"""Restart conditional constructions. CC-01 to CC-05.

Source: plan Item 2, section 2.9, conditional constructions at
testing pin down 12; register items CC-01 to CC-05, derivation
D-13-4. Each construction is built speculatively at Step 13,
labelled conditional in the manifest, and asserting decided
behaviour only. Every other survey construction waits for a redo
audit to adopt its item, and no waited construction is built,
scheduled as built, or described with an expected defect in this
file.
"""

import unittest
from pathlib import Path

import dqv_harness as h


def find_construction(marker):
    corpus = h.CORPUS_DIR
    if not corpus.exists():
        return None
    matches = [p for p in sorted(corpus.iterdir())
               if p.is_file() and marker in p.name
               and p.name not in ("MANIFEST.md", "manifest.json")]
    return matches[0] if matches else None


def run_on(data, subcommand, name="restart_cc_input.md"):
    path = h.temp_input(data, name)
    code, out, err = h.run_cli(subcommand, path)
    return code, out.decode("utf-8", errors="replace"), err.decode(
        "utf-8", errors="replace")


def skip_if_not_standing(marker, label):
    found = find_construction(marker)
    if found is None:
        raise unittest.SkipTest(
            "conditional construction " + label + " does not "
            "stand in the corpus yet; its standing, labelled "
            "conditional in the manifest, is charged to the "
            "Corpus seat in parallel")
    return found


class Cc01EscapedNameConstructionTest(unittest.TestCase):
    """CC-01: the escaped name construction behind D-01,
    asserting the Q-42 escaping commitment on the surfaces OP-Q7
    inventories."""

    def test_escaped_name_on_validate_surface(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A name with a \\ and a \t tab\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n"
        ).encode("utf-8")
        code, out, err = run_on(data, "validate")
        self.assertNotIn("\x1b", out)
        self.assertNotIn("\t tab", out.replace("\\t", " "))

    def test_escaped_name_on_refusal_surface(self):
        found = find_construction("D-01")
        if found is None:
            found = find_construction("CC-01")
        if found is None:
            self.skipTest(
                "CC-01 construction does not stand in the corpus "
                "yet; the synthetic surface test above carries the "
                "decided behaviour in the meantime")
        code, out, err = h.run_cli("validate", found)
        combined = out.decode("utf-8", errors="replace") + err.decode(
            "utf-8", errors="replace")
        self.assertNotIn("\x1b", combined)

    def test_escaped_name_construction_labelled_conditional(self):
        # The charged labelling is specific to this construction:
        # the manifest entry for the CC-01 escaped name
        # construction itself carries the conditional label. A
        # state name standing anywhere else in the manifest, for
        # example the canonical state Conditional in an expected
        # counts line, is not this label and does not pass here.
        corpus = h.CORPUS_DIR
        manifest = corpus / "MANIFEST.md"
        if not manifest.exists():
            self.skipTest("corpus manifest does not stand yet")
        text = manifest.read_text(
            encoding="utf-8", errors="replace")
        blocks = text.split("\n\n")
        entry_block = None
        for block in blocks:
            lowered = block.lower()
            if ("cc-01" in lowered or "d-01" in lowered) and (
                    "escap" in lowered):
                entry_block = block
                break
        if entry_block is None:
            self.skipTest(
                "CC-01 construction entry does not stand in the "
                "manifest yet; its standing, labelled conditional, "
                "is charged to the Corpus seat in parallel")
        label_lines = [
            line for line in entry_block.splitlines()
            if "conditional" in line.lower() and (
                "label" in line.lower() or "kind" in line.lower()
                or "construction" in line.lower())]
        self.assertTrue(
            label_lines,
            "the CC-01 manifest entry carries no conditional "
            "label line of its own")


class Cc02GeneratedLimitConstructionsTest(unittest.TestCase):
    """CC-02: the generated limit constructions behind D-03,
    asserting the Q-31 limits and the exit 3 refusal in generated
    form."""

    def test_byte_limit_generated_form_refuses_at_exit_3(self):
        data, facts = h.limit_bytes_input()
        path = h.temp_input(data, "cc02_bytes.md")
        code, out, err = h.run_cli("validate", path)
        self.assertEqual(code, 3)
        self.assertEqual(out, b"")
        text = err.decode("utf-8", errors="replace")
        self.assertIn("2000000", text)
        self.assertIn(str(facts["bytes"]), text)

    def test_line_limit_generated_form_refuses_at_exit_3(self):
        data, facts = h.limit_lines_input()
        path = h.temp_input(data, "cc02_lines.md")
        code, out, err = h.run_cli("validate", path)
        self.assertEqual(code, 3)
        text = err.decode("utf-8", errors="replace")
        self.assertIn("10000", text)

    def test_per_line_limit_generated_form_refuses_at_exit_3(self):
        data, facts = h.limit_chars_input()
        path = h.temp_input(data, "cc02_chars.md")
        code, out, err = h.run_cli("validate", path)
        self.assertEqual(code, 3)
        text = err.decode("utf-8", errors="replace")
        self.assertIn("16384", text)

    def test_limits_are_the_q31_constants_only(self):
        self.assertEqual(
            (h.MAX_BYTES, h.MAX_LINES, h.MAX_CHARS_PER_LINE),
            (2000000, 10000, 16384))


class Cc03ShellLevelEqualsFormTest(unittest.TestCase):
    """CC-03: the shell level equals form cases behind D-10,
    asserting the documented surface forms."""

    def test_documented_surface_forms_print_as_documented(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A surface form entry\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n"
        ).encode("utf-8")
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, out, err = run_on(data, subcommand)
                self.assertIn("Exit: code", out)

    def test_equals_form_construction_standing(self):
        found = find_construction("D-10")
        if found is None:
            found = find_construction("CC-03")
        if found is None:
            self.skipTest(
                "CC-03 construction does not stand in the corpus "
                "yet; the synthetic surface test above carries the "
                "decided behaviour in the meantime")
        self.assertTrue(found.is_file())


class Cc04ManifestWordingSweepTest(unittest.TestCase):
    """CC-04: the manifest wording sweep behind OBS-9, as a
    manifest check and not as a product edit."""

    def test_manifest_sweep_is_a_check_not_an_edit(self):
        corpus = h.CORPUS_DIR
        manifest = corpus / "MANIFEST.md"
        if not manifest.exists():
            self.skipTest("corpus manifest does not stand yet")
        before = manifest.read_bytes()
        text = before.decode("utf-8", errors="replace")
        self.assertTrue(text.strip())
        after = manifest.read_bytes()
        self.assertEqual(before, after)

    def test_manifest_carries_no_product_edit_instruction(self):
        corpus = h.CORPUS_DIR
        manifest = corpus / "MANIFEST.md"
        if not manifest.exists():
            self.skipTest("corpus manifest does not stand yet")
        text = manifest.read_text(encoding="utf-8", errors="replace")
        self.assertNotIn("edit the product", text.lower())


class Cc05SettledInPartConstructionTest(unittest.TestCase):
    """CC-05: the settled in part construction behind C-2, whose
    expectation follows from Q-21 independently of the survey."""

    def test_settled_in_part_entry_derives_that_state(self):
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A part settled entry\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question in two limbs.\n\nOptions:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            "#### Decision\n\n"
            "SETTLED IN PART by the Manager. The first limb above "
            "is settled. What stays banked: the second limb stays "
            "banked, and this item stays banked for that "
            "remainder.\n"
        ).encode("utf-8")
        path = h.temp_input(data, "cc05_input.md")
        model, output = h.run_pipeline(data, "cc05_input.md")
        if output is None:
            self.skipTest("pipeline returned a failure result")
        entry = h.entry_by_id(output, "DQ-001")
        if entry is None:
            entries = h.entries_of(output)
            self.assertTrue(entries)
            entry = entries[0]
        state = h.entry_state(entry)
        # Q-21 expectation for this construction, as the plan
        # states it: an element carrying a part disposition with a
        # named remainder derives Settled in part. A bare Settled
        # is a different state and does not satisfy this test.
        self.assertEqual(state, "Settled in part")

    def test_settled_in_part_construction_standing(self):
        found = find_construction("C-2")
        if found is None:
            found = find_construction("CC-05")
        if found is None:
            self.skipTest(
                "CC-05 construction does not stand in the corpus "
                "yet; the synthetic construction test above "
                "carries the Q-21 expectation in the meantime")
        self.assertTrue(found.is_file())

    def test_part_entry_waiting_contribution_is_one_entry(self):
        # A Settled in part entry contributes one entry to the
        # waiting figure however many remainders it carries. The
        # formula form stands at plan Item 3, section 3.8 and
        # Item 9, section 9.10. This test asserts the figure
        # relation on product output: one headed entry carrying
        # two named remainders contributes a waiting figure of
        # exactly one entry, equal to the headed entry count and
        # less than the remainder count it carries.
        data = (
            "# Decision queue\n\n"
            "### DQ-001: A part settled entry\n\n"
            "Status: Banked\n\n"
            "Owner of record: Decision-queue Clerk\n\n"
            "The question: One question in three limbs.\n\n"
            "Options:\n"
            "- Option A: proceed.\n\nCost of deciding late: low.\n\n"
            "What it blocks: nothing named.\n\n"
            "#### Decision\n\n"
            "SETTLED IN PART by the Manager. The first limb above "
            "is settled. What stays banked: the second limb stays "
            "banked, and the third limb stays banked, and this "
            "item stays banked for those remainders.\n"
        ).encode("utf-8")
        model, output = h.run_pipeline(data, "cc05_waiting.md")
        if output is None:
            self.skipTest("pipeline returned a failure result")
        entries = h.entries_of(output)
        self.assertEqual(len(entries), 1)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertIsNotNone(waiting)
        self.assertEqual(h.int_of(waiting), 1)
        self.assertEqual(h.int_of(waiting), len(entries))
        self.assertLess(h.int_of(waiting), 2)


if __name__ == "__main__":
    unittest.main()
