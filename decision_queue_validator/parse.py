"""Parse: the Input value and the Limits value, and nothing else.

Parse is a pure function over values in memory. It decodes the raw
bytes as UTF-8, takes the measurements once, enforces the limits at
entry, partitions the lines under the terminator rule, cuts the
spans on the heading forms, collects the status bearing element
inventory in element order, the field occurrences, the decision
blocks, the file header facts, the orphan segments and the parse
notes, and returns either the Queue file model or the file level
failure result. It grades nothing, resolves no contradiction, and
never looks a phrasing up in any vocabulary: the forms are recognised
by their surface forms alone.
"""

import hashlib
import re

from .types import (
    CensusEntry,
    DecisionBlock,
    DistinctPhrasingCount,
    ElementTuple,
    EntryRecord,
    ExitDecision,
    FieldOccurrence,
    FileHeaderFacts,
    FileLevelFailure,
    Finding,
    HeadedEntryCount,
    Input,
    InputValue,
    Limits,
    LimitsValue,
    NearMarkerOccurrence,
    OrphanSegment,
    ParseNote,
    QueueFileModel,
    ReconciliationBlock,
    SegmentClaim,
    Span,
    StatusBearingElement,
    Unit,
    ValidateOutput,
    VerbatimAppendixRow,
    Vocabulary,
)

__all__ = [
    "parse_queue",
    "Input",
    "InputValue",
    "Limits",
    "LimitsValue",
    "Vocabulary",
]

_HEADING_RE = re.compile(r"^(#{1,6}) (.*)$")
_NUMBERED_RE = re.compile(r"^DQ-(\d{3})(?:: | )(\S.*)$")
_UNNUMBERED_RE = re.compile(r"^(R-\d+) (\S.*)$")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_ADDITION_RE = re.compile(
    r"^(?:[A-Za-z]+ )?addition to (DQ-\d{3})\b", re.IGNORECASE)
_LABEL_RE = re.compile(r"^([A-Z][A-Za-z0-9 '&()/.-]{0,58}?):(?:[ ]+(.*)|[ ]*)$")
_DQ_TOKEN_RE = re.compile(r"\bDQ-\d{3}\b")
_R_TOKEN_RE = re.compile(r"\bR-\d+\b")

_STATUS_MARKER = "Status:"
_VARIANT_MARKER = "Status unchanged"

_DISPOSITION_WORDS = {
    "BANKED": "Banked",
    "OPEN": "Open",
    "PRESENTED": "Presented",
    "PARKED": "Parked",
    "RULED": "Ruled",
    "SETTLED": "Settled",
    "CLOSED": "Closed",
}

# Labels whose paragraphs carry entry fields and no prose element.
_FIELD_PARAGRAPH_LABELS = {
    "Owner of record",
    "Source",
    "The question",
    "Question",
    "Options",
    "The options",
    "Cost of deciding late",
    "What it blocks",
    "Ordering reason",
}

# First line labels that open an unheaded labelled paragraph block.
_DECISION_LABELS = {
    "Ruled",
    "Settled",
    "Settlement",
    "Ruled by",
    "Settled by",
    "Decision",
    "Ruling outcome",
    "Outcome of this decision",
    "Form outcome",
    "Addition to",
}

# Single word lead in labels that are named forms of the contract.
_KNOWN_SINGLE_LABELS = {
    "Status", "Ruled", "Settled", "Settlement", "Landing", "Origin",
    "Source", "Options", "Decision", "Remainder", "Condition",
    "Examined", "Question", "Correction", "Addition", "Note",
    "Assessment", "Assessed", "Ruling", "Outcome", "Form", "Her",
    "His", "The", "Captain", "Flag", "Basis", "Where", "Deciding",
    "Governing", "Strictness", "Evidence", "Implementation",
    "Cross-reference", "Per-report", "Partial", "Ruling",
}


def _partition_lines(text):
    """The model lines of a decoded text, under the terminator rule.

    The terminator is a line feed, or a carriage return immediately
    before a line feed, the pair counting as one terminator. A lone
    carriage return is an ordinary character of its line. A final
    line with no terminator is a line, and a terminator at the end
    of the text closes the last line and begins no further line.
    """
    lines = []
    start = 0
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "\n":
            lines.append(text[start:index])
            index += 1
            start = index
        elif char == "\r" and index + 1 < length and \
                text[index + 1] == "\n":
            lines.append(text[start:index])
            index += 2
            start = index
        else:
            index += 1
    if start < length:
        lines.append(text[start:])
    return lines


def _first_word(text):
    match = re.match(r"[A-Za-z]+", text.lstrip())
    return match.group(0) if match else ""


def _disposition_from_value(value):
    """The disposition of a status value, from its opening forms."""
    word = _first_word(value).upper()
    if word in _DISPOSITION_WORDS:
        return _DISPOSITION_WORDS[word]
    if re.search(r"\bRuled by:", value):
        return "Ruled"
    if re.search(r"\bSettled by:", value):
        return "Settled"
    return None


def _find_disposition(text):
    """Find a disposition statement in one line of prose or a block.

    Returns a pair of the disposition and the offset at which the
    statement stands in the line, or None where the line states no
    disposition under the named forms.
    """
    checks = (
        (r"\bSETTLED IN PART\b", "Settled"),
        (r"\bRULED IN (PRINCIPLE|FULL)\b", "Ruled"),
        (r"\b(RULED|Ruled) by\b", "Ruled"),
        (r"\b(SETTLED|Settled) by\b", "Settled"),
        (r"\bis (Ruled|RULED) and closed\b", "Ruled"),
        (r"^(Ruled|RULED)\b", "Ruled"),
        (r"^(Settled|SETTLED|Settlement)\b", "Settled"),
        (r"^(Closed|CLOSED)\b", "Closed"),
        (r"^(Banked)\b", "Banked"),
        (r"^(Parked)\b", "Parked"),
        (r"^(Presented)\b", "Presented"),
        (r"^(Open)\b", "Open"),
        (r"\bdecided by assessment\b", "Closed"),
        (r"\bRULED, closed\b", "Ruled"),
        (r"\bRuled:\s", "Ruled"),
        (r"\bSettled:\s", "Settled"),
        (r"\bcloses in full\b", "Closed"),
        (r"\bitem closes\b", "Closed"),
        (r"\bis closed\b", "Closed"),
        (r"\bClosed\.\s*$", "Closed"),
        (r"\bstays banked\b", "Banked"),
        (r"\bremains banked\b", "Banked"),
        (r"\bstill banked\b", "Banked"),
        (r"\bnot finished\b", "Open"),
        (r"\bremains open\b", "Open"),
        (r"\bstays open\b", "Open"),
    )
    best = None
    for priority, (pattern, disposition) in enumerate(checks):
        match = re.search(pattern, text)
        if not match:
            continue
        candidate = (match.start(), priority, disposition)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        return None
    return best[2], best[0]


def _decider_from_text(text):
    """The decider category and decider text a statement names."""
    if re.search(r"by the Manager\b", text) or \
            re.search(r"(Settled|SETTLED) by:? The Manager\b", text) or \
            re.search(r"by a (decision|pick) of the Manager\b", text):
        named = re.search(r"The Manager \(Muse\)[^.]*", text)
        if named:
            return "a Manager grant form", named.group(0).rstrip()
        return "a Manager grant form", "The Manager"
    if re.search(r"(RULED|Ruled) by:? Captain JP\b", text):
        return "Captain JP", "Captain JP"
    if "DQ-148" in text and re.search(r"[Aa]ssessment", text):
        return "assessment by cross reference", "assessment under DQ-148"
    named = re.search(r"(?:Ruled|Settled) by:? ([A-Z][A-Za-z .]+?)(?:,|\.|$)",
                      text)
    if named:
        return "another named source", named.group(1).strip()
    if "Captain JP" in text and re.search(r"\b(Ruled|RULED)\b", text) and \
            "in her words" in text:
        return "Captain JP", "Captain JP"
    return None, None


def _remainder_from_text(text):
    """The remainder text a statement names, or None."""
    labelled = re.search(r"^Remainder:[ ]*(.+)$", text, re.MULTILINE)
    if labelled:
        return labelled.group(1).strip()
    banked = re.search(r"[Ww]hat stays banked:[ ]*(.+)", text, re.DOTALL)
    if banked:
        value = banked.group(1).strip()
        if value.endswith("."):
            value = value[:-1]
        return value
    leaving = re.search(r"\bleaving (.+?) (open|undecided)\b", text)
    if leaving:
        return leaving.group(1).strip()
    if re.search(r"[Tt]he remainder stays banked", text):
        return "The remainder stays banked"
    return None


def _condition_from_text(text):
    """The condition text a statement carries, or None."""
    labelled = re.search(r"^Condition:[ ]*(.+)$", text, re.MULTILINE)
    if labelled:
        return labelled.group(1).strip()
    for marker in ("conditional on", "subject to"):
        at = text.find(marker)
        if at >= 0:
            value = text[at + len(marker):].strip()
            if value.endswith("."):
                value = value[:-1]
            return value
    return None


def _scope_of(text, remainder):
    if re.search(r"in part", text, re.IGNORECASE):
        if remainder is not None:
            return "Part with a named remainder"
        return "Part with no remainder named"
    return "Whole"


def _make_element(kind, verbatim, disposition, line, position,
                  occurrence_kind, own_text, statement=None,
                  decision_block=None, decider_text_override=None):
    remainder = _remainder_from_text(own_text)
    condition = _condition_from_text(own_text)
    scope = _scope_of(own_text, remainder)
    decider, decider_text = _decider_from_text(own_text)
    if decider_text_override is not None:
        decider_text = decider_text_override
    core = ElementTuple(
        disposition=disposition,
        scope=scope,
        condition=condition,
        decider=decider,
        line=line,
    )
    return StatusBearingElement(
        kind=kind,
        verbatim=verbatim,
        tuple=core,
        line=line,
        position_in_line=position,
        occurrence_kind=occurrence_kind,
        remainder_text=remainder,
        decider_text=decider_text,
        statement=statement if statement is not None else verbatim,
        decision_block=decision_block,
        line_span=Span(line, line, "heading cut"),
    )


def _is_near_marker(text):
    """The three near marker forms, and no other."""
    if re.match(r"^Status[ ]+:", text):
        return True
    if re.match(r"^Status;", text):
        return True
    match = re.match(r"^([A-Za-z]+):", text)
    if match and match.group(1).lower() == "status" and \
            match.group(1) != "Status":
        return True
    return False


def _heading_info(line_text):
    match = _HEADING_RE.match(line_text)
    if not match:
        return None
    return len(match.group(1)), match.group(2)


def _numbered_heading(text):
    match = _NUMBERED_RE.match(text)
    if not match:
        return None
    return "DQ-" + match.group(1), int(match.group(1)), match.group(2)


def _unnumbered_heading(text):
    match = _UNNUMBERED_RE.match(text)
    if not match:
        return None
    return match.group(1), match.group(2)


def _is_note_section(text):
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return False
    lowered = [word.lower() for word in words]
    if lowered[0] in ("note", "notes"):
        return True
    if len(lowered) >= 2 and lowered[0] == "amendment" and \
            lowered[1] == "note":
        return True
    if "note" in lowered or "notes" in lowered:
        return True
    return False


def _failure(kinds, name, byte_count, line_count, digest,
             breached=None, missing=None):
    breached_limit = None
    measured = None
    breached_limits = []
    breached_measured_values = {}
    if breached:
        breached_limits = [item[0] for item in breached]
        breached_limit = breached[0][0]
        measured = breached[0][1]
        breached_measured_values = {
            item[0]: item[1] for item in breached}
    decision = ExitDecision(code=3, reason_classes=list(kinds))
    return FileLevelFailure(
        failure_kinds=list(kinds),
        input_name=name,
        byte_count=byte_count,
        line_count=line_count,
        digest=digest,
        breached_limit=breached_limit,
        measured_value=measured,
        breached_limits=breached_limits,
        breached_measured_values=breached_measured_values,
        missing_structure=missing,
        exit_decision=decision,
    )


class _EntryBuilder:
    """Collects the fields, blocks and elements of one entry."""

    def __init__(self, record, lines_by_number):
        self.record = record
        self.lines_by_number = lines_by_number
        self.elements = []
        self.blocks = []
        self.fields = []
        self.notes = []
        self.near = []
        self.seen_line_start = False
        self.closing_status_line = None
        self.closing_status_block = None
        self.closed_seen = False

    def line_text(self, number):
        return self.lines_by_number[number]

    def add_field_lines(self, numbered_lines):
        for number, text in numbered_lines:
            if text.startswith("#") or text.startswith("- "):
                continue
            if text.startswith(_STATUS_MARKER) or _is_near_marker(text):
                continue
            match = _LABEL_RE.match(text)
            if not match:
                continue
            label = match.group(1).strip()
            if "," in label or "." in label or ";" in label:
                continue
            if len(re.findall(r"\S+", label)) > 7:
                continue
            value = match.group(2) or ""
            self.fields.append(
                FieldOccurrence(label=label, value=value, line=number))

    def scan_line_occurrences(self, number, text, decision_block=None):
        """Collect the marker occurrences of one line.

        Returns True where the line is a line start Status line.
        """
        if _is_near_marker(text):
            self.near.append(
                NearMarkerOccurrence(line=number, text=text))
            return False
        if text.startswith("Origin:"):
            return self._scan_origin_line(number, text, decision_block)
        starts = []
        for match in re.finditer(re.escape(_VARIANT_MARKER), text):
            starts.append((match.start(), "variant", match.end()))
        for match in re.finditer(re.escape(_STATUS_MARKER), text):
            starts.append((match.start(), "marker", match.end()))
        starts.sort()
        is_line_start = False
        for index, (start, flavour, end) in enumerate(starts):
            stop = starts[index + 1][0] if index + 1 < len(starts) \
                else len(text)
            if flavour == "variant":
                verbatim = text[start:stop]
                if stop < len(text):
                    verbatim = verbatim.rstrip(" ")
                self.elements.append(_make_element(
                    kind="variant phrasing",
                    verbatim=verbatim,
                    disposition="Relative",
                    line=number,
                    position=start,
                    occurrence_kind="variant",
                    own_text=verbatim,
                    decision_block=decision_block,
                ))
                continue
            value = text[end:stop].lstrip(" ")
            if stop < len(text):
                value = value.rstrip(" ")
            disposition = _disposition_from_value(value)
            if start == 0:
                is_line_start = True
                if self.seen_line_start:
                    kind = "later Status line"
                else:
                    kind = "head Status line"
                    self.seen_line_start = True
                occurrence = "line start"
            else:
                kind = "embedded status value"
                occurrence = "embedded"
            element = _make_element(
                kind=kind,
                verbatim=value,
                disposition=disposition,
                line=number,
                position=start,
                occurrence_kind=occurrence,
                own_text=value,
                decision_block=decision_block,
            )
            self.elements.append(element)
            if start == 0 and kind == "later Status line" and \
                    disposition in ("Ruled", "Settled", "Closed"):
                self.closing_status_line = number
                self.closing_status_block = decision_block
        return is_line_start

    def _scan_origin_line(self, number, text, decision_block=None):
        body = text[len("Origin:"):]
        has_marker = _STATUS_MARKER in body
        has_decider_form = bool(
            re.search(r"\b(Ruled|Settled) by:", body))
        if not has_marker and not has_decider_form:
            return False
        if has_marker:
            at = body.find(_STATUS_MARKER)
            value = body[at + len(_STATUS_MARKER):].lstrip(" ")
            self.elements.append(_make_element(
                kind="Origin line matter",
                verbatim=value,
                disposition=_disposition_from_value(value),
                line=number,
                position=len("Origin:") + at,
                occurrence_kind="embedded",
                own_text=value,
                decision_block=decision_block,
            ))
        else:
            found = _find_disposition(body)
            disposition = found[0] if found else None
            self.elements.append(_make_element(
                kind="Origin line matter",
                verbatim=body.lstrip(" "),
                disposition=disposition,
                line=number,
                position=len("Origin:"),
                occurrence_kind=None,
                own_text=body,
                decision_block=decision_block,
            ))
        return False

    def note_unrecognised_lead_in(self, paragraph):
        number, text = paragraph[0]
        match = re.match(r"^([A-Z][A-Za-z]+):[ ]", text)
        if not match:
            return
        label = match.group(1)
        if label in _KNOWN_SINGLE_LABELS:
            return
        span = Span(paragraph[0][0], paragraph[-1][0], "heading cut")
        self.notes.append(ParseNote(
            kind="unrecognised label form",
            text="a paragraph begins with the label " + label +
                 ", which is no named label form; its matter is body "
                 "text only",
            line_span=span,
            entry_identifier=self.record.identifier or
            self.record.heading,
        ))

    def process_paragraph(self, paragraph, decision_block=None,
                          in_block_segment=False):
        """Process one plain paragraph outside any block segment."""
        if not paragraph:
            return
        self.assessment_closure_element(paragraph, decision_block)
        first_number, first_text = paragraph[0]
        if self.closing_status_line is not None and \
                first_number > self.closing_status_line and \
                decision_block is None:
            self.record.post_status_blocks = True
        produced_line_start = False
        for number, text in paragraph:
            if self.scan_line_occurrences(number, text, decision_block):
                produced_line_start = True
        self.add_field_lines(paragraph)
        self.note_unrecognised_lead_in(paragraph)
        if produced_line_start:
            return
        label_match = _LABEL_RE.match(first_text)
        label = label_match.group(1).strip() if label_match else ""
        if label in _FIELD_PARAGRAPH_LABELS:
            return
        found = None
        found_line = None
        for number, text in paragraph:
            hit = _find_disposition(text)
            if hit:
                found = hit
                found_line = (number, text)
                break
        if not found:
            return
        disposition, offset = found
        number, text = found_line
        joined = "\n".join(item[1] for item in paragraph)
        if label in _DECISION_LABELS or \
                first_text.startswith("Addition to") or \
                first_text.startswith("Decision under"):
            block = DecisionBlock(
                marking_form="unheaded labelled paragraph",
                span=Span(paragraph[0][0], paragraph[-1][0],
                          "heading cut"),
                heading_text=None,
                post_status_flag=bool(
                    self.closing_status_line is not None and
                    paragraph[0][0] > self.closing_status_line),
            )
            self.blocks.append(block)
            block_index = len(self.blocks) - 1
            element = _make_element(
                kind="decision block matter",
                verbatim=text,
                disposition=disposition,
                line=number,
                position=offset,
                occurrence_kind=None,
                own_text=joined,
                statement=text,
                decision_block=block_index,
                decider_text_override=None,
            )
            block.elements.append(element)
            self.elements.append(element)
        else:
            element = _make_element(
                kind="closing prose",
                verbatim=text,
                disposition=disposition,
                line=number,
                position=offset,
                occurrence_kind=None,
                own_text=joined,
                statement=text,
                decision_block=decision_block,
            )
            self.elements.append(element)
        if disposition == "Closed":
            self.closed_seen = True
        self._terminal_closure_element(paragraph, joined)

    def _terminal_closure_element(self, paragraph, joined):
        """A plain paragraph that ends on its own closure sentence.

        Where a paragraph carries an earlier disposition statement
        and then closes itself with a final closure sentence, the
        closure is its own element, positioned at the sentence.
        """
        stripped = joined.rstrip()
        match = re.search(
            r"(?:^|\.\s)(Closed\.|This (?:item|entry) is closed\.)\s*$",
            stripped)
        if not match:
            return
        if self.elements and self.elements[-1].tuple[0] == "Closed":
            return
        for number, text in reversed(paragraph):
            at = text.find("Closed.")
            if at >= 0:
                element = _make_element(
                    kind="closing prose",
                    verbatim=text,
                    disposition="Closed",
                    line=number,
                    position=at,
                    occurrence_kind=None,
                    own_text=text,
                    statement=text,
                )
                self.elements.append(element)
                self.closed_seen = True
                return

    def process_block(self, heading_text, numbered_lines):
        """Process one H4 sub part block of the entry."""
        block = DecisionBlock(
            marking_form="H4 sub part",
            span=Span(numbered_lines[0][0] if numbered_lines else 0,
                      numbered_lines[-1][0] if numbered_lines else 0,
                      "heading cut"),
            heading_text=heading_text,
            post_status_flag=bool(
                self.closing_status_line is not None and
                numbered_lines and
                numbered_lines[0][0] > self.closing_status_line and
                self.closing_status_block != len(self.blocks)),
        )
        self.blocks.append(block)
        block_index = len(self.blocks) - 1
        if block.post_status_flag:
            self.record.post_status_blocks = True
        body = numbered_lines[1:]
        self.add_field_lines(body)
        segment = []

        def flush_segment(run):
            if not run:
                return
            self.assessment_closure_element(run, block_index)
            if self.closing_status_line is not None and \
                    self.closing_status_block == block_index:
                for number, text in run:
                    if number > self.closing_status_line and \
                            re.match(r"^(Implementation addition:|"
                                     r"Addition to|Correction)", text):
                        self.record.post_status_blocks = True
            for number, text in run:
                self.scan_line_occurrences(number, text, block_index)
            found = None
            found_line = None
            for number, text in run:
                hit = _find_disposition(text)
                if hit:
                    found = hit
                    found_line = (number, text)
                    break
            if not found:
                return
            disposition, offset = found
            number, text = found_line
            joined = "\n".join(item[1] for item in run)
            own = (heading_text or "") + "\n" + joined
            element = _make_element(
                kind="decision block matter",
                verbatim=text,
                disposition=disposition,
                line=number,
                position=offset,
                occurrence_kind=None,
                own_text=own,
                statement=text,
                decision_block=block_index,
            )
            block.elements.append(element)
            self.elements.append(element)
            if disposition == "Closed":
                self.closed_seen = True

        for number, text in body:
            if text.startswith(_STATUS_MARKER):
                flush_segment(segment)
                segment = []
                self.scan_line_occurrences(number, text, block_index)
            else:
                segment.append((number, text))
        flush_segment(segment)
        for element in self.elements:
            if element.decision_block == block_index:
                block.elements.append(element) \
                    if element not in block.elements else None
        return block

    def assessment_closure_element(self, numbered_lines,
                                   decision_block=None):
        """The pin 14 assessment closure element of a paragraph.

        A paragraph carrying an explicit statement of closure in
        the form Closed as decided under DQ-148 bears that closure
        as an element of its entry: disposition Closed, decider
        assessment by cross reference, at the closure line.
        """
        for number, text in numbered_lines:
            at = text.find("Closed as decided under DQ-148")
            if at < 0:
                continue
            for element in self.elements:
                if element.line == number and \
                        element.tuple[0] == "Closed":
                    return
            core = ElementTuple(
                disposition="Closed",
                scope="Whole",
                condition=None,
                decider="assessment by cross reference",
                line=number,
            )
            self.elements.append(StatusBearingElement(
                kind="closing prose",
                verbatim=text,
                tuple=core,
                line=number,
                position_in_line=at,
                occurrence_kind=None,
                remainder_text=None,
                decider_text="assessment under DQ-148",
                statement=text,
                decision_block=decision_block,
                line_span=Span(number, number, "heading cut"),
            ))
            self.closed_seen = True
            return

    def attach_remainders_and_conditions(self, numbered_lines):
        """Attach Remainder and Condition label lines to an element."""
        ordered = sorted(
            self.elements, key=lambda item: (item.line,
                                             item.position_in_line))
        for number, text in numbered_lines:
            kind = None
            value = None
            if text.startswith("Remainder:"):
                kind = "remainder"
                value = text[len("Remainder:"):].strip()
            elif text.startswith("Condition:"):
                kind = "condition"
                value = text[len("Condition:"):].strip()
            elif text.strip().startswith("Item closed") or \
                    "closed, subject to" in text:
                index = text.find("subject to")
                if index < 0:
                    continue
                value = text[index + len("subject to"):].strip()
                value = value.split(";")[0].strip().rstrip(".")
                if not value:
                    continue
                kind = "condition"
            if kind is None:
                continue
            target = None
            for element in ordered:
                if element.line < number:
                    target = element
                else:
                    break
            if target is None:
                continue
            if kind == "remainder" and target.remainder_text is None:
                target.remainder_text = value
                scope = target.tuple[1]
                if scope.startswith("Part"):
                    target.tuple = target.tuple._replace(
                        scope="Part with a named remainder")
            elif kind == "condition" and target.tuple[2] is None:
                target.tuple = target.tuple._replace(condition=value)


def _paragraphs(numbered_lines):
    """Split numbered lines into paragraphs on blank lines."""
    paragraphs = []
    current = []
    for item in numbered_lines:
        if item[1].strip() == "":
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append(item)
    if current:
        paragraphs.append(current)
    return paragraphs


def parse_queue(input_value, limits):
    """Parse the Input value under the Limits value.

    Returns the Queue file model, or the file level failure result
    where no model exists for the file.
    """
    raw = input_value.raw_bytes
    name = input_value.input_name
    byte_count = len(raw)
    digest = hashlib.sha256(raw).hexdigest()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        kinds = []
        breached = []
        if byte_count > limits.max_bytes:
            kinds.append("byte limit breach")
            breached.append(("max bytes", byte_count))
        kinds.append("invalid bytes")
        return _failure(kinds, name, byte_count, None, digest,
                        breached=breached)

    lines = _partition_lines(text)
    line_count = len(lines)
    longest = 0
    for line in lines:
        if len(line) > longest:
            longest = len(line)

    breached = []
    kinds = []
    if byte_count > limits.max_bytes:
        kinds.append("byte limit breach")
        breached.append(("max bytes", byte_count))
    if line_count > limits.max_lines:
        kinds.append("line limit breach")
        breached.append(("max lines", line_count))
    if longest > limits.max_characters_per_line:
        kinds.append("per line limit breach")
        breached.append(("max characters per line", longest))
    if kinds:
        line_field = None if byte_count > limits.max_bytes \
            else line_count
        return _failure(kinds, name, byte_count, line_field, digest,
                        breached=breached)

    if line_count == 0:
        return _failure(
            ["empty file"], name, byte_count, 0, digest,
            missing="the file is empty: no queue header and no entry "
                    "heading is present")

    headings = []
    for index, line in enumerate(lines):
        info = _heading_info(line)
        if info is not None:
            headings.append((index + 1, info[0], info[1]))

    first_heading = headings[0] if headings else None
    # Brief section 5.3: the file header test is level and first
    # position only, with its text not tested. Any first heading at
    # level 1 is the queue header, whatever words it carries.
    queue_header_present = bool(
        first_heading and first_heading[1] == 1)

    def entry_form(level, heading_text):
        if level in (2, 3):
            numbered = _numbered_heading(heading_text)
            if numbered:
                return ("numbered", numbered)
        if level == 3:
            unnumbered = _unnumbered_heading(heading_text)
            if unnumbered:
                return ("unnumbered", unnumbered)
        return None

    has_entry_heading = any(
        entry_form(level, heading_text)
        for _number, level, heading_text in headings)

    if not has_entry_heading and not queue_header_present:
        return _failure(
            ["no recognisable queue structure"], name, byte_count,
            line_count, digest,
            missing="no queue header and no entry heading "
                    "is present")
    if not has_entry_heading and queue_header_present:
        return _failure(
            ["header only"], name, byte_count, line_count, digest,
            missing="a queue header is present but no entry heading "
                    "in a numbered or unnumbered entry heading form "
                    "is present")

    def is_section_introduction(position):
        number, level, heading_text = headings[position]
        for later in headings[position + 1:]:
            if later[1] == 2:
                stop = later[0]
                break
        else:
            stop = line_count + 1
        for other in headings[position + 1:]:
            if other[0] >= stop:
                break
            if entry_form(other[1], other[2]):
                return True
        return False

    starts = []
    started = False
    current_kind = "file header"
    for position, (number, level, heading_text) in enumerate(headings):
        form = entry_form(level, heading_text)
        if form:
            starts.append((number, "entry", (level, heading_text, form)))
            started = True
            current_kind = "entry"
            continue
        if level == 1:
            if position == 0:
                continue
            starts.append((number, "orphan unmatched",
                           (level, heading_text, None)))
            started = True
            current_kind = "orphan"
            continue
        if level == 2:
            if _is_note_section(heading_text):
                starts.append((number, "orphan note",
                               (level, heading_text, None)))
                started = True
                current_kind = "orphan"
                continue
            if is_section_introduction(position):
                starts.append((number, "section introduction",
                               (level, heading_text, None)))
                started = True
                current_kind = "section introduction"
                continue
            if not started:
                continue
            starts.append((number, "orphan unmatched",
                           (level, heading_text, None)))
            started = True
            current_kind = "orphan"
            continue
        if level == 4 and current_kind == "entry":
            continue
        starts.append((number, "orphan unmatched",
                       (level, heading_text, None)))
        started = True
        current_kind = "orphan"

    units = []
    unit_ranges = []
    if starts and starts[0][0] > 1:
        unit_ranges.append((1, starts[0][0] - 1, "file header", None))
    elif not starts:
        unit_ranges.append((1, line_count, "file header", None))
    for index, (number, kind, info) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) \
            else line_count
        unit_ranges.append((number, end, kind, info))

    lines_by_number = {}
    for index, line in enumerate(lines):
        lines_by_number[index + 1] = line

    entries = []
    entries_by_id = {}
    orphans = []
    parse_notes = []
    h4_count = 0
    current_section = None
    builders = {}

    for start, end, kind, info in unit_ranges:
        span = Span(start, end, "heading cut")
        if kind == "section introduction":
            current_section = info[1]
            units.append(Unit(kind="section introduction", span=span,
                              heading_text=info[1]))
            continue
        if kind == "file header":
            heading_text = None
            if first_heading and first_heading[0] >= start and \
                    first_heading[0] <= end:
                heading_text = first_heading[2]
            units.append(Unit(kind="file header", span=span,
                              heading_text=heading_text))
            continue
        if kind in ("orphan note", "orphan unmatched"):
            level, heading_text, _form = info
            if kind == "orphan note":
                lowered = heading_text.lower()
                if lowered.startswith("amendment note"):
                    orphan_kind = "amendment note section"
                else:
                    orphan_kind = "file level note section"
                unmatched = False
            else:
                orphan_kind = "another file level segment"
                unmatched = True
            segment_lines = [(number, lines_by_number[number])
                             for number in range(start, end + 1)]
            named = []
            for _number, segment_text in segment_lines:
                for token in _DQ_TOKEN_RE.findall(segment_text):
                    if token not in named:
                        named.append(token)
                for token in _R_TOKEN_RE.findall(segment_text):
                    if token not in named:
                        named.append(token)
            claims = []
            segment_joined = "\n".join(
                item[1] for item in segment_lines)
            if "governs" in segment_joined:
                statement = ""
                for _number, segment_text in segment_lines:
                    if "governs" in segment_text:
                        statement = segment_text
                        break
                claim_named = []
                for _number, segment_text in segment_lines:
                    if segment_text.startswith("- "):
                        for token in _DQ_TOKEN_RE.findall(segment_text):
                            if token not in claim_named:
                                claim_named.append(token)
                claims.append(SegmentClaim(
                    named_entries=claim_named or named,
                    statement=statement))
            segment = OrphanSegment(
                kind=orphan_kind,
                span=span,
                heading_text=heading_text,
                named_entries=named,
                claims=claims,
                unmatched_heading=unmatched,
                lines=segment_lines,
            )
            orphans.append(segment)
            units.append(Unit(kind="orphan segment", span=span,
                              heading_text=heading_text))
            if unmatched:
                parse_notes.append(ParseNote(
                    kind="unmatched heading",
                    text="the heading " + heading_text +
                         " matches no entry form, no known file "
                         "level form and no sub part form; its lines "
                         "stand in an orphan segment",
                    line_span=Span(start, start, "heading cut"),
                ))
            continue
        level, heading_text, form = info
        form_kind, form_data = form
        if form_kind == "numbered":
            identifier = form_data[0]
            title = form_data[2]
        else:
            identifier = None
            title = form_data[1]
        record = EntryRecord(
            identifier=identifier,
            heading=heading_text,
            heading_level=level,
            heading_line=start,
            title=title,
            spans=[span],
            section=current_section,
        )
        entries.append(record)
        if identifier is not None:
            entries_by_id.setdefault(identifier, record)
        units.append(Unit(kind="entry", span=span,
                          heading_text=heading_text,
                          entry_identifier=identifier))
        builders[start] = _EntryBuilder(record, lines_by_number)

    for index, line in enumerate(lines):
        info = _heading_info(line)
        if info and info[0] == 4:
            number = index + 1
            for start, end, kind, _info in unit_ranges:
                if kind == "entry" and start <= number <= end:
                    h4_count += 1
                    break

    pending_additions = []
    for start, end, kind, info in unit_ranges:
        if kind != "entry":
            continue
        builder = builders[start]
        record = builder.record
        body = [(number, lines_by_number[number])
                for number in range(start + 1, end + 1)]
        record.body_lines = list(body)
        chunks = []
        chunk = []
        block = None
        for item in body:
            info_line = _heading_info(item[1])
            if info_line and info_line[0] == 4:
                if block is not None:
                    chunks.append(("block", block))
                elif chunk:
                    chunks.append(("plain", chunk))
                chunk = []
                block = [item]
            elif block is not None:
                block.append(item)
            else:
                chunk.append(item)
        if block is not None:
            chunks.append(("block", block))
        elif chunk:
            chunks.append(("plain", chunk))

        for chunk_kind, chunk_lines in chunks:
            if chunk_kind == "block":
                heading_text = _heading_info(chunk_lines[0][1])[1]
                builder.process_block(heading_text, chunk_lines)
                continue
            for paragraph in _paragraphs(chunk_lines):
                first_text = paragraph[0][1]
                addition = _ADDITION_RE.match(first_text)
                if addition and addition.group(1) != record.identifier:
                    pending_additions.append(
                        (addition.group(1), paragraph, record))
                    continue
                if addition and builder.closed_seen:
                    continue
                if first_text.startswith("Correction") and \
                        builder.closed_seen:
                    continue
                builder.process_paragraph(paragraph)

    for target_id, paragraph, source_record in pending_additions:
        target = entries_by_id.get(target_id)
        if target is None:
            continue
        span = Span(paragraph[0][0], paragraph[-1][0],
                    "label reattachment", True)
        target.spans.append(span)
        target.body_lines = sorted(
            target.body_lines + list(paragraph),
            key=lambda item: item[0])
        note = ParseNote(
            kind="label reattachment",
            text="a paragraph labelled for " + target_id +
                 " stands outside its span and is reattached to it",
            line_span=Span(paragraph[0][0], paragraph[-1][0],
                           "label reattachment", True),
            entry_identifier=target_id,
        )
        parse_notes.append(note)
        target.parse_notes.append(note)
        builder = builders[target.heading_line]
        if not builder.closed_seen:
            builder.process_paragraph(paragraph)
        source_record.body_lines = [
            item for item in source_record.body_lines
            if not (paragraph[0][0] <= item[0] <= paragraph[-1][0])]

    for start, end, kind, info in unit_ranges:
        if kind != "entry":
            continue
        builder = builders[start]
        record = builder.record
        heading_match = re.search(
            r"(RULED|Ruled|SETTLED|Settled) by ([^.]+?)"
            r"( \d{4}-\d{2}-\d{2})?\s*$", record.heading)
        if heading_match:
            prefix = "#" * record.heading_level + " "
            element = _make_element(
                kind="heading borne evidence",
                verbatim=record.heading,
                disposition=_DISPOSITION_WORDS[
                    heading_match.group(1).upper()],
                line=record.heading_line,
                position=len(prefix) + heading_match.start(),
                occurrence_kind=None,
                own_text=record.heading,
                statement=record.heading,
            )
            builder.elements.append(element)
        builder.elements.sort(
            key=lambda item: (item.line, item.position_in_line))
        record.status_elements = builder.elements
        record.decision_blocks = builder.blocks
        record.fields = builder.fields
        record.near_marker_occurrences = builder.near
        record.parse_notes = record.parse_notes + builder.notes
        parse_notes.extend(builder.notes)
        builder.attach_remainders_and_conditions(record.body_lines)
        body_present = any(
            text.strip() != "" for _number, text in record.body_lines
            if _number > record.heading_line and
            not any(span.boundary_basis == "label reattachment" and
                    span.start_line <= _number <= span.end_line
                    for span in record.spans[1:]))
        record.unparsed = not body_present
        date = _DATE_RE.search(record.heading)
        if date:
            record.date_text = date.group(0)
        else:
            for _number, text in record.body_lines:
                if text.startswith(("Source:", "Origin:", "Ruled by:",
                                    "Settled by:")):
                    found_date = _DATE_RE.search(text)
                    if found_date:
                        record.date_text = found_date.group(0)
                        break

    unit_counts = {
        "entry": 0,
        "orphan_segment": 0,
        "file_header": 0,
        "section_introduction": 0,
    }
    for unit in units:
        if unit.kind == "entry":
            unit_counts["entry"] += 1
        elif unit.kind == "orphan segment":
            unit_counts["orphan_segment"] += 1
        elif unit.kind == "file header":
            unit_counts["file_header"] += 1
        elif unit.kind == "section introduction":
            unit_counts["section_introduction"] += 1

    stated_vocabulary = None
    for unit in units:
        if unit.kind != "file header":
            continue
        for number in range(unit.span.start_line,
                            unit.span.end_line + 1):
            if "vocabulary" in lines_by_number[number].lower():
                stated_vocabulary = lines_by_number[number]
                break
        break

    facts = FileHeaderFacts(
        input_name=name,
        stated_vocabulary=stated_vocabulary,
        byte_count=byte_count,
        line_count=line_count,
        longest_line_length=longest,
        digest=digest,
        limits=limits,
        vocabulary_version=None,
        unit_counts=unit_counts,
    )
    return QueueFileModel(
        header_facts=facts,
        units=units,
        entries=entries,
        orphan_segments=orphans,
        parse_notes=parse_notes,
        unassigned_lines=[],
        double_assigned_lines=[],
        h4_sub_heading_count=h4_count,
        lines=lines,
        unmatched_headings=[
            segment for segment in orphans if segment.unmatched_heading],
    )
