/* Danish: cascade (chapter 8) */
WT.L.ch.cascade = {
  num: "Kapitel 11", title: "Emissionskaskaden", short: "Kaskade",
  lead: "Én emission er sjældent enden: den kerne, der bliver tilbage, er ofte varm nok til at udsende igen.",
  html: `
<div class="step">
  <p>En neutron har forladt compoundkernen (til venstre), og den <b>restkerne</b>, den efterlader (til højre), er stadig varm. Den orange kugle er energien. Restkernens grundtilstand ligger højere med neutronens <b>separationsenergi</b> S<sub>n</sub>, prisen for at trække den ud.</p>
  <p>Hver gang en neutron forlader kernen, falder kuglen med neutronens kinetiske energi. Hvor den stopper, er restkernens <b>excitation</b>, dens overskydende energi; prikkerne til højre tæller landingerne.</p>
  <div class="ctl"><label for="cs-e">Neutronenergi</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Udsendte neutroner er som regel langsomme, så de fleste fald er korte. Blå prikker ligger over den stiplede neutrontærskel: de har råd til en neutron mere, (n,2n)-reaktionen. Under omkring 11 MeV kommer ingen derop.</p>
</div>
<div class="step">
  <h3>Sekventiel emission hen over kortet</h3>
  <p>Strømmene er reaktioner, der vandrer hen over et hjørne af <b>nuklidkortet</b>, kerner afbildet efter neutrontal N (vandret) og protontal Z (lodret). Hver starter i det omkransede compoundfelt; hvert felt er opkaldt efter den reaktion, der ender dér.</p>
  <p>En <em class="n">neutron</em> ud flytter ét felt til venstre, en <em class="p">proton</em> ét ned, en <em class="a">alfapartikel</em> (to protoner, to neutroner) to diagonalt. Strømmens bredde er, hvor meget der tager det skridt; farvetone og procent viser, hvor reaktionerne ender.</p>
  <div class="ctl"><label for="cs-e4">Neutronenergi</label><input id="cs-e4" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Affyr 200 reaktioner</button></div>
  <p>Træk i energien: ved et par MeV standser næsten alt på målfeltet; højere oppe når strømmene længere. Hvert skridt koster 7 til 11 MeV i separationsenergi, så selv ved 30 MeV er vandringen højst tre eller fire skridt.</p>
</div>
<div class="step">
  <h3>Regnskab over bestanden</h3>
  <p>Motoren tømmer hver kerne oppefra og ned, én energiskive, eller ét <b>interval</b>, ad gangen. Til højre: restkernen fra den første emission; til venstre: dens datterkerne, med én neutron mindre. Orange kugler er reaktioner, der venter i hvert interval. Intervallerne er 1 MeV her; motoren bruger omkring 40 pr. kerne, afpasset efter den tilgængelige energi.</p>
  <p>Når markøren fejer hen over et interval, tager hver kugle en udgang efter konkurrencen fra kapitel 9: en foton (<em class="g">γ</em>) sænker den til et lavere interval, en <em class="n">neutron</em> flytter den over i datterkernen, en proton eller alfapartikel fjerner den fra billedet. Under alle tærskler fører fotoner resten ned til grundtilstanden (grå). Derefter fejes datterkernen.</p>
  <div class="ctl"><label for="cs-e3">Neutronenergi</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Start forfra</button></div>
  <p>Fotoner falder kun nedad, og hver kerne er færdig før sine datterkerner, så intet lander i et interval, der allerede er tømt.</p>
</div>
<div class="step">
  <h3>Eksklusive reaktionskanaler</h3>
  <p>Én reaktion afspilles ad gangen: markøren hopper hen over kortet, og hver udsendt partikel falder ned i bakken. Hver kanal afspilles ved en energi, hvor den rent faktisk sker (øverst i billedet): (n,3n) ved 25 MeV, da tre neutroner her koster mere end 20 MeV; indfangning, (n,γ), ved 1 MeV. Den fyldte bakke navngiver den <b>eksklusive kanal</b>, fx (n,2n); fotoner tæller ikke med. Motoren giver hver kanal sit eget tværsnit (dens sandsynlighed, som et effektivt målareal).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Næste kanal</button></div>
  <p>Gå dem igennem. (n,np) afspilles to gange, med neutronen først og med protonen først: samme felt, samme bakke, én kanal. Derefter når en spøgelsesdeuteron (en bundet proton og neutron) samme felt i ét hop: dens bakke viser d, en anden kanal, (n,d).</p>
</div>
<div class="step">
  <h3>Produktion af restkerner</h3>
  <p>Hvert felt har nu hylder: blæk for <b>grundtilstanden</b>, grøn (på to felter) for en <b>isomer</b>, en exciteret tilstand, der lever længe nok til at tælle som et separat produkt. Bunkens højde er <b>restkerneproduktionen</b>: hvor meget af hver kerne reaktionerne har lavet.</p>
  <div class="ctl"><label for="cs-e2">Neutronenergi</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Affyr 200 reaktioner</button></div>
  <p>Træk i energien: den næste portion bruger den, og gamle bunker blegner. Produktionen flytter sig væk fra starten, efterhånden som flere partikler kan slippe ud. Hver historie ender på en hylde, og en aktiveringsmåling ser netop disse bunker: bestrål en prøve, og tæl derefter hvert produkts henfald.</p>
  <div class="aside">I koden: <code>emission/multiple.py</code> (løkken over kerner og intervaller, γ-kaskaden), <code>emission/feeding.py</code> (gitre og input for hver kerne i kæden), <code>compound/continuum.py</code> (henfaldet af ét interval), <code>emission/channels.py</code> (eksklusive kanaler, restkerneproduktion, isomergrene), <code>emission/binary.py</code> (bogføringen for den første emission).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged in Danish)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "compound", "target": "target",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "neutrontal →",
  // scene 1
  "levels": "niveauer",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "grund",
  "residual": "restkerne", "residual (one neutron fewer)": "restkerne (én neutron mindre)",
  "n threshold": "n-tærskel", "its neutron threshold": "dens neutrontærskel",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "fald = neutronens kinetiske energi",
  "{#} % land above the threshold: a second neutron can leave": "{#} % lander over tærsklen: en neutron mere kan slippe ud",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % lander over tærsklen: en neutron mere kan slippe ud",
  "all land below the threshold: only photons remain": "alle lander under tærsklen: kun fotoner er tilbage",
  "{#} % above threshold: (n,{#}n) possible": "{#} % over tærsklen: (n,{#}n) mulig",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % over tærsklen: (n,{#}n) mulig",
  "all below threshold: photons only": "alle under tærsklen: kun fotoner",
  // scene 2
  "incoming neutron: {#} MeV": "indkommende neutron: {#} MeV",
  "shade and % = where reactions end": "tone og % = hvor reaktioner ender",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "bredde = strøm · tone og % = andel af reaktioner, der ender i den kerne",
  // scene 3
  "residual (first step)": "restkerne (første skridt)",
  "daughter: n fewer": "datter: én n mindre", "daughter (one neutron fewer)": "datter (én neutron mindre)",
  "now: {#}–{#} MeV": "nu: {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "færdig: {#} gik ud som proton eller alfa, resten er i grundtilstande",
  "done: everything sits on a ground state": "færdig: alt er i en grundtilstand",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "orange kugle = ventende reaktioner · grå = i grundtilstanden · blege intervaller = allerede tømt",
  // scene 4
  "collected": "samlet",
  "tray: d": "bakke: d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "en deuteron lander i samme felt, men dens bakke viser d: kanal (n,d)",
  "tray: n n  →  (n,{#}n)": "bakke: n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "bakke: n  →  (n,n′)",
  "tray: p  →  (n,p)": "bakke: p  →  (n,p)",
  "tray: n p  →  (n,np)": "bakke: n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "bakke: n p  →  (n,np) · samme felt, samme bakke",
  "tray: a  →  (n,α)": "bakke: a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "bakke: n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "bakken tom, kun fotoner: (n,γ), indfangning",
  "each emitted particle falls into the tray": "hver udsendt partikel falder i bakken",
  "no particle gets out: only photons": "ingen partikel slipper ud: kun fotoner",
  "incoming neutron: {#} MeV · channel {#} of {#}": "indkommende neutron: {#} MeV · kanal {#} af {#}",
  // scene 5
  "isomer": "isomer",
  "batch of {#} at {#} MeV": "portion på {#} ved {#} MeV",
  "ink shelf: ground state · green: isomer": "blæk: grundtilstand · grøn: isomer",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "blæk: grundtilstand · grøn: isomer · højde = hvor meget af den kerne der blev lavet",
});
