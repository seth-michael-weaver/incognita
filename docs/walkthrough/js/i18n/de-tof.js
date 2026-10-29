/* German (Deutsch): tof (Kapitel 17, Flugzeitmessungen) */
WT.L.ch.tof = {
  num: "Kapitel 17", title: "Flugzeitmessungen", short: "Peaks messen",
  html: `
<div class="step">
  <p>Die Flugzeit eines Neutrons verrät seine Energie. Ein kurzer Puls von Neutronen mit allen möglichen Energien verlässt die Quelle und rast durch ein leeres Rohr zum Detektor; die schnellen kommen zuerst an. Die Länge <i>L</i> des Rohrs ist bekannt, also liefert jede Ankunftszeit <i>t</i> die Geschwindigkeit des Neutrons, und die Geschwindigkeit liefert seine Energie:</p>
  <div class="formula">E = (72,3 · L / t)²   (E in eV, L in Metern, t in Mikrosekunden)</div>
  <p>Die Uhr über dem Rohr zählt die echte Zeit seit dem Puls; der Flug ist etwa 1400-mal langsamer gezeichnet. Unter dem Rohr wird die letzte Ankunft in eine Energie umgerechnet. Ziehen Sie an der Flugstrecke: Ein längeres Rohr streckt dieselben Energien über eine längere Zeit, sodass sich jede feiner unterscheiden lässt.</p>
  <div class="ctl"><label for="tof-l1">Flugstrecke (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Dünne Probe: Der Einbruch zeichnet den Wirkungsquerschnitt nach. Nun steht eine Probe im Strahl. Bei etwa 6,7 eV haben ihre Kerne eine Resonanz und fangen Neutronen ein (die Blitze), sodass zur passenden Zeit weniger ankommen. Das Diagramm vergleicht die Zählraten mit und ohne Probe: die <b>Transmission</b>, die 1 ist, wenn jedes Neutron hindurchkommt.</p>
  <p>Die Punkte sind simulierte Zählungen mit ihrer Streuung; die durchgezogene Linie ist das, was der Detektor im Mittel aufzeichnet; die gestrichelte Linie ist die Form des Wirkungsquerschnitts selbst. Bei einer dünnen Probe kopiert der Einbruch diese Form.</p>
  <div class="ctl"><label for="tof-d1">Probendicke (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Dicke Probe: Der Einbruch sättigt. Bei der Peakenergie fängt die Vorderseite der Probe jedes Neutron ein, das Zentrum wird also schwarz und bleibt es, so dick Sie die Probe auch machen; der Einbruch kann nur wachsen, indem er sich zu den Flanken hin verbreitert. Das ist die <b>Selbstabschirmung</b>: Die vorderen Schichten schirmen die hinteren ab. Eine dicke Probe verrät daher mehr über die Flügel der Resonanz als über ihren Peak.</p>
  <div class="ctl"><label for="tof-d2">Probendicke (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Längere Pulse, kürzere Flugstrecken: Der Einbruch verschwimmt. Drei Dinge bestimmen die Breite eines Einbruchs, alle unter dem Diagramm angegeben: die Eigenbreite der Resonanz; die Wärmebewegung der Probenatome, die die Energie jedes Stoßes etwas verschmiert (<b>Doppler</b>-Verbreiterung); und die Zeitunschärfe, denn ein längerer Puls oder ein kürzeres Rohr macht jede Ankunftszeit und damit jede Energie unsicherer.</p>
  <p>Verlängern Sie den Puls oder verkürzen Sie das Rohr: Der Einbruch wird breiter und flacher, obwohl der Anteil der entfernten Neutronen etwa gleich bleibt.</p>
  <div class="ctl"><label for="tof-p1">Pulsbreite (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Flugstrecke (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA arbeitet rückwärts: Es nimmt gemessene Zählraten wie diese und fragt, welche Resonanz, durch denselben Versuch geschickt (Dicke, Wärme, Zeitunschärfe), sie reproduziert. Hier startet die Anpassung bei einem Schätzwert, dessen Neutronenbreite Γ<sub>n</sub> (wie fest das Niveau Neutronen hält) fast viermal zu groß ist (die blaue Kurve), und ändert ihn Schritt für Schritt, bis die Kurve durch die Punkte läuft.</p>
  <p>Die Anzeige zeigt den aktuellen Schätzwert und die <b>Fehlanpassung</b>: Etwa 1 bedeutet, dass die Kurve den Punkten so nahe kommt, wie ihre Zählstreuung erlaubt. Ändern Sie den Versuch, und die Anpassung beginnt von vorn, mit neuen Zählungen, und landet nahe bei derselben Breite; wo sie die Punkte nicht gut trifft, sagt die Fehlanpassung es.</p>
  <div class="ctl"><label for="tof-l3">Flugstrecke (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Probendicke (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Pulsbreite (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
