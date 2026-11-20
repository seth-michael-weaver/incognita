/* Renderer for the TERRA section (WT.terra2). Uses textContent only. */
(function () {
  const T = (window.WT || {}).terra2; if (!T) return;
  const H = T.headline;
  const pct = (v, d = 1) => (v * 100).toFixed(d) + ' %';
  const f1 = (v) => (+v).toFixed(1);
  const el = (tag, txt, cls) => { const e = document.createElement(tag); if (txt != null) e.textContent = txt; if (cls) e.className = cls; return e; };

  const asof = document.getElementById('sb-terra2-asof');
  if (asof) asof.textContent = 'Comparison of ' + T.asof + ' · ' + T.points.toLocaleString('en') + ' measured points in ' + T.cells.toLocaleString('en') + ' comparisons';

  // Headline tiles: a number, a short label, one plain sentence under it.
  const tiles = document.getElementById('sb-terra2-tiles');
  if (tiles) {
    const tile = (big, lab, sub, cls) => {
      const t = el('div', null, 'sb-tile' + (cls ? ' ' + cls : ''));
      t.appendChild(el('div', big, 'sb-n'));
      t.appendChild(el('div', lab, 'sb-l'));
      if (sub) t.appendChild(el('div', sub, 'sb-t2-sub'));
      tiles.appendChild(t);
    };
    tile(pct(H.share_points_beat_every_rival), 'Closer than all four', 'Share of measured points where TERRA is closer than every library.', 'sb-win');
    tile(f1(H.pooled_chi2_terra), 'TERRA χ² per point', 'Best library on each comparison: ' + f1(H.pooled_chi2_best_rival) + '. Lower is better.');
    tile(pct(T.tension.share_points, 0), 'In disputed data', 'Points where laboratories disagree beyond their stated uncertainties.', 'sb-tie');
  }

  // Head to head: one row per library, with a split bar.
  const tb = document.getElementById('sb-t2rival');
  if (tb) {
    const thead = el('thead'); const hr = el('tr');
    [['Library', ''], ['Split of measured points', ''], ['TERRA closer', 'r'], ['About equal', 'r'], ['Library closer', 'r'], ['χ²: TERRA / library', 'r']]
      .forEach(([h, c]) => hr.appendChild(el('th', h, c || null)));
    thead.appendChild(hr); tb.appendChild(thead);
    const body = el('tbody');
    for (const r of T.rivals) {
      const tr = el('tr');
      tr.appendChild(el('th', r.rival, 'sb-t2-lib'));
      const cell = el('td', null, 'sb-t2-splitcell');
      const bar = el('div', null, 'sb-strip sb-t2-split');
      bar.setAttribute('role', 'img');
      bar.setAttribute('aria-label', 'TERRA closer ' + pct(r.share_points_closer) + ', about equal ' + pct(r.share_points_tie) + ', ' + r.rival + ' closer ' + pct(r.share_points_behind));
      [['sb-win', r.share_points_closer], ['sb-tie', r.share_points_tie], ['sb-loss', r.share_points_behind]].forEach(([c, v]) => {
        const s = el('span', null, 'sb-seg ' + c); s.style.flexGrow = String(v); bar.appendChild(s);
      });
      cell.appendChild(bar); tr.appendChild(cell);
      [pct(r.share_points_closer), pct(r.share_points_tie), pct(r.share_points_behind)].forEach((v) => tr.appendChild(el('td', v, 'num r')));
      const ours = H.pooled_chi2_terra_on_rival_cells[r.rival], theirs = H.pooled_chi2_rival_same_cells[r.rival];
      const td = el('td', null, 'num r');
      td.appendChild(el('span', f1(ours), ours > theirs ? 'neg' : 'sb-t2-good'));
      td.appendChild(document.createTextNode(' / ' + f1(theirs)));
      tr.appendChild(td);
      body.appendChild(tr);
    }
    tb.appendChild(body);
  }

  // By kind of reaction: share of points closer than ENDF/B-VIII.1, with a 50 % mark.
  const fam = document.getElementById('sb-terra2-fam');
  if (fam) for (const f of T.families) {
    const row = el('div', null, 'sb-fam-row');
    row.appendChild(el('span', f.family, 'sb-fam-lab'));
    const track = el('span', null, 'sb-fam-track');
    const fill = el('span', null, 'sb-fam-fill'); fill.style.width = (f.share_points_closer_than_VIII1 * 100).toFixed(1) + '%';
    track.appendChild(fill); track.appendChild(el('span', null, 'sb-fam-mid'));
    row.appendChild(track);
    row.appendChild(el('span', pct(f.share_points_closer_than_VIII1, 0), 'sb-fam-val'));
    row.appendChild(el('span', f.points.toLocaleString('en') + ' pts', 'sb-fam-n'));
    fam.appendChild(row);
  }

  const ten = document.getElementById('sb-terra2-tension');
  if (ten) ten.textContent = T.tension.cells.toLocaleString('en') + ' comparisons, holding ' + pct(T.tension.share_points) + ' of the measured points, have laboratories that disagree with each other beyond their stated uncertainties. No single curve can match all of those points, so a share of them is out of reach for TERRA and for every library.';
})();
