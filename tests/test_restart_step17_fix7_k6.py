"""Restart Step 17 fix wave 7, Fix Seat K6 tests.

Charges CH-129, CH-130, and CH-131, ruled at section 66
of design/steps/step-17r-record.md, on round 7 attack
seat 4 findings F-1, F-2, and F-3 (design/steps/
step-17r-attack7-4.md).

CH-129 (validate, and the parse segment claim naming
scan): seat 4 finding F-1. The CH-97 digit following limb
of the continuation guard reads one character only, so a
citation token continuing in a run of two or more visible
characters of classes L, S, and P, or in a visible
interrupter followed by a digit of a non ASCII script, is
still read in part as its ASCII head on every guarded
surface. Express ruling (a) of section 66: the CH-97
m02 excl stack inside form stands RE-OPENED in its
charged form and is cured inside this charge, on its
original charged construction (round 6 case m02 excl
stack inside, byte identical to round 7 case n01 excl
stack inside, sha256 5180e1f4f674ce1e).

CH-130 (validate, check 8): seat 4 finding F-2. The
Decision on noun limb of the decision evidence verb claim
scan stands outside the continuation guard the CH-97 cure
applied to the verb first limb of the same scan, and
misattributes claims from interrupted tokens.

CH-131 (validate, check 8): seat 4 finding F-3. The token
plus predicate claim scan stands outside the continuation
guard entirely, in its entry body and entry heading forms
alike, and its remains predicate bridge consumes the
interrupter standing after the digit head.

Constructions are the finding paper's own constructions,
rebuilt inline from the attack scratch files. Governing
pins stand as controls in this file and in the fix wave 6
K5 and fix wave 5 K5 files re-run at the close. Seat 4
observation 2 (the enumeration separator family) stands
undecided for the gate and no construction in this file
rests on it.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

PUA = "\ue000"
ALM = "\u061c"
ZWSP = "\u200b"
HYPHEN = "\u2010"
MINUS = "\u002d"
EXCL = "\u0021"
ALPHA = "\u03b1"
ARABIC_EIGHT = "\u0668"
FULLWIDTH_EIGHT = "\uff18"


def _run(data, name):
    _model, output = h.run_pipeline(data.encode("utf-8"), name)
    if output is None:
        raise AssertionError("pipeline returned a failure for " + name)
    return output


def _statements(output):
    return [h.finding_statement(f) or ""
            for f in h.findings_of(output)]


def _pd_r7(output, number):
    return [f for f in h.findings_of(output)
            if (h.finding_statement(f) or "").startswith(
                "DQ-%03d is cited, but" % number)]


def _claims_about(output, number):
    return [s for s in _statements(output)
            if "records a claim" in s
            and "DQ-%03d" % number in s]


def _framed_warnings(output, number):
    return [s for s in _statements(output)
            if "DQ-%03d is cited in a citation frame" % number in s]


def _named_entries(output):
    names = set()
    for f in h.findings_of(output):
        for name in getattr(f, "named_entries", None) or []:
            names.add(name)
    return names


def _banked_entry(number, title, extra=""):
    return (
        "### DQ-%03d: %s\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "This question is waiting for a decision.\n"
        "%s" % (number, title, extra))


def _segment_queue(hostile_line):
    body = (
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-999\n"
        "\n"
        "A plain paragraph of context for this entry.\n")
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-002: A sample open question\n"
        "\n"
        + body +
        "\n"
        "### DQ-00" + ZWSP + "1: A sample open question\n"
        "\n"
        + body +
        "\n"
        + hostile_line + "\n")


def _ghost_status_entry(number, status_value):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Ghost status probe\n"
        "\n"
        "Status: RULED, closed. %s\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"Settle DQ-%03d as follows.\"\n"
        "\n"
        "Ruling outcome: DQ-%03d is decided and closed.\n"
        "\n"
        "Where the ruling landed: NOWHERE.md, sample rule.\n"
        % (number, status_value, number, number))


def _evidence_entry(ruling_line):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Evidence claim probe\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"" + ruling_line + "\"\n"
        "\n"
        "Ruling outcome: Recorded in full.\n"
        "\n"
        "Where the ruling landed: NOWHERE.md, sample rule.\n"
        "\n"
        "### DQ-002: A sample open question\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-999\n"
        "\n"
        "A plain paragraph of context for this entry.\n")


def _remains_queue(claim_line, headed=True):
    data = ("# Decision queue\n\n" + _banked_entry(
        1, "A sample open question", "\n" + claim_line + "\n"))
    if headed:
        data += "\n" + _banked_entry(
            2, "A sample open question") + "\n"
    return data


class Ch129MultiInterrupterTest(unittest.TestCase):
    """CH-129: the multi interrupter continuation limb, F-1."""

    def test_m02_excl_stack_inside_manufactures_nothing(self):
        # The re-opened CH-97 charged construction itself,
        # ruling (a) of section 66: round 6 case m02 excl
        # stack inside, byte identical to round 7 case n01
        # excl stack inside.
        output = _run(_segment_queue(
            "See the note at DQ-88" + EXCL + EXCL
            + "8 for context."), "n01-excl-stack-inside")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual([], _framed_warnings(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])

    def test_framed_multi_interrupter_runs_manufacture_nothing(self):
        runs = {
            "triple excl": EXCL + EXCL + EXCL,
            "hyphen stack": MINUS + MINUS,
            "mixed stack": EXCL + ALPHA,
            "alpha stack": ALPHA + ALPHA,
        }
        for name, run in runs.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "See the note at DQ-88" + run
                    + "8 for context."), "n01-run")
                self.assertEqual([], _pd_r7(output, 88))
                self.assertEqual([], _framed_warnings(output, 88))
                self.assertEqual(
                    [], [s for s in _statements(output)
                         if "DQ-088" in s])

    def test_framed_alpha_alm_run_manufactures_nothing(self):
        output = _run(_segment_queue(
            "See the note at DQ-88" + ALPHA + ALM
            + "8 for context."), "n01-alpha-alm-inside")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual([], _framed_warnings(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])

    def test_framed_interrupter_foreign_digit_manufactures_nothing(self):
        forms = {
            "excl arabic": EXCL + ARABIC_EIGHT,
            "hyphen fullwidth": HYPHEN + FULLWIDTH_EIGHT,
        }
        for name, tail in forms.items():
            with self.subTest(form=name):
                output = _run(_segment_queue(
                    "See the note at DQ-88" + tail
                    + " for context."), "n01-foreign-digit")
                self.assertEqual([], _pd_r7(output, 88))
                self.assertEqual([], _framed_warnings(output, 88))
                self.assertEqual(
                    [], [s for s in _statements(output)
                         if "DQ-088" in s])

    def test_entry_plain_multi_interrupter_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nThe token DQ-88" + EXCL + EXCL
            + "8 stands as context.\n"))
        output = _run(data, "n02-excl-stack-entry-plain")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])

    def test_blocks_multi_interrupter_manufactures_nothing(self):
        data = ("# Decision queue\n\n"
                "### DQ-001: A sample open question\n"
                "\n"
                "Status: Banked\n"
                "\n"
                "Question: Which option should we take?\n"
                "\n"
                "Options: Option A, Option B\n"
                "\n"
                "Cost of deciding late: Work stays blocked.\n"
                "\n"
                "Blocks: DQ-00" + EXCL + EXCL + "2\n"
                "\n"
                "A plain paragraph of context for this entry.\n")
        output = _run(data, "n02-excl-stack-blocks")
        self.assertEqual([], _pd_r7(output, 0))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-000" in s])

    def test_heading_title_multi_interrupter_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            5, "See DQ-88" + EXCL + EXCL + "8 for context"))
        output = _run(data, "n02-excl-stack-heading-title")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])

    def test_supersession_multi_interrupter_manufactures_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nThis ruling supersedes DQ-88" + EXCL + EXCL
            + "8 and DQ-777.\n"))
        output = _run(data, "n02-excl-stack-super")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])
        self.assertEqual(1, len(_pd_r7(output, 777)))

    def test_segment_claim_multi_interrupter_manufactures_nothing(self):
        output = _run(_segment_queue(
            "DQ-88" + EXCL + EXCL + "8 was ruled and closed."),
            "n02-excl-stack-segclaim")
        self.assertEqual([], _claims_about(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])

    def test_ghost_multi_interrupter_manufactures_nothing(self):
        output = _run(_ghost_status_entry(
            502, "Ruled DQ-88" + EXCL + EXCL + "8 in full."),
            "n02-excl-stack-ghost")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])

    def test_parse_governs_bullet_multi_interrupter_names_nothing(self):
        output = _run(_segment_queue(
            "This note governs the queue.\n"
            "- DQ-888" + EXCL + EXCL
            + "9 was ruled and closed."),
            "n05-excl-stack-governs-bullet")
        self.assertNotIn("DQ-888", _named_entries(output))

    def test_parse_governs_prose_multi_interrupter_names_nothing(self):
        output = _run(_segment_queue(
            "This note governs DQ-888" + EXCL + EXCL
            + "9 and the queue."),
            "n05-excl-stack-governs-prose")
        self.assertNotIn("DQ-888", _named_entries(output))

    def test_parse_governs_bullet_foreign_digit_names_nothing(self):
        output = _run(_segment_queue(
            "This note governs the queue.\n"
            "- DQ-888" + EXCL + ARABIC_EIGHT
            + " was ruled and closed."),
            "n05-excl-arabic-governs-bullet")
        self.assertNotIn("DQ-888", _named_entries(output))


class Ch129PinsTest(unittest.TestCase):
    """CH-129 pins: the held forms of the guard, both ways."""

    def test_clean_framed_token_still_reports_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-888 for context."), "clean-pin")
        self.assertEqual(1, len(_pd_r7(output, 888)))

    def test_trailing_punctuation_token_still_reports_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-888" + HYPHEN + " for context."),
            "m02-trailing-pin")
        self.assertEqual(1, len(_pd_r7(output, 888)))

    def test_single_interrupter_inside_still_refused_pin(self):
        output = _run(_segment_queue(
            "See the note at DQ-88" + HYPHEN + "8 for context."),
            "m01-single-pin")
        self.assertEqual([], _pd_r7(output, 88))
        self.assertEqual(
            [], [s for s in _statements(output) if "DQ-088" in s])

    def test_blocks_full_stop_token_still_reports_pin(self):
        data = ("# Decision queue\n\n"
                "### DQ-001: A sample open question\n"
                "\n"
                "Status: Banked\n"
                "\n"
                "Question: Which option should we take?\n"
                "\n"
                "Options: Option A, Option B\n"
                "\n"
                "Cost of deciding late: Work stays blocked.\n"
                "\n"
                "Blocks: DQ-00.2\n"
                "\n"
                "A plain paragraph of context for this entry.\n")
        output = _run(data, "h34c-pin")
        named = [s for s in _statements(output) if "DQ-000" in s]
        self.assertTrue(named)

    def test_parse_governs_clean_still_names_pin(self):
        output = _run(_segment_queue(
            "This note governs the queue.\n"
            "- DQ-888 was ruled and closed."),
            "m16-clean-governs")
        self.assertIn("DQ-888", _named_entries(output))


class Ch130DecisionOnTest(unittest.TestCase):
    """CH-130: the Decision on noun limb, seat 4 F-2."""

    def test_decision_on_interrupted_misattributes_nothing(self):
        forms = {
            "arabic letter mark": ALM + "9",
            "private use": PUA + "9",
            "hyphen": HYPHEN + "9",
            "excl stack": EXCL + EXCL + "9",
        }
        for name, tail in forms.items():
            with self.subTest(form=name):
                output = _run(_evidence_entry(
                    "Decision on DQ-002" + tail + " in full."),
                    "n03-decision-on")
                self.assertEqual([], _claims_about(output, 2))

    def test_decision_on_clean_still_reports_pin(self):
        output = _run(_evidence_entry(
            "Decision on DQ-002 in full."), "n03-clean-decision-on")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_evidence_verb_first_interrupted_still_refused_pin(self):
        output = _run(_evidence_entry(
            "Ruled DQ-002" + ALM + "9 in full."),
            "m15-evidence-headed-pin")
        self.assertEqual([], _claims_about(output, 2))


class Ch131TokenPredicateTest(unittest.TestCase):
    """CH-131: the token plus predicate limb, seat 4 F-3."""

    def test_remains_headed_interrupted_misattributes_nothing(self):
        chars = {"arabic letter mark": ALM, "private use": PUA,
                 "hyphen": HYPHEN}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + char + " remains banked."),
                    "n04-remains-headed")
                self.assertEqual([], _claims_about(output, 2))

    def test_remains_inside_headed_interrupted_misattributes_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            1, "A sample open question",
            "\nDQ-088" + ALM + "9 remains banked.\n")
            + "\n" + _banked_entry(88, "A sample open question")
            + "\n")
        output = _run(data, "n04-alm-remains-inside-headed")
        self.assertEqual([], _claims_about(output, 88))

    def test_remains_heading_interrupted_misattributes_nothing(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            2, "A sample open question")
            + "\n" + _banked_entry(
                5, "DQ-002" + ALM + " remains banked") + "\n")
        output = _run(data, "n04-alm-remains-heading")
        self.assertEqual([], _claims_about(output, 2))

    def test_remains_clean_still_reports_pin(self):
        output = _run(_remains_queue("DQ-002 remains banked."),
                      "n04-clean-remains-headed")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_colon_separator_claim_still_reports_pin(self):
        # The governed corpus claim form of this scan: a
        # token, a colon, an assessment, and a bridge
        # predicate state (fixture R1, the DQ-112 form).
        # The colon is the form's own separator, and the
        # narrowed guard of CH-131 leaves it standing.
        output = _run(_remains_queue(
            "DQ-002: assessed under this ruling as hers, "
            "and left banked."), "r1-colon-claim-pin")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_is_headed_interrupted_takes_no_claim_pin(self):
        output = _run(_remains_queue(
            "DQ-002" + ALM + " is settled."), "n04-alm-is-headed")
        self.assertEqual([], _claims_about(output, 2))


if __name__ == "__main__":
    unittest.main()
