"""MACSPEED: whole nuclides in a long-lived worker, the way a chart sweep runs them.

Nothing here is a TALYS routine and no number changes: it is `engine.ChainedFull` + `engine.run`
(talysreaction.f90:1, talysreaction) called the cheap way.

* `run_nuclide` runs one target under `torch.inference_mode()`. The dump-free default path never
  asks for a gradient, and inference mode drops autograd's per-op bookkeeping (version counters,
  view tracking): 8 % of a spherical nuclide's CPU on the Mac M2, bit-identical on every channel.
  Anything that differentiates (DIFFPARAM, `capture_fast(..., differentiable=True)`) must keep
  calling `engine.run` directly.
* `drop_target_caches` is what a worker does between targets. Every `lru_cache` in `physics.hf`
  that is keyed by a target or holds a target's tensors is dropped, so RSS stays flat over 482
  nuclides and no target sees another's state. The caches in `KEEP` are pure functions of their
  arguments with no target in them (parsed data files, format plans, spin masks, 6j/CG tables);
  those survive, so the next target does not parse `levels/final/Ge.lev` or the mass tables again.

TALYS: talysreaction.f90:1 (talysreaction)
Test: scripts/hf_macspeed_chart.py close (whole chart, per cell against the plain call)
"""

from __future__ import annotations

import functools
import gc
import sys

# `lru_cache`d functions (by `__wrapped__.__name__`, module-qualified) whose results depend on
# nothing but their own arguments and are not tied to one target.
KEEP: frozenset[str] = frozenset({
    "physics.hf.structure.files._parse_format",
    "physics.hf.core.grids._egrid_values",
    "physics.hf.structure.files._read_plan",
    "physics.hf.structure.files._lines",
    "physics.hf.structure.files._lazy_lines",
    "physics.hf.structure.files._level_headers",  # NATIVEX2: a level file's block index
    "physics.hf.structure.files._d0global_table",
    "physics.hf.structure.levels._level_block",
    "physics.hf.structure.levels._levels_of_values",
    "physics.hf.structure.masses._mass_table",
    "physics.hf.structure.masses._duflo_grid",
    "physics.hf.structure.masses._mass10",
    "physics.hf.structure.masses._shell",
    "physics.hf.density.parameters._ld_file_rows",
    "physics.hf.density.tables._file_lines",
    "physics.hf.omp.parameters._kd03_file",
    "physics.hf.omp.parameters._local_omp_file",
    "physics.hf.omp.schrodinger._ame2020_table",
    "physics.hf.omp.ripl._library_lines",
    "physics.hf.omp.ripl.read_om_index",
    "physics.hf.omp.ripl._gs_mass_sp",
    "physics.hf.gamma.parameters._read_gdr",
    "physics.hf.gamma.parameters._psf_lines",
    "physics.hf.gamma.parameters._read_psf_table",
    "physics.hf.compound.target_batch._exit_mask",
    "physics.hf.compound.decay_fast._mask",
    "physics.hf.compound.decay_fast._mask_c",
    "physics.hf.compound.decay_fast._mask_d",
    "physics.hf.compound.continuum._spin_l_mask",
    "physics.hf.compound.decay_native.spin_l_bounds",
    "physics.hf.compound.decay_native._lib",
    "physics.hf.native.speedw.lib",
    "physics.hf.emission.channels._channel_keys",
    "physics.hf.density.particle_hole._nfac_tensor",
    "physics.hf.density.particle_hole._signed_ncomb_table",
    "physics.hf.ecis.dwba_setb.cg_weights",  # SETB: DWBA Clebsch-Gordan weights by (lambda, lmax)
    "physics.hf.ecis.dwba_setb._cg_table",  # CENGSETUP: the table they are sliced from
    "physics.hf.omp.ripl.read_om_parameter",  # CENGSETUP: one om-parameter-u.dat entry by iref
    # SPEED50C: a RIPL potential's full table on (Z, A): files only (omp_table hands out copies).
    # With CCGPU the plan pass builds it and the target's run needed it again after the drop
    "physics.hf.omp.ripl._full_table",
    "physics.hf.core.constants._talys_constants_memo",  # SETB: constants.f90's values
    "physics.hf.native.nativex.lib",  # NATIVEX: the loaded kernels
    "physics.hf.engine_c.lib",  # CENGWIRE: the loaded cascade engine, with its kernel pointers
    "physics.hf.native.nx2.lib",  # NATIVEX2: the loaded kernels
    "physics.hf.native.nx2._bound",  # NATIVEX2: their signatures
    "physics.hf.ecis.vibm._cg0",  # NATIVEX2: vibm's Clebsch-Gordan and 6j by integer arguments
    "physics.hf.ecis.vibm._sixj",
    "physics.hf.ecis.vibm._reduced_matrix_elements",  # NATIVEX2: a band's vibm table by value
    "physics.hf.density.parameters._ld_parameter_file",  # NATIVEX2 ld: one LD table row by value
    "physics.hf.structure.deformation._irigid0",  # NATIVEX2 ld: Irigid0 of A
    "physics.hf.density.tables._table_blocks",  # NATIVEX2 ld2: a table file's records by mass
    "physics.hf.omp.parameters._kd03_values",  # NATIVEX2 omp: the KD03 file parsed once
    "physics.hf.emission.channels._limits_of",  # NATIVEX: channels.f90's loop limits
})

# plain-dict memos keyed by band spins or by energy rather than by target (CCFAST2's list)
_DICT_MEMOS = (("physics.hf.ecis.solver", ("_CHANNELS", "_NJ_SEEN")),
               ("physics.hf.ecis.incident", ("_SOLVED", "_PARAMS_CACHE")),
               ("physics.hf.compound.psf_nx2", ("_PACKS",)),  # NATIVEX2: packed by object id
               ("physics.hf.direct.dwba", ("_GR_LAST",)),  # NATIVEX2 dwba: one-entry memos
               ("physics.hf.ecis.dwba", ("_CORE_LAST",)),
               ("physics.hf.omp.omp_nx2", ("_FACTORS",)))  # NATIVEX2 omp: by Params identity


def run_nuclide(Z: int, A: int, declared_energies: tuple[float, ...]):
    """`engine_c.run(injection=ChainedFull(Z, A, declared_energies))` in inference mode.

    CENGWIRE: the entry point takes `engine_c.run`, not `engine.run`. `engine_c.run` **is**
    `engine.run` for the dump-free chain, statement for statement, with CENGDECAY's `ce_cascade`
    in place of the Python multiple-emission walk, and it picks itself: with no build (or
    `HF_ENGINE_C=0`, `HF_NATIVEX=0`, `HF_NATIVE=0`) `lib()` is None and it calls `engine.run`
    itself, and per incident energy it falls back to `ChainedFull.cases` for anything the C call
    does not take (`_Unsupported`). So this is a dispatch change only -- every number is the one
    `engine.run` gave (tests/hf/test_engine_c.py holds every array of the two paths together).

    `inventory.report` warns once per process about kernels that did not load, so a box with no
    build says so instead of silently costing about twice as much over 482 nuclides. Anything that
    differentiates (DIFFPARAM, `capture_fast(..., differentiable=True)`) must still call
    `engine.run` directly -- inference mode, not the C path, is what rules that out here.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: tests/hf/test_cengwire.py, scripts/hf_macspeed_chart.py close
    """
    import torch

    from physics.hf.engine import ChainedFull
    from physics.hf.engine_c import run as engine_run
    from physics.hf.native.inventory import report

    report()
    with torch.inference_mode():
        return engine_run(injection=ChainedFull(Z=Z, A=A, declared_energies=declared_energies))


def drop_target_caches(keep: frozenset[str] = KEEP) -> None:
    """Drop every per-target cache of `physics.hf`, keeping the pure ones in `keep`.

    TALYS: none (worker hygiene)
    Test: scripts/hf_macspeed_chart.py close
    """
    for name, mod in list(sys.modules.items()):
        if not name.startswith("physics.hf"):
            continue
        for obj in list(vars(mod).values()):
            if not isinstance(obj, functools._lru_cache_wrapper):
                continue
            fn = obj.__wrapped__
            if f"{getattr(fn, '__module__', '')}.{getattr(fn, '__name__', '')}" in keep:
                continue
            try:
                obj.cache_clear()
            except Exception:
                pass
    for modname, names in _DICT_MEMOS:
        mod = sys.modules.get(modname)
        for n in names:
            memo = getattr(mod, n, None)
            if memo is not None:
                memo.clear()
    gc.collect()
