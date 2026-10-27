/* Danish: measure (chapter 11) */
WT.L.ch.measure = {
  num: "Kapitel 12", title: "Hvad der kommer ud", short: "Observabler",
  lead: "Et eksperiment, en reaktor eller en stjerne ser kun en håndfuld tal. Dette kapitel viser, hvordan motoren omsætter det, der sker inde i kernen, til dem.",
  html: `
<div class="step">
  <p>Den blege skive omkring hver kerne er dens <b>tværsnit</b>: det areal, en neutron skal ramme, for at en reaktion finder sted, ikke kernens virkelige størrelse. En stråle kommer fra venstre gennem en tynd folie af kerner; den andel, der reagerer, er det areal gange antallet af kerner, strålen møder. Enheden er barn (10⁻²⁴ cm², omtrent tværsnittet af en urankerne).</p>
  <div class="ctl"><label for="mea-e">Neutronenergi (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Sænk energien, og skiverne svulmer op: en langsom neutron er en bred bølge og reagerer på længere afstand. Ved høj energi skrumper skiven ind mod selve kernen.</p>
</div>
<div class="step">
  <h3>Nye udgange åbner med energien</h3>
  <p>Hver dør er én udgang, eller <b>kanal</b>: neutronen preller af (elastisk), efterlader targetkernen exciteret (n′), slår flere neutroner ud (2n, 3n), indfanges, så kun fotoner forlader kernen (γ), eller en proton eller α-partikel forlader den i stedet. En dør med hængelås har en <b>tærskel</b>: reaktionen koster mere energi, end neutronen bringer med.</p>
  <div class="ctl"><label for="mea-e2">Neutronenergi (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Træk energien forbi en tærskel, og døren springer op; spandene fyldes til hver kanals andel, og hver ny dør tager en andel fra de andre. Tærsklerne kommer fra kernernes masser; andelene fra konkurrencen i kapitel 6.</p>
</div>
<div class="step">
  <h3>Hvad en detektor ser</h3>
  <p>De to bunker er de neutroner, der når den forreste og den bageste halvdel af en detektorring, sorteret efter energi. Strålen er pulseret, så hver neutrons flyvetid giver dens energi: de hurtige kommer først.</p>
  <div class="ctl"><label for="mea-ein">Indfaldende energi (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Begge bunker har en pukkel af langsomme, <b>fordampede</b> neutroner: de koger af compoundkernen, når energien er fordelt, ens i alle retninger. Kun den forreste bunke har en lang, hurtig hale: neutroner fra <b>præligevægt</b>, som forlader kernen allerede ved de første stød og stadig bevæger sig nogenlunde med strålen. Skru op for den indfaldende energi, og halen vokser.</p>
</div>
<div class="step">
  <h3>Hvilken vej de går</h3>
  <p>Kronbladet viser, hvor mange neutroner der forlader kernen i hver retning; strålen kommer fra venstre. Fordampede neutroner har glemt strålen og forlader den ens i alle retninger; hurtige præligevægtsneutroner hælder fremad. Kalbachs regel bestemmer hvor meget, med én hældning <i>a</i>, der vokser med den udgående energi. Motoren kan også skrive disse vinkelfordelinger ud som et valgfrit output.</p>
  <div class="ctl"><label for="mea-eo">Udgående energi (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Sænk den udgående energi, og kronbladet bliver rundt: langsomme neutroner er for det meste fordampede.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>I en stjerne</h3>
  <p>Bunken nedenfor samler energierne for neutroner, der indfanges i en stjernes varme gas. Deres hastigheder følger en Maxwell-fordeling bestemt af temperaturen <i>kT</i> (30 keV svarer til omkring 350 millioner grader); længere spor betyder hurtigere neutroner, og hver passage forbi en kerne kan ende i et indfangningsglimt.</p>
  <div class="ctl"><label for="mea-kt">Temperatur kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Langsomme neutroner er lette at fange, men kommer sjældent forbi, og hurtige er der få af, så de fleste indfangninger kommer fra et vindue, der er nogle få <i>kT</i> bredt. Raten over hele gassen er det <b>Maxwell-midlede tværsnit</b> (MACS) i millibarn (mb). Opvarm gassen, og vinduet glider op mod højere energi, hvor targetkernen er mindre. MACS foldes ud fra motorens indfangningskurve.</p>
</div>
<div class="step">
  <h3>Targetkernen er også varm</h3>
  <p>Kuglerne viser, hvor stor en andel af targetkernerne der ligger i hvert af de laveste niveauer ved denne temperatur. I en stjerne er nogle targetkerner allerede exciterede, og hvert exciteret niveau er en anden indgang til den samme compoundkerne. Et niveau med spin <i>J</i> rummer flere, fordi det har 2<i>J</i>+1 orienteringer.</p>
  <div class="ctl"><label for="mea-kt2">Temperatur kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Skru op for temperaturen, og se kernerne rykke op. En stellar rate beregner indfangning fra hvert besat niveau og lægger resultaterne sammen med disse andele; vægtene summerer til partitionsfunktionen <i>G</i>, og forholdet til raten fra grundtilstanden er den <b>stellare forstærkningsfaktor</b>. Motoren kan gøre dette som en valgmulighed, der som standard er slået fra; normalt starter hver targetkerne i sin grundtilstand.</p>
</div>
<div class="step">
  <h3>Hvor sikkert er alt dette?</h3>
  <p>Hver svag skive er én kørsel af motoren med inputtene skubbet tilfældigt: dybden af den optiske brønd, niveautætheden og fotonstyrken, som hver kun kendes inden for nogle procent. Spredningen over mange kørsler er en ærlig usikkerhed: <b>Total Monte Carlo</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Kør en variant</button><button class="btn ghost" data-act="tmc">Kør 10</button><button class="btn ghost" data-act="clear">Ryd</button></div>
  <p>En skarp kant betyder, at inputtene fastlægger svaret; en sløret kant betyder, at de ikke gør, og det er dér, nye målinger ville hjælpe mest.</p>
  <div class="aside">I koden: <code>emission/channels.py</code> (eksklusive kanaler og restkerner), <code>specout.py</code> og <code>specang.py</code> (udgående spektre, vinkelfordelinger og dobbeltdifferentielle tværsnit, skrevet kun på forespørgsel), <code>astro/stellar.py</code> (indfangning fra termisk besatte niveauer i targetkernen, valgfrit), <code>tmc.py</code> (Total Monte Carlo-sampleren). MACS fra grundtilstanden foldes ud fra indfangningskurverne i <code>validation/differential/core.py</code>.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "hver skive: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "hver skive: tværsnit σ ≈ {#} b, arealet en neutron skal ramme",
  "beam →": "stråle →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "kernens egen flade ≈ {#} b · {#} % reagerer",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "kernens egen flade ≈ {#} b · {#} % af strålen reagerer i denne folie",
  "slow: the neutron's wave reaches well past the surface": "langsom: neutronens bølge rækker langt ud over overfladen",
  "the target still looks bigger than the nucleus": "targetkernen ser stadig større ud end kernen",
  "fast: close to the nucleus's own size": "hurtig: tæt på kernens egen størrelse",
  // doors
  "elastic": "elastisk", "n′ inelastic": "n′ uelastisk", "{#}n": "{#}n", "γ capture": "γ-indfangning", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ uelastisk · {#} MeV",
  "opens at {#} MeV": "åbner ved {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "forreste halvdel", "backward half": "bageste halvdel",
  "pulsed beam": "pulseret stråle", "pulsed beam →": "pulseret stråle →",
  "backward": "bagud", "backward detectors": "bageste detektorer",
  "forward": "fremad", "forward detectors": "forreste detektorer",
  "outgoing neutron energy from the flight time (MeV) →": "udgående neutronenergi ud fra flyvetiden (MeV) →",
  "fast tail": "hurtig hale", "fast tail: pre-equilibrium": "hurtig hale: præligevægt",
  "evaporated hump": "fordampet pukkel", "hump: evaporated, every way alike": "pukkel: fordampet, ens i alle retninger",
  "{#} % leave before the energy is shared": "{#} % forlader kernen, før energien er fordelt",
  // angle
  "beam": "stråle",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "forhold frem/tilbage ≈ {#}  ·  hældning a ≈ {#}",
  "mostly evaporated: every direction alike": "mest fordampede: ens i alle retninger",
  "a mix: the fast share leans forward": "en blanding: den hurtige andel hælder fremad",
  "mostly pre-equilibrium: strongly forward": "mest præligevægt: stærkt fremad",
  "forward →": "fremad →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "energier for indfangede neutroner",
  "each capture drops here, by the neutron's energy: the window that counts": "hver indfangning lander her efter neutronens energi: vinduet, der tæller",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb ved kT = {#} keV · indfangninger set: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  grundtilstand", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "targetkernens niveauer med andelen af kerner i hvert",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#} % starter i grundtilstanden · partitionsfunktion G ≈ {#}",
  // TMC
  "optical well": "optisk brønd", "optical well depth": "den optiske brønds dybde",
  "level density": "niveautæthed", "photon strength": "fotonstyrke",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "stiplet: bedste input · hver skive i egen skala",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "stiplet ring: input med bedste værdier · hver energi i sin egen skala (skivens areal ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} kørsler af motoren, hver med inputtene skubbet tilfældigt",
});
