"""Restart Step 17 fix wave 8, Fix Seat K10 tests.

Charge CH-176, ruled at section 77 of design/steps/
step-17r-record.md, on round 8 attack seat 4 finding
F-1 (design/steps/step-17r-attack8-4.md), Low, T8-23.

CH-176 (validate, check 8): the bridge interrupter limb.
The CH-131 claim guard of the token plus predicate scan
adds one trailing character class only (the hyphen class,
Pd), and a token standing before a bridge predicate with
any other visible interrupter after its digits is still
read in part as its digit head, in the entry body and
entry heading forms alike, and on both bridge predicate
forms (the remains family and the still waiting form).
The charged interrupters are the visible characters of
classes L, S, and P other than the hyphen class, standing
between the digit head and a bridge predicate, with no
digit after them: the finding paper's own forms are the
exclamation, question, comma, dollar, plus, and tilde
forms of the remains headed construction. The letter
class forms stand pinned below: the token pattern's own
word boundary already refuses them whole on this scan.

Constructions are the finding paper's own constructions,
rebuilt inline from the attack scratch files in
product/attack8-4-scratch/cases (the p01 family).
Governing pins stand as controls in this file: the clean
remains form, the colon separator claim form of the
CH-131 narrowing, the hyphen and ground character forms
cured at CH-131, and the full stop and semicolon forms
closed by the bridge's own form. The governing pin
module of the earlier waves for this surface,
product/tests/test_restart_step17_fix7_k6.py (the CH-129
to CH-131 pins), stands re-run at the close. Seat 4
observations 1 and 2 stand recorded at the bounds their
cure texts state under ruling (j) of section 77 and no
construction in this file rests on them; the enumeration
separator family rides the carries and no construction
in this file rests on it either.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

PUA = "\ue000"
ALM = "\u061c"
HYPHEN = "\u2010"
EXCL = "\u0021"
QUEST = "\u003f"
COMMA = "\u002c"
DOLLAR = "\u0024"
PLUS = "\u002b"
TILDE = "\u007e"
DOT = "\u002e"
SEMI = "\u003b"
ALPHA = "\u03b1"
LETTER_X = "x"


def _run(data, name):
    _model, output = h.run_pipeline(data.encode("utf-8"), name)
    if output is None:
        raise AssertionError("pipeline returned a failure for " + name)
    return output


def _statements(output):
    return [h.finding_statement(f) or ""
            for f in h.findings_of(output)]


def _claims_about(output, number):
    return [s for s in _statements(output)
            if "records a claim" in s
            and "DQ-%03d" % number in s]


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
        "Blocks: DQ-999\n"
        "\n"
        "This question is waiting for a decision.\n"
        "%s" % (number, title, extra))


def _remains_queue(claim_line, headed=True):
    data = ("# Decision queue\n\n" + _banked_entry(
        1, "A sample open question", "\n" + claim_line + "\n"))
    if headed:
        data += "\n" + _banked_entry(
            2, "A sample open question") + "\n"
    return data


class Ch176BridgeInterrupterTest(unittest.TestCase):
    """CH-176: the bridge interrupter limb, seat 4 F-1."""

    def test_remains_headed_visible_interrupters_misattribute_nothing(self):
        # The finding paper's own p01 remains headed family:
        # punctuation other than the hyphen class, and
        # symbols, standing between the digit head and the
        # remains bridge predicate.
        chars = {
            "exclamation": EXCL,
            "question": QUEST,
            "comma": COMMA,
            "dollar": DOLLAR,
            "plus": PLUS,
            "tilde": TILDE,
        }
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + char + " remains banked."),
                    "p01-remains-headed")
                self.assertEqual([], _claims_about(output, 2))

    def test_remains_heading_visible_interrupter_misattributes_nothing(self):
        # The entry heading form of the same scan: a valid
        # DQ-005 heading whose title carries the corrupted
        # token before the remains bridge predicate.
        for name, char in {"exclamation": EXCL,
                           "question": QUEST}.items():
            with self.subTest(form=name):
                data = ("# Decision queue\n\n" + _banked_entry(
                    2, "A sample open question")
                    + "\n" + _banked_entry(
                        5, "DQ-002" + char + " remains banked")
                    + "\n")
                output = _run(data, "p01-remains-heading")
                self.assertEqual([], _claims_about(output, 2))

    def test_still_waiting_visible_interrupter_misattributes_nothing(self):
        # The second bridge form of the same scan: the
        # still waiting predicate consumes the interrupter
        # as bridge text in the same way.
        for name, char in {"exclamation": EXCL,
                           "dollar": DOLLAR}.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + char + " still waiting."),
                    "p01-still-waiting")
                self.assertEqual([], _claims_about(output, 2))


class Ch176PinsTest(unittest.TestCase):
    """CH-176 pins: the held forms of the claim guard."""

    def test_remains_clean_still_reports_pin(self):
        output = _run(_remains_queue("DQ-002 remains banked."),
                      "p01-clean-remains-headed")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_colon_separator_claim_still_reports_pin(self):
        # The governed corpus claim form of this scan, held
        # by the CH-131 narrowing: a token, a colon, an
        # assessment, and a bridge predicate state.
        output = _run(_remains_queue(
            "DQ-002: assessed under this ruling as hers, "
            "and left banked."), "r1-colon-claim-pin")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_remains_hyphen_still_refused_pin(self):
        output = _run(_remains_queue(
            "DQ-002" + HYPHEN + " remains banked."),
            "n04-hyphen-remains-headed")
        self.assertEqual([], _claims_about(output, 2))

    def test_remains_ground_characters_still_refused_pin(self):
        chars = {"arabic letter mark": ALM, "private use": PUA}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + char + " remains banked."),
                    "n04-remains-headed")
                self.assertEqual([], _claims_about(output, 2))

    def test_remains_full_stop_takes_no_claim_pin(self):
        # Closed by the bridge's own form, which excludes
        # the full stop expressly: bounded pass 2 of the
        # finding paper, standing unmoved by this cure.
        output = _run(_remains_queue(
            "DQ-002" + DOT + " remains banked."),
            "p01-dot-remains-headed")
        self.assertEqual([], _claims_about(output, 2))

    def test_remains_headed_letter_interrupters_take_no_claim_pin(self):
        # The letter class named in the finding stands
        # refused whole on this scan by the token pattern
        # itself: no word boundary stands between a digit
        # and a letter, so no token match stands at all.
        # Pinned here so the class bound stands stated.
        chars = {"greek alpha": ALPHA, "ascii letter": LETTER_X}
        for name, char in chars.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + char + " remains banked."),
                    "p01-letter-remains-headed")
                self.assertEqual([], _claims_about(output, 2))

    def test_remains_semicolon_takes_no_claim_pin(self):
        output = _run(_remains_queue(
            "DQ-002" + SEMI + " remains banked."),
            "p01-semi-remains-headed")
        self.assertEqual([], _claims_about(output, 2))


if __name__ == "__main__":
    unittest.main()
