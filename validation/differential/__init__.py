"""Differential validation harness (WP-16). The implementation lives in ``core``; this
package re-exports it so ``from validation import differential as D`` gives the whole API,
and later work packages can add ``fission.py`` / ``medical.py`` beside it (plan WP-24/25).
"""

from validation.differential.core import *  # noqa: F401,F403
from validation.differential.core import (  # noqa: F401  (explicit for type checkers / greps)
    EXFOR_KINDS,
    LIBRARIES,
    MASS_REGIONS,
    REGIONS,
    ExforPoints,
    HarnessResult,
    Library,
    Prediction,
    PredictionSet,
    add_holdout_flags,
    aggregate_library_rows,
    bin_prediction,
    chi2_with_covariance,
    compare_to_exfor,
    compare_to_kadonis,
    compare_to_library,
    load_exfor_points,
    load_kadonis,
    macs_table,
    mass_region,
    maxwellian_average,
    nuclide_id,
    parse_nuclide_id,
    point_metrics,
    region_holdouts,
    rrr_bounds,
    run_harness,
    summarize_exfor,
    summarize_macs,
)
