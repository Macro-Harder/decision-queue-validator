"""Restart Step 17 fix wave 8, Correction Seat K10B tests.

Charge CH-190, on the determination at design/steps/
step-17r-fix8-suite-determination.md: charge CH-176
(Fix Seat K10) widened the limb in
_claim_token_continues_at in validate.py to every
character not a full stop or a semicolon whose category
starts with L, S, or P. The character after the digits
in the possessive token "DQ-070's" is U+0027 APOSTROPHE
(category Po), so the cured guard refuses the possessive
token whole and the bridge predicate is never read,
losing one genuine governed Note: the check 8 cross
entry claim Note on DQ-138 about DQ-070 (PIN.md line
4056). The determination grades the loss UNCHARGED.

This module pins, test first:
(i) the possessive forms: a token carrying an
apostrophe (U+0027, and U+2019 in the same dress)
followed by "s" and a non alphanumeric boundary, before
a bridge predicate, takes its claim reading, in the
entry body form and the entry heading form, on the
remains family and the still waiting form;
(ii) every CH-176 charged construction standing exactly
as K10 cured it, restated here from that seat's module
(product/tests/test_restart_step17_fix8_k10.py), which
also stands in this seat's run set whole;
(iii) the PIN corpus totals standing at Error 16,
Warning 57, Note 13, in the form the Step 16 guard
modules pin them, with the lost DQ-138 claim Note on
DQ-070 named expressly.

The narrowing bounds stand pinned too: an apostrophe
with no "s" after it, and an apostrophe plus "s" glued
to a further alphanumeric character, stand refused
exactly as the CH-176 limb refuses them.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

APOS = "\u0027"
APOS_CURLY = "\u2019"
EXCL = "\u0021"
QUEST = "\u003f"
COMMA = "\u002c"
DOLLAR = "\u0024"
PLUS = "\u002b"
TILDE = "\u007e"


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


def _continues(text):
    position = text.index("DQ-002") + len("DQ-002")
    return validate._claim_token_continues_at(text, position)


class Ch190PossessiveClaimTest(unittest.TestCase):
    """CH-190: the possessive token takes its claim reading."""

    def test_dq070_construction_from_the_corpus_reports(self):
        # The differing case itself, rebuilt from the
        # determination paper's minimal extract: the
        # DQ-138 ruling outcome sentence of PIN.md line
        # 4056, standing in a DQ-138 entry about a headed
        # DQ-070 entry.
        claim = (
            "This settles the open principle recorded at "
            "DQ-070; DQ-070" + APOS + "s own question, the "
            "consequence for stages passed by a gate later "
            "reclassified, stays banked and is not decided "
            "by this ruling.")
        data = ("# Decision queue\n\n"
                + _banked_entry(70, "A sample open question")
                + "\n" + _banked_entry(
                    138, "The corpus gate against the "
                    "strictness cost limb", "\n" + claim + "\n")
                + "\n")
        output = _run(data, "k10b-dq070-possessive")
        claims = _claims_about(output, 70)
        self.assertEqual(1, len(claims))
        self.assertIn("DQ-138 records a claim", claims[0])
        self.assertIn("DQ-070" + APOS + "s own question",
                      claims[0])

    def test_possessive_remains_body_reports_both_apostrophes(self):
        for name, apos in {"ascii": APOS,
                           "curly": APOS_CURLY}.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + apos + "s own question, the "
                    "consequence for stages passed by a gate "
                    "later reclassified, stays banked."),
                    "k10b-possessive-remains")
                self.assertEqual(
                    1, len(_claims_about(output, 2)))

    def test_possessive_remains_heading_reports_both_apostrophes(self):
        for name, apos in {"ascii": APOS,
                           "curly": APOS_CURLY}.items():
            with self.subTest(form=name):
                data = ("# Decision queue\n\n" + _banked_entry(
                    2, "A sample open question")
                    + "\n" + _banked_entry(
                        5, "DQ-002" + apos + "s own question, "
                        "the consequence for stages passed by "
                        "a gate later reclassified, stays "
                        "banked")
                    + "\n")
                output = _run(data, "k10b-possessive-heading")
                self.assertEqual(
                    1, len(_claims_about(output, 2)))

    def test_possessive_still_waiting_reports_both_apostrophes(self):
        for name, apos in {"ascii": APOS,
                           "curly": APOS_CURLY}.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + apos + "s own question is "
                    "still waiting."),
                    "k10b-possessive-still-waiting")
                self.assertEqual(
                    1, len(_claims_about(output, 2)))

    def test_possessive_comma_boundary_reports(self):
        # The character after the possessive "s" is a
        # comma, a non alphanumeric boundary, and the
        # bridge predicate stands after it.
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s, the question itself, "
            "stays banked."), "k10b-possessive-comma")
        self.assertEqual(1, len(_claims_about(output, 2)))


class Ch190GuardFormTest(unittest.TestCase):
    """CH-190 at the guard itself: the possessive form
    returns no continuation, and no other form moves."""

    def test_guard_possessive_space_boundary_no_continuation(self):
        for apos in (APOS, APOS_CURLY):
            self.assertFalse(_continues(
                "DQ-002" + apos + "s own question"))

    def test_guard_possessive_comma_boundary_no_continuation(self):
        for apos in (APOS, APOS_CURLY):
            self.assertFalse(_continues(
                "DQ-002" + apos + "s, the question"))

    def test_guard_possessive_end_of_text_no_continuation(self):
        for apos in (APOS, APOS_CURLY):
            self.assertFalse(_continues("DQ-002" + apos + "s"))

    def test_guard_apostrophe_without_s_still_continues(self):
        self.assertTrue(_continues(
            "DQ-002" + APOS + " remains banked."))
        self.assertTrue(_continues(
            "DQ-002" + APOS_CURLY + " remains banked."))

    def test_guard_possessive_glued_alphanumeric_still_continues(self):
        # An apostrophe plus "s" followed at once by a
        # further alphanumeric character is no possessive
        # boundary: the CH-176 limb stands over it.
        self.assertTrue(_continues(
            "DQ-002" + APOS + "sx remains banked."))
        self.assertTrue(_continues(
            "DQ-002" + APOS + "stays banked."))


class Ch190NarrowingPinsTest(unittest.TestCase):
    """CH-190 pipeline pins: the forms beside the
    possessive stand exactly where the cured guard
    stands them."""

    def test_apostrophe_without_s_takes_no_claim(self):
        output = _run(_remains_queue(
            "DQ-002" + APOS + " remains banked."),
            "k10b-apostrophe-no-s")
        self.assertEqual([], _claims_about(output, 2))

    def test_possessive_glued_alphanumeric_takes_no_claim(self):
        output = _run(_remains_queue(
            "DQ-002" + APOS + "sx remains banked."),
            "k10b-possessive-glued")
        self.assertEqual([], _claims_about(output, 2))

    def test_clean_remains_still_reports_pin(self):
        output = _run(_remains_queue("DQ-002 remains banked."),
                      "k10b-clean-remains")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_colon_separator_claim_still_reports_pin(self):
        output = _run(_remains_queue(
            "DQ-002: assessed under this ruling as hers, "
            "and left banked."), "k10b-colon-claim")
        self.assertEqual(1, len(_claims_about(output, 2)))


class Ch176ChargedFormsRestatedTest(unittest.TestCase):
    """CH-176 charged constructions, restated from the
    K10 module: every one stands refused exactly as
    K10 cured it."""

    def test_remains_headed_visible_interrupters_misattribute_nothing(self):
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
                    "k10b-ch176-remains-headed")
                self.assertEqual([], _claims_about(output, 2))

    def test_remains_heading_visible_interrupter_misattributes_nothing(self):
        for name, char in {"exclamation": EXCL,
                           "question": QUEST}.items():
            with self.subTest(form=name):
                data = ("# Decision queue\n\n" + _banked_entry(
                    2, "A sample open question")
                    + "\n" + _banked_entry(
                        5, "DQ-002" + char + " remains banked")
                    + "\n")
                output = _run(data, "k10b-ch176-remains-heading")
                self.assertEqual([], _claims_about(output, 2))

    def test_still_waiting_visible_interrupter_misattributes_nothing(self):
        for name, char in {"exclamation": EXCL,
                           "dollar": DOLLAR}.items():
            with self.subTest(form=name):
                output = _run(_remains_queue(
                    "DQ-002" + char + " still waiting."),
                    "k10b-ch176-still-waiting")
                self.assertEqual([], _claims_about(output, 2))


class Ch190PinTotalsTest(unittest.TestCase):
    """CH-190: the PIN corpus totals stand at the pins,
    and the lost Note stands among them by name."""

    def test_pin_totals_stand(self):
        _model, output = h.cached_pipeline("PIN")
        counts = {"Error": 0, "Warning": 0, "Note": 0}
        for finding in h.findings_of(output):
            counts[h.finding_severity(finding)] += 1
        self.assertEqual(
            counts, {"Error": 16, "Warning": 57, "Note": 13})

    def test_pin_dq138_possessive_claim_note_stands(self):
        _model, output = h.cached_pipeline("PIN")
        claims = [s for s in _statements(output)
                  if "DQ-138 records a claim about the state "
                  "of DQ-070" in s]
        self.assertEqual(1, len(claims))
        self.assertIn(
            "DQ-070" + APOS + "s own question, the "
            "consequence for stages passed by a gate later "
            "reclassified, stays banked", claims[0])


if __name__ == "__main__":
    unittest.main()
