/* German (Deutsch): waste (Abgebrannter Brennstoff im Lauf der Zeit) */
WT.L.ch.waste = {
  num: "Lektion 5", title: "Abgebrannter Brennstoff im Lauf der Zeit", short: "Abgebrannter Brennstoff",
  html: `
<div class="step">
  <h3>Was herauskommt</h3>
  <p>Nach vier oder fünf Jahren im Kern ist eine Brennstofftablette immer noch größtenteils Uran. Ein paar Prozent sind <b>Spaltprodukte</b>, die gespaltenen Atome. Etwa 1 % ist Plutonium, und eine Spur sind schwerere <b>minore Actinoide</b> wie Americium.</p>
  <div class="btns"><button class="btn" data-act="sort">Atome sortieren</button></div>
</div>
<div class="step">
  <h3>Die ersten Jahrhunderte</h3>
  <p>Die Kurve vergleicht die Gefährlichkeit des abgebrannten Brennstoffs beim Verschlucken mit der des Uranerzes, aus dem er hergestellt wurde. Anfangs dominieren die Spaltprodukte, aber die meisten haben Halbwertszeiten von etwa 30 Jahren: Nach rund 300 Jahren sind sie unter das Erz abgeklungen.</p>
  <div class="ctl"><label for="wst-t1">Jahre nach der Entladung</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Dann Plutonium</h3>
  <p>Was bleibt, sind Plutonium und Americium, mit Halbwertszeiten von Jahrhunderten bis zu Zehntausenden Jahren. Sie halten abgebrannten Brennstoff über hunderttausend Jahre lang über dem Niveau des Erzes.</p>
  <div class="ctl"><label for="wst-t2">Jahre nach der Entladung</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Rezyklieren und transmutieren</h3>
  <p>Trennt man das Plutonium ab und verbrennt es als neuen Brennstoff, sinkt die Zeit auf etwa zehntausend Jahre. Spaltet man außerdem die minoren Actinoide in schnellen Reaktoren, bleiben nur die Spaltprodukte übrig: ein paar hundert Jahre.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Plutonium rezyklieren</button><button class="btn ghost" data-act="tm" aria-pressed="false">Minore Actinoide transmutieren</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Sort the atoms": "Atome sortieren",
  "Mix them again": "Wieder mischen",
  "Am, Cm, Np": "Am, Cm, Np",
  "a used fuel pellet, {#} atoms": "eine abgebrannte Brennstofftablette, {#} Atome",
  "a used fuel pellet, {#} atoms shown": "eine abgebrannte Brennstofftablette, {#} Atome gezeigt",
  "americium, curium…": "Americium, Curium …",
  "below the ore it came from": "unter dem Erz, aus dem er stammt",
  "fission prod.": "Spaltprod.",
  "fission products": "Spaltprodukte",
  "hazard if swallowed, relative to the ore (log scale)": "Gefährlichkeit beim Verschlucken, relativ zum Erz (log. Skala)",
  "hazard vs ore (log)": "Gefahr vs. Erz (log)",
  "illustrative shape (after OECD-NEA)": "schematischer Verlauf (nach OECD-NEA)",
  "minor act.": "min. Actin.",
  "minor actinides": "minore Actinoide",
  "minor actinides removed, plutonium left in": "minore Actinoide entfernt, Plutonium verbleibt",
  "mostly from americium": "größtenteils aus Americium",
  "mostly from fission products": "größtenteils aus Spaltprodukten",
  "mostly from plutonium": "größtenteils aus Plutonium",
  "only minor actinides removed": "nur minore Actinoide entfernt",
  "plutonium": "Plutonium",
  "plutonium recycled": "Plutonium rezykliert",
  "plutonium recycled, minor actinides in the waste": "Plutonium rezykliert, minore Actinoide im Abfall",
  "reaches the ore level after ~{#} years": "erreicht das Niveau des Erzes nach ~{#} Jahren",
  "recycle + transmute": "rezyklieren + transmutieren",
  "recycle Pu and transmute minor actinides": "Pu rezyklieren und minore Actinoide transmutieren",
  "spent fuel": "abgebrannter Brennstoff",
  "spent fuel as it is": "abgebrannter Brennstoff, unbehandelt",
  "spent fuel kept as it is": "abgebrannter Brennstoff, unbehandelt gelagert",
  "spent fuel, one tonne": "abgebrannter Brennstoff, eine Tonne",
  "the glow: fission products are the most radioactive": "das Leuchten: Spaltprodukte sind am radioaktivsten",
  "the glow: the fission products are by far the most radioactive part": "das Leuchten: die Spaltprodukte sind bei Weitem der radioaktivste Teil",
  "the ore": "das Erz",
  "the ore it was made from": "das Erz, aus dem er stammt",
  "the uranium ore it was made from": "das Uranerz, aus dem er stammt",
  "uranium": "Uran",
  "uranium ore level": "Niveau des Uranerzes",
  "years after unloading (log scale) →": "Jahre nach der Entladung (log. Skala) →",
  "{#} million": "{#} Millionen",
  "{#} years: {#} × the ore": "{#} Jahre: {#} × das Erz",
  "{#} yr": "{#} a",
});
