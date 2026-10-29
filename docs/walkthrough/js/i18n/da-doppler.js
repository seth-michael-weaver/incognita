/* Danish: doppler (Kapitel 19, dopplerudvidelse) */
WT.L.ch.doppler = {
  num: "Kapitel 19", title: "Dopplerudvidelse", short: "Doppler",
  html: `
<div class="step">
  <h3>Målets termiske bevægelse</h3>
  <p>Varmere brændsel: dets atomer vibrerer hurtigere. Hvert uranatom sidder ikke længere stille, når en neutron ankommer.</p>
  <div class="ctl"><label for="dop-t1">Brændselstemperatur (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Dopplerudvidelse</h3>
  <p>Kurven er sandsynligheden for, at uran-238 fanger en neutron, afbildet mod neutronens energi. Dens højde er et målareal i <b>barn</b> (én barn er 10<sup>−24</sup> cm², omtrent den størrelse, en kerne viser en neutron). Fordi atomerne bevæger sig, møder nogle neutronen frontalt, og andre løber væk fra den, så den smalle top bliver udtværet: lavere og bredere. Dens areal forbliver det samme.</p>
  <div class="ctl"><label for="dop-t2">Brændselstemperatur (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Selvafskærmning af resonanser</h3>
  <p>En brændselspille er tyk. Det skraverede bånd er den andel af neutronerne, den standser ved hver energi. Toppens midte standser allerede alt, varm som kold, så en lavere top mister intet dér; de bredere flanker fanger mere. Flere neutroner går tabt til indfangning i stedet for at forårsage fission, så <i>k</i> falder af sig selv. (<i>k</i> er, hvor mange nye fissioner hver fission fører til; kapitel <a href="#critical">21</a> forklarer det.)</p>
  <div class="ctl"><label for="dop-t3">Brændselstemperatur (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>
`,
};
Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "uranatomer i brændslet",
  "{#} K": "{#} K",
  "caught in the peak": "fanget i toppen",
  "k": "k",
  "neutron energy (eV) →": "neutronenergi (eV) →",
  "capture cross section": "indfangningstværsnit",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "top {#}k barn · Dopplerbredde {#} meV · areal uændret",
  "all stopped": "alle standset",
  "wider wings catch more": "bredere flanker fanger mere",
  "share of neutrons stopped in the fuel": "andel neutroner standset i brændslet",
  "the peak's centre already stops everything; the wider wings catch more": "toppens midte standser allerede alt; de bredere flanker fanger mere",
});
