/* Danish (Dansk): sandbox (Byg en reaktor) */
WT.L.ch.sandbox = {
  num: "Lektion 1", title: "Byg en reaktor", short: "Byg en reaktor",
  lead: "Vælg et brændsel, en moderator, et kølemiddel og en størrelse, og se om en kædereaktion kan holde sig selv i gang. En forenklet lærebogsmodel.",
  html: `
<div class="step">
  <h3>Fire faktorer</h3>
  <p>Hvis ingen neutroner slap ud, ville hver absorberet neutron give <i>k</i><sub>∞</sub> = <i>η f p ε</i> nye; denne grafitstabel af naturligt uran klarer det lige akkurat.</p>
</div>
<div class="step">
  <h3>Vælg en moderator</h3>
  <p>Med naturligt uran får kun tungt vand eller grafit <i>k</i><sub>∞</sub> over 1: let vand bremser neutroner godt, men absorberer for mange.</p>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_h2o">Let vand</button> <button class="btn ghost" data-act="mo_d2o">Tungt vand</button> <button class="btn ghost" data-act="mo_c">Grafit</button></div>
  <div class="ctl"><label for="sb-m1">Moderator pr. brændsel</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Berig brændslet</h3>
  <p>Nogle få procent uran-235 gør almindeligt vand brugbart, og derfor bruger de fleste reaktorer i dag det.</p>
  <div class="btns" role="group" aria-label="Brændsel"><button class="btn ghost" data-act="fu_nat">Naturligt U</button> <button class="btn ghost" data-act="fu_leu">Beriget U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Fissil andel (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Størrelse og lækage</h3>
  <p>Neutroner slipper ud gennem overfladen, så <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Træk kanten af denne grafitstabel af naturligt uran ud til den stiplede ring.</p>
  <div class="ctl"><label for="sb-r1">Kerneradius (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Når kølemidlet koger</h3>
  <p>I en grafitkerne kølet med vand øger kogning <i>k</i>, fordi vandet absorberede mere, end det bremsede: RBMK-reaktorens fejl i Tjernobyl. Prøv andre kølemidler.</p>
  <div class="btns" role="group" aria-label="Kølemiddel"><button class="btn ghost" data-act="co_h2o">Vand</button> <button class="btn ghost" data-act="co_gas">CO₂ / helium</button> <button class="btn ghost" data-act="co_na">Natrium</button></div>
</div>
<div class="step">
  <h3>Byg din egen</h3>
  <p>Alt er tilladt. En hurtig reaktor har ingen moderator og kræver langt mere fissilt brændsel.</p>
  <div class="btns" role="group" aria-label="Brændsel"><button class="btn ghost" data-act="fu_nat">Naturligt U</button> <button class="btn ghost" data-act="fu_leu">Beriget U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Fissil andel (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_none">Ingen moderator</button> <button class="btn ghost" data-act="mo_h2o">Let vand</button> <button class="btn ghost" data-act="mo_d2o">Tungt vand</button> <button class="btn ghost" data-act="mo_c">Grafit</button></div>
  <div class="ctl"><label for="sb-m2">Moderator pr. brændsel</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Kølemiddel"><button class="btn ghost" data-act="co_h2o">Vand</button> <button class="btn ghost" data-act="co_d2o">Tungt vand</button> <button class="btn ghost" data-act="co_gas">CO₂ / helium</button> <button class="btn ghost" data-act="co_na">Natrium</button> <button class="btn ghost" data-act="co_pb">Bly</button> <button class="btn ghost" data-act="co_salt">Smeltet salt</button></div>
  <div class="ctl"><label for="sb-r2">Kerneradius (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} % U{#}": "{#} % U{#}",
  "= η f p ε, if nothing leaked": "= η f p ε, uden lækage",
  "= η f, if nothing leaked": "= η f, uden lækage",
  "absorbed in fuel": "absorberet i brændsel",
  "bonus from fast fission": "bonus fra hurtig fission",
  "can never sustain a chain, at any size": "kan aldrig holde en kæde i gang, uanset størrelse",
  "caught by fuel": "fanget af brændsel",
  "CO₂ / helium gas coolant": "kølemiddel: CO₂-/heliumgas",
  "coolant boils away: k ↑": "kølemidlet koger væk: k ↑",
  "coolant boils away: k ↑ (big sodium cores: spectrum hardens)": "kølemidlet koger væk: k ↑ (store natriumkerner: spektret bliver hårdere)",
  "coolant boils away: k ↑ (small; positive in CANDU)": "kølemidlet koger væk: k ↑ (lille; positiv i CANDU)",
  "coolant boils away: k ↑ (smaller than with sodium)": "kølemidlet koger væk: k ↑ (mindre end med natrium)",
  "coolant boils away: k ↓": "kølemidlet koger væk: k ↓",
  "coolant boils away: k ≈": "kølemidlet koger væk: k ≈",
  "coolant boils away: k barely changes": "kølemidlet koger væk: k ændres knap",
  "coolant boils: k ↑": "kølemidlet koger: k ↑",
  "coolant boils: k ↓": "kølemidlet koger: k ↓",
  "coolant boils: k ≈": "kølemidlet koger: k ≈",
  "coolant heats: k ↑": "kølemidlet varmes op: k ↑",
  "coolant heats: k ↑ (big sodium cores: spectrum hardens)": "kølemidlet varmes op: k ↑ (store natriumkerner: spektret bliver hårdere)",
  "coolant heats: k ↑ (small; positive in CANDU)": "kølemidlet varmes op: k ↑ (lille; positiv i CANDU)",
  "coolant heats: k ↑ (smaller than with sodium)": "kølemidlet varmes op: k ↑ (mindre end med natrium)",
  "coolant heats: k ↓": "kølemidlet varmes op: k ↓",
  "coolant heats: k ≈": "kølemidlet varmes op: k ≈",
  "coolant heats: k barely changes": "kølemidlet varmes op: k ændres knap",
  "coolant lost: k ↑": "kølemidlet tabt: k ↑",
  "coolant lost: k ↑ (big sodium cores: spectrum hardens)": "kølemidlet tabt: k ↑ (store natriumkerner: spektret bliver hårdere)",
  "coolant lost: k ↑ (small; positive in CANDU)": "kølemidlet tabt: k ↑ (lille; positiv i CANDU)",
  "coolant lost: k ↑ (smaller than with sodium)": "kølemidlet tabt: k ↑ (mindre end med natrium)",
  "coolant lost: k ↓": "kølemidlet tabt: k ↓",
  "coolant lost: k ≈": "kølemidlet tabt: k ≈",
  "coolant lost: k barely changes": "kølemidlet tabt: k ændres knap",
  "critical at {#} m": "kritisk ved {#} m",
  "critical size": "kritisk størrelse",
  "enriched U": "beriget U",
  "escape capture": "undslipper indfangning",
  "escape capture while slowing": "undslipper indfangning under nedbremsning",
  "f": "f",
  "fast fission": "hurtig fission",
  "fast fission counted in η": "hurtig fission talt med i η",
  "fission": "fission",
  "fuel": "brændsel",
  "fuel heats up: k ↓ (Doppler)": "brændslet varmes op: k ↓ (Doppler)",
  "fuel hotter: k ↓": "brændsel varmere: k ↓",
  "graphite moderator": "moderator: grafit",
  "graphite moderator · CO₂ / helium gas coolant": "moderator: grafit · kølemiddel: CO₂-/heliumgas",
  "graphite moderator · heavy water coolant": "moderator: grafit · kølemiddel: tungt vand",
  "graphite moderator · lead coolant": "moderator: grafit · kølemiddel: bly",
  "graphite moderator · molten salt coolant": "moderator: grafit · kølemiddel: smeltet salt",
  "graphite moderator · sodium coolant": "moderator: grafit · kølemiddel: natrium",
  "graphite moderator · water coolant": "moderator: grafit · kølemiddel: vand",
  "heavy water coolant": "kølemiddel: tungt vand",
  "heavy water moderates": "tungt vand modererer",
  "heavy water moderator": "moderator: tungt vand",
  "heavy water moderator · CO₂ / helium gas coolant": "moderator: tungt vand · kølemiddel: CO₂-/heliumgas",
  "heavy water moderator · heavy water coolant": "moderator: tungt vand · kølemiddel: tungt vand",
  "heavy water moderator · lead coolant": "moderator: tungt vand · kølemiddel: bly",
  "heavy water moderator · molten salt coolant": "moderator: tungt vand · kølemiddel: smeltet salt",
  "heavy water moderator · sodium coolant": "moderator: tungt vand · kølemiddel: natrium",
  "heavy water moderator · water coolant": "moderator: tungt vand · kølemiddel: vand",
  "k": "k",
  "k∞": "k∞",
  "lead coolant": "kølemiddel: bly",
  "leak": "lækage",
  "leak out": "slipper ud",
  "light water moderator": "moderator: let vand",
  "light water moderator · CO₂ / helium gas coolant": "moderator: let vand · kølemiddel: CO₂-/heliumgas",
  "light water moderator · heavy water coolant": "moderator: let vand · kølemiddel: tungt vand",
  "light water moderator · lead coolant": "moderator: let vand · kølemiddel: bly",
  "light water moderator · molten salt coolant": "moderator: let vand · kølemiddel: smeltet salt",
  "light water moderator · sodium coolant": "moderator: let vand · kølemiddel: natrium",
  "light water moderator · water coolant": "moderator: let vand · kølemiddel: vand",
  "mod./cool.": "mod./køl.",
  "moderator, coolant": "moderator, kølemiddel",
  "molten salt coolant": "kølemiddel: smeltet salt",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % plutonium{#}",
  "natural U": "naturligt U",
  "natural uranium ({#} % U{#})": "naturligt uran ({#} % U{#})",
  "neutrons per absorption in fuel": "neutroner pr. absorption i brændsel",
  "never critical": "aldrig kritisk",
  "no chain, any size": "ingen kæde, uanset størrelse",
  "no leakage": "ingen lækage",
  "no moderator, but the heavy water moderates": "ingen moderator, men tungt vand modererer",
  "no moderator, but the heavy water moderates · heavy water coolant": "ingen moderator, men tungt vand modererer · kølemiddel: tungt vand",
  "no moderator, but the water moderates": "ingen moderator, men vand modererer",
  "no moderator, but the water moderates · water coolant": "ingen moderator, men vand modererer · kølemiddel: vand",
  "no moderator: a fast reactor": "ingen moderator: en hurtig reaktor",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "ingen moderator: en hurtig reaktor · kølemiddel: CO₂-/heliumgas",
  "no moderator: a fast reactor · heavy water coolant": "ingen moderator: en hurtig reaktor · kølemiddel: tungt vand",
  "no moderator: a fast reactor · lead coolant": "ingen moderator: en hurtig reaktor · kølemiddel: bly",
  "no moderator: a fast reactor · molten salt coolant": "ingen moderator: en hurtig reaktor · kølemiddel: smeltet salt",
  "no moderator: a fast reactor · sodium coolant": "ingen moderator: en hurtig reaktor · kølemiddel: natrium",
  "no moderator: a fast reactor · water coolant": "ingen moderator: en hurtig reaktor · kølemiddel: vand",
  "no moderator: fast": "ingen moderator: hurtig",
  "no size is big enough": "ingen størrelse er stor nok",
  "no slowing down, no resonance loss": "ingen nedbremsning, intet resonanstab",
  "p": "p",
  "per fuel absorption": "pr. absorption i brændsel",
  "R {#} m": "R {#} m",
  "radius {#} m": "radius {#} m",
  "radius {#} m · drag the edge": "radius {#} m · træk i kanten",
  "share absorbed in fuel": "andel absorberet i brændsel",
  "simplified model": "forenklet model",
  "simplified one-group model · illustration": "forenklet én-gruppe-model · illustration",
  "sodium coolant": "kølemiddel: natrium",
  "stays in": "bliver inde",
  "stays in (M² {#} cm²)": "bliver inde (M² {#} cm²)",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "bliver inde: {#} / ({#} + M²B²), M² = {#} cm²",
  "sustains a chain, {#} % to spare (ρ)": "holder en kæde i gang, {#} % i overskud (ρ)",
  "sustains: +{#} % spare": "holder: +{#} % overskud",
  "thorium + U{#}": "thorium + U{#}",
  "thorium, {#} % U{#}": "thorium, {#} % U{#}",
  "too small: critical at radius {#} m": "for lille: kritisk ved radius {#} m",
  "too small: needs {#} m": "for lille: kræver {#} m",
  "uranium, {#} % U{#}": "uran, {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "uran, {#} % U{#} (højberiget)",
  "water boils: k ↑": "vandet koger: k ↑",
  "water boils: k ↓": "vandet koger: k ↓",
  "water boils: k ≈": "vandet koger: k ≈",
  "water coolant": "kølemiddel: vand",
  "water heats or boils: k ↑": "vandet varmes op eller koger: k ↑",
  "water heats or boils: k ↑ (big sodium cores: spectrum hardens)": "vandet varmes op eller koger: k ↑ (store natriumkerner: spektret bliver hårdere)",
  "water heats or boils: k ↑ (small; positive in CANDU)": "vandet varmes op eller koger: k ↑ (lille; positiv i CANDU)",
  "water heats or boils: k ↑ (smaller than with sodium)": "vandet varmes op eller koger: k ↑ (mindre end med natrium)",
  "water heats or boils: k ↓": "vandet varmes op eller koger: k ↓",
  "water heats or boils: k ≈": "vandet varmes op eller koger: k ≈",
  "water heats or boils: k barely changes": "vandet varmes op eller koger: k ændres knap",
  "water moderates": "vand modererer",
  "where the neutrons go": "hvor neutronerne går hen",
});
