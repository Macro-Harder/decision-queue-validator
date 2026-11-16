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
import sys

from .types import (
    DQNumber,
    DecisionBlock,
    ElementTuple,
    EntryRecord,
    ExitDecision,
    FieldOccurrence,
    FileHeaderFacts,
    FileLevelFailure,
    Input,
    InputValue,
    Limits,
    LimitsValue,
    NearMarkerOccurrence,
    OrphanSegment,
    ParseNote,
    QueueFileModel,
    SegmentClaim,
    Span,
    StatusBearingElement,
    Unit,
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
_NUMBERED_RE = re.compile(r"^DQ-(\d+): (\S.*)$")
_NAMED_UNNUMBERED_HEADING = "R-7 closure conflict"
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_ADDITION_RE = re.compile(
    r"^(?:[A-Za-z]+ )?addition to (DQ-\d{3})\b", re.IGNORECASE)
_LABEL_RE = re.compile(r"^([A-Z][A-Za-z0-9 '&()/.-]{0,58}?):(?:[ ]+(.*)|[ ]*)$")
_BOLD_LEAD_RE = re.compile(r"^\*\*(.+?)\*\*")
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
# The set is the recorded label list at brief section 5.2, PIN-01,
# form 2: labels of the ruling, settlement, assessment, and outcome
# families in their recorded forms.
_DECISION_LABELS = {
    "Ruled",
    "Settled",
    "Settlement",
    "Ruled by",
    "Settled by",
    "Decision",
    "Ruling text",
    "Ruling texts",
    "Ruling outcome",
    "Outcome of this decision",
    "Form outcome",
    "Addition to",
}

# The disposition a recorded label form itself carries, where the
# labelled matter states no disposition of its own: the matter
# under the label performs the act the label names, under PIN-01,
# form 2. A label standing in the decision set with no entry here,
# the Decision label, carries no disposition from its form.
_LABEL_DISPOSITIONS = {
    "Ruled": "Ruled",
    "Ruled by": "Ruled",
    "Ruling text": "Ruled",
    "Ruling texts": "Ruled",
    "Ruling outcome": "Ruled",
    "Outcome of this decision": "Ruled",
    "Form outcome": "Ruled",
    "Settled": "Settled",
    "Settled by": "Settled",
    "Settlement": "Settled",
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
    """The disposition of a status value, from its opening forms.

    The disposition is read from the surface forms of the value
    alone: its opening word, or a Ruled by or Settled by form it
    carries. A value whose opening forms state no disposition
    takes no disposition here. Parse holds no vocabulary mapping
    and performs no translation: the translation of a verbatim
    phrasing to a canonical family, and every mapping to a
    canonical state, is validate work under the seam at plan
    Item 3, section 3.5, and a phrasing parse cannot read stands
    in the element list with no disposition, under PIN-04.
    """
    word = _first_word(value).upper()
    if word in _DISPOSITION_WORDS:
        return _DISPOSITION_WORDS[word]
    if re.search(r"\bRuled by:", value):
        return "Ruled"
    if re.search(r"\bSettled by:", value):
        return "Settled"
    return None


def _find_disposition(text, start=0):
    """Find a disposition statement in one line of prose or a block.

    Returns a pair of the disposition and the offset at which the
    statement stands in the line, or None where the line states no
    disposition under the named forms. The search runs from the
    given offset, and the offset it returns is absolute in the line.
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
        (r"\bfurther [Rr]uled\b", "Ruled"),
        (r"\bfurther [Ss]ettled\b", "Settled"),
        (r"\b[Ss]ettled this entry\b", "Settled"),
        (r"\b[Rr]uled this entry\b", "Ruled"),
        (r"\bhas set the outstanding values\b", "Settled"),
        (r"\blimb of this entry is [Rr]uled\b", "Ruled"),
        (r"\blimb of this entry is [Ss]ettled\b", "Settled"),
    )
    best = None
    for priority, (pattern, disposition) in enumerate(checks):
        match = re.search(pattern, text[start:])
        if not match:
            continue
        candidate = (start + match.start(), priority, disposition)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        return None
    return best[2], best[0]


def _sentence_spans(text):
    """The sentence spans of a text, as start and end offsets.

    A sentence ends at a period followed by a space, the period
    standing inside its own sentence, or at the end of the text.
    """
    spans = []
    start = 0
    index = text.find(". ", start)
    while index >= 0:
        spans.append((start, index + 1))
        start = index + 2
        index = text.find(". ", start)
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def _marked_statement(sentence):
    """Whether a sentence opens in a marked statement form.

    The marked forms are the ones PIN-01 names as carrying a
    statement at their head: a contained Status line form, a bold
    lead in start, or a recorded decision label. A sentence that
    opens in plain prose and only describes a state further in, as
    a remainder sentence does, carries no statement of its own:
    its matter belongs to the statement it follows, under the part
    and remainder machinery. A bare closure sentence forms no
    statement either: the terminal closure machinery owns that
    position, and inside a block segment it formed no element in
    the recorded reading.
    """
    stripped = sentence.strip()
    if stripped.startswith("Status:") or stripped.startswith("**"):
        return True
    label_match = _LABEL_RE.match(stripped)
    if label_match and \
            label_match.group(1).strip() in _DECISION_LABELS:
        return True
    return False


_MARKED_STATEMENT_WORD_RE = re.compile(
    r"(Ruled|Settled|Banked|Parked|Presented|Open|"
    r"RULED|SETTLED|BANKED)\b")


def _weak_marked_statement(sentence):
    """Whether a sentence opens with a bare disposition word.

    The weak marked form: a sentence whose first word is itself a
    disposition word, as a line standing as Ruled. or Settled in
    part. A closure word does not open a weak statement, for the
    reason _marked_statement states.
    """
    if _marked_statement(sentence):
        return True
    stripped = sentence.strip()
    return _MARKED_STATEMENT_WORD_RE.match(stripped) is not None


def _find_disposition_statements(text):
    """Every disposition statement in one line, in statement order.

    Returns a list of triples: the disposition, the offset at which
    its statement stands in the line, and the statement text, being
    the sentence the disposition form stands in. The first
    statement is the disposition the text as a whole carries, found
    as _find_disposition finds it. A further statement stands only
    where a later sentence opens in a marked statement form and
    carries a disposition, under the segmentation rule at brief
    section 5.2, PIN-01, form 1: a segment carrying two disposition
    statements splits at the second statement, wherever the two
    stand. Descriptive prose after the first statement, as a
    sentence describing what a remainder does, forms no statement
    of its own. A bare closure sentence standing last forms no
    statement here: the terminal closure machinery owns that
    position, and inside a block segment it formed no element in
    the recorded reading.
    """
    primary = _find_disposition(text)
    if primary is None:
        return []
    disposition, offset = primary
    sentences = _sentence_spans(text)
    primary_index = 0
    for index, (start, end) in enumerate(sentences):
        if start <= offset < end:
            primary_index = index
            break
    start, end = sentences[primary_index]
    results = [(disposition, offset, text[start:end])]
    for index in range(primary_index + 1, len(sentences)):
        start, end = sentences[index]
        sentence = text[start:end]
        if not _marked_statement(sentence):
            continue
        hit = _find_disposition(sentence)
        if hit:
            results.append((hit[0], start + hit[1], sentence))
    return results


def _statements_in_lines(lines):
    """The disposition statements standing in a run of lines.

    A run of lines, a block segment or a plain paragraph, carries
    one primary statement: the statements of its first line that
    carries one, under _find_disposition_statements. A later line
    adds a statement only where one of its sentences opens in a
    marked statement form, or its first sentence opens in the weak
    marked form, and carries a disposition: the two statements of
    the segmentation rule stand wherever they stand, on one line
    or on two lines, and descriptive prose lines after the primary
    statement form no statement of their own. Returns a list of
    five tuples: the line number, the line text, the disposition,
    the offset of the disposition expression within its line, and
    the statement text.
    """
    results = []
    primary_found = False
    for number, text in lines:
        if not primary_found:
            statements = _find_disposition_statements(text)
            if statements:
                primary_found = True
                for disposition, offset, statement in statements:
                    results.append((number, text, disposition,
                                    offset, statement))
            continue
        for index, (start, end) in enumerate(_sentence_spans(text)):
            sentence = text[start:end]
            if _marked_statement(sentence) or \
                    (index == 0 and _weak_marked_statement(sentence)):
                hit = _find_disposition(sentence)
                if hit:
                    results.append((number, text, hit[0],
                                    start + hit[1], sentence))
    return results


def _decider_from_text(text):
    """The decider category and decider text a statement names."""
    if re.search(r"by the Manager\b", text) or \
            re.search(r"(Settled|SETTLED) by:? The Manager\b", text) or \
            re.search(r"by a (decision|pick) of the Manager\b", text) or \
            re.search(r"the Manager's pick under .* delegation", text):
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
    """The scope of a disposition statement: Whole or Part.

    Scope is Part where the statement in words limits the act to a
    named part, limb, or portion of the entry, or where the
    statement names a remainder, as plan Item 3, section 3.5,
    field 6 states. The remainder itself is carried by the
    remainder text of the element, never by the scope word.
    """
    if remainder is not None:
        return "Part"
    if re.search(r"in part", text, re.IGNORECASE):
        return "Part"
    if re.search(r"\b(?:limb|portion) of this entry\b", text):
        return "Part"
    if re.search(r"\bOnly the\b.+\bof this entry is\b", text):
        return "Part"
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
    """The named unnumbered entry form, and no other.

    The one unnumbered headed entry this version recognises is
    the named R-7 entry, under its literal heading text as
    measured. A heading in an R number form with any other
    number, or with the R-7 number under any other title, is no
    entry form: it takes the Warning and file level unit
    treatment under PIN-06.
    """
    if text != _NAMED_UNNUMBERED_HEADING:
        return None
    return "R-7", text[len("R-7 "):]


_HEADING_BY_RE = re.compile(
    r"(RULED|Ruled|SETTLED|Settled) by ([^.]+?)"
    r"( \d{4}-\d{2}-\d{2})?\s*$")
_HEADING_WORD_BY_RE = re.compile(
    r"\b(RULED|SETTLED|ORDERED|BANKED|CLOSED|PARKED|PRESENTED|OPEN|"
    r"Ruled|Settled|Ordered|Banked|Closed|Parked|Presented|Open)"
    r" by\b")
_HEADING_TAIL_WORD_RE = re.compile(
    r"\b(RULED|SETTLED|ORDERED|BANKED|CLOSED|PARKED|PRESENTED|OPEN|"
    r"Ruled|Settled|Ordered|Banked|Closed|Parked|Presented|Open)"
    r"( \d{4}-\d{2}-\d{2})?\s*$")
_ADDITION_THIS_ENTRY_RE = re.compile(
    r"^Addition to this entry\b", re.IGNORECASE)
_SEGMENT_STATE_CLAIM_RE = re.compile(
    r"\b(remains|stays|stands|is|was|left)\b[^.]{0,80}?"
    r"\b(open|settled|ruled|closed|banked|parked|presented)\b",
    re.IGNORECASE)


def _heading_borne(record):
    """The heading borne element of an entry, where one stands.

    Under PIN-05 the heading is a status bearing element where it
    carries status evidence: a heading outcome word, a decider
    named in the heading, or a ruling stated in the heading. The
    forms, in the order they are tried: a ruling or settlement
    stated in the heading in the by form at its end; an outcome
    word in the by form anywhere in the heading tail; an outcome
    word at the end of the heading, with a date after it where one
    stands; and a heading whose whole title is the one outcome
    word, classifiable or unclassifiable, as the MK-4 construction
    at plan Item 3, section 3.10, attack 3 states. An outcome word
    with no translation, as ORDERED, extracts an element with no
    disposition: the element stands, and PIN-04 governs it.

    Returns a pair of the disposition, or None, and the position of
    the outcome word within the heading line, or None where the
    heading carries no status evidence.
    """
    heading = record.heading
    prefix = "#" * record.heading_level + " "
    match = _HEADING_BY_RE.search(heading)
    if match:
        return (_DISPOSITION_WORDS[match.group(1).upper()],
                len(prefix) + match.start())
    match = _HEADING_WORD_BY_RE.search(heading)
    if match:
        return (_DISPOSITION_WORDS.get(match.group(1).upper()),
                len(prefix) + match.start())
    match = _HEADING_TAIL_WORD_RE.search(heading)
    if match:
        return (_DISPOSITION_WORDS.get(match.group(1).upper()),
                len(prefix) + match.start())
    title = (record.title or "").strip()
    if title and " " not in title and \
            title.replace("-", "").isalpha():
        at = heading.find(title)
        return (_DISPOSITION_WORDS.get(title.upper()),
                len(prefix) + (at if at >= 0 else 0))
    return None


def _addition_paragraphs_after_closing(record, closing_line):
    """Paragraphs labelled as additions to this entry, after a line.

    The paragraphs of the entry body that stand after the given
    closing Status line and open with an addition label naming this
    entry, by its number or as this entry, in file order.
    """
    paragraphs = []
    current = []
    for number, text in record.body_lines:
        if number <= closing_line:
            continue
        if text.strip() == "":
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append((number, text))
    if current:
        paragraphs.append(current)
    found = []
    for paragraph in paragraphs:
        first_text = paragraph[0][1]
        if _ADDITION_THIS_ENTRY_RE.match(first_text):
            found.append(paragraph)
            continue
        addition = _ADDITION_RE.match(first_text)
        if addition and addition.group(1) == str(record.identifier):
            found.append(paragraph)
    return found


def _is_note_section(text):
    """Whether a heading stands in a recorded note section form.

    The recorded forms are the forms the brief names at PIN-06:
    a heading opening with the word Note or Notes, an Amendment
    note heading, and the Manager addition note heading, in
    either of its written forms. A heading whose words merely
    contain the word note or notes in some other position stands
    in no recorded form and is no note section: it takes the
    recognition test, and where it names a single DQ entry as
    its subject it takes the Warning and file level unit
    treatment.
    """
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return False
    lowered = [word.lower() for word in words]
    if lowered[0] in ("note", "notes"):
        return True
    if len(lowered) >= 2 and lowered[0] == "amendment" and \
            lowered[1] == "note":
        return True
    stripped = text.strip()
    if stripped.startswith("Manager's addition note") or \
            stripped.startswith("Manager addition note"):
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
                    kind = "line start Status line"
                    self.seen_line_start = True
                occurrence = "line start"
            else:
                kind = "tail paragraph element"
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
        """The matter under an Origin label, tested by its own form.

        The Origin line is not an element by itself, under PIN-05:
        the matter under the label is tested under the marking form
        that carries it. A terminal Status value in the matter is a
        tail paragraph element where its value states a disposition,
        a closure, or a remaining open state of the entry. A terminal
        Status sentence whose value states no disposition, as the
        landing record form at brief section 5.2, PIN-01, form 4,
        carries no element at all. A decider form stated in the
        matter is an element of the labelled paragraph that carries
        it.
        """
        body = text[len("Origin:"):]
        has_marker = _STATUS_MARKER in body
        has_decider_form = bool(
            re.search(r"\b(Ruled|Settled) by:", body))
        if not has_marker and not has_decider_form:
            return False
        if has_marker:
            at = body.find(_STATUS_MARKER)
            value = body[at + len(_STATUS_MARKER):].lstrip(" ")
            disposition = _disposition_from_value(value)
            if disposition is not None:
                self.elements.append(_make_element(
                    kind="tail paragraph element",
                    verbatim=value,
                    disposition=disposition,
                    line=number,
                    position=len("Origin:") + at,
                    occurrence_kind="embedded",
                    own_text=value,
                    decision_block=decision_block,
                ))
                return False
            if not has_decider_form:
                return False
        found = _find_disposition(body)
        disposition = found[0] if found else None
        self.elements.append(_make_element(
            kind="labelled paragraph element",
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
            entry_identifier=str(self.record.identifier)
            if self.record.identifier is not None
            else self.record.heading,
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
        joined = "\n".join(item[1] for item in paragraph)
        bold = _BOLD_LEAD_RE.match(first_text)
        if bold is not None:
            lead = bold.group(1)
            lead_hit = _find_disposition(lead)
            if lead_hit is not None or "Supersession:" in lead:
                disposition = lead_hit[0] if lead_hit else None
                alone = len(paragraph) == 1 and \
                    first_text.strip() == "**" + lead + "**"
                if alone and "Supersession:" in lead:
                    # The bold supersession block reading, plan
                    # Item 6, section 6.7: a bold line standing
                    # alone carrying a supersession is read as a
                    # decision block segment carrying the
                    # supersession statement, and that statement is
                    # the determining element for its entry. It is
                    # not read as a bold lead in paragraph element,
                    # because the line stands alone and leads no
                    # paragraph. The disposition is the state the
                    # superseding act carries: a Manager pick under
                    # Captain JP's delegation settles, a ruling by
                    # Captain JP rules.
                    decider, _decider_text = _decider_from_text(lead)
                    if decider == "a Manager grant form":
                        disposition = "Settled"
                    elif decider == "Captain JP":
                        disposition = "Ruled"
                    block = DecisionBlock(
                        marking_form="bold supersession segment",
                        span=Span(paragraph[0][0], paragraph[-1][0],
                                  "heading cut"),
                        heading_text=None,
                        post_status_flag=bool(
                            self.closing_status_line is not None and
                            paragraph[0][0] >
                            self.closing_status_line),
                    )
                    self.blocks.append(block)
                    block_index = len(self.blocks) - 1
                    element = _make_element(
                        kind="decision block matter",
                        verbatim=first_text,
                        disposition=disposition,
                        line=first_number,
                        position=0,
                        occurrence_kind=None,
                        own_text=joined,
                        statement=joined,
                        decision_block=block_index,
                    )
                    block.elements.append(element)
                    self.elements.append(element)
                    if disposition == "Closed":
                        self.closed_seen = True
                    return
                element = _make_element(
                    kind="bold lead in paragraph element",
                    verbatim=first_text,
                    disposition=disposition,
                    line=first_number,
                    position=0,
                    occurrence_kind=None,
                    own_text=joined,
                    statement=joined,
                    decision_block=decision_block,
                )
                self.elements.append(element)
                if disposition == "Closed":
                    self.closed_seen = True
                return
        hits = _statements_in_lines(paragraph)
        labelled = label in _DECISION_LABELS or \
            first_text.startswith("Addition to") or \
            first_text.startswith("Decision under")
        if not hits:
            if labelled and (label in _LABEL_DISPOSITIONS
                             or label == "Decision"):
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
                    kind="labelled paragraph element",
                    verbatim=first_text,
                    disposition=_LABEL_DISPOSITIONS.get(label),
                    line=first_number,
                    position=0,
                    occurrence_kind=None,
                    own_text=joined,
                    statement=first_text,
                    decision_block=block_index,
                    decider_text_override=None,
                )
                block.elements.append(element)
                self.elements.append(element)
            return
        if labelled:
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
            for number, text, disposition, offset, statement in hits:
                if len(hits) == 1:
                    verbatim, own, stmt = text, joined, text
                else:
                    verbatim, own, stmt = statement, statement, \
                        statement
                element = _make_element(
                    kind="labelled paragraph element",
                    verbatim=verbatim,
                    disposition=disposition,
                    line=number,
                    position=offset,
                    occurrence_kind=None,
                    own_text=own,
                    statement=stmt,
                    decision_block=block_index,
                    decider_text_override=None,
                )
                block.elements.append(element)
                self.elements.append(element)
                if disposition == "Closed":
                    self.closed_seen = True
        else:
            for number, text, disposition, offset, statement in hits:
                if len(hits) == 1:
                    verbatim, own, stmt = text, joined, text
                else:
                    verbatim, own, stmt = statement, statement, \
                        statement
                element = _make_element(
                    kind="closing prose",
                    verbatim=verbatim,
                    disposition=disposition,
                    line=number,
                    position=offset,
                    occurrence_kind=None,
                    own_text=own,
                    statement=stmt,
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
            hits = _statements_in_lines(run)
            if not hits:
                return
            joined = "\n".join(item[1] for item in run)
            own = (heading_text or "") + "\n" + joined
            for number, text, disposition, offset, statement in hits:
                if len(hits) == 1:
                    verbatim, own_text, stmt = text, own, text
                else:
                    verbatim, own_text, stmt = statement, statement, \
                        statement
                element = _make_element(
                    kind="decision block matter",
                    verbatim=verbatim,
                    disposition=disposition,
                    line=number,
                    position=offset,
                    occurrence_kind=None,
                    own_text=own_text,
                    statement=stmt,
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
        """The assessment closure element of a paragraph.

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
                if target.tuple[1] != "Part":
                    target.tuple = target.tuple._replace(scope="Part")
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
    if hasattr(sys, "set_int_max_str_digits"):
        # Plan Item 3, section 3.2, field 11, in its Step 12
        # correction: before any heading digit string is converted,
        # the run raises the integer string conversion limit to
        # 16,384, the per line limit, so a DQ number inside the
        # stated limits takes no refusal, no error, and no exception
        # on account of its digit count.
        sys.set_int_max_str_digits(16384)
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

    file_terminated = text.endswith("\n")
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
            starts.append((number, "file header",
                           (level, heading_text, None)))
            started = True
            current_kind = "file header"
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
            starts.append((number, "orphan unmatched",
                           (level, heading_text, None)))
            started = True
            current_kind = "orphan"
            continue
        if level == 4 and current_kind == "entry":
            continue
        if level == 3 and _is_note_section(heading_text):
            starts.append((number, "orphan note",
                           (level, heading_text, None)))
            started = True
            current_kind = "orphan"
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
    number_ledger = {}

    def unit_text(start, end):
        return "\n".join(lines_by_number[number]
                         for number in range(start, end + 1))

    for start, end, kind, info in unit_ranges:
        span = Span(start, end, "heading cut")
        if kind == "section introduction":
            current_section = info[1]
            units.append(Unit(kind="section introduction", span=span,
                              heading_text=info[1],
                              text=unit_text(start, end)))
            continue
        if kind == "file header":
            heading_text = None
            if info is not None:
                heading_text = info[1]
            elif first_heading and first_heading[0] >= start and \
                    first_heading[0] <= end:
                heading_text = first_heading[2]
            units.append(Unit(kind="file header", span=span,
                              heading_text=heading_text,
                              text=unit_text(start, end)))
            continue
        if kind in ("orphan note", "orphan unmatched"):
            level, heading_text, _form = info
            if kind == "orphan note":
                orphan_kind = "note section"
                unmatched = False
            else:
                orphan_kind = "other file level segment"
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
            for _number, segment_text in segment_lines:
                # A state claim in the Manager addition note form:
                # a bullet naming one entry as its subject and
                # stating that entry's state, as the note at the
                # pin states DQ-001 and DQ-002 as still open
                # against their own ruled bodies. PIN-09 covers a
                # governing or state claim alike, and the claim is
                # recorded here, where the segment is built, in
                # the same shape as the governing claim above.
                bullet = re.match(r"^- (DQ-\d{3})\b", segment_text)
                if not bullet:
                    continue
                target = bullet.group(1)
                if any(target in claim.named_entries
                       for claim in claims):
                    continue
                if _SEGMENT_STATE_CLAIM_RE.search(segment_text):
                    claims.append(SegmentClaim(
                        named_entries=[target],
                        statement=segment_text))
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
            units.append(Unit(kind=orphan_kind, span=span,
                              heading_text=heading_text,
                              text=unit_text(start, end)))
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
            identifier = DQNumber(form_data[1], form_data[0])
            title = form_data[2]
            number_ledger.setdefault(form_data[1], []).append(
                identifier)
        else:
            identifier = heading_text
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
            entries_by_id.setdefault(str(identifier), record)
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
                if addition and addition.group(1) != str(
                        record.identifier):
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
        if builder.closing_status_line is not None:
            additions = _addition_paragraphs_after_closing(
                record, builder.closing_status_line)
            for paragraph in additions:
                span = Span(paragraph[0][0], paragraph[-1][0],
                            "label reattachment", True)
                record.spans.append(span)
                note = ParseNote(
                    kind="label reattachment",
                    text="a paragraph labelled as an addition to "
                         "this entry stands after its closing "
                         "Status line and is reattached to it",
                    line_span=Span(paragraph[0][0], paragraph[-1][0],
                                   "label reattachment", True),
                    entry_identifier=str(record.identifier)
                    if record.identifier is not None
                    else record.heading,
                )
                parse_notes.append(note)
                record.parse_notes.append(note)
                if not any(paragraph[0][0] <= element.line <=
                           paragraph[-1][0]
                           for element in builder.elements):
                    builder.process_paragraph(paragraph)
            if additions and record.spans and \
                    record.spans[0].end_line > \
                    builder.closing_status_line:
                primary = record.spans[0]
                record.spans[0] = Span(
                    primary.start_line, builder.closing_status_line,
                    primary.boundary_basis, primary.non_contiguous)
        borne = _heading_borne(record)
        if borne is not None:
            disposition, position = borne
            element = _make_element(
                kind="heading borne evidence",
                verbatim=record.heading,
                disposition=disposition,
                line=record.heading_line,
                position=position,
                occurrence_kind=None,
                own_text=record.heading,
                statement=record.heading,
            )
            builder.elements.append(element)

        def assembled_key(element):
            # PIN-02: elements stand in assembled order, the in
            # place elements in file order first, then the
            # elements of the reattached spans in the order the
            # spans were collected, each span flagged not
            # contiguous. Raw file position orders only within
            # one span, never across the assembled entry.
            for index, span in enumerate(record.spans):
                if span.start_line <= element.line <= span.end_line:
                    return (index, element.line,
                            element.position_in_line)
            return (0, element.line, element.position_in_line)

        builder.elements.sort(key=assembled_key)
        record.status_elements = builder.elements
        record.decision_blocks = builder.blocks
        record.fields = builder.fields
        record.near_marker_occurrences = builder.near
        record.parse_notes = record.parse_notes + builder.notes
        parse_notes.extend(builder.notes)
        builder.attach_remainders_and_conditions(record.body_lines)
        has_body_line = any(
            _number > record.heading_line
            for _number, _text in record.body_lines)
        heading_is_last_line = record.heading_line == line_count
        cut_off = bool(
            not file_terminated and has_body_line and record.spans
            and max(span.end_line for span in record.spans) ==
            line_count)
        record.unparsed = bool(
            (heading_is_last_line or cut_off)
            and not builder.elements)
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

    header_text = ""
    if queue_header_present and first_heading is not None:
        header_text = lines_by_number[first_heading[0]]
    facts = FileHeaderFacts(header_text)
    return QueueFileModel(
        header_facts=facts,
        units=list(units),
        entries=entries,
        orphan_segments=orphans,
        parse_notes=parse_notes,
        unassigned_lines=[],
        double_assigned_lines=[],
        h4_sub_heading_count=h4_count,
        lines=lines,
        unmatched_headings=[
            segment for segment in orphans if segment.unmatched_heading],
        input_name=name,
        source_designation="live",
        raw_bytes=raw,
        line_count=line_count,
        byte_count=byte_count,
        digest=digest,
        number_ledger=number_ledger,
    )
