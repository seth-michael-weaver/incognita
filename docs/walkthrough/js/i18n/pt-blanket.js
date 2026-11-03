/* Portuguese (pt-PT): blanket (Capítulo 32, manto regenerador e primeira parede) */
WT.L.ch.blanket = {
  num: "Capítulo 32", title: "Manto regenerador e primeira parede", short: "Manto",
  lead: "O trítio quase não existe na natureza. Uma central de D–T tem de produzir o seu a partir do lítio, com os neutrões que o seu plasma gera.",
  html: `
<div class="step">
  <h3>Razão de regeneração de trítio</h3>
  <p>Cada neutrão vagueia até que o lítio o capture e forme um tritão. Cada ponto luminoso é um tritão.</p>
  <div class="ctl"><label for="bk-e">Proporção de lítio-6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Espessura do regenerador (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>fusão</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Multiplicação de neutrões por (n,2n)</h3>
  <p>Um neutrão de 14 MeV que atinge chumbo pode arrancar um segundo neutrão: (n,2n). Compara com o lítio sozinho.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Chumbo–lítio</button> <button class="btn ghost" data-act="li" aria-pressed="false">Só lítio</button></div>
  <div class="ctl"><label for="bk-e2">Proporção de lítio-6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Hélio e hidrogénio na primeira parede</h3>
  <p>A primeira parede recebe o feixe completo de 14 MeV. O hélio e o hidrogénio acumulam-se no seu interior, às taxas que a INCOGNITA calcula.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Aço</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Tungsténio</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Vanádio</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Cobre</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Carga na parede (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Anos</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Secções eficazes: a biblioteca v0.2 da INCOGNITA (<code>library/v0.2/channels_v02.parquet</code>), as mesmas curvas que em <a href="data.html#Fe-56" data-keep-lang>Todos os nuclídeos</a>.</div>
</div>`,
};
