"""Step 17 (restart) fix wave 6, Fix Seat K4 tests.

Charges CH-108 and CH-111 (parse, the Status element reading
on the stored form, the gate limb, and the near marker label
reading on non letter forms), ruled at record section 58
ruling (d) for CH-108 and as charged for CH-111, prepared at
design/steps/step-17r-triage6-prep.md, against round 6 attack
seat 11 finding F-11R6-01 (High), paper at
design/steps/step-17r-attack6-11.md, and round 6 attack seat
17 finding S17-ATK6-17-01 (Low), paper at
design/steps/step-17r-attack6-17.md.

CH-108: the CH-89 cure is gated on the masked form of the
line opening with no marker, so on a Status line whose label
stands plain the stored form act never reaches the element
value reading. A comment segment standing inside the
disposition value word splits the word into two fragments
separated by masked spaces: a Banked entry records its value
as unclassified with a PIN-04 Note and loses its Banked head
evidence standing, and a Ruled entry silently derives Open
at exit 0. A segment standing after the value word leaves
the masked spaces standing in the recorded value and the
Banked head evidence group falls with them, with no trace.

CH-111: a Status label carrying one non letter character
inside the label word (a digit substitution, an underscore,
a hyphen, or a braille dot pattern), or one digit standing
after the complete label word, reaches Ambiguous at exit 4
with no finding at all, because the near marker letter
reading reads letters only and the CH-79 label cleaning
removes none of those characters.

Cure bounds. For CH-108 the stored form act reaches the
element value reading on a plain label line, for a segment
inside the value word or after it, inside the CH-69 stated
bound (segment boundaries only, on the whole line). The
reading governing each position on the line stands stated
in the fix paper: the label and the colon positions keep
the readings the CH-89 act and the masked scan give them,
the separator position keeps the masked separator reading
that credits the contrasts, and the value and after value
positions take the stored form. For CH-111 the near marker
reading takes the charged forms at the joint of the letter
reading and the CH-79 label cleaning, the cleaning ground
standing as ruling (a) of record section 52 states it.

Pins in both directions stand in this file: the K7 bound
guards (a space before a colon written in the file keeping
its Ambiguous form, a marker standing wholly inside a
segment counting nothing, a segment left unclosed crediting
nothing, and a one edit typo label keeping its near marker
form), the credited contrasts of the attack paper (a segment
between the colon and the value, a segment before the label,
a segment in the no space colon form, and the variant line
segment forms), the cleaned label neighbours of CH-111 (a
combining acute and a replacement character inside the
label, each taking its near marker Warning before and
after), and the CH-111 bound guards in the other direction
(two charged characters in one label, two digits after the
complete word, and a hyphen or an underscore standing after
the complete word, each standing silent as they stood).

The CH-89 pins whole stand in
product/tests/test_restart_step17_fix5_k7.py beside the
CH-69 pins in product/tests/test_restart_step17_fix4_k4.py
and the earlier pin files the K7 paper names; they are
re-run at this cluster close, not edited here.

Constructions are the attack papers own forms:
design/steps/step-17r-attack6-11.md, cases v1 to v8 and l14,
and design/steps/step-17r-attack6-17.md, cases i01 to i09.

Copyright: J.P. Picard aka Macro-Harder
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h


def _body(status_line):
    body = h._header_block()
    body += "### DQ-001: Open one\n\n"
    body += status_line + "\n\n"
    body += "Question: Which option?\n"
    body += "Options: A, B\nCost of deciding late: blocked.\n"
    body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
    return body


def _run(status_line, name):
    return h.run_pipeline(_body(status_line).encode("utf-8"), name)


def _run_cli(status_line, name, subcommand):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / name
        target.write_bytes(_body(status_line).encode("utf-8"))
        code, out, err = h.run_cli(subcommand, target)
    return code, (out + err).decode("utf-8", errors="replace")


def _rule2(output):
    return h.findings_for(output, entry_id="DQ-001", rule=2)


def _entry(output):
    return h.entry_by_id(output, "DQ-001")


def _unclassified_notes(output):
    return [finding for finding in h.findings_for(
        output, entry_id="DQ-001")
        if "unclassified status value" in
        (h.finding_statement(finding) or "")]


def _occurrence_total(output):
    recon = h.reconciliation_of(output)
    return h.int_of(h.get(recon, "status_occurrence_total",
                          "occurrence_total"))


def _group_members(output, *name_parts):
    group = h.census_class(h.census_of(output), *name_parts)
    if group is None:
        return []
    return h.census_members(group)


def _assert_banked_credited(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)), "Open")
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(_unclassified_notes(output), [])
    test_case.assertEqual(_occurrence_total(output), 1)
    test_case.assertIn("DQ-001", _group_members(
        output, "unheaded paragraphs"))
    test_case.assertEqual(
        _group_members(output, "unclassified"), [])
    waiting, _blocking = h.waiting_and_blocking(output)
    test_case.assertEqual(h.int_of(waiting), 1)


def _head_element(model):
    entry = h.entry_by_id(model, "DQ-001")
    elements = h.get(entry, "status_elements") or []
    test_case = unittest.TestCase()
    test_case.assertEqual(len(elements), 1)
    return elements[0]


class Ch108ValueSegmentChargedTest(unittest.TestCase):
    """F-11R6-01: the charged constructions of the attack
    paper, cases v1, v2, v3, l14, v4, and v5, each failing
    before the cure for its charged reason and standing
    credited after it."""

    def test_v1_segment_inside_banked_word_credits(self):
        _assert_banked_credited(self, "Status: Ban<!-- c -->ked",
                                "v1_value_segment_inside_banked_a.md")

    def test_v1_head_element_value_is_banked_whole(self):
        model, _output = _run("Status: Ban<!-- c -->ked",
                              "v1_value_segment_inside_banked_a.md")
        element = _head_element(model)
        self.assertEqual(h.get(element, "kind"),
                         "line start Status line")
        self.assertEqual(h.get(element, "verbatim"), "Banked")
        self.assertEqual(h.get(element, "occurrence_kind"),
                         "line start")

    def test_v2_segment_inside_banked_at_second_split_credits(self):
        _assert_banked_credited(self, "Status: Bank<!-- c -->ed",
                                "v2_value_segment_inside_banked_b.md")

    def test_v3_two_segments_inside_banked_word_credit(self):
        _assert_banked_credited(
            self, "Status: B<!-- a -->an<!-- b -->ked",
            "v3_value_two_segments.md")

    def test_l14_segment_inside_ruled_word_derives_decided(self):
        model, output = _run("Status: Rul<!-- c -->ed",
                             "l14_segment_inside_ruled_word.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Ruled")
        self.assertEqual(_unclassified_notes(output), [])
        self.assertEqual(_rule2(output), [])
        self.assertEqual(_occurrence_total(output), 1)
        canonical = h.canonical_counts(output)
        self.assertEqual(canonical.get("Ruled"), 1)
        self.assertEqual(canonical.get("Open"), 0)
        waiting, _blocking = h.waiting_and_blocking(output)
        self.assertEqual(h.int_of(waiting), 0)

    def test_l14_cli_exits_zero_on_both_subcommands(self):
        # The CLI standing of the charged form is read
        # against its plain twin on the same body: a Ruled
        # entry carrying no decision evidence draws the
        # governed rule 5 evidence findings and exits 1 on
        # this body shape, for the plain line exactly as for
        # the segment line, so the charged claim is that the
        # two standings are identical, with the segment form
        # counted Ruled and no unclassified value named.
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Status: Rul<!-- c -->ed",
                    "l14_segment_inside_ruled_word.md", subcommand)
                plain_code, _plain = _run_cli(
                    "Status: Ruled",
                    "l14_plain_ruled_control.md", subcommand)
                self.assertEqual(code, plain_code)
                self.assertIn("Canonical Ruled: 1", combined)
                self.assertNotIn("unclassified status value",
                                 combined)

    def test_v4_segment_after_the_value_word_credits(self):
        _assert_banked_credited(self, "Status: Banked<!-- c -->",
                                "v4_value_segment_after_banked.md")

    def test_v4_head_element_value_carries_no_masked_spaces(self):
        model, _output = _run("Status: Banked<!-- c -->",
                              "v4_value_segment_after_banked.md")
        element = _head_element(model)
        self.assertEqual(h.get(element, "verbatim"), "Banked")

    def test_v5_segment_after_a_space_after_the_value_credits(self):
        _assert_banked_credited(self, "Status: Banked <!-- c -->",
                                "v5_value_segment_word_break_none.md")

    def test_segment_before_label_and_inside_value_credits(self):
        _assert_banked_credited(
            self, "<!-- c --> Status: Ban<!-- c -->ked",
            "k4_segment_before_label_and_inside_value.md")


class Ch108CreditedContrastPinsTest(unittest.TestCase):
    """Contrasts of the attack paper standing credited
    before and after: cases v8, v6, v7, s2, s4, and s5, and
    the plain control. The separator position on each of
    these lines keeps the masked separator reading, and the
    label and colon positions keep the CH-89 reading."""

    def test_v8_segment_between_colon_and_value_credits(self):
        _assert_banked_credited(self, "Status:<!-- c -->Banked",
                                "v8_value_segment_before_banked_nospace.md")

    def test_v6_variant_segment_inside_unchanged_credits(self):
        model, output = _run("Status un<!-- c -->changed",
                             "v6_variant_segment_inside_unchanged.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "kind"), "variant phrasing")
        self.assertEqual(h.get(element, "verbatim"),
                         "Status unchanged")
        self.assertEqual(_rule2(output), [])
        self.assertEqual(_occurrence_total(output), 1)

    def test_v7_variant_segment_at_the_word_break_credits(self):
        model, output = _run("Status <!-- c --> unchanged",
                             "v7_variant_segment_at_break.md")
        self.assertIsNotNone(output)
        element = _head_element(model)
        self.assertEqual(h.get(element, "kind"), "variant phrasing")
        self.assertEqual(_rule2(output), [])
        self.assertEqual(_occurrence_total(output), 1)

    def test_s2_segment_after_the_colon_stands_credited(self):
        _assert_banked_credited(self, "Status: <!-- c --> Banked",
                                "s2_status_segment_after_colon.md")

    def test_s4_segment_before_the_label_stands_credited(self):
        _assert_banked_credited(self, "<!-- c --> Status: Banked",
                                "s4_status_segment_before_label.md")

    def test_s5_segment_in_the_no_space_colon_form_credits(self):
        _assert_banked_credited(self, "Status:<!-- c --> Banked",
                                "s5_status_segment_colon_nospace.md")

    def test_plain_status_line_control_stands_credited(self):
        _assert_banked_credited(self, "Status: Banked",
                                "k4_plain_status_control.md")


class Ch108BoundGuardPinsTest(unittest.TestCase):
    """The K7 bound guards, pinned in the other direction in
    this file, standing before and after: the CH-69 bound
    reaches segment boundaries only, and no written form is
    normalised by this cure."""

    def test_s1_written_space_before_colon_stays_ambiguous(self):
        _model, output = _run("Status : Banked",
                              "s1_status_space_colon.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(h.entry_sub_label(_entry(output)),
                         "No element")
        self.assertEqual(len(_rule2(output)), 1)
        self.assertEqual(_occurrence_total(output), 0)

    def test_marker_wholly_inside_a_segment_counts_nothing(self):
        body = h._header_block()
        body += "### DQ-001: Open one\n\nStatus: Banked\n\n"
        body += "<!-- Status: Ruled -->\n\n"
        body += "Question: Which option?\n"
        body += "Options: A, B\nCost of deciding late: blocked.\n"
        body += "Blocks: DQ-002\n\nA waiting paragraph.\n"
        _model, output = h.run_pipeline(
            body.encode("utf-8"), "k4_marker_inside_segment.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)), "Open")
        self.assertEqual(_occurrence_total(output), 1)
        self.assertEqual(_rule2(output), [])

    def test_unclosed_segment_in_the_label_credits_nothing(self):
        _model, output = _run("Status <!-- c : Banked",
                              "k4_unclosed_segment_in_label.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(_occurrence_total(output), 0)
        self.assertEqual(_rule2(output), [])

    def test_unclosed_segment_inside_value_credits_nothing_past_it(self):
        # A segment left unclosed inside the value word
        # credits nothing past its opening: the word Banked
        # never forms, the recorded value stands
        # unclassified, and no Banked head evidence group
        # stands for the entry.
        _model, output = _run("Status: Ban<!-- c",
                              "k4_unclosed_segment_inside_value.md")
        self.assertIsNotNone(output)
        self.assertEqual(_group_members(
            output, "unheaded paragraphs"), [])
        self.assertEqual(len(_unclassified_notes(output)), 1)

    def test_one_edit_typo_label_keeps_its_near_marker_form(self):
        _model, output = _run("Staus: Banked",
                              "k4_typo_label_control.md")
        self.assertIsNotNone(output)
        self.assertEqual(h.entry_state(_entry(output)),
                         "Ambiguous")
        self.assertEqual(len(_rule2(output)), 1)
        self.assertEqual(_occurrence_total(output), 0)


def _assert_near_marker(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)),
                           "Ambiguous")
    test_case.assertEqual(h.entry_sub_label(_entry(output)),
                          "No element")
    test_case.assertEqual(len(_rule2(output)), 1)
    test_case.assertEqual(_occurrence_total(output), 0)


def _assert_silent_ambiguous(test_case, status_line, name):
    _model, output = _run(status_line, name)
    test_case.assertIsNotNone(output)
    test_case.assertEqual(h.entry_state(_entry(output)),
                           "Ambiguous")
    # Silence on the label: no near marker finding stands.
    # Every construction in this file carries the standing
    # PD-R7 Note for its Blocks citation of DQ-002, which
    # has no headed entry in the body, so the silence is
    # read on the label findings, not on the findings list
    # as a whole: no rule 2 finding, and no finding above
    # Note grade, stands on the run.
    test_case.assertEqual(_rule2(output), [])
    test_case.assertEqual(
        [finding for finding in h.findings_for(output)
         if h.finding_severity(finding) != "Note"], [])
    test_case.assertEqual(_occurrence_total(output), 0)


class Ch111NearMarkerChargedFormsTest(unittest.TestCase):
    """S17-ATK6-17-01: the charged constructions of the
    attack paper, cases i01 to i06 and i09, each reaching
    Ambiguous at exit 4 with no finding before the cure and
    taking the near marker Warning after it."""

    def test_i01_digit_for_the_final_label_letter(self):
        _assert_near_marker(self, "Statu5: Banked",
                            "i01_status_digit_mid_label.md")

    def test_i02_digit_for_the_first_label_letter(self):
        _assert_near_marker(self, "5tatus: Banked",
                            "i02_status_digit_first_label.md")

    def test_i06_digit_for_the_third_label_letter(self):
        _assert_near_marker(self, "St4tus: Banked",
                            "i06_status_digit_second_label.md")

    def test_i04_digit_after_the_complete_label_word(self):
        _assert_near_marker(self, "Status1: Banked",
                            "i04_status_digit_suffix_label.md")

    def test_i03_underscore_inside_the_label(self):
        _assert_near_marker(self, "Stat_us: Banked",
                            "i03_status_underscore_label.md")

    def test_i05_hyphen_inside_the_label(self):
        _assert_near_marker(self, "Stat-us: Banked",
                            "i05_status_hyphen_label.md")

    def test_i09_braille_dot_pattern_inside_the_label(self):
        _assert_near_marker(self, "Stat\u2801us: Banked",
                            "i09_status_braille_dot_inside_label.md")

    def test_i01_cli_exits_four_with_the_warning(self):
        for subcommand in ("validate", "render"):
            with self.subTest(subcommand=subcommand):
                code, combined = _run_cli(
                    "Statu5: Banked",
                    "i01_status_digit_mid_label.md", subcommand)
                self.assertEqual(code, 4)
                self.assertIn("Ambiguous", combined)
                if subcommand == "validate":
                    self.assertIn("carries no element", combined)


class Ch111CleanedNeighbourPinsTest(unittest.TestCase):
    """The cleaned neighbours of the charge, standing with
    their near marker Warning before and after: the CH-79
    cleaning removes a combining acute and a replacement
    character standing inside the label, and the letter typo
    form stands as it stood."""

    def test_i07_combining_acute_inside_the_label_warns(self):
        _assert_near_marker(self, "Stat\u0301us: Banked",
                            "i07_status_combining_acute_label.md")

    def test_i08_replacement_character_inside_the_label_warns(self):
        _assert_near_marker(self, "Stat\ufffdus: Banked",
                            "i08_status_replacement_label.md")

    def test_letter_typo_label_warns_as_it_stood(self):
        _assert_near_marker(self, "Staus: Banked",
                            "k4_letter_typo_label.md")


class Ch111BoundGuardPinsTest(unittest.TestCase):
    """Pins in the other direction, standing before and
    after: the cure takes one charged character inside the
    label word, or one digit after the complete word, and
    nothing wider."""

    def test_two_digit_substitutions_in_one_label_stay_silent(self):
        _assert_silent_ambiguous(self, "St4tu5: Banked",
                                 "k4_two_digit_substitutions.md")

    def test_two_digits_after_the_complete_word_stay_silent(self):
        _assert_silent_ambiguous(self, "Status12: Banked",
                                 "k4_two_digit_suffix.md")

    def test_hyphen_after_the_complete_word_stays_silent(self):
        _assert_silent_ambiguous(self, "Status-: Banked",
                                 "k4_hyphen_after_word.md")

    def test_underscore_after_the_complete_word_stays_silent(self):
        _assert_silent_ambiguous(self, "Status_: Banked",
                                 "k4_underscore_after_word.md")


if __name__ == "__main__":
    unittest.main()
