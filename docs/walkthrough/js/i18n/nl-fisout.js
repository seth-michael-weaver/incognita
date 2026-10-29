/* Dutch (Nederlands): fisout (Hoofdstuk 13, splijtingsneutronen) */
WT.L.ch.fisout = {
  num: "Hoofdstuk 13", title: "Splijtingsneutronen", short: "Splijtingsneutronen",
  html: `
<div class="step">
  <p>Elke splijting maakt twee of drie neutronen vrij: gemiddeld 2,4. Bovenaan zie je één splijting tegelijk: de uraniumkern scheurt in twee brokstukken en de blauwe bollen vliegen weg. Dit zijn de <b>prompte</b> neutronen, die er in veel minder dan een miljoenste seconde uit zijn.</p>
  <p>De linkergrafiek telt hoeveel splijtingen 0, 1, 2, 3 … neutronen vrijmaakten. De balken zijn de splijtingen die je afvuurde; de dunne lijn op elke balk is het gemeten aandeel. Vuur er meer af en de balken zetten zich op de lijnen.</p>
  <div class="btns"><button class="btn" data-act="f100">100 splijtingen</button><button class="btn ghost" data-act="f1000">1000 splijtingen</button></div>
</div>
<div class="step">
  <p>Ze worden snel geboren: gemiddeld ongeveer 2 MeV, zo'n 80 miljoen keer de energie van een langzaam neutron in een reactor bij kamertemperatuur. De rechtergrafiek sorteert de prompte neutronen naar energie. De lijn is de gemeten vorm (het Watt-spectrum): een bult rond 1 MeV en een lange staart tot 10 MeV.</p>
  <p>Zulke snelle neutronen veroorzaken zelden de volgende splijting in uranium-235, dus een reactor remt ze eerst af, zoals een later hoofdstuk laat zien.</p>
  <div class="btns"><button class="btn" data-act="f100">100 splijtingen</button><button class="btn ghost" data-act="f1000">1000 splijtingen</button></div>
</div>
<div class="step">
  <p>Een paar komen seconden later: 0,65 % van alle neutronen. Sommige brokstukken zijn zo neutronrijk dat de nieuwe kern bij hun verval een van zijn neutronen niet kan vasthouden en het laat gaan. Dat neutron moet op het verval wachten, vaak seconden lang.</p>
  <p>De onderste lijn is een klok na de splijting, van 0,01 s tot 100 s; elk streepje is tien keer later dan het vorige. De bol links is alle prompte neutronen, in één keer eruit. Elk klein stipje is één vertraagd neutron: het rijdt mee langs de lijn zolang zijn wachttijd loopt, op een klok die 20 keer sneller gaat, en komt tot rust waar het uiteindelijk naar buiten kwam. Deze weinige late neutronen maken een reactor regelbaar: ze vertragen de reactietijd van de keten van duizendsten van een seconde tot seconden.</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 splijtingen</button><button class="btn ghost" data-act="clear">Wissen</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "n + U{#} → two fragments + neutrons": "n + U{#} → twee brokstukken + neutronen",
  "prompt neutrons per fission": "prompte neutronen per splijting",
  "lines: measured shares": "lijnen: gemeten aandelen",
  "mean {#}": "gemiddeld {#}",
  "prompt-neutron energy (MeV)": "energie prompte neutronen (MeV)",
  "mean {#} MeV": "gemiddeld {#} MeV",
  "line: measured shape": "lijn: gemeten vorm",
  "prompt": "prompt",
  "time after fission · clock sped up {#}×": "tijd na splijting · klok {#}× versneld",
  "delayed {#} of {#} ({#} %)": "vertraagd {#} van {#} ({#} %)",
  "{#} fissions": "{#} splijtingen",
});
