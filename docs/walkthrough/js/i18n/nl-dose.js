/* Dutch (Nederlands): dose (Stralingsdosis) */
WT.L.ch.dose = {
  num: "Les 3", title: "Stralingsdosis", short: "Dosis",
  html: `
<div class="step">
  <h3>Wat een sievert meet</h3>
  <p>Dosis begint als energie die per kilogram lichaam wordt opgenomen. Een <b>sievert</b> weegt die energie vervolgens naar de schade die ze aanricht: dezelfde energie telt bij alfadeeltjes twintig keer zwaarder dan bij gammastraling, omdat ze in een paar dichte sporen is gepakt.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Gammastraling</button><button class="btn ghost" data-act="ra" aria-pressed="false">Alfadeeltjes</button></div>
</div>
<div class="step">
  <h3>Alledaagse doses</h3>
  <p>Elk streepje op deze toren is tien keer het streepje eronder. Sleep het gloeiende kraaltje om te vergelijken: een CT-scan van de borst is de dosis van vele duizenden bananen, een jaar natuurlijke achtergrond die van een paar dozijn vluchten.</p>
  <div class="ctl"><label for="ds-l">Dosis</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Stapel je jaar op</h3>
  <p>Iedereen krijgt ongeveer 2,4 millisievert per jaar uit de natuur, vooral radongas uit de bodem. Tel je eigen vluchten, scans en hoogte erbij op.</p>
  <div class="ctl"><label for="ds-f">Vluchten over de Atlantische Oceaan</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">CT-scans van de borst</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Hoogte van je woonplaats (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Een grote dosis in één keer</h3>
  <p>Onder ongeveer 100 millisievert is een extra kankerrisico te klein om te meten; veiligheidsregels nemen aan dat het evenredig met de dosis groeit. Rond één sievert in één keer worden cellen zo vaak geraakt dat stralingsziekte begint.</p>
  <div class="ctl"><label for="ds-a">Dosis in één keer</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Atlantic flight  ·  {#} µSv": "trans-Atlantische vlucht  ·  {#} µSv",
  "CT  {#}": "CT  {#}",
  "Kerala, {#} yr  ·  {#} mSv": "Kerala, {#} jr  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "Ramsar, {#} jr  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "een jaar in de hoogste huizen van Ramsar  ·  {#} mSv",
  "a year of natural background  ·  {#} mSv": "een jaar natuurlijke achtergrond  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "een jaar aan de kust van Kerala (hoge plekken)  ·  {#} mSv",
  "at once: about half die untreated  ·  {#} Sv": "in één keer: ongeveer de helft sterft onbehandeld  ·  {#} Sv",
  "at once: radiation sickness begins  ·  {#} Sv": "in één keer: stralingsziekte begint  ·  {#} Sv",
  "average {#}": "gemiddeld {#}",
  "banana  ·  {#} µSv": "banaan  ·  {#} µSv",
  "cell nuclei in a patch of body": "celkernen in een stukje lichaam",
  "cell nuclei in a patch of body tissue": "celkernen in een stukje lichaamsweefsel",
  "chest CT  ·  {#} mSv": "CT borst  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "CT-scan van de borst  ·  {#} mSv",
  "chest X-ray  ·  {#} µSv": "röntgenfoto borst  ·  {#} µSv",
  "close to the world average": "dicht bij het wereldgemiddelde",
  "cosmic  {#}": "kosmisch  {#}",
  "cosmic rays  {#}": "kosmische straling  {#}",
  "cosmic rays at {#} m  {#}": "kosmische straling op {#} m  {#}",
  "counts as {#} millisievert": "telt als {#} millisievert",
  "dental X-ray  ·  {#} µSv": "tandfoto  ·  {#} µSv",
  "eating a banana  ·  {#} µSv": "een banaan eten  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "vlucht over de Atlantische Oceaan  ·  {#} µSv",
  "flights  {#}": "vluchten  {#}",
  "food  {#}": "voedsel  {#}",
  "food and water  {#}": "voedsel en water  {#}",
  "ground  {#}": "bodem  {#}",
  "illustration": "illustratie",
  "lethal": "dodelijk",
  "mSv": "mSv",
  "more than the yearly worker limit": "meer dan de jaarlimiet voor werknemers",
  "no effect seen": "geen effect gezien",
  "often lethal": "vaak dodelijk",
  "radon  {#}": "radon  {#}",
  "radon in the air  {#}": "radon in de lucht  {#}",
  "risk assumed": "risico aangenomen",
  "rocks and soil  {#}": "gesteente en bodem  {#}",
  "same energy · counts as {#} millisieverts": "zelfde energie · telt als {#} millisievert",
  "sickness": "ziekte",
  "small added risk assumed": "klein extra risico aangenomen",
  "tracks through each cell nucleus: about {#}": "sporen door elke celkern: ongeveer {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "sporen door elke celkern: ongeveer {#} (enkele getekend)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "sporen door elke celkern: ongeveer {#} duizend (enkele getekend)",
  "tracks through each cell nucleus: about {#} million (a few drawn)": "sporen door elke celkern: ongeveer {#} miljoen (enkele getekend)",
  "typical values": "typische waarden",
  "worker limit {#}": "limiet werknemers {#}",
  "worker limit {#} mSv": "limiet werknemers {#} mSv",
  "worker limit/yr  ·  {#} mSv": "limiet werknemers/jr  ·  {#} mSv",
  "world average {#} mSv": "wereldgemiddelde {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "jaarlimiet voor stralingswerkers  ·  {#} mSv",
  "your year: {#} mSv": "jouw jaar: {#} mSv",
  "{#} Sv": "{#} Sv",
  "{#} Sv at once  ·  {#} Sv": "{#} Sv in één keer  ·  {#} Sv",
  "{#} Sv at once: about half die without treatment": "{#} Sv in één keer: ongeveer de helft sterft zonder behandeling",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "{#} Sv in één keer: stralingsziekte: misselijkheid, lage bloedwaarden",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv: {#} miljoen bananen, of {#} duizend vluchten",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} miljoen bananen, {#} duizend vluchten of {#} jaar achtergrond",
  "{#} chest CT  {#}": "{#} CT borst  {#}",
  "{#} flights  {#}": "{#} vluchten  {#}",
  "{#} mSv": "{#} mSv",
  "{#} mSv at once: any extra risk too small to measure": "{#} mSv in één keer: een extra risico is te klein om te meten",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "{#} mSv in één keer: geen ziekte; risico verondersteld te stijgen met de dosis",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv: {#} miljoen bananen, of {#} duizend vluchten",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} miljoen bananen, {#} duizend vluchten of {#} jaar achtergrond",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv: {#} duizend bananen, of {#} vluchten",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv: {#} duizend bananen, {#} vluchten of {#} jaar achtergrond",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv: {#} duizend bananen, of {#} vluchten",
  "{#} µSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} µSv: {#} duizend bananen, {#} vluchten of {#} jaar achtergrond",
  "{#} milligray of alpha: a few cells hit hard": "{#} milligray alfa: een paar cellen hard geraakt",
  "{#} milligray of gamma: about one track per cell": "{#} milligray gamma: ongeveer één spoor per cel",
  "{#} times the world average": "{#} keer het wereldgemiddelde",
  "{#} yr background  ·  {#} mSv": "{#} jr achtergrond  ·  {#} mSv",
  "{#} µSv": "{#} µSv",
  "{#} µSv: the dose of {#} bananas": "{#} µSv: de dosis van {#} bananen",
  "{#} µSv: the dose of {#} thousand bananas": "{#} µSv: de dosis van {#} duizend bananen",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv: {#} bananen, of {#} vluchten",
  "{#} µSv: {#} bananas, {#} flights or {#} years of background": "{#} µSv: {#} bananen, {#} vluchten of {#} jaar achtergrond",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv: {#} bananen, of {#} vluchten",
  "{#}–{#} Sv at once  ·  {#} Sv": "{#}–{#} Sv in één keer  ·  {#} Sv",
});
