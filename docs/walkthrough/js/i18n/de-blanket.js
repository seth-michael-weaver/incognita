/* German (Deutsch): blanket (Kapitel 32, Brutblanket und erste Wand) */
WT.L.ch.blanket = {
  num: "Kapitel 32", title: "Brutblanket und erste Wand", short: "Blanket",
  lead: "Tritium gibt es in der Natur kaum. Ein D–T-Kraftwerk muss sein eigenes aus Lithium erbrüten, mit den Neutronen, die sein Plasma erzeugt.",
  html: `
<div class="step">
  <h3>Tritiumbrutrate</h3>
  <p>Jedes Neutron wandert umher, bis Lithium es einfängt und daraus ein Triton macht. Jeder leuchtende Punkt ist ein Triton.</p>
  <div class="ctl"><label for="bk-e">Anteil Lithium-6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Tiefe des Brutmaterials (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>Fusion</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Neutronenvervielfachung durch (n,2n)</h3>
  <p>Ein 14-MeV-Neutron, das auf Blei trifft, kann ein zweites Neutron herausschlagen: (n,2n). Vergleiche mit Lithium allein.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Blei–Lithium</button> <button class="btn ghost" data-act="li" aria-pressed="false">Nur Lithium</button></div>
  <div class="ctl"><label for="bk-e2">Anteil Lithium-6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Helium und Wasserstoff in der ersten Wand</h3>
  <p>Die erste Wand bekommt den vollen 14-MeV-Strahl ab. Helium und Wasserstoff sammeln sich darin an, mit den Raten, die INCOGNITA berechnet.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Stahl</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Wolfram</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanadium</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Kupfer</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Wandbelastung (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Jahre</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Wirkungsquerschnitte: INCOGNITAs Bibliothek v0.2 (<code>library/v0.2/channels_v02.parquet</code>), dieselben Kurven wie unter <a href="data.html#Fe-56" data-keep-lang>Alle Nuklide</a>.</div>
</div>`,
};
