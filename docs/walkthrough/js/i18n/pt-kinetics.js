/* Portuguese (pt-PT): kinetics (Lição 1, cinética do reator: seis grupos e a equação inhour) */
WT.L.ch.kinetics = {
  num: "Lição 1", title: "Cinética do reator: seis grupos e a equação inhour", short: "Cinética",
  html: `
<div class="step">
  <h3>Seis grupos de neutrões tardios</h3>
  <p>Os neutrões retardados vêm de cerca de seis grupos de produtos de fissão, com meias-vidas de 0,23 s a 56 s (Keepin, U-235). Os grupos de 2 s e de 22 s emitem a maior parte, enquanto os grupos de vida longa guardam a maior parte do stock em espera: atraso médio Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Para as fissões e vê cada grupo esgotar-se ao seu próprio ritmo.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Parar as fissões</button></div>
</div>
<div class="step">
  <h3>A equação inhour</h3>
  <p>Experimenta <i>n</i> ∝ e<sup><i>ωt</i></sup> na cinética pontual a seis grupos e obténs <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): sete ramos separados pelos polos em −<i>λ</i><sub>i</sub>. Um degrau de <i>ρ</i> cruza cada ramo uma vez; a raiz mais à direita dá o período estável <i>T</i> = 1/<i>ω</i><sub>1</sub>, as outras seis extinguem-se.</p>
  <div class="ctl"><label for="ki-r1">Reatividade ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Salto pronto e criticalidade pronta</h3>
  <p>Um degrau de reatividade começa por elevar a potência em milissegundos por um fator <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), e depois ela sobe com o período estável. Em <i>ρ</i> = 1 $ os neutrões prontos bastam sozinhos para a criticalidade e o período desaba para Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">Reatividade ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Depois de um scram</h3>
  <p>Insere uma grande reatividade negativa: a potência cai de imediato para cerca de <i>β</i>/(<i>β</i> − <i>ρ</i>) e depois não pode descer mais depressa do que decai o grupo de vida mais longa. Por mais profundo que seja o scram, o período tende para −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Reatividade ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="kistop" data-act="kistop" */

Object.assign(WT.L.labels, {
  "Stop fissions": "Parar as fissões",
  "Restart fissions": "Retomar as fissões",
  "half-life · share emitted": "meia-vida · fração emitida",
  "waiting stock": "stock em espera",
  "delayed neutrons out": "neutrões retardados emitidos",
  "{#} s": "{#} s",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s após a paragem · emissão retardada {#} % da inicial",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "atraso médio Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "Keepin six-group data": "dados de Keepin a seis grupos",
  "prompt critical": "crítico pronto",
  "drag ρ": "arrasta ρ",
  "prompt root": "raiz pronta",
  "prompt root ≈ −(β−ρ)/Λ": "raiz pronta ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), esticado",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), eixo esticado (asinh)",
  "ρ = 0: power stays flat": "ρ = 0: a potência mantém-se constante",
  "ρ = {#}: power stays flat": "ρ = {#}: a potência mantém-se constante",
  "stable period T = {#}/ω₁ = {#} ms": "período estável T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "período estável T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "período estável T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "período estável T = {#}/ω₁ = {#} h",
  "drag the rods out": "arrasta para retirar as barras",
  "prompt jump β/(β−ρ) = {#}": "salto pronto β/(β−ρ) = {#}",
  "power": "potência",
  "prompt critical · period {#} ms (Λ = {#} µs)": "crítico pronto · período {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "crítico pronto · período {#} s (Λ = {#} µs)",
  "prompt critical · period {#} min (Λ = {#} µs)": "crítico pronto · período {#} min (Λ = {#} µs)",
  "prompt critical · period {#} h (Λ = {#} µs)": "crítico pronto · período {#} h (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · período estável {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · período estável {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · período estável {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · período estável {#} h",
  "drag the rods in": "arrasta para introduzir as barras",
  "prompt drop to {#}": "queda pronta para {#}",
  "slope e^(−t/{#} s)": "declive e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "declive e^(−t / {#} s): o grupo de {#} s",
  "power ×{#} speed": "potência, velocidade ×{#}",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · período estável {#} ms (limite {#} s)",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · período estável {#} s (limite {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · período estável {#} min (limite {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · período estável {#} h (limite {#} s)",
});
