/* French: layers (chapter 12). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"][+m[2] - 1];
    return mois ? `${+m[3] === 1 ? "1er" : +m[3]} ${mois} ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} victoires, ${T.t} égalités, ${T.l} défaites"><div class="w"><b>${T.w}</b><span>victoire</span></div><div><b>${T.t}</b><span>égalité</span></div><div class="l"><b>${T.l}</b><span>défaite</span></div></div>` : "");
  const libs = LIBS.length ? `les principales bibliothèques de données évaluées (${LIBS.join(", ")})` : "les principales bibliothèques de données évaluées";
  const engineScore = TE ? ` Sur ${TE.d} de ces comparaisons, il est nettement devant dans ${TE.w}, à égalité dans ${TE.t} et derrière dans ${TE.l}.` : "";
  const terraScore = TT ? `Face à ${libs}, il est devant dans ${TT.w} comparaisons sur ${TT.d}, à égalité dans ${TT.t} et derrière dans ${TT.l}.` : `Il est comparé à ${libs}.`;

  WT.L.ch.layers = {
    num: "Chapitre 12", title: "Comment le modèle est construit en couches", short: "Couches",
    lead: "Ce que nous livrons est construit en couches au-dessus du moteur, et chaque couche doit mériter sa place face aux mesures.",
    html: `
<div class="step">
  <div class="layer-chip on">En service</div>
  <h3>Couche 1 · Une règle pour tous les noyaux</h3>
  <p>La ligne bleue est la prédiction du moteur pour une réaction. Le moteur est la couche du bas : la même physique et les mêmes réglages globaux pour tous les nucléides, sans jamais être ajusté sur les sections efficaces sur lesquelles il est jugé.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Afficher les mesures</button></div>
  <p>C'est ce qui le rend vérifiable : il est noté sur des mesures qu'il n'a jamais vues, face à d'autres codes de modèles exécutés sur les mêmes noyaux.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Testée : pas encore de gain</div>
  <h3>Couche 2 · Les mesures propres à chaque noyau</h3>
  <p>Cette couche remplace la règle globale par les valeurs mesurées de chaque noyau : son espacement des niveaux D0, ses fonctions de force S0 et S1 (la facilité avec laquelle il absorbe les neutrons lents), sa largeur gamma moyenne ⟨Γγ⟩ et ses niveaux d'énergie connus.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Règle globale</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Mesures propres</button></div>
  <p>Activez-la : la ligne bouge à peine. Les tests n'ont jusqu'ici trouvé aucun gain global : la seule variante qui aide une réaction près de son seuil dégrade la capture neutronique. Cette couche reste donc désactivée pour l'instant.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Candidate</div>
  <h3>Couche 3 · Suivre les bonnes données (TERRA)</h3>
  <p>Là où une réaction a été bien mesurée, la ligne doit suivre les mesures. La troisième couche, TERRA, fait passer la ligne du moteur par les bonnes données là où elles existent et revient au moteur là où il n'y en a pas.</p>
  <div class="ctl"><label for="lay-cov">Part du domaine d'énergie mesurée (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} La plupart sont « dans l'échantillon » : TERRA a vu ces mesures, tout comme les bibliothèques.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">En cours</div>
  <h3>Couche 4 · Des barres d'erreur honnêtes</h3>
  <p>La couche du haut place autour de la ligne une bande qui devrait contenir la vraie valeur environ deux fois sur trois (une bande à 68 %) : étroite là où de bonnes données la fixent, plus large ailleurs.</p>
  <div class="ctl"><label for="lay-band">Largeur de bande · mesures à l'intérieur (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Faites-la glisser et comptez les mesures à l'intérieur. Trop étroite, la bande promet une précision qu'elle n'a pas ; trop large, elle ne dit rien. La bande propre au moteur n'est pas encore adoptée : elle vise juste quand toutes les réactions sont regroupées, mais pas encore dans chaque famille de réactions. TERRA porte ses propres bandes, qui font partie de ses comparaisons ci-dessus.</p>
</div>
<div class="step">
  <h3>Où nous en sommes</h3>
  <p>Une couche n'est adoptée qu'après avoir été testée face aux mesures, et elle reste désactivée si elle n'aide pas. Aujourd'hui, le moteur est en service et TERRA est candidate ; la couche de structure mesurée et la bande d'incertitude du moteur sont encore en test.</p>
  <p><a href="scoreboard.html" data-keep-lang>Voir le tableau des scores complet →</a> Toutes les comparaisons que nous ne gagnons pas, chaque rival, et comment le lire.</p>
  <div class="aside">${ASOF ? `Scores au ${ASOF}, tirés du` : "Scores tirés du"} registre de recherche du projet. Les courbes de l'image sont indicatives.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · blind engine": "{#} · moteur aveugle",
  "{#} · measured structure": "{#} · structure mesurée",
  "{#} · TERRA: anchored to data": "{#} · TERRA : ancré sur les données",
  "{#} · uncertainty band": "{#} · bande d'incertitude",
  "measured here": "mesuré ici",
  "neutron energy →": "énergie du neutron →",
  "how often the reaction happens": "fréquence de la réaction",
  "hollow dots: measurements the engine never saw": "points creux : mesures que le moteur n'a jamais vues",
  "own measured values: the line barely moves": "valeurs mesurées propres : la ligne bouge à peine",
  "global rule": "règle globale",
  "no measurements: TERRA falls back to the engine": "pas de mesures : TERRA revient au moteur",
  "solid: follows the data · dashed: the engine alone": "plein : suit les données · tirets : le moteur seul",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} mesures sur {#} dans la bande (objectif : environ {#} %)",
  "no measurements to check the band against": "aucune mesure pour vérifier la bande",
});
Object.assign(WT.L.ui, { nav_board: "Tableau des scores" });
