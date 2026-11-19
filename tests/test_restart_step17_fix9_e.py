"""Restart Step 17 fix wave 9, Fix Seat E tests.

Charges CH-199 to CH-205, ruled at section 81 of
design/steps/step-17r-record.md under ruling (a), on the
round 9 triage preparation paper
design/steps/step-17r-r9-triage-prep.md, Cluster E, and
on the round 9 attack seat 7 paper,
design/steps/step-17r-attack9-7.md.

CH-199 (validate, the ghost resolved family limb):
finding S17-ATK9-7-01 (T9-03), a ghost number named on
the entry own Status line in the is resolved, stands
resolved, remains resolved, has been resolved, or got
resolved form is read by no scan.

CH-200 (validate, the ghost was parked and was
presented limb): finding S17-ATK9-7-02 (T9-04), a ghost
number named on the entry own Status line in the was
parked or was presented form is read by no scan.

CH-201 (validate, the ghost has sealed and bare past
sealed limb): finding S17-ATK9-7-03 (T9-05), a ghost
number named on the entry own Status line in the has
sealed or bare past sealed form is read by no scan.

CH-202 (validate, the ghost left sealed limb): finding
S17-ATK9-7-04 (T9-06), a ghost number named on the
entry own Status line in the left sealed form is read
by no scan.

CH-203 (validate, the evidence resolved forms limb):
finding S17-ATK9-7-05 (T9-07), decision evidence naming
a headed entry with the remains resolved or was
resolved form takes no claim Note.

CH-204 (validate, the closing prose resolved and
sealed verb beside shut and sealed limb): finding
S17-ATK9-7-06 (T9-08), closing prose stating the
standing contradiction with a resolved verb beside
shut, a sealed verb beside shut, or a resolved verb
beside sealed still derives Open as the determining
element. The two K7 bound guards (the decision noun
beside sealed, the verdict noun beside shut) stand
pinned deriving Open in both directions, fenced in
neither direction.

CH-205 (validate, the cross entry claim resolved
beyond the is form limb): finding S17-ATK9-7-07
(T9-25), cross entry state claims in the remains
resolved, is still resolved, was resolved, has been
resolved, bare past resolved, or stands resolved form
take no claim Note.

Constructions are the finding paper own constructions,
rebuilt inline from the attack scratch files in
attack9-7-scratch/cases. Governing pins stand as
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


class Ch199GhostResolvedFamilyTest(unittest.TestCase):
    """CH-199: the ghost resolved family limb,
    S17-ATK9-7-01."""

    def test_status_is_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            902, "DQ-999 is resolved."), "g01")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_stands_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            907, "DQ-999 stands resolved."), "g06")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_remains_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            908, "DQ-999 remains resolved."), "g07")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_been_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            909, "DQ-999 has been resolved."), "g08")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_got_resolved_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            910, "DQ-999 got resolved."), "g09")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_is_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            912, "DQ-999 is sealed."), "g11-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_been_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            913, "DQ-999 has been sealed."), "g12-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch200GhostWasParkedPresentedTest(unittest.TestCase):
    """CH-200: the ghost was parked and was presented
    limb, S17-ATK9-7-02."""

    def test_status_was_parked_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            903, "DQ-999 was parked."), "g02")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_was_presented_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            904, "DQ-999 was presented."), "g03")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_was_sealed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            914, "DQ-999 was sealed."), "g02-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch201GhostHasSealedBarePastSealedTest(unittest.TestCase):
    """CH-201: the ghost has sealed and bare past
    sealed limb, S17-ATK9-7-03."""

    def test_status_has_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            905, "DQ-999 has sealed."), "g04")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_sealed_bare_past_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            906, "DQ-999 sealed yesterday."), "g05")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_has_settled_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            915, "DQ-999 has settled."), "g04-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_settled_bare_past_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            916, "DQ-999 settled yesterday."), "g05-pin")
        self.assertEqual(1, len(_pd_r7(output, 999)))


class Ch202GhostLeftSealedTest(unittest.TestCase):
    """CH-202: the ghost left sealed limb,
    S17-ATK9-7-04."""

    def test_status_left_sealed_takes_ghost_note(self):
        output = _run(_ghost_status_entry(
            911, "DQ-999 left sealed."), "g10")
        self.assertEqual(1, len(_pd_r7(output, 999)))

    def test_status_left_closed_still_takes_note_pin(self):
        output = _run(_ghost_status_entry(
            917, "DQ-999 left closed."), "g10-pin")
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


class Ch203EvidenceResolvedFormsTest(unittest.TestCase):
    """CH-203: the evidence resolved forms limb,
    S17-ATK9-7-05."""

    def test_evidence_remains_resolved_takes_claim_note(self):
        output = _run(_evidence_entry(
            922, "DQ-923 remains resolved.", 923), "e01")
        self.assertEqual(1, len(_claims_about(output, 923)))

    def test_evidence_was_resolved_takes_claim_note(self):
        output = _run(_evidence_entry(
            924, "DQ-925 was resolved.", 925), "e02")
        self.assertEqual(1, len(_claims_about(output, 925)))

    def test_evidence_is_resolved_still_takes_note_pin(self):
        output = _run(_evidence_entry(
            926, "DQ-927 is resolved.", 927), "e03-pin")
        self.assertEqual(1, len(_claims_about(output, 927)))


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


class Ch204ClosingProseResolvedSealedShutTest(unittest.TestCase):
    """CH-204: the closing prose resolved and sealed
    verb beside shut and sealed limb, S17-ATK9-7-06,
    named crossings only."""

    def test_resolved_verb_beside_shut_derives_ambiguous(self):
        output = _run(_prose_file(
            952, "The question was resolved in full and this "
                 "entry is now shut."), "p01")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-952"))

    def test_sealed_verb_beside_shut_derives_ambiguous(self):
        output = _run(_prose_file(
            953, "This entry was sealed in full and is now "
                 "shut."), "p02")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-953"))

    def test_resolved_verb_beside_sealed_derives_ambiguous(self):
        output = _run(_prose_file(
            954, "The question was resolved in full and this "
                 "entry is now sealed."), "p03")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-954"))

    def test_resolved_verb_beside_closed_still_ambiguous_pin(self):
        output = _run(_prose_file(
            955, "The question was resolved in full and this "
                 "entry is now closed."), "p04-pin")
        self.assertEqual("Ambiguous", _state_of(output, "DQ-955"))

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


class Ch205ClaimResolvedBeyondIsTest(unittest.TestCase):
    """CH-205: the cross entry claim resolved beyond
    the is form limb, S17-ATK9-7-07."""

    def test_claim_remains_resolved_takes_note(self):
        output = _run(_claim_file(
            932, "DQ-933 remains resolved.", 933), "c01")
        self.assertEqual(1, len(_claims_about(output, 933)))

    def test_claim_is_still_resolved_takes_note(self):
        output = _run(_claim_file(
            934, "DQ-935 is still resolved.", 935), "c02")
        self.assertEqual(1, len(_claims_about(output, 935)))

    def test_claim_was_resolved_takes_note(self):
        output = _run(_claim_file(
            936, "DQ-937 was resolved.", 937), "c03")
        self.assertEqual(1, len(_claims_about(output, 937)))

    def test_claim_has_been_resolved_takes_note(self):
        output = _run(_claim_file(
            938, "DQ-939 has been resolved.", 939), "c04")
        self.assertEqual(1, len(_claims_about(output, 939)))

    def test_claim_resolved_bare_past_takes_note(self):
        output = _run(_claim_file(
            940, "DQ-941 resolved yesterday.", 941), "c05")
        self.assertEqual(1, len(_claims_about(output, 941)))

    def test_claim_stands_resolved_takes_note(self):
        output = _run(_claim_file(
            942, "DQ-943 stands resolved.", 943), "c06")
        self.assertEqual(1, len(_claims_about(output, 943)))

    def test_claim_is_resolved_still_takes_note_pin(self):
        output = _run(_claim_file(
            944, "DQ-945 is resolved.", 945), "c07-pin")
        self.assertEqual(1, len(_claims_about(output, 945)))


if __name__ == "__main__":
    unittest.main()
