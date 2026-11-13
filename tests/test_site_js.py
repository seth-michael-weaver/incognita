"""Site JS regressions (docs/walkthrough/js): data.js formatting, band lookup and axis range; ch/pipeline.js pulse; nav.js."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

JS = Path(__file__).resolve().parents[1] / "docs" / "walkthrough" / "js"
DATA = (JS / "data.js").read_text(encoding="utf-8")


def _node(code):
    node = shutil.which("node")
    if not node:
        pytest.skip("needs node")
    return json.loads(subprocess.run([node, "-e", code], capture_output=True, text=True, encoding="utf-8", check=True).stdout)


def _defs():
    lines = DATA.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("  const num = "))
    j = next(k for k, l in enumerate(lines) if l.startswith("  const SUP = "))
    return "const WT = { dec: (s) => s };\n" + "\n".join(lines[i:j])


def test_fmtE_picks_the_unit_after_rounding():
    out = _node(_defs() + "\nconsole.log(JSON.stringify([999.95, 999.7, 999999, 1500, 2.5e6, 0.0253].map(fmtE)));")
    assert out == ["1 keV", "1 keV", "1 MeV", "1.5 keV", "2.5 MeV", "0.0253 eV"]


def test_band_between_its_points():
    # the (n,p) band sits at benchmark energies: a grid energy between two band points gets the log-log value
    out = _node(_defs() + "\nconst b = [[8e6, 1, 4], [1e7, 4, 16]];"
                "\nconsole.log(JSON.stringify([bandAt(b, 8e6), bandAt(b, Math.sqrt(8e7 * 1e6)), bandAt(b, 7e6), bandAt(null, 1)]));")
    assert out[0] == [8e6, 1, 4] and out[2] is None and out[3] is None
    assert abs(out[1][1] - 2) < 1e-9 and abs(out[1][2] - 8) < 1e-9


def test_y_padding_is_code_not_comment():
    for line in DATA.splitlines():
        if "y1 - y0 < 1) { y0 -= 0.5" in line:
            assert "//" not in line.split("y1 - y0 < 1")[0], line
            break
    else:
        raise AssertionError("y padding statement missing")


def test_pulse_cancels_the_running_animation_first():
    src = (JS / "ch" / "pipeline.js").read_text(encoding="utf-8")
    body = src[src.index("function pulseTo"):]
    body = body[:body.index("\n  }")]
    assert body.index("cancelAnimationFrame") < body.index("= { path,")


def test_expert_menu_uses_chapter_short_names():
    nav = (JS / "nav.js").read_text(encoding="utf-8")
    for k in ("hauser", "optical", "densities", "strength", "exciton", "averages"):
        label = re.search(rf'\["{k}",3,"([^"]*)"\]', nav).group(1)
        short = re.search(r'title: "[^"]*", short: "([^"]*)"', (JS / "ch" / f"{k}.js").read_text(encoding="utf-8")).group(1)
        assert label == short, k


def _pipeline_fn(name):
    src = (JS / "ch" / "pipeline.js").read_text(encoding="utf-8")
    body = src[src.index(f"  function {name}("):]
    return body[:body.index("\n  }\n") + 4]


def test_stage_subtitle_cut_gets_an_ellipsis():
    # pipeline.js: a stage subtitle wrapped to more lines than the panel holds (German) was cut with no "…"
    fn = _pipeline_fn("clampLines")
    ctx = "const ctx = { measureText: (s) => ({ width: s.length * 10 }) };"   # 10 px per character
    out = _node(ctx + "\n" + fn + "\nconsole.log(JSON.stringify(["
                "clampLines(ctx, ['aaaa bbbb', 'cccc dddd', 'eeee'], 2, 90),"
                "clampLines(ctx, ['aaaa', 'bbbb'], 2, 90),"
                "clampLines(ctx, ['aaaa bbbb', 'cccc'], 1, 50)]));")
    assert out[0][0] == "aaaa bbbb" and out[0][1].startswith("cccc d") and len(out[0]) == 2
    assert all(len(l) * 10 <= 90 for l in out[0]) and out[0][-1].endswith("…")
    assert out[1] == ["aaaa", "bbbb"]                       # fits: unchanged, no ellipsis
    assert out[2][-1].endswith("…") and len(out[2]) == 1 and len(out[2][0]) * 10 <= 50


def test_stage_subtitle_long_word_stays_in_its_box():
    # pipeline.js (German, 1536 px): "ICSBEP-Kritikalitätsexperimente," is one word wider than the stage box; wrap() could not
    # break it and text() stopped shrinking at 9 px, so it ran past the box border. Now wrap() breaks after hyphens and
    # text() cuts with "…" when 9 px is still too wide.
    pre = ("const WT = {}; const SANS = 's', MONO = 'm'; const C = { ink: '#fff' };"
           "const ctx = { font: '13px', measureText(s) { return { width: s.length * parseFloat(this.font.split(' ')[1]) }; },"
           " fillText(s) { this.drawn = s; } };")
    out = _node(pre + "\n" + _pipeline_fn("font") + "\n" + _pipeline_fn("text") + "\n" + _pipeline_fn("wrap") +
                "\nconst w = wrap(ctx, 'ICSBEP-Kritikalitaetsexperimente, k-eff', 200, 12, 500);"
                "\nconst w2 = wrap(ctx, 'aa bb cc', 50, 10);"
                "\ntext(ctx, 'Kritikalitaetsexperimentezzzzzzzzzz', 0, 0, { size: 12, max: 200 }); const cut = ctx.drawn, fitCut = ctx.measureText(cut).width;"
                "\ntext(ctx, 'short', 0, 0, { size: 12, max: 200 });"
                "\nconsole.log(JSON.stringify({ w, w2, cut, fitCut, short: ctx.drawn }));")
    assert out["w"][0] == "ICSBEP-" and out["w"][1].startswith("Kritikalitaetsexperimente,")
    assert out["w2"] == ["aa bb", "cc"]                     # ordinary words: unchanged behaviour
    assert out["cut"].endswith("…") and out["fitCut"] <= 200
    assert out["short"] == "short"


def test_stage_subtitle_uses_clamp():
    src = (JS / "ch" / "pipeline.js").read_text(encoding="utf-8")
    assert "clampLines(ctx, sl," in src


def _live_job():
    src = (Path(__file__).resolve().parents[1] / "scripts" / "talysworld" / "web" / "js" / "calc.js").read_text(encoding="utf-8")
    body = src[src.index("  async function liveJob("):]
    return body[:body.index("\n  }\n") + 4]


def test_live_job_stops_when_the_service_restarts():
    # calculator live mode: after a service restart, /api/run answers {"error": "no such run"} for ever; the poll used to
    # loop for ever (spinner never cleared). Now: retry the job once, then fail with a message.
    out = _node(_live_job() + """
let sub = 0;
const lost = () => liveJob(async () => ({ run: "r" + (++sub) }), async () => ({ error: "no such run" }), { every: 1 });
const slow = () => { let t = 0; return liveJob(async () => ({ run: "x" }), async () => ({ done: false }), { every: 1, timeout: 50, now: () => (t += 20) }); };
let n2 = 0;
const second = () => liveJob(async () => ({ run: "y" + (++n2) }), async (run) => run === "y1" ? { error: "no such run" } : { done: true, points: [{ ok: 1 }] }, { every: 1 });
const eng = () => { let k = 0; return liveJob(async () => { k++; return { run: "z" }; }, async () => ({ done: true, points: [{ err: "engine failed" }] }), { every: 1 }).catch((e) => [k, e.message]); };
(async () => {
  const a = await lost().then(() => "resolved", (e) => e.message);
  const b = await slow().then(() => "resolved", (e) => e.message);
  const c = await second();
  const d = await eng();
  console.log(JSON.stringify([a, sub, b, c, n2, d]));
})();""")
    a, sub, b, c, n2, d = out
    assert "no such run" in a and sub == 2          # submitted twice (one retry), then a message
    assert "no result after" in b
    assert c == {"ok": 1} and n2 == 2               # the retry succeeds
    assert d == [1, "engine failed"]                # the engine's own error is not retried
