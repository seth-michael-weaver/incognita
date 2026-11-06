/* German (Deutsch): sandbox (Baue einen Reaktor) */
WT.L.ch.sandbox = {
  num: "Lektion 1", title: "Baue einen Reaktor", short: "Reaktor bauen",
  lead: "Wähle einen Brennstoff, einen Moderator, ein Kühlmittel und eine Größe, und sieh, ob sich eine Kettenreaktion selbst erhalten kann. Ein vereinfachtes Lehrbuchmodell.",
  html: `
<div class="step">
  <h3>Vier Faktoren</h3>
  <p>Wenn keine Neutronen entwichen, führte jedes absorbierte zu <i>k</i><sub>∞</sub> = <i>η f p ε</i> neuen; dieser Graphitmeiler aus Natururan schafft es gerade so.</p>
</div>
<div class="step">
  <h3>Wähle einen Moderator</h3>
  <p>Mit Natururan bringt nur Schwerwasser oder Graphit <i>k</i><sub>∞</sub> über 1: Leichtwasser bremst Neutronen gut, schluckt aber zu viele.</p>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_h2o">Leichtwasser</button> <button class="btn ghost" data-act="mo_d2o">Schwerwasser</button> <button class="btn ghost" data-act="mo_c">Graphit</button></div>
  <div class="ctl"><label for="sb-m1">Moderator pro Brennstoff</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Den Brennstoff anreichern</h3>
  <p>Ein paar Prozent Uran-235 machen gewöhnliches Wasser brauchbar, deshalb nutzen es die meisten Reaktoren heute.</p>
  <div class="btns" role="group" aria-label="Brennstoff"><button class="btn ghost" data-act="fu_nat">Natururan</button> <button class="btn ghost" data-act="fu_leu">Angereichertes U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Spaltbarer Anteil (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Größe und Leckage</h3>
  <p>Neutronen entweichen durch die Oberfläche, also gilt <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Zieh den Rand dieses Graphitmeilers aus Natururan bis zum gestrichelten Ring.</p>
  <div class="ctl"><label for="sb-r1">Kernradius (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Wenn das Kühlmittel siedet</h3>
  <p>In einem wassergekühlten Graphitkern erhöht Sieden <i>k</i>, weil das Wasser mehr absorbierte als bremste: der Konstruktionsfehler des RBMK in Tschernobyl. Probiere andere Kühlmittel.</p>
  <div class="btns" role="group" aria-label="Kühlmittel"><button class="btn ghost" data-act="co_h2o">Wasser</button> <button class="btn ghost" data-act="co_gas">CO₂ / Helium</button> <button class="btn ghost" data-act="co_na">Natrium</button></div>
</div>
<div class="step">
  <h3>Bau deinen eigenen</h3>
  <p>Alles ist erlaubt. Ein schneller Reaktor hat keinen Moderator und braucht weit mehr spaltbaren Brennstoff.</p>
  <div class="btns" role="group" aria-label="Brennstoff"><button class="btn ghost" data-act="fu_nat">Natururan</button> <button class="btn ghost" data-act="fu_leu">Angereichertes U</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Thorium + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Spaltbarer Anteil (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Moderator"><button class="btn ghost" data-act="mo_none">Kein Moderator</button> <button class="btn ghost" data-act="mo_h2o">Leichtwasser</button> <button class="btn ghost" data-act="mo_d2o">Schwerwasser</button> <button class="btn ghost" data-act="mo_c">Graphit</button></div>
  <div class="ctl"><label for="sb-m2">Moderator pro Brennstoff</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Kühlmittel"><button class="btn ghost" data-act="co_h2o">Wasser</button> <button class="btn ghost" data-act="co_d2o">Schwerwasser</button> <button class="btn ghost" data-act="co_gas">CO₂ / Helium</button> <button class="btn ghost" data-act="co_na">Natrium</button> <button class="btn ghost" data-act="co_pb">Blei</button> <button class="btn ghost" data-act="co_salt">Salzschmelze</button></div>
  <div class="ctl"><label for="sb-r2">Kernradius (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} % U{#}": "{#} % U{#}",
  "= η f p ε, if nothing leaked": "= η f p ε, ohne Leckage",
  "= η f, if nothing leaked": "= η f, ohne Leckage",
  "absorbed in fuel": "im Brennstoff absorbiert",
  "bonus from fast fission": "Zugabe durch Schnellspaltung",
  "can never sustain a chain, at any size": "kann nie eine Kette erhalten, bei keiner Größe",
  "caught by fuel": "vom Brennstoff eingefangen",
  "CO₂ / helium gas coolant": "Kühlmittel: CO₂-/Heliumgas",
  "coolant boils away: k ↑": "Kühlmittel verdampft: k ↑",
  "coolant boils away: k ↑ (big sodium cores: spectrum hardens)": "Kühlmittel verdampft: k ↑ (große Natriumkerne: Spektrum wird härter)",
  "coolant boils away: k ↑ (small; positive in CANDU)": "Kühlmittel verdampft: k ↑ (klein; im CANDU positiv)",
  "coolant boils away: k ↑ (smaller than with sodium)": "Kühlmittel verdampft: k ↑ (kleiner als bei Natrium)",
  "coolant boils away: k ↓": "Kühlmittel verdampft: k ↓",
  "coolant boils away: k ≈": "Kühlmittel verdampft: k ≈",
  "coolant boils away: k barely changes": "Kühlmittel verdampft: k ändert sich kaum",
  "coolant boils: k ↑": "Kühlmittel siedet: k ↑",
  "coolant boils: k ↓": "Kühlmittel siedet: k ↓",
  "coolant boils: k ≈": "Kühlmittel siedet: k ≈",
  "coolant heats: k ↑": "Kühlmittel erwärmt sich: k ↑",
  "coolant heats: k ↑ (big sodium cores: spectrum hardens)": "Kühlmittel erwärmt sich: k ↑ (große Natriumkerne: Spektrum wird härter)",
  "coolant heats: k ↑ (small; positive in CANDU)": "Kühlmittel erwärmt sich: k ↑ (klein; im CANDU positiv)",
  "coolant heats: k ↑ (smaller than with sodium)": "Kühlmittel erwärmt sich: k ↑ (kleiner als bei Natrium)",
  "coolant heats: k ↓": "Kühlmittel erwärmt sich: k ↓",
  "coolant heats: k ≈": "Kühlmittel erwärmt sich: k ≈",
  "coolant heats: k barely changes": "Kühlmittel erwärmt sich: k ändert sich kaum",
  "coolant lost: k ↑": "Kühlmittel verloren: k ↑",
  "coolant lost: k ↑ (big sodium cores: spectrum hardens)": "Kühlmittel verloren: k ↑ (große Natriumkerne: Spektrum wird härter)",
  "coolant lost: k ↑ (small; positive in CANDU)": "Kühlmittel verloren: k ↑ (klein; im CANDU positiv)",
  "coolant lost: k ↑ (smaller than with sodium)": "Kühlmittel verloren: k ↑ (kleiner als bei Natrium)",
  "coolant lost: k ↓": "Kühlmittel verloren: k ↓",
  "coolant lost: k ≈": "Kühlmittel verloren: k ≈",
  "coolant lost: k barely changes": "Kühlmittel verloren: k ändert sich kaum",
  "critical at {#} m": "kritisch bei {#} m",
  "critical size": "kritische Größe",
  "enriched U": "angereichertes U",
  "escape capture": "entgehen dem Einfang",
  "escape capture while slowing": "entgehen dem Einfang beim Abbremsen",
  "f": "f",
  "fast fission": "Schnellspaltung",
  "fast fission counted in η": "Schnellspaltung in η enthalten",
  "fission": "Spaltung",
  "fuel": "Brennstoff",
  "fuel heats up: k ↓ (Doppler)": "Brennstoff erwärmt sich: k ↓ (Doppler)",
  "fuel hotter: k ↓": "Brennstoff heißer: k ↓",
  "graphite moderator": "Moderator: Graphit",
  "graphite moderator · CO₂ / helium gas coolant": "Moderator: Graphit · Kühlmittel: CO₂-/Heliumgas",
  "graphite moderator · heavy water coolant": "Moderator: Graphit · Kühlmittel: Schwerwasser",
  "graphite moderator · lead coolant": "Moderator: Graphit · Kühlmittel: Blei",
  "graphite moderator · molten salt coolant": "Moderator: Graphit · Kühlmittel: Salzschmelze",
  "graphite moderator · sodium coolant": "Moderator: Graphit · Kühlmittel: Natrium",
  "graphite moderator · water coolant": "Moderator: Graphit · Kühlmittel: Wasser",
  "heavy water coolant": "Kühlmittel: Schwerwasser",
  "heavy water moderates": "Schwerwasser moderiert",
  "heavy water moderator": "Moderator: Schwerwasser",
  "heavy water moderator · CO₂ / helium gas coolant": "Moderator: Schwerwasser · Kühlmittel: CO₂-/Heliumgas",
  "heavy water moderator · heavy water coolant": "Moderator: Schwerwasser · Kühlmittel: Schwerwasser",
  "heavy water moderator · lead coolant": "Moderator: Schwerwasser · Kühlmittel: Blei",
  "heavy water moderator · molten salt coolant": "Moderator: Schwerwasser · Kühlmittel: Salzschmelze",
  "heavy water moderator · sodium coolant": "Moderator: Schwerwasser · Kühlmittel: Natrium",
  "heavy water moderator · water coolant": "Moderator: Schwerwasser · Kühlmittel: Wasser",
  "k": "k",
  "k∞": "k∞",
  "lead coolant": "Kühlmittel: Blei",
  "leak": "Leckage",
  "leak out": "entweichen",
  "light water moderator": "Moderator: Leichtwasser",
  "light water moderator · CO₂ / helium gas coolant": "Moderator: Leichtwasser · Kühlmittel: CO₂-/Heliumgas",
  "light water moderator · heavy water coolant": "Moderator: Leichtwasser · Kühlmittel: Schwerwasser",
  "light water moderator · lead coolant": "Moderator: Leichtwasser · Kühlmittel: Blei",
  "light water moderator · molten salt coolant": "Moderator: Leichtwasser · Kühlmittel: Salzschmelze",
  "light water moderator · sodium coolant": "Moderator: Leichtwasser · Kühlmittel: Natrium",
  "light water moderator · water coolant": "Moderator: Leichtwasser · Kühlmittel: Wasser",
  "mod./cool.": "Mod./Kühlm.",
  "moderator, coolant": "Moderator, Kühlmittel",
  "molten salt coolant": "Kühlmittel: Salzschmelze",
  "MOX": "MOX",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % Plutonium{#}",
  "natural U": "Natururan",
  "natural uranium ({#} % U{#})": "Natururan ({#} % U{#})",
  "neutrons per absorption in fuel": "Neutronen pro Absorption im Brennstoff",
  "never critical": "nie kritisch",
  "no chain, any size": "keine Kette, bei jeder Größe",
  "no leakage": "keine Leckage",
  "no moderator, but the heavy water moderates": "kein Moderator, aber das Schwerwasser moderiert",
  "no moderator, but the heavy water moderates · heavy water coolant": "kein Moderator, aber das Schwerwasser moderiert · Kühlmittel: Schwerwasser",
  "no moderator, but the water moderates": "kein Moderator, aber das Wasser moderiert",
  "no moderator, but the water moderates · water coolant": "kein Moderator, aber das Wasser moderiert · Kühlmittel: Wasser",
  "no moderator: a fast reactor": "kein Moderator: ein schneller Reaktor",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "kein Moderator: ein schneller Reaktor · Kühlmittel: CO₂-/Heliumgas",
  "no moderator: a fast reactor · heavy water coolant": "kein Moderator: ein schneller Reaktor · Kühlmittel: Schwerwasser",
  "no moderator: a fast reactor · lead coolant": "kein Moderator: ein schneller Reaktor · Kühlmittel: Blei",
  "no moderator: a fast reactor · molten salt coolant": "kein Moderator: ein schneller Reaktor · Kühlmittel: Salzschmelze",
  "no moderator: a fast reactor · sodium coolant": "kein Moderator: ein schneller Reaktor · Kühlmittel: Natrium",
  "no moderator: a fast reactor · water coolant": "kein Moderator: ein schneller Reaktor · Kühlmittel: Wasser",
  "no moderator: fast": "kein Moderator: schnell",
  "no size is big enough": "keine Größe reicht",
  "no slowing down, no resonance loss": "keine Abbremsung, kein Resonanzverlust",
  "p": "p",
  "per fuel absorption": "pro Absorption im Brennstoff",
  "R {#} m": "R {#} m",
  "radius {#} m": "Radius {#} m",
  "radius {#} m · drag the edge": "Radius {#} m · Rand ziehen",
  "share absorbed in fuel": "im Brennstoff absorbierter Anteil",
  "simplified model": "vereinfachtes Modell",
  "simplified one-group model · illustration": "vereinfachtes Eingruppenmodell · Illustration",
  "sodium coolant": "Kühlmittel: Natrium",
  "stays in": "bleibt drin",
  "stays in (M² {#} cm²)": "bleibt drin (M² {#} cm²)",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "bleibt drin: {#} / ({#} + M²B²), M² = {#} cm²",
  "sustains a chain, {#} % to spare (ρ)": "erhält eine Kette, {#} % Reserve (ρ)",
  "sustains: +{#} % spare": "erhält: +{#} % Reserve",
  "Th + {#} % U{#}": "Th + {#} % U{#}",
  "thorium + U{#}": "Thorium + U{#}",
  "thorium, {#} % U{#}": "Thorium, {#} % U{#}",
  "too small: critical at radius {#} m": "zu klein: kritisch bei Radius {#} m",
  "too small: needs {#} m": "zu klein: braucht {#} m",
  "uranium, {#} % U{#}": "Uran, {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "Uran, {#} % U{#} (hoch angereichert)",
  "water boils: k ↑": "Wasser siedet: k ↑",
  "water boils: k ↓": "Wasser siedet: k ↓",
  "water boils: k ≈": "Wasser siedet: k ≈",
  "water coolant": "Kühlmittel: Wasser",
  "water heats or boils: k ↑": "Wasser erwärmt sich oder siedet: k ↑",
  "water heats or boils: k ↑ (big sodium cores: spectrum hardens)": "Wasser erwärmt sich oder siedet: k ↑ (große Natriumkerne: Spektrum wird härter)",
  "water heats or boils: k ↑ (small; positive in CANDU)": "Wasser erwärmt sich oder siedet: k ↑ (klein; im CANDU positiv)",
  "water heats or boils: k ↑ (smaller than with sodium)": "Wasser erwärmt sich oder siedet: k ↑ (kleiner als bei Natrium)",
  "water heats or boils: k ↓": "Wasser erwärmt sich oder siedet: k ↓",
  "water heats or boils: k ≈": "Wasser erwärmt sich oder siedet: k ≈",
  "water heats or boils: k barely changes": "Wasser erwärmt sich oder siedet: k ändert sich kaum",
  "water moderates": "Wasser moderiert",
  "where the neutrons go": "wohin die Neutronen gehen",
});
