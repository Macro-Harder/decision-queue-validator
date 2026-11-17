"""Restart Step 16 fix wave 9, Fix seat Z tests.

Seat Z owns finding A9-8-1 (Auditor 8, confirmation
round 9, design/steps/step-16r-audit9-8.md, section 2):
a name written as one word whose joined form reads
whole as the evidenced name sequence, with the
separator standing inside a name token rather than at
a name token boundary, still satisfies the ruling text
test in both limbs and every container. Its evidenced
forms include "Ruled: J.P. morga-nstanley" and the
displacements "morganstan-ley", "mo-rganstanley",
"morg-anstanley", "stanle-ymorgan", "mar-ymorgan",
the triple "morga-nstanle-ymary", "marymorga-n" and
"stanleymorga-n", under the hyphen, full stop, slash,
underscore, plus, ampersand and comma joiners, beside
fragmented initials, spaced initials, a spaced
attribution, a combined attribution, a spaced name
anchor and a combined name pair anchor, plus the
attribution and a name fragmented inside one word,
"capt-ainmorgan" and "morga-ncaptain". Every run of
each such word is a fragment of an attribution or
name token and its joined form reads whole as a
sequence of attribution and name tokens.

The triage charge, at step record section 30: the
anchored name reading takes the sequence reading for
a single further word, in the narrowest form that
preserves the standing bounds. Those bounds stand
pinned below as guards: a word carrying a whole non
name run keeps the matter standing ("morgan-harbour",
"morgan-captain", "morgan-42"); "morgan-stanley
smith" and a joined name word with no fragmented or
spaced attribution beside it still pass; the harbour
bound ("Ruled: J.P. harbour") still passes; and the
separator free concatenation "morganstanley" still
passes, the cure requiring at least two runs in the
word, so a one run word is not read as a sequence.

Each test below pins the specified behaviour, written
before the cure. The construction form tests fail
before the cure and pass after it, in the labelled
paragraph block and in the element limb alike. The
control and guard tests pass before and after.

Copyright: J.P. Picard aka Macro-Harder
"""

import unittest

import dqv_harness as h


def _decided_entry(entry_id, ruling_paragraph,
                   decider_sentence=None, closing="Status: closed."):
    if decider_sentence is None:
        decider_sentence = (
            "Ruled by Captain JP in the roles chat on 2026-11-14.")
    text = (
        "# Decision queue\n"
        "\n"
        "### %s: the checker note form\n"
        "\n"
        "Status: Banked\n"
        "\n"
        "%s\n"
        "\n"
        "%s\n"
        "\n"
        "Landed: the checker note in NOTES.md section 2 now "
        "states the agreed form.\n"
        "\n"
        "%s\n"
    ) % (entry_id, decider_sentence, ruling_paragraph, closing)
    return text.encode("utf-8")


SETTLED_DECIDER = (
    "Settled by the Manager under the grant, recorded in the "
    "roles chat on 2026-11-14.")

BLOCK_FORM = (
    "# Decision queue\n"
    "\n"
    "### DQ-1102: the harbour consequence\n"
    "\n"
    "Status: Banked\n"
    "\n"
    "#### Ruling by Captain JP\n"
    "\n"
    "Ruled by: Captain JP\n"
    "\n"
    "Ruling text: \"Count it as a fail.\"\n"
    "\n"
    "Ruling outcome: The outcome stands as recorded.\n"
    "\n"
    "Where the ruling landed: NOTES.md section 2.\n"
    "\n"
    "Status: RULED, closed. This item is ruled.\n"
).encode("utf-8")


CLOSING_PROSE_FORM = (
    "## DQ-1103: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


DISPLACED_LABELLED_FORMS = (
    ("DQ-1110", "Ruled: J.P. morga-nstanley", None),
    ("DQ-1111", "Ruled: J.P. morganstan-ley", None),
    ("DQ-1112", "Ruled: J.P. mo-rganstanley", None),
    ("DQ-1113", "Ruled: J.P. morg-anstanley", None),
    ("DQ-1114", "Ruled: J.P. stanle-ymorgan", None),
    ("DQ-1115", "Ruled: J.P. mar-ymorgan", None),
    ("DQ-1116", "Ruled: J.P. morga-nstanle-ymary", None),
    ("DQ-1117", "Ruled: J.P. marymorga-n", None),
    ("DQ-1118", "Ruled: J.P. stanleymorga-n", None),
    ("DQ-1119", "Ruled: J.P. morga.nstanley", None),
    ("DQ-1120", "Ruled: J.P. morga/nstanley", None),
    ("DQ-1121", "Ruled: J.P. morga_nstanley", None),
    ("DQ-1122", "Ruled: J.P. morga+nstanley", None),
    ("DQ-1123", "Ruled: J.P. morga&nstanley", None),
    ("DQ-1124", "Ruled: J.P. morga,nstanley", None),
    ("DQ-1125", "Ruled: J. P. morga-nstanley", None),
    ("DQ-1126", "Ruled: Cap tain morga-nstanley", None),
    ("DQ-1127", "Ruled: Ca.p tain morga-nstanley", None),
    ("DQ-1128", "Ruled: Mor gan morga-nstanley", None),
    ("DQ-1129", "Ruled: mor-gan stan-ley morga-nstanley", None),
    ("DQ-1130", "Settled: J.P. morga-nstanley", SETTLED_DECIDER),
    ("DQ-1131", "Ruled: J.P. morga-nstanley.", None),
    ("DQ-1132", "Ruled: J.P. morga-nStanley", None),
    ("DQ-1133", "Ruled: J.P. capt-ainmorgan", None),
    ("DQ-1134", "Ruled: J.P. morga-ncaptain", None),
)


DISPLACED_ELEMENT_FORMS = (
    ("DQ-1140", "Ruled:\tJ.P. morga-nstanley", None),
    ("DQ-1141", "Settled:\tJ.P. morga-nstanley", SETTLED_DECIDER),
    ("DQ-1142", "```\nRuled: J.P. morga-nstanley\n```", None),
    ("DQ-1143", "> Ruled: J.P. morga-nstanley", None),
    ("DQ-1144", "The meeting ended at noon. "
              "Ruled: J.P. morga-nstanley", None),
    ("DQ-1145", "```\nRuled: J.P. capt-ainmorgan\n```", None),
    ("DQ-1146", "> Ruled: J.P. morga-ncaptain", None),
)


def _ruling_text_errors(output, entry_id):
    found = []
    for finding in h.findings_for(output, entry_id=entry_id, rule=5):
        statement = h.finding_statement(finding) or ""
        if "No ruling text" in statement:
            found.append(finding)
    return found


def _rule5_findings(output, entry_id):
    return h.findings_for(output, entry_id=entry_id, rule=5)


class _FormAssert:
    def _assert_one_error(self, entry_id, paragraph, decider_sentence):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        found = _ruling_text_errors(output, entry_id)
        self.assertEqual(len(found), 1, entry_id)
        self.assertEqual(h.finding_severity(found[0]), "Error")

    def _assert_no_error(self, entry_id, paragraph, decider_sentence=None):
        data = _decided_entry(
            entry_id, paragraph, decider_sentence=decider_sentence)
        _model, output = h.run_pipeline(data, name="probe.md")
        self.assertEqual(
            _ruling_text_errors(output, entry_id), [], entry_id)


class DisplacedLabelledFormTest(_FormAssert, unittest.TestCase):
    """A9-8-1 in the labelled paragraph block: a name
    written as one word whose separator stands inside
    a name token, beside an anchor, records no ruling
    text."""

    def test_separator_inside_second_name(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[0])

    def test_separator_near_end_of_joined_pair(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[1])

    def test_separator_after_two_letters(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[2])

    def test_separator_inside_first_name(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[3])

    def test_reversed_pair_separator_inside_first_name(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[4])

    def test_given_name_separator_inside_it(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[5])

    def test_triple_with_two_displaced_separators(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[6])

    def test_separator_inside_final_token_of_pair(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[7])

    def test_separator_inside_final_token_after_surname(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[8])

    def test_full_stop_joiner_displaced(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[9])

    def test_slash_joiner_displaced(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[10])

    def test_underscore_joiner_displaced(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[11])

    def test_plus_joiner_displaced(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[12])

    def test_ampersand_joiner_displaced(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[13])

    def test_comma_joiner_displaced(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[14])

    def test_displaced_beside_spaced_initials(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[15])

    def test_displaced_beside_spaced_attribution(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[16])

    def test_displaced_beside_combined_attribution(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[17])

    def test_displaced_beside_spaced_name_anchor(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[18])

    def test_displaced_beside_combined_name_pair_anchor(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[19])

    def test_settled_displaced_beside_initials(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[20])

    def test_displaced_with_closing_full_stop(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[21])

    def test_displaced_with_capitalised_second_name(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[22])

    def test_attribution_and_name_inside_one_word(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[23])

    def test_name_and_attribution_inside_one_word(self):
        self._assert_one_error(*DISPLACED_LABELLED_FORMS[24])


class DisplacedElementFormTest(_FormAssert, unittest.TestCase):
    """A9-8-1 in the element limb: the same displaced
    joined name matters in the tab, fenced, blockquoted
    and prose spellings record no ruling text through
    that limb either."""

    def test_tab_displaced_pair(self):
        self._assert_one_error(*DISPLACED_ELEMENT_FORMS[0])

    def test_tab_settled_displaced_pair(self):
        self._assert_one_error(*DISPLACED_ELEMENT_FORMS[1])

    def test_fenced_displaced_pair(self):
        self._assert_one_error(*DISPLACED_ELEMENT_FORMS[2])

    def test_blockquote_displaced_pair(self):
        self._assert_one_error(*DISPLACED_ELEMENT_FORMS[3])

    def test_prose_displaced_pair(self):
        self._assert_one_error(*DISPLACED_ELEMENT_FORMS[4])

    def test_fenced_attribution_and_name_inside_one_word(self):
        self._assert_one_error(*DISPLACED_ELEMENT_FORMS[5])

    def test_blockquote_name_and_attribution_inside_one_word(self):
        self._assert_one_error(*DISPLACED_ELEMENT_FORMS[6])


class ControlFormTest(_FormAssert, unittest.TestCase):
    """The controls the earlier rounds fix: the single
    split name token and the boundary joined pair
    already take exactly one Error and keep doing so."""

    def test_single_split_name_token_keeps_the_error(self):
        self._assert_one_error(
            "DQ-1150", "Ruled: J.P. mor-gan", None)

    def test_boundary_joined_pair_keeps_the_error(self):
        self._assert_one_error(
            "DQ-1151", "Ruled: J.P. morgan-stanley", None)


class GuardFormTest(_FormAssert, unittest.TestCase):
    """The standing bounds keep their passes: a word
    carrying a whole non name run keeps the matter
    standing, a further non qualifying word keeps the
    whole matter standing, a joined name word with no
    anchor passes, the harbour bound passes, genuine
    matter after a displaced word passes, and the
    separator free concatenation passes, this cure
    requiring at least two runs in the word."""

    def test_whole_harbour_run_joined_word_still_passes(self):
        self._assert_no_error("DQ-1160", "Ruled: J.P. morgan-harbour")

    def test_whole_attribution_run_joined_word_still_passes(self):
        self._assert_no_error("DQ-1161", "Ruled: J.P. morgan-captain")

    def test_whole_number_run_joined_word_still_passes(self):
        self._assert_no_error("DQ-1162", "Ruled: J.P. morgan-42")

    def test_joined_pair_beside_further_word_still_passes(self):
        self._assert_no_error(
            "DQ-1163", "Ruled: J.P. morgan-stanley smith")

    def test_joined_pair_with_no_anchor_still_passes(self):
        self._assert_no_error("DQ-1164", "Ruled: morgan-stanley")

    def test_harbour_bound_still_passes(self):
        self._assert_no_error("DQ-1165", "Ruled: J.P. harbour")

    def test_genuine_matter_after_displaced_word_still_passes(self):
        self._assert_no_error(
            "DQ-1166", "Ruled: J.P. morga-nstanley takes the harbour.")

    def test_separator_free_concatenation_still_passes(self):
        self._assert_no_error("DQ-1167", "Ruled: J.P. morganstanley")

    def test_genuine_lowercase_words_beside_initials_still_pass(self):
        self._assert_no_error("DQ-1168", "Ruled: J.P. checker note")

    def test_number_alone_still_passes(self):
        self._assert_no_error("DQ-1169", "Ruled: 42.")


class StandingPositionGuardTest(unittest.TestCase):
    """The positions the earlier seats established still
    hold: fixture F-12 keeps exactly its one ruling text
    Error, the eight compact form entries keep their
    passes, the pin totals stand, and the level 4 block
    and closing prose forms keep passing."""

    def test_f12_keeps_exactly_one_ruling_text_error(self):
        _model, output = h.cached_pipeline("F-12")
        found = _ruling_text_errors(output, "DQ-001")
        self.assertEqual(len(found), 1)
        self.assertEqual(h.finding_severity(found[0]), "Error")
        self.assertEqual(len(_rule5_findings(output, "DQ-001")), 1)

    def test_pin_compact_form_entries_take_no_ruling_text_error(self):
        _model, output = h.cached_pipeline("PIN")
        for entry_id in ("DQ-147", "DQ-148", "DQ-149", "DQ-150",
                         "DQ-151", "DQ-152", "DQ-154", "DQ-155"):
            self.assertEqual(
                _ruling_text_errors(output, entry_id), [], entry_id)

    def test_pin_totals_stand(self):
        _model, output = h.cached_pipeline("PIN")
        counts = {"Error": 0, "Warning": 0, "Note": 0}
        for finding in h.findings_of(output):
            counts[h.finding_severity(finding)] += 1
        self.assertEqual(
            counts, {"Error": 16, "Warning": 57, "Note": 13})

    def test_level4_block_form_still_passes(self):
        _model, output = h.run_pipeline(BLOCK_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-1102"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_closing_prose_form_still_passes(self):
        _model, output = h.run_pipeline(
            CLOSING_PROSE_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-1103"), [])


if __name__ == "__main__":
    unittest.main()
