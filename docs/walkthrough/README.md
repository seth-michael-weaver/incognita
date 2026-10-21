# Inside a Nuclear Reaction

An explorable explanation of the physics in the INCOGNITA engine (`physics/hf`, `physics/resonance`): one scrolling
story in the order the engine computes a reaction. The drawing beside the text changes as you read, and controls in the
text let you drag the physics (energy, angular momentum, deformation, temperature …) and watch it respond.

## View

```bash
cd docs/walkthrough && python3 serve.py 8765    # then open http://localhost:8765
```

Opening `index.html` straight from disk also works (plain scripts, no build step). Fonts come from Google Fonts and
fall back to system fonts offline.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `style.css` | Page shell, typography, layout (hero, contents bar, chapters, "where this lives in the code") |
| `js/kit.js` | Runtime: scroll-driven steps, inline controls (`data-bind`, `data-show`, `data-act`), eased state, drawing helpers |
| `js/glossary.js` | Glossary: one entry per technical term; `kit.js` marks each term's first use per step and explains it in a card |
| `glossary_check.py` | Lists technical-looking words in the prose that no glossary entry covers (`python3 glossary_check.py`) |
| `js/ch/<id>.js` | One chapter each: its text (`html`) and its drawing (`frame`), so a chapter is edited in one place |
| `scoreboard.html`, `js/scoreboard.js` | The scoreboard page (losses first); its data is `js/scoreboard-data.js` |

## Rules for editing

- Pictures explain the physics; plots only when the shape is the idea, drawn as a landscape, not a chart.
- Physics must match the code; numbers are illustrative unless computed.
- No project status in the text. The one code reference per chapter is its closing "In the code" note.

## Deploy on Vercel

The site is plain static files (no build step). `vercel.json` sets caching and security headers; `.vercelignore` keeps the dev files
(briefs, screenshot scripts, `serve.py`) out of the deployment when this folder is the Vercel root; with the repo-root
`vercel.json` (output = this folder) it does not apply, so that file redirects those paths to the page instead.

**Dashboard (Git):** import the repo in Vercel and deploy. The repo-root `vercel.json` already serves `docs/walkthrough` as a
static site (framework none, no build), so the default project settings work. (Alternatively set **Root Directory** to
`docs/walkthrough`; then this folder's own `vercel.json` applies.)

**CLI (no Git needed):** from this folder, `npx vercel` (preview) then `npx vercel --prod`. Needs Node.js; on first run it asks
you to log in and to confirm the project settings (accept the defaults: no build command, output = this folder).

Language: the page opens in English; `?lang=es` (or the EN | ES switch in the contents bar) shows Spanish, and the choice is remembered.
