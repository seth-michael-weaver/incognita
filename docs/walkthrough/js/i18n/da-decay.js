/* Danish: decay (chapter 6) */
WT.L.ch.decay = {
  num: "Kapitel 9", title: "Compoundkernens henfald", short: "Henfald",
  lead: "Compoundkernen skal af med sin energi ved at udsende en partikel eller en foton. Dette kapitel tegner hver vej ud som en dør. Motorens opgave er at sige, hvor stor en del af fluxen (strømmen af reaktioner, der når hertil) der går ud gennem hver dør.",
  html: `
<div class="step">
  <p>Én dør pr. udgang: en <em class="g">foton</em> (γ), en <em class="n">neutron</em> (n), en <em class="p">proton</em> (p), en <em class="a">alfapartikel</em> (α: to protoner og to neutroner) og, kun for tunge kerner, <em class="f">fission</em> (spaltning i to). Den oplyste åbning i hver dør er den udgangs andel, og kuglerne strømmer ud i samme takt; grå døre er lukkede. Da kernen har glemt, hvordan den blev dannet, bruger den hver dør b i forhold til en vægt:</p>
  <div class="formula">andel<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p><b>Transmissionskoefficienten</b> <i>T</i> er sandsynligheden for, at en partikel, der når kanten, slipper igennem; for partikler kommer den fra den optiske model i kapitel 5, kørt baglæns. <b>Niveautætheden</b> ρ, skrevet ved siden af hver dør, tæller de tilstande, den tilbageværende kerne kan ende i. At dele efter <i>T</i> gange ρ er <b>Hauser–Feshbach</b>-reglen. Ved 10 MeV tager neutrondøren næsten det hele.</p>
</div>
<div class="step">
  <h3>Fordampningsspektre</h3>
  <p>Neutrondøren, opdelt efter udgående energi ε (langsom til venstre, hurtig til højre). Hver dørs åbning <i>T</i>(ε) bliver bredere for hurtigere neutroner. Under den står mængden af tilstande, den tilbageværende kerne kan være i: en langsom neutron efterlader det meste af energien, hvor der er masser af tilstande, så mængderne skrumper mod højre.</p>
  <div class="ctl"><label for="dc-sp">Overskydende energi</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>Dør × mængde gør bunken til en pukkel, <b>fordampningsspektret</b>, som damp, der forlader en varm væske. Træk i den overskydende energi (i MeV, millioner elektronvolt): bunken starter forfra, og toppen bliver nær 1 MeV, fastlagt af kernetemperaturen. Ekstra energi gør mest den tilbageværende kerne varmere.</p>
</div>
<div class="step">
  <h3>Coulombbarrieren ved emission</h3>
  <p>En protons energi i hver afstand r fra centrum: en brønd indeni, og udenfor en bakke fra den elektriske (Coulomb) frastødning, der aftager som 1/r. Under bakketoppen kan protonen, som rasler rundt i brønden, kun <b>tunnelere</b> gennem den skraverede strækning, en kvanteeffekt, der lykkes én gang ud af mange banken på væggen. Oddsene regnes ud som i kapitel 4: jo bredere og højere strækningen er, jo flere nuller i “1 bank ud af 10<sup>N</sup>”.</p>
  <div class="ctl"><label for="dc-ce">Partikelenergi</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">Skift proton / alfa</button></div>
  <p>Træk energien ned, og se tunnelen blive bredere; skift så til alfapartiklen, hvis to ladninger møder en bakke omtrent dobbelt så høj. Derfor vinder de uladede neutroner som regel, så snart de kan slippe ud, og derfor betyder proton- og alfaudgange mest for lette kerner og høje energier.</p>
</div>
<div class="step">
  <h3>Kanaltærskler</h3>
  <p>Hver partikeldør åbner først over sin <b>separationsenergi</b>, prisen for at trække den partikel ud: her 8 MeV for en neutron, 9 for en proton, 7 for en alfapartikel. Under neutronens 8 MeV udsender næsten hvert henfald lys.</p>
  <div class="ctl"><label for="dc-e">Excitationsenergi</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>Træk excitationsenergien forbi 8 MeV. Inden for omkring 1 MeV svinger neutrondøren vidt op, og fotonernes andel falder hundredfold. Alfadøren låses op først, ved 7 MeV, men åbner knap nok: dens Coulombbakke (kapitel 4) holder den næsten lukket til langt over. Protondøren låses op ved 9 MeV og forbliver også smal, holdt tilbage af sin egen bakke.</p>
</div>
<div class="step">
  <h3>Bevarelse af impulsmoment og paritet</h3>
  <p>Compoundkernen (øverst) har spin <i>J</i>; den tilbageværende kernes tilstande ligger nedenfor i skuffer efter spin <i>J</i>′. Neutronen tager forskellen i spin og paritet med sig: når den forlader kernen med baneimpulsmoment <i>l</i>, ændrer den spinnet med op til <i>l</i> + ½ og vender pariteten, når <i>l</i> er ulige. Større <i>l</i> betyder en smallere dør; hver skuffes dør er det mindste <i>l</i>, der når den. Fyldte landinger bevarer pariteten; hule vender den.</p>
  <div class="ctl"><label for="dc-j">Compoundspin J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>Træk <i>J</i> op. De åbne døre glider mod skufferne med højt spin, som rummer få tilstande, mens de fulde skuffer står bag lukkede døre. En compoundkerne med højt spin er langsom til at udsende partikler, hvilket giver fotoner og isomerer (langlivede tilstande, kapitel 10) deres chance.</p>
</div>
<div class="step">
  <h3>Elastisk forstærkning</h3>
  <p>Ved lav energi er compoundkernen et sæt skarpe <b>resonanser</b>, energier hvor neutronen let absorberes; otte er tegnet, én pr. række. Hver har tilfældige dørbredder: indgangen (neutronkanalen) til venstre, bredde <i>x</i>, og de andre døre, her mest fotoner, til højre, bredder <i>y</i>.</p>
  <div class="btns"><button class="btn" data-act="fire">Affyr 40 neutroner</button><button class="btn ghost" data-act="reroll">Nye resonanser</button></div>
  <p>Tryk på Affyr og følg neutronerne. En neutron kommer ind i en række i forhold til rækkens indgangsbredde <i>x</i>. Når den er inde, vælger den en vej ud i forhold til bredderne: tilbage gennem indgangen med sandsynligheden <i>x</i> / (<i>x</i> + Σ<i>y</i>), ellers gennem en af de andre døre. Bakkerne tæller, hvor de endte.</p>
  <p>Fælden: en række med bred indgang får flere neutroner ind og sender også flere af dem tilbage ud. Så der kommer flere tilbage, end man ville gætte ud fra de gennemsnitlige bredder alene. Den sande andel ud igen (et <b>gennemsnit af produkter</b>) slår det simple estimat (et <b>produkt af gennemsnit</b>); begge står øverst.</p>
  <p>Deres forhold er den <b>elastiske forstærkning</b>. Motorens <b>breddefluktuationskorrektion</b> anvender den: den flytter den ekstra flux fra de andre døre tilbage til indgangen.</p>
  <div class="ctl"><label for="dc-n">Andre døre</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>Tilføj døre. Med mange udgange holder deres samlede bredde op med at fluktuere, så korrektionen betyder mest, hvor få døre er åbne. Motoren anvender den, med Moldauers formel, for indkommende neutroner op til targetkernens neutronseparationsenergi og udelader den derover.</p>
</div>
<div class="step">
  <h3>Flux efter direkte reaktioner</h3>
  <p>Dørene i dette kapitel fordeler kun de neutroner, der faktisk blev. Kapitel 6 og 7 har allerede taget deres andel: nogle neutroner rammer kun ét strejf og flyver væk (direkte), nogle støder rundt en eller to gange og skyder hurtigt ud (præligevægt). Kun resten bliver indeni og opvarmer kernen. Tællerne til højre opgør hvert skæbne; dem, der bliver, forlader aldrig kernen, de bliver kun talt.</p>
  <div class="ctl"><label for="dc-einc">Neutronenergi</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>Kun de, der bliver, går med i konkurrencen om dørene. Træk i neutronenergien: ved nogle få MeV bliver næsten alle; ved 30 MeV er omkring halvdelen væk, før ligevægten nås.</p>
  <div class="aside">I koden: <code>compound/prepare.py</code> (udgangsvægte T·ρ pr. spin og paritet, udvælgelsesregler), <code>compound/target.py</code> (første henfald med breddefluktuationer), <code>compound/continuum.py</code> (henfald af hvert senere interval), <code>compound/wfc.py</code> (Moldauer-, HRTW-, GOE-korrektioner), <code>compound/normalization.py</code> (flux tilbage til compoundkernen), <code>omp/inverse.py</code> (døre kørt baglæns).</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "fission",
    "heavy only": "kun tunge",
    "heavy nuclei only": "kun tunge kerner",
    "shut below {#} MeV": "lukket under {#} MeV",
    "the neutron door takes nearly everything": "neutrondøren tager næsten det hele",
    "below the neutron threshold, nearly all decays emit light": "under neutrontærsklen udsender næsten alle henfald lys",
    "the doors share the decays": "dørene deler henfaldene",
    // hump
    "{#} MeV to spare": "{#} MeV i overskud",
    "door gap = T(ε)": "åbning = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "døre: én pr. neutronenergi ε, åbning = T(ε)",
    "× states left behind": "× efterladte tilstande",
    "× states the leftover nucleus can be in: many after a slow neutron": "× restkernens mulige tilstande: mange efter en langsom neutron",
    "most ≈ {#} MeV": "flest ≈ {#} MeV",
    "= the pile": "= bunken",
    "= where the neutrons land: the evaporation spectrum": "= hvor neutronerne lander: fordampningsspektret",
    "slow": "langsomme",
    "slow neutrons": "langsomme neutroner",
    "fast: {#} MeV →": "hurtige: {#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "hurtige: {#} MeV (derover, op til {#}, næsten ingen)",
    "fast: {#}": "hurtige: {#}",
    "fast: {#} MeV, the neutron takes it all": "hurtige: {#} MeV, neutronen tager det hele",
    // coulomb
    "well ↓": "brønd ↓",
    "well (much deeper) ↓": "brønd (meget dybere) ↓",
    "hilltop ≈ {#} MeV": "bakketop ≈ {#} MeV",
    "falls as {#}/r": "aftager som {#}/r",
    "Coulomb hill, falling as {#}/r": "Coulombbakke, aftager som {#}/r",
    "tunnel: wider than the picture": "tunnel: bredere end billedet",
    "tunnel {#} fm": "tunnel {#} fm",
    "proton energy {#} MeV": "protonenergi {#} MeV",
    "alpha energy {#} MeV": "alfaenergi {#} MeV",
    "proton energy {#} MeV ↑": "protonenergi {#} MeV ↑",
    "alpha energy {#} MeV ↑": "alfaenergi {#} MeV ↑",
    "above the hilltop: it rolls straight out": "over bakketoppen: den triller lige ud",
    "below the top, must tunnel: nearly every knock gets through": "under toppen, må tunnelere: næsten hvert stød slipper igennem",
    "below the top, must tunnel: about {#} knock in {#} gets through": "under toppen, må tunnelere: ca. {#} stød ud af {#} slipper igennem",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "under toppen, må tunnelere: ca. {#} stød ud af {#} × {#}^{#} slipper igennem",
    "out": "ude",
    "through after {#} knock": "igennem efter {#} stød",
    "through after {#} knocks": "igennem efter {#} stød",
    "knocks so far: {#}": "stød indtil nu: {#}",
    "distance r from the centre (fm) →": "afstand r fra centrum (fm) →",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}, paritet +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "resttilstande efter spin J′ →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "skuffer: restkernens tilstande efter spin J′ (svagt: tilstande den har) →",
    "open doors reach {#} %": "åbne døre når {#} %",
    "open doors reach about {#} % of the states": "åbne døre når ca. {#} % af tilstandene",
    "● parity kept (even l)   ○ flipped (odd l)": "● paritet bevaret (lige l)   ○ vendt (ulige l)",
    // wfc
    "entrance x": "indgang x",
    "entrance, width x": "indgang, bredde x",
    "{#} other doors, y": "{#} andre døre, y",
    "{#} other door, widths y": "{#} anden dør, bredder y",
    "{#} other doors, widths y": "{#} andre døre, bredder y",
    "back out the entrance: {#} of {#}": "ud gennem indgangen: {#} af {#}",
    "out another door: {#}": "ud ad en anden dør: {#}",
    // norm
    "absorbed neutrons, {#} MeV →": "absorberede neutroner, {#} MeV →",
    "direct: {#} %": "direkte: {#} %",
    "pre-equilibrium: {#} %": "præligevægt: {#} %",
    "compound nucleus: {#} %": "compoundkerne: {#} %",
    "one glancing hit on the surface": "ét strejfende stød på overfladen",
    "a knock or two, then out fast": "et stød eller to, så hurtigt ud",
    "stayed: on to the door competition": "blev: videre til dørkonkurrencen",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} tilstand"], ["{#} states", "{#} tilstande"], ["{#} thousand states", "{#} tusind tilstande"], ["{#} million states", "{#} millioner tilstande"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `svag dør × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `tilbage ${a}, ikke ${b}: × {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `andel tilbage: gennemsnit af produkter ${a} · produkt af gennemsnit ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `andre døre ${a}, ikke ${b}`;
    L[`other doors together: ${a} instead of ${b}`] = `andre døre i alt: ${a} i stedet for ${b}`;
  }
  Object.assign(WT.L.labels, L);
})();
