/* Italian: neutrons (Capitolo 5, perché i reattori funzionano a neutroni) */
WT.L.ch.neutrons = {
  num: "Capitolo 5", title: "Perché i reattori funzionano a neutroni", short: "Perché i neutroni",
  html: `
<div class="step">
  <p>Un protone è positivo, e lo sono anche gli 82 protoni del nucleo. Le cariche uguali si respingono, quindi il protone viene spinto via, e la spinta cresce rapidamente man mano che si avvicina (la freccia). Un protone lento si ferma prima e torna indietro senza toccare. Solo sopra circa 13 MeV supera la spinta; appena sotto, a volte passa comunque (<b>effetto tunnel</b>). Il piccolo grafico mostra la stessa spinta come una collina di energia.</p>
  <div class="ctl"><label for="wn-e1">Energia del protone (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>Un neutrone non ha carica: entra a qualsiasi velocità. Niente lo respinge, quindi non c'è nessuna collina da scalare; deve solo raggiungere il nucleo, e poi la forza forte lo attira dentro.</p>
  <div class="ctl"><label for="wn-e2">Energia del neutrone (lento → veloce)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>Il cursore va da 0,025 eV, la velocità di un neutrone a temperatura ambiente, fino a 20 MeV, quasi un miliardo di volte di più. Fino all'estremo più lento, il neutrone entra comunque.</p>
</div>
<div class="step">
  <p>Perciò in un reattore anche i neutroni lenti possono spezzare l'uranio. Un nucleo di uranio-235 che ne inghiotte uno diventa uranio-236 con un po' di energia in più, abbastanza da oscillare, allungarsi in un collo e rompersi in due. I due pezzi volano via con circa 200 MeV, e i due o tre nuovi neutroni che emettono possono spezzare i nuclei successivi: una reazione a catena.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "+{#} charge: the push grows as the proton gets closer": "carica +{#}: la spinta cresce man mano che il protone si avvicina",
  "lead{#}": "piombo{#}",
  "closest approach": "massimo avvicinamento",
  "proton · {#} MeV": "protone · {#} MeV",
  "energy vs distance": "energia in funzione della distanza",
  "hill ≈ {#} MeV": "collina ≈ {#} MeV",
  "pushed back · about {#} in {#}³ tunnels through": "respinto · circa {#} su {#}³ passa per effetto tunnel",
  "no charge, no push": "niente carica, niente spinta",
  "neutron · {#} eV": "neutrone · {#} eV",
  "even this crawling neutron gets in": "anche questo neutrone lentissimo entra",
  "≈ {#} MeV released": "≈ {#} MeV liberati",
  "two fragments + {#} new neutrons": "due frammenti + {#} nuovi neutroni",
  "a slow neutron + U{#} → two fragments, {#}–{#} new neutrons, about {#} MeV": "un neutrone lento + U{#} → due frammenti, {#}–{#} nuovi neutroni, circa {#} MeV",
  "a proton this slow could never get in": "un protone così lento non potrebbe mai entrare",
});
