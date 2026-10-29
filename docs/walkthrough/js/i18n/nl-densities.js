/* Dutch (Nederlands): densities (Hoofdstuk 24, niveaudichtheden, aangesloten) */
WT.L.ch.densities = {
  num: "Hoofdstuk 24", title: "Niveaudichtheden, aangesloten", short: "Niveaudichtheden",
  lead: "Hoofdstuk 8 verbond een rechte plank met een heuvelhelling. Dit hoofdstuk schrijft beide uit, laat zien hoe het verbindingspunt uit de getelde niveaus wordt gevonden, en wat er gebeurt als er geen verbindingspunt bestaat.",
  html: `
<div class="step">
  <h3>Het fermigas met gedempte schileffecten</h3>
  <p>De standaardniveaudichtheid van de motor, is de samengestelde vorm van <b>Gilbert–Cameron</b>: een fermigas bij hoge energie, een constante temperatuur daaronder. Het fermigas heeft één getal nodig, de niveaudichtheidsparameter <i>a</i>, en bij lage energie voelt dat getal de schillen. De vorm van <b>Ignatyuk</b> laat de schilcorrectie δW bij lage excitatie volledig werken en met een dempingssnelheid γ uitdoven, zodat <i>a</i>(<i>U</i>) naar de gladde waarde <i>ã</i> gaat zodra de kern heet is.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Schilcorrectie δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>De bovenste curven zijn <i>a</i>(<i>U</i>)/<i>ã</i> voor verschillende δW; de jouwe is vet. Daaronder staat ln ρ<sub>F</sub>. Een negatieve δW (een gesloten schil) onderdrukt de dichtheid met één à twee ordes van grootte, en de onderdrukking dooft maar langzaam uit: <i>a</i>(<i>U</i>) keert terug naar <i>ã</i> als δW/<i>U</i>, zodat zelfs bij 20 MeV een δW van −6 MeV nog een factor van ongeveer 40 kost. Δ is de paringsverschuiving, 12/√A per gepaarde nucleonsoort.</p>
</div>
<div class="step">
  <h3>Een raaklijn eronder</h3>
  <p>Onder de aansluitenergie <i>E<sub>x</sub></i> wordt het fermigas vervangen door de wet van de <b>constante temperatuur</b>. Twee voorwaarden leggen haar twee parameters vast: gelijke waarde en gelijke helling bij <i>E<sub>x</sub></i>, dus de lijn is daar de raaklijn aan ln ρ<sub>F</sub>.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Aansluitenergie Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Verschuif <i>E<sub>x</sub></i> en de raaklijn zwaait mee: een hoger verbindingspunt geeft een hogere <i>T</i> (een vlakkere lijn) en een lagere <i>E</i>₀. Elke <i>E<sub>x</sub></i> geeft een gladde curve. De getelde niveaus beslissen welke de juiste is.</p>
</div>
<div class="step">
  <h3>Het verbindingspunt vinden uit de getelde niveaus</h3>
  <p>De trap is het aantal bekende niveaus onder <i>E</i>, op een logaritmische schaal. De wet van de constante temperatuur integreert tot een rechte lijn, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + const, en die moet het aantal niveaus tussen niveau <i>N<sub>L</sub></i> en niveau <i>N<sub>P</sub></i> reproduceren, het stuk van het niveauschema dat als volledig geldt. Dat is één vergelijking voor de ene onbekende <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Proefwaarde Eₓ (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Het onderste paneel is <i>F</i>. De motor doorzoekt, net als TALYS, een interval in 100 stappen op een tekenwisseling en halveert het daarna herhaaldelijk; het krimpende interval toont die bisectie. Waar <i>F</i> = 0 ligt de proeflijn op de trap.</p>
</div>
<div class="step">
  <h3>Als er geen verbindingspunt is</h3>
  <p>Soms kunnen de twee krommen niet vloeiend worden verbonden. In een kern met gesloten schillen voor zowel protonen als neutronen, zoals lood-208, wordt het fermigas zo ver omlaag gehouden dat geen enkele raaklijn de getelde niveaus ontmoet: er is geen aansluitenergie. De code valt dan terug op vuistregels voor de temperatuur en voor het verbindingspunt. De twee stukken sluiten nog steeds op elkaar aan, maar met een knik: de waarden komen overeen en de hellingen niet.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Raaklijn bij de terugvalenergie</button></div>
  <p>Druk op de knop om in plaats daarvan de vloeiende raaklijn te zien. Met de standaardinvoer verschijnt de knik voor zeven kernen rond lood, en door haar weg te nemen verschuift hun neutronenvangst met tot 20 à 30 %. INCOGNITA reproduceert hier TALYS; de wijziging is gemeld aan de ontwikkelaars van TALYS.</p>
  <div class="aside">De details: bij een dubbel gesloten schil blijft het fermigas bij lage energie overal koud, en <i>F</i> wisselt nooit van teken. TALYS neemt dan de empirische temperatuur <i>T</i> = −0,25 + 10,2/√(<i>A</i>(1 + γδW)) en zoekt de energie waarbij het fermigas die temperatuur heeft. Bij een dubbel gesloten schil bereikt het die pas ver boven elk zinnig verbindingspunt, of nooit, dus valt ook het verbindingspunt terug op systematiek, <i>E<sub>x</sub></i> = 2,33 + 253/<i>A</i> + Δ, en wordt <i>E</i>₀ zo vastgelegd dat de waarde continu is. De empirische <i>T</i> is niet de temperatuur van het fermigas bij die energie, dus de helling springt: met de standaardinvoer voor ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb en ²¹⁰Bi, met 34 tot 62 %. Neem je daar <i>T</i> uit het fermigas, zoals TALYS al doet wanneer <i>E<sub>x</sub></i> in de invoer wordt opgegeven, dan komt de raaklijn terug. De afbeelding is een illustratie voor een loodachtige kern, met <i>ã</i> 30 % verhoogd zodat het fermigas tot ongeveer 24 MeV, voorbij het zoekbereik, onder de empirische temperatuur blijft; de helling springt er met 62 %.</div>
</div>
<div class="step">
  <h3>De afstand D₀ als controle</h3>
  <p>Bij de neutronseparatie-energie wordt de dichtheid direct gemeten: de gemiddelde afstand <i>D</i>₀ van s-golfresonanties telt de toestanden met de ene spin en pariteit die een langzaam neutron kan bereiken. Voor een trefkern met spin 0 is dat alleen <i>J</i><sup>π</sup> = ½⁺.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Schaalfactor op ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>De afbeelding geldt voor een compoundkern zoals ijzer-57, met de globale <i>ã</i>, tegenover de gemeten 25,4 ± 2,2 keV. Een paar procent op <i>ã</i> verschuift <i>D</i>₀ met tientallen procenten, dus waar <i>D</i>₀ gemeten is, ligt de dichtheid bij <i>S<sub>n</sub></i> goed vast, en waar dat niet zo is, is ze de grootste afzonderlijke onzekerheid in vangst. Evaluaties passen <i>a</i> aan <i>D</i>₀ aan, en dat doet ook de standaard van TALYS, die de motor volgt: voor een kern met een gemeten <i>D</i>₀ leest hij een daaraan gefitte niveaudichtheidsparameter in, en de globale formule gebruikt hij alleen voor de andere.</p>
  <div class="aside">In de code: <code>density/parameters.py</code> (ã, demping volgens Ignatyuk, paring, spinafsnijding), <code>density/models.py</code> (fermigas, constante temperatuur, tabellen), <code>density/matching.py</code> (het nulpunt voor de aansluiting, de empirische terugval, met de eigen details van TALYS in enkele precisie gereproduceerd). De afbeelding gebruikt de globale parameters van TALYS voor ldmodel 1 met illustratieve niveauschema's en schilcorrecties (en, voor het loodachtige geval, <i>ã</i> × 1,3); de gemeten <i>D</i>₀ is de RIPL-waarde voor ⁵⁷Fe.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: Ignatyuk and the Fermi gas
    "a(U) / ã": "a(U) / ã", "U (MeV)": "U (MeV)", "E (MeV)": "E (MeV)", "Eₓ (MeV)": "Eₓ (MeV)",
    "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
    "ρ_F (states per MeV), A = {#}": "ρ_F (toestanden per MeV), A = {#}",
    "dashed: δW = {#}": "gestippeld: δW = {#}",
    "at {#} MeV: ×{#} against δW = {#}": "bij {#} MeV: ×{#} tegenover δW = {#}",
    "at {#} MeV: ×{#}e{#} against δW = {#}": "bij {#} MeV: ×{#}e{#} tegenover δW = {#}",
    // scene 2: the tangent
    "T = {#} MeV": "T = {#} MeV", "× e": "× e",
    "joint Eₓ = {#} MeV": "verbindingspunt Eₓ = {#} MeV",
    "E₀ = {#} MeV": "E₀ = {#} MeV",
    "Fermi gas": "fermigas", "constant temperature": "constante temperatuur",
    "ln ρ (states per MeV), A = {#}": "ln ρ (toestanden per MeV), A = {#}",
    // scene 3: the staircase and the bisection
    "levels {#}–{#}": "niveaus {#}–{#}",
    "levels {#} to {#}: taken as complete": "niveaus {#} tot {#}: als volledig genomen",
    "number of levels below E": "aantal niveaus onder E",
    "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "proefwaarde Eₓ = {#} MeV: de lijn geeft {#} niveaus, geteld zijn er {#}",
    "F = {#}": "F = {#}",
    "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ): voorspeld min geteld (logaritmische schaal met teken)",
    "bisection step {#}: [{#}, {#}]": "bisectiestap {#}: [{#}; {#}]",
    "root Eₓ = {#} MeV": "nulpunt Eₓ = {#} MeV",
    // scene 4: no root
    "below: {#}/T with T = {#} MeV (Fermi-gas T)": "eronder: {#}/T met T = {#} MeV (T van het fermigas)",
    "below: {#}/T with T = {#} MeV (empirical T)": "eronder: {#}/T met T = {#} MeV (empirische T)",
    "above: Fermi gas, T = {#} MeV": "erboven: fermigas, T = {#} MeV",
    "slope jumps by {#} % at Eₓ = {#} MeV": "helling springt {#} % bij Eₓ = {#} MeV",
    "tangent at Eₓ = {#} MeV: no jump": "raaklijn bij Eₓ = {#} MeV: geen sprong",
    "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, loodachtige kern (A = {#}, δW = {#} MeV)",
    "F changes sign: a root exists": "F wisselt van teken: er is een nulpunt",
    "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) wordt nooit nul: geen aansluitenergie",
    // scene 5: D0
    "{#} keV": "{#} keV",
    "measured {#} ± {#} keV": "gemeten {#} ± {#} keV",
    "computed D₀ = {#} keV": "berekend D₀ = {#} keV",
    "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "s-golfresonanties boven Sₙ, {#} keV getoond: ongeveer {#} niveaus",
    // "iron-57-like": the number is read as −57, so the hyphen travels with it
    "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "compoundkern zoals ijzer{#}, Sₙ = {#} MeV, spin en pariteit ½⁺",
  };
  // rho(Sn) printed plainly or in e-notation
  for (const r of ["{#}", "{#}e{#}"])
    L[`ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = ${r} per MeV`] = `ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = ${r} per MeV`;
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron"],
    short: "Een samengestelde niveaudichtheid: een wet van constante temperatuur bij lage energie, boven een aansluitenergie verbonden met het fermigas, met gelijke waarde en helling in het verbindingspunt.",
    more: "Voorgesteld door A. Gilbert en A. G. W. Cameron in 1965. Het is de standaard van TALYS en van de motor (ldmodel 1), met de energieafhankelijke niveaudichtheidsparameter van Ignatyuk.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "De vorm van Ignatyuk voor de niveaudichtheidsparameter: de schilcorrectie werkt volledig bij lage excitatie en dooft uit met de energie, zodat a(U) naar zijn gladde waarde gaat.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="tang" */
