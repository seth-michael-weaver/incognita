/* Danish: slowing (Kapitel 18, neutronmoderation) */
WT.L.ch.slowing = {
  num: "Kapitel 18", title: "Neutronmoderation", short: "Opbremsning",
  html: `
<div class="step">
  <p>Hvert tilbagekast fra brint koster omkring halvdelen af energien. En fissionsneutron starter ved 2 MeV og preller gennem vand. En brintkerne vejer det samme som neutronen, så, som billardkugler, afgiver hvert tilbagekast i gennemsnit halvdelen af neutronens energi til den.</p>
  <p>Grafen viser neutronens energi efter hvert tilbagekast; hver mærkat ned ad siden er tusind gange mindre energi. At miste den samme andel hver gang giver et lige glid, den stiplede linje. Efter omkring 18 tilbagekast når neutronen den <b>termiske</b> energi, 0,025 eV, hvor det varme vand sparker den op lige så ofte, som det bremser den. Ilt er 16 gange tungere: hvert tilbagekast tager kun lidt, og det kræver over hundrede.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Brint</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Ilt</button><button class="btn" data-act="again">Affyr igen</button></div>
</div>
<div class="step">
  <p>Under omkring 1 eV former molekylets bindinger hvert tilbagekast. Hver brint er bundet til sin ilt (de lysende linjer). En langsom neutron rammer ikke længere en fri brint: den rammer et helt molekyle, 18 gange tungere, så et almindeligt tilbagekast tager næsten intet.</p>
  <p>Den kan også få molekylet til at rotere eller vibrere, men kun ved at aflevere en fast mængde energi ad gangen, 0,06, 0,2 eller 0,45 eV (de lysende glimt). Varme molekyler giver nogle gange sådan en mængde tilbage. På grafen er det skraverede bånd under 1 eV, hvor det har betydning. Slå bindingen fra for at sammenligne med fri brint.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Kemisk binding</button><button class="btn" data-act="again">Affyr igen</button></div>
</div>
<div class="step">
  <p>En computerkode har brug for alt dette som en tabel: <b>spredningsloven</b>, kortet. Vandret: hvor hårdt stødet er, α (skubbet, molekylet får; lille ved et strejf, stort ved et frontalt stød). Lodret: den energi, neutronen vinder (op) eller taber (ned), β, regnet i enheder af vandets termiske energi, 0,025 eV. Lyst betyder sandsynligt, blegt betyder sjældent.</p>
  <p>Omridset er det, en neutron med den valgte energi kan nå: den kan ikke tabe mere, end den har, og hver energiændring tillader kun et område af stød. Træk i energien, og omridset vokser eller skrumper. Uden binding er kortet fri brintgas, én lys ryg langs den stiplede tilbagekastlinje; med binding tilføjer molekylet lyse striber, dets faste energimængder. INCOGNITA beregner sine egne love for vand og beryllium: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Neutronenergi (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Kemisk binding</button></div>
</div>
`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
