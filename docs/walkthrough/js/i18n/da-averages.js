/* Danish: averages (chapter 18, Expert) */
WT.L.ch.averages = {
  num: "Kapitel 27", title: "Fra resonanser til gennemsnit", short: "Resonanser til gennemsnit",
  lead: "Kapitel 15 tegnede resonansstiger. Her er de som tværsnit: R-matrixformlen, statistikken bag parametrene, temperaturens virkning, og hvordan et gennemsnit over mange resonanser bliver til Hauser–Feshbach.",
  html: `
<div class="step">
  <h3>R-matrix, niveau for niveau</h3>
  <p>Under nogle få keV i en tung kerne viser hvert compoundniveau sig for sig selv, og tværsnittet skrives eksakt ved niveauparametre: energier <i>E</i><sub>λ</sub>, reducerede neutronbredder og indfangningsbredder. Evalueringer bruger <b>R-matrixteori</b>, oftest i <b>Reich–Moore</b>-formen, som bevarer interferensen mellem niveauerne i neutronkanalen og behandler de mange indfangningskanaler som én absorptiv bredde.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Enkeltniveau-Breit–Wigner</button></div>
  <p>Den øverste linje er det totale tværsnit, den nederste indfangning, for én stige af s-bølge-niveauer på en targetkerne med spin 0, uran-238-lignende. Mellem niveauerne falder det totale tværsnit under potentialspredningen, hvor resonans- og potentialamplituderne udslukker hinanden. Enkeltniveauformen lægger niveauernes tværsnit sammen i stedet for deres amplituder; den er tæt på ved toppene og forkert i dalene, hvor halerne fra mange niveauer lægges sammen, og det totale tværsnit kan endda blive negativt.</p>
</div>
<div class="step">
  <h3>Statistikken bag parametrene</h3>
  <p>En kerne, der ikke er målt, har ingen stige, kun sine gennemsnit: <i>D</i>₀, styrkefunktionen <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ og ⟨Γ<sub>γ</sub>⟩. Teorien for tilfældige matricer giver resten: afstandene mellem niveauer med samme spin og paritet følger Wigner-fordelingen, de reducerede neutronbredder følger Porter–Thomas, en χ² med én frihedsgrad.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = afstand/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Træk ti stiger mere</button></div>
  <p>Histogrammerne samler afstandene og bredderne fra alle stiger, der er trukket indtil nu; kurverne er de to love. Indfangningsbredden, en sum over hundredvis af fotonkanaler, fluktuerer næsten ikke og tages derfor som fast.</p>
</div>
<div class="step">
  <h3>Varme udtværer toppene</h3>
  <p>Targetkernerne bevæger sig. En neutron med energien <i>E</i> møder dem med en spredning af relative energier med bredden Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), og hver resonans ses gennem denne spredning: <b>Dopplerudvidelse</b>. For et enkelt niveau er resultatet ψ-funktionen, en Lorentz-kurve foldet med en gaussfunktion.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Temperatur (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>Den forstørrede resonans er den stærkeste af de laveste få i stigen; den stiplede linje er dens form ved 0 K. Varme sænker toppen og breder flankerne ud, og arealet under indfangningstoppen forbliver det samme. I en tyk prøve er det ikke neutralt: toppen er selvafskærmet, flankerne er ikke, så et varmere brændsel indfanger mere. Det er en reaktors Doppler-tilbagekobling.</p>
</div>
<div class="step">
  <h3>Gennemsnittet er Hauser–Feshbach</h3>
  <p>Midlet over mange resonanser bliver indfangning en glat funktion af energien. Vinduet glider hen over stigen, og dets gennemsnit plottes undervejs; de glatte linjer er Hauser–Feshbach-værdien med transmissionerne <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> og <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Vinduesbredde (niveauer)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">En anden stige</button></div>
  <p>Et smalt vindue spreder sig vidt: få resonanser, Porter–Thomas-bredder. Et bredt falder til ro på den nederste linje, den med breddefluktuationskorrektionen. Den øverste linje, produktet af gennemsnit, er her 25 til 47 procent for høj, mest hvor ⟨Γ<sub>n</sub>⟩ er en til tre gange ⟨Γ<sub>γ</sub>⟩, fra omkring 100 eV til 1 keV. (Med p-bølger og flere åbne kanaler er korrektionen mindre.) For én neutronkanal med Porter–Thomas-bredder og en fast indfangningsbredde er den korrigerede værdi eksakt: (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Opløst, uopløst, glat</h3>
  <p>Hvad en måling kan opløse, afhænger af dens energiopløsning, som bliver dårligere, når energien stiger. Linjen er tværsnittet, som et instrument ser det, udvidet med en opløsning, der vokser som <i>E</i><sup>3/2</sup>, som ved flyvetidsmålinger. Ved lav energi står hvert niveau alene, og dets parametre kan tilpasses: det opløste resonansområde. Højere oppe smelter niveauerne sammen i et fluktuerende bånd, hvis statistik er kendt, men hvis enkelte toppe ikke er: det uopløste område, beskrevet ved gennemsnitsparametre og, for selvafskærmning, ved sandsynlighedstabeller bygget ud fra udtrukne stiger. Derover tager Hauser–Feshbach og den optiske model over.</p>
  <div class="ctl"><label for="av-r">Instrumentets opløsning (relativ)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>INCOGNITAs bibliotek har endnu intet opløst resonansområde. Dets kurver er Hauser–Feshbach-gennemsnit helt ned til de laveste energier; hvor målte resonanser er opløst, markerer siden <a href="data.html" data-keep-lang>Alle nuklider</a> kurven som et gennemsnit. Resonansparametre og de Dopplerudvidede punktvise tværsnit, der bygges ud fra dem, er under udarbejdelse.</p>
  <div class="aside">I koden: <code>physics/resonance/ladder.py</code> (afstande fra tilfældige matricer, Porter–Thomas-bredder, enkeltniveautværsnit, ensembler), <code>ladder_statistics.py</code> (lovene testet på målte stiger), <code>compound/wfc.py</code> (breddefluktuationskorrektionen, som gennemsnittene konvergerer mod). Reich–Moore-, ψ–χ- og opløsningsformlerne i billedet evalueres her med illustrative uran-238-lignende parametre; Hauser–Feshbach-motoren, og dermed biblioteket, beregner endnu ikke tværsnit i resonansområdet.</div>
</div>`,
};
(function () {
  const L = {
    // axes
    "{#} eV": "{#} eV", "{#} keV": "{#} keV", "{#} b": "{#} b",
    "{#}⁻¹ b": "{#}⁻¹ b", "{#}¹ b": "{#}¹ b", "{#}² b": "{#}² b", "{#}³ b": "{#}³ b", "{#}⁴ b": "{#}⁴ b",
    // scene 1
    "potential scattering {#}πR′² ≈ {#} b": "potentialspredning {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "Reich–Moore (stiplet: enkeltniveau)",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "enkeltniveau-Breit–Wigner (stiplet: Reich–Moore)",
    "total": "totalt", "capture": "indfangning",
    // scene 2
    "spacings: Wigner": "afstande: Wigner",
    "s = spacing / D₀": "s = afstand / D₀",
    "reduced neutron widths: Porter–Thomas": "reducerede neutronbredder: Porter–Thomas",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "{#} stiger · {#} afstande",
    "s = {#}": "s = {#}",
    // scene 3
    "capture near the {#} eV resonance": "indfangning nær resonansen ved {#} eV",
    "area {#} b·eV ({#} K: {#})": "areal {#} b·eV ({#} K: {#})",
    "target nuclei at {#} K": "targetkerner ved {#} K",
    "target nuclei at rest": "targetkerner i hvile",
    // scene 4
    "Hauser–Feshbach, no correction": "Hauser–Feshbach, uden korrektion",
    "with width fluctuations": "med breddefluktuationer",
    "average capture cross section": "gennemsnitligt indfangningstværsnit",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} niveauer omkring {#} eV: {#} b · HF {#} b uden, {#} b med korrektionen",
    // scene 5
    "resolved": "opløst", "unresolved": "uopløst", "averaged": "midlet",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "indfangning målt med endelig opløsning · stiplet: Hauser–Feshbach med fluktuationer",
    "resolution reaches D₀/{#} at {#} eV": "opløsningen når D₀/{#} ved {#} eV",
    "resolution reaches D₀/{#} at {#} keV": "opløsningen når D₀/{#} ved {#} keV",
    "time of flight: the arrival time measures the energy": "flyvetid: ankomsttiden måler energien",
  };
  // labels that carry cross sections printed as "12 b" or "3.4k b" (each value independently)
  const B = ["{#} b", "{#}k b"];
  for (const a of B) for (const b of B) {
    L[`{#} eV · total ${a} · capture ${b}`] = `{#} eV · totalt ${a} · indfangning ${b}`;
    L[`Γ = {#} meV · Δ = {#} meV · peak ${a} ({#} K: ${b})`] = `Γ = {#} meV · Δ = {#} meV · top ${a} ({#} K: ${b})`;
  }
  L["{#}k b"] = "{#}k b";
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "R-matrixteori", aliases: ["R-matrixteori", "R-matrixteorien", "R-matrixformlen", "R-matrix", "R-matricen"],
    short: "Den eksakte beskrivelse af resonansreaktioner ved niveauenergier og reducerede bredder inden for en kanalradius, tilpasset frie bølger uden for den.",
    more: "Evalueringer tilpasser dens parametre til målte resonanser. Enkelt- og flerniveau-Breit–Wigner og Reich–Moore-formen er approksimationer til den fulde teori.",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore", "Reich–Moore-formen"],
    short: "Den R-matrix-approksimation, der bruges i de fleste evalueringer af tunge kerner: neutronkanalerne behandles eksakt, de mange fotonkanaler som én absorptiv bredde pr. niveau.",
    chapter: "averages",
  },
  doppler: {
    term: "Dopplerudvidelse", aliases: ["Dopplerudvidelse", "Dopplerudvidelsen", "Doppler-udvidelse", "Doppler-udvidelsen", "Dopplerudvidede"],
    short: "Udtværingen af resonanser på grund af targetkernernes termiske bevægelse: toppen falder og flankerne breder sig, mens arealet af en isoleret top forbliver det samme.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "Opløst og uopløst resonansområde", aliases: ["opløste resonansområde", "opløst resonansområde", "uopløste område", "uopløst område", "uopløste resonansområde", "uopløst resonansområde"],
    short: "Under en vis energi måles hver resonans for sig (opløst); derover kendes kun deres gennemsnitsparametre (uopløst), indtil gennemsnittene bliver glatte.",
    more: "I det uopløste område håndteres selvafskærmning med sandsynlighedstabeller, fordelinger af tværsnittet bygget ud fra udtrukne resonansstiger.",
    chapter: "averages",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="bw" data-act="rm" */
