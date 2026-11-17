/* Portuguese: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Lição 1", title: "Cálculo da criticidade", short: "Cálculo de k",
  html: `
<div class="step">
  <h3>Os benchmarks</h3>
  <p>Quatro conjuntos críticos rápidos metálicos do ICSBEP, à escala. Godiva e Jezebel são esferas nuas; Flattop-25 e Flattop-Pu têm um refletor de urânio natural.</p>
</div>
<div class="step">
  <h3><i>k</i><sub>eff</sub> calculado</h3>
  <p>OpenMC, energia contínua, geometria 3-D. Os quatro estão dentro de ±1σ do benchmark. <i>k</i><sub>eff</sub> não é usado no ajuste.</p>
</div>
<div class="step">
  <h3>Perfis de sensibilidade</h3>
  <p>Sensibilidade adjunta de <i>k</i><sub>eff</sub> a cada reação, por unidade de letargia.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Verificação por perturbação direta</h3>
  <p>Variações de <i>k</i><sub>eff</sub> previstas face a recalculadas, 63 conjuntos de dados perturbados.</p>
</div>
<div class="step">
  <h3>Núcleo do reator C5G7</h3>
  <p>Quarto de núcleo OECD/NEA C5G7, 1056 varetas de UO<sub>2</sub> e MOX: em 2-D e na extensão 3-D com barras de controlo inseridas. <i>k</i><sub>eff</sub> a menos de 19&nbsp;pcm da referência em 2-D e a menos de 9&nbsp;pcm em cada configuração 3-D.</p>
  <div class="btns"><button class="btn ghost" data-act="c50" aria-pressed="true">2-D</button><button class="btn ghost" data-act="c51" aria-pressed="false">3-D</button><button class="btn ghost" data-act="c52" aria-pressed="false">Barras A</button><button class="btn ghost" data-act="c53" aria-pressed="false">Barras B</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (±{#} benchmark)",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (±{#} benchmark)",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "k calculado − experimental, com a banda ±{#}σ do benchmark",
  "Drag to rotate": "Arraste para rodar",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, sensibilidade integral: ν {#}, fissão {#} (% de k por % de variação)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, sensibilidade integral: ν {#}, fissão {#} (% de k por % de variação)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, sensibilidade integral: ν {#}, fissão {#} (% de k por % de variação)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, fissão {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, fissão {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, fissão {#}",
  "UO₂: {#} × mean": "UO₂: {#} × média",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × média",
  "OpenMC re-solve, Δk (pcm)": "Recálculo OpenMC, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Previsto pelas sensibilidades, Δk (pcm)",
  "predicted Δk, pcm": "Δk previsto, pcm",
  "U{#} capture": "captura de U{#}",
  "Pu{#} capture": "captura de Pu{#}",
  "U{#} elastic": "elástica de U{#}",
  "Pu{#} elastic": "elástica de Pu{#}",
  "U{#} fission": "fissão de U{#}",
  "Pu{#} fission": "fissão de Pu{#}",
  "U{#} inelastic": "inelástica de U{#}",
  "Pu{#} inelastic": "inelástica de Pu{#}",
  "U{#} neutrons per fission (ν)": "neutrões por fissão de U{#} (ν)",
  "Pu{#} neutrons per fission (ν)": "neutrões por fissão de Pu{#} (ν)",
  "Relative pin power (hover a pin)": "Potência relativa por vareta (passe sobre uma vareta)",
  "Relative pin power (tap a pin)": "Potência relativa por vareta (toque numa vareta)",
  "To scale.": "À escala.",
  "To scale. Drag to rotate.": "À escala. Arraste para rodar.",
  "core {#} cm, reflector {#} cm": "núcleo {#} cm, refletor {#} cm",
  "radius {#} cm": "raio {#} cm",
  "{#} cm in {#} cm": "{#} cm em {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; referência {#} ({#} pcm)",
  "k = {#}; reference {#} (+{#} pcm)": "k = {#}; referência {#} (+{#} pcm)",
  "k {#}, reference {#}": "k {#}, referência {#}",
  "plutonium in natural uranium": "plutónio em urânio natural",
  "plutonium metal": "plutónio metálico",
  "uranium{#} in natural uranium": "urânio{#} em urânio natural",
  "uranium{#} metal": "urânio{#} metálico",
  "water": "água",
  "×{#} of mean": "×{#} da média",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
