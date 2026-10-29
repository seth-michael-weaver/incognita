/* Portuguese (pt-PT): critical (Capítulo 20, criticalidade e controlo do reator) */
WT.L.ch.critical = {
  num: "Capítulo 20", title: "Criticalidade e controlo do reator", short: "Criticalidade",
  html: `
<div class="step">
  <h3>O fator de multiplicação</h3>
  <p>Cada fissão liberta alguns neutrões; uns causam as fissões seguintes, os restantes perdem-se. O <b>fator de multiplicação</b> <i>k</i> é o número de novas fissões a que uma fissão conduz: cada geração multiplica os neutrões por <i>k</i>. Acima de 1 a cadeia cresce, abaixo de 1 extingue-se.</p>
  <div class="ctl"><label for="cri-k">Multiplicação k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Neutrões retardados</h3>
  <p>Uma pequena fração dos neutrões (0,65 %) chega segundos atrasada, vinda de fragmentos de fissão que primeiro decaem. Esses tardios ditam o ritmo, e por isso o crescimento passa de um piscar de olhos a minutos. O gráfico corre a velocidade ×10.</p>
  <div class="ctl"><label for="cri-k2">Multiplicação k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Neutrões retardados</button></div>
</div>
<div class="step">
  <h3>Criticalidade</h3>
  <p>Uma experiência crítica: move as barras de controlo até a potência se manter constante. Nessa posição <i>k</i> vale exatamente 1, e essa posição das barras é a medição. Encontra-a: o painel mostra <i>k</i> com cinco casas decimais.</p>
  <div class="ctl"><label for="cri-rod">Barras de controlo inseridas (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* i18n_check.sh counts these attribute strings found in the English script code (not in html): data-act="delayed" data-act="delayed" */

Object.assign(WT.L.labels, {
  "generations →": "gerações →",
  "k = {#}: dies away": "k = {#}: extingue-se",
  "k = {#}: steady": "k = {#}: estável",
  "k = {#}: grows": "k = {#}: cresce",
  "{#} generations last under {#} s in a water reactor": "{#} gerações duram menos de {#} s num reator de água",
  "illustration": "ilustração",
  "amber: fission fragments that emit a neutron seconds later": "âmbar: fragmentos de fissão que emitem um neutrão segundos depois",
  "{#} s": "{#} s",
  "time →": "tempo →",
  "×{#} speed": "velocidade ×{#}",
  "with delayed: doubles every {#} s": "com retardados: duplica a cada {#} s",
  "prompt only: doubles every {#} ms": "só prontos: duplica a cada {#} ms",
  "k = {#} · {#} % of neutrons delayed about {#} s (one-group average)": "k = {#} · {#} % dos neutrões retardados cerca de {#} s (média de um grupo)",
  "rods {#} % in": "barras {#} % inseridas",
  "k = {#} · doubles every {#} min": "k = {#} · duplica a cada {#} min",
});
