"""Step 17 (restart) fix wave 8, Fix Seat K13 tests.

Charge CH-189 (Medium), ruled TO FIX at record section 77
ruling (d) of design/steps/step-17r-record.md, from round 8
attack seat 3 observation O-2 at
design/steps/step-17r-attack8-3.md: a fence standing
unclosed inside a Banked entry body takes a tool fault at
exit 4 on both subcommands, the tool own counts do not sum
(the Banked head evidence groups sum to 0 against a Banked
head population of 1), and the summary is withheld in full.
The bounding probes beside the finding case show the fault
fires identically where no join and no heading stands
anywhere, and the mechanism stands in the fence reading and
the Banked head evidence footing, not in the CH-96 split
scan.

The charged constructions are the attack paper own forms,
built byte for byte from its one entry base (sha256 head
4ce5bc382415): s24 (a fence closing line carrying a join
and a heading part), s27 (the closing line joined to plain
prose), s28 (the closing line carrying a heading part
behind a plain space, no join character), and s29 (the
fence simply standing unclosed, no closing line and no
heading anywhere). In each form the entry body carries the
opening line of a fence that never closes, so the genuine
paragraph behind the opener stands inside the fence and
takes no evidence group credit, while the entry itself is
whole and parsed.

The cure bound, stated in the open: an entry whose own
body carries the opening line of a fence that stands open
at the end of its body, and that takes no evidence group,
stands outside the Banked head population, on the footing
bound the cut entry bound already states in the same
reading. An entry that takes a group keeps its population
and group standing exactly as before.

F1 bounds, stated expressly where they arise, as the
charge requires. The F1 shape (a Banked head entry whose
body carries no later Status line, no level 4 decision
block, and no unheaded paragraph, only the labelled
fields) stands in neither direction under this cure: the
plain F1 form and the closed fence form whose only
paragraph stands inside a properly closed fence both keep
their standing tool fault at exit 4, pinned below in both
directions. A following entry whose body stands wholly
inside a fence opened in an earlier entry body is also
bounded expressly: the opening line stands outside its own
body, so this cure does not reach it and its footing fault
stands, pinned below.

Copyright: J.P. Picard aka Macro-Harder
"""

import tempfile
import unittest
from pathlib import Path

import dqv_harness as h

LS = "\u2028"

BASE = (
    "# Decision queue\n\n"
    "### DQ-001: A sample open question\n\n"
    "Status: Banked\n\n"
    "Question: Which option should we take?\n\n"
    "Options: Option A, Option B\n\n"
    "Cost of deciding late: Work stays blocked.\n\n"
    "Blocks: DQ-002\n\n"
    "This question is waiting for a decision.\n"
)

TAIL = "This question is waiting for a decision.\n"

S24 = BASE.replace(
    TAIL,
    "Example:\n\n```\ncode\n```" + LS
    + "### DQ-002: Example heading\n\n" + TAIL)
S27 = BASE.replace(
    TAIL,
    "Example:\n\n```\ncode\n```" + LS + "plain text\n\n" + TAIL)
S28 = BASE.replace(
    TAIL,
    "Example:\n\n```\ncode\n``` ### DQ-002: Example heading\n\n"
    + TAIL)
S29 = BASE.replace(
    TAIL, "Example:\n\n```\ncode\n\n" + TAIL)
S29_TILDE = BASE.replace(
    TAIL, "Example:\n\n~~~\ncode\n\n" + TAIL)
S29_INFO = BASE.replace(
    TAIL, "Example:\n\n```text\ncode\n\n" + TAIL)

CLOSED_FENCE_PARA_AFTER = BASE.replace(
    TAIL, "Example:\n\n```\ncode\n```\n\n" + TAIL)
CLOSED_FENCE_NO_PARA = BASE.replace(
    TAIL, "Example:\n\n```\ncode\n\n" + TAIL + "```\n")
PARA_BEFORE_UNCLOSED = BASE.replace(
    TAIL, TAIL + "\nExample:\n\n```\ncode\n")
LATER_STATUS_UNCLOSED = BASE.replace(
    "Blocks: DQ-002\n",
    "Blocks: DQ-002\n\nStatus: Banked\n").replace(
    TAIL, "Example:\n\n```\ncode\n\n" + TAIL)
F1_PLAIN = BASE.replace("\n" + TAIL, "\n")
OPEN_UNCLOSED = BASE.replace("Status: Banked", "Status: Open").replace(
    TAIL, "Example:\n\n```\ncode\n\n" + TAIL)
SWALLOWED_SECOND = (
    BASE.replace(
        TAIL, "Example:\n\n```\ncode\n\n" + TAIL)
    + "\n### DQ-002: Second question\n\n"
    + "Status: Banked\n\n"
    + "Question: Which other option should we take?\n\n"
    + "Options: Option C, Option D\n\n"
    + "Cost of deciding late: More work stays blocked.\n\n"
    + "Blocks: DQ-001\n\n"
    + "This question is also waiting for a decision.\n")

FOOTING_LINE = ("the Banked head evidence groups sum to 0 "
                "against a Banked head population of 1")


def _cli(data, subcommand):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "queue.md"
        target.write_bytes(data.encode("utf-8"))
        code, out, err = h.run_cli(subcommand, target)
    return code, (out + err).decode("utf-8", errors="replace")


def _pipeline(data):
    return h.run_pipeline(data.encode("utf-8"), "queue.md")


def _group_rows(output):
    rows = []
    for row in getattr(output, "census", None) or []:
        name = getattr(row, "class_name", "") or ""
        if name.startswith("Banked head evidence group:"):
            rows.append((name, row.count,
                         list(row.member_entry_ids or [])))
    return rows


def _sums_agree(output):
    rec = getattr(output, "reconciliation", None)
    check = getattr(rec, "self_check", None)
    return getattr(check, "sums_agree", None)


class Ch189UnclosedFenceFootingTest(unittest.TestCase):

    def test_base_control_stands_clean(self):
        for sub in ("validate", "render"):
            code, combined = _cli(BASE, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)
        _model, output = _pipeline(BASE)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(
            _group_rows(output),
            [("Banked head evidence group: unheaded paragraphs "
              "only", 1, ["DQ-001"])])

    def test_s24_closing_line_join_heading(self):
        for sub in ("validate", "render"):
            code, combined = _cli(S24, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)
            self.assertNotIn(FOOTING_LINE, combined)
        _model, output = _pipeline(S24)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(_group_rows(output), [])

    def test_s27_closing_line_join_prose(self):
        for sub in ("validate", "render"):
            code, combined = _cli(S27, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)
            self.assertNotIn(FOOTING_LINE, combined)
        _model, output = _pipeline(S27)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(_group_rows(output), [])

    def test_s28_closing_line_space_heading(self):
        for sub in ("validate", "render"):
            code, combined = _cli(S28, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)
            self.assertNotIn(FOOTING_LINE, combined)
        _model, output = _pipeline(S28)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(_group_rows(output), [])

    def test_s29_fence_unclosed_plain(self):
        for sub in ("validate", "render"):
            code, combined = _cli(S29, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)
            self.assertNotIn(FOOTING_LINE, combined)
        _model, output = _pipeline(S29)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(_group_rows(output), [])
        findings = [(f.rule_id, f.severity)
                    for f in getattr(output, "findings", None) or []]
        self.assertEqual(findings, [("PD-R7", "Note")])

    def test_s29_tilde_fence_unclosed(self):
        for sub in ("validate", "render"):
            code, combined = _cli(S29_TILDE, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)
        _model, output = _pipeline(S29_TILDE)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(_group_rows(output), [])

    def test_s29_info_string_fence_unclosed(self):
        for sub in ("validate", "render"):
            code, combined = _cli(S29_INFO, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)
        _model, output = _pipeline(S29_INFO)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(_group_rows(output), [])

    def test_paragraph_before_unclosed_fence_keeps_group(self):
        _model, output = _pipeline(PARA_BEFORE_UNCLOSED)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(
            _group_rows(output),
            [("Banked head evidence group: unheaded paragraphs "
              "only", 1, ["DQ-001"])])
        for sub in ("validate", "render"):
            code, combined = _cli(PARA_BEFORE_UNCLOSED, sub)
            self.assertEqual(code, 0, sub)
            self.assertNotIn("Tool fault", combined)

    def test_later_status_before_unclosed_fence_keeps_group(self):
        _model, output = _pipeline(LATER_STATUS_UNCLOSED)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(
            _group_rows(output),
            [("Banked head evidence group: later Status line in "
              "the body", 1, ["DQ-001"])])

    def test_closed_fence_paragraph_after_keeps_group(self):
        _model, output = _pipeline(CLOSED_FENCE_PARA_AFTER)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(
            _group_rows(output),
            [("Banked head evidence group: unheaded paragraphs "
              "only", 1, ["DQ-001"])])
        for sub in ("validate", "render"):
            code, _combined = _cli(CLOSED_FENCE_PARA_AFTER, sub)
            self.assertEqual(code, 0, sub)

    def test_open_entry_unclosed_fence_unaffected(self):
        _model, output = _pipeline(OPEN_UNCLOSED)
        self.assertTrue(_sums_agree(output))
        self.assertEqual(_group_rows(output), [])
        for sub in ("validate", "render"):
            code, combined = _cli(OPEN_UNCLOSED, sub)
            self.assertNotIn("Tool fault", combined)
            self.assertNotEqual(code, 4, sub)


class Ch189F1BoundTest(unittest.TestCase):
    """The F1 adjacent forms this cure touches, bounded
    expressly: each stands in its standing posture before
    and after the cure, and the cure settles none of them."""

    def test_f1_plain_form_stands_unchanged(self):
        # The F1 shape itself: labelled fields only, no
        # fence anywhere. Bounded expressly: not settled
        # in either direction by this cure.
        for sub in ("validate", "render"):
            code, combined = _cli(F1_PLAIN, sub)
            self.assertEqual(code, 4, sub)
            self.assertIn(FOOTING_LINE, combined)

    def test_closed_fence_no_outside_paragraph_stands(self):
        # F1 adjacent: the only paragraph stands inside a
        # properly closed fence, so no fence stands open at
        # the end of the body. Bounded expressly: not
        # settled in either direction by this cure.
        for sub in ("validate", "render"):
            code, combined = _cli(CLOSED_FENCE_NO_PARA, sub)
            self.assertEqual(code, 4, sub)
            self.assertIn(FOOTING_LINE, combined)

    def test_swallowed_following_entry_stands(self):
        # F1 adjacent: the second entry body stands wholly
        # inside a fence opened in the first entry body, so
        # the opening line stands outside its own body and
        # this cure does not reach it. Bounded expressly:
        # its footing fault stands, at the population the
        # first entry exclusion leaves.
        for sub in ("validate", "render"):
            code, combined = _cli(SWALLOWED_SECOND, sub)
            self.assertEqual(code, 4, sub)
            self.assertIn("Tool fault", combined)
            self.assertIn("the Banked head evidence groups sum "
                          "to 0 against a Banked head population",
                          combined)


if __name__ == "__main__":
    unittest.main()
