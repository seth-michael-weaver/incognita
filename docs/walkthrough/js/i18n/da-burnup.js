/* Danish: burnup (Udbrænding af brændsel) */
WT.L.ch.burnup = {
  num: "Lektion 10", title: "Udbrænding af brændsel", short: "Udbrænding",
  html: `
<div class="step">
  <h3>En pille gennem dens levetid</h3>
  <p>Her er tusind atomer fra en frisk brændselspille: 45 er uran-235, resten uran-238. Kør reaktoren, og se uran-235 spaltes, mens nye atomer dukker op. <b>Udbrænding</b> tæller den udtagne energi i gigawattdage pr. ton uran; vandreaktorer stopper ved omkring 45–55.</p>
  <div class="ctl"><label for="bu-d1">Dage ved fuld effekt</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Plutonium kommer med</h3>
  <p>Uran-238 fanger neutroner og bliver til plutonium-239, som også spaltes. Sent i levetiden sker mere end halvdelen af fissionerne i plutonium; over hele levetiden kommer omkring en tredjedel af energien derfra.</p>
  <div class="ctl"><label for="bu-d2">Dage ved fuld effekt</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Gifte hober sig op</h3>
  <p>Hver fission efterlader to fissionsprodukter, og nogle af dem suger neutroner op. Med mindre uran-235 og mere gift glider <i>k</i><sub>∞</sub> (nye fissioner pr. fission i et uendeligt gitter af dette brændsel) nedad, indtil brændslet ikke længere kan holde en kæde i gang alene.</p>
  <div class="ctl"><label for="bu-d3">Dage ved fuld effekt</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Bor og genopladninger</h3>
  <p>En kerne blander frisk, midaldrende og gammelt brændsel. Frisk brændsel har for meget reaktivitet, så bor opløst i kølevandet suger overskuddet op og fortyndes langsomt. Når det når nul, tages den ældste tredjedel ud, og frisk brændsel sættes i.</p>
  <div class="ctl"><label for="bu-m">Måneder ved fuld effekt</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "GWd/t →": "GWd/t →",
  "boron (ppm)": "bor (ppm)",
  "boron in the water (ppm)": "bor i vandet (ppm)",
  "burnup (GWd/t) →": "udbrænding (GWd/t) →",
  "can't keep a chain going alone": "kan ikke holde en kæde i gang alene",
  "cycle {a} months · fuel leaves at {b} GWd/t": "cyklus {a} måneder · brændslet tages ud ved {b} GWd/t",
  "each dot: one atom in a thousand": "hver prik: ét atom ud af tusind",
  "each dot: {#} atom in {#}": "hver prik: {#} atom ud af {#}",
  "energy so far": "energi indtil nu",
  "fission products": "fissionsprodukter",
  "fission products (pairs)": "fissionsprodukter (par)",
  "fission products catch {a} % of neutrons": "fissionsprodukter fanger {a} % af neutronerne",
  "fissions": "fissioner",
  "fissions now": "fissioner nu",
  "fresh": "frisk",
  "illustrative model": "illustrativ model",
  "k = {#}": "k = {#}",
  "k∞ = {a}": "k∞ = {a}",
  "k∞ reaches {#}": "k∞ når {#}",
  "months at full power →": "måneder ved fuld effekt →",
  "months →": "måneder →",
  "one cycle old": "én cyklus gammel",
  "other Pu": "andet Pu",
  "other plutonium": "andet plutonium",
  "plutonium": "plutonium",
  "plutonium's share": "plutoniums andel",
  "plutonium{#}": "plutonium{#}",
  "reload": "genopladning",
  "split": "spaltet",
  "this fuel alone can no longer keep a chain going": "dette brændsel alene kan ikke længere holde en kæde i gang",
  "two cycles old": "to cyklusser gammel",
  "typical discharge": "typisk udtagning",
  "typical discharge {#}–{#}": "typisk udtagning {#}–{#}",
  "uranium{#}": "uran{#}",
  "uranium{#}: the remaining ~{#}–{#} %": "uran{#}: de resterende ~{#}–{#} %",
  "{#} cycle": "{#} cyklus",
  "{#} cycles": "{#} cyklusser",
  "{a} days · burnup {b} GWd/t": "{a} dage · udbrænding {b} GWd/t",
  "{a} in 1000": "{a} ud af 1000",
  "{a} ppm": "{a} ppm",
});
