#!/usr/bin/env python3
"""WP-02: raw data acquisition with a checksummed manifest.

Fetches every open source listed in BLUEPRINT.md section 3 into ``raw/<source>/`` and records
sha256 / size / fetch date / URL per file in ``raw/MANIFEST.json``.

Design rules
------------
* stdlib only (urllib, hashlib, subprocess) so it runs before the uv env is fully installed.
* idempotent: a file that is present *and* whose sha256 matches the manifest is skipped; a file
  that is present but not yet in the manifest is hashed and adopted (this is how background
  downloads started with curl/wget get registered once they finish).
* large Phase 1 fetches are spawned with nohup (``--background``) so they outlive the caller;
  the PID and exact command are written to ``raw/DOWNLOADS_IN_PROGRESS.md``.

Usage
-----
    python3 data/ingest/download.py --phase 0          # Phase 0 sources, foreground
    python3 data/ingest/download.py --background       # spawn Phase 1 large fetches with nohup
    python3 data/ingest/download.py --only ensdf       # one source by name
    python3 data/ingest/download.py --verify-manifest      # re-hash every recorded file
    python3 data/ingest/download.py --verify --phase all   # ...only what SOURCES still owns
    python3 data/ingest/download.py --verify               # ...phase 0 only (default)
    python3 data/ingest/download.py --list
"""

from __future__ import annotations

import argparse
import os
import fcntl
import hashlib
import json
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parents[2]
RAW = Path(os.environ.get("INCOGNITA_MAIN", REPO)).expanduser() / "raw"   # one data directory for every tool (default: the repository root)
MANIFEST = RAW / "MANIFEST.json"
LOGS = RAW / "_logs"
IN_PROGRESS = RAW / "DOWNLOADS_IN_PROGRESS.md"

# Several IAEA/NNDC endpoints answer 402/403 to the default urllib/curl UA.
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0 Safari/537.36"
)
CHUNK = 1 << 20


@dataclass
class Source:
    name: str
    url: str
    dest: str  # relative to raw/
    license: str
    phase: int
    kind: str = "file"  # file | git | mirror
    notes: str = ""
    background: bool = False  # spawn with nohup instead of fetching in the foreground
    expected_md5: str | None = None
    expected_sha1: str | None = None
    min_bytes: int = 1  # anything smaller is treated as a failed/truncated download
    mirror_accept: str = "*.zip"  # for kind == "mirror" (wget -A)
    extra: dict = field(default_factory=dict)


# --------------------------------------------------------------------------------------------
# License notes (short form; docs/data-licensing.md has the full findings)
# --------------------------------------------------------------------------------------------
LIC_AMDC = "AMDC/IAEA: open, cite Wang et al. Chin.Phys.C45 030001 (2021) / Kondev et al. (2021)"
LIC_NNDC = "NNDC/BNL: US public domain data, cite ENSDF DOI 10.18139/nndc.ensdf/1845010"
LIC_RIPL4 = "IAEA RIPL-4: open, redistribution with attribution; no SPDX license file in repo"
LIC_EXFOR = "CC BY 4.0 (stated on nds.iaea.org/nrdc/exfor-master); cite NDS 120 (2014) 272"
LIC_ENDFB = "ENDF/B: US public domain (BNL/DOE); cite Nucl. Data Sheets ENDF/B-VIII.1 paper"
LIC_JEFF = "JEFF (OECD/NEA): open, attribution; cite Plompen et al. EPJA 56 (2020) 181"
LIC_JENDL = "JENDL (JAEA): open, attribution; cite Iwamoto et al. JNST 60 (2023) 1"
LIC_TENDL = "TENDL (PSI/IAEA): open, attribution; cite Koning et al. NDS 155 (2019) 1"
LIC_CENDL = "CENDL (CIAE): open, attribution; distributed via IAEA-NDS mirror"
LIC_BRUSLIB = "BRUSLIB (ULB): open for scientific use, cite Goriely/Chamel/Pearson HFB papers"
LIC_WS4 = "WS4 (imqmd.com, N. Wang): open, cite Wang et al. PLB 734 (2014) 215"
LIC_KADONIS = "KADoNiS 1.0: open web tables, cite Dillmann et al. AIP Conf. Proc. 819 (2006) 123"
LIC_STD = "IAEA Neutron Data Standards 2017: public, cite Carlson et al. NDS 148 (2018) 143"
LIC_DZ = "Duflo-Zuker 1995 Fortran (AMDC theory dir): open, cite PRC 52 (1995) R23"
LIC_IAEA_PD = ("IAEA Photonuclear Data Library 2019: open, attribution; cite Kawano et al. "
               "NDS 163 (2020) 109")
LIC_OCL = ("Oslo Cyclotron Laboratory compilation of level densities and gamma strength: public "
           "web tables, cite the per-file publication (listed on the page)")
LIC_IAEA_PSF = ("IAEA Photon Strength Function Database v2024.1: CC BY 4.0; cite Goriely et al. "
                "EPJA 55 (2019) 172 and the per-file data authors")

AMDC = "https://www-nds.iaea.org/amdc/ame2020/"
LIC_JEFF40 = ("JEFF-4.0 (OECD/NEA, June 2025): CC BY 4.0 per the NEA data platform record "
              "(DOI 10.82555/e9ajn-a3p20, 'JEFF-4.0 Evaluated Data: neutron data'); cite that DOI")
LIC_FENDL = ("FENDL-3.2 (IAEA): free IAEA-NDS download, no licence file; cite Schnabel et al., "
             "Nucl. Data Sheets 193 (2024) 1")
LIC_BROND = ("BROND-3.1 (IPPE Obninsk, 2016), IAEA-NDS mirror: free download, no licence file; "
             "cite Blokhin et al., VANT ser. Yad. Konstanty 2016(2) 62")
LIC_IRDFF = ("IRDFF-II (IAEA, 2019/2020): free IAEA-NDS download, no licence file; cite "
             "Trkov et al., Nucl. Data Sheets 163 (2020) 1")

IAEA_ENDF = "https://www-nds.iaea.org/public/download-endf/"
NNDC_REL = "https://www.nndc.bnl.gov/endf-releases/releases/B-VIII.1/"
STD2017 = "https://www-nds.iaea.org/standards/std2017/"

STD2017_FILES = [
    "Standards2017_Tables.txt",
    "Standards2017_TNC.txt",
    "std17-001_H_001.endf",
    "std17-001_H_001.txt",
    "std17-003_Li_006.endf",
    "std17-003_Li_006.txt",
    "std17-005_B_010.endf",
    "std17-005_B_010.txt",
    "std17-006_C_000.endf",
    "std17-006_C_000.txt",
    "std17-079_Au_197.endf",
    "std17-079_Au_197.txt",
    "std17-092_U_235.endf",
    "std17-092_U_235.txt",
    "std17-092_U_238.endf",
    "std17-092_U_238.txt",
    "rec17-092_U_238g.endf",
    "rec17-092_U_238g.txt",
    "rec17-094_Pu_239.endf",
    "rec17-094_Pu_239.txt",
]

SOURCES: list[Source] = [
    # ---------------------------------------------------------------- Phase 0: masses/structure
    Source(
        "ame2020_mass",
        AMDC + "mass_1.mas20.txt",
        "ame2020/mass_1.mas20.txt",
        LIC_AMDC,
        0,
        notes="AME2020 mass table; '#' marks extrapolated (non-measured) values",
    ),
    Source(
        "ame2020_massround",
        AMDC + "massround.mas20.txt",
        "ame2020/massround.mas20.txt",
        LIC_AMDC,
        0,
        notes="rounded mass table",
    ),
    Source(
        "ame2020_rct1",
        AMDC + "rct1.mas20.txt",
        "ame2020/rct1.mas20.txt",
        LIC_AMDC,
        0,
        notes="reaction/separation energies S2n S2p Qa Q2b Qep Qb-n",
    ),
    Source(
        "ame2020_rct2",
        AMDC + "rct2_1.mas20.txt",
        "ame2020/rct2_1.mas20.txt",
        LIC_AMDC,
        0,
        notes="reaction/separation energies Sn Sp Q4b Qda Qpa Qna",
    ),
    Source(
        "ame2020_covariance",
        AMDC + "covariance.zip",
        "ame2020/covariance.zip",
        LIC_AMDC,
        0,
        notes="AME2020 correlation/covariance matrices",
    ),
    Source(
        "nubase2020",
        AMDC + "nubase_4.mas20.txt",
        "nubase2020/nubase_4.mas20.txt",
        LIC_AMDC,
        0,
        notes="NUBASE2020 g.s. + isomers: mass, Ex, T1/2, Jpi, decay modes; '#' = estimated",
    ),
    Source(
        "ensdf_full",
        "https://www.nndc.bnl.gov/ensdfarchivals/distributions/dist26/ensdf_260901.zip",
        "ensdf/ensdf_260901.zip",
        LIC_NNDC,
        0,
        notes="ENSDF full dump 2026-09-01 (latest per distributions/files.json)",
    ),
    Source(
        "ripl4",
        "https://github.com/IAEA-NDS/RIPL-4",
        "ripl4/RIPL-4",
        LIC_RIPL4,
        0,
        kind="git",
        notes="RIPL-4 (May 2026) all 7 segments: masses levels resonances optical densities gamma "
        "fission + RIPLpy + Codes. masses/ carries mass-frdm12, mass-hfb27, mass-ws4, "
        "mass-bskg3, mass-d1m, mass-ame20",
    ),
    # ------------------------------------------------------------- Phase 0: mass-model tables
    Source(
        "hfb24",
        "http://www.astro.ulb.ac.be/bruslib/nucdata/hfb24-dat",
        "mass_models/bruslib/hfb24-dat",
        LIC_BRUSLIB,
        0,
        notes="HFB-24 (BSk24) mass table, Goriely, Chamel, Pearson PRC 88 024308 (2013)",
    ),
    Source(
        "hfb27",
        "http://www.astro.ulb.ac.be/bruslib/nucdata/hfb27-dat",
        "mass_models/bruslib/hfb27-dat",
        LIC_BRUSLIB,
        0,
        notes="HFB-27 (BSk27) mass table (also in RIPL-4 masses/mass-hfb27.dat)",
    ),
    Source(
        "hfb31",
        "http://www.astro.ulb.ac.be/bruslib/nucdata/hfb31-dat",
        "mass_models/bruslib/hfb31-dat",
        LIC_BRUSLIB,
        0,
        notes="HFB-31 (BSk31) mass table, Goriely, Chamel, Pearson PRC 93 034337 (2016)",
    ),
    Source(
        "ws4",
        "http://www.imqmd.com/mass/WS4.txt",
        "mass_models/ws4/WS4.txt",
        LIC_WS4,
        0,
        notes="WS4 global mass formula table (2014-06-03)",
    ),
    Source(
        "ws4_rbf",
        "http://www.imqmd.com/mass/WS4_RBF.txt",
        "mass_models/ws4/WS4_RBF.txt",
        LIC_WS4,
        0,
        notes="WS4 + radial-basis-function correction",
    ),
    Source(
        "ws4_barriers",
        "http://www.imqmd.com/mass/BFWS4.txt",
        "mass_models/ws4/BFWS4.txt",
        LIC_WS4,
        0,
        notes="fission barriers from WS4 (2024-08-17)",
    ),
    Source(
        "dz28_rbf",
        "http://www.imqmd.com/mass/DZ28_RBF.txt",
        "mass_models/dz/DZ28_RBF.txt",
        LIC_WS4,
        0,
        notes="Duflo-Zuker 28-parameter masses with RBF correction (imqmd)",
    ),
    Source(
        "dz10_fortran",
        "https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96fort",
        "mass_models/dz/du_zu_10.feb96fort",
        LIC_DZ,
        0,
        notes="Duflo-Zuker 10-parameter formula, original Fortran (Feb 1996). Reference "
        "implementation for features/; DZ28 Fortran is not served by AMDC (404)",
    ),
    # ------------------------------------------------------------- Phase 1 (small, foreground)
    Source(
        "kadonis1_macs",
        "https://exp-astro.de/kadonis1.0/maketable.php?type=macs",
        "kadonis/kadonis1.0_macs.tsv",
        LIC_KADONIS,
        1,
        min_bytes=10_000,
        notes="KADoNiS 1.0 recommended MACS 5-100 keV, tab-separated",
    ),
    Source(
        "kadonis1_sef",
        "https://exp-astro.de/kadonis1.0/maketable.php?type=sef",
        "kadonis/kadonis1.0_sef.tsv",
        LIC_KADONIS,
        1,
        min_bytes=10_000,
        notes="KADoNiS 1.0 stellar enhancement factors",
    ),
    Source(
        "kadonis1_rrate",
        "https://exp-astro.de/kadonis1.0/maketable.php?type=rrate",
        "kadonis/kadonis1.0_rrate.tsv",
        LIC_KADONIS,
        1,
        min_bytes=10_000,
        notes="KADoNiS 1.0 reaction rates; server truncates after the first row (113 B) as of "
        "2026-09-08 -- treated as failed until the site is fixed",
    ),
    *[
        Source(
            f"std2017_{f}",
            STD2017 + f,
            f"standards/std2017/{f}",
            LIC_STD,
            1,
            notes="IAEA Neutron Data Standards 2017",
        )
        for f in STD2017_FILES
    ],
    # ------------------------------------------------------------- Phase 1 (large, background)
    Source(
        "exfor_master_2025",
        "https://nds.iaea.org/nrdc/exfor-master/exfor-2025/exfor-2025.zip",
        "exfor/exfor-2025.zip",
        LIC_EXFOR,
        1,
        background=True,
        notes="EXFOR Master File 2025 (snapshot 31 Dec 2025), DOI 10.61092/iaea.tqn1-2yc4, ~355 MB",
    ),
    Source(
        "exfor_entry_current",
        "https://nds.iaea.org/nrdc/exfor-master/entry/entry.zip",
        "exfor/entry.zip",
        LIC_EXFOR,
        1,
        background=True,
        notes="EXFOR Entry File, current snapshot (2026-08-27), ~380 MB; also on "
        "github.com/iaea-nds/exfor-entry-file",
    ),
    Source(
        "endfb81_endf6",
        NNDC_REL + "ENDF-B-VIII.1.tar.gz",
        "endf/endfb81/ENDF-B-VIII.1.tar.gz",
        LIC_ENDFB,
        1,
        background=True,
        expected_md5="2f65aceca3577b996dd997db3c02c59a",
        expected_sha1="32b25248c2e6e3e8c202f21a27c2787af6bd8b5c",
        notes="ENDF/B-VIII.1 full library, ENDF-6 format, ~1.08 GB "
        "(checksums from NNDC metadata.json)",
    ),
    Source(
        "endfb81_gnds",
        NNDC_REL + "ENDF-B-VIII.1-GNDS.zip",
        "endf/endfb81/ENDF-B-VIII.1-GNDS.zip",
        LIC_ENDFB,
        1,
        background=True,
        expected_md5="e528edd74b7ecc66fefe020e5c4c7c43",
        expected_sha1="e12380b6dcc779a64aab1b387929054b1ab2dbdc",
        notes="ENDF/B-VIII.1 full library, GNDS format, ~1.34 GB",
    ),
    Source(
        "jeff33_n",
        "https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/JEFF33-n.tgz",
        "endf/jeff33/JEFF33-n.tgz",
        LIC_JEFF,
        1,
        background=True,
        notes="JEFF-3.3 incident-neutron sublibrary, ENDF-6, ~469 MB",
    ),
    Source(
        "jendl5_n",
        "https://wwwndc.jaea.go.jp/ftpnd/ftp/JENDL/jendl5-n.tar.gz",
        "endf/jendl5/jendl5-n.tar.gz",
        LIC_JENDL,
        1,
        background=True,
        notes="JENDL-5 incident-neutron sublibrary, ENDF-6, ~4.4 GB",
    ),
    Source(
        "tendl2025_n",
        IAEA_ENDF + "TENDL-2025/n/",
        "endf/tendl2025/n",
        LIC_TENDL,
        1,
        kind="mirror",
        background=True,
        notes="TENDL-2025 neutron sublibrary, 2850 per-nuclide ENDF-6 zips from the IAEA-NDS "
        "mirror. "
        "tendl.web.psi.ch does not resolve in DNS (NXDOMAIN on 2026-09-08)",
    ),
    Source(
        "iaea_pd2019_g",
        IAEA_ENDF + "IAEA-PD-2019/g/",
        "photonuclear/iaea_pd2019",
        LIC_IAEA_PD,
        1,
        kind="mirror",
        background=True,
        notes="IAEA Photonuclear Data Library 2019 (IAEA/PD-2019), 219 per-isotope ENDF-6 zips "
        "from the CRP that reconciled the Saclay/Livermore photoneutron discrepancy. A8 uses it "
        "as a CROSS-CHECK only: it is an evaluation, and A3 is the register row that says an "
        "evaluation is not a measurement. The measured anchor comes from EXFOR "
        "(data/ingest/exfor_photonuclear.py)",
    ),
    Source(
        "iaea_psfdb_2024",
        "https://www-nds.iaea.org/PSFdatabase/download",
        "psf_database/psfdb_v2024.1.zip",
        LIC_IAEA_PSF,
        1,
        min_bytes=1_000_000,
        notes="IAEA Photon Strength Function Database v2024.1 (1,130 files; the site's own "
        "whole-database download, a stored zip). A13/OSLOFIT uses its oslo/ segment: Oslo-method "
        "dipole strength f1(E_gamma) for 103 nuclei, each with a readme recording the D0 and "
        "<Gamma_gamma> used to normalise it -- the normalisation-degeneracy audit reads those",
    ),
    Source(
        "ocl_compilation",
        "https://www.mn.uio.no/fysikk/english/research/about/infrastructure/ocl/"
        "nuclear-physics-research/compilation/",
        "oslo_compilation",
        LIC_OCL,
        1,
        kind="mirror",
        background=True,
        mirror_accept="*.txt",
        notes="The Oslo group's own compiled Oslo-method tables: level density rho(E_x) and "
        "strength f(E_gamma), one directory per publication, ~300 text files in the formats each "
        "paper used. A13/OSLOFIT takes rho from here (the IAEA PSF database carries only f). "
        "ocl.uio.no/compilation, the older address, does not resolve (2026-09-18)",
    ),
    Source(
        "cendl32_n",
        IAEA_ENDF + "CENDL-3.2/backup/cendl-3-2_n.sublib.zip",
        "endf/cendl32/cendl-3-2_n.sublib.zip",
        LIC_CENDL,
        1,
        background=True,
        notes="CENDL-3.2 neutron sublibrary via IAEA-NDS mirror, ~114 MB",
    ),
    # Four more evaluated neutron libraries to score next to JENDL-5 / TENDL-2025 / ENDF/B-VIII.1.
    # All four come from the IAEA-NDS per-material mirror (same E4-util zips as TENDL-2025).
    Source(
        "jeff40_n",
        IAEA_ENDF + "JEFF-4.0/n/",
        "endf/jeff40/n",
        LIC_JEFF40,
        1,
        kind="mirror",
        background=True,
        notes="JEFF-4.0 incident-neutron sublibrary (NSUB=10), 593 per-material zips, 667 MB. "
        "The NEA originals (databank.io.oecd-nea.org/data/jeff/40/, data.oecd-nea.org) sit "
        "behind a Cloudflare challenge and answer 403 to scripts even with the browser UA",
    ),
    Source(
        "fendl32_n",
        IAEA_ENDF + "FENDL-3.2c/n/",
        "endf/fendl32/n",
        LIC_FENDL,
        1,
        kind="mirror",
        background=True,
        notes="FENDL-3.2c neutron sublibrary, 192 per-material zips, 258 MB. 3.2c is the current "
        "IAEA release of FENDL-3.2 (3.2 -> 3.2b -> 3.2c are fix releases; www-nds.iaea.org/fendl/)",
    ),
    Source(
        "brond31_n",
        IAEA_ENDF + "BROND-3.1/n/",
        "endf/brond31/n",
        LIC_BROND,
        1,
        kind="mirror",
        background=True,
        notes="BROND-3.1 neutron sublibrary (IPPE, 2016), 372 per-material zips, 123 MB",
    ),
    Source(
        "irdff2_n",
        IAEA_ENDF + "IRDFF-II/n/",
        "endf/irdff2/n",
        LIC_IRDFF,
        1,
        kind="mirror",
        background=True,
        notes="IRDFF-II dosimetry library, 70 per-material zips, 32 MB (same data as "
        "nds.iaea.org/IRDFF/IRDFF-II_ENDF.zip). Dosimetry reactions only: MF3 for the "
        "ground-state/total channels, MF10 for isomer-resolved production (not staged)",
    ),
]

# Sources that could not be fetched by script; recorded for the licensing doc and the manifest.
UNREACHABLE = {
    "jeff40_nea": {
        "url": "https://databank.io.oecd-nea.org/data/jeff/40/ (DOI 10.82555/e9ajn-a3p20)",
        "status": "HTTP 403 Cloudflare challenge on data.oecd-nea.org and www.oecd-nea.org/dbdata "
        "(2026-09-22, browser UA)",
        "fallback": "IAEA-NDS mirror " + IAEA_ENDF + "JEFF-4.0/n/",
    },
    "frdm2012_lanl": {
        "url": "https://t2.lanl.gov/nis/data/astro/molleretal/",
        "status": "TLS handshake failure (CloudFront alert 40) over v4 and v6; http -> 403",
        "fallback": "ripl4/RIPL-4/masses/mass-frdm12.dat "
        "(FRDM2012 as compiled by S. Goriely, 2024-04-18)",
    },
    "tendl2025_psi": {
        "url": "https://tendl.web.psi.ch/tendl_2025/",
        "status": "DNS NXDOMAIN",
        "fallback": "IAEA-NDS mirror " + IAEA_ENDF + "TENDL-2025/",
    },
    "x4pro": {
        "url": "https://nds.iaea.org/exfor/x4pro/",
        "status": "HTTP 404 (also www-nds.iaea.org/x4toc4/ 404)",
        "fallback": "EXFOR Master File exfor-2025.zip + entry.zip (raw X4)",
    },
    "anl_amdc_mirror": {
        "url": "https://www.anl.gov/phy/atomic-mass-data-resources",
        "status": "HTTP 403 (not needed: www-nds.iaea.org/amdc/ answered 200 with a browser UA)",
        "fallback": "-",
    },
}


# --------------------------------------------------------------------------------------------
def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def digest(path: Path, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with path.open("rb") as fh:
        while chunk := fh.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"generated_by": "data/ingest/download.py", "files": {}, "unreachable": {}}


def save_manifest(m: dict) -> None:
    m["updated_at"] = now()
    m["unreachable"] = UNREACHABLE
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    tmp.replace(MANIFEST)


def http_get(url: str, dest: Path, timeout: int = 60) -> tuple[int, int]:
    """Stream url to dest.part then rename. Returns (status, bytes)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    req = Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urlopen(req, timeout=timeout) as resp, part.open("wb") as out:
        status = resp.status
        n = 0
        while chunk := resp.read(CHUNK):
            out.write(chunk)
            n += len(chunk)
    part.replace(dest)
    return status, n


def record(m: dict, src: Source, path: Path, status: str, **extra) -> dict:
    rel = str(path.relative_to(RAW))
    entry = {
        "source": src.name,
        "url": src.url,
        "license": src.license,
        "phase": src.phase,
        "status": status,
        "fetched_at": now(),
        "bytes": path.stat().st_size if path.exists() else None,
        "sha256": digest(path) if path.exists() and path.is_file() else None,
        "notes": src.notes,
    }
    entry.update(extra)
    m["files"][rel] = entry
    return entry


def verify_expected(src: Source, path: Path) -> list[str]:
    problems = []
    if src.expected_md5 and digest(path, "md5") != src.expected_md5:
        problems.append("md5 mismatch vs publisher")
    if src.expected_sha1 and digest(path, "sha1") != src.expected_sha1:
        problems.append("sha1 mismatch vs publisher")
    return problems


# --------------------------------------------------------------------------------------------
def fetch_file(src: Source, m: dict, verify: bool) -> str:
    dest = RAW / src.dest
    rel = str(dest.relative_to(RAW))
    known = m["files"].get(rel)

    if verify and src.background and not dest.exists():
        # --verify must never start a 4 GB download for something that was never fetched
        return "absent (background source; verify does not fetch)"

    if dest.exists() and dest.stat().st_size >= src.min_bytes:
        if known and known.get("sha256"):
            if not verify or digest(dest) == known["sha256"]:
                return "skip (present, manifest ok)"
            record(m, src, dest, "drift", previous_sha256=known["sha256"])
            return "DRIFT: sha256 differs from manifest"
        problems = verify_expected(src, dest)
        record(
            m,
            src,
            dest,
            "adopted" if not problems else "adopted-with-problems",
            problems=problems or None,
        )
        return "adopted (present, hashed)" + (f" problems={problems}" if problems else "")

    if (dest.with_name(dest.name + ".part")).exists():
        return "in progress (.part exists) -- skipping"

    try:
        status, n = http_get(src.url, dest)
    except HTTPError as e:
        m["files"][rel] = {
            "source": src.name,
            "url": src.url,
            "license": src.license,
            "phase": src.phase,
            "status": f"failed HTTP {e.code}",
            "fetched_at": now(),
            "bytes": None,
            "sha256": None,
            "notes": src.notes,
        }
        return f"FAILED HTTP {e.code}"
    except (URLError, OSError, TimeoutError) as e:
        m["files"][rel] = {
            "source": src.name,
            "url": src.url,
            "license": src.license,
            "phase": src.phase,
            "status": f"failed {e}",
            "fetched_at": now(),
            "bytes": None,
            "sha256": None,
            "notes": src.notes,
        }
        return f"FAILED {e}"

    if n < src.min_bytes:
        dest.unlink(missing_ok=True)
        m["files"][rel] = {
            "source": src.name,
            "url": src.url,
            "license": src.license,
            "phase": src.phase,
            "status": f"failed truncated ({n} B < {src.min_bytes})",
            "fetched_at": now(),
            "bytes": n,
            "sha256": None,
            "notes": src.notes,
        }
        return f"FAILED truncated ({n} B)"

    problems = verify_expected(src, dest)
    record(m, src, dest, "ok" if not problems else "ok-with-problems", problems=problems or None)
    return f"fetched {n:,} B" + (f" problems={problems}" if problems else "")


def fetch_git(src: Source, m: dict, verify: bool) -> str:
    dest = RAW / src.dest
    if not (dest / ".git").exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        log = LOGS / f"{src.name}_clone.log"
        LOGS.mkdir(parents=True, exist_ok=True)
        with log.open("w") as fh:
            rc = subprocess.call(
                ["git", "clone", "--depth", "1", src.url, str(dest)],
                stdout=fh,
                stderr=subprocess.STDOUT,
            )
        if rc != 0:
            return f"FAILED git clone rc={rc} (see {log})"
        action = "cloned"
    else:
        action = "present"
    commit = subprocess.check_output(
        ["git", "-C", str(dest), "rev-parse", "HEAD"], text=True
    ).strip()
    commit_date = subprocess.check_output(
        ["git", "-C", str(dest), "log", "-1", "--format=%ci"], text=True
    ).strip()

    # per-file entries so a fresh clone can be diffed file-by-file
    n_new = n_ok = 0
    for p in sorted(dest.rglob("*")):
        if not p.is_file() or ".git" in p.relative_to(dest).parts:
            continue
        rel = str(p.relative_to(RAW))
        known = m["files"].get(rel)
        if known and known.get("sha256") and known.get("commit") == commit and not verify:
            n_ok += 1
            continue
        record(
            m,
            src,
            p,
            "ok",
            commit=commit,
            commit_date=commit_date,
            url=f"{src.url}/blob/{commit}/{p.relative_to(dest)}",
        )
        n_new += 1
    m["files"][str(dest.relative_to(RAW))] = {
        "source": src.name,
        "url": src.url,
        "license": src.license,
        "phase": src.phase,
        "status": "ok",
        "kind": "git",
        "commit": commit,
        "commit_date": commit_date,
        "fetched_at": now(),
        "notes": src.notes,
        "n_files": n_new + n_ok,
    }
    return (
        f"{action} @ {commit[:12]} ({commit_date}); "
        f"{n_new} files hashed, {n_ok} already in manifest"
    )


def verify_manifest() -> int:
    """Re-hash every file the manifest records, and report drift, truncation and loss.

    `--verify` walks SOURCES and checks what those sources own. That leaves anything adopted by
    another route unchecked forever: `endf/endfb71/n` holds 423 ENDF/B-VII.1 zips with recorded
    sha256s and no Source in this file claims them, so no amount of `--verify` would ever look
    at the library half the differential validation is scored against.

    This walks the manifest instead, so coverage follows what was recorded rather than what the
    fetcher happens to still know how to fetch. Aggregate rows -- the `kind: mirror` and
    `kind: git` directory entries -- carry no sha256 and are skipped; their members are listed
    individually and are what actually gets hashed.

    Exit code is non-zero if anything is missing or has drifted, so it can gate a release.
    """
    m = load_manifest()
    files = m.get("files", {})
    ok = drift = missing = aggregate = unchecksummed = 0
    problems: list[str] = []
    for rel, meta in sorted(files.items()):
        want = meta.get("sha256")
        if not want:
            # Two very different things live here and must not be pooled. An aggregate row --
            # `kind: mirror` or `kind: git` -- describes a directory and has nothing to hash;
            # its members are listed separately. Anything ELSE without a checksum is a file we
            # meant to have and do not: kadonis1.0_rrate.tsv sits here with bytes=null because
            # its upstream answers HTTP 500. Counting that as "aggregate" is how a hole in the
            # data reads as a clean run.
            if meta.get("kind") in ("mirror", "git") or meta.get("n_files") or meta.get("commit"):
                aggregate += 1
            else:
                unchecksummed += 1
                problems.append(f"NO SHA   {rel} (bytes={meta.get('bytes')}, "
                                f"status={meta.get('status')})")
            continue
        path = RAW / rel
        if not path.is_file():
            missing += 1
            problems.append(f"MISSING  {rel}")
            continue
        got = digest(path)
        if got == want:
            ok += 1
        else:
            drift += 1
            size = path.stat().st_size
            note = f" (size {size} vs recorded {meta.get('bytes')})" if meta.get("bytes") else ""
            problems.append(f"DRIFT    {rel}{note}")
    for line in problems[:50]:
        print(line)
    if len(problems) > 50:
        print(f"... and {len(problems) - 50} more")
    print(f"manifest verify: {ok} ok, {drift} drifted, {missing} missing, "
          f"{unchecksummed} recorded without a checksum, {aggregate} aggregate directory rows")
    return 1 if (drift or missing or unchecksummed) else 0


def adopt_mirror(src: Source, m: dict, verify: bool) -> str:
    """Register whatever a wget mirror has landed so far (mirror runs only in the background)."""
    dest = RAW / src.dest
    if not dest.exists():
        return "not started (run --background)"
    n_new = n_ok = 0
    for p in sorted(dest.rglob("*")):
        if not p.is_file() or p.suffix == ".part" or p.name.endswith(".tmp"):
            continue
        rel = str(p.relative_to(RAW))
        known = m["files"].get(rel)
        if known and known.get("sha256") and not verify:
            n_ok += 1
            continue
        record(m, src, p, "ok", url=src.url + p.name)
        n_new += 1
    m["files"][str(dest.relative_to(RAW))] = {
        "source": src.name,
        "url": src.url,
        "license": src.license,
        "phase": src.phase,
        "status": "ok" if not list(dest.glob("*.part")) else "in progress",
        "kind": "mirror",
        "fetched_at": now(),
        "notes": src.notes,
        "n_files": n_new + n_ok,
    }
    return f"mirror: {n_new} files hashed, {n_ok} already in manifest"


# --------------------------------------------------------------------------------------------
def background_command(src: Source) -> str:
    """Shell command that downloads the source, then re-invokes this script to hash/adopt it."""
    py = shlex.quote(sys.executable if "python" in Path(sys.executable).name else "python3")
    me = shlex.quote(str(Path(__file__).resolve()))
    adopt = f"{py} {me} --only {src.name}"
    dest = RAW / src.dest
    if src.kind == "mirror":
        # -nH --cut-dirs keeps only the leaf directory; -np stays below the URL; -c resumes.
        depth = src.url.rstrip("/").count("/") - 2
        return (
            f"mkdir -p {shlex.quote(str(dest))} && wget -q -c -r -np -nH --cut-dirs={depth} "
            f"-A {shlex.quote(src.mirror_accept)} -R 'index.html*' -U {shlex.quote(UA)} "
            f"--tries=10 --waitretry=30 -P {shlex.quote(str(dest))} {shlex.quote(src.url)} ; "
            f"rm -f {shlex.quote(str(dest))}/index.html* ; {adopt}"
        )
    part = dest.with_name(dest.name + ".part")
    return (
        f"mkdir -p {shlex.quote(str(dest.parent))} && curl -sS -L -C - --retry 10 --retry-delay 30 "
        f"--retry-all-errors -A {shlex.quote(UA)} "
        f"-o {shlex.quote(str(part))} {shlex.quote(src.url)} "
        f"&& mv {shlex.quote(str(part))} {shlex.quote(str(dest))} && {adopt}"
    )


def spawn_background(sources: list[Source]) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Downloads in progress (spawned by data/ingest/download.py --background)",
        "",
        f"Spawned {now()}. Each job downloads with curl/wget under nohup, then runs "
        "`download.py --only <name>` to hash the result into MANIFEST.json.",
        "Check `raw/_logs/<name>.log`; `ps -p <pid>` tells you whether it is still running.",
        "Re-running `--background` is safe: jobs whose destination already exists are skipped, "
        "curl resumes `.part` files with `-C -`, wget resumes with `-c`.",
        "",
        "| source | dest | url | pid | log | command |",
        "|---|---|---|---|---|---|",
    ]
    for src in sources:
        dest = RAW / src.dest
        if src.kind != "mirror" and dest.exists():
            print(f"  {src.name:22s} already present, not spawning")
            continue
        cmd = background_command(src)
        log = LOGS / f"{src.name}.log"
        proc = subprocess.Popen(
            ["nohup", "sh", "-c", cmd],
            stdout=log.open("a"),
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            cwd=str(REPO),
        )
        print(f"  {src.name:22s} pid={proc.pid} -> {src.dest}")
        lines.append(
            f"| {src.name} | `{src.dest}` | {src.url} | {proc.pid} | `{log.relative_to(REPO)}` "
            f"| `{cmd.replace('|', '\\|')}` |"
        )
    lines += ["", "## Not fetchable by script", ""]
    for k, v in UNREACHABLE.items():
        lines.append(f"- **{k}**: {v['url']} -- {v['status']}; fallback: {v['fallback']}")
    IN_PROGRESS.write_text("\n".join(lines) + "\n")
    print(f"wrote {IN_PROGRESS.relative_to(REPO)}")


# --------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--phase", default="0", help="0 | 1 | 2 | all (default 0)")
    ap.add_argument("--only", nargs="*", help="source names to fetch (overrides --phase)")
    ap.add_argument(
        "--background",
        action="store_true",
        help="spawn the large Phase 1 fetches with nohup and exit",
    )
    ap.add_argument(
        "--verify", action="store_true", help="re-hash present files against the manifest"
    )
    ap.add_argument(
        "--verify-manifest",
        action="store_true",
        help="re-hash every file the manifest records, whatever fetched it (see verify_manifest)",
    )
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if args.verify_manifest:
        return verify_manifest()

    if args.list:
        for s in SOURCES:
            flag = "bg" if s.background else "  "
            print(f"P{s.phase} {flag} {s.kind:6s} {s.name:24s} {s.dest:50s} {s.url}")
        return 0

    RAW.mkdir(exist_ok=True)
    # Background jobs re-invoke this script when they finish; serialise manifest read/write.
    lock = (RAW / ".manifest.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    m = load_manifest()

    if args.background:
        spawn_background([s for s in SOURCES if s.background])
        save_manifest(m)
        return 0

    if args.only:
        todo = [s for s in SOURCES if s.name in set(args.only)]
        missing = set(args.only) - {s.name for s in todo}
        if missing:
            print(f"unknown sources: {sorted(missing)}", file=sys.stderr)
            return 2
    elif args.phase == "all":
        todo = [s for s in SOURCES if not s.background or args.verify]
    else:
        todo = [s for s in SOURCES
                if s.phase == int(args.phase) and (not s.background or args.verify)]
    # `background` marks sources too large to fetch inline -- they are spawned with nohup. That
    # is a rule about DOWNLOADING, and it was also excluding them from --verify, which only
    # hashes what is already on disk. The effect was that `--verify --phase all` checked 39
    # small sources, printed "0 failures", and never touched the ENDF/TENDL/JENDL mirrors --
    # the majority of raw/ by volume, and the data whose silent corruption would change every
    # library comparison in the project. Verification is local, so it covers them now; the
    # guards in fetch_file/fetch_git/adopt_mirror below make sure verify never starts a fetch.

    failures = 0
    t0 = time.time()
    for src in todo:
        if src.kind == "git":
            msg = fetch_git(src, m, args.verify)
        elif src.kind == "mirror":
            msg = adopt_mirror(src, m, args.verify)
        else:
            msg = fetch_file(src, m, args.verify)
        if msg.startswith(("FAILED", "DRIFT")):
            failures += 1
        print(f"{src.name:24s} {msg}")
        save_manifest(m)  # persist after every source so a crash loses nothing
    print(
        f"done in {time.time() - t0:.0f}s; {len(todo)} sources, {failures} failures; "
        f"manifest has {len(m['files'])} entries -> {MANIFEST.relative_to(REPO)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
