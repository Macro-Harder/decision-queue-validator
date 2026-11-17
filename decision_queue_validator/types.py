"""Core value types for the decision queue validator.

Every shape the pipeline hands across a module boundary is defined
here, before any module behaviour. The types carry construction and
equality only. Counts whose unit is not carried by a field name are
carried by a dedicated type, so a count of one unit is never read as
a count of another.

Field lists follow the design shapes: the Input value and the Limits
value, the Queue file model with its unit and entry forms, the file
level failure result, the Status bearing element with its five part
tuple, the Finding, the census entry, the Validate output with every
field render prints, the Exit decision, and the Vocabulary value.
"""

from dataclasses import dataclass, field
from typing import NamedTuple, Optional


class HeadedEntryCount:
    """A count of headed entries, the unit carried by the type."""

    __slots__ = ("value",)

    def __init__(self, value):
        self.value = int(value)

    def __eq__(self, other):
        if isinstance(other, HeadedEntryCount):
            return self.value == other.value
        if isinstance(other, int) and not isinstance(other, bool):
            return self.value == other
        return NotImplemented

    def __hash__(self):
        return hash(self.value)

    def __int__(self):
        return self.value

    def __repr__(self):
        return "HeadedEntryCount(%r)" % (self.value,)


class DQNumber(int):
    """The numeric value a DQ heading's digits denote.

    The value is the integer itself: equality, hashing, and
    ordering are the integer's, so two headings whose digits
    differ in width alone carry the one value. The string form
    is the DQ label as written in the heading, which is the
    form print surfaces use. The heading text verbatim stands
    on the Entry record itself, at its heading field.
    """

    def __new__(cls, value, label=""):
        obj = int.__new__(cls, value)
        obj.label = label or ("DQ-%d" % int(value))
        return obj

    def __str__(self):
        return self.label

    def __repr__(self):
        return "DQNumber(%r, %r)" % (int(self), self.label)


class DistinctPhrasingCount:
    """A count of distinct verbatim status phrasings."""

    __slots__ = ("value",)

    def __init__(self, value):
        self.value = int(value)

    def __eq__(self, other):
        if isinstance(other, DistinctPhrasingCount):
            return self.value == other.value
        if isinstance(other, int) and not isinstance(other, bool):
            return self.value == other
        return NotImplemented

    def __hash__(self):
        return hash(self.value)

    def __int__(self):
        return self.value

    def __repr__(self):
        return "DistinctPhrasingCount(%r)" % (self.value,)


@dataclass
class Input:
    """The value the shell hands to parse: a name and raw bytes."""

    input_name: str
    raw_bytes: bytes

    @property
    def name(self):
        return self.input_name


@dataclass
class Limits:
    """The per file limits of this version, printed in every head."""

    max_bytes: int = 2000000
    max_lines: int = 10000
    max_characters_per_line: int = 16384


InputValue = Input
LimitsValue = Limits


@dataclass
class Span:
    """A line span: start line, end line, basis, contiguity flag."""

    start_line: int
    end_line: int
    boundary_basis: str = "heading cut"
    non_contiguous: bool = False

    @property
    def start(self):
        return self.start_line

    @property
    def end(self):
        return self.end_line


@dataclass
class ParseNote:
    """One accommodation parse made, with its line span."""

    kind: str
    text: str
    line_span: Optional[Span] = None
    entry_identifier: Optional[str] = None


@dataclass
class FieldOccurrence:
    """One field occurrence: label as written, value, line."""

    label: str
    value: str
    line: int


class ElementTuple(NamedTuple):
    """The five part core of a Status bearing element.

    The components are the disposition, the scope, the condition,
    the decider, and the line at which the status value is stated.
    The scope component is one of the words Whole or Part, with a
    named remainder carried by the remainder text of the element
    record, never by the scope word. The condition component is
    None or the condition text verbatim. The decider component is
    one of the decider categories or None where no decider is
    named.
    """

    disposition: Optional[str]
    scope: str
    condition: Optional[str]
    decider: Optional[str]
    line: int


@dataclass
class StatusBearingElement:
    """A status bearing element record, as parse collects it.

    Around the five part tuple the record carries the element kind,
    the verbatim status phrasing where one exists, the position of
    the value within its line, the occurrence kind under the kind
    counting precedence (line start, embedded, or variant), the
    remainder text where one is named, the decider text where one is
    named, the statement the disposition was read from, the decision
    block the element sits in where one applies, and the lines the
    element was read from.

    The disposition, the scope, and the condition stand as fields
    of the record in their own right, as the element shape at plan
    Item 3, section 3.5 names them. The tuple is the construction
    record of those three fields and of the decider: the fields are
    taken from the tuple when the record is built, and assigning a
    new tuple to a built record refreshes the three fields from it,
    so the two carriers never stand apart after either write. The
    determining flag and the underlying state without condition are
    validate owned fields under the seam at section 3.5: parse
    leaves both at their empty values, and validate sets them where
    its mapping runs.
    """

    kind: str
    verbatim: Optional[str]
    tuple: ElementTuple
    line: int
    position_in_line: int = 0
    occurrence_kind: Optional[str] = None
    remainder_text: Optional[str] = None
    decider_text: Optional[str] = None
    statement: Optional[str] = None
    decision_block: Optional[int] = None
    line_span: Optional[Span] = None
    disposition: Optional[str] = None
    scope: str = "Whole"
    condition: Optional[str] = None
    determining_flag: bool = False
    underlying_state_without_condition: Optional[str] = None

    def __post_init__(self):
        object.__setattr__(self, "disposition", self.tuple[0])
        object.__setattr__(self, "scope", self.tuple[1])
        object.__setattr__(self, "condition", self.tuple[2])

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == "tuple":
            object.__setattr__(self, "disposition", value[0])
            object.__setattr__(self, "scope", value[1])
            object.__setattr__(self, "condition", value[2])

    @property
    def element_kind(self):
        return self.kind

    @property
    def verbatim_value(self):
        return self.verbatim

    @property
    def decider(self):
        return self.tuple[3]


@dataclass
class DecisionBlock:
    """A decision block: a container and a source of elements.

    The block carries its marking form, its span, the elements inside
    it, its heading text where it has one, and a post Status flag,
    true where the block stands after a closing Status line in the
    same entry. A block is not itself a state.
    """

    marking_form: str
    span: Span
    elements: list = field(default_factory=list)
    heading_text: Optional[str] = None
    post_status_flag: bool = False


@dataclass
class NearMarkerOccurrence:
    """A near marker line: it carries no element, and is recorded."""

    line: int
    text: str


@dataclass
class EntryRecord:
    """One headed entry, as parse records it.

    The record carries the identifier (the DQ number as the numeric
    value the heading digits denote, in the DQNumber type, or the
    literal heading text for the named R-7 entry), the verbatim
    heading text, the heading level and line, the
    title text after the entry token, the spans in file order, the
    section as provenance only, the ordered field occurrences, the
    ordered status elements, the ordered decision blocks, the post
    Status blocks flag, the parse notes for this entry, the near
    marker occurrences, the unparsed flag, and the body lines as
    (line number, text) pairs in file order.

    The entry outcome stands in three separate carriers, never one
    merged value, as plan Item 3, section 3.4 states: the derived
    effective state in the effective state field, the Ambiguous
    reporting form in the reporting form field, and the unparsed
    marker in the unparsed flag. The record also carries the decider
    label as recorded, the remainder texts in element order, the
    condition text verbatim, the supersession pointers, and the
    internal undecided note, each in a field of its own.
    """

    identifier: object
    heading: str
    heading_level: int
    heading_line: int
    title: str = ""
    spans: list = field(default_factory=list)
    section: Optional[str] = None
    fields: list = field(default_factory=list)
    status_elements: list = field(default_factory=list)
    decision_blocks: list = field(default_factory=list)
    post_status_blocks: bool = False
    parse_notes: list = field(default_factory=list)
    near_marker_occurrences: list = field(default_factory=list)
    unparsed: bool = False
    body_lines: list = field(default_factory=list)
    date_text: Optional[str] = None
    decider_label: Optional[str] = None
    remainder_texts: list = field(default_factory=list)
    condition_text: Optional[str] = None
    supersession_pointers: list = field(default_factory=list)
    internal_undecided_note: Optional[str] = None
    effective_state: Optional[str] = None
    reporting_form: Optional[str] = None

    @property
    def heading_text(self):
        return self.heading

    @property
    def span(self):
        return self.spans[0] if self.spans else None

    @property
    def unparsed_flag(self):
        return self.unparsed


@dataclass
class SegmentClaim:
    """A claim a segment carries over named entries, as data."""

    named_entries: list = field(default_factory=list)
    statement: str = ""


@dataclass
class OrphanSegment:
    """An orphan segment: a first class member of the model.

    The kind is one of the file level unit kinds at plan Item 3,
    section 3.3: note section, for a segment under one of the
    recorded note section headings, or other file level segment,
    for a segment under a heading matching no known form. A
    segment created by an unmatched heading carries its unmatched
    flag, so the finding that belongs to it can be raised from the
    model. The entries the segment names are taken from its own text.
    """

    kind: str
    span: Span
    heading_text: Optional[str] = None
    named_entries: list = field(default_factory=list)
    claims: list = field(default_factory=list)
    unmatched_heading: bool = False
    lines: list = field(default_factory=list)


@dataclass
class Unit:
    """One file level unit of the partition.

    The kind is exactly one of the kinds plan Item 3, section 3.3
    states: file header, section introduction, note section, or
    other file level segment. Entry spans are not units of this
    shape; they stand on the Entry records. Every line of the file
    belongs to exactly one entry or exactly one unit of this
    shape, or stands in the model unassigned list.

    The unit identifier stands in the one fixed form plan Item 3,
    section 3.3 states: the words file level unit, followed by the
    kind value, followed by the start line of the span. Where no
    identifier is supplied at construction, that form is composed
    from the kind and the span. The text field carries the unit
    text as written.
    """

    kind: str
    span: Span
    heading_text: Optional[str] = None
    entry_identifier: Optional[str] = None
    unit_identifier: str = ""
    text: str = ""

    def __post_init__(self):
        if not self.unit_identifier:
            start = 0
            if self.span is not None:
                start = getattr(self.span, "start_line", 0) or 0
            self.unit_identifier = (
                "file level unit, kind %s, beginning at line %s"
                % (self.kind, start))


class FileHeaderFacts(str):
    """The header facts of the File shape: one verbatim text field.

    The value is the queue header text as written, supplied by the
    first occurrence of the queue header in the file and by no
    later occurrence, as plan Item 3, section 3.2, field 7 states.
    It carries no subfield list. The line count, the byte count,
    and the digest of the bytes read stand as fields of the File
    shape itself, not as parts of this value.
    """


@dataclass
class QueueFileModel:
    """The whole parse result where a parse stands.

    The File shape fields at plan Item 3, section 3.2 stand on the
    model itself: the input name as given, the source designation,
    the raw bytes as read, the line count and the byte count of
    those bytes, their digest, and the number ledger keyed on the
    numeric value of the entry number alone. The header facts field
    carries the queue header text verbatim, in the one text field
    section 3.2, field 7 states, and no measurement stands inside
    it; the measurements stand on the model fields named here.
    """

    header_facts: str = ""
    units: list = field(default_factory=list)
    entries: list = field(default_factory=list)
    orphan_segments: list = field(default_factory=list)
    parse_notes: list = field(default_factory=list)
    unassigned_lines: list = field(default_factory=list)
    double_assigned_lines: list = field(default_factory=list)
    h4_sub_heading_count: int = 0
    lines: list = field(default_factory=list)
    unmatched_headings: list = field(default_factory=list)
    input_name: str = ""
    source_designation: str = "live"
    raw_bytes: bytes = b""
    line_count: int = 0
    byte_count: int = 0
    digest: str = ""
    number_ledger: dict = field(default_factory=dict)

    @property
    def file_header_facts(self):
        return self.header_facts


@dataclass
class ExitDecision:
    """The exit code and the set of reason classes that produced it.

    Where the masking rule at OP-Q4 applies, the masked findings
    summary stands in its own field: the Error and Warning findings
    present at a code the masking rule governs, with their counts.
    No summary stands where the tool inconsistency reason class
    stands at code 4.
    """

    code: int
    reason_classes: list = field(default_factory=list)
    masked_findings_summary: object = None

    @property
    def exit_code(self):
        return self.code


@dataclass
class FileLevelFailure:
    """The typed result parse returns where no model exists.

    The result carries every failure kind present, the name as given,
    the byte count (present in every case), the line count (present
    or absent under the per kind rules, absent winning over present
    where kinds co-occur), the digest (present in every case where
    the file was read), the breached limit and its measured value
    where a limit breach kind is present, the measured value of
    every breached limit where more than one breach stands, a statement of what
    recognisable queue structure is missing where a structure kind is
    present, the byte offset of the first invalid byte where an
    invalid bytes kind is present, and the Exit decision for the run.
    """

    failure_kinds: list
    input_name: str
    byte_count: int
    line_count: Optional[int]
    digest: Optional[str]
    breached_limit: Optional[str] = None
    measured_value: Optional[int] = None
    breached_limits: list = field(default_factory=list)
    breached_measured_values: dict = field(default_factory=dict)
    missing_structure: Optional[str] = None
    invalid_byte_offset: Optional[int] = None
    exit_decision: Optional[ExitDecision] = None

    @property
    def kinds(self):
        return self.failure_kinds

    @property
    def statement(self):
        return self.missing_structure


FileLevelFailureResult = FileLevelFailure


@dataclass
class Finding:
    """A finding, as validate raises it. A census entry is not one.

    The determining element stands named in its own field where the
    class requires it. On a claim finding, the claiming unit or
    claiming entry and the named entries stand in fields of their
    own, and those fields never overwrite the entry identifier
    field, as plan Item 3, section 3.6 states.
    """

    rule_id: object
    severity: str
    entry_identifier: str
    line_span: Optional[Span] = None
    evidence: object = None
    statement: str = ""
    basis: Optional[str] = None
    banked_question_id: Optional[str] = None
    suggested_edit: Optional[str] = None
    determining_element: object = None
    claiming_unit: Optional[str] = None
    named_entries: list = field(default_factory=list)


@dataclass
class CensusEntry:
    """One census class: its name, its count, its member entries.

    The row states its class rule in words and the counting unit
    its count stands in. On a canonical state row where at least
    one entry has a head line view giving that state, the row also
    carries the head line count and the variance, the body derived
    count minus the head line count, each in entries. The head line
    view is a counting view only: the row carries no field that
    derivation reads, as plan Item 3, section 3.6 states.
    """

    class_name: str
    count: int
    member_entry_ids: list = field(default_factory=list)
    class_rule_statement: str = ""
    counting_unit: str = ""
    head_line_count: Optional[int] = None
    variance: Optional[int] = None


@dataclass
class VerbatimAppendixRow:
    """One verbatim appendix row: a phrasing under one kind.

    The occurrence count stands in the unit the counting unit
    field states: status occurrences, as plan Item 3, section 3.6
    states the count.
    """

    phrasing: str
    occurrence_count: int
    kind: str
    member_entry_ids: list = field(default_factory=list)
    counting_unit: str = "status occurrences"


@dataclass
class SelfCheckResult:
    """The reconciliation self check result."""

    sums_agree: bool
    failed_components: list = field(default_factory=list)


@dataclass
class ReconciliationBlock:
    """The reconciliation block data, computed once by validate.

    The entry total stands in the HeadedEntryCount type and is the
    only entry count printed anywhere. The H4 sub heading count
    reaches this block through its single carriage in the Queue file
    model and no other. The distinct phrasing count stands in the
    DistinctPhrasingCount type at its single home here. The finding
    count stands only as the per severity view, the per rule view,
    and the length of the findings list.
    """

    entry_total: Optional[HeadedEntryCount] = None
    dq_entry_count: int = 0
    unnumbered_entry_count: int = 0
    headed_span_count: int = 0
    orphan_note_segment_count: int = 0
    h4_sub_heading_count: int = 0
    status_occurrences_by_kind: dict = field(default_factory=dict)
    status_occurrence_total: int = 0
    canonical_counts: dict = field(default_factory=dict)
    ambiguous_count: int = 0
    unparsed_count: int = 0
    findings_per_severity: dict = field(default_factory=dict)
    findings_per_rule: dict = field(default_factory=dict)
    distinct_phrasing_count: Optional[DistinctPhrasingCount] = None
    self_check: Optional[SelfCheckResult] = None
    paired_total_declarations: list = field(default_factory=list)


@dataclass
class FileFactsData:
    """The file facts data for the shared head, carried by validate.

    The source designation of the File shape stands on this value
    in its own field, so the designation recorded on the parse
    model reaches the printed head through the validate handoff.
    """

    input_name: str
    byte_count: int = 0
    line_count: int = 0
    entry_count: Optional[HeadedEntryCount] = None
    digest: str = ""
    source_designation: str = "live"


@dataclass
class EntryResult:
    """One entry of the Validate output, in file order."""

    identifier: Optional[str]
    heading: str
    title: str = ""
    date: Optional[str] = None
    effective_state: Optional[str] = None
    sub_label: Optional[str] = None
    determining_element: Optional[StatusBearingElement] = None
    competing_elements: list = field(default_factory=list)
    element_summary: list = field(default_factory=list)
    decider_label: Optional[str] = None
    banked_question_id: Optional[str] = None
    status_phrasings: list = field(default_factory=list)
    head_phrasing: Optional[str] = None
    remainder_text: Optional[str] = None
    condition_text: Optional[str] = None
    ordering_reason: Optional[str] = None
    open_fields: dict = field(default_factory=dict)
    unparsed: bool = False


@dataclass
class CountingUnitsKey:
    """The counting units key of the render model.

    The counts of the render model stand under this key, as plan
    Item 3, section 3.7 states: each field names the unit the
    count it keys stands in, so no count of the model is read
    without its unit. Validate populates the key; render reads
    the figures under it.
    """

    canonical_counts: str = "entries"
    headed_entry_count: str = "headed entries"
    residue_items: str = "residue items"
    supersession_chains: str = "chains"
    waiting: str = "entries"
    blocking: str = "entries"


@dataclass
class ValidateOutput:
    """The sole validate to render handoff.

    Every field render prints has its named source inside this value:
    the per entry results, the file facts data, the limits in force,
    the vocabulary version in force, the output form edition, the
    verbatim appendix rows, the per rule clearing forms, the findings
    list, the census, the reconciliation block, the crosswalk counts,
    the decider subtotals, the waiting and blocking figures, the
    blocks coverage counts, the effort coverage counts, the limbo
    sentence data, the segment claim reports, the fastest item
    value, and the Exit decision.

    The render model fields at plan Item 3, section 3.7 stand as
    fields of this value in their own names: the canonical counts
    by state, the residue items, the residue share computation
    carried as its exact pair and in no rounded form, the
    supersession chains, and the counting units key the counts of
    this model stand under.
    """

    entries: list = field(default_factory=list)
    entry_groups: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    census: list = field(default_factory=list)
    reconciliation: Optional[ReconciliationBlock] = None
    exit_decision: Optional[ExitDecision] = None
    file_facts: Optional[FileFactsData] = None
    limits: Optional[Limits] = None
    vocabulary_version: Optional[str] = None
    output_form_edition: Optional[str] = None
    verbatim_appendix_rows: list = field(default_factory=list)
    per_rule_clearing_forms: dict = field(default_factory=dict)
    crosswalk_counts: dict = field(default_factory=dict)
    decider_subtotals: dict = field(default_factory=dict)
    waiting: object = None
    blocking: object = None
    blocking_list: list = field(default_factory=list)
    blocks_coverage: dict = field(default_factory=dict)
    effort_coverage: dict = field(default_factory=dict)
    limbo_data: dict = field(default_factory=dict)
    segment_claim_reports: list = field(default_factory=list)
    fastest_item: str = "not derivable from the file"
    canonical_counts: dict = field(default_factory=dict)
    residue_items: list = field(default_factory=list)
    residue_share: object = None
    supersession_chains: list = field(default_factory=list)
    counting_units: CountingUnitsKey = field(
        default_factory=CountingUnitsKey)


_SHIPPED_VOCABULARY_VERSION = "1"

_SHIPPED_VOCABULARY_MAPPING = {
    "Café fermé": "Closed as decided",
    "Banked": "Banked",
    "Banked in part, the intake limb only.": "Banked",
    "Banked, marked as hers under DQ-143. No settlement is made.": "Banked",
    "Open": "Open",
    "Parked": "Parked",
    "Parked with trigger": "Parked",
    "Presented": "Presented",
    "RULED, closed": "Ruled",
    "RULED, closed on the principle": "Ruled",
    "RULED, closed, subject to the landings recorded at DQ-142 standing verified in tier-ruling-trace.md.": "Ruled",
    "RULED, closed. This item is ruled.": "Ruled",
    "Ruled by Captain JP": "Ruled",
    "Ruled in part by Captain JP. The ruled limb above is ruled.": "Ruled",
    "SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The renewal form limb above is settled. What stays banked: the remaining budget substance of this item stays banked, nothing else in it is decided, and this item stays banked for that remainder.": "Settled",
    "SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: her session length, volume, and intake limit and the delegation at the limit stay banked, and this item stays banked for those limbs.": "Settled",
    "SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the consequence for stages passed by a reclassified gate stays banked, and this item stays banked for that limb.": "Settled",
    "SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the independent checker of the labels limb and the consequence for a mislabel found later limb stay banked, and this item stays banked for those limbs.": "Settled",
    "SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the later upgrades limb stays banked, and this item stays banked for that limb.": "Settled",
    "SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limb above is settled. What stays banked: the published standard versus written in standard choice and the identity of the standard stay banked, and this item stays banked for those limbs.": "Settled",
    "SETTLED IN PART by the Manager under the pass 2 grant, not ruled by Captain JP. The settled limbs above are settled. What stays banked: the maximum length for a deferral limb stays banked, and this item stays banked for that limb.": "Settled",
    "SETTLED IN PART stands, the no default limb under the pass 2 grant. The remainder stays banked. Reason, in one line: her personal intake limit and what she delegates at it are hers alone to state, and cannot be set for her.": "Settled",
    "SETTLED IN PART stands, the renewal form limb under the pass 2 grant. The remainder stays banked. Reason, in one line: the remainder is budget setting substance, which is Captain JP's under DQ-143, and cannot be finished for her.": "Settled",
    "SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The value set stands until Captain JP overrules it.": "Settled",
    "SETTLED as a Manager fill-in under DQ-141, not ruled by Captain JP. The values set stand until Captain JP overrules them.": "Settled",
    "SETTLED by the Manager under the grant, not ruled by Captain JP. This item is settled.": "Settled",
    "SETTLED by the Manager under the pass 2 grant, not ruled by Captain JP. This item is settled.": "Settled",
    "SETTLED by the Manager, the pass 2 limb under the pass 2 grant and the remaining limb under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.": "Settled",
    "SETTLED by the Manager, the pass 2 limb under the pass 2 grant and the remaining limbs under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.": "Settled",
    "SETTLED by the Manager, the pass 2 limbs under the pass 2 grant and the remaining limb under DQ-145, not ruled by Captain JP. This item is settled and closed as a Manager completion; Captain JP may overrule it.": "Settled",
    "SETTLED in part as a Manager fill-in under DQ-141, not ruled by Captain JP. The values set stand until Captain JP overrules them.": "Settled",
    "SETTLED, closed. Settled by a decision of the Manager under Captain JP's discernment grant. This entry is not a ruling by Captain JP, and it is not recorded as one.": "Settled",
    "SETTLED, closed. Settled by a decision of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.": "Settled",
    "SETTLED, closed. Settled by a decision of the Manager under Captain JP's standing delegation. This entry is not a ruling by Captain JP, and it is not recorded as one.": "Settled",
    "SETTLED, closed. Settled by a pick of the Manager under Captain JP's grant. This entry is not a ruling by Captain JP, and it is not recorded as one.": "Settled",
    "Status unchanged: Banked.": "Relative",
}


@dataclass
class Vocabulary:
    """The canonical mapping, as a versioned value.

    The value maps verbatim status phrasings to canonical families.
    It is handed to validate as one value, whole, for the whole run.
    The shipped copy stands in this module as recorded data; a run
    never edits it and never reads it from a user supplied file.
    """

    version: str = _SHIPPED_VOCABULARY_VERSION
    mapping: dict = field(
        default_factory=lambda: dict(_SHIPPED_VOCABULARY_MAPPING))

    @classmethod
    def shipped(cls):
        return cls(
            version=_SHIPPED_VOCABULARY_VERSION,
            mapping=dict(_SHIPPED_VOCABULARY_MAPPING))

    @classmethod
    def from_shipped_copy(cls):
        return cls.shipped()

    @classmethod
    def default(cls):
        return cls.shipped()

    def family_of(self, phrasing):
        return self.mapping.get(phrasing)

    def __contains__(self, phrasing):
        return phrasing in self.mapping


@dataclass
class ResidueItem:
    """One residue item: an untranslatable phrasing, held as unknown.

    A residue item is never forced to a nearest state and never
    assigned a canonical state, as plan Item 3, section 3.6 states.
    It carries the phrasing as written, the identifier of the entry
    that carries it, and its line span, in lines.
    """

    phrasing: str
    entry_identifier: str = ""
    line_span: Optional[Span] = None


@dataclass
class CorpusManifestEntry:
    """One entry of the corpus manifest, in testing pin down 1 order.

    The field order is the manifest order: fixture, kind, source,
    hash, the byte count, the line count, the expected counts, the
    expected findings, and the expected exit. The byte count stands
    in bytes and the line count in lines. The expected count labels
    field stands after those nine: it holds, per expected count,
    the label that count carries, one of pinned, derived, or open,
    so the manifest self check at plan Item 3, section 3.9 has a
    carrier for the label it checks for.
    """

    fixture: str = ""
    kind: str = ""
    source: str = ""
    hash: str = ""
    bytes_count: int = 0
    lines_count: int = 0
    expected_counts: dict = field(default_factory=dict)
    expected_findings: list = field(default_factory=list)
    expected_exit: str = ""
    expected_count_labels: dict = field(default_factory=dict)


@dataclass
class AcceptanceRunRecord:
    """The record of one acceptance run, as plan Item 3 names it.

    The record carries the input name as given, its line count and
    byte count, the full digest of the bytes read, the three
    version fields in force for the run, the method check record,
    the footing check results, and the unproved ground field, which
    states the ground the run did not prove, in the open.
    """

    input_name: str = ""
    line_count: int = 0
    byte_count: int = 0
    digest: str = ""
    vocabulary_version: str = ""
    output_form_edition: str = ""
    rule_set_version: str = ""
    method_check_record: object = None
    footing_check_results: object = None
    unproved_ground: object = None


@dataclass
class LiveProofRecord:
    """The record of one live proof, as plan Item 7 names it.

    The record carries the source commit the proof ran from, the
    new public head it produced, the installed copy equality check,
    the installed position, the label state, the subcommand
    results, the file facts and the version fields the proof
    printed, the live path statement, the fresh measurement record,
    and the target verification record.
    """

    source_commit: str = ""
    new_public_head: str = ""
    equality_check: object = None
    installed_position: str = ""
    label_state: str = ""
    subcommand_results: list = field(default_factory=list)
    file_facts: object = None
    version_fields: object = None
    live_path_statement: str = ""
    fresh_measurement_record: object = None
    target_verification_record: object = None


@dataclass
class SharedHead:
    """The shared head as a six position ordered line group.

    The positions stand in the OP-Q2 order and in no other: the
    scope statement, the input name line, the file facts line, the
    limits line, the version fields line, and the residue share
    line position, which stands only where the WV-9 decision has
    taken effect to print. Shell owns the wording of the lines and
    render owns their printing only, as plan Item 3, section 3.7
    states.
    """

    scope_statement: str = ""
    input_name_line: str = ""
    file_facts_line: str = ""
    limits_line: str = ""
    version_fields_line: str = ""
    residue_share_line: str = ""
