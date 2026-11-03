/* Danish: breeding blanket and first wall (chapter 32) */
WT.L.ch.blanket = {
  num: "Kapitel 32", title: "Avlskappe og første væg", short: "Avlskappe",
  lead: "Tritium findes næsten ikke i naturen. Et D–T-kraftværk må avle sit eget af lithium med de neutroner, som dets plasma laver.",
  html: `
<div class="step">
  <h3>Tritiumavlsforholdet</h3>
  <p>Hver neutron vandrer, indtil lithium fanger den og laver en triton. Hver lysende prik er én triton.</p>
  <div class="ctl"><label for="bk-e">Lithium-6-andel (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Avlslagets dybde (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>fusion</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Neutronmultiplikation ved (n,2n)</h3>
  <p>En 14 MeV-neutron, der rammer bly, kan slå endnu en neutron løs: (n,2n). Sammenlign med lithium alene.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Bly–lithium</button> <button class="btn ghost" data-act="li" aria-pressed="false">Kun lithium</button></div>
  <div class="ctl"><label for="bk-e2">Lithium-6-andel (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Helium og brint i den første væg</h3>
  <p>Den første væg tager hele 14 MeV-strålen. Helium og brint ophobes inde i den med de rater, INCOGNITA beregner.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Stål</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Wolfram</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanadium</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Kobber</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Vægbelastning (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">År</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Tværsnit: INCOGNITAs bibliotek v0.2 (<code>library/v0.2/channels_v02.parquet</code>), de samme kurver som i <a href="data.html#Fe-56" data-keep-lang>Alle nuklider</a>.</div>
</div>`,
};
