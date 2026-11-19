"""Restart Step 17 fix wave 10, Fix Seat F tests.

Charge CH-256, Cluster F of the round 10 triage
preparation (design/steps/step-17r-r10-triage-prep.md,
section 3), ruled TO FIX at record section 83 ruling
(a). Finding T10-33: seat 4 finding F-1 and seat 6
Finding 1 of round 10, one distinct finding filed by
both seats at Low.

CH-256, T10-33, Low. Locus: validate.py, the token plus
predicate claim scan of check 8, at the CH-214 cure
bound. The CH-214 cure gained the possessive dress for
the one anchored is still pattern only, and its text
states in the open that no other anchored list of the
scan gains the dress by that charge. A possessive token
standing directly before any sibling anchored predicate
of the same scan therefore takes no claim Note, where
the plain token takes it: the was list, the is list,
the has been list, the got list, the has list, the bare
past lists, the is shut form, and the remains and
stands resolved direct form, in the entry body form
and in the heading form. The bridge families of the
same scan, which tolerate intervening text, already
read the same dress without loss since CH-190, and the
claim guard itself honours the dress, so the token
reaches the predicate matching and is refused there
alone.

The cure bound this module pins: every anchored
pattern of the scan gains the dress in the CH-214 form
(an apostrophe, U+0027 or U+2019, and the letter s
standing immediately after the digits and immediately
before the verb), and nothing else gains anything. The
intervening word forms take no Note in either dress,
the shorter is open form takes no Note in either
dress, the comma form and the capital s dress and the
glued form take no Note, and a bare past verb carrying
an object after it still reads as a ruling mention,
not a claim, in either dress.

The module carries the CH-214 charged forms, the
corpus possessive row of the wave 8 suite
determination, and the PIN totals (Error 16, Warning
57, Note 13) as pins, in the form the cluster charge
states.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

APOS = "\u0027"
APOS_CURLY = "\u2019"


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


def _duplicate_queue(claim_line):
    # The seat 6 probe skeleton (probes p01 to p10 of
    # round 9, rebuilt in the round 10 papers of seats
    # 4 and 6): two standing copies of DQ-001, one Open
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


def _heading_queue(title):
    # The same duplicate host, with the claim standing
    # in the DQ-002 heading title (seat 4 cases g23 and
    # g24, seat 6 cases x20 and x21).
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
        "### DQ-002: " + title + "\n"
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
        "This entry is waiting for a decision.\n")


class Ch256BodyPairsTest(unittest.TestCase):
    """CH-256 charged body forms: the possessive token
    standing directly before a sibling anchored
    predicate takes its claim Note, one method per
    predicate form named in the two source papers."""

    def test_possessive_was_reports(self):
        # Seat 4 pair g02 against g01, seat 6 was list.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s was open."),
            "fix10f-g02-poss-was")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn("DQ-001" + APOS + "s was open", claims[0])

    def test_possessive_was_curly_reports(self):
        output = _run(_duplicate_queue(
            "DQ-001" + APOS_CURLY + "s was open."),
            "fix10f-poss-was-curly")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_is_reports(self):
        # Seat 4 pair g04 against g03.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is Open."),
            "fix10f-g04-poss-is")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn("DQ-001" + APOS + "s is Open", claims[0])

    def test_possessive_is_settled_reports(self):
        # Seat 6 pair x02 against x01, straight dress.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is Settled."),
            "fix10f-x02-poss-is-settled")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_is_settled_curly_reports(self):
        # Seat 6 case x03, curly dress.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS_CURLY + "s is Settled."),
            "fix10f-x03-poss-is-settled-curly")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_has_been_reports(self):
        # Seat 4 pair g06 against g05, seat 6 pair x07
        # against x06.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s has been settled."),
            "fix10f-g06-poss-hasbeen")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn(
            "DQ-001" + APOS + "s has been settled", claims[0])

    def test_possessive_has_been_curly_reports(self):
        output = _run(_duplicate_queue(
            "DQ-001" + APOS_CURLY + "s has been settled."),
            "fix10f-poss-hasbeen-curly")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_got_reports(self):
        # Seat 4 pair g08 against g07, seat 6 pair x13
        # against x12.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s got settled."),
            "fix10f-g08-poss-got")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_has_reports(self):
        # Seat 4 pair g10 against g09, seat 6 pair x17
        # against x16.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s has settled."),
            "fix10f-g10-poss-has")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_bare_past_adverb_reports(self):
        # Seat 4 pair g12 against g11, seat 6 pair x15
        # against x14: the bare past with a time adverb.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s settled yesterday."),
            "fix10f-g12-poss-barepast")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn(
            "DQ-001" + APOS + "s settled yesterday", claims[0])

    def test_possessive_bare_past_closing_reports(self):
        # The second bare past pattern of the same scan:
        # the sentence closing on its own full stop.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s settled."),
            "fix10f-poss-barepast-closing")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_bare_past_in_full_reports(self):
        # The in full member of the same pattern.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s settled in full."),
            "fix10f-poss-barepast-infull")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_is_shut_reports(self):
        # Seat 4 pair g14 against g13, seat 6 pair x11
        # against x10.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is shut."),
            "fix10f-g14-poss-isshut")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn("DQ-001" + APOS + "s is shut", claims[0])

    def test_possessive_remains_resolved_reports(self):
        # Seat 4 pair g16 against g15, seat 6 pair x09
        # against x08: the remains resolved direct form.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s remains resolved."),
            "fix10f-g16-poss-remainsresolved")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn(
            "DQ-001" + APOS + "s remains resolved", claims[0])

    def test_possessive_stands_resolved_reports(self):
        # The stands member of the same direct pattern.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s stands resolved."),
            "fix10f-poss-standsresolved")
        self.assertEqual(1, len(_claims_about(output, 1)))


class Ch256HeadingFormsTest(unittest.TestCase):
    """CH-256 charged heading forms: the same scan in
    the heading form the CH-214 cure itself serves."""

    def test_heading_possessive_was_reports(self):
        # Seat 4 case g23 against its control g24.
        output = _run(_heading_queue(
            "DQ-001" + APOS + "s was open"),
            "fix10f-g23-poss-was-heading")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_heading_possessive_is_settled_reports(self):
        # Seat 6 case x21 against its control x20.
        output = _run(_heading_queue(
            "DQ-001" + APOS + "s is Settled"),
            "fix10f-x21-heading-poss-is-settled")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_heading_possessive_is_settled_curly_reports(self):
        output = _run(_heading_queue(
            "DQ-001" + APOS_CURLY + "s is Settled"),
            "fix10f-heading-poss-is-settled-curly")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_heading_possessive_has_reports(self):
        output = _run(_heading_queue(
            "DQ-001" + APOS + "s has settled"),
            "fix10f-heading-poss-has")
        self.assertEqual(1, len(_claims_about(output, 1)))


class Ch256PlainControlsTest(unittest.TestCase):
    """CH-256 controls: the plain token takes its claim
    Note on every charged predicate, before the cure and
    after it, in body and heading forms."""

    def test_plain_was_reports(self):
        output = _run(_duplicate_queue("DQ-001 was open."),
                      "fix10f-g01-plain-was")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_is_settled_reports(self):
        output = _run(_duplicate_queue("DQ-001 is Settled."),
                      "fix10f-x01-plain-is-settled")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_has_been_reports(self):
        output = _run(_duplicate_queue(
            "DQ-001 has been settled."), "fix10f-g05-plain-hasbeen")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_got_reports(self):
        output = _run(_duplicate_queue("DQ-001 got settled."),
                      "fix10f-g07-plain-got")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_has_reports(self):
        output = _run(_duplicate_queue("DQ-001 has settled."),
                      "fix10f-g09-plain-has")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_bare_past_adverb_reports(self):
        output = _run(_duplicate_queue(
            "DQ-001 settled yesterday."), "fix10f-g11-plain-barepast")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_is_shut_reports(self):
        output = _run(_duplicate_queue("DQ-001 is shut."),
                      "fix10f-g13-plain-isshut")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_remains_resolved_reports(self):
        output = _run(_duplicate_queue(
            "DQ-001 remains resolved."),
            "fix10f-g15-plain-remainsresolved")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_heading_plain_was_reports(self):
        output = _run(_heading_queue("DQ-001 was open"),
                      "fix10f-g24-plain-was-heading")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_heading_plain_is_settled_reports(self):
        output = _run(_heading_queue("DQ-001 is Settled"),
                      "fix10f-x20-heading-plain-is-settled")
        self.assertEqual(1, len(_claims_about(output, 1)))


class Ch256BoundPinsTest(unittest.TestCase):
    """CH-256 pins: the CH-214 cure on the is still form
    stands, the CH-190 bridge forms stand, and the forms
    at the dress bound take no Note in either dress."""

    def test_possessive_is_still_open_reports(self):
        # CH-214 charged form, seat 6 probe p06.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is still open."),
            "fix10f-p06-possessive-adjacent")
        claims = _claims_about(output, 1)
        self.assertEqual(1, len(claims))
        self.assertIn("still open", claims[0])

    def test_curly_is_still_open_reports(self):
        # CH-214 charged form, seat 6 probe p08.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS_CURLY + "s is still open."),
            "fix10f-p08-curly-adjacent")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_is_still_resolved_reports(self):
        # Seat 4 case g17: the cured list past its
        # charged state.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is still resolved."),
            "fix10f-g17-poss-stillresolved")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_heading_possessive_is_still_open_reports(self):
        # Seat 6 case x22: the cured form in the
        # heading form.
        output = _run(_heading_queue(
            "DQ-001" + APOS + "s is still open"),
            "fix10f-x22-heading-poss-is-still-open")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_banked_bridge_reports(self):
        # Seat 6 probe p02, the CH-190 charged form.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s own question, the "
            "consequence for stages passed, stays banked."),
            "fix10f-p02-possessive-banked")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_curly_banked_bridge_reports(self):
        # Seat 6 probe p03, the CH-190 charged form in
        # the curly dress.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS_CURLY + "s own question, the "
            "consequence for stages passed, stays banked."),
            "fix10f-p03-curly-banked")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_possessive_remains_banked_bridge_reports(self):
        # The bridge remains form reads the dress
        # without loss, as seat 4 case q11 records on
        # its own skeleton.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s remains banked."),
            "fix10f-poss-remains-banked-bridge")
        self.assertEqual(1, len(_claims_about(output, 1)))

    def test_plain_is_open_takes_no_claim(self):
        # Seat 6 probe p09: the shorter is open form
        # takes no Note in the plain dress.
        output = _run(_duplicate_queue("DQ-001 is open."),
                      "fix10f-p09-plain-is-open")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_is_open_takes_no_claim(self):
        # Seat 6 probe p10: the same form in the
        # possessive dress. This pin bounds the cure:
        # the is list gains the dress and still does
        # not read the shorter form.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s is open."),
            "fix10f-p10-possessive-is-open")
        self.assertEqual([], _claims_about(output, 1))

    def test_plain_intervening_takes_no_claim(self):
        # Seat 6 probe p07.
        output = _run(_duplicate_queue(
            "DQ-001 own question is still open."),
            "fix10f-p07-plain-intervening")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_intervening_takes_no_claim(self):
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s own question is still open."),
            "fix10f-possessive-intervening")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_intervening_was_takes_no_claim(self):
        # The dress stands only where it stands
        # immediately before the verb: a word standing
        # between the dress and a sibling verb loses
        # the Note exactly as the intervening is still
        # form does.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s own question was open."),
            "fix10f-possessive-intervening-was")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_comma_still_takes_no_claim(self):
        # Seat 4 observation 3, case g20.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s, is still open."),
            "fix10f-g20-poss-comma-still")
        self.assertEqual([], _claims_about(output, 1))

    def test_plain_comma_still_takes_no_claim(self):
        # Seat 4 observation 3, case g21, symmetric.
        output = _run(_duplicate_queue(
            "DQ-001, is still open."),
            "fix10f-g21-plain-comma-still")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_upper_still_takes_no_claim(self):
        # Seat 4 observation 2, case g18: the capital
        # letter S dress stands refused whole at the
        # claim guard, before any pattern is reached.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "S is still open."),
            "fix10f-g18-poss-upper-still")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_glued_was_takes_no_claim(self):
        # The glued form at the CH-190 narrowing edge:
        # a digit standing immediately after the s.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s8 was open."),
            "fix10f-poss-glued-was")
        self.assertEqual([], _claims_about(output, 1))

    def test_plain_object_mention_takes_no_claim(self):
        # A bare past verb carrying an object after it
        # reads as a ruling mention, not a claim, on
        # the standing bound of the bare past lists.
        output = _run(_duplicate_queue(
            "DQ-001 settled R-92 yesterday."),
            "fix10f-plain-object-mention")
        self.assertEqual([], _claims_about(output, 1))

    def test_possessive_object_mention_takes_no_claim(self):
        # The same mention in the possessive dress:
        # the cure gains the anchored bare past forms
        # and does not widen the object bound.
        output = _run(_duplicate_queue(
            "DQ-001" + APOS + "s settled R-92 yesterday."),
            "fix10f-poss-object-mention")
        self.assertEqual([], _claims_about(output, 1))


class Ch256PinTotalsTest(unittest.TestCase):
    """The corpus possessive row of the wave 8 suite
    determination and the PIN totals stand as pins in
    this module, as the cluster charge states."""

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
