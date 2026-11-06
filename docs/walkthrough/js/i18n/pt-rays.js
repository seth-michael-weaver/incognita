/* Portuguese (pt-PT): rays (Alfa, beta, gama e neutrões) */
WT.L.ch.rays = {
  num: "Lição 2", title: "Alfa, beta, gama e neutrões", short: "Radiação",
  html: `
<div class="step">
  <h3>Quatro tipos de radiação</h3>
  <p>A radiação <em class="a">alfa</em> é um aglomerado pesado de dois protões e dois neutrões. A <b>beta</b> é um eletrão rápido. A <em class="g">gama</em> é luz, com energia demasiado alta para se ver. Os <em class="n">neutrões</em> não têm carga nenhuma. Cada uma é travada por coisas diferentes.</p>
</div>
<div class="step">
  <h3>Papel e alumínio</h3>
  <p>As partículas alfa são grandes e têm carga, por isso chocam logo com os átomos: uma folha de papel trava-as. Os eletrões beta vão mais longe, mas alguns milímetros de alumínio também os travam.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Papel</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Alumínio</button></div>
</div>
<div class="step">
  <h3>Raios gama: reduzidos a metade, nunca a zero</h3>
  <p>Os raios gama não têm carga e normalmente passam ao lado dos átomos. Cada centímetro de chumbo dá a cada um a mesma hipótese de ser apanhado, por isso cada fatia reduz a metade o que resta. O feixe vai enfraquecendo, mas nunca chega bem a zero.</p>
  <div class="ctl"><label for="ry-pb">Chumbo (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Neutrões: o chumbo não chega</h3>
  <p>Um neutrão a ressaltar num pesado núcleo de chumbo é uma bola de pingue-pongue a bater numa bola de bowling: mantém a velocidade. O hidrogénio da água pesa o mesmo que um neutrão, por isso cada choque abranda-o, até ficar lento o suficiente para ser absorvido.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Chumbo</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Água</button></div>
  <div class="ctl"><label for="ry-nx">Espessura (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Constrói uma blindagem</h3>
  <p>Empilha camadas até os quatro feixes ficarem travados. Os raios gama nunca descem exatamente a zero, apenas a uma fração minúscula.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Papel</button><button class="btn ghost" data-act="add_al">+ Alumínio</button><button class="btn ghost" data-act="add_pb">+ Chumbo</button><button class="btn ghost" data-act="add_water">+ Água</button><button class="btn" data-act="clear">Limpar</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "alpha": "alfa",
  "beta": "beta",
  "gamma": "gama",
  "neutron": "neutrão",
  "paper": "papel",
  "aluminium {#} mm": "alumínio {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "chumbo {#} cm",
  "water {#} cm": "água {#} cm",
  "no shield": "sem blindagem",
  "stopped": "travado",
  "all through": "passa tudo",
  "{#} % through": "passa {#} %",
  "{#} in {#}": "{#} em {#}",
  "{#} in {#} million": "{#} em {#} milhões",
  "{#} in a billion": "{#} em mil milhões",
  "drag ↔": "arrasta ↔",
  "all four stopped": "os quatro travados",
  "all four beams stopped": "os quatro feixes travados",
  "flash = stopped inside the shield": "clarão = travado na blindagem",
  "each source fires a steady beam": "cada fonte emite um feixe contínuo",
  "flash = stopped": "clarão = travado",
  "four beams": "quatro feixes",
  "not to scale": "fora de escala",
  "gamma rays (caesium{#})": "raios gama (césio{#})",
  "cm of lead": "cm de chumbo",
  "share still going": "fração que continua",
  "through: all · halved every {#} mm": "passa: tudo · metade a cada {#} mm",
  "through: {#} % · halved every {#} mm": "passa: {#} % · metade a cada {#} mm",
  "through: {#} in {#} · halved every {#} mm": "passa: {#} em {#} · metade a cada {#} mm",
  "gets through: {#} % · halved every {#} mm of lead": "atravessa: {#} % · reduz-se a metade a cada {#} mm de chumbo",
  "gets through: {#} in {#} · halved every {#} mm of lead": "atravessa: {#} em {#} · reduz-se a metade a cada {#} mm de chumbo",
  "counted: {#} of {#}": "contados: {#} de {#}",
  "through {#} % · back {#} % · caught {#} %": "passam {#} % · voltam {#} % · capturados {#} %",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "atravessaram {#} % · ressaltaram para trás {#} % · abrandados e capturados {#} %",
  "bright = fast · dim = slowed": "brilhante = rápido · ténue = abrandado",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "brilhante = neutrão rápido · vermelho = núcleo de hidrogénio projetado · clarão verde = absorvido",
  "simplified model": "modelo simplificado",
});
