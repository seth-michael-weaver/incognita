/* Dutch (Nederlands): rays (Alfa, bèta, gamma en neutronen) */
WT.L.ch.rays = {
  num: "Les 2", title: "Alfa, bèta, gamma en neutronen", short: "Straling",
  html: `
<div class="step">
  <h3>Vier soorten straling</h3>
  <p><em class="a">Alfa</em> is een zwaar klompje van twee protonen en twee neutronen. <b>Bèta</b> is een snel elektron. <em class="g">Gamma</em> is licht, veel te energierijk om te zien. <em class="n">Neutronen</em> hebben helemaal geen lading. Elk wordt door iets anders tegengehouden.</p>
</div>
<div class="step">
  <h3>Papier en aluminium</h3>
  <p>Alfadeeltjes zijn groot en geladen, dus botsen ze meteen op atomen: een vel papier houdt ze tegen. Bèta-elektronen komen verder, maar een paar millimeter aluminium houdt ook hen tegen.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Papier</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Aluminium</button></div>
</div>
<div class="step">
  <h3>Gammastraling: gehalveerd, nooit nul</h3>
  <p>Gammastraling heeft geen lading en gaat meestal langs atomen heen. Elke centimeter lood geeft elk foton dezelfde kans om gevangen te worden, dus halveert elke laag wat er over is. De bundel zwakt af maar bereikt nooit helemaal nul.</p>
  <div class="ctl"><label for="ry-pb">Lood (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Neutronen: lood is niet genoeg</h3>
  <p>Een neutron dat op een zware loodkern botst, is als een pingpongbal tegen een bowlingbal: hij houdt zijn snelheid. Waterstof in water weegt evenveel als een neutron, dus elke botsing remt het af, tot het traag genoeg is om opgeslokt te worden.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Lood</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Water</button></div>
  <div class="ctl"><label for="ry-nx">Dikte (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Bouw een afscherming</h3>
  <p>Stapel lagen tot alle vier de bundels gestopt zijn. Gammastraling zakt nooit tot precies nul, alleen tot een piepklein deel.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Papier</button><button class="btn ghost" data-act="add_al">+ Aluminium</button><button class="btn ghost" data-act="add_pb">+ Lood</button><button class="btn ghost" data-act="add_water">+ Water</button><button class="btn" data-act="clear">Wissen</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Al {#} mm": "Al {#} mm",
  "all four beams stopped": "alle vier de bundels gestopt",
  "all four stopped": "alle vier gestopt",
  "all through": "alles erdoor",
  "alpha": "alfa",
  "aluminium {#} mm": "aluminium {#} mm",
  "beta": "bèta",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "helder = snel neutron · rood = weggestoten waterstofkern · groene flits = opgeslokt",
  "bright = fast · dim = slowed": "helder = snel · dof = afgeremd",
  "cm of lead": "cm lood",
  "counted: {#} of {#}": "geteld: {#} van {#}",
  "drag ↔": "sleep ↔",
  "each source fires a steady beam": "elke bron zendt een constante bundel uit",
  "flash = stopped": "flits = gestopt",
  "flash = stopped inside the shield": "flits = gestopt in de afscherming",
  "four beams": "vier bundels",
  "gamma": "gamma",
  "gamma rays (caesium{#})": "gammastraling (cesium{#})",
  "gets through: {#} % · halved every {#} mm of lead": "komt erdoor: {#} % · gehalveerd per {#} mm lood",
  "gets through: {#} in {#} · halved every {#} mm of lead": "komt erdoor: {#} op {#} · gehalveerd per {#} mm lood",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "komt erdoor: {#} op {#} miljoen · gehalveerd per {#} mm lood",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "erdoor {#} % · teruggekaatst {#} % · afgeremd en gevangen {#} %",
  "lead {#} cm": "lood {#} cm",
  "neutron": "neutron",
  "no shield": "geen afscherming",
  "not to scale": "niet op schaal",
  "paper": "papier",
  "share still going": "deel nog onderweg",
  "simplified model": "vereenvoudigd model",
  "stopped": "gestopt",
  "through {#} % · back {#} % · caught {#} %": "erdoor {#} % · terug {#} % · gevangen {#} %",
  "through: all · halved every {#} mm": "erdoor: alles · gehalveerd per {#} mm",
  "through: {#} % · halved every {#} mm": "erdoor: {#} % · gehalveerd per {#} mm",
  "through: {#} in {#} · halved every {#} mm": "erdoor: {#} op {#} · gehalveerd per {#} mm",
  "water {#} cm": "water {#} cm",
  "{#} % through": "{#} % erdoor",
  "{#} in {#}": "{#} op {#}",
  "{#} in {#} million": "{#} op {#} miljoen",
  "{#} in a billion": "{#} op een miljard",
});
