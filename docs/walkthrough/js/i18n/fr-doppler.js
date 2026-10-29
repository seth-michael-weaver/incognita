/* French: doppler (Chapitre 19, élargissement Doppler) */
WT.L.ch.doppler = {
  num: "Chapitre 19", title: "Élargissement Doppler", short: "Doppler",
  html: `
<div class="step">
  <h3>L'agitation thermique de la cible</h3>
  <p>Un combustible plus chaud : ses atomes s'agitent plus vite. Chaque atome d'uranium n'est plus immobile quand un neutron arrive.</p>
  <div class="ctl"><label for="dop-t1">Température du combustible (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>L'élargissement Doppler</h3>
  <p>La courbe est la probabilité que l'uranium-238 capture un neutron, tracée en fonction de l'énergie du neutron. Sa hauteur est une surface cible en <b>barns</b> (un barn vaut 10<sup>−24</sup> cm², à peu près la taille qu'un noyau présente à un neutron). Comme les atomes bougent, certains rencontrent le neutron de plein fouet et d'autres s'enfuient devant lui : l'étroit pic est donc étalé, plus bas et plus large. Son aire reste la même.</p>
  <div class="ctl"><label for="dop-t2">Température du combustible (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>L'autoprotection des résonances</h3>
  <p>Une pastille de combustible est épaisse. La bande ombrée est la part des neutrons qu'elle arrête à chaque énergie. Le centre du pic arrête déjà tout, à chaud comme à froid, donc un pic plus bas n'y perd rien ; les ailes plus larges, elles, captent davantage. Plus de neutrons sont perdus par capture au lieu de provoquer des fissions, si bien que <i>k</i> diminue de lui-même. (<i>k</i> est le nombre de nouvelles fissions auquel mène chaque fission ; le chapitre <a href="#critical">21</a> l'explique.)</p>
  <div class="ctl"><label for="dop-t3">Température du combustible (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "atomes d'uranium dans le combustible",
  "{#} K": "{#} K",
  "caught in the peak": "captés dans le pic",
  "k": "k",
  "neutron energy (eV) →": "énergie du neutron (eV) →",
  "capture cross section": "section efficace de capture",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "pic {#}k barns · largeur Doppler {#} meV · aire inchangée",
  "all stopped": "tous arrêtés",
  "wider wings catch more": "les ailes plus larges captent plus",
  "share of neutrons stopped in the fuel": "part des neutrons arrêtés dans le combustible",
  "the peak's centre already stops everything; the wider wings catch more": "le centre du pic arrête déjà tout ; les ailes plus larges captent plus",
});
