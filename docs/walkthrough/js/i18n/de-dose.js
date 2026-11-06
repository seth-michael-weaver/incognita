/* German (Deutsch): dose (Strahlendosis) */
WT.L.ch.dose = {
  num: "Lektion 3", title: "Strahlendosis", short: "Dosis",
  html: `
<div class="step">
  <h3>Was ein Sievert misst</h3>
  <p>Die Dosis beginnt als Energie, die pro Kilogramm Körper aufgenommen wird. Ein <b>Sievert</b> gewichtet diese Energie dann nach dem Schaden, den sie anrichtet: Dieselbe Energie zählt bei Alphateilchen zwanzigmal mehr als bei Gammastrahlen, weil sie auf wenige dichte Spuren gepackt ist.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Gammastrahlen</button><button class="btn ghost" data-act="ra" aria-pressed="false">Alphateilchen</button></div>
</div>
<div class="step">
  <h3>Alltägliche Dosen</h3>
  <p>Jede Marke an diesem Turm ist zehnmal so groß wie die darunter. Ziehe die leuchtende Perle zum Vergleichen: Eine CT des Brustkorbs ist die Dosis vieler Tausend Bananen, ein Jahr natürlicher Untergrund die von ein paar Dutzend Flügen.</p>
  <div class="ctl"><label for="ds-l">Dosis</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Stapel dein Jahr auf</h3>
  <p>Jeder bekommt etwa 2,4 Millisievert im Jahr aus der Natur, größtenteils durch Radongas aus dem Boden. Füge deine eigenen Flüge, Untersuchungen und die Höhenlage hinzu.</p>
  <div class="ctl"><label for="ds-f">Flüge über den Atlantik</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">CT-Aufnahmen des Brustkorbs</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Höhe des Wohnorts (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Eine große Dosis auf einmal</h3>
  <p>Unter etwa 100 Millisievert ist ein zusätzliches Krebsrisiko zu klein, um es zu messen; Sicherheitsregeln nehmen an, dass es proportional zur Dosis wächst. Bei etwa einem Sievert auf einmal werden Zellen so oft getroffen, dass die Strahlenkrankheit beginnt.</p>
  <div class="ctl"><label for="ds-a">Dosis auf einmal</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Atlantic flight  ·  {#} µSv": "Atlantikflug  ·  {#} µSv",
  "CT  {#}": "CT  {#}",
  "Kerala, {#} yr  ·  {#} mSv": "Kerala, {#} Jahr  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "Ramsar, {#} Jahr  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "ein Jahr in den höchstbelasteten Häusern von Ramsar  ·  {#} mSv",
  "a year of natural background  ·  {#} mSv": "ein Jahr natürlicher Untergrund  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "ein Jahr an der Küste von Kerala (Spitzenorte)  ·  {#} mSv",
  "at once: about half die untreated  ·  {#} Sv": "auf einmal: etwa die Hälfte stirbt unbehandelt  ·  {#} Sv",
  "at once: radiation sickness begins  ·  {#} Sv": "auf einmal: Strahlenkrankheit beginnt  ·  {#} Sv",
  "average {#}": "Mittel {#}",
  "banana  ·  {#} µSv": "Banane  ·  {#} µSv",
  "cell nuclei in a patch of body": "Zellkerne in einem Stück Körper",
  "cell nuclei in a patch of body tissue": "Zellkerne in einem Stück Körpergewebe",
  "chest CT  ·  {#} mSv": "Brust-CT  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "CT des Brustkorbs  ·  {#} mSv",
  "chest X-ray  ·  {#} µSv": "Röntgenbild der Brust  ·  {#} µSv",
  "close to the world average": "nahe am Weltmittel",
  "cosmic  {#}": "kosmisch  {#}",
  "cosmic rays  {#}": "kosmische Strahlung  {#}",
  "cosmic rays at {#} m  {#}": "kosmische Strahlung auf {#} m  {#}",
  "counts as {#} millisievert": "zählt als {#} Millisievert",
  "dental X-ray  ·  {#} µSv": "Zahnröntgen  ·  {#} µSv",
  "eating a banana  ·  {#} µSv": "eine Banane essen  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "Flug über den Atlantik  ·  {#} µSv",
  "flights  {#}": "Flüge  {#}",
  "food  {#}": "Nahrung  {#}",
  "food and water  {#}": "Nahrung und Wasser  {#}",
  "ground  {#}": "Boden  {#}",
  "illustration": "Illustration",
  "lethal": "tödlich",
  "mSv": "mSv",
  "more than the yearly worker limit": "mehr als der Jahresgrenzwert für Beschäftigte",
  "no effect seen": "keine Wirkung beobachtet",
  "often lethal": "oft tödlich",
  "radon  {#}": "Radon  {#}",
  "radon in the air  {#}": "Radon in der Luft  {#}",
  "risk assumed": "Risiko angenommen",
  "rocks and soil  {#}": "Gestein und Boden  {#}",
  "same energy · counts as {#} millisieverts": "gleiche Energie · zählt als {#} Millisievert",
  "sickness": "Krankheit",
  "small added risk assumed": "kleines Zusatzrisiko angenommen",
  "tracks through each cell nucleus: about {#}": "Spuren durch jeden Zellkern: etwa {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "Spuren durch jeden Zellkern: etwa {#} (einige gezeichnet)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "Spuren durch jeden Zellkern: etwa {#} Tausend (einige gezeichnet)",
  "tracks through each cell nucleus: about {#} million (a few drawn)": "Spuren durch jeden Zellkern: etwa {#} Millionen (einige gezeichnet)",
  "typical values": "typische Werte",
  "worker limit {#}": "Grenzwert Beschäftigte {#}",
  "worker limit {#} mSv": "Grenzwert Beschäftigte {#} mSv",
  "worker limit/yr  ·  {#} mSv": "Grenzwert Beschäftigte/Jahr  ·  {#} mSv",
  "world average {#} mSv": "Weltmittel {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "Jahresgrenzwert für beruflich strahlenexponierte Personen  ·  {#} mSv",
  "your year: {#} mSv": "dein Jahr: {#} mSv",
  "{#} Sv": "{#} Sv",
  "{#} Sv at once  ·  {#} Sv": "{#} Sv auf einmal  ·  {#} Sv",
  "{#} Sv at once: about half die without treatment": "{#} Sv auf einmal: etwa die Hälfte stirbt ohne Behandlung",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "{#} Sv auf einmal: Strahlenkrankheit: Übelkeit, niedrige Blutwerte",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv: {#} Millionen Bananen oder {#} Tausend Flüge",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} Millionen Bananen, {#} Tausend Flüge oder {#} Jahre Untergrund",
  "{#} chest CT  {#}": "{#} Brust-CT  {#}",
  "{#} flights  {#}": "{#} Flüge  {#}",
  "{#} mSv": "{#} mSv",
  "{#} mSv at once: any extra risk too small to measure": "{#} mSv auf einmal: ein Zusatzrisiko ist zu klein, um es zu messen",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "{#} mSv auf einmal: keine Krankheit; Risiko steigt vermutlich mit der Dosis",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv: {#} Millionen Bananen oder {#} Tausend Flüge",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} Millionen Bananen, {#} Tausend Flüge oder {#} Jahre Untergrund",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv: {#} Tausend Bananen oder {#} Flüge",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv: {#} Tausend Bananen, {#} Flüge oder {#} Jahre Untergrund",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv: {#} Tausend Bananen oder {#} Flüge",
  "{#} µSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} µSv: {#} Tausend Bananen, {#} Flüge oder {#} Jahre Untergrund",
  "{#} milligray of alpha: a few cells hit hard": "{#} Milligray Alpha: wenige Zellen hart getroffen",
  "{#} milligray of gamma: about one track per cell": "{#} Milligray Gamma: etwa eine Spur pro Zelle",
  "{#} times the world average": "{#}-mal das Weltmittel",
  "{#} yr background  ·  {#} mSv": "{#} Jahr Untergrund  ·  {#} mSv",
  "{#} µSv": "{#} µSv",
  "{#} µSv: the dose of {#} bananas": "{#} µSv: die Dosis von {#} Bananen",
  "{#} µSv: the dose of {#} thousand bananas": "{#} µSv: die Dosis von {#} Tausend Bananen",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv: {#} Bananen oder {#} Flüge",
  "{#} µSv: {#} bananas, {#} flights or {#} years of background": "{#} µSv: {#} Bananen, {#} Flüge oder {#} Jahre Untergrund",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv: {#} Bananen oder {#} Flüge",
  "{#}–{#} Sv at once  ·  {#} Sv": "{#}–{#} Sv auf einmal  ·  {#} Sv",
});
