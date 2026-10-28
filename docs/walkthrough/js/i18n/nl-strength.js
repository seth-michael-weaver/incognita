/* Dutch (Nederlands): strength (Hoofdstuk 25, fotonsterkte in detail) */
WT.L.ch.strength = {
  num: "Hoofdstuk 25", title: "Fotonsterkte in detail", short: "Fotonsterkte",
  lead: "Hoofdstuk 10 liet zien welke fotonen een hete kern verkiest. Dit hoofdstuk schrijft de sterktefuncties uit, volgt ze tot in de transmissiecoëfficiënten en de gemiddelde stralingsbreedte, en draait de cascade die ze aandrijven.",
  html: `
<div class="step">
  <h3>E1: de staart van de gigantische dipoolresonantie</h3>
  <p>De <b>fotonsterktefunctie</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) is de gemiddelde gereduceerde waarschijnlijkheid voor een foton van type <i>XL</i>: elektrische dipool E1, magnetische dipool M1, enzovoort. Voor E1 wordt ze gedomineerd door de gigantische dipoolresonantie rond 18 MeV, maar verval bij <i>S<sub>n</sub></i> gebruikt fotonen van 1 tot 7 MeV, ver in haar staart, en de vorm van die staart is de hele vraag.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Temperatuur van de eindtoestanden T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>De gestippelde lijn is de standaardlorentziaan (SLO), de vorm die aan fotoabsorptie is gefit. Met haar constante breedte overschat ze de sterkte in het vervalvenster met een factor 2 tot 5, een al lang bekend tekort bij sferische kernen. De doorgetrokken lijn is de vereenvoudigde gemodificeerde lorentziaan (<b>SMLO</b>): haar breedte groeit met de fotonenergie en met de temperatuur van de eindtoestanden, wat de staart in het venster verlaagt maar bij fotonenergie nul een eindige sterkte overlaat, zoals vervalsdata vereisen. Sleep <i>T</i> naar 0 en die bodem bij lage energie valt weg.</p>
</div>
<div class="step">
  <h3>M1: spin-flip, schaar, upbend</h3>
  <p>M1-sterkte is zwakker maar niet verwaarloosbaar: een spin-flipresonantie rond 41<i>A</i><sup>−1/3</sup> MeV, een schaarmodus rond 3 MeV in vervormde kernen (sterkte die groeit als β²), en een upbend, een stijging naar fotonenergie nul die wordt gezien in data volgens de Oslo-methode en in berekeningen met het schillenmodel.</p>
  <div class="ctl"><label for="ps-b">Vervorming β (schaar)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>De vage lijn erachter is E1. Bij de laagste fotonenergieën, hier onder ongeveer 2 MeV, laat de upbend M1 E1 evenaren of overtreffen (de markering toont waar), en daarom telt de upbend voor het zachte einde van de cascade en voor vangst ver van de stabiliteit. De standaard-M1 van de motor is de IAEA-aanbeveling met upbend, per kern getabelleerd, en zijn standaard-E1 is de getabelleerde SMLO-2019; de gesloten vormen hier staan in voor die tabellen.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p>De <b>hypothese van Brink–Axel</b> zegt dat de sterkte afhangt van de fotonenergie en niet van waar de kern begint: dezelfde <i>f</i> geldt voor een resonantie bij <i>S<sub>n</sub></i> en voor een toestand bij 4 MeV. (SMLO houdt via <i>T</i> een zwakke afhankelijkheid.) Elke beginenergie straalt dan uit met de transmissiecoëfficiënt maal de dichtheid van eindtoestanden.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Beginenergie Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Het product van een stijgende <i>E</i><sub>γ</sub>³<i>f</i> en een dalende ρ maakt een bult. Vanaf <i>S<sub>n</sub></i> piekt die hier rond 4 à 5 MeV. Vanuit lagere beginpunten wordt ze afgekapt bij de beginenergie; onder de aansluitenergie, waar ρ een exponentiële functie met constante temperatuur is, is de vorm vanuit elk beginpunt dezelfde, alleen afgekapt. Toets de hypothese door sterkten te vergelijken die bij verschillende excitatie-energieën zijn bepaald; dat doen analyses volgens de Oslo-methode.</p>
</div>
<div class="step">
  <h3>De gemiddelde stralingsbreedte</h3>
  <p>Optellen over elke eindtoestand die met E1 of M1 bereikbaar is vanuit de s-golfresonanties (<i>J</i><sup>π</sup> = ½⁺ op een trefkern met spin 0) geeft hun gemiddelde totale fotonbreedte. Die is voor een paar honderd kernen gemeten, uit resonantievormen, en ze is de belangrijkste controle op de sterkte bij <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Schaalfactor op de sterkte</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>De curven tonen waar de breedte vandaan komt, foton voor foton: vooral van 3 tot 7 MeV, en vooral E1, waarbij M1 ongeveer 15 % toevoegt. Hier, met gesloten vormen en een schematische niveaudichtheid in plaats van de tabellen van de motor, komt de breedte uit op ongeveer een zesde van de gemeten 0,92 eV: zo gevoelig is ze voor de niveaudichtheid onder <i>S<sub>n</sub></i> en voor de staart van de sterkte. De standaardinstellingen van TALYS, die de motor volgt, geven voor deze kern ongeveer 1,3 eV. De schuif past de ene totale factor toe die een evaluatie zou fitten. Vangst in het keV-gebied is bijna evenredig met ⟨Γ<sub>γ</sub>⟩ wanneer Γ<sub>γ</sub> ≪ Γ<sub>n</sub>, dus een factor hier is een factor in (n,γ). TALYS kan de sterkte herschalen naar een gemeten ⟨Γ<sub>γ</sub>⟩ (<code>gnorm</code>); in INCOGNITA is die herschaling, toegepast op elke kern van de cascade, een optionele schakelaar, standaard uit.</p>
</div>
<div class="step">
  <h3>De cascade</h3>
  <p>Onder het eerste foton herhaalt dezelfde regel zich: vanuit elke nieuwe energie wordt het volgende foton getrokken uit <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>), tot de kern haar bekende niveaus bereikt. Elke geschiedenis telt een paar fotonen; hun opgetelde spectrum is wat een calorimeter na vangst ziet.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Opnieuw beginnen</button></div>
  <p>De upbend voegt zachte fotonen toe en verhoogt de multipliciteit een beetje. De motor trekt geen geschiedenissen: hij verplaatst populaties bin voor bin, van boven naar beneden (hoofdstuk 11), wat dezelfde gemiddelden geeft zonder steekproefruis.</p>
  <div class="aside">In de code: <code>gamma/strength.py</code> (elk sterktemodel dat TALYS ondersteunt; standaard de SMLO-2019-tabellen en de IAEA-M1 met upbend), <code>gamma/parameters.py</code> (systematiek en tabellen voor gigantische resonanties), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (optionele ⟨Γγ⟩-normalisatie), <code>emission/</code> (de cascade). De afbeelding gebruikt gesloten vormen en systematiek voor een kern zoals ijzer-57; de gemeten ⟨Γγ⟩ is de RIPL-waarde voor ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "Eγ (MeV)": "Eγ (MeV)", "{#} eV": "{#} eV", "Sₙ": "Sₙ",
  // scene 1: E1
  "E{#} strength f (MeV⁻³), A = {#}": "E{#}-sterkte f (MeV⁻³), A = {#}",
  "photons that decay uses": "fotonen die het verval gebruikt",
  "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
  "dashed: SLO": "gestippeld: SLO",
  "at {#} MeV: SMLO / SLO = {#}": "bij {#} MeV: SMLO / SLO = {#}",
  "protons against neutrons": "protonen tegen neutronen",
  // scene 2: M1
  "M{#} strength f (MeV⁻³), A = {#}": "M{#}-sterkte f (MeV⁻³), A = {#}",
  "spin-flip": "spin-flip", "upbend": "upbend",
  "scissors, β = {#}": "schaar, β = {#}",
  "faint: E{#} at T = {#} MeV": "vaag: E{#} bij T = {#} MeV",
  "M{#} > E{#} below {#} MeV": "M{#} > E{#} onder {#} MeV",
  "E{#} dominates at every energy here": "E{#} domineert hier bij elke energie",
  "scissors: the two deformed clouds rock": "schaar: de twee vervormde wolken schommelen",
  // scene 3: Brink-Axel
  "from {#} MeV": "vanaf {#} MeV",
  "peak at Eγ ≈ {#} MeV": "piek bij Eγ ≈ {#} MeV",
  "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "primair spectrum T(Eγ) ρ(Eₓ − Eγ), elk geschaald op de eigen piek",
  // scene 4: <Gamma_gamma>
  "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "bijdrage aan ⟨Γγ⟩ per MeV fotonenergie: E{#} (geel), M{#} (paars, erbovenop)",
  "measured {#} eV": "gemeten {#} eV",
  "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "berekend ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)",
  // scene 5: cascades
  "all photons from all cascades": "alle fotonen uit alle cascades",
  "{#} cascades · mean multiplicity {#}": "{#} cascades · gemiddelde multipliciteit {#}",
});
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "De vereenvoudigde gemodificeerde lorentziaan (simplified modified Lorentzian): een E1-sterktefunctie waarvan de breedte groeit met de fotonenergie en met de temperatuur van de eindtoestanden.",
    more: "Voorgesteld door V. Plujko en medewerkers, en voor elke kern getabelleerd in de IAEA-database van fotonsterktefuncties (2019). De standaard-E1 van de motor is, net als die van TALYS-2, die SMLO-2019-tabel.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Hypothese van Brink–Axel", aliases: ["hypothese van Brink–Axel", "Brink–Axel"],
    short: "De aanname dat de fotonsterktefunctie alleen afhangt van de fotonenergie, niet van de excitatie-energie van de toestand die het foton uitzendt.",
    more: "Daardoor kan één sterkte, gemeten of berekend voor de grondtoestand, de hele cascade bedienen. Ze wordt getoetst door sterkten bij verschillende excitatie-energieën te bepalen; ze geldt bij benadering, en over afwijkingen voor bepaalde kernen en energieën wordt nog gediscussieerd.",
    chapter: "strength",
  },
});
