/* Dutch (Nederlands): waste (Gebruikte brandstof in de loop van de tijd) */
WT.L.ch.waste = {
  num: "Les 5", title: "Gebruikte brandstof in de loop van de tijd", short: "Gebruikte brandstof",
  html: `
<div class="step">
  <h3>Wat eruit komt</h3>
  <p>Na vier of vijf jaar in de kern is een brandstoftablet nog grotendeels uranium. Een paar procent bestaat uit <b>splijtingsproducten</b>, de gespleten atomen. Ongeveer 1 % is plutonium, en een spoortje zijn zwaardere <b>minor actiniden</b> zoals americium.</p>
  <div class="btns"><button class="btn" data-act="sort">Sorteer de atomen</button></div>
</div>
<div class="step">
  <h3>De eerste eeuwen</h3>
  <p>De curve vergelijkt het gevaar van de gebruikte brandstof bij inslikken met dat van het uraniumerts waaruit ze gemaakt is. Eerst domineren de splijtingsproducten, maar de meeste hebben halveringstijden van ongeveer 30 jaar: na zo'n 300 jaar zijn ze onder het erts gezakt.</p>
  <div class="ctl"><label for="wst-t1">Jaren na het ontladen</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Dan plutonium</h3>
  <p>Wat blijft, zijn plutonium en americium, met halveringstijden van eeuwen tot tienduizenden jaren. Zij houden gebruikte brandstof meer dan honderdduizend jaar boven het niveau van het erts.</p>
  <div class="ctl"><label for="wst-t2">Jaren na het ontladen</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Recyclen en transmuteren</h3>
  <p>Haal het plutonium eruit en verbrand het als nieuwe brandstof, en de tijd zakt tot ongeveer tienduizend jaar. Splijt ook de minor actiniden in snelle reactoren, en alleen de splijtingsproducten blijven over: een paar honderd jaar.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Plutonium recyclen</button><button class="btn ghost" data-act="tm" aria-pressed="false">Minor actiniden transmuteren</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Sort the atoms": "Sorteer de atomen",
  "Mix them again": "Meng ze weer",
  "Am, Cm, Np": "Am, Cm, Np",
  "a used fuel pellet, {#} atoms": "een gebruikte brandstoftablet, {#} atomen",
  "a used fuel pellet, {#} atoms shown": "een gebruikte brandstoftablet, {#} atomen getoond",
  "americium, curium…": "americium, curium…",
  "below the ore it came from": "onder het erts waar het vandaan kwam",
  "fission prod.": "splijtingsprod.",
  "fission products": "splijtingsproducten",
  "hazard if swallowed, relative to the ore (log scale)": "gevaar bij inslikken, t.o.v. het erts (log. schaal)",
  "hazard vs ore (log)": "gevaar vs erts (log)",
  "illustrative shape (after OECD-NEA)": "illustratieve vorm (naar OECD-NEA)",
  "minor act.": "min. act.",
  "minor actinides": "minor actiniden",
  "minor actinides removed, plutonium left in": "minor actiniden verwijderd, plutonium blijft",
  "mostly from americium": "vooral van americium",
  "mostly from fission products": "vooral van splijtingsproducten",
  "mostly from plutonium": "vooral van plutonium",
  "only minor actinides removed": "alleen minor actiniden verwijderd",
  "plutonium": "plutonium",
  "plutonium recycled": "plutonium gerecycled",
  "plutonium recycled, minor actinides in the waste": "plutonium gerecycled, minor actiniden in het afval",
  "reaches the ore level after ~{#} years": "bereikt het ertsniveau na ~{#} jaar",
  "recycle + transmute": "recyclen + transmuteren",
  "recycle Pu and transmute minor actinides": "Pu recyclen en minor actiniden transmuteren",
  "spent fuel": "gebruikte brandstof",
  "spent fuel as it is": "gebruikte brandstof zoals ze is",
  "spent fuel kept as it is": "gebruikte brandstof onbehandeld bewaard",
  "spent fuel, one tonne": "gebruikte brandstof, één ton",
  "the glow: fission products are the most radioactive": "de gloed: splijtingsproducten zijn het radioactiefst",
  "the glow: the fission products are by far the most radioactive part": "de gloed: de splijtingsproducten zijn verreweg het radioactiefste deel",
  "the ore": "het erts",
  "the ore it was made from": "het erts waaruit het gemaakt is",
  "the uranium ore it was made from": "het uraniumerts waaruit het gemaakt is",
  "uranium": "uranium",
  "uranium ore level": "niveau van uraniumerts",
  "years after unloading (log scale) →": "jaren na het ontladen (log. schaal) →",
  "{#} million": "{#} miljoen",
  "{#} years: {#} × the ore": "{#} jaar: {#} × het erts",
  "{#} yr": "{#} jr",
});
