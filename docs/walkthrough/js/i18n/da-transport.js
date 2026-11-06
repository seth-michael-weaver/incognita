/* Danish: transport (Neutrontransport og Monte Carlo) */
WT.L.ch.transport = {
  num: "Lektion 16", title: "Neutrontransport og Monte Carlo", short: "Monte Carlo",
  html: `
<div class="step">
  <h3>Transportligningen</h3>
  <p>Eksakt adlyder neutronerne Boltzmann-ligningen for vinkelfluxen <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Monte Carlo løser den ved at spille neutronerne én ad gangen: flyv <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, og spred så, bliv indfanget eller giv fission.</p>
  <div class="btns"><button class="btn" data-act="trnew">Ny neutron</button></div>
</div>
<div class="step">
  <h3>Hvor diffusion svigter</h3>
  <p>Diffusion antager næsten den samme flux i alle retninger. Det svigter inden for en fri vejlængde eller to fra en overflade og i stærke absorbere. Sammenlign den med Monte Carlo-fluxen i en plade med en jævn kilde, mens du hæver absorptionen.</p>
  <div class="ctl"><label for="tr-pa">Absorption Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Potensiteration</h3>
  <p>For <i>k</i><sub>eff</sub> bliver hver generations fissionssteder kilden for den næste; <i>k</i> er antallet af gemte steder pr. startet neutron. Start fra et dårligt gæt, hver neutron ved den ene kant, og se kilden brede sig ud til grundmoden.</p>
  <div class="btns"><button class="btn" data-act="trbad">Genstart fra et dårligt gæt</button></div>
</div>
<div class="step">
  <h3>Er kilden konvergeret?</h3>
  <p>Shannon-entropien <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> af den inddelte kilde flader ud, når kilden er faldet til ro; først da midles generationerne. Fejlmarginen på <i>k</i> skrumper som 1/√<i>N</i> med antallet af talte historier.</p>
  <div class="ctl"><label for="tr-n">Historier pr. generation</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "vacuum": "vakuum",
  "tap the slab to start neutrons": "tryk på pladen for at starte neutroner",
  "chance to fly at least s:  e^(−Σₜ s)": "chance for at flyve mindst s:  e^(−Σₜ s)",
  "infinite medium S/Σₐ": "uendeligt medium S/Σₐ",
  "Monte Carlo": "Monte Carlo",
  "diffusion": "diffusion",
  "flux": "flux",
  "source entropy H (bits)": "kildeentropi H (bit)",
  "k per generation": "k pr. generation",
  "illustrative one-group data": "illustrative engruppedata",
  "scatter": "spredning",
  "capture": "indfangning",
  "fission": "fission",
  "leak": "lækage",
  "glow: collision density": "glød: stødtæthed",
  "amber glow: where collisions pile up": "ravfarvet glød: hvor stødene hober sig op",
  "{#} free paths": "{#} frie vejlængder",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} frie vejlængder",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "diffusion vs Monte Carlo: +{#} % ved overfladen, +{#} % i midten",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "diffusion vs Monte Carlo: +{#} % ved overfladen, {#} % i midten",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "diffusion vs Monte Carlo: {#} % ved overfladen, +{#} % i midten",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "diffusion vs Monte Carlo: {#} % ved overfladen, {#} % i midten",
  "tap: drop the source there": "tryk: sæt kilden dér",
  "tap the slab to drop the whole source there": "tryk på pladen for at sætte hele kilden dér",
  "generation {#}": "generation {#}",
  "source · dashed: fundamental mode": "kilde · stiplet: grundmode",
  "fission source · dashed: fundamental mode": "fissionskilde · stiplet: grundmode",
  "inactive | active": "inaktiv | aktiv",
  "inactive  |  active generations": "inaktive  |  aktive generationer",
  "generation {#}: k = {#} · H = {#} bits": "generation {#}: k = {#} · H = {#} bit",
  "starting…": "starter…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} historier) · diffusion {#}",
  "{#} generations, averaging starts after {#}": "{#} generationer, midling starter efter {#}",
});
