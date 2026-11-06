/* Dutch (Nederlands): burnup (Opbrand van brandstof) */
WT.L.ch.burnup = {
  num: "Les 10", title: "Opbrand van brandstof", short: "Opbrand",
  html: `
<div class="step">
  <h3>Een tablet gedurende zijn leven</h3>
  <p>Hier zijn duizend atomen uit een verse brandstoftablet: 45 zijn uranium-235, de rest uranium-238. Laat de reactor draaien en kijk hoe het uranium-235 splijt terwijl nieuwe atomen verschijnen. <b>Opbrand</b> telt de onttrokken energie, in gigawattdagen per ton uranium; waterreactoren stoppen bij ongeveer 45–55.</p>
  <div class="ctl"><label for="bu-d1">Dagen op vol vermogen</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Plutonium doet mee</h3>
  <p>Uranium-238 vangt neutronen in en wordt plutonium-239, dat ook splijt. Laat in het leven vindt meer dan de helft van de splijtingen in plutonium plaats; over het hele leven komt ongeveer een derde van de energie ervan.</p>
  <div class="ctl"><label for="bu-d2">Dagen op vol vermogen</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Gifstoffen stapelen zich op</h3>
  <p>Elke splijting laat twee splijtingsproducten achter, en sommige daarvan slokken neutronen op. Met minder uranium-235 en meer gif zakt <i>k</i><sub>∞</sub> (nieuwe splijtingen per splijting in een oneindig rooster van deze brandstof) langzaam, tot de brandstof alleen geen keten meer gaande kan houden.</p>
  <div class="ctl"><label for="bu-d3">Dagen op vol vermogen</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Boor en herladingen</h3>
  <p>Een kern mengt verse, middelbare en oude brandstof. Verse brandstof heeft te veel reactiviteit, dus in het koelwater opgelost boor slokt het overschot op en wordt langzaam verdund. Bereikt het nul, dan gaat het oudste derde eruit en komt er verse brandstof in.</p>
  <div class="ctl"><label for="bu-m">Maanden op vol vermogen</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "GWd/t →": "GWd/t →",
  "boron (ppm)": "boor (ppm)",
  "boron in the water (ppm)": "boor in het water (ppm)",
  "burnup (GWd/t) →": "opbrand (GWd/t) →",
  "can't keep a chain going alone": "houdt alleen geen keten gaande",
  "cycle {a} months · fuel leaves at {b} GWd/t": "cyclus {a} maanden · brandstof gaat eruit bij {b} GWd/t",
  "each dot: one atom in a thousand": "elke stip: één atoom op duizend",
  "each dot: {#} atom in {#}": "elke stip: {#} atoom op {#}",
  "energy so far": "energie tot nu toe",
  "fission products": "splijtingsproducten",
  "fission products (pairs)": "splijtingsproducten (paren)",
  "fission products catch {a} % of neutrons": "splijtingsproducten vangen {a} % van de neutronen",
  "fissions": "splijtingen",
  "fissions now": "splijtingen nu",
  "fresh": "vers",
  "illustrative model": "illustratief model",
  "k = {#}": "k = {#}",
  "k∞ = {a}": "k∞ = {a}",
  "k∞ reaches {#}": "k∞ bereikt {#}",
  "months at full power →": "maanden op vol vermogen →",
  "months →": "maanden →",
  "one cycle old": "één cyclus oud",
  "other Pu": "overig Pu",
  "other plutonium": "overig plutonium",
  "plutonium": "plutonium",
  "plutonium's share": "aandeel plutonium",
  "plutonium{#}": "plutonium{#}",
  "reload": "herlading",
  "split": "gespleten",
  "this fuel alone can no longer keep a chain going": "deze brandstof alleen kan geen keten meer gaande houden",
  "two cycles old": "twee cycli oud",
  "typical discharge": "typische ontlaadopbrand",
  "typical discharge {#}–{#}": "typische ontlaadopbrand {#}–{#}",
  "uranium{#}": "uranium{#}",
  "uranium{#}: the remaining ~{#}–{#} %": "uranium{#}: de overige ~{#}–{#} %",
  "{#} cycle": "{#} cyclus",
  "{#} cycles": "{#} cycli",
  "{a} days · burnup {b} GWd/t": "{a} dagen · opbrand {b} GWd/t",
  "{a} in 1000": "{a} op 1000",
  "{a} ppm": "{a} ppm",
});
