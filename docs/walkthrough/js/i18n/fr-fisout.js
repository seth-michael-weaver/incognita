/* French: fisout (Chapitre 13, les neutrons de fission) */
WT.L.ch.fisout = {
  num: "Chapitre 13", title: "Les neutrons de fission", short: "Neutrons de fission",
  html: `
<div class="step">
  <p>Chaque fission libère deux ou trois neutrons : 2,4 en moyenne. En haut, une fission à la fois : le noyau d'uranium se déchire en deux fragments et les boules bleues s'envolent. Ce sont les neutrons <b>prompts</b>, émis en bien moins d'un millionième de seconde.</p>
  <p>Le graphique de gauche compte combien de fissions ont libéré 0, 1, 2, 3 … neutrons. Les barres sont les fissions que vous avez tirées ; le trait fin sur chaque barre est la part mesurée. Tirez-en davantage et les barres viennent se poser sur les traits.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissions</button><button class="btn ghost" data-act="f1000">1000 fissions</button></div>
</div>
<div class="step">
  <p>Ils naissent rapides : environ 2 MeV en moyenne, soit quelque 80 millions de fois l'énergie d'un neutron lent dans un réacteur à température ambiante. Le graphique de droite trie les neutrons prompts par énergie. La ligne est la forme mesurée (le spectre de Watt) : une bosse vers 1 MeV et une longue queue jusqu'à 10 MeV.</p>
  <p>De tels neutrons rapides provoquent rarement la fission suivante dans l'uranium-235 ; un réacteur commence donc par les ralentir, comme le montre un chapitre ultérieur.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissions</button><button class="btn ghost" data-act="f1000">1000 fissions</button></div>
</div>
<div class="step">
  <p>Quelques-uns arrivent des secondes plus tard : 0,65 % de tous les neutrons. Certains fragments sont si riches en neutrons que, lorsqu'ils se désintègrent plus tard, le nouveau noyau ne peut retenir l'un de ses neutrons et le laisse partir. Ce neutron doit attendre la désintégration, souvent quelques secondes.</p>
  <p>La ligne du bas est une horloge qui part de la fission, de 0,01 s à 100 s ; chaque graduation est dix fois plus tardive que la précédente. La boule de gauche représente tous les neutrons prompts, sortis d'un coup. Chaque petit point est un neutron retardé : il avance le long de la ligne pendant que son attente s'écoule, sur une horloge accélérée 20 fois, et se pose là où il est finalement sorti. Ces quelques neutrons tardifs sont ce qui rend un réacteur pilotable : ils ralentissent la réponse de la chaîne, des millièmes de seconde aux secondes.</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 fissions</button><button class="btn ghost" data-act="clear">Effacer</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "n + U{#} → two fragments + neutrons": "n + U{#} → deux fragments + neutrons",
  "prompt neutrons per fission": "neutrons prompts par fission",
  "lines: measured shares": "traits : parts mesurées",
  "mean {#}": "moyenne {#}",
  "prompt-neutron energy (MeV)": "énergie des neutrons prompts (MeV)",
  "mean {#} MeV": "moyenne {#} MeV",
  "line: measured shape": "ligne : forme mesurée",
  "prompt": "prompts",
  "time after fission · clock sped up {#}×": "temps après la fission · horloge accélérée {#}×",
  "delayed {#} of {#} ({#} %)": "retardés {#} sur {#} ({#} %)",
  "{#} fissions": "{#} fissions",
});
