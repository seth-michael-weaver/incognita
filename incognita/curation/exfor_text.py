"""Read EXFOR records from the IAEA master archive (entry.zip) and check quoted evidence against them."""
from __future__ import annotations

import functools
import re
import zipfile

from . import paths

_WS = re.compile(r"\s+")


@functools.lru_cache(maxsize=2)
def _zip(path: str = str(paths.ENTRY_ZIP)) -> tuple[zipfile.ZipFile, dict[str, str]]:
    z = zipfile.ZipFile(path)
    names = {}
    for n in z.namelist():
        m = re.search(r"(\w{5})\.txt$", n)
        if m:
            names[m.group(1).upper()] = n
    return z, names


@functools.lru_cache(maxsize=8192)
def entry_text(entry: str) -> str:
    z, names = _zip()
    return z.read(names[str(entry).strip().upper()]).decode("latin-1")


def subentry_text(entry: str, subentry: str, *, with_common: bool = True) -> str:
    """The text of SUBENT ``subentry`` (plus the entry's common SUBENT xxxxx001)."""
    common = f"{entry}001"
    out, cur = [], None
    for ln in entry_text(entry).splitlines():
        if ln.startswith("SUBENT") or ln.startswith("NOSUBENT"):
            parts = ln.split()
            cur = parts[1] if len(parts) > 1 else ""
        if cur == str(subentry) or (with_common and cur == common):
            out.append(ln)
        if ln.startswith("ENDSUBENT"):
            cur = None
    return "\n".join(out)


def _norm(s: str) -> str:
    return _WS.sub(" ", s).strip().upper()


def normalised_record(entry: str, subentry: str) -> str:
    """Record text with the 11-column EXFOR line tags removed and whitespace collapsed (quote matching)."""
    lines = [ln[:66] if len(ln) >= 66 else ln for ln in subentry_text(entry, subentry).splitlines()]
    return _norm(" ".join(lines))


def quote_found(entry: str, subentry: str, quote: str) -> bool:
    """True if ``quote`` occurs verbatim (case and whitespace insensitive) in the subentry or SUBENT 001."""
    return _norm(quote) in normalised_record(entry, subentry)


STATUS_RE = re.compile(r"^STATUS\s+(.*)$")


def status_codes(entry: str, subentry: str) -> set[str]:
    """EXFOR STATUS codes of the subentry and of SUBENT 001, e.g. {'PRELM', 'CURVE', 'SPSDD'}."""
    codes: set[str] = set()
    in_status = False
    for ln in subentry_text(entry, subentry).splitlines():
        kw = ln[:10].strip()
        body = ln[11:66] if len(ln) > 11 else ""
        if kw:
            in_status = kw == "STATUS"
        if in_status:
            codes.update(re.findall(r"\(([A-Z]{4,5})[,)]", body))
    return codes
