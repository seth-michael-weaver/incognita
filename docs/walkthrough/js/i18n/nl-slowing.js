/* Dutch (Nederlands): slowing (Hoofdstuk 18, neutronenmoderatie) */
WT.L.ch.slowing = {
  num: "Hoofdstuk 18", title: "Neutronenmoderatie", short: "Afremmen",
  html: `
<div class="step">
  <p>Elke botsing met waterstof kost ongeveer de helft van de energie. Een splijtingsneutron begint bij 2 MeV en stuitert door water. Een waterstofkern weegt evenveel als het neutron, dus, zoals biljartballen, neemt elke botsing gemiddeld de helft van de energie van het neutron mee.</p>
  <p>De grafiek zet de energie van het neutron uit na elke botsing; elk label langs de zijkant is duizend keer minder energie. Telkens hetzelfde aandeel verliezen maakt een rechte glijbaan, de stippellijn. Na ongeveer 18 botsingen bereikt het neutron de <b>thermische</b> energie, 0,025 eV, waar het warme water het net zo vaak omhoog schopt als afremt. Zuurstof is 16 keer zwaarder: elke botsing neemt maar weinig, en er zijn er meer dan honderd nodig.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Waterstof</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Zuurstof</button><button class="btn" data-act="again">Opnieuw afvuren</button></div>
</div>
<div class="step">
  <p>Onder ongeveer 1 eV bepalen de bindingen van het molecuul elke botsing. Elk waterstofatoom zit vast aan zijn zuurstof (de heldere lijnen). Een langzaam neutron raakt geen vrij waterstofatoom meer: het raakt een heel molecuul, 18 keer zwaarder, dus een gewone botsing neemt bijna niets weg.</p>
  <p>Het kan het molecuul ook laten schommelen of trillen, maar alleen door telkens een vaste hoeveelheid energie over te dragen, 0,06, 0,2 of 0,45 eV (de heldere flitsen). Warme moleculen geven zo'n hoeveelheid soms terug. In de grafiek is de gearceerde band onder 1 eV waar dit telt. Zet de binding uit om met vrij waterstof te vergelijken.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Chemische binding</button><button class="btn" data-act="again">Opnieuw afvuren</button></div>
</div>
<div class="step">
  <p>Een computercode heeft dit alles nodig als tabel: de <b>verstrooiingswet</b>, de kaart. Horizontaal: hoe hard de klap is, α (de duw die aan het molecuul wordt gegeven; klein bij een schampende aanraking, groot bij een frontale treffer). Verticaal: de energie die het neutron wint (omhoog) of verliest (omlaag), β, geteld in eenheden van de thermische energie van het water, 0,025 eV. Helder betekent waarschijnlijk, bleek betekent zeldzaam.</p>
  <p>De omtrek is wat een neutron van de gekozen energie kan bereiken: het kan niet meer verliezen dan het heeft, en elke energieverandering staat maar een bereik aan klappen toe. Sleep de energie en de omtrek groeit of krimpt. Zonder binding is de kaart vrij waterstofgas, één heldere rug langs de gestippelde terugslaglijn; met binding voegt het molecuul heldere strepen toe, zijn vaste hoeveelheden energie. INCOGNITA berekent zijn eigen wetten voor water en beryllium: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Neutronenergie (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Chemische binding</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
