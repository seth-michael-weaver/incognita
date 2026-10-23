/* Danish: compound (chapter 5) */
WT.L.ch.compound = {
  num: "Kapitel 5", title: "Energien deles", short: "Compoundkerne",
  lead: "Når de første hurtige stød er overstået, deler alle nukleonerne energien. Denne rolige tilstand er compoundkernen. For at forudsige, hvad den gør bagefter, skal motoren vide, på hvor mange måder den kan rumme sin energi.",
  html: `
<div class="step">
  <p>En neutron rammer den ene side af en kerne. Dens energi plus den energi, der frigøres ved indfangningen, begynder som en varm plet (det orange skær); stødene giver den videre, og inden for omkring 10⁻²¹ sekunder bærer hver nukleon en andel.</p>
  <div class="btns"><button class="btn" data-act="hit">Ram fra en anden side</button></div>
  <p>Tryk på knappen for at sende neutronen ind fra en anden side. Skæret ender altid på samme måde: kernen har <b>glemt, hvordan den blev dannet</b>. Det er Bohrs compoundkerne. Herfra betyder kun tre ting noget: dens energi, dens spin (hvor meget den roterer) og dens paritet (et + eller − som mærke for dens spejlsymmetri).</p>
</div>
<div class="step">
  <h3>Fra adskilte niveauer til et kontinuum</h3>
  <p>Stigen til venstre rummer kernens tilstande, med energien stigende opad; vinduet til højre forstørrer en skive på 1 MeV omkring den orange kugle. Nær bunden står trinene langt fra hinanden, og hvert eneste er målt. Højere oppe mangedobles måderne at dele energien mellem 56 nukleoner på, til trinene flyder sammen i et massivt bånd, kontinuet.</p>
  <div class="ctl"><label for="cn-e">Excitationsenergi</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Træk i excitationsenergien (energien over den laveste tilstand, i MeV), og hold øje med vinduet. <b>Niveautætheden</b> ρ, tilstande pr. MeV, vokser omtrent som e<sup>2√(aE)</sup>, hvor <i>a</i> sætter tempoet for hver kerne: nogle få pr. MeV ved 3 MeV, hundreder nær 8 MeV (hvor en neutron kunne slippe ud), millioner ved 20 MeV. Deroppe regner motoren med selve ρ.</p>
</div>
<div class="step">
  <h3>Tre stykker, samlet ved én energi</h3>
  <p>Terrænets højde er niveautætheden på en logaritmisk skala, med energien mod højre. Nederst til venstre står de optalte niveauer. Den lige planke er <b>konstanttemperaturloven</b>: ρ ganges med e (cirka 2,7) for hver <i>T</i> MeV, hvor <i>T</i> er kernetemperaturen. Skråningen er <b>Fermigassen</b>, som behandler nukleonerne som uafhængige partikler. Undtagen for de tungeste targets, hvor den læser tabellerede tætheder, bruger motoren som standard dette par.</p>
  <div class="ctl"><label for="cn-ex">Tilpasningsenergi</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Træk i tilpasningsenergien: samlingen glider langs skråningen, og planken drejer for at møde den med samme højde og hældning. De to stakke nedenfor sammenligner de niveauer, planken forudsiger, med dem, der faktisk er optalt. Kun én samling gør dem lige store; dér bliver planken grøn. Det er den energi, motoren vælger.</p>
</div>
<div class="step">
  <h3>Skaller, der smelter</h3>
  <p>Enkeltnukleonniveauer, med to nukleoner i hvert, for to kerner. Til venstre en lukket skal: alt under et stort hul er fyldt, så ethvert skift koster hele hullet. Til højre en kerne midt i en skal med et halvfyldt øverste niveau, så billige skift findes med det samme. Hver tæller viser, hvor mange arrangementer der kan rumme den givne varme.</p>
  <div class="ctl"><label for="cn-u">Varme (excitation)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Skru op for varmen, og se nukleonerne hoppe. Ved lav varme mangler den lukkede skal arrangementer; med nok varme holder hullet op med at betyde noget, og begge tal vokser ens. <b>Niveautæthedsparameteren</b> <i>a</i> bærer dette: viserne starter adskilt og nærmer sig den glatte værdi <i>ã</i> over cirka 10 MeV. Motoren lader skalkorrektionen δW aftage med en rate γ:</p>
  <div class="formula">a(U) = ã · [1 + δW · (1 − e<sup>−γU</sup>) / U]</div>
</div>
<div class="step">
  <h3>Sorteret efter spin og paritet</h3>
  <p>Tilstandene ved én energi fordeles i skuffer efter spin <i>J</i>, kernens impulsmoment: fyldte brikker for + paritet, hule for −. De midterste skuffer fyldes mest, efter (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, hvor spin-cutoff σ bestemmer spredningen. De to pariteter bliver omtrent lige store.</p>
  <div class="ctl"><label for="cn-u2">Excitation</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Deformér kernen</button></div>
  <p>Træk excitationen op: σ vokser, fordi en varmere kerne kan bære mere spin. Tryk så på Deformér. En kerne formet som en amerikansk fodbold kan også rotere som helhed, så hver skuffe får flere tilstande (de blå brikker): den <b>kollektive forstærkning</b>. Som standard tilføjer motoren den kun for targets tungere end omkring 215 nukleoner.</p>
</div>
<div class="step">
  <h3>Skåret i intervaller</h3>
  <p>Over det sidste optalte niveau skærer motoren kontinuet i skiver af samme energibredde, kaldet intervaller (bins). I hvert interval smelter prikkerne sammen til én blok med ρ·ΔE tilstande (ΔE er intervalbredden), sorteret efter spin og paritet som ovenfor.</p>
  <div class="ctl"><label for="cn-emax">Toppen af stigen</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Sortér igen</button></div>
  <p>Træk i toppen af stigen, den største energi neutronen kan bringe med. Det samme antal intervaller skal dække mere energi, så hvert bliver højere. Den orange kugle falder fra interval til interval: hvert senere trin (valget af udgang, fotonkaskaden, vandringen ned ad kortet) arbejder på disse intervaller. Her er ti tegnet; motoren bruger op til 40.</p>
  <div class="aside">I koden: <code>density/parameters.py</code> (Ignatyuk <i>a</i>(U), spin-cutoff, Wigner-fordeling, kollektiv forstærkning), <code>density/models.py</code> (konstant temperatur, Fermigas, tabeller), <code>density/matching.py</code> (tilpasningsenergien ud fra de optalte niveauer), <code>core/grids.py</code> (excitationsintervaller).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "en neutron kommer ind",
    "a hot spot: the energy is still local": "en varm plet: energien er stadig lokal",
    "equilibrium: every nucleon holds a share": "ligevægt: hver nukleon har en andel",
    "no trace left of where it was hit": "intet spor af, hvor den blev ramt",
    // scene 2
    "ground state": "grundtilstand",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, forstørret",
    "no level in this slice": "intet niveau i denne skive",
    "{#} rung in {#} MeV": "{#} trin på {#} MeV",
    "{#} rungs in {#} MeV": "{#} trin på {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#} trin i denne skive på {#} MeV",
    "{#} rungs in this {#}-MeV slice": "{#} trin i denne skive på {#} MeV",
    "about {#} rungs: too close to draw": "ca. {#} trin: for tætte til at tegne",
    "about {#}k rungs: too close to draw": "ca. {#} tusind trin: for tætte til at tegne",
    "about {#}M rungs: too close to draw": "ca. {#} mio. trin: for tætte til at tegne",
    "about {#}B rungs: too close to draw": "ca. {#} mia. trin: for tætte til at tegne",
    "about {#} rungs in this slice: too close to draw": "ca. {#} trin i denne skive: for tætte til at tegne",
    "about {#} thousand rungs in this slice: too close to draw": "ca. {#} tusind trin i denne skive: for tætte til at tegne",
    "about {#} million rungs in this slice: too close to draw": "ca. {#} millioner trin i denne skive: for tætte til at tegne",
    "about {#} billion rungs in this slice: too close to draw": "ca. {#} milliarder trin i denne skive: for tætte til at tegne",
    "each one measured: energy, spin and parity": "hvert enkelt målt: energi, spin og paritet",
    "the rungs are multiplying": "trinene mangedobles",
    "a continuum: the engine uses ρ itself": "et kontinuum: motoren bruger selve ρ",
    "≈ energy to free a neutron": "≈ energi til at frigøre en neutron",
    "energy ↑": "energi ↑",
    // scene 3
    "gap: plank below the rungs": "afstand: planken under trinene",
    "gap: plank above the rungs": "afstand: planken over trinene",
    "counted levels": "optalte niveauer",
    "CT plank": "KT-planke",
    "constant-temperature plank": "konstanttemperatur-planke",
    "Fermi-gas hillside": "Fermigas-skråning",
    "joint {#} MeV": "samling {#} MeV",
    "energy →": "energi →",
    "+{#} more": "+{#} mere",
    "{#} counted": "{#} optalt",
    "{#} predicted": "{#} forudsagt",
    "{#}+ predicted": "{#}+ forudsagt",
    "equal: the plank rests on the counted rungs": "lige: planken hviler på de optalte trin",
    "too few: the plank is too steep and sinks": "for få: planken er for stejl og synker",
    "too many: the plank is too shallow and floats": "for mange: planken er for flad og svæver",
    // scene 4
    "closed shell": "lukket skal",
    "mid-shell": "midt i skallen",
    "gap": "hul",
    "no arrangement holds this heat": "intet arrangement rummer denne varme",
    "≈ {#} arrangement": "≈ {#} arrangement",
    "≈ {#} arrangements": "≈ {#} arrangementer",
    "≈ {#} thousand arrangements": "≈ {#} tusind arrangementer",
    "≈ {#} million arrangements": "≈ {#} millioner arrangementer",
    "≈ {#} billion arrangements": "≈ {#} milliarder arrangementer",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "kold: ingen kan flytte sig",
    "temperature ≈ {#} MeV": "temperatur ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "tilstande ved {#} MeV",
    "spin J →": "spin J →",
    "+ parity": "+ paritet",
    "− parity": "− paritet",
    "rotation ×{#}": "rotation ×{#}",
    "added by rotation: ×{#} (a few drawn)": "tilføjet af rotation: ×{#} (nogle få tegnet)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "spredning σ ≈ {#}: flest tilstande nær J ≈ {#}",
    "deformed: it can rotate": "deformeret: den kan rotere",
    "spherical": "kugleformet",
    // scene 6
    "≈ {#} thousand": "≈ {#} tusind",
    "≈ {#} million": "≈ {#} millioner",
    "≈ {#} billion": "≈ {#} milliarder",
    "≈ {#}k": "≈ {#} t",
    "≈ {#}M": "≈ {#} mio.",
    "≈ {#}B": "≈ {#} mia.",
    "{#} bins, each {#} MeV wide": "{#} intervaller, hver {#} MeV brede",
    "counted": "optalt",
    "states in each bin": "tilstande i hvert interval",
  };
  Object.assign(WT.L.labels, L);
})();
