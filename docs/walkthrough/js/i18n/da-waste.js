/* Danish: waste (Brugt brændsel over tid) */
WT.L.ch.waste = {
  num: "Lektion 5", title: "Brugt brændsel over tid", short: "Brugt brændsel",
  html: `
<div class="step">
  <h3>Hvad der kommer ud</h3>
  <p>Efter fire eller fem år i kernen er en brændselspille stadig mest uran. Et par procent er <b>fissionsprodukter</b>, de spaltede atomer. Omkring 1 % er plutonium, og et spor er tungere <b>mindre actinider</b> som americium.</p>
  <div class="btns"><button class="btn" data-act="sort">Sortér atomerne</button></div>
</div>
<div class="step">
  <h3>De første århundreder</h3>
  <p>Kurven sammenligner det brugte brændsels farlighed, hvis det sluges, med farligheden af den uranmalm, det blev lavet af. Først dominerer fissionsprodukterne, men de fleste har halveringstider på omkring 30 år: efter cirka 300 år er de faldet under malmen.</p>
  <div class="ctl"><label for="wst-t1">År efter udtagning</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Så plutonium</h3>
  <p>Det, der bliver tilbage, er plutonium og americium med halveringstider fra århundreder til titusinder af år. De holder brugt brændsel over malmens niveau i mere end hundrede tusind år.</p>
  <div class="ctl"><label for="wst-t2">År efter udtagning</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Genanvend og transmutér</h3>
  <p>Tag plutoniummet ud og brænd det som nyt brændsel, så falder tiden til omkring ti tusind år. Spalt også de mindre actinider i hurtige reaktorer, så er kun fissionsprodukterne tilbage: et par hundrede år.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Genanvend plutonium</button><button class="btn ghost" data-act="tm" aria-pressed="false">Transmutér mindre actinider</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Sort the atoms": "Sortér atomerne",
  "Mix them again": "Bland dem igen",
  "Am, Cm, Np": "Am, Cm, Np",
  "a used fuel pellet, {#} atoms": "en brugt brændselspille, {#} atomer",
  "a used fuel pellet, {#} atoms shown": "en brugt brændselspille, {#} atomer vist",
  "americium, curium…": "americium, curium…",
  "below the ore it came from": "under malmen, det kom fra",
  "fission prod.": "fissionsprod.",
  "fission products": "fissionsprodukter",
  "hazard if swallowed, relative to the ore (log scale)": "farlighed ved indtagelse, i forhold til malmen (log. skala)",
  "hazard vs ore (log)": "farlighed vs malm (log)",
  "illustrative shape (after OECD-NEA)": "illustrativ form (efter OECD-NEA)",
  "minor act.": "mindre act.",
  "minor actinides": "mindre actinider",
  "minor actinides removed, plutonium left in": "mindre actinider fjernet, plutonium bliver",
  "mostly from americium": "mest fra americium",
  "mostly from fission products": "mest fra fissionsprodukter",
  "mostly from plutonium": "mest fra plutonium",
  "only minor actinides removed": "kun mindre actinider fjernet",
  "plutonium": "plutonium",
  "plutonium recycled": "plutonium genanvendt",
  "plutonium recycled, minor actinides in the waste": "plutonium genanvendt, mindre actinider i affaldet",
  "reaches the ore level after ~{#} years": "når malmens niveau efter ~{#} år",
  "recycle + transmute": "genanvend + transmutér",
  "recycle Pu and transmute minor actinides": "genanvend Pu og transmutér mindre actinider",
  "spent fuel": "brugt brændsel",
  "spent fuel as it is": "brugt brændsel, som det er",
  "spent fuel kept as it is": "brugt brændsel opbevaret, som det er",
  "spent fuel, one tonne": "brugt brændsel, ét ton",
  "the glow: fission products are the most radioactive": "gløden: fissionsprodukterne er mest radioaktive",
  "the glow: the fission products are by far the most radioactive part": "gløden: fissionsprodukterne er langt den mest radioaktive del",
  "the ore": "malmen",
  "the ore it was made from": "malmen, det blev lavet af",
  "the uranium ore it was made from": "uranmalmen, det blev lavet af",
  "uranium": "uran",
  "uranium ore level": "uranmalmens niveau",
  "years after unloading (log scale) →": "år efter udtagning (log. skala) →",
  "{#} million": "{#} millioner",
  "{#} years: {#} × the ore": "{#} år: {#} × malmen",
  "{#} yr": "{#} år",
});
