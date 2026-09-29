"""Open, library-free EXFOR curation register (rule v2: docs/release/CURATION_RULE_v2.md).

    python -m incognita.curation.build       # regenerate the register from EXFOR + the rule
    python -m incognita.curation.validate    # agreement with the v1 register, flips, audit sample

Evidence is EXFOR, the EXFOR-derived series table, IAEA standards, RIPL/NUBASE and physics bounds
only. No evaluated-library value is read anywhere in this package.
"""
