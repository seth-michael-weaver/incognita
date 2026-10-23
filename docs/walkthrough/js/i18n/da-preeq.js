/* Danish: preeq (Kapitel 4, præligevægt) */
WT.L.ch.preeq = {
  num: "Kapitel 4", title: "Kollisioner før roen", short: "Præligevægt",
  lead: "En neutron, der trænger ind i en kerne, deler ikke sin energi med alle på én gang. I de første par kollisioner har én partikel det meste af den, og den partikel kan flyve lige ud igen. Det er præligevægt: emission “før energien udjævnes”.",
  html: `
<div class="step">
  <p>To brønde, én for <em class="p">protoner</em> og én for <em class="n">neutroner</em>. Hver kugle er en nukleon på et energiniveau, tegnet som et trin; trinene er fyldt nedefra op til <b>Fermifladen</b>. En nukleon over den stiplede “fri”-linje har energi nok til at undslippe. Motoren holder styr på protoner og neutroner hver for sig.</p>
  <p>Den indkommende neutron svæver ovenover med al energien: sin egen plus flere MeV (millioner elektronvolt), der frigøres ved indfangningen.</p>
</div>
<div class="step">
  <h3>Par løftes op</h3>
  <p>Hver kollision løfter en nukleon op på et tomt trin og efterlader et <b>hul</b> (en åben ring). Partikler over overfladen og huller under den kaldes begge <b>excitoner</b>. Den første kollision giver 2 partikler og 1 hul (n = 3); hver senere tilføjer endnu et par.</p>
  <div class="btns"><button class="btn" data-act="collide">Kollidér</button><button class="btn ghost" data-act="reset">Start forfra</button></div>
  <p>Tryk på Kollidér et par gange. Den løftede nukleon kan være en proton eller en neutron, og motoren tæller hver slags. Med hvert par deles energien på flere, så den øverste partikel ligger lavere.</p>
</div>
<div class="step">
  <h3>Forgreningen ved hvert trin</h3>
  <p>På hvert trin undslipper den øverste neutron enten (pil op, kun hvis den er over fri-linjen) eller kolliderer igen (pil ned); tykkelsen viser oddsene. Undslipningsraten følger af <b>detaljeret balance</b>: af sandsynligheden for den omvendte proces, at samme partikel absorberes, som kapitel 2 beregner. Kollisionsraten er styrken af én nukleon–nukleon-kollision gange antallet af nye konfigurationer, den kan nå.</p>
  <div class="ctl"><label for="pe-n">Trin (excitoner n)</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>Træk trinnet op. Tidligt har én partikel det meste af energien, så det, der slipper ud, er hurtigt. Senere er energien spredt tyndt, og lidt kommer ud.</p>
</div>
<div class="step">
  <h3>Hvor den hurtige hale kommer fra</h3>
  <p>Bunken til højre er <b>spektret</b>: hvor mange neutroner der kommer ud ved hver energi, langsomme til venstre, hurtige til højre. Hver reaktion kører kæden, indtil den øverste neutron undslipper, og dens farve fortæller hvornår: <em style="font-style:normal;color:var(--warm);font-weight:600">dyb orange</em> på trin 3, blegere senere, <em class="n">blå</em>, hvis den først kom ud, efter at kernen var faldet til ro (kapitel 5).</p>
  <div class="btns"><button class="btn" data-act="run">Kør 300 reaktioner</button></div>
  <p>Trin 3 bygger en bred, næsten flad hylde, der når den maksimale energi. Senere trin hober sig op lavere. Den blå pukkel er <b>fordampning</b>: når alle deler energien, siver kun langsomme neutroner ud, som damp fra en varm væske.</p>
  <div class="ctl"><label for="pe-e">Neutronenergi</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>Træk i den indkommende neutrons energi: et nyt hold kører, og hylden strækker sig længere. Fordampning alene giver aldrig hurtige neutroner.</p>
</div>
<div class="step">
  <h3>Konfigurationer tælles</h3>
  <p>Tælleren gennemgår alle måder at placere partikler på tomme trin og huller i fyldte trin, så deres energier summer til den energi, der skal deles (trinene ligger her 1 MeV fra hinanden). Nukleoner er fermioner: to kan ikke dele et trin, så en partikel må lande på et tomt trin, og et hul opstår kun, hvor der var en nukleon. Det er <b>Pauli-blokering</b>.</p>
  <div class="ctl"><label for="pe-u">Energi at dele (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">Tilføj et par</button><button class="btn ghost" data-act="droppair">Fjern et par</button></div>
  <p>Tilføj et par, og tallet springer op; hæv energien, og det stiger omtrent som <i>E</i><sup>n−1</sup>. Dette tal, <b>partikel-hul-tilstandstætheden</b>, bestemmer kollisionsraten: flere konfigurationer, flere steder en kollision kan føre hen. Motoren tæller på den virkelige stige, med trin en brøkdel af en MeV fra hinanden, og tilføjer én grænse, du ser ved høj energi: et hul kan ikke ligge under brøndens bund.</p>
</div>
<div class="step">
  <h3>Klynger forlader også kernen</h3>
  <p>Små klynger kan også forlade kernen tidligt. Ved <b>pickup</b> griber en proton på vej ud en neutron ved overfladen og forlader kernen sammen med den som en <em class="n">deuteron</em>; griber den to, bliver det en triton eller helium-3. Ved <b>knockout</b> rammer den indkommende neutron en <em class="a">alfapartikel</em> (to protoner og to neutroner), der allerede er dannet nær overfladen, og slår den ud. Motoren bruger Kalbachs formler til begge.</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">Grib en neutron → d</button><button class="btn ghost" data-act="knock">Slå en α ud</button></div>
  <p>Tryk på en knap for at se en af dem. Begge giver deuteroner og alfapartikler deres egne hurtige haler, der begynder lige over den energi, det koster at trække hver af dem ud.</p>
</div>
<div class="step">
  <h3>En hurtig nummer to</h3>
  <p>Ved høj energi kan en anden løftet nukleon stadig ligge over fri-linjen, når den første neutron forlader kernen, og også undslippe, som en hurtig neutron eller proton. Brøndene genafspiller én reaktion ad gangen, med energiskalaen trykket sammen.</p>
  <div class="ctl"><label for="pe-e2">Neutronenergi</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>Træk i energien. Under ca. 20 MeV kommer den anden nukleon sjældent over linjen; derover afgiver flere og flere reaktioner to hurtige partikler. Det er <b>multipel præligevægt</b>, som motoren medtager fra 20 MeV og op. Det, der ikke er sluppet ud, bliver til næste kapitels compoundkerne. Under nogle få MeV (målkernens højeste diskrete niveau i brug) springer motoren helt kæden over.</p>
  <div class="aside">I koden: <code>preeq/exciton.py</code> (excitonkæde med to komponenter, kollisions- og undslipningsrater), <code>density/particle_hole.py</code> (partikel-hul-tilstandstætheder med Pauli- og endelig-brønd-korrektioner), <code>preeq/complex.py</code> (Kalbachs pickup, stripping og α-knockout), <code>preeq/multi.py</code> (multipel præligevægt), <code>compound/normalization.py</code> (overdragelse til compoundkernen).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "protoner",
  "neutrons": "neutroner",
  "Fermi": "Fermi",
  "Fermi surface": "Fermifladen",
  "free": "fri",
  "free: can escape": "fri: kan undslippe",
  "all the energy in one nucleon": "al energien i én nukleon",
  "{#} particle, {#} holes": "{#} partikel, {#} huller",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} partikel, {#} huller: n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} partikel, {#} hul: n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} partikler, {#} hul: n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} partikler, {#} huller: n = {#}",
  "protons: {#} lifted, {#} hole": "protoner: {#} løftet, {#} hul",
  "protons: {#} lifted, {#} holes": "protoner: {#} løftet, {#} huller",
  "neutrons: {#} lifted, {#} hole": "neutroner: {#} løftet, {#} hul",
  "neutrons: {#} lifted, {#} holes": "neutroner: {#} løftet, {#} huller",
  "chain ends: the rest becomes a compound nucleus": "kæden slutter: resten bliver en compoundkerne",
  // fork
  "about {#} MeV above surface": "ca. {#} MeV over overfladen",
  "escapes  {#}%": "undslipper  {#} %",
  "collides again  {#}%": "kolliderer igen  {#} %",
  "below the free line: it cannot leave": "under fri-linjen: kan ikke slippe ud",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}: {#} partikler, {#} hul, {#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}: {#} partikler, {#} huller, {#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "trin n = {#}: {#} partikler og {#} hul deler {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "trin n = {#}: {#} partikler og {#} huller deler {#} MeV",
  // tail
  "max {#} MeV": "maks. {#} MeV",
  "slow": "langsom",
  "fast →": "hurtig →",
  "stage {#}": "trin {#}",
  "chain over: compound": "kæden slut: compound",
  "left at:": "ude ved:",
  "neutron left at:": "neutron ude ved:",
  "evaporation": "fordampning",
  "{#} of {#} landed · {#} left during the chain": "{#} af {#} landet · {#} ude under kæden",
  // pauli
  "well bottom: no deeper hole": "brøndens bund: intet dybere hul",
  "bottom of the well": "brøndens bund",
  "{#} MeV to share": "{#} MeV at dele",
  "{#} particles · {#} hole": "{#} partikler · {#} hul",
  "{#} particles · {#} holes": "{#} partikler · {#} huller",
  "ways, all counted": "måder, alle talt",
  "arrangements so far": "konfigurationer indtil nu",
  "one more pair: {#} ways": "ét par mere: {#} måder",
  "never two on one rung · holes only where a nucleon was": "aldrig to på ét trin · huller kun hvor en nukleon var",
  "(first {#} shown as ticks)": "(de første {#} vist som streger)",
  // cluster
  "a deuteron leaves": "en deuteron forlader kernen",
  "grabs a neutron at the edge": "griber en neutron ved kanten",
  "a fast proton heads out": "en hurtig proton på vej ud",
  "an α ({#} protons + {#} neutrons) waits at the edge": "en α ({#} protoner + {#} neutroner) venter ved kanten",
  "knocked straight out": "slået lige ud",
  // second
  "first fast neutron": "første hurtige neutron",
  "second fast proton": "anden hurtige proton",
  "second fast neutron": "anden hurtige neutron",
  "below the free line: stays": "under fri-linjen: bliver",
  "below the free line: it stays": "under fri-linjen: den bliver",
  "the rest settles: compound nucleus": "resten falder til ro: compoundkerne",
  "{#} MeV carried in": "{#} MeV bragt ind",
  "second fast particle in {#} of the last {#} reactions": "anden hurtige partikel i {#} af de seneste {#} reaktioner",
});
