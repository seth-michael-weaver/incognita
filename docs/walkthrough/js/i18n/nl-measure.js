/* Dutch (Nederlands): measure (Hoofdstuk 11, wat eruit komt) */
WT.L.ch.measure = {
  num: "Hoofdstuk 11", title: "Wat eruit komt", short: "Observabelen",
  lead: "Een experiment, een reactor of een ster ziet maar een handvol getallen. Dit hoofdstuk laat zien hoe de motor wat er in de kern gebeurt in die getallen omzet.",
  html: `
<div class="step">
  <p>De bleke schijf rond elke kern is haar <b>werkzame doorsnede</b>: het oppervlak dat een neutron moet raken om een reactie te laten plaatsvinden, niet de echte grootte van de kern. Van links komt een bundel door een dunne folie van kernen; het deel dat reageert is dat oppervlak maal het aantal kernen dat de bundel tegenkomt. De eenheid is de barn (10⁻²⁴ cm², ongeveer het vooraanzicht van een uraniumkern).</p>
  <div class="ctl"><label for="mea-e">Neutronenergie (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Verlaag de energie en de schijven zwellen op: een langzaam neutron is een brede golf en reageert van verder weg. Bij hoge energie krimpt de schijf naar de kern zelf.</p>
</div>
<div class="step">
  <h3>Met de energie gaan nieuwe uitgangen open</h3>
  <p>Elke deur is één uitgang, of <b>kanaal</b>: het neutron kaatst eruit (elastisch), laat de trefkern aangeslagen achter (n′), stoot meer neutronen uit (2n, 3n), wordt ingevangen terwijl alleen fotonen vertrekken (γ), of er vertrekt in plaats daarvan een proton of α-deeltje. Een deur met een hangslot heeft een <b>drempel</b>: de reactie kost meer energie dan het neutron meebrengt.</p>
  <div class="ctl"><label for="mea-e2">Neutronenergie (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Sleep de energie voorbij een drempel en die deur flitst open; de emmers vullen zich tot het aandeel van elk kanaal, en elke nieuwe deur neemt aandeel af van de andere. De drempels komen uit de massa's van de kernen; de aandelen uit de competitie van hoofdstuk 6.</p>
</div>
<div class="step">
  <h3>Wat een detector ziet</h3>
  <p>De twee stapels zijn de neutronen die de voorste en achterste helft van een detectorring bereiken, gesorteerd op energie. De bundel is gepulst, dus de vliegtijd van elk neutron geeft zijn energie: snelle komen het eerst aan.</p>
  <div class="ctl"><label for="mea-ein">Invallende energie (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Beide stapels hebben een bult van langzame, <b>verdampte</b> neutronen: die koken van de compoundkern af zodra de energie verdeeld is, in alle richtingen gelijk. Alleen de voorste stapel heeft een lange snelle staart: neutronen uit het <b>pre-evenwicht</b>, die al bij de eerste botsingen vertrekken en nog ruwweg met de bundel mee bewegen. Verhoog de invallende energie en de staart groeit.</p>
</div>
<div class="step">
  <h3>Welke kant ze op gaan</h3>
  <p>Het bloemblad toont hoeveel neutronen in elke richting vertrekken; de bundel komt van links. Verdampte neutronen zijn de bundel vergeten en vertrekken alle kanten even veel op; snelle neutronen uit het pre-evenwicht hellen naar voren. De regel van Kalbach bepaalt hoe ver, met één helling <i>a</i> die groeit met de uitgaande energie. De motor kan deze hoekverdelingen ook wegschrijven, als optionele uitvoer.</p>
  <div class="ctl"><label for="mea-eo">Uitgaande energie (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Verlaag de uitgaande energie en het bloemblad wordt ronder: langzame neutronen zijn vooral verdampt.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>In een ster</h3>
  <p>De stapel eronder verzamelt de energieën van neutronen die in het hete gas van een ster worden ingevangen. Hun snelheden volgen een maxwellverdeling die door de temperatuur <i>kT</i> wordt bepaald (30 keV is ongeveer 350 miljoen graden); langere sporen betekenen snellere neutronen, en elke passage langs een kern kan eindigen in een vangstflits.</p>
  <div class="ctl"><label for="mea-kt">Temperatuur kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Langzame neutronen zijn makkelijk te vangen maar komen zelden langs, en snelle zijn er weinig, dus de meeste vangsten komen uit een venster van een paar <i>kT</i> breed. De snelheid over het hele gas is de <b>maxwelliaans gemiddelde werkzame doorsnede</b> (MACS), in millibarn (mb). Verhit het gas en het venster schuift naar hogere energie, waar het doel kleiner is. De MACS wordt berekend uit de vangstcurve van de motor.</p>
</div>
<div class="step">
  <h3>Ook de trefkern is heet</h3>
  <p>De bolletjes tonen welk deel van de trefkernen bij deze temperatuur op elk van hun laagste niveaus zit. In een ster zijn sommige trefkernen al aangeslagen, en elk aangeslagen niveau is een andere ingang naar dezelfde compoundkern. Een niveau met spin <i>J</i> bevat er meer omdat het 2<i>J</i>+1 oriëntaties heeft.</p>
  <div class="ctl"><label for="mea-kt2">Temperatuur kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Verhoog de temperatuur en kijk hoe kernen omhoog schuiven. Een stellaire snelheid berekent de vangst vanuit elk bezet niveau en telt de resultaten met deze aandelen op; de gewichten tellen op tot de partitiefunctie <i>G</i>, en de verhouding tot de snelheid vanuit de grondtoestand is de <b>stellaire versterkingsfactor</b>. De motor kan dit als optie doen, standaard uit; normaal begint elke trefkern in zijn grondtoestand.</p>
</div>
<div class="step">
  <h3>Hoe zeker is dit allemaal?</h3>
  <p>Elke vage schijf is één run van de motor waarin de invoer willekeurig is bijgesteld: de diepte van de optische put, de niveaudichtheid en de fotonsterkte, die elk maar tot op een paar procent bekend zijn. De spreiding van veel runs is een eerlijke onzekerheid: <b>Total Monte Carlo</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Draai een variant</button><button class="btn ghost" data-act="tmc">Draai er 10</button><button class="btn ghost" data-act="clear">Wissen</button></div>
  <p>Een scherpe rand betekent dat de invoer het antwoord vastlegt; een vage rand betekent dat dat niet zo is, en daar zouden nieuwe metingen het meest helpen.</p>
  <div class="aside">In de code: <code>emission/channels.py</code> (exclusieve kanalen en restkernen), <code>specout.py</code> en <code>specang.py</code> (uitgaande spectra, hoekverdelingen en dubbel-differentiële werkzame doorsneden, alleen weggeschreven als erom gevraagd wordt), <code>astro/stellar.py</code> (vangst vanuit thermisch bezette niveaus van de trefkern, optioneel), <code>tmc.py</code> (de Total Monte Carlo-sampler). MACS vanuit de grondtoestand worden berekend uit de vangstcurven in <code>validation/differential/core.py</code>.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "elke schijf: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "elke schijf: werkzame doorsnede σ ≈ {#} b, het oppervlak dat een neutron moet raken",
  "beam →": "bundel →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "eigen vooraanzicht kern ≈ {#} b · {#} % reageert",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "het eigen vooraanzicht van de kern ≈ {#} b · {#} % van de bundel reageert in deze folie",
  "slow: the neutron's wave reaches well past the surface": "langzaam: de golf van het neutron reikt ver voorbij het oppervlak",
  "the target still looks bigger than the nucleus": "het doel lijkt nog groter dan de kern",
  "fast: close to the nucleus's own size": "snel: dicht bij de eigen grootte van de kern",
  // doors
  "elastic": "elastisch", "n′ inelastic": "n′ inelastisch", "{#}n": "{#}n", "γ capture": "γ-vangst", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ inelastisch · {#} MeV",
  "opens at {#} MeV": "opent bij {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "voorste helft", "backward half": "achterste helft",
  "pulsed beam": "gepulste bundel", "pulsed beam →": "gepulste bundel →",
  "backward": "achter", "backward detectors": "achterste detectoren",
  "forward": "voor", "forward detectors": "voorste detectoren",
  "outgoing neutron energy from the flight time (MeV) →": "uitgaande neutronenergie uit de vliegtijd (MeV) →",
  "fast tail": "snelle staart", "fast tail: pre-equilibrium": "snelle staart: pre-evenwicht",
  "evaporated hump": "verdampte bult", "hump: evaporated, every way alike": "bult: verdampt, alle kanten gelijk",
  "{#} % leave before the energy is shared": "{#} % vertrekt voordat de energie verdeeld is",
  // angle
  "beam": "bundel",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "verhouding voor/achter ≈ {#}  ·  helling a ≈ {#}",
  "mostly evaporated: every direction alike": "vooral verdampt: alle richtingen gelijk",
  "a mix: the fast share leans forward": "een mengsel: het snelle deel helt naar voren",
  "mostly pre-equilibrium: strongly forward": "vooral pre-evenwicht: sterk naar voren",
  "forward →": "voor →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "energieën van ingevangen neutronen",
  "each capture drops here, by the neutron's energy: the window that counts": "elke vangst valt hier, naar de energie van het neutron: het venster dat telt",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb bij kT = {#} keV · bekeken vangsten: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  grondtoestand", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "niveaus van de trefkern, met het deel van de kernen op elk niveau",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#} % begint in de grondtoestand · partitiefunctie G ≈ {#}",
  // TMC
  "optical well": "optische put", "optical well depth": "diepte optische put",
  "level density": "niveaudichtheid", "photon strength": "fotonsterkte",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "gestippeld: beste invoer · elke schijf op eigen schaal",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "gestippelde ring: invoer met beste waarden · elke energie op eigen schaal (schijfoppervlak ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} runs van de motor, elk met willekeurig bijgestelde invoer",
});
