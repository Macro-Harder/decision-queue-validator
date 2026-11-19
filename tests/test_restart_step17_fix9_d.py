"""Step 17 fix wave 9, Fix Seat D tests.

Charge CH-198, as numbered consecutively from CH-191 in
cluster order per the proposed charge split as filed in
design/steps/step-17r-r9-triage-prep.md and ruled at
section 81 ruling (a) of design/steps/step-17r-record.md:
Cluster A carries CH-191 and CH-192 (T9-01 and T9-02),
Cluster B carries CH-193 to CH-196 (T9-14, T9-15, T9-16,
and T9-35), Cluster C carries CH-197 (T9-12), and Cluster
D carries CH-198 (T9-13). Cluster D is seat 10 finding
A9-10-F2, Medium, consolidated as T9-13 in the round 9
triage preparation, sourced at
design/steps/step-17r-attack9-10.md, with seat 12
observation O-9-12-5's M25 form (the rest is in limbo)
standing as the limbo member of the same construction,
counted once inside it. The cure stands in
product/decision_queue_validator/validate.py only, at
the charged locus: the remainder reading, the CH-163
cure family (_REMAINDER_PATTERNS, the CH-147 locus
standing on CH-106 and CH-87).

CH-198 (T9-13, A9-10-F2, Medium): a remainder named with
the verbs is awaiting a ruling, waits for a ruling, has
not been settled, is not settled, is in limbo, stands
adjourned, is held over, is carried over, awaits a
verdict, is suspended, or stands suspended is not read,
in the statement or in its own paragraph. Hand truth
under PIN-01 and PIN-03: every entry in the
constructions names its remainder in words, so Settled
in part for each; the statement construction of the
attack paper stands at Settled in part 22, Ambiguous
reporting count 0, Waiting 22 entries, and its own
paragraph construction at Settled in part 6, Ambiguous
reporting count 0, Waiting 6 entries. The ten read forms
at seat 10 observation O7 stand as pins, passing before
and after. The balance subject forms at seat 10
observation O5 stand outside the charge and keep their
standing, as in the CH-163 paper.

No construction in this file builds the F1 shape, and
no banked question is named in any construction.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def taught_entry(number, title, ruling_paragraphs):
    text = (
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
        "A plain context paragraph.\n" % (number, title))
    for paragraph in ruling_paragraphs:
        text += "\n" + paragraph + "\n"
    return text


def statement_paragraph(sentence):
    return ("Ruled by Captain JP: the first part is ruled, "
            "take Option A. " + sentence)


def state_of(output, entry_id):
    found = h.entry_by_id(output, entry_id)
    if found is None:
        raise AssertionError("no entry %s in the output" % entry_id)
    return h.entry_state(found)


class Ch198RemainderRound9Test(unittest.TestCase):
    """CH-198, A9-10-F2: part scope remainder verb widths,
    round 9 limbs, in the statement and in the own
    paragraph shapes alike."""

    STATEMENT_FORMS = (
        (2, "Awaiting a ruling",
         "The rest is awaiting a ruling."),
        (3, "Waits for a ruling",
         "The remainder waits for a ruling."),
        (10, "Has not been settled",
         "The rest has not been settled."),
        (11, "Is not settled",
         "The remainder is not settled."),
        (12, "Is in limbo",
         "The rest is in limbo."),
        (13, "Stands adjourned",
         "The remainder stands adjourned."),
        (14, "Is held over",
         "The rest is held over."),
        (15, "Is carried over",
         "The remainder is carried over."),
        (17, "Awaits a verdict",
         "The remainder awaits a verdict."),
        (19, "Is suspended",
         "The remainder is suspended."),
        (20, "Stands suspended",
         "The rest stands suspended."),
    )

    VERBS = (
        "is awaiting a ruling",
        "waits for a ruling",
        "has not been settled",
        "is not settled",
        "is in limbo",
        "stands adjourned",
        "is held over",
        "is carried over",
        "awaits a verdict",
        "is suspended",
        "stands suspended",
    )

    O7_FORMS = (
        (4, "Still pending",
         "The rest is still pending."),
        (5, "Remains pending",
         "The remainder remains pending."),
        (6, "Stands pending",
         "The rest stands pending."),
        (7, "Has yet to be decided",
         "The remainder has yet to be decided."),
        (8, "Is yet to be decided",
         "The rest is yet to be decided."),
        (9, "Remains to be decided",
         "The remainder remains to be decided."),
        (16, "Remains outstanding",
         "The rest remains outstanding."),
        (18, "Is pending a ruling",
         "The rest is pending a ruling."),
        (21, "Remains undecided",
         "The remainder remains undecided."),
        (22, "Stands undecided",
         "The rest stands undecided."),
    )

    def test_statement_forms_derive_settled_in_part(self):
        for number, title, sentence in self.STATEMENT_FORMS:
            with self.subTest(title=title):
                text = ("# Decision queue\n\n" + taught_entry(
                    number, title,
                    [statement_paragraph(sentence)]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                entry_id = "DQ-%03d" % number
                self.assertEqual(state_of(output, entry_id),
                                 "Settled in part")
                found = h.entry_by_id(output, entry_id)
                remainder = h.get(found, "remainder_text",
                                  "remainder")
                self.assertTrue(remainder)

    def test_statement_combined_figures(self):
        # The attack paper's case r9-verbs-statement at its
        # 22 entries: the control, the ten O7 read forms,
        # and the eleven charged forms.
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control stands open",
            [statement_paragraph(
                "The rest, the second part, stands open.")]))
        for number, title, sentence in (
                self.STATEMENT_FORMS + self.O7_FORMS):
            parts.append(taught_entry(
                number, title, [statement_paragraph(sentence)]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 22)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 22)

    def test_all_subject_and_naming_variants_derive(self):
        for verb in self.VERBS:
            for sentence in (
                    "The remainder, the second part, %s." % verb,
                    "The rest %s." % verb):
                with self.subTest(sentence=sentence):
                    text = ("# Decision queue\n\n"
                            + taught_entry(
                                1, "Variant form",
                                [statement_paragraph(sentence)]))
                    _model, output = h.run_pipeline(
                        text.encode("utf-8"))
                    self.assertIsNotNone(output)
                    self.assertEqual(
                        state_of(output, "DQ-001"),
                        "Settled in part")

    def test_own_paragraph_forms_derive_settled_in_part(self):
        # The two failing forms of the attack paper's case
        # r9-verbs-nextpara, each in its own paragraph.
        forms = (
            (2, "Awaiting a ruling para",
             "The rest is awaiting a ruling."),
            (4, "Is in limbo para",
             "The rest is in limbo."),
        )
        for number, title, remainder_line in forms:
            with self.subTest(title=title):
                text = ("# Decision queue\n\n" + taught_entry(
                    number, title,
                    ["Ruled by Captain JP: the first part is "
                     "ruled, take Option A.",
                     remainder_line]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                entry_id = "DQ-%03d" % number
                self.assertEqual(state_of(output, entry_id),
                                 "Settled in part")

    def test_own_paragraph_combined_figures(self):
        # The attack paper's case r9-verbs-nextpara at its
        # six entries: the control, the two charged forms,
        # and the three O7 read forms of that file.
        parts = ["# Decision queue\n\n"]
        parts.append(taught_entry(
            1, "Control stands open",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The remainder, the second part, still stands "
             "open."]))
        forms = (
            (2, "Awaiting a ruling para",
             "The rest is awaiting a ruling."),
            (3, "Has yet to be decided para",
             "The remainder has yet to be decided."),
            (4, "Is in limbo para",
             "The rest is in limbo."),
            (5, "Remains undecided para",
             "The remainder remains undecided."),
            (6, "Is pending a ruling para",
             "The rest is pending a ruling."),
        )
        for number, title, remainder_line in forms:
            parts.append(taught_entry(
                number, title,
                ["Ruled by Captain JP: the first part is "
                 "ruled, take Option A.",
                 remainder_line]))
        text = "\n".join(parts)
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        counts = h.canonical_counts(output)
        self.assertEqual(counts.get("Settled in part"), 6)
        self.assertEqual(h.ambiguous_count(output), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 6)

    def test_o7_read_forms_still_derive(self):
        # Pin, passing before and after: the ten read forms
        # at seat 10 observation O7 of the round 9 paper.
        for number, title, sentence in self.O7_FORMS:
            with self.subTest(title=title):
                text = ("# Decision queue\n\n" + taught_entry(
                    number, title,
                    [statement_paragraph(sentence)]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertEqual(
                    state_of(output, "DQ-%03d" % number),
                    "Settled in part")

    def test_ch163_and_earlier_cured_forms_still_derive(self):
        # Pin, passing before and after: the CH-163,
        # CH-147, CH-106, and CH-87 cured forms whole, in
        # the statement and own paragraph shapes.
        forms = (
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest is waiting for a "
             "decision."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder waits for a "
             "decision."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest has not been ruled."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder is adjourned."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest awaits a ruling."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder awaits a decision."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The rest stays unresolved."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A. The remainder is in abeyance."],
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A.",
             "The rest is tabled."],
        )
        for paragraphs in forms:
            with self.subTest(paragraphs=paragraphs):
                text = ("# Decision queue\n\n" + taught_entry(
                    1, "Cured form", paragraphs))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertEqual(state_of(output, "DQ-001"),
                                 "Settled in part")

    def test_pin03_part_act_with_no_remainder_is_ambiguous(self):
        # PIN-03 pin, passing before and after.
        text = ("# Decision queue\n\n" + taught_entry(
            1, "Part no remainder",
            ["Ruled by Captain JP: the first part is ruled, "
             "take Option A."]))
        _model, output = h.run_pipeline(text.encode("utf-8"))
        self.assertIsNotNone(output)
        self.assertEqual(state_of(output, "DQ-001"), "Ambiguous")
        self.assertEqual(h.ambiguous_count(output), 1)

    def test_balance_subject_stands_outside_the_charge(self):
        # Observation O5 of the round 9 attack paper (the
        # round 8 paper's observation O6 form), passing
        # before and after: no governing text names a
        # third subject, and the balance forms keep their
        # standing.
        for paragraph in (
                "Ruled by Captain JP: the first part is "
                "ruled, take Option A. The balance, the "
                "second part, stands open.",
                "Ruled by Captain JP: the first part is "
                "ruled, take Option A. The balance stands "
                "open."):
            with self.subTest(paragraph=paragraph):
                text = ("# Decision queue\n\n" + taught_entry(
                    1, "Balance subject", [paragraph]))
                _model, output = h.run_pipeline(
                    text.encode("utf-8"))
                self.assertIsNotNone(output)
                self.assertEqual(state_of(output, "DQ-001"),
                                 "Ambiguous")


if __name__ == "__main__":
    unittest.main()
