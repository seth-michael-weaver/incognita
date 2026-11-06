/* Danish: xenon (Xenonforgiftning) */
WT.L.ch.xenon = {
  num: "Lektion 13", title: "Xenonforgiftning", short: "Xenon",
  html: `
<div class="step">
  <h3>En gift skabt af fission</h3>
  <p>Omkring 6,6 % af fissionerne fører via jod-135 til xenon-135: den stærkeste kendte neutronabsorber. Den opbygges i omkring to døgn, indtil neutroner brænder den, og henfald fjerner den lige så hurtigt, som den dannes. Højere effekt brænder den også hurtigere, så niveauet mættes.</p>
  <div class="ctl"><label for="xe-p1">Effekt (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Xenonhullet</h3>
  <p>Luk ned, og afbrændingen stopper, men det allerede dannede jod bliver ved med at blive til xenon. Giften topper omkring ni timer senere, mere end stavene kan give tilbage, så reaktoren kan ikke genstarte; den aftager over to til tre døgn.</p>
  <div class="ctl"><label for="xe-th">Timer efter nedlukning</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Luk ned, genstart</h3>
  <p>Nu kører det live, tre timer pr. sekund. Luk ned, og prøv så at genstarte: inde i hullet afvises det; senere brænder neutronerne xenonen væk. Alene en effektændring får også xenonen til at svinge i timevis.</p>
  <div class="ctl"><label for="xe-p3">Effekt (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Luk ned</button><button class="btn ghost" data-act="xerestart">Genstart</button></div>
</div>
<div class="step">
  <h3>Xenonsvingninger</h3>
  <p>I en stor kerne er de to sider kun løst koblet. Skub stave ind i den ene side: mindre flux dér brænder mindre xenon, så effekten driver over og svinger så tilbage, omkring én gang i døgnet. I større kerner vokser svingningen, medmindre operatørerne dæmper den.</p>
  <div class="ctl"><label for="xe-wd">Kernestørrelse (m)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Skub stave ind i venstre side</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "drag": "træk",
  "equilibrium {#} %": "ligevægt {#} %",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "fission → jod{#} ({#} t) → xenon{#} ({#} t) → Cs{#}",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "fission → jod{#} ({#} t) → xenon{#} ({#} t) → Cs{#}  ·  Xe{#} sluger neutroner: {#} millioner barn",
  "illustration": "illustration",
  "left {#} %": "venstre {#} %",
  "more power left": "mere effekt til venstre",
  "more power right": "mere effekt til højre",
  "no restart": "ingen genstart",
  "peak {#} % at {#} h": "top {#} % ved {#} t",
  "power": "effekt",
  "refused: more xenon than spare reactivity": "afvist: mere xenon end reservereaktivitet",
  "restarted": "genstartet",
  "right {#} %": "højre {#} %",
  "running at {#} % · xenon {#} %": "kører ved {#} % · xenon {#} %",
  "shut down": "lukket ned",
  "shut down · in the pit · xenon {#} %": "lukket ned · i hullet · xenon {#} %",
  "shut down · restart possible · xenon {#} %": "lukket ned · genstart mulig · xenon {#} %",
  "shutdown": "nedlukning",
  "spare reactivity": "reservereaktivitet",
  "spare reactivity the rods can give": "reservereaktivitet, stavene kan give",
  "swing period {#} h · {#} m core: the swing dies away": "svingningsperiode {#} t · {#} m-kerne: svingningen dør ud",
  "swing period {#} h · {#} m core: the swing dies away slowly": "svingningsperiode {#} t · {#} m-kerne: svingningen dør langsomt ud",
  "swing period {#} h · {#} m core: the swing grows": "svingningsperiode {#} t · {#} m-kerne: svingningen vokser",
  "tap a side to push rods in": "tryk på en side for at skubbe stave ind",
  "tap the core to restart": "tryk på kernen for at genstarte",
  "tap the core to shut down": "tryk på kernen for at lukke ned",
  "too poisoned to restart": "for forgiftet til at genstarte",
  "xenon worth (% of k)": "xenonværdi (% af k)",
  "xenon{#} + n → Xe{#}: {#} million barns": "xenon{#} + n → Xe{#}: {#} millioner barn",
  "{#} % power · {#} h after start-up · xenon {#} %": "{#} % effekt · {#} t efter opstart · xenon {#} %",
  "{#} h": "{#} t",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} t efter nedlukning · xenon {#} % · kan ikke genstarte",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} t efter nedlukning · xenon {#} % · genstart mulig",
  "{#} m core: push the rods to start a swing": "{#} m-kerne: skub stavene for at starte en svingning",
});
