/* Danish: xsec (Kapitel 2, tværsnit) */
WT.L.ch.xsec = {
  num: "Kapitel 2", title: "Hvad er et tværsnit?", short: "Tværsnit",
  html: `
<div class="step">
  <p>Hver skive er en kernes målareal: dens <b>tværsnit</b>, skrevet σ (sigma). Billedet ser lige ned på et tyndt lag af kerner, mens neutroner regner ned over det på tilfældige steder. En neutron, der lander inde i en skive, reagerer med den kerne (et orange glimt); en, der lander mellem skiverne, går lige igennem (den toner bare ud).</p>
  <p>Den andel, der reagerer, er altså blot den andel af laget, som skiverne dækker. Den lille sorte firkant er arealenheden, én <b>barn</b>, 10⁻²⁴ cm²: en kernes virkelige areal set forfra er omkring én barn.</p>
  <div class="ctl"><label for="xs-e1">Neutronenergi (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Langsommere neutroner ser større mål. Skiven er ikke kernens virkelige størrelse: den er, hvor stor kernen virker for en neutron ved denne energi, og en langsom neutron bliver længere nær kernen, så den har større chance for at blive fanget. For indfangning får det σ til at vokse som 1/hastighed.</p>
  <p>Kurven under laget er σ over alle energier (begge skalaer er logaritmiske); den orange prik markerer den energi, du valgte. Træk ned til de langsomste neutroner, og se skiverne vokse og den reagerede andel stige.</p>
  <div class="ctl"><label for="xs-e2">Neutronenergi (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Ved en resonans svulmer målet op. Ved 7 eV har neutronen plus kernen præcis energien af ét af kernens egne niveauer, så den optages langt lettere: skiven vokser omkring halvtreds gange i areal, her til omkring 400 barn.</p>
  <p>Flyt dig lidt væk fra 7 eV, og skiven skrumper straks tilbage: toppen i kurven er smal. Rigtige kerner har mange sådanne toppe; kapitel 1 viste deres stregkode.</p>
  <div class="ctl"><label for="xs-e3">Neutronenergi (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "this square: {#} barn = {#}⁻²⁴ cm²": "denne firkant: {#} barn = {#}⁻²⁴ cm²",
  "σ: the target area at each energy": "σ: målarealet ved hver energi",
  "σ ≈ {#} b · reacted {#} % · passed through {#} %": "σ ≈ {#} b · reagerede {#} % · gik igennem {#} %",
  "each falling dot is a neutron: an orange flash means it hit a disc and reacted, a fading dot passed through": "hver faldende prik er en neutron: orange glimt = ramte en skive og reagerede; en prik, der toner ud, gik igennem",
});
