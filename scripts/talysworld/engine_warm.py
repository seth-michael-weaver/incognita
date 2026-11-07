#!/usr/bin/env python3
"""Warm engine worker for the talysworld service (Linux): imports the engine once, then forks one child per job.

The engine spends about 5-6 s per job on start-up (Python, numpy, the engine modules). This process pays that once:
it imports everything (engine_grid.preload), then reads one JSON request per line on stdin,
    {"args": {z, a, grid, comp, kw, work, smin}, "out": "/path/result.json"}
and forks a child for it. The child runs engine_grid.run(**args) with the already-imported modules (a fresh copy of
the parent's memory, so no job sees another job's state) and writes the result JSON atomically to "out". The service
limits how many jobs run at once and waits for the file. Started by server.py under nice 10; it exits with its stdin.
"""
import json, os, signal, sys, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_grid as EG  # noqa: E402

EG.preload()
signal.signal(signal.SIGCHLD, signal.SIG_IGN)   # children are reaped automatically
sys.stderr.write("engine_warm: ready\n"); sys.stderr.flush()
for line in sys.stdin:
    try:
        req = json.loads(line)
    except ValueError:
        continue
    if os.fork() == 0:
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        try:
            res = EG.run(**req["args"])
        except BaseException as ex:  # noqa: BLE001
            res = dict(err=f"warm worker: {type(ex).__name__}: {ex}"[:400], log_tail=traceback.format_exc()[-400:])
        try:
            tmp = req["out"] + ".tmp"
            with open(tmp, "w") as f: json.dump(res, f)
            os.replace(tmp, req["out"])
        finally:
            os._exit(0)
