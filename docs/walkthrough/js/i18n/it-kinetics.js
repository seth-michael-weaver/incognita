/* Italian: kinetics (Lezione 1, cinetica del reattore: sei gruppi ed equazione inhour) */
WT.L.ch.kinetics = {
  num: "Lezione 1", title: "Cinetica del reattore: sei gruppi ed equazione inhour", short: "Cinetica",
  html: `
<div class="step">
  <h3>Sei gruppi di neutroni tardivi</h3>
  <p>I neutroni ritardati provengono da circa sei gruppi di prodotti di fissione, con tempi di dimezzamento da 0,23 s a 56 s (Keepin, U-235). I gruppi da 2 s e da 22 s ne emettono la maggior parte, mentre i gruppi a vita lunga custodiscono la maggior parte della scorta in attesa: ritardo medio Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s. Ferma le fissioni e guarda ogni gruppo esaurirsi con il proprio ritmo.</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">Ferma le fissioni</button></div>
</div>
<div class="step">
  <h3>L'equazione inhour</h3>
  <p>Prova <i>n</i> ∝ e<sup><i>ωt</i></sup> nella cinetica puntiforme a sei gruppi e ottieni <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>): sette rami separati dai poli in −<i>λ</i><sub>i</sub>. Un gradino di <i>ρ</i> incontra ogni ramo una volta; la radice più a destra dà il periodo stabile <i>T</i> = 1/<i>ω</i><sub>1</sub>, le altre sei si smorzano.</p>
  <div class="ctl"><label for="ki-r1">Reattività ρ ($)</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Salto pronto e criticità pronta</h3>
  <p>Un gradino di reattività alza prima la potenza, in pochi millisecondi, di un fattore <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>), poi la potenza cresce con il periodo stabile. A <i>ρ</i> = 1 $ i soli neutroni pronti sono critici e il periodo crolla verso Λ/(<i>ρ</i> − <i>β</i>).</p>
  <div class="ctl"><label for="ki-r2">Reattività ρ ($)</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Dopo uno scram</h3>
  <p>Inserisci una forte reattività negativa: la potenza cade subito a circa <i>β</i>/(<i>β</i> − <i>ρ</i>), poi non può scendere più in fretta di quanto decada il gruppo a vita più lunga. Per quanto profondo sia lo scram, il periodo tende a −1/<i>λ</i><sub>1</sub> ≈ −80 s.</p>
  <div class="ctl"><label for="ki-r3">Reattività ρ ($)</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="kistop" data-act="kistop" */

Object.assign(WT.L.labels, {
  "Stop fissions": "Ferma le fissioni",
  "Restart fissions": "Riavvia le fissioni",
  "half-life · share emitted": "dimezzamento · quota emessa",
  "waiting stock": "scorta in attesa",
  "delayed neutrons out": "neutroni ritardati emessi",
  "{#} s": "{#} s",
  "{#} s after stopping · delayed emission {#} % of the start": "{#} s dall'arresto · emissione ritardata {#} % dell'inizio",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "ritardo medio Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})",
  "Keepin six-group data": "dati di Keepin a sei gruppi",
  "prompt critical": "pronto critico",
  "drag ρ": "trascina ρ",
  "prompt root": "radice pronta",
  "prompt root ≈ −(β−ρ)/Λ": "radice pronta ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω ({#}/s), dilatato",
  "ω ({#}/s), axis stretched (asinh)": "ω ({#}/s), asse dilatato (asinh)",
  "ρ = 0: power stays flat": "ρ = 0: la potenza resta costante",
  "ρ = {#}: power stays flat": "ρ = {#}: la potenza resta costante",
  "stable period T = {#}/ω₁ = {#} ms": "periodo stabile T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "periodo stabile T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "periodo stabile T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "periodo stabile T = {#}/ω₁ = {#} h",
  "drag the rods out": "trascina per estrarre le barre",
  "prompt jump β/(β−ρ) = {#}": "salto pronto β/(β−ρ) = {#}",
  "power": "potenza",
  "prompt critical · period {#} ms (Λ = {#} µs)": "pronto critico · periodo {#} ms (Λ = {#} µs)",
  "prompt critical · period {#} s (Λ = {#} µs)": "pronto critico · periodo {#} s (Λ = {#} µs)",
  "prompt critical · period {#} min (Λ = {#} µs)": "pronto critico · periodo {#} min (Λ = {#} µs)",
  "prompt critical · period {#} h (Λ = {#} µs)": "pronto critico · periodo {#} h (Λ = {#} µs)",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · periodo stabile {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · periodo stabile {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · periodo stabile {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · periodo stabile {#} h",
  "drag the rods in": "trascina per inserire le barre",
  "prompt drop to {#}": "caduta pronta a {#}",
  "slope e^(−t/{#} s)": "pendenza e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "pendenza e^(−t / {#} s): il gruppo da {#} s",
  "power ×{#} speed": "potenza, velocità ×{#}",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · periodo stabile {#} ms (limite {#} s)",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · periodo stabile {#} s (limite {#} s)",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · periodo stabile {#} min (limite {#} s)",
  "ρ = {#} $ · stable period {#} h (limit {#} s)": "ρ = {#} $ · periodo stabile {#} h (limite {#} s)",
});
