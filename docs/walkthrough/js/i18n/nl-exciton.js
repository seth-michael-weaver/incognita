/* Dutch (Nederlands): exciton (Hoofdstuk 26, het excitonmodel in getallen) */
WT.L.ch.exciton = {
  num: "Hoofdstuk 26", title: "Het excitonmodel in getallen", short: "Excitonmodel",
  lead: "Hoofdstuk 7 volgde één snel neutron door een paar botsingen. Hier staan de snelheden die in elk stadium beslissen of het volgende een nieuwe botsing is of een ontsnapping, en het spectrum dat ze samen opleveren.",
  html: `
<div class="step">
  <h3>Deeltje-gattoestanden tellen</h3>
  <p>Het excitonmodel deelt de kern op weg naar evenwicht in naar zijn aantal aangeslagen deeltjes <i>p</i> en gaten <i>h</i>, <i>n</i> = <i>p</i> + <i>h</i>. Een neutron dat een trefkern binnengaat, begint bij <i>p</i> = 1, <i>h</i> = 0; elke botsing voegt een paar toe. Wat in elk stadium telt, is op hoeveel manieren de energie over de <i>n</i> excitonen kan worden verdeeld: de deeltje-gattoestandsdichtheid.</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">Deeltjes p (gaten p − 1)</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">Pauli-correctie</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ is de dichtheid van eendeeltjesniveaus bij de fermi-energie. <i>A<sub>p,h</sub></i> is de correctie voor <b>Pauli</b>: twee deeltjes kunnen geen niveau delen, dus de laagste configuraties kosten energie en de dichtheid bij de drempel daalt. De krommen zijn genoemd naar hun aantallen: 3p2h betekent 3 deeltjes en 2 gaten. De schets toont telkens één configuratie met de gekozen <i>p</i>, willekeurig getrokken: elk gat is een nucleon dat onder het fermi-niveau ontbreekt.</p>
</div>
<div class="step">
  <h3>Overgangs- en emissiesnelheden</h3>
  <p>Vanuit elk stadium kunnen twee dingen gebeuren. Een botsing maakt een nieuw paar, met de snelheid λ<sup>+</sup>, die volgens de gulden regel van Fermi het kwadraat van het matrixelement is maal de dichtheid van de toestanden die de botsing kan bereiken. Of een deeltje vertrekt, met de snelheid <i>W</i>, die via gedetailleerd evenwicht volgt uit de inverse werkzame doorsnede en de verhouding van de toestandsdichtheden met en zonder het ontsnappende deeltje.</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">Neutronenergie (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Elk stadium is gelabeld met zijn aantallen (2p1h: 2 deeltjes, 1 gat). De balken zijn de twee snelheden in elk stadium, op een logaritmische schaal: λ<sup>+</sup> van de orde 10²² s⁻¹, <i>W</i> in het eerste stadium ongeveer een tiende daarvan en dalend met elk stadium, omdat elk nieuw paar de energie verdunt die het voorste deeltje kan meenemen. De motor neemt M² uit de vorm van Koning–Duijvestijn, die daalt met de energie per exciton:</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>De keten in de tijd</h3>
  <p>Als je de zeldzame botsingen verwaarloost die een paar weghalen (de never-come-back-benadering), gehoorzamen de populaties aan een eenvoudige keten: elk stadium vult zich vanuit het vorige en loopt leeg in het volgende en in het continuüm. De balken lossen die mastervergelijking op; de tijd staat in eenheden van 10⁻²² s.</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">Neutronenergie (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>De hele keten is in een paar keer 10⁻²² s voorbij. Het deel dat onderweg ontsnapt, is de pre-evenwichtsemissie; de rest wordt, na hoogstens zes deeltjes in de motor, net als in TALYS, aan de compoundkern overgedragen. Integratie over de tijd geeft elk stadium een sterkte τ(<i>n</i>)·<i>P</i>(<i>n</i>), en dat product is wat de motor berekent.</p>
</div>
<div class="step">
  <h3>De hoogenergetische staart</h3>
  <p>Het emissiespectrum is de som over de stadia van populatie maal levensduur maal emissiesnelheid, plus daarna de verdamping van wat overblijft. Alleen stadium <i>n</i> = 3, twee deeltjes en een gat, bereikt de hoogste uitgaande energieën: zijn spectrum daalt naar het eindpunt toe slechts lineair. Elk later stadium is zachter.</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + verdamping</div>
  <div class="ctl"><label for="ex-e3">Neutronenergie (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>Verhoog de energie en het spectrum wordt harder: de pre-evenwichtsstaart rekt uit tot het eindpunt, terwijl de verdampingsbult op 1 à 2 MeV blijft. Boven ongeveer 10 MeV zijn de gemeten hoogenergetische neutronen alleen met deze staart te reproduceren.</p>
</div>
<div class="step">
  <h3>De pre-evenwichtsfractie</h3>
  <p>Het deel van de emissie dat pre-evenwicht is, groeit met de inval-energie, hier van een paar procent bij 5 MeV tot ongeveer 40 procent bij 40 MeV. Het hangt af van één instelbare constante, de totale grootte van het matrixelement: een zwakkere wisselwerking betekent een tragere evenwichtsinstelling en meer vroege emissie.</p>
  <div class="ctl"><label for="ex-c">Constante van het matrixelement C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>De gestippelde curve is C₁ = 1, de standaard van de motor; de doorgetrokken curve volgt de schuif. Halveren van C₁ verhoogt het deel met een factor 1,5 tot 1,9, niet 2: de ontsnappingskans van elk stadium is W/(λ<sup>+</sup> + W), niet W/λ<sup>+</sup>, en minder kernen overleven tot de latere stadia.</p>
</div>
<div class="step">
  <h3>Twee componenten, en een tweede ontsnapping</h3>
  <p>De motor volgt protonen en neutronen apart (<i>p</i><sub>π</sub>, <i>h</i><sub>π</sub>, <i>p</i><sub>ν</sub>, <i>h</i><sub>ν</sub>), met verschillende matrixelementen voor gelijke en ongelijke paren, een kleinere putdiepte voor de eerste botsing bij het oppervlak, en de regels van Kalbach voor clusters. Boven 20 MeV laat hij ook de restkern, die nog excitonen bevat, een tweede snel deeltje uitzenden voordat ze in evenwicht is.</p>
  <div class="ctl"><label for="ex-e4">Neutronenergie (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>De curve is daarvan een sterk vereenvoudigde versie: na een eerste emissie uit het stadium met drie excitonen, de kans dat het overgebleven deeltje van de restkern ontsnapt vóór zijn volgende botsing. Die kans blijft klein onder 20 MeV en groeit erboven, en precies daar zet de motor meervoudig pre-evenwicht aan.</p>
  <div class="aside">In de code: <code>density/particle_hole.py</code> (dichtheden van Williams, correcties voor Pauli en de eindige put, één en twee componenten), <code>preeq/exciton.py</code> (matrixelementen, emissie- en overgangssnelheden, levensduren, de never-come-back-oplossing), <code>preeq/complex.py</code> (pick-up, stripping en knock-out volgens Kalbach), <code>preeq/multi.py</code> (meervoudig pre-evenwicht, standaard vanaf 20 MeV). De afbeelding gebruikt één component met een schematische inverse werkzame doorsnede, voor een trefkern zoals ijzer-56.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: state densities
  "E (MeV)": "E (MeV)",
  "ω(p, h, E) per MeV": "ω(p, h, E) per MeV",
  "{#}p{#}h": "{#}p{#}h",
  "dashed: no Pauli correction": "gestippeld: zonder Pauli-correctie",
  "Fermi level": "fermi-niveau",
  "{#} particles, {#} holes": "{#} deeltjes, {#} gaten",
  // scene 2: rates
  "rate (s⁻¹)": "snelheid (s⁻¹)",
  "n = {#}": "n = {#}",
  "W/λ⁺ = {#}": "W/λ⁺ = {#}",
  "blue: λ⁺, the next collision · yellow: W, neutron escape": "blauw: λ⁺, de volgende botsing · geel: W, ontsnapping van een neutron",
  "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
  // scene 3: the master equation
  "compound": "compound",
  "emitted before equilibrium: {#} % (of {#} % in the end)": "uitgezonden vóór evenwicht: {#} % (van uiteindelijk {#} %)",
  "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
  // scene 4: the spectrum
  "outgoing neutron energy ε (MeV)": "uitgaande neutronenergie ε (MeV)",
  "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
  "evaporation": "verdamping",
  "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV: {#} % uit n = {#}",
  "pre-equilibrium {#} % of the emission · solid: total": "pre-evenwicht {#} % van de emissie · doorgetrokken: totaal",
  // scene 5: the share
  "{#} MeV": "{#} MeV",
  "pre-equilibrium share of the emission": "aandeel pre-evenwicht in de emissie",
  "{#} MeV: {#} %": "{#} MeV: {#} %",
  "C₁ = {#} (dashed: {#})": "C₁ = {#} (gestippeld: {#})",
  // scene 6: a second escape
  "{#} MeV: multiple pre-equilibrium on": "{#} MeV: meervoudig pre-evenwicht aan",
  "chance of a second fast emission (toy estimate)": "kans op een tweede snelle emissie (ruwe schatting)",
  "residual: {#}p{#}h": "restkern: {#}p{#}h",
});
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "Never-come-back-benadering", aliases: ["never-come-back-benadering", "never-come-back"],
    short: "De benadering dat botsingen vroeg in de evenwichtsinstelling alleen deeltje-gatparen toevoegen en ze nooit weghalen.",
    more: "Ze maakt van de mastervergelijking een eenvoudige keten die stadium voor stadium kan worden geïntegreerd. Ze geldt zolang het excitongetal ver onder zijn evenwichtswaarde ligt, en juist daar vindt de pre-evenwichtsemissie plaats.",
    chapter: "exciton",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="pauli" */
Object.assign(WT.L.labels, {
  "({#} particles, {#} hole)": "({#} deeltjes, {#} gat)",
  "({#} particle, {#} hole)": "({#} deeltje, {#} gat)",
});
