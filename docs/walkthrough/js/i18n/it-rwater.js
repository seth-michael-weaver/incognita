/* Italian: rwater (Reattori raffreddati ad acqua) */
WT.L.ch.rwater = {
  num: "Lezione 1", title: "Reattori raffreddati ad acqua", short: "Reattori ad acqua",
  lead: "Quasi tutti i reattori di potenza di oggi sono raffreddati ad acqua. Si distinguono per il modo in cui l'acqua porta fuori il calore.",
  html: `
<div class="step">
  <h3>Acqua pressurizzata (PWR)</h3>
  <p>Acqua ad alta pressione porta il calore a un generatore di vapore; un secondo circuito produce il vapore.</p>
</div>
<div class="step">
  <h3>Acqua bollente (BWR)</h3>
  <p>L'acqua bolle nel nocciolo stesso e il vapore va dritto in turbina: un solo circuito.</p>
</div>
<div class="step">
  <h3>Acqua pesante (CANDU)</h3>
  <p>L'acqua pesante rallenta i neutroni senza assorbirne molti, così basta l'uranio naturale.</p>
</div>
<div class="step">
  <h3>Grafite e acqua bollente (RBMK)</h3>
  <p>La grafite rallenta i neutroni; l'acqua bolle in centinaia di tubi separati.</p>
</div>
<div class="step">
  <h3>Piccolo modulare (SMR)</h3>
  <p>Un piccolo PWR con tutto dentro un solo recipiente, costruito in fabbrica.</p>
</div>
<div class="step">
  <h3>Acqua supercritica (SCWR)</h3>
  <p>Sopra i 221 bar l'acqua non bolle mai, quindi può lavorare più calda e trasformare più calore in elettricità.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "BWR": "BWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU; Canada, India, Romania, Argentina",
  "Generation IV design, not yet built": "progetto di IV generazione, non ancora costruito",
  "NuScale (US), Linglong One (China)": "NuScale (USA), Linglong One (Cina)",
  "PHWR": "PHWR",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "circa il {#} % dei reattori; USA, Giappone, Svezia",
  "about {#} in {#} of the world's reactors": "circa {#} reattori su {#} nel mondo",
  "all in one vessel": "tutto in un recipiente",
  "boiling water in tubes": "acqua bollente nei tubi",
  "boils in the core": "bolle nel nocciolo",
  "calandria: cool heavy water": "calandria: acqua pesante fredda",
  "calandria: cool heavy water slows the neutrons": "calandria: l'acqua pesante fredda rallenta i neutroni",
  "condenser": "condensatore",
  "control rods from below": "barre di controllo dal basso",
  "coolant out": "uscita refrigerante",
  "core": "nocciolo",
  "core, pump-free loop and steam generator in one vessel": "nocciolo, circuito senza pompe e generatore di vapore in un solo recipiente",
  "electricity": "elettricità",
  "gen.": "altern.",
  "generator": "alternatore",
  "graphite": "grafite",
  "graphite blocks slow the neutrons": "i blocchi di grafite rallentano i neutroni",
  "horizontal pressure tubes, refuelled while running": "tubi in pressione orizzontali, ricaricati in marcia",
  "illustration": "illustrazione",
  "outlet": "uscita",
  "pressure": "pressione",
  "pressure tubes": "tubi in pressione",
  "reactor vessel": "recipiente in pressione",
  "rods from below": "barre dal basso",
  "steam gen.": "gen. vapore",
  "steam generator": "generatore di vapore",
  "the Chernobyl type; a few still run in Russia": "il tipo di Černobyl'; alcuni funzionano ancora in Russia",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "neutroni termici · moderatore: grafite · refrigerante: acqua bollente",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "neutroni termici · moderatore: acqua pesante · refrigerante: acqua pesante",
  "thermal neutrons · moderator: light water · coolant: boiling water": "neutroni termici · moderatore: acqua leggera · refrigerante: acqua bollente",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "neutroni termici · moderatore: acqua leggera · refrigerante: acqua supercritica",
  "thermal neutrons · moderator: light water · coolant: water": "neutroni termici · moderatore: acqua leggera · refrigerante: acqua",
  "thermal · mod.: graphite · cool.: boiling water": "termici · mod.: grafite · refr.: acqua bollente",
  "thermal · mod.: heavy water · cool.: heavy water": "termici · mod.: acqua pesante · refr.: acqua pesante",
  "thermal · mod.: light water · cool.: boiling water": "termici · mod.: acqua leggera · refr.: acqua bollente",
  "thermal · mod.: light water · cool.: supercritical water": "termici · mod.: acqua leggera · refr.: acqua supercritica",
  "thermal · mod.: light water · cool.: water": "termici · mod.: acqua leggera · refr.: acqua",
  "turbine": "turbina",
  "vessel": "recipiente",
  "water boils in the core": "l'acqua bolle nel nocciolo",
  "water boils in ~{#} pressure tubes": "l'acqua bolle in ~{#} tubi in pressione",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar: oltre l'ebollizione, ma resta un solo fluido",
  "{#} bar: never boils": "{#} bar: non bolle mai",
  "{#} °C": "{#} °C",
});
