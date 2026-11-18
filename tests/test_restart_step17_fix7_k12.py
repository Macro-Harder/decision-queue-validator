"""Restart Step 17 fix wave 7, Seat K12 tests.

Charges CH-150, CH-151, and CH-152, as ruled at section 66
of design/steps/step-17r-record.md, with ruling (f) on the
cost charges and ruling (g) on the residue carry discharge.
The three charges stand in validate.py: the findings
assembly and the model cost loci.

CH-150 (seat 5 A7-5-1, Medium, a cost finding): the file
findings sort key encodes the whole evidence line and the
whole statement of every finding it keys, and a sort holds
every key at once, so many citation lines in one file level
note segment pay a transient peak memory at the product of
the cited token count and the line length, on both
subcommands, while the printed output stands combined,
correct, and linear. The cure stands at the key: the key
carries the evidence and statement texts themselves, in
the same order the encoded bytes stood in (the UTF-8 byte
order of a text is its code point order), and holds no
encoded copy of either. The order of the sort stands
exactly as governed.

CH-151 (seat 21 A7-21-2, Medium, a cost finding): the
residue list construction loops over every entry for every
appendix row outside the vocabulary mapping, calling the
display identifier reading once per entry per row, so the
scan stands in the square of the entry count where the
phrasings stand distinct. This charge cures the locus of
the K1 residue carry named in the open in the fix wave 6
seat K1 paper. The cure reads each entry once: its display
identifier and its first status element of each phrasing
and kind stand gathered before the row loop, and each row
reads only the entries its member list names. The residue
items, their order, and the residue share stand exactly
as before.

CH-152 (seat 21 A7-21-3, Medium, a cost finding): the
CH-113 walk skip applies only where a recorded cycle
stands pure, so one leaf entry superseding one entry of a
ring makes the recorded cycle impure in the successor
relation and every start of the ring is walked again, at
the quadratic suffix sum cost. The cure widens the skip
at its charged bound: a start is not walked where every
recorded cycle carrying it stands clear, a cycle standing
clear where no edge of a cycle entry that is not the
cycle edge points inside the component at all, so every
further edge leaves the component, can neither be
descended nor close a cycle, and the descent from the
start can do nothing but follow the recorded cycle until
its earliest entry blocks it, recording no cycle. A cycle
carrying any further edge inside the component stands
outside the limb and its starts are walked exactly as
before: the first form of this cure, which also skipped
starts whose cycles carried only edges to earlier file
order entries inside the component, moved the governed
work figures of the wall and detour families, and the
cure stands narrowed to the bound above, as the seat
paper records in the open. On the charged form the work
figure stands at the ring count plus the one examination
the recording descent pays at the leaf edge itself,
where before the cure it stood at the ring count plus
one such examination for every start up to the middle
entry. The inventory, the counts, the refusal figures,
and the PIN-10 counts stand exactly as counted.

Cost and time figures are measurements, stated in the
seat paper, never as pass or fail verdicts here. The
failures before the cure stand on the constructions
themselves: the sort key holding encoded copies, the
display identifier call count on the residue form, and
the work figure on the impure ring form.

Copyright: J.P. Picard aka Macro-Harder
"""

import tracemalloc
import unittest

import dqv_harness as h

validate = h.import_module("validate")
types = h.import_module("types")

_HEADER = "# Decision queue\n\n"
WORK_BOUND = getattr(validate, "_CYCLE_WORK_BOUND", None)


def _run_text(text):
    _model, output = h.run_pipeline(text.encode("utf-8"))
    if output is None:
        raise AssertionError("pipeline returned the failure result")
    return output


def _by_rule(output, rule_text):
    return [f for f in h.findings_of(output)
            if (h.text_of(h.get(f, "rule_id", "rule")) or "")
            == rule_text]


def _cycle_warnings(output):
    return [f for f in _by_rule(output, "PIN-10")
            if h.finding_severity(f) == "Warning"
            and "cycle" in (h.finding_statement(f) or "")]


def _work_measured(output):
    return h.get(output, "cycle_work_measured",
                 "supersession_cycle_work_measured")


def _work_over(output):
    return h.get(output, "cycle_work_over_bound",
                 "supersession_cycle_work_over_bound")


def _count_over(output):
    return h.get(output, "cycle_over_bound",
                 "supersession_cycle_over_bound")


def _simple_entry(number, targets):
    stmt = "This supersedes the ruling at " + " and ".join(
        "DQ-%03d" % t for t in targets) + ".\n"
    return ("### DQ-%03d: Entry %d\nStatus: Banked\n%s\n"
            % (number, number, stmt))


def _dense_text(n, base=0):
    parts = [_HEADER]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            base + i,
            [base + t for t in range(1, n + 1) if t != i]))
    return "".join(parts)


def _bip_text(width):
    parts = [_HEADER]
    n = 2 * width
    odds = [i for i in range(1, n + 1) if i % 2 == 1]
    evens = [i for i in range(1, n + 1) if i % 2 == 0]
    for i in range(1, n + 1):
        parts.append(_simple_entry(
            i, evens if i % 2 == 1 else odds))
    return "".join(parts)


def _wall_text(w, layers):
    per = w + 3

    def sp(lay, k):
        return (lay - 1) * per + k

    def bush(lay, j):
        return (lay - 1) * per + w + j

    sid = layers * per + 1
    tid = layers * per + 2
    edges = {}
    for lay in range(1, layers + 1):
        for k in range(1, w + 1):
            edges[sp(lay, k)] = (
                [sp(lay + 1, k)] if lay < layers else [tid])
        nxt = ([bush(lay + 1, j) for j in (1, 2, 3)]
               if lay < layers else [tid])
        for j in (1, 2, 3):
            edges[bush(lay, j)] = list(nxt)
    edges[tid] = [sid]
    edges[sid] = [bush(1, 1)] + [sp(1, k) for k in range(1, w + 1)]
    parts = [_HEADER]
    for i in range(1, tid + 1):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _detour_text(layers):
    def nid(lay, k):
        return (lay - 1) * 5 + k + 1

    sid = layers * 5 + 1
    tid = layers * 5 + 2
    edges = {}
    for lay in range(1, layers + 1):
        a, b, c, d, e = (nid(lay, k) for k in range(5))
        if lay < layers:
            na, nb, nc, nd, ne = (nid(lay + 1, k) for k in range(5))
            edges[a] = [na]
            edges[b] = [na, nb, nc]
            edges[c] = [na, nb, nc, nd, ne]
            edges[d] = [nb, nc, nd, ne]
            edges[e] = [nb, nc, nd, ne]
        else:
            for node in (a, b, c, d, e):
                edges[node] = [tid]
    edges[tid] = [sid]
    edges[sid] = [nid(1, 2), nid(1, 0), nid(1, 1)]
    parts = [_HEADER]
    for i in range(1, tid + 1):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _ring_text(n, leaf_target=None):
    parts = [_HEADER]
    for i in range(1, n + 1):
        target = i - 1 if i > 1 else n
        parts.append(
            "### DQ-%03d: Entry %d\nStatus: Banked. "
            "This supersedes the ruling at DQ-%03d.\n"
            % (i, i, target))
    if leaf_target is not None:
        parts.append(
            "### DQ-%03d: Leaf\nStatus: Banked. "
            "This supersedes the ruling at DQ-%03d.\n"
            % (n + 1, leaf_target))
    return "".join(parts)


def _chord_text():
    edges = {1: [6], 2: [1], 3: [2], 4: [3, 2], 5: [4], 6: [5]}
    parts = [_HEADER]
    for i in range(1, 7):
        parts.append(_simple_entry(i, edges[i]))
    return "".join(parts)


def _residue_text(n, phrasing):
    parts = [_HEADER]
    for i in range(1, n + 1):
        parts.append(
            "### DQ-%03d: Entry %d\nStatus: %s\n"
            "This entry asks whether the queue should adopt "
            "option %d for the shared record, with two named "
            "options and a stated cost of deciding late, and "
            "it blocks nothing.\n" % (i, i, phrasing(i), i))
    return "".join(parts)


def _segcite_text(per, nlines):
    parts = [_HEADER,
             "### DQ-001: Entry 1\nStatus: Banked\n"
             "This entry asks whether the queue should adopt "
             "option 1 for the shared record, with two named "
             "options and a stated cost of deciding late, and "
             "it blocks nothing.\n",
             "\n## Notes\n\n"]
    nxt = 100
    for _ in range(nlines):
        toks = ["DQ-%03d" % i for i in range(nxt, nxt + per)]
        nxt += per
        parts.append("See also " + ", ".join(toks) + ".\n")
    return "".join(parts)


class Ch150SortKeyMemoryTest(unittest.TestCase):
    """CH-150: the file findings sort key holds no encoded
    copy of the evidence or the statement, and the sort
    order stands exactly as the encoded key ordered it."""

    def test_sort_key_carries_the_texts_themselves(self):
        span = types.Span(3, 3)
        evidence = "See also DQ-100, DQ-101."
        statement = "A citation stands here."
        finding = validate._finding(
            "PD-R7", "Note", "FILE", span, evidence, statement)
        key = validate._file_order_key(finding)
        self.assertIs(key[3], evidence)
        self.assertIs(key[4], statement)

    def test_sort_key_traced_peak_stands_bounded(self):
        span = types.Span(1, 1)
        line = "See also " + ", ".join(
            "DQ-%03d" % i for i in range(100, 700)) + "."
        findings = []
        for i in range(3000):
            findings.append(validate._finding(
                "PD-R7", "Note", "FILE", span, line,
                "statement %d" % i))
        tracemalloc.start()
        try:
            findings.sort(key=validate._file_order_key)
            _current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        # Before the cure the keys held one encoded copy of
        # the line per finding and the traced peak of this
        # same construction stood at 30,031,700 bytes. The
        # bound stands at a tenth of that figure.
        self.assertLess(peak, 3000000)

    def test_sort_order_stands_as_the_encoded_key_ordered(self):
        def governed_key(finding):
            span = finding.line_span
            start = span.start_line if span is not None else 0
            end = span.end_line if span is not None else 0
            evidence = finding.evidence
            text = (evidence if isinstance(evidence, str)
                    else str(evidence))
            return (validate._rule_order_key(finding.rule_id),
                    start, end, text.encode("utf-8"),
                    (finding.statement or "").encode("utf-8"))

        specs = [
            ("PD-R7", 5, "bravo line", "second"),
            ("PD-R7", 5, "alpha line", "zz last"),
            ("PD-R7", 5, "alpha line", "aa first"),
            ("PIN-09", 5, "alpha line", "aa first"),
            ("PD-R7", 2, "zulu line", "mm"),
            (7, 5, "alpha line", "aa first"),
            ("PD-R7", 5, "alpha line", "aa first"),
        ]
        findings = []
        for rule, line, evidence, statement in specs:
            findings.append(validate._finding(
                rule, "Note", "FILE", types.Span(line, line),
                evidence, statement))
        expected = sorted(findings, key=governed_key)
        actual = sorted(findings, key=validate._file_order_key)
        self.assertEqual(
            [(f.rule_id, f.evidence, f.statement) for f in actual],
            [(f.rule_id, f.evidence, f.statement) for f in expected])

    def test_segment_citation_output_stands_combined_in_order(self):
        output = _run_text(_segcite_text(100, 20))
        notes = _by_rule(output, "PD-R7")
        self.assertEqual(len(notes), 20)
        spans = [h.span_of(f) for f in notes]
        self.assertEqual(spans, sorted(spans))
        for f in notes:
            self.assertEqual(
                len(h.as_list(h.get(f, "named_entries"))), 100)


class Ch151ResidueScanTest(unittest.TestCase):
    """CH-151: the residue list construction reads each
    entry once, and the residue items stand exactly as
    before, in form, in order, and in count."""

    def test_display_id_calls_stand_linear_on_distinct_form(self):
        n = 160
        text = _residue_text(n, lambda i: "Banked Qzx%d" % i)
        original = validate._display_id
        calls = [0]

        def counting(entry):
            calls[0] += 1
            return original(entry)

        validate._display_id = counting
        try:
            _run_text(text)
        finally:
            validate._display_id = original
        # Before the cure this same run stood at 29,000 and
        # more calls, the residue scan part standing at the
        # square of the entry count (160 squared is 25,600,
        # beside some 23 calls per entry elsewhere in the
        # model). The bound stands at 40 calls per entry.
        self.assertLessEqual(calls[0], 40 * n)

    def test_residue_items_stand_exact_on_untranslated_form(self):
        parts = [_HEADER]
        phrasings = ("Qzxalpha one", "Qzxbeta two", "Qzxalpha one")
        for i, phr in enumerate(phrasings, start=1):
            parts.append(
                "### DQ-%03d: Entry %d\nStatus: %s\n"
                "This entry asks whether the queue should adopt "
                "option %d for the shared record, with two named "
                "options and a stated cost of deciding late, and "
                "it blocks nothing.\n" % (i, i, phr, i))
        output = _run_text("".join(parts))
        items = h.as_list(h.get(output, "residue_items", "residue"))
        got = [(h.get(it, "phrasing"),
                h.get(it, "entry_identifier"),
                h.span_of(it)) for it in items]
        self.assertEqual(got, [
            ("Qzxalpha one", "DQ-001", (4, 4)),
            ("Qzxalpha one", "DQ-003", (10, 10)),
            ("Qzxbeta two", "DQ-002", (7, 7)),
        ])
        self.assertEqual(
            tuple(h.get(output, "residue_share")), (3, 3))

    def test_translated_phrasing_takes_no_residue_item(self):
        # The disposition limb stands: a phrasing whose
        # carrying element holds a disposition stands
        # translated and keeps no item, on the charged
        # distinct form itself.
        output = _run_text(_residue_text(
            12, lambda i: "Banked Qzx%d" % i))
        items = h.as_list(h.get(output, "residue_items", "residue"))
        self.assertEqual(items, [])
        self.assertEqual(
            tuple(h.get(output, "residue_share")), (0, 12))

    def test_shared_phrasing_control_stands(self):
        output = _run_text(_residue_text(
            12, lambda i: "Qzxshared form"))
        items = h.as_list(h.get(output, "residue_items", "residue"))
        self.assertEqual(len(items), 12)
        self.assertEqual(
            tuple(h.get(output, "residue_share")), (12, 12))


class Ch152CyclePurityTest(unittest.TestCase):
    """CH-152: a recorded cycle whose only further edges
    leave the component is not re-walked from its later
    starts, and every governed figure of the enumeration
    stands as counted."""

    def test_impure_ring_successor_leaf_work_stands_at_ring(self):
        # Before the cure this form stood at work 1200: the
        # ring count, plus the one examination of the leaf
        # edge the recording descent pays at the middle
        # entry, plus one such examination for every later
        # start whose walk reached the middle entry. After
        # the cure the later starts are not walked and the
        # figure stands at the ring count plus the recording
        # descent examination alone.
        n = 800
        output = _run_text(_ring_text(n, leaf_target=n // 2))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), n + 1)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_impure_ring_successor_leaf_second_size(self):
        # Before the cure this form stood at work 600, on
        # the same count as the larger size.
        n = 400
        output = _run_text(_ring_text(n, leaf_target=n // 2))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), n + 1)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_pure_ring_pin_stands(self):
        n = 800
        output = _run_text(_ring_text(n))
        self.assertEqual(len(_cycle_warnings(output)), 1)
        self.assertEqual(_work_measured(output), n)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_chord_inside_component_stands_walked_and_whole(self):
        # The chord target stands inside the component and
        # later in file order than the starts it could close
        # from, so no start of either cycle stands clear and
        # both cycles stand recorded, exactly as before.
        output = _run_text(_chord_text())
        self.assertEqual(len(_cycle_warnings(output)), 2)
        self.assertEqual(_work_measured(output), 10)
        self.assertEqual(_work_over(output), False)
        self.assertEqual(_count_over(output), False)

    def test_governed_work_figures_stand(self):
        cases = [
            ("dense6", _dense_text(6), 409, 1866),
            ("bip4", _bip_text(4), 424, 2690),
            ("detour6", _detour_text(6), 987, 171535),
            ("wall6", _wall_text(200, 6), 443, 604492),
        ]
        for name, text, cycles, work in cases:
            with self.subTest(name=name):
                output = _run_text(text)
                self.assertEqual(
                    len(_cycle_warnings(output)), cycles)
                self.assertEqual(_work_measured(output), work)
                self.assertEqual(_work_over(output), False)
                self.assertEqual(_count_over(output), False)


if __name__ == "__main__":
    unittest.main()
