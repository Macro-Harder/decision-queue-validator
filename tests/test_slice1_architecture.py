"""Slice 1, architecture group.

The group pins three things and no more: module boundary crossings
occur only in the handoff types; no count is recounted past validate;
and no count quantity stands without its unit in its type or in its
field name. Pins that other rows own stand in the groups that own
them: the entry module delegation and the shell main entry in the
Slice 5 group, the purity of each core module in that module own
slice group, the element tuple shape in the Slice 2 group, and the
criterion 1 figures with their single carriage in the Slice 3
reconciliation group.
"""

import ast
import importlib
import inspect
import unittest

import dqv_harness as h


def _signature_params(fn):
    return list(inspect.signature(fn).parameters)


class ArchitectureBoundariesTest(unittest.TestCase):

    def test_package_modules_exist(self):
        package = importlib.import_module(h.PACKAGE)
        self.assertIsNotNone(package)
        for part in ("parse", "validate", "render", "shell"):
            module = h.import_module(part)
            self.assertIsNotNone(module, part)

    def test_shell_holds_the_output_form_edition(self):
        shell = h.import_module("shell")
        edition = h.get(shell, "OUTPUT_FORM_EDITION", "output_form_edition",
                        "EDITION")
        self.assertIsNotNone(edition)

    def test_parse_receives_input_and_limits_and_no_vocabulary(self):
        parse_module = h.import_module("parse")
        params = _signature_params(h.parse_function(parse_module))
        lowered = [name.lower() for name in params]
        self.assertTrue(any("input" in name for name in lowered))
        self.assertTrue(any("limit" in name for name in lowered))
        self.assertFalse(any("vocab" in name for name in lowered))

    def test_validate_receives_model_and_vocabulary(self):
        validate_module = h.import_module("validate")
        params = _signature_params(h.validate_function(validate_module))
        lowered = [name.lower() for name in params]
        self.assertTrue(any("vocab" in name for name in lowered))
        self.assertTrue(any(
            "model" in name or "queue" in name or "parsed" in name
            for name in lowered))
        self.assertFalse(any(name == "input" or name == "raw_bytes"
                             for name in lowered))

    def test_render_receives_the_validate_output_only(self):
        render_module = h.import_module("render")
        for name in ("render_validate", "render_summary", "render_output"):
            fn = getattr(render_module, name, None)
            if callable(fn):
                params = _signature_params(fn)
                self.assertLessEqual(len(params), 2, name)
                lowered = [item.lower() for item in params]
                self.assertFalse(any("model" in item or "parse" in item
                                     or "bytes" in item or "text" in item
                                     for item in lowered), name)
                return
        self.fail("no render function was found on the render module")

    def test_tuple_construction_lives_in_parse_only(self):
        for part in ("validate", "render", "shell"):
            source = h.module_source(part)
            tree = ast.parse(source)
            class_names = [node.name for node in ast.walk(tree)
                           if isinstance(node, ast.ClassDef)]
            self.assertNotIn("StatusBearingElement", class_names, part)
            self.assertNotIn("ElementTuple", class_names, part)

    def test_headed_entry_count_is_its_own_type(self):
        type_cls = h.find_type("HeadedEntryCount")
        self.assertIsNotNone(type_cls)
        _model, output = h.cached_pipeline("S5")
        total = h.entry_total(output)
        self.assertIs(type(total), type_cls)
        self.assertNotIsInstance(total, bool)
        self.assertEqual(h.int_of(total), 1)

    def test_render_prints_validate_counts_without_recounting(self):
        _model, output = h.cached_pipeline("S5")
        altered = h.deepcopy_value(output)
        recon = h.reconciliation_of(altered)
        counts = h.canonical_counts(altered)
        self.assertEqual(counts.get("Open"), 1)
        if isinstance(recon, dict):
            rows = recon.get("canonical_counts") or \
                recon.get("entries_per_canonical_state") or {}
            if isinstance(rows, dict):
                rows["Open"] = 41
            else:
                recon["canonical_counts"] = {"Open": 41}
        else:
            try:
                recon.canonical_counts = {"Open": 41}
            except Exception as exc:
                self.fail("reconciliation counts are not settable "
                          "on this value form: " + str(exc))
        # The pin binds in every path: the altered count must read
        # back as 41 before the render is made, so a value form whose
        # counts cannot be altered fails here and never passes as a
        # skip.
        self.assertEqual(h.canonical_counts(altered).get("Open"), 41)
        text = h.render_text(altered, "render")
        self.assertIn("41", text)

    def test_no_conversion_between_count_quantities(self):
        for part in ("parse", "validate", "render", "shell"):
            source = h.module_source(part)
            tree = ast.parse(source)
            fn_names = [node.name.lower() for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef)]
            for name in fn_names:
                self.assertNotIn("convert", name, part + " defines " + name)
                self.assertNotIn("to_headed", name, part)
                self.assertNotIn("to_phrasing", name, part)


class NoDesignReferencesInShippedCodeTest(unittest.TestCase):
    """Step 19 R-17: shipped code names no design document and
    no design pin at the two charged sites.

    The shell module head cited a design brief by file name and
    section, and the parse module's assessment closure docstring
    named a design pin. Both are reworded so the code stands on
    its own words, keeping its meaning: the shell duties list
    stands whole, and the assessment closure element keeps its
    name and its form.
    """

    def test_shell_docstring_names_no_design_document(self):
        source = h.module_source("shell")
        self.assertNotIn("DESIGN-BRIEF", source)
        self.assertNotIn("DESIGN-PLAN", source)
        self.assertIn("argument handling for the two", source)
        self.assertIn("reading the input once as bytes", source)

    def test_parse_assessment_closure_names_no_design_pin(self):
        source = h.module_source("parse")
        self.assertNotIn("pin 14", source.lower())
        self.assertIn("assessment closure element of a paragraph",
                      source)
        self.assertIn("Closed as decided under DQ-148", source)


if __name__ == "__main__":
    unittest.main()
