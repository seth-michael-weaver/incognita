/* French: densities (Chapitre 24, expert: level densities, matched) */
WT.L.ch.densities = {
  num: "Chapitre 24", title: "Densités de niveaux : le raccordement", short: "Densités de niveaux",
  lead: "Le chapitre 8 raccordait une planche droite à un versant. Ce chapitre écrit les deux lois, montre comment le point de raccordement se déduit des niveaux dénombrés, et ce qui se passe quand ce point n'existe pas.",
  html: `
<div class="step">
  <h3>Le gaz de Fermi aux effets de couches amortis</h3>
  <p>La densité de niveaux par défaut du moteur, ldmodel 1, est la forme composite de <b>Gilbert–Cameron</b> : un gaz de Fermi à haute énergie, une température constante en dessous. Le gaz de Fermi n'a besoin que d'un nombre, le paramètre de densité de niveaux <i>a</i>, et à basse énergie ce nombre ressent les couches. La forme d'<b>Ignatyuk</b> laisse la correction de couches δW agir pleinement à basse excitation puis s'estomper avec un taux d'amortissement γ, si bien que <i>a</i>(<i>U</i>) tend vers la valeur lissée <i>ã</i> dès que le noyau est chaud.</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">Correction de couches δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0,01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>Les courbes du haut sont <i>a</i>(<i>U</i>)/<i>ã</i> pour plusieurs valeurs de δW ; la vôtre est en gras. En dessous figure ln ρ<sub>F</sub>. Un δW négatif (une couche fermée) réduit la densité d'un à deux ordres de grandeur, et cette réduction ne s'estompe que lentement : <i>a</i>(<i>U</i>) revient vers <i>ã</i> comme δW/<i>U</i>, si bien que même à 20 MeV un δW de −6 MeV coûte encore un facteur d'environ 40. Δ est le décalage d'appariement, 12/√A par type de nucléon apparié.</p>
</div>
<div class="step">
  <h3>Une tangente en dessous</h3>
  <p>Sous l'énergie de raccordement <i>E<sub>x</sub></i>, le gaz de Fermi est remplacé par la loi à <b>température constante</b>. Deux conditions fixent ses deux paramètres : même valeur et même pente en <i>E<sub>x</sub></i> ; la droite est donc la tangente à ln ρ<sub>F</sub> en ce point.</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">Énergie de raccordement Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Faites varier <i>E<sub>x</sub></i> et la tangente pivote : un raccordement plus haut donne un <i>T</i> plus élevé (une droite plus plate) et un <i>E</i>₀ plus bas. N'importe quel <i>E<sub>x</sub></i> donne une courbe lisse. Ce sont les niveaux dénombrés qui désignent la bonne.</p>
</div>
<div class="step">
  <h3>Trouver le raccordement à partir des niveaux dénombrés</h3>
  <p>L'escalier est le nombre de niveaux connus sous <i>E</i>, en échelle logarithmique. Intégrée, la loi à température constante donne une droite, <i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + const, qui doit reproduire le compte entre le niveau <i>N<sub>L</sub></i> et le niveau <i>N<sub>P</sub></i>, la portion du schéma de niveaux jugée complète. C'est une équation pour une seule inconnue, <i>E<sub>x</sub></i>.</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">Eₓ d'essai (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>Le panneau du bas représente <i>F</i>. Comme TALYS, le moteur parcourt un intervalle en 100 pas à la recherche d'un changement de signe, puis le resserre par dichotomie ; l'encadrement qui rétrécit montre la dichotomie. Là où <i>F</i> = 0, la droite d'essai se pose sur l'escalier.</p>
</div>
<div class="step">
  <h3>Quand il n'y a pas de raccordement</h3>
  <p>Pour une double fermeture de couches, le gaz de Fermi de basse énergie est si réduit que sa température reste basse partout, et <i>F</i> ne change jamais de signe : il n'y a pas d'énergie de raccordement. TALYS prend alors la température empirique <i>T</i> = −0,25 + 10,2/√(<i>A</i>(1 + γδW)) et cherche l'énergie où le gaz de Fermi a cette température. Près d'une double fermeture de couches, le gaz de Fermi n'atteint cette température que bien au-dessus de tout raccordement raisonnable, voire jamais ; le raccordement se rabat donc lui aussi sur des systématiques, <i>E<sub>x</sub></i> = 2,33 + 253/<i>A</i> + Δ, et <i>E</i>₀ est fixé pour que la valeur soit continue.</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">Tangente à l'énergie de repli</button></div>
  <p>La valeur est continue, mais le <i>T</i> empirique n'est pas la température du gaz de Fermi à cette énergie : la pente fait donc un saut. Avec l'entrée par défaut, cela se produit pour ²⁰⁵,²⁰⁶Tl, ²⁰⁶⁻²⁰⁹Pb et ²¹⁰Bi, avec des sauts de pente de 34 à 62 % ; prendre là le <i>T</i> du gaz de Fermi, comme TALYS le fait déjà quand <i>E<sub>x</sub></i> est donné en entrée, rétablit la tangente et modifie la capture dans la région du plomb de 20 à 30 % au plus. INCOGNITA reproduit TALYS sur ce point ; la modification a été signalée aux développeurs de TALYS. L'image est une illustration de type plomb, avec <i>ã</i> augmenté de 30 % pour que son gaz de Fermi reste sous la température empirique jusqu'à environ 24 MeV, au-delà de la recherche ; sa pente fait un saut de 62 %.</p>
</div>
<div class="step">
  <h3>L'espacement D₀ comme contrôle</h3>
  <p>À l'énergie de séparation du neutron, la densité se mesure directement : l'espacement moyen <i>D</i>₀ des résonances en onde s compte les états du seul spin et de la seule parité qu'un neutron lent peut atteindre. Pour une cible de spin 0, c'est <i>J</i><sup>π</sup> = ½⁺ uniquement.</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">Facteur sur ã</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>L'image représente un noyau composé de type fer 57 avec le <i>ã</i> global, face à la valeur mesurée de 25,4 ± 2,2 keV. Quelques pour cent sur <i>ã</i> déplacent <i>D</i>₀ de plusieurs dizaines de pour cent : là où <i>D</i>₀ est mesuré, la densité en <i>S<sub>n</sub></i> est donc bien contrainte, et là où il ne l'est pas, elle constitue la principale source d'incertitude de la capture. Les évaluations ajustent <i>a</i> sur <i>D</i>₀, et le calcul par défaut de TALYS, que suit le moteur, fait de même : pour un noyau dont le <i>D</i>₀ est mesuré, il lit un paramètre de densité de niveaux ajusté sur celui-ci, et n'utilise la formule globale que pour les autres.</p>
  <div class="aside">Dans le code : <code>density/parameters.py</code> (ã, amortissement d'Ignatyuk, appariement, coupure en spin), <code>density/models.py</code> (gaz de Fermi, température constante, tables), <code>density/matching.py</code> (la racine du raccordement, le repli empirique, les détails propres à TALYS en simple précision, reproduits). L'image utilise les paramètres globaux de TALYS pour ldmodel 1, avec des schémas de niveaux et des corrections de couches illustratifs (et, pour le cas de type plomb, <i>ã</i> × 1,3) ; le <i>D</i>₀ mesuré est la valeur RIPL pour ⁵⁷Fe.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // shared axes
  "E (MeV)": "E (MeV)", "U (MeV)": "U (MeV)", "Eₓ (MeV)": "Eₓ (MeV)", "F = {#}": "F = {#}",
  // scene 1: Ignatyuk
  "a(U) / ã": "a(U) / ã",
  "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
  "ρ_F (states per MeV), A = {#}": "ρ_F (états par MeV), A = {#}",
  "dashed: δW = {#}": "tirets : δW = {#}",
  "at {#} MeV: ×{#} against δW = {#}": "à {#} MeV : ×{#} par rapport à δW = {#}",
  "at {#} MeV: ×{#}e{#} against δW = {#}": "à {#} MeV : ×{#}e{#} par rapport à δW = {#}",
  // scene 2: tangent
  "T = {#} MeV": "T = {#} MeV", "× e": "× e",
  "joint Eₓ = {#} MeV": "raccordement Eₓ = {#} MeV",
  "E₀ = {#} MeV": "E₀ = {#} MeV",
  "Fermi gas": "gaz de Fermi", "constant temperature": "température constante",
  "ln ρ (states per MeV), A = {#}": "ln ρ (états par MeV), A = {#}",
  // scene 3: root
  "levels {#}–{#}": "niveaux {#}–{#}",
  "levels {#} to {#}: taken as complete": "niveaux {#} à {#} : jugés complets",
  "number of levels below E": "nombre de niveaux sous E",
  "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "Eₓ d'essai = {#} MeV : la droite donne {#} niveaux pour {#} dénombrés",
  "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ) : prédits moins dénombrés (échelle log signée)",
  "bisection step {#}: [{#}, {#}]": "dichotomie, étape {#} : [{#} ; {#}]",
  "root Eₓ = {#} MeV": "racine Eₓ = {#} MeV",
  // scene 4: no root
  "below: {#}/T with T = {#} MeV (Fermi-gas T)": "en dessous : {#}/T avec T = {#} MeV (T du gaz de Fermi)",
  "below: {#}/T with T = {#} MeV (empirical T)": "en dessous : {#}/T avec T = {#} MeV (T empirique)",
  "above: Fermi gas, T = {#} MeV": "au-dessus : gaz de Fermi, T = {#} MeV",
  "slope jumps by {#} % at Eₓ = {#} MeV": "la pente saute de {#} % en Eₓ = {#} MeV",
  "tangent at Eₓ = {#} MeV: no jump": "tangente en Eₓ = {#} MeV : pas de saut",
  "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ, noyau de type plomb (A = {#}, δW = {#} MeV)",
  "F changes sign: a root exists": "F change de signe : une racine existe",
  "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) n'atteint jamais zéro : pas d'énergie de raccordement",
  // scene 5: D0
  "{#} keV": "{#} keV",
  "measured {#} ± {#} keV": "mesuré {#} ± {#} keV",
  "computed D₀ = {#} keV": "D₀ calculé = {#} keV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} par MeV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} par MeV",
  "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "résonances en onde s au-dessus de Sₙ, {#} keV affichés : environ {#} niveaux",
  "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "noyau composé de type fer{#}, Sₙ = {#} MeV, spin et parité ½⁺",
});
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron"],
    short: "Une densité de niveaux composite : une loi à température constante à basse énergie, raccordée au gaz de Fermi au-delà d'une énergie de raccordement, avec même valeur et même pente au point de jonction.",
    more: "Proposée par A. Gilbert et A. G. W. Cameron en 1965. C'est le choix par défaut de TALYS et du moteur (ldmodel 1), avec le paramètre de densité de niveaux d'Ignatyuk, dépendant de l'énergie.",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "La forme d'Ignatyuk du paramètre de densité de niveaux : la correction de couches agit pleinement à basse excitation et s'estompe avec l'énergie, si bien que a(U) tend vers sa valeur lissée.",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
