"""Every default a neutron-induced TALYS run reads, ported from the Defaults sections of
input_*.f90 (not the keyword parser). `Options` holds model switches and numerical settings
(ints/bools/non-adjustable floats); `Params` holds the adjustable continuous parameters as
tensors named after their TALYS keywords (contract §4.4).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T3 (physics/hf/CONTRACT.md §7). Acceptance test: A-omppar (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    input_main.f90:1 (input_main)
    input_basicreac.f90:1 (input_basicreac)
    input_basicpar.f90:1 (input_basicpar)
    input_best.f90:1 (input_best)
    input_astro.f90:1 (input_astro)
    input_numerics.f90:1 (input_numerics)
    input_mass.f90:1 (input_mass)
    input_levels.f90:1 (input_levels)
    input_densitymodel.f90:1 (input_densitymodel)
    input_densitypar.f90:1 (input_densitypar)
    input_gammamodel.f90:1 (input_gammamodel)
    input_gammapar.f90:1 (input_gammapar)
    input_ompmodel.f90:1 (input_ompmodel)
    input_omppar.f90:1 (input_omppar)
    input_compoundmodel.f90:1 (input_compoundmodel)
    input_compoundpar.f90:1 (input_compoundpar)
    input_directmodel.f90:1 (input_directmodel)
    input_directpar.f90:1 (input_directpar)
    input_fissionmodel.f90:1 (input_fissionmodel)
    input_fissionpar.f90:1 (input_fissionpar)
    input_preeqmodel.f90:1 (input_preeqmodel)
    input_preeqpar.f90:1 (input_preeqpar)
    input_medical.f90:1 (input_medical)
    input_fit.f90:1 (input_fit)
    nuclides.f90:1 (nuclides)      maxZ/maxN caps and the structure-dependent onsets
    energies.f90:1 (energies)      per-incident-energy switches derived from those onsets
    grid.f90:1 (grid)              resolution of eninclow

How to read this module
-----------------------
* **Order.** TALYS resolves defaults module by module in the order of talysinput.f90, and later
  defaults read earlier ones (`strengthM1` reads `strength`, `wtable` reads `ldmodel` and
  `flagcol`, `flagspher` reads `flagjlm`, which reads `flagmicro`). `default_options` replays
  that order, applying each explicit keyword at the point TALYS reads it, so a cascade comes out
  as TALYS computes it.
* **Absent is not the same as explicit.** A keyword left out takes the default *resolved for
  this target*; the same value written explicitly can differ. The known case: `ldmodel` resolves
  to 7 for a neutron on A > 215 (input_densitymodel.f90:90), so `ldmodel 1` on U-238 -- "the
  documented default" -- switches the level density model and collapses (n,f) 17x
  (docs/results/wp24-fission-ldmodel-trap.md). `Options.explicit` records which keywords were
  set, and `default_options` accepts only the keyword values, never "defaults" to pin.
* **Sentinels.** Many TALYS defaults are placeholders that later physics routines replace:
  `alev = 0` (level density parameter, from systematics), `D0 = 0`, `ewfc = -1` (the neutron
  separation energy), `epreeq = -1` (the last discrete level), `vfiscor = -1`. They are ported
  verbatim so a component that owns the resolution can test "sentinel in, value out".
  `PARAM_SPECS[k].resolved_by` names the owning routine and task. `resolve_structure_defaults`
  does the few that are pure bookkeeping on structure numbers.
* **Indices.** Parameter tensors keep the Fortran index. Arrays declared 1-based carry an unused
  slot 0; arrays declared from -1 are shifted by +1 (`ParamSpec.offsets`). Nucleus arrays are
  indexed `[Zix, Nix]` counted from the initial compound nucleus, as in TALYS (contract §4.2).
* **Out of scope.** Output switches (`out*`, `file*`, `block*`), ENDF-6 writing, medical yields,
  fitted-parameter libraries (`best`, `*fit` with `fit y`), and per-nucleus keyword *forms*
  (`ldmodel 92 238 1`) -- pass a full tensor through `default_params(overrides=...)` instead.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field, fields, replace
from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

from physics.hf.omp import regional  # OSENGINE: the one non-TALYS default (imports nothing back)

# ---------------------------------------------------------------------------------------------
# TALYS dimensions and constants (A0_talys_mod.f90 parameters; constants.f90)
# ---------------------------------------------------------------------------------------------

MEMORYPAR = 6  # A0_talys_mod.f90:23
NUMPAR = 6  # A0_talys_mod.f90:24 -- particle types 0..6 = g n p d t h a
NUMZ = 2 + 2 * MEMORYPAR  # A0_talys_mod.f90:32 -- 14
NUMN = 10 + 4 * MEMORYPAR  # A0_talys_mod.f90:33 -- 34
NUMBAR = 3  # A0_talys_mod.f90:36
NUMGAM = 6  # A0_talys_mod.f90:39
NUMRANGE = 10  # A0_talys_mod.f90:40
NUMLEV = 40  # A0_talys_mod.f90:43
NUMISOM = 10  # A0_talys_mod.f90:44
NUMOMPADJ = 13  # A0_talys_mod.f90:53
NUMANG = 90  # A0_talys_mod.f90:60
NUMJ = 40  # A0_talys_mod.f90:68
NUMENREC = 4 * (MEMORYPAR - 1)  # A0_talys_mod.f90:69 -- 20
NUMANGREC = 9  # A0_talys_mod.f90:70
NUMT = 30  # A0_talys_mod.f90:81
FISLIM = 215  # constants.f90:178 -- mass above which fission and the actinide defaults apply
EMAXTALYS_MEV = 1000.0  # constants.f90:182

PARSYM = ("g", "n", "p", "d", "t", "h", "a")  # constants.f90:89 (types 0..6)
PARZ = (0, 0, 1, 1, 1, 2, 2)  # constants.f90:90
PARN = (0, 1, 0, 1, 2, 1, 2)  # constants.f90:91

DTYPE = torch.float64


# ---------------------------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Options:
    """Resolved TALYS switches for one target and projectile.

    Field names are the Fortran variable names; the comment on each gives the file:line where
    TALYS sets the default. Units are in the name where a field has one (`_mev`). Energy onsets
    that TALYS derives from structure (`ewfc`, `eurr`, `epreeq`) keep their -1 sentinel until
    :func:`resolve_structure_defaults` fills them.
    """

    # --- target and projectile (input_main.f90) ---
    Ztarget: int
    Atarget: int
    k0: int  # particle type of the projectile, input_main.f90:214-219
    Ltarget: int = 0  # input_main.f90:72
    Estop_mev: float = EMAXTALYS_MEV  # input_main.f90:74
    flagastro: bool = False  # input_main.f90:79
    # --- basic reaction switches (input_basicreac.f90) ---
    flagendf: bool = False  # :69
    flagendfdet: bool = True  # :70-74, true for k0 <= 1
    flagendfecis: bool = True  # :75
    flagchannels: bool = False  # :76
    flaglabddx: bool = False  # :77
    flagpopMeV: bool = False  # :78
    flagmassdis: bool = False  # :79
    flagmicro: bool = False  # :80
    flagreaction: bool = True  # :82
    flagrecoil: bool = False  # :83
    flagrecoilav: bool = False  # :84
    flagrel: bool = True  # :85
    flagrpevap: bool = False  # :86
    flaglegacy: bool = False  # :87
    flagEchannel: bool = False  # :68
    # --- basic parameters (input_basicpar.f90) ---
    eninclow_mev: float = 1.0e-6  # :54-58; 0 (resolved in grid.f90) for k0 == 1 with endf y
    flagequi: bool = True  # :59
    flagequispec: bool = False  # :60
    isomer_s: float = 1.0  # :61, half-life above which a level counts as an isomer
    Lisoinp: int = -1  # :62
    flagfit: bool = False  # :66
    # --- best / fit / astro / medical ---
    flagbest: bool = False  # input_best.f90:57
    flagbestend: bool = False  # input_best.f90:58
    flagngfit: bool = False  # input_fit.f90:53
    flagnnfit: bool = False  # input_fit.f90:54
    flagnffit: bool = False  # input_fit.f90:55
    flagnafit: bool = False  # input_fit.f90:56
    flagndfit: bool = False  # input_fit.f90:57
    flagpnfit: bool = False  # input_fit.f90:58
    flaggnfit: bool = False  # input_fit.f90:59
    flagdnfit: bool = False  # input_fit.f90:60
    flaganfit: bool = False  # input_fit.f90:61
    flagmacsfit: bool = False  # input_fit.f90:62
    flaggamgamfit: bool = False  # input_fit.f90:63
    flagastroex: bool = False  # input_astro.f90:49
    flagastrogs: bool = False  # input_astro.f90:50
    nonthermlev: int = -1  # input_astro.f90:51
    flagprod: bool = False  # input_medical.f90:52
    # --- numerics (input_numerics.f90) ---
    maxenrec: int = NUMENREC  # :64
    maxN: int = NUMN - 2  # :65, then capped at Ninit - 3 (nuclides.f90:141)
    maxNrp: int = NUMN - 2  # :66
    maxZ: int = NUMZ - 2  # :67, then capped at Zinit - 3 (nuclides.f90:140)
    maxZrp: int = NUMZ - 2  # :68
    nbins0: int = 40  # :69
    segment: int = 1  # :70
    nangle: int = NUMANG  # :71
    nanglecont: int = 18  # :72
    maxchannel: int = 4  # :73
    nanglerec: int = 1  # :74-78, numangrec with labddx y
    transpower: int = 5  # :79; 10 with massdis y (:84), 15 with astro y (:90)
    transeps: float = 1.0e-8  # :80; 1e-12 / 1e-18
    xseps_mb: float = 1.0e-7  # :81; 1e-12 / 1e-17
    popeps_mb: float = 1.0e-3  # :82; 1e-10 / 1e-13
    # --- masses (input_mass.f90) ---
    flagexpmass: bool = True  # :70
    massmodel: int = 2  # :73
    # --- discrete levels (input_levels.f90) ---
    flagpseudores: bool = False  # :93
    flagelectron: bool = True  # :97
    disctable: int = 1  # :101
    flagbestbr: bool = False  # :102
    nlevmax: int = 30  # :106, max(30, Ltarget)
    nlevmaxres: int = 30  # :108
    nlevbin: tuple[int, ...] = (30,) * 7  # :107 and :109 (nlevbin(k0) = nlevmax), types 0..6
    # --- level density models (input_densitymodel.f90, input_densitypar.f90) ---
    ldmodelall: int = 1  # input_densitymodel.f90:84-90; 7 for micro y or k0 <= 1 with A > 215
    ldmodelCN: int = 1  # input_densitymodel.f90:91 and :245-249
    strength: int = 9  # input_densitymodel.f90:89
    shellmodel: int = 1  # input_densitymodel.f90:92
    spincutmodel: int = 1  # input_densitymodel.f90:93
    kvibmodel: int = 2  # input_densitymodel.f90:94
    flagcolall: bool = False  # input_densitymodel.f90:95-99, true for A > 215
    flagcolldamp: bool = False  # input_densitymodel.f90:101
    flagldglobal: bool = False  # input_densitymodel.f90:104
    flagasys: bool = False  # input_densitymodel.f90:105
    flagctmglob: bool = False  # input_densitymodel.f90:106
    flagparity: bool = False  # input_densitypar.f90:176-180, true for ldmodelall >= 5
    flaggshell: bool = False  # input_preeqmodel.f90:62 (read with the density keywords)
    nlow_default: int = -1  # input_densitypar.f90:188 -- Nlow, resolved by T6
    ntop_default: int = -1  # input_densitypar.f90:189 -- Ntop, resolved by T6
    # --- gamma (input_gammamodel.f90, input_gammapar.f90) ---
    strengthM1: int = 3  # input_gammamodel.f90:73-79
    flagracap: bool = False  # input_gammamodel.f90:61
    flagupbend: bool = True  # input_gammamodel.f90:64-68, true for k0 >= 1
    flagpsfglobal: bool = False  # input_gammamodel.f90:69
    flagglobalwtable: bool = True  # input_gammamodel.f90:70
    flagstrengthjp: bool = False  # input_gammamodel.f90:71
    flaggnorm: bool = False  # input_gammamodel.f90:72
    ldmodelracap: int = 3  # input_gammamodel.f90:80
    gammax: int = 2  # input_gammapar.f90:108
    # --- optical model (input_ompmodel.f90, input_omppar.f90) ---
    flagdisp: bool = False  # input_ompmodel.f90:96
    flagincadj: bool = True  # input_ompmodel.f90:97
    flagjlm: bool = False  # input_ompmodel.f90:98-102 (= flagmicro)
    pruitt: str = "n"  # input_ompmodel.f90:103
    flaglocalomp: bool = True  # input_ompmodel.f90:104
    flagglobaldisp: bool = False  # input_ompmodel.f90:105
    flagglobalfermi: bool = True  # input_ompmodel.f90:106
    flagompall: bool = False  # input_ompmodel.f90:107
    flagomponly: bool = False  # input_ompmodel.f90:108
    flagriplrisk: bool = False  # input_ompmodel.f90:111, input_omppar.f90:183
    flagsoukho: bool = (
        True  # input_ompmodel.f90:112; false for Z 90-97, A 228-249 (input_omppar.f90:185)
    )
    flagsoukhoinp: bool = False  # input_ompmodel.f90:113, true when `soukho` is given
    radialmodel: int = 2  # input_ompmodel.f90:118
    jlmmode: int = 0  # input_ompmodel.f90:119
    alphaomp: int = 6  # input_ompmodel.f90:120
    deuteronomp: int = 4  # input_ompmodel.f90:121
    altomp: tuple[bool, ...] = (False,) * 6 + (True,)  # input_ompmodel.f90:122-123, types 0..6
    pruittset: int = 0  # input_omppar.f90:171
    ecisstep_fm: float = 0.0  # input_omppar.f90:172
    flagspher: bool = False  # input_omppar.f90:173-178, true for jlm or k0 > 2
    riplomp: tuple[int, ...] = (
        0,
    ) * 7  # input_omppar.f90:179, :186 (riplomp(1) = 2408), types 0..6
    flagriplomp: bool = False  # input_omppar.f90:180, :184
    # --- compound nucleus (input_compoundmodel.f90, input_compoundpar.f90) ---
    flagcomp: bool = True  # input_compoundmodel.f90:67-71, false with omponly
    flageciscomp: bool = False  # input_compoundmodel.f90:72
    flagfullhf: bool = False  # input_compoundmodel.f90:73
    flagurrnjoy: bool = False  # input_compoundmodel.f90:76
    wmode: int = 1  # input_compoundmodel.f90:78-82; 1 (Moldauer) for neutrons, 2 (HRTW) otherwise
    WFCfactor: int = 1  # input_compoundmodel.f90:83
    ewfc_mev: float = -1.0  # input_compoundmodel.f90:84; sentinel -> S_k0(target), nuclides.f90:251
    reslib: str = "tendl.2025"  # input_compoundpar.f90:61
    eurr_mev: float = (
        -1.0
    )  # input_compoundpar.f90:63-67; 0 unless k0 == 1 with compound; nuclides.f90:252
    flagurr: bool = False  # input_compoundpar.f90:68-69, true with endf y, k0 == 1, A > 20
    lurr: int = 2  # input_compoundpar.f90:70
    # --- direct reactions (input_directmodel.f90, input_directpar.f90) ---
    flagautorot: bool = False  # input_directmodel.f90:70-74 (= flagmicro)
    flagrot: bool = False  # input_directmodel.f90:75
    flagcoulomb: bool = True  # input_directmodel.f90:76
    flagcpang: bool = False  # input_directmodel.f90:77
    flageciscalc: bool = True  # input_directmodel.f90:82
    flaginccalc: bool = True  # input_directmodel.f90:85
    flagecissave: bool = False  # input_directmodel.f90:88-92 (= flagompall)
    flaggiant0: bool = True  # input_directmodel.f90:93-98, true for k0 in (1, 2) without omponly
    flaglegendre: bool = False  # input_directmodel.f90:99-103 (= flagendf)
    flagstate: bool = False  # input_directmodel.f90:105
    flagsys: bool = False  # input_directmodel.f90:106
    flagtransen: bool = True  # input_directmodel.f90:107
    maxband: int = 0  # input_directpar.f90:52
    maxrot: int = 4  # input_directpar.f90:53
    core: int = -1  # input_directpar.f90:54
    eadd_mev: float = 0.0  # input_directpar.f90:55, :59 (30 with endf y and k0 == 1)
    eaddel_mev: float = 0.0  # input_directpar.f90:56, :60 (Emaxtalys with endf y and k0 == 1)
    soswitch_mev: float = 10.0  # input_directpar.f90:64
    # --- fission (input_fissionmodel.f90, input_fissionpar.f90) ---
    flagfission: bool = False  # input_fissionmodel.f90:78-80, true for A > 215
    fismodel: int = 6  # input_fissionmodel.f90:85
    fismodelalt: int = 3  # input_fissionmodel.f90:86
    flaghbstate: bool = False  # input_fissionmodel.f90:87
    flagclass2: bool = False  # input_fissionmodel.f90:88
    flagfispartdamp: bool = False  # input_fissionmodel.f90:89
    flagsffactor: bool = False  # input_fissionmodel.f90:90
    flagffevap: bool = True  # input_fissionmodel.f90:91
    flagfisfeed: bool = False  # input_fissionmodel.f90:92
    flagffspin: bool = False  # input_fissionmodel.f90:93
    flagoutfy: bool = False  # input_fissionmodel.f90:94
    fymodel: int = 2  # input_fissionmodel.f90:95
    ffmodel: int = 1  # input_fissionmodel.f90:96
    pfnsmodel: int = 1  # input_fissionmodel.f90:97-101; 2 with massdis y
    gefran: int = 50000  # input_fissionpar.f90:122
    Rfiseps: float = 1.0e-3  # input_fissionpar.f90:123-125; 1e-9 massdis, 1e-6 astro
    # --- pre-equilibrium (input_preeqmodel.f90, input_preeqpar.f90) ---
    flag2comp: bool = True  # input_preeqmodel.f90:59
    flagecisdwba: bool = True  # input_preeqmodel.f90:60
    flagonestep: bool = False  # input_preeqmodel.f90:63
    flagpecomp: bool = True  # input_preeqmodel.f90:65-71, true for k0 >= 1
    flagsurface: bool = True  # input_preeqmodel.f90:65-71, true for k0 >= 1
    breakupmodel: int = 1  # input_preeqmodel.f90:73
    mpreeqmode: int = 2  # input_preeqmodel.f90:74
    pairmodel: int = 2  # input_preeqmodel.f90:75
    pespinmodel: int = 1  # input_preeqmodel.f90:76-80; 2 for k0 > 1
    phmodel: int = 1  # input_preeqmodel.f90:81
    preeqmode: int = 2  # input_preeqmodel.f90:82
    emulpre_mev: float = 20.0  # input_preeqmodel.f90:83
    epreeq_mev: float = (
        -1.0
    )  # input_preeqmodel.f90:84-92; sentinel -> last discrete level, nuclides.f90:259
    msdbins: int = 6  # input_preeqpar.f90:89
    # --- bookkeeping ---
    explicit: frozenset[str] = field(default_factory=frozenset)  # keywords given, lowercase

    # aliases kept for the field names the phase-1 stub published
    @property
    def ldmodel(self) -> int:
        return self.ldmodelall

    @property
    def widthmode(self) -> int:
        return self.wmode

    @property
    def numJ(self) -> int:
        return NUMJ

    @property
    def projectile(self) -> str:
        return PARSYM[self.k0]

    @property
    def Ntarget(self) -> int:
        return self.Atarget - self.Ztarget

    @property
    def Zinit(self) -> int:
        """Charge number of the initial compound nucleus (input_main.f90:223)."""
        return self.Ztarget + PARZ[self.k0]

    @property
    def Ninit(self) -> int:
        """Neutron number of the initial compound nucleus (input_main.f90:224)."""
        return self.Ntarget + PARN[self.k0]

    @property
    def Ainit(self) -> int:
        return self.Zinit + self.Ninit

    # per-nucleus switches; (Zix, Nix) count protons/neutrons removed from the compound nucleus
    def ldmodel_of(self, Zix: int, Nix: int) -> int:
        """ldmodel(Zix, Nix): ldmodelCN for the compound nucleus, ldmodelall elsewhere
        (input_densitymodel.f90:245-255). Per-nucleus keyword forms are out of scope."""
        return self.ldmodelCN if (Zix, Nix) == (0, 0) else self.ldmodelall

    def flagcol_of(self, Zix: int, Nix: int) -> bool:
        """flagcol(Zix, Nix) = flagcolall (input_densitymodel.f90:100, :253)."""
        return self.flagcolall

    def nlev_of(self, Zix: int, Nix: int) -> int:
        """nlev(Zix, Nix): nlevmax for the target, nlevbin(type) for the first residual reached
        by each ejectile, nlevmaxres elsewhere (nuclides.f90, the loops before `strucinitial`)."""
        if (Zix, Nix) == (PARZ[self.k0], PARN[self.k0]):
            return self.nlevmax
        for t in range(7):
            if (Zix, Nix) == (PARZ[t], PARN[t]):
                return self.nlevbin[t]
        return self.nlevmaxres

    def fismodelx_of(self, Zix: int, Nix: int) -> int:
        """fismodelx(Zix, Nix) = fismodel (input_fissionpar.f90:119)."""
        return self.fismodel

    def axtype_of(self, Zix: int, Nix: int, ibar: int) -> int:
        """axtype(Zix, Nix, ibar), the barrier axiality (input_fissionpar.f90:103, :149-154)."""
        if not 1 <= ibar <= NUMBAR:
            raise IndexError(f"ibar {ibar} outside 1..{NUMBAR}")
        ax = 1
        if ibar == 1 and (self.Ninit - Nix > 144 or self.fismodel == 5):
            ax = 3
        if ibar == 2 and self.fismodel < 5:
            ax = 2
        if self.fismodel == 6 and ibar in (1, 2):
            ax = 1
        return ax

    def is_explicit(self, keyword: str) -> bool:
        return keyword.lower() in self.explicit


# keyword -> (stage, Options field, kind). A stage is the input_*.f90 routine whose keyword loop
# reads the keyword; kinds: yn (y/n), int, float, str, or a named special handler.
_OPTION_KEYWORDS: dict[str, tuple[str, str, str]] = {
    "ltarget": ("main", "Ltarget", "int"),
    "estop": ("main", "Estop_mev", "float"),
    "astro": ("main", "flagastro", "yn"),
    "endf": ("basicreac", "flagendf", "yn"),
    "endfdetail": ("basicreac", "flagendfdet", "yn"),
    "endfecis": ("basicreac", "flagendfecis", "yn"),
    "channels": ("basicreac", "flagchannels", "yn"),
    "labddx": ("basicreac", "flaglabddx", "yn"),
    "popmev": ("basicreac", "flagpopMeV", "yn"),
    "massdis": ("basicreac", "flagmassdis", "yn"),
    "micro": ("basicreac", "flagmicro", "yn"),
    "reaction": ("basicreac", "flagreaction", "yn"),
    "recoil": ("basicreac", "flagrecoil", "yn"),
    "recoilaverage": ("basicreac", "flagrecoilav", "yn"),
    "relativistic": ("basicreac", "flagrel", "yn"),
    "rpevap": ("basicreac", "flagrpevap", "yn"),
    "legacy": ("basicreac", "flaglegacy", "yn"),
    "channelenergy": ("basicreac", "flagEchannel", "yn"),
    "elow": ("basicpar", "eninclow_mev", "float"),
    "equidistant": ("basicpar", "flagequi", "yn"),
    "equispec": ("basicpar", "flagequispec", "yn"),
    "isomer": ("basicpar", "isomer_s", "float"),
    "liso": ("basicpar", "Lisoinp", "int"),
    "fit": ("basicpar", "flagfit", "yn"),
    "best": ("best", "flagbest", "yn"),
    "bestend": ("best", "flagbestend", "yn"),
    "astroex": ("astro", "flagastroex", "yn"),
    "astrogs": ("astro", "flagastrogs", "yn"),
    "nonthermlev": ("astro", "nonthermlev", "int"),
    "maxenrec": ("numerics", "maxenrec", "int"),
    "maxn": ("numerics", "maxN", "int"),
    "maxnrp": ("numerics", "maxNrp", "int"),
    "maxz": ("numerics", "maxZ", "int"),
    "maxzrp": ("numerics", "maxZrp", "int"),
    "bins": ("numerics", "nbins0", "int"),
    "segment": ("numerics", "segment", "int"),
    "angles": ("numerics", "nangle", "int"),
    "anglescont": ("numerics", "nanglecont", "int"),
    "anglesrec": ("numerics", "nanglerec", "int"),
    "maxchannel": ("numerics", "maxchannel", "int"),
    "transpower": ("numerics", "transpower", "int"),
    "transeps": ("numerics", "transeps", "float"),
    "xseps": ("numerics", "xseps_mb", "float"),
    "popeps": ("numerics", "popeps_mb", "float"),
    "expmass": ("mass", "flagexpmass", "yn"),
    "massmodel": ("mass", "massmodel", "int"),
    "pseudoresonances": ("levels", "flagpseudores", "yn"),
    "electronconv": ("levels", "flagelectron", "yn"),
    "disctable": ("levels", "disctable", "int"),
    "bestbranch": ("levels", "flagbestbr", "yn"),
    "maxlevelstar": ("levels", "nlevmax", "maxlevelstar"),
    "maxlevelsres": ("levels", "nlevmaxres", "int"),
    "ldmodel": ("densitymodel", "ldmodelall", "int"),
    "ldmodelcn": ("densitymodel", "ldmodelCN", "int"),
    "strength": ("densitymodel", "strength", "int"),
    "shellmodel": ("densitymodel", "shellmodel", "int"),
    "spincutmodel": ("densitymodel", "spincutmodel", "int"),
    "kvibmodel": ("densitymodel", "kvibmodel", "int"),
    "colenhance": ("densitymodel", "flagcolall", "yn"),
    "colldamp": ("densitymodel", "flagcolldamp", "yn"),
    "ldglobal": ("densitymodel", "flagldglobal", "yn"),
    "asys": ("densitymodel", "flagasys", "yn"),
    "ctmglobal": ("densitymodel", "flagctmglob", "yn"),
    "parity": ("densitypar", "flagparity", "yn"),
    "gshell": ("preeqmodel", "flaggshell", "yn"),
    "strengthm1": ("gammamodel", "strengthM1", "int"),
    "racap": ("gammamodel", "flagracap", "yn"),
    "upbend": ("gammamodel", "flagupbend", "yn"),
    "psfglobal": ("gammamodel", "flagpsfglobal", "yn"),
    "globalwtable": ("gammamodel", "flagglobalwtable", "yn"),
    "strengthjp": ("gammamodel", "flagstrengthjp", "yn"),
    "gnorm": ("gammamodel", "flaggnorm", "yn"),
    "ldmodelracap": ("gammamodel", "ldmodelracap", "int"),
    "gammax": ("gammapar", "gammax", "int"),
    "dispersion": ("ompmodel", "flagdisp", "yn"),
    "incadjust": ("ompmodel", "flagincadj", "yn"),
    "jlmomp": ("ompmodel", "flagjlm", "yn"),
    "pruitt": ("ompmodel", "pruitt", "str"),
    "localomp": ("ompmodel", "flaglocalomp", "yn"),
    "globaldisp": ("ompmodel", "flagglobaldisp", "yn"),
    "globalfermi": ("ompmodel", "flagglobalfermi", "yn"),
    "optmodall": ("ompmodel", "flagompall", "yn"),
    "omponly": ("ompmodel", "flagomponly", "yn"),
    "riplrisk": ("ompmodel", "flagriplrisk", "yn"),
    "soukho": ("ompmodel", "flagsoukho", "soukho"),
    "radialmodel": ("ompmodel", "radialmodel", "int"),
    "jlmmode": ("ompmodel", "jlmmode", "int"),
    "alphaomp": ("ompmodel", "alphaomp", "int"),
    "deuteronomp": ("ompmodel", "deuteronomp", "int"),
    "pruittset": ("omppar", "pruittset", "int"),
    "ecisstep": ("omppar", "ecisstep_fm", "float"),
    "spherical": ("omppar", "flagspher", "yn"),
    "compound": ("compoundmodel", "flagcomp", "yn"),
    "eciscompound": ("compoundmodel", "flageciscomp", "yn"),
    "fullhf": ("compoundmodel", "flagfullhf", "yn"),
    "urrnjoy": ("compoundmodel", "flagurrnjoy", "yn"),
    "widthmode": ("compoundmodel", "wmode", "int"),
    "wfcfactor": ("compoundmodel", "WFCfactor", "int"),
    "widthfluc": ("compoundmodel", "ewfc_mev", "widthfluc"),
    "reslib": ("compoundpar", "reslib", "str"),
    "urr": ("compoundpar", "flagurr", "urr"),
    "lurr": ("compoundpar", "lurr", "int"),
    "autorot": ("directmodel", "flagautorot", "yn"),
    "coulomb": ("directmodel", "flagcoulomb", "yn"),
    "cpang": ("directmodel", "flagcpang", "yn"),
    "eciscalc": ("directmodel", "flageciscalc", "yn"),
    "inccalc": ("directmodel", "flaginccalc", "yn"),
    "ecissave": ("directmodel", "flagecissave", "yn"),
    "giantresonance": ("directmodel", "flaggiant0", "yn"),
    "outlegendre": ("directmodel", "flaglegendre", "yn"),
    "statepot": ("directmodel", "flagstate", "yn"),
    "maxband": ("directpar", "maxband", "int"),
    "maxrot": ("directpar", "maxrot", "int"),
    "core": ("directpar", "core", "int"),
    "adddiscrete": ("directpar", "eadd_mev", "onset"),
    "addelastic": ("directpar", "eaddel_mev", "onset"),
    "soswitch": ("directpar", "soswitch_mev", "float"),
    "fission": ("fissionmodel", "flagfission", "yn"),
    "fismodel": ("fissionmodel", "fismodel", "int"),
    "fismodelalt": ("fissionmodel", "fismodelalt", "int"),
    "hbstate": ("fissionmodel", "flaghbstate", "yn"),
    "class2": ("fissionmodel", "flagclass2", "yn"),
    "fispartdamp": ("fissionmodel", "flagfispartdamp", "yn"),
    "sffactor": ("fissionmodel", "flagsffactor", "yn"),
    "ffevaporation": ("fissionmodel", "flagffevap", "yn"),
    "fisfeed": ("fissionmodel", "flagfisfeed", "yn"),
    "ffspin": ("fissionmodel", "flagffspin", "yn"),
    "outfy": ("fissionmodel", "flagoutfy", "yn"),
    "fymodel": ("fissionmodel", "fymodel", "int"),
    "ffmodel": ("fissionmodel", "ffmodel", "int"),
    "pfnsmodel": ("fissionmodel", "pfnsmodel", "int"),
    "gefran": ("fissionpar", "gefran", "int"),
    "rfiseps": ("fissionpar", "Rfiseps", "float"),
    "twocomponent": ("preeqmodel", "flag2comp", "yn"),
    "ecisdwba": ("preeqmodel", "flagecisdwba", "yn"),
    "onestep": ("preeqmodel", "flagonestep", "yn"),
    "preeqcomplex": ("preeqmodel", "flagpecomp", "yn"),
    "preeqsurface": ("preeqmodel", "flagsurface", "yn"),
    "breakupmodel": ("preeqmodel", "breakupmodel", "int"),
    "mpreeqmode": ("preeqmodel", "mpreeqmode", "int"),
    "pairmodel": ("preeqmodel", "pairmodel", "int"),
    "preeqspin": ("preeqmodel", "pespinmodel", "int"),
    "phmodel": ("preeqmodel", "phmodel", "int"),
    "preeqmode": ("preeqmodel", "preeqmode", "int"),
    "preequilibrium": ("preeqmodel", "epreeq_mev", "onset"),
    "multipreeq": ("preeqmodel", "emulpre_mev", "onset"),
    "msdbins": ("preeqpar", "msdbins", "int"),
    "production": ("medical", "flagprod", "yn"),
    "ngfit": ("fit", "flagngfit", "yn"),
    "nnfit": ("fit", "flagnnfit", "yn"),
    "nffit": ("fit", "flagnffit", "yn"),
    "nafit": ("fit", "flagnafit", "yn"),
    "ndfit": ("fit", "flagndfit", "yn"),
    "pnfit": ("fit", "flagpnfit", "yn"),
    "gnfit": ("fit", "flaggnfit", "yn"),
    "dnfit": ("fit", "flagdnfit", "yn"),
    "anfit": ("fit", "flaganfit", "yn"),
    "macsfit": ("fit", "flagmacsfit", "yn"),
    "gamgamfit": ("fit", "flaggamgamfit", "yn"),
}

# the order of talysinput.f90 (input_main ... input_fit)
_STAGES = (
    "main", "best", "basicreac", "basicpar", "astro", "numerics", "mass", "levels",
    "densitymodel", "densitypar", "gammamodel", "gammapar", "ompmodel", "omppar",
    "compoundmodel", "compoundpar", "directmodel", "directpar", "fissionmodel", "fissionpar",
    "preeqmodel", "preeqpar", "medical", "fit",
)  # fmt: skip

OPTION_KEYWORDS = frozenset(_OPTION_KEYWORDS)


def _yn(value) -> bool:
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s[:1] == "y":
        return True
    if s[:1] == "n":
        return False
    raise ValueError(f"expected y/n, got {value!r}")


def _is_yn(value) -> bool:
    return isinstance(value, bool) or str(value).strip().lower()[:1] in ("y", "n")


def _apply_stage(stage: str, o: dict, overrides: Mapping[str, object]) -> None:
    """Apply the explicit keywords that the `stage` routine's keyword loop reads."""
    for key, value in overrides.items():
        spec = _OPTION_KEYWORDS.get(key)
        if spec is None or spec[0] != stage:
            continue
        _, name, kind = spec
        if kind == "yn":
            o[name] = _yn(value)
        elif kind == "int":
            o[name] = int(value)
        elif kind == "float":
            o[name] = float(value)
        elif kind == "str":
            o[name] = str(value)
        elif kind == "maxlevelstar":  # input_levels.f90, sets nlevmax and nlevbin(k0)
            o["nlevmax"] = int(value)
            nb = list(o["nlevbin"])
            nb[o["k0"]] = int(value)
            o["nlevbin"] = tuple(nb)
        elif kind == "soukho":  # input_ompmodel.f90 keyword loop: also flagsoukhoinp
            o["flagsoukho"] = _yn(value)
            o["flagsoukhoinp"] = True
        elif kind == "widthfluc":  # input_compoundmodel.f90 keyword loop
            if _is_yn(value) and not isinstance(value, (int, float)):
                if _yn(value):
                    if o["k0"] > 1:
                        o["ewfc_mev"] = 10.0
                else:
                    o["ewfc_mev"] = 0.0
            else:
                o["ewfc_mev"] = float(value)
        elif kind == "onset":  # preequilibrium / multipreeq / adddiscrete / addelastic: y, n or MeV
            if _is_yn(value) and not isinstance(value, (int, float)):
                o[name] = 0.0 if _yn(value) else EMAXTALYS_MEV
            else:
                o[name] = float(value)
        elif kind == "urr":  # input_compoundpar.f90 keyword loop: y/n or an onset energy
            if _is_yn(value) and not isinstance(value, (int, float)):
                o["flagurr"] = _yn(value)
            else:
                o["flagurr"] = True
                o["eurr_mev"] = float(value)
        else:  # pragma: no cover - table is static
            raise AssertionError(kind)


def default_options(
    Z: int, A: int, projectile: str = "n", overrides: Mapping[str, object] | None = None,
    _fit: bool = True,
) -> Options:
    """The TALYS defaults for this target and projectile, with optional explicit keywords.

    `overrides` maps lowercase TALYS keywords (``{"ldmodel": 1, "widthfluc": "n"}``) to their
    values; each is applied at the point in talysinput.f90 where TALYS reads it, so dependent
    defaults follow. Only global scalar keyword forms are accepted. Structure-dependent onsets
    (`ewfc_mev`, `eurr_mev`, `epreeq_mev`) and `eninclow_mev == 0` stay sentinels; see
    :func:`resolve_structure_defaults`.

    TALYS: input_main.f90:1 (input_main), input_basicreac.f90:1 (input_basicreac),
    input_basicpar.f90:1 (input_basicpar), input_numerics.f90:1 (input_numerics),
    input_levels.f90:1 (input_levels), input_densitymodel.f90:1 (input_densitymodel),
    input_densitypar.f90:1 (input_densitypar), input_gammamodel.f90:1 (input_gammamodel),
    input_ompmodel.f90:1 (input_ompmodel), input_omppar.f90:1 (input_omppar),
    input_compoundmodel.f90:1 (input_compoundmodel), input_compoundpar.f90:1 (input_compoundpar),
    input_directmodel.f90:1 (input_directmodel), input_directpar.f90:1 (input_directpar),
    input_fissionmodel.f90:1 (input_fissionmodel), input_fissionpar.f90:1 (input_fissionpar),
    input_preeqmodel.f90:1 (input_preeqmodel), input_fit.f90:1 (input_fit),
    nuclides.f90:1 (nuclides)
    Test: tests/hf/test_defaults.py (talys.out "USER INPUT FILE + DEFAULTS" echo)
    """
    if projectile not in PARSYM:
        raise ValueError(f"projectile {projectile!r} not one of {PARSYM}")
    ov = {str(k).lower(): v for k, v in (overrides or {}).items()}
    if _fit:
        # BESTFIT: `best y` puts the best file's lines BEFORE the user's (initial_best.f90:113-124),
        # so a keyword the caller gives itself still wins. Off unless INCOGNITA_TALYS_FIT is set.
        from physics.hf.input import fitlib

        fit_ov = fitlib.option_overrides()
        if fit_ov:
            ov = {**{str(k).lower(): v for k, v in fit_ov.items()}, **ov}
    unknown = sorted(set(ov) - OPTION_KEYWORDS)
    if unknown:
        raise KeyError(
            f"not an Options keyword (or out of scope for T3): {unknown}; adjustable parameters "
            "go to default_params(overrides=...)"
        )
    for k, v in ov.items():
        if isinstance(v, str) and len(v.split()) > 1:
            raise ValueError(f"{k}: per-nucleus keyword forms are out of scope, got {v!r}")

    k0 = PARSYM.index(projectile)
    o: dict = {f.name: f.default for f in fields(Options) if f.name != "explicit"}
    o.update(Ztarget=int(Z), Atarget=int(A), k0=k0)
    # input_main.f90: ltarget, estop, astro are read there
    _apply_stage("main", o, ov)
    _apply_stage("best", o, ov)

    # input_basicreac.f90
    o["flagendfdet"] = k0 <= 1  # :70-74
    _apply_stage("basicreac", o, ov)

    # input_basicpar.f90 (runs after read_energies)
    o["eninclow_mev"] = 0.0 if (k0 == 1 and o["flagendf"]) else 1.0e-6  # :54-58
    _apply_stage("basicpar", o, ov)
    _apply_stage("astro", o, ov)

    # input_numerics.f90
    o["nanglerec"] = NUMANGREC if o["flaglabddx"] else 1  # :74-78
    if o["flagmassdis"]:  # :83-88
        o.update(transpower=10, transeps=1.0e-12, xseps_mb=1.0e-12, popeps_mb=1.0e-10)
    if o["flagastro"]:  # :89-94
        o.update(transpower=15, transeps=1.0e-18, xseps_mb=1.0e-17, popeps_mb=1.0e-13)
    _apply_stage("numerics", o, ov)
    _apply_stage("mass", o, ov)

    # input_levels.f90
    if o["flagendf"]:  # :98
        o["flagelectron"] = True
    o["nlevmax"] = max(30, o["Ltarget"])  # :106
    nb = [30] * 7  # :107
    nb[k0] = o["nlevmax"]  # :109
    o["nlevbin"] = tuple(nb)
    _apply_stage("levels", o, ov)

    # input_densitymodel.f90
    o["ldmodelall"] = 7 if o["flagmicro"] else 1  # :84-88
    o["strength"] = 9  # :89
    if k0 <= 1 and A > FISLIM:  # :90
        o["ldmodelall"] = 7
    o["ldmodelCN"] = 0  # :91
    o["flagcolall"] = A > FISLIM  # :95-99
    _apply_stage("densitymodel", o, ov)
    if o["ldmodelCN"] <= 0:  # :245-249
        o["ldmodelCN"] = o["ldmodelall"]

    # input_densitypar.f90
    o["flagparity"] = o["ldmodelall"] >= 5  # :176-180
    _apply_stage("densitypar", o, ov)

    # input_gammamodel.f90
    o["flagupbend"] = k0 >= 1  # :64-68
    s = o["strength"]
    m1 = 3  # :73-79
    if s == 8:
        m1 = 8
    if s == 10:
        m1 = 10
    if s == 11:
        m1 = 11
    if s == 12:
        m1 = 12
    if s == 13:
        m1 = 8
    if s <= 2:
        m1 = 2
    o["strengthM1"] = m1
    _apply_stage("gammamodel", o, ov)
    _apply_stage("gammapar", o, ov)

    # input_ompmodel.f90
    o["flagjlm"] = o["flagmicro"]  # :98-102
    _apply_stage("ompmodel", o, ov)

    # input_omppar.f90
    o["flagspher"] = bool(o["flagjlm"]) or k0 > 2  # :173-178
    rip = [0] * 7
    if not o["flagsoukhoinp"] and A > FISLIM:  # :181-188
        if (90 <= Z <= 97 and 228 <= A <= 249) or o["flagriplrisk"]:
            o["flagriplrisk"] = True
            o["flagriplomp"] = True
            o["flagsoukho"] = False
            rip[1] = 2408
    o["riplomp"] = tuple(rip)
    _apply_stage("omppar", o, ov)

    # input_compoundmodel.f90
    o["flagcomp"] = not o["flagomponly"]  # :67-71
    o["wmode"] = 1 if k0 == 1 else 2  # :78-82
    o["ewfc_mev"] = -1.0  # :84
    _apply_stage("compoundmodel", o, ov)

    # input_compoundpar.f90
    o["eurr_mev"] = 0.0 if (k0 != 1 or not o["flagcomp"]) else -1.0  # :63-67
    o["flagurr"] = bool(o["flagendf"] and k0 == 1 and A > 20)  # :68-69
    _apply_stage("compoundpar", o, ov)

    # input_directmodel.f90
    o["flagautorot"] = o["flagmicro"]  # :70-74
    o["flagecissave"] = o["flagompall"]  # :88-92
    o["flaggiant0"] = k0 in (1, 2) and not o["flagomponly"]  # :93-98
    o["flaglegendre"] = o["flagendf"]  # :99-103
    _apply_stage("directmodel", o, ov)

    # input_directpar.f90
    if o["flagendf"] and k0 == 1:  # :57-62
        o["eadd_mev"], o["eaddel_mev"] = 30.0, EMAXTALYS_MEV
    _apply_stage("directpar", o, ov)

    # input_fissionmodel.f90
    o["flagfission"] = A > FISLIM  # :78-80
    o["pfnsmodel"] = 2 if o["flagmassdis"] else 1  # :97-101
    _apply_stage("fissionmodel", o, ov)

    # input_fissionpar.f90
    o["Rfiseps"] = 1.0e-3  # :123-125
    if o["flagmassdis"]:
        o["Rfiseps"] = 1.0e-9
    if o["flagastro"]:
        o["Rfiseps"] = 1.0e-6
    _apply_stage("fissionpar", o, ov)

    # input_preeqmodel.f90
    o["flagpecomp"] = o["flagsurface"] = k0 >= 1  # :65-71
    o["pespinmodel"] = 1 if k0 <= 1 else 2  # :76-80
    o["emulpre_mev"] = 20.0  # :83
    o["epreeq_mev"] = -1.0  # :84-88 (ptype0 == '0' is not a projectile this port takes)
    if o["flagomponly"]:  # :89-92
        o["epreeq_mev"] = o["emulpre_mev"] = EMAXTALYS_MEV
    _apply_stage("preeqmodel", o, ov)
    _apply_stage("preeqpar", o, ov)
    _apply_stage("medical", o, ov)

    # input_fit.f90: :53-63
    fit, astro = o["flagfit"], o["flagastro"]
    o.update(
        flagngfit=k0 == 1 and fit and not astro, flagnnfit=k0 == 1 and fit,
        flagnffit=k0 == 1 and fit, flagnafit=k0 == 1 and fit, flagndfit=k0 == 1 and fit,
        flagpnfit=k0 == 2 and fit, flaggnfit=k0 == 0 and fit, flagdnfit=k0 == 3 and fit,
        flaganfit=k0 == 6 and fit, flagmacsfit=k0 == 1 and fit and astro, flaggamgamfit=False,
    )  # fmt: skip
    _apply_stage("fit", o, ov)

    # input_output.f90:127-143 -- the one physics switch the output defaults touch: ENDF-6 mode
    # with detail turns on the exclusive-channel calculation (read after every other stage)
    if o["flagendf"] and o["flagendfdet"] and "channels" not in ov:
        o["flagchannels"] = True

    # nuclides.f90:140-141 -- no residual beyond three protons/neutrons short of the CN
    zinit, ninit = Z + PARZ[k0], (A - Z) + PARN[k0]
    o["maxZ"] = min(o["maxZ"], zinit - 3)
    o["maxN"] = min(o["maxN"], ninit - 3)

    return Options(**o, explicit=frozenset(ov))


#: Keyword settings the port does not implement. Each one used to run and return numbers that are
#: NOT the TALYS model asked for (a silent fallback) or crash deep inside a calculation; checked
#: against stock TALYS-2.24 on 2026-09-21 (THRESH-SCREEN, development notes).
UNPORTED = (
    ("flagjlm", lambda v: bool(v), "jlmomp y: JLM microscopic optical model. Silently kept the phenomenological "
     "potential where a local OMP file exists and gave a different response elsewhere (Se-80: stock reaction "
     "cross section -12 %, engine -1.3 %)"),
    ("alphaomp", lambda v: 3 <= int(v) <= 5, "alphaomp 3-5: double-folding alpha potentials. Silently equal to "
     "the Watanabe potential (alphaomp 1)"),
    ("preeqmode", lambda v: int(v) == 3, "preeqmode 3: exciton model with optical-model transition rates "
     "(bonetti.f90)"),
    ("pespinmodel", lambda v: int(v) == 3, "preeqspin 3: J-dependent pre-equilibrium population "
     "(xspreeqjp is consumed but never produced)"),
    ("flag2comp", lambda v: not bool(v), "twocomponent n: one-component exciton model (transition_rates has "
     "only the two-component path)"),
    ("flaggshell", lambda v: bool(v), "gshell y: shell-damped single-particle density in the exciton model "
     "(damp_comp never reaches multiple pre-equilibrium)"),
    ("flaggnorm", lambda v: bool(v), "gnorm y: normalise the E1 strength to the measured <Gamma_gamma>. "
     "gamma.transmission.radwidtheory has the iteration but no calculation calls it, so the run was "
     "identical to gnorm n (223 nuclides, 2026-09-22); scale the strength with `ftable Z A f` instead"),
)


def reject_unported(options) -> None:
    """Refuse, at the start of a CALCULATION, keyword settings the port does not implement, instead
    of returning wrong numbers. Option resolution itself stays faithful (the echo tests replay TALYS
    inputs that use them); only computing with them is refused.

    TALYS: (none -- a port guard)
    Test: tests/hf/test_unported_options.py
    """
    o = options if isinstance(options, dict) else vars(options)
    bad = [msg for key, is_bad, msg in UNPORTED if key in o and is_bad(o[key])]
    if bad:
        raise NotImplementedError("not ported: " + "; ".join(bad))


def resolve_structure_defaults(
    options: Options,
    *,
    s_projectile_mev: float,
    e_last_level_mev: float,
    d0_ev: float | None = None,
    d0theo_ev: float | None = None,
    energies_mev: tuple[float, ...] = (),
) -> Options:
    """Fill the defaults TALYS derives from structure once the target is read.

    `s_projectile_mev` is S(parZ(k0), parN(k0), k0), the separation energy of the projectile
    from the *target* (Fe-56 + n: 11.197 MeV); `e_last_level_mev` is edis of the last discrete
    level NL of the target; `d0_ev` / `d0theo_ev` are D0(0,0) (tabulated, 0 if absent) and its
    theoretical value for the compound nucleus, used only when `eninclow_mev == 0` (endf y); if
    neither is given, eninclow stays 0 (unresolved). `energies_mev` is the incident-energy list.
    Explicit keywords are left alone because they replaced the sentinel.

    TALYS: nuclides.f90:1 (nuclides) lines 251, 252, 259; grid.f90:1 (grid) lines 221-229
    Test: tests/hf/test_defaults.py (echo of widthfluc / urr / preequilibrium / elow)
    """
    ch: dict = {}
    if options.k0 >= 1 and options.ewfc_mev == -1.0:  # nuclides.f90:251
        ch["ewfc_mev"] = float(s_projectile_mev)
    if options.k0 == 1 and options.eurr_mev == -1.0 and options.flagurr:  # nuclides.f90:252
        ch["eurr_mev"] = float(s_projectile_mev)
    if options.epreeq_mev == -1.0:  # nuclides.f90:259
        ch["epreeq_mev"] = max(float(e_last_level_mev), 1.0)
    elow = options.eninclow_mev
    if elow == 0.0 and d0_ev is None and d0theo_ev is None:
        return replace(options, **ch)
    if elow == 0.0:  # grid.f90:221-227
        d0 = (d0theo_ev or 0.0) if not d0_ev else d0_ev
        elow = min(d0 * 1.0e-6, 1.0)
    numenlow = 20  # A0_talys_mod.f90:99
    if len(energies_mev) >= numenlow - 2:  # grid.f90:228
        elow = min(elow, sorted(energies_mev)[numenlow - 3])
    ch["eninclow_mev"] = max(elow, 1.0e-11)  # grid.f90:229
    return replace(options, **ch)


def energy_flags(options: Options, e_inc_mev: float) -> dict[str, bool]:
    """Switches TALYS sets per incident energy from the resolved onsets (energies.f90).

    Returns flagwidth, flagurr, flagpreeq, flaggiant, flagmulpre. Requires the onsets to be
    resolved (:func:`resolve_structure_defaults`); a -1 sentinel raises.

    TALYS: energies.f90:1 (energies) lines 179-210
    Test: tests/hf/test_defaults.py (echo of widthfluc / preequilibrium / multipreeq at 1 MeV)
    """
    if (options.k0 >= 1 and options.ewfc_mev == -1.0) or options.epreeq_mev == -1.0:
        raise ValueError("onsets not resolved; call resolve_structure_defaults first")
    e = float(e_inc_mev)
    preeq = not e < options.epreeq_mev  # :194-203
    return {
        "flagwidth": e <= options.ewfc_mev,  # :179-183
        "flagurr": e <= options.eurr_mev,  # :184-188
        "flagpreeq": preeq,
        "flaggiant": preeq and options.flaggiant0,
        "flagmulpre": not e < options.emulpre_mev,  # :205-209
    }


# ---------------------------------------------------------------------------------------------
# Params
# ---------------------------------------------------------------------------------------------

_Z = (0, NUMZ)
_N = (0, NUMN)
_BAR0 = (0, NUMBAR)
_BAR1 = (1, NUMBAR)
_PAR0 = (0, NUMPAR)
_PARM1 = (-1, NUMPAR)
_IRAD = (0, 1)
_GAM = (1, NUMGAM)
_IGR = (1, 2)
_UPB = (1, 3)
_LEV = (0, NUMLEV)
_OMPADJ = (1, NUMOMPADJ)
_RANGE = (1, NUMRANGE)
_ISOM = (-1, NUMISOM)


@dataclass(frozen=True)
class ParamSpec:
    """One adjustable TALYS parameter.

    `dims` are the Fortran bounds `(lo, hi)` of each axis. The tensor keeps the Fortran index:
    storage index = Fortran index - min(lo, 0), so 1-based axes have an unused slot 0 and
    (-1)-based axes are shifted by +1 (`offsets`). `source` is the file:line of the default;
    `resolved_by` names the routine (and port task) that replaces a sentinel default.
    """

    keyword: str
    variable: str
    dims: tuple[tuple[int, int], ...]
    default: float | str
    source: str
    unit: str = ""
    resolved_by: str | None = None

    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(hi - min(lo, 0) + 1 for lo, hi in self.dims)

    @property
    def offsets(self) -> tuple[int, ...]:
        return tuple(-min(lo, 0) for lo, _ in self.dims)


def _spec(keyword, variable, dims, default, source, unit="", resolved_by=None) -> ParamSpec:
    return ParamSpec(keyword, variable, tuple(dims), default, source, unit, resolved_by)


# `default` is the fill value; a string names a builder in `default_params` for defaults that
# depend on the nucleus, the barrier, or earlier switches.
_SPECS: tuple[ParamSpec, ...] = (
    # --- masses and deformation (input_mass.f90) ---
    _spec("beta2", "beta2", [(0, NUMZ + 4), (0, NUMN + 4), _BAR0], "beta2", "input_mass.f90:60-69"),
    _spec(
        "massexcess",
        "massexcess",
        [(0, NUMZ + 4), (0, NUMN + 4)],
        0.0,
        "input_mass.f90:72",
        "MeV",
        "0 = use the mass table (masses.f90, T2)",
    ),
    _spec(
        "massnucleus",
        "massnucleus",
        [(0, NUMZ + 4), (0, NUMN + 4)],
        0.0,
        "input_mass.f90:74",
        "amu",
        "0 = use the mass table (masses.f90, T2)",
    ),
    # --- discrete levels (input_levels.f90) ---
    _spec("risomer", "Risomer", [_Z, _N], 1.0, "input_levels.f90:92"),
    _spec("emaxpseudores", "Emaxpseudores", [], -1.0, "input_levels.f90:94", "MeV"),
    _spec("pseudoreswidth", "pseudoreswidth", [], 0.3, "input_levels.f90:95", "MeV"),
    _spec("pseudoresfade", "pseudoresfade", [], 0.2, "input_levels.f90:96", "MeV"),
    # --- level densities (input_densitymodel.f90, input_densitypar.f90) ---
    _spec("cglobal", "cglobal", [], 1.0e-20, "input_densitymodel.f90:108"),
    _spec("pglobal", "pglobal", [], 1.0e-20, "input_densitymodel.f90:109", "MeV"),
    _spec("rspincutff", "Rspincutff", [], 4.0, "input_densitymodel.f90:110"),
    _spec("alphald", "alphald", [_Z, _N], "ld_systematics", "input_densitypar.f90:116-164"),
    _spec("betald", "betald", [_Z, _N], "ld_systematics", "input_densitypar.f90:116-164"),
    _spec("gammashell1", "gammashell1", [_Z, _N], "ld_systematics", "input_densitypar.f90:116-164"),
    _spec(
        "pshiftconstant",
        "Pshiftconstant",
        [_Z, _N],
        "ld_systematics",
        "input_densitypar.f90:116-164",
        "MeV",
    ),
    _spec("aadjust", "aadjust", [_Z, _N], 1.0, "input_densitypar.f90:165"),
    _spec(
        "a",
        "alev",
        [_Z, _N],
        0.0,
        "input_densitypar.f90:166",
        "MeV^-1",
        "densitypar.f90 systematics (T6)",
    ),
    _spec(
        "alimit",
        "alimit",
        [_Z, _N],
        0.0,
        "input_densitypar.f90:167",
        "MeV^-1",
        "densitypar.f90 (T6)",
    ),
    _spec("ctableadjust", "ctableadjust", [_Z, _N, _BAR0], 0.0, "input_densitypar.f90:168"),
    _spec("ptableadjust", "ptableadjust", [_Z, _N, _BAR0], 0.0, "input_densitypar.f90:169", "MeV"),
    _spec(
        "deltaw",
        "deltaW",
        [_Z, _N, _BAR0],
        0.0,
        "input_densitypar.f90:170",
        "MeV",
        "shell correction from the mass tables (T6)",
    ),
    _spec(
        "d0", "D0", [_Z, _N], 0.0, "input_densitypar.f90:171", "eV", "resonance parameter file (T2)"
    ),
    _spec(
        "e0", "E0", [_Z, _N, _BAR0], 1.0e-20, "input_densitypar.f90:172", "MeV", "CTM matching (T6)"
    ),
    _spec("e0adjust", "E0adjust", [_Z, _N, _BAR0], 1.0, "input_densitypar.f90:173"),
    _spec(
        "exmatch",
        "Exmatch",
        [_Z, _N, _BAR0],
        0.0,
        "input_densitypar.f90:174",
        "MeV",
        "CTM matching (T6)",
    ),
    _spec("exmatchadjust", "Exmatchadjust", [_Z, _N, _BAR0], 1.0, "input_densitypar.f90:175"),
    _spec(
        "gammald",
        "gammald",
        [_Z, _N],
        -1.0,
        "input_densitypar.f90:185",
        "",
        "densitypar.f90 systematics (T6)",
    ),
    _spec("gammashell2", "gammashell2", [], 0.0, "input_densitypar.f90:186"),
    _spec("krotconstant", "Krotconstant", [_Z, _N, _BAR0], 1.0, "input_densitypar.f90:187"),
    _spec(
        "pair",
        "pair",
        [_Z, _N],
        1.0e-20,
        "input_densitypar.f90:190",
        "MeV",
        "densitypar.f90 pairing systematics (T6)",
    ),
    _spec("pairconstant", "pairconstant", [], 12.0, "input_densitypar.f90:191", "MeV"),
    _spec(
        "pshift",
        "Pshift",
        [_Z, _N, _BAR0],
        1.0e-20,
        "input_densitypar.f90:192",
        "MeV",
        "densitypar.f90 (T6)",
    ),
    _spec("pshiftadjust", "Pshiftadjust", [_Z, _N, _BAR0], 0.0, "input_densitypar.f90:193", "MeV"),
    _spec("rclass2mom", "Rclass2mom", [_Z, _N, _BAR0], 1.0, "input_densitypar.f90:194"),
    _spec("rspincut", "Rspincut", [], 1.0, "input_densitypar.f90:195"),
    _spec("rtransmom", "Rtransmom", [_Z, _N, _BAR0], "rtransmom", "input_densitypar.f90:196-199"),
    _spec("ufermi", "Ufermi", [_Z, _N, _BAR0], "ufermi", "input_densitypar.f90:200-205", "MeV"),
    _spec("cfermi", "cfermi", [_Z, _N, _BAR0], 5.0, "input_densitypar.f90:201-204", "MeV"),
    _spec("s2adjust", "s2adjust", [_Z, _N, _BAR0], 1.0, "input_densitypar.f90:208"),
    _spec("t", "T", [_Z, _N, _BAR0], 0.0, "input_densitypar.f90:209", "MeV", "CTM matching (T6)"),
    _spec("tadjust", "Tadjust", [_Z, _N, _BAR0], 1.0, "input_densitypar.f90:210"),
    _spec(
        "ctable",
        "ctable",
        [_Z, _N, _BAR0],
        "cglobal",
        "input_densitypar.f90:211",
        "",
        "for ldmodel >= 4: the HFB table normalisation read with the tables (T6)",
    ),
    _spec(
        "ptable",
        "ptable",
        [_Z, _N, _BAR0],
        "pglobal",
        "input_densitypar.f90:212",
        "MeV",
        "for ldmodel >= 4: the HFB table normalisation read with the tables (T6)",
    ),
    # --- photon strength (input_gammapar.f90) ---
    _spec(
        "egr",
        "egr",
        [_Z, _N, _IRAD, _GAM, _IGR],
        0.0,
        "input_gammapar.f90:82",
        "MeV",
        "gammapar.f90 GDR systematics (T7)",
    ),
    _spec(
        "ggr",
        "ggr",
        [_Z, _N, _IRAD, _GAM, _IGR],
        0.0,
        "input_gammapar.f90:83",
        "MeV",
        "gammapar.f90 (T7)",
    ),
    _spec(
        "sgr",
        "sgr",
        [_Z, _N, _IRAD, _GAM, _IGR],
        0.0,
        "input_gammapar.f90:84",
        "mb",
        "gammapar.f90 (T7)",
    ),
    _spec("epr", "epr", [_Z, _N, _IRAD, _GAM, _IGR], 0.0, "input_gammapar.f90:85", "MeV"),
    _spec("gpr", "gpr", [_Z, _N, _IRAD, _GAM, _IGR], 0.0, "input_gammapar.f90:86", "MeV"),
    _spec("spr", "tpr", [_Z, _N, _IRAD, _GAM, _IGR], 0.0, "input_gammapar.f90:87", "mb"),
    _spec("egradjust", "egradjust", [_Z, _N, _IRAD, _GAM, _IGR], 1.0, "input_gammapar.f90:88"),
    _spec("ggradjust", "ggradjust", [_Z, _N, _IRAD, _GAM, _IGR], 1.0, "input_gammapar.f90:89"),
    _spec("sgradjust", "sgradjust", [_Z, _N, _IRAD, _GAM, _IGR], 1.0, "input_gammapar.f90:90"),
    _spec("epradjust", "epradjust", [_Z, _N, _IRAD, _GAM, _IGR], 1.0, "input_gammapar.f90:91"),
    _spec("gpradjust", "gpradjust", [_Z, _N, _IRAD, _GAM, _IGR], 1.0, "input_gammapar.f90:92"),
    _spec("spradjust", "tpradjust", [_Z, _N, _IRAD, _GAM, _IGR], 1.0, "input_gammapar.f90:93"),
    _spec("etable", "etable", [_Z, _N, _IRAD, _GAM], 0.0, "input_gammapar.f90:94", "MeV"),
    _spec("ftable", "ftable", [_Z, _N, _IRAD, _GAM], 1.0, "input_gammapar.f90:95"),
    _spec("wtable", "wtable", [_Z, _N, _IRAD, _GAM], "wtable", "input_gammapar.f90:96, :113-138"),
    _spec(
        "etableadjust", "etableadjust", [_Z, _N, _IRAD, _GAM], 0.0, "input_gammapar.f90:98", "MeV"
    ),
    _spec("ftableadjust", "ftableadjust", [_Z, _N, _IRAD, _GAM], 1.0, "input_gammapar.f90:99"),
    _spec("wtableadjust", "wtableadjust", [_Z, _N, _IRAD, _GAM], 1.0, "input_gammapar.f90:100"),
    _spec(
        "upbend",
        "upbend",
        [_Z, _N, _IRAD, _GAM, _UPB],
        "upbend",
        "input_gammapar.f90:101, :139-159 (keywords upbendc/upbende/upbendf = last axis 1/2/3)",
    ),
    _spec("fiso", "fiso", [_PARM1], -1.0, "input_gammapar.f90:102", "", "gammapar.f90 (T7)"),
    _spec("fisom", "fisom", [_PARM1], -1.0, "input_gammapar.f90:103", "", "gammapar.f90 (T7)"),
    _spec(
        "gamgam",
        "gamgam",
        [_Z, _N],
        0.0,
        "input_gammapar.f90:106",
        "eV",
        "resonance file or systematics (T2/T7)",
    ),
    _spec("gamgamadjust", "gamgamadjust", [_Z, _N], 1.0, "input_gammapar.f90:107"),
    _spec(
        "sfexp",
        "spectfacexp",
        [_Z, _N, _LEV],
        "sfexp",
        "input_gammapar.f90:109, :163-164, :482-489",
    ),
    _spec("sfth", "spectfacth", [_Z, _N], 1.0, "input_gammapar.f90:110, :162, :487"),
    _spec(
        "upbendadjust",
        "upbendadjust",
        [_Z, _N, _IRAD, _GAM, _UPB],
        1.0,
        "input_gammapar.f90:111 (keywords upbendcadjust/upbendeadjust/upbendfadjust)",
    ),
    _spec("levinger", "levinger", [], 6.5, "input_gammapar.f90:112"),
    # --- optical model (input_omppar.f90), one entry per particle type 0..6 ---
    _spec("rprime", "RprimeU", [], 0.0, "input_omppar.f90:125", "fm"),
    *(
        _spec(k, v, [_PAR0], d, f"input_omppar.f90:{ln}")
        for k, v, d, ln in (
            ("v1adjust", "v1adjust", 1.0, 126),
            ("v2adjust", "v2adjust", 1.0, 127),
            ("v3adjust", "v3adjust", 1.0, 128),
            ("v4adjust", "v4adjust", 1.0, 129),
            ("rvadjust", "rvadjust", 1.0, 130),
            ("avadjust", "avadjust", 1.0, 131),
            ("w1adjust", "w1adjust", 1.0, 132),
            ("w2adjust", "w2adjust", 1.0, 133),
            ("w3adjust", "w3adjust", 1.0, 134),
            ("w4adjust", "w4adjust", 1.0, 135),
            ("rwadjust", "rwadjust", "omp_link", 136),
            ("awadjust", "awadjust", "omp_link", 137),
            ("rvdadjust", "rvdadjust", "omp_link", 138),
            ("avdadjust", "avdadjust", "omp_link", 139),
            ("d1adjust", "d1adjust", 1.0, 140),
            ("d2adjust", "d2adjust", 1.0, 141),
            ("d3adjust", "d3adjust", 1.0, 142),
            ("rwdadjust", "rwdadjust", 1.0, 143),
            ("awdadjust", "awdadjust", 1.0, 144),
            ("vso1adjust", "vso1adjust", 1.0, 145),
            ("vso2adjust", "vso2adjust", 1.0, 146),
            ("rvsoadjust", "rvsoadjust", 1.0, 147),
            ("avsoadjust", "avsoadjust", 1.0, 148),
            ("wso1adjust", "wso1adjust", 1.0, 149),
            ("wso2adjust", "wso2adjust", 1.0, 150),
            ("rwsoadjust", "rwsoadjust", "omp_link", 151),
            ("awsoadjust", "awsoadjust", "omp_link", 152),
            ("rcadjust", "rcadjust", 1.0, 153),
            ("ejoin", "Ejoin", 200.0, 154),
            ("vinfadjust", "Vinfadjust", 1.0, 155),
        )
    ),  # fmt: skip
    _spec(
        "ompadjuste1", "ompadjustE1", [_PAR0, _OMPADJ, _RANGE], 0.0, "input_omppar.f90:157", "MeV"
    ),
    _spec(
        "ompadjuste2", "ompadjustE2", [_PAR0, _OMPADJ, _RANGE], 0.0, "input_omppar.f90:158", "MeV"
    ),
    _spec("ompadjustd", "ompadjustD", [_PAR0, _OMPADJ, _RANGE], 1.0, "input_omppar.f90:159"),
    _spec("ompadjusts", "ompadjusts", [_PAR0, _OMPADJ, _RANGE], 1.0, "input_omppar.f90:160"),
    _spec("lvadjust", "lvadjust", [], 1.0, "input_omppar.f90:163"),
    _spec("lwadjust", "lwadjust", [], 1.0, "input_omppar.f90:164"),
    _spec("lv1adjust", "lv1adjust", [], 1.0, "input_omppar.f90:165"),
    _spec("lw1adjust", "lw1adjust", [], 1.0, "input_omppar.f90:166"),
    _spec("lvsoadjust", "lvsoadjust", [], 1.0, "input_omppar.f90:167"),
    _spec("lwsoadjust", "lwsoadjust", [], 1.0, "input_omppar.f90:168"),
    _spec("aradialcor", "aradialcor", [], 1.0, "input_omppar.f90:169"),
    _spec("adepthcor", "adepthcor", [], 1.0, "input_omppar.f90:170"),
    # --- compound nucleus (input_compoundpar.f90) ---
    _spec("tres", "Tres", [], 293.16, "input_compoundpar.f90:71", "K"),
    _spec(
        "xsalphatherm",
        "xsalphatherm",
        [_ISOM],
        0.0,
        "input_compoundpar.f90:72",
        "mb",
        "thermal cross sections from structure/resonances (T2)",
    ),
    _spec(
        "xscaptherm",
        "xscaptherm",
        [_ISOM],
        0.0,
        "input_compoundpar.f90:73",
        "mb",
        "thermal cross sections from structure/resonances (T2)",
    ),
    _spec(
        "xsptherm",
        "xsptherm",
        [_ISOM],
        0.0,
        "input_compoundpar.f90:74",
        "mb",
        "thermal cross sections from structure/resonances (T2)",
    ),
    _spec("tjadjust", "TJadjust", [_Z, _N, _PARM1], 1.0, "input_compoundpar.f90:76"),
    # --- direct (input_directpar.f90) ---
    _spec("elwidth", "elwidth", [], 0.5, "input_directpar.f90:63", "MeV"),
    # --- fission (input_fissionpar.f90) ---
    _spec("bdamp", "bdamp", [_Z, _N, _BAR1], 0.01, "input_fissionpar.f90:104"),
    _spec("bdampadjust", "bdampadjust", [_Z, _N, _BAR1], 1.0, "input_fissionpar.f90:105"),
    _spec("betafiscor", "betafiscor", [_Z, _N], 1.0, "input_fissionpar.f90:106"),
    _spec("betafiscoradjust", "betafiscoradjust", [_Z, _N], 1.0, "input_fissionpar.f90:107"),
    _spec(
        "rmiufiscor",
        "rmiufiscor",
        [_Z, _N],
        -1.0,
        "input_fissionpar.f90:108",
        "",
        "fissionpar.f90 (T11)",
    ),
    _spec("rmiufiscoradjust", "rmiufiscoradjust", [_Z, _N], 1.0, "input_fissionpar.f90:109"),
    _spec("fisbaradjust", "fbaradjust", [_Z, _N, _BAR1], 1.0, "input_fissionpar.f90:110"),
    _spec(
        "fisbar",
        "fbarrier",
        [_Z, _N, _BAR1],
        0.0,
        "input_fissionpar.f90:111",
        "MeV",
        "barrier tables / systematics (T11)",
    ),
    _spec(
        "fishw",
        "fwidth",
        [_Z, _N, _BAR1],
        0.0,
        "input_fissionpar.f90:120",
        "MeV",
        "barrier tables / systematics (T11)",
    ),
    _spec("fishwadjust", "fwidthadjust", [_Z, _N, _BAR1], 1.0, "input_fissionpar.f90:121"),
    _spec(
        "vfiscor",
        "vfiscor",
        [_Z, _N],
        "vfiscor",
        "input_fissionpar.f90:126, :133-148",
        "",
        "-1 under fismodel 6 is resolved in fissionpar.f90 (T11)",
    ),
    _spec("vfiscoradjust", "vfiscoradjust", [_Z, _N], 1.0, "input_fissionpar.f90:127"),
    _spec("cnubar1", "Cnubar1", [], 1.0, "input_fissionpar.f90:128"),
    _spec("cnubar2", "Cnubar2", [], 1.0, "input_fissionpar.f90:129"),
    _spec("tmadjust", "Tmadjust", [], 1.0, "input_fissionpar.f90:130"),
    _spec("fsadjust", "Fsadjust", [], 1.0, "input_fissionpar.f90:131"),
    _spec("cbarrier", "Cbarrier", [], 1.0, "input_fissionpar.f90:132"),
    _spec("class2width", "widthc2", [_Z, _N, _BAR1], 0.2, "input_fissionpar.f90:157", "MeV"),
    # --- pre-equilibrium (input_preeqpar.f90) ---
    _spec("cbreak", "Cbreak", [_PAR0], "cbreak", "input_preeqpar.f90:90-91"),
    _spec("cknock", "Cknock", [_PAR0], 1.0, "input_preeqpar.f90:92"),
    _spec("cstrip", "Cstrip", [_PAR0], 1.0, "input_preeqpar.f90:93"),
    _spec("emsdmin", "Emsdmin", [], 0.0, "input_preeqpar.f90:94", "MeV"),
    _spec("esurf", "Esurf0", [], -1.0, "input_preeqpar.f90:95", "MeV", "preeqpar / exciton (T8)"),
    _spec(
        "g", "g", [_Z, _N], 0.0, "input_preeqpar.f90:96", "MeV^-1", "single-particle density (T8)"
    ),
    _spec("gadjust", "gadjust", [_Z, _N], 1.0, "input_preeqpar.f90:97"),
    _spec(
        "gn", "gn", [_Z, _N], 0.0, "input_preeqpar.f90:98", "MeV^-1", "single-particle density (T8)"
    ),
    _spec("gnadjust", "gnadjust", [_Z, _N], 1.0, "input_preeqpar.f90:99"),
    _spec(
        "gp",
        "gp",
        [_Z, _N],
        0.0,
        "input_preeqpar.f90:100",
        "MeV^-1",
        "single-particle density (T8)",
    ),
    _spec("gpadjust", "gpadjust", [_Z, _N], 1.0, "input_preeqpar.f90:101"),
    _spec("kph", "Kph", [], 15.0, "input_preeqpar.f90:102", "MeV"),
    _spec("m2constant", "M2constant", [], 1.0, "input_preeqpar.f90:103"),
    _spec("m2limit", "M2limit", [], 1.0, "input_preeqpar.f90:104"),
    _spec("m2shift", "M2shift", [], 1.0, "input_preeqpar.f90:105"),
    _spec("rgamma", "Rgamma", [], 2.0, "input_preeqpar.f90:106"),
    _spec("rnunu", "Rnunu", [], 1.5, "input_preeqpar.f90:107"),
    _spec("rnupi", "Rnupi", [], 1.0, "input_preeqpar.f90:108"),
    _spec("rpinu", "Rpinu", [], 1.0, "input_preeqpar.f90:109"),
    _spec("rpipi", "Rpipi", [], 1.0, "input_preeqpar.f90:110"),
    _spec("rspincutpreeq", "Rspincutpreeq", [], 1.0, "input_preeqpar.f90:111"),
    *(
        _spec(k.lower(), k, [], 1.0, f"input_preeqpar.f90:{ln}")
        for k, ln in (
            ("GMRadjustE", 112),
            ("GQRadjustE", 113),
            ("LEORadjustE", 114),
            ("HEORadjustE", 115),
            ("GMRadjustG", 116),
            ("GQRadjustG", 117),
            ("LEORadjustG", 118),
            ("HEORadjustG", 119),
            ("GMRadjustD", 120),
            ("GQRadjustD", 121),
            ("LEORadjustD", 122),
            ("HEORadjustD", 123),
        )
    ),  # fmt: skip
)

PARAM_SPECS: dict[str, ParamSpec] = {s.keyword: s for s in _SPECS}
assert len(PARAM_SPECS) == len(_SPECS), "duplicate Params keyword"


@dataclass
class Params:
    """Adjustable continuous parameters, float64 tensors keyed by lowercase TALYS keyword
    (contract §4.4). Shapes and index conventions are in `PARAM_SPECS[keyword]`; lookup is
    case-insensitive (`params["M2constant"]`). Call `requires_grad_` on the entries to fit.
    """

    values: dict[str, Tensor]

    def __getitem__(self, keyword: str) -> Tensor:
        return self.values[keyword.lower()]

    def __contains__(self, keyword: str) -> bool:
        return keyword.lower() in self.values

    def at(self, keyword: str, *index: int) -> Tensor:
        """Element at a Fortran index tuple, e.g. ``params.at("fiso", -1)``."""
        spec = PARAM_SPECS[keyword.lower()]
        if len(index) != len(spec.dims):
            raise IndexError(f"{keyword}: expected {len(spec.dims)} indices, got {len(index)}")
        pos = []
        for i, (lo, hi), o in zip(index, spec.dims, spec.offsets, strict=True):
            if not lo <= i <= hi:
                raise IndexError(f"{keyword}: index {i} outside Fortran bounds {lo}..{hi}")
            pos.append(i + o)
        return self.values[spec.keyword][tuple(pos)]

    def requires_grad_(self, keywords: list[str] | None = None) -> Params:
        for k in keywords if keywords is not None else list(self.values):
            self.values[k.lower()].requires_grad_(True)
        return self


def _fill(spec: ParamSpec, value: float, device) -> Tensor:
    return torch.full(spec.shape, float(value), dtype=DTYPE, device=device)


def _set_cells(t: Tensor, rows: list[list[float]]) -> Tensor:
    """`t[zix, nix] = rows[zix][nix]` for every (Zix, Nix) cell, every trailing index, in one
    write (MACSPEED: the per-cell tensor writes were most of `default_params`' cost)."""
    v = torch.tensor(rows, dtype=DTYPE, device=t.device)
    t[:] = v.reshape(v.shape + (1,) * (t.dim() - 2)).expand(t.shape)
    return t
#: UQ1 (Total Monte Carlo). A process-wide keyword perturbation: None (the default) or a callable
#: `(Z, A, options) -> {keyword: value}` in `default_params`'s `overrides` form, asked for the
#: call's OWN target. It is how a TALYS input file's keywords reach every consumer of `Params`
#: -- the whole dump-free run builds its `Params` in a dozen places, several of them for a
#: residual nucleus treated as a target -- without threading an argument through each. Explicit
#: `overrides` still win. Set it only in a process whose caches hold nothing built without it
#: (`physics.hf.tmc.install` in a freshly forked child).
TMC_OVERRIDES = None


def default_params(
    Z: int,
    A: int,
    options: Options,
    overrides: Mapping[str, object] | None = None,
    device: torch.device | str | None = None,
) -> Params:
    """Default values of every adjustable parameter (aadjust, wtable, rvadjust, ...) for the
    compound system of target (Z, A), resolved with `options` (which must be for the same target).

    `overrides` maps a lowercase keyword to a scalar (applied to every entry, TALYS's global
    form), to a full tensor of `PARAM_SPECS[k].shape`, or, for per-particle OMP and
    pre-equilibrium parameters, to ``{"n": 1.1}`` (TALYS's `rvadjust n 1.1`). They are applied
    before TALYS's post-loop resolution, so the links TALYS makes still follow: `rwadjust` takes
    `rvadjust` unless given (input_omppar.f90:632), `alphald` etc. take the global value
    (input_densitypar.f90:496-499), `ctable`/`ptable` take `cglobal`/`pglobal`.

    OSENGINE: if (Z, A) is in a region `omp.regional` carries a measured OMP correction for, that
    correction goes in **underneath** `overrides` -- through this same keyword path, so TALYS's
    links follow it exactly as they would for a hand-written `rvadjust n 0.96` card. It is the
    one default here that is not TALYS's own; `regional.disabled()` (or `INCOGNITA_OMP_REGION=0`)
    is how the port's fidelity measurements get TALYS's.

    TALYS: input_mass.f90:1 (input_mass), input_levels.f90:1 (input_levels),
    input_densitymodel.f90:1 (input_densitymodel), input_densitypar.f90:1 (input_densitypar),
    input_gammapar.f90:1 (input_gammapar), input_omppar.f90:1 (input_omppar),
    input_compoundpar.f90:1 (input_compoundpar), input_directpar.f90:1 (input_directpar),
    input_fissionpar.f90:1 (input_fissionpar), input_preeqpar.f90:1 (input_preeqpar)
    Test: tests/hf/test_defaults.py (parameters.dat from `partable y`)
    """
    if (options.Ztarget, options.Atarget) != (int(Z), int(A)):
        raise ValueError(
            f"options are for Z={options.Ztarget} A={options.Atarget}, not Z={Z} A={A}"
        )
    ov = regional.merged(int(Z), int(A), overrides)
    from physics.hf.input import fitlib  # BESTFIT: xsfit.f90 runs after the input is resolved

    fit = fitlib.active()
    if fit is not None and not fit.empty():
        if not ov and device is None and TMC_OVERRIDES is None:
            return fitlib.apply_params(
                Z, A, options,
                Params({k: t.clone() for k, t in _default_params_values(int(Z), int(A),
                                                                        options).items()}))
        return fitlib.apply_params(Z, A, options,
                                   Params(_default_params_build(Z, A, options, ov, device)))
    # UQ1: a TMC sample (`TMC_OVERRIDES`) is applied inside `_default_params_build` and keyed to
    # the run's target, which the shared caches below ignore (NATIVEX2 templates are shared
    # across targets), so a warmed worker would hand a sampled run the unsampled tensors. Build.
    if TMC_OVERRIDES is not None:
        return Params(_default_params_build(Z, A, options, ov, device))
    if not ov and device is None:
        # COREX: without overrides the result is a pure function of (Z, A, options); the tensors
        # are built once per key and every caller gets its own copies (callers may write them)
        base = _default_params_values(int(Z), int(A), options)
        return Params({k: t.clone() for k, t in base.items()})
    if ov is not None and overrides is None and device is None:
        # OSENGINE: a region member with no caller overrides is as pure a function of
        # (Z, A, options) as the line above, and every run of it pays the same ~16 ms build
        base = _region_params_values(int(Z), int(A), options)
        return Params({k: t.clone() for k, t in base.items()})
    return Params(_default_params_build(Z, A, options, ov, device))


def default_params_shared(Z: int, A: int, options: Options) -> Params:
    """`default_params(Z, A, options)` holding the cached tensors themselves, for a caller that
    only reads them and shares them onwards (NATIVEX2: `dens_reference._structure_of`, whose
    result is itself one object per run for every caller, built for each cascade nucleus; the
    ~160 copies per build were a third of its cost).

    TALYS: input_gammapar.f90:1 (input_gammapar) and the other input_*par routines, as
    `default_params`
    Test: tests/hf/test_defaults.py
    """
    if (options.Ztarget, options.Atarget) != (int(Z), int(A)):
        raise ValueError(
            f"options are for Z={options.Ztarget} A={options.Atarget}, not Z={Z} A={A}"
        )
    from physics.hf.input import fitlib

    if TMC_OVERRIDES is not None:  # UQ1: never from the target-blind caches (see default_params)
        p = Params(_default_params_build(Z, A, options, regional.overrides_for(int(Z), int(A)),
                                         None))
    elif regional.overrides_for(int(Z), int(A)) is not None:
        p = Params(dict(_region_params_values(int(Z), int(A), options)))
    else:
        p = Params(dict(_default_params_values(int(Z), int(A), options)))
    return fitlib.apply_params(Z, A, options, p)  # BESTFIT (clones only what it writes)


@lru_cache(maxsize=4)
def _region_params_values(Z: int, A: int, options: Options) -> dict[str, Tensor]:
    """`_default_params_values` for a target `omp.regional` holds a correction for (OSENGINE).

    No template sharing: the correction is a function of the target, which is exactly what the
    templates below are keyed to ignore. There are 16 such targets on the whole chart and a chart
    worker runs one at a time, so a small cache holds the run in front of it and nothing more.
    """
    return _default_params_build(Z, A, options, regional.overrides_for(Z, A), None)


@lru_cache(maxsize=16)
def _default_params_values(Z: int, A: int, options: Options) -> dict[str, Tensor]:
    # NATIVEX2 `struct`: the build reads the target only through `vfiscor` (Zinit, Ninit), the
    # parity of A (`sfexp`) and Ainit >= 105 (`upbend`); every other tensor is a function of the
    # remaining option values. So the tensors of the first build with those values are shared
    # by every later target that has them, and only `vfiscor` is made per target.
    # tests/hf/test_nx2_struct.py compares every tensor bitwise with a fresh build.
    key = (int(A) % 2, options.Ainit >= 105,
           tuple(v for k, v in vars(options).items() if k not in _TEMPLATE_FREE))
    tpl = _PARAMS_TEMPLATES.get(key)
    if tpl is None:
        tpl = _default_params_build(Z, A, options, None, None)
        if len(_PARAMS_TEMPLATES) >= 12:  # ~3.8 MB each
            _PARAMS_TEMPLATES.pop(next(iter(_PARAMS_TEMPLATES)))
        _PARAMS_TEMPLATES[key] = tpl
        return tpl
    out = dict(tpl)
    out["vfiscor"] = _vfiscor_tensor(PARAM_SPECS["vfiscor"], options.Zinit, options.Ninit,
                                     options.fismodel, None)
    return out


# The option fields `_default_params_build` never reads (the target is read only through Zinit,
# Ninit, Ainit and A, handled in the key above and in `vfiscor`), and the templates by those
# values: pure, no target in them, read-only like every `_default_params_values` result.
_TEMPLATE_FREE = frozenset({"Ztarget", "Atarget", "maxZ", "maxN"})
_PARAMS_TEMPLATES: dict[tuple, dict[str, Tensor]] = {}


def _vfiscor_tensor(s: ParamSpec, zinit: int, ninit: int, fismodel: int, device) -> Tensor:
    """`vfiscor` (input_fissionpar.f90:133-148) for the compound nucleus (zinit, ninit).

    TALYS: input_fissionpar.f90:1 (input_fissionpar)
    Test: tests/hf/test_defaults.py
    """
    t = _fill(s, 0.0, device)
    # COREX: the cell loop as grid operations (the same float64 arithmetic per cell)
    z = zinit - np.arange(NUMZ + 1)[:, None]
    n = ninit - np.arange(NUMN + 1)[None, :]
    vf0 = np.array([[0.83, 0.86], [0.91, 0.85]])[z % 2, n % 2]  # [(oz, on)]
    aact = np.clip(z + n, 225, 255)
    cells = np.full(vf0.shape, -1.0) if fismodel == 6 else vf0 - 0.005 * (aact - 240)
    return _set_cells(t, cells)


def _default_params_build(Z, A, options, overrides, device) -> dict[str, Tensor]:
    """`default_params`' tensors (COREX: its former body)."""
    ov = {str(k).lower(): v for k, v in (overrides or {}).items()}
    if TMC_OVERRIDES is not None:
        ov = {**{str(k).lower(): v for k, v in TMC_OVERRIDES(int(Z), int(A), options).items()},
              **ov}
    unknown = sorted(set(ov) - set(PARAM_SPECS))
    if unknown:
        raise KeyError(f"not a Params keyword: {unknown}")

    zinit, ninit, k0 = options.Zinit, options.Ninit, options.k0
    v: dict[str, Tensor] = {}
    builders = {}

    def given(k: str) -> bool:
        return k in ov

    # beta2 (input_mass.f90:60-69)
    def _beta2(s):
        t = _fill(s, 0.0, device)
        t[:, :, 1], t[:, :, 2], t[:, :, 3:] = 0.6, 0.8, 1.0
        return t

    # alphald/betald/gammashell1/Pshiftconstant (input_densitypar.f90:116-164)
    ld_table = {  # (ldmodel class, flagcol) -> (alphald, betald, gammashell1, Pshiftconstant)
        (1, True): (0.0207305, 0.229537, 0.473625, 0.0),
        (1, False): (0.0692559, 0.282769, 0.433090, 0.0),
        (2, True): (0.0381563, 0.105378, 0.546474, 0.743229),
        (2, False): (0.0722396, 0.195267, 0.410289, 0.173015),
        (3, True): (0.0357750, 0.135307, 0.699663, -0.149106),
        (3, False): (0.110575, 0.0313662, 0.648723, 1.13208),
    }
    ld_names = ("alphald", "betald", "gammashell1", "pshiftconstant")

    ld_cells: list = []  # COREX: the per-cell (alphald, betald, gammashell1, Pshiftconstant), once

    def _ld(s):
        col = ld_names.index(s.keyword)
        t = _fill(s, 0.0, device)
        if not ld_cells:
            for zix in range(NUMZ + 1):
                row = []
                for nix in range(NUMN + 1):
                    ldm, fc = options.ldmodel_of(zix, nix), options.flagcol_of(zix, nix)
                    cls = 1 if (ldm == 1 or ldm >= 4) else ldm
                    vals = ld_table[(cls, fc)]
                    if cls == 1 and options.flagcolldamp:  # :130-135
                        vals = (0.0666, 0.258, 0.459, 0.0)
                    row.append(vals)
                ld_cells.append(row)
        return _set_cells(t, [[cell[col] for cell in row] for row in ld_cells])

    def _rtransmom(s):
        t = _fill(s, 1.0, device)  # :196
        t[:, :, 1] = 0.6  # :199
        return t

    def _ufermi(s):
        t = _fill(s, 45.0, device)  # :203
        t[:, :, 0] = 30.0  # :200
        return t

    def _wtable(s):  # input_gammapar.f90:96, :113-138
        t = _fill(s, 1.0, device)
        if k0 <= 1 and options.flagglobalwtable and options.strength in (8, 9):
            from physics.hf.gamma import e1_width as _e1w
            tab8 = {(1, True): 1.052, (1, False): 1.076, (2, True): 0.942, (2, False): 0.943,
                    (3, True): 0.905, (3, False): 0.911, 4: 0.918, 5: 1.017, 6: 0.942}  # fmt: skip
            tab9 = {(1, True): 1.048, (1, False): 1.081, (2, True): 0.911, (2, False): 0.934,
                    (3, True): 0.884, (3, False): 0.919, 4: 0.921, 5: 1.021, 6: 0.936}  # fmt: skip
            tab = tab8 if options.strength == 8 else tab9
            rows = []
            for zix in range(NUMZ + 1):
                row = []
                for nix in range(NUMN + 1):
                    ldm = options.ldmodel_of(zix, nix)
                    key = (ldm, options.flagcol_of(zix, nix)) if ldm <= 3 else ldm
                    row.append(_e1w.constant(options.strength, tab[key]) if key in tab else 1.0)  # the fill above; INDEP_FIX: INCOGNITA_E1_WTABLE
                rows.append(row)
            t[:, :, 1, 1] = torch.tensor(rows, dtype=DTYPE, device=t.device)
        return t

    def _upbend(s):  # input_gammapar.f90:101, :139-159
        t = _fill(s, 0.0, device)
        if options.strengthM1 in (8, 10):
            if options.Ainit >= 105:
                t[:, :, 0, 1, 1], t[:, :, 0, 1, 3] = 1.0e-8, 0.0
            else:
                t[:, :, 0, 1, 1], t[:, :, 0, 1, 3] = 3.0e-8, 4.0
        if options.strengthM1 == 3:
            t[:, :, 0, 1, 1], t[:, :, 0, 1, 3] = 3.5e-8, 6.0
        t[:, :, 0, 1, 2] = 0.8
        if options.strength == 8:
            t[:, :, 1, 1, 1], t[:, :, 1, 1, 2] = 1.0e-10, 3.0
        return t

    def _sfexp(s):  # input_gammapar.f90:163-164; unset levels get sfexpall (:482-489)
        return _fill(s, 1.0 if int(A) % 2 != 0 else 0.347, device)

    def _vfiscor(s):  # input_fissionpar.f90:133-148
        return _vfiscor_tensor(s, zinit, ninit, options.fismodel, device)

    def _cbreak(s):  # input_preeqpar.f90:90-91
        return _fill(s, 0.0 if k0 == 6 else 1.0, device)

    builders.update(
        beta2=_beta2, ld_systematics=_ld, rtransmom=_rtransmom, ufermi=_ufermi, wtable=_wtable,
        upbend=_upbend, sfexp=_sfexp, vfiscor=_vfiscor, cbreak=_cbreak,
    )  # fmt: skip

    def _override(s: ParamSpec, t: Tensor) -> Tensor:
        val = ov[s.keyword]
        if isinstance(val, Mapping):  # {particle symbol or type index: value}, particle axes only
            if s.dims != (_PAR0,):
                raise ValueError(f"{s.keyword}: per-particle overrides need a particle axis")
            t = t.clone()
            for part, x in val.items():
                i = PARSYM.index(part) if isinstance(part, str) else int(part)
                # DIFFPARAM: `float(x)` here dropped a requires_grad override off the graph, so
                # `rvadjust n <tensor>` (TALYS's own per-particle form) differentiated to zero.
                idx = torch.tensor([i], device=t.device)
                t = t.index_put((idx,), torch.as_tensor(x, dtype=DTYPE, device=t.device
                                                        ).reshape(1))
            return t
        if isinstance(val, Tensor):
            if val.dim() == 0:
                # TALYS's global form (`aadjust 1.05` applies to every nuclide), on the graph.
                return val.to(dtype=DTYPE, device=t.device).expand(s.shape).clone()
            if tuple(val.shape) != s.shape:
                raise ValueError(
                    f"{s.keyword}: tensor shape {tuple(val.shape)} is neither () nor {s.shape}")
            return val.to(dtype=DTYPE, device=t.device).clone()
        return torch.full_like(t, float(val))

    # pass 1: stage defaults and explicit values (links resolved in pass 2)
    for s in _SPECS:
        if isinstance(s.default, str) and s.default in builders:
            t = builders[s.default](s)
        elif isinstance(s.default, str):  # "cglobal", "pglobal", "omp_link": filled in pass 2
            t = _fill(s, -1.0, device)
        else:
            t = _fill(s, s.default, device)
        if given(s.keyword) and s.keyword not in ld_names:
            t = _override(s, t)
        v[s.keyword] = t

    # pass 2: TALYS's post-loop links
    for k in ("ctable", "ptable"):  # input_densitypar.f90:211-212 (ctable = cglobal)
        if not given(k):
            g = "cglobal" if k == "ctable" else "pglobal"
            # DIFFPARAM: `.expand`, not `torch.full(..., float(...))`, so an overridden
            # `cglobal`/`pglobal` still reaches `ctable`/`ptable` on the graph.
            v[k] = v[g].reshape(()).to(dtype=DTYPE).expand(PARAM_SPECS[k].shape).clone()
    for k in ld_names:  # input_densitypar.f90:496-499 (the keyword sets the *all value)
        if given(k):
            v[k] = _override(PARAM_SPECS[k], v[k])
    for t_ in range(NUMPAR + 1):  # input_omppar.f90:632-648
        if (t_ == 3 and options.deuteronomp >= 2) or (t_ == 6 and options.alphaomp >= 2):
            src = {"rwadjust": None, "awadjust": None, "rvdadjust": None,
                   "avdadjust": None, "rwsoadjust": None, "awsoadjust": None}  # fmt: skip
        else:
            src = {
                "rwadjust": "rvadjust", "awadjust": "avadjust", "rvdadjust": "rwdadjust",
                "avdadjust": "awdadjust", "rwsoadjust": "rvsoadjust", "awsoadjust": "avsoadjust",
            }  # fmt: skip
        for dst, frm in src.items():
            if given(dst) and float(v[dst][t_]) != -1.0:
                continue
            v[dst][t_] = 1.0 if frm is None else v[frm][t_]
    return v


# ---------------------------------------------------------------------------------------------
# Reading TALYS's own echo of its resolved defaults (the validation reference for this module)
# ---------------------------------------------------------------------------------------------

_IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def parse_talys_echo(text: str) -> dict[str, str]:
    """The "USER INPUT FILE + DEFAULTS" block of talys.out as {keyword: printed value}.

    Keywords keep TALYS's spelling (`maxZrp`, `ldmodelCN`); `maxlevelsbin` becomes
    `"maxlevelsbin <particle>"`. The printed value is a string exactly as written.

    TALYS: inputout.f90:1 (inputout)
    Test: tests/hf/test_defaults.py
    """
    start = text.find("USER INPUT FILE + DEFAULTS")
    if start < 0:
        raise ValueError("no 'USER INPUT FILE + DEFAULTS' block in this talys.out")
    out: dict[str, str] = {}
    for line in text[start:].splitlines()[1:]:
        if line.startswith(" ####"):
            break
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("Keyword"):
            continue
        toks = [(m.start(), m.group()) for m in re.finditer(r"\S+", line)]
        key, v0 = toks[0][1], 1
        if key == "maxlevelsbin" and len(toks) > 1:
            key, v0 = f"{key} {toks[1][1]}", 2
        # the Fortran variable column starts near column 27; long names start a few earlier
        var = next(
            (i for i in range(v0, len(toks))
             if toks[i][0] >= 22 and len(toks[i][1]) >= 2 and _IDENT.fullmatch(toks[i][1])),
            None,
        )  # fmt: skip
        if var is None:
            continue
        out[key] = line[toks[v0][0] : toks[var][0]].strip() if var > v0 else ""
    return out


def parse_partable(text: str) -> list[tuple[str, int, int, float, str]]:
    """parameters.dat (`partable y`) as (keyword, Z, A, value, qualifier) rows.

    `qualifier` is what follows the value: a barrier index, or `E1`/`M1`, or empty.

    TALYS: partable.f90:1 (partable)
    Test: tests/hf/test_defaults.py
    """
    rows = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            z, a, val = int(parts[1]), int(parts[2]), float(parts[3])
        except ValueError:
            continue
        rows.append((parts[0], z, a, val, " ".join(parts[4:])))
    return rows


def parse_partable_general(text: str) -> list[tuple[str, str | None, str]]:
    """The "## General parameters" block of parameters.dat (written by finalout at the end of a
    run with `reaction y`) as (keyword, particle symbol or None, printed value) rows.

    TALYS: finalout.f90:1 (finalout)
    Test: tests/hf/test_defaults.py
    """
    start = text.find("## General parameters")
    if start < 0:
        return []
    rows = []
    for line in text[start:].splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 2:
            rows.append((parts[0], None, parts[1]))
        elif len(parts) == 3 and parts[1] in PARSYM:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def _yes(b: bool) -> str:
    return "y" if b else "n"


def echo_expected(options: Options, e_inc_mev: float | None = None) -> dict[str, str | float]:
    """What TALYS's defaults echo should print for these options, keyed like
    :func:`parse_talys_echo`. Floats are returned as floats (compare with a tolerance), all else
    as the exact printed string. Keys whose printed form depends on the incident-energy grid
    (`widthfluc`, `urr`, `preequilibrium`, `multipreeq`) are included only when `e_inc_mev` is
    given, as the y/n flag TALYS prints for a single incident energy.

    TALYS: inputout.f90:1 (inputout)
    Test: tests/hf/test_defaults.py
    """
    o = options
    e: dict[str, str | float] = {
        "maxz": str(o.maxZ), "maxn": str(o.maxN), "bins": str(o.nbins0),
        "equidistant": _yes(o.flagequi), "equispec": _yes(o.flagequispec),
        "popmev": _yes(o.flagpopMeV), "segment": str(o.segment),
        "maxlevelstar": str(o.nlevmax), "maxlevelsres": str(o.nlevmaxres),
        "ltarget": str(o.Ltarget), "isomer": o.isomer_s, "transpower": str(o.transpower),
        "transeps": o.transeps, "xseps": o.xseps_mb, "popeps": o.popeps_mb, "Rfiseps": o.Rfiseps,
        "angles": str(o.nangle), "anglescont": str(o.nanglecont),
        "anglesrec": str(o.nanglerec), "maxenrec": str(o.maxenrec),
        "channels": _yes(o.flagchannels), "maxchannel": str(o.maxchannel),
        "micro": _yes(o.flagmicro), "best": _yes(o.flagbest), "bestbranch": _yes(o.flagbestbr),
        "bestend": _yes(o.flagbestend), "relativistic": _yes(o.flagrel),
        "recoil": _yes(o.flagrecoil), "labddx": _yes(o.flaglabddx),
        "recoilaverage": _yes(o.flagrecoilav), "channelenergy": _yes(o.flagEchannel),
        "reaction": _yes(o.flagreaction), "fit": _yes(o.flagfit),
        "ngfit": _yes(o.flagngfit), "nffit": _yes(o.flagnffit), "nnfit": _yes(o.flagnnfit),
        "nafit": _yes(o.flagnafit), "ndfit": _yes(o.flagndfit), "pnfit": _yes(o.flagpnfit),
        "dnfit": _yes(o.flagdnfit), "gnfit": _yes(o.flaggnfit), "anfit": _yes(o.flaganfit),
        "gamgamfit": _yes(o.flaggamgamfit), "macsfit": _yes(o.flagmacsfit),
        "astro": _yes(o.flagastro), "astrogs": _yes(o.flagastrogs),
        "astroex": _yes(o.flagastroex), "nonthermlev": str(o.nonthermlev),
        "massmodel": str(o.massmodel), "expmass": _yes(o.flagexpmass),
        "disctable": str(o.disctable), "production": _yes(o.flagprod),
        "outfy": _yes(o.flagoutfy), "gefran": str(o.gefran), "Estop": o.Estop_mev,
        "rpevap": _yes(o.flagrpevap), "legacy": _yes(o.flaglegacy),
        "maxZrp": str(o.maxZrp), "maxNrp": str(o.maxNrp),
        "localomp": _yes(o.flaglocalomp), "globaldisp": _yes(o.flagglobaldisp),
        "globalfermi": _yes(o.flagglobalfermi), "dispersion": _yes(o.flagdisp),
        "jlmomp": _yes(o.flagjlm), "pruitt": o.pruitt, "pruittset": str(o.pruittset),
        "riplomp": _yes(o.flagriplomp), "riplrisk": _yes(o.flagriplrisk),
        "optmodall": _yes(o.flagompall), "incadjust": _yes(o.flagincadj),
        "omponly": _yes(o.flagomponly), "autorot": _yes(o.flagautorot),
        "spherical": _yes(o.flagspher), "soukho": _yes(o.flagsoukho),
        "coulomb": _yes(o.flagcoulomb), "statepot": _yes(o.flagstate),
        "maxband": str(o.maxband), "maxrot": str(o.maxrot), "core": str(o.core),
        "ecissave": _yes(o.flagecissave), "eciscalc": _yes(o.flageciscalc),
        "inccalc": _yes(o.flaginccalc), "endfecis": _yes(o.flagendfecis),
        "radialmodel": str(o.radialmodel), "jlmmode": str(o.jlmmode),
        "alphaomp": str(o.alphaomp), "deuteronomp": str(o.deuteronomp),
        "ecisstep": o.ecisstep_fm, "widthmode": str(o.wmode), "WFCfactor": str(o.WFCfactor),
        "compound": _yes(o.flagcomp), "fullhf": _yes(o.flagfullhf),
        "eciscompound": _yes(o.flageciscomp), "cpang": _yes(o.flagcpang),
        "urrnjoy": _yes(o.flagurrnjoy), "lurr": str(o.lurr), "gammax": str(o.gammax),
        "strength": str(o.strength), "strengthM1": str(o.strengthM1),
        "pseudoresonances": _yes(o.flagpseudores), "electronconv": _yes(o.flagelectron),
        "racap": _yes(o.flagracap), "ldmodelracap": str(o.ldmodelracap),
        "upbend": _yes(o.flagupbend), "psfglobal": _yes(o.flagpsfglobal),
        "globalwtable": _yes(o.flagglobalwtable), "strengthjp": _yes(o.flagstrengthjp),
        "gnorm": _yes(o.flaggnorm), "preeqmode": str(o.preeqmode),
        "mpreeqmode": str(o.mpreeqmode), "breakupmodel": str(o.breakupmodel),
        "phmodel": str(o.phmodel), "pairmodel": str(o.pairmodel),
        "preeqspin": str(o.pespinmodel), "giantresonance": _yes(o.flaggiant0),
        "preeqsurface": _yes(o.flagsurface), "preeqcomplex": _yes(o.flagpecomp),
        "twocomponent": _yes(o.flag2comp), "ecisdwba": _yes(o.flagecisdwba),
        "onestep": _yes(o.flagonestep), "ldmodel": str(o.ldmodelall),
        "ldmodelCN": str(o.ldmodelCN), "shellmodel": str(o.shellmodel),
        "kvibmodel": str(o.kvibmodel), "spincutmodel": str(o.spincutmodel),
        "ldglobal": _yes(o.flagldglobal), "asys": _yes(o.flagasys),
        "parity": _yes(o.flagparity), "colenhance": _yes(o.flagcolall),
        "ctmglobal": _yes(o.flagctmglob), "gshell": _yes(o.flaggshell),
        "colldamp": _yes(o.flagcolldamp), "fission": _yes(o.flagfission),
        "fismodel": str(o.fismodel), "fismodelalt": str(o.fismodelalt),
        "hbstate": _yes(o.flaghbstate), "class2": _yes(o.flagclass2),
        "fispartdamp": _yes(o.flagfispartdamp), "sffactor": _yes(o.flagsffactor),
        "massdis": _yes(o.flagmassdis), "ffevaporation": _yes(o.flagffevap),
        "fisfeed": _yes(o.flagfisfeed), "fymodel": str(o.fymodel), "ffmodel": str(o.ffmodel),
        "pfnsmodel": str(o.pfnsmodel), "ffspin": _yes(o.flagffspin),
        "outtransenergy": _yes(o.flagtransen), "outlegendre": _yes(o.flaglegendre),
        "endf": _yes(o.flagendf), "endfdetail": _yes(o.flagendfdet),
    }  # fmt: skip
    for t, sym in enumerate(PARSYM):
        e[f"maxlevelsbin {sym}"] = str(o.nlevbin[t])
    if o.eninclow_mev != 0.0:  # 0 prints the grid.f90 resolution, which needs D0
        e["elow"] = o.eninclow_mev
    if e_inc_mev is not None:
        f = energy_flags(o, e_inc_mev)
        e["widthfluc"] = _yes(f["flagwidth"])
        e["urr"] = _yes(f["flagurr"])
        e["preequilibrium"] = _yes(f["flagpreeq"])
        e["multipreeq"] = _yes(f["flagmulpre"])
    return e


# echo keys this module deliberately does not model: identification, file names, the TALYS
# build string, and output switches (contract §8)
ECHO_NOT_MODELLED = frozenset({
    "projectile", "element", "mass", "energy", "ejectiles", "user", "source", "format",
    "sysreaction", "rotational", "partable", "adddiscrete", "addelastic", "components", "sacs",
    "outmain", "outbasic", "outall", "outpopulation", "outcheck", "outlevels", "outdensity",
    "outomp", "outkd", "outdirect", "outinverse", "outdecay", "outecis", "outgamma",
    "outpreequilibrium", "outfission", "outdiscrete", "outspectra", "outbinspectra", "resonance",
    "group", "outangle", "ddxmode", "outdwba", "outgamdis", "outexcitation", "filedensity",
    "filepsf", "filechannels", "fileelastic", "filefission", "filegamdis", "filerecoil",
    "fileresidual", "filetotal", "block", "blockddx", "blockspectra", "blockangle",
    "blockdirect", "blockbin", "blocklevels", "blockomp", "blockpreeq", "blockastro",
    "blockyield", "blockZA",
})  # fmt: skip


def compare_echo(
    expected: Mapping[str, str | float], echo: Mapping[str, str], rtol: float = 5e-3
) -> dict[str, tuple]:
    """Mismatches between :func:`echo_expected` and a parsed echo, {key: (expected, printed)}.
    Floats compare with `rtol` (TALYS prints es9.2 / f8.3). Keys missing from the echo count.

    TALYS: inputout.f90:1 (inputout)
    Test: tests/hf/test_defaults.py
    """
    bad = {}
    for k, want in expected.items():
        if k not in echo:
            bad[k] = (want, None)
            continue
        got = echo[k]
        if isinstance(want, float):
            try:
                g = float(got)
            except ValueError:
                bad[k] = (want, got)
                continue
            if not math.isclose(g, want, rel_tol=rtol, abs_tol=1e-30):
                bad[k] = (want, got)
        elif got != want:
            bad[k] = (want, got)
    return bad
