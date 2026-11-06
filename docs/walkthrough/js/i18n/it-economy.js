/* Italian: economy (Il bilancio neutronico) */
WT.L.ch.economy = {
  num: "Lezione 1", title: "Il bilancio neutronico", short: "Bilancio neutronico",
  html: `
<div class="step">
  <h3>Mille neutroni</h3>
  <p>Segui 1000 neutroni veloci per una generazione. Alcuni provocano fissioni in più, alcuni sfuggono, alcuni vengono catturati lungo il percorso, e i restanti spezzano l'uranio-235 producendo il migliaio successivo. Sei fattori si moltiplicano per dare <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>L'arricchimento</h3>
  <p>Più uranio-235 nel combustibile significa che più neutroni vengono assorbiti dove provocano la fissione. Con uranio naturale (0,7 %) e acqua normale, <i>k</i> non arriva mai a 1.</p>
  <div class="ctl"><label for="eco-e">Uranio-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>L'acqua fra le barrette</h3>
  <p>Con troppa poca acqua, i neutroni che rallentano vengono catturati dall'uranio-238; con troppa, è l'acqua stessa ad assorbirli. Esiste un rapporto ottimale, e i reattori ad acqua sono costruiti un po' al di sotto.</p>
  <div class="ctl"><label for="eco-m">Acqua per combustibile (× tipico)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Le dimensioni</h3>
  <p>I neutroni nati vicino alla superficie possono sfuggire. Un nocciolo piccolo ne perde troppi; uno più grande li trattiene. Trova la dimensione a cui <i>k</i> supera 1.</p>
  <div class="ctl"><label for="eco-s">Dimensione del nocciolo (× tipica)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "fast fission": "fissione veloce",
  "fast leak": "fuga veloce",
  "leaks out, fast": "sfuggono, veloci",
  "U{#} catches": "cattura U{#}",
  "caught by U{#}": "catturati dall'U{#}",
  "slow leak": "fuga lenta",
  "leaks out, slow": "sfuggono, lenti",
  "water, steel…": "acqua, acciaio…",
  "water, steel, boron": "acqua, acciaio, boro",
  "P fast {#}": "P veloci {#}",
  "P slow {#}": "P lenti {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "rallent.",
  "slowing down": "rallentamento",
  "{#} split U{#}": "{#} fissioni di U{#}",
  "next: {#}": "prossima: {#}",
  "next generation: {#}": "generazione successiva: {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "critico: stabile",
  "grows": "cresce",
  "dies away": "si spegne",
  "best ≈ {#}×": "ottimo ≈ {#}×",
  "less water": "meno acqua",
  "more water": "più acqua",
  "{#} % leak out": "{#} % sfuggono",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "valori da manuale (D&H); andamenti illustrativi",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "fattori: valori da manuale (Duderstadt & Hamilton) al {#} %; andamenti dei cursori illustrativi",
});
