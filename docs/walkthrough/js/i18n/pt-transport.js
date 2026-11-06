/* Portuguese (pt-PT): transport (Lição 1, transporte de neutrões e Monte Carlo) */
WT.L.ch.transport = {
  num: "Lição 1", title: "Transporte de neutrões e Monte Carlo", short: "Monte Carlo",
  html: `
<div class="step">
  <h3>A equação de transporte</h3>
  <p>Em rigor, os neutrões obedecem à equação de Boltzmann para o fluxo angular <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. O Monte Carlo resolve-a jogando com os neutrões um de cada vez: voar <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, e depois dispersar-se, ser capturado ou provocar uma fissão.</p>
  <div class="btns"><button class="btn" data-act="trnew">Novo neutrão</button></div>
</div>
<div class="step">
  <h3>Onde a difusão falha</h3>
  <p>A difusão supõe um fluxo quase igual em todas as direções. Isso falha a um ou dois livres percursos de uma superfície e em absorventes fortes. Compara-a com o fluxo de Monte Carlo numa placa com uma fonte uniforme enquanto aumentas a absorção.</p>
  <div class="ctl"><label for="tr-pa">Absorção Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Iteração de potência</h3>
  <p>Para obter <i>k</i><sub>eff</sub>, os locais de fissão de cada geração tornam-se a fonte da geração seguinte; <i>k</i> é o número de locais guardados por neutrão lançado. Parte de uma má estimativa, todos os neutrões num dos bordos, e vê a fonte espalhar-se até ao modo fundamental.</p>
  <div class="btns"><button class="btn" data-act="trbad">Recomeçar de uma má estimativa</button></div>
</div>
<div class="step">
  <h3>A fonte convergiu?</h3>
  <p>A entropia de Shannon <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> da fonte repartida por intervalos estabiliza quando a fonte assenta; só então se faz a média das gerações. A barra de erro de <i>k</i> diminui como 1/√<i>N</i> com as histórias contadas.</p>
  <div class="ctl"><label for="tr-n">Histórias por geração</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "vácuo",
  "glow: collision density": "brilho: densidade de colisões",
  "amber glow: where collisions pile up": "brilho âmbar: onde as colisões se acumulam",
  "tap the slab to start neutrons": "toca na placa para lançar neutrões",
  "scatter": "dispersão",
  "capture": "captura",
  "fission": "fissão",
  "leak": "fuga",
  "chance to fly at least s:  e^(−Σₜ s)": "probabilidade de voar pelo menos s:  e^(−Σₜ s)",
  "{#} free paths": "{#} livres percursos",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} livres percursos",
  "infinite medium S/Σₐ": "meio infinito S/Σₐ",
  "Monte Carlo": "Monte Carlo",
  "diffusion": "difusão",
  "flux": "fluxo",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "difusão vs Monte Carlo: +{#} % à superfície, +{#} % no centro",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "difusão vs Monte Carlo: +{#} % à superfície, {#} % no centro",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "difusão vs Monte Carlo: {#} % à superfície, +{#} % no centro",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "difusão vs Monte Carlo: {#} % à superfície, {#} % no centro",
  "tap: drop the source there": "toca: põe lá a fonte",
  "tap the slab to drop the whole source there": "toca na placa para pôr lá toda a fonte",
  "generation {#}": "geração {#}",
  "source · dashed: fundamental mode": "fonte · tracejado: modo fundamental",
  "fission source · dashed: fundamental mode": "fonte de fissão · tracejado: modo fundamental",
  "source entropy H (bits)": "entropia da fonte H (bits)",
  "inactive | active": "inativas | ativas",
  "inactive  |  active generations": "gerações inativas  |  ativas",
  "k per generation": "k por geração",
  "generation {#}: k = {#} · H = {#} bits": "geração {#}: k = {#} · H = {#} bits",
  "starting…": "a iniciar…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} histórias) · difusão {#}",
  "{#} generations, averaging starts after {#}": "{#} gerações, a média começa após {#}",
  "illustrative one-group data": "dados ilustrativos a um grupo",
});
