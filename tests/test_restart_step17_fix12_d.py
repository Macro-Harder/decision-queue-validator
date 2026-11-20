"""Restart Step 17 fix wave 12, Fix Seat D tests.

Charges CH-330 to CH-334, Cluster D (the ghost and
claim scans), as proposed in section 3 of
design/steps/step-17r-r12-triage-prep.md, on round 12
attack seat 6 findings S17-ATK12-6-01 to
S17-ATK12-6-05 (design/steps/step-17r-r12-seat06-run.md)
and round 12 attack seat 14 findings F-15-12-1 to
F-15-12-3 (design/steps/step-17r-r12-seat14-run.md).
The ghost intervening word limb (CH-331) stands at
Medium, seat 14's grade governing over seat 6's Low,
as the triage preparation names the split.

CH-330 (validate, the ghost bare past time phrase
limb): a ghost number on the entry own Status line in
the bare past form closing on last month or last year
is read by no scan.

CH-331 (validate, the ghost intervening word limb,
Medium as the governing grade): a ghost number on the
entry own Status line with an intervening word outside
the CH-293 sets, with two intervening words, with a
word standing between has and been or between been and
the state word, or in the present tense verb first
form (Parks, Presents), is read by no scan.

CH-332 (validate, the decision evidence limb):
decision evidence in the has with an intervening word,
is yet, was already, fully with a state word outside
the direct pattern, is now with a state word outside
the direct pattern, got with an intervening word, bare
past on a month phrase, has been with an intervening
word, stands still, or present tense verb first form
takes no claim Note.

CH-333 (validate, the closing prose limb): closing
prose beside a pairing or a closure word the CH-292
crossings do not carry (the decision, ruling, and
verdict nouns beside done, ended, and over; the sealed
verb beside finished; the closure words wrapped up and
finalized beside the decided verb, the resolved verb,
and the settlement noun) still derives Open. The two
K7 bound guards stand pinned deriving Open, expressly
outside this charge.

CH-334 (validate, the cross entry claim limb): cross
entry state claims in the same forms as CH-332 take
no claim Note.

Constructions are the finding papers own
constructions, rebuilt inline from the attack scratch
files in attack12-06-scratch and attack12-14-scratch.
The cured Cluster D forms stand as pins in this file
and in the earlier wave files for this surface.
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")


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


def _state_of(output, identifier):
    entry = h.entry_by_id(output, identifier)
    if entry is None:
        raise AssertionError("no entry %s in output" % identifier)
    return h.entry_state(entry)


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


def _ghost_case(test, host, status_value, tag):
    output = _run(_ghost_status_entry(host, status_value), tag)
    test.assertEqual(1, len(_pd_r7(output, 999)), status_value)


class Ch330GhostBarePastTimePhraseTest(unittest.TestCase):
    """CH-330: the ghost bare past form closing on last
    month or last year, S17-ATK12-6-01 (T12-16)."""

    def test_status_parked_last_month_takes_ghost_note(self):
        _ghost_case(self, 1601, "DQ-999 parked last month.", "g08")

    def test_status_parked_last_year_takes_ghost_note(self):
        _ghost_case(self, 1602, "DQ-999 parked last year.", "g16")

    def test_status_resolved_last_month_takes_ghost_note(self):
        _ghost_case(self, 1603, "DQ-999 resolved last month.", "g17")

    def test_status_presented_last_year_takes_ghost_note(self):
        _ghost_case(self, 1604, "DQ-999 presented last year.", "g18")

    def test_status_parked_yesterday_still_takes_note_pin(self):
        _ghost_case(self, 1605, "DQ-999 parked yesterday.", "pin1")

    def test_status_closed_last_week_still_takes_note_pin(self):
        _ghost_case(self, 1606, "DQ-999 closed last week.", "pin2")


class Ch331GhostInterveningWordTest(unittest.TestCase):
    """CH-331: the ghost intervening word limb,
    S17-ATK12-6-02 with F-15-12-1, at Medium as the
    governing grade (T12-17)."""

    def test_one_word_outside_sets_seat6_members(self):
        forms = [
            "DQ-999 was now resolved.",
            "DQ-999 is finally resolved.",
            "DQ-999 has fully resolved.",
            "DQ-999 remains still resolved.",
            "DQ-999 stands already sealed.",
            "DQ-999 got fully resolved.",
            "DQ-999 remains completely resolved.",
            "DQ-999 is soon resolved.",
        ]
        for i, form in enumerate(forms):
            with self.subTest(form=form):
                _ghost_case(self, 1610 + i, form, "s6-%d" % i)

    def test_one_word_outside_sets_seat14_members(self):
        forms = [
            "DQ-999 remains already resolved.",
            "DQ-999 stands still resolved.",
            "DQ-999 stays yet sealed.",
            "DQ-999 was finally resolved.",
            "DQ-999 has just resolved.",
            "DQ-999 remains now resolved.",
            "DQ-999 stands already resolved.",
        ]
        for i, form in enumerate(forms):
            with self.subTest(form=form):
                _ghost_case(self, 1620 + i, form, "s14-%d" % i)

    def test_two_intervening_words(self):
        forms = [
            "DQ-999 is still fully resolved.",
            "DQ-999 remains very fully resolved.",
            "DQ-999 has now fully resolved.",
        ]
        for i, form in enumerate(forms):
            with self.subTest(form=form):
                _ghost_case(self, 1630 + i, form, "two-%d" % i)

    def test_word_between_has_and_been_or_after_been(self):
        forms = [
            "DQ-999 has been fully resolved.",
            "DQ-999 has already been resolved.",
            "DQ-999 has been still resolved.",
        ]
        for i, form in enumerate(forms):
            with self.subTest(form=form):
                _ghost_case(self, 1640 + i, form, "been-%d" % i)

    def test_present_tense_verb_first_parks(self):
        _ghost_case(self, 1650, "Parks DQ-999.", "g12")

    def test_present_tense_verb_first_presents(self):
        _ghost_case(self, 1651, "Presents DQ-999.", "g13")

    def test_status_was_yet_resolved_still_takes_note_pin(self):
        _ghost_case(self, 1652, "DQ-999 was yet resolved.", "pin1")

    def test_status_has_now_resolved_still_takes_note_pin(self):
        _ghost_case(self, 1653, "DQ-999 has now resolved.", "pin2")

    def test_status_remains_fully_sealed_still_takes_note_pin(self):
        _ghost_case(self, 1654, "DQ-999 remains fully sealed.", "pin3")

    def test_status_has_finally_resolved_still_takes_note_pin(self):
        _ghost_case(self, 1655, "DQ-999 has finally resolved.", "pin4")


def _evidence_entry(number, ruling_text, target_number):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Evidence claim probe\n"
        "\n"
        "Status: RULED, closed\n"
        "\n"
        "Ruled by: Captain JP\n"
        "\n"
        "Ruling text: \"%s\"\n"
        "\n"
        "Ruling outcome: Recorded in full.\n"
        "\n"
        "Where the ruling landed: NOWHERE.md, sample rule.\n"
        "\n"
        % (number, ruling_text)
        + _banked_entry(target_number, "An ordinary banked entry"))


def _evidence_case(test, host, text, target, tag):
    output = _run(_evidence_entry(host, text, target), tag)
    test.assertEqual(1, len(_claims_about(output, target)), text)


class Ch332EvidenceFormsTest(unittest.TestCase):
    """CH-332: decision evidence in the forms named at
    T12-18, S17-ATK12-6-03 with F-15-12-2."""

    def test_evidence_has_intervening_word(self):
        forms = [
            (1660, "DQ-1661 has now resolved.", 1661),
            (1662, "DQ-1663 has finally sealed.", 1663),
            (1664, "DQ-1665 has now sealed.", 1665),
        ]
        for host, text, target in forms:
            with self.subTest(text=text):
                _evidence_case(self, host, text, target, "has")

    def test_evidence_is_yet_and_was_already(self):
        forms = [
            (1666, "DQ-1667 is yet resolved.", 1667),
            (1668, "DQ-1669 was already resolved.", 1669),
            (1670, "DQ-1671 was already sealed.", 1671),
        ]
        for host, text, target in forms:
            with self.subTest(text=text):
                _evidence_case(self, host, text, target, "yet")

    def test_evidence_fully_state_outside_direct(self):
        forms = [
            (1672, "DQ-1673 stands fully parked.", 1673),
            (1674, "DQ-1675 remains fully closed.", 1675),
            (1676, "DQ-1677 remains fully parked.", 1677),
        ]
        for host, text, target in forms:
            with self.subTest(text=text):
                _evidence_case(self, host, text, target, "fully")

    def test_evidence_is_now_state_outside_direct(self):
        forms = [
            (1678, "DQ-1679 is now parked.", 1679),
            (1680, "DQ-1681 is now presented.", 1681),
        ]
        for host, text, target in forms:
            with self.subTest(text=text):
                _evidence_case(self, host, text, target, "isnow")

    def test_evidence_got_fully_parked(self):
        _evidence_case(self, 1682, "DQ-1683 got fully parked.",
                       1683, "e08")

    def test_evidence_parked_last_month(self):
        _evidence_case(self, 1684, "DQ-1685 parked last month.",
                       1685, "e09")

    def test_evidence_has_been_fully_resolved(self):
        _evidence_case(self, 1686, "DQ-1687 has been fully resolved.",
                       1687, "e10")

    def test_evidence_stands_still_resolved(self):
        _evidence_case(self, 1688, "DQ-1689 stands still resolved.",
                       1689, "h06")

    def test_evidence_parks_verb_first(self):
        _evidence_case(self, 1690, "Parks DQ-1691.", 1691, "e05vf")

    def test_evidence_presents_verb_first(self):
        _evidence_case(self, 1692, "Presents DQ-1693.", 1693, "e06vf")

    def test_evidence_got_parked_still_takes_note_pin(self):
        _evidence_case(self, 1694, "DQ-1695 got parked.", 1695, "pin1")

    def test_evidence_is_now_sealed_still_takes_note_pin(self):
        _evidence_case(self, 1696, "DQ-1697 is now sealed.", 1697,
                       "pin2")


def _prose_file(number, closing_sentence):
    return (
        "# Decision queue\n"
        "\n"
        "### DQ-%03d: Banked head, prose probe\n"
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
        "\n"
        "%s Nothing remains open on it.\n"
        % (number, closing_sentence))


class Ch333ClosingProseCrossingsTest(unittest.TestCase):
    """CH-333: closing prose beside a pairing or a
    closure word the CH-292 crossings do not carry,
    S17-ATK12-6-05 (T12-19), named crossings only."""

    def test_noun_beside_done_ended_over_derives_ambiguous(self):
        forms = [
            (1701, "The decision was recorded in full and this "
                   "entry is now done."),
            (1702, "The ruling was recorded in full and this "
                   "entry is now ended."),
            (1703, "The verdict was recorded in full and this "
                   "entry is now over."),
            (1704, "The decision was recorded in full and this "
                   "entry is now over."),
            (1705, "The ruling was recorded in full and this "
                   "entry is now done."),
            (1706, "The verdict was recorded in full and this "
                   "entry is now ended."),
        ]
        for number, sentence in forms:
            with self.subTest(sentence=sentence):
                output = _run(_prose_file(number, sentence), "noun")
                self.assertEqual("Ambiguous",
                                 _state_of(output, "DQ-%04d" % number))

    def test_sealed_verb_beside_finished_derives_ambiguous(self):
        output = _run(_prose_file(
            1707, "The question was sealed in full and this "
                  "entry is now finished."), "p05")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1707"))

    def test_new_closure_words_derive_ambiguous(self):
        forms = [
            (1708, "The question was decided in full and this "
                   "entry is now wrapped up."),
            (1709, "The question was resolved in full and this "
                   "entry is now finalized."),
            (1710, "The settlement was recorded in full and this "
                   "entry is now wrapped up."),
        ]
        for number, sentence in forms:
            with self.subTest(sentence=sentence):
                output = _run(_prose_file(number, sentence), "new")
                self.assertEqual("Ambiguous",
                                 _state_of(output, "DQ-%04d" % number))

    def test_settlement_beside_over_still_ambiguous_pin(self):
        output = _run(_prose_file(
            1711, "The settlement was recorded in full and this "
                  "entry is now over."), "pin1")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1711"))

    def test_decision_beside_complete_still_ambiguous_pin(self):
        output = _run(_prose_file(
            1712, "The decision was recorded in full and this "
                  "entry is now complete."), "pin2")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1712"))

    def test_decision_noun_beside_sealed_still_open_guard(self):
        output = _run(_prose_file(
            535, "The decision is final and this entry is now "
                 "sealed."), "guard-decision-sealed")
        self.assertEqual("Open", _state_of(output, "DQ-535"))

    def test_verdict_noun_beside_shut_still_open_guard(self):
        output = _run(_prose_file(
            536, "The verdict is final and this entry is now "
                 "shut."), "guard-verdict-shut")
        self.assertEqual("Open", _state_of(output, "DQ-536"))


def _claim_file(number, claim_sentence, target_number):
    host = (
        "### DQ-%03d: Claim probe\n"
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
        "This question is waiting for a decision. %s\n"
        % (number, claim_sentence))
    return ("# Decision queue\n\n" + host + "\n"
            + _banked_entry(target_number,
                            "An ordinary banked entry"))


def _claim_case(test, host, text, target, tag):
    output = _run(_claim_file(host, text, target), tag)
    test.assertEqual(1, len(_claims_about(output, target)), text)


class Ch334ClaimCrossEntryFormsTest(unittest.TestCase):
    """CH-334: cross entry state claims in the forms
    named at T12-25, S17-ATK12-6-04 with F-15-12-3."""

    def test_claim_fully_state_outside_direct(self):
        forms = [
            (1720, "DQ-1721 remains fully parked.", 1721),
            (1722, "DQ-1723 stands fully presented.", 1723),
            (1724, "DQ-1725 stays fully closed.", 1725),
            (1726, "DQ-1727 remains fully decided.", 1727),
            (1728, "DQ-1729 stands fully parked.", 1729),
        ]
        for host, text, target in forms:
            with self.subTest(text=text):
                _claim_case(self, host, text, target, "fully")

    def test_claim_is_now_state_outside_direct(self):
        forms = [
            (1730, "DQ-1731 is now parked.", 1731),
            (1732, "DQ-1733 is now closed.", 1733),
            (1734, "DQ-1735 is now decided.", 1735),
        ]
        for host, text, target in forms:
            with self.subTest(text=text):
                _claim_case(self, host, text, target, "isnow")

    def test_claim_adverb_between_verb_and_state(self):
        forms = [
            (1736, "DQ-1737 was already resolved.", 1737),
            (1738, "DQ-1739 is yet resolved.", 1739),
            (1740, "DQ-1741 has now resolved.", 1741),
            (1742, "DQ-1743 remains already resolved.", 1743),
            (1744, "DQ-1745 has finally resolved.", 1745),
        ]
        for host, text, target in forms:
            with self.subTest(text=text):
                _claim_case(self, host, text, target, "adv")

    def test_claim_got_fully_resolved(self):
        _claim_case(self, 1746, "DQ-1747 got fully resolved.",
                    1747, "c17")

    def test_claim_is_still_fully_resolved_two_words(self):
        _claim_case(self, 1748, "DQ-1749 is still fully resolved.",
                    1749, "c16")

    def test_claim_presented_last_month(self):
        _claim_case(self, 1750, "DQ-1751 presented last month.",
                    1751, "c09")

    def test_claim_has_been_fully_resolved(self):
        _claim_case(self, 1752, "DQ-1753 has been fully resolved.",
                    1753, "c10")

    def test_claim_remains_fully_resolved_still_takes_note_pin(self):
        _claim_case(self, 1754, "DQ-1755 remains fully resolved.",
                    1755, "pin1")

    def test_claim_was_still_sealed_still_takes_note_pin(self):
        _claim_case(self, 1756, "DQ-1757 was still sealed.",
                    1757, "pin2")


if __name__ == "__main__":
    unittest.main()
