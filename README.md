# Decision Queue Validator

A small offline command line tool that checks one Markdown decision
queue file for form and internal consistency, and reports what it
finds. It checks the file only. It does not judge whether any ruling
recorded in the file was right, and its reports are advisory: a report
may not be cited as a pass or fail condition for any step, gate, or
release.

## Running it

The tool runs with Python 3 and uses only the standard library.
Nothing is installed and no network access is needed or used.

```
python3 -m decision_queue_validator validate QUEUE.md
python3 -m decision_queue_validator render QUEUE.md
```

Each run takes exactly one input file. Both subcommands read the same
file in the same way; they differ only in the output they print.

- `validate` prints the findings report: a head with the file facts, an
  index of the per entry findings, the findings themselves grouped by
  entry, the list of checks that fired, and the census of special
  entries.
- `render` prints the readable summary: the reconciliation block, the
  census, the open and decided entry groups, the docket of entries
  whose state could not be determined and of entries carrying a
  status disagreement finding, the counts, the verbatim appendix of
  Status phrasings as written, and the summary figures for the queue
  (how many entries are waiting, how many block other work, and the
  blocks and effort coverage the file carries). The summary also
  reports whether the fastest item to clear is derivable from the
  file: in this version it is always reported as not derivable from
  the file. An entry carries an effort signal where it records an
  effort field or an Effort line.

In the census, member lists name one identifier per member entry, so
a number that heads two entries appears twice.

By default the output goes to standard output. To write it to a file
instead, add `--output`:

```
python3 -m decision_queue_validator render QUEUE.md --output summary.txt
```

The output is composed in full before any of it is written. A named
output file is replaced whole, by way of a temporary file in the same
directory, so a failed write leaves no partial file behind and leaves
an existing output file untouched. Naming the input file itself as
the output is refused, so a run can never overwrite the queue it is
checking. The input file is never modified by any run, and the tool
itself writes nothing else: no log file and no run record. In a
default environment one run does leave a cache behind in the tool's
own directory, written by the Python interpreter rather than by the
tool: a `decision_queue_validator/__pycache__` directory holding
`.pyc` files, the interpreter's standard import behaviour. Running
with `PYTHONDONTWRITEBYTECODE=1` set suppresses that cache, and no
cache is left then.

## Input

One Markdown decision queue file per run, written in the queue forms
the tool recognises: a queue header, entry headings, Status lines and
the decision evidence recorded inside entries. A file with no
recognisable queue structure is refused as a whole, as described
under exit code 3 below.

A minimal example of a queue file in those forms:

```
# Decision queue

### DQ-001: A sample open question

Status: Banked
```

Three size limits apply, and a file that breaches one is refused as a
whole:

- 2,000,000 bytes per file
- 10,000 lines per file
- 16,384 characters per line

## Exit codes

The exit code reports what the run found. It never means that the
queue itself is valid or invalid.

- 0: the run completed and reported no findings, or Note findings
  only.
- 1: the run completed and reported Error or Warning findings.
- 2: the run did not take place, or its output could not be
  delivered. This covers usage errors, an input file that is missing,
  unreadable, a directory, or not a regular file, the refusal of an
  output file that is the same file as the input, and a failed write
  or a closed standard output. Failures of this kind are reported on
  the standard error channel where they concern delivery.
- 3: the file was refused as a whole and no entry report was
  produced. This covers a file that is not valid text, a file that
  breaches one of the size limits (the report names the breached
  limit and the measured value), an empty file, a header only file,
  and a file with no recognisable queue structure.
- 4: the run completed, but the file contains material whose state
  could not be determined (Ambiguous or Conditional entries, or an
  entry that could not be parsed), or the tool's own consistency
  check failed on the run. Totals in the report are then stated under
  that condition, and the closing line of the report names each cause
  present. Exit 4 takes precedence over exit 1, so a run can carry
  Error or Warning findings and still exit 4; the findings themselves
  are still printed in full.

Running either subcommand twice over the same input produces the same
output and the same exit code. The tool keeps no state between runs.
