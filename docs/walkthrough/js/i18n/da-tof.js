/* Danish: tof (Kapitel 16, flyvetidsmålinger) */
WT.L.ch.tof = {
  num: "Kapitel 16", title: "Flyvetidsmålinger", short: "Måling af toppe",
  html: `
<div class="step">
  <p>En neutrons flyvetid afslører dens energi. Et kort pulsudbrud af neutroner med alle slags energier forlader kilden og suser ned ad et tomt rør til detektoren; de hurtige ankommer først. Rørets længde <i>L</i> er kendt, så hvert ankomsttidspunkt <i>t</i> giver neutronens hastighed, og hastigheden giver dens energi:</p>
  <div class="formula">E = (72,3 · L / t)²   (E i eV, L i meter, t i mikrosekunder)</div>
  <p>Uret over røret tæller den virkelige tid siden pulsen; flyvningen er tegnet omkring 1400 gange langsommere. Under røret omregnes den seneste ankomst til en energi. Træk i flyvevejen: et længere rør spreder de samme energier over længere tid, så hver kan skelnes mere præcist.</p>
  <div class="ctl"><label for="tof-l1">Flyvevej (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Tynd prøve: dyket følger tværsnittet. Nu står en prøve i strålen. Nær 6,7 eV har dens kerner en resonans og snupper neutroner (glimtene), så færre ankommer på det tilsvarende tidspunkt. Grafen sammenligner tællingerne med og uden prøven: <b>transmissionen</b>, 1 når alle neutroner kommer igennem.</p>
  <p>Prikkerne er simulerede tællinger med deres spredning; den fuldt optrukne linje er det, detektoren i gennemsnit registrerer; den stiplede linje er selve tværsnittets form. Med en tynd prøve kopierer dyket den form.</p>
  <div class="ctl"><label for="tof-d1">Prøvetykkelse (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Tyk prøve: dyket mætter. Ved topenergien fanger prøvens forside hver eneste neutron, så midten bliver sort og forbliver sort, uanset hvor tyk du gør prøven; dyket kan kun vokse ved at brede sig ud til siderne. Dette er <b>selvafskærmning</b>: de forreste lag afskærmer de bageste. En tyk prøve fortæller så mere om resonansens flanker end om dens top.</p>
  <div class="ctl"><label for="tof-d2">Prøvetykkelse (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Længere pulser, kortere flyvning: dyket udviskes. Tre ting afgør et dyks bredde, alle skrevet under grafen: resonansens egen bredde; prøvens atomer, der vibrerer af varme, hvilket udtværer hver kollisions energi en smule (<b>Doppler</b>-udvidelse); og tidsudtværingen, fordi en længere puls eller et kortere rør gør hvert ankomsttidspunkt, og dermed hver energi, mindre sikker.</p>
  <p>Forlæng pulsen eller forkort røret: dyket bliver bredere og lavere, selvom den andel af neutroner, det fjerner, forbliver omtrent den samme.</p>
  <div class="ctl"><label for="tof-p1">Pulsbredde (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Flyvevej (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA arbejder baglæns: den tager målte tællinger som disse og spørger, hvilken resonans, sendt gennem præcis dette eksperiment (tykkelse, varme, tidsudtværing), der gengiver dem. Her starter tilpasningen fra et gæt, hvis neutronbredde Γ<sub>n</sub> (hvor stærkt niveauet holder fast i neutroner) er næsten fire gange for stor (den blå kurve), og ændrer den trin for trin, til kurven løber gennem prikkerne.</p>
  <p>Aflæsningen viser det aktuelle gæt og <b>misfittet</b>: omkring 1 betyder, at kurven ligger så tæt på prikkerne, som deres tællespredning tillader. Ændrer du eksperimentet, starter tilpasningen forfra med nye tællinger og lander tæt på den samme bredde; hvor den ikke kan ramme prikkerne godt, siger misfittet det.</p>
  <div class="ctl"><label for="tof-l3">Flyvevej (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Prøvetykkelse (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Pulsbredde (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>
`,
};
