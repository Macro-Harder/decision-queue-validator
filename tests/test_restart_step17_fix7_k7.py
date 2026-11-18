"""Restart Step 17 fix wave 7, Fix Seat K7 tests.

Charges CH-132 to CH-137, ruled at section 66 of
design/steps/step-17r-record.md, on the round 7 attack
seat 7 paper, design/steps/step-17r-attack7-7.md.

CH-132 (validate, the ghost Seal limb): finding
S17-ATK7-7-01, a ghost number named on the entry own
Status line in a Seal form, verb first (Sealed DQ-999)
or with the is predicate (DQ-999 is sealed), read by no
scan before this cure.

CH-133 (validate, the ghost state word limb): finding
S17-ATK7-7-02, a ghost number named on the entry own
Status line in the remains parked, stands presented,
left decided, or has been parked form.

CH-134 (validate, the rule 8 Note limb): finding
S17-ATK7-7-03, decision evidence naming a headed entry
with the verb first form Sealed takes no claim Note.

CH-135 (validate, the closing prose settlement limb):
finding S17-ATK7-7-04, closing prose stating the same
contradiction with a settlement noun beside closed, or
with a settlement noun beside sealed, still derives
Open as the determining element. The two K7 bound
guards (the decision noun beside sealed, the verdict
noun beside shut) stand pinned deriving Open.

CH-136 (validate, the claim form limb): finding
S17-ATK7-7-05, cross entry state claims in the is
sealed, is still shut, has been parked, and remains
sealed forms take no claim Note.

CH-137 (validate, the dressed Status heading limb):
finding S17-ATK7-7-06, a Status line standing as a
level 4 heading with a bold dressed status word inside
an entry is counted nowhere and listed nowhere.

Constructions are the finding paper own constructions,
rebuilt inline from the attack scratch files in
attack7-7-scratch/cases. Governing pins stand as
controls in this file and in the fix wave 6 K5 file
re-run whole at the close.
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


class Ch132GhostSealTest(unittest.TestCase):
    """CH-132: the ghost Seal limb, S17-ATK7-7-01."""

    def test_status_sealed_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            702, "Sealed DQ-999 in full."), "g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            703, "DQ-999 is sealed."), "g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_ruled_verb_first_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            708, "Ruled DQ-999 in full."), "g01-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_closed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            709, "DQ-999 is closed."), "g02-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch133GhostStateWordTest(unittest.TestCase):
    """CH-133: the ghost state word limb, S17-ATK7-7-02."""

    def test_status_remains_parked_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            704, "DQ-999 remains parked."), "g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stands_presented_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            705, "DQ-999 stands presented."), "g04")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_decided_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            706, "DQ-999 left decided."), "g05")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_been_parked_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            707, "DQ-999 has been parked."), "g06")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_closed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            710, "DQ-999 left closed."), "g05-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stands_decided_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            711, "DQ-999 stands decided."), "g04-pin")
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


class Ch134EvidenceSealTest(unittest.TestCase):
    """CH-134: the rule 8 Note limb, S17-ATK7-7-03."""

    def test_evidence_sealed_verb_first_takes_claim_note(self):
        output = _run(_evidence_entry(
            722, "Sealed DQ-723 in full.", 723), "e01")
        self.assertEqual(1, len(_claims_about(output, 723)))

    def test_evidence_resolved_verb_first_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            724, "Resolved DQ-725 in full.", 725), "e02")
        self.assertEqual(1, len(_claims_about(output, 725)))


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


class Ch135ClosingProseSettlementTest(unittest.TestCase):
    """CH-135: the closing prose settlement limb,
    S17-ATK7-7-04, named crossings only."""

    def test_settlement_noun_beside_closed_derives_ambiguous(self):
        output = _run(_prose_file(
            732, "The settlement is final and this entry is now "
                 "closed."), "p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-732"))

    def test_settlement_noun_beside_sealed_derives_ambiguous(self):
        output = _run(_prose_file(
            733, "The settlement is final and this entry is now "
                 "sealed."), "p02")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-733"))

    def test_settlement_noun_beside_shut_still_ambiguous_pin(self):
        output = _run(_prose_file(
            734, "The settlement is final and this entry is now "
                 "shut."), "p02-pin")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-734"))

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


class Ch136ClaimFormTest(unittest.TestCase):
    """CH-136: the claim form limb, S17-ATK7-7-05."""

    def test_claim_is_sealed_takes_note(self):
        output = _run(_claim_file(
            712, "DQ-713 is sealed.", 713), "c01")
        self.assertEqual(1, len(_claims_about(output, 713)))

    def test_claim_is_still_shut_takes_note(self):
        output = _run(_claim_file(
            714, "DQ-715 is still shut.", 715), "c02")
        self.assertEqual(1, len(_claims_about(output, 715)))

    def test_claim_has_been_parked_takes_note(self):
        output = _run(_claim_file(
            716, "DQ-717 has been parked.", 717), "c03")
        self.assertEqual(1, len(_claims_about(output, 717)))

    def test_claim_remains_sealed_takes_note(self):
        output = _run(_claim_file(
            718, "DQ-719 remains sealed.", 719), "c04")
        self.assertEqual(1, len(_claims_about(output, 719)))

    def test_claim_remains_parked_still_takes_note_pin(self):
        output = _run(_claim_file(
            720, "DQ-721 remains parked.", 721), "c01-pin")
        self.assertEqual(1, len(_claims_about(output, 721)))

    def test_claim_is_still_decided_still_takes_note_pin(self):
        output = _run(_claim_file(
            726, "DQ-727 is still decided.", 727), "c02-pin")
        self.assertEqual(1, len(_claims_about(output, 727)))


class Ch137DressedStatusHeadingTest(unittest.TestCase):
    """CH-137: the dressed Status heading limb,
    S17-ATK7-7-06."""

    def _heading_hits(self, output):
        return [f for f in h.findings_of(output)
                if h.span_of(f)[0] == 17
                and "standing as a heading" in
                (h.finding_statement(f) or "")]

    def test_heading_bold_status_line_takes_a_signal(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            743, "Banked head, heading status probe",
            "\n#### **Status:** RULED, closed\n"))
        output = _run(data, "s02-bold")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_plain_status_still_takes_signal_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            744, "Banked head, heading status probe",
            "\n#### Status: RULED, closed\n"))
        output = _run(data, "s02-plain-pin")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_lowercase_status_still_takes_signal_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            745, "Banked head, heading status probe",
            "\n#### status: RULED, closed\n"))
        output = _run(data, "s02-lower-pin")
        self.assertEqual(1, len(self._heading_hits(output)))

    def test_heading_no_space_form_stays_counted_pin(self):
        data = ("# Decision queue\n\n" + _banked_entry(
            742, "Banked head, heading status probe",
            "\n####Status: RULED, closed\n"))
        output = _run(data, "s01-nospace")
        self.assertEqual([], self._heading_hits(output))
        self.assertEqual("Ruled", _state_of(output, "DQ-742"))


if __name__ == "__main__":
    unittest.main()
