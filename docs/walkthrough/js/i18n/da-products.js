/* Danish: products (Kapitel 15, fissionsprodukter og eftervarme) */
WT.L.ch.products = {
  num: "Kapitel 15", title: "Fissionsprodukter og eftervarme", short: "Fissionsprodukter",
  html: `
<div class="step">
  <p>Stykkerne er ulige: ét let, ét tungt. Diagrammet viser for hver fragmentmasse A (protoner plus neutroner) den andel af fissionerne, der danner den. To pukler: lette stykker nær A = 95, tunge nær 139. En symmetrisk deling, nær A = 117, er omkring hundrede gange sjældnere.</p>
  <p>Hver stiplet linje er ti gange højere end den under den, så de sjældne masser stadig kan ses. Tryk på en søjle eller træk i skyderen: nedenfor er de to stykker af den deling. Deres masser summerer til 234, ikke 236 (uran-235 plus neutronen), fordi omkring 2,4 neutroner også flyver væk.</p>
  <div class="ctl"><label for="pr-a">Let fragment A</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Deres henfald fortsætter med at opvarme brændslet efter nedlukning. Fragmenterne er radioaktive: de henfalder efter hinanden, og hvert henfald frigiver varme, uanset om kædereaktionen kører eller ej.</p>
  <div class="ctl"><label for="pr-t">Tid efter nedlukning</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>Træk i tiden. Ét sekund efter at reaktoren stopper, giver henfaldene stadig omkring 6 % af fuld effekt; efter et døgn omkring en halv procent; efter et år nogle få hundrededele af en procent, stadig det meste af en megawatt i en stor reaktor. Det er derfor, brugt brændsel opbevares i kølebassiner i årevis. Kurven er Way–Wigner-tommelfingerreglen: én simpel formel for alle fragmenternes henfald tilsammen, efter et års drift. Begge skalaer springer ti gange ved hvert mærke.</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "fragment mass number A →": "fragmentets massetal A →",
  "share of fissions that make it (each line ×{#})": "andel af fissioner, der danner den (hver linje ×{#})",
  "Rb{#} · {#} %": "Rb{#} · {#} %",
  "Xe{#} · {#} %": "Xe{#} · {#} %",
  "+ about {#} neutrons": "+ ca. {#} neutroner",
  "{#} % of full power": "{#} % af fuld effekt",
  "≈ {#} MW in a {#} MW reactor · {#} s after shutdown": "≈ {#} MW i en {#} MW-reaktor · {#} s efter nedlukning",
  "{#} min": "{#} min",
  "{#} h": "{#} t",
  "{#} day": "{#} døgn",
  "{#} yr": "{#} år",
  "time after shutdown (each mark much later) →": "tid efter nedlukning (hvert mærke meget senere) →",
  "Way–Wigner rule of thumb, after a year at full power": "Way–Wigner-tommelfingerregel, efter et år ved fuld effekt",
});
