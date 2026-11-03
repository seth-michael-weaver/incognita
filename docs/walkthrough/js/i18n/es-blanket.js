/* Spanish: blanket (chapter 32, breeding blanket and first wall) */
WT.L.ch.blanket = {
  num: "Capítulo 32", title: "Manto regenerador y primera pared", short: "Manto",
  lead: "El tritio apenas existe en la naturaleza. Una central de D–T debe producir el suyo a partir del litio, con los neutrones que genera su plasma.",
  html: `
<div class="step">
  <h3>Tasa de regeneración de tritio</h3>
  <p>Cada neutrón vaga hasta que el litio lo captura y forma un tritón. Cada punto luminoso es un tritón.</p>
  <div class="ctl"><label for="bk-e">Proporción de litio-6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Espesor del regenerador (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>fusión</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Multiplicación de neutrones por (n,2n)</h3>
  <p>Un neutrón de 14 MeV que choca con plomo puede arrancar un segundo neutrón: (n,2n). Compáralo con el litio solo.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Plomo–litio</button> <button class="btn ghost" data-act="li" aria-pressed="false">Solo litio</button></div>
  <div class="ctl"><label for="bk-e2">Proporción de litio-6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Helio e hidrógeno en la primera pared</h3>
  <p>La primera pared recibe todo el haz de 14 MeV. El helio y el hidrógeno se acumulan dentro de ella, a las tasas que calcula INCOGNITA.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Acero</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Wolframio</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanadio</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Cobre</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Carga en la pared (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Años</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Secciones eficaces: la biblioteca v0.2 de INCOGNITA (<code>library/v0.2/channels_v02.parquet</code>), las mismas curvas que en <a href="data.html#Fe-56" data-keep-lang>Todos los núclidos</a>.</div>
</div>`,
};
