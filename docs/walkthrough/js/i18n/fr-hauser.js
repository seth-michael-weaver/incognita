/* French: hauser (Chapitre 22, Expert) */
WT.L.ch.hauser = {
  num: "Chapitre 22", title: "Hauser–Feshbach, voie par voie", short: "Hauser–Feshbach",
  lead: "Le chapitre 9 a raconté la compétition entre les sorties sous la forme de portes. Voici la formule derrière les portes, une voie à la fois, et la correction dont elle a besoin quand seules quelques voies sont ouvertes.",
  html: `
<div class="step">
  <h3>Une transmission pour chaque voie</h3>
  <p>Une <b>voie</b> est une adresse de sortie complète : quelle particule, dans quel état reste le noyau résiduel, le moment angulaire orbital <i>l</i> et le moment total <i>j</i> = <i>l</i> ± ½ de la particule. Le modèle optique du chapitre 5 attribue à chacune un <b>coefficient de transmission</b> <i>T<sub>lj</sub></i>. Les colonnes sont celles du neutron incident, pour une cible de spin 0.</p>
  <div class="ctl"><label for="hf-e">Énergie du neutron (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>À 1 keV, seul <i>l</i> = 0 est ouvert, avec <i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>, quelques pour cent. Chaque unité supplémentaire de <i>l</i> coûte à basse énergie un facteur (<i>kR</i>)² environ : les colonnes s'ouvrent donc une à une quand l'énergie monte. Chaque colonne alimente le noyau composé avec le poids g<sub>J</sub><i>T</i> :</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>Un spin et une parité à la fois</h3>
  <p>Le moment angulaire et la parité sont conservés : le noyau composé se désexcite donc indépendamment dans chaque <i>J</i><sup>π</sup>. À l'intérieur d'un bloc, chaque voie de sortie ouverte entre en compétition avec son propre <i>T</i> : l'élastique, retour à l'état fondamental ; l'inélastique vers chaque niveau excité (une colonne additionne les (<i>l</i>, <i>j</i>) qui se couplent au même <i>J</i>) ; le continuum au-dessus de 3,6 MeV, dont les intervalles comptent pour autant de voies, pondérées par la densité de niveaux ; et la capture, regroupée en un unique <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>, minuscule. Les hauteurs sont en échelle logarithmique.</p>
  <div class="ctl"><label for="hf-j">Bloc de spin et parité</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">Énergie du neutron (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>La barre du bas est le partage de <b>Hauser–Feshbach</b> : chaque sortie prend la part <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> de ce qui est entré par la voie <i>a</i>. En dessous de 0,85 MeV, seuls l'élastique et la capture sont ouverts, et l'élastique prend presque tout.</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>Fluctuations des largeurs</h3>
  <p>La formule simple sous-estime légèrement la diffusion élastique, et la correction y ramène un peu de flux depuis les autres sorties. Voici pourquoi.</p>
  <p>Avec <i>W<sub>ab</sub></i> = 1, la formule multiplie des moyennes. Or les résonances qui se cachent derrière ces moyennes ont des largeurs dispersées (Porter–Thomas, chapitre 15) et, pour la diffusion élastique, la largeur qui laisse entrer le neutron est celle-là même qui le laisse sortir : les deux sont corrélées. Pour l'élastique, la moyenne des produits dépasse alors le produit des moyennes, et les autres sorties perdent ce que l'élastique gagne.</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">Sans correction</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">Énergie du neutron (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>Les étiquettes donnent σ avec correction divisée par σ sans correction. Sous le premier seuil inélastique, l'élastique prend déjà presque tout le flux et ne change guère, tandis que la capture perd de 10 à 25 %. Entre 1 et 1,5 MeV, l'élastique composé gagne de 15 à 35 % et le premier niveau 2⁺ perd environ un tiers. À mesure que s'ouvrent d'autres niveaux puis le continuum, l'élastique composé devient une petite part du flux : son propre facteur monte vers 2, mais ce qu'il prend aux autres diminue, et leurs facteurs reviennent vers 1. Dans la recette de Moldauer, chaque voie reçoit un nombre de degrés de liberté ν<sub>c</sub>, et <i>W</i> est une intégrale à une dimension, évaluée avec la quadrature de Gauss–Laguerre à 32 points de TALYS.</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1,78 + (T<sub>c</sub><sup>1,212</sup> − 0,78) e<sup>−0,228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer et HRTW</h3>
  <p>Les courbes reprennent le même calcul sur tout le domaine d'énergie : le rapport pour l'élastique composé, pour le premier niveau 2⁺ et pour la capture, Moldauer en trait plein et la recette <b>HRTW</b> en tirets. HRTW remplace l'intégrale par un facteur élastique <i>W<sub>a</sub></i> et des transmissions effectives <i>V<sub>a</sub></i> obtenues par itération.</p>
  <div class="ctl"><label for="hf-e4">Énergie du neutron (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>Les deux concordent étroitement pour l'élastique et l'inélastique ; pour la capture dans le domaine du keV, HRTW retire jusqu'à 10 % de plus. Entre 0,85 et 2 MeV, la capture gagne même : la largeur totale y est dominée par quelques largeurs neutroniques qui fluctuent, et la moyenne de 1/Γ dépasse 1/⟨Γ⟩. Les deux recettes sont des ajustements sur le résultat exact des matrices aléatoires (GOE), que TALYS propose aussi sous la forme d'une intégrale triple. INCOGNITA porte les trois (<code>widthmode</code> 1, 2, 3) ; Moldauer est la valeur par défaut, appliquée aux neutrons incidents jusqu'à l'énergie de séparation du neutron de la cible.</p>
</div>
<div class="step">
  <h3>Limites de l'amplification élastique</h3>
  <p>Jusqu'où l'amplification élastique peut-elle aller ? Entre deux et trois fois, selon que les résonances sont séparées ou se recouvrent.</p>
  <p>Les limites expliquent l'ampleur de l'effet. Prenons <i>N</i> voies égales sans capture, et faisons varier leur somme ΣT, qui vaut 2π fois le rapport de la largeur totale moyenne à l'espacement des niveaux, Γ/<i>D</i>. Pour des résonances isolées (ΣT ≪ 1) et de nombreuses voies, chaque largeur suit une loi de Porter–Thomas à un degré de liberté, et l'amplification élastique vaut ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3. Quand les résonances se recouvrent fortement (ΣT ≫ 2π), la section efficace fluctue comme une onde aléatoire (fluctuations d'Ericson) et l'amplification tombe à 2.</p>
  <div class="ctl"><label for="hf-n">Voies ouvertes N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>Pour <i>N</i> voies isolées, la valeur exacte est 3<i>N</i>/(<i>N</i>+2) (le losange) : avec deux voies seulement, l'amplification ne peut dépasser 1,5, car la largeur totale fluctue alors autant que la largeur élastique. La recette de Moldauer reproduit cette limite ; HRTW reste en deçà quand de nombreuses voies faibles sont ouvertes. L'encart dessine des résonances ayant la largeur qui correspond au point mobile. Dans la formule de Moldauer, la limite à grand nombre de voies est 1 + 2/ν : ν → 1 pour des résonances isolées et ν → 1,78 quand elles se recouvrent. Cela donne 2,12 en recouvrement complet au lieu de 2 : une petite erreur de l'ajustement.</p>
  <div class="aside">Dans le code : <code>compound/prepare.py</code> (les voies de sortie et leurs transmissions pour chaque <i>J</i><sup>π</sup>), <code>compound/target.py</code> (les sommes de Hauser–Feshbach), <code>compound/wfc.py</code> (Moldauer, HRTW et GOE, portés depuis TALYS). L'image évalue les mêmes formules avec des ingrédients indicatifs : des transmissions de sphère dure pour une cible semblable au fer, sept niveaux, un continuum à température constante et une seule voie de capture regroupée.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // incident T_lj
  "T = {#}": "T = {#}", "l={#}": "l={#}",
  "hollow: j = l − ½ · solid: j = l + ½": "creux : j = l − ½ · plein : j = l + ½",
  "compound nucleus": "noyau composé",
  "compound nucleus · σ(CN) ≈ {#} b": "noyau composé · σ(CN) ≈ {#} b",
  "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
  "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}", "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
  "transmission Tₗⱼ of the incident neutron": "transmission Tₗⱼ du neutron incident",
  // one J^pi block
  "elastic": "élastique", "cont.": "cont.",
  "level energy (MeV) under each column": "énergie du niveau (MeV) sous chaque colonne",
  "residual level (energy in MeV) · n×: number of (l, j) channels summed": "niveau résiduel (énergie en MeV) · n× : nombre de voies (l, j) additionnées",
  "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "bloc {#}/{#}⁺ · entrée par l = {#}, Tₐ = {#}",
  "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "bloc {#}/{#}⁻ · entrée par l = {#}, Tₐ = {#}",
  "elastic {#} %": "élastique {#} %", "higher {#} %": "supérieurs {#} %",
  "Hauser–Feshbach split: T / ΣT for each exit": "partage de Hauser–Feshbach : T / ΣT pour chaque sortie",
  // HF against WFC
  "closed": "fermé",
  "compound elastic": "élastique composé", "first {#}⁺ level": "premier niveau {#}⁺",
  "higher levels": "niveaux supérieurs", "capture": "capture",
  "{#} mb": "{#} mb",
  "with Moldauer's correction": "avec la correction de Moldauer",
  "Hauser–Feshbach without correction": "Hauser–Feshbach sans correction",
  "compound formation {#} mb at {#} keV": "formation du noyau composé {#} mb à {#} keV",
  "compound formation {#} mb at {#} MeV": "formation du noyau composé {#} mb à {#} MeV",
  // curves
  "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
  "{#}⁺ opens": "ouverture du {#}⁺", "continuum": "continuum", "continuum opens": "ouverture du continuum",
  "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "élastique ×{#} (Moldauer) · ×{#} (HRTW)",
  "capture ×{#} (Moldauer) · ×{#} (HRTW)": "capture ×{#} (Moldauer) · ×{#} (HRTW)",
  "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "premier {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
  "solid: Moldauer · dashed: HRTW": "trait plein : Moldauer · tirets : HRTW",
  "σ with correction / σ without": "σ avec correction / σ sans",
  // limits
  "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
  "elastic enhancement Wₐₐ": "amplification élastique Wₐₐ",
  "T → {#} per channel": "T → {#} par voie",
  "exact, isolated: {#}N/(N+{#}) = {#}": "exact, isolées : {#}N/(N+{#}) = {#}",
  "Porter–Thomas: {#}": "Porter–Thomas : {#}", "Ericson: {#}": "Ericson : {#}",
  "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} voies · ΣT = {#} · Wₐₐ = {#}",
  "isolated resonances: Γ ≪ D": "résonances isolées : Γ ≪ D",
  "resonances begin to overlap": "les résonances commencent à se recouvrir",
  "strongly overlapping: Γ ≫ D": "fort recouvrement : Γ ≫ D",
});
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Une recette de fluctuation des largeurs due à Hofmann, Richert, Tepel et Weidenmüller : un facteur élastique par voie et des transmissions effectives obtenues par itération.",
    more: "Comme celle de Moldauer, elle a été ajustée sur des calculs numériques de matrices aléatoires. TALYS la propose comme widthmode 2 ; Moldauer (1) est la valeur par défaut et l'intégrale triple exacte du GOE (3) la référence.",
    chapter: "hauser",
  },
  ericson: {
    term: "Fluctuations d'Ericson", aliases: ["fluctuations d'Ericson"],
    short: "Les fluctuations aléatoires d'une section efficace avec l'énergie lorsque de nombreuses résonances se recouvrent, sur une échelle d'énergie fixée par leur largeur totale moyenne.",
    more: "Elles sont la limite de fort recouvrement de la même statistique qui donne des largeurs de Porter–Thomas pour des résonances isolées. Dans cette limite, le facteur d'amplification élastique tend vers 2.",
    chapter: "hauser",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-show="jbShow" data-act="w0" data-act="w1" */
