/* Dutch (Nederlands): cascade (Hoofdstuk 11, de kaart af) */
WT.L.ch.cascade = {
  num: "Hoofdstuk 11", title: "De emissiecascade", short: "Cascade",
  lead: "Eén emissie is zelden het einde: de kern die achterblijft, is vaak heet genoeg om opnieuw iets uit te zenden.",
  html: `
<div class="step">
  <p>Een neutron heeft de compoundkern (links) verlaten, en de <b>restkern</b> die het achterlaat (rechts) is nog heet. Het oranje bolletje is de energie. De grondtoestand van de restkern ligt hoger, met de <b>separatie-energie</b> S<sub>n</sub> van het neutron, de kosten om het eruit te halen.</p>
  <p>Telkens als er een neutron vertrekt, zakt het bolletje met de kinetische energie van het neutron. Waar het stopt, is de <b>excitatie</b> van de restkern, haar reserve-energie; de stippen rechts tellen de landingen.</p>
  <div class="ctl"><label for="cs-e">Neutronenergie</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Uitgezonden neutronen zijn meestal langzaam, dus de meeste vallen zijn kort. Blauwe stippen liggen boven de gestippelde neutrondrempel: die kunnen zich een tweede neutron veroorloven, de reactie (n,2n). Onder ongeveer 11 MeV komt er geen enkele zover.</p>
</div>
<div class="step">
  <h3>Opeenvolgende emissie over de kaart</h3>
  <p>De stromen zijn reacties die over een hoek van de <b>nuclidenkaart</b> lopen, waarop kernen staan uitgezet naar neutronengetal N (horizontaal) en protonengetal Z (verticaal). Elke stroom begint in het omlijnde compoundvakje; elk vakje is genoemd naar de reactie die daar eindigt.</p>
  <p>Een <em class="n">neutron</em> eruit schuift één vakje naar links, een <em class="p">proton</em> één naar beneden, een <em class="a">alfadeeltje</em> (twee protonen, twee neutronen) twee schuin. De breedte van een stroom is hoeveel die stap zet; tint en percentage geven aan waar reacties eindigen.</p>
  <div class="ctl"><label for="cs-e4">Neutronenergie</label><input id="cs-e4" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Schiet 200 reacties af</button></div>
  <p>Sleep de energie: bij een paar MeV stopt bijna alles op het doelvakje; hoger bereiken de stromen verder. Elke stap kost 7 tot 11 MeV aan separatie-energie, dus zelfs bij 30 MeV is de tocht hooguit drie of vier stappen lang.</p>
</div>
<div class="step">
  <h3>Boekhouding van de bezetting</h3>
  <p>De motor leegt elke kern van boven naar beneden, één energieplak, of <b>bin</b>, tegelijk. Rechts: de restkern van de eerste emissie; links: haar dochter, met één neutron minder. Oranje bolletjes zijn reacties die in elke bin wachten. De bins zijn hier 1 MeV; de motor gebruikt er ongeveer 40 per kern, afgestemd op de beschikbare energie.</p>
  <p>Terwijl de markering een bin doorloopt, neemt elk bolletje een uitgang volgens de competitie van hoofdstuk 9: een foton (<em class="g">γ</em>) laat het naar een lagere bin zakken, een <em class="n">neutron</em> verplaatst het naar de dochter, een proton of alfa haalt het uit beeld. Onder elke drempel brengen fotonen de rest naar de grondtoestand (grijs). Dan wordt de dochter doorlopen.</p>
  <div class="ctl"><label for="cs-e3">Neutronenergie</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Opnieuw beginnen</button></div>
  <p>Fotonen vallen alleen omlaag, en elke kern is klaar voordat haar dochters aan de beurt zijn, dus niets landt op een bin die al geleegd is.</p>
</div>
<div class="step">
  <h3>Exclusieve reactiekanalen</h3>
  <p>Er speelt telkens één reactie af: de markering springt over de kaart en elk uitgezonden deeltje valt in het bakje. Elk kanaal speelt af bij een energie waarbij het echt gebeurt (bovenaan de afbeelding): (n,3n) bij 25 MeV, omdat drie neutronen hier meer dan 20 MeV kosten; vangst, (n,γ), bij 1 MeV. Het volle bakje geeft de naam van het <b>exclusieve kanaal</b>, zoals (n,2n); fotonen tellen niet mee. De motor geeft elk kanaal zijn eigen werkzame doorsnede (zijn waarschijnlijkheid, uitgedrukt als effectief trefoppervlak).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Volgend kanaal</button></div>
  <p>Loop ze door. (n,np) speelt twee keer af, eerst het neutron en eerst het proton: hetzelfde vakje, hetzelfde bakje, één kanaal. Dan bereikt een spookdeuteron (een gebonden proton en neutron) dat vakje in één sprong: zijn bakje zegt d, een ander kanaal, (n,d).</p>
</div>
<div class="step">
  <h3>Residuproductie</h3>
  <p>Elk vakje heeft nu planken: inkt voor de <b>grondtoestand</b>, groen (op twee vakjes) voor een <b>isomeer</b>, een aangeslagen toestand die lang genoeg leeft om als apart product te tellen. De hoogte van de stapel is de <b>productie van restkernen</b>: hoeveel van elke kern de reacties hebben gemaakt.</p>
  <div class="ctl"><label for="cs-e2">Neutronenergie</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Schiet 200 reacties af</button></div>
  <p>Sleep de energie: de volgende reeks gebruikt haar en oude stapels vervagen. De productie schuift weg van het begin naarmate meer deeltjes kunnen vertrekken. Elke geschiedenis eindigt op een plank, en een activeringsmeting ziet precies deze stapels: bestraal een monster en tel daarna de vervallen van elk product.</p>
  <div class="aside">In de code: <code>emission/multiple.py</code> (de lus over kernen en bins, de γ-cascade), <code>emission/feeding.py</code> (roosters en invoer voor elke kern van de keten), <code>compound/continuum.py</code> (het verval van één bin), <code>emission/channels.py</code> (exclusieve kanalen, productie van restkernen, isomeertakken), <code>emission/binary.py</code> (de boekhouding van de eerste emissie).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged in Dutch)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "compound", "target": "trefkern",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "neutronengetal →",
  // scene 1
  "levels": "niveaus",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "grond",
  "residual": "restkern", "residual (one neutron fewer)": "restkern (één neutron minder)",
  "n threshold": "n-drempel", "its neutron threshold": "haar neutrondrempel",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "val = kinetische energie van het neutron",
  "{#} % land above the threshold: a second neutron can leave": "{#} % landt boven de drempel: een tweede neutron kan vertrekken",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % landt boven de drempel: een tweede neutron kan vertrekken",
  "all land below the threshold: only photons remain": "alles landt onder de drempel: alleen fotonen blijven over",
  "{#} % above threshold: (n,{#}n) possible": "{#} % boven drempel: (n,{#}n) mogelijk",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % boven drempel: (n,{#}n) mogelijk",
  "all below threshold: photons only": "alles onder drempel: alleen fotonen",
  // scene 2
  "incoming neutron: {#} MeV": "binnenkomend neutron: {#} MeV",
  "shade and % = where reactions end": "tint en % = waar reacties eindigen",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "breedte = stroom · tint en % = deel van de reacties dat in die kern eindigt",
  // scene 3
  "residual (first step)": "restkern (eerste stap)",
  "daughter: n fewer": "dochter: n minder", "daughter (one neutron fewer)": "dochter (één neutron minder)",
  "now: {#}–{#} MeV": "nu: {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "klaar: {#} vertrokken via proton of alfa, de rest zit op grondtoestanden",
  "done: everything sits on a ground state": "klaar: alles zit op een grondtoestand",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "oranje bolletje = wachtende reacties · grijs = op de grondtoestand · bleke bins = al geleegd",
  // scene 4
  "collected": "verzameld",
  "tray: d": "bakje: d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "een deuteron landt op hetzelfde vakje, maar zijn bakje zegt d: kanaal (n,d)",
  "tray: n n  →  (n,{#}n)": "bakje: n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "bakje: n  →  (n,n′)",
  "tray: p  →  (n,p)": "bakje: p  →  (n,p)",
  "tray: n p  →  (n,np)": "bakje: n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "bakje: n p  →  (n,np) · zelfde vakje, zelfde bakje",
  "tray: a  →  (n,α)": "bakje: a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "bakje: n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "bakje leeg, alleen fotonen: (n,γ), vangst",
  "each emitted particle falls into the tray": "elk uitgezonden deeltje valt in het bakje",
  "no particle gets out: only photons": "er komt geen deeltje uit: alleen fotonen",
  "incoming neutron: {#} MeV · channel {#} of {#}": "binnenkomend neutron: {#} MeV · kanaal {#} van {#}",
  // scene 5
  "isomer": "isomeer",
  "batch of {#} at {#} MeV": "reeks van {#} bij {#} MeV",
  "ink shelf: ground state · green: isomer": "inkt: grondtoestand · groen: isomeer",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "inkt: grondtoestand · groen: isomeer · stapelhoogte = hoeveel van die kern gemaakt is",
});
