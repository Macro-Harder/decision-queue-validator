"""Shared scaffolding for the decision queue validator suite.

This module is test scaffolding only. It is never part of the product
package. It holds the corpus access helpers, the command line runner,
the in process pipeline runner, the tolerant field accessors the groups
use to read the handoff values, and the generator for the generated
inputs family.

Expectation values in the groups come from the corpus manifest and from
the design texts the groups cite in their docstrings. Nothing in this
module computes a product expectation from a run of the tool. The
generator measures only construction facts about the inputs it builds
(for example the line count and byte count of an input as constructed),
and those facts are asserted as construction facts only.
"""

import copy
import hashlib
import importlib
import importlib.util
import inspect
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PRODUCT_ROOT = TESTS_DIR.parent
CORPUS_DIR = TESTS_DIR / "fixtures" / "decision_queue_corpus"
MANIFEST_JSON = CORPUS_DIR / "manifest.json"
MANIFEST_MD = CORPUS_DIR / "MANIFEST.md"

PACKAGE = "decision_queue_validator"
SEED_ONE = 4241
SEED_TWO = 9176
SEEDS = (SEED_ONE, SEED_TWO)

MAX_BYTES = 2000000
MAX_LINES = 10000
MAX_CHARS_PER_LINE = 16384

FIXTURE_IDS = (
    "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9",
    "S1", "S2", "S3a", "S3b", "S3c", "S4", "S4b", "S5", "S5b",
    "S6", "S7a", "S7b", "S7c", "S8", "S10", "S11", "S12", "S13",
    "S14", "S15", "S17", "S18", "S19", "S20", "S21",
)

_MANIFEST_CACHE = None


def manifest():
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is None:
        with open(MANIFEST_JSON, "r", encoding="utf-8") as handle:
            _MANIFEST_CACHE = json.load(handle)
    return _MANIFEST_CACHE


def manifest_entry(fixture_id):
    return manifest()["fixtures"][fixture_id]


def manifest_value(entry, *path):
    node = entry
    for part in path:
        node = node[part]
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return node


def corpus_path(fixture_id):
    return CORPUS_DIR / (fixture_id + ".md")


def fixture_bytes(fixture_id):
    with open(corpus_path(fixture_id), "rb") as handle:
        return handle.read()


def fixture_text(fixture_id):
    return fixture_bytes(fixture_id).decode("utf-8")


def count_lines_formula(data):
    """Line count of bytes under the decided terminator rule.

    The count is the number of line feed terminators, a carriage return
    and line feed pair counting as the one terminator its line feed
    marks, plus one further line where the bytes are not empty and do
    not end with a terminator.
    """
    if not data:
        return 0
    terminators = data.count(b"\n")
    if data.endswith(b"\n"):
        return terminators
    return terminators + 1


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------
# Command line runner
# ---------------------------------------------------------------------

def cli_env(seed):
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(seed)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(PRODUCT_ROOT)
    return env


def run_cli(subcommand, input_path, seed=SEED_ONE, output_path=None,
            extra_args=(), cwd=None):
    argv = [sys.executable, "-m", PACKAGE]
    if subcommand is not None:
        argv.append(subcommand)
    if input_path is not None:
        argv.append(str(input_path))
    argv.extend(extra_args)
    if output_path is not None:
        argv.extend(["--output", str(output_path)])
    proc = subprocess.run(
        argv,
        cwd=str(cwd or PRODUCT_ROOT),
        env=cli_env(seed),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout, proc.stderr


_CLOSED_DESCRIPTOR_DRIVER = (
    "import os, sys\n"
    "fd = int(sys.argv[1])\n"
    "args = sys.argv[2:]\n"
    "try:\n"
    "    os.close(fd)\n"
    "except OSError:\n"
    "    pass\n"
    "os.execve(sys.executable, [sys.executable, '-m', "
    "'decision_queue_validator'] + args, os.environ)\n"
)


def run_cli_closed_descriptor(argv, closed_descriptor, seed=SEED_ONE):
    """Run the CLI with a standard descriptor closed before launch.

    A small driver process closes the named descriptor and then execs
    a fresh interpreter running the module, so the child interpreter
    starts with the matching standard stream set to None, exactly the
    descriptor closed before launch condition. argv holds the module
    arguments after the module name, as plain strings.
    """
    proc = subprocess.run(
        [sys.executable, "-c", _CLOSED_DESCRIPTOR_DRIVER,
         str(closed_descriptor)] + [str(item) for item in argv],
        cwd=str(PRODUCT_ROOT),
        env=cli_env(seed),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_cli_with_timeout(subcommand, input_path, seed=SEED_ONE,
                         output_path=None, timeout=30):
    """Run the CLI under a timeout, in the run_cli argument form.

    A run that exceeds the timeout raises TimeoutExpired, failing
    the calling test rather than hanging the suite.
    """
    argv = [sys.executable, "-m", PACKAGE]
    if subcommand is not None:
        argv.append(subcommand)
    if input_path is not None:
        argv.append(str(input_path))
    if output_path is not None:
        argv.extend(["--output", str(output_path)])
    proc = subprocess.run(
        argv,
        cwd=str(PRODUCT_ROOT),
        env=cli_env(seed),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_cli_stdout_redirect(subcommand, input_path, stdout_path,
                            seed=SEED_ONE):
    """Run with standard output redirected to a regular file.

    Returns the process return code and the captured standard error
    bytes. The caller controls the state of the target file and any
    resource limits in force around the run.
    """
    argv = [sys.executable, "-m", PACKAGE, subcommand, str(input_path)]
    with open(stdout_path, "wb") as out_handle:
        proc = subprocess.run(
            argv,
            cwd=str(PRODUCT_ROOT),
            env=cli_env(seed),
            stdout=out_handle,
            stderr=subprocess.PIPE,
        )
    return proc.returncode, proc.stderr


def run_cli_stderr_redirect(argv, stderr_path, stdout_path=None,
                            seed=SEED_ONE):
    """Run with standard error redirected to a regular file.

    argv holds the module arguments after the module name, as plain
    strings. Returns the process return code and the captured
    standard output bytes, or empty standard output bytes where
    stdout_path names a regular file to receive standard output
    instead. The caller controls the state of the target files and
    any resource limits in force around the run.
    """
    full_argv = [sys.executable, "-m", PACKAGE] + \
        [str(item) for item in argv]
    with open(stderr_path, "wb") as err_handle:
        if stdout_path is not None:
            with open(stdout_path, "wb") as out_handle:
                proc = subprocess.run(
                    full_argv,
                    cwd=str(PRODUCT_ROOT),
                    env=cli_env(seed),
                    stdout=out_handle,
                    stderr=err_handle,
                )
            return proc.returncode, b""
        proc = subprocess.run(
            full_argv,
            cwd=str(PRODUCT_ROOT),
            env=cli_env(seed),
            stdout=subprocess.PIPE,
            stderr=err_handle,
        )
    return proc.returncode, proc.stdout


def run_cli_closed_pipe(subcommand, input_path, seed=SEED_ONE):
    """Run with standard output connected to a pipe with no reader."""
    argv = [sys.executable, "-m", PACKAGE, subcommand, str(input_path)]
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    proc = subprocess.Popen(
        argv,
        cwd=str(PRODUCT_ROOT),
        env=cli_env(seed),
        stdout=write_fd,
        stderr=subprocess.PIPE,
    )
    os.close(write_fd)
    _out, err = proc.communicate()
    return proc.returncode, err


_RUN_CACHE = {}


def cached_run(fixture_id, subcommand, seed=SEED_ONE):
    key = (fixture_id, subcommand, seed)
    if key not in _RUN_CACHE:
        _RUN_CACHE[key] = run_cli(subcommand, corpus_path(fixture_id),
                                  seed=seed)
    return _RUN_CACHE[key]


def expected_exit(fixture_id):
    return manifest_value(manifest_entry(fixture_id), "expected_exit_code")


# ---------------------------------------------------------------------
# Tolerant field access over handoff values
# ---------------------------------------------------------------------

def get(obj, *names, default=None):
    """Read the first named field present on a value or mapping."""
    for name in names:
        if isinstance(obj, dict):
            if name in obj:
                return obj[name]
        elif obj is not None and hasattr(obj, name):
            value = getattr(obj, name)
            if not callable(value):
                return value
    return default


def get_any(obj, names, default=None):
    return get(obj, *names, default=default)


def text_of(value):
    """Normalise an enum like or plain value to its text form."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    inner = getattr(value, "value", None)
    if isinstance(inner, str):
        return inner
    name = getattr(value, "name", None)
    if isinstance(name, str):
        return name
    return str(value)


def int_of(value):
    if isinstance(value, bool):
        raise TypeError("a boolean is not a count")
    if isinstance(value, int):
        return value
    inner = getattr(value, "value", None)
    if isinstance(inner, int):
        return inner
    return int(value)


def as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def span_of(finding_or_element):
    span = get(finding_or_element, "line_span", "span", "lines")
    if span is None:
        line = get(finding_or_element, "line", "line_number")
        if line is not None:
            return (int_of(line), int_of(line))
        return (0, 0)
    if isinstance(span, (list, tuple)) and len(span) >= 2:
        return (int_of(span[0]), int_of(span[1]))
    start = get(span, "start", "start_line", "first_line")
    end = get(span, "end", "end_line", "last_line")
    if start is None:
        return (0, 0)
    if end is None:
        end = start
    return (int_of(start), int_of(end))


# ---------------------------------------------------------------------
# Module surface resolution
# ---------------------------------------------------------------------

def import_module(part):
    return importlib.import_module(PACKAGE + "." + part)


def module_source(part):
    spec = importlib.util.find_spec(PACKAGE + "." + part)
    if spec is None or spec.origin is None:
        raise AssertionError("module not found: " + PACKAGE + "." + part)
    with open(spec.origin, "r", encoding="utf-8") as handle:
        return handle.read()


def first_callable(module, names):
    for name in names:
        candidate = getattr(module, name, None)
        if callable(candidate):
            return candidate
    raise AttributeError(
        "none of " + ", ".join(names) + " on " + module.__name__)


def build_input(parse_module, data, name):
    cls = None
    for candidate in ("Input", "InputValue"):
        cls = getattr(parse_module, candidate, None)
        if cls is not None:
            break
    if cls is None:
        raise AttributeError("no Input value type on the parse module")
    attempts = (
        lambda: cls(name, data),
        lambda: cls(data, name),
        lambda: cls(name=name, raw_bytes=data),
        lambda: cls(raw_bytes=data, name=name),
        lambda: cls(input_name=name, raw_bytes=data),
    )
    last_error = None
    for attempt in attempts:
        try:
            return attempt()
        except TypeError as error:
            last_error = error
    raise last_error


def build_limits(parse_module):
    cls = None
    for candidate in ("Limits", "LimitsValue"):
        cls = getattr(parse_module, candidate, None)
        if cls is not None:
            break
    if cls is None:
        raise AttributeError("no Limits value type on the parse module")
    for attempt in (lambda: cls(),
                    lambda: cls(MAX_BYTES, MAX_LINES, MAX_CHARS_PER_LINE),
                    lambda: cls(max_bytes=MAX_BYTES, max_lines=MAX_LINES,
                                max_characters_per_line=MAX_CHARS_PER_LINE)):
        try:
            return attempt()
        except TypeError:
            continue
    raise TypeError("the Limits value could not be constructed")


def parse_function(parse_module):
    return first_callable(
        parse_module, ("parse_queue", "parse_input", "parse", "run_parse"))


def validate_function(validate_module):
    return first_callable(
        validate_module,
        ("validate_model", "validate_queue", "validate", "run_validate"))


def build_vocabulary(validate_module):
    cls = getattr(validate_module, "Vocabulary", None)
    if cls is not None:
        for factory_name in ("shipped", "from_shipped_copy", "default",
                             "load_shipped", "from_shipped"):
            factory = getattr(cls, factory_name, None)
            if callable(factory):
                return factory()
        try:
            return cls()
        except TypeError:
            pass
    for name in ("shipped_vocabulary", "build_vocabulary",
                 "default_vocabulary"):
        factory = getattr(validate_module, name, None)
        if callable(factory):
            return factory()
    shell_module = import_module("shell")
    for name in ("build_vocabulary", "shipped_vocabulary",
                 "construct_vocabulary"):
        factory = getattr(shell_module, name, None)
        if callable(factory):
            return factory()
    raise AttributeError("no Vocabulary construction was found")


def is_failure_result(value):
    if value is None:
        return True
    type_name = type(value).__name__
    if "Failure" in type_name:
        return True
    if get(value, "failure_kinds", "kinds") is not None:
        return True
    if get(value, "entries", "units") is None and \
            get(value, "exit_decision") is not None:
        return True
    return False


def run_parse(data, name="input.md"):
    parse_module = import_module("parse")
    input_value = build_input(parse_module, data, name)
    limits = build_limits(parse_module)
    result = parse_function(parse_module)(input_value, limits)
    return result


def run_pipeline(data, name="input.md"):
    """Run parse then validate over bytes. Returns (model, output).

    Where parse returns the file level failure result, returns
    (failure_result, None).
    """
    result = run_parse(data, name)
    if is_failure_result(result):
        return result, None
    validate_module = import_module("validate")
    vocabulary = build_vocabulary(validate_module)
    shell_module = import_module("shell")
    edition = getattr(shell_module, "OUTPUT_FORM_EDITION", None)
    output = validate_function(validate_module)(result, vocabulary,
                                                edition)
    return result, output


def pipeline_for_fixture(fixture_id):
    return run_pipeline(fixture_bytes(fixture_id),
                        name=fixture_id + ".md")


_PIPELINE_CACHE = {}


def cached_pipeline(fixture_id):
    if fixture_id not in _PIPELINE_CACHE:
        _PIPELINE_CACHE[fixture_id] = pipeline_for_fixture(fixture_id)
    return _PIPELINE_CACHE[fixture_id]


def render_text(validate_output, form):
    render_module = import_module("render")
    if form == "render":
        fn = first_callable(
            render_module,
            ("render_summary", "render_render", "render_output_text"))
        try:
            return fn(validate_output)
        except TypeError:
            return first_callable(render_module, ("render_output",))(
                validate_output, "render")
    fn = first_callable(
        render_module,
        ("render_validate", "render_findings", "render_output_text"))
    try:
        return fn(validate_output)
    except TypeError:
        return first_callable(render_module, ("render_output",))(
            validate_output, "validate")


# ---------------------------------------------------------------------
# Reading entries, findings, census and reconciliation off a Validate
# output or a parse model
# ---------------------------------------------------------------------

def entries_of(container):
    entries = get(container, "entries", "entry_records",
                  "entry_results", "per_entry")
    return as_list(entries)


def entry_identifier(entry):
    ident = get(entry, "identifier", "entry_id", "id", "dq_number")
    if ident is None:
        heading = get(entry, "heading", "heading_text", "literal_heading")
        return text_of(heading)
    return text_of(ident)


def entry_by_id(container, wanted):
    for entry in entries_of(container):
        if entry_identifier(entry) == wanted:
            return entry
    return None


def entry_state(entry):
    state = get(entry, "effective_state", "state", "canonical_state",
                "reported_state")
    return text_of(state)


def entry_sub_label(entry):
    label = get(entry, "sub_label", "ambiguous_sub_label", "wv7_sub_label")
    return text_of(label)


def is_ambiguous(entry):
    if entry_state(entry) == "Ambiguous":
        return True
    report = get(entry, "ambiguous_report", "ambiguity")
    return report is not None


def findings_of(validate_output):
    findings = get(validate_output, "findings", "findings_list")
    return as_list(findings)


def finding_entry_id(finding):
    ident = get(finding, "entry_id", "entry_identifier", "identifier",
                "entry")
    return text_of(ident)


def finding_rule_number(finding):
    raw = get(finding, "rule_id", "rule", "check", "check_id")
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    text = text_of(raw)
    digits = ""
    for char in text:
        if char.isdigit():
            digits += char
        elif digits:
            break
    return int(digits) if digits else None


def finding_severity(finding):
    return text_of(get(finding, "severity", "grade"))


def finding_statement(finding):
    return text_of(get(finding, "statement", "message", "summary"))


def finding_evidence_text(finding):
    evidence = get(finding, "evidence", "verbatim_evidence", "quotes")
    if evidence is None:
        return ""
    if isinstance(evidence, str):
        return evidence
    parts = []
    for item in as_list(evidence):
        if isinstance(item, str):
            parts.append(item)
        else:
            parts.append(text_of(get(item, "text", "verbatim", "value",
                                     default="")) or "")
    return "\n".join(parts)


def findings_for(validate_output, entry_id=None, rule=None,
                 severity=None):
    chosen = []
    for finding in findings_of(validate_output):
        if entry_id is not None and finding_entry_id(finding) != entry_id:
            continue
        if rule is not None and finding_rule_number(finding) != rule:
            continue
        if severity is not None and finding_severity(finding) != severity:
            continue
        chosen.append(finding)
    return chosen


def census_of(validate_output):
    census = get(validate_output, "census", "census_entries")
    return as_list(census)


def census_class(census_entries, *name_parts):
    for entry in census_entries:
        name = text_of(get(entry, "class_name", "name", "census_class",
                           "kind")) or ""
        lowered = name.lower()
        if all(part.lower() in lowered for part in name_parts):
            return entry
    return None


def census_count(census_entry):
    return int_of(get(census_entry, "count", "member_count", "total"))


def census_members(census_entry):
    members = get(census_entry, "member_entry_ids", "members",
                  "member_ids", "entry_ids")
    return [text_of(item) for item in as_list(members)]


def reconciliation_of(validate_output):
    recon = get(validate_output, "reconciliation", "reconciliation_block",
                "reconciliation_data")
    if recon is None:
        raise AttributeError("the Validate output carries no "
                             "reconciliation block data")
    return recon


def canonical_counts(validate_output):
    recon = reconciliation_of(validate_output)
    raw = get(recon, "canonical_counts", "entries_per_canonical_state",
              "canonical_state_counts", "canonical_rows")
    counts = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            counts[text_of(key)] = int_of(value)
        return counts
    for item in as_list(raw):
        state = text_of(get(item, "state", "canonical_state", "name"))
        counts[state] = int_of(get(item, "count", "entries", "value"))
    if counts:
        return counts
    for state in ("Open", "Presented", "Parked", "Ruled", "Settled",
                  "Settled in part", "Closed as decided", "Conditional"):
        value = get(recon, state.lower().replace(" ", "_") + "_count",
                    state.lower().replace(" ", "_"))
        if value is not None:
            counts[state] = int_of(value)
    return counts


def ambiguous_count(validate_output):
    recon = reconciliation_of(validate_output)
    value = get(recon, "ambiguous_count", "ambiguous")
    if value is not None:
        return int_of(value)
    return sum(1 for entry in entries_of(validate_output)
               if is_ambiguous(entry))


def unparsed_count(validate_output):
    recon = reconciliation_of(validate_output)
    value = get(recon, "unparsed_count", "unparsed_entries",
                "unparsed_row")
    if value is not None:
        return int_of(value)
    return sum(1 for entry in entries_of(validate_output)
               if get(entry, "unparsed", "unparsed_flag"))


def entry_total(validate_output):
    recon = reconciliation_of(validate_output)
    value = get(recon, "entry_total", "headed_entry_count", "entry_count")
    if value is None:
        facts = get(validate_output, "file_facts", "file_facts_data")
        value = get(facts, "entry_count", "entry_total")
    if value is None:
        raise AttributeError("no entry total on the Validate output")
    return value


def exit_decision_of(validate_output):
    decision = get(validate_output, "exit_decision", "exit")
    if decision is None:
        raise AttributeError("no Exit decision on the Validate output")
    return decision


def exit_code_of(validate_output):
    decision = exit_decision_of(validate_output)
    if isinstance(decision, int):
        return decision
    return int_of(get(decision, "code", "exit_code", "value"))


def reason_classes_of(validate_output):
    decision = exit_decision_of(validate_output)
    raw = get(decision, "reason_classes", "reasons", "reason_class_set",
              "causes")
    return [text_of(item) for item in as_list(raw)]


def waiting_and_blocking(validate_output):
    waiting = get(validate_output, "waiting", "waiting_figure",
                  "waiting_count")
    blocking = get(validate_output, "blocking", "blocking_figure",
                   "blocking_count")
    if waiting is None or blocking is None:
        figures = get(validate_output, "project_manager_figures",
                      "pm_figures", "figures")
        if figures is not None:
            if waiting is None:
                waiting = get(figures, "waiting", "waiting_count")
            if blocking is None:
                blocking = get(figures, "blocking", "blocking_count")
    return waiting, blocking


def find_type(name):
    candidates = []
    package = importlib.import_module(PACKAGE)
    candidates.append(package)
    for part in ("parse", "validate", "render", "shell", "types",
                 "model", "core"):
        try:
            candidates.append(import_module(part))
        except Exception:
            pass
    for module in candidates:
        value = getattr(module, name, None)
        if isinstance(value, type):
            return value
    return None


# ---------------------------------------------------------------------
# Model doubles, built in the scaffolding only
# ---------------------------------------------------------------------

class HeaderFactsDouble:
    """A stand in for the parse owned file header facts of a model."""

    def __init__(self, unit_counts=None, byte_count=0, line_count=0,
                 longest_line_length=0, input_name="double.md"):
        self.unit_counts = dict(unit_counts or {})
        self.counts_by_kind = dict(unit_counts or {})
        self.byte_count = byte_count
        self.line_count = line_count
        self.longest_line_length = longest_line_length
        self.input_name = input_name
        self.digest = "0" * 64


class ParseModelDouble:
    """A parse model stand in handed to validate at a named seam.

    The double carries the model fields the validate boundary reads.
    Its counts are internally consistent except where a test states a
    deliberate break.
    """

    def __init__(self, entries=(), units=(), orphan_segments=(),
                 unassigned_lines=(), double_assigned_lines=(),
                 parse_notes=(), h4_sub_heading_count=0,
                 header_facts=None, input_name="double.md"):
        self.entries = list(entries)
        self.units = list(units)
        self.orphan_segments = list(orphan_segments)
        self.unassigned_lines = list(unassigned_lines)
        self.double_assigned_lines = list(double_assigned_lines)
        self.parse_notes = list(parse_notes)
        self.h4_sub_heading_count = h4_sub_heading_count
        if header_facts is None:
            header_facts = HeaderFactsDouble(
                unit_counts={"entry": len(self.entries),
                             "orphan_segment": len(self.orphan_segments)},
                input_name=input_name)
        self.header_facts = header_facts
        self.file_header_facts = self.header_facts
        self.input_name = input_name


def check6_model_double():
    """One line assigned to no unit and one line assigned to two."""
    return ParseModelDouble(unassigned_lines=[7],
                            double_assigned_lines=[9])


def self_check_model_double():
    """A model whose parse owned entry unit count breaks the sum.

    The header facts claim two entry units while the entry list holds
    one entry, so the entry total validate computes from its own list
    cannot agree with the parse owned count the self check compares it
    against.
    """
    entry = {
        "identifier": "DQ-901",
        "heading": "DQ-901: A doubled count entry",
        "heading_text": "DQ-901: A doubled count entry",
        "elements": [],
        "status_elements": [],
        "fields": [],
        "decision_blocks": [],
        "unparsed": False,
    }
    facts = HeaderFactsDouble(unit_counts={"entry": 2,
                                           "orphan_segment": 0})
    return ParseModelDouble(entries=[entry], header_facts=facts)


# ---------------------------------------------------------------------
# The generated inputs family
# ---------------------------------------------------------------------

def _queue_entry(number, title, extra_lines=()):
    lines = [
        "### DQ-%03d: %s" % (number, title),
        "",
        "Status: Banked",
        "",
        "Owner of record: Decision-queue Clerk",
        "",
        "The question: A generated question for entry %d." % number,
        "",
        "Options:",
        "- Option A: proceed.",
        "- Option B: wait.",
        "",
        "Cost of deciding late: low.",
        "",
        "What it blocks: a generated note.",
        "",
    ]
    lines.extend(extra_lines)
    return "\n".join(lines) + "\n"


def _header_block():
    return "# Decision queue\n\nGenerated queue shaped input.\n\n"


def limit_bytes_input():
    body = _header_block() + _queue_entry(901, "A byte limit entry")
    filler = "Filler line of plain queue prose.\n"
    repeats = (MAX_BYTES // len(filler)) + 2
    data = (body + filler * repeats).encode("utf-8")
    return data, {"bytes": len(data)}


def limit_lines_input():
    lines = ["# Decision queue", ""]
    lines.append("### DQ-901: A line limit entry")
    lines.append("")
    lines.append("Status: Banked")
    lines.append("")
    while len(lines) < MAX_LINES + 1:
        lines.append("A valid queue shaped prose line.")
    data = ("\n".join(lines) + "\n").encode("utf-8")
    return data, {"lines": count_lines_formula(data), "bytes": len(data)}


def limit_chars_input():
    long_line = "x" * (MAX_CHARS_PER_LINE + 1)
    body = _header_block() + _queue_entry(901, "A long line entry")
    data = (body + long_line + "\n").encode("utf-8")
    return data, {"longest_line_characters": MAX_CHARS_PER_LINE + 1,
                  "bytes": len(data)}


def terminator_lines_input(total_terminators):
    lines = ["# Decision queue", "", "### DQ-901: Terminator entry", "",
             "Status: Banked", ""]
    while len(lines) < total_terminators:
        lines.append("A valid queue shaped prose line.")
    data = ("\n".join(lines[:total_terminators]) + "\n").encode("utf-8")
    return data, {"lines": count_lines_formula(data), "bytes": len(data)}


def lone_carriage_return_input():
    """The six model line construction, exactly as stated for it.

    CR stands for one carriage return character and LF for one line
    feed character in these comments only.
    """
    lines = []
    lines.append("### DQ-901: Lone carriage return case\n")
    lines.append("alpha\rbeta\n")
    lines.append("gamma\r\r" + "delta\n")
    lines.append("epsilon\r" + "\r\n")
    lines.append("Status: Banked\rnoted\n")
    lines.append("omega\r")
    data = "".join(lines).encode("utf-8")
    expected_texts = [
        "### DQ-901: Lone carriage return case",
        "alpha\rbeta",
        "gamma\r\r" + "delta",
        "epsilon\r",
        "Status: Banked\rnoted",
        "omega\r",
    ]
    facts = {"lines": count_lines_formula(data), "bytes": len(data),
             "expected_texts": expected_texts}
    return data, facts


def doubled_input():
    """Renumbered duplication of real extracts, generated, not stored.

    The construction takes fixture R3 and fixture R9, then a second
    copy of each with its entry number raised, joined with blank
    separator lines. The facts returned are construction facts about
    the bytes as built.
    """
    first = fixture_bytes("R3")
    second = fixture_bytes("R9")
    first_copy = first.replace(b"DQ-050", b"DQ-051")
    second_copy = second.replace(b"DQ-099", b"DQ-100")
    separator = b"\n"
    data = first + separator + first_copy + separator + second + \
        separator + second_copy
    facts = {"lines": count_lines_formula(data), "bytes": len(data),
             "source_fixtures": ["R3", "R9"],
             "renumbered": [("DQ-050", "DQ-051"), ("DQ-099", "DQ-100")]}
    return data, facts


def combined_defects_input():
    """Four independent recoverable defects in one valid queue file.

    Carriers are kept apart: the duplicate pair are both recognised
    entry headings; the gap is read from recognised headings only
    (901 and 903 stand, 902 is missing); the near marker line stands
    inside the DQ-903 entry span; the unmatched heading stands after
    the last entry, and its orphan span holds only its own lines.
    """
    parts = [_header_block()]
    parts.append(_queue_entry(901, "A first entry"))
    parts.append(_queue_entry(901, "A duplicate entry"))
    parts.append(_queue_entry(
        903, "An entry carrying a near marker line",
        extra_lines=["status: Banked", ""]))
    parts.append("##### An unmatched generated heading\n")
    parts.append("\n")
    parts.append("Prose standing under the unmatched heading.\n")
    data = "".join(parts).encode("utf-8")
    facts = {"lines": count_lines_formula(data), "bytes": len(data),
             "missing_numbers": [902]}
    return data, facts


def unmatched_heading_input(variant):
    base = fixture_bytes("S5")
    if variant == "second_h1":
        extra = b"\n# A second top level heading\n\nProse under it.\n"
    elif variant == "h5":
        extra = b"\n##### A level five heading\n\nProse under it.\n"
    elif variant == "h6":
        extra = b"\n###### A level six heading\n\nProse under it.\n"
    else:
        raise ValueError("unknown unmatched heading variant: " + variant)
    if not base.endswith(b"\n"):
        base = base + b"\n"
    return base + extra, {"variant": variant}


def coincident_input():
    """Two status bearing elements on one line of one paragraph."""
    body = _header_block()
    body += "### DQ-901: A coincident element entry\n\n"
    body += "Owner of record: Decision-queue Clerk\n\n"
    body += "Status: Banked Status: Ruled by Captain JP\n"
    data = body.encode("utf-8")
    return data, {"lines": count_lines_formula(data), "bytes": len(data)}


def temp_input(data, name="generated_input.md"):
    """Write generated bytes to a fresh temporary file and return it."""
    handle = tempfile.NamedTemporaryFile(
        mode="wb", suffix=".md", prefix="dqv_generated_", delete=False)
    handle.write(data)
    handle.close()
    return Path(handle.name)


def make_unreadable_input(directory):
    """Return a path naming an input the run cannot read.

    A permissions based unreadable file is tried first. Where the
    running account can still read it, a path through a regular file
    is used instead, which no account can open as a file.
    """
    target = Path(directory) / "unreadable_input.md"
    target.write_bytes(b"# Decision queue\n")
    os.chmod(target, 0)
    try:
        with open(target, "rb") as handle:
            handle.read()
    except OSError:
        return target
    blocker = Path(directory) / "blocker.md"
    blocker.write_bytes(b"plain file\n")
    return blocker / "unreadable_input.md"


def deepcopy_value(value):
    return copy.deepcopy(value)
