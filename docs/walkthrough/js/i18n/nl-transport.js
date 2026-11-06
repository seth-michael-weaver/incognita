/* Dutch (Nederlands): transport (Neutronentransport en Monte Carlo) */
WT.L.ch.transport = {
  num: "Les 16", title: "Neutronentransport en Monte Carlo", short: "Monte Carlo",
  html: `
<div class="step">
  <h3>De transportvergelijking</h3>
  <p>Exact gehoorzamen de neutronen aan de boltzmannvergelijking voor de hoekflux <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Monte Carlo lost haar op door neutronen één voor één na te spelen: vlieg <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, en verstrooi dan, word ingevangen of veroorzaak splijting.</p>
  <div class="btns"><button class="btn" data-act="trnew">Nieuw neutron</button></div>
</div>
<div class="step">
  <h3>Waar diffusie faalt</h3>
  <p>Diffusie neemt in elke richting bijna dezelfde flux aan. Dat faalt binnen een of twee vrije weglengten van een oppervlak en in sterke absorbeerders. Vergelijk haar met de Monte Carlo-flux in een plaat met een uniforme bron terwijl je de absorptie verhoogt.</p>
  <div class="ctl"><label for="tr-pa">Absorptie Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Machtsiteratie</h3>
  <p>Voor <i>k</i><sub>eff</sub> worden de splijtingsplaatsen van elke generatie de bron van de volgende; <i>k</i> is het aantal opgeslagen plaatsen per gestart neutron. Begin met een slechte gok, elk neutron aan één rand, en kijk hoe de bron zich uitspreidt tot de grondmode.</p>
  <div class="btns"><button class="btn" data-act="trbad">Herstart vanuit een slechte gok</button></div>
</div>
<div class="step">
  <h3>Is de bron geconvergeerd?</h3>
  <p>De shannonentropie <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> van de in vakjes verdeelde bron vlakt af zodra de bron tot rust is gekomen; pas dan worden generaties gemiddeld. De foutmarge op <i>k</i> krimpt als 1/√<i>N</i> met het aantal getelde geschiedenissen.</p>
  <div class="ctl"><label for="tr-n">Geschiedenissen per generatie</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "vacuüm",
  "tap the slab to start neutrons": "tik op de plaat om neutronen te starten",
  "chance to fly at least s:  e^(−Σₜ s)": "kans om minstens s te vliegen:  e^(−Σₜ s)",
  "infinite medium S/Σₐ": "oneindig medium S/Σₐ",
  "Monte Carlo": "Monte Carlo",
  "diffusion": "diffusie",
  "flux": "flux",
  "source entropy H (bits)": "bronentropie H (bits)",
  "k per generation": "k per generatie",
  "illustrative one-group data": "illustratieve eengroepsdata",
  "scatter": "verstrooiing",
  "capture": "invangst",
  "fission": "splijting",
  "leak": "lek",
  "glow: collision density": "gloed: botsingsdichtheid",
  "amber glow: where collisions pile up": "amberkleurige gloed: waar botsingen zich ophopen",
  "{#} free paths": "{#} vrije weglengten",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} vrije weglengten",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "diffusie vs Monte Carlo: +{#} % aan het oppervlak, +{#} % in het midden",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "diffusie vs Monte Carlo: +{#} % aan het oppervlak, {#} % in het midden",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "diffusie vs Monte Carlo: {#} % aan het oppervlak, +{#} % in het midden",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "diffusie vs Monte Carlo: {#} % aan het oppervlak, {#} % in het midden",
  "tap: drop the source there": "tik: zet de bron daar",
  "tap the slab to drop the whole source there": "tik op de plaat om de hele bron daar te zetten",
  "generation {#}": "generatie {#}",
  "source · dashed: fundamental mode": "bron · gestreept: grondmode",
  "fission source · dashed: fundamental mode": "splijtingsbron · gestreept: grondmode",
  "inactive | active": "inactief | actief",
  "inactive  |  active generations": "inactieve  |  actieve generaties",
  "generation {#}: k = {#} · H = {#} bits": "generatie {#}: k = {#} · H = {#} bits",
  "starting…": "start…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} geschiedenissen) · diffusie {#}",
  "{#} generations, averaging starts after {#}": "{#} generaties, middelen begint na {#}",
});
