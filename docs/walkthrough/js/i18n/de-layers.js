/* German (Deutsch): layers (Kapitel 21). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mon = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"][+m[2] - 1];
    return mon ? `${+m[3]}. ${mon} ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} Siege, ${T.t} Remis, ${T.l} Niederlagen"><div class="w"><b>${T.w}</b><span>Sieg</span></div><div><b>${T.t}</b><span>Remis</span></div><div class="l"><b>${T.l}</b><span>Niederlage</span></div></div>` : "");
  const libs = LIBS.length ? `den wichtigsten evaluierten Datenbibliotheken (${LIBS.join(", ")})` : "den wichtigsten evaluierten Datenbibliotheken";
  const engineScore = TE ? ` Von ${TE.d} solchen Vergleichen liegt sie in ${TE.w} klar vorn, in ${TE.t} gleichauf und in ${TE.l} zurück.` : "";
  const terraScore = TT ? `Im Vergleich mit ${libs} liegt sie in ${TT.w} von ${TT.d} Vergleichen vorn, in ${TT.t} gleichauf und in ${TT.l} zurück.` : `Sie wird mit ${libs} verglichen.`;

  WT.L.ch.layers = {
    num: "Kapitel 21", title: "Wie das Modell geschichtet ist", short: "Schichten",
    lead: "Was wir liefern, ist in Schichten auf der Engine aufgebaut, und jede Schicht muss sich ihren Platz gegenüber Messungen verdienen.",
    html: `
<div class="step">
  <div class="layer-chip on">In Gebrauch</div>
  <h3>Schicht 1 · Eine Regel für jeden Kern</h3>
  <p>Die blaue Linie ist die Vorhersage der Engine für eine Reaktion. Die Engine ist die unterste Schicht: dieselbe Physik und dieselben globalen Einstellungen für jedes Nuklid, ohne dass etwas an die Wirkungsquerschnitte eines einzelnen Kerns angepasst ist.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Messungen zeigen</button></div>
  <p>Das macht sie überprüfbar, an Messungen und im Vergleich mit anderen Modellcodes, die auf denselben Kernen laufen. Ein Blindtest ist es nicht: Die globalen Einstellungen wurden mit Blick auf genau diese Vergleiche gewählt.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Getestet: noch kein Gewinn</div>
  <h3>Schicht 2 · Die eigenen Messungen jedes Kerns</h3>
  <p>Diese Schicht ersetzt die globale Regel durch die eigenen Messwerte jedes Kerns: seinen Niveauabstand D0, seine Stärkefunktionen S0 und S1 (wie bereitwillig er langsame Neutronen absorbiert), seine mittlere Gammabreite ⟨Γγ⟩ und seine bekannten Energieniveaus.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Globale Regel</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Eigene Messungen</button></div>
  <p>Schalte sie ein, und die Linie bewegt sich kaum. Tests haben bisher keinen Gewinn insgesamt gefunden: Die eine Variante, die einer Reaktion nahe ihrer Schwelle hilft, verschlechtert den Neutroneneinfang. Daher bleibt diese Schicht vorerst aus.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Kandidat</div>
  <h3>Schicht 3 · Guten Daten folgen (TERRA)</h3>
  <p>Wo eine Reaktion gut gemessen wurde, sollte die Linie den Messungen folgen. Die dritte Schicht, TERRA, führt die Linie der Engine durch gute Daten, wo es sie gibt, und fällt dort, wo es keine gibt, auf die Engine zurück.</p>
  <div class="ctl"><label for="lay-cov">Gemessener Anteil des Energiebereichs (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} Die meisten davon sind In-Sample: TERRA hat diese Messungen gesehen, genau wie die Bibliotheken.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">In Arbeit</div>
  <h3>Schicht 4 · Ehrliche Fehlerbalken</h3>
  <p>Die oberste Schicht legt um die Linie ein Band, das den wahren Wert in etwa zwei von drei Fällen enthalten sollte (ein 68-%-Band): schmal, wo gute Daten ihn festlegen, breiter, wo nicht.</p>
  <div class="ctl"><label for="lay-band">Bandbreite · Messungen innerhalb (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Zieh daran und zähl die Messungen innerhalb. Zu schmal, und das Band behauptet eine Genauigkeit, die es nicht hat; zu breit, und es sagt nichts aus. Das eigene Band der Engine ist noch nicht übernommen: Es trifft das Ziel, wenn alle Reaktionen zusammengefasst werden, aber noch nicht in jeder Reaktionsfamilie. TERRA bringt eigene Bänder mit, und sie sind Teil seiner Vergleiche oben.</p>
</div>
<div class="step">
  <h3>Wo es steht</h3>
  <p>Eine Schicht wird erst übernommen, nachdem sie an Messungen getestet wurde, und sie bleibt aus, wenn sie nicht hilft. Heute ist die Engine in Gebrauch und TERRA ein Kandidat; die Schicht mit gemessener Struktur und das Unsicherheitsband der Engine werden noch getestet.</p>
  <p><a href="scoreboard.html" data-keep-lang>Zur vollständigen Rangliste →</a> Jeder Vergleich, den wir nicht gewinnen, jeder Konkurrent und wie man das liest.</p>
  <div class="aside">${ASOF ? `Ergebnisse mit Stand ${ASOF}, aus` : "Ergebnisse aus"} dem Forschungsprotokoll des Projekts. Die Kurven im Bild dienen der Veranschaulichung.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · Engine",
  "{#} · measured structure": "{#} · gemessene Struktur",
  "{#} · TERRA: anchored to data": "{#} · TERRA: an Daten verankert",
  "{#} · uncertainty band": "{#} · Unsicherheitsband",
  "measured here": "hier gemessen",
  "neutron energy →": "Neutronenenergie →",
  "how often the reaction happens": "wie oft die Reaktion stattfindet",
  "hollow dots: measurements the engine is compared with": "hohle Punkte: Messungen, mit denen die Engine verglichen wird",
  "own measured values: the line barely moves": "eigene Messwerte: die Linie bewegt sich kaum",
  "global rule": "globale Regel",
  "no measurements: TERRA falls back to the engine": "keine Messungen: TERRA fällt auf die Engine zurück",
  "solid: follows the data · dashed: the engine alone": "durchgezogen: folgt den Daten · gestrichelt: nur die Engine",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} von {#} Messungen im Band (Ziel: etwa {#} %)",
  "no measurements to check the band against": "keine Messungen, an denen sich das Band prüfen lässt",
});
Object.assign(WT.L.ui, { nav_board: "Rangliste" });
