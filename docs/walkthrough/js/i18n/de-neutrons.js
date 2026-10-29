/* German (Deutsch): neutrons (Kapitel 5, warum Reaktoren mit Neutronen laufen) */
WT.L.ch.neutrons = {
  num: "Kapitel 5", title: "Warum Reaktoren mit Neutronen laufen", short: "Warum Neutronen",
  html: `
<div class="step">
  <p>Ein Proton ist positiv, und die 82 Protonen des Kerns sind es auch. Gleiche Ladungen stoßen sich ab, das Proton wird also weggedrückt, und die Abstoßung wächst schnell, je näher es kommt (der Pfeil). Ein langsames Proton bleibt davor stehen und kehrt um, ohne den Kern zu berühren. Erst über etwa 13 MeV überwindet es die Abstoßung; knapp darunter schlüpft es manchmal trotzdem hindurch (<b>Tunneln</b>). Das kleine Diagramm zeigt dieselbe Abstoßung als Energieberg.</p>
  <div class="ctl"><label for="wn-e1">Protonenenergie (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>Ein Neutron hat keine Ladung: Es dringt bei jeder Geschwindigkeit ein. Nichts stößt es ab, es gibt also keinen Berg zu erklimmen; es muss nur den Kern erreichen, dann zieht die starke Kraft es hinein.</p>
  <div class="ctl"><label for="wn-e2">Neutronenenergie (langsam → schnell)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>Der Regler reicht von 0,025 eV, der Geschwindigkeit eines Neutrons bei Raumtemperatur, bis 20 MeV, fast eine Milliarde Mal mehr. Selbst ganz unten dringt das Neutron noch ein.</p>
</div>
<div class="step">
  <p>Deshalb können selbst langsame Neutronen in einem Reaktor Uran spalten. Ein Uran-235-Kern, der eines verschluckt, wird zu Uran-236 mit etwas Zusatzenergie, genug, um zu wackeln, sich zu einem Hals zu strecken und in zwei Teile zu brechen. Die beiden Stücke fliegen mit etwa 200 MeV auseinander, und die zwei oder drei neuen Neutronen, die sie abgeben, können die nächsten Kerne spalten: eine Kettenreaktion.</p>
</div>`
};

Object.assign(WT.L.labels, {
  "+{#} charge: the push grows as the proton gets closer": "Ladung +{#}: die Abstoßung wächst, je näher das Proton kommt",
  "lead{#}": "Blei{#}",
  "closest approach": "größte Annäherung",
  "proton · {#} MeV": "Proton · {#} MeV",
  "energy vs distance": "Energie über Abstand",
  "hill ≈ {#} MeV": "Berg ≈ {#} MeV",
  "pushed back · about {#} in {#}³ tunnels through": "zurückgestoßen · etwa {#} von {#}³ tunnelt hindurch",
  "no charge, no push": "keine Ladung, keine Abstoßung",
  "neutron · {#} eV": "Neutron · {#} eV",
  "even this crawling neutron gets in": "selbst dieses kriechende Neutron dringt ein",
  "≈ {#} MeV released": "≈ {#} MeV frei",
  "two fragments + {#} new neutrons": "zwei Bruchstücke + {#} neue Neutronen",
  "a slow neutron + U{#} → two fragments, {#}–{#} new neutrons, about {#} MeV": "langsames Neutron + U{#} → zwei Bruchstücke, {#}–{#} neue Neutronen, etwa {#} MeV",
  "a proton this slow could never get in": "ein so langsames Proton käme nie hinein",
});
