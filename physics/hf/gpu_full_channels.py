"""channels.f90's exclusive channels on the (nuclide, energy) batch axis, streamed behind
`gpu_full_cascade`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: GPUFULL. No physics of its own: `emission.channels.exclusive_channels` rearranged.

TALYS routines computed here:
    channels.f90:1 (channels)

**What channels.f90 computes.** For each channel nucleus (Zix, Nix) and each exclusive channel
(i_n, ip, id, it, ih, ia) reaching it, the channel's population per excitation bin `xsexcl` is the
sum over ejectile types t of its source channel's `xsexcl` (the same channel less one particle t,
at the mother nucleus) contracted with `feedexcl(t) / popexcl`, plus the initial compound
nucleus's binary row, plus the photon recurrence (the channel itself one bin higher), solved as
a unit upper triangular system. The channel cross section is its ground state plus isomers.

**Three rearrangements, none of them numbers.**

* Streaming. Every source of a nucleus is at a nucleus the cascade decayed earlier, so a
  source's contraction is formed when the cascade has the mother's tables and the channels at
  the mother, and the tables are freed (`contribute`). A contraction is kept per (channel,
  source type) because whether the source is FOUND is not known yet (next point).
* The index give-back. channels.f90 hands a channel's index back when its cross section is under
  `xseps`, it has more than one particle and it is not in `chanopen`; the next channel takes the
  slot, so a given-back channel is never found as a source again. That is all the index does to
  a number: a source is found iff it was not given back. `chanopen` persists across the
  incident energies of a run (strucinitial.f90), so validity at energy i needs `opened` at the
  energies before it: the cumulative OR over the energy axis per nuclide, with what earlier
  batches opened carried in `chan_state`. Validity is formed when a whole level (every nucleus
  with the same number of nucleons removed) is done, which is before any channel that reads it.
* `Qexcl` is formed from the first found source, as channels.f90:283-318 does, and read only for
  the non-threshold floor (channels.f90:435-445).

**Stacked channels (GPU3).** Every channel of one channel nucleus is a column of one tensor
((runs, channels, rows) for `xsexcl`, (runs, channels) for `qexcl`, `xs`, `opened`, `valid`), and
the pending source contractions of a nucleus are one (runs, pairs, rows) tensor, a pair being a
(channel, ejectile type) whose source channel exists at the mother nucleus. The per-channel Python
loop is then a loop over the seven ejectile types, and the photon recurrence of all channels is
one triangular solve with a matrix right-hand side. The arithmetic per cell is unchanged; sums of
the pending sources run in another order (last bits). A nucleus's `xsexcl` is read only by
contractions made while its own level decays, so it is freed when that level's validity is formed.

Test: GPUFULL / tests/hf/test_gpu_full.py
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor

F64 = torch.float64
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)


def channel_code(k: tuple[int, ...]) -> str:
    return f"xs{100000 * k[0] + 10000 * k[1] + 1000 * k[2] + 100 * k[3] + 10 * k[4] + k[5]:06d}"


class ChannelWalk:
    """channels.f90 for every run of a batch (module docstring).

    TALYS: channels.f90:1 (channels)
    Test: GPUFULL, GPU3
    """

    def __init__(self, bk, chan_state: dict | None = None):
        from physics.hf.emission.channels import _channel_keys, _limits

        dev = bk.device
        E = bk.host["E"]
        B, R = bk.dims["B"], bk.dims["R"]
        self.bk, self.dev, self.B, self.R = bk, dev, B, R
        runs = bk.runs
        sc = [r["sc"] for r, _ in runs]
        zend = [min(6, s["maxz"], s["zinit"]) for s in sc]
        nend = [min(10, s["maxn"], s["ninit"]) for s in sc]
        nuclei = sorted({(z, n) for b in range(B) for z in range(zend[b] + 1)
                         for n in range(nend[b] + 1)})
        # runs of one nuclide share `sc`: the channel lists are formed once per nuclide
        by_sc: dict[int, list[int]] = {}
        for b in range(B):
            by_sc.setdefault(id(sc[b]), []).append(b)
        self.keys: dict[tuple[int, int], list] = {}
        present: dict[tuple, np.ndarray] = {}
        for (z, n) in nuclei:
            ks = []
            for bs in by_sc.values():
                b0 = bs[0]
                if z > zend[b0] or n > nend[b0]:
                    continue
                lim = _limits(z, n, list(sc[b0]["parinclude"]), sc[b0]["maxchannel"])
                for key in _channel_keys(z, n, lim, sc[b0]["maxchannel"]):
                    if key not in present:
                        present[key] = np.zeros(B, dtype=bool)
                        ks.append(key)
                    present[key][bs] = True
            self.keys[(z, n)] = ks
        self.by_level: dict[int, list] = {}
        for k in nuclei:
            self.by_level.setdefault(k[0] + k[1], []).append(k)
        self.col = {k: (key, i) for key, ks in self.keys.items() for i, k in enumerate(ks)}
        self.pres = {key: torch.as_tensor(np.stack([present[k] for k in ks], 1), device=dev)
                     for key, ks in self.keys.items() if ks}
        self.npart0 = {key: torch.as_tensor(np.array([sum(k) == 0 for k in ks]), device=dev)
                       for key, ks in self.keys.items() if ks}
        # (channel, ejectile type) pairs whose source channel exists at the mother nucleus
        self.pairs: dict[tuple[int, int], dict] = {}
        for key, ks in self.keys.items():
            by_ty = {}
            npair = 0
            for ty in range(1, 7):
                mother = (key[0] - PARZ[ty], key[1] - PARN[ty])
                kix, six = [], []
                for i, k in enumerate(ks):
                    if k[ty - 1] < 1:
                        continue
                    cnt = list(k)
                    cnt[ty - 1] -= 1
                    got = self.col.get(tuple(cnt))
                    if got is None or got[0] != mother:
                        continue
                    kix.append(i)
                    six.append(got[1])
                if kix:
                    by_ty[ty] = dict(mother=mother, kix=torch.as_tensor(kix, device=dev),
                                     six=torch.as_tensor(six, device=dev),
                                     pix=torch.arange(npair, npair + len(kix), device=dev),
                                     kix_h=np.array(kix), six_h=np.array(six))
                    npair += len(kix)
            self.pairs[key] = dict(by_ty=by_ty, n=npair)
        self.parskip = torch.as_tensor(np.array([s["parskip"] for s in sc]), device=dev)
        self.xseps = torch.as_tensor(np.array([s["xseps"] for s in sc]), device=dev)
        self.q00 = torch.as_tensor(np.array(
            [e["specs"][(0, 0)]["sep"][r["k0"]] + r["sc"]["targete"]
             for (r, _), e in zip(runs, E, strict=True)]), device=dev)
        # chanopen across energies: (nuclide, energy index) grid
        names = [(r["Z"], r["A"]) for r, _ in runs]
        self.names = names
        uniq = sorted(set(names))
        self.nuc_names = uniq
        nid = {u: i for i, u in enumerate(uniq)}
        self.eix = np.array([i for _, i in runs])
        self.NN, self.NE = len(uniq), int(self.eix.max()) + 1
        self.flat = torch.as_tensor(np.array([nid[u] for u in names]) * self.NE + self.eix,
                                    device=dev)
        self.chan_state = chan_state if chan_state is not None else {}
        prev = {}
        if any(isinstance(k, tuple) for k in self.chan_state):  # GPUC: "_sfactor" is binary's
            for key, ks in self.keys.items():
                v = np.array([[self.chan_state.get((u, k), False) for k in ks] for u in names],
                             dtype=bool).reshape(B, len(ks))
                if v.any():
                    prev[key] = torch.as_tensor(v, device=dev)
        self.prev_bucket = prev
        reach: dict[tuple, np.ndarray] = {}
        for b, e in enumerate(E):
            for k in e["static_reach"]:
                reach.setdefault(tuple(k), np.zeros(B, dtype=bool))[b] = True
        self.reach = {k: torch.as_tensor(v, device=dev) for k, v in reach.items()}
        self._spec_cache: dict = {}
        self._src_cache: dict = {}
        self.pending: dict = {}  # channel nucleus -> (B, pairs, R)
        self.xsexcl: dict = {}  # channel nucleus -> (B, channels, R), until its level is done
        self.qexcl: dict = {}  # channel nucleus -> (B, channels)
        self.opened: dict = {}
        self.valid: dict = {}
        self.xs: dict = {}
        self.covered: dict = {}  # channel nucleus -> (B,) runs already walked by a cascade row

    # ------------------------------------------------------------------ structure
    def _spec(self, key):
        got = self._spec_cache.get(key)
        if got is not None:
            return got
        E = self.bk.host["E"]
        B, R = self.B, self.R
        mx = np.zeros(B, dtype=np.int64)
        nl = np.zeros(B, dtype=np.int64)
        tau = np.zeros((B, R))
        ex0 = np.zeros(B)
        sep = np.zeros((B, 7))
        for b, e in enumerate(E):
            sp = e["specs"].get(key)
            if sp is None:
                continue
            mx[b], nl[b] = sp["maxex"], sp["nlast"]
            k = min(sp["nlast"], 300, len(sp["ex"]) - 1) + 1
            tau[b, :k] = sp["tau"][:k]
            ex0[b] = sp["ex"][0]
            sep[b] = sp["sep"]
        d = self.dev
        got = self._spec_cache[key] = tuple(torch.as_tensor(a, device=d)
                                            for a in (mx, nl, tau, ex0, sep))
        return got

    def mark_reached(self, key, runs: Tensor) -> None:
        m = torch.zeros(self.B, dtype=torch.bool, device=self.dev)
        m[runs] = True
        cur = self.reach.get(key)
        self.reach[key] = m if cur is None else (cur | m)

    def reached(self, key) -> Tensor:
        got = self.reach.get(key)
        return got if got is not None else torch.zeros(self.B, dtype=torch.bool,
                                                        device=self.dev)

    def is_channel_nucleus(self, key) -> bool:
        return key in self.keys

    # ------------------------------------------------------------------ the walk
    def _sources(self, key) -> dict:
        """What nucleus `key`'s channels read of other nuclei, per run (B, ...): its spec rows
        (reached), the separation energies of the seven ejectiles, and per (channel, ejectile)
        pair the source channel's validity and Qexcl and its pending contraction. All of it is
        final once every nucleus with fewer nucleons removed is done, which it is when `key`
        is first walked, so it is formed once."""
        got = self._src_cache.get(key)
        if got is not None:
            return got
        dev, B, R = self.dev, self.B, self.R
        z, nn = key
        reached = self.reached(key)
        mx, nl, tau, ex0, sep = self._spec(key)
        mx = torch.where(reached, mx, 0)
        nl = torch.where(reached, nl, 0)
        tau = torch.where(reached[:, None], tau, 0.0)
        ex0 = torch.where(reached, ex0, 0.0)
        seps = {}
        for ty in range(7):
            mk = (z - PARZ[ty], nn - PARN[ty])
            if mk[0] < 0 or mk[1] < 0:
                continue
            if mk == key:
                sv = torch.where(reached, sep[:, ty], 0.0)
            else:
                sv = torch.where(self.reached(mk), self._spec(mk)[4][:, ty], 0.0)
            seps[ty] = torch.where(self.parskip[:, ty], 0.0, sv)
        ks = self.keys[key]
        nk = len(ks)
        pres = self.pres[key]
        P = self.pending.pop(key, None)
        xe_src = torch.zeros((B, nk, R), dtype=F64, device=dev)
        by_ty = {}
        for ty, ent in self.pairs[key]["by_ty"].items():
            mother, kix, six = ent["mother"], ent["kix"], ent["six"]
            if mother not in self.valid:
                continue
            found = (pres[:, kix] & ~self.parskip[:, ty: ty + 1] & self.pres[mother][:, six]
                     & self.valid[mother][:, six])
            if P is not None:
                xe_src[:, kix] += torch.where(found[..., None], P[:, ent["pix"]], 0.0)
            by_ty[ty] = (kix, found, self.qexcl[mother][:, six])
        got = self._src_cache[key] = dict(reached=reached, mx=mx, nl=nl, tau=tau, ex0=ex0,
                                          seps=seps, xe_src=xe_src, by_ty=by_ty)
        return got

    def nucleus(self, key, runs: Tensor | None, popexcl: Tensor | None = None,
                f0: Tensor | None = None, top0: Tensor | None = None,
                runs_h: np.ndarray | None = None) -> None:
        """The channels at nucleus `key` for runs `runs` (host copy `runs_h`; None: every run not
        yet walked).

        `popexcl` (n, R + 2) and `f0` (n, R + 1, R) are the nucleus's own popexcl and photon
        feedexcl rows 0..R for those runs (None: the nucleus was not decayed in them); `top0`
        (n, R) is the initial compound nucleus's binary photon row.

        TALYS: channels.f90:1 (channels)
        Test: GPUFULL, GPU3
        """
        dev, B, R = self.dev, self.B, self.R
        cov = self.covered.get(key)
        if runs is None:
            left = np.flatnonzero(~cov) if cov is not None else np.arange(B)
            if left.size == 0:
                return
            runs = torch.as_tensor(left, device=dev)
        else:
            if cov is None:
                cov = self.covered[key] = np.zeros(B, dtype=bool)
            cov[runs_h if runs_h is not None else runs.cpu().numpy()] = True
        ks = self.keys[key]
        if not ks:
            return
        src = self._sources(key)
        n, nk = runs.numel(), len(ks)
        reached = src["reached"][runs]
        mx, nl, tau, ex0 = (src[k][runs] for k in ("mx", "nl", "tau", "ex0"))
        rows = torch.arange(R, device=dev)
        rmask = rows[None, :] <= mx[:, None]
        parskip0 = self.parskip[runs, :1]
        A = None
        if f0 is not None:
            pop = popexcl[:, 1: R + 1]
            f = f0[:, 1: R + 1, :]
            ok = (f != 0.0) & (pop != 0.0)[:, :, None] & \
                (rows[None, :, None] + 1 <= mx[:, None, None])
            ratio = torch.where(ok, f / torch.where(pop != 0.0, pop, 1.0)[:, :, None], 0.0)
            Uc = torch.zeros((n, R, R), dtype=F64, device=dev)
            Uc[:, :, 1:] = ratio[:, : R - 1, :].transpose(1, 2)
            A = torch.eye(R, dtype=F64, device=dev)[None] - torch.triu(Uc, diagonal=1)
        xsrows = (rows[None, :] <= torch.minimum(mx, nl)[:, None]) & (
            (tau != 0.0) | (rows[None, :] == 0))
        xseps = self.xseps[runs][:, None]
        pres = self.pres[key][runs]  # (n, nk)
        npart0 = self.npart0[key]
        xe = src["xe_src"][runs]
        q = torch.zeros((n, nk), dtype=F64, device=dev)
        zero = [i for i, k in enumerate(ks) if sum(k) == 0]
        if key == (0, 0) and zero:
            q[:, zero[0]] = self.q00[runs]
            if top0 is not None:
                xe[:, zero[0]] += top0
        for ty in range(7):
            if ty == 0:
                found = pres & ~parskip0
                qsrc = q
                kix = None
            else:
                got = src["by_ty"].get(ty)
                if got is None:
                    continue
                kix, found_B, qsrc_B = got
                found = found_B[runs]
                qsrc = qsrc_B[runs]
            sv = src["seps"].get(ty)
            if sv is None:
                continue
            sv = sv[runs][:, None]
            qk = q if kix is None else q[:, kix]
            qk = torch.where(found & (qk == 0.0), qsrc - sv, qk)
            qk = torch.where(found & reached[:, None], qk - ex0[:, None], qk)
            if kix is None:
                q = qk
            else:
                q[:, kix] = qk
        if A is not None:
            sol = torch.linalg.solve_triangular(A, xe.transpose(1, 2), upper=True,
                                                unitriangular=True).transpose(1, 2)
            xe = torch.where((pres & ~parskip0)[..., None], sol, xe)
        xe = torch.where(rmask[:, None, :], xe, 0.0)
        xs = torch.where(xsrows[:, None, :], xe, 0.0).flip(2).sum(2)
        xs = torch.where((q > 0.0) & (xs <= xseps), xseps, xs)
        opened = pres & ((xs >= xseps) | npart0[None, :])
        for store, v in ((self.xsexcl, xe), (self.qexcl, q), (self.xs, xs), (self.opened, opened)):
            cur = store.get(key)
            if cur is None:
                cur = store[key] = torch.zeros((B,) + v.shape[1:], dtype=v.dtype, device=dev)
            cur[runs] = v

    def level_done(self, level: int) -> None:
        """Channel nuclei at `level` not walked by any cascade row, then validity of every
        channel at `level` (module docstring)."""
        dev = self.dev
        for key in self.by_level.get(level, []):
            self.nucleus(key, None)
            ks = self.keys[key]
            if not ks:
                continue
            nk = len(ks)
            opened = self.opened[key]
            grid = torch.zeros((self.NN * self.NE, nk), dtype=torch.int8, device=dev)
            grid[self.flat] = opened.to(torch.int8)
            cum = torch.cumsum(grid.reshape(self.NN, self.NE, nk), dim=1)
            before = torch.cat([torch.zeros((self.NN, 1, nk), dtype=cum.dtype, device=dev),
                                cum[:, :-1]], dim=1) > 0
            prev = before.reshape(-1, nk)[self.flat]
            if key in self.prev_bucket:
                prev = prev | self.prev_bucket[key]
            npart1 = torch.as_tensor([sum(k) <= 1 for k in ks], device=dev)
            xs = self.xs[key]
            valid = (xs >= self.xseps[:, None]) | npart1[None, :] | prev
            self.valid[key] = valid
            self.xs[key] = torch.where(self.pres[key] & valid, xs, 0.0)
            self.pending.pop(key, None)
            self.xsexcl.pop(key, None)
            self._src_cache.pop(key, None)

    def contribute(self, mother, runs: Tensor, ty: int, bins: Tensor, ok_bins: Tensor,
                   popexcl: Tensor, mcont: Tensor) -> None:
        """Source contractions from mother nucleus `mother` through ejectile `ty` for runs `runs`:
        for every channel at the daughter, `xsexcl(source, nex) feedexcl(nex, .) / popexcl(nex)`
        over mother bins `bins` (n, mc) (`ok_bins` masks them), with `mcont` (n, mc, Rt) the
        feedexcl rows. `runs` may repeat (the contractions add).

        TALYS: channels.f90:370-383
        Test: GPUFULL, GPU3
        """
        dk = (mother[0] + PARZ[ty], mother[1] + PARN[ty])
        pr = self.pairs.get(dk)
        if pr is None:
            return
        ent = pr["by_ty"].get(ty)
        xsm = self.xsexcl.get(mother)
        if ent is None or xsm is None:
            return
        dev, B, R = self.dev, self.B, self.R
        n, mc, Rt = mcont.shape
        pop = popexcl.gather(1, bins)  # (n, mc)
        live = ok_bins & (pop != 0.0)
        # feedexcl / popexcl with channels.f90's `ok` (both non-zero)
        w = torch.where(live[..., None] & (mcont != 0.0),
                        mcont / torch.where(live, pop, 1.0)[..., None], 0.0)
        six = ent["six"]
        xv = xsm[runs][:, six].gather(2, bins[:, None, :].expand(n, six.numel(), mc))
        contrib = torch.einsum("bkm,bmr->bkr", xv, w)  # (n, pairs of ty, Rt)
        P = self.pending.get(dk)
        if P is None:
            P = self.pending[dk] = torch.zeros((B, pr["n"], R), dtype=F64, device=dev)
        np_ = pr["n"]
        flat = ((runs[:, None] * np_ + ent["pix"][None, :]) * R)  # (n, pairs of ty)
        idx = (flat[:, :, None] + torch.arange(Rt, device=dev)[None, None, :]).reshape(-1)
        P.view(-1).index_add_(0, idx, contrib.reshape(-1))

    def contribute_top(self, runs: Tensor, ty: int, top: Tensor) -> None:
        """The initial compound nucleus's binary row alone (no decayed bins in the contraction)."""
        dk = (PARZ[ty], PARN[ty])
        pr = self.pairs.get(dk)
        if pr is None or ty not in pr["by_ty"]:
            return
        ent = pr["by_ty"][ty]
        ks = self.keys[dk]
        sel = [j for j, i in enumerate(ent["kix_h"].tolist()) if sum(ks[i]) == 1]
        if not sel:
            return
        B, R, dev = self.B, self.R, self.dev
        P = self.pending.get(dk)
        if P is None:
            P = self.pending[dk] = torch.zeros((B, pr["n"], R), dtype=F64, device=dev)
        pix = ent["pix"][torch.as_tensor(sel, device=dev)]
        P[runs[:, None], pix[None, :], : top.shape[1]] += top[:, None, :]

    def results(self) -> dict:
        """channel code -> (B,) mb, and the updated `chan_state` for the next batch."""
        out = {}
        for key, v in self.xs.items():
            for i, k in enumerate(self.keys[key]):
                out[channel_code(k)] = v[:, i]
        # chanopen carried to the next batch: opened at any energy of this batch
        for key, v in self.opened.items():
            vv = v.cpu().numpy()
            ks = self.keys[key]
            for b, i in zip(*np.nonzero(vv), strict=True):
                self.chan_state[(self.names[b], ks[i])] = True
        return out
