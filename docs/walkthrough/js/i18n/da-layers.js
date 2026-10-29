/* Danish: layers (chapter 12). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
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
    const md = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"][+m[2] - 1];
    return md ? `${+m[3]}. ${md} ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} sejre, ${T.t} uafgjorte, ${T.l} nederlag"><div class="w"><b>${T.w}</b><span>sejr</span></div><div><b>${T.t}</b><span>uafgjort</span></div><div class="l"><b>${T.l}</b><span>nederlag</span></div></div>` : "");
  const libs = LIBS.length ? `de vigtigste evaluerede databiblioteker (${LIBS.join(", ")})` : "de vigtigste evaluerede databiblioteker";
  const engineScore = TE ? ` Ud af ${TE.d} sådanne sammenligninger ligger den klart foran i ${TE.w}, lige i ${TE.t} og bagud i ${TE.l}.` : "";
  const terraScore = TT ? `Over for ${libs} ligger den foran i ${TT.w} af ${TT.d} sammenligninger, lige i ${TT.t} og bagud i ${TT.l}.` : `Den sammenlignes med ${libs}.`;

  WT.L.ch.layers = {
    num: "Kapitel 21", title: "Hvordan modellen er bygget i lag", short: "Lag",
    lead: "Det, vi leverer, er bygget i lag oven på motoren, og hvert lag skal gøre sig fortjent til sin plads over for målinger.",
    html: `
<div class="step">
  <div class="layer-chip on">I brug</div>
  <h3>Lag 1 · Én regel for alle kerner</h3>
  <p>Den blå linje er motorens forudsigelse for én reaktion. Motoren er det nederste lag: den samme fysik og de samme globale indstillinger for alle nuklider, uden at noget er tilpasset til tværsnittene for en enkelt kerne.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Vis målingerne</button></div>
  <p>Det gør den testbar, over for målinger og over for andre modelkoder kørt på de samme kerner. Det er ikke en blindtest: de globale indstillinger blev valgt, mens vi fulgte netop disse sammenligninger.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Testet: ingen gevinst endnu</div>
  <h3>Lag 2 · Hver kernes egne målinger</h3>
  <p>Dette lag udskifter den globale regel med hver kernes egne målte værdier: dens niveauafstand D0, dens styrkefunktioner S0 og S1 (hvor let den absorberer langsomme neutroner), dens gennemsnitlige gammabredde ⟨Γγ⟩ og dens kendte energiniveauer.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Global regel</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Egne målinger</button></div>
  <p>Slå det til, og linjen flytter sig knap nok. Testene har indtil nu ikke fundet nogen samlet gevinst: den ene variant, der hjælper en reaktion nær dens tærskel, gør neutronindfangning værre. Så dette lag forbliver slået fra indtil videre.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Kandidat</div>
  <h3>Lag 3 · At følge gode data (TERRA)</h3>
  <p>Hvor en reaktion er målt godt, bør linjen følge målingerne. Det tredje lag, TERRA, trækker motorens linje gennem gode data, hvor de findes, og falder tilbage på motoren, hvor de ikke gør.</p>
  <div class="ctl"><label for="lay-cov">Andel af energiområdet, der er målt (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} De fleste af dem er in-sample: TERRA har set de målinger, ligesom bibliotekerne har.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">Under udvikling</div>
  <h3>Lag 4 · Ærlige fejlstænger</h3>
  <p>Det øverste lag lægger et bånd om linjen, som bør indeholde den sande værdi omkring to ud af tre gange (et 68 %-bånd): smalt, hvor gode data fastlægger den, bredere, hvor de ikke gør.</p>
  <div class="ctl"><label for="lay-band">Båndbredde · målinger inden for (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Træk i det, og tæl målingerne inden for båndet. For smalt, og båndet påstår en præcision, det ikke har; for bredt, og det siger ingenting. Motorens eget bånd er ikke taget i brug endnu: det rammer målet, når alle reaktioner lægges sammen, men endnu ikke i hver reaktionsfamilie. TERRA har sine egne bånd, og de indgår i sammenligningerne ovenfor.</p>
</div>
<div class="step">
  <h3>Aktuel status</h3>
  <p>Et lag tages kun i brug, efter at det er testet over for målinger, og det forbliver slået fra, når det ikke hjælper. I dag er motoren i brug, og TERRA er kandidat; laget med målt struktur og motorens usikkerhedsbånd testes stadig.</p>
  <p><a href="scoreboard.html" data-keep-lang>Se hele resultattavlen →</a> Hver sammenligning, vi ikke vinder, hver konkurrent, og hvordan du læser det.</p>
  <div class="aside">${ASOF ? `Resultater pr. ${ASOF}, fra` : "Resultater fra"} projektets forskningslog. Kurverne på billedet er illustrative.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · motor",
  "{#} · measured structure": "{#} · målt struktur",
  "{#} · TERRA: anchored to data": "{#} · TERRA: forankret i data",
  "{#} · uncertainty band": "{#} · usikkerhedsbånd",
  "measured here": "målt her",
  "neutron energy →": "neutronenergi →",
  "how often the reaction happens": "hvor ofte reaktionen sker",
  "hollow dots: measurements the engine is compared with": "hule prikker: målinger, motoren sammenlignes med",
  "own measured values: the line barely moves": "egne målte værdier: linjen flytter sig knap",
  "global rule": "global regel",
  "no measurements: TERRA falls back to the engine": "ingen målinger: TERRA falder tilbage på motoren",
  "solid: follows the data · dashed: the engine alone": "fuld: følger data · stiplet: motoren alene",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} af {#} målinger inden for båndet (mål: ca. {#} %)",
  "no measurements to check the band against": "ingen målinger at tjekke båndet op imod",
});
Object.assign(WT.L.ui, { nav_board: "Resultattavle" });
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
