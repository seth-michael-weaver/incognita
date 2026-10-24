/* Danish: exciton (chapter 17, Expert) */
WT.L.ch.exciton = {
  num: "Kapitel 17", title: "Excitonmodellen i tal", short: "Excitonmodel",
  lead: "Kapitel 4 fulgte én hurtig neutron gennem nogle få kollisioner. Her er de rater, der på hvert trin afgør, om det næste bliver endnu en kollision eller en udsendelse, og det spektrum, de lægges sammen til.",
  html: `
<div class="step">
  <h3>Optælling af partikel–hul-tilstande</h3>
  <p>Excitonmodellen inddeler kernen på vej mod ligevægt efter dens antal exciterede partikler <i>p</i> og huller <i>h</i>, <i>n</i> = <i>p</i> + <i>h</i>. En neutron, der går ind i en targetkerne, starter ved <i>p</i> = 1, <i>h</i> = 0; hver kollision tilføjer et par. Det, der betyder noget på hvert trin, er, på hvor mange måder energien kan deles mellem de <i>n</i> excitoner: partikel–hul-tilstandstætheden.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Partikler p (huller p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Pauli-korrektion</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ er tætheden af enkeltpartikelniveauer nær Fermienergien. <i>A<sub>p,h</sub></i> er <b>Pauli</b>-korrektionen: to partikler kan ikke dele et niveau, så de laveste konfigurationer koster energi, og tætheden nær tærsklen falder. Skitsen viser én konfiguration ad gangen med det valgte <i>p</i>, trukket tilfældigt.</p>
</div>
<div class="step">
  <h3>Dybere ind eller ud</h3>
  <p>Fra hvert trin kan der ske to ting. En kollision skaber endnu et par med raten λ<sup>+</sup>, som efter Fermis gyldne regel er det kvadrerede matrixelement gange tætheden af de tilstande, den kan nå. Eller en partikel forlader kernen med raten <i>W</i>, givet ved detaljeret balance ud fra det inverse tværsnit og forholdet mellem tilstandstæthederne med og uden den udsendte partikel.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Neutronenergi (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Søjlerne er de to rater på hvert trin, på en logaritmisk skala: λ<sup>+</sup> af størrelsesordenen 10²² s⁻¹, <i>W</i> omkring en tiendedel af den på første trin og faldende for hvert trin, da hvert nyt par udtynder den energi, den førende partikel kan bære. Motoren tager M² fra Koning–Duijvestijn-formen, der falder med energien pr. exciton:</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>Kæden i tid</h3>
  <p>Ser man bort fra de sjældne kollisioner, der fjerner et par (<b>never-come-back-approksimationen</b>), adlyder populationerne en simpel kæde: hvert trin fyldes fra det foregående og tømmes ind i det næste og ud i kontinuet. Søjlerne kører denne masterligning; tiden er i enheder af 10⁻²² s.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Neutronenergi (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Hele kæden er overstået på nogle få 10⁻²² s. Den andel, der slipper ud undervejs, er præligevægtsemissionen; resten overdrages, efter højst seks partikler i motoren ligesom i TALYS, til compoundkernen. Tidsintegrationen giver hvert trin en styrke τ(<i>n</i>)·<i>P</i>(<i>n</i>), og det er dette produkt, motoren beregner.</p>
</div>
<div class="step">
  <h3>Hvor den hårde hale kommer fra</h3>
  <p>Emissionsspektret er summen over trinene af population gange levetid gange emissionsrate plus fordampningen af det, der er tilbage. Trinnet <i>n</i> = 3 alene, to partikler og ét hul, når de højeste udgående energier: dets spektrum falder kun lineært mod endepunktet. Hvert senere trin er blødere.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + fordampning</div>
  <div class="ctl"><label for="ex-e3">Neutronenergi (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Hæv energien, og spektret bliver hårdere: præligevægtshalen strækker sig ud til endepunktet, mens fordampningspuklen bliver ved 1 til 2 MeV. Over omkring 10 MeV kan de målte højenergetiske neutroner kun gengives med denne hale.</p>
</div>
<div class="step">
  <h3>Hvor stor en andel</h3>
  <p>Den andel af emissionen, der er præligevægt, vokser med den indkommende energi, fra nogle få procent nær 5 MeV til omkring 40 procent ved 40 MeV her. Den afhænger af én justerbar konstant, matrixelementets samlede størrelse: en svagere vekselvirkning betyder langsommere ligevægtsindstilling og mere tidlig emission.</p>
  <div class="ctl"><label for="ex-c">Matrixelementkonstant C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>Den stiplede kurve er C₁ = 1, motorens standard; den fuldt optrukne følger skyderen. En halvering af C₁ hæver andelen med en faktor 1,5 til 1,9, ikke 2: hvert trins udslipssandsynlighed er W/(λ<sup>+</sup> + W), ikke W/λ<sup>+</sup>, og færre kerner overlever til de senere trin.</p>
</div>
<div class="step">
  <h3>To komponenter og et andet udslip</h3>
  <p>Motoren følger protoner og neutroner hver for sig (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), med forskellige matrixelementer for ens og uens par, en reduceret brønddybde for den første kollision nær overfladen og Kalbachs regler for klynger. Over 20 MeV lader den også restkernen, som stadig rummer excitoner, udsende en anden hurtig partikel, før den når ligevægt.</p>
  <div class="ctl"><label for="ex-e4">Neutronenergi (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Kurven er en legetøjsudgave af det: efter en første udsendelse fra trinnet med tre excitoner, sandsynligheden for, at restkernens tilbageværende partikel slipper ud før sin næste kollision. Den forbliver lille under 20 MeV og vokser derover, og det er dér, motoren slår multipel præligevægt til.</p>
  <div class="aside">I koden: <code>density/particle_hole.py</code> (Williams-tætheder, Pauli- og endelig-brønd-korrektioner, én og to komponenter), <code>preeq/exciton.py</code> (matrixelementer, emissions- og overgangsrater, levetider, never-come-back-løsningen), <code>preeq/complex.py</code> (Kalbachs pickup, stripping og knockout), <code>preeq/multi.py</code> (multipel præligevægt, som standard fra 20 MeV). Billedet er énkomponent med et skematisk inverst tværsnit for en jern-56-lignende targetkerne.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: state densities
  "E (MeV)": "E (MeV)",
  "ω(p, h, E) per MeV": "ω(p, h, E) pr. MeV",
  "{#}p{#}h": "{#}p{#}h",
  "dashed: no Pauli correction": "stiplet: uden Pauli-korrektion",
  "Fermi level": "Ferminiveau",
  "{#} particles, {#} holes": "{#} partikler, {#} huller",
  "{#} particles, {#} hole": "{#} partikler, {#} hul",
  // scene 2: rates
  "rate (s⁻¹)": "rate (s⁻¹)",
  "n = {#}": "n = {#}",
  "W/λ⁺ = {#}": "W/λ⁺ = {#}",
  "blue: λ⁺, the next collision · yellow: W, neutron escape": "blå: λ⁺, næste kollision · gul: W, neutronen slipper ud",
  "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
  // scene 3: master equation
  "compound": "compoundkerne",
  "emitted before equilibrium: {#} % (of {#} % in the end)": "udsendt før ligevægt: {#} % (af {#} % til sidst)",
  "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
  // scene 4: spectrum
  "outgoing neutron energy ε (MeV)": "udgående neutronenergi ε (MeV)",
  "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
  "evaporation": "fordampning",
  "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV: {#} % fra n = {#}",
  "pre-equilibrium {#} % of the emission · solid: total": "præligevægt {#} % af emissionen · fuldt optrukket: total",
  // scene 5: share
  "{#} MeV": "{#} MeV",
  "pre-equilibrium share of the emission": "præligevægtsandel af emissionen",
  "{#} MeV: {#} %": "{#} MeV: {#} %",
  "C₁ = {#} (dashed: {#})": "C₁ = {#} (stiplet: {#})",
  // scene 6: second escape
  "{#} MeV: multiple pre-equilibrium on": "{#} MeV: multipel præligevægt slås til",
  "chance of a second fast emission (toy estimate)": "chance for en anden hurtig udsendelse (groft skøn)",
  "residual: {#}p{#}h": "restkerne: {#}p{#}h",
});
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "Never-come-back-approksimationen", aliases: ["never-come-back-approksimationen", "never-come-back-approksimation", "never-come-back-løsningen", "never-come-back"],
    short: "Approksimationen, at kollisioner tidligt i ligevægtsindstillingen kun tilføjer partikel–hul-par og aldrig fjerner dem.",
    more: "Den gør masterligningen til en simpel kæde, der kan integreres trin for trin. Den holder, så længe excitontallet er langt under sin ligevægtsværdi, og det er netop dér, præligevægtsemission finder sted.",
    chapter: "exciton",
  },
});
