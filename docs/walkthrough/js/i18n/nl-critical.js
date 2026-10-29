/* Dutch (Nederlands): critical (Hoofdstuk 20, kritikaliteit en reactorregeling) */
WT.L.ch.critical = {
  num: "Hoofdstuk 20", title: "Kritikaliteit en reactorregeling", short: "Kritikaliteit",
  html: `
<div class="step">
  <h3>De vermenigvuldigingsfactor</h3>
  <p>Elke splijting maakt een paar neutronen vrij; sommige veroorzaken de volgende splijtingen, de rest gaat verloren. De <b>vermenigvuldigingsfactor</b> <i>k</i> is tot hoeveel nieuwe splijtingen één splijting leidt: elke generatie vermenigvuldigt de neutronen met <i>k</i>. Boven 1 groeit de keten, onder 1 sterft ze uit.</p>
  <div class="ctl"><label for="cri-k">Vermenigvuldiging k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Vertraagde neutronen</h3>
  <p>Een klein deel van de neutronen (0,65 %) komt seconden te laat, van splijtingsbrokstukken die eerst vervallen. Die late neutronen bepalen het tempo, dus de groei vertraagt van een oogwenk tot minuten. De grafiek loopt op ×10 snelheid.</p>
  <div class="ctl"><label for="cri-k2">Vermenigvuldiging k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Vertraagde neutronen</button></div>
</div>
<div class="step">
  <h3>Kritikaliteit</h3>
  <p>Een kritiek experiment: beweeg de regelstaven tot het vermogen vlak blijft. Bij die stand is <i>k</i> precies 1, en die staafpositie is de meting. Vind hem: de uitlezing toont <i>k</i> op vijf decimalen.</p>
  <div class="ctl"><label for="cri-rod">Regelstaven erin (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */
Object.assign(WT.L.labels, {
  "generations →": "generaties →",
  "k = {#}: dies away": "k = {#}: sterft uit",
  "k = {#}: steady": "k = {#}: constant",
  "k = {#}: grows": "k = {#}: groeit",
  "{#} generations last under {#} s in a water reactor": "{#} generaties duren in een waterreactor minder dan {#} s",
  "illustration": "illustratie",
  "amber: fission fragments that emit a neutron seconds later": "amber: brokstukken die seconden later een neutron uitzenden",
  "{#} s": "{#} s",
  "time →": "tijd →",
  "×{#} speed": "×{#} snelheid",
  "with delayed: doubles every {#} s": "met vertraagde: verdubbelt elke {#} s",
  "prompt only: doubles every {#} ms": "alleen prompt: verdubbelt elke {#} ms",
  "k = {#} · {#} % of neutrons delayed about {#} s (one-group average)": "k = {#} · {#} % van de neutronen ca. {#} s vertraagd (één-groepsgemiddelde)",
  "rods {#} % in": "staven {#} % in",
  "k = {#} · doubles every {#} min": "k = {#} · verdubbelt elke {#} min",
});
