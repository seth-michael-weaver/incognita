/* Portuguese (Português): sandbox (Construa um reator) */
WT.L.ch.sandbox = {
  num: "Lição 1", title: "Construa um reator", short: "Construa um reator",
  lead: "Escolha um combustível, um moderador, um refrigerante e um tamanho, e veja se uma reação em cadeia se consegue manter sozinha. Um modelo de manual simplificado.",
  html: `
<div class="step">
  <h3>Quatro fatores</h3>
  <p>Se nenhum neutrão escapasse, cada neutrão absorvido daria origem a <i>k</i><sub>∞</sub> = <i>η f p ε</i> novos; esta pilha de grafite com urânio natural consegue-o à justa.</p>
</div>
<div class="step">
  <h3>Escolha um moderador</h3>
  <p>Com urânio natural, só a água pesada ou a grafite levam <i>k</i><sub>∞</sub> acima de 1: a água leve abranda bem os neutrões, mas absorve demasiados.</p>
  <div class="btns" role="group" aria-label="Moderador"><button class="btn ghost" data-act="mo_h2o">Água leve</button> <button class="btn ghost" data-act="mo_d2o">Água pesada</button> <button class="btn ghost" data-act="mo_c">Grafite</button></div>
  <div class="ctl"><label for="sb-m1">Moderador por combustível</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Enriqueça o combustível</h3>
  <p>Uns poucos por cento de urânio-235 tornam a água comum utilizável, e é por isso que a maioria dos reatores atuais a usa.</p>
  <div class="btns" role="group" aria-label="Combustível"><button class="btn ghost" data-act="fu_nat">U natural</button> <button class="btn ghost" data-act="fu_leu">U enriquecido</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Tório + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Fração físsil (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Tamanho e fugas</h3>
  <p>Os neutrões escapam pela superfície, por isso <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Arraste a borda desta pilha de grafite com urânio natural até ao anel tracejado.</p>
  <div class="ctl"><label for="sb-r1">Raio do núcleo (m)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Quando o refrigerante ferve</h3>
  <p>Num núcleo de grafite arrefecido a água, a ebulição aumenta <i>k</i>, porque a água absorvia mais do que abrandava: a falha do RBMK em Chernobyl. Experimente outros refrigerantes.</p>
  <div class="btns" role="group" aria-label="Refrigerante"><button class="btn ghost" data-act="co_h2o">Água</button> <button class="btn ghost" data-act="co_gas">CO₂ / hélio</button> <button class="btn ghost" data-act="co_na">Sódio</button></div>
</div>
<div class="step">
  <h3>Construa o seu</h3>
  <p>Vale tudo. Um reator rápido não tem moderador e precisa de muito mais combustível físsil.</p>
  <div class="btns" role="group" aria-label="Combustível"><button class="btn ghost" data-act="fu_nat">U natural</button> <button class="btn ghost" data-act="fu_leu">U enriquecido</button> <button class="btn ghost" data-act="fu_mox">MOX (Pu)</button> <button class="btn ghost" data-act="fu_th">Tório + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Fração físsil (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Moderador"><button class="btn ghost" data-act="mo_none">Sem moderador</button> <button class="btn ghost" data-act="mo_h2o">Água leve</button> <button class="btn ghost" data-act="mo_d2o">Água pesada</button> <button class="btn ghost" data-act="mo_c">Grafite</button></div>
  <div class="ctl"><label for="sb-m2">Moderador por combustível</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Refrigerante"><button class="btn ghost" data-act="co_h2o">Água</button> <button class="btn ghost" data-act="co_d2o">Água pesada</button> <button class="btn ghost" data-act="co_gas">CO₂ / hélio</button> <button class="btn ghost" data-act="co_na">Sódio</button> <button class="btn ghost" data-act="co_pb">Chumbo</button> <button class="btn ghost" data-act="co_salt">Sal fundido</button></div>
  <div class="ctl"><label for="sb-r2">Raio do núcleo (m)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} % U{#}": "{#} % U{#}",
  "= η f p ε, if nothing leaked": "= η f p ε, sem fugas",
  "= η f, if nothing leaked": "= η f, sem fugas",
  "absorbed in fuel": "absorvidos no combustível",
  "bonus from fast fission": "bónus da fissão rápida",
  "can never sustain a chain, at any size": "nunca sustenta uma cadeia, seja qual for o tamanho",
  "caught by fuel": "capturados pelo combustível",
  "CO₂ / helium gas coolant": "refrigerante: gás CO₂ / hélio",
  "coolant boils away: k ↑": "o refrigerante evapora-se: k ↑",
  "coolant boils away: k ↑ (big sodium cores: spectrum hardens)": "o refrigerante evapora-se: k ↑ (núcleos grandes de sódio: o espectro endurece)",
  "coolant boils away: k ↑ (small; positive in CANDU)": "o refrigerante evapora-se: k ↑ (pequeno; positivo no CANDU)",
  "coolant boils away: k ↑ (smaller than with sodium)": "o refrigerante evapora-se: k ↑ (menor do que com sódio)",
  "coolant boils away: k ↓": "o refrigerante evapora-se: k ↓",
  "coolant boils away: k ≈": "o refrigerante evapora-se: k ≈",
  "coolant boils away: k barely changes": "o refrigerante evapora-se: k quase não muda",
  "coolant boils: k ↑": "o refrigerante ferve: k ↑",
  "coolant boils: k ↓": "o refrigerante ferve: k ↓",
  "coolant boils: k ≈": "o refrigerante ferve: k ≈",
  "coolant heats: k ↑": "o refrigerante aquece: k ↑",
  "coolant heats: k ↑ (big sodium cores: spectrum hardens)": "o refrigerante aquece: k ↑ (núcleos grandes de sódio: o espectro endurece)",
  "coolant heats: k ↑ (small; positive in CANDU)": "o refrigerante aquece: k ↑ (pequeno; positivo no CANDU)",
  "coolant heats: k ↑ (smaller than with sodium)": "o refrigerante aquece: k ↑ (menor do que com sódio)",
  "coolant heats: k ↓": "o refrigerante aquece: k ↓",
  "coolant heats: k ≈": "o refrigerante aquece: k ≈",
  "coolant heats: k barely changes": "o refrigerante aquece: k quase não muda",
  "coolant lost: k ↑": "refrigerante perdido: k ↑",
  "coolant lost: k ↑ (big sodium cores: spectrum hardens)": "refrigerante perdido: k ↑ (núcleos grandes de sódio: o espectro endurece)",
  "coolant lost: k ↑ (small; positive in CANDU)": "refrigerante perdido: k ↑ (pequeno; positivo no CANDU)",
  "coolant lost: k ↑ (smaller than with sodium)": "refrigerante perdido: k ↑ (menor do que com sódio)",
  "coolant lost: k ↓": "refrigerante perdido: k ↓",
  "coolant lost: k ≈": "refrigerante perdido: k ≈",
  "coolant lost: k barely changes": "refrigerante perdido: k quase não muda",
  "critical at {#} m": "crítico a {#} m",
  "critical size": "tamanho crítico",
  "enriched U": "U enriquecido",
  "escape capture": "escapam à captura",
  "escape capture while slowing": "escapam à captura ao abrandar",
  "f": "f",
  "fast fission": "fissão rápida",
  "fast fission counted in η": "fissão rápida incluída em η",
  "fission": "fissão",
  "fuel": "combustível",
  "fuel heats up: k ↓ (Doppler)": "o combustível aquece: k ↓ (Doppler)",
  "fuel hotter: k ↓": "combustível mais quente: k ↓",
  "graphite moderator": "moderador: grafite",
  "graphite moderator · CO₂ / helium gas coolant": "moderador: grafite · refrigerante: gás CO₂ / hélio",
  "graphite moderator · heavy water coolant": "moderador: grafite · refrigerante: água pesada",
  "graphite moderator · lead coolant": "moderador: grafite · refrigerante: chumbo",
  "graphite moderator · molten salt coolant": "moderador: grafite · refrigerante: sal fundido",
  "graphite moderator · sodium coolant": "moderador: grafite · refrigerante: sódio",
  "graphite moderator · water coolant": "moderador: grafite · refrigerante: água",
  "heavy water coolant": "refrigerante: água pesada",
  "heavy water moderates": "a água pesada modera",
  "heavy water moderator": "moderador: água pesada",
  "heavy water moderator · CO₂ / helium gas coolant": "moderador: água pesada · refrigerante: gás CO₂ / hélio",
  "heavy water moderator · heavy water coolant": "moderador: água pesada · refrigerante: água pesada",
  "heavy water moderator · lead coolant": "moderador: água pesada · refrigerante: chumbo",
  "heavy water moderator · molten salt coolant": "moderador: água pesada · refrigerante: sal fundido",
  "heavy water moderator · sodium coolant": "moderador: água pesada · refrigerante: sódio",
  "heavy water moderator · water coolant": "moderador: água pesada · refrigerante: água",
  "k": "k",
  "k∞": "k∞",
  "lead coolant": "refrigerante: chumbo",
  "leak": "fuga",
  "leak out": "escapam",
  "light water moderator": "moderador: água leve",
  "light water moderator · CO₂ / helium gas coolant": "moderador: água leve · refrigerante: gás CO₂ / hélio",
  "light water moderator · heavy water coolant": "moderador: água leve · refrigerante: água pesada",
  "light water moderator · lead coolant": "moderador: água leve · refrigerante: chumbo",
  "light water moderator · molten salt coolant": "moderador: água leve · refrigerante: sal fundido",
  "light water moderator · sodium coolant": "moderador: água leve · refrigerante: sódio",
  "light water moderator · water coolant": "moderador: água leve · refrigerante: água",
  "mod./cool.": "mod./refr.",
  "moderator, coolant": "moderador, refrigerante",
  "molten salt coolant": "refrigerante: sal fundido",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX, {#} % de plutónio{#}",
  "natural U": "U natural",
  "natural uranium ({#} % U{#})": "urânio natural ({#} % U{#})",
  "neutrons per absorption in fuel": "neutrões por absorção no combustível",
  "never critical": "nunca crítico",
  "no chain, any size": "sem cadeia, a qualquer tamanho",
  "no leakage": "sem fugas",
  "no moderator, but the heavy water moderates": "sem moderador, mas a água pesada modera",
  "no moderator, but the heavy water moderates · heavy water coolant": "sem moderador, mas a água pesada modera · refrigerante: água pesada",
  "no moderator, but the water moderates": "sem moderador, mas a água modera",
  "no moderator, but the water moderates · water coolant": "sem moderador, mas a água modera · refrigerante: água",
  "no moderator: a fast reactor": "sem moderador: um reator rápido",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "sem moderador: um reator rápido · refrigerante: gás CO₂ / hélio",
  "no moderator: a fast reactor · heavy water coolant": "sem moderador: um reator rápido · refrigerante: água pesada",
  "no moderator: a fast reactor · lead coolant": "sem moderador: um reator rápido · refrigerante: chumbo",
  "no moderator: a fast reactor · molten salt coolant": "sem moderador: um reator rápido · refrigerante: sal fundido",
  "no moderator: a fast reactor · sodium coolant": "sem moderador: um reator rápido · refrigerante: sódio",
  "no moderator: a fast reactor · water coolant": "sem moderador: um reator rápido · refrigerante: água",
  "no moderator: fast": "sem moderador: rápido",
  "no size is big enough": "nenhum tamanho chega",
  "no slowing down, no resonance loss": "sem abrandamento, sem perdas por ressonância",
  "p": "p",
  "per fuel absorption": "por absorção no combustível",
  "R {#} m": "R {#} m",
  "radius {#} m": "raio {#} m",
  "radius {#} m · drag the edge": "raio {#} m · arraste a borda",
  "share absorbed in fuel": "fração absorvida no combustível",
  "simplified model": "modelo simplificado",
  "simplified one-group model · illustration": "modelo simplificado a um grupo · ilustração",
  "sodium coolant": "refrigerante: sódio",
  "stays in": "ficam",
  "stays in (M² {#} cm²)": "ficam (M² {#} cm²)",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "ficam: {#} / ({#} + M²B²), M² = {#} cm²",
  "sustains a chain, {#} % to spare (ρ)": "sustenta uma cadeia, {#} % de margem (ρ)",
  "sustains: +{#} % spare": "sustenta: +{#} % de margem",
  "thorium + U{#}": "tório + U{#}",
  "thorium, {#} % U{#}": "tório, {#} % U{#}",
  "too small: critical at radius {#} m": "pequeno demais: crítico com raio de {#} m",
  "too small: needs {#} m": "pequeno demais: precisa de {#} m",
  "uranium, {#} % U{#}": "urânio, {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "urânio, {#} % U{#} (altamente enriquecido)",
  "water boils: k ↑": "a água ferve: k ↑",
  "water boils: k ↓": "a água ferve: k ↓",
  "water boils: k ≈": "a água ferve: k ≈",
  "water coolant": "refrigerante: água",
  "water heats or boils: k ↑": "a água aquece ou ferve: k ↑",
  "water heats or boils: k ↑ (big sodium cores: spectrum hardens)": "a água aquece ou ferve: k ↑ (núcleos grandes de sódio: o espectro endurece)",
  "water heats or boils: k ↑ (small; positive in CANDU)": "a água aquece ou ferve: k ↑ (pequeno; positivo no CANDU)",
  "water heats or boils: k ↑ (smaller than with sodium)": "a água aquece ou ferve: k ↑ (menor do que com sódio)",
  "water heats or boils: k ↓": "a água aquece ou ferve: k ↓",
  "water heats or boils: k ≈": "a água aquece ou ferve: k ≈",
  "water heats or boils: k barely changes": "a água aquece ou ferve: k quase não muda",
  "water moderates": "a água modera",
  "where the neutrons go": "para onde vão os neutrões",
});
