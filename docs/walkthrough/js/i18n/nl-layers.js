/* Dutch (Nederlands): layers (hoofdstuk 21). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
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
    const maand = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"][+m[2] - 1];
    return maand ? `${+m[3]} ${maand} ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} gewonnen, ${T.t} gelijk, ${T.l} verloren"><div class="w"><b>${T.w}</b><span>winst</span></div><div><b>${T.t}</b><span>gelijk</span></div><div class="l"><b>${T.l}</b><span>verlies</span></div></div>` : "");
  const libs = LIBS.length ? `de belangrijkste geëvalueerde databibliotheken (${LIBS.join(", ")})` : "de belangrijkste geëvalueerde databibliotheken";
  const engineScore = TE ? ` Van ${TE.d} van zulke vergelijkingen ligt hij er in ${TE.w} duidelijk voor, in ${TE.t} gelijk en in ${TE.l} achter.` : "";
  const terraScore = TT ? `Tegenover ${libs} ligt het in ${TT.w} van ${TT.d} vergelijkingen voor, in ${TT.t} gelijk en in ${TT.l} achter.` : `Het wordt vergeleken met ${libs}.`;

  WT.L.ch.layers = {
    num: "Hoofdstuk 21", title: "Hoe het model in lagen is opgebouwd", short: "Lagen",
    lead: "Wat we leveren, is in lagen bovenop de motor gebouwd, en elke laag moet haar plaats verdienen tegenover metingen.",
    html: `
<div class="step">
  <div class="layer-chip on">In gebruik</div>
  <h3>Laag 1 · Eén regel voor elke kern</h3>
  <p>De blauwe lijn is de voorspelling van de motor voor één reactie. De motor is de onderste laag: dezelfde natuurkunde en globale instellingen voor elke nuclide, zonder dat er iets gefit is aan de werkzame doorsneden van één afzonderlijke kern.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Toon de metingen</button></div>
  <p>Dat maakt hem toetsbaar, aan metingen en tegenover andere modelcodes die op dezelfde kernen zijn gedraaid. Een blinde test is het niet: de globale instellingen zijn gekozen terwijl we naar precies deze vergelijkingen keken.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Getest: nog geen winst</div>
  <h3>Laag 2 · De eigen metingen van elke kern</h3>
  <p>Deze laag ruilt de globale regel in voor de eigen gemeten waarden van elke kern: zijn niveauafstand D0, zijn sterktefuncties S0 en S1 (hoe makkelijk hij langzame neutronen absorbeert), zijn gemiddelde gammabreedte ⟨Γγ⟩ en zijn bekende energieniveaus.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Globale regel</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Eigen metingen</button></div>
  <p>Zet haar aan en de lijn beweegt nauwelijks. Tests hebben tot nu toe geen algehele winst gevonden: de enige variant die een reactie bij haar drempel helpt, maakt neutronvangst slechter. Daarom blijft deze laag voorlopig uit.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Kandidaat</div>
  <h3>Laag 3 · Goede data volgen (TERRA)</h3>
  <p>Waar een reactie goed gemeten is, moet de lijn de metingen volgen. De derde laag, TERRA, trekt de lijn van de motor door goede data waar die er zijn en valt terug op de motor waar ze er niet zijn.</p>
  <div class="ctl"><label for="lay-cov">Gemeten deel van het energiebereik (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} De meeste daarvan zijn binnen de steekproef: TERRA heeft die metingen gezien, net als de bibliotheken.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">In ontwikkeling</div>
  <h3>Laag 4 · Eerlijke foutmarges</h3>
  <p>De bovenste laag legt een band rond de lijn die de werkelijke waarde ongeveer twee op de drie keer zou moeten bevatten (een band van 68 %): smal waar goede data haar vastleggen, breder waar dat niet zo is.</p>
  <div class="ctl"><label for="lay-band">Bandbreedte · metingen erbinnen (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Sleep eraan en tel de metingen erbinnen. Te smal, en de band belooft een precisie die hij niet heeft; te breed, en hij zegt niets. De eigen band van de motor is nog niet aangenomen: die zit op het doel als alle reacties samen worden genomen, maar nog niet in elke reactiefamilie. TERRA heeft zijn eigen banden, en die maken deel uit van zijn vergelijkingen hierboven.</p>
</div>
<div class="step">
  <h3>Huidige stand van zaken</h3>
  <p>Een laag wordt pas aangenomen nadat ze tegenover metingen is getest, en ze blijft uit als ze niet helpt. Vandaag is de motor in gebruik en is TERRA kandidaat; de laag met gemeten structuur en de onzekerheidsband van de motor worden nog getest.</p>
  <p><a href="scoreboard.html" data-keep-lang>Bekijk het volledige scorebord →</a> Elke vergelijking die we niet winnen, elke concurrent, en hoe je het leest.</p>
  <div class="aside">${ASOF ? `Scores per ${ASOF}, uit` : "Scores uit"} het onderzoekslogboek van het project. De curven in de afbeelding zijn ter illustratie.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · motor",
  "{#} · measured structure": "{#} · gemeten structuur",
  "{#} · TERRA: anchored to data": "{#} · TERRA: verankerd aan data",
  "{#} · uncertainty band": "{#} · onzekerheidsband",
  "measured here": "hier gemeten",
  "neutron energy →": "neutronenergie →",
  "how often the reaction happens": "hoe vaak de reactie plaatsvindt",
  "hollow dots: measurements the engine is compared with": "open stippen: metingen waarmee de motor wordt vergeleken",
  "own measured values: the line barely moves": "eigen gemeten waarden: de lijn beweegt nauwelijks",
  "global rule": "globale regel",
  "no measurements: TERRA falls back to the engine": "geen metingen: TERRA valt terug op de motor",
  "solid: follows the data · dashed: the engine alone": "doorgetrokken: volgt de data · gestippeld: alleen de motor",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} van {#} metingen binnen de band (doel: ongeveer {#} %)",
  "no measurements to check the band against": "geen metingen om de band aan te toetsen",
});
Object.assign(WT.L.ui, { nav_board: "Scorebord" });
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
