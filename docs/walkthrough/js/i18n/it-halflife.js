/* Italian: halflife (Radioattività e tempo di dimezzamento) */
WT.L.ch.halflife = {
  num: "Lezione 1", title: "Radioattività e tempo di dimezzamento", short: "Dimezzamento",
  lead: "Alcuni atomi sono instabili: prima o poi il loro nucleo scoppia, emette radiazione e diventa qualcos'altro. Nessuno può dire quando succederà a un singolo nucleo, eppure un intero campione segue un orologio preciso come pochi.",
  html: `
<div class="step">
  <h3>Un campione che scoppia a caso</h3>
  <p>Ogni pallina luminosa è un nucleo instabile. Ognuna può scoppiare in qualsiasi momento, emettendo un lampo di radiazione e diventando un atomo calmo e stabile. Toccane una per farla scoppiare.</p>
  <div class="btns"><button class="btn" data-act="refill">Nuovo campione</button></div>
</div>
<div class="step">
  <h3>La metà, e poi ancora la metà</h3>
  <p>Nessuno può dire quale sarà il prossimo, ma la folla è prevedibile: dopo un <b>tempo di dimezzamento</b> (o emivita) ne resta circa la metà, dopo due un quarto, poi un ottavo. Allunga o accorcia il tempo di dimezzamento.</p>
  <div class="ctl"><label for="hl-th">Tempo di dimezzamento (secondi)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Nuovo campione</button></div>
</div>
<div class="step">
  <h3>I nuclei non hanno memoria</h3>
  <p>Segui un sopravvissuto. Per quanto a lungo sia già durato, la sua probabilità di durare un altro tempo di dimezzamento resta una su due: un nucleo non invecchia.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Seguine un altro</button><button class="btn ghost" data-act="refill">Nuovo campione</button></div>
</div>
<div class="step">
  <h3>Tempi di dimezzamento reali</h3>
  <p>Gli isotopi reali vanno da pochi giorni a miliardi di anni. Su questa scala dei tempi dilatata, ciascuno precipita da una scogliera al proprio tempo di dimezzamento. Scegline uno e fai avanzare il tempo.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Iodio-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Cesio-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Carbonio-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Uranio-238</button></div>
  <div class="ctl"><label for="hl-t1">Tempo trascorso</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Attività: decadimenti al secondo</h3>
  <p>Un grammo di ciascuno, fianco a fianco. Un tempo di dimezzamento breve significa molti decadimenti ogni secondo, ma per poco; uno lungo brilla debolmente per ere. Fai avanzare il tempo e guarda le lampade spegnersi una dopo l'altra.</p>
  <div class="ctl"><label for="hl-t2">Tempo trascorso</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "survived {#} half-lives": "sopravvissuto a {#} emivite",
  "chance to last one more: {#} in {#}": "probabilità di durarne un'altra: {#} su {#}",
  "survived {#} half-lives · still {#} in {#}": "sopravvissuto a {#} emivite · ancora {#} su {#}",
  "it popped: follow another": "è scoppiato: seguine un altro",
  "{#} of {#} still unstable": "{#} su {#} ancora instabili",
  "{#} half-life": "{#} emivita",
  "1 half-life": "1 emivita",
  "half-lives →": "emivite →",
  "nuclei left": "nuclei rimasti",
  "{#} of {#} left · half-life {#} s": "ne restano {#} su {#} · emivita {#} s",
  "every survivor has the same 1-in-2 chance per half-life": "ogni sopravvissuto ha la stessa probabilità, 1 su 2, per emivita",
  "every survivor has the same {#}-in{#} chance per half-life": "ogni sopravvissuto ha la stessa probabilità, {#} su {#}, per emivita",
  "illustrative half-life": "emivita illustrativa",
  "1 hour": "1 ora",
  "{#} hour": "{#} ora",
  "{#} day": "{#} giorno",
  "{#} d": "{#} g",
  "{#} year": "{#} anno",
  "{#} yr": "{#} a",
  "{#} years": "{#} anni",
  "10³ yr": "10³ a",
  "10⁶ yr": "10⁶ a",
  "10⁹ yr": "10⁹ a",
  "{#}³ yr": "{#}³ a",
  "{#}⁶ yr": "{#}⁶ a",
  "{#}⁹ yr": "{#}⁹ a",
  "1 million years": "1 milione di anni",
  "1 billion years": "1 miliardo di anni",
  "{#} million years": "{#} milioni di anni",
  "{#} billion years": "{#} miliardi di anni",
  "drag": "trascina",
  "iodine{#} · half-life {#} days": "iodio{#} · emivita {#} giorni",
  "caesium{#} · half-life {#} years": "cesio{#} · emivita {#} anni",
  "carbon{#} · half-life {#} years": "carbonio{#} · emivita {#} anni",
  "uranium{#} · half-life {#} billion years": "uranio{#} · emivita {#} miliardi di anni",
  "medicine, fission product": "medicina, prodotto di fissione",
  "fission product": "prodotto di fissione",
  "radiocarbon dating": "datazione al radiocarbonio",
  "natural uranium": "uranio naturale",
  "all": "tutti",
  "{#} % left after {#} minutes": "resta il {#} % dopo {#} minuti",
  "{#} % left after {#} hours": "resta il {#} % dopo {#} ore",
  "{#} % left after {#} days": "resta il {#} % dopo {#} giorni",
  "{#} % left after {#} months": "resta il {#} % dopo {#} mesi",
  "{#} % left after {#} years": "resta il {#} % dopo {#} anni",
  "{#} % left after {#} thousand years": "resta il {#} % dopo {#} mila anni",
  "{#} % left after {#} million years": "resta il {#} % dopo {#} milioni di anni",
  "{#} % left after {#} billion years": "resta il {#} % dopo {#} miliardi di anni",
  "under {#} % left after {#} minutes": "resta meno dello {#} % dopo {#} minuti",
  "under {#} % left after {#} hours": "resta meno dello {#} % dopo {#} ore",
  "under {#} % left after {#} days": "resta meno dello {#} % dopo {#} giorni",
  "under {#} % left after {#} months": "resta meno dello {#} % dopo {#} mesi",
  "under {#} % left after {#} years": "resta meno dello {#} % dopo {#} anni",
  "under {#} % left after {#} thousand years": "resta meno dello {#} % dopo {#} mila anni",
  "under {#} % left after {#} million years": "resta meno dello {#} % dopo {#} milioni di anni",
  "under {#} % left after {#} billion years": "resta meno dello {#} % dopo {#} miliardi di anni",
  "iodine{#}": "iodio{#}",
  "caesium{#}": "cesio{#}",
  "carbon{#}": "carbonio{#}",
  "uranium{#}": "uranio{#}",
  "½ {#} days": "½ {#} giorni",
  "½ {#} years": "½ {#} anni",
  "½ {#} billion years": "½ {#} miliardi di anni",
  "½ {#} bn years": "½ {#} mld di anni",
  "almost none": "quasi nulla",
  "pops per second (log)": "decadimenti al secondo (log)",
  "pops per second, {#} gram (each line ×{#})": "decadimenti al secondo, {#} grammo (ogni linea ×{#})",
  "one gram of each, after {#} minutes": "un grammo di ciascuno, dopo {#} minuti",
  "one gram of each, after {#} hours": "un grammo di ciascuno, dopo {#} ore",
  "one gram of each, after {#} days": "un grammo di ciascuno, dopo {#} giorni",
  "one gram of each, after {#} months": "un grammo di ciascuno, dopo {#} mesi",
  "one gram of each, after {#} years": "un grammo di ciascuno, dopo {#} anni",
  "one gram of each, after {#} thousand years": "un grammo di ciascuno, dopo {#} mila anni",
  "one gram of each, after {#} million years": "un grammo di ciascuno, dopo {#} milioni di anni",
  "one gram of each, after {#} billion years": "un grammo di ciascuno, dopo {#} miliardi di anni",
});
