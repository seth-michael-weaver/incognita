/* Danish: gamma (chapter 7) */
WT.L.ch.gamma = {
  num: "Kapitel 7", title: "Kernen lyser", short: "Fotoner",
  lead: "Når ingen partikel slipper ud, køler kernen af ved at udsende fotoner: gammastråler, partikler af højenergetisk lys. Denne udgang er åben ved alle energier.",
  html: `
<div class="step">
  <p>En varm tilstand ved 8 MeV (millioner elektronvolt) udsender fotoner (γ); bunken ved siden af stigen samler, hvor de lander. Under 2 MeV er tilstandene nogle få navngivne trin; derover en mængde, der bliver stejlt tættere med energien (grå prikker). Hver foton tager energien fra sit fald, <i>E<sub>γ</sub></i>, med sig og tegnes lysere i forhold til <i>E<sub>γ</sub></i>³.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p><i>T<sub>γ</sub></i> er fotonens transmissionskoefficient (døren fra kapitel 6), <i>l</i> = 1 for dipolfotoner, og <i>f</i> er <b>fotonstyrken</b>: hvor villigt kernen stråler ved den energi. Et falds chance er <i>T<sub>γ</sub></i> gange mængden af tilstande, hvor det lander: små fald finder mange tilstande, men er svage; store fald er lysstærke, men finder få.</p>
  <div class="ctl"><label for="gm-e0">Startenergi</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">Udsend 100</button></div>
  <p>Bunken topper nogle få MeV under starten: de fleste fotoner bærer 2 til 4 MeV. Flyt startenergien, og toppen følger med.</p>
</div>
<div class="step">
  <h3>Hele kernen svinger</h3>
  <p>Den store top til højre er <b>kæmpedipolresonansen</b>: alle protonerne (skraveret, til venstre) svinger mod alle neutronerne (fyldt). Dens frekvens bestemmer den fotonenergi, kernen lettest absorberer og udsender. Kurven er fotonstyrken <i>f</i> på en logaritmisk skala (hvert trin op er ti gange mere).</p>
  <div class="ctl"><label for="gm-a">Massetal A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Træk i massetallet A (protoner plus neutroner): tunge kerner svinger langsommere, nær 12 til 14 MeV; lette nær 20. En henfaldende kerne udsender kun fotoner på nogle få MeV, så det, der betyder mest, er den skraverede lavenergihale.</p>
</div>
<div class="step">
  <h3>Saksen og upbend</h3>
  <p>En deformeret kerne stråler også magnetisk: dens protoner (skraveret) og neutroner (fyldt), to amerikanske fodbolde, vipper mod hinanden som saksens blade. Denne <b>saksetilstand</b> ligger nær 3 MeV. <b>Spin-flip</b>, nær 8 MeV, er enkelte nukleoner, der vender deres spin (de små pile), uanset form.</p>
  <div class="ctl"><label for="gm-b">Deformation β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Træk i deformationen β₂ (0 er en kugle). Jo mere strakt, jo flere saksefotoner flyver; en kugle har ingen. Ved de laveste energier stiger styrken igen: <b>upbend</b>, en sivende strøm af bløde fotoner, som motoren svækker, når kernen deformeres. En valgfri indstilling, slået fra som standard, bruger en stærkere saksesystematik, der passer med målinger fra Oslo (fire til fem gange stærkere i uran).</p>
</div>
<div class="step">
  <h3>Ned ad stigen</h3>
  <p>En kaskade er fotoner udsendt én efter én, fra intervallerne øverst (tilstande for tætte til at liste, kapitel 5) ned til de navngivne niveauer, strakt ud så de kan læses (fyldt trin paritet +, hult −). Dér holder motoren op med at estimere og følger de tabellerede <b>forgreningsforhold</b>: hvert niveaus målte sandsynlighed for at henfalde til hvert lavere niveau.</p>
  <div class="btns"><button class="btn" data-act="drop">Slip en kaskade</button></div>
  <p>Tryk på knappen et par gange: den øverste del ændrer sig hver gang; slutningen følger en af nogle få målte veje.</p>
</div>
<div class="step">
  <h3>Hylder, der holder</h3>
  <p>Niveauet 11/2− ved 0,40 MeV er en <b>isomer</b>: dets spin ligger så langt fra niveauerne nedenunder, at en foton næppe kan forbinde dem, så det lever fra sekunder til år, og hvad der lander dér, bliver der. Motoren behandler ethvert niveau, der lever længere end ét sekund, som et endepunkt. Hver kugle er én kaskade, der ender i isomerens bunke eller grundtilstandens.</p>
  <div class="ctl"><label for="gm-j">Indgangsspin</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Træk i indgangsspinnet, hvor kaskaderne starter, og bunkerne starter forfra. Den andel, der ender på isomeren, <b>isomerforholdet</b>, afhænger af det: en start med højt spin fodrer isomeren med højt spin; en start med lavt spin glider forbi den til grundtilstanden.</p>
</div>
<div class="step">
  <h3>Indfangning</h3>
  <p>En kerne, der lige har absorberet en langsom neutron, har to udgangsdøre (kapitel 6): fotoner (øverst) og neutronen, der går ud igen (til højre). Hver dørs åbning er dens <b>bredde</b>, i eV: hvor hurtigt kernen henfalder gennem den. Fotonbredden ændrer sig næsten ikke; neutronbredden vokser med neutronens fart.</p>
  <div class="ctl"><label for="gm-e">Neutronenergi</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1,0 keV</output></div>
  <p>Træk i neutronenergien, fra 10 eV til 2 MeV. <b>Indfangning</b>, (n,γ), betyder, at neutronen bliver, og en foton forlader kernen: den vinder for det meste ved 10 eV og bliver en lille andel over nogle få keV. Fotonbredden ved tærsklen er målt for hundredvis af kerner, et tjek af fotonstyrken. Som standard bruger motoren sin egen; en valgfri indstilling skalerer hver målt kernes fotonstyrke, til de to stemmer overens.</p>
  <div class="aside">I koden: <code>gamma/parameters.py</code> (tabellerede E1-styrker; systematik for kæmperesonans, spin-flip, saks og upbend), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) for hver multipol), <code>gamma/transmission.py</code> (T<sub>γ</sub> og den gennemsnitlige strålingsbredde), <code>structure/levels.py</code> (forgreningsforhold, isomerer), <code>emission/multiple.py</code> (kaskaden). Valgfrit, slået fra som standard: <code>gamma/scissors.py</code> (stærkere saks), <code>gamma/ggnorm.py</code> (tilpas til den målte ⟨Γγ⟩, op til bly), <code>gamma/actphys.py</code> (begge, for actinider).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "energi ↑",
  "named levels": "navngivne niveauer",
  "a crowd of states": "en mængde tilstande",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "varm tilstand, {#} MeV",
  "most photons ≈ {#} MeV": "flest fotoner ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "små fald: svage (E³ lille)",
  "big drops: bright, but few states to land on": "store fald: lyse, men få tilstande at lande på",
  // scene 2: gdr
  "protons": "protoner",
  "neutrons": "neutroner",
  "A = {#}: rings at {#} MeV": "A = {#}: svinger ved {#} MeV",
  "peak {#} MeV": "top {#} MeV",
  "giant resonance at {#} MeV": "kæmperesonans ved {#} MeV",
  "width ≈ {#} MeV": "bredde ≈ {#} MeV",
  "decays use this": "henfald bruger dette",
  "shaded: the tail decays use": "skraveret: halen, henfald bruger",
  "photon energy (MeV) →": "fotonenergi (MeV) →",
  "photon strength f (log scale) ↑": "fotonstyrke f (log-skala) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "en kugle har ingen blade: ingen saks",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "saks ≈ {#} MeV: styrke {#} % af den mest strakte",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "spin-flip ≈ {#} MeV: stabil, enhver form (tykke fotoner)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "upbend under {#} MeV: bløde fotoner, mange ved denne form",
  "upbend below {#} MeV: soft photons, fewer at this shape": "upbend under {#} MeV: bløde fotoner, færre ved denne form",
  "upbend below {#} MeV: soft photons, few at this shape": "upbend under {#} MeV: bløde fotoner, få ved denne form",
  // scene 4: cascade
  "ground state": "grundtilstand",
  "isomer": "isomer",
  "isomer: long-lived": "isomer: langlivet",
  "bins: too dense to list": "intervaller: for tætte at liste",
  "one photon at a time": "én foton ad gangen",
  "measured branching ratios": "målte forgreningsforhold",
  "▬ parity +   ▭ parity −": "▬ paritet +   ▭ paritet −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "indgang: J = {#}/{#}",
  "isomer: {#} ({#} %)": "isomer: {#} ({#} %)",
  "ground state: {#} ({#} %)": "grundtilstand: {#} ({#} %)",
  "many cascades: ≈ {#} % isomer": "mange kaskader: ≈ {#} % isomer",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "over mange kaskader fra J = {#}/{#}: ≈ {#} % ender på isomeren",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "fotondør: {#} eV, ændrer sig knap",
  "captured (n,γ): {#} ({#} %)": "indfanget (n,γ): {#} ({#} %)",
  "neutron: {#} eV": "neutron: {#} eV",
  "neutron door: {#} eV, wider when faster": "neutrondør: {#} eV, bredere når hurtigere",
  "back out: {#} ({#} %)": "ud igen: {#} ({#} %)",
  "more doors open (target left excited)": "flere døre åbne (target efterladt exciteret)",
  "{#} eV neutrons →": "neutroner på {#} eV →",
  "{#} keV neutrons →": "neutroner på {#} keV →",
  "{#} MeV neutrons →": "neutroner på {#} MeV →",
  "slow neutrons: the photon door wins": "langsomme neutroner: fotondøren vinder",
  "the neutron door wins; capture takes about {#} %": "neutrondøren vinder; indfangning tager ca. {#} %",
  "fast: capture is a rare event": "hurtige: indfangning er sjælden",
});
