"""Step 17 fix wave 12, Fix Seat C tests.

Charges CH-327, CH-328, and CH-329, Cluster C (the
blocking figure), 3 TO FIX, all Medium, distinct
findings T12-13, T12-14, and T12-15, as proposed in
design/steps/step-17r-r12-triage-prep.md at section 2.3
and Cluster C of section 3: CH-327 the phrase limb,
CH-328 the joiner limb, and CH-329 the wrapper limb,
sourced at round 12 attack seat 09 finding A12-09-F1
and round 12 attack seat 11 findings F-12-11-1,
F-12-11-2, and F-12-11-3. The cure stands in
product/decision_queue_validator/validate.py only, at
the charged locus: the Blocks value reading as cured
at CH-287 to CH-289.

CH-327 (T12-13, Medium), the phrase limb: the blocking
figure counts blocks fields that name no item, in the
9 fresh phrase forms of seat 09 and the 18 probes P01
to P18 of seat 11, shared members counted once (the
blocks no delays, impedes no ruling, hinders no
ruling, and obstructs no ruling forms standing in both
papers), each at Blocking 1 against a hand truth of 0
under OP-Q12 as corrected, with the seat 09 scale case
b12-combined at Blocking 4 against a hand truth of 1,
the seat 11 combined file C01 at Blocking 7 against a
hand reading of 0, and the same forms under the What
it blocks label at b12-whatblocks-fresh and C02a.

CH-328 (T12-14, Medium), the joiner limb: the blocking
figure counts blocks fields whose parts are joined by
the 5 fresh joiner forms of seat 09 and the 7 probes
K01 to K07 of seat 11, the double dagger form standing
shared between the papers and counted once, each at
Blocking 1 against a hand truth of 0.

CH-329 (T12-15, Medium), the wrapper limb: the blocking
figure counts blocks fields standing inside the 3
fresh wrapper forms of seat 09 and the 2 probes X05
and X06 of seat 11, each at Blocking 1 against a hand
truth of 0.

Hand truth under OP-Q12 as corrected: an entry counts
only where its blocks field names at least one item.
The cured phrase control, the D2 exact form, and the
O4 corpus form stand as governed bound pins in both
directions, a real reference beside a no item part
stands as a confinement pin on the fresh forms, and
the guarded neighbour forms of the seats observations
(seat 09 O3 and seat 11 O-12-11-1) stand as pins at
Blocking 0.

No construction in this file builds the F1 shape, and
no banked question is named in any construction.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def open_entry(number, blocks_value, label="Blocks"):
    return (
        "### DQ-%03d: Blocks case %d\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "Question: Which option?\n"
        "\n"
        "Options: Option A, Option B\n"
        "\n"
        "Cost of deciding late: Work stays blocked.\n"
        "\n"
        "%s: %s\n"
        "\n"
        "A plain context paragraph.\n"
        % (number, number, label, blocks_value))


def blocking_of(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline produced no output")
    _waiting, blocking = h.waiting_and_blocking(output)
    return output, h.int_of(blocking)


def check_values(case, values, expected):
    for value in values:
        with case.subTest(value=value):
            text = ("# Decision queue\n\n"
                    + open_entry(1, value))
            _output, blocking = blocking_of(text)
            case.assertEqual(blocking, expected)


class Ch327BlockingPhrasesRound12Test(unittest.TestCase):
    """CH-327, T12-13: the phrase limb of round 12."""

    def test_seat09_phrases_do_not_count(self):
        check_values(self, (
            "blocks no delays",
            "no delays",
            "blocks zero blockages",
            "free of impediments",
            "no impediment",
            "holds up no items",
            "impedes no ruling",
            "hinders no ruling",
            "obstructs no ruling",
        ), 0)

    def test_seat11_phrases_do_not_count(self):
        check_values(self, (
            "blocks no barriers",
            "blocks zero barriers",
            "no barrier is blocked",
            "blocks no holdups",
            "blocks no delays",
            "zero barriers blocked",
            "obstructs no ruling",
            "hinders no ruling",
            "impedes no ruling",
            "holds up no entry",
            "blocks no snags",
            "free of blockages",
            "clear of barriers",
            "the way forward is clear",
            "no blockage at all",
            "blocks nil rulings",
            "not one ruling blocked",
            "blocks no blockage",
        ), 0)

    def test_phrase_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "blocks zero blockages",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)

    def test_seat11_phrase_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "blocks no barriers",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)


class Ch328BlockingJoinersRound12Test(unittest.TestCase):
    """CH-328, T12-14: the joiner limb of round 12."""

    def test_seat09_joiners_do_not_count(self):
        check_values(self, (
            "none\u2021nothing",
            "none\u2215nothing",
            "none\u2044nothing",
            "none\uff0fnothing",
            "none\u29f5nothing",
        ), 0)

    def test_seat11_joiners_do_not_count(self):
        check_values(self, (
            "none\u2021nothing",
            "none\u00acnothing",
            "none\u00a6nothing",
            "none\u2190nothing",
            "none\u2194nothing",
            "none\u2030nothing",
            "none\u221enothing",
        ), 0)

    def test_real_reference_beside_fresh_joiner_counts(self):
        # Confinement pin, passing before and after: a
        # real reference beside a no item part counts, on
        # the fresh joiners as on the standing ones.
        check_values(self, (
            "none\u2021DQ-099",
            "none\u00acDQ-002",
            "DQ-002\u221enone",
            "none\u29f5DQ-002",
        ), 1)


class Ch329BlockingWrappersRound12Test(unittest.TestCase):
    """CH-329, T12-15: the wrapper limb of round 12."""

    def test_seat09_wrappers_do_not_count(self):
        check_values(self, (
            "\u3014none\u3015",
            "\u3016none\u3017",
            "\u300cnone]",
        ), 0)

    def test_seat11_wrappers_do_not_count(self):
        check_values(self, (
            "\u201enone'",
            "\u300enone]",
        ), 0)


class BlockingScaleRound12Test(unittest.TestCase):
    """The scale cases of the two papers, spanning the
    limbs as the papers file them."""

    def test_seat09_combined_foots_to_hand_truth(self):
        values = (
            "blocks zero blockages",
            "none\u2021nothing",
            "\u3014none\u3015",
            "blocks zero rulings",
            "DQ-002",
            "blocks no items",
            "none",
            "\u300cnone\u300d",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)
        listed = h.as_list(h.get(output, "blocking_list"))
        listed_ids = [h.text_of(h.get(
            item, "entry_id", "identifier")) for item in listed]
        self.assertEqual(listed_ids, ["DQ-005"])

    def test_seat11_combined_foots_to_zero(self):
        values = (
            "blocks no barriers",
            "blocks no holdups",
            "no barrier is blocked",
            "[none\u00bb",
            "none\u2021nothing",
            "blocks no delays",
            "obstructs no ruling",
            "holds up no entry",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)

    def test_seat09_whatblocks_fresh_foots(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002",
                             label="What it blocks")
                + "\n"
                + open_entry(2, "blocks zero blockages",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)


class BlockingPinsRound12Test(unittest.TestCase):
    """The governed pins of the locus, passing before
    and after in both directions."""

    def test_cured_phrase_control_still_does_not_count(self):
        # The cured phrase controls of seats 09 and 11
        # (the CH-287 forms), standing as pins.
        check_values(self, (
            "blocks zero questions",
            "blocks zero rulings",
            "blocks no obstacles",
            "blocks no item at all",
        ), 0)

    def test_d2_part_exactly_nothing_dot_still_names(self):
        # Pin under the D2 blocking narrowing pin (seat
        # 09 observation O1, a governed bound), in both
        # directions beside the cured control above.
        check_values(self, (
            "Nothing.",
            "nothing.",
            "nothing. and none",
            "none, nothing.",
        ), 1)

    def test_o4_corpus_form_nothing_named_stands(self):
        # Pin under the O4 corpus bound (seat 09
        # observation O2, a governed bound).
        check_values(self, ("nothing named.",), 1)

    def test_guarded_neighbour_forms_stand(self):
        # Forms guarded in the safe direction past the
        # same bounds, at the seats observations (seat
        # 09 O3 and seat 11 O-12-11-1), passing before
        # and after.
        check_values(self, (
            "all clear",
            "blocks no items",
            "blocks no items at all",
            "blocks nothing at all",
            "blocks zero entries",
            "blocks zero items",
            "clear of obstacles",
            "no blockage",
            "no items are blocked",
            "no question is blocked",
            "nothing is blocked",
            "path is clear",
            "the way is clear",
            "zero items blocked",
            "none\u2020nothing",
            "none\u2022nothing",
            "none\u00b7nothing",
            "none\u00b6nothing",
            "none\u00a7nothing",
            "\u300cnone\u300d",
            "\u300enone\u300f",
            "\uff08none\uff09",
            "\u2039none\u203a",
            "\u201enone\u201c",
            "\uff08none)",
            "\u2039none]",
            "[none\u00bb",
            "{none\u00bb",
            "<none)",
            "\"none}",
        ), 0)

    def test_real_reference_beside_no_item_part_counts(self):
        # Confinement pin, passing before and after: a
        # real reference beside a no item part counts,
        # beside a fresh phrase as beside a cured one
        # (the seat 11 form K08 among them).
        check_values(self, (
            "DQ-002, blocks no barriers",
            "DQ-002, blocks zero blockages",
            "none*DQ-099",
        ), 1)


if __name__ == "__main__":
    unittest.main()
