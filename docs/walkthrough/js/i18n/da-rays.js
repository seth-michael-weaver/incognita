/* Danish: rays (Alfa, beta, gamma og neutroner) */
WT.L.ch.rays = {
  num: "Lektion 2", title: "Alfa, beta, gamma og neutroner", short: "Stråling",
  html: `
<div class="step">
  <h3>Fire slags stråling</h3>
  <p><em class="a">Alfa</em> er en tung klump af to protoner og to neutroner. <b>Beta</b> er en hurtig elektron. <em class="g">Gamma</em> er lys, alt for energirigt til at se. <em class="n">Neutroner</em> har slet ingen ladning. Hver af dem standses af noget forskelligt.</p>
</div>
<div class="step">
  <h3>Papir og aluminium</h3>
  <p>Alfapartikler er store og ladede, så de støder straks ind i atomer: et ark papir standser dem. Beta-elektroner når længere, men nogle få millimeter aluminium standser også dem.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Papir</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Aluminium</button></div>
</div>
<div class="step">
  <h3>Gammastråler: halveret, aldrig nul</h3>
  <p>Gammastråler har ingen ladning og passerer som regel atomerne. Hver centimeter bly giver hver eneste den samme chance for at blive fanget, så hvert lag halverer det, der er tilbage. Strålen svækkes, men når aldrig helt nul.</p>
  <div class="ctl"><label for="ry-pb">Bly (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Neutroner: bly er ikke nok</h3>
  <p>En neutron, der preller af en tung blykerne, er som en bordtennisbold, der rammer en bowlingkugle: den beholder sin fart. Brint i vand vejer det samme som en neutron, så hvert stød bremser den, indtil den er langsom nok til at blive slugt.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Bly</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Vand</button></div>
  <div class="ctl"><label for="ry-nx">Tykkelse (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Byg en afskærmning</h3>
  <p>Stabl lag, indtil alle fire stråler er standset. Gammastråler falder aldrig til præcis nul, kun til en bitte lille andel.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Papir</button><button class="btn ghost" data-act="add_al">+ Aluminium</button><button class="btn ghost" data-act="add_pb">+ Bly</button><button class="btn ghost" data-act="add_water">+ Vand</button><button class="btn" data-act="clear">Ryd</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Al {#} mm": "Al {#} mm",
  "all four beams stopped": "alle fire stråler standset",
  "all four stopped": "alle fire standset",
  "all through": "alt igennem",
  "alpha": "alfa",
  "aluminium {#} mm": "aluminium {#} mm",
  "beta": "beta",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "lys = hurtig neutron · rød = bortslået brintkerne · grønt glimt = slugt",
  "bright = fast · dim = slowed": "lys = hurtig · mat = bremset",
  "cm of lead": "cm bly",
  "counted: {#} of {#}": "talt: {#} af {#}",
  "drag ↔": "træk ↔",
  "each source fires a steady beam": "hver kilde sender en jævn stråle",
  "flash = stopped": "glimt = standset",
  "flash = stopped inside the shield": "glimt = standset i afskærmningen",
  "four beams": "fire stråler",
  "gamma": "gamma",
  "gamma rays (caesium{#})": "gammastråler (cæsium{#})",
  "gets through: {#} % · halved every {#} mm of lead": "slipper igennem: {#} % · halveret for hver {#} mm bly",
  "gets through: {#} in {#} · halved every {#} mm of lead": "slipper igennem: {#} ud af {#} · halveret for hver {#} mm bly",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "slipper igennem: {#} ud af {#} millioner · halveret for hver {#} mm bly",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "kom igennem {#} % · kastet tilbage {#} % · bremset og fanget {#} %",
  "lead {#} cm": "bly {#} cm",
  "neutron": "neutron",
  "no shield": "ingen afskærmning",
  "not to scale": "ikke målfast",
  "paper": "papir",
  "share still going": "andel stadig på vej",
  "simplified model": "forenklet model",
  "stopped": "standset",
  "through {#} % · back {#} % · caught {#} %": "igennem {#} % · tilbage {#} % · fanget {#} %",
  "through: all · halved every {#} mm": "igennem: alt · halveret for hver {#} mm",
  "through: {#} % · halved every {#} mm": "igennem: {#} % · halveret for hver {#} mm",
  "through: {#} in {#} · halved every {#} mm": "igennem: {#} ud af {#} · halveret for hver {#} mm",
  "water {#} cm": "vand {#} cm",
  "{#} % through": "{#} % igennem",
  "{#} in {#}": "{#} ud af {#}",
  "{#} in {#} million": "{#} ud af {#} millioner",
  "{#} in a billion": "{#} ud af en milliard",
});
