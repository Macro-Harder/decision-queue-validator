"""Restart Step 17 fix wave 11, Fix Seat D tests.

Charges CH-290 to CH-294, as determined at record
section 108 of design/steps/step-17r-record.md, on the
round 11 triage preparation paper
design/steps/step-17r-r11-triage-prep.md, Cluster D,
and on round 11 attack seat 7 findings
S17-ATK11-7-01 to S17-ATK11-7-05
(design/steps/step-17r-r11-seat07-run.md) and round 11
attack seat 15 findings F-15-11-1 to F-15-11-3
(design/steps/step-17r-r11-seat15-run.md).

CH-290 (validate, the ghost own Status line has, left,
and bare past parked and presented limb): findings
S17-ATK11-7-01 (T11-15) with seat 15 finding F-15-11-1
standing inside it, a ghost number named on the entry
own Status line in the has parked, has presented, left
parked, left presented, parked bare past, or presented
bare past form is read by no scan.

CH-291 (validate, the decision evidence got, bare
past, fully, verb first, and is now limb): finding
S17-ATK11-7-03 (T11-16) with seat 15 finding F-15-11-2
standing inside it, decision evidence naming a headed
entry in the got parked, bare past parked, stands
fully resolved, remains fully sealed, verb first
parked, or is now sealed form takes no claim Note.

CH-292 (validate, the closing prose noun and closure
word limb): finding S17-ATK11-7-05 (T11-17), closing
prose stating the same contradiction beside a noun or
a closure word the CH-246 crossings do not carry still
derives Open. The two K7 bound guards (the decision
noun beside sealed, the verdict noun beside shut)
stand pinned deriving Open in both directions,
expressly outside this charge.

CH-293 (validate, the ghost word between and verb
first limb): finding S17-ATK11-7-02 (T11-24) with seat
15 finding F-15-11-1's was still resolved member
standing inside it, a ghost number named on the entry
own Status line with a word standing between the verb
and the state word, or in the verb first form, is read
by no scan.

CH-294 (validate, the cross entry claim limb):
finding S17-ATK11-7-04 (T11-25) with seat 15 finding
F-15-11-3 standing inside it, cross entry state claims
in the got, has, and bare past parked and presented
forms and in the stands fully, stays fully, remains
fully sealed, is already, was still, and is already
sealed forms take no claim Note.

Constructions are the finding papers own
constructions, rebuilt inline from the attack scratch
files in attack11-7-scratch and attack11-15-scratch.
The cured Cluster D forms stand as pins in this file
and in the earlier wave files for this surface re-run
whole at the close.
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


class Ch290GhostHasLeftBarePastParkedPresentedTest(unittest.TestCase):
    """CH-290: the ghost own Status line has parked,
    has presented, left parked, left presented, parked
    bare past, and presented bare past limb,
    S17-ATK11-7-01 with F-15-11-1 inside it."""

    def test_status_has_parked_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1102, "DQ-999 has parked."), "g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_presented_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1103, "DQ-999 has presented."), "g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_parked_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1104, "DQ-999 left parked."), "g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_presented_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1105, "DQ-999 left presented."), "g04")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_parked_bare_past_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1106, "DQ-999 parked yesterday."), "g05")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_presented_bare_past_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1107, "DQ-999 presented yesterday."), "g06")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1201, "DQ-999 has sealed."), "x04-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_been_parked_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1202, "DQ-999 has been parked."), "g14-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_resolved_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1203, "DQ-999 left resolved."), "w03-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_got_parked_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1204, "DQ-999 got parked."), "g06-r10-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch293GhostWordBetweenVerbFirstTest(unittest.TestCase):
    """CH-293: the ghost word between and verb first
    limb, S17-ATK11-7-02 with F-15-11-1's was still
    resolved member inside it."""

    def test_status_remains_fully_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1112, "DQ-999 remains fully resolved."), "g07")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stands_fully_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1113, "DQ-999 stands fully sealed."), "g08")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_already_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1114, "DQ-999 is already resolved."), "g09")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_already_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1115, "DQ-999 is already sealed."), "g10")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_was_still_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1116, "DQ-999 was still resolved."), "g11")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_now_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1117, "DQ-999 has now resolved."), "g12")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_parked_verb_first_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1118, "Parked DQ-999."), "g13")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_yet_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1119, "DQ-999 is yet resolved."), "own-g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_was_already_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1120, "DQ-999 was already resolved."), "own-g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_finally_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            1121, "DQ-999 has finally resolved."), "own-g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_still_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1211, "DQ-999 is still sealed."), "own-g06-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_resolved_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            1212, "DQ-999 is resolved."), "g08-r10-pin")
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


class Ch291EvidenceGotBarePastFullyVerbFirstNowTest(
        unittest.TestCase):
    """CH-291: the decision evidence got parked, bare
    past parked, stands fully resolved, remains fully
    sealed, verb first parked, and is now sealed limb,
    S17-ATK11-7-03 with F-15-11-2 inside it."""

    def test_evidence_got_parked_takes_claim_note(self):
        output = _run(_evidence_entry(
            1162, "DQ-1163 got parked.", 1163), "e01")
        self.assertEqual(1, len(_claims_about(output, 1163)))

    def test_evidence_parked_bare_past_takes_claim_note(self):
        output = _run(_evidence_entry(
            1164, "DQ-1165 parked yesterday.", 1165), "e02")
        self.assertEqual(1, len(_claims_about(output, 1165)))

    def test_evidence_stands_fully_resolved_takes_claim_note(self):
        output = _run(_evidence_entry(
            1166, "DQ-1167 stands fully resolved.", 1167), "e03")
        self.assertEqual(1, len(_claims_about(output, 1167)))

    def test_evidence_remains_fully_sealed_takes_claim_note(self):
        output = _run(_evidence_entry(
            1168, "DQ-1169 remains fully sealed.", 1169), "e04")
        self.assertEqual(1, len(_claims_about(output, 1169)))

    def test_evidence_parked_verb_first_takes_claim_note(self):
        output = _run(_evidence_entry(
            1170, "Parked DQ-1171.", 1171), "e05")
        self.assertEqual(1, len(_claims_about(output, 1171)))

    def test_evidence_is_now_sealed_takes_claim_note(self):
        output = _run(_evidence_entry(
            926, "DQ-927 is now sealed.", 927), "z03")
        self.assertEqual(1, len(_claims_about(output, 927)))

    def test_evidence_was_parked_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            1221, "DQ-1222 was parked.", 1222), "e06-pin")
        self.assertEqual(1, len(_claims_about(output, 1222)))

    def test_evidence_has_resolved_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            1223, "DQ-1224 has resolved.", 1224), "own-e02-pin")
        self.assertEqual(1, len(_claims_about(output, 1224)))

    def test_evidence_remains_fully_resolved_still_takes_note_pin(
            self):
        output = _run(_evidence_entry(
            1225, "DQ-1226 remains fully resolved.", 1226),
            "z04-pin")
        self.assertEqual(1, len(_claims_about(output, 1226)))


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


class Ch292ClosingProseNounClosureWordTest(unittest.TestCase):
    """CH-292: the closing prose noun and closure word
    limb, S17-ATK11-7-05, named crossings only."""

    def test_decision_noun_beside_finished_derives_ambiguous(self):
        output = _run(_prose_file(
            1182, "The decision was recorded in full and this "
                  "entry is now finished."), "p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1182"))

    def test_ruling_noun_beside_concluded_derives_ambiguous(self):
        output = _run(_prose_file(
            1183, "The ruling was recorded in full and this "
                  "entry is now concluded."), "p02")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1183"))

    def test_verdict_noun_beside_complete_derives_ambiguous(self):
        output = _run(_prose_file(
            1184, "The verdict was recorded in full and this "
                  "entry is now complete."), "p03")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1184"))

    def test_decided_verb_beside_done_derives_ambiguous(self):
        output = _run(_prose_file(
            1185, "The question was decided in full and this "
                  "entry is now done."), "p04")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1185"))

    def test_resolved_verb_beside_ended_derives_ambiguous(self):
        output = _run(_prose_file(
            1186, "The question was resolved in full and this "
                  "entry is now ended."), "p05")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1186"))

    def test_settlement_noun_beside_done_derives_ambiguous(self):
        output = _run(_prose_file(
            1187, "The settlement was recorded in full and this "
                  "entry is now done."), "p06")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1187"))

    def test_decided_verb_beside_over_derives_ambiguous(self):
        output = _run(_prose_file(
            1232, "The question was decided in full and this "
                  "entry is now over."), "own-p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1232"))

    def test_ruling_noun_beside_closed_still_ambiguous_pin(self):
        output = _run(_prose_file(
            1233, "The ruling was recorded in full and this "
                  "entry is now closed."), "p07-pin")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1233"))

    def test_decided_verb_beside_finished_still_ambiguous_pin(self):
        output = _run(_prose_file(
            1234, "The question was decided in full and this "
                  "entry is now finished."), "own-p02-pin")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-1234"))

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


class Ch294ClaimCrossEntryFormsTest(unittest.TestCase):
    """CH-294: the cross entry claim got, has, and bare
    past parked and presented forms and the stands
    fully, stays fully, remains fully sealed, is
    already, was still, and is already sealed forms,
    S17-ATK11-7-04 with F-15-11-3 inside it."""

    def test_claim_got_parked_takes_note(self):
        output = _run(_claim_file(
            1132, "DQ-1133 got parked.", 1133), "c01")
        self.assertEqual(1, len(_claims_about(output, 1133)))

    def test_claim_got_presented_takes_note(self):
        output = _run(_claim_file(
            1134, "DQ-1135 got presented.", 1135), "c02")
        self.assertEqual(1, len(_claims_about(output, 1135)))

    def test_claim_has_parked_takes_note(self):
        output = _run(_claim_file(
            1136, "DQ-1137 has parked.", 1137), "c03")
        self.assertEqual(1, len(_claims_about(output, 1137)))

    def test_claim_has_presented_takes_note(self):
        output = _run(_claim_file(
            1138, "DQ-1139 has presented.", 1139), "c04")
        self.assertEqual(1, len(_claims_about(output, 1139)))

    def test_claim_parked_bare_past_takes_note(self):
        output = _run(_claim_file(
            1140, "DQ-1141 parked yesterday.", 1141), "c05")
        self.assertEqual(1, len(_claims_about(output, 1141)))

    def test_claim_presented_bare_past_takes_note(self):
        output = _run(_claim_file(
            1142, "DQ-1143 presented yesterday.", 1143), "c06")
        self.assertEqual(1, len(_claims_about(output, 1143)))

    def test_claim_stands_fully_resolved_takes_note(self):
        output = _run(_claim_file(
            1144, "DQ-1145 stands fully resolved.", 1145), "c07")
        self.assertEqual(1, len(_claims_about(output, 1145)))

    def test_claim_stays_fully_resolved_takes_note(self):
        output = _run(_claim_file(
            1146, "DQ-1147 stays fully resolved.", 1147), "c08")
        self.assertEqual(1, len(_claims_about(output, 1147)))

    def test_claim_remains_fully_sealed_takes_note(self):
        output = _run(_claim_file(
            1148, "DQ-1149 remains fully sealed.", 1149), "c09")
        self.assertEqual(1, len(_claims_about(output, 1149)))

    def test_claim_is_already_resolved_takes_note(self):
        output = _run(_claim_file(
            1150, "DQ-1151 is already resolved.", 1151), "c10")
        self.assertEqual(1, len(_claims_about(output, 1151)))

    def test_claim_was_still_resolved_takes_note(self):
        output = _run(_claim_file(
            1152, "DQ-1153 was still resolved.", 1153), "c11")
        self.assertEqual(1, len(_claims_about(output, 1153)))

    def test_claim_was_still_sealed_takes_note(self):
        output = _run(_claim_file(
            1222, "DQ-1223 was still sealed.", 1223), "own-c01")
        self.assertEqual(1, len(_claims_about(output, 1223)))

    def test_claim_is_already_sealed_takes_note(self):
        output = _run(_claim_file(
            1224, "DQ-1225 is already sealed.", 1225), "own-c02")
        self.assertEqual(1, len(_claims_about(output, 1225)))

    def test_claim_is_now_sealed_takes_note(self):
        output = _run(_claim_file(
            940, "DQ-941 is now sealed.", 941), "y05")
        self.assertEqual(1, len(_claims_about(output, 941)))

    def test_claim_has_been_parked_still_takes_note_pin(self):
        output = _run(_claim_file(
            1241, "DQ-1242 has been parked.", 1242), "c12-pin")
        self.assertEqual(1, len(_claims_about(output, 1242)))

    def test_claim_remains_fully_resolved_still_takes_note_pin(
            self):
        output = _run(_claim_file(
            1243, "DQ-1244 remains fully resolved.", 1244),
            "y06-pin")
        self.assertEqual(1, len(_claims_about(output, 1244)))

    def test_claim_left_parked_still_takes_note_pin(self):
        output = _run(_claim_file(
            932, "DQ-933 left parked.", 933), "w04-pin")
        self.assertEqual(1, len(_claims_about(output, 933)))


if __name__ == "__main__":
    unittest.main()
