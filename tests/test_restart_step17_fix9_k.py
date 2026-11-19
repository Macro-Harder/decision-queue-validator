"""Step 17 (restart) fix wave 9, Fix Seat K tests, test first.

Charge CH-224, Cluster K, the R form width identity, on
the validate surface, in one sitting: finding T9-24
(seat 6 finding 2, Low), consolidated in
design/steps/step-17r-r9-triage-prep.md at its Cluster K
and ruled TO FIX at section 81 ruling (a) of
design/steps/step-17r-record.md. Section 81 ruling (a)
numbers the charges consecutively from CH-191 in
cluster order per the preparation's proposed charge
split as filed, one charge per distinct finding:
Cluster A carries CH-191 and CH-192, Cluster B CH-193
to CH-196, Cluster C CH-197, Cluster D CH-198,
Cluster E CH-199 to CH-205, Cluster F CH-206 to
CH-212, Cluster G CH-213 and CH-214, Cluster H CH-215
to CH-218, Cluster I CH-219 to CH-221, Cluster J
CH-222 and CH-223, and Cluster K CH-224 (T9-24).
Register item 17R-415 states the range CH-191 to
CH-225.

CH-224 (validate, the blocks value identity reading,
the CH-148 cure family): seat 6 finding 2 at
design/steps/step-17r-attack9-6.md. The CH-148 cure
text confines its digit width identity to values in
the DQ form, DQ- followed by digits in any width, so
two blocks values naming the one standing R entry in
different widths (Blocks: R-007 beside Blocks: R-7,
case w08c) still take the one check 9 contradictory
values Warning at exit 1, on the difference of the
strings alone, where the R form is a whole entry
identifier form the product itself reads: R headings
stand as entries (verify/r1/c08a takes its duplicate
Error on two R-7 copies) and duplicate detection by
number holds across R widths on headings
(verify/r3/g08, R-07 beside R-7, counts one headed R
entry with no duplicate Error).

Cure bound, stated expressly: at the blocks field
value comparison, two values that are each a single
entry identifier in the R form, R- followed by digits
in any width, naming the one entry number state no
contradiction, exactly as the DQ form stands under
CH-148. The identity is per identifier form: a DQ
value and an R value naming the same digits name two
different entries and still contradict. Every other
comparison stands as CH-59 and CH-148 stand, exact
strings: two R values naming two different numbers
contradict in any widths, and the forms the round 8
seat 6 observation 3 records as the CH-148 bound (the
lowercase identifier, the trailing stop, and the list
value against the single) stand outside this cure in
their R dresses as in their DQ dresses.

Constructions stand in the attack paper's own shape:
case w08c (DQ-001 Open carrying Blocks: R-007 then
Blocks: R-7, with the standing R-7 entry in its
recognised heading form beside it, Headed entries 2,
Waiting 2 and Blocking 2), with the DQ width twins of
the CH-148 verification set standing cured as pins
and the R heading duplicate readings (verify/r1/c08a
and verify/r3/g08) stated in this file's pins at the
unit level of the comparison itself.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h

validate = h.import_module("validate")

HEAD = "# Decision queue\n\n"


def r_queue(blocks_paragraphs):
    """The seat 6 w08c base: DQ-001 Open carrying the
    blocks paragraphs under test, beside the standing
    R-7 entry in its recognised heading form."""
    parts = [HEAD,
             "### DQ-001: Alpha question\n\n",
             "Status: Open\n\n",
             "Question: Which option should we take?\n\n",
             "Options: Option A, Option B\n\n",
             "Cost of deciding late: Work stays blocked.\n\n"]
    for paragraph in blocks_paragraphs:
        parts.append(paragraph + "\n\n")
    parts.extend([
        "This entry is waiting for a decision.\n\n",
        "### R-7 closure conflict\n\n",
        "Status: Open\n\n",
        "Question: Which option should we take?\n\n",
        "Options: Option A, Option B\n\n",
        "Cost of deciding late: Work stays blocked.\n\n",
        "Blocks: DQ-001\n\n",
        "This entry is waiting for a decision.\n",
    ])
    return "".join(parts).encode("utf-8")


def dq_queue(blocks_paragraphs):
    """The CH-148 base: DQ-001 Open carrying the blocks
    paragraphs under test, DQ-002 Open complete."""
    parts = [HEAD,
             "### DQ-001: Alpha question\n\n",
             "Status: Open\n\n",
             "Question: Which option should we take?\n\n",
             "Options: Option A, Option B\n\n",
             "Cost of deciding late: Work stays blocked.\n\n"]
    for paragraph in blocks_paragraphs:
        parts.append(paragraph + "\n\n")
    parts.extend([
        "This entry is waiting for a decision.\n\n",
        "### DQ-002: Beta question\n\n",
        "Status: Open\n\n",
        "Question: Which other option should we take?\n\n",
        "Options: Option C, Option D\n\n",
        "Cost of deciding late: Work stays blocked.\n\n",
        "Blocks: DQ-001\n\n",
        "This second entry is waiting for a decision.\n",
    ])
    return "".join(parts).encode("utf-8")


def run(data, name="fix9_k.md"):
    model, output = h.run_pipeline(data, name)
    if output is None or h.is_failure_result(model):
        raise AssertionError("pipeline returned a failure")
    return output


def cli_codes(data):
    path = h.temp_input(data)
    codes = []
    for subcommand in ("validate", "render"):
        code, _out, _err = h.run_cli(subcommand, path)
        codes.append(code)
    return codes


def statements(output, entry_id="DQ-001"):
    return [h.finding_statement(f) or ""
            for f in h.findings_for(output, entry_id=entry_id)]


def conflict_statements(output):
    return [s for s in statements(output)
            if "contradictory values" in s]


# ---------------------------------------------------------------------
# CH-224: the R form width identity at the blocks field
# value comparison
# ---------------------------------------------------------------------

class Ch224RWidthIdentityTest(unittest.TestCase):
    """CH-224, seat 6 finding 2 (T9-24): two blocks
    values naming the one R entry in different digit
    widths state no contradiction."""

    def test_r_width_pair_no_conflict(self):
        # Case w08c: Blocks R-007 then Blocks R-7, with
        # the standing R-7 entry beside the host.
        data = r_queue(["Blocks: R-007", "Blocks: R-7"])
        output = run(data, "fix9_k_w08c.md")
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(h.findings_of(output), [])
        waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(waiting), 2)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_codes(data), [0, 0])

    def test_r_width_pair_reversed_no_conflict(self):
        data = r_queue(["Blocks: R-7", "Blocks: R-007"])
        output = run(data, "fix9_k_w08c_rev.md")
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(h.findings_of(output), [])
        self.assertEqual(cli_codes(data), [0, 0])

    def test_r_width_alias_pair_no_conflict(self):
        # Across the Blocks and What it blocks alias
        # pair, as the CH-148 u04 form stands for DQ.
        data = r_queue(
            ["Blocks: R-007", "What it blocks: R-7"])
        output = run(data, "fix9_k_alias.md")
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(cli_codes(data), [0, 0])

    def test_r_width_forms_same_number_no_conflict(self):
        # The identity at further widths of the one
        # number 7: one digit, two digit, three digit,
        # and four digit forms against each other.
        for first, second in (("R-007", "R-7"),
                              ("R-07", "R-007"),
                              ("R-007", "R-0007")):
            with self.subTest(first=first, second=second):
                data = r_queue(
                    ["Blocks: " + first, "Blocks: " + second])
                output = run(data, "fix9_k_widths.md")
                self.assertEqual(conflict_statements(output), [])
                self.assertEqual(cli_codes(data), [0, 0])

    def test_r_width_pair_then_genuine_value_conflicts_on_it(self):
        # The width pair states one value; a third value
        # that names no entry contradicts that one
        # value, and the finding names the third value
        # against the governing first value, not the
        # width twin.
        data = r_queue(
            ["Blocks: R-007", "Blocks: R-7", "Blocks: none"])
        output = run(data, "fix9_k_width_third.md")
        conflicts = conflict_statements(output)
        self.assertEqual(len(conflicts), 1)
        self.assertIn('"none"', conflicts[0])
        self.assertIn("stands as \"R-007\"", conflicts[0])
        self.assertEqual(cli_codes(data), [1, 1])

    def test_r_width_identity_at_the_comparison(self):
        # The comparison itself: the R width twins state
        # no contradiction in either order, at the one
        # helper the check 9 reading runs.
        self.assertFalse(validate._field_values_contradict(
            "blocks", "R-007", "R-7"))
        self.assertFalse(validate._field_values_contradict(
            "blocks", "R-7", "R-007"))
        self.assertFalse(validate._field_values_contradict(
            "blocks", "R-0007", "R-07"))


class Ch224PinsTest(unittest.TestCase):
    """CH-224 pins, passing before and after: the CH-59
    and CH-148 readings stand whole outside the charged
    R width forms, and the observation 3 bound forms
    keep their standings in their R dresses."""

    def test_dq_width_pair_no_conflict(self):
        # The CH-148 cured form (case t65) stands as a
        # pin: Blocks DQ-002 beside Blocks DQ-02 passes
        # in silence.
        data = dq_queue(["Blocks: DQ-002", "Blocks: DQ-02"])
        output = run(data, "fix9_k_t65.md")
        self.assertEqual(conflict_statements(output), [])
        _waiting, blocking = h.waiting_and_blocking(output)
        self.assertEqual(int(blocking), 2)
        self.assertEqual(cli_codes(data), [0, 0])

    def test_identical_r_pair_no_conflict(self):
        data = r_queue(["Blocks: R-7", "Blocks: R-7"])
        output = run(data, "fix9_k_identical.md")
        self.assertEqual(conflict_statements(output), [])
        self.assertEqual(cli_codes(data), [0, 0])

    def test_different_r_numbers_still_conflict(self):
        # Two different R numbers contradict in any
        # widths: R-007 names entry 7, R-8 names entry 8.
        data = r_queue(["Blocks: R-007", "Blocks: R-8"])
        output = run(data, "fix9_k_diff_r.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_cross_form_same_digits_still_conflict(self):
        # The identity is per identifier form: a DQ
        # value and an R value naming the same digits
        # name two different entries and contradict, in
        # either order.
        for first, second in (("DQ-007", "R-7"),
                              ("R-007", "DQ-7")):
            with self.subTest(first=first, second=second):
                data = r_queue(
                    ["Blocks: " + first, "Blocks: " + second])
                output = run(data, "fix9_k_cross.md")
                self.assertEqual(
                    len(conflict_statements(output)), 1)
                self.assertEqual(cli_codes(data), [1, 1])

    def test_lowercase_r_form_still_conflicts(self):
        # Observation 3 bound, the lowercase identifier:
        # r-007 beside R-7 takes its Warning as before.
        data = r_queue(["Blocks: r-007", "Blocks: R-7"])
        output = run(data, "fix9_k_lower.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_trailing_stop_r_form_still_conflicts(self):
        # Observation 3 bound, the trailing stop: R-7.
        # beside R-007 takes its Warning as before.
        data = r_queue(["Blocks: R-7.", "Blocks: R-007"])
        output = run(data, "fix9_k_stop.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_list_value_vs_single_still_conflicts(self):
        # Observation 3 bound, the list value against
        # the single: the list form stands outside the
        # identity in its R dress as in its DQ dress.
        data = r_queue(
            ["Blocks: R-007, R-7", "Blocks: R-007"])
        output = run(data, "fix9_k_list.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_genuine_r_conflict_still_fires(self):
        # The CH-59 charged form stands on the R host
        # pair: R-007 beside none takes its one Warning.
        data = r_queue(["Blocks: R-007", "Blocks: none"])
        output = run(data, "fix9_k_genuine.md")
        self.assertEqual(len(conflict_statements(output)), 1)
        self.assertEqual(cli_codes(data), [1, 1])

    def test_comparison_pins(self):
        # The comparison's standing forms, at the helper
        # itself: the DQ identity of CH-148 whole, the
        # different number pairs contradicting, and the
        # cross form pair contradicting.
        self.assertFalse(validate._field_values_contradict(
            "blocks", "DQ-002", "DQ-02"))
        self.assertTrue(validate._field_values_contradict(
            "blocks", "DQ-02", "DQ-003"))
        self.assertTrue(validate._field_values_contradict(
            "blocks", "R-007", "R-8"))
        self.assertTrue(validate._field_values_contradict(
            "blocks", "DQ-007", "R-7"))
        self.assertTrue(validate._field_values_contradict(
            "blocks", "R-007", "DQ-7"))
        self.assertFalse(validate._field_values_contradict(
            "blocks", "R-7", "R-7"))


if __name__ == "__main__":
    unittest.main()
