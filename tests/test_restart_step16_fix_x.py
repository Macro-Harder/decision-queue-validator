"""Restart Step 16 fix wave 8, Fix seat X tests.

Seat X owns the merged construction of findings A8-3-1
(Auditor 3, confirmation round 8,
design/steps/step-16r-audit8-3.md, section 4) and A8-8-1
part (a) (Auditor 8, confirmation round 8,
design/steps/step-16r-audit8-8.md, section 2), ruled one
construction at step record section 27 on the round 8
trace ruling E-26, and finding A8-8-1 part (b) (Auditor 8,
section 3). The merged construction: a name written as
two or three of the evidenced name words (morgan,
stanley, mary) joined by punctuation inside one lowercase
word, standing beside a fragmented or spaced attribution
anchor, still satisfies the ruling text test in both
limbs, because the helper _labelled_matter_tokens tests
each further word by its joined form and by its first
letter, and the joined form of two name words is no
single name token while the first letter is lowercase.
Part (b): an attribution split by punctuation inside the
word and by a space together, in the forms "Ca.p tain
JP", "Cap t.ain JP", "C.ap tain JP", "Ma.n ager
decided.", "the Ma.n ager decided." and "Gr.a nt",
stands on attribution fragments alone in both limbs,
because the fragmented reading takes a break inside one
word, the spaced reading takes whole standing words, and
this construction carries both breaks at once.

The triage ground, at step record sections 21, 24 and
27: name matter or attribution matter restated in a
spelling the helper does not yet read as that matter is
the same matter, not ruling matter, and an attribution
with nothing beside it but name matter earns no pass.

Each test below pins the specified behaviour, written
before the cure. The construction form tests fail before
the cure and pass after it, in the labelled paragraph
block and in the element limb alike. The control and
guard tests pass before and after: the capitalised joined
forms and the single split token "mor-gan" keep exactly
their one Error; genuine ruling matter beside an anchor
keeps passing, including genuine matter standing after a
joined name word; a person name with no fragmented or
spaced attribution word beside it still passes; one thin
lowercase word beside fragmented initials still passes;
the separator free concatenation form "morganstanley"
still passes, standing inside Fix Seat V's stated bound
edge 4 as Auditor 8 ruled it; fixture F-12 keeps exactly
its one ruling text Error; the eight compact form entries
of the corpus pin keep taking no ruling text Error; and
the pin totals stand.

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
    "### DQ-902: the harbour consequence\n"
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
    "## DQ-903: the harbour store note. RULED by Captain JP "
    "2026-11-15\n"
    "\n"
    "Origin: the harbour store question in the Clerk note of "
    "2026-11-14. Captain JP ruled in her own words: \"Keep the "
    "store by the harbour gate.\" Ruled: the harbour store "
    "stands by the harbour gate, and the night keeper holds "
    "its key. Landed: the harbour store paragraph in the Clerk "
    "note now states the gate form. Status: closed.\n"
).encode("utf-8")


JOINED_LABELLED_FORMS = (
    ("DQ-910", "Ruled: J.P. morgan-stanley", None),
    ("DQ-911", "Ruled: J.P. stanley-morgan", None),
    ("DQ-912", "Ruled: J.P. morgan-mary", None),
    ("DQ-913", "Ruled: J.P. morgan.stanley", None),
    ("DQ-914", "Ruled: J.P. morgan/stanley", None),
    ("DQ-915", "Ruled: J.P. morgan_stanley", None),
    ("DQ-916", "Ruled: J.P. morgan,stanley", None),
    ("DQ-917", "Ruled: J.P. morgan-stanley-mary", None),
    ("DQ-918", "Ruled: J.P. morgan-Stanley", None),
    ("DQ-919", "Ruled: Cap tain morgan-stanley", None),
    ("DQ-920", "Ruled: J. P. morgan-stanley", None),
    ("DQ-921", "Settled: J.P. morgan-stanley", SETTLED_DECIDER),
    ("DQ-922", "Ruled: J.P. morgan+stanley", None),
    ("DQ-923", "Ruled: J.P. morgan&stanley", None),
    ("DQ-924", "Ruled: J.P. mary-morgan", None),
    ("DQ-925", "Ruled: J.P. stanley-mary", None),
    ("DQ-926", "Ruled: J.P. morgan-stanley.", None),
    ("DQ-927", "Ruled: Captain J.P. morgan-stanley", None),
    ("DQ-928", "Settled: Cap tain mary-morgan", SETTLED_DECIDER),
    ("DQ-929", "Ruled: J.P. morgan-stanley morgan-stanley "
              "morgan-stanley", None),
    ("DQ-930", "Ruled: J.P. morgan-stanley mary", None),
    ("DQ-931", "Ruled: J.P. Mor gan-stanley", None),
)


JOINED_ELEMENT_FORMS = (
    ("DQ-940", "Ruled:\tJ.P. morgan-stanley", None),
    ("DQ-941", "Ruled:\tCap tain morgan-stanley", None),
    ("DQ-942", "Settled:\tJ.P. morgan-stanley", SETTLED_DECIDER),
    ("DQ-943", "Ruled:\tJ.P. morgan/stanley", None),
    ("DQ-944", "```\nRuled: J.P. morgan-stanley\n```", None),
    ("DQ-945", "> Ruled: J.P. morgan-stanley", None),
    ("DQ-946", "The meeting ended at noon. "
              "Ruled: J.P. morgan-stanley", None),
    ("DQ-947", "```\nRuled: J.P. mary-morgan\n```", None),
    ("DQ-948", "> Ruled: Cap tain stanley-mary", None),
)


COMBINED_LABELLED_FORMS = (
    ("DQ-950", "Ruled: Ca.p tain JP", None),
    ("DQ-951", "Ruled: Cap t.ain JP", None),
    ("DQ-952", "Ruled: C.ap tain JP", None),
    ("DQ-953", "Ruled: Ma.n ager decided.", None),
    ("DQ-954", "Ruled: the Ma.n ager decided.", None),
    ("DQ-955", "Ruled: Gr.a nt", None),
)


COMBINED_ELEMENT_FORMS = (
    ("DQ-960", "Ruled:\tCa.p tain JP", None),
    ("DQ-961", "Ruled:\tMa.n ager decided.", None),
    ("DQ-962", "Ruled:\tGr.a nt", None),
    ("DQ-963", "```\nRuled: Ca.p tain JP\n```", None),
    ("DQ-964", "> Ruled: Ca.p tain JP", None),
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


class JoinedLabelledFormTest(_FormAssert, unittest.TestCase):
    """A8-3-1 and A8-8-1 part (a) in the labelled paragraph
    block: a name written as two or three evidenced name
    words joined by punctuation inside one lowercase word,
    beside a fragmented or spaced attribution anchor,
    records no ruling text."""

    def test_hyphen_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[0])

    def test_hyphen_pair_reversed_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[1])

    def test_hyphen_pair_mary_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[2])

    def test_full_stop_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[3])

    def test_slash_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[4])

    def test_underscore_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[5])

    def test_comma_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[6])

    def test_hyphen_triple_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[7])

    def test_mixed_case_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[8])

    def test_hyphen_pair_beside_spaced_attribution(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[9])

    def test_hyphen_pair_beside_spaced_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[10])

    def test_settled_hyphen_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[11])

    def test_plus_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[12])

    def test_ampersand_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[13])

    def test_mary_first_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[14])

    def test_stanley_mary_pair_beside_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[15])

    def test_hyphen_pair_with_closing_stop(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[16])

    def test_hyphen_pair_beside_whole_captain_and_initials(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[17])

    def test_settled_mary_pair_beside_spaced_attribution(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[18])

    def test_tripled_stuffing_form(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[19])

    def test_joined_pair_before_further_name_word(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[20])

    def test_hybrid_spaced_and_joined_surname(self):
        self._assert_one_error(*JOINED_LABELLED_FORMS[21])


class JoinedElementFormTest(_FormAssert, unittest.TestCase):
    """The merged construction in the element limb: the
    same joined name matters in the tab, fenced,
    blockquoted and prose spellings parse classifies as a
    closing prose element record no ruling text through
    that limb either."""

    def test_tab_hyphen_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[0])

    def test_tab_pair_beside_spaced_attribution(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[1])

    def test_tab_settled_hyphen_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[2])

    def test_tab_slash_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[3])

    def test_fenced_hyphen_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[4])

    def test_blockquote_hyphen_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[5])

    def test_prose_hyphen_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[6])

    def test_fenced_mary_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[7])

    def test_blockquote_stanley_mary_pair(self):
        self._assert_one_error(*JOINED_ELEMENT_FORMS[8])


class CombinedLabelledFormTest(_FormAssert, unittest.TestCase):
    """A8-8-1 part (b) in the labelled paragraph block: an
    attribution split by punctuation inside the word and
    by a space together stands on attribution fragments
    alone and records no ruling text."""

    def test_captain_split_after_first_syllable(self):
        self._assert_one_error(*COMBINED_LABELLED_FORMS[0])

    def test_captain_split_inside_second_word(self):
        self._assert_one_error(*COMBINED_LABELLED_FORMS[1])

    def test_captain_split_after_first_letter(self):
        self._assert_one_error(*COMBINED_LABELLED_FORMS[2])

    def test_manager_split_combined(self):
        self._assert_one_error(*COMBINED_LABELLED_FORMS[3])

    def test_manager_split_combined_after_article(self):
        self._assert_one_error(*COMBINED_LABELLED_FORMS[4])

    def test_grant_split_combined(self):
        self._assert_one_error(*COMBINED_LABELLED_FORMS[5])


class CombinedElementFormTest(_FormAssert, unittest.TestCase):
    """A8-8-1 part (b) in the element limb: the same
    combined split attributions in the tab, fenced and
    blockquoted spellings record no ruling text through
    that limb either."""

    def test_tab_captain_split_combined(self):
        self._assert_one_error(*COMBINED_ELEMENT_FORMS[0])

    def test_tab_manager_split_combined(self):
        self._assert_one_error(*COMBINED_ELEMENT_FORMS[1])

    def test_tab_grant_split_combined(self):
        self._assert_one_error(*COMBINED_ELEMENT_FORMS[2])

    def test_fenced_captain_split_combined(self):
        self._assert_one_error(*COMBINED_ELEMENT_FORMS[3])

    def test_blockquote_captain_split_combined(self):
        self._assert_one_error(*COMBINED_ELEMENT_FORMS[4])


class ControlFormTest(_FormAssert, unittest.TestCase):
    """The controls the round 8 papers fix: the capitalised
    joined forms and the single split name token already
    take exactly one Error and keep doing so."""

    def test_capitalised_joined_pair_keeps_the_error(self):
        self._assert_one_error(
            "DQ-970", "Ruled: J.P. Morgan-Stanley", None)

    def test_capitalised_first_joined_pair_keeps_the_error(self):
        self._assert_one_error(
            "DQ-971", "Ruled: J.P. Morgan-stanley", None)

    def test_single_split_name_token_keeps_the_error(self):
        self._assert_one_error(
            "DQ-972", "Ruled: J.P. mor-gan", None)


class GuardFormTest(_FormAssert, unittest.TestCase):
    """The standing bounds keep their passes: genuine
    ruling matter beside an anchor passes, a person name
    with no fragmented or spaced attribution word beside
    it passes, one thin lowercase word beside fragmented
    initials passes, and the separator free concatenation
    form passes inside Fix Seat V's stated bound edge 4,
    this cure not reaching it."""

    def test_genuine_matter_after_joined_pair_still_passes(self):
        self._assert_no_error(
            "DQ-980", "Ruled: J.P. morgan-stanley takes the harbour.")

    def test_genuine_matter_after_combined_split_still_passes(self):
        self._assert_no_error(
            "DQ-981", "Ruled: Ca.p tain JP takes the harbour.")

    def test_genuine_matter_after_manager_split_still_passes(self):
        self._assert_no_error(
            "DQ-982", "Ruled: Ma.n ager decided the harbour form stands.")

    def test_name_alone_still_passes(self):
        self._assert_no_error("DQ-983", "Ruled: Alice")

    def test_two_word_name_alone_still_passes(self):
        self._assert_no_error("DQ-984", "Ruled: Morgan Stanley")

    def test_name_beside_whole_attribution_still_passes(self):
        self._assert_no_error("DQ-985", "Ruled: Captain JP Morgan")

    def test_one_thin_lowercase_word_beside_initials_still_passes(self):
        self._assert_no_error("DQ-986", "Ruled: J.P. harbour")

    def test_unevidenced_lowercase_word_beside_initials_still_passes(self):
        self._assert_no_error("DQ-987", "Ruled: J.P. smith")

    def test_separator_free_concatenation_still_passes(self):
        self._assert_no_error("DQ-988", "Ruled: J.P. morganstanley")

    def test_genuine_lowercase_words_beside_initials_still_pass(self):
        self._assert_no_error("DQ-989", "Ruled: J.P. checker note")

    def test_hyphenated_genuine_word_still_passes(self):
        self._assert_no_error("DQ-990", "Ruled: har-bour.")

    def test_number_alone_still_passes(self):
        self._assert_no_error("DQ-991", "Ruled: 42.")


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
        self.assertEqual(_rule5_findings(output, "DQ-902"), [])
        self.assertEqual(h.findings_of(output), [])

    def test_closing_prose_form_still_passes(self):
        _model, output = h.run_pipeline(
            CLOSING_PROSE_FORM, name="probe.md")
        self.assertEqual(_rule5_findings(output, "DQ-903"), [])


if __name__ == "__main__":
    unittest.main()
