/* Danish: fisout (Kapitel 14, fissionsneutroner) */
WT.L.ch.fisout = {
  num: "Kapitel 14", title: "Fissionsneutroner", short: "Fissionsneutroner",
  html: `
<div class="step">
  <p>Hver fission frigør to eller tre neutroner: 2,4 i gennemsnit. Øverst, én fission ad gangen: urankernen flænges i to fragmenter, og de blå kugler flyver af sted. Det er de <b>prompte</b> neutroner, ude på langt under en milliontedel sekund.</p>
  <p>Diagrammet til venstre tæller, hvor mange fissioner der frigjorde 0, 1, 2, 3 … neutroner. Søjlerne er de fissioner, du har affyret; den tynde streg på hver søjle er den målte andel. Affyr flere, og søjlerne lægger sig ind på stregerne.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissioner</button><button class="btn ghost" data-act="f1000">1000 fissioner</button></div>
</div>
<div class="step">
  <p>De fødes hurtige: omkring 2 MeV i gennemsnit, ca. 80 millioner gange energien af en langsom neutron i en reaktor ved stuetemperatur. Diagrammet til højre sorterer de prompte neutroner efter energi. Linjen er den målte form (Watt-spektret): en pukkel nær 1 MeV og en lang hale ud til 10 MeV.</p>
  <p>Så hurtige neutroner forårsager sjældent den næste fission i uran-235, så en reaktor bremser dem først, som et senere kapitel viser.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissioner</button><button class="btn ghost" data-act="f1000">1000 fissioner</button></div>
</div>
<div class="step">
  <p>Nogle få kommer sekunder senere: 0,65 % af alle neutronerne. Nogle fragmenter er så neutronrige, at den nye kerne, når de senere henfalder, ikke kan holde på en af sine neutroner og slipper den. Det venter på henfaldet, ofte sekunder.</p>
  <p>Den nederste linje er et ur efter fissionen, fra 0,01 s til 100 s; hvert mærke er ti gange senere end det forrige. Kuglen til venstre er alle de prompte neutroner, ude på én gang. Hver lille prik er én forsinket neutron: den følger linjen, mens dens ventetid løber, på et ur sat 20 gange hurtigere, og lægger sig, hvor den til sidst kom ud. Netop disse få sene neutroner gør en reaktor styrbar: de forlænger kædens reaktionstid fra tusindedele af et sekund til sekunder.</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 fissioner</button><button class="btn ghost" data-act="clear">Ryd</button></div>
</div>`,
};
