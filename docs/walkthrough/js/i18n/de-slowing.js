/* German (Deutsch): slowing (Kapitel 19, Neutronenmoderation) */
/* (structure-check parity with ch/slowing.js script: data-act="${act}") */
WT.L.ch.slowing = {
  num: "Kapitel 19", title: "Neutronenmoderation", short: "Abbremsen",
  html: `
<div class="step">
  <p>Jeder Stoß an Wasserstoff kostet etwa die halbe Energie. Ein Spaltneutron startet mit 2 MeV und prallt im Wasser von Kern zu Kern. Ein Wasserstoffkern wiegt so viel wie das Neutron, daher übernimmt er wie bei Billardkugeln bei jedem Stoß im Mittel die Hälfte der Neutronenenergie.</p>
  <p>Das Diagramm zeigt die Energie des Neutrons nach jedem Stoß; jede Marke am Rand steht für tausendmal weniger Energie. Wer jedes Mal denselben Anteil verliert, rutscht auf einer Geraden hinab, der gestrichelten Linie. Nach etwa 18 Stößen erreicht das Neutron die <b>thermische</b> Energie, 0,025 eV, bei der das warme Wasser es ebenso oft beschleunigt wie abbremst. Sauerstoff ist 16-mal schwerer: Jeder Stoß nimmt nur wenig, und es braucht über hundert Stöße.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Wasserstoff</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Sauerstoff</button><button class="btn" data-act="again">Nochmal schießen</button></div>
</div>
<div class="step">
  <p>Unterhalb von etwa 1 eV prägen die Bindungen des Moleküls jeden Stoß. Jeder Wasserstoff ist an seinen Sauerstoff gebunden (die hellen Linien). Ein langsames Neutron trifft keinen freien Wasserstoff mehr, sondern ein ganzes Molekül, 18-mal schwerer, sodass ein gewöhnlicher Stoß fast nichts nimmt.</p>
  <p>Es kann das Molekül auch zum Rotieren oder Schwingen bringen, aber nur, indem es jeweils eine feste Energiemenge abgibt, 0,06, 0,2 oder 0,45 eV (die hellen Blitze). Warme Moleküle geben eine solche Menge manchmal zurück. Im Diagramm ist das schattierte Band unterhalb von 1 eV der Bereich, in dem das zählt. Schalte die Bindung aus, um mit freiem Wasserstoff zu vergleichen.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Chemische Bindung</button><button class="btn" data-act="again">Nochmal schießen</button></div>
</div>
<div class="step">
  <p>Ein Rechencode braucht all das als Tabelle: das <b>Streugesetz</b>, die Karte. Waagerecht: wie hart der Stoß ist, α (der auf das Molekül übertragene Impuls; klein bei einer streifenden Berührung, groß bei einem Frontaltreffer). Senkrecht: die Energie, die das Neutron gewinnt (oben) oder verliert (unten), β, gezählt in Einheiten der thermischen Energie des Wassers, 0,025 eV. Hell heißt wahrscheinlich, blass heißt selten.</p>
  <p>Der Umriss ist das, was ein Neutron der gewählten Energie erreichen kann: Es kann nicht mehr verlieren, als es hat, und jede Energieänderung erlaubt nur einen Bereich von Stößen. Zieh an der Energie, und der Umriss wächst oder schrumpft. Ohne Bindung ist die Karte ein freies Wasserstoffgas, ein heller Kamm entlang der gestrichelten Rückstoßlinie; mit Bindung fügt das Molekül helle Streifen hinzu, seine festen Energiemengen. INCOGNITA berechnet eigene Gesetze für Wasser und Beryllium: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Neutronenenergie (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Chemische Bindung</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "water · neutron hits hydrogen": "Wasser · Neutron trifft Wasserstoff",
  "thermal · kT ≈ {#} eV": "thermisch · kT ≈ {#} eV",
  "{#} meV": "{#} meV",
  "collisions →": "Stöße →",
  "energy": "Energie",
  "typical bounce: energy × {#} (theory × {#}) · {#} bounces to thermal": "typischer Stoß: Energie × {#} (Theorie × {#}) · {#} Stöße bis thermisch",
  "typical: the average step along the dashed line (energy shares multiply, so the average is taken on this scale)": "typisch: der mittlere Schritt entlang der gestrichelten Linie (Energieanteile multiplizieren sich, daher wird auf dieser Skala gemittelt)",
  "bright line: a bond holding H to its O": "helle Linie: eine Bindung, die H an sein O hält",
  "bright flash: the neutron left a fixed amount of energy in the molecule": "heller Blitz: das Neutron ließ eine feste Energiemenge im Molekül",
  "below {#} eV: the bonds shape each bounce": "unter {#} eV: die Bindungen prägen jeden Stoß",
  "free-atom recoil": "Rückstoß freier Atome",
  "α: how hard the knock (momentum handed over) →": "α: wie hart der Stoß (übertragener Impuls) →",
  "β: the neutron's energy change, in units of kT = {#} eV": "β: Energieänderung des Neutrons, in Einheiten von kT = {#} eV",
  "gain ↑": "Gewinn ↑",
  "loss ↓": "Verlust ↓",
  "outline: reachable from {#} eV": "Umriss: erreichbar ab {#} eV",
  "rare → likely": "selten → wahrscheinlich",
  "scattering law S(α,β) · hydrogen bound in water": "Streugesetz S(α,β) · in Wasser gebundener Wasserstoff",
  "stripes: energy lost to the molecule in fixed amounts": "Streifen: an das Molekül abgegebene Energie in festen Mengen",
});
