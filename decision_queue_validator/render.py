"""Render: the operator output forms, and nothing else.

Render owns presentation only. It receives the render model as its
sole value, and it grades nothing, merges nothing, drops nothing,
recounts nothing and rederives nothing. Every figure it prints
stands in the render model it is handed, in the fields validate
computed once. The closing exit line is not part of what render
prints: shell prints it as the last line of the output.
"""

__all__ = [
    "render_validate",
    "render_summary",
    "render_output",
    "escape_text",
]

SCOPE_LINE = (
    "Checked: form and internal consistency only. Not checked: "
    "merits, truth of rulings, landings elsewhere, companion file "
    "contents, decider authority."
)
FINDINGS_HEAD_LINE = (
    "Findings concern form and internal consistency only. "
    "No finding judges whether a ruling was right."
)
MAP_HEAD_LINE = (
    "Supersession concerns form and internal consistency only. "
    "No chain in this map judges which matter governs in "
    "substance."
)
UNITS_KEY_LINE = (
    "Units key: canonical rows count entries; appendix rows count "
    "status occurrences as written; headed entries exceed DQ "
    "entries by one, the unnumbered R-7 entry, and every count "
    "that includes it states its unit; the line start figure is a "
    "census figure, not the status line total; the reported "
    "status line total is the occurrence total."
)
WAITING_FORMULA = (
    "Waiting is the count of distinct entries that are either "
    "effectively open entries, or Settled in part entries "
    "carrying at least one named remainder, or entries whose "
    "determining element takes Closed as decided for a part and "
    "which carry at least one standing remainder."
)
COMPANION_DEFINITION = (
    "entries carrying a standing remainder whose entry carries "
    "a supersession pointer"
)

_CANONICAL_ORDER = (
    "Open", "Presented", "Parked", "Ruled", "Settled",
    "Settled in part", "Closed as decided", "Conditional",
)
_GROUP_ORDER = (
    "Open", "Settled in part", "Presented", "Parked", "Conditional",
    "Ambiguous", "Ruled", "Settled", "Closed as decided",
)
_SEVERITY_ORDER = ("Error", "Warning", "Note")
_KIND_ORDER = ("line start", "embedded", "variant")

_U_FORM = set()
_U_FORM.update([0x061C, 0x200E, 0x200F, 0x00AD, 0x2060, 0xFEFF])
_U_FORM.update(range(0x202A, 0x202F))
_U_FORM.update(range(0x2066, 0x206A))
_U_FORM.update(range(0x200B, 0x200E))
_U_FORM.update(range(0x2061, 0x2065))
_U_FORM.update(range(0x206A, 0x2070))
_TAG_FORM = set([0xE0001])
_TAG_FORM.update(range(0xE0020, 0xE0080))


def escape_text(value):
    """The visible escaped form of one operator supplied text.

    One table governs both owning layers. Backslash doubles.
    Newline, carriage return, and tab print as backslash forms.
    Escape and the other C0, DEL, and C1 controls print as
    backslash, x, and two uppercase hexadecimal digits.
    Directional, zero width, invisible format, and invisible
    operator characters print as backslash, u, and four uppercase
    hexadecimal digits. Tag characters print as backslash, u, and
    five uppercase hexadecimal digits. Every other character
    prints as itself.
    """
    if value is None:
        return ""
    out = []
    for char in str(value):
        code = ord(char)
        if char == "\\":
            out.append("\\\\")
        elif char == "\n":
            out.append("\\n")
        elif char == "\r":
            out.append("\\r")
        elif char == "\t":
            out.append("\\t")
        elif code == 0x1B:
            out.append("\\x1B")
        elif code < 0x20 or code == 0x7F or 0x80 <= code <= 0x9F:
            out.append("\\x%02X" % code)
        elif code in _TAG_FORM:
            out.append("\\u%05X" % code)
        elif code in _U_FORM:
            out.append("\\u%04X" % code)
        else:
            out.append(char)
    return "".join(out)


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


def _esc(value):
    text = _text(value)
    if text is None:
        return ""
    return escape_text(text)


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


def _carried_number(value):
    if value is None:
        return None
    return _number(value)


def _items(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _counted(count, singular, plural):
    return "%d %s" % (count, singular if count == 1 else plural)


def _rule_text(raw):
    if raw is None:
        return ""
    if isinstance(raw, int):
        return str(raw)
    return _text(raw) or ""


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
        return "none recorded"
    if isinstance(element, str):
        return escape_text(element)
    kind = _esc(_field(element, "kind", "element_kind")) or "element"
    verbatim = _field(element, "verbatim", "verbatim_value", "value")
    line = _field(element, "line", "line_number", "position_line")
    if line is None:
        span = _field(element, "line_span", "span")
        line = _field(span, "start_line", "start")
    parts = [kind]
    if line is not None:
        parts.append("at line %d" % _number(line))
    text = " ".join(parts)
    if verbatim:
        text += ": " + escape_text(_text(verbatim))
    return text


def _head_lines(output):
    facts = _field(output, "file_facts", "file_facts_data")
    lines = [SCOPE_LINE]
    name = _field(facts, "input_name", "name")
    if name is None:
        name = _field(output, "input_name")
    lines.append("Input: %s" % _esc(name))
    if facts is not None:
        source = _text(_field(
            facts, "source_designation", "source", "designation"))
        if source not in ("live", "pinned"):
            source = _text(_field(
                output, "source_designation", "source"))
        if source not in ("live", "pinned"):
            source = "live"
        digest = _text(_field(facts, "digest")) or ""
        lines.append(
            "File: %s, %d lines, %d bytes, digest %s" % (
                source,
                _number(_field(facts, "line_count")),
                _number(_field(facts, "byte_count")),
                escape_text(digest[:12])))
    limits = _field(output, "limits")
    max_bytes = _field(limits, "max_bytes")
    max_lines = _field(limits, "max_lines")
    max_chars = _field(limits, "max_characters_per_line")
    lines.append(
        "Limits: %d bytes, %d lines, %d characters per line" % (
            _number(max_bytes) if max_bytes is not None else 2000000,
            _number(max_lines) if max_lines is not None else 10000,
            _number(max_chars) if max_chars is not None else 16384))
    lines.append(
        "Versions: vocabulary %s, output form %s, rule set %s" % (
            _esc(_field(output, "vocabulary_version") or "1"),
            _esc(_field(output, "output_form_edition") or "1"),
            _esc(_field(output, "rule_set_version",
                        "rule_set") or "1")))
    return lines


def _foot_line(form):
    other = "render" if form == "validate" else "validate"
    return ("For the other view, run the %s subcommand on the "
            "same file" % other)


def _carried_entry_total_break(output):
    """A footing break carried in the model itself, or None.

    Where the model handed to render carries parse owned header
    facts whose entry unit count disagrees with the entry list
    the model carries, and no reconciliation self check result
    stands in the model, the break the self check compares is
    already present in the carried values. It is reported in the
    form validate itself uses for that component, so the run
    takes the tool inconsistency surface in place of the summary.
    No figure is repaired and no count is recomputed for any
    other surface: a model carrying a reconciliation block is
    governed by its self check result alone, exactly as before.
    """
    facts = _field(output, "header_facts", "file_header_facts")
    if facts is None:
        return None
    counts = _field(facts, "unit_counts", "counts_by_kind")
    if not isinstance(counts, dict) or "entry" not in counts:
        return None
    claimed = _number(counts.get("entry"))
    actual = len(_entries(output))
    if claimed == actual:
        return None
    return {"failed_components": [
        "entry total: the entry list holds %d entries and the "
        "parse owned count records %d entry units"
        % (actual, claimed)]}


def _self_check_failed(output):
    recon = _field(output, "reconciliation", "reconciliation_block")
    check = _field(recon, "self_check", "self_check_result")
    if check is None:
        check = _field(output, "self_check", "self_check_result")
    if check is None:
        return _carried_entry_total_break(output)
    if isinstance(check, str):
        lowered = check.lower()
        return check if "not agree" in lowered or \
            "do not agree" in lowered else None
    ok = _field(check, "sums_agree", "ok", "passed", "agrees")
    if ok is None or bool(ok):
        return None
    return check


def _failure_output(output, form):
    check = _self_check_failed(output)
    lines = _head_lines(output)
    lines.append("")
    lines.append(
        "Tool fault: the tool own counts do not sum, and this run "
        "is reported as a tool inconsistency. The summary is "
        "withheld in full.")
    failed = _items(_field(check, "failed_components", "failures",
                           "failed"))
    if failed:
        lines.append(
            "Failed components, with the values computed for each "
            "side, each marked as a failed value:")
        for item in failed:
            if isinstance(item, str):
                lines.append("- failed component: %s" %
                             escape_text(item))
            else:
                name = _esc(_field(item, "name", "component",
                                   "text", "statement")) or "component"
                left = _field(item, "left", "expected", "first")
                right = _field(item, "right", "actual", "second")
                if left is not None or right is not None:
                    lines.append(
                        "- failed component: %s: failed value %s, "
                        "failed value %s" % (
                            name, _esc(left), _esc(right)))
                else:
                    lines.append("- failed component: %s" % name)
    else:
        detail = _text(_field(check, "detail", "statement"))
        if detail:
            lines.append("- failed component: %s" % escape_text(detail))
    lines.append(
        "Next step: report this run as a tool fault, and do not "
        "edit the queue file on the basis of this run.")
    lines.append(_foot_line(form))
    return "\n".join(lines) + "\n"


def _entries(output):
    return _items(_field(output, "entries", "entry_results",
                         "per_entry", "entry_groups"))


def _entry_label(entry):
    ident = _text(_field(entry, "identifier", "entry_id", "id",
                         "dq_number"))
    if ident is None:
        ident = _text(_field(entry, "heading", "heading_text")) or ""
    return ident


def _entry_state(entry):
    state = _text(_field(entry, "effective_state", "state",
                         "canonical_state", "reported_state",
                         "derived_state"))
    return state


def _entry_group(entry):
    if _field(entry, "unparsed", "unparsed_flag"):
        return "Unparsed"
    reporting = _text(_field(entry, "reporting_form",
                             "report_form"))
    if reporting == "Ambiguous":
        return "Ambiguous"
    state = _entry_state(entry)
    if state == "Ambiguous":
        return "Ambiguous"
    if state in _GROUP_ORDER:
        return state
    return None


def _pointers(entry):
    found = []
    for name in ("supersession_pointers", "supersession_pointer",
                 "pointers", "pointer"):
        value = _field(entry, name)
        for item in _items(value):
            text = None
            if isinstance(item, str):
                text = item
            else:
                text = _text(_field(
                    item, "superseding_entry", "superseding",
                    "entry", "identifier", "entry_id", "names"))
            if text and text not in found:
                found.append(text)
    return found


def _entry_row_lines(entry):
    lines = []
    ident = _entry_label(entry)
    title = _text(_field(entry, "title")) or ""
    heading = _text(_field(entry, "heading", "heading_text")) or ""
    if title:
        lines.append("%s: %s" % (escape_text(ident),
                                 escape_text(title)))
    elif heading:
        lines.append(escape_text(heading))
    else:
        lines.append(escape_text(ident))
    date = _text(_field(entry, "date", "date_text"))
    lines.append("Date: %s" % (escape_text(date) if date
                               else "no date recorded"))
    phrasings = [_text(item) for item in _items(
        _field(entry, "status_phrasings", "phrasings"))]
    phrasings = [item for item in phrasings if item]
    if not phrasings:
        head = _text(_field(entry, "head_phrasing"))
        if head:
            phrasings = [head]
    if phrasings:
        lines.append("Status as written: " + "; ".join(
            escape_text(item) for item in phrasings))
    state = _entry_state(entry)
    group = _entry_group(entry)
    if group == "Ambiguous":
        sub = _text(_field(entry, "sub_label",
                           "ambiguous_sub_label"))
        if sub:
            lines.append("Ambiguous sub label: %s" % escape_text(sub))
    elif state:
        lines.append("State: %s" % escape_text(state))
    if group == "Unparsed":
        lines.append(
            "This entry is carried as unparsed and is assigned "
            "no state.")
    determining = _field(entry, "determining_element")
    if determining is not None:
        lines.append("Determining element: %s" %
                     _element_text(determining))
    competing = _items(_field(entry, "competing_elements"))
    if competing:
        lines.append("Competing elements:")
        for element in competing:
            lines.append("- %s" % _element_text(element))
    label = _text(_field(entry, "decider_label"))
    if label:
        lines.append("Decider label: %s" % escape_text(label))
    else:
        annotation = _text(_field(entry, "decider_annotation",
                                  "annotation"))
        if annotation:
            lines.append("Decider: %s" % escape_text(annotation))
    fields = _field(entry, "open_fields", "open_row_fields",
                    "fields") or {}
    if isinstance(fields, (list, tuple)):
        converted = {}
        for item in fields:
            key = _text(_field(item, "label"))
            if key:
                converted[key] = _field(item, "value")
        fields = converted

    def shown(*names):
        for name in names:
            value = None
            if isinstance(fields, dict):
                value = fields.get(name)
            if value is None:
                value = _field(entry, name)
            text = _text(value)
            if text:
                return escape_text(text)
        return None

    question = shown("question", "The question", "Question",
                     "Question as put on the Questions space")
    if question is not None:
        lines.append("Question: %s" % question)
    options = shown("options", "Options")
    if options is not None:
        lines.append("Options: %s" % options)
    cost = shown("cost_of_deciding_late", "cost",
                 "Cost of deciding late")
    if cost is not None:
        lines.append("Cost of deciding late: %s" % cost)
    blocks = shown("what_it_blocks", "blocks", "What it blocks")
    if blocks is not None:
        lines.append("What it blocks: %s" % blocks)
    effort = shown("effort_signal", "effort", "Effort signal",
                   "Effort")
    if effort is not None:
        lines.append("Effort signal: %s" % effort)
    remainders = [_text(item) for item in _items(
        _field(entry, "remainder_texts", "remainders"))]
    remainders = [item for item in remainders if item]
    if not remainders:
        single = _text(_field(entry, "remainder_text", "remainder"))
        if single:
            remainders = [single]
    for remainder in remainders:
        lines.append("Remainder: %s" % escape_text(remainder))
    condition = _text(_field(entry, "condition_text", "condition"))
    if condition:
        lines.append("Condition: %s" % escape_text(condition))
    reason = _text(_field(entry, "ordering_reason"))
    if reason:
        lines.append("Ordering reason: %s" % escape_text(reason))
    note = _text(_field(entry, "internal_undecided_note",
                        "undecided_note"))
    if note:
        lines.append("Internal undecided note: %s" %
                     escape_text(note))
    for pointer in _pointers(entry):
        lines.append(
            "Supersession pointer: this entry is superseded by "
            "%s." % escape_text(pointer))
    banked = _text(_field(entry, "banked_question_id",
                          "banked_question"))
    if banked:
        lines.append(
            "no action available to the reader: awaiting ruling "
            "on %s" % escape_text(banked))
    return lines


def _group_sections(entries, include_all_headings):
    lines = []
    groups = {}
    for entry in entries:
        groups.setdefault(_entry_group(entry), []).append(entry)
    for state in _GROUP_ORDER:
        chosen = groups.get(state) or []
        if not chosen and not include_all_headings:
            continue
        title = "Unparsed entries" if state == "Unparsed" else \
            "%s group" % state
        if state == "Ambiguous":
            title = "Ambiguous group"
        lines.append(title)
        lines.append("")
        for entry in chosen:
            lines.extend(_entry_row_lines(entry))
            lines.append("")
    unparsed = groups.get("Unparsed") or []
    if unparsed or include_all_headings:
        lines.append("Unparsed entries")
        lines.append("")
        for entry in unparsed:
            lines.extend(_entry_row_lines(entry))
            lines.append("")
    return lines


def _presentation_marking_lines():
    return [
        "Presentation set: the Open group, and the Settled in "
        "part group for its remainders, form the set a presenter "
        "draws from.",
        "Standing outside the set: Presented, because its "
        "entries have already been presented, so a presenter "
        "does not draw them for presentation again.",
        "Standing outside the set: Parked, because its entries "
        "stand held back from presentation while they stand "
        "parked, awaiting reopening.",
        "Standing outside the set: Conditional, because the file "
        "does not record whether its condition is satisfied.",
        "Standing outside the set: Ambiguous, because its state "
        "is undetermined on its own elements.",
        "Standing outside the set: the decided groups, Ruled, "
        "Settled, and Closed as decided, because nothing in them "
        "is open.",
        "Standing outside the set: unparsed entries, because no "
        "state is assigned to them.",
        "File order is not presentation order. Presentation "
        "order lives outside the file with the Decision-queue "
        "Clerk.",
        "",
    ]


def _finding_rule(finding):
    return _rule_text(_field(finding, "rule_id", "rule", "check"))


def _finding_entry(finding):
    return _text(_field(finding, "entry_identifier", "entry_id",
                        "identifier", "entry"))


def _evidence_lines(evidence):
    lines = []
    for item in _items(evidence):
        if isinstance(item, str):
            lines.append(escape_text(item))
        elif isinstance(item, dict):
            text = _text(_field(item, "text", "verbatim", "value"))
            line = _field(item, "line", "line_number")
            if text is not None:
                lines.append((("line %d: " % _number(line)) if line
                              is not None else "") + escape_text(text))
        else:
            text = _text(_field(item, "text", "verbatim", "value"))
            line = _field(item, "line", "line_number")
            if text is None:
                text = _text(item)
            if text is not None:
                lines.append((("line %d: " % _number(line)) if line
                              is not None else "") + escape_text(text))
    return lines


def _validate_body(output):
    lines = []
    findings = _items(_field(output, "findings", "findings_list"))
    lines.append("Findings index")
    lines.append("")
    indexed = []
    for position, finding in enumerate(findings):
        ident = _finding_entry(finding)
        if ident is None or ident == "FILE":
            continue
        severity = _text(_field(finding, "severity", "grade")) or ""
        rank = _SEVERITY_ORDER.index(severity) \
            if severity in _SEVERITY_ORDER else len(_SEVERITY_ORDER)
        indexed.append((rank, position, finding))
    indexed.sort(key=lambda item: (item[0], item[1]))
    if indexed:
        for _rank, _position, finding in indexed:
            span = _field(finding, "line_span", "span", "lines")
            lines.append("%s %s %s %s" % (
                escape_text(_finding_entry(finding) or ""),
                escape_text(_finding_rule(finding)),
                escape_text(_text(_field(finding, "severity",
                                         "grade")) or ""),
                _span_text(span)))
    else:
        lines.append("No per entry findings.")
    lines.append("")
    lines.append("Findings")
    lines.append("")
    lines.append(FINDINGS_HEAD_LINE)
    lines.append("")
    if findings:
        current = None
        for finding in findings:
            ident = _finding_entry(finding)
            if ident != current:
                current = ident
                lines.append("%s" % escape_text(ident or ""))
            span = _field(finding, "line_span", "span", "lines")
            lines.append("%s %s %s" % (
                escape_text(_finding_rule(finding)),
                escape_text(_text(_field(finding, "severity",
                                         "grade")) or ""),
                _span_text(span)))
            statement = _text(_field(finding, "statement",
                                     "message", "summary"))
            if statement:
                lines.append("Statement: %s" % escape_text(statement))
            basis = _text(_field(finding, "basis"))
            if basis:
                lines.append("Basis: %s" % escape_text(basis))
            for evidence in _evidence_lines(
                    _field(finding, "evidence", "verbatim_evidence",
                           "quotes")):
                lines.append("Evidence: %s" % evidence)
            claiming = _text(_field(finding, "claiming_unit",
                                    "claiming_entry", "claiming"))
            if claiming:
                lines.append("Claiming unit: %s" %
                             escape_text(claiming))
            named = [_text(item) for item in _items(
                _field(finding, "named_entries", "named_entry_ids"))]
            named = [item for item in named if item]
            if named:
                lines.append("Named entries: " + ", ".join(
                    escape_text(item) for item in named))
            banked = _text(_field(finding, "banked_question_id",
                                  "banked_question"))
            if banked:
                lines.append(
                    "no action available to the reader: awaiting "
                    "ruling on %s" % escape_text(banked))
            edit = _text(_field(finding, "suggested_edit"))
            if edit:
                lines.append("Suggested edit: %s" % escape_text(edit))
            lines.append("")
    else:
        lines.append("No findings.")
        lines.append("")
    lines.append("Rule list")
    lines.append("")
    forms = _field(output, "per_rule_clearing_forms",
                   "clearing_forms", "rule_list")
    form_entries = []

    def _form_entry(number_key, label, value):
        text = None
        if isinstance(value, str):
            text = value
        elif value is not None:
            text = _text(_field(value, "clearing_form", "form",
                                "text", "statement"))
            if text is None and not isinstance(value, dict):
                text = _text(value)
        form_entries.append((number_key, label, text))

    if isinstance(forms, dict):
        for key, value in forms.items():
            label = key if isinstance(key, str) else \
                "check %s" % _rule_text(key)
            _form_entry(_rule_text(key), label, value)
    elif forms:
        for item in _items(forms):
            rule = _finding_rule(item)
            _form_entry(rule, "check %s" % rule, item)
    if not form_entries:
        seen = set()
        for finding in findings:
            rule = _finding_rule(finding)
            if rule and rule not in seen:
                seen.add(rule)
                _form_entry(rule, "check %s" % rule, None)
    form_entries.sort(key=lambda entry: entry[0])
    if form_entries:
        for _key, label, text in form_entries:
            if text:
                lines.append("%s: %s" % (escape_text(_text(label)),
                                         escape_text(text)))
            else:
                lines.append(
                    "%s: a finding of this rule clears when the "
                    "recorded form for this check stands in the "
                    "file." % escape_text(_text(label)))
    else:
        lines.append("No rule fired in this run.")
    lines.append("")
    return lines


def _crosswalk_lines(output):
    lines = []
    crosswalk = _field(output, "crosswalk_counts", "crosswalk")
    if isinstance(crosswalk, dict) and crosswalk:
        lines.append("Crosswalk for the Banked head phrasing:")
        for phrasing, row in crosswalk.items():
            if isinstance(row, dict):
                parts = []
                for state in _CANONICAL_ORDER:
                    if state in row:
                        parts.append("%s %d" % (
                            state, _number(row[state])))
                for state in row:
                    if state not in _CANONICAL_ORDER and \
                            state != "Ambiguous":
                        parts.append("%s %d" % (
                            escape_text(_text(state)),
                            _number(row[state])))
                ambiguous = row.get("Ambiguous")
                if ambiguous is not None:
                    parts.append(
                        "Ambiguous reporting count %d" %
                        _number(ambiguous))
                lines.append("%s: %s" % (escape_text(_text(phrasing)),
                                         ", ".join(parts)))
            else:
                lines.append("%s: %d" % (escape_text(_text(phrasing)),
                                         _number(row)))
    elif isinstance(crosswalk, (list, tuple)) and crosswalk:
        lines.append("Crosswalk for the Banked head phrasing:")
        for row in crosswalk:
            lines.append(escape_text(_text(row)))
    return lines


def _census_lines(output):
    lines = ["Census", ""]
    census = _items(_field(output, "census", "census_entries"))
    if not census:
        lines.append("No census classes stand in this run.")
        return lines
    for entry in census:
        name = _text(_field(entry, "class_name", "name",
                            "census_class", "class_identifier",
                            "kind")) or "class"
        count = _number(_field(entry, "count", "member_count",
                               "total"))
        lines.append("%s: %s" % (escape_text(name),
                                 _counted(count, "entry", "entries")))
        rule = _text(_field(entry, "class_rule", "rule_statement"))
        if rule:
            lines.append("Rule: %s" % escape_text(rule))
        head_count = _carried_number(_field(entry, "head_line_count"))
        if head_count is not None:
            lines.append("Head line count: %s" % _counted(
                head_count, "entry", "entries"))
            variance = _field(entry, "variance")
            if variance is not None:
                lines.append("Variance: %d entries" %
                             _number(variance))
        members = [_text(item) for item in _items(
            _field(entry, "member_entry_ids", "members",
                   "member_ids", "entry_ids"))]
        members = [item for item in members if item]
        if members:
            lines.append("Members: " + ", ".join(
                escape_text(item) for item in members))
    return lines


def _reconciliation_lines(output):
    lines = ["Reconciliation", ""]
    recon = _field(output, "reconciliation", "reconciliation_block")
    if recon is None:
        lines.append("No reconciliation block stands in this run.")
        return lines

    def _figure(label, value):
        carried = _carried_number(value)
        if carried is None:
            return "%s: absent" % label
        return "%s: %d" % (label, carried)

    lines.append(_figure(
        "Headed entries",
        _field(recon, "entry_total", "headed_entry_count",
               "entry_count")))
    lines.append(_figure("DQ entries",
                         _field(recon, "dq_entry_count")))
    lines.append(_figure("Unnumbered entries",
                         _field(recon, "unnumbered_entry_count")))
    lines.append(_figure("Headed spans",
                         _field(recon, "headed_span_count")))
    lines.append(_figure(
        "Orphan note segments",
        _field(recon, "orphan_note_segment_count",
               "orphan_segment_count")))
    lines.append(_figure("H4 sub headings",
                         _field(recon, "h4_sub_heading_count")))
    by_kind = _field(recon, "status_occurrences_by_kind",
                     "occurrences_by_kind") or {}
    if isinstance(by_kind, dict) and by_kind:
        parts = []
        for kind in _KIND_ORDER:
            if kind in by_kind:
                parts.append("%s %d" % (kind, _number(by_kind[kind])))
        for kind in by_kind:
            if kind not in _KIND_ORDER:
                parts.append("%s %d" % (escape_text(_text(kind)),
                                        _number(by_kind[kind])))
        lines.append("Status occurrences by kind: " + ", ".join(parts))
    lines.append(_figure(
        "Status occurrence total",
        _field(recon, "status_occurrence_total", "occurrence_total")))
    canonical = _field(recon, "canonical_counts",
                       "entries_per_canonical_state") or {}
    if isinstance(canonical, dict):
        for state in _CANONICAL_ORDER:
            if state in canonical:
                lines.append("Canonical %s: %d entries" % (
                    state, _number(canonical[state])))
        for state in canonical:
            if state not in _CANONICAL_ORDER:
                lines.append("Canonical %s: %d entries" % (
                    escape_text(_text(state)), _number(canonical[state])))
    lines.append("Ambiguous reporting count: %d" % _number(
        _field(recon, "ambiguous_count", "ambiguous")))
    lines.append(_figure(
        "Unparsed entries",
        _field(recon, "unparsed_count", "unparsed_entries")))
    per_severity = _field(recon, "findings_per_severity",
                          "findings_by_severity") or {}
    if isinstance(per_severity, dict) and per_severity:
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
            if isinstance(value, dict):
                count = sum(_number(item) for item in value.values())
            else:
                count = _number(value)
            numbered.append((_rule_text(key), count))
        numbered.sort()
        lines.append("Findings per rule: " + ", ".join(
            "%s: %d" % pair for pair in numbered))
    distinct = _carried_number(_field(recon, "distinct_phrasing_count"))
    if distinct is None:
        lines.append("Distinct status phrasings: absent")
    else:
        lines.append("Distinct status phrasings: %s" %
                     _counted(distinct, "phrasing", "phrasings"))
    check = _field(recon, "self_check", "self_check_result")
    ok = _field(check, "sums_agree", "ok", "passed", "agrees")
    if check is None or ok is None:
        lines.append("Self check: absent")
    else:
        lines.append("Self check: sums agree" if ok else
                     "Self check: sums do not agree")
    entry_total = _carried_number(
        _field(recon, "entry_total", "headed_entry_count",
               "entry_count"))
    canonical_sum = 0
    if isinstance(canonical, dict):
        canonical_sum = sum(_number(value) for value in
                            canonical.values())
    ambiguous = _number(_field(recon, "ambiguous_count", "ambiguous"))
    unparsed = _number(_field(recon, "unparsed_count",
                              "unparsed_entries"))
    occurrence = _carried_number(
        _field(recon, "status_occurrence_total", "occurrence_total"))
    if occurrence is None:
        occurrence_clause = "the Status occurrence total is absent"
    else:
        occurrence_clause = (
            "the Status occurrence total of %d equals the sum of "
            "the verbatim appendix rows, both views from the one "
            "parse" % occurrence)
    if entry_total is None:
        lines.append(
            "Paired totals: the entry total is absent and is not "
            "stated as a number; the canonical rows total of %d "
            "plus the Ambiguous reporting count of %d plus the "
            "unparsed row of %d, both views from the one parse; "
            "%s." % (canonical_sum, ambiguous, unparsed,
                     occurrence_clause))
    else:
        lines.append(
            "Paired totals: the entry total of %s equals the "
            "canonical rows total of %d plus the Ambiguous "
            "reporting count of %d plus the unparsed row of %d, "
            "both views from the one parse; %s." % (
                _counted(entry_total, "headed entry",
                         "headed entries"), canonical_sum, ambiguous,
                unparsed, occurrence_clause))
    return lines


def _appendix_lines(output):
    rows = _items(_field(output, "verbatim_appendix_rows",
                         "appendix_rows", "verbatim_appendix"))
    if not rows:
        return []
    lines = ["Verbatim appendix", ""]
    lines.append(
        "Rows count Status occurrences as written, not entries; "
        "one entry can contribute several occurrences, and one "
        "line can contribute two; the entry counts are in the "
        "canonical table; rows are not merged.")
    unclassified = []
    for row in rows:
        if isinstance(row, str):
            lines.append(escape_text(row))
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
            escape_text(phrasing), escape_text(kind),
            _counted(count, "occurrence", "occurrences"))
        members = [item for item in members if item]
        if members:
            line += " | entries: " + ", ".join(
                escape_text(item) for item in members)
        if _field(row, "unclassified"):
            line += " | unclassified"
            unclassified.append(line)
        lines.append(line)
    if unclassified:
        lines.append("")
        lines.append("Unclassified phrasings, held as unknown:")
        lines.extend(unclassified)
    return lines


def _residue_lines(output):
    items = _items(_field(output, "residue_items", "residue_list",
                          "residue"))
    if not items:
        return []
    lines = ["Residue list", ""]
    for item in items:
        if isinstance(item, str):
            lines.append(escape_text(item))
            continue
        phrasing = _text(_field(item, "phrasing", "verbatim",
                                "value")) or ""
        ident = _text(_field(item, "entry_identifier", "entry_id",
                             "identifier")) or ""
        span = _field(item, "line_span", "span")
        lines.append("%s | %s | %s" % (
            escape_text(phrasing), escape_text(ident),
            _span_text(span)))
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
            lines.append("Segment: %s" % escape_text(heading))
        statement = _text(_field(report, "statement", "text"))
        if statement:
            lines.append("Claim, reported as a claim: %s" %
                         escape_text(statement))
        else:
            lines.append("Claim, reported as a claim.")
        named = [_text(item) for item in _items(
            _field(report, "named_entries", "entries_named",
                   "named_entry_ids"))]
        named = [item for item in named if item]
        if named:
            lines.append("Entries named in the claim: " +
                         ", ".join(escape_text(item) for item in named))
        lines.append(
            "Reported as a claim only: the claim is not applied "
            "to any entry it names.")
        lines.append("")
    return lines


def _chain_lines(output):
    records = _field(output, "supersession_chain_records",
                     "chain_records")
    chains = records if records else _field(
        output, "supersession_chains", "chains", "map_chains")
    if chains is None:
        return []
    rendered = []
    for chain in _items(chains):
        cycle = False
        if isinstance(chain, dict):
            cycle = bool(_field(chain, "cycle", "is_cycle",
                                "closed"))
            ids = [_text(item) for item in _items(
                _field(chain, "entries", "entry_ids", "chain",
                       "identifiers"))]
        elif isinstance(chain, (list, tuple)):
            ids = [_text(item) for item in chain]
        else:
            ids = [_text(chain)]
        ids = [item for item in ids if item]
        if len(ids) < 2:
            continue
        line = " -> ".join(escape_text(item) for item in ids)
        if cycle:
            line += " (cycle)"
        rendered.append(line)
    if not rendered:
        return []
    lines = ["Supersession map", "", MAP_HEAD_LINE]
    lines.extend(rendered)
    lines.append("")
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
                raw_ids = _field(raw, "entry_ids",
                                 "member_entry_ids", "ids", "members")
                if raw_ids is not None:
                    ids = [_text(item) for item in _items(raw_ids)]
                count = _carried_number(
                    _field(raw, "count", "total"))
            elif isinstance(raw, (list, tuple)):
                ids = [_text(item) for item in raw]
                count = len(ids)
            elif raw is not None:
                count = _number(raw)
            if ids is None:
                raw_ids = limbo.get(key + "_ids")
                if raw_ids is None:
                    raw_ids = limbo.get(key + "_entry_ids")
                if raw_ids is not None:
                    ids = [_text(item) for item in _items(raw_ids)]
            if count is None:
                raw_count = limbo.get(key + "_count")
                if raw_count is not None:
                    count = _number(raw_count)
            if count is None and ids is not None:
                count = len(ids)
        if ids is None:
            if key == "unparsed":
                ids = [_entry_label(entry) for entry in entries
                       if _entry_group(entry) == "Unparsed"]
            else:
                ids = [_entry_label(entry) for entry in entries
                       if _entry_group(entry) == state]
        if count is None:
            recon = _field(output, "reconciliation",
                           "reconciliation_block")
            if key == "conditional":
                canonical = _field(recon, "canonical_counts") or {}
                if isinstance(canonical, dict) and \
                        "Conditional" in canonical:
                    count = _number(canonical["Conditional"])
            elif key == "ambiguous":
                count = _carried_number(_field(
                    recon, "ambiguous_count", "ambiguous"))
            elif key == "unparsed":
                count = _carried_number(_field(
                    recon, "unparsed_count", "unparsed_entries"))
        result[key] = (count,
                       [item for item in ids if item])
    return result


def _figures_lines(output, entries):
    lines = ["Figures", ""]
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
    waiting_carried = _carried_number(waiting)
    if waiting_carried is None:
        lines.append("Waiting: absent. %s" % WAITING_FORMULA)
    else:
        lines.append("Waiting: %s. %s" % (
            _counted(waiting_carried, "entry", "entries"),
            WAITING_FORMULA))
    companion = _field(output, "companion_count", "companion")
    if companion is None and figures is not None:
        companion = _field(figures, "companion_count", "companion")
    companion_carried = _carried_number(companion)
    if companion_carried is None:
        lines.append("Companion count: absent.")
    else:
        lines.append("Companion count: %d entries." %
                     companion_carried)
    lines.append("Companion definition: %s" % COMPANION_DEFINITION)
    blocking_carried = _carried_number(blocking)
    if blocking_carried is None:
        lines.append("Blocking: absent.")
    else:
        lines.append("Blocking: %s." % _counted(
            blocking_carried, "entry", "entries"))
    lines.append("Blocking list, in file order:")
    blocking_raw = _field(output, "blocking_list")
    blocking_list = _items(blocking_raw)
    printed = False
    if blocking_raw is None:
        lines.append("- absent")
        printed = True
    for item in blocking_list:
        if isinstance(item, str):
            lines.append("- %s" % escape_text(item))
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
        row = "- %s" % escape_text(ident)
        if title:
            row += ": %s" % escape_text(title)
        if blocks:
            row += ". What it blocks: %s" % escape_text(blocks)
        lines.append(row)
        printed = True
    if not printed:
        lines.append("- none")
    limbo = _limbo_parts(output, entries)
    parts = []
    for key, label in (("conditional", "Conditional"),
                       ("ambiguous", "Ambiguous"),
                       ("unparsed", "unparsed")):
        count, ids = limbo[key]
        if count is None:
            parts.append("%s absent" % label)
            continue
        id_part = (": " + ", ".join(
            escape_text(item) for item in ids)) if ids else ""
        parts.append("%d %s %s%s" % (
            count, label, "entry" if count == 1 else "entries",
            id_part))
    lines.append(
        "Limbo: " + "; ".join(parts) + " stand outside both "
        "figures. Ruled entries, Settled entries, and Closed as "
        "decided entries also stand outside both figures, by "
        "decision, except that a Closed as decided entry with a "
        "standing remainder stands in the waiting figure on "
        "account of that remainder and outside the blocking "
        "figure only.")
    fastest = _text(_field(output, "fastest_item",
                           "fastest_item_to_clear"))
    if fastest is None and figures is not None:
        fastest = _text(_field(figures, "fastest_item"))
    lines.append("Fastest item to clear: %s" % escape_text(
        fastest if fastest else "not derivable from the file"))
    return lines


def _counts_block(output):
    lines = [UNITS_KEY_LINE, ""]
    lines.extend(_crosswalk_lines(output))
    if lines[-1] != "":
        lines.append("")
    lines.extend(_census_lines(output))
    lines.append("")
    lines.extend(_reconciliation_lines(output))
    lines.append("")
    appendix = _appendix_lines(output)
    if appendix:
        lines.extend(appendix)
        lines.append("")
    residue = _residue_lines(output)
    if residue:
        lines.extend(residue)
        lines.append("")
    return lines


def render_validate(validate_output):
    """Compose the validate output text from a render model."""
    if _self_check_failed(validate_output) is not None:
        return _failure_output(validate_output, "validate")
    entries = _entries(validate_output)
    lines = _head_lines(validate_output)
    lines.append("")
    lines.extend(_validate_body(validate_output))
    lines.extend(_group_sections(entries, False))
    lines.extend(_counts_block(validate_output))
    lines.extend(_segment_claim_lines(validate_output))
    lines.extend(_figures_lines(validate_output, entries))
    lines.append(_foot_line("validate"))
    return "\n".join(lines) + "\n"


def render_summary(validate_output):
    """Compose the render output text from a render model."""
    if _self_check_failed(validate_output) is not None:
        return _failure_output(validate_output, "render")
    entries = _entries(validate_output)
    lines = _head_lines(validate_output)
    lines.append("")
    lines.append(
        "Layers in order: the entry groups, the supersession "
        "map, the counts, the census, the reconciliation, the "
        "verbatim appendix, the residue list, and the figures. "
        "Each group states the entries it settles; the appendix "
        "carries the phrasings as written.")
    lines.append("")
    lines.extend(_presentation_marking_lines())
    lines.extend(_group_sections(entries, True))
    lines.extend(_chain_lines(validate_output))
    lines.extend(_counts_block(validate_output))
    lines.extend(_segment_claim_lines(validate_output))
    lines.extend(_figures_lines(validate_output, entries))
    lines.append(_foot_line("render"))
    return "\n".join(lines) + "\n"


def render_output(validate_output, form="validate"):
    if form == "render":
        return render_summary(validate_output)
    return render_validate(validate_output)
