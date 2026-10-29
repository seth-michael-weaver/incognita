/* Danish: strength (chapter 16, Expert) */
WT.L.ch.strength = {
  num: "Kapitel 25", title: "Fotonstyrke i detaljer", short: "Fotonstyrke",
  lead: "Kapitel 10 viste, hvilke fotoner en varm kerne foretrækker. Dette kapitel skriver styrkefunktionerne op, følger dem ind i transmissionskoefficienter og den gennemsnitlige strålingsbredde og kører den kaskade, de driver.",
  html: `
<div class="step">
  <h3>E1: halen af kæmpedipolresonansen</h3>
  <p><b>Fotonstyrkefunktionen</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) er den gennemsnitlige reducerede sandsynlighed for en foton af typen <i>XL</i>: elektrisk dipol E1, magnetisk dipol M1 og så videre. For E1 domineres den af kæmpedipolresonansen nær 18 MeV, men henfald ved <i>S<sub>n</sub></i> bruger fotoner på 1 til 7 MeV, langt nede ad dens hale, og halens form er hele spørgsmålet.</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">Sluttilstandenes temperatur T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>Den stiplede linje er den almindelige Lorentzfunktion (SLO), den form der er tilpasset fotoabsorption. Med sin konstante bredde overvurderer den styrken i henfaldsvinduet med en faktor 2 til 5, en længe kendt svigt for sfæriske kerner. Den fuldt optrukne linje er den forenklede modificerede Lorentzfunktion (<b>SMLO</b>): dens bredde vokser med fotonenergien og med sluttilstandenes temperatur, hvilket sænker halen i vinduet, men efterlader en endelig styrke ved nul fotonenergi, som henfaldsdata kræver. Zoomboksen viser dette gulv under 2 MeV: træk <i>T</i> til 0, og det forsvinder.</p>
</div>
<div class="step">
  <h3>M1: spin-flip, saksemode, upbend</h3>
  <p>M1-styrken er svagere, men ikke ubetydelig: en spin-flip-resonans nær 41<i>A</i><sup>−1/3</sup> MeV, en saksemode nær 3 MeV i deformerede kerner (styrken vokser som β²) og et upbend, en stigning mod fotonenergi nul, set i data fra Oslo-metoden og i skalmodelberegninger.</p>
  <div class="ctl"><label for="ps-b">Deformation β (saksemode)</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">Upbend</button></div>
  <p>Den svage linje bagved er E1. Ved de laveste fotonenergier, her under omkring 2 MeV, lader upbendet M1 komme på højde med den eller overgå den (markøren viser hvor), og derfor betyder upbendet noget for den bløde ende af kaskaden og for indfangning langt fra stabilitet. Motorens standard-M1 er IAEA's anbefaling med upbend, tabelleret pr. kerne, og dens standard-E1 er den tabellerede SMLO-2019; de lukkede udtryk her står i stedet for disse tabeller.</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p><b>Brink–Axel-hypotesen</b> siger, at styrken afhænger af fotonenergien og ikke af, hvor kernen starter: det samme <i>f</i> gælder for en resonans ved <i>S<sub>n</sub></i> og for en tilstand ved 4 MeV. (SMLO bevarer en svag afhængighed gennem <i>T</i>.) Hver startenergi udsender så med transmissionskoefficienten gange tætheden af sluttilstande.</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">Startenergi Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Produktet af et stigende <i>E</i><sub>γ</sub>³<i>f</i> og et faldende ρ giver en pukkel. Fra <i>S<sub>n</sub></i> topper den her nær 4 til 5 MeV. Fra lavere starter skæres den af ved startenergien; under tilpasningsenergien, hvor ρ er en konstanttemperatur-eksponentialfunktion, er formen den samme fra hver start, blot afskåret. Hypotesen testes ved at sammenligne styrker udtrukket ved forskellige excitationsenergier, og det er netop, hvad analyser af Oslo-typen gør.</p>
</div>
<div class="step">
  <h3>Den gennemsnitlige strålingsbredde</h3>
  <p>Summen over hver sluttilstand, der kan nås med E1 eller M1 fra s-bølge-resonanserne (<i>J</i><sup>π</sup> = ½⁺ på en targetkerne med spin 0), giver deres gennemsnitlige totale fotonbredde. Den er målt, ud fra resonansformer, for nogle hundrede kerner, og den er den vigtigste kontrol af styrken ved <i>S<sub>n</sub></i>.</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">Skala på styrken</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>Kurverne viser, hvor bredden kommer fra, foton for foton: mest 3 til 7 MeV og mest E1, hvor M1 bidrager med omkring 15 %. Her, med lukkede former og en skematisk niveautæthed i stedet for motorens tabeller, kommer bredden ud på omkring en sjettedel af de målte 0,92 eV: den er så følsom over for niveautætheden under <i>S<sub>n</sub></i> og for styrkens hale. TALYS' standarder, som motoren følger, giver omkring 1,3 eV for denne kerne. Skyderen anvender den ene samlede faktor, en evaluering ville tilpasse: omkring ×6 bringer den ind i det målte bånd. Indfangning i keV-området er næsten proportional med ⟨Γ<sub>γ</sub>⟩, når Γ<sub>γ</sub> ≪ Γ<sub>n</sub>, så en faktor her er en faktor i (n,γ). TALYS kan skalere styrken til en målt ⟨Γ<sub>γ</sub>⟩ (<code>gnorm</code>); i INCOGNITA er den skalering, anvendt på hver kerne i kaskaden, en valgfri kontakt, slukket som standard.</p>
</div>
<div class="step">
  <h3>Kaskaden</h3>
  <p>Under den første foton gentager den samme regel sig: fra hver ny energi trækkes den næste foton ud fra <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>), indtil kernen når sine kendte niveauer. Hver historie er nogle få fotoner; deres summerede spektrum er det, et kalorimeter ser efter indfangning.</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">Upbend</button><button class="btn ghost" data-act="clear">Start forfra</button></div>
  <p>Upbendet tilføjer bløde fotoner og en smule til multipliciteten. Motoren trækker ikke historier: den flytter populationer interval for interval, oppefra og ned (kapitel 11), hvilket giver de samme gennemsnit uden stikprøvestøj.</p>
  <div class="aside">I koden: <code>gamma/strength.py</code> (alle styrkemodeller, TALYS understøtter; som standard SMLO-2019-tabeller og IAEA's M1 med upbend), <code>gamma/parameters.py</code> (systematik for kæmperesonanser, tabeller), <code>gamma/transmission.py</code> (T = 2π E<sup>2L+1</sup> f), <code>gamma/ggnorm.py</code> (valgfri normering til ⟨Γγ⟩), <code>emission/</code> (kaskaden). Billedet bruger lukkede udtryk og systematik for en jern-57-lignende kerne; den målte ⟨Γγ⟩ er RIPL-værdien for ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: E1
  "E{#} strength f (MeV⁻³), A = {#}": "E{#}-styrke f (MeV⁻³), A = {#}",
  "Eγ (MeV)": "Eγ (MeV)",
  "photons that decay uses": "fotoner, som henfaldet bruger",
  "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
  "dashed: SLO": "stiplet: SLO",
  "at {#} MeV: SMLO / SLO = {#}": "ved {#} MeV: SMLO / SLO = {#}",
  "protons against neutrons": "protoner mod neutroner",
  // scene 2: M1
  "M{#} strength f (MeV⁻³), A = {#}": "M{#}-styrke f (MeV⁻³), A = {#}",
  "spin-flip": "spin-flip",
  "scissors, β = {#}": "saksemode, β = {#}",
  "upbend": "upbend",
  "faint: E{#} at T = {#} MeV": "svag: E{#} ved T = {#} MeV",
  "M{#} > E{#} below {#} MeV": "M{#} > E{#} under {#} MeV",
  "E{#} dominates at every energy here": "E{#} dominerer her ved alle energier",
  "scissors: the two deformed clouds rock": "saksemode: de to deformerede skyer vipper",
  // scene 3: Brink-Axel
  "from {#} MeV": "fra {#} MeV",
  "peak at Eγ ≈ {#} MeV": "top ved Eγ ≈ {#} MeV",
  "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "primærspektrum T(Eγ) ρ(Eₓ − Eγ), hvert skaleret til sin top",
  // scene 4: <Gamma_gamma>
  "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "bidrag til ⟨Γγ⟩ pr. MeV fotonenergi: E{#} (gul), M{#} (lilla, ovenpå)",
  "{#} eV": "{#} eV",
  "measured {#} eV": "målt {#} eV",
  "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "beregnet ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)",
  // scene 5: cascades
  "Sₙ": "Sₙ",
  "all photons from all cascades": "alle fotoner fra alle kaskader",
  "{#} cascades · mean multiplicity {#}": "{#} kaskader · middelmultiplicitet {#}",
});
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "Den forenklede modificerede Lorentz-form: en E1-styrkefunktion, hvis bredde vokser med fotonenergien og med sluttilstandenes temperatur.",
    more: "Foreslået af V. Plujko og medarbejdere og tabelleret for hver kerne i IAEA's database over fotonstyrkefunktioner (2019). Motorens standard-E1 er, ligesom i TALYS-2, denne SMLO-2019-tabel.",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Brink–Axel-hypotesen", aliases: ["Brink–Axel-hypotesen", "Brink–Axel-hypotese", "Brink–Axel"],
    short: "Antagelsen, at fotonstyrkefunktionen kun afhænger af fotonenergien og ikke af excitationsenergien for den tilstand, der udsender fotonen.",
    more: "Den lader én styrke, målt eller beregnet for grundtilstanden, gælde for hele kaskaden. Den testes ved at udtrække styrker ved forskellige excitationsenergier; den holder tilnærmelsesvis, med afvigelser, der diskuteres for bestemte kerner og energier.",
    chapter: "strength",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="up" data-act="up2" */
Object.assign(WT.L.labels, {
  "zoom: Eγ from {#} to {#} MeV": "zoom: Eγ fra {#} til {#} MeV",
  "floor: stays above zero": "bund: holder sig over nul",
  "continuum:": "kontinuum:",
  "dark = dense": "mørk = tæt",
  "known levels": "kendte niveauer",
});
