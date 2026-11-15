"""Restart Slice 1 tests, group TG-S1-01.

Source: plan Item 2, section 2.3, against the shapes at plan Item 3,
sections 3.1 to 3.9, and the exit condition at plan Item 1, section 1.2.
No fixture file is relied on, as section 2.3 states. Expectations come
from Item 3 only. The first run test files and the first run product
types are base material and data only: where a first run type merges a
distinction the restart texts keep apart, these tests fail against it,
and that failure is the expected state before the Step 14 build.

A name may differ in code, so shape discovery accepts the candidate
names listed per shape. A distinction may not be merged away, so the
field groups and the separation tests bind in every naming form.
"""

import dataclasses
import importlib
import inspect
import re
import unittest

import dqv_harness as h

CANONICAL_STATES = (
    "Open", "Presented", "Parked", "Ruled", "Settled",
    "Settled in part", "Conditional", "Closed as decided",
)

LIMIT_VALUES = {"byte": 2000000, "line": 10000, "per_line": 16384}


def _modules():
    mods = []
    try:
        mods.append(importlib.import_module(h.PACKAGE))
    except Exception:
        pass
    for part in ("types", "parse", "validate", "render", "shell",
                 "model", "core"):
        try:
            mods.append(h.import_module(part))
        except Exception:
            pass
    return mods


def find_shape(names):
    for mod in _modules():
        for name in names:
            value = getattr(mod, name, None)
            if isinstance(value, type):
                return value
    return None


def _norm(name):
    return name.lower().replace("_", "").replace(" ", "")


def field_names(cls):
    if dataclasses.is_dataclass(cls):
        return [item.name for item in dataclasses.fields(cls)]
    try:
        params = list(inspect.signature(cls.__init__).parameters)
        return [name for name in params if name != "self"]
    except (TypeError, ValueError):
        return list(getattr(cls, "__annotations__", {}))


def resolve_field(cls, synonyms):
    fields = field_names(cls)
    for synonym in synonyms:
        if synonym in fields:
            return synonym
    wanted = {_norm(synonym) for synonym in synonyms}
    for name in fields:
        if _norm(name) in wanted:
            return name
    return None


def _dummy(cls, field_name, annotation):
    text = (str(annotation) + " " + field_name).lower()
    if "bytes" in text:
        return b"bytes"
    if "bool" in text:
        return False
    if "list" in text or "sequence" in text:
        return []
    if "dict" in text or "map" in text:
        return {}
    if "float" in text:
        return 1.0
    if ("int" in text or "count" in field_name or "line" in field_name
            or "number" in field_name or "size" in field_name
            or "code" in field_name):
        return 1
    nested = find_shape([str(annotation).strip("'\" ")]) \
        if annotation else None
    if nested is not None and nested is not cls:
        try:
            return build_value(nested)
        except Exception:
            pass
    return "text"


def build_value(cls, overrides=None):
    overrides = overrides or {}
    resolved = {}
    for synonyms, value in overrides.items():
        if isinstance(synonyms, str):
            synonyms = (synonyms,)
        actual = resolve_field(cls, synonyms)
        if actual is not None:
            resolved[actual] = value
    kwargs = {}
    if dataclasses.is_dataclass(cls):
        for item in dataclasses.fields(cls):
            if item.name in resolved:
                kwargs[item.name] = resolved[item.name]
            elif item.default is not dataclasses.MISSING:
                continue
            elif item.default_factory is not dataclasses.MISSING:
                continue
            else:
                kwargs[item.name] = _dummy(cls, item.name, item.type)
        return cls(**kwargs)
    params = list(inspect.signature(cls.__init__).parameters.values())
    for param in params:
        if param.name == "self":
            continue
        if param.name in resolved:
            kwargs[param.name] = resolved[param.name]
        elif param.default is not inspect.Parameter.empty:
            continue
        else:
            kwargs[param.name] = _dummy(cls, param.name, param.annotation)
    return cls(**kwargs)


def require_shape(testcase, names, label):
    cls = find_shape(names)
    testcase.assertIsNotNone(
        cls, "restart shape not found for " + label +
        "; the Step 14 build must provide it under a candidate name")
    return cls


def assert_groups(testcase, cls, groups, label):
    for group_label, synonyms in groups:
        with testcase.subTest(shape=label, field_group=group_label):
            testcase.assertIsNotNone(
                resolve_field(cls, synonyms),
                label + " carries no field for " + group_label +
                "; fields standing: " + ", ".join(field_names(cls)))


SHAPE_CANDIDATES = {
    "File": ("File", "QueueFile", "QueueFileModel"),
    "File level unit": ("FileLevelUnit", "FileLevelSegment", "Unit",
                        "OrphanSegment"),
    "Entry": ("Entry", "EntryRecord", "HeadedEntry"),
    "Status bearing element": ("StatusBearingElement", "StatusElement",
                               "Element"),
    "Finding": ("Finding",),
    "Census row": ("CensusRow", "CensusEntry", "CensusClass"),
    "Verbatim appendix row": ("VerbatimAppendixRow", "AppendixRow"),
    "Residue item": ("ResidueItem", "ResidueEntry"),
    "Render model": ("RenderModel", "ValidateOutput"),
    "Exit decision": ("ExitDecision",),
}


class ConstantsTest(unittest.TestCase):

    def test_limits_build_with_plan_values_and_units(self):
        cls = require_shape(self, ("Limits", "LimitsValue"), "Limits")
        value = build_value(cls)
        byte_field = resolve_field(
            cls, ("max_bytes", "byte_limit", "bytes_limit", "bytes"))
        line_field = resolve_field(
            cls, ("max_lines", "line_limit", "lines_limit", "lines"))
        per_line_field = resolve_field(
            cls, ("max_characters_per_line", "per_line_limit",
                  "max_characters", "characters_per_line"))
        self.assertIsNotNone(byte_field, "no byte limit field")
        self.assertIsNotNone(line_field, "no line limit field")
        self.assertIsNotNone(per_line_field, "no per line limit field")
        self.assertEqual(h.int_of(getattr(value, byte_field)),
                         LIMIT_VALUES["byte"])
        self.assertEqual(h.int_of(getattr(value, line_field)),
                         LIMIT_VALUES["line"])
        self.assertEqual(h.int_of(getattr(value, per_line_field)),
                         LIMIT_VALUES["per_line"])

    def test_limits_build_twice_with_the_same_constant_values(self):
        cls = require_shape(self, ("Limits", "LimitsValue"), "Limits")
        first = build_value(cls)
        second = build_value(cls)
        self.assertEqual(first, second)

    def test_vocabulary_value_builds_with_version_one(self):
        cls = require_shape(self, ("Vocabulary", "VocabularyValue"),
                            "Vocabulary")
        value = None
        for factory_name in ("shipped", "from_shipped_copy", "default",
                             "load_shipped"):
            factory = getattr(cls, factory_name, None)
            if callable(factory):
                value = factory()
                break
        if value is None:
            value = build_value(cls)
        version = h.get(value, "version", "vocabulary_version")
        self.assertIsNotNone(version, "vocabulary carries no version")
        self.assertEqual(h.text_of(version), "1")

    def test_vocabulary_value_compares_for_equality(self):
        cls = require_shape(self, ("Vocabulary", "VocabularyValue"),
                            "Vocabulary")
        try:
            first = h.build_vocabulary(h.import_module("validate"))
            second = h.build_vocabulary(h.import_module("validate"))
        except Exception:
            first = build_value(cls)
            second = build_value(cls)
        self.assertEqual(first, second)

    def _version_carriers(self):
        carriers = {}
        patterns = {
            "vocabulary": ("vocabulary_version", "VOCABULARY_VERSION",
                           "vocabularyversion"),
            "output form": ("output_form_edition", "OUTPUT_FORM_EDITION",
                            "outputformedition", "edition"),
            "rule set": ("rule_set_version", "RULE_SET_VERSION",
                         "rulesetversion"),
        }
        for label, names in patterns.items():
            for mod in _modules():
                for name in names:
                    if hasattr(mod, name):
                        value = getattr(mod, name)
                        if not callable(value) and \
                                not isinstance(value, type):
                            carriers[label] = (name, value)
                            break
                if label in carriers:
                    break
        vocab_cls = find_shape(("Vocabulary", "VocabularyValue"))
        if "vocabulary" not in carriers and vocab_cls is not None:
            try:
                value = build_value(vocab_cls)
                version = h.get(value, "version")
                if version is not None:
                    carriers["vocabulary"] = ("version", version)
            except Exception:
                pass
        shell = None
        try:
            shell = h.import_module("shell")
        except Exception:
            pass
        if shell is not None and "output form" not in carriers:
            value = h.get(shell, "OUTPUT_FORM_EDITION",
                          "output_form_edition")
            if value is not None:
                carriers["output form"] = ("OUTPUT_FORM_EDITION", value)
        return carriers

    def test_three_version_fields_are_distinct_carriers_each_one(self):
        carriers = self._version_carriers()
        for label in ("vocabulary", "output form", "rule set"):
            with self.subTest(carrier=label):
                self.assertIn(
                    label, carriers,
                    "no distinct carrier stands for the " + label +
                    " version field; the three version fields at plan "
                    "Item 3, section 3.8 must stand as three carriers")
                self.assertEqual(h.text_of(carriers[label][1]), "1")
        names = [carriers[label][0] for label in carriers]
        self.assertEqual(len(names), len(set(names)),
                         "version carriers are not distinct fields")

    def test_version_field_printed_form_has_no_padding_or_separator(self):
        carriers = self._version_carriers()
        self.assertTrue(carriers, "no version carrier stands at all")
        for label, (_name, value) in carriers.items():
            with self.subTest(carrier=label):
                text = h.text_of(value)
                self.assertIsNotNone(
                    re.fullmatch(r"[0-9]+", text or ""),
                    "version value does not print as an unsigned "
                    "integer: " + repr(text))
                self.assertEqual(str(int(text)), text,
                                 "version value carries padding")

    def test_canonical_state_set_is_closed_at_eight_without_ambiguous(self):
        found = None
        for mod in _modules():
            for name in dir(mod):
                if "state" not in name.lower():
                    continue
                value = getattr(mod, name)
                if isinstance(value, (list, tuple, set, frozenset)):
                    texts = [h.text_of(item) for item in value]
                    if "Closed as decided" in texts:
                        found = set(texts)
        if found is None:
            vocab_cls = find_shape(("Vocabulary", "VocabularyValue"))
            self.assertIsNotNone(
                vocab_cls,
                "no canonical state set stands in any module and no "
                "vocabulary value stands to read one from")
            self.fail("no canonical state set constant stands in the "
                      "product modules; Item 3, section 3.8 fixes the "
                      "closed set of eight states as a shape constant")
        self.assertEqual(found, set(CANONICAL_STATES))
        self.assertNotIn("Ambiguous", found)


class ShapeFieldsTest(unittest.TestCase):

    def test_file_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["File"], "File")
        assert_groups(self, cls, (
            ("input name as given", ("input_name_as_given", "input_name",
                                     "name_as_given")),
            ("source designation", ("source_designation", "designation",
                                    "source")),
            ("raw bytes as read", ("raw_bytes_as_read", "raw_bytes",
                                   "bytes_as_read")),
            ("line count", ("line_count",)),
            ("byte count", ("byte_count",)),
            ("digest", ("digest", "digest_of_bytes_read")),
            ("header facts", ("header_facts", "header")),
            ("file level units", ("file_level_units", "units",
                                  "file_units")),
            ("entries", ("entries",)),
            ("unassigned lines", ("unassigned_lines", "unassigned")),
            ("number ledger", ("number_ledger", "ledger",
                               "dq_number_ledger", "number_map")),
        ), "File")

    def test_file_level_unit_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["File level unit"],
                            "File level unit")
        assert_groups(self, cls, (
            ("unit identifier", ("unit_identifier", "identifier")),
            ("kind", ("kind",)),
            ("span", ("span", "line_span")),
            ("text as written", ("text_as_written", "text", "lines")),
        ), "File level unit")

    def test_entry_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Entry"], "Entry")
        assert_groups(self, cls, (
            ("identifier", ("identifier", "entry_identifier", "id")),
            ("heading level", ("heading_level",)),
            ("heading text verbatim", ("heading_text_verbatim",
                                       "heading_text", "heading")),
            ("spans", ("spans", "span")),
            ("status bearing elements", ("status_bearing_elements",
                                         "status_elements", "elements")),
            ("decider label as recorded", ("decider_label_as_recorded",
                                           "decider_label", "decider")),
            ("remainder texts", ("remainder_texts", "remainders",
                                 "remainder_text")),
            ("condition text verbatim", ("condition_text_verbatim",
                                         "condition_text", "condition")),
            ("supersession pointer", ("supersession_pointer",
                                      "supersession_pointers",
                                      "pointer")),
            ("internal undecided note", ("internal_undecided_note",
                                         "undecided_note")),
        ), "Entry")

    def test_status_bearing_element_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Status bearing element"],
                            "Status bearing element")
        assert_groups(self, cls, (
            ("kind", ("kind", "element_kind")),
            ("position line", ("position_line", "line")),
            ("span", ("span", "line_span")),
            ("verbatim value text", ("verbatim_value_text", "verbatim",
                                     "verbatim_value")),
            ("disposition", ("disposition",)),
            ("scope", ("scope",)),
            ("condition", ("condition",)),
            ("determining flag", ("determining_flag", "determining",
                                  "is_determining")),
            ("underlying state without condition",
             ("underlying_state_without_condition", "underlying_state")),
        ), "Status bearing element")

    def test_finding_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Finding"], "Finding")
        assert_groups(self, cls, (
            ("rule identifier", ("rule_identifier", "rule_id", "rule")),
            ("severity", ("severity",)),
            ("entry identifier or file level marker",
             ("entry_identifier", "entry_id", "file_level_marker",
              "identifier")),
            ("line span", ("line_span", "span")),
            ("verbatim evidence", ("verbatim_evidence", "evidence")),
            ("determining element named", ("determining_element",
                                           "determining_element_named")),
            ("claiming unit or claiming entry",
             ("claiming_unit", "claiming_entry",
              "claiming_unit_or_entry", "claiming")),
            ("named entries", ("named_entries",)),
        ), "Finding")

    def test_census_row_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Census row"],
                            "Census row")
        assert_groups(self, cls, (
            ("class identifier", ("class_identifier", "class_name",
                                  "class_id", "identifier")),
            ("class rule statement", ("class_rule_statement",
                                      "class_rule", "rule_statement")),
            ("count", ("count",)),
            ("member entry identifiers", ("member_entry_identifiers",
                                          "member_entry_ids", "members")),
            ("counting unit", ("counting_unit", "unit")),
            ("head line count", ("head_line_count",)),
            ("variance", ("variance",)),
        ), "Census row")

    def test_verbatim_appendix_row_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Verbatim appendix row"],
                            "Verbatim appendix row")
        assert_groups(self, cls, (
            ("phrasing as written", ("phrasing_as_written", "phrasing")),
            ("kind", ("kind",)),
            ("occurrence count", ("occurrence_count",)),
            ("entry identifiers carrying the phrasing",
             ("entry_identifiers", "member_entry_ids", "entry_ids")),
        ), "Verbatim appendix row")

    def test_residue_item_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Residue item"],
                            "Residue item")
        assert_groups(self, cls, (
            ("phrasing as written", ("phrasing_as_written", "phrasing")),
            ("entry identifier", ("entry_identifier", "entry_id")),
            ("line span", ("line_span", "span")),
        ), "Residue item")

    def test_render_model_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Render model"],
                            "Render model")
        assert_groups(self, cls, (
            ("file facts", ("file_facts",)),
            ("canonical counts by state", ("canonical_counts",
                                           "canonical_counts_by_state")),
            ("verbatim appendix rows", ("verbatim_appendix_rows",
                                        "appendix_rows")),
            ("census rows", ("census_rows", "census")),
            ("findings", ("findings",)),
            ("entry groups", ("entry_groups", "entries")),
            ("crosswalk counts", ("crosswalk_counts", "crosswalk")),
            ("residue items", ("residue_items", "residue")),
            ("residue share computation", ("residue_share_computation",
                                           "residue_share")),
            ("waiting figure", ("waiting_figure", "waiting")),
            ("blocking figure", ("blocking_figure", "blocking")),
            ("reconciliation", ("reconciliation_components",
                                "reconciliation")),
            ("exit decision", ("exit_decision",)),
            ("supersession chains", ("supersession_chains", "chains")),
        ), "Render model")

    def test_exit_decision_shape_fields(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Exit decision"],
                            "Exit decision")
        assert_groups(self, cls, (
            ("exit code", ("exit_code", "code")),
            ("reason classes present", ("reason_classes",
                                        "reason_class_list", "reasons")),
            ("masked findings summary", ("masked_findings_summary",
                                         "masked_summary",
                                         "masked_findings")),
        ), "Exit decision")

    def test_corpus_manifest_entry_shape_in_pin_down_1_order(self):
        cls = find_shape(("CorpusManifestEntry", "ManifestEntry",
                          "CorpusEntry"))
        expected = ("fixture", "kind", "source", "hash", "bytes",
                    "lines", "expectedcounts", "expectedfindings",
                    "expectedexit")
        if cls is not None:
            names = [_norm(name) for name in field_names(cls)]
            positions = []
            for label in expected:
                match = [i for i, name in enumerate(names)
                         if label in name]
                self.assertTrue(
                    match, "manifest entry shape carries no field for "
                    + label)
                positions.append(match[0])
            self.assertEqual(positions, sorted(positions),
                             "manifest entry fields stand out of the "
                             "testing pin down 1 order")
            return
        self.fail("no corpus manifest entry shape stands; Slice 1 "
                  "relies on the manifest form at testing pin down 1 "
                  "for this shape, in the field order Fixture, Kind, "
                  "Source, Hash, Bytes, Lines, Expected counts, "
                  "Expected findings, Expected exit")

    def test_acceptance_run_record_shape_fields(self):
        cls = require_shape(
            self, ("AcceptanceRunRecord", "AcceptanceRecord"),
            "Acceptance run record")
        assert_groups(self, cls, (
            ("input name as given", ("input_name_as_given", "input_name")),
            ("line count", ("line_count",)),
            ("byte count", ("byte_count",)),
            ("full digest", ("full_digest", "digest")),
            ("vocabulary version", ("vocabulary_version",)),
            ("output form edition", ("output_form_edition",)),
            ("rule set version", ("rule_set_version",)),
            ("method check record", ("method_check_record",
                                     "method_check")),
            ("footing check results", ("footing_check_results",
                                       "footing_results", "footing")),
            ("unproved ground field", ("unproved_ground",
                                       "unproved_ground_field")),
        ), "Acceptance run record")

    def test_live_proof_record_shape_fields(self):
        cls = require_shape(self, ("LiveProofRecord", "ProofRecord"),
                            "Live proof record")
        assert_groups(self, cls, (
            ("source commit", ("source_commit",)),
            ("new public head", ("new_public_head", "public_head")),
            ("installed copy equality check", ("equality_check",
                                               "installed_copy_check")),
            ("installed position", ("installed_position",)),
            ("label state", ("label_state", "r24_label_state")),
            ("subcommand results", ("subcommand_results",
                                    "subcommand_runs")),
            ("file facts", ("file_facts",)),
            ("version fields", ("version_fields", "versions")),
            ("live path statement", ("live_path_statement",
                                     "statement_live_path")),
            ("fresh measurement record", ("fresh_measurement_record",
                                          "fresh_measurement")),
            ("target verification record", ("target_verification_record",
                                            "target_verification")),
        ), "Live proof record")

    def test_shared_head_shape_positions(self):
        cls = require_shape(self, ("SharedHead", "SharedHeadLayout",
                                   "HeadLayout"), "Shared head")
        assert_groups(self, cls, (
            ("scope statement", ("scope_statement", "scope")),
            ("input name line", ("input_name_line", "input_line")),
            ("file facts line", ("file_facts_line", "file_facts")),
            ("limits line", ("limits_line", "limits")),
            ("version fields line", ("version_fields_line",
                                     "versions_line", "versions")),
            ("residue share line position", ("residue_share_line",
                                             "share_line", "residue_line")),
        ), "Shared head")


class SeparationTest(unittest.TestCase):

    def test_claim_finding_keeps_three_fields_apart(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Finding"], "Finding")
        entry_field = resolve_field(
            cls, ("entry_identifier", "entry_id", "identifier"))
        claiming_field = resolve_field(
            cls, ("claiming_unit", "claiming_entry",
                  "claiming_unit_or_entry", "claiming"))
        named_field = resolve_field(cls, ("named_entries",))
        self.assertIsNotNone(entry_field)
        self.assertIsNotNone(
            claiming_field,
            "a claim finding carries no claiming unit field of its own")
        self.assertIsNotNone(named_field)
        self.assertEqual(
            len({entry_field, claiming_field, named_field}), 3,
            "claiming unit, named entries, and the identifier field "
            "are not three separate carriers")
        value = build_value(cls, {
            (entry_field,): "DQ-900",
            (claiming_field,): "file level unit, kind note section, "
                               "beginning at line 40",
            (named_field,): ["DQ-001", "DQ-002"],
        })
        self.assertEqual(h.text_of(getattr(value, entry_field)), "DQ-900")
        self.assertIn("note section",
                      h.text_of(getattr(value, claiming_field)) or "")
        self.assertEqual(
            [h.text_of(item) for item in
             h.as_list(getattr(value, named_field))],
            ["DQ-001", "DQ-002"])

    def test_entry_outcome_three_separate_carriers(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Entry"], "Entry")
        state_field = resolve_field(
            cls, ("derived_effective_state", "effective_state",
                  "canonical_state", "derived_state", "state"))
        report_field = resolve_field(
            cls, ("reporting_form", "ambiguous_reporting_form",
                  "ambiguous_report", "report_form"))
        marker_field = resolve_field(
            cls, ("unparsed_marker", "unparsed", "unparsed_flag",
                  "marker"))
        self.assertIsNotNone(state_field, "no canonical state carrier")
        self.assertIsNotNone(
            report_field,
            "the Ambiguous reporting form has no carrier of its own; "
            "it must not be stored inside the canonical state field")
        self.assertIsNotNone(marker_field, "no unparsed marker carrier")
        self.assertEqual(len({state_field, report_field, marker_field}),
                         3, "the three outcome carriers are merged")

    def test_census_head_line_view_is_a_counting_view_only(self):
        cls = require_shape(self, SHAPE_CANDIDATES["Census row"],
                            "Census row")
        fields = field_names(cls)
        lowered = [name.lower() for name in fields]
        self.assertFalse(
            any("effective" in name or "derived_state" in name
                for name in lowered),
            "the census row carries a derivation read state field; "
            "the head line view is a counting view only")
        count_field = resolve_field(cls, ("count",))
        head_field = resolve_field(cls, ("head_line_count",))
        self.assertIsNotNone(count_field)
        self.assertIsNotNone(head_field)
        self.assertNotEqual(count_field, head_field)
        value = build_value(cls, {(count_field,): 5, (head_field,): 3})
        self.assertEqual(h.int_of(getattr(value, count_field)), 5)
        self.assertEqual(h.int_of(getattr(value, head_field)), 3)

    def test_no_shape_carries_a_count_without_a_stated_unit(self):
        unit_words = ("entries", "lines", "bytes", "occurrences",
                      "findings", "items", "chains", "headed", "units",
                      "spans", "head")
        for label, names in SHAPE_CANDIDATES.items():
            cls = find_shape(names)
            if cls is None:
                continue
            fields = field_names(cls)
            has_unit_field = any("unit" in name.lower()
                                 for name in fields)
            annotations = {}
            if dataclasses.is_dataclass(cls):
                annotations = {item.name: str(item.type)
                               for item in dataclasses.fields(cls)}
            for name in fields:
                if "count" not in name.lower():
                    continue
                with self.subTest(shape=label, field=name):
                    carried = (
                        any(word in name.lower() for word in unit_words)
                        or has_unit_field
                        or "count" in annotations.get(name, "").lower()
                        and any(word in annotations.get(name, "").lower()
                                for word in ("entry", "line", "byte",
                                             "occurrence", "finding")))
                    self.assertTrue(
                        carried,
                        label + " field " + name + " carries a count "
                        "whose unit neither the field nor the row states")


class EqualityTest(unittest.TestCase):

    def test_each_shape_builds_and_compares_for_equality(self):
        labels = ("File", "File level unit", "Entry",
                  "Status bearing element", "Finding", "Census row",
                  "Verbatim appendix row", "Residue item",
                  "Render model", "Exit decision")
        for label in labels:
            cls = find_shape(SHAPE_CANDIDATES[label])
            with self.subTest(shape=label):
                self.assertIsNotNone(cls, "shape not found: " + label)
                first = build_value(cls)
                second = build_value(cls)
                self.assertEqual(first, second,
                                 label + " values built alike do not "
                                 "compare equal")
                changed = None
                for name in field_names(cls):
                    probe = build_value(cls)
                    try:
                        current = getattr(probe, name)
                    except Exception:
                        continue
                    if isinstance(current, str):
                        setattr(probe, name, current + " changed")
                        changed = probe
                        break
                    if isinstance(current, int) and \
                            not isinstance(current, bool):
                        setattr(probe, name, current + 1)
                        changed = probe
                        break
                if changed is not None:
                    self.assertNotEqual(
                        first, changed,
                        label + " compares equal after a field change")

    def test_file_shape_holds_entries_in_the_order_given(self):
        cls = require_shape(self, SHAPE_CANDIDATES["File"], "File")
        entries_field = resolve_field(cls, ("entries",))
        self.assertIsNotNone(entries_field)
        sentinels = ["entry-b", "entry-a", "entry-c"]
        value = build_value(cls, {(entries_field,): list(sentinels)})
        held = [h.text_of(item) for item in
                h.as_list(getattr(value, entries_field))]
        self.assertEqual(held, sentinels,
                         "file order is a property of the list, not a "
                         "sort applied later")


if __name__ == "__main__":
    unittest.main()
