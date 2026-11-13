"""Shell: the only module that touches the filesystem and the terminal.

Duties (DESIGN-BRIEF.md 5.1): argument handling for the two
subcommands, reading the input once as bytes, constructing the
Vocabulary value from the shipped copy, calling parse, validate and
render in that order, composing the output in full, the write
mechanism for a named output file, head composition for the exit 2
and file level exit 3 runs from the constants held here, failure
reports on the standard error channel, and return of the exit code
the run carries. The shell assigns no state, grades no finding,
counts nothing, decodes nothing and takes no limit measurement.
"""

import os
import stat
import sys
import tempfile

from .parse import parse_queue
from .render import render_summary, render_validate
from .types import FileLevelFailure, Input, Limits, Vocabulary
from .validate import validate_model

OUTPUT_FORM_EDITION = "1"

LIMITS = Limits()

VOCABULARY_VERSION = Vocabulary.shipped().version

__all__ = [
    "OUTPUT_FORM_EDITION",
    "LIMITS",
    "VOCABULARY_VERSION",
    "build_vocabulary",
    "main",
]


def build_vocabulary():
    """Construct the Vocabulary value from the shipped copy."""
    return Vocabulary.shipped()


def _limits_line(with_units):
    if with_units:
        return (
            "Limits in force: {:,} bytes per file; {:,} lines per file; "
            "{:,} characters per line; vocabulary version {}; output form "
            "edition {}".format(
                LIMITS.max_bytes,
                LIMITS.max_lines,
                LIMITS.max_characters_per_line,
                VOCABULARY_VERSION,
                OUTPUT_FORM_EDITION,
            )
        )
    return (
        "Limits in force: {}; {}; {}; vocabulary version {}; output form "
        "edition {}".format(
            LIMITS.max_bytes,
            LIMITS.max_lines,
            LIMITS.max_characters_per_line,
            VOCABULARY_VERSION,
            OUTPUT_FORM_EDITION,
        )
    )


def _head_lines(file_facts_line, limits_line):
    """Compose the shell held head for runs with no Validate output."""
    lines = [
        "Decision queue validator",
        "Scope: this run checks form and internal consistency of this one "
        "file only. Not checked: the truth of any ruling, landings in "
        "other documents, companion trace files, and any step closure.",
        "Advisory bound: this report may not be cited as a pass or fail "
        "condition for any step, gate, or release until Captain JP rules "
        "otherwise.",
    ]
    if file_facts_line is not None:
        lines.append(file_facts_line)
    lines.append(limits_line)
    return lines


def _not_read_output(input_name):
    """The input not read form: the name as given, and no measurements."""
    lines = _head_lines(
        "File facts: {}; input not read".format(input_name),
        _limits_line(True),
    )
    lines.append("")
    lines.append(
        "The input file was not read: it is missing, unreadable, a "
        "directory, or not a regular file, so no run took place."
    )
    return "\n".join(lines) + "\n"


def _refusal_output(input_name, output_name):
    """The refusal form for output equals input, distinct from exit 3."""
    lines = _head_lines(
        "File facts: {}; refused: the named output file {} resolves to "
        "the same file as the input file".format(input_name, output_name),
        _limits_line(True),
    )
    lines.append("")
    lines.append(
        "The run is refused before any parse, before any writing, and "
        "before any output is composed, so the input file cannot be "
        "overwritten by its own report."
    )
    return "\n".join(lines) + "\n"


def _file_level_output(failure, subcommand):
    """Compose the whole output for a file level (exit 3) run."""
    facts = [
        failure.input_name,
        "{} bytes".format(failure.byte_count),
    ]
    if failure.line_count is not None:
        facts.append("{} lines".format(failure.line_count))
    if failure.digest:
        facts.append("digest {}".format(failure.digest[:12]))
    facts.append("entry count: not parsed")
    lines = _head_lines(
        "File facts: " + "; ".join(facts),
        _limits_line(True),
    )
    lines.append("")
    lines.append("File level failure: this file was not parsed.")
    for kind in failure.failure_kinds or []:
        lines.append("Failure kind: {}".format(kind))
    if failure.breached_limit:
        lines.append(
            "Breached limit: {} (measured value {})".format(
                failure.breached_limit, failure.measured_value
            )
        )
    for name in failure.breached_limits or []:
        if name != failure.breached_limit:
            lines.append("Breached limit: {}".format(name))
    if failure.missing_structure:
        lines.append(
            "Missing structure: {}".format(failure.missing_structure)
        )
    lines.append("")
    other = "render" if subcommand == "validate" else "validate"
    lines.append(
        "The {} subcommand shows the other output form of the tool; on "
        "this file it reaches the same file level outcome.".format(other)
    )
    decision = failure.exit_decision
    reasons = "; ".join(decision.reason_classes or [])
    lines.append(
        "exit {}: {}; this exit code is a file level signal and is not a "
        "step verdict.".format(decision.code, reasons)
    )
    return "\n".join(lines) + "\n"


def _usage_error(message):
    try:
        sys.stderr.write("usage error: {}\n".format(message))
        sys.stderr.write(
            "usage: python3 -m decision_queue_validator "
            "{validate|render} INPUT [--output OUTPUT]\n"
        )
    except (OSError, AttributeError, ValueError):
        pass
    return 2


def _report_stderr(message):
    try:
        sys.stderr.write(message + "\n")
        sys.stderr.flush()
    except (OSError, AttributeError, ValueError):
        pass


def _deliver(text, output_path):
    """Deliver the composed output; return 0, or 2 when delivery fails."""
    data = text.encode("utf-8")
    if output_path is None:
        try:
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        except (OSError, AttributeError, ValueError) as exc:
            try:
                sys.stdout.close()
            except (OSError, AttributeError, ValueError):
                pass
            _report_stderr(
                "error: standard output was closed before the output was "
                "delivered ({})".format(exc)
            )
            return 2
        return 0
    try:
        existing_stat = os.stat(output_path)
    except OSError:
        existing_stat = None
    if existing_stat is not None and not stat.S_ISREG(
            existing_stat.st_mode):
        reason = "Is a directory" if stat.S_ISDIR(
            existing_stat.st_mode) else "Not a regular file"
        _report_stderr(
            "error: could not write the output file {} ({})".format(
                output_path, reason
            )
        )
        return 2
    directory = os.path.dirname(os.path.abspath(output_path))
    handle = None
    temp_path = None
    try:
        handle, temp_path = tempfile.mkstemp(
            dir=directory, prefix=".dqv-output-", suffix=".tmp"
        )
        with os.fdopen(handle, "wb") as stream:
            handle = None
            stream.write(data)
            stream.flush()
        os.replace(temp_path, output_path)
        temp_path = None
    except OSError as exc:
        if handle is not None:
            try:
                os.close(handle)
            except OSError:
                pass
        if temp_path is not None:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        reason = getattr(exc, "strerror", None) or \
            "the write could not be completed"
        _report_stderr(
            "error: could not write the output file {} ({})".format(
                output_path, reason
            )
        )
        return 2
    return 0


def _same_file(input_path, output_path):
    try:
        input_stat = os.stat(input_path)
        output_stat = os.stat(output_path)
    except OSError:
        return False
    return (input_stat.st_dev, input_stat.st_ino) == (
        output_stat.st_dev,
        output_stat.st_ino,
    )


def main(argv=None):
    """Run one command line invocation; return the exit code it carries."""
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)
    if argv and argv[0] not in ("validate", "render"):
        return _usage_error("unknown subcommand: {}".format(argv[0]))
    if len(argv) < 2:
        return _usage_error("a subcommand and an input file are required")
    subcommand = argv[0]
    input_name = argv[1]
    output_name = None
    rest = argv[2:]
    index = 0
    while index < len(rest):
        token = rest[index]
        if token == "--output":
            if index + 1 >= len(rest):
                return _usage_error("--output requires a value")
            if output_name is not None:
                return _usage_error("--output given twice")
            output_name = rest[index + 1]
            index += 2
        elif token.startswith("--output="):
            if output_name is not None:
                return _usage_error("--output given twice")
            output_name = token[len("--output="):]
            if not output_name:
                return _usage_error("--output requires a value")
            index += 1
        else:
            return _usage_error("unexpected argument: {}".format(token))

    # Exit 2 input branches, decided before any read attempt.
    try:
        input_stat = os.stat(input_name)
    except OSError:
        delivered = _deliver(_not_read_output(input_name), output_name)
        return delivered if delivered != 0 else 2
    if stat.S_ISDIR(input_stat.st_mode) or not stat.S_ISREG(input_stat.st_mode):
        delivered = _deliver(_not_read_output(input_name), output_name)
        return delivered if delivered != 0 else 2

    # Output equals input is refused on file identity, before any
    # parse, before any writing, and before any output is composed.
    if output_name is not None and _same_file(input_name, output_name):
        delivered = _deliver(_refusal_output(input_name, output_name), None)
        return delivered if delivered != 0 else 2

    # Read the input once, as bytes.
    try:
        with open(input_name, "rb") as stream:
            raw_bytes = stream.read()
    except OSError:
        delivered = _deliver(_not_read_output(input_name), output_name)
        return delivered if delivered != 0 else 2

    vocabulary = build_vocabulary()
    result = parse_queue(
        Input(input_name=input_name, raw_bytes=raw_bytes), LIMITS
    )
    if isinstance(result, FileLevelFailure):
        delivered = _deliver(_file_level_output(result, subcommand), output_name)
        if delivered != 0:
            return delivered
        return result.exit_decision.code

    output = validate_model(result, vocabulary, OUTPUT_FORM_EDITION)
    if subcommand == "validate":
        text = render_validate(output)
    else:
        text = render_summary(output)
    delivered = _deliver(text, output_name)
    if delivered != 0:
        return delivered
    return output.exit_decision.code
