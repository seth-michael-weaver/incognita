#!/usr/bin/env python3
"""Minimal client of the talysworld service: submit one run, wait for all points, print them as JSON lines.
usage: client.py Z A E_EV[,E_EV...] [--comp library] [--kw key=value ...] [--extra "kw v;kw v"] [--url http://localhost:8765]"""
import argparse, json, time, urllib.request


def run(z, a, energies, comp="library", kw=None, extra="", url="http://localhost:8765", poll=5.0, quiet=False):
    body = json.dumps(dict(z=z, a=a, energies_ev=list(energies), comp=comp, kw=kw or {}, extra=extra)).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(url + "/api/run", body, {"Content-Type": "application/json"})))
    while True:
        s = json.load(urllib.request.urlopen(f"{url}/api/run?run={r['run']}"))
        if not quiet: print(f"  {z}-{a} {len(s['points'])}/{s['n']}", flush=True)
        if s["done"]: return r, sorted(s["points"], key=lambda p: p["e_ev"])
        time.sleep(poll)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("z", type=int); ap.add_argument("a", type=int); ap.add_argument("e")
    ap.add_argument("--comp", default="library"); ap.add_argument("--kw", nargs="*", default=[]); ap.add_argument("--extra", default="")
    ap.add_argument("--url", default="http://localhost:8765")
    a = ap.parse_args()
    info, pts = run(a.z, a.a, [float(x) for x in a.e.split(",")], a.comp, dict(k.split("=", 1) for k in a.kw), a.extra, a.url, quiet=True)
    print(json.dumps({k: info[k] for k in ("comp", "kw", "key")}))
    for p in pts: print(json.dumps(p))
