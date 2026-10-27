#!/usr/bin/env python3
"""Archive a library release on Zenodo as a DRAFT with a reserved DOI (publish only with --publish).

Files come from a local directory and are checked against the release's SHA256SUMS before upload. Releases larger than
--max-gb are split into numbered records ("part 1 of N"). The result (record ids, draft URLs, reserved DOIs, files) is
written to library/<release>/ZENODO.json and, with --update-readme, an "Archived at" section is added to the README.

Token: ~/.zenodo_token (or env ZENODO_TOKEN); scopes deposit:write and deposit:actions. --sandbox uses sandbox.zenodo.org
(token from ~/.zenodo_sandbox_token). Zenodo records cannot be deleted once published, so publishing is a separate step.

  python3 scripts/zenodo_release.py res-v0.1 --files ~/release_files/res-v0.1 --dry-run
  python3 scripts/zenodo_release.py res-v0.1 --files ~/release_files/res-v0.1 --sandbox --update-readme
  python3 scripts/zenodo_release.py res-v0.1 --publish          # publishes the drafts listed in ZENODO.json
"""
import argparse, hashlib, json, os, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {False: "https://zenodo.org", True: "https://sandbox.zenodo.org"}


def token(sandbox):
    env = os.environ.get("ZENODO_SANDBOX_TOKEN" if sandbox else "ZENODO_TOKEN")
    if env:
        return env.strip()
    f = Path.home() / (".zenodo_sandbox_token" if sandbox else ".zenodo_token")
    if not f.exists():
        sys.exit(f"no token: put it in {f} (chmod 600) or set the env var")
    return f.read_text().strip()


def api(method, url, tok, body=None, data=None, ctype="application/json"):
    req = urllib.request.Request(url, method=method, headers={"Authorization": f"Bearer {tok}"})
    if body is not None:
        data = json.dumps(body).encode()
    if data is not None:
        req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, data=data, timeout=3600) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {url} -> {e.code}: {e.read().decode()[:500]}")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def citation():
    """Creators and title from CITATION.cff (no YAML dependency: the fields we need are simple)."""
    txt = (ROOT / "CITATION.cff").read_text()
    fam = re.findall(r"family-names:\s*(.+)", txt)
    giv = re.findall(r"given-names:\s*(.+)", txt)
    creators = [{"name": f"{f.strip()}, {g.strip()}"} for f, g in zip(fam, giv)] or [{"name": "Weaver, Seth Michael"}]
    return creators[:1]  # the first authors block is the project author; later ones belong to references


def readme_summary(rel):
    """First heading + first paragraph of library/<rel>/README.md, as the record description."""
    lines = (ROOT / "library" / rel / "README.md").read_text().splitlines()
    title = lines[0].lstrip("# ").strip()
    para, started = [], False
    for l in lines[1:]:
        if l.strip() and not l.startswith("#"):
            para.append(l.strip()); started = True
        elif started:
            break
    return title, " ".join(para).replace("**", "")


def plan(rel, files_dir, max_gb):
    sums = {}
    for l in (ROOT / "library" / rel / "SHA256SUMS").read_text().splitlines():
        if l.strip():
            h, name = l.split(None, 1)
            sums[name.strip()] = h
    files = []
    for name, h in sorted(sums.items()):
        p = Path(files_dir).expanduser() / name
        if not p.exists():
            sys.exit(f"missing {p} (listed in SHA256SUMS)")
        if sha256(p) != h:
            sys.exit(f"sha256 mismatch: {p}")
        files.append((p, p.stat().st_size))
    for extra in ("README.md", "SHA256SUMS", "MANIFEST.json"):
        p = ROOT / "library" / rel / extra
        if p.exists():
            files.append((p, p.stat().st_size))
    parts, cur, size = [], [], 0
    for p, s in files:
        if cur and size + s > max_gb * 1e9:
            parts.append(cur); cur, size = [], 0
        cur.append(p); size += s
    parts.append(cur)
    return parts


def create(rel, parts, sandbox, version):
    tok, host = token(sandbox), HOSTS[sandbox]
    title, desc = readme_summary(rel)
    out = []
    for i, part in enumerate(parts, 1):
        t = title if len(parts) == 1 else f"{title} (part {i} of {len(parts)})"
        meta = {"metadata": {
            "title": t, "upload_type": "dataset", "description": desc or t, "creators": citation(),
            "license": "cc-by-4.0", "version": version or rel, "prereserve_doi": True,
            "related_identifiers": [
                {"identifier": f"https://github.com/seth-michael-weaver/incognita/releases/tag/{rel}", "relation": "isIdenticalTo"},
                {"identifier": f"https://github.com/seth-michael-weaver/incognita/tree/main/library/{rel}", "relation": "isDocumentedBy"},
                {"identifier": "https://www.incognitanuclear.org/", "relation": "isSupplementTo"}],
            "keywords": ["nuclear data", "neutron cross sections", "OpenMC", "ENDF-6", "INCOGNITA"]}}
        dep = api("POST", f"{host}/api/deposit/depositions", tok, body=meta)
        bucket = dep["links"]["bucket"]
        for p in part:
            with open(p, "rb") as f:
                api("PUT", f"{bucket}/{p.name}", tok, data=f.read(), ctype="application/octet-stream")
        doi = dep["metadata"].get("prereserve_doi", {}).get("doi")
        out.append({"part": i, "id": dep["id"], "draft": dep["links"]["html"], "doi": doi, "host": host,
                    "files": [p.name for p in part], "published": False})
        print(f"draft {dep['id']}: {dep['links']['html']}  reserved DOI {doi}  ({len(part)} files)")
    return out


def publish(rel, sandbox):
    zj = ROOT / "library" / rel / "ZENODO.json"
    recs = json.loads(zj.read_text())
    tok = token(sandbox)
    for r in recs["records"]:
        if r["published"]:
            continue
        res = api("POST", f"{r['host']}/api/deposit/depositions/{r['id']}/actions/publish", tok)
        r["published"], r["doi"] = True, res.get("doi", r["doi"])
        print(f"published {r['id']}: DOI {r['doi']}")
    zj.write_text(json.dumps(recs, indent=1) + "\n")


def update_readme(rel, records):
    p = ROOT / "library" / rel / "README.md"
    s = re.sub(r"\n## Archived at\n.*?(?=\n## |\Z)", "", p.read_text(), flags=re.S).rstrip("\n")
    lines = [f"- DOI [{r['doi']}](https://doi.org/{r['doi']})" + (f" (part {r['part']})" if len(records) > 1 else "")
             + ("" if r["published"] else " (reserved; record not yet published)") for r in records]
    p.write_text(s + "\n\n## Archived at\nZenodo (CC BY 4.0):\n" + "\n".join(lines) + "\n")


def main():
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("release")
    a.add_argument("--files", help="directory holding the files listed in library/<release>/SHA256SUMS")
    a.add_argument("--max-gb", type=float, default=45.0)
    a.add_argument("--version")
    a.add_argument("--sandbox", action="store_true")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--update-readme", action="store_true")
    a.add_argument("--publish", action="store_true")
    o = a.parse_args()
    if o.publish:
        publish(o.release, o.sandbox)
        if o.update_readme:
            update_readme(o.release, json.loads((ROOT / "library" / o.release / "ZENODO.json").read_text())["records"])
        return
    if not o.files:
        sys.exit("--files is required")
    parts = plan(o.release, o.files, o.max_gb)
    for i, part in enumerate(parts, 1):
        print(f"part {i}: {len(part)} files, {sum(p.stat().st_size for p in part) / 1e9:.2f} GB")
    if o.dry_run:
        return
    recs = create(o.release, parts, o.sandbox, o.version)
    (ROOT / "library" / o.release / "ZENODO.json").write_text(
        json.dumps({"release": o.release, "sandbox": o.sandbox, "records": recs}, indent=1) + "\n")
    if o.update_readme:
        update_readme(o.release, recs)


if __name__ == "__main__":
    main()
