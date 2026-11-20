"""Step 17 fix wave 11, Fix Seat C tests.

Charges CH-287, CH-288, and CH-289, the blocking family
of round 11 in the three charge form of record section
108: CH-287 the phrase limb (distinct finding T11-12),
CH-288 the joiner limb (T11-13), and CH-289 the wrapper
limb (T11-14), sourced at round 11 attack seat 10
finding A11-10-F1, round 11 attack seat 12 findings
F-11-12-1, F-11-12-2, and F-11-12-3, and round 11
attack seat 20 findings F-20-11-5 and F-20-11-6,
consolidated in design/steps/step-17r-r11-triage-prep.md
at section 2.3 and Cluster C. The cure stands in
product/decision_queue_validator/validate.py only, at
the charged locus: the Blocks value reading as cured
at CH-239 to CH-241.

CH-287 (T11-12, Medium), the phrase limb: the blocking
figure counts blocks fields that name no item, in the
17 fresh phrase forms of seat 10, the 24 staged probes
P01 to P24 and the 7 own probes of seat 12, and the
9 staged wordings cb01 to cb08 and cb13 and the 8 own
wordings of seat 20, shared members counted once, each
at Blocking 1 against a hand truth of 0 under OP-Q12
as corrected, with the seat 10 scale case b11-combined
at Blocking 4 against a hand truth of 1, the seat 12
combined file C01 at Blocking 7 against a hand reading
of 0, and the same edge under the What it blocks label.

CH-288 (T11-13, Medium), the joiner limb: the blocking
figure counts blocks fields whose parts are joined by
the 10 fresh joiner forms of seat 10 and the 7 staged
probes K01 to K07 and the own probe R14 of seat 12,
each at Blocking 1 against a hand truth of 0.

CH-289 (T11-14, Medium, the governing grade), the
wrapper limb: the blocking figure counts blocks fields
standing inside the 6 fresh wrapper forms of seat 10,
the 7 staged probes X04 to X10 of seat 12, and the one
mismatched pair (none plus a closing guillemet of seat
20 case cb31, shared members counted once, each at
Blocking 1 against a hand truth of 0.

Hand truth under OP-Q12 as corrected: an entry counts
only where its blocks field names at least one item.
The cured phrase control, the D2 exact form, and the
O4 corpus form stand as governed bound pins in both
directions, and a real reference beside a no item part
stands as a confinement pin on the fresh forms as on
the standing ones.

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


class Ch287BlockingPhrasesRound11Test(unittest.TestCase):
    """CH-287, T11-12: the phrase limb of round 11."""

    def test_seat10_phrases_do_not_count(self):
        check_values(self, (
            "blocks zero rulings",
            "zero rulings blocked",
            "no rulings blocked",
            "not a single ruling blocked",
            "zero blockers blocked",
            "blocks no entries at all",
            "free of blockage",
            "no obstacle",
            "no obstructions",
            "holds up no question",
            "holds up nothing at all",
            "nothing is held up",
            "impedes nothing at all",
            "nothing is hindered",
            "is not impeding",
            "clear of hindrance",
            "no hindrance at all",
        ), 0)

    def test_seat12_phrases_do_not_count(self):
        check_values(self, (
            "blocks no obstacles",
            "blocks zero obstacles",
            "no obstacle is blocked",
            "zero obstacles blocked",
            "blocks no hindrances",
            "blocks no roadblocks",
            "no rulings blocked",
            "no questions are blocked",
            "no decisions are blocked",
            "hinders no question",
            "obstructs no question",
            "impedes no question",
            "holds up no question",
            "blocks no question",
            "free of obstruction",
            "no hindrance at all",
            "blocks nil questions",
            "blocks zero rulings",
            "not one question blocked",
            "not a single decision blocked",
            "no entry blocks anything",
            "clear of hindrances",
            "the route is clear",
            "zero blockers blocked",
        ), 0)

    def test_seat12_own_phrases_do_not_count(self):
        check_values(self, (
            "blocks no impediments",
            "no impediment is blocked",
            "blocks zero roadblocks",
            "zero hindrances blocked",
            "holds up no ruling",
            "the path forward is clear",
            "blocks no blockages",
        ), 0)

    def test_seat20_phrases_do_not_count(self):
        check_values(self, (
            "blocks no decision at all",
            "blocks nothing whatsoever",
            "no decision blocked",
            "zero decisions are blocked",
            "blocks zero rulings",
            "no rulings blocked",
            "blocks no question at all",
            "no item is obstructed",
            "zero blockers blocked",
        ), 0)

    def test_seat20_own_phrases_do_not_count(self):
        check_values(self, (
            "blocks no rulings at all",
            "no rulings are blocked",
            "zero rulings are blocked",
            "blocks zero entries at all",
            "road is clear",
            "clear of obstructions",
            "holds up no decision",
            "no question is obstructed",
        ), 0)

    def test_phrase_under_what_it_blocks_label(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002")
                + "\n"
                + open_entry(2, "blocks no obstacles",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)


class Ch288BlockingJoinersRound11Test(unittest.TestCase):
    """CH-288, T11-13: the joiner limb of round 11."""

    def test_seat10_joiners_do_not_count(self):
        check_values(self, (
            "none\u00bfnothing",
            "none\u00abnothing",
            "none\u00bbnothing",
            "none\u2039nothing",
            "none\u203anothing",
            "none\u201cnothing",
            "none\u201dnothing",
            "none\u2019nothing",
            "none\u00d7nothing",
            "none\u00f7nothing",
        ), 0)

    def test_seat12_joiners_do_not_count(self):
        check_values(self, (
            'none"nothing',
            "none\u2026nothing",
            "none\u2122nothing",
            "none\u00f7nothing",
            "none\u00d7nothing",
            "none\u2192nothing",
            "none\u203dnothing",
            "none\u25e6nothing",
        ), 0)

    def test_real_reference_beside_fresh_joiner_counts(self):
        # Confinement pin, passing before and after: a
        # real reference beside a no item part counts, on
        # the fresh joiners as on the standing ones.
        check_values(self, (
            "none\u00bfDQ-099",
            'none"DQ-002',
            "DQ-002\u2026none",
            "none\u2192DQ-002",
        ), 1)


class Ch289BlockingWrappersRound11Test(unittest.TestCase):
    """CH-289, T11-14: the wrapper limb of round 11."""

    def test_seat10_wrappers_do_not_count(self):
        check_values(self, (
            '"none]',
            "\u00abnone}",
            "\u00abnone>",
            "\u3008none\u3009",
            "\u3010none\u3011",
            "\u300anone\u300b",
        ), 0)

    def test_seat12_wrappers_do_not_count(self):
        check_values(self, (
            "\u00abnone}",
            "\u2039none]",
            "\u201enone\u201d",
            "\u300enone\u300d",
            "\uff08none)",
            "(none\uff09",
            "\u201anone'",
        ), 0)

    def test_seat20_wrapper_does_not_count(self):
        check_values(self, (
            "(none\u00bb",
        ), 0)


class BlockingScaleRound11Test(unittest.TestCase):
    """The scale cases of the three papers, spanning the
    limbs as the papers file them."""

    def test_seat10_combined_foots_to_hand_truth(self):
        values = (
            "blocks zero rulings",
            "no obstacle",
            "none\u00bfnothing",
            "<none)",
            "blocks zero questions",
            "DQ-002",
            "none",
            "(none]",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)
        listed = h.as_list(h.get(output, "blocking_list"))
        listed_ids = [h.text_of(h.get(
            item, "entry_id", "identifier")) for item in listed]
        self.assertEqual(listed_ids, ["DQ-006"])

    def test_seat12_combined_foots_to_zero(self):
        values = (
            "blocks no obstacles",
            "blocks no hindrances",
            "no questions are blocked",
            "[none>",
            "none\u2026nothing",
            "blocks no question",
            "hinders no question",
            "no entry blocks anything",
        )
        text = "# Decision queue\n\n" + "\n".join(
            open_entry(number, value)
            for number, value in enumerate(values, start=1))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 0)

    def test_seat10_whatblocks_fresh_foots(self):
        text = ("# Decision queue\n\n"
                + open_entry(1, "DQ-002",
                             label="What it blocks")
                + "\n"
                + open_entry(2, "blocks zero rulings",
                             label="What it blocks"))
        _output, blocking = blocking_of(text)
        self.assertEqual(blocking, 1)


class BlockingPinsRound11Test(unittest.TestCase):
    """The governed pins of the locus, passing before
    and after in both directions."""

    def test_cured_phrase_control_still_does_not_count(self):
        # The cured phrase control of seats 10 and 12
        # (the CH-239 form), standing as a pin.
        check_values(self, (
            "blocks zero questions",
            "blocks no blockers",
            "the road is clear",
            "blocks no item at all",
        ), 0)

    def test_d2_part_exactly_nothing_dot_still_names(self):
        # Pin under the D2 blocking narrowing pin (seat
        # 10 observation O1, a governed bound), in both
        # directions beside the cured control above.
        check_values(self, (
            "Nothing.",
            "nothing.",
            "nothing. and none",
            "none, nothing.",
        ), 1)

    def test_o4_corpus_form_nothing_named_stands(self):
        # Pin under the O4 corpus bound (seat 10
        # observation O2, a governed bound).
        check_values(self, ("nothing named.",), 1)

    def test_guarded_neighbour_forms_stand(self):
        # Forms guarded in the safe direction past the
        # same bounds, at the seats observations (seat
        # 10 O3, seat 12 O-11-12-3, seat 20 O-11-20-3),
        # passing before and after.
        check_values(self, (
            "<none)",
            "[none>",
            "{none>",
            "<none}",
            "'none)",
            "free of roadblocks",
            "\u201enone\u201c",
            "\u2039none\u203a",
            "\u00abnone\u00bb",
            "none\u2022nothing",
            "none\u00a7nothing",
            "free of obstacles",
            "no hindrance",
            "impedes nothing",
            "holds up nothing",
            "no entries blocked",
            "impedes no item",
            "none&nothing",
            "none^nothing",
            "none%nothing",
            "none/nothing",
            "none_nothing",
            "none+nothing",
            "none=nothing",
            "[none}",
            "{none)",
        ), 0)

    def test_real_reference_beside_no_item_part_counts(self):
        # Confinement pin, passing before and after: a
        # real reference beside a no item part counts,
        # beside a fresh phrase as beside a cured one
        # (the seat 20 confinement forms cb33 and
        # own_cb16, and the seat 12 form K08).
        check_values(self, (
            "DQ-002, blocks no decision at all",
            "DQ-002, blocks no rulings at all",
            "none*DQ-099",
        ), 1)


if __name__ == "__main__":
    unittest.main()
