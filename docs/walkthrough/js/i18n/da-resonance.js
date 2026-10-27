/* Danish: resonance (chapter 10) */
WT.L.ch.resonance = {
  num: "Kapitel 15", title: "Skarpe toppe", short: "Resonanser",
  lead: "Ved lav nok energi ser en neutron ikke længere en glat, gennemsnitlig kerne. Den ser compoundkernens enkelte energiniveauer, ét ad gangen.",
  html: `
<div class="step">
  <p>Hver top er én <b>resonans</b>: et energiniveau i compoundkernen, som en neutron med netop den energi kan falde ned i. Højden er tværsnittet for <b>indfangning</b> dér (neutronen absorberes, fotoner kommer ud) på en logaritmisk skala; bredden er resonansbredden Γ, tegnet omkring hundrede gange bredere, end den er.</p>
  <div class="ctl"><label for="res-e">Neutronenergi (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>Neutronen hopper hen ad energiaksen; der, hvor den lander, kan den blive indfanget i et glimt af fotoner. På en top er tværsnittet tusinder af barn, og indfangning er næsten sikker; mellem toppene er det nogle få barn. Træk i energien for at parkere den på en top og derefter mellem to.</p>
</div>
<div class="step">
  <h3>Toppene holder afstand</h3>
  <p>Den midterste række viser, hvordan virkelige niveauer ligger: to niveauer med samme spin og paritet frastøder hinanden, så næsten-sammenfald er sjældne. <b>Teorien for tilfældige matricer</b> beskriver dette mønster. Helt tilfældige positioner (øverste række) klumper sig sammen og efterlader huller.</p>
  <div class="btns"><button class="btn" data-act="again">Træk igen</button></div>
  <p>Træk igen for at få en ny stikprøve. ⟨r̃⟩ sammenligner hver afstand med den næste: omkring 0,39 for tilfældige, 0,53 for niveauer, der frastøder hinanden; koden bruger frastødningsmønsteret. Blandes to sekvenser, f.eks. to spin (nederste række), skjules frastødningen delvist.</p>
</div>
<div class="step">
  <h3>Højderne spreder sig vildt</h3>
  <p>Nu er hver tops højde dens <b>neutronbredde</b> Γ<sub>n</sub> på en lineær skala: hvor stærkt niveauet kobler til en neutron. Den gule hætte er dens γ-bredde Γ<sub>γ</sub>, hvor hurtigt den udsender fotoner; den summerer hundredvis af fotonveje, så den er næsten ens for alle niveauer.</p>
  <div class="btns"><button class="btn" data-act="roll">Slå en bredde</button><button class="btn ghost" data-act="equal">Ens bredder</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>Et niveau har kun én måde at bryde op i neutron plus targetkerne på, så dets bredde opfører sig som kvadratet af ét tal fra en klokkekurve. Slå et: kuglen lander i <i>x</i>, <i>x</i>² bliver den næste tops højde, og en prik falder ned i bunken. Bunken hober sig op nær nul med en lang hale, <b>Porter–Thomas-loven</b>: de fleste niveauer er svage, nogle få enorme. Ens bredder viser i stedet en række gennemsnitlige toppe.</p>
</div>
<div class="step">
  <h3>En stige ud fra fire tal</h3>
  <p>Toppene kommer nu fra fire gennemsnit, som du selv kan indstille. For en kerne, der ikke er målt, kan kun disse gennemsnit forudsiges: middelafstanden <i>D</i><sub>0</sub>; <b>styrkefunktionerne</b> <i>S</i><sub>0</sub> og <i>S</i><sub>1</sub>, den gennemsnitlige neutronbredde pr. afstandsenhed for s-bølge-neutroner (centralt ramt) og p-bølge-neutroner (skævt ramt); og den gennemsnitlige γ-bredde. Ud fra dem bygger koden en <b>stige</b>: ét tilfældigt sæt niveauer med netop de gennemsnit.</p>
  <div class="ctl"><label for="res-d0">Afstand D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Styrke S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">γ-bredde ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Træk i <i>D</i><sub>0</sub>, og toppene spredes eller trænges sammen. Udfyldte toppe er s-bølge-niveauer (positiv paritet), konturtoppe p-bølge-niveauer (negativ paritet). Neutronbredderne vokser som √<i>E</i> for s-bølger og som <i>E</i><sup>3/2</sup> for p-bølger, så konturtoppene starter lave og vokser mod højre.</p>
</div>
<div class="step">
  <h3>Nede ved termisk energi</h3>
  <p>De samme toppe på en logaritmisk energiskala, ned til tusindedele af en eV. Neutroner i en reaktor bremses ved at støde mod lette kerner og mister omtrent den samme brøkdel af deres energi hver gang, så hvert hop her er lige langt. Nogle bliver fanget af toppene undervejs.</p>
  <div class="btns"><button class="btn" data-act="slow">Brems 10 neutroner</button></div>
  <p>De, der kommer igennem, falder til ro ved stuetemperatur, 0,025 eV, den <b>termiske</b> energi, langt under den første top. Dér er tværsnittet, skivens areal, summen af resonansernes haler, også fra bundne niveauer lige under nul; halerne vokser som 1/<i>v</i> (<i>v</i> er neutronens fart), så bunden stiger mod venstre. Fangsten på vejen ned måles med <b>resonansintegralet</b>: tværsnittet over 0,5 eV, hvor hver energi vægtes med 1/<i>E</i>.</p>
</div>
<div class="step">
  <h3>Kun statistikken kan forudsiges</h3>
  <p>Hver række er én stige trukket ud fra de samme fire tal, med en skive, hvis areal er dens termiske indfangningstværsnit. Klammen rækker hen til den top, der bestemmer værdien, som regel den nærmeste; dens afstand skifter fra stige til stige, og skiven svinger med en faktor ti eller mere.</p>
  <div class="btns"><button class="btn" data-act="draw1">Træk en stige</button><button class="btn ghost" data-act="more">Træk 20</button></div>
  <p>Hver værdi falder ned i bunken til højre. For en kerne, der ikke er målt, er svaret en spredning af værdier, ikke ét tal, og ingen bedre model kan indsnævre den. Resonansintegralet, en sum over mange toppe, spreder sig mindre. Hvor niveauerne ligger mere end omkring 10 keV fra hinanden, som i lette kerner, ligger ingen nær termisk energi: indfangning dér er direkte, og koden nægter at svare.</p>
  <div class="aside">I koden: <code>physics/resonance/ladder.py</code> (afstande fra tilfældige matricer, Porter–Thomas-bredder, Breit–Wigner-tværsnit, termisk indfangning og resonansintegral over et ensemble), <code>ladder_statistics.py</code> (de samme love testet på målte stiger), <code>ensemble_runner.py</code>. De kører ved siden af reaktionsmotoren, ikke inde i den.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "højde: maks. indfangning (log) · bredde Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "tophøjde: indfangningstværsnit (log-skala) · bredde: resonansbredde Γ, tegnet {#}× bredere",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "s-bølge (+ paritet)", "p-wave (− parity)": "p-bølge (− paritet)",
  "caught {#} times in {#} landings": "fanget {#} gange ved {#} landinger",
  "each peak: one level of the compound nucleus": "hver top: ét niveau i compoundkernen",
  "each peak: one level of the compound nucleus · about {#} eV apart": "hver top: ét niveau i compoundkernen · ca. {#} eV imellem",
  // spacing
  "random positions (Poisson)": "tilfældige positioner (Poisson)",
  "repelling levels (random-matrix)": "frastødende niveauer (tilfældige matricer)",
  "two repelling sequences mixed": "to frastødende sekvenser blandet",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "klumper og huller · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "jævnt adskilt · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "frastødning halvt skjult · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "klumper og huller · afstandsforhold ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "jævnt adskilt · afstandsforhold ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "frastødning halvt skjult · afstandsforhold ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩: {#} hvis tilfældig, {#} for tilfældige matricer",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "samme middelafstand i hver række · ⟨r̃⟩: {#} hvis tilfældig, {#} for tilfældige matricer",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "højde: neutronbredde Γn (lineær)",
  "peak height: neutron width Γn, linear scale": "tophøjde: neutronbredde Γn, lineær skala",
  "yellow: γ width": "gul: γ-bredde",
  "yellow cap: γ width, nearly the same on every peak": "gul hætte: γ-bredde, næsten ens på alle toppe",
  "equal widths: every peak the average": "ens bredder: hver top er gennemsnittet",
  "rolled widths": "slåede bredder", "pile of rolled widths": "bunke af slåede bredder",
  "× average": "× gennemsnit", "(in units of the average)": "(i enheder af gennemsnittet)",
  "dashed: Porter–Thomas": "stiplet: Porter–Thomas", "dashed: the Porter–Thomas law": "stiplet: Porter–Thomas-loven",
  "bell-curve number x": "klokkekurvetal x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "tryk på Slå en bredde",
  // thermal
  "bound level {#} eV": "bundet niveau {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "et bundet niveau ved {#} eV: dets hale løfter denne ende",
  "resonance integral ≈ {#} b": "resonansintegral ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "resonansintegral over {#} eV ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "fanget af en top på vej ned: {#} · nåede termisk: {#}",
  "each hop: one bounce, the same fraction of energy lost": "hvert hop: ét stød, samme brøkdel energi tabt",
  // ensemble
  "thermal neutron": "termisk neutron",
  "σ disc": "σ-skive", "disc area = σ at {#} eV": "skivens areal = σ ved {#} eV",
  "{#}k": "{#}k",
  "thermal σ (b)": "termisk σ (b)", "thermal σ, barns": "termisk σ, barn",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} stiger · termisk ×{#} · res.-integral ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · fanget ved {#} % af landingerne`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · fanget ved <{#} % af landingerne`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `termisk, {#} eV: σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} stiger · termisk σ median ${b}, midterste to tredjedele ×{#} · resonansintegral kun ×{#}`;
  }
})();
