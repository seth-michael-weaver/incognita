/* Danish: dose (Stråledosis) */
WT.L.ch.dose = {
  num: "Lektion 3", title: "Stråledosis", short: "Dosis",
  html: `
<div class="step">
  <h3>Hvad en sievert måler</h3>
  <p>Dosis begynder som energi optaget pr. kilogram krop. En <b>sievert</b> vægter så den energi efter den skade, den gør: den samme energi afsat af alfapartikler tæller tyve gange mere end af gammastråler, fordi den er pakket i nogle få tætte spor.</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">Gammastråler</button><button class="btn ghost" data-act="ra" aria-pressed="false">Alfapartikler</button></div>
</div>
<div class="step">
  <h3>Hverdagsdoser</h3>
  <p>Hvert mærke op ad dette tårn er ti gange det nedenunder. Træk den glødende perle for at sammenligne: en CT-scanning af brystet er dosis fra mange tusind bananer, et års naturlig baggrund fra et par dusin flyrejser.</p>
  <div class="ctl"><label for="ds-l">Dosis</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>Stabl dit år op</h3>
  <p>Alle får omkring 2,4 millisievert om året fra naturen, mest radongas fra jorden. Læg dine egne flyrejser, scanninger og højde oven i.</p>
  <div class="ctl"><label for="ds-f">Flyrejser over Atlanten</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">CT-scanninger af brystet</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">Boligens højde (m)</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>En stor dosis på én gang</h3>
  <p>Under omkring 100 millisievert er en ekstra kræftrisiko for lille til at måle; sikkerhedsregler antager, at den vokser proportionalt med dosis. Omkring én sievert på én gang rammes cellerne så ofte, at strålesyge begynder.</p>
  <div class="ctl"><label for="ds-a">Dosis på én gang</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Atlantic flight  ·  {#} µSv": "flyrejse over Atlanten  ·  {#} µSv",
  "CT  {#}": "CT  {#}",
  "Kerala, {#} yr  ·  {#} mSv": "Kerala, {#} år  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "Ramsar, {#} år  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "et år i de højeste huse i Ramsar  ·  {#} mSv",
  "a year of natural background  ·  {#} mSv": "et års naturlig baggrund  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "et år på Keralas kyst (høje steder)  ·  {#} mSv",
  "at once: about half die untreated  ·  {#} Sv": "på én gang: omkring halvdelen dør ubehandlet  ·  {#} Sv",
  "at once: radiation sickness begins  ·  {#} Sv": "på én gang: strålesyge begynder  ·  {#} Sv",
  "average {#}": "gennemsnit {#}",
  "banana  ·  {#} µSv": "banan  ·  {#} µSv",
  "cell nuclei in a patch of body": "cellekerner i et stykke krop",
  "cell nuclei in a patch of body tissue": "cellekerner i et stykke kropsvæv",
  "chest CT  ·  {#} mSv": "CT af brystet  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "CT-scanning af brystet  ·  {#} mSv",
  "chest X-ray  ·  {#} µSv": "røntgen af brystet  ·  {#} µSv",
  "close to the world average": "tæt på verdensgennemsnittet",
  "cosmic  {#}": "kosmisk  {#}",
  "cosmic rays  {#}": "kosmisk stråling  {#}",
  "cosmic rays at {#} m  {#}": "kosmisk stråling i {#} m  {#}",
  "counts as {#} millisievert": "tæller som {#} millisievert",
  "dental X-ray  ·  {#} µSv": "tandrøntgen  ·  {#} µSv",
  "eating a banana  ·  {#} µSv": "at spise en banan  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "flyrejse over Atlanten  ·  {#} µSv",
  "flights  {#}": "flyrejser  {#}",
  "food  {#}": "mad  {#}",
  "food and water  {#}": "mad og vand  {#}",
  "ground  {#}": "jord  {#}",
  "illustration": "illustration",
  "lethal": "dødelig",
  "mSv": "mSv",
  "more than the yearly worker limit": "mere end den årlige grænse for arbejdstagere",
  "no effect seen": "ingen effekt set",
  "often lethal": "ofte dødelig",
  "radon  {#}": "radon  {#}",
  "radon in the air  {#}": "radon i luften  {#}",
  "risk assumed": "risiko antaget",
  "rocks and soil  {#}": "sten og jord  {#}",
  "same energy · counts as {#} millisieverts": "samme energi · tæller som {#} millisievert",
  "sickness": "syge",
  "small added risk assumed": "lille ekstra risiko antaget",
  "tracks through each cell nucleus: about {#}": "spor gennem hver cellekerne: omkring {#}",
  "tracks through each cell nucleus: about {#} (a few drawn)": "spor gennem hver cellekerne: omkring {#} (nogle få tegnet)",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "spor gennem hver cellekerne: omkring {#} tusind (nogle få tegnet)",
  "tracks through each cell nucleus: about {#} million (a few drawn)": "spor gennem hver cellekerne: omkring {#} millioner (nogle få tegnet)",
  "typical values": "typiske værdier",
  "worker limit {#}": "grænse for arbejdstagere {#}",
  "worker limit {#} mSv": "grænse for arbejdstagere {#} mSv",
  "worker limit/yr  ·  {#} mSv": "grænse for arbejdstagere/år  ·  {#} mSv",
  "world average {#} mSv": "verdensgennemsnit {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "årlig grænse for strålingsarbejdere  ·  {#} mSv",
  "your year: {#} mSv": "dit år: {#} mSv",
  "{#} Sv": "{#} Sv",
  "{#} Sv at once  ·  {#} Sv": "{#} Sv på én gang  ·  {#} Sv",
  "{#} Sv at once: about half die without treatment": "{#} Sv på én gang: omkring halvdelen dør uden behandling",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "{#} Sv på én gang: strålesyge: kvalme, lave blodtal",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv: {#} millioner bananer eller {#} tusind flyrejser",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv: {#} millioner bananer, {#} tusind flyrejser eller {#} års baggrund",
  "{#} chest CT  {#}": "{#} CT af brystet  {#}",
  "{#} flights  {#}": "{#} flyrejser  {#}",
  "{#} mSv": "{#} mSv",
  "{#} mSv at once: any extra risk too small to measure": "{#} mSv på én gang: en ekstra risiko er for lille til at måle",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "{#} mSv på én gang: ingen sygdom; risikoen antages at stige med dosis",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv: {#} millioner bananer eller {#} tusind flyrejser",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv: {#} millioner bananer, {#} tusind flyrejser eller {#} års baggrund",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv: {#} tusind bananer eller {#} flyrejser",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv: {#} tusind bananer, {#} flyrejser eller {#} års baggrund",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv: {#} tusind bananer eller {#} flyrejser",
  "{#} µSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} µSv: {#} tusind bananer, {#} flyrejser eller {#} års baggrund",
  "{#} milligray of alpha: a few cells hit hard": "{#} milligray alfa: nogle få celler ramt hårdt",
  "{#} milligray of gamma: about one track per cell": "{#} milligray gamma: omkring ét spor pr. celle",
  "{#} times the world average": "{#} gange verdensgennemsnittet",
  "{#} yr background  ·  {#} mSv": "{#} års baggrund  ·  {#} mSv",
  "{#} µSv": "{#} µSv",
  "{#} µSv: the dose of {#} bananas": "{#} µSv: dosis fra {#} bananer",
  "{#} µSv: the dose of {#} thousand bananas": "{#} µSv: dosis fra {#} tusind bananer",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv: {#} bananer eller {#} flyrejser",
  "{#} µSv: {#} bananas, {#} flights or {#} years of background": "{#} µSv: {#} bananer, {#} flyrejser eller {#} års baggrund",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv: {#} bananer eller {#} flyrejser",
  "{#}–{#} Sv at once  ·  {#} Sv": "{#}–{#} Sv på én gang  ·  {#} Sv",
});
