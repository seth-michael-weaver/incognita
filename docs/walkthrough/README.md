# Inside a Nuclear Reaction (website)

Live at <https://www.incognitanuclear.org/>. Three pages, in English and Spanish (`?lang=es` or the EN | ES switch):

| Page | What it is |
|---|---|
| `index.html` | **The physics**: an explorable explanation of what the engine computes, in the order it computes it. A live, full-screen hero (a neutron hitting a nucleus), then twenty-six chapters (twenty, then six Expert chapters in part two): a pinned drawing beside the text that changes as you read, with controls in the text that drag the physics. |
| `topics.html` | **More Nuclear Topics**: lessons beside the main story, in the same chapter style, Intro to Expert, under their own hero (a reactor pool, `js/topics/hero.js`) and a lesson index with a level filter (`js/topics/index.js`): radiation, inside a reactor (opening with the fuel cycle, mine to waste: `js/topics/fuelcycle.js`), kinds of reactor (every type: water, gas, fast, molten salt, special; `js/topics/types.js`; and a build-your-own sandbox, `js/topics/sandbox.js`), stability and control (ending with the physics of the Three Mile Island, Chernobyl and Fukushima accidents, `js/topics/accidents.js`), fusion, in the stars (`js/topics/stars.js`: s- and r-process; its σN and chart-of-nuclides pictures use INCOGNITA's v0.2 MACS at 30 keV and the board's `k_pernuc.csv` ratios, abundances from Lodders et al. 2009). Lessons in `js/topics/<id>.js` carry their own `level`; Criticality, Doppler and the four fusion chapters moved here from `index.html` on 2026-11-05 (old `#critical`-style links on the main page redirect). |
| `data.html` | **Every nuclide**: a chart of nuclides; for any nuclide, the v0.2 library's predicted curves (68 / 95 % bands) beside every curated EXFOR measurement, with dataset links, a table view and the command that reproduces the numbers. |
| `scoreboard.html` | **Scoreboard**: how the engine and the data product compare with other codes and libraries, losses first. |
| `pipeline.html` | **Pipeline**: how measurements become a reactor library (measurements, R-matrix fit, ENDF-6 file, NJOY, OpenMC library, benchmarks, judges), as a lit diagram with one live drawing per stage and the current status, losses first. Code in `js/pipeline.js`, styles in `pipeline.css`. |

Plain static files: no build step, no framework. Fonts come from Google Fonts and fall back to system fonts offline.

## Run it locally

```bash
cd docs/walkthrough && python3 serve.py 8765    # then open http://localhost:8765
```

`serve.py` is `python -m http.server` with caching turned off.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `style.css` | Page shell, typography and layout for all pages (light and dark tokens on `:root`) |
| `js/nav.js` | Site header on every page: links, EN \| ES switch, phone menu |
| `js/kit.js` | Chapter runtime: scroll-driven steps, inline controls (`data-bind`, `data-show`, `data-act`), eased state, drawing helpers (`g.label` shrinks labels to fit), glossary cards, `WT.shader` (WebGL fragment shaders drawn into a chapter canvas; null without WebGL, so keep a CPU fallback), `WT.grab` (drags and taps on the drawing) |
| `js/ch/intro.js` | The hero animation (standalone canvas loop, not a chapter) |
| `js/ch/<id>.js` | One chapter each: its text (`html`) and its drawing (`frame`) |
| `js/ch/fusion.js`, `gamow.js`, `tokamak.js`, `blanket.js` | Fusion (on `topics.html`). Physics explanation, except the last step of the blanket chapter, which reads INCOGNITA's (n,α), (n,p), (n,2n) at 14.1 MeV from `data/n/`. `WT.fus` (Bosch–Hale reactivities) lives in fusion.js. Plan: `FUSION_PLAN.md` |
| `js/glossary.js` | One entry per technical term; the first use per chapter is marked and explained in a card |
| `js/i18n.js`, `js/i18n/es-*.js` | Language layer and Spanish text; the Spanish files load only for Spanish readers |
| `js/data.js`, `data/` | The data explorer and its data: `data/index.json` (one row per nuclide) and `data/n/<Z>/<A>.json` (one nuclide, fetched only when it is opened) |
| `js/scoreboard.js`, `js/scoreboard-data.js` | The scoreboard page and its data (`WT.board`, also read by Chapter 12) |

## Updating the data

- **Every nuclide:** `uv run --no-project --with pyarrow python scripts/build_site_data.py` (from the repo root) rebuilds
  `data/` from `library/v0.2`, `data/curation/inputs` and `incognita/bench/data/exam_rows`. Re-run it when any of those change.
- **Scoreboard and Chapter 12:** regenerate `js/scoreboard-data.js` from the research ledger.
- After changing any JS or CSS, bump the `?v=` asset version in all three HTML files so returning visitors fetch the new files.

## Rules for editing the chapters

- Pictures explain the physics; plots only when the shape is the idea, drawn as a landscape, not a chart.
- Physics must match the code in `physics/hf` (say "optional" for opt-in switches); numbers are illustrative unless computed.
- No project status in the prose. The one code reference per chapter is its closing "In the code" note.
- Every change in English goes into the matching `js/i18n/es-*.js` (same tags and attributes; canvas labels keyed with `{#}` for numbers).
- Check phone width: the drawing is pinned on top of the text there; gate phone-only layout on `g.W < 600`.

## Performance

- Canvases draw at up to 2× pixel density on desktop and 1.5× on phones; the hero steps down to 1× by itself on slow devices.
- Only on-screen chapters animate; the hero pauses when scrolled away or when the tab is hidden.
- The hero's backdrop is painted once per size; the data chart drops its glow while you drag.
- `prefers-reduced-motion` gets still frames.

## Dev aids (URL parameters)

| Parameter | Effect |
|---|---|
| `?shot=<chapter>:<step>` | Show one chapter step alone (for screenshots) |
| `?shot=code` | Show only "Where this lives in the code" |
| `?herot=<seconds>` | Fast-forward the hero animation and hold it still |
| `?og=1` | Render the hero alone at 1200 × 630, as used for `og.png` (the share image) |
| `?theme=dark` / `?theme=light` | Force a colour theme |
| `?i18ndump=1` | List canvas labels that have no Spanish translation |
| `?nogl=1` | Turn WebGL off, to check the CPU fallback of shader drawings |

## Deploy

Vercel deploys `main` of this repository: the repo-root `vercel.json` serves `docs/walkthrough` as a static site (no build).
This folder's own `vercel.json` sets caching and security headers when the folder itself is used as the Vercel root.
