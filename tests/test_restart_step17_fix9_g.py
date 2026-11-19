"""Restart Step 17 fix wave 9, Fix Seat G tests.

Cluster G of the round 9 triage preparation
(design/steps/step-17r-r9-triage-prep.md, section 3),
ruled TO FIX at record section 81 ruling (a), charges
numbered consecutively from CH-191 in cluster order
per the preparation split as filed. The reading this
seat took, stated in the open: one charge per distinct
finding, in the preparation order within the cluster,
so Cluster G carries two charges, CH-213 for T9-22
(seat 4 finding F-1 of round 9) and CH-214 for T9-23
(seat 6 finding 1 of round 9). Both findings stand at
the one locus, the CH-190 possessive exception at the
head of _claim_token_continues_at in validate.py,
standing ahead of the CH-176 limb and the CH-129 run
reading, and a cure at that locus must satisfy both
directions and the governed PIN totals at once.

CH-213, T9-22, Low: the CH-190 exception returns no
continuation on its first three characters alone, the
CH-129 run reading is never reached, and a possessive
token followed by an interrupter and a digit (seat 4
cases q01 in four dresses and the heading form) is
read in part as its digit head, so a corrupted claim
fires quoting the corrupted string. The cure bound:
the exception stands only where the continuation run
reading, applied at the first character after the
possessive dress, does not read a run ending at a
digit. The interrupter with no digit after it (seat 4
case q04) stands at the CH-190 cure stated bound and
still takes its claim, pinned here.

CH-214, T9-23, Low: a possessive token standing
directly before the predicate "is still open" takes
no claim Note, in both apostrophe dresses (seat 6
probes p06 and p08), where the plain token takes its
Note (probe p01) and the same possessive token takes
its Note before the banked predicate (probes p02 and
p03, the CH-190 charged form). The neighbouring forms
stand bounded as seat 6 observation 7 records them:
intervening words lose the Note for the plain token
as well (probe p07, and the possessive dress of the
same form), and the shorter "is open" form takes no
Note in either dress (probes p09 and p10). Those
bounds stand pinned here and the cure reaches none
of them.

The module carries the corpus possessive row of the
wave 8 suite determination and the PIN totals guard
totals (Error 16, Warning 57, Note 13) as pins, as
the cluster charge states.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

APOS = "\u0027"
APOS_CURLY = "\u2019"
EXCL = "\u0021"
GROUND = "\u061c"
HYPHEN = "\u002d"


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


def _continues(text):
    position = text.index("DQ-002") + len("DQ-002")
    return validate._claim_token_continues_at(text, position)


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
        "A plain paragraph of context for this entry.\n"
        "%s" % (number, title, extra))


def _remains_queue(claim_line):
    return ("# Decision queue\n\n" + _banked_entry(
        1, "A sample open question", "\n" + claim_line + "\n")
        + "\n" + _banked_entry(2, "A sample open question")
        + "\n")


def _duplicate_queue(claim_line):
    # The seat 6 probe skeleton (probes p01 to p10 of
    # round 9): two standing copies of DQ-001, one Open
    # and one Ruled, beside DQ-002, whose body carries
    # the claim line.
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-001: Alpha open\n"
        "\n"
        "Status: Open\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-002\n"
        "\n"
        "\n"
        "This entry is waiting for a decision.\n"
        "### DQ-001: Alpha ruled\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"Decided.\"\n"
        "\n"
        "Ruling outcome: Decided in full.\n"
        "\n"
        "Where the ruling landed: the scratch file.\n"
        "\n"
        "### DQ-002: Beta question\n"
        "\n"
        "Status: Open\n"
        "\n"
        "Question: Which option should we take?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "Blocks: DQ-001\n"
        "\n"
        + claim_line + "\n"
        "\n"
        "\n"
        "This entry is waiting for a decision.\n")


class Ch213PossessiveRunTest(unittest.TestCase):
    """CH-213: a possessive dress followed by an
    interrupter and a digit is refused whole, never
    read in part as its digit head."""

    def test_excl_digit_takes_no_claim(self):
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s" + EXCL + "8 remains banked."),
            "fix9g-q01-excl-digit")
        self.assertEqual([], _claims_about(output, 2))

    def test_excl_digit_curly_takes_no_claim(self):
        output = _run(_remains_queue(
            "DQ-002" + APOS_CURLY + "s" + EXCL
            + "8 remains banked."),
            "fix9g-q01-excl-digit-curly")
        self.assertEqual([], _claims_about(output, 2))

    def test_ground_digit_takes_no_claim(self):
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s" + GROUND
            + "8 remains banked."),
            "fix9g-q01-ground-digit")
        self.assertEqual([], _claims_about(output, 2))

    def test_hyphen_digit_still_waiting_takes_no_claim(self):
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s" + HYPHEN + "8 still waiting."),
            "fix9g-q01-hyphen-digit-waiting")
        self.assertEqual([], _claims_about(output, 2))

    def test_excl_digit_heading_takes_no_claim(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            2, "A sample open question")
            + "\n" + _banked_entry(
                5, "DQ-002" + APOS + "s" + EXCL
                + "8 remains banked")
            + "\n")
        output = _run(data, "fix9g-q01-excl-digit-heading")
        self.assertEqual([], _claims_about(output, 2))

    def test_guard_run_forms_continue(self):
        forms = {
            "exclamation": "DQ-002" + APOS + "s" + EXCL
                           + "8 remains banked.",
            "curly exclamation": "DQ-002" + APOS_CURLY + "s"
                                 + EXCL + "8 remains banked.",
            "ground": "DQ-002" + APOS + "s" + GROUND
                      + "8 remains banked.",
            "hyphen waiting": "DQ-002" + APOS + "s" + HYPHEN
                              + "8 still waiting.",
        }
        for name, text in forms.items():
            with self.subTest(form=name):
                self.assertTrue(_continues(text))


class Ch213BoundPinsTest(unittest.TestCase):
    """CH-213 pins: the forms beside the charged run
    forms stand exactly where the standing cures
    stand them."""

    def test_clean_possessive_still_reports(self):
        # Seat 4 case q02, the governed possessive dress.
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s own question, the "
            "consequence for stages passed by a gate later "
            "reclassified, stays banked."),
            "fix9g-q02-poss-clean")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_possessive_remains_short_reports(self):
        # Seat 4 case q11.
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s remains banked."),
            "fix9g-q11-poss-remains")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_possessive_comma_boundary_reports(self):
        # Seat 4 case q12, at the comma boundary the
        # K10B module pins.
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s, remains banked."),
            "fix9g-q12-poss-comma")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_excl_no_digit_reports_at_the_stated_bound(self):
        # Seat 4 case q04, observation 1 of that paper:
        # an interrupter with no digit after it stands
        # at the bound the CH-190 cure states in its
        # own text, and its claim still takes its Note.
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s" + EXCL + " remains banked."),
            "fix9g-q04-poss-excl-nodigit")
        self.assertEqual(1, len(_claims_about(output, 2)))

    def test_glued_digit_takes_no_claim(self):
        # Seat 4 case q03, the glued form at the CH-190
        # narrowing edge: a digit standing immediately
        # after the s is alphanumeric and the exception
        # does not stand.
        output = _run(_remains_queue(
            "DQ-002" + APOS + "s8 remains banked."),
            "fix9g-q03-poss-glued-digit")
        self.assertEqual([], _claims_about(output, 2))

    def test_apostrophe_no_s_digit_takes_no_claim(self):
        # Seat 4 case q09: an apostrophe with no s after
        # it, standing before an interrupter and a
        # digit, stands refused by the CH-129 run
        # reading and the CH-176 limb together.
        output = _run(_remains_queue(
            "DQ-002" + APOS + EXCL + "8 remains banked."),
            "fix9g-q09-apos-nos-digit")
        self.assertEqual([], _claims_about(output, 2))

    def test_ch176_excl_remains_still_refused(self):
        output = _run(_remains_queue(
            "DQ-002" + EXCL + " remains banked."),
            "fix9g-ch176-excl-remains")
        self.assertEqual([], _claims_about(output, 2))

    def test_guard_possessive_boundaries_no_continuation(self):
        for apos in (APOS, APOS_CURLY):
            self.assertFalse(_continues(
                "DQ-002" + apos + "s own question"))
            self.assertFalse(_continues(
                "DQ-002" + apos + "s, the question"))
            self.assertFalse(_continues("DQ-002" + apos + "s"))
        self.assertFalse(_continues(
            "DQ-002" + APOS + "s" + EXCL + " remains banked."))


class Ch214PossessiveStillOpenTest(unittest.TestCase):
    """CH-214: the possessive token standing directly
    before the predicate "is still open" takes its
    claim Note, in both apostrophe dresses."""

    def test_possessive_adjacent_still_open_reports(self):
        # Seat 6 probe p06, straight apostrophe.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is still open."),
            "fix9g-p06-possessive-adjacent")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn("DQ-002 records a claim", claims[0])
        self.assertIn("still open", claims[0])

    def test_curly_adjacent_still_open_reports(self):
        # Seat 6 probe p08, curly apostrophe.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS_CURLY + "s is still open."),
            "fix9g-p08-curly-adjacent")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn("DQ-002 records a claim", claims[0])
        self.assertIn("still open", claims[0])


class Ch214BoundPinsTest(unittest.TestCase):
    """CH-214 pins: the plain control, the CH-190
    banked form, and the adjacency bounds of seat 6
    observation 7 stand exactly as measured."""

    def test_plain_adjacent_still_open_reports(self):
        # Seat 6 probe p01, the plain control.
        output = _run(_duplicate_queue("DQ-001 is still open."),
                      "fix9g-p01-plain-control")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn("one for each standing copy", claims[0])

    def test_possessive_banked_reports(self):
        # Seat 6 probe p02, the CH-190 charged form.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s own question, the "
            "consequence for stages passed, stays banked."),
            "fix9g-p02-possessive-banked")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_curly_banked_reports(self):
        # Seat 6 probe p03, the CH-190 charged form in
        # the curly dress.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS_CURLY + "s own question, the "
            "consequence for stages passed, stays banked."),
            "fix9g-p03-curly-banked")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_intervening_takes_no_claim(self):
        # Seat 6 probe p07: intervening words lose the
        # Note for the plain token as well.
        output = _run(_duplicate_queue(
            "DQ-001 own question is still open."),
            "fix9g-p07-plain-intervening")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_intervening_takes_no_claim(self):
        # Seat 6 fresh form w01: the possessive dress
        # of the same intervening form.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s own question is still open."),
            "fix9g-w01-possessive-intervening")
        self.assertEqual([], _claims_about(output, 1))

    def test_plain_is_open_takes_no_claim(self):
        # Seat 6 probe p09: the shorter "is open" form
        # takes no Note in the plain dress.
        output = _run(_duplicate_queue("DQ-001 is open."),
                      "fix9g-p09-plain-is-open")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_is_open_takes_no_claim(self):
        # Seat 6 probe p10: the shorter "is open" form
        # takes no Note in the possessive dress either.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is open."),
            "fix9g-p10-possessive-is-open")
        self.assertEqual([], _claims_about(output, 1))


class Ch213Ch214PinTotalsTest(unittest.TestCase):
    """The corpus possessive row of the wave 8 suite
    determination and the PIN totals guard totals
    stand as pins in this module, as the cluster
    charge states."""

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
