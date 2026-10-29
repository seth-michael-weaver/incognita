/* Danish: fission (chapter 9) */
WT.L.ch.fission = {
  num: "Kapitel 12", title: "Fission", short: "Fission",
  lead: "De tungeste kerner har en udgang, som lettere kerner mangler: i stedet for at kaste én partikel ud river hele kernen sig over i to. Det er fission.",
  html: `
<div class="step">
  <p>En tung kerne opfører sig som en dråbe elektrisk ladet væske. Overfladespændingen (grå pile) holder den rund; protonerne, der alle er positivt ladede, skubber den fra hinanden (røde pile). For uran er de to kræfter næsten i balance.</p>
  <div class="ctl"><label for="fis-d">Stræk dråben</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Træk for at strække den, og følg prikken på den lille energikurve nedenfor. At strække den giver mere overflade, hvilket koster energi, men spreder ladningen, hvilket frigør energi. Forbi toppen af kurven vinder ladningen: der dannes en hals, og halvdelene flyver fra hinanden med omkring 200 MeV.</p>
</div>
<div class="step">
  <h3>Potentialenergioverfladen</h3>
  <p>Kurven er energien for hver form, fra rund (til venstre) til delt (til højre). En glat væskedråbe giver én bakke, men nukleonerne fylder energiniveauerne i grupper, kaldet <b>skaller</b>, og i de tungeste grundstoffer graver det en brønd ud i den: en <b>dobbeltpuklet barriere</b>, hvor kernen kan blive hængende et stykke tid i en strakt form.</p>
  <p>Motoren antager ikke denne kurve: den aflæser den punkt for punkt fra en mikroskopisk beregning af energien ved hver deformation (hvor meget kernen er strakt).</p>
</div>
<div class="step">
  <h3>Gennemtrængning af barrieren</h3>
  <p>Kuglen er den exciterede kerne i den første dal, ved excitationsenergien på den orange stiplede linje, under bakketoppen på 6 MeV. Klassisk kan den aldrig komme over; kvantemekanikken lader den <b>tunnelere</b> gennem den mørkere, forbudte del med en sandsynlighed <i>T</i>, der falder eksponentielt, når den del bliver tykkere.</p>
  <div class="ctl"><label for="fis-e">Excitationsenergi</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Skru op for energien, og se <i>T</i> stige, efterhånden som den forbudte del bliver tyndere. Lærebogens genvej (Hill–Wheeler) behandler bakketoppen som en parabel (blå stiplet). Motoren følger den virkelige form, som er bredere længere nede, så langt under toppen er dens sandsynlighed mindre. <i>K</i> måler, hvor meget bakke der står i vejen.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Overgangstilstande</h3>
  <p>Dørene på bakketoppen er <b>overgangstilstandene</b>, kvantetilstandene for kernen strakt hen over barrieren. Hver har et spin og en paritet (0⁺, 2⁻, …) og fungerer som en låge; den oplyste sprække viser, hvor åben den er. En kerne passerer kun gennem låger med samme spin og paritet som den selv, og hver låge åbner sig gradvist, når energien når op over dens højde.</p>
  <div class="ctl"><label for="fis-e2">Excitationsenergi</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Alle spin</button><button class="btn ghost" data-act="jp0">Compoundkerne 0⁺</button><button class="btn ghost" data-act="jp1">Compoundkerne 1⁻</button></div>
  <p>Vælg ét spin og én paritet: kun de matchende låger tæller, og den samlede åbning falder. Længere oppe trænger lågerne sig sammen i et <b>kontinuum</b>, og motoren tæller dem ud fra deres tæthed, ligesom den gør for almindelige niveauer.</p>
</div>
<div class="step">
  <h3>Dobbeltpuklede barrierer</h3>
  <p>Nu begge bakker, hver med sin låge (cirklen; den udfyldte del viser, hvor åben den er). Kernerne kommer ind fra venstre; de, der kommer over den første bakke, fanges i brønden og hopper frem og tilbage mellem lågerne, indtil de forlader den den ene eller den anden vej. Sandsynlighederne kombineres som modstande i serie, så det er mest den sværeste bakke, der afgør det.</p>
  <div class="ctl"><label for="fis-b">Den ydre bakkes højde</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Træk den ydre bakke op, og se strømmen mod fission blive kvalt, uanset hvor åben den indre låge er.</p>
</div>
<div class="step">
  <h3>Flerchancefission</h3>
  <p>Uran-238 absorberer neutronen og bliver til uran-239 med excitationen <i>E</i>* (stiplet linje). Hvis den ikke flækker, kan den i stedet udsende en neutron; linjen falder, og det uran-238, der bliver tilbage, stadig varmt, prøver sin egen barriere: fission ved <b>anden chance</b>, (n,n′f). Bunkerne samler, hvordan hver kerne endte.</p>
  <div class="ctl"><label for="fis-en">Neutronenergi</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Hæv energien, og senere forsøg begynder at lykkes; en tredje chance åbner sig nær 12 MeV. Hver ny chance viser sig som et trin i det målte <b>fissionstværsnit</b>, hvor sandsynligt det er, at kernen deles: den lille graf øverst til højre tegner disse trin med din energi markeret. Motoren beregner, hvor ofte den deles, ikke hvilke stykker den deles i.</p>
  <div class="aside">I koden: <code>fission/wkb.py</code> (deformationsenergiens vej og WKB-integralerne), <code>fission/barriers.py</code> (Hill–Wheeler, overgangstilstande, niveautætheden ved barrieren), <code>fission/transmission.py</code> (pukler i serie, T<sub>fis</sub> for hvert spin og hver paritet), <code>fission/chain.py</code> (barrierer for hver kerne i kaskaden).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "overfladespænding gør den rund",
  "the protons push it apart": "protonerne skubber den fra hinanden",
  "a charged drop, nearly round": "en ladet dråbe, næsten rund",
  "stretched: more surface, charge further apart": "strakt: mere overflade, ladning mere spredt",
  "a neck forms": "der dannes en hals",
  "two fragments, carrying about {#} MeV": "to fragmenter med omkring {#} MeV",
  "energy of the drop": "dråbens energi",
  // landscape
  "ground state": "grundtilstand", "inner barrier": "indre barriere", "second well": "anden brønd",
  "outer barrier": "ydre barriere", "split (scission)": "delt (scission)", "one smooth hill": "én glat bakke",
  "shell effects carving the second well": "skaleffekter graver den anden brønd ud",
  "round → stretched → necked → split": "rund → strakt → med hals → delt",
  "stretch (deformation) →": "strækning (deformation) →",
  // tunnel
  "forbidden zone": "forbudt zone",
  "excitation {#} MeV": "excitation {#} MeV",
  "hilltop {#} MeV": "bakketop {#} MeV",
  "parabola fit": "parabeltilpasning",
  "passes over the top": "passerer over toppen",
  // gates
  "continuum: a density": "kontinuum: en tæthed",
  "continuum of gates: counted as a density": "kontinuum af låger: tælles som en tæthed",
  "gates: transition states": "låger: overgangstilstande",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "alle låger: samlet åbning {#}",
  "all gates: total opening {#} + {#} from the continuum": "alle låger: samlet åbning {#} + {#} fra kontinuet",
  "{#}⁺ gates only: total opening {#}": "kun {#}⁺-låger: samlet åbning {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "kun {#}⁺-låger: samlet åbning {#} + {#} fra kontinuet",
  "{#}⁻ gates only: total opening {#}": "kun {#}⁻-låger: samlet åbning {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "kun {#}⁻-låger: samlet åbning {#} + {#} fra kontinuet",
  // series
  "nuclei arriving →": "kerner, der ankommer →",
  "trapped in the well": "fanget i brønden",
  "fission": "fission",
  "so far: {#} through, {#} turned back": "indtil nu: {#} igennem, {#} vendt om",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* over billedet",
  "fission!": "fission!",
  "emits a neutron, cools, tries again": "udsender en neutron, køles, prøver igen",
  "too cool to split: a photon, no fission": "for kold til at flække: en foton, ingen fission",
  "attempt {#}: barrier {#} % open": "forsøg {#}: barriere {#} % åben",
  "{#}st chance (n,f)": "{#}. chance (n,f)", "{#}nd chance (n,n′f)": "{#}. chance (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}. chance (n,{#}nf)",
  "{#}st (n,f)": "{#}. (n,f)", "{#}nd (n,n′f)": "{#}. (n,n′f)", "{#}rd (n,{#}nf)": "{#}. (n,{#}nf)",
  "no fission": "ingen fission",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `indre låge T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `ydre låge T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `begge bakker: T ≈ ${a}, {#} % af det, der ankommer, kommer igennem`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} virkelig form · ${b} parabel`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `tunneleringschance T ≈ ${a} med den virkelige form, ${b} med parablen`;
    }
  }
})();
