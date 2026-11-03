/* Italian: blanket (Capitolo 32, mantello triziogeno e prima parete) */
WT.L.ch.blanket = {
  num: "Capitolo 32", title: "Mantello triziogeno e prima parete", short: "Mantello",
  lead: "Il trizio quasi non esiste in natura. Un impianto D–T deve produrre da sé il proprio a partire dal litio, usando i neutroni generati dal suo plasma.",
  html: `
<div class="step">
  <h3>Rapporto di triziogenesi</h3>
  <p>Ogni neutrone vaga finché il litio non lo cattura e produce un tritone. Ogni punto luminoso è un tritone.</p>
  <div class="ctl"><label for="bk-e">Quota di litio-6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Spessore del fertilizzante (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>fusione</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Moltiplicazione dei neutroni per (n,2n)</h3>
  <p>Un neutrone da 14 MeV che colpisce il piombo può farne uscire un secondo: (n,2n). Confronta con il solo litio.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Piombo–litio</button> <button class="btn ghost" data-act="li" aria-pressed="false">Solo litio</button></div>
  <div class="ctl"><label for="bk-e2">Quota di litio-6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Elio e idrogeno nella prima parete</h3>
  <p>La prima parete riceve in pieno il fascio da 14 MeV. Elio e idrogeno vi si accumulano dentro, ai ritmi calcolati da INCOGNITA.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Acciaio</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Tungsteno</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanadio</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Rame</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Carico sulla parete (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Anni</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Sezioni d'urto: la libreria v0.2 di INCOGNITA (<code>library/v0.2/channels_v02.parquet</code>), le stesse curve di <a href="data.html#Fe-56" data-keep-lang>Ogni nuclide</a>.</div>
</div>`,
};
