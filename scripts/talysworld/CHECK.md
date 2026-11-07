# Check: one engine job per energy against library v0.2.1 (2026-11-07)

**Question.** Run the production engine one incident energy per job, with library-default settings, on the library's own
energy grid. Does it reproduce the published library v0.2.1 curves? Or does the grid dependence found on 11-06 show up?

**Answer.**
- **13 of the 20 nuclides are reproduced.** Capture matches to ≤ 3e-4 below 2 MeV and to ~1e-10 typically, and
  (n,p) and (n,2n) match to ≤ 1.4e-4. This includes all six named nuclides.
- **The other 7 nuclides show the grid dependence.** These are the heavy proton-rich and very neutron-deficient nuclei
  from the v0.2.2 mismatch list. For them the one-energy jobs differ from the library by up to ×61 in capture and ×43 in
  (n,p).
- **The difference is not confined to 1 keV.** It is largest from 1 keV to 100 keV, still 5-40 % at 0.1-1 MeV, and
  goes to ≤ 2 % at 12-20 MeV.
- **The one-energy value equals the short-grid (2 eV - 1 keV) run.** At 1 keV it is the same as v0.2.2's short-grid
  value to 1e-11, and below 1 keV too. So the 11-06 mismatch is reproduced exactly: one energy per job behaves like a
  short grid, and the library's 134-point run is the odd one out for these nuclei.

## Set-up

- **Tool:** `scripts/talysworld/` (service `server.py`, job `engine_job.py`, this check `check.py`).
  - Each point is one engine process with a one-point energy grid `[E]`.
  - At most 3 processes ran at once, at nice 10, on laptop WSL.
- **Engine:** engine-20261022-3 = nucleus 16606b356d6e (laptop install `~/fastgate_data/eng/16606b356d6e`, its own venv).
  - Environment, runner, deck and inputs are those of the v0.2 runs: `~/libv02/inputs` and the run.sh environment, with
    worker.py -> prodrun -> pprun, `fewres off`, `pewindow g`.
  - Each nucleus was composed as the library composed it: P, A(rotor), ACTJS A(rotor), or JS(P,A) via
    `physics.hf.jointcap.combine`. "[FEW->mean]" was treated as its base composition, as v0.2.2's collect step does.
  - (n,p), (n,2n) and (n,α) are taken from the P arm (the A arm for rotor compositions), as the v0.2 build does.
- **Energies:** the library grid, 64 points from 1 keV to 20 MeV. Three of v0.2.2's points below 1 keV were added:
  10.49, 126.0 and 660.8 eV. In total 20 × 67 = 1,340 jobs, about 45 min wall time, with 0 failed jobs.
- **Library:** `library/v0.2.1/capture_v021.parquet` and `channels_v021.parquet`.
  - For grid points from 1 keV up, v0.2.1 capture is v0.2's.
  - None of the 20 is ANCHORED, so no anchor factor was removed. None has floor-repaired points.
- **Below 1 keV** two references were used:
  - v0.2.2's engine values (`library/v0.2.2/below1keV_engine_v022.parquet`, libv022 worktree, unpushed). These come
    from the 16-point 2 eV - 1 keV short grid, and from the long grid only for its 14 control nuclei.
  - v0.2.1's 1/v extension from 1 keV.
- **Sample, 20 nuclides:**
  - O-16, Na-23, Ca-40, Fe-56, Ni-62, Zr-90, Sn-120, Ba-138, Gd-158, Au-197, Pb-208, Th-232, U-238.
  - From the v0.2.2 short-grid mismatch list (|short-grid / v0.2 − 1| at 1 keV): I-109 (+31.2), Pa-200 (+4.78),
    Ra-215 (+3.72), Fr-190 (+3.51), Bi-178 (+2.00), Tl-174 (+1.91) and Te-104 (−0.82).
- **Relative difference:** one-job / library − 1, per point.
  - Values at or below the engine's output floor (1e-7 mb) count as zero. Points where both are zero count as 0.
  - Points where exactly one is zero are counted separately. They cannot be expressed as a relative difference.

## Per channel (64 library-grid points × 20 nuclides = 1,280 points per channel)

| channel | median abs. rel. diff | max | where the max is | points > 1e-6 | points > 1 % | one zero, other not |
|---|---|---|---|---|---|---|
| capture (n,γ) | 6.9e-11 | 60.8 (×61.8) | I-109, 19.8 keV | 550 | 393 | 0 |
| (n,p) | 0 | 42.1 (×43) | Te-104, 95.5 keV | 412 | 375 | 0 |
| (n,2n) | 0 | 0.057 | Pa-200, 10.7 MeV | 45 | 3 | 0 |
| (n,α) | 0 | 1.28 | Te-104, 14.6 MeV | 431 | 401 | 50 |
| total, elastic, fission | — | — | not in the library (engine values are in the tool's CSV) | | | |

Split by nuclide group:

| group | channel | median | max |
|---|---|---|---|
| 13 reproduced nuclides | capture | 5.4e-13 | 1.2e-2 (Ca-40, 20 MeV; ≤ 3.3e-4 below 2 MeV) |
| | (n,p) | 0 | 4.3e-5 |
| | (n,2n) | 0 | 1.4e-4 |
| | (n,α) | 0 | 0.98 (Pb-208, U-238, Th-232 near threshold, values 1e-5 to 2 mb) |
| 7 mismatch-list nuclides | capture | 0.24 | 60.8 |
| | (n,p) | 0.13 | 42.1 |
| | (n,2n) | 0 | 0.057 |
| | (n,α) | 0.98 | 1.28 |

## Per nuclide: max abs. rel. diff per channel, and 1 keV

| nuclide | composition | capture | (n,p) | (n,2n) | (n,α) | one job vs library at 1 keV | v0.2.2 short grid vs library at 1 keV |
|---|---|---|---|---|---|---|---|
| O-16 | P | 1.9e-5 | 0 | 0 | 0 | −2e-16 | −2e-16 |
| Na-23 | P | ~0 | 0 | 0 | 0 | 4e-13 | 3e-13 |
| Ca-40 | JS(P,A) | 1.2e-2 | 4.3e-5 | 0 | 7e-6 | 2e-12 | 1e-12 |
| Fe-56 | JS(P,A) | ~0 | 0 | 0 | 0 | −6e-14 | 7e-15 |
| Ni-62 | JS(P,A) | ~0 | 0 | 0 | 0 | 2e-13 | 2e-14 |
| Zr-90 | JS(P,A) | ~0 | 0 | 0 | 0 | 3e-13 | 3e-13 |
| Sn-120 | JS(P,A) | ~0 | 0 | 0 | 0 | 2e-13 | 1e-12 |
| Ba-138 | JS(P,A) | ~0 | 0 | 0 | 0 | 8e-12 | 8e-12 |
| Gd-158 | A(rotor) | ~0 | 0 | 0 | 0 | 5e-13 | 5e-13 |
| Au-197 | JS(P,A) | ~0 | 0 | 3.9e-5 | 0.036 | 2e-13 | 3e-14 |
| Pb-208 | JS(P,A) | 3e-6 | 5e-6 | 1.4e-4 | 0.98 (+1 zero) | 6e-11 | 1e-14 |
| Th-232 | ACTJS A(rotor) | 1.7e-5 | 0 | 1.1e-5 | 0.96 (+2 zero) | 2e-13 | 5e-14 |
| U-238 | ACTJS A(rotor) | 2.0e-5 | 0 | 1.3e-4 | 0.98 (+3 zero) | −2.6e-6 | 0 |
| **Te-104** | P | **1.56** | **42.1** | 4.5e-3 | 1.28 | **−0.819** | −0.818 |
| **I-109** | P | **60.8** | **31.6** | 5.1e-3 | 0.96 | **+31.16** | +31.16 |
| **Tl-174** | P | **1.91** | **2.23** | 0.027 | 0.99 | **+1.911** | +1.911 |
| **Bi-178** | P | **2.63** | **21.8** | 7.8e-4 | 1.00 | **+2.000** | +2.000 |
| **Fr-190** | P | **3.51** | **5.75** | 9.6e-3 | 1.00 | **+3.510** | +3.510 |
| **Ra-215** | P | **3.72** | 0.030 | 3.4e-3 | 1.00 (+44 zero) | **+3.721** | +3.721 |
| **Pa-200** | P | **4.78** | **5.96** | 0.057 | 1.00 | **+4.780** | +4.780 |

"~0" means below 1e-9.

## Where the differences sit in energy

Max abs. rel. diff over capture, (n,p), (n,2n) and (n,α), and the nuclides with any point above 1e-6:

| energy band | max | nuclides > 1e-6 |
|---|---|---|
| 1 keV (first grid point) | 31.2 | the 7 mismatch nuclides + U-238 (2.6e-6) |
| 1-10 keV | 48.3 | the 7 + Th-232, U-238 |
| 10-100 keV | 60.8 | the 7 + Th-232, U-238 |
| 0.1-1 MeV | 25.7 | the 7 + Ca-40, Th-232, U-238 |
| 1-5 MeV | 3.6 | the 7 + Ca-40, O-16 |
| 5-20 MeV | 1.28 | the 7 + Ca-40, O-16, Au-197, Pb-208, Th-232, U-238 |

The 7 mismatch nuclides, capture, median abs. rel. diff per band:

| nuclide | 1 keV | 1-10 keV | 10-100 keV | 0.1-1 MeV | 1-5 MeV | 5-20 MeV |
|---|---|---|---|---|---|---|
| I-109 | 31.2 | 39.8 | 5.09 | 0.20 | 0.051 | 0.000 |
| Pa-200 | 4.78 | 0.94 | 0.21 | 0.085 | 0.057 | 0.004 |
| Ra-215 | 3.72 | 3.19 | 2.41 | 2.69 | 3.16 | 0.000 |
| Fr-190 | 3.51 | 0.78 | 0.16 | 0.040 | 0.015 | 0.001 |
| Bi-178 | 2.00 | 2.01 | 1.03 | 0.18 | 0.046 | 0.001 |
| Tl-174 | 1.91 | 0.62 | 0.17 | 0.062 | 0.038 | 0.000 |
| Te-104 | 0.82 | 0.82 | 0.56 | 0.58 | 0.033 | 0.016 |

From 12.5 to 20 MeV their capture agrees to ≤ 0.1 %, except Pa-200 at 20 MeV (1.0 %) and Te-104 (1.2-2.1 %). It is not
exact, even at 20 MeV, the library grid's top energy.

**Below 1 keV** (60 points: 20 nuclides × 10.49, 126.0 and 660.8 eV):

| comparison | median abs. rel. diff | max |
|---|---|---|
| one job vs v0.2.2 engine values (short grid; long grid for the 14 control nuclei) | 1.4e-13 | 3.5e-3 (Te-104, the same −0.35 % at all three energies) |
| one job vs v0.2.1's 1/v extension from 1 keV | 1.45 | 27.2 (I-109, 660.8 eV) |

The engine's own capture rises much faster than 1/v below 1 keV, by ×2-8 at 10 eV for most nuclei. v0.2.2 already uses
the engine below 1 keV, for that reason.

## Reading

1. **For most nuclei the engine has no grid dependence on this grid.** 13 of 20 are reproduced point by point, mostly
   bit-for-bit (90 % of all compared points of these nuclides are equal to < 1e-9). That includes Fe-56, Au-197, U-238,
   Zr-90, Sn-120 and Pb-208. The one-energy tool is a faithful way to run the library's engine.
2. **The 11-06 mismatch is real, and it is not a 1 keV effect.** For the nuclei on the v0.2.2 list:
   - the one-energy result at 1 keV equals the short-grid result exactly (to 1e-11);
   - the v0.2 library value differs from both, by the same factors as on 11-06;
   - the difference covers the whole keV range and fades towards 20 MeV.

   So it is the 134-point production run that comes out differently for these nuclei. A set-up that depends on the
   highest incident energy, or on the grid as a whole, is consistent with this: agreement improves as the job's energy
   approaches the production grid's top.

   The library curves of these nuclei (all EXTRAPOLATED, P composition, proton-rich or neutron-deficient) therefore
   depend on the run's grid. They are not a property of the nucleus alone. The one-energy value is the grid-independent
   reference; which value is "right" is an engine question.

   In this sample, (n,p) moves with capture (up to ×43). These nuclei have open proton channels at keV energies.
3. **Small MeV-region differences on otherwise reproduced nuclei.** These are grid dependence on a smaller scale:
   - Ca-40 capture: −0.05 % at 2.6 MeV rising to −1.2 % at 20 MeV.
   - (n,α) on Pb-208, Th-232 and U-238: −50 to −98 % near the threshold, where the values are 1e-6 to 2 mb. It is still
     −65 % at 17 MeV on U-238 (1.37 vs 0.47 mb).
   - Au-197 (n,α): +3.6 % at 17 MeV.
   - Three to 44 (n,α) points are zero in the one-energy job but nonzero in the library: Ra-215 has 44, the actinides
     and Pb-208 a few each.
   - (n,2n) is reproduced to ≤ 1.4e-4 (≤ 5.7 % on the mismatch nuclides).
4. **Te-104 below 1 keV.** It differs from v0.2.2's short-grid values by a constant −0.35 %. It does not differ at 1 keV
   (both −0.818 against the library). Not chased.

## Files

- `check_points.csv`: every compared point, with columns nuclide, channel, e_ev, library_mb, onejob_mb and rel (5.5k
  rows, ~200 kB). The channels are `capture`, `np`, `n2n`, `na`, `capture<1keV vs v0.2.2 engine` and
  `capture<1keV vs v0.2.1 1/v`.
- `check_nuclides.csv`: per nuclide, the tier, composition, 1 keV values, and the one-job and short-grid differences at
  1 keV.
- `check_summary.json`: the numbers above.
- Rerun:
  1. Start the service: `wsl -e python3 scripts/talysworld/server.py`.
  2. In laptop WSL, run `python3 scripts/talysworld/check.py run`, then `python3 scripts/talysworld/check.py analyze`.
  3. Results are cached under `~/talysworld_data/cache`, so a rerun of the analysis is instant.
