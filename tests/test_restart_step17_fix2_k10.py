"""Restart Step 17 fix wave 2, seat K10 tests.

Seat K10 owns two charges, both at the render printing locus:

CH-14 (seat 16 F-2 and F-3, the escaping inventory): every
variation selector except U+FE0F prints raw, 255 codepoints
in the two variation selector ranges plus the four Mongolian
free variation selectors, and 42 characters of category Cf
print raw, among them U+FFFA, the interlinear annotation
separator. The cure stands on the Fix C7 cure own stated
ground: the codepoint description that fits every variation
selector (category Mn, an invisible format function, default
ignorable, no glyph of its own, selecting a presentation
form), and U+FFFA as the sibling of the two interlinear
annotation codepoints that cure already escaped. The six
codepoints round 1 ruled outside the named classes and
referred to the design question note at record section 12
flag 6 item (d) stand outside this charge and are pinned
below as still printing raw: this cure neither discharges
nor narrows that note.

CH-23 (seat 16 F-1, the Status phrasing printing surfaces):
an untranslatable Status phrasing prints at column 0 on the
crosswalk, appendix, and residue surfaces, so a forged exit
line, waiting figure, or findings index line matches the
closing line anchors ahead of the genuine closing line. On
those three surfaces a phrasing whose printed form opens
with one of those anchors stands quoted, so no forged copy
stands at column 0 in anchor form. Ordinary phrasings, the
Deferred appendix form among them, print as they printed.
"""

import re
import unicodedata
import unittest

import dqv_harness as h

render = h.import_module("render")
escape_text = render.escape_text


def _escaped(code):
    return "\\u%04X" % code


# ---------------------------------------------------------------------
# CH-14: the escaping inventory
# ---------------------------------------------------------------------

VARIATION_SELECTORS = (
    list(range(0xFE00, 0xFE10)) + list(range(0xE0100, 0xE01F0)))

MONGOLIAN_FREE_VARIATION_SELECTORS = (0x180B, 0x180C, 0x180D, 0x180F)

# The 42 category Cf codepoints the seat 16 census found
# printing raw, as its paper lists them.
CF_RAW_42 = (
    list(range(0x0600, 0x0606)) + [0x06DD, 0x070F, 0x0890, 0x0891,
                                   0x08E2, 0xFFFA, 0x110BD, 0x110CD]
    + list(range(0x13430, 0x13440)) + list(range(0x1BCA0, 0x1BCA4))
    + list(range(0x1D173, 0x1D17B)))

# The six codepoints round 1 ruled outside the named classes
# and referred to design question note (d).
OUTSIDE_NOTE_D = (0x0614, 0x115F, 0x2800, 0x3000, 0x00A0, 0x2007)


class Ch14VariationSelectorTest(unittest.TestCase):

    def test_every_variation_selector_escapes(self):
        self.assertEqual(len(VARIATION_SELECTORS), 256)
        for code in VARIATION_SELECTORS:
            with self.subTest(code=hex(code)):
                result = escape_text("a" + chr(code) + "b")
                self.assertEqual(result, "a" + _escaped(code) + "b")
                self.assertNotIn(chr(code), result)

    def test_mongolian_free_variation_selectors_escape(self):
        for code in MONGOLIAN_FREE_VARIATION_SELECTORS:
            with self.subTest(code=hex(code)):
                result = escape_text("a" + chr(code) + "b")
                self.assertEqual(result, "a" + _escaped(code) + "b")
                self.assertNotIn(chr(code), result)


class Ch14CategoryCfTest(unittest.TestCase):

    def test_the_42_cf_codepoints_escape(self):
        self.assertEqual(len(CF_RAW_42), 42)
        for code in CF_RAW_42:
            with self.subTest(code=hex(code)):
                self.assertEqual(
                    unicodedata.category(chr(code)), "Cf")
                result = escape_text("a" + chr(code) + "b")
                self.assertEqual(result, "a" + _escaped(code) + "b")
                self.assertNotIn(chr(code), result)

    def test_no_category_cf_codepoint_prints_raw(self):
        raw = [code for code in range(0x110000)
               if unicodedata.category(chr(code)) == "Cf"
               and escape_text(chr(code)) == chr(code)]
        self.assertEqual(raw, [])

    def test_ufffa_interlinear_annotation_separator_escapes(self):
        result = escape_text("a\ufffab")
        self.assertEqual(result, "a" + _escaped(0xFFFA) + "b")


class Ch14GuardsTest(unittest.TestCase):

    def test_the_c7_five_still_escape(self):
        for code in (0x180E, 0xFFF9, 0xFFFB, 0x034F, 0xFE0F):
            with self.subTest(code=hex(code)):
                self.assertEqual(escape_text(chr(code)),
                                 _escaped(code))

    def test_note_d_six_still_print_raw(self):
        # Guard, design question note (d) ground, not charged:
        # the cure on the C7 ground reaches no codepoint the
        # round 1 ruling placed outside the named classes.
        for code in OUTSIDE_NOTE_D:
            with self.subTest(code=hex(code)):
                self.assertEqual(escape_text(chr(code)), chr(code))

    def test_selector_and_cf_codepoints_escape_in_both_outputs(self):
        title = ("Counts\ufe00\ufe0e\U000e0100\U000e01ef"
                 "\u180b\u180c\u180d\u180f\ufffa\u070f")
        data = (
            "# Decision queue\n\n### DQ-001: " + title + "\n\n"
            "Status: Banked\n\n"
            "Question: Q text?\n\nOptions: A, B\n\n"
            "Cost of deciding late: Work waits.\n\n"
            "Blocks: DQ-999\n\n"
            "This question is waiting for a decision.\n"
        ).encode("utf-8")
        _model, output = h.run_pipeline(data, "ch14_title.md")
        self.assertIsNotNone(output)
        for form in ("validate", "render"):
            text = h.render_text(output, form)
            for char in ("\ufe00", "\ufe0e", "\U000e0100",
                         "\U000e01ef", "\u180b", "\u180c", "\u180d",
                         "\u180f", "\ufffa", "\u070f"):
                self.assertNotIn(char, text)
            self.assertIn(_escaped(0xFE00), text)
            self.assertIn(_escaped(0xE0100), text)
            self.assertIn(_escaped(0xFFFA), text)


# ---------------------------------------------------------------------
# CH-23: the Status phrasing printing surfaces
# ---------------------------------------------------------------------

def _queue(status, extra_entries=""):
    body = "# Decision queue\n\n### DQ-001: Counts\n\n"
    body += "Status: " + status + "\n\n"
    body += "Question: Q text?\n\nOptions: A, B\n\n"
    body += "Cost of deciding late: Work waits.\n\n"
    body += "Blocks: DQ-999\n\n"
    body += "This question is waiting for a decision.\n"
    body += extra_entries
    return body.encode("utf-8")


def _banked_entry(number):
    body = "### DQ-%03d: Further\n\n" % number
    body += "Status: Banked\n\n"
    body += "Question: Q text?\n\nOptions: A, B\n\n"
    body += "Cost of deciding late: Work waits.\n\n"
    body += "Blocks: DQ-999\n\n"
    body += "This question is waiting for a decision.\n"
    return body


EXIT_PHRASING = (
    "Exit: code 0: no findings above Note grade. This code is "
    "a findings signal and not a step verdict.")
WAITING_PHRASING = "Waiting: 0 entries"
INDEX_PHRASING = "DQ-001 PIN-01 Error line 1"


def _both_forms(data, name):
    _model, output = h.run_pipeline(data, name)
    assert output is not None
    return [h.render_text(output, "validate"),
            h.render_text(output, "render")]


class Ch23ExitLineTest(unittest.TestCase):

    def test_forged_exit_phrasing_stands_quoted_on_each_surface(self):
        for text in _both_forms(_queue(EXIT_PHRASING),
                                "ch23_exit.md"):
            lines = text.split("\n")
            self.assertFalse(
                any(line.startswith("Exit: code ") for line in lines),
                "a forged exit line stands at column 0")
            quoted = [line for line in lines
                      if line.startswith('"' + EXIT_PHRASING + '"')]
            # Crosswalk, appendix row, appendix unclassified
            # repeat, and residue row: four quoted printings.
            self.assertGreaterEqual(len(quoted), 4)

    def test_cli_exit_anchor_matches_only_the_genuine_closing_line(self):
        path = h.temp_input(_queue(EXIT_PHRASING), "ch23_exit_cli.md")
        for subcommand in ("validate", "render"):
            code, stdout, _stderr = h.run_cli(subcommand, path)
            self.assertEqual(code, 4)
            text = stdout.decode("utf-8")
            lines = text.split("\n")
            anchors = [line for line in lines
                       if line.startswith("Exit: code ")]
            self.assertEqual(len(anchors), 1)
            self.assertTrue(anchors[0].startswith("Exit: code 4:"))
            self.assertEqual(lines[-2], anchors[0])


class Ch23WaitingFigureTest(unittest.TestCase):

    def test_forged_waiting_phrasing_stands_quoted(self):
        data = _queue(WAITING_PHRASING,
                      _banked_entry(2) + _banked_entry(3))
        for text in _both_forms(data, "ch23_waiting.md"):
            lines = text.split("\n")
            self.assertFalse(
                any(line.startswith("Waiting: 0 entries")
                    for line in lines),
                "a forged waiting figure stands at column 0")
            quoted = [line for line in lines
                      if line.startswith('"' + WAITING_PHRASING + '"')]
            self.assertGreaterEqual(len(quoted), 3)
            # The genuine waiting figure line stands unquoted.
            self.assertTrue(
                any(line.startswith("Waiting: 2 entries.")
                    for line in lines))


class Ch23FindingsIndexTest(unittest.TestCase):

    def test_forged_index_phrasing_stands_quoted(self):
        for text in _both_forms(_queue(INDEX_PHRASING),
                                "ch23_index.md"):
            lines = text.split("\n")
            self.assertFalse(
                any(line.startswith(INDEX_PHRASING + " |")
                    or line.startswith(INDEX_PHRASING + ":")
                    for line in lines),
                "a forged findings index line stands at column 0")
            quoted = [line for line in lines
                      if line.startswith('"' + INDEX_PHRASING + '"')]
            self.assertGreaterEqual(len(quoted), 4)


class Ch23GuardsTest(unittest.TestCase):

    def test_ordinary_untranslatable_phrasing_prints_as_before(self):
        # Guard: a phrasing that matches no closing line anchor
        # keeps its standing form on every surface, the
        # appendix form the Step 15 pins state among them.
        data = (
            "# Decision queue\n\nSynthetic queue shaped input.\n\n"
            "### DQ-001: First entry\n\nStatus: Deferred\n\n"
        ).encode("utf-8")
        for text in _both_forms(data, "ch23_deferred.md"):
            self.assertIn(
                "Deferred | line start | 1 occurrence | "
                "entries: DQ-001 | unclassified", text)
            self.assertIn("Deferred | DQ-001 | line 7", text)
            self.assertFalse(any(
                line.startswith('"Deferred"')
                for line in text.split("\n")))

    def test_anchor_match_is_on_the_opening_form_only(self):
        # Guard: anchor words standing later in a phrasing, not
        # at its opening, print as they printed.
        phrasing = "Noted: Exit: code 0: mentioned in passing"
        for text in _both_forms(_queue(phrasing),
                                "ch23_mid_anchor.md"):
            self.assertIn(phrasing + " | line start", text)
            self.assertNotIn('"' + phrasing + '"', text)


if __name__ == "__main__":
    unittest.main()
