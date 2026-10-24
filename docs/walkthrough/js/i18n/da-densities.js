/* Danish: densities (chapter 15, Expert) */
WT.L.ch.densities = {
  num: "Kapitel 15", title: "Niveautætheder, tilpasset", short: "Niveautætheder",
  lead: "Kapitel 5 satte en lige planke sammen med en skråning. Dette kapitel skriver begge op, viser, hvordan samlingen findes ud fra de optalte niveauer, og hvad der sker, når der ikke findes nogen samling.",
  html: `
<div class="step">
  <h3>Fermigassen med dæmpede skaleffekter</h3>
  <p>Motorens standardniveautæthed, ldmodel 1, er den sammensatte model af <b>Gilbert–Cameron</b>: en Fermigas ved høj energi og konstant temperatur nedenunder. Fermigassen behøver ét tal, niveautæthedsparameteren <i>a</i>, og ved lav energi mærker det tal skallerne. <b>Ignatyuks</b> form lader skalkorrektionen δW virke fuldt ved lav excitation og aftage med en dæmpningsrate γ, så <i>a</i>(<i>U</i>) går mod den glatte værdi <i>ã</i>, når kernen er varm.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Skalkorrektion δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>De øverste kurver er <i>a</i>(<i>U</i>)/<i>ã</i> for flere værdier af δW; din er fed. Nedenunder står ln ρ<sub>F</sub>. En negativ δW (en lukket skal) undertrykker tætheden med en til to størrelsesordener, og undertrykkelsen aftager kun langsomt: <i>a</i>(<i>U</i>) vender tilbage til <i>ã</i> som δW/<i>U</i>, så selv ved 20 MeV koster en δW på −6 MeV stadig en faktor på omkring 40. Δ er parringsforskydningen, 12/√A for hver slags parret nukleon.</p>
</div>
<div class="step">
  <h3>En tangent nedenunder</h3>
  <p>Under tilpasningsenergien <i>E<sub>x</sub></i> erstattes Fermigassen af <b>konstanttemperaturloven</b>. To betingelser fastlægger dens to parametre: samme værdi og samme hældning i <i>E<sub>x</sub></i>, så linjen er tangenten til ln ρ<sub>F</sub> dér.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Tilpasningsenergi Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Flyt <i>E<sub>x</sub></i>, og tangenten svinger: en højere samling giver et højere <i>T</i> (en fladere linje) og et lavere <i>E</i>₀. Ethvert <i>E<sub>x</sub></i> giver en glat kurve. De optalte niveauer afgør, hvilken der er den rigtige.</p>
</div>
<div class="step">
  <h3>Samlingen findes ud fra de optalte niveauer</h3>
  <p>Trappen er antallet af kendte niveauer under <i>E</i>, på en logaritmisk skala. Konstanttemperaturloven integrerer til en ret linje, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + konst., og den skal gengive antallet mellem niveau <i>N<sub>L</sub></i> og niveau <i>N<sub>P</sub></i>, det stykke af niveauskemaet, der anses for fuldstændigt. Det er én ligning for den ene ubekendte <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Prøve-Eₓ (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Det nederste panel er <i>F</i>. Motoren gennemsøger, ligesom TALYS, et interval i 100 skridt efter et fortegnsskift og halverer det derefter; det skrumpende interval viser bisektionen. Hvor <i>F</i> = 0, ligger prøvelinjen på trappen.</p>
</div>
<div class="step">
  <h3>Når der ingen samling er</h3>
  <p>For en dobbelt lukket skal er Fermigassen ved lav energi så undertrykt, at dens temperatur forbliver lav overalt, og <i>F</i> skifter aldrig fortegn: der findes ingen tilpasningsenergi. TALYS tager så den empiriske temperatur <i>T</i> = −0,25 + 10,2/√(<i>A</i>(1 + γδW)) og leder efter den energi, hvor Fermigassen har den temperatur. Nær en dobbelt lukket skal når Fermigassen først den temperatur langt over enhver fornuftig samling, eller aldrig, så samlingen falder også tilbage på systematik, <i>E<sub>x</sub></i> = 2,33 + 253/<i>A</i> + Δ, og <i>E</i>₀ fastlægges, så værdien er kontinuert.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Tangent ved reserveenergien</button></div>
  <p>Værdien er kontinuert, men det empiriske <i>T</i> er ikke Fermigassens temperatur ved den energi, så hældningen springer. Med standardinputtet sker det for ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb og ²¹⁰Bi, med hældningsspring på 34 til 62 %; tages <i>T</i> fra Fermigassen dér, som TALYS allerede gør, når <i>E<sub>x</sub></i> er givet i inputtet, genoprettes tangenten, og indfangning i blyområdet flytter sig med op til 20 til 30 %. INCOGNITA gengiver TALYS her; ændringen er rapporteret til TALYS-udviklerne. Billedet er en blylignende illustration med <i>ã</i> hævet med 30 %, så dens Fermigas holder sig under den empiriske temperatur op til omkring 24 MeV, ud over søgningen; dens hældning springer med 62 %.</p>
</div>
<div class="step">
  <h3>Afstanden D₀ som kontrol</h3>
  <p>Ved neutronseparationsenergien måles tætheden direkte: middelafstanden <i>D</i>₀ mellem s-bølge-resonanser tæller tilstandene med det ene spin og den ene paritet, en langsom neutron kan nå. For en targetkerne med spin 0 er det <i>J</i><sup>π</sup> = ½⁺ alene.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Skalering af ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>Billedet er for en jern-57-lignende compoundkerne med det globale <i>ã</i>, sammenlignet med de målte 25,4 ± 2,2 keV. Nogle få procent på <i>ã</i> flytter <i>D</i>₀ med titals procent, så hvor <i>D</i>₀ er målt, er tætheden ved <i>S<sub>n</sub></i> godt fastlagt, og hvor den ikke er, er den den største enkeltstående usikkerhed i indfangning. Evalueringer justerer <i>a</i> til <i>D</i>₀, og det gør TALYS' standard også, som motoren følger: for en kerne med en målt <i>D</i>₀ indlæser den en niveautæthedsparameter tilpasset den, og den bruger kun den globale formel for de øvrige.</p>
  <div class="aside">I koden: <code>density/parameters.py</code> (ã, Ignatyuk-dæmpning, parring, spin-cutoff), <code>density/models.py</code> (Fermigas, konstant temperatur, tabeller), <code>density/matching.py</code> (tilpasningsroden, den empiriske reserve, TALYS' egne detaljer i enkelt præcision gengivet). Billedet bruger TALYS' globale parametre for ldmodel 1 med illustrative niveauskemaer og skalkorrektioner (og, for det blylignende tilfælde, <i>ã</i> × 1,3); den målte <i>D</i>₀ er RIPL-værdien for ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "E (MeV)": "E (MeV)", "Eₓ (MeV)": "Eₓ (MeV)", "U (MeV)": "U (MeV)", "a(U) / ã": "a(U) / ã",
  "F = {#}": "F = {#}", "T = {#} MeV": "T = {#} MeV", "E₀ = {#} MeV": "E₀ = {#} MeV", "× e": "× e",
  // scene 1
  "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
  "ρ_F (states per MeV), A = {#}": "ρ_F (tilstande pr. MeV), A = {#}",
  "dashed: δW = {#}": "stiplet: δW = {#}",
  "at {#} MeV: ×{#} against δW = {#}": "ved {#} MeV: ×{#} i forhold til δW = {#}",
  "at {#} MeV: ×{#}e{#} against δW = {#}": "ved {#} MeV: ×{#}e{#} i forhold til δW = {#}",
  // scene 2
  "joint Eₓ = {#} MeV": "samling Eₓ = {#} MeV",
  "Fermi gas": "Fermigas",
  "constant temperature": "konstant temperatur",
  "ln ρ (states per MeV), A = {#}": "ln ρ (tilstande pr. MeV), A = {#}",
  // scene 3
  "levels {#} to {#}: taken as complete": "niveau {#} til {#}: antaget fuldstændige",
  "levels {#}–{#}": "niveau {#}–{#}",
  "number of levels below E": "antal niveauer under E",
  "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "prøve-Eₓ = {#} MeV: linjen giver {#} niveauer mod {#} optalte",
  "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ): forudsagt minus optalt (log-skala med fortegn)",
  "bisection step {#}: [{#}, {#}]": "bisektionsskridt {#}: [{#}; {#}]",
  "root Eₓ = {#} MeV": "rod Eₓ = {#} MeV",
  // scene 4
  "below: {#}/T with T = {#} MeV (Fermi-gas T)": "under: {#}/T med T = {#} MeV (Fermigas-T)",
  "below: {#}/T with T = {#} MeV (empirical T)": "under: {#}/T med T = {#} MeV (empirisk T)",
  "above: Fermi gas, T = {#} MeV": "over: Fermigas, T = {#} MeV",
  "slope jumps by {#} % at Eₓ = {#} MeV": "hældningen springer {#} % ved Eₓ = {#} MeV",
  "tangent at Eₓ = {#} MeV: no jump": "tangent ved Eₓ = {#} MeV: intet spring",
  "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, blylignende kerne (A = {#}, δW = {#} MeV)",
  "F changes sign: a root exists": "F skifter fortegn: der findes en rod",
  "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) når aldrig nul: ingen tilpasningsenergi",
  // scene 5
  "{#} keV": "{#} keV",
  "measured {#} ± {#} keV": "målt {#} ± {#} keV",
  "computed D₀ = {#} keV": "beregnet D₀ = {#} keV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} pr. MeV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} pr. MeV",
  "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "s-bølge-resonanser over Sₙ, {#} keV vist: ca. {#} niveauer",
  "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "jern{#}-lignende compoundkerne, Sₙ = {#} MeV, spin og paritet ½⁺",
});
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron", "Gilbert–Cameron-modellen"],
    short: "En sammensat niveautæthed: en konstanttemperaturlov ved lav energi, sat sammen med Fermigassen over en tilpasningsenergi, med samme værdi og hældning i samlingen.",
    more: "Foreslået af A. Gilbert og A. G. W. Cameron i 1965. Den er standard i TALYS og i motoren (ldmodel 1), med Ignatyuks energiafhængige niveautæthedsparameter.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk", "Ignatyuks", "Ignatyuk-dæmpning"],
    short: "Ignatyuks form for niveautæthedsparameteren: skalkorrektionen virker fuldt ved lav excitation og aftager med energien, så a(U) går mod sin glatte værdi.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
