/* Danish: hauser (chapter 13, Expert) */
WT.L.ch.hauser = {
  num: "Kapitel 22", title: "Hauser–Feshbach, kanal for kanal", short: "Hauser–Feshbach",
  lead: "Kapitel 9 fortalte konkurrencen mellem udgangene som døre. Her er formlen bag dørene, én kanal ad gangen, og den korrektion, den har brug for, når kun få kanaler er åbne.",
  html: `
<div class="step">
  <h3>En transmission for hver kanal</h3>
  <p>En <b>kanal</b> er en fuldstændig udgangsadresse: hvilken partikel, hvilken tilstand restkernen efterlades i, partiklens baneimpulsmoment <i>l</i> og dens totale <i>j</i> = <i>l</i> ± ½. Den optiske model fra kapitel 5 giver hver af dem en <b>transmissionskoefficient</b> <i>T<sub>lj</sub></i>. Søjlerne er den indkommende neutrons, for en targetkerne med spin 0.</p>
  <div class="ctl"><label for="hf-e">Neutronenergi (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Ved 1 keV er kun <i>l</i> = 0 åben, med <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, nogle få procent. Hver ekstra enhed af <i>l</i> koster omtrent en faktor (<i>kR</i>)² ved lav energi, så søjlerne åbner én efter én, når energien stiger. Hver søjle fører flux ind i compoundkernen med vægten g<sub>J</sub><i>T</i>:</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>Ét spin og én paritet ad gangen</h3>
  <p>Impulsmoment og paritet er bevarede, så compoundkernen henfalder uafhængigt i hvert <i>J</i><sup>π</sup>. Inden for én blok konkurrerer hver åben udgangskanal med sit eget <i>T</i>: elastisk tilbage til grundtilstanden, uelastisk til hvert exciteret niveau (en søjle summerer de (<i>l</i>, <i>j</i>), der kobler til samme <i>J</i>), kontinuet over 3,6 MeV, hvis intervaller tæller som mange kanaler, vægtet med niveautætheden, og indfangning, samlet i ét lille <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>. Højderne er på en logaritmisk skala.</p>
  <div class="ctl"><label for="hf-j">Blok for spin og paritet</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Neutronenergi (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Bjælken nederst er <b>Hauser–Feshbach</b>-fordelingen: hver udgang får andelen <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> af det, der kom ind gennem kanal <i>a</i>. Under 0,85 MeV er kun elastisk spredning og indfangning åbne, og den elastiske kanal tager næsten det hele.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Breddefluktuationer</h3>
  <p>Den simple formel undervurderer elastisk spredning en smule, og korrektionen flytter lidt flux tilbage til den fra de andre udgange. Her er hvorfor.</p>
  <p>Med <i>W<sub>ab</sub></i> = 1 ganger formlen gennemsnit. Resonanserne bag gennemsnittene har bredder, der spreder sig (Porter–Thomas, kapitel 15), og ved elastisk spredning er den bredde, der lukker neutronen ind, den samme, som lukker den ud, så de to er korrelerede. Gennemsnittet af produkterne overstiger da produktet af gennemsnittene for den elastiske kanal, og de andre udgange mister, hvad den elastiske vinder.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Uden korrektion</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Neutronenergi (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Mærkerne viser σ med korrektionen divideret med σ uden. Under den første uelastiske tærskel tager den elastiske kanal allerede næsten hele fluxen og ændrer sig knap, mens indfangning taber 10 til 25 procent. Mellem 1 og 1,5 MeV vinder compound-elastisk spredning 15 til 35 procent, og det første 2⁺-niveau taber omkring en tredjedel. Efterhånden som flere niveauer og kontinuet åbner, bliver compound-elastisk spredning en lille del af fluxen: dens egen faktor stiger mod 2, men det, den tager fra de andre, skrumper, og deres faktorer vender tilbage mod 1. I Moldauers opskrift får hver kanal et antal frihedsgrader ν<sub>c</sub>, og <i>W</i> er et endimensionalt integral, beregnet med TALYS' 32-punkts Gauss–Laguerre-regel.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer og HRTW</h3>
  <p>Kurverne kører den samme beregning over hele energiområdet: forholdet for compound-elastisk spredning, for det første 2⁺-niveau og for indfangning, med Moldauer fuldt optrukket og <b>HRTW</b>-opskriften stiplet. HRTW erstatter integralet med en elastisk faktor <i>W<sub>a</sub></i> og effektive transmissioner <i>V<sub>a</sub></i>, der findes ved iteration.</p>
  <div class="ctl"><label for="hf-e4">Neutronenergi (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>De to stemmer nøje overens for elastisk og uelastisk spredning; for indfangning i keV-området fjerner HRTW op til 10 procent mere. Mellem 0,85 og 2 MeV vinder indfangning endda: dér domineres den totale bredde af nogle få fluktuerende neutronbredder, og gennemsnittet af 1/Γ overstiger 1/⟨Γ⟩. Begge opskrifter er tilpasninger til det eksakte resultat fra teorien for tilfældige matricer (GOE), som TALYS også tilbyder som et tredobbelt integral. INCOGNITA porterer alle tre (<code>widthmode</code> 1, 2, 3); Moldauer er standard og anvendes for indkommende neutroner op til targetkernens neutronseparationsenergi.</p>
</div>
<div class="step">
  <h3>Grænser for den elastiske forstærkning</h3>
  <p>Hvor stor kan den elastiske forstærkning blive? Mellem to og tre gange, afhængigt af om resonanserne ligger adskilt eller overlapper.</p>
  <p>Grænsetilfældene forklarer effektens størrelse. Tag <i>N</i> ens kanaler uden indfangning, og varier deres sum ΣT, som er 2π gange forholdet mellem den gennemsnitlige totale bredde og niveauafstanden, Γ/<i>D</i>. Med isolerede resonanser (ΣT ≪ 1) og mange kanaler følger hver bredde Porter–Thomas med én frihedsgrad, og den elastiske forstærkning er ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. Når resonanserne overlapper kraftigt (ΣT ≫ 2π), fluktuerer tværsnittet som en tilfældig bølge (Ericson-fluktuationer), og forstærkningen falder til 2.</p>
  <div class="ctl"><label for="hf-n">Åbne kanaler N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>For <i>N</i> isolerede kanaler er den eksakte værdi 3<i>N</i>/(<i>N</i>+2) (diamanten): med kun to kanaler kan forstærkningen ikke overstige 1,5, fordi den totale bredde da fluktuerer lige så meget som den elastiske. Moldauers opskrift gengiver denne grænse; HRTW når ikke op på den, når mange svage kanaler er åbne. Indsatsen tegner resonanser med den bredde, der hører til det bevægelige punkt. I Moldauers formel er mangekanalgrænsen 1 + 2/ν: ν → 1 for isolerede resonanser og ν → 1,78, når de overlapper. Det giver 2,12 ved fuldt overlap i stedet for 2: en lille fejl i tilpasningen.</p>
  <div class="aside">I koden: <code>compound/prepare.py</code> (udgangskanaler og deres transmissioner pr. <i>J</i><sup>π</sup>), <code>compound/target.py</code> (Hauser–Feshbach-summerne), <code>compound/wfc.py</code> (Moldauer, HRTW og GOE, porteret fra TALYS). Billedet evaluerer de samme formler med illustrative ingredienser: hårdkugletransmissioner for en jernlignende targetkerne, syv niveauer, et konstanttemperatur-kontinuum og én samlet indfangningskanal.</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: incident T_lj
    "T = {#}": "T = {#}",
    "l={#}": "l={#}",
    "hollow: j = l − ½ · solid: j = l + ½": "hul: j = l − ½ · fyldt: j = l + ½",
    "compound nucleus": "compoundkerne",
    "compound nucleus · σ(CN) ≈ {#} b": "compoundkerne · σ(CN) ≈ {#} b",
    "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
    "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
    "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
    "transmission Tₗⱼ of the incident neutron": "transmission Tₗⱼ for den indkommende neutron",
    // scene 2: one J^pi block
    "elastic": "elastisk", "cont.": "kont.", "higher": "højere",
    "level energy (MeV) under each column": "niveauenergi (MeV) under hver søjle",
    "residual level (energy in MeV) · n×: number of (l, j) channels summed": "restkernens niveau (energi i MeV) · n×: antal summerede (l, j)-kanaler",
    "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "blok {#}/{#}⁺ · ind gennem l = {#}, Tₐ = {#}",
    "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "blok {#}/{#}⁻ · ind gennem l = {#}, Tₐ = {#}",
    "{#}⁺ block · in through l = {#}, Tₐ = {#}": "blok {#}⁺ · ind gennem l = {#}, Tₐ = {#}",
    "{#}⁻ block · in through l = {#}, Tₐ = {#}": "blok {#}⁻ · ind gennem l = {#}, Tₐ = {#}",
    "elastic {#} %": "elastisk {#} %", "higher {#} %": "højere {#} %", "{#}⁺ {#} %": "{#}⁺ {#} %", "γ {#} %": "γ {#} %",
    "Hauser–Feshbach split: T / ΣT for each exit": "Hauser–Feshbach-fordeling: T / ΣT for hver udgang",
    // scene 3: HF vs WFC
    "closed": "lukket",
    "compound elastic": "compound-elastisk", "first {#}⁺ level": "første {#}⁺-niveau",
    "higher levels": "højere niveauer", "capture": "indfangning",
    "{#} mb": "{#} mb",
    "with Moldauer's correction": "med Moldauers korrektion",
    "Hauser–Feshbach without correction": "Hauser–Feshbach uden korrektion",
    "compound formation {#} mb at {#} MeV": "compounddannelse {#} mb ved {#} MeV",
    "compound formation {#} mb at {#} keV": "compounddannelse {#} mb ved {#} keV",
    // scene 4: ratio curves
    "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
    "{#}⁺ opens": "{#}⁺ åbner", "continuum": "kontinuum", "continuum opens": "kontinuet åbner",
    "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "elastisk ×{#} (Moldauer) · ×{#} (HRTW)",
    "capture ×{#} (Moldauer) · ×{#} (HRTW)": "indfangning ×{#} (Moldauer) · ×{#} (HRTW)",
    "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "første {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
    "solid: Moldauer · dashed: HRTW": "fuldt optrukket: Moldauer · stiplet: HRTW",
    "σ with correction / σ without": "σ med korrektion / σ uden",
    // scene 5: limits
    "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
    "elastic enhancement Wₐₐ": "elastisk forstærkning Wₐₐ",
    "T → {#} per channel": "T → {#} pr. kanal",
    "exact, isolated: {#}N/(N+{#}) = {#}": "eksakt, isoleret: {#}N/(N+{#}) = {#}",
    "Porter–Thomas: {#}": "Porter–Thomas: {#}",
    "Ericson: {#}": "Ericson: {#}",
    "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} kanaler · ΣT = {#} · Wₐₐ = {#}",
    "isolated resonances: Γ ≪ D": "isolerede resonanser: Γ ≪ D",
    "resonances begin to overlap": "resonanserne begynder at overlappe",
    "strongly overlapping: Γ ≫ D": "kraftigt overlappende: Γ ≫ D",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "En opskrift på breddefluktuationskorrektionen fra Hofmann, Richert, Tepel og Weidenmüller: en elastisk faktor pr. kanal og effektive transmissioner, fundet ved iteration.",
    more: "Den blev, ligesom Moldauers, tilpasset numeriske beregninger med tilfældige matricer. TALYS tilbyder den som widthmode 2; Moldauer (1) er standard, og det eksakte tredobbelte GOE-integral (3) er referencen.",
    chapter: "hauser",
  },
  ericson: {
    term: "Ericson-fluktuationer", aliases: ["Ericson-fluktuationer", "Ericson-fluktuationerne"],
    short: "Tilfældige udsving i et tværsnit med energien, når mange resonanser overlapper, på en energiskala fastlagt af deres gennemsnitlige totale bredde.",
    more: "De er grænsen for kraftigt overlap af den samme statistik, der giver Porter–Thomas-bredder for isolerede resonanser. Dér går den elastiske forstærkningsfaktor mod 2.",
    chapter: "hauser",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="w0" data-act="w1" data-show="jbShow" */
