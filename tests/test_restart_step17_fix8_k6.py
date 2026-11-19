"""Restart Step 17 fix wave 8, Fix Seat K6 tests.

Charges CH-164, CH-165, CH-167, CH-168, CH-169, CH-177,
CH-178, and CH-179, ruled at section 77 of
design/steps/step-17r-record.md, on the round 8 attack
seat 7 paper, design/steps/step-17r-attack8-7.md.

CH-164 (validate, the ghost sealed family limb):
finding S17-ATK8-7-01, a ghost number named on the entry
own Status line in the was sealed, has been sealed,
stands sealed, remains sealed, or got sealed form is
read by no scan.

CH-165 (validate, the ghost parked, presented, and
left shut limb): finding S17-ATK8-7-02, a ghost number
named on the entry own Status line in the is parked,
is presented, or left shut form is read by no scan.

CH-167 (validate, the ghost verb first Shut limb):
finding S17-ATK8-7-03, a ghost number named on the
entry own Status line in the verb first Shut form is
read by no scan.

CH-168 (validate, the evidence verb first Shut limb):
finding S17-ATK8-7-04, decision evidence naming a
headed entry with the verb first forms Shut or Shuts
takes no claim Note.

CH-169 (validate, the closing prose resolved and
sealed verb limb): finding S17-ATK8-7-05, closing prose
stating the standing contradiction with a resolved verb
beside closed, or with a sealed verb beside closed,
still derives Open as the determining element. The two
K7 bound guards (the decision noun beside sealed, the
verdict noun beside shut) stand pinned deriving Open.

CH-177 (validate, the cross entry claim sealed family
limb): finding S17-ATK8-7-06, cross entry state claims
in the was sealed, has been sealed, got sealed, and
bare past sealed forms take no claim Note.

CH-178 (validate, the cross entry claim is resolved
limb): finding S17-ATK8-7-07, a cross entry state claim
in the is resolved form takes no claim Note.

CH-179 (validate, the dressed Status heading limb):
finding S17-ATK8-7-08, a Status line standing as a
level 4 heading with an italic dressed, underscore
dressed, or bold dress with its colon outside the
dress, status word inside an entry is counted nowhere
and listed nowhere.

Constructions are the finding paper own constructions,
rebuilt inline from the attack scratch files in
attack8-7-scratch/cases. Governing pins stand as
controls in this file and in the earlier wave files for
this surface re-run whole at the close.
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


class Ch164GhostSealedFamilyTest(unittest.TestCase):
    """CH-164: the ghost sealed family limb,
    S17-ATK8-7-01."""

    def test_status_was_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            804, "DQ-999 was sealed."), "g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_been_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            805, "DQ-999 has been sealed."), "g04")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stands_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            806, "DQ-999 stands sealed."), "g05")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_remains_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            810, "DQ-999 remains sealed."), "g09")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_got_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            809, "DQ-999 got sealed."), "g08")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            811, "DQ-999 is sealed."), "g03-pin-is")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_been_parked_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            812, "DQ-999 has been parked."), "g04-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch165GhostParkedPresentedLeftShutTest(unittest.TestCase):
    """CH-165: the ghost is parked, is presented, and
    left shut limb, S17-ATK8-7-02."""

    def test_status_is_parked_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            802, "DQ-999 is parked."), "g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_presented_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            803, "DQ-999 is presented."), "g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_shut_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            807, "DQ-999 left shut."), "g06")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_closed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            813, "DQ-999 left closed."), "g06-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_closed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            814, "DQ-999 is closed."), "g01-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch167GhostShutVerbFirstTest(unittest.TestCase):
    """CH-167: the ghost verb first Shut limb,
    S17-ATK8-7-03."""

    def test_status_shut_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            808, "Shut DQ-999 in full."), "g07")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_sealed_verb_first_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            815, "Sealed DQ-999 in full."), "g07-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


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


class Ch168EvidenceShutVerbFirstTest(unittest.TestCase):
    """CH-168: the evidence verb first Shut limb,
    S17-ATK8-7-04."""

    def test_evidence_shut_verb_first_takes_claim_note(self):
        output = _run(_evidence_entry(
            822, "Shut DQ-823 in full.", 823), "e01")
        self.assertEqual(1, len(_claims_about(output, 823)))

    def test_evidence_shuts_verb_first_takes_claim_note(self):
        output = _run(_evidence_entry(
            824, "Shuts DQ-825 in full.", 825), "e02")
        self.assertEqual(1, len(_claims_about(output, 825)))

    def test_evidence_sealed_verb_first_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            826, "Sealed DQ-827 in full.", 827), "e01-pin")
        self.assertEqual(1, len(_claims_about(output, 827)))


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


class Ch169ClosingProseResolvedSealedVerbTest(unittest.TestCase):
    """CH-169: the closing prose resolved and sealed
    verb limb, S17-ATK8-7-05, named crossings only."""

    def test_resolved_verb_beside_closed_derives_ambiguous(self):
        output = _run(_prose_file(
            832, "The question was resolved in full and this "
                 "entry is now closed."), "p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-832"))

    def test_sealed_verb_beside_closed_derives_ambiguous(self):
        output = _run(_prose_file(
            833, "This entry was sealed in full and is now "
                 "closed."), "p02")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-833"))

    def test_settlement_noun_beside_shut_still_ambiguous_pin(self):
        output = _run(_prose_file(
            834, "The settlement is final and this entry is now "
                 "shut."), "p01-pin")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-834"))

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


class Ch177ClaimSealedFamilyTest(unittest.TestCase):
    """CH-177: the cross entry claim sealed family limb,
    S17-ATK8-7-06."""

    def test_claim_was_sealed_takes_note(self):
        output = _run(_claim_file(
            812, "DQ-813 was sealed.", 813), "c01")
        self.assertEqual(1, len(_claims_about(output, 813)))

    def test_claim_has_been_sealed_takes_note(self):
        output = _run(_claim_file(
            814, "DQ-815 has been sealed.", 815), "c02")
        self.assertEqual(1, len(_claims_about(output, 815)))

    def test_claim_got_sealed_takes_note(self):
        output = _run(_claim_file(
            818, "DQ-819 got sealed.", 819), "c04")
        self.assertEqual(1, len(_claims_about(output, 819)))

    def test_claim_sealed_bare_past_takes_note(self):
        output = _run(_claim_file(
            816, "DQ-817 sealed yesterday.", 817), "c03")
        self.assertEqual(1, len(_claims_about(output, 817)))

    def test_claim_remains_sealed_still_takes_note_pin(self):
        output = _run(_claim_file(
            828, "DQ-829 remains sealed.", 829), "c01-pin")
        self.assertEqual(1, len(_claims_about(output, 829)))

    def test_claim_is_sealed_still_takes_note_pin(self):
        output = _run(_claim_file(
            830, "DQ-831 is sealed.", 831), "c02-pin")
        self.assertEqual(1, len(_claims_about(output, 831)))


class Ch178ClaimIsResolvedTest(unittest.TestCase):
    """CH-178: the cross entry claim is resolved limb,
    S17-ATK8-7-07."""

    def test_claim_is_resolved_takes_note(self):
        output = _run(_claim_file(
            820, "DQ-821 is resolved.", 821), "c05")
        self.assertEqual(1, len(_claims_about(output, 821)))

    def test_claim_is_decided_still_takes_note_pin(self):
        output = _run(_claim_file(
            836, "DQ-837 is decided.", 837), "c05-pin")
        self.assertEqual(1, len(_claims_about(output, 837)))


class Ch179DressedStatusHeadingTest(unittest.TestCase):
    """CH-179: the dressed Status heading limb,
    S17-ATK8-7-08."""

    def _heading_hits(self, output):
        return [f for f in h.findings_of(output)
                if h.span_of(f)[0] == 17
                and "standing as a heading" in
                (h.finding_statement(f) or "")]

    def test_heading_italic_status_line_takes_a_signal(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            842, "Banked head, heading status probe",
            "\n#### *Status:* RULED, closed\n"))
        output = _run(data, "s01-italic")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_underscore_status_line_takes_a_signal(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            843, "Banked head, heading status probe",
            "\n#### __Status:__ RULED, closed\n"))
        output = _run(data, "s02-underscore")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_bold_colon_outside_takes_a_signal(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            844, "Banked head, heading status probe",
            "\n#### **Status**: RULED, closed\n"))
        output = _run(data, "s03-bold-outside")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_bold_colon_inside_still_takes_signal_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            845, "Banked head, heading status probe",
            "\n#### **Status:** RULED, closed\n"))
        output = _run(data, "s03-pin-bold-inside")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_plain_status_still_takes_signal_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            846, "Banked head, heading status probe",
            "\n#### Status: RULED, closed\n"))
        output = _run(data, "s01-pin-plain")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_no_space_form_stays_counted_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            847, "Banked head, heading status probe",
            "\n####Status: RULED, closed\n"))
        output = _run(data, "s01-pin-nospace")
        self.assertEqual([], self._heading_hits(output))
        self.assertEqual("Ruled", _state_of(output, "DQ-847"))


if __name__ == "__main__":
    unittest.main()
