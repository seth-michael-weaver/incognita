/* French: breeding blanket and first wall (chapter 32) */
WT.L.ch.blanket = {
  num: "Chapitre 32", title: "Couverture tritigène et première paroi", short: "Couverture",
  lead: "Le tritium n'existe presque pas dans la nature. Une centrale D–T doit produire le sien à partir du lithium, avec les neutrons de son plasma.",
  html: `
<div class="step">
  <h3>Taux de régénération du tritium</h3>
  <p>Chaque neutron erre jusqu'à ce que le lithium le capture et produise un triton. Chaque point lumineux est un triton.</p>
  <div class="ctl"><label for="bk-e">Part de lithium 6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Épaisseur de la couverture (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>fusion</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Multiplication des neutrons par (n,2n)</h3>
  <p>Un neutron de 14 MeV qui frappe du plomb peut en arracher un second : (n,2n). Comparez avec le lithium seul.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Plomb–lithium</button> <button class="btn ghost" data-act="li" aria-pressed="false">Lithium seul</button></div>
  <div class="ctl"><label for="bk-e2">Part de lithium 6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Hélium et hydrogène dans la première paroi</h3>
  <p>La première paroi reçoit tout le faisceau de 14 MeV. L'hélium et l'hydrogène s'y accumulent, aux taux que calcule INCOGNITA.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Acier</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Tungstène</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanadium</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Cuivre</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Charge sur la paroi (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Années</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Sections efficaces : bibliothèque v0.2 d'INCOGNITA (<code>library/v0.2/channels_v02.parquet</code>), les mêmes courbes que dans <a href="data.html#Fe-56" data-keep-lang>Tous les nucléides</a>.</div>
</div>`,
};
