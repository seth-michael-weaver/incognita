"""Register schema and reason codes of curation rule v2 (docs/release/CURATION_RULE_v2.md)."""
from __future__ import annotations

RULE_VERSION = "v2"
RULE_DOC = "docs/release/CURATION_RULE_v2.md"

# rule code -> (reason code, family, grade). grade: exclude | downweight | renorm | info | corroborating
RULES: dict[str, tuple[str, str, str]] = {
    "R1": ("R1_RECORD_PROVEN_ERROR", "record", "exclude"),
    "R2x": ("R2X_NOT_THE_SCORED_QUANTITY", "record", "exclude"),
    "R2d": ("R2D_PARTIAL_STATE_AS_TOTAL", "record", "downweight"),
    "R3": ("R3_TWIN_SUPERSEDED", "identity", "exclude"),
    "R3d": ("R3D_DUPLICATE_REFERENCE_DROPPED", "identity", "info"),
    "R4": ("R4_RENORMALISED_TO_STANDARD", "record", "renorm"),
    "R5x": ("R5X_INTER_DATASET_SCATTER", "data", "exclude"),
    "R5d": ("R5D_INTER_DATASET_SCATTER", "data", "downweight"),
    "R6x": ("R6X_SERIES_SYSTEMATIC", "data", "exclude"),
    "R6d": ("R6D_SERIES_SYSTEMATIC", "data", "downweight"),
    "R7": ("R7_PHYSICS_BOUND", "physics", "exclude"),
    "R8": ("R8_UNCORRECTED_LOW_ENERGY_BACKGROUND", "record", "downweight"),
    "R9": ("R9_CROSS_NUCLIDE_14MEV_SYSTEMATIC", "data", "downweight"),
    "R10x": ("R10X_ISOTOPIC_SYSTEMATIC", "data", "exclude"),
    "R10d": ("R10D_ISOTOPIC_SYSTEMATIC", "data", "downweight"),
    "R11x": ("R11X_MACS_CONTRADICTS_SERIES", "data", "exclude"),
    "R11d": ("R11D_MACS_CONTRADICTS_SERIES", "data", "downweight"),
    "R12": ("R12_RECORD_QUALITY", "record", "corroborating"),
}
LADDER2 = "L2_DATA_PLUS_RECORD"          # ladder step 2: data downweight + record finding -> exclude
DOWNWEIGHT_FACTOR = 0.25                  # trust x0.25 (sigma x4), the register's only trust reduction

EXCLUDE_RULES = {k for k, v in RULES.items() if v[2] == "exclude"}
DATA_DOWN = {"R5d", "R6d", "R9", "R10d", "R11d"}
RECORD_DOWN = {"R2d", "R8", "R12"}
# precedence of the rule that is reported as the primary reason (first match wins)
PRIMARY_ORDER = ["R3", "R1", "R2x", "R7", "R11x", "R5x", "R6x", "R10x", "R2d", "R8", "R11d", "R5d", "R6d",
                 "R10d", "R9", "R12", "R4"]

# JSON schema of one register record (curation_register_v2.jsonl)
RECORD_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Library-free EXFOR curation register, one decision",
    "type": "object",
    "required": ["id", "rule_version", "dataset_key", "entry", "subentry", "pointer", "nuclide", "kind",
                 "decision", "scope", "reason_code", "rules_fired", "cells", "summary"],
    "properties": {
        "id": {"type": "string", "description": "stable id: CR2-<entry><subentry-suffix>-<pointer>-<scope hash>"},
        "rule_version": {"const": RULE_VERSION},
        "dataset_key": {"type": "string", "description": "EXFOR entry/subentry/pointer"},
        "entry": {"type": "string"}, "subentry": {"type": "string"}, "pointer": {"type": "string"},
        "nuclide": {"type": "string", "description": "target, Z###N###M0 (ground-state target)"},
        "z": {"type": ["integer", "null"]}, "a": {"type": ["integer", "null"]},
        "kind": {"type": "string", "description": "EXFOR quantity class of the dataset (sig, av, mxw, ...)"},
        "first_author": {"type": ["string", "null"]}, "year": {"type": ["integer", "null"]},
        "decision": {"enum": ["exclude", "downweight", "renorm"]},
        "factor": {"type": ["number", "null"], "description": "downweight: trust multiplier 0.25; renorm: value multiplier"},
        "scope": {"enum": ["dataset", "cells"],
                  "description": "dataset: every cell of the dataset; cells: only the listed 0.1-dex energy cells"},
        "reason_code": {"enum": sorted({v[0] for v in RULES.values()} | {LADDER2})},
        "rules_fired": {"type": "array", "items": {"enum": sorted(RULES)}},
        "cells": {"type": "array", "description": "cells covered, each with its own rules and evidence numbers",
                  "items": {"type": "object", "required": ["bin", "e_lo_ev", "e_hi_ev", "mean_b", "rules"]}},
        "evidence": {"type": "object", "description": "dataset-level evidence: twin partner, MACS groups, "
                     "record findings with verbatim EXFOR quotes, flags"},
        "standard": {"type": ["object", "null"], "description": "R4: the standard, documented and reference values"},
        "flags": {"type": "object", "description": "EXFOR flags used: sf9, STATUS codes, no_uncertainty"},
        "v1": {"type": "object", "description": "link to the v1 register lines on the same dataset (validation only)"},
        "summary": {"type": "string", "description": "one-line human-readable reason generated from the codes"},
    },
}
