/* Portuguese (pt-PT): doppler (Capítulo 19, alargamento de Doppler) */
WT.L.ch.doppler = {
  num: "Capítulo 19", title: "Alargamento de Doppler", short: "Doppler",
  html: `
<div class="step">
  <h3>Agitação térmica do alvo</h3>
  <p>Combustível mais quente: os seus átomos agitam-se mais depressa. Cada átomo de urânio já não está parado quando chega um neutrão.</p>
  <div class="ctl"><label for="dop-t1">Temperatura do combustível (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Alargamento de Doppler</h3>
  <p>A curva é a probabilidade de o urânio-238 captar um neutrão, em função da energia do neutrão. A sua altura é uma área-alvo em <b>barns</b> (um barn é 10<sup>−24</sup> cm², aproximadamente o tamanho que um núcleo mostra a um neutrão). Como os átomos se movem, uns encontram o neutrão de frente e outros fogem dele, e por isso o pico estreito esbate-se: mais baixo e mais largo. A sua área mantém-se.</p>
  <div class="ctl"><label for="dop-t2">Temperatura do combustível (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Autoblindagem das ressonâncias</h3>
  <p>Uma pastilha de combustível é espessa. A faixa sombreada é a fração de neutrões que ela trava em cada energia. O centro do pico já trava tudo, quente ou frio, pelo que um pico mais baixo nada perde aí; as asas mais largas apanham mais. Perdem-se mais neutrões por captura em vez de causarem fissão, e assim <i>k</i> desce por si só. (<i>k</i> é o número de novas fissões a que cada fissão conduz; o Capítulo <a href="#critical">21</a> explica-o.)</p>
  <div class="ctl"><label for="dop-t3">Temperatura do combustível (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "átomos de urânio no combustível",
  "{#} K": "{#} K",
  "caught in the peak": "apanhados no pico",
  "k": "k",
  "neutron energy (eV) →": "energia do neutrão (eV) →",
  "capture cross section": "secção eficaz de captura",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "pico {#}k barns · largura Doppler {#} meV · área inalterada",
  "all stopped": "todos travados",
  "wider wings catch more": "as asas mais largas apanham mais",
  "share of neutrons stopped in the fuel": "fração de neutrões travados no combustível",
  "the peak's centre already stops everything; the wider wings catch more": "o centro do pico já trava tudo; as asas mais largas apanham mais",
});
