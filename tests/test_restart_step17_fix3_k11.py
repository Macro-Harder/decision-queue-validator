"""Restart Step 17 fix wave 3, Seat K11 tests: date digits.

One charge stands in this file, in parse.py, written before
its cure:

CH-47 (F-15-3-1, Low): dates written in assigned non ASCII
digit scripts are read at parse level through the unpinned
digit classes in _DATE_RE and the heading tail date group,
so a Ruled entry whose only date is Arabic Indic stands at
"Missing ruling date on a decided entry: 0 entries" exactly
as the ASCII control. The cure bound, from ruling (l) at
section 26 of the step record: the date patterns read ASCII
digits only, as the count and citation patterns do, so a
date written wholly in a non ASCII digit script stands as
no date recorded, and the missing ruling date census takes
it. The cure reaches the digit classes only, in _DATE_RE
and in the heading tail date group of _HEADING_TAIL_WORD_RE.

Pins that must not break: the CH-24 pins whole, the ASCII
date pins (a date as written prints as written, in the
digits as written, for ASCII forms), and the F-15-2-1
discharge ground standing (the introduction count pattern
pinned to ASCII, which this cure does not touch). The
F-15-2-2 residue (the heading borne element still runtime
dependent at the parse _heading_borne isalpha limb) stands
in its governed form and is not cured here.

Constructions stand in the attack paper own forms
(design/steps/step-17r-attack3-15.md, cases t01 to t11):
the heading form, one Open entry whose heading tail carries
the date, and the decided entry form, one Ruled entry in
the Ruled Record whose only date stands on its Ruled by
line. Digit scripts are written with explicit escapes:
Arabic Indic, Devanagari, and fullwidth forms of the date
2026-11-17, each assigned in Unicode 15.0.0 and 16.0.0.
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

parse = h.import_module("parse")

ASCII_DATE = "2026-11-17"
ARABIC_DATE = "٢٠٢٦-١١-١٧"
DEVANAGARI_DATE = "२०२६-११-१७"
FULLWIDTH_DATE = "２０２６-１１-１７"
MIXED_DATE = "2026-١١-17"
FOREIGN_DATES = (ARABIC_DATE, DEVANAGARI_DATE, FULLWIDTH_DATE)

NO_DATE_LINE = "Date: no date recorded"
ASCII_DATE_LINE = "Date: " + ASCII_DATE
CENSUS_ONE = "Missing ruling date on a decided entry: 1 entry"
CENSUS_ZERO = "Missing ruling date on a decided entry: 0 entries"


def _heading_case(date_text):
    return (
        "# Decision queue\n\n"
        "### DQ-001: Harbour Ruled " + date_text + "\n\n"
        "Status: Open\n\n"
        "Question: Which option should we take?\n\n"
        "Options: Option A, Option B\n\n"
        "Cost of deciding late: Work stays blocked while "
        "this waits.\n\n"
        "Blocks: DQ-002\n\n"
        "This question is waiting for a decision, "
        "recorded 2026-11-17.\n")


def _ruled_case(date_suffix):
    ruled_by = "Ruled by: Captain JP"
    if date_suffix:
        ruled_by += ", " + date_suffix
    return (
        "# Decision queue\n\n"
        "## Ruled Record\n\n"
        "### DQ-001: The harbour question\n\n"
        "Status: Ruled\n\n"
        + ruled_by + "\n\n"
        "Ruling: Option A stands.\n\n"
        "Outcome: The harbour option is settled.\n\n"
        "Landed: Recorded in the queue.\n\n"
        "This ruling is recorded, recorded 2026-11-17.\n")


def _run_both(text):
    """Run validate and render over one case; return texts."""
    outputs = {}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "case.md"
        path.write_bytes(text.encode("utf-8"))
        for subcommand in ("validate", "render"):
            code, out, err = h.run_cli(subcommand, path)
            outputs[subcommand] = (
                code, out.decode("utf-8", errors="replace"))
    return outputs


class Step17Fix3K11DatePatternUnitTest(unittest.TestCase):
    """CH-47: the date patterns at unit level."""

    def test_date_re_reads_ascii_only(self):
        self.assertEqual(
            parse._DATE_RE.search(ASCII_DATE).group(0),
            ASCII_DATE)
        for foreign in FOREIGN_DATES + (MIXED_DATE,):
            with self.subTest(date=foreign):
                self.assertIsNone(parse._DATE_RE.search(foreign))

    def test_heading_tail_date_group_reads_ascii_only(self):
        ascii_heading = "Harbour Ruled " + ASCII_DATE
        match = parse._HEADING_TAIL_WORD_RE.search(ascii_heading)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "Ruled")
        for foreign in FOREIGN_DATES:
            with self.subTest(date=foreign):
                self.assertIsNone(
                    parse._HEADING_TAIL_WORD_RE.search(
                        "Harbour Ruled " + foreign))


class Step17Fix3K11HeadingDateTest(unittest.TestCase):
    """CH-47: the heading form, cases t01 to t04."""

    def test_ascii_heading_date_prints_as_written(self):
        # Control, passing before and after: the ASCII date
        # pin, a date as written prints as written.
        for subcommand, (code, out) in _run_both(
                _heading_case(ASCII_DATE)).items():
            with self.subTest(subcommand=subcommand):
                self.assertEqual(code, 0)
                self.assertIn(ASCII_DATE_LINE, out)

    def test_foreign_heading_dates_stand_as_no_date(self):
        for foreign in FOREIGN_DATES:
            outputs = _run_both(_heading_case(foreign))
            for subcommand, (code, out) in outputs.items():
                with self.subTest(date=foreign,
                                  subcommand=subcommand):
                    self.assertEqual(code, 0)
                    self.assertIn(NO_DATE_LINE, out)
                    self.assertNotIn("Date: " + foreign, out)


class Step17Fix3K11RuledDateCensusTest(unittest.TestCase):
    """CH-47: the decided entry form, cases t08 to t11."""

    def test_ascii_ruled_date_satisfies_census(self):
        # Control, passing before and after.
        for subcommand, (code, out) in _run_both(
                _ruled_case(ASCII_DATE)).items():
            with self.subTest(subcommand=subcommand):
                self.assertIn(ASCII_DATE_LINE, out)
                self.assertIn(CENSUS_ZERO, out)

    def test_no_date_ruled_entry_stands_in_census(self):
        # Control, passing before and after.
        for subcommand, (code, out) in _run_both(
                _ruled_case("")).items():
            with self.subTest(subcommand=subcommand):
                self.assertIn(NO_DATE_LINE, out)
                self.assertIn(CENSUS_ONE, out)

    def test_foreign_ruled_dates_stand_in_census(self):
        for foreign in FOREIGN_DATES:
            outputs = _run_both(_ruled_case(foreign))
            for subcommand, (code, out) in outputs.items():
                with self.subTest(date=foreign,
                                  subcommand=subcommand):
                    self.assertIn(NO_DATE_LINE, out)
                    self.assertNotIn("Date: " + foreign, out)
                    self.assertIn(CENSUS_ONE, out)
                    self.assertNotIn(CENSUS_ZERO, out)


if __name__ == "__main__":
    unittest.main()
