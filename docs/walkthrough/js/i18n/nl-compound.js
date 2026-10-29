/* Dutch (Nederlands): compound (Hoofdstuk 8, de compoundkern) */
WT.L.ch.compound = {
  num: "Hoofdstuk 8", title: "De compoundkern", short: "Compoundkern",
  lead: "Zodra de eerste snelle botsingen voorbij zijn, delen alle nucleonen de energie. Deze tot rust gekomen toestand is de compoundkern. Om te voorspellen wat die daarna doet, moet de motor weten op hoeveel manieren ze haar energie kan vasthouden.",
  html: `
<div class="step">
  <p>Een neutron treft één kant van een kern. Zijn energie, plus de energie die bij zijn vangst vrijkomt, begint als een hete plek (de oranje gloed); botsingen geven haar door, en binnen ongeveer 10⁻²¹ seconde draagt elk nucleon een deel.</p>
  <div class="btns"><button class="btn" data-act="hit">Raak hem van een andere kant</button></div>
  <p>Druk op de knop om het neutron van een andere kant binnen te sturen. De gloed eindigt altijd hetzelfde: de kern is <b>vergeten hoe ze is ontstaan</b>. Dit is de compoundkern van Bohr. Vanaf hier tellen maar drie feiten: haar energie, haar spin (hoeveel ze roteert) en haar pariteit (een label + of − voor haar spiegelsymmetrie).</p>
</div>
<div class="step">
  <h3>Van discrete niveaus naar het continuüm</h3>
  <p>De ladder links bevat de toestanden van de kern, met de energie naar boven; het venster rechts vergroot een plak van 1 MeV rond het oranje bolletje. Onderaan liggen de sporten ver uit elkaar, en elke sport is gemeten. Hoger op vermenigvuldigen de manieren om de energie over 56 nucleonen te verdelen zich, tot de sporten vervagen tot één dichte band, het continuüm.</p>
  <div class="ctl"><label for="cn-e">Excitatie-energie</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Sleep de excitatie-energie (de energie boven de laagste toestand, in MeV) en kijk naar het venster. De <b>niveaudichtheid</b> ρ, toestanden per MeV, groeit ruwweg als e<sup>2√(aE)</sup>, waarbij <i>a</i> het tempo van elke kern bepaalt: een paar per MeV bij 3 MeV, honderden rond 8 MeV (waar een neutron zou kunnen ontsnappen), miljoenen bij 20 MeV. Daarboven werkt de motor met ρ zelf.</p>
</div>
<div class="step">
  <h3>De samengestelde niveaudichtheid</h3>
  <p>De hoogte van het landschap is de niveaudichtheid op een logaritmische schaal, met de energie naar rechts. Linksonder staan de getelde niveaus. De rechte plank is de wet van de <b>constante temperatuur</b>: ρ wordt elke <i>T</i> MeV met e (ongeveer 2,7) vermenigvuldigd, waarbij <i>T</i> de kerntemperatuur is. De helling is het <b>fermigas</b>, dat de nucleonen als onafhankelijke deeltjes behandelt. Behalve voor de zwaarste trefkernen, waar hij getabelleerde dichtheden inleest, gebruikt de motor standaard dit paar.</p>
  <div class="ctl"><label for="cn-ex">Aansluitenergie</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Sleep de aansluitenergie: het verbindingspunt glijdt langs de heuvel, en de plank draait mee om er met dezelfde hoogte en helling op aan te sluiten. De twee stapels eronder vergelijken de niveaus die de plank voorspelt met de niveaus die echt geteld zijn. Maar één verbindingspunt maakt ze gelijk; daar wordt de plank groen. Dat is de energie die de motor kiest.</p>
</div>
<div class="step">
  <h3>Schileffecten en hun demping</h3>
  <p>Niveaus voor afzonderlijke nucleonen, twee nucleonen per niveau, voor twee kernen. Links een gesloten schil: alles onder een grote kloof is vol, dus elke verplaatsing betaalt voor de hele kloof. Rechts een kern midden in een schil met een half gevuld bovenste niveau, dus goedkope verplaatsingen zijn er meteen. Elke teller toont hoeveel configuraties de gegeven warmte kunnen bevatten.</p>
  <div class="ctl"><label for="cn-u">Warmte (excitatie)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Sleep de warmte omhoog en kijk hoe nucleonen springen. Bij weinig warmte heeft de gesloten schil een tekort aan configuraties; met genoeg warmte doet de kloof er niet meer toe en groeien beide tellingen gelijk op. De motor vat dit samen in één getal per kern, de <b>niveaudichtheidsparameter</b> <i>a</i>: hoe groter <i>a</i>, hoe sneller het aantal configuraties met de warmte toeneemt. De wijzers tonen het voor elke kern: ze beginnen uit elkaar en komen over ongeveer 10 MeV allebei op dezelfde gladde waarde (geschreven als <i>ã</i>, “a-tilde”), die van een kern zonder schilkloven.</p>
  <p>De motor begint dus met het schileffect van elke kern, de extra energie die zijn kloven waard zijn (geschreven als δW), en laat dat effect uitdoven naarmate de warmte stijgt.</p>
  <div class="aside">De formule: <i>a</i>(<i>U</i>) = <i>ã</i> · [1 + δW · (1 − e<sup>−γ<i>U</i></sup>) / <i>U</i>], met <i>U</i> de warmte en γ (gamma, hier ongeveer 0,1 per MeV, minder in zwaardere kernen) hoe snel het schileffect uitdooft.</div>
</div>
<div class="step">
  <h3>Spin- en pariteitsverdelingen</h3>
  <p>De toestanden bij één energie vallen in laden naar spin <i>J</i>, het impulsmoment van de kern: dichte fiches voor pariteit +, holle voor −. De middelste laden vullen zich het meest, volgens (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, waarbij de spinafsnijding σ de spreiding bepaalt. De twee pariteiten komen ongeveer gelijk uit.</p>
  <div class="ctl"><label for="cn-u2">Excitatie</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Vervorm de kern</button></div>
  <p>Sleep de excitatie omhoog: σ groeit, want een hetere kern kan meer spin dragen. Druk dan op Vervorm. Een rugbybalvormige kern kan ook als geheel roteren, dus elke la krijgt er toestanden bij (de blauwe fiches): de <b>collectieve versterking</b>. Standaard voegt de motor die alleen toe voor trefkernen zwaarder dan ongeveer 215 nucleonen.</p>
</div>
<div class="step">
  <h3>Energiebins in het continuüm</h3>
  <p>Boven het laatst getelde niveau hakt de motor het continuüm in plakken van gelijke energiebreedte, bins genoemd. In elke bin vallen de stippen samen tot één blok van ρ·ΔE toestanden (ΔE is de binbreedte), gesorteerd op spin en pariteit zoals hierboven.</p>
  <div class="ctl"><label for="cn-emax">Top van de ladder</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Opnieuw sorteren</button></div>
  <p>Sleep de top van de ladder, de meeste energie die het neutron kan meebrengen. Hetzelfde aantal bins moet meer energie bestrijken, dus elke bin wordt hoger. Het oranje bolletje valt van bin naar bin: elke latere stap (een uitgang kiezen, de fotoncascade, de tocht omlaag over de kaart) werkt op deze bins. Hier zijn er tien getekend; de motor gebruikt er tot 40.</p>
  <div class="aside">In de code: <code>density/parameters.py</code> (<i>a</i>(U) van Ignatyuk, spinafsnijding, Wigner-verdeling, collectieve versterking), <code>density/models.py</code> (constante temperatuur, fermigas, tabellen), <code>density/matching.py</code> (de aansluitenergie uit de getelde niveaus), <code>core/grids.py</code> (excitatiebins).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "er komt een neutron binnen",
    "a hot spot: the energy is still local": "een hete plek: de energie is nog lokaal",
    "equilibrium: every nucleon holds a share": "evenwicht: elk nucleon heeft een deel",
    "no trace left of where it was hit": "geen spoor meer van waar hij geraakt werd",
    // scene 2
    "ground state": "grondtoestand",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, vergroot",
    "no level in this slice": "geen niveau in deze plak",
    "{#} rung in {#} MeV": "{#} sport in {#} MeV",
    "{#} rungs in {#} MeV": "{#} sporten in {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#} sport in deze plak van {#} MeV",
    "{#} rungs in this {#}-MeV slice": "{#} sporten in deze plak van {#} MeV",
    "about {#} rungs: too close to draw": "ongeveer {#} sporten: te dicht om te tekenen",
    "about {#}k rungs: too close to draw": "ongeveer {#} duizend sporten: te dicht om te tekenen",
    "about {#}M rungs: too close to draw": "ongeveer {#} mln. sporten: te dicht om te tekenen",
    "about {#}B rungs: too close to draw": "ongeveer {#} mld. sporten: te dicht om te tekenen",
    "about {#} rungs in this slice: too close to draw": "ongeveer {#} sporten in deze plak: te dicht om te tekenen",
    "about {#} thousand rungs in this slice: too close to draw": "ongeveer {#} duizend sporten in deze plak: te dicht om te tekenen",
    "about {#} million rungs in this slice: too close to draw": "ongeveer {#} miljoen sporten in deze plak: te dicht om te tekenen",
    "about {#} billion rungs in this slice: too close to draw": "ongeveer {#} miljard sporten in deze plak: te dicht om te tekenen",
    "each one measured: energy, spin and parity": "elk gemeten: energie, spin en pariteit",
    "the rungs are multiplying": "de sporten vermenigvuldigen zich",
    "a continuum: the engine uses ρ itself": "een continuüm: de motor gebruikt ρ zelf",
    "≈ energy to free a neutron": "≈ energie om een neutron vrij te maken",
    "energy ↑": "energie ↑",
    // scene 3
    "gap: plank below the rungs": "verschil: plank onder de sporten",
    "gap: plank above the rungs": "verschil: plank boven de sporten",
    "counted levels": "getelde niveaus",
    "CT plank": "CT-plank",
    "constant-temperature plank": "plank met constante temperatuur",
    "Fermi-gas hillside": "helling van het fermigas",
    "joint {#} MeV": "verbinding {#} MeV",
    "energy →": "energie →",
    "+{#} more": "+{#} meer",
    "{#} counted": "{#} geteld",
    "{#} predicted": "{#} voorspeld",
    "{#}+ predicted": "{#}+ voorspeld",
    "equal: the plank rests on the counted rungs": "gelijk: de plank rust op de getelde sporten",
    "too few: the plank is too steep and sinks": "te weinig: de plank is te steil en zakt",
    "too many: the plank is too shallow and floats": "te veel: de plank is te vlak en zweeft",
    // scene 4
    "closed shell": "gesloten schil",
    "mid-shell": "midden in een schil",
    "gap": "kloof",
    "no arrangement holds this heat": "geen configuratie bevat deze warmte",
    "≈ {#} arrangement": "≈ {#} configuratie",
    "≈ {#} arrangements": "≈ {#} configuraties",
    "≈ {#} thousand arrangements": "≈ {#} duizend configuraties",
    "≈ {#} million arrangements": "≈ {#} miljoen configuraties",
    "≈ {#} billion arrangements": "≈ {#} miljard configuraties",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "koud: niemand kan bewegen",
    "temperature ≈ {#} MeV": "temperatuur ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "toestanden bij {#} MeV",
    "spin J →": "spin J →",
    "+ parity": "pariteit +",
    "− parity": "pariteit −",
    "rotation ×{#}": "rotatie ×{#}",
    "added by rotation: ×{#} (a few drawn)": "door rotatie toegevoegd: ×{#} (een paar getekend)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "spreiding σ ≈ {#}: de meeste toestanden rond J ≈ {#}",
    "deformed: it can rotate": "vervormd: kan roteren",
    "spherical": "sferisch",
    // scene 6
    "≈ {#} thousand": "≈ {#} duizend",
    "≈ {#} million": "≈ {#} miljoen",
    "≈ {#} billion": "≈ {#} miljard",
    "≈ {#}k": "≈ {#}k",
    "≈ {#}M": "≈ {#} mln.",
    "≈ {#}B": "≈ {#} mld.",
    "{#} bins, each {#} MeV wide": "{#} bins, elk {#} MeV breed",
    "counted": "geteld",
    "states in each bin": "toestanden per bin",
  };
  Object.assign(WT.L.labels, L);
})();
