/* Scoreboard page: renders WT.board (js/scoreboard-data.js, generated from the project's records) in the page's language. */
(function () {
  "use strict";
  const B = WT.board, es = WT.tl, T = (k, en) => WT.ui(k, en);
  const $ = (s) => document.querySelector(s);
  const th = /[?&]theme=(dark|light)/.exec(location.search); if (th) document.documentElement.dataset.theme = th[1]; // dev aid, as in kit.js
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const num = (v, d = 4) => (v > 0 ? "+" : v < 0 ? "−" : "") + WT.dec(Math.abs(v).toFixed(d));
  const dex = (v, d = 3) => WT.dec(Number(v).toFixed(d));
  const date = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString(WT.loc(), { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
  const V = { WIN: T("v_win", "WIN"), TIE: T("v_tie", "TIE"), LOSS: T("v_loss", "LOSS"), NA: "N/A" };
  const ORDER = ["WIN", "TIE", "LOSS"];   // one order everywhere: hero, tiles, strips, tables
  const badge = (v) => `<span class="vd vd-${v.toLowerCase()}">${V[v] || v}</span>`;
  const big = (n) => Number(n).toLocaleString(WT.loc());

  // static text, language switch, links that keep the language
  if (es) {
    if (WT.L.ui.sb_title) document.title = WT.L.ui.sb_title;
    document.querySelectorAll("[data-i18n]").forEach((el) => { const t = WT.L.ui[el.dataset.i18n]; if (t != null) el.innerHTML = t; });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { const t = WT.L.ui[el.dataset.i18nAria]; if (t != null) el.setAttribute("aria-label", t); });
  }
  if (!B) return;
  $("#sb-date").textContent = date(B.asof); $("#sb-date").setAttribute("datetime", B.asof);
  // the templates below are ui keys (sb_sum, sb_n_*); {name} slots are filled from the data
  const fill = (t, o) => t.replace(/\{(\w+)\}/g, (m, k) => (k in o ? o[k] : m));
  const I = B.incognita, R = B.terra, E = I.effect, S = I.scope, C = I.curation, TL = I.by_rival["TALYS-2.24"];
  const DATA = "https://github.com/seth-michael-weaver/incognita/tree/main/docs/walkthrough/data/board";

  // scope, then the summary: what is compared, against what, the cleanest result, the totals and their size
  $("#sb-scope").innerHTML = fill(T("sb_scope", "Neutron-induced reactions from {elo} keV to {ehi} MeV (capture, (n,2n), (n,p), (n,α), fission) and stellar capture: {nuc} nuclides, {rows} scored rows ({vals} distinct measured values; some comparisons reuse rows)."),
    { elo: S.e_lo_kev, ehi: S.e_hi_mev, nuc: big(S.nuclides), rows: big(S.rows), vals: big(S.values) });
  $("#sb-sum").innerHTML = fill(T("sb_sum", "The INCOGNITA engine is compared on measured neutron cross sections with the TALYS-2.24 program it was ported from, two independent codes (CoH3, YAHFC), and this project's reproduction of TENDL's no-data recipe. Against TALYS-2.24 it wins {tw}, ties {tt} and loses {tl}; that edge comes from global rules chosen while watching these comparisons. Over all {n} comparisons, it wins {win}, ties {tie} and loses {loss}. Its error is {emin}–{emax} dex (about {pmin}–{pmax} %) across comparisons; where it wins, its error is typically {wg} dex lower. These are development comparisons, not a blind test. The TERRA data product, an in-sample fit compared with four evaluated libraries, wins {twin}, ties {ttie} and loses {tloss}."),
    { n: I.decided, win: I.WIN, tie: I.TIE, loss: I.LOSS, tw: TL.WIN, tt: TL.TIE, tl: TL.LOSS,
      emin: dex(E.err_min), emax: dex(E.err_max), pmin: E.pct_min, pmax: E.pct_max, wg: dex(E.win_gap),
      twin: R.WIN, ttie: R.TIE, tloss: R.LOSS });
  $("#sb-keep-5").innerHTML = fill(T("sb_keep_5", "The measurements were curated by this project: {exc} of {rows} rows were left out (curation register, documented defects, or estimates), and each capture value is a trust-weighted consensus of EXFOR datasets. All of it is in the <a href=\"{data}\">data package</a>."),
    { exc: big(C.excluded), rows: big(C.rows), data: DATA });
  $("#sb-keep-3").innerHTML = fill(T("sb_keep_3", "Some comparisons reuse the same measurements (for example a second scoring of the same (n,2n) data), so the {n} are not independent; no correction for multiple comparisons is applied."), { n: I.decided });
  // family-wise count (WT.boardFW, in scoreboard.html, from data/board/familywise.csv): a range over two methods
  const FW = WT.boardFW, rng = (a) => a[0] === a[1] ? String(a[0]) : `${a[0]}–${a[1]}`;
  if (FW) {
    const o = { k: rng(FW.views), kc: rng(FW.cells), m: FW.m_views, n: FW.m_cells, w: FW.wins, W: V.WIN };
    $("#sb-keep-3").innerHTML += " " + fill(T("sb_keep_fw", "With a Bonferroni correction for the {m} kinds of measurement, {k} of the {w} wins would remain."), o);
    $("#sb-how-fw").innerHTML = fill(T("sb_how_fw_d", "Bonferroni, for m = {m} kinds of measurement (or all {n} comparisons): a win remains when the interval from the 0.05/2m to the 1 − 0.05/2m percentile of the same 2,000 resamples lies below zero. With 2,000 resamples those percentiles are coarse, so a normal approximation is used as well; the two methods keep {k} of the {w} wins ({kc} over all {n} comparisons). The verdicts on this page are not corrected."), o);
  }
  const KS = I.k_scope;
  if (KS) $("#sb-how-k").innerHTML = fill(T("sb_how_k_d", "Maxwellian-averaged capture cross sections (MACS) at 30 keV, grouped by proton number Z. They are scored on the {kn} nuclides whose compiled value is measured, not estimated ({knt} against TALYS-2.24, which has no stored value for the others). The bands Z &lt; 20 and Z ≥ 84 hold no such nuclide and are not counted."), { kn: KS.n, knt: KS.talys });
  if (es) WT.keepLang();   // after the text above: links inside translated text keep the language too

  // headline tiles and a proportional strip (labels always in text, never colour alone)
  function tiles(el, d) {
    el.innerHTML = ORDER.map((v) => `<div class="sb-tile sb-${v.toLowerCase()}"><div class="sb-n">${d[v]}</div><div class="sb-l">${V[v]}</div></div>`).join("")
      + `<div class="sb-tile sb-of"><div class="sb-n">${d.decided}</div><div class="sb-l">${T("sb_compared", "comparisons")}</div></div>`;
  }
  function strip(el, d) {
    const parts = ORDER.filter((v) => d[v]);
    el.innerHTML = parts.map((v) => `<span class="sb-seg sb-${v.toLowerCase()}" style="flex-grow:${d[v]}" title="${V[v]}: ${d[v]}"></span>`).join("");
    el.setAttribute("aria-label", parts.map((v) => `${d[v]} ${V[v]}`).join(", ") + ` / ${d.decided}`);
  }
  // "No losses" / "The one loss" / "N losses", from the data
  const lossHead = (n) => n === 0 ? T("sb_loss_h", "No losses") : n === 1 ? T("sb_terra_loss_h", "The one loss") : fill(T("sb_loss_hn", "{n} losses"), { n });

  // ---- 1. the engine against other codes
  tiles($("#sb-inc-tiles"), I); strip($("#sb-inc-strip"), I);
  $("#sb-inc-note").innerHTML = fill(T("sb_n_inc", "{na} more comparisons are N/A, not counted: the rival gives no value, 5 or fewer nuclei were measured, or the rival's run failed (error above 1 dex)."), { na: I.NA });
  $("#sb-loss-h").textContent = lossHead(I.LOSS);
  $("#sb-loss-p").innerHTML = I.LOSS
    ? fill(T("sb_n_someloss", "{loss} comparisons are losses; they are listed first below."), { loss: I.LOSS })
    : fill(T("sb_n_noloss", "In {trail} ties the engine is behind on the point estimate, but the 95 % interval contains zero."), { trail: I.by_class.trail });

  // plain names of the comparisons (translations: ui keys sb_g_<cell>) and of the rivals (sb_r_<id>, descriptions sb_rd_<id>)
  const GLOSS = {
    thrA1_np: "(n,p) near threshold", np_FRESH_curated: "(n,p), curated set",
    thrA1_n2n: "(n,2n) near threshold", n2n_step1: "(n,2n) near threshold, second scoring",
    n2n_SELECT: "(n,2n), selected nuclei", n2n_SELECT_RL3: "(n,2n), selected nuclei, second data set",
    thrA1_na: "(n,α) near threshold", na_LOBO9: "(n,α), second scoring", na_SELECT: "(n,α), selected nuclei",
    capture_all: "capture, all", capture_NEAR: "capture, nuclei near stability", capture_FAR: "capture, nuclei far from stability",
    capture_10_100keV: "capture, 10–100 keV", macs_Zge20: "stellar capture (MACS) by temperature, Z ≥ 20",
    fission_SELECT: "fission, selected actinides",
  };
  const gloss = (cell) => {
    const m = /^(?:K\d+|MACS) (.+)$/.exec(cell);
    if (m) return T("sb_g_macs", "stellar capture (MACS), ") + (m[1] === "all" ? T("sb_g_allz", "all Z") : m[1].replace(/^Z(>=|<)?/, (x, op) => "Z " + (op === ">=" ? "≥ " : op ? "< " : "")).replace("-", "⁠–⁠"));
    const s = /^SURR (.+)$/.exec(cell); if (s) return gloss(s[1]) + T("sb_g_surr", ", surrogate measurements");
    const g = GLOSS[cell]; return g ? T("sb_g_" + cell, g) : cell;
  };
  const RN = { "TALYS-2.24": "TALYS-2.24", R_T: "TENDL-style recipe", CoH3: "CoH3", YAHFC: "YAHFC" };
  const RD = { "TALYS-2.24": "the TALYS program, default input", R_T: "our reproduction of TENDL's default recipe, not the TENDL library", CoH3: "version 3.6.1, default input", YAHFC: "version 3.67, default input; no (n,α)" };
  const rk = (r) => r.replace(/[^A-Za-z0-9]/g, "");
  const rname = (r) => T("sb_r_" + rk(r), RN[r] || r);
  const CLS = { trail: T("cls_trail", "engine behind"), parity: T("cls_parity", "about level"), underpowered: T("cls_under", "engine ahead, not resolved") };
  const open = I.open.slice().sort((a, b) => ((b.verdict === "LOSS") - (a.verdict === "LOSS")) || (b.hi - a.hi));   // losses, then closest to a loss
  // the interval as a small bar around zero (Seth 2026-11-06: "much more palatable"); numbers stay in text beside it
  const scale = (cs) => Math.max(...cs.map((c) => Math.max(Math.abs(c.lo), Math.abs(c.hi)))) * 1.08 || 1;
  const span = scale(open);
  const ci = (c, sp = span) => {
    const X = (v) => (50 + 50 * v / sp).toFixed(2);
    return `<span class="sb-ci" aria-hidden="true"><i class="z"></i><i class="bar ${c.verdict.toLowerCase()}" style="left:${X(c.lo)}%;width:${(X(c.hi) - X(c.lo)).toFixed(2)}%"></i><i class="pt" style="left:${X(c.gap)}%"></i></span>`;
  };
  $("#sb-open").insertAdjacentHTML("beforeend",
    `<thead><tr><th scope="col">${T("th_cell", "Comparison")}</th><th scope="col" class="r">${T("th_n", "Nuclei")}</th><th scope="col" class="r">${T("th_ours", "Engine error")}</th><th scope="col" class="r">${T("th_theirs", "Rival error")}</th><th scope="col">${T("th_ci", "95 % interval")}</th><th scope="col">${T("th_verdict", "Verdict")}</th></tr></thead><tbody>`
    + open.map((c) => `<tr><td><div class="sb-cell">${esc(gloss(c.cell))}</div><div class="sb-gl">${T("vs", "vs")} ${esc(rname(c.rival))}</div></td><td class="r">${c.n}</td><td class="r num">${dex(c.ours)}</td><td class="r num">${dex(c.theirs)}</td><td class="sb-citd">${ci(c)}<div class="sb-cin num">${num(c.gap)} <span>[${num(c.lo)}, ${num(c.hi)}]</span></div></td><td class="sb-vd">${badge(c.verdict)}<div class="sb-gl">${CLS[c.cls] || ""}</div></td></tr>`).join("")
    + "</tbody>");

  // wins to read with care: few nuclei (marked †) or an interval ending close to zero; last column: after the correction
  if (FW) {
    const care = FW.care.map((c) => Object.assign({ verdict: "WIN" }, c)).sort((a, b) => (b.small - a.small) || (b.hi - a.hi));
    const sp = scale(care);
    $("#sb-care-cap").innerHTML = fill(T("sb_care_cap", "Wins that rest on {sn} or fewer nuclei (marked †), or whose interval ends within {nz} dex of zero. The last column applies the correction for {m} kinds of measurement, by bootstrap percentiles / normal approximation."),
      { sn: FW.small_n, nz: dex(FW.near_zero), m: FW.m_views });
    const fwv = (c) => c.boot === c.normal ? badge(c.boot) : `${badge(c.boot)} / ${badge(c.normal)}`;
    $("#sb-care").insertAdjacentHTML("beforeend",
      `<thead><tr><th scope="col">${T("th_cell", "Comparison")}</th><th scope="col" class="r">${T("th_n", "Nuclei")}</th><th scope="col" class="r">${T("th_ours", "Engine error")}</th><th scope="col" class="r">${T("th_theirs", "Rival error")}</th><th scope="col">${T("th_ci", "95 % interval")}</th><th scope="col">${T("th_fw", "Corrected")}</th></tr></thead><tbody>`
      + care.map((c) => `<tr><td><div class="sb-cell">${esc(gloss(c.cell))}</div><div class="sb-gl">${T("vs", "vs")} ${esc(rname(c.rival))}</div></td><td class="r">${c.n}${c.small ? " †" : ""}</td><td class="r num">${dex(c.ours)}</td><td class="r num">${dex(c.theirs)}</td><td class="sb-citd">${ci(c, sp)}<div class="sb-cin num">${num(c.gap)} <span>[${num(c.lo)}, ${num(c.hi)}]</span></div></td><td class="sb-vd">${fwv(c)}</td></tr>`).join("")
      + "</tbody>");
  }

  const rivals = ["TALYS-2.24", "R_T", "CoH3", "YAHFC"].filter((r) => I.by_rival[r]);
  const sum = (o, k) => rivals.reduce((s, r) => s + o[r][k], 0);
  const rivalTable = (rows, total, hasNA) =>
    `<thead><tr><th scope="col">${T("th_rival", "Rival")}</th>${ORDER.map((v) => `<th scope="col" class="r">${V[v]}</th>`).join("")}${hasNA ? `<th scope="col" class="r">N/A</th>` : ""}</tr></thead><tbody>`
    + rows.map((r) => `<tr><th scope="row"><span class="sb-rn">${esc(r.name)}</span>${r.desc ? `<div class="sb-gl">${esc(r.desc)}</div>` : ""}</th><td class="r">${r.WIN}</td><td class="r">${r.TIE}</td><td class="r${r.LOSS ? " neg" : ""}">${r.LOSS}</td>${hasNA ? `<td class="r">${r.NA}</td>` : ""}</tr>`).join("")
    + `</tbody><tfoot><tr><th scope="row">${T("total", "All")}</th><td class="r">${total.WIN}</td><td class="r">${total.TIE}</td><td class="r">${total.LOSS}</td>${hasNA ? `<td class="r">${total.NA}</td>` : ""}</tr></tfoot>`;
  $("#sb-rival").insertAdjacentHTML("beforeend", rivalTable(rivals.map((r) => Object.assign({ name: rname(r), desc: T("sb_rd_" + rk(r), RD[r] || "") }, I.by_rival[r])),
    { WIN: sum(I.by_rival, "WIN"), TIE: sum(I.by_rival, "TIE"), LOSS: sum(I.by_rival, "LOSS"), NA: sum(I.by_rival, "NA") }, true));

  if (I.changes.length) {
    const ul = $("#sb-changes"); ul.hidden = false;
    ul.innerHTML = I.changes.map((c) => `<li>${esc(gloss(c.cell))} ${T("vs", "vs")} ${esc(rname(c.rival))}: ${badge(c.from)} → ${badge(c.to)} <span class="num">${num(c.gap)} [${num(c.lo)}, ${num(c.hi)}]</span></li>`).join("");
  }
  $("#sb-src").innerHTML = fill(T("sb_n_src", "Production engine <code>{engine}</code> (<code>{commit}</code>), {date}."),
    { engine: esc(I.engine), commit: esc(I.commit), date: date(I.date) });

  // ---- 2. TERRA against evaluated libraries
  $("#sb-terra-asof").innerHTML = fill(T("sb_terra_asof", "Board of {date}, on an older engine than section 1."), { date: date(R.date) });
  tiles($("#sb-terra-tiles"), R); strip($("#sb-terra-strip"), R);
  const A = R.split.acc, K = R.split.cov;
  $("#sb-terra-split").innerHTML = fill(T("sb_n_tsplit", "Accuracy: {aw} {W}, {at} {T}, {al} {L}. Uncertainty coverage: {cw} {W}, {ct} {T}, {cl} {L}. {na} more comparisons have too few nuclei and are not counted."),
    { aw: A.WIN, at: A.TIE, al: A.LOSS, cw: K.WIN, ct: K.TIE, cl: K.LOSS, na: R.NA, W: V.WIN, T: V.TIE, L: V.LOSS });
  $("#sb-terra-loss-h").textContent = lossHead(R.LOSS);
  const L = R.losses[0];
  $("#sb-terra-loss").innerHTML = L
    ? fill(T("sb_n_loss", "Uncertainty coverage in (n,p) against {rival}: gap {gap} [{lo}, {hi}]. TERRA's (n,p) uncertainty bands are wider than needed: they contain the measurements more often than the stated 68 % and 95 %."),
      { rival: esc(L.rival), gap: num(L.gap, 3), lo: num(L.lo, 3), hi: num(L.hi, 3) })
    : "";
  $("#sb-trival").insertAdjacentHTML("beforeend", rivalTable(R.by_rival.map((r) => Object.assign({ name: r.rival }, r)), R, R.by_rival.every((r) => "NA" in r)));
  const O = R.loso;
  $("#sb-terra-note").innerHTML = fill(T("sb_n_terra", "{n} comparisons are scored leave-one-series-out: TERRA is refitted without the measurement series being judged, while the libraries, which cannot be refitted, stay in-sample. {ncov} of them score uncertainty coverage and {nacc} score capture resonance integrals ({win} {W}, {tie} {T}, {loss} {L}). {same} of the coverage ones equal their in-sample versions, because TERRA does not fit (n,2n) or fission. All other comparisons, thermal cross sections included, are in-sample. A rebuild on the current engine is in progress."),
    { n: O.WIN + O.TIE + O.LOSS, ncov: O.cov, nacc: O.acc, same: O.same, win: O.WIN, tie: O.TIE, loss: O.LOSS, W: V.WIN, T: V.TIE, L: V.LOSS });

  // ---------- summary at the top: one calm row per board (label, counts, a thin proportional bar) ----------
  (function summary() {
    const box = document.querySelector(".sb-hero"); if (!box) return;
    const fwh = FW ? fill(T("sb_fw_head", "{k} {W} after correcting for {m} kinds of measurement"), { k: rng(FW.views), m: FW.m_views, W: V.WIN }) : "";
    const rows = [[I, T("sb_h_eng", "The engine against other codes"), "#sb-inc-h", fwh], [B.terra, T("sb_h_terra", "The data product (an in-sample fit) against evaluated libraries"), "#sb-terra-h", ""]].filter((r) => r[0]);
    box.innerHTML = rows.map(([b, label, href, sub]) => {
      const tot = ORDER.reduce((n, v) => n + (b[v] || 0), 0) || 1;
      return `<a class="sb-sumrow" href="${href}"><div class="sb-sumlab">${esc(label)}${sub ? `<span class="sb-gl" style="display:block;font-weight:400">(${sub})</span>` : ""}</div><div class="sb-sumnums">${ORDER.map((v) => `<span class="sb-${v.toLowerCase()}"><b>${b[v] || 0}</b> ${V[v]}</span>`).join("")}</div>`
        + `<div class="sb-sumbar" role="img" aria-label="${ORDER.map((v) => `${b[v] || 0} ${V[v]}`).join(", ")}">${ORDER.filter((v) => b[v]).map((v) => `<i class="sb-${v.toLowerCase()}" style="flex-grow:${b[v]}"></i>`).join("")}</div></a>`;
    }).join("");
  })();
})();
