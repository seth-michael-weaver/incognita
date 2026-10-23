/* Dutch (Nederlands): gamma (Hoofdstuk 7, fotonemissie) */
WT.L.ch.gamma = {
  num: "Hoofdstuk 7", title: "Licht afgeven", short: "Fotonen",
  lead: "Als er geen deeltje vertrekt, koelt de kern af door fotonen uit te zenden: gammastralen, deeltjes van hoogenergetisch licht. Deze uitgang staat bij elke energie open.",
  html: `
<div class="step">
  <p>Een hete toestand bij 8 MeV (miljoen elektronvolt) zendt fotonen (γ) uit; de stapel naast de ladder verzamelt waar ze landen. Onder 2 MeV zijn de toestanden een paar benoemde sporten; daarboven een menigte die met de energie steil dichter wordt (grijze stippen). Elk foton neemt de energie van zijn val mee, <i>E<sub>γ</sub></i>, en wordt helderder getekend naar verhouding van <i>E<sub>γ</sub></i>³.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p><i>T<sub>γ</sub></i> is de transmissiecoëfficiënt van het foton (de deur uit hoofdstuk 6), <i>l</i> = 1 voor dipoolfotonen, en <i>f</i> is de <b>fotonsterkte</b>: hoe makkelijk de kern bij die energie straalt. De kans op een val is <i>T<sub>γ</sub></i> maal de menigte toestanden waar hij landt: kleine vallen vinden veel toestanden maar zijn zwak; grote vallen zijn helder maar vinden er weinig.</p>
  <div class="ctl"><label for="gm-e0">Beginenergie</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">Zend er 100 uit</button></div>
  <p>De stapel piekt een paar MeV onder het begin: de meeste fotonen dragen 2 tot 4 MeV. Verschuif de beginenergie en de piek volgt.</p>
</div>
<div class="step">
  <h3>De hele kern trilt</h3>
  <p>De grote piek rechts is de <b>gigantische dipoolresonantie</b>: alle protonen (gearceerd, links) die tegen alle neutronen (gevuld) in heen en weer klotsen. Haar frequentie bepaalt bij welke fotonenergie de kern het makkelijkst absorbeert en uitzendt. De curve is de fotonsterkte <i>f</i>, op een logaritmische schaal (elke stap omhoog is tien keer meer).</p>
  <div class="ctl"><label for="gm-a">Massagetal A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Sleep het massagetal A (protonen plus neutronen): zware kernen klotsen langzamer en trillen rond 12 tot 14 MeV; lichte rond 20. Een vervallende kern zendt fotonen van maar een paar MeV uit, dus wat het meest telt is de gearceerde staart bij lage energie.</p>
</div>
<div class="step">
  <h3>Schaar en upbend</h3>
  <p>Een vervormde kern straalt ook magnetisch: zijn protonen (gearceerd) en neutronen (gevuld), twee rugbyballen, schommelen tegen elkaar in als schaarbladen. Deze <b>schaarmodus</b> ligt rond 3 MeV. <b>Spin-flip</b>, rond 8 MeV, is het omklappen van de spin van afzonderlijke nucleonen (de pijltjes), bij elke vorm.</p>
  <div class="ctl"><label for="gm-b">Vervorming β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Sleep de vervorming β₂ (0 is een bol). Hoe sterker uitgerekt, hoe meer schaarfotonen er vliegen; een bol heeft er geen. Bij de laagste energieën stijgt de sterkte weer: de <b>upbend</b>, een straaltje zachte fotonen, die de motor afzwakt naarmate de kern vervormt. Een optionele schakelaar, standaard uit, gebruikt een sterkere schaarsystematiek die overeenkomt met Oslo-metingen (vier tot vijf keer sterker in uranium).</p>
</div>
<div class="step">
  <h3>De ladder af</h3>
  <p>Een cascade is een reeks fotonen die na elkaar worden uitgezonden, van de bins bovenaan (toestanden te dicht om op te sommen, hoofdstuk 5) tot de benoemde niveaus, uitgerekt zodat je ze kunt lezen (dichte sport pariteit +, holle −). Daar stopt de motor met schatten en volgt hij de getabelleerde <b>vertakkingsverhoudingen</b>: de gemeten kansen dat elk niveau naar elk lager niveau vervalt.</p>
  <div class="btns"><button class="btn" data-act="drop">Laat een cascade vallen</button></div>
  <p>Druk een paar keer op de knop: het bovenste deel verandert elke keer; het einde volgt een van een paar gemeten paden.</p>
</div>
<div class="step">
  <h3>Planken die vasthouden</h3>
  <p>Het 11/2−-niveau bij 0,40 MeV is een <b>isomeer</b>: zijn spin ligt zo ver van de niveaus eronder dat een foton ze nauwelijks kan verbinden, dus het leeft seconden tot jaren, en wat daar landt, blijft. De motor behandelt elk niveau dat langer dan een seconde leeft als een eindpunt. Elk bolletje is één cascade, die eindigt op de stapel van de isomeer of op die van de grondtoestand.</p>
  <div class="ctl"><label for="gm-j">Beginspin</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Sleep de beginspin, waar de cascades starten, en de stapels beginnen opnieuw. Het deel dat op de isomeer eindigt, de <b>isomeerverhouding</b>, hangt ervan af: een begin met hoge spin voedt de isomeer met hoge spin; een begin met lage spin glijdt erlangs naar de grondtoestand.</p>
</div>
<div class="step">
  <h3>Vangst</h3>
  <p>Een kern die net een langzaam neutron heeft geabsorbeerd, heeft twee uitgangsdeuren (hoofdstuk 6): fotonen (boven) en het neutron dat weer naar buiten gaat (rechts). De opening van elke deur is haar <b>breedte</b>, in eV: hoe snel de kern erdoor vervalt. De fotonbreedte verandert nauwelijks; de neutronbreedte groeit met de snelheid van het neutron.</p>
  <div class="ctl"><label for="gm-e">Neutronenergie</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1,0 keV</output></div>
  <p>Sleep de neutronenergie, van 10 eV tot 2 MeV. <b>Vangst</b>, (n,γ), betekent dat het neutron blijft en er een foton vertrekt: bij 10 eV wint ze meestal, boven een paar keV wordt ze een klein aandeel. De fotonbreedte bij de drempel is voor honderden kernen gemeten, een controle op de fotonsterkte. Standaard gebruikt de motor zijn eigen; een optionele schakelaar schaalt de fotonsterkte van elke gemeten kern tot de twee overeenkomen.</p>
  <div class="aside">In de code: <code>gamma/parameters.py</code> (getabelleerde E1-sterkten; systematiek voor gigantische resonantie, spin-flip, schaar en upbend), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) voor elke multipool), <code>gamma/transmission.py</code> (T<sub>γ</sub> en de gemiddelde stralingsbreedte), <code>structure/levels.py</code> (vertakkingsverhoudingen, isomeren), <code>emission/multiple.py</code> (de cascade). Optioneel, standaard uit: <code>gamma/scissors.py</code> (sterkere schaar), <code>gamma/ggnorm.py</code> (de gemeten ⟨Γγ⟩ halen, tot lood), <code>gamma/actphys.py</code> (beide, voor actiniden).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "energie ↑",
  "named levels": "benoemde niveaus",
  "a crowd of states": "een menigte toestanden",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "hete toestand, {#} MeV",
  "most photons ≈ {#} MeV": "meeste fotonen ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "kleine vallen: zwak (E³ piepklein)",
  "big drops: bright, but few states to land on": "grote vallen: helder, maar weinig toestanden om op te landen",
  // scene 2: gdr
  "protons": "protonen",
  "neutrons": "neutronen",
  "A = {#}: rings at {#} MeV": "A = {#}: trilt bij {#} MeV",
  "peak {#} MeV": "piek {#} MeV",
  "giant resonance at {#} MeV": "gigantische resonantie bij {#} MeV",
  "width ≈ {#} MeV": "breedte ≈ {#} MeV",
  "decays use this": "verval gebruikt dit",
  "shaded: the tail decays use": "gearceerd: de staart die verval gebruikt",
  "photon energy (MeV) →": "fotonenergie (MeV) →",
  "photon strength f (log scale) ↑": "fotonsterkte f (log. schaal) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "een bol heeft geen bladen: geen schaar",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "schaar ≈ {#} MeV: sterkte {#} % van de meest uitgerekte",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "spin-flip ≈ {#} MeV: constant, elke vorm (dikke fotonen)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "upbend onder {#} MeV: zachte fotonen, veel bij deze vorm",
  "upbend below {#} MeV: soft photons, fewer at this shape": "upbend onder {#} MeV: zachte fotonen, minder bij deze vorm",
  "upbend below {#} MeV: soft photons, few at this shape": "upbend onder {#} MeV: zachte fotonen, weinig bij deze vorm",
  // scene 4: cascade
  "ground state": "grondtoestand",
  "isomer": "isomeer",
  "isomer: long-lived": "isomeer: langlevend",
  "bins: too dense to list": "bins: te dicht om op te sommen",
  "one photon at a time": "één foton tegelijk",
  "measured branching ratios": "gemeten vertakkingsverhoudingen",
  "▬ parity +   ▭ parity −": "▬ pariteit +   ▭ pariteit −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "begin: J = {#}/{#}",
  "isomer: {#} ({#} %)": "isomeer: {#} ({#} %)",
  "ground state: {#} ({#} %)": "grondtoestand: {#} ({#} %)",
  "many cascades: ≈ {#} % isomer": "veel cascades: ≈ {#} % isomeer",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "over veel cascades vanaf J = {#}/{#}: ≈ {#} % eindigt op de isomeer",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "fotondeur: {#} eV, verandert nauwelijks",
  "captured (n,γ): {#} ({#} %)": "ingevangen (n,γ): {#} ({#} %)",
  "neutron: {#} eV": "neutron: {#} eV",
  "neutron door: {#} eV, wider when faster": "neutrondeur: {#} eV, breder als het sneller is",
  "back out: {#} ({#} %)": "weer eruit: {#} ({#} %)",
  "more doors open (target left excited)": "meer deuren open (trefkern aangeslagen)",
  "{#} eV neutrons →": "neutronen van {#} eV →",
  "{#} keV neutrons →": "neutronen van {#} keV →",
  "{#} MeV neutrons →": "neutronen van {#} MeV →",
  "slow neutrons: the photon door wins": "langzame neutronen: de fotondeur wint",
  "the neutron door wins; capture takes about {#} %": "de neutrondeur wint; vangst neemt ongeveer {#} %",
  "fast: capture is a rare event": "snel: vangst is zeldzaam",
});
