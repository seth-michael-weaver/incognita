/* French: averages (Chapitre 27, Expert : des résonances aux moyennes) */
WT.L.ch.averages = {
  num: "Chapitre 27", title: "Des résonances aux moyennes", short: "Des résonances aux moyennes",
  lead: "Le chapitre 15 a tiré des séries de résonances. Les voici sous forme de sections efficaces : la formule de la matrice R, la statistique derrière les paramètres, l'effet de la température, et comment une moyenne sur de nombreuses résonances devient Hauser–Feshbach.",
  html: `
<div class="step">
  <h3>La matrice R, niveau par niveau</h3>
  <p>Sous quelques keV, dans un noyau lourd, chaque niveau du noyau composé apparaît isolément, et la section efficace s'écrit exactement en fonction des paramètres des niveaux : énergies <i>E</i><sub>λ</sub>, largeurs neutroniques réduites et largeurs de capture. Les évaluations utilisent la théorie de la <b>matrice R</b>, le plus souvent sous la forme de <b>Reich–Moore</b>, qui conserve l'interférence entre niveaux dans la voie neutron et traite les nombreuses voies de capture comme une seule largeur d'absorption.</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">Breit–Wigner à un niveau</button></div>
  <p>La courbe du haut est la section efficace totale, celle du bas la capture, pour une série de niveaux en onde s sur une cible de spin 0, semblable à l'uranium 238. Entre les niveaux, la section totale descend sous la diffusion potentielle là où les amplitudes de résonance et de potentiel s'annulent. La forme à un niveau additionne les sections efficaces des niveaux au lieu de leurs amplitudes : elle est correcte aux pics et fausse dans les creux, où les queues de nombreux niveaux s'accumulent et où la section totale peut même devenir négative.</p>
</div>
<div class="step">
  <h3>La statistique derrière les paramètres</h3>
  <p>Un noyau non mesuré n'a pas de série, seulement ses moyennes : <i>D</i>₀, la fonction de force <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ et ⟨Γ<sub>γ</sub>⟩. La théorie des matrices aléatoires fournit le reste : les espacements des niveaux de même spin et de même parité suivent la distribution de Wigner, les largeurs neutroniques réduites suivent la loi de Porter–Thomas, un χ² à un degré de liberté.</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = espacement/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">Tirer dix séries de plus</button></div>
  <p>Les histogrammes rassemblent les espacements et les largeurs de toutes les séries tirées jusqu'ici ; les courbes sont les deux lois. La largeur de capture, somme sur des centaines de voies photon, ne fluctue presque pas : on la prend donc fixe.</p>
</div>
<div class="step">
  <h3>La chaleur étale les pics</h3>
  <p>Les noyaux de la cible bougent. Un neutron d'énergie <i>E</i> les rencontre avec une dispersion d'énergies relatives de largeur Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>), et chaque résonance est vue à travers cette dispersion : c'est l'<b>élargissement Doppler</b>. Pour un niveau isolé, le résultat est la fonction ψ, une lorentzienne convoluée par une gaussienne.</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">Température (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>La résonance agrandie est la plus forte des quelques premières de la série ; le trait en tirets est sa forme à 0 K. La chaleur abaisse le pic et élargit les ailes, et l'aire sous le pic de capture reste la même. Dans un échantillon épais, ce n'est pas neutre : le pic est autoprotégé, les ailes ne le sont pas, si bien qu'un combustible plus chaud capture davantage. C'est la contre-réaction Doppler d'un réacteur.</p>
</div>
<div class="step">
  <h3>La moyenne, c'est Hauser–Feshbach</h3>
  <p>Moyennée sur de nombreuses résonances, la capture devient une fonction régulière de l'énergie. La fenêtre glisse sur la série et sa moyenne est tracée au fur et à mesure ; les courbes lisses sont la valeur de Hauser–Feshbach avec les transmissions <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> et <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>.</p>
  <div class="ctl"><label for="av-w">Largeur de la fenêtre (niveaux)</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">Une autre série</button></div>
  <p>Une fenêtre étroite donne une forte dispersion : peu de résonances, des largeurs de Porter–Thomas. Une fenêtre large se stabilise sur la courbe du bas, celle qui inclut la correction de fluctuation des largeurs. La courbe du haut, le produit des moyennes, est ici trop haute de 25 à 47 %, surtout là où ⟨Γ<sub>n</sub>⟩ vaut une à trois fois ⟨Γ<sub>γ</sub>⟩, d'environ 100 eV à 1 keV. (Avec les ondes p et davantage de voies ouvertes, la correction est plus faible.) Pour une seule voie neutron avec des largeurs de Porter–Thomas et une largeur de capture fixe, la valeur corrigée est exacte : (2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩.</p>
</div>
<div class="step">
  <h3>Résolu, non résolu, lisse</h3>
  <p>Ce qu'une mesure résout dépend de sa résolution en énergie, qui se dégrade quand l'énergie augmente. La courbe est la section efficace telle que la voit un instrument, élargie par une résolution qui croît comme <i>E</i><sup>3/2</sup>, comme en temps de vol. À basse énergie, chaque niveau est isolé et ses paramètres peuvent être ajustés : c'est le domaine des résonances résolues. Plus haut, les niveaux se fondent en une bande fluctuante dont la statistique est connue, mais pas les pics individuels : c'est le domaine non résolu, décrit par des paramètres moyens et, pour l'autoprotection, par des tables de probabilité construites à partir de séries tirées au hasard. Au-delà, Hauser–Feshbach et le modèle optique prennent le relais.</p>
  <div class="ctl"><label for="av-r">Résolution de l'instrument (relative)</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>La bibliothèque d'INCOGNITA n'a pas encore de domaine des résonances résolues. Ses courbes sont des moyennes de Hauser–Feshbach jusqu'aux plus basses énergies ; là où des résonances mesurées sont résolues, la page <a href="data.html" data-keep-lang>Tous les nucléides</a> signale que la courbe est une moyenne. Les paramètres de résonance, et les sections efficaces ponctuelles élargies par effet Doppler qui en découlent, sont en cours de développement.</p>
  <div class="aside">Dans le code : <code>physics/resonance/ladder.py</code> (espacements des matrices aléatoires, largeurs de Porter–Thomas, sections efficaces à un niveau, ensembles de séries), <code>ladder_statistics.py</code> (les lois testées sur des séries mesurées), <code>compound/wfc.py</code> (la correction de fluctuation des largeurs vers laquelle les moyennes convergent). Les formules de Reich–Moore, ψ–χ et de résolution de l'image sont évaluées ici, avec des paramètres illustratifs semblables à ceux de l'uranium 238 ; le moteur Hauser–Feshbach, et donc la bibliothèque, ne calcule pas encore de sections efficaces dans le domaine des résonances.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "{#} eV": "{#} eV", "{#} keV": "{#} keV",
  "{#}⁻¹ b": "{#}⁻¹ b", "{#}¹ b": "{#}¹ b", "{#}² b": "{#}² b", "{#}³ b": "{#}³ b", "{#}⁴ b": "{#}⁴ b",
  // Reich-Moore
  "potential scattering {#}πR′² ≈ {#} b": "diffusion potentielle {#}πR′² ≈ {#} b",
  "Reich–Moore (dashed: single-level)": "Reich–Moore (tirets : un niveau)",
  "single-level Breit–Wigner (dashed: Reich–Moore)": "Breit–Wigner à un niveau (tirets : Reich–Moore)",
  "total": "totale", "capture": "capture",
  // statistics
  "spacings: Wigner": "espacements : Wigner",
  "reduced neutron widths: Porter–Thomas": "largeurs neutroniques réduites : Porter–Thomas",
  "s = spacing / D₀": "s = espacement / D₀",
  "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
  "{#} ladders · {#} spacings": "{#} séries · {#} espacements",
  "s = {#}": "s = {#}",
  // Doppler
  "capture near the {#} eV resonance": "capture près de la résonance à {#} eV",
  "area {#} b·eV ({#} K: {#})": "aire {#} b·eV ({#} K : {#})",
  "target nuclei at {#} K": "noyaux cibles à {#} K",
  "target nuclei at rest": "noyaux cibles au repos",
  // averages
  "Hauser–Feshbach, no correction": "Hauser–Feshbach, sans correction",
  "with width fluctuations": "avec fluctuations des largeurs",
  "average capture cross section": "section efficace de capture moyenne",
  "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} niveaux autour de {#} eV : {#} b · HF {#} b sans, {#} b avec la correction",
  // regions
  "resolved": "résolu", "unresolved": "non résolu", "averaged": "moyenné",
  "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "capture mesurée avec une résolution finie · tirets : Hauser–Feshbach avec fluctuations",
  "resolution reaches D₀/{#} at {#} eV": "la résolution atteint D₀/{#} à {#} eV",
  "resolution reaches D₀/{#} at {#} keV": "la résolution atteint D₀/{#} à {#} keV",
  "time of flight: the arrival time measures the energy": "temps de vol : l'instant d'arrivée mesure l'énergie",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    for (const c of ["{#} b", "{#}k b"]) {
      L[`{#} eV · total ${b} · capture ${c}`] = `{#} eV · totale ${b} · capture ${c}`;
      L[`Γ = {#} meV · Δ = {#} meV · peak ${b} ({#} K: ${c})`] = `Γ = {#} meV · Δ = {#} meV · pic ${b} ({#} K : ${c})`;
    }
  }
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "Théorie de la matrice R", aliases: ["théorie de la matrice R", "matrice R"],
    short: "La description exacte des réactions résonnantes par des énergies de niveaux et des largeurs réduites à l'intérieur d'un rayon de voie, raccordées à des ondes libres à l'extérieur.",
    more: "Les évaluations ajustent ses paramètres sur les résonances mesurées. Les formes de Breit–Wigner à un niveau et à plusieurs niveaux, ainsi que celle de Reich–Moore, sont des approximations de la théorie complète.",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore"],
    short: "L'approximation de la matrice R utilisée dans la plupart des évaluations de noyaux lourds : les voies neutron sont traitées exactement, les nombreuses voies photon comme une seule largeur d'absorption par niveau.",
    chapter: "averages",
  },
  doppler: {
    term: "Élargissement Doppler", aliases: ["élargissement Doppler"],
    short: "L'étalement des résonances par l'agitation thermique des noyaux de la cible : le pic baisse et les ailes s'élargissent, tandis que l'aire d'un pic isolé reste la même.",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "Domaines des résonances résolues et non résolues", aliases: ["domaine des résonances résolues", "domaine non résolu"],
    short: "Sous une certaine énergie, chaque résonance est mesurée séparément (domaine résolu) ; au-dessus, seuls leurs paramètres moyens sont connus (domaine non résolu), jusqu'à ce que les moyennes deviennent lisses.",
    more: "Dans le domaine non résolu, l'autoprotection est traitée avec des tables de probabilité, des distributions de la section efficace construites à partir de séries de résonances tirées au hasard.",
    chapter: "averages",
  },
});
