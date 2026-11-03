/* Dutch (Nederlands): blanket (Hoofdstuk 32, kweekmantel en eerste wand) */
WT.L.ch.blanket = {
  num: "Hoofdstuk 32", title: "Kweekmantel en eerste wand", short: "Kweekmantel",
  lead: "Tritium bestaat in de natuur nauwelijks. Een D–T-centrale moet zijn eigen tritium kweken uit lithium, met de neutronen die zijn plasma maakt.",
  html: `
<div class="step">
  <h3>Tritiumkweekverhouding</h3>
  <p>Elk neutron dwaalt rond tot lithium het vangt en er een triton van maakt. Elk gloeiend puntje is één triton.</p>
  <div class="ctl"><label for="bk-e">Aandeel lithium-6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Dikte kweeklaag (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>fusie</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Neutronenvermenigvuldiging door (n,2n)</h3>
  <p>Een neutron van 14 MeV dat lood raakt, kan er een tweede neutron uitslaan: (n,2n). Vergelijk met alleen lithium.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Lood–lithium</button> <button class="btn ghost" data-act="li" aria-pressed="false">Alleen lithium</button></div>
  <div class="ctl"><label for="bk-e2">Aandeel lithium-6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Helium en waterstof in de eerste wand</h3>
  <p>De eerste wand vangt de volle bundel van 14 MeV. Helium en waterstof hopen zich erin op, met de snelheden die INCOGNITA berekent.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Staal</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Wolfraam</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanadium</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Koper</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Wandbelasting (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Jaren</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Werkzame doorsneden: bibliotheek v0.2 van INCOGNITA (<code>library/v0.2/channels_v02.parquet</code>), dezelfde curven als bij <a href="data.html#Fe-56" data-keep-lang>Alle nucliden</a>.</div>
</div>`,
};
