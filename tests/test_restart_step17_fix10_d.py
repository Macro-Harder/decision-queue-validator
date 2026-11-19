"""Restart Step 17 fix wave 10, Fix Seat D tests.

Charges CH-242 to CH-248, ruled at section 83 of
design/steps/step-17r-record.md, on the round 10 triage
preparation paper
design/steps/step-17r-r10-triage-prep.md, Cluster D, and
on the round 10 attack seat 7 paper,
design/steps/step-17r-r10-seat07.md, and the round 10
attack seat 15 paper,
design/steps/step-17r-r10-seat15.md.

CH-242 (validate, the ghost was, has, and bare past
resolved limb): finding S17-ATK10-7-01 (T10-14), a ghost
number named on the entry own Status line in the was
resolved, has resolved, or bare past resolved form is
read by no scan. Seat 15 finding F-15-10-1 states the
same constructions.

CH-243 (validate, the ghost left list limb): finding
S17-ATK10-7-02 (T10-15), a ghost number named on the
entry own Status line in the left settled, left ruled,
or left resolved form is read by no scan.

CH-244 (validate, the ghost got parked and got
presented limb): finding S17-ATK10-7-03 (T10-16), a
ghost number named on the entry own Status line in the
got parked or got presented form is read by no scan.

CH-245 (validate, the evidence stays, got, and has
limb): finding S17-ATK10-7-05 (T10-17), decision
evidence naming a headed entry in the stays resolved,
got resolved, has sealed, or has resolved form takes
no claim Note. Seat 15 finding F-15-10-2 states the
stays and got members of the same constructions.

CH-246 (validate, the closing prose finished,
concluded, and complete limb): finding
S17-ATK10-7-07 (T10-18), closing prose with the
closure word finished, concluded, or complete beside
a cured verb or noun form still derives Open as the
determining element. The two K7 bound guards (the
decision noun beside sealed, the verdict noun beside
shut) stand pinned deriving Open in both directions,
expressly outside this charge.

CH-247 (validate, the ghost is still and is now
limb): finding S17-ATK10-7-04 (T10-27), the ghost
scan reads no is still form and no is now form for
any state word, the resolved and sealed forms among
them.

CH-248 (validate, the cross entry claim stays, got,
has, remains fully, left, and is now limb): finding
S17-ATK10-7-06 (T10-28), cross entry state claims in
the stays, got, has, remains fully, left, and is now
resolved forms, and in the has sealed form, take no
claim Note. Seat 15 finding F-15-10-3 states the
stays, got, has resolved, and has sealed members of
the same constructions.

Constructions are the finding papers own
constructions, rebuilt inline from the attack scratch
files in attack10-7-scratch and
attack10-15-scratch. Governing pins stand as controls
in this file and in the earlier wave files for this
surface re-run whole at the close.
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


class Ch242GhostWasHasBarePastResolvedTest(unittest.TestCase):
    """CH-242: the ghost was, has, and bare past
    resolved limb, S17-ATK10-7-01."""

    def test_status_was_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1002, "DQ-999 was resolved."), "g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1004, "DQ-999 has resolved."), "g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_resolved_bare_past_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1003, "DQ-999 resolved yesterday."), "g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_was_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1012, "DQ-999 was sealed."), "g11-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_settled_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1101, "DQ-999 has settled."), "g03-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch243GhostLeftListTest(unittest.TestCase):
    """CH-243: the ghost left settled, left ruled, and
    left resolved limb, S17-ATK10-7-02."""

    def test_status_left_settled_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1005, "DQ-999 left settled."), "g04")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_ruled_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1006, "DQ-999 left ruled."), "g05")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1013, "DQ-999 left resolved."), "g12")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_closed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1102, "DQ-999 left closed."), "g04-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch244GhostGotParkedPresentedTest(unittest.TestCase):
    """CH-244: the ghost got parked and got presented
    limb, S17-ATK10-7-03."""

    def test_status_got_parked_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1007, "DQ-999 got parked."), "g06")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_got_presented_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1008, "DQ-999 got presented."), "g07")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_got_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1103, "DQ-999 got sealed."), "g06-pin")
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


class Ch245EvidenceStaysGotHasTest(unittest.TestCase):
    """CH-245: the evidence stays resolved, got
    resolved, has sealed, and has resolved limb,
    S17-ATK10-7-05."""

    def test_evidence_stays_resolved_takes_claim_note(self):
        output = _run(_evidence_entry(
            1052, "DQ-1053 stays resolved.", 1053), "e01")
        self.assertEqual(1, len(_claims_about(output, 1053)))

    def test_evidence_got_resolved_takes_claim_note(self):
        output = _run(_evidence_entry(
            1054, "DQ-1055 got resolved.", 1055), "e02")
        self.assertEqual(1, len(_claims_about(output, 1055)))

    def test_evidence_has_sealed_takes_claim_note(self):
        output = _run(_evidence_entry(
            1056, "DQ-1057 has sealed.", 1057), "e03")
        self.assertEqual(1, len(_claims_about(output, 1057)))

    def test_evidence_has_resolved_takes_claim_note(self):
        output = _run(_evidence_entry(
            1060, "DQ-1061 has resolved.", 1061), "e05")
        self.assertEqual(1, len(_claims_about(output, 1061)))

    def test_evidence_was_resolved_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            1058, "DQ-1059 was resolved.", 1059), "e04-pin")
        self.assertEqual(1, len(_claims_about(output, 1059)))


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


class Ch246ClosingProseFinishedConcludedCompleteTest(
        unittest.TestCase):
    """CH-246: the closing prose finished, concluded,
    and complete limb, S17-ATK10-7-07, named crossings
    only."""

    def test_decided_verb_beside_finished_derives_ambiguous(self):
        output = _run(_prose_file(
            1072, "The question was decided in full and this "
                  "entry is now finished."), "p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1072"))

    def test_resolved_verb_beside_concluded_derives_ambiguous(self):
        output = _run(_prose_file(
            1073, "The question was resolved in full and this "
                  "entry is now concluded."), "p02")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1073"))

    def test_settlement_noun_beside_finished_derives_ambiguous(self):
        output = _run(_prose_file(
            1074, "The settlement was recorded in full and this "
                  "entry is now finished."), "p03")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1074"))

    def test_decided_verb_beside_complete_derives_ambiguous(self):
        output = _run(_prose_file(
            1076, "The question was decided in full and this "
                  "entry is now complete."), "p05")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1076"))

    def test_resolved_verb_beside_closed_still_ambiguous_pin(self):
        output = _run(_prose_file(
            1075, "The question was resolved in full and this "
                  "entry is now closed."), "p04-pin")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1075"))

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


class Ch247GhostIsStillIsNowTest(unittest.TestCase):
    """CH-247: the ghost is still and is now limb,
    S17-ATK10-7-04."""

    def test_status_is_still_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1009, "DQ-999 is still resolved."), "g08")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_still_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1010, "DQ-999 is still sealed."), "g09")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_now_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1014, "DQ-999 is now resolved."), "g13")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_now_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1015, "DQ-999 is now sealed."), "g14")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_resolved_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1104, "DQ-999 is resolved."), "g08-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


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


class Ch248ClaimStaysGotHasFullyLeftNowTest(unittest.TestCase):
    """CH-248: the cross entry claim stays, got, has,
    remains fully, left, and is now resolved forms, and
    the has sealed form, S17-ATK10-7-06."""

    def test_claim_stays_resolved_takes_note(self):
        output = _run(_claim_file(
            1032, "DQ-1033 stays resolved.", 1033), "c01")
        self.assertEqual(1, len(_claims_about(output, 1033)))

    def test_claim_got_resolved_takes_note(self):
        output = _run(_claim_file(
            1034, "DQ-1035 got resolved.", 1035), "c02")
        self.assertEqual(1, len(_claims_about(output, 1035)))

    def test_claim_has_resolved_takes_note(self):
        output = _run(_claim_file(
            1036, "DQ-1037 has resolved.", 1037), "c03")
        self.assertEqual(1, len(_claims_about(output, 1037)))

    def test_claim_has_sealed_takes_note(self):
        output = _run(_claim_file(
            1038, "DQ-1039 has sealed.", 1039), "c04")
        self.assertEqual(1, len(_claims_about(output, 1039)))

    def test_claim_remains_fully_resolved_takes_note(self):
        output = _run(_claim_file(
            1040, "DQ-1041 remains fully resolved.", 1041), "c05")
        self.assertEqual(1, len(_claims_about(output, 1041)))

    def test_claim_left_resolved_takes_note(self):
        output = _run(_claim_file(
            1042, "DQ-1043 left resolved.", 1043), "c06")
        self.assertEqual(1, len(_claims_about(output, 1043)))

    def test_claim_is_now_resolved_takes_note(self):
        output = _run(_claim_file(
            1048, "DQ-1049 is now resolved.", 1049), "c09")
        self.assertEqual(1, len(_claims_about(output, 1049)))

    def test_claim_stands_resolved_still_takes_note_pin(self):
        output = _run(_claim_file(
            1044, "DQ-1045 stands resolved.", 1045), "c07-pin")
        self.assertEqual(1, len(_claims_about(output, 1045)))

    def test_claim_has_been_sealed_still_takes_note_pin(self):
        output = _run(_claim_file(
            1046, "DQ-1047 has been sealed.", 1047), "c08-pin")
        self.assertEqual(1, len(_claims_about(output, 1047)))


if __name__ == "__main__":
    unittest.main()
