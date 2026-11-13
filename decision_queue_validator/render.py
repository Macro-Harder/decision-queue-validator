"""Render: the Validate output only, and nothing else.

Render owns presentation only. It receives the Validate output as
its sole value, and it grades nothing, merges nothing, drops
nothing, recounts nothing and rederives nothing. Every figure it
prints stands in the Validate output it is handed, in the fields
validate computed once.
"""

__all__ = [
    "render_validate",
    "render_summary",
    "render_output",
]

_CANONICAL_ORDER = (
    "Open", "Presented", "Parked", "Ruled", "Settled",
    "Settled in part", "Closed as decided", "Conditional",
)
_SEVERITY_ORDER = ("Error", "Warning", "Note")
_KIND_ORDER = ("line start", "embedded", "variant")


def _field(value, *names, default=None):
    for name in names:
        if isinstance(value, dict):
            if name in value and value[name] is not None:
                return value[name]
        elif value is not None and hasattr(value, name):
            found = getattr(value, name)
            if found is not None and not callable(found):
                return found
    return default


def _text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    inner = getattr(value, "value", None)
    if isinstance(inner, str):
        return inner
    return str(value)


def _counted(count, singular, plural):
    """A count with its unit noun, singular exactly at count 1."""
    return "%d %s" % (count, singular if count == 1 else plural)


def _number(value):
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    inner = getattr(value, "value", None)
    if isinstance(inner, int):
        return inner
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _items(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _rule_number(raw):
    if raw is None:
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    digits = ""
    for char in str(raw):
        if char.isdigit():
            digits += char
        elif digits:
            break
    return int(digits) if digits else None


def _span_text(span):
    if span is None:
        return "no line span recorded"
    start = _field(span, "start_line", "start", "first_line")
    end = _field(span, "end_line", "end", "last_line")
    if start is None and isinstance(span, (list, tuple)) and span:
        start = span[0]
        end = span[1] if len(span) > 1 else span[0]
    if start is None:
        line = _field(span, "line", "line_number")
        if line is not None:
            start = end = line
    if start is None:
        return "no line span recorded"
    if end is None or _number(end) == _number(start):
        return "line %d" % _number(start)
    return "lines %d to %d" % (_number(start), _number(end))


def _element_text(element):
    if element is None:
        return "no determining element"
    if isinstance(element, str):
        return element
    kind = _text(_field(element, "kind", "element_kind")) or "element"
    verbatim = _text(_field(element, "verbatim", "verbatim_value",
                            "value", "phrasing"))
    line = _field(element, "line", "line_number")
    if line is None:
        span = _field(element, "line_span", "span")
        line = _field(span, "start_line", "start")
    parts = [kind]
    if line is not None:
        parts.append("at line %d" % _number(line))
    if verbatim:
        parts.append(verbatim)
    return ": ".join((parts[0], " ".join(parts[1:]))) if len(parts) > 1 \
        else parts[0]


def _finding_rule(finding):
    return _rule_number(_field(finding, "rule_id", "rule", "check"))


def _finding_entry(finding):
    return _text(_field(finding, "entry_identifier", "entry_id",
                        "identifier", "entry"))


def _evidence_lines(evidence):
    lines = []
    for item in _items(evidence):
        if isinstance(item, str):
            lines.append(item)
        elif isinstance(item, dict):
            text = _text(_field(item, "text", "verbatim", "value"))
            line = _field(item, "line", "line_number")
            if text is not None:
                lines.append((("line %d: " % _number(line)) if line
                              is not None else "") + text)
        else:
            text = _text(_field(item, "text", "verbatim", "value"))
            line = _field(item, "line", "line_number")
            if text is None:
                text = _text(item)
            if text is not None:
                lines.append((("line %d: " % _number(line)) if line
                              is not None else "") + text)
    return lines


def _head_lines(output):
    facts = _field(output, "file_facts", "file_facts_data")
    limits = _field(output, "limits")
    lines = []
    lines.append("Decision queue validator")
    lines.append(
        "Scope: this run checks form and internal consistency of "
        "this one file only. Not checked: the truth of any ruling, "
        "landings in other documents, companion trace files, and "
        "any step closure.")
    lines.append(
        "Advisory bound: this report may not be cited as a pass or "
        "fail condition for any step, gate, or release until "
        "Captain JP rules otherwise.")
    if facts is not None:
        name = _text(_field(facts, "input_name", "name")) or ""
        digest = _text(_field(facts, "digest")) or ""
        entry_count = _field(facts, "entry_count", "entry_total")
        lines.append(
            "File facts: %s; %d bytes; %d lines; entry count: %s; "
            "digest %s" % (
                name, _number(_field(facts, "byte_count")),
                _number(_field(facts, "line_count")),
                _counted(_number(entry_count), "headed entry",
                         "headed entries"), digest[:12]))
    if limits is not None:
        lines.append(
            "Limits in force: %s bytes per file; %s lines per file; "
            "%s characters per line; vocabulary version %s; output "
            "form edition %s" % (
                format(_number(_field(limits, "max_bytes")), ","),
                format(_number(_field(limits, "max_lines")), ","),
                format(_number(_field(
                    limits, "max_characters_per_line")), ","),
                _text(_field(output, "vocabulary_version")),
                _text(_field(output, "output_form_edition"))))
    return lines


def _self_check_failed(output):
    recon = _field(output, "reconciliation", "reconciliation_block")
    check = _field(recon, "self_check", "self_check_result")
    if check is None:
        check = _field(output, "self_check", "self_check_result")
    if check is None:
        return None
    ok = _field(check, "sums_agree", "ok", "passed", "agrees")
    if isinstance(check, str):
        return check if "not agree" in check.lower() or \
            "do not agree" in check.lower() else None
    if ok is None or bool(ok):
        return None
    return check


def _banner_lines(output):
    decision = _field(output, "exit_decision", "exit")
    code = _number(_field(decision, "code", "exit_code"))
    if code != 4:
        return []
    recon = _field(output, "reconciliation", "reconciliation_block")
    ambiguous = _number(_field(recon, "ambiguous_count", "ambiguous"))
    canonical = _field(recon, "canonical_counts",
                       "entries_per_canonical_state") or {}
    conditional = 0
    if isinstance(canonical, dict):
        conditional = _number(canonical.get("Conditional"))
    if ambiguous == 0 and conditional == 0:
        return []
    return [
        "Banner: %s %s Ambiguous and %s %s Conditional, and totals "
        "depending on entry states are reported under that "
        "condition." % (
            _counted(ambiguous, "entry", "entries"),
            "is" if ambiguous == 1 else "are",
            _counted(conditional, "entry", "entries"),
            "is" if conditional == 1 else "are"),
        "",
    ]


def _reason_text(output):
    decision = _field(output, "exit_decision", "exit")
    reasons = [_text(item) for item in _items(
        _field(decision, "reason_classes", "reasons", "causes"))]
    return [item for item in reasons if item]


def _closing_lines(output, form):
    decision = _field(output, "exit_decision", "exit")
    code = _number(_field(decision, "code", "exit_code"))
    other = "render" if form == "validate" else "validate"
    if form == "validate":
        foot = ("The render subcommand shows the readable summary "
                "of this same parse.")
    else:
        foot = ("The validate subcommand shows the findings for "
                "this same parse.")
    del other
    reasons = _reason_text(output)
    if reasons:
        reason_part = "; ".join(reasons)
    elif code == 0:
        reason_part = "no findings above Note grade"
    else:
        reason_part = "the causes recorded in the Exit decision"
    closing = "exit %d: %s" % (code, reason_part)
    if code == 4 and _self_check_failed(output) is None:
        recon = _field(output, "reconciliation",
                       "reconciliation_block")
        per_severity = _field(recon, "findings_per_severity",
                              "findings_by_severity") or {}
        if isinstance(per_severity, dict):
            errors = _number(per_severity.get("Error"))
            warnings = _number(per_severity.get("Warning"))
            notes = _number(per_severity.get("Note"))
            closing += ("; findings present at lower grades: %d "
                        "Error, %d Warning, %d Note" % (
                            errors, warnings, notes))
    closing += ("; this exit code is a findings signal and is not "
                "a step verdict.")
    return ["", foot, closing]


def _failure_output(output, form):
    check = _self_check_failed(output)
    lines = _head_lines(output)
    lines.append("")
    failed = _field(check, "failed_components", "failures", "failed")
    lines.append(
        "Tool fault: the tool own counts do not sum, and this run "
        "is reported as a tool inconsistency. The summary is "
        "withheld in full.")
    failed_items = _items(failed)
    if failed_items:
        lines.append("Failed components, with the values computed "
                     "for each side:")
        for item in failed_items:
            lines.append("- failed: %s" % _text(item))
    else:
        detail = _text(_field(check, "detail", "statement"))
        if detail:
            lines.append("- failed: %s" % detail)
    lines.append(
        "Next step: report this run as a tool fault; do not edit "
        "the queue file on the basis of this run.")
    lines.extend(_closing_lines(output, form))
    return "\n".join(lines) + "\n"


def _reconciliation_lines(output):
    recon = _field(output, "reconciliation", "reconciliation_block")
    lines = ["Reconciliation", ""]
    if recon is None:
        lines.append("No reconciliation block stands in this run.")
        return lines
    entry_total = _field(recon, "entry_total", "headed_entry_count",
                         "entry_count")
    lines.append("Headed entries: %d" % _number(entry_total))
    lines.append("DQ entries: %d" % _number(
        _field(recon, "dq_entry_count")))
    lines.append("Unnumbered entries: %d" % _number(
        _field(recon, "unnumbered_entry_count")))
    lines.append("Headed spans: %d" % _number(
        _field(recon, "headed_span_count")))
    lines.append("Orphan note segments: %d" % _number(
        _field(recon, "orphan_note_segment_count",
               "orphan_segment_count")))
    lines.append("H4 sub headings: %d" % _number(
        _field(recon, "h4_sub_heading_count")))
    by_kind = _field(recon, "status_occurrences_by_kind",
                     "occurrences_by_kind") or {}
    if isinstance(by_kind, dict):
        parts = []
        for kind in _KIND_ORDER:
            if kind in by_kind:
                parts.append("%s %d" % (kind, _number(by_kind[kind])))
        for kind in by_kind:
            if kind not in _KIND_ORDER:
                parts.append("%s %d" % (_text(kind),
                                        _number(by_kind[kind])))
        lines.append("Status occurrences by kind: " + ", ".join(parts))
    lines.append("Status occurrence total: %d" % _number(
        _field(recon, "status_occurrence_total", "occurrence_total")))
    canonical = _field(recon, "canonical_counts",
                       "entries_per_canonical_state") or {}
    if isinstance(canonical, dict):
        for state in _CANONICAL_ORDER:
            if state in canonical:
                lines.append("Canonical %s: %d" % (
                    state, _number(canonical[state])))
        for state in canonical:
            if state not in _CANONICAL_ORDER:
                lines.append("Canonical %s: %d" % (
                    _text(state), _number(canonical[state])))
    lines.append("Ambiguous: %d" % _number(
        _field(recon, "ambiguous_count", "ambiguous")))
    lines.append("Unparsed entries: %d" % _number(
        _field(recon, "unparsed_count", "unparsed_entries")))
    per_severity = _field(recon, "findings_per_severity",
                          "findings_by_severity") or {}
    if isinstance(per_severity, dict):
        parts = []
        for severity in _SEVERITY_ORDER:
            if severity in per_severity:
                parts.append("%s %d" % (
                    severity, _number(per_severity[severity])))
        lines.append("Findings per severity: " + ", ".join(parts))
    per_rule = _field(recon, "findings_per_rule", "findings_by_rule") \
        or {}
    if isinstance(per_rule, dict) and per_rule:
        numbered = []
        for key, value in per_rule.items():
            number = _rule_number(key)
            if isinstance(value, dict):
                count = sum(_number(item) for item in value.values())
            else:
                count = _number(value)
            numbered.append((number if number is not None else 0,
                             count))
        numbered.sort()
        lines.append("Findings per rule: " + ", ".join(
            "check %d: %d" % pair for pair in numbered))
    distinct = _field(recon, "distinct_phrasing_count")
    lines.append("Distinct status phrasings: %s" %
                 _counted(_number(distinct), "phrasing", "phrasings"))
    check = _field(recon, "self_check", "self_check_result")
    ok = _field(check, "sums_agree", "ok", "passed", "agrees")
    lines.append("Self check: sums agree" if ok else
                 "Self check: sums do not agree")
    declarations = _items(_field(recon, "paired_total_declarations",
                                 "paired_totals"))
    for item in declarations:
        text = _text(_field(item, "text", "statement", "declaration"))
        lines.append(text if text is not None else _text(item))
    canonical_sum = 0
    if isinstance(canonical, dict):
        canonical_sum = sum(_number(value) for value in
                            canonical.values())
    lines.append(
        "Paired totals: the entry total of %s "
        "equals the canonical rows total of %d plus the Ambiguous "
        "count of %d plus the unparsed row of %d, both views from "
        "the one parse; the Status occurrence total of %d equals "
        "the sum of the verbatim appendix rows, both views from "
        "the one parse." % (
            _counted(_number(entry_total), "headed entry",
                     "headed entries"), canonical_sum,
            _number(_field(recon, "ambiguous_count", "ambiguous")),
            _number(_field(recon, "unparsed_count",
                           "unparsed_entries")),
            _number(_field(recon, "status_occurrence_total",
                           "occurrence_total"))))
    return lines


def _census_lines(output):
    lines = ["Census", ""]
    census = _items(_field(output, "census", "census_entries"))
    if not census:
        lines.append("No census classes stand in this run.")
        return lines
    for entry in census:
        name = _text(_field(entry, "class_name", "name",
                            "census_class", "kind")) or "class"
        count = _number(_field(entry, "count", "member_count",
                               "total"))
        members = [_text(item) for item in _items(
            _field(entry, "member_entry_ids", "members",
                   "member_ids", "entry_ids"))]
        lines.append("%s: %d" % (name, count))
        if members:
            lines.append("Members: " + ", ".join(
                item for item in members if item is not None))
    return lines


def _segment_claim_lines(output):
    reports = _items(_field(output, "segment_claim_reports",
                            "segment_claims"))
    if not reports:
        return []
    lines = ["Segment claims", ""]
    lines.append(
        "Claims carried by note segments are reported here as "
        "claims. A claim reported here is not applied to any "
        "entry it names.")
    lines.append("")
    for report in reports:
        heading = _text(_field(report, "segment_heading", "heading",
                               "heading_text")) or ""
        if heading:
            lines.append("Segment: %s" % heading)
        statement = _text(_field(report, "statement", "text"))
        if statement:
            lines.append("Claim, reported as a claim: %s" % statement)
        else:
            lines.append("Claim, reported as a claim.")
        named = [_text(item) for item in _items(
            _field(report, "named_entries", "entries_named",
                   "named_entry_ids"))]
        named = [item for item in named if item]
        if named:
            lines.append("Entries named in the claim: " +
                         ", ".join(named))
        lines.append(
            "Reported as a claim only: the claim is not applied "
            "to any entry it names.")
        lines.append("")
    return lines


def _entry_label(entry):
    ident = _text(_field(entry, "identifier", "entry_id", "id",
                         "dq_number"))
    if ident is None:
        ident = _text(_field(entry, "heading", "heading_text")) or ""
    return ident


def _entry_state(entry):
    return _text(_field(entry, "effective_state", "state",
                        "canonical_state", "reported_state"))


def _date_text(entry):
    date = _text(_field(entry, "date", "date_text"))
    return date if date else "no date recorded"


def _base_row_lines(entry):
    lines = []
    ident = _entry_label(entry)
    title = _text(_field(entry, "title")) or ""
    lines.append("%s: %s" % (ident, title) if title else ident)
    lines.append("Date: %s" % _date_text(entry))
    phrasings = [_text(item) for item in _items(
        _field(entry, "status_phrasings", "phrasings"))]
    phrasings = [item for item in phrasings if item]
    if not phrasings:
        head = _text(_field(entry, "head_phrasing"))
        if head:
            phrasings = [head]
    if phrasings:
        lines.append("Status as written: " + "; ".join(phrasings))
    label = _text(_field(entry, "decider_label"))
    if label:
        lines.append("Decider label: %s" % label)
    return lines


def _determining_line(entry):
    element = _field(entry, "determining_element")
    if element is None:
        return "Determining element: none recorded"
    return "Determining element: %s" % _element_text(element)


def _banked_line(entry):
    banked = _text(_field(entry, "banked_question_id",
                          "banked_question"))
    if not banked:
        return None
    return ("no action available to the reader: awaiting ruling "
            "on %s" % banked)


def _open_row_lines(entry):
    lines = _base_row_lines(entry)
    lines.append(_determining_line(entry))
    fields = _field(entry, "open_fields", "open_row_fields") or {}

    def shown(*names):
        value = _field(fields, *names) if fields else None
        if value is None and not isinstance(fields, dict):
            value = _field(entry, *names)
        text = _text(value)
        return text if text else "absent"

    lines.append("Question: %s" % shown(
        "question", "The question", "Question",
        "Question as put on the Questions space"))
    lines.append("Options: %s" % shown("options", "Options"))
    lines.append("Cost of deciding late: %s" % shown(
        "cost_of_deciding_late", "cost", "Cost of deciding late"))
    lines.append("What it blocks: %s" % shown(
        "what_it_blocks", "blocks", "What it blocks"))
    lines.append("Effort signal: %s" % shown(
        "effort_signal", "effort", "Effort signal"))
    reason = _text(_field(entry, "ordering_reason"))
    if reason:
        lines.append("Ordering reason (the entry own claim): %s" %
                     reason)
    banked = _banked_line(entry)
    if banked:
        lines.append(banked)
    return lines


def _part_row_lines(entry):
    lines = _base_row_lines(entry)
    lines.append(_determining_line(entry))
    remainder = _text(_field(entry, "remainder_text", "remainder"))
    lines.append("Remainder: %s" % (remainder if remainder
                                    else "absent"))
    condition = _text(_field(entry, "condition_text", "condition"))
    if condition:
        lines.append("Condition: %s" % condition)
    banked = _banked_line(entry)
    if banked:
        lines.append(banked)
    return lines


def _conditional_row_lines(entry):
    lines = _base_row_lines(entry)
    lines.append(_determining_line(entry))
    condition = _text(_field(entry, "condition_text", "condition"))
    lines.append("Condition: %s" % (condition if condition
                                     else "absent"))
    remainder = _text(_field(entry, "remainder_text", "remainder"))
    if remainder:
        lines.append("Remainder: %s" % remainder)
    banked = _banked_line(entry)
    if banked:
        lines.append(banked)
    return lines


def _ambiguous_row_lines(entry):
    lines = _base_row_lines(entry)
    sub = _text(_field(entry, "sub_label", "ambiguous_sub_label"))
    if sub:
        lines.append("Ambiguous sub label: %s" % sub)
    competing = _items(_field(entry, "competing_elements"))
    if competing:
        lines.append("Competing elements:")
        for element in competing:
            lines.append("- %s" % _element_text(element))
            verbatim = _text(_field(element, "verbatim",
                                    "verbatim_value", "value"))
            statement = _text(_field(element, "statement"))
            if statement and statement != verbatim:
                lines.append("  %s" % statement)
    else:
        lines.append(_determining_line(entry))
    banked = _banked_line(entry)
    if banked:
        lines.append(banked)
    return lines


def _decided_row_lines(entry):
    lines = _base_row_lines(entry)
    state = _entry_state(entry)
    if state:
        lines.append("State: %s" % state)
    if not _text(_field(entry, "decider_label")):
        annotation = _text(_field(entry, "decider_annotation",
                                  "annotation"))
        lines.append("Decider: %s" % (
            annotation if annotation else "decider not recorded"))
    lines.append(_determining_line(entry))
    banked = _banked_line(entry)
    if banked:
        lines.append(banked)
    return lines


def _group_lines(entries, wanted, title, row_fn):
    chosen = [entry for entry in entries
              if _entry_state(entry) == wanted]
    if not chosen:
        return []
    lines = [title, ""]
    for entry in chosen:
        lines.extend(row_fn(entry))
        lines.append("")
    return lines


def _summary_text(element):
    """The ordered element summary form of one element object.

    Mirrors the summary validate builds (brief section 5.5): line
    number, kind, verbatim value in full, disposition.
    """
    line = _field(element, "line", "line_number")
    kind = _text(_field(element, "kind", "element_kind"))
    verbatim = _text(_field(element, "verbatim", "verbatim_value",
                            "value"))
    raw_disposition = _field(element, "disposition")
    disposition = _text(raw_disposition)
    if raw_disposition is None:
        disposition = "None"
    if verbatim:
        return "line %s: %s: %s: %s" % (line, kind, verbatim,
                                        disposition)
    return "line %s: %s: %s" % (line, kind, disposition)


def _docket_lines(output, entries):
    findings = _items(_field(output, "findings", "findings_list"))
    disagreement_ids = []
    for finding in findings:
        if _finding_rule(finding) == 3:
            ident = _finding_entry(finding)
            if ident and ident not in disagreement_ids:
                disagreement_ids.append(ident)
    chosen = []
    for entry in entries:
        ident = _entry_label(entry)
        if _entry_state(entry) == "Ambiguous" or \
                ident in disagreement_ids:
            chosen.append(entry)
    if not chosen:
        return []
    lines = ["Docket", ""]
    for entry in chosen:
        ident = _entry_label(entry)
        lines.append("Docket for %s" % ident)
        summary = _items(_field(entry, "element_summary",
                                "elements", "ordered_elements"))
        if not summary:
            summary = []
            det = _field(entry, "determining_element")
            if det is not None:
                summary.append(det)
            summary.extend(_items(_field(entry,
                                         "competing_elements")))
        det = _field(entry, "determining_element")
        competing = _items(_field(entry, "competing_elements"))
        det_summary = _summary_text(det) if det is not None else None
        competing_summaries = set(
            _summary_text(element) for element in competing)
        for element in summary:
            mark = ""
            if isinstance(element, str):
                # The summary strings are matched against the same
                # summary form built from the determining and
                # competing element objects; comparing a string
                # against the objects themselves can never hold,
                # which is why no mark printed before this fix.
                # For an Ambiguous entry the competing mark is the
                # brief's mark, so it is tested first there: the
                # derivation also names a candidate element as
                # determining on such an entry, and the competing
                # mark is the one section 5.5 rules for it.
                if _entry_state(entry) == "Ambiguous":
                    if element in competing_summaries:
                        mark = " [competing element]"
                    elif det_summary is not None and \
                            element == det_summary:
                        mark = " [determining element]"
                elif det_summary is not None and \
                        element == det_summary:
                    mark = " [determining element]"
                elif element in competing_summaries:
                    mark = " [competing element]"
            else:
                if det is not None and element == det:
                    mark = " [determining element]"
                elif element in competing:
                    mark = " [competing element]"
            lines.append("- %s%s" % (_element_text(element), mark))
        lines.append("")
    return lines


def _counts_lines(output):
    lines = ["Counts", ""]
    lines.append(
        "Glossary: headed spans and orphan segments are file "
        "units; canonical states are the derived state names; "
        "phrasings are the verbatim Status values as written.")
    recon = _field(output, "reconciliation", "reconciliation_block")
    canonical = _field(recon, "canonical_counts",
                       "entries_per_canonical_state") or {}
    if isinstance(canonical, dict):
        lines.append("Canonical counts:")
        for state in _CANONICAL_ORDER:
            if state in canonical:
                lines.append("%s: %d" % (state,
                                         _number(canonical[state])))
        for state in canonical:
            if state not in _CANONICAL_ORDER:
                lines.append("%s: %d" % (_text(state),
                                         _number(canonical[state])))
        lines.append("Ambiguous: %d" % _number(
            _field(recon, "ambiguous_count", "ambiguous")))
    subtotals = _field(output, "decider_subtotals", "decider_counts")
    if isinstance(subtotals, dict) and subtotals:
        lines.append("Counts of entries by recorded decider label:")
        for label, value in subtotals.items():
            lines.append("%s: %d" % (_text(label), _number(value)))
        lines.append(
            "these figures measure the queue and its questions; "
            "they are not a measure of any person")
    crosswalk = _field(output, "crosswalk_counts", "crosswalk")
    if isinstance(crosswalk, dict) and crosswalk:
        lines.append("Crosswalk, head phrasing by canonical state:")
        for phrasing, row in crosswalk.items():
            if isinstance(row, dict):
                parts = []
                for state in _CANONICAL_ORDER:
                    if state in row:
                        parts.append("%s %d" % (
                            state, _number(row[state])))
                for state in row:
                    if state not in _CANONICAL_ORDER:
                        parts.append("%s %d" % (
                            _text(state), _number(row[state])))
                lines.append("%s: %s" % (_text(phrasing),
                                         ", ".join(parts)))
            else:
                lines.append("%s: %d" % (_text(phrasing),
                                         _number(row)))
    elif isinstance(crosswalk, (list, tuple)):
        lines.append("Crosswalk, head phrasing by canonical state:")
        for row in crosswalk:
            lines.append(_text(row))
    return lines


def _appendix_lines(output):
    lines = ["Verbatim appendix", ""]
    lines.append(
        "rows count Status occurrences as written, not entries; "
        "one entry can contribute several occurrences, and one "
        "line can contribute two; the entry counts are in the "
        "canonical table; rows are not merged.")
    rows = _items(_field(output, "verbatim_appendix_rows",
                         "appendix_rows", "verbatim_appendix"))
    for row in rows:
        if isinstance(row, str):
            lines.append(row)
            continue
        phrasing = _text(_field(row, "phrasing", "status_phrasing",
                                "verbatim_phrasing", "value")) or ""
        kind = _text(_field(row, "kind", "kind_marker")) or ""
        count = _number(_field(row, "occurrence_count", "count",
                               "occurrences"))
        members = [_text(item) for item in _items(
            _field(row, "member_entry_ids", "members", "entry_ids",
                   "entries"))]
        line = "%s | %s | %s" % (
            phrasing, kind,
            _counted(count, "occurrence", "occurrences"))
        if members:
            line += " | entries: " + ", ".join(
                item for item in members if item is not None)
        if _field(row, "unclassified"):
            line += " | unclassified"
        lines.append(line)
    return lines


def _limbo_parts(output, entries):
    limbo = _field(output, "limbo_data", "limbo",
                   "limbo_sentence_data")
    result = {}
    for key, state in (("conditional", "Conditional"),
                       ("ambiguous", "Ambiguous"),
                       ("unparsed", None)):
        ids = None
        count = None
        if isinstance(limbo, dict):
            raw = limbo.get(key)
            if isinstance(raw, dict):
                ids = [_text(item) for item in _items(
                    _field(raw, "entry_ids", "member_entry_ids",
                           "ids", "members"))]
                count = _number(_field(raw, "count", "total"))
            elif isinstance(raw, (list, tuple)):
                ids = [_text(item) for item in raw]
                count = len(ids)
            elif raw is not None:
                count = _number(raw)
            if ids is None:
                raw_ids = limbo.get(key + "_ids") or \
                    limbo.get(key + "_entry_ids")
                if raw_ids is not None:
                    ids = [_text(item) for item in _items(raw_ids)]
            if count is None:
                raw_count = limbo.get(key + "_count")
                if raw_count is not None:
                    count = _number(raw_count)
        if ids is None:
            if state is not None:
                ids = [_entry_label(entry) for entry in entries
                       if _entry_state(entry) == state]
            else:
                ids = [_entry_label(entry) for entry in entries
                       if _field(entry, "unparsed")]
            count = len(ids)
        if count is None:
            count = len(ids)
        result[key] = (count, [item for item in ids if item])
    return result


def _figures_lines(output, entries):
    lines = ["Project Manager figures", ""]
    waiting = _field(output, "waiting", "waiting_figure",
                     "waiting_count")
    blocking = _field(output, "blocking", "blocking_figure",
                      "blocking_count")
    figures = _field(output, "project_manager_figures", "pm_figures",
                     "figures")
    if waiting is None and figures is not None:
        waiting = _field(figures, "waiting", "waiting_count")
    if blocking is None and figures is not None:
        blocking = _field(figures, "blocking", "blocking_count")
    lines.append(
        "Waiting: %d. The waiting figure is effective Open "
        "entries plus Settled in part remainders." % _number(waiting))
    blocking_count = _number(blocking)
    lines.append("Blocking: %s that %s." % (
        _counted(blocking_count, "entry", "entries"),
        "blocks" if blocking_count == 1 else "block"))
    coverage = _field(output, "blocks_coverage", "blocks_counts")
    blocks_with = None
    blocks_without = None
    if isinstance(coverage, dict):
        blocks_with = _field(coverage, "with_blocks_field",
                             "with_field")
        blocks_without = _field(coverage, "without_blocks_field",
                                "without_field")
    if blocks_with is None or blocks_without is None:
        open_entries = [entry for entry in entries
                        if _entry_state(entry) == "Open"]
        blocks_with = 0
        for entry in open_entries:
            fields = _field(entry, "open_fields",
                            "open_row_fields") or {}
            keys = fields.keys() if isinstance(fields, dict) else []
            if any("blocks" in str(key).lower() for key in keys):
                blocks_with += 1
        blocks_without = len(open_entries) - blocks_with
    blocks_with = _number(blocks_with)
    blocks_without = _number(blocks_without)
    lines.append(
        "Blocks coverage: %d effectively open %s a blocks field "
        "and %d %s none." % (
            blocks_with,
            "entry records" if blocks_with == 1
            else "entries record",
            blocks_without,
            "records" if blocks_without == 1 else "record"))
    limbo = _limbo_parts(output, entries)
    parts = []
    for key, label in (("conditional", "Conditional"),
                       ("ambiguous", "Ambiguous"),
                       ("unparsed", "unparsed")):
        count, ids = limbo[key]
        id_part = (": " + ", ".join(ids)) if ids else ""
        parts.append("%d %s %s%s" % (
            count, label,
            "entry" if count == 1 else "entries", id_part))
    lines.append(
        "Limbo: " + "; ".join(parts) + " stand outside both "
        "figures.")
    lines.append("Blocking list:")
    blocking_list = _items(_field(output, "blocking_list"))
    printed = False
    for item in blocking_list:
        if isinstance(item, str):
            lines.append("- %s" % item)
            printed = True
            continue
        ident = _text(_field(item, "identifier", "entry_id", "id"))
        if ident is None:
            ident = _entry_label(item)
        title = _text(_field(item, "title")) or ""
        blocks = None
        fields = _field(item, "open_fields", "open_row_fields")
        if fields:
            blocks = _text(_field(fields, "what_it_blocks",
                                  "blocks"))
        if blocks is None:
            blocks = _text(_field(item, "what_it_blocks", "blocks"))
        row = "- %s" % ident
        if title:
            row += ": %s" % title
        if blocks:
            row += ". What it blocks: %s" % blocks
        lines.append(row)
        printed = True
    if not printed:
        lines.append("- none")
    effort = _field(output, "effort_coverage", "effort_counts")
    with_signal = None
    without_signal = None
    if isinstance(effort, dict):
        with_signal = _number(_field(
            effort, "with_effort_signal", "with_signal", "carrying"))
        without_signal = _number(_field(
            effort, "without_effort_signal", "without_signal",
            "carrying_none"))
    if with_signal is None:
        open_entries = [entry for entry in entries
                        if _entry_state(entry) == "Open"]
        with_signal = 0
        for entry in open_entries:
            fields = _field(entry, "open_fields",
                            "open_row_fields") or {}
            signal = _field(fields, "effort_signal", "effort") \
                if fields else None
            if _text(signal):
                with_signal += 1
        without_signal = len(open_entries) - with_signal
    with_signal = _number(with_signal)
    without_signal = _number(without_signal)
    lines.append(
        "Effort coverage: %d effectively open %s an effort signal "
        "and %d %s none." % (
            with_signal,
            "entry carries" if with_signal == 1
            else "entries carry",
            without_signal,
            "carries" if without_signal == 1 else "carry"))
    fastest = _text(_field(output, "fastest_item",
                           "fastest_item_to_clear"))
    if fastest is None and figures is not None:
        fastest = _text(_field(figures, "fastest_item"))
    lines.append("Fastest item to clear: %s" % (
        fastest if fastest else "not derivable from the file"))
    lines.append(
        "these figures measure the queue and its questions; they "
        "are not a measure of any person")
    return lines


def render_validate(validate_output):
    """Compose the validate output text from a Validate output."""
    if _self_check_failed(validate_output) is not None:
        return _failure_output(validate_output, "validate")
    lines = _head_lines(validate_output)
    lines.extend(_banner_lines(validate_output))
    recon = _field(validate_output, "reconciliation",
                   "reconciliation_block")
    per_severity = _field(recon, "findings_per_severity",
                          "findings_by_severity") or {}
    per_rule = _field(recon, "findings_per_rule", "findings_by_rule") \
        or {}
    findings = _items(_field(validate_output, "findings",
                             "findings_list"))
    if isinstance(per_severity, dict) and per_severity:
        parts = []
        for severity in _SEVERITY_ORDER:
            if severity in per_severity:
                parts.append("%s %d" % (
                    severity, _number(per_severity[severity])))
        lines.append("Head counts, findings per severity: " +
                     ", ".join(parts))
    if isinstance(per_rule, dict) and per_rule:
        numbered = []
        for key, value in per_rule.items():
            number = _rule_number(key)
            if isinstance(value, dict):
                count = sum(_number(item) for item in value.values())
            else:
                count = _number(value)
            numbered.append((number if number is not None else 0,
                             count))
        numbered.sort()
        lines.append("Head counts, findings per rule: " + ", ".join(
            "check %d: %d" % pair for pair in numbered))
    lines.append("")
    lines.append("Index")
    lines.append("")
    indexed = []
    for position, finding in enumerate(findings):
        if _finding_entry(finding) == "FILE":
            continue
        severity = _text(_field(finding, "severity", "grade")) or ""
        rank = _SEVERITY_ORDER.index(severity) \
            if severity in _SEVERITY_ORDER else len(_SEVERITY_ORDER)
        indexed.append((rank, position, finding))
    indexed.sort(key=lambda item: (item[0], item[1]))
    if indexed:
        for _rank, _position, finding in indexed:
            span = _field(finding, "line_span", "span", "lines")
            lines.append("%s check %s %s %s" % (
                _finding_entry(finding),
                _finding_rule(finding),
                _text(_field(finding, "severity", "grade")),
                _span_text(span)))
    else:
        lines.append("No per entry findings.")
    lines.append("")
    lines.append("Findings")
    lines.append("")
    lines.append(
        "Findings concern form and internal consistency only; no "
        "finding judges whether a ruling was right, and the non "
        "gate bound applies.")
    lines.append("")
    if findings:
        current = None
        for finding in findings:
            ident = _finding_entry(finding)
            if ident != current:
                current = ident
                lines.append("%s" % ident)
            span = _field(finding, "line_span", "span", "lines")
            lines.append("check %s %s %s" % (
                _finding_rule(finding),
                _text(_field(finding, "severity", "grade")),
                _span_text(span)))
            statement = _text(_field(finding, "statement",
                                     "message", "summary"))
            if statement:
                lines.append("Statement: %s" % statement)
            basis = _text(_field(finding, "basis"))
            if basis:
                lines.append("Basis: %s" % basis)
            for evidence in _evidence_lines(
                    _field(finding, "evidence", "verbatim_evidence",
                           "quotes")):
                lines.append("Evidence: %s" % evidence)
            banked = _text(_field(finding, "banked_question_id",
                                  "banked_question"))
            if banked:
                lines.append(
                    "no action available to the reader: awaiting "
                    "ruling on %s" % banked)
            edit = _text(_field(finding, "suggested_edit"))
            if edit:
                lines.append("Suggested edit: %s" % edit)
            lines.append("")
    else:
        lines.append("No findings.")
        lines.append("")
    forms = _field(validate_output, "per_rule_clearing_forms",
                   "clearing_forms", "rule_list")
    lines.append("Rule list")
    lines.append("")
    # Each clearing form prints under its own name: a numbered
    # check under "check N", and a form keyed by a pin name (the
    # pin 5 unmatched heading form) under that name, ordered after
    # the check of the same number.
    form_entries = []

    def _form_entry(number, label, value):
        text = None
        if isinstance(value, str):
            text = value
        elif isinstance(value, dict):
            text = _text(_field(value, "clearing_form", "form",
                                "text", "statement"))
        elif value is not None:
            text = _text(_field(value, "clearing_form", "form",
                                "text", "statement"))
            if text is None:
                text = _text(value)
        form_entries.append((number, label, text))

    if isinstance(forms, dict):
        for key, value in forms.items():
            number = _rule_number(key)
            if number is None and isinstance(value, dict):
                number = _finding_rule(value)
            if number is not None:
                if isinstance(key, str) and not key.isdigit():
                    label = key
                else:
                    label = "check %d" % number
                _form_entry(number, label, value)
    elif forms:
        for item in _items(forms):
            number = _finding_rule(item)
            if number is not None:
                _form_entry(number, "check %d" % number, item)
    if not form_entries:
        seen = set()
        for finding in findings:
            number = _finding_rule(finding)
            if number is not None and number not in seen:
                seen.add(number)
                _form_entry(number, "check %d" % number, None)
    form_entries.sort(
        key=lambda entry: (entry[0], 0 if entry[1].startswith(
            "check") else 1, entry[1]))
    if form_entries:
        for _number_key, label, text in form_entries:
            if text:
                lines.append("%s: %s" % (label, text))
            else:
                lines.append(
                    "%s: a finding of this rule clears when "
                    "the recorded form for this check stands in "
                    "the file." % label)
    else:
        lines.append("No rule fired in this run.")
    lines.append("")
    lines.extend(_census_lines(validate_output))
    lines.extend(_closing_lines(validate_output, "validate"))
    return "\n".join(lines) + "\n"


def render_summary(validate_output):
    """Compose the render output text from a Validate output."""
    if _self_check_failed(validate_output) is not None:
        return _failure_output(validate_output, "render")
    entries = _items(_field(validate_output, "entries",
                            "entry_results", "per_entry"))
    lines = _head_lines(validate_output)
    lines.extend(_banner_lines(validate_output))
    lines.append(
        "Contents: the reconciliation block for the Project "
        "Manager at step checks; the census for the Clerk; the "
        "open groups, the docket and the decided groups for the "
        "Clerk; the counts and the verbatim appendix for the "
        "Auditor and for Captain JP.")
    lines.append(
        "this summary is not a presentation list: presentation "
        "order is not in the file and is not reconstructed here")
    lines.append(
        "Presentation set: the set includes Open entries, plus "
        "Settled in part remainders. Standing outside the set: "
        "Conditional entries, because the file does not record "
        "whether its condition is satisfied; Ambiguous entries, "
        "because its state is a queue defect to be reported "
        "upward, and for the BQ-2 pair because it awaits a ruling; "
        "and unparsed entries, because no state is assigned to "
        "them and their carriage is reported in their own "
        "reconciliation row.")
    lines.append("")
    lines.append(
        "Units key: entries, headed entries, Status lines, and "
        "phrasings are different units, and the unnumbered R-7 "
        "entry is why headed entries exceed DQ entries by one.")
    lines.append("")
    lines.extend(_reconciliation_lines(validate_output))
    lines.append("")
    lines.extend(_census_lines(validate_output))
    lines.append("")
    lines.extend(_segment_claim_lines(validate_output))
    lines.extend(_group_lines(entries, "Open", "Open group",
                              _open_row_lines))
    lines.extend(_group_lines(entries, "Settled in part",
                              "Settled in part group",
                              _part_row_lines))
    lines.extend(_group_lines(entries, "Conditional",
                              "Conditional group",
                              _conditional_row_lines))
    lines.extend(_group_lines(entries, "Ambiguous",
                              "Ambiguous group",
                              _ambiguous_row_lines))
    unparsed = [entry for entry in entries
                if _field(entry, "unparsed")]
    if unparsed:
        lines.append("Unparsed entries")
        lines.append("")
        for entry in unparsed:
            lines.extend(_base_row_lines(entry))
            lines.append(
                "This entry is carried as unparsed and is assigned "
                "no state.")
            lines.append("")
    lines.extend(_docket_lines(validate_output, entries))
    decided_states = ("Presented", "Parked", "Ruled", "Settled",
                      "Closed as decided")
    for state in decided_states:
        chosen = [entry for entry in entries
                  if _entry_state(entry) == state]
        if not chosen:
            continue
        chosen = sorted(
            chosen,
            key=lambda entry: (
                _text(_field(entry, "decider_label")) or "",
                entries.index(entry)))
        lines.append("%s group" % state)
        lines.append("")
        for entry in chosen:
            lines.extend(_decided_row_lines(entry))
            lines.append("")
    lines.extend(_counts_lines(validate_output))
    lines.append("")
    lines.extend(_appendix_lines(validate_output))
    lines.append("")
    lines.extend(_figures_lines(validate_output, entries))
    lines.extend(_closing_lines(validate_output, "render"))
    return "\n".join(lines) + "\n"


def render_output(validate_output, form):
    """Compose an output text for the named form."""
    if form == "render":
        return render_summary(validate_output)
    return render_validate(validate_output)
