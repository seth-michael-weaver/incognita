/* Renderer for the TERRA section (WT.terra2). Uses textContent only. */
(function () {
  const T = (window.WT || {}).terra2; if (!T) return;
  const pct = (v) => (v * 100).toFixed(1) + ' %';
  const f1 = (v) => (+v).toFixed(1);
  const el = (tag, txt, cls) => { const e = document.createElement(tag); if (txt != null) e.textContent = txt; if (cls) e.className = cls; return e; };
  const asof = document.getElementById('sb-terra2-asof'); if (asof) asof.textContent = 'As of ' + T.asof + ' · ' + T.points.toLocaleString() + ' measured points in ' + T.cells.toLocaleString() + ' comparisons';
  const tiles = document.getElementById('sb-terra2-tiles');
  if (tiles) {
    const H = T.headline;
    const add = (big, lab) => { const t = el('div', null, 'sb-tile'); t.appendChild(el('div', big, 'sb-n')); t.appendChild(el('div', lab, 'sb-l')); tiles.appendChild(t); };
    add(pct(H.share_points_beat_every_rival), 'of measured points: TERRA closer than all four libraries');
    add(f1(H.pooled_chi2_terra), 'TERRA average error (chi-squared per point; best library on each comparison: ' + f1(H.pooled_chi2_best_rival) + ')');
  }
  const tb = document.getElementById('sb-t2rival');
  if (tb) {
    const head = el('tr'); ['Library', 'TERRA closer', 'About equal', 'Library closer', 'TERRA error', 'Library error'].forEach((h) => head.appendChild(el('th', h)));
    const thead = el('thead'); thead.appendChild(head); tb.appendChild(thead);
    const body = el('tbody');
    for (const r of T.rivals) {
      const tr = el('tr');
      [r.rival, pct(r.share_points_closer), pct(r.share_points_tie), pct(r.share_points_behind),
       f1(T.headline.pooled_chi2_terra_on_rival_cells[r.rival]), f1(T.headline.pooled_chi2_rival_same_cells[r.rival])].forEach((v, i) => tr.appendChild(el(i ? 'td' : 'th', v, i ? 'num' : null)));
      body.appendChild(tr);
    }
    tb.appendChild(body);
  }
  const fam = document.getElementById('sb-terra2-fam');
  if (fam) for (const f of T.families) {
    const row = el('div', null, 'sb-fam-row');
    row.appendChild(el('span', f.family, 'sb-fam-lab'));
    const bar = el('span', null, 'sb-fam-bar'); bar.style.width = (f.share_points_closer_than_VIII1 * 100).toFixed(1) + '%';
    row.appendChild(bar); row.appendChild(el('span', pct(f.share_points_closer_than_VIII1), 'sb-fam-val'));
    fam.appendChild(row);
  }
  const ten = document.getElementById('sb-terra2-tension');
  if (ten) ten.textContent = pct(T.tension.share_points) + ' of measured points sit in comparisons where the laboratories disagree beyond their stated uncertainties (' + T.tension.cells.toLocaleString() + ' comparisons); no single curve can match all of them.';
})();
