/* Renderer for the TERRA comparison (WT.terra2, js/terra2-data.js): the opening answer (one split bar per library), then
   the full numbers inside "All TERRA numbers". Text through WT.ui keys (sb3_*, sb_*); numbers only from the data. */
(function () {
  const D = (window.WT || {}).terra2; if (!D) return;
  const H = D.headline;
  const T = (k, en) => WT.ui(k, en);
  const fill = (t, o) => t.replace(/\{(\w+)\}/g, (m, k) => (k in o ? o[k] : m));
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const pct = (v, d = 0) => (WT.sb3pct ? WT.sb3pct(v, d) : (v * 100).toFixed(d) + " %");
  const f1 = (v) => WT.dec((+v).toFixed(1));
  const big = (n) => Number(n).toLocaleString(WT.loc());
  const $ = (id) => document.getElementById(id);
  const date = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString(WT.loc(), { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
  // whole percents that add up to 100 (largest remainder), so the three numbers on a bar always sum to 100
  const whole = (vs) => {
    const raw = vs.map((v) => v * 100), fl = raw.map(Math.floor);
    let left = 100 - fl.reduce((a, b) => a + b, 0);
    raw.map((v, i) => [v - fl[i], i]).sort((a, b) => b[0] - a[0]).forEach(([, i]) => { if (left > 0) { fl[i]++; left--; } });
    return fl.map((v) => v / 100);
  };
  const LG = [T("sb3_lg_closer", "TERRA closer"), T("sb3_lg_equal", "about equal (within 5 %)"), T("sb3_lg_further", "library closer")];

  // ---- the answer: one sentence, one bar per library
  const ahead = D.rivals.every((r) => r.share_points_closer > r.share_points_behind);
  const lo = Math.min(...D.rivals.map((r) => r.share_points_closer)), hi = Math.max(...D.rivals.map((r) => r.share_points_closer));
  const h1 = $("sb3-h1");
  if (h1) h1.textContent = ahead
    ? T("sb3_h1", "Against measured data, TERRA is closer than each of the four major libraries more often than it is further away.")
    : fill(T("sb3_h1_alt", "Against measured data, TERRA is closer than the four major libraries on {lo} to {hi} of the points."), { lo: pct(lo), hi: pct(hi) });
  const bars = $("sb3-terra");
  if (bars && WT.sb3row) {
    bars.innerHTML = D.rivals.map((r) => {
      const [a, b, c] = whole([r.share_points_closer, r.share_points_tie, r.share_points_behind]);
      return WT.sb3row(r.rival, "", fill(T("sb3_terra_row", "TERRA closer on {p} of points"), { p: `<b>${pct(a)}</b>` }),
        [[a, pct(a)], [b, pct(b)], [c, pct(c)]], `${r.rival}: ${LG[0]} ${pct(a)}, ${LG[1]} ${pct(b)}, ${LG[2]} ${pct(c)}`, 0.12, true);
    }).join("");
  }
  const foot = $("sb3-terra-foot");
  if (foot) foot.textContent = fill(T("sb3_terra_foot", "{pts} measured points in {cells} comparisons (each one nuclide, one reaction and one energy band), as of {date}."),
    { pts: big(D.points), cells: big(D.cells), date: date(D.asof) });

  // ---- "What to keep in mind": where the point count flatters TERRA (average chi-squared on the same comparisons)
  const chi = $("sb3-keep-chi");
  if (chi) {
    const worse = D.rivals.filter((r) => H.pooled_chi2_rival_same_cells[r.rival] < H.pooled_chi2_terra_on_rival_cells[r.rival]);
    if (worse.length) chi.innerHTML = fill(T("sb3_keep_chi", "Counting points is not the whole story: where TERRA misses, it can miss by more. Its average χ² per point (lower is better) is higher than that of {libs} on the same comparisons."),
      { libs: worse.map((r) => `${esc(r.rival)} (${f1(H.pooled_chi2_terra_on_rival_cells[r.rival])} ${esc(T("sb3_against", "against"))} ${f1(H.pooled_chi2_rival_same_cells[r.rival])})`).join(", ") });
    else chi.remove();
  }

  // ---- inside "All TERRA numbers"
  const ex = $("sb3-terra-extra");
  if (ex) ex.textContent = fill(T("sb3_terra_extra", "On {all} of the points TERRA is closer than every library at once. Average χ² per point: TERRA {t}; the best library on each comparison {b}. Lower is better."),
    { all: pct(H.share_points_beat_every_rival, 1), t: f1(H.pooled_chi2_terra), b: f1(H.pooled_chi2_best_rival) });

  const tb = $("sb-t2rival");
  if (tb) {
    const el = (tag, html, cls) => { const e = document.createElement(tag); if (html != null) e.innerHTML = html; if (cls) e.className = cls; return e; };
    const thead = el("thead"), hr = el("tr");
    [[T("sb3_th_lib", "Library"), ""], [T("sb3_th_split", "Split of measured points"), ""], [T("sb3_lg_closer", "TERRA closer"), "r"], [T("sb3_th_equal", "About equal"), "r"],
     [T("sb3_lg_further", "library closer"), "r"], [T("sb3_th_chi", "χ²: TERRA / library"), "r"]].forEach(([h, c]) => { const t = el("th", esc(h), c || null); t.scope = "col"; hr.appendChild(t); });
    thead.appendChild(hr); tb.appendChild(thead);
    const body = el("tbody");
    for (const r of D.rivals) {
      const tr = el("tr");
      const name = el("th", esc(r.rival), "sb-t2-lib"); name.scope = "row"; tr.appendChild(name);
      const cell = el("td", null, "sb-t2-splitcell");
      const bar = el("div", null, "sb-strip sb-t2-split");
      bar.setAttribute("role", "img");
      bar.setAttribute("aria-label", `${LG[0]} ${pct(r.share_points_closer, 1)}, ${LG[1]} ${pct(r.share_points_tie, 1)}, ${LG[2]} ${pct(r.share_points_behind, 1)}`);
      [["sb-win", r.share_points_closer], ["sb-tie", r.share_points_tie], ["sb-loss", r.share_points_behind]].forEach(([c, v]) => {
        const s = el("span", null, "sb-seg " + c); s.style.flexGrow = String(v); bar.appendChild(s);
      });
      cell.appendChild(bar); tr.appendChild(cell);
      [pct(r.share_points_closer, 1), pct(r.share_points_tie, 1), pct(r.share_points_behind, 1)].forEach((v) => tr.appendChild(el("td", v, "num r")));
      const ours = H.pooled_chi2_terra_on_rival_cells[r.rival], theirs = H.pooled_chi2_rival_same_cells[r.rival];
      tr.appendChild(el("td", `<span class="${ours > theirs ? "neg" : "sb-t2-good"}">${f1(ours)}</span> / ${f1(theirs)}`, "num r"));
      body.appendChild(tr);
    }
    tb.appendChild(body);
  }

  // by kind of reaction: share of points closer than ENDF/B-VIII.1, with a 50 % mark
  const FAM = { "Total": "total", "Fission": "fission", "Capture": "capture", "Elastic": "elastic", "Inelastic": "inelastic", "Charged-particle": "charged", "(n,2n)": "n2n", "Other": "other" };
  const fam = $("sb-terra2-fam");
  if (fam) for (const f of D.families) {
    const row = document.createElement("div"); row.className = "sb-fam-row";
    const lab = FAM[f.family] ? T("sb3_fam_" + FAM[f.family], f.family) : f.family;
    row.innerHTML = `<span class="sb-fam-lab">${esc(lab)}</span><span class="sb-fam-track"><span class="sb-fam-fill" style="width:${(f.share_points_closer_than_VIII1 * 100).toFixed(1)}%"></span><span class="sb-fam-mid"></span></span>`
      + `<span class="sb-fam-val">${pct(f.share_points_closer_than_VIII1)}</span><span class="sb-fam-n">${esc(fill(T("sb3_pts", "{n} points"), { n: big(f.points) }))}</span>`;
    fam.appendChild(row);
  }

  const ten = $("sb-terra2-tension");
  if (ten) ten.textContent = fill(T("sb3_tension", "{cells} comparisons, holding {p} of the measured points, have laboratories that disagree with each other beyond their stated uncertainties. No single curve can match all of those points, so a share of them is out of reach for TERRA and for every library."),
    { cells: big(D.tension.cells), p: pct(D.tension.share_points, 1) });
})();
