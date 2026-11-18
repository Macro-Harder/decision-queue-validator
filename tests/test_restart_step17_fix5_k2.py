"""Step 17 fix wave 5, Fix Seat K2 tests, test first.

Charges CH-77, CH-78, and CH-79, as ruled at section 52 of
design/steps/step-17r-record.md, ruling (a) especially, and
prepared at design/steps/step-17r-triage5-prep.md. The run
ground is restated once there and governs the whole cluster:
a character stands in the run ground when it presents no
visible glyph: the categories Cn, Co, Cf, Cc (the governed
terminators excepted), Zs, Zl, Zp, Mn, Mc, and Me, together
with any character, in any category, whose Unicode name
carries BLANK, FILLER, FILL, or REPLACEMENT. The private use
class Co stands inside the ground at every surface, decided
expressly. CH-77 carries seat 3 findings A5-3-F1 (High),
A5-3-F2 (Medium), and A5-3-F4 (Low), and seat 19 findings
F1 and F2 (Low). CH-78 carries seat 3 findings A5-3-F3
(Medium) and A5-3-F5 (Low). CH-79 carries seat 17 findings
S17-ATK5-17-01, S17-ATK5-17-02, and S17-ATK5-17-03 (Low).
The governing pins stand whole: the ruling (d) and ruling
(e) pin sets, the fix wave 4 K2 pins (CH-54, CH-55, CH-56),
and the pins the preparation names for these charges. The
plain spaces separator guard (design question note (f)
ground) stands as a guard below, passing before and after.
"""

import unittest

import dqv_harness as h


def _elements(model, entry_id="DQ-001"):
    entry = h.entry_by_id(model, entry_id)
    if entry is None:
        return []
    return h.as_list(h.get(entry, "status_elements", "elements"))


def _kinds(model, entry_id="DQ-001"):
    return [(h.text_of(h.get(el, "kind", "element_kind")) or "")
            for el in _elements(model, entry_id)]


def _dispositions(model, entry_id="DQ-001"):
    out = []
    for el in _elements(model, entry_id):
        tup = h.get(el, "tuple", "element_tuple", "core_tuple")
        out.append(h.text_of(tuple(tup)[0]) if tup is not None
                   else h.text_of(h.get(el, "disposition")))
    return out


def _entry(status_line, first_paragraph=None):
    body = h._header_block()
    body += "### DQ-001: A sample open question\n\n"
    if first_paragraph is not None:
        body += first_paragraph + "\n\n"
    body += status_line
    if not status_line.endswith("\n"):
        body += "\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n"
    return body.encode("utf-8")


def _two_entry_file(prefix, first_prefix=""):
    body = h._header_block()
    body += first_prefix + "### DQ-001: First question\n\n"
    body += "Status: Banked\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += prefix + "### DQ-002: Second question\n\n"
    body += "Status: Banked\n\n"
    body += "Question: Which other option should we take?\n\n"
    body += "Options: Option C, Option D\n\n"
    body += "Cost of deciding late: More work stays blocked.\n\n"
    body += "Blocks: DQ-001\n\n"
    body += "This question is also waiting for a decision.\n"
    return body.encode("utf-8")


def _twin_file(prefix):
    one = ("### DQ-001: Same question\n\n"
           "Status: Banked\n\n"
           "Question: Which option should we take?\n\n"
           "Options: Option A, Option B\n\n"
           "Cost of deciding late: Work stays blocked.\n\n"
           "Blocks: DQ-002\n\n"
           "This question is waiting for a decision.\n\n")
    two = one.replace("DQ-001", "DQ-002").replace(
        "Blocks: DQ-002", "Blocks: DQ-001")
    return (h._header_block() + one + prefix + two).encode("utf-8")


def _cr_tail_file(tail_parts):
    body = h._header_block()
    body += "### DQ-001: A sample open question"
    for part in tail_parts:
        body += "\r" + part
    body += "\n\nQuestion: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n"
    return body.encode("utf-8")


def _joined_file(joiner):
    body = h._header_block()
    body += "### DQ-001: A sample open question" + joiner
    body += "Status: Banked\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n\n"
    body += "This question is waiting for a decision.\n"
    return body.encode("utf-8")


def _preamble_file(prefix, status_line="Status: Parked"):
    body = "# Decision queue\n\n"
    body += prefix + status_line + "\n\n"
    body += "Generated queue shaped input.\n\n"
    body += "### DQ-001: A sample open question\n\n"
    body += "Status: Banked\n\n"
    body += "This question is waiting for a decision.\n\n"
    body += "Question: Which option should we take?\n\n"
    body += "Options: Option A, Option B\n\n"
    body += "Cost of deciding late: Work stays blocked.\n\n"
    body += "Blocks: DQ-002\n"
    return body.encode("utf-8")


# The round 5 ground members outside the ruling (e) classes:
# unassigned characters (Cn), private use characters (Co),
# and characters in any category whose name carries one of
# the ruling (a) words (a braille pattern blank, So, BLANK;
# a hangul filler, Lo, FILLER; an object replacement
# character, So, REPLACEMENT; gap fillers, Po, FILLER; an
# ideographic half fill space, So, FILL).
CN_CHARS = ("\u0378", "\ufffe", "\ufdd0", "\uffff", "\u2065")
CO_CHARS = ("\ue000", "\uf8ff")
NAME_CHARS = ("\u2800", "\u3164", "\ufffc")
GAP_FILLER_CHARS = ("\ua8f9", "\U0001144e", "\U00011945", "\u303f")


class Ch77HeadingGroundTest(unittest.TestCase):
    """CH-77, A5-3-F1 (High): heading recognition reads the
    heading after a leading run on the ruling (a) ground."""

    def test_ch77_heading_prefix_cn_co_characters(self):
        for char in CN_CHARS + CO_CHARS:
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _two_entry_file(char), "ch77_heading.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(
                    h.entry_by_id(model, "DQ-002"))
                self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch77_heading_prefix_name_characters(self):
        for char in NAME_CHARS:
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _two_entry_file(char), "ch77_heading_name.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIsNotNone(
                    h.entry_by_id(model, "DQ-002"))
                self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch77_heading_prefix_sandwich_run(self):
        model = h.run_parse(
            _two_entry_file("\ufeff\u0378\ufeff"),
            "ch77_sandwich.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-002"))
        self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch77_heading_prefix_before_first_entry(self):
        model = h.run_parse(
            _two_entry_file("", first_prefix="\u0378"),
            "ch77_first.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIsNotNone(h.entry_by_id(model, "DQ-001"))
        self.assertEqual(len(h.entries_of(model)), 2)

    def test_ch77_heading_prefix_identical_twin(self):
        model = h.run_parse(
            _twin_file("\u0378"), "ch77_twin.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertEqual(len(h.entries_of(model)), 2)


class Ch77CrTailGroundTest(unittest.TestCase):
    """CH-77, A5-3-F2 (Medium): the carriage return tail
    selection reads its parts on the same ground."""

    def test_ch77_cr_tail_behind_cn_co_is_counted(self):
        for char in ("\u0378", "\ue000"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _cr_tail_file([char + "Status: Banked"]),
                    "ch77_cr_tail.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn("Banked", _dispositions(model))
                self.assertIn(
                    "line start Status line", _kinds(model))

    def test_ch77_cr_tail_behind_sandwich_run_is_counted(self):
        model = h.run_parse(
            _cr_tail_file(["\ufeff\u0378Status: Banked"]),
            "ch77_cr_sandwich.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertIn("line start Status line", _kinds(model))

    def test_ch77_cr_tail_second_part_behind_cn(self):
        model = h.run_parse(
            _cr_tail_file(["Status: Banked",
                           "\u0378Status: Ruled"]),
            "ch77_cr_two.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertIn("Ruled", _dispositions(model))
        kinds = _kinds(model)
        self.assertEqual(
            kinds.count("line start Status line")
            + kinds.count("later Status line"), 2)

    def test_ch77_cr_tail_behind_name_characters_takes_signal(self):
        # The blank presenting tail parts take the near marker
        # report they take at body position (the held p12 and
        # p13 forms), instead of erasing the occurrence in
        # silence.
        for char in ("\u2800", "\u3164"):
            with self.subTest(char=repr(char)):
                model, output = h.run_pipeline(
                    _cr_tail_file([char + "Status: Banked"]),
                    "ch77_cr_blank.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))


class Ch77StatusLeadingGroundTest(unittest.TestCase):
    """CH-77, A5-3-F4 (Low) and seat 19 F1 (Low): the Status
    leading run at the entry surface, on the ruling (a)
    ground."""

    def test_ch77_entry_status_leading_cn_co_characters(self):
        for char in CN_CHARS + CO_CHARS:
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _entry(char + "Status: Banked\n"),
                    "ch77_status.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_ch77_entry_status_leading_mixed_runs(self):
        for prefix in ("\ue000 ", " \ue000", "\ue000\x0b",
                       "\u0378 ", "\u2065\ufeff"):
            with self.subTest(prefix=repr(prefix)):
                model = h.run_parse(
                    _entry(prefix + "Status: Banked\n"),
                    "ch77_mixed.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))
                self.assertIn("Banked", _dispositions(model))

    def test_ch77_entry_status_leading_gap_fillers_take_signal(self):
        # Characters the ruling (a) name limb admits (gap
        # fillers in category Po, the half fill space in So)
        # take the near marker report the blank presenting
        # forms take, instead of a silent demotion.
        for char in GAP_FILLER_CHARS:
            with self.subTest(char=repr(char)):
                model, output = h.run_pipeline(
                    _entry(char + "Status: Banked\n"),
                    "ch77_gap.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn(
                    "line start Status line", _kinds(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch77_entry_status_leading_gap_filler_mixed_run(self):
        model, output = h.run_pipeline(
            _entry("\ua8f9 Status: Banked\n"), "ch77_gap_mixed.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("line start Status line", _kinds(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_ch77_variant_marker_behind_cn_co(self):
        for char in ("\u0378", "\ue000"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _entry(char + "Status unchanged: Banked\n"),
                    "ch77_variant.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn("variant phrasing", _kinds(model))

    def test_ch77_cn_co_before_no_space_separator(self):
        # Seat 19 combination limb: the damaged separator
        # behind a ground character takes the near marker
        # signal, as it does behind an admitted class run.
        for char in ("\u0378", "\ue000", "\ua8f9"):
            with self.subTest(char=repr(char)):
                model, output = h.run_pipeline(
                    _entry(char + "Status:Banked\n"),
                    "ch77_nospace.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch77_co_before_empty_value(self):
        model, output = h.run_pipeline(
            _entry("\ue000Status:\n"), "ch77_empty.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_ch77_co_before_tab_separator(self):
        model, output = h.run_pipeline(
            _entry("\ue000Status:\tBanked\n"), "ch77_tab.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))


class Ch77PreambleGroundTest(unittest.TestCase):
    """CH-77, seat 19 F2 (Low): a preamble Status line behind
    a ground character takes the rule 2 preamble finding."""

    def test_ch77_preamble_leading_ground_characters(self):
        for char in ("\u0378", "\ue000", "\uf8ff", "\ufffe",
                     "\ua8f9", "\u303f", "\u2800"):
            with self.subTest(char=repr(char)):
                _model, output = h.run_pipeline(
                    _preamble_file(char), "ch77_preamble.md")
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch77_preamble_ground_character_tab_separator(self):
        for char in ("\ue000", "\u0378"):
            with self.subTest(char=repr(char)):
                _model, output = h.run_pipeline(
                    _preamble_file(char, "Status:\tParked"),
                    "ch77_preamble_tab.md")
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))


class Ch78SeparatorJoinTest(unittest.TestCase):
    """CH-78, A5-3-F3 (Medium): a separator character joining
    the heading line to its Status line."""

    def test_ch78_heading_joined_to_status_by_separator(self):
        for joiner in ("\u2028", "\u2029", "\u0085", "\x0b",
                       "\x0c"):
            with self.subTest(joiner=repr(joiner)):
                model = h.run_parse(
                    _joined_file(joiner), "ch78_join.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn("Banked", _dispositions(model))
                self.assertIn(
                    "line start Status line", _kinds(model))

    def test_ch78_separator_trailing_on_heading_line_pin(self):
        # Pin, the paper held form: a separator character
        # trailing on the heading line, with the Status line
        # on its own line after it, stands as it stood.
        body = h._header_block()
        body += "### DQ-001: A sample open question\u2028\n\n"
        body += "Status: Banked\n\n"
        body += "Question: Which option should we take?\n\n"
        body += "Options: Option A, Option B\n\n"
        body += "Cost of deciding late: Work stays blocked.\n\n"
        body += "Blocks: DQ-002\n"
        model = h.run_parse(body.encode("utf-8"), "ch78_trail.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertIn("line start Status line", _kinds(model))
        self.assertIn("Banked", _dispositions(model))


class Ch78DamagedTailMarkerTest(unittest.TestCase):
    """CH-78, A5-3-F5 (Low): a damaged marker inside a
    carriage return tail takes a signal."""

    def test_ch78_cr_tail_damaged_marker_takes_signal(self):
        model, output = h.run_pipeline(
            _cr_tail_file(["Sta\u0378tus: Banked"]),
            "ch78_damaged.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))


class Ch79SeparatorRunGroundTest(unittest.TestCase):
    """CH-79, S17-ATK5-17-01 (Low): a separator run of plain
    spaces followed by one ground character, or by the null
    notehead, folds nothing into the Status value in silence,
    at line start and in the embedded only position alike."""

    def test_ch79_line_start_separator_ground_characters(self):
        forms = (
            "Status: \u2065Banked\n",
            "Status: \ue000Banked\n",
            "Status: \U0001d159Banked\n",
            "Status:  \u2065Banked\n",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry(form), "ch79_sep.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_ch79_embedded_separator_ground_characters(self):
        forms = (
            "Closing prose stands here. Status: \u2065Banked",
            "Closing prose stands here. Status:\u2065Banked",
            "Closing prose stands here. Status: \ue000Banked",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry("", first_paragraph=form),
                    "ch79_embedded.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))


class Ch79LeadingGroundTest(unittest.TestCase):
    """CH-79, S17-ATK5-17-02 (Low): the null notehead in the
    leading position takes the near marker report instead of
    a silent demotion. The Cn and Co members of this finding
    stand at the CH-77 entry Status tests above."""

    def test_ch79_leading_null_notehead_takes_signal(self):
        model, output = h.run_pipeline(
            _entry("\U0001d159Status: Banked\n"), "ch79_lead.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("line start Status line", _kinds(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))


class Ch79LabelCleaningGroundTest(unittest.TestCase):
    """CH-79, S17-ATK5-17-03 (Low): a Status label carrying
    one ground character inside the label or before its colon
    takes the near marker report, so no Ambiguous stands
    without a finding on those forms."""

    def test_ch79_ground_character_inside_label_takes_near(self):
        forms = (
            "Stat\u2800us: Banked\n",
            "Status\u2800: Banked\n",
            "Stat\ue000us: Banked\n",
        )
        for form in forms:
            with self.subTest(form=repr(form)):
                model, output = h.run_pipeline(
                    _entry(form), "ch79_label.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn(
                    "line start Status line", _kinds(model))
                self.assertNotIn("Banked", _dispositions(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))


class K2PinHoldTest(unittest.TestCase):
    """Governing pins of the earlier waves on this surface,
    standing whole under the restated ground."""

    def test_pin_ruling_d_heading_characters(self):
        for char in ("\u00a0", "\u200b", "\x0b", "\x0c",
                     "\u200c", "\u2060", "\u2028", "\u0085",
                     "\u0301"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _two_entry_file(char), "pin_heading.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertEqual(len(h.entries_of(model)), 2)

    def test_pin_class_status_leading_characters(self):
        for char in ("\u2029", "\u200e", "\u0000", "\u061c",
                     "\u0086"):
            with self.subTest(char=repr(char)):
                model = h.run_parse(
                    _entry(char + "Status: Banked\n"),
                    "pin_status.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertIn(
                    "line start Status line", _kinds(model))

    def test_pin_blank_presenting_leading_takes_signal(self):
        for char in ("\u2800", "\u3164", "\u115f"):
            with self.subTest(char=repr(char)):
                model, output = h.run_pipeline(
                    _entry(char + "Status: Banked\n"),
                    "pin_blank_lead.md")
                self.assertFalse(h.is_failure_result(model))
                self.assertNotIn(
                    "line start Status line", _kinds(model))
                self.assertTrue(h.findings_for(
                    output, rule=2, severity="Warning"))

    def test_pin_separator_blank_presenting_takes_near(self):
        model, output = h.run_pipeline(
            _entry("Status: \u2800Banked\n"), "pin_sep_blank.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_pin_invisible_inside_label_takes_near(self):
        model, output = h.run_pipeline(
            _entry("Stat\u200bus: Banked\n"), "pin_label.md")
        self.assertFalse(h.is_failure_result(model))
        self.assertNotIn("Banked", _dispositions(model))
        self.assertTrue(h.findings_for(
            output, rule=2, severity="Warning"))

    def test_pin_plain_spaces_separator_guard(self):
        # Guard, design question note (f) ground, not charged:
        # a run of plain spaces alone still extracts in
        # silence, as pinned. Passes before and after.
        model, output = h.run_pipeline(
            _entry("Status:  Banked\n"), "pin_guard.md")
        self.assertIn("line start Status line", _kinds(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertEqual(h.findings_for(output, rule=2), [])

    def test_pin_embedded_plain_form_still_extracts(self):
        model, output = h.run_pipeline(
            _entry("", first_paragraph=(
                "Closing prose stands here. Status: Banked")),
            "pin_embedded_plain.md")
        self.assertIn("tail paragraph element", _kinds(model))
        self.assertIn("Banked", _dispositions(model))
        self.assertEqual(h.findings_for(output, rule=2), [])


if __name__ == "__main__":
    unittest.main()
