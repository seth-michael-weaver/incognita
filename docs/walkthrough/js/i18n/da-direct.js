/* Danish: direct (Kapitel 6, direkte reaktioner) */
WT.L.ch.direct = {
  num: "Kapitel 6", title: "Direkte reaktioner", short: "Direkte reaktioner",
  lead: "Ikke alle neutroner, der når kernen, bliver slugt. Nogle strejfer dens overflade, giver den ét skub og flyver videre.",
  html: `
<div class="step">
  <p>En neutron, der kun strejfer kernen, kan skubbe den én gang op i et exciteret niveau og flyve videre, mest fremad og kun lidt langsommere. Det er en <b>direkte reaktion</b>: ét trin, overstået på ca. 10⁻²² sekunder. Her flyver en neutron forbi i afstanden <i>b</i>, <b>stødparameteren</b>, målt i kerneradier <i>R</i>; den prikkede ring er kernens overflade.</p>
  <div class="ctl"><label for="di-b">Sigte b (i radier)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Træk i <i>b</i>. Under ca. 0,8 bliver neutronen slugt. Nær 1 strejfer den og efterlader kernen i dens første exciterede niveau, 2⁺. Over ca. 1,2 rammer den ikke og afbøjes kun: <b>elastisk spredning</b>, kernen er uændret.</p>
</div>
<div class="step">
  <h3>Rotationsexcitation af deformerede kerner</h3>
  <p>Et skub sætter en aflang kerne (kapitel 1) i rotation, op ad stigen i dens <b>rotationsbånd</b>: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. Neutronen kan skubbe kernen op, og kernen kan skubbe tilbage, så intet niveau kan regnes ud alene. Motoren løser dem alle samtidig: <b>koblede kanaler</b>, hvor hver kanal er ét udfald, her ét niveau i båndet.</p>
  <div class="btns"><button class="btn" data-act="kick">Skub den et niveau op</button><button class="btn ghost" data-act="rpause">Pause / fortsæt</button></div>
  <div class="ctl"><label for="di-beta">Deformation β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>Buerne viser, hvilke niveauer der er forbundet: <i>λ</i> = 2, den samlede strækning, forbinder naboer; <i>λ</i> = 4, en finere udbuling, springer to over. Træk i <i>β₂</i>: en mere strakt kerne forbinder sine niveauer stærkere, og buerne bliver tykkere. Fordi båndet regnes ud sammen med den indkommende neutron, ved motoren præcis, hvor mange neutroner det tager, og den giver kun resten videre til de langsommere veje i de næste kapitler.</p>
</div>
<div class="step">
  <h3>Overfladevibrationer</h3>
  <p>En rund kerne kan kruse, og krusningsenergi kommer i lige store portioner kaldet <b>fononer</b>. Én fonon af krusningen fra amerikansk fodbold til skive (<i>λ</i> = 2) giver 2⁺-niveauet; to giver tre niveauer, 0⁺, 2⁺ og 4⁺, ved den dobbelte energi. For at nå dem kræves to skub i træk. Motoren løser disse niveauer sammen med grundtilstanden.</p>
  <div class="ctl"><label for="di-lam">Krusningsform λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Én fonon</button><button class="btn ghost" data-act="ph2">To fononer</button></div>
  <p>Sæt <i>λ</i> = 3 for en pæreformet krusning, hvis første niveau er 3⁻. Tryk på knapperne for at tilføje en eller to fononer.</p>
</div>
<div class="step">
  <h3>Direkte énstrinsreaktioner</h3>
  <p>For de fleste niveauer er koblingen svag, og ét skub er nok: <b>DWBA</b> (Born-approksimationen med forvrængede bølger). Den indkommende bølge fra kapitel 5 skubber kernen én gang, ved kanten, hvor potentialet falder fra dybt til nul; kanten lyser, hvor bølgetoppene rammer. Den cirkulære bølge, der breder sig udad, er de neutroner, der efterlod kernen exciteret.</p>
  <div class="ctl"><label for="di-bd">Niveauets deformation β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Træk i <i>β</i>: kanten vugger kraftigere, og cirklerne bliver lysere, som <i>β</i>²: dobbelt deformation, fire gange så mange. Motoren tager hvert niveaus <i>β</i> fra målte værdier eller fra systematik, hvor ingen kendes. Hvordan de spredte neutroner fordeler sig på vinkler, er et valgfrit ekstra output.</p>
</div>
<div class="step">
  <h3>Kæmperesonanser</h3>
  <p>Alle nukleonerne kan bevæge sig sammen: ånde, trykkes flad og strækkes eller svinge ud i en pæreform. Det er <b>kæmperesonanser</b>. I denne mellemtunge kerne ligger de ca. 7 til 25 MeV oppe, hver flere MeV bred, for bred til at tælle som ét niveau; puklerne markerer hver enkelts <b>excitationsenergi</b>.</p>
  <p>Motoren fastsætter hver enkelts samlede styrke ud fra en <b>sumregel</b>, en grænse fra grundlæggende fysik for, hvor kraftigt en kerne kan reagere, og fordeler den som en pukkel over det sidste kendte niveau. Disse pukler plus skub til høje niveauer udgør det <b>kollektive kontinuum</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Ånding</button><button class="btn ghost" data-act="quad">Fladtrykning</button><button class="btn ghost" data-act="oct">Pære</button></div>
  <p>Den mest kendte, hvor protoner skvulper mod neutroner (kæmpedipolresonansen), absorberer og udsender hovedsageligt lys, så den hører til kapitel 10.</p>
</div>
<div class="step">
  <h3>Direkte indfangning</h3>
  <p>En fri neutron kan falde direkte ned i en tom <b>bane</b> i brønden (en tilladt energi for én neutron indeni) og sende den overskydende energi ud som en <em class="g">foton</em>. Kernen bliver aldrig opvarmet. Det er <b>direkte indfangning</b>. Motoren kan beregne den ud fra samme brønd som i kapitel 5: den frie bølge udenfor, den bundne bane indeni og fotonen, der forbinder dem. Den er valgfri og slået fra som standard.</p>
  <div class="btns"><button class="btn" data-act="drop">Slip en neutron ned</button></div>
  <p>Direkte indfangning betyder mest, hvor den sædvanlige vej, hvor neutronens energi deles, er svag: lette kerner og kerner langt fra stabilitet, med få niveauer langt fra hinanden.</p>
</div>
<div class="step">
  <h3>Direkte versus compound-flux</h3>
  <p>Motoren deler reaktionstværsnittet fra kapitel 5 i rækkefølge: først direkte reaktioner, så hurtige kollisioner, og kun resten danner en compoundkerne. På billedet møder hver neutron én af tre skæbner: <b>direkte</b> (strejfer og flyver videre), hurtig (slår en nukleon ud, før energien fordeles: <b>præligevægt</b>, kapitel 7) eller slugt (en <b>compoundkerne</b>, kapitel 8). Bunkerne tæller dem.</p>
  <div class="ctl"><label for="di-e">Neutronenergi (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Træk i energien og se bunkerne fyldes igen. Ved nogle få MeV bliver næsten alle neutroner slugt. Ved flere titals MeV tager direkte reaktioner og hurtige kollisioner tilsammen en stor del.</p>
  <div class="aside">I koden: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (deformeret potential, koblede kanaler for rotorer og vibratorer), <code>ecis/dwba.py</code> og <code>direct/dwba.py</code> (enkelt skub, kæmperesonanser, kollektivt kontinuum), <code>direct/racapcalc.py</code> (direkte indfangning, valgfri, slået fra som standard), <code>compound/normalization.py</code> (regnskabet).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "hud (overflade)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "absorberet: energien deles af alle nukleoner",
  "{#}⁺ level": "{#}⁺-niveau",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "ét skub efterlader kernen i {#}⁺; neutronen flyver videre",
  "a miss: deflected, nucleus unchanged (elastic)": "forbi: afbøjet, kernen uændret (elastisk)",
  // scene: rotor
  "at rest: {#}⁺": "i hvile: {#}⁺",
  "rotating: {#}⁺": "roterer: {#}⁺",
  "rotating: {#}⁺ (paused)": "roterer: {#}⁺ (pause)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "niveauer løst samtidig",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "kvadrupolkrusning: bold ↔ skive",
  "octupole ripple: pear ↔ pear": "oktupolkrusning: pære ↔ pære",
  "{#}⁺  no phonon": "{#}⁺  ingen fonon",
  "{#}⁺  one phonon": "{#}⁺  én fonon",
  "{#}⁻  one phonon": "{#}⁻  én fonon",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  to fononer",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  to fononer",
  "one push": "ét skub",
  "two pushes": "to skub",
  "two phonons": "to fononer",
  "equal energy steps": "lige store energitrin",
  // scene: DWBA
  "rim: the push happens here": "kant: her sker skubbet",
  "incoming wave": "indkommende bølge",
  "outgoing: nucleus left excited": "udgående: kernen efterladt exciteret",
  "outgoing circles: the nucleus left on an excited level": "udgående cirkler: kernen efterladt i et exciteret niveau",
  "push strength ∝ β²: {#}× that at β = {#}": "skubstyrke ∝ β²: {#}× den ved β = {#}",
  // scene: giant resonances
  "breathing": "ånding",
  "squash and stretch": "fladtrykning og strækning",
  "pear": "pære",
  "breathing (monopole)": "ånding (monopol)",
  "squash and stretch (quadrupole)": "fladtrykning og strækning (kvadrupol)",
  "pear-shaped (octupole), low and high": "pæreformet (oktupol), lav og høj",
  "about {#} MeV up": "ca. {#} MeV oppe",
  "last known level": "sidste kendte niveau",
  "excitation energy (MeV) →": "excitationsenergi (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "fri: uden for kernen",
  "empty orbit": "tom bane",
  "drops straight in; a photon carries off the spare energy": "falder direkte ind; en foton bærer overskuddet væk",
  // scene: ledger
  "direct": "direkte",
  "fast (pre-eq.)": "hurtig (præligev.)",
  "compound": "compound",
  "direct: grazed, flew on": "direkte: strejfede, fløj videre",
  "fast collision: one out at once": "hurtig kollision: én ud med det samme",
  "compound: swallowed": "compound: slugt",
  "{#}% (model {#}%)": "{#}% (model {#}%)",
  "{#}% seen · model {#}%": "{#}% set · model {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "{#} MeV-neutroner på en mellemtung kerne (illustrative andele)",
});
