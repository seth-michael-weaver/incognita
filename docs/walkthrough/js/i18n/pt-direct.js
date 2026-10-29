/* Portuguese (pt-PT): direct (Capítulo 6, reações diretas) */
WT.L.ch.direct = {
  num: "Capítulo 6", title: "Reações diretas", short: "Reações diretas",
  lead: "Nem todo o neutrão que chega ao núcleo é engolido. Alguns roçam a sua superfície, dão-lhe um empurrão e continuam a voar.",
  html: `
<div class="step">
  <p>Um neutrão que apenas roça o núcleo pode empurrá-lo uma vez para um nível excitado e seguir viagem, quase sempre para a frente e só um pouco mais lento. Isso é uma <b>reação direta</b>: um só passo, que termina em cerca de 10⁻²² segundos. Aqui um neutrão passa a uma distância <i>b</i>, o <b>parâmetro de impacto</b>, em raios nucleares <i>R</i>; o anel pontilhado é a pele do núcleo.</p>
  <div class="ctl"><label for="di-b">Pontaria b (em raios)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Arrasta <i>b</i>. Abaixo de cerca de 0,8 o neutrão é engolido. Perto de 1 roça o núcleo e deixa-o no seu primeiro nível excitado, 2⁺. Acima de cerca de 1,2 falha e apenas se desvia: <b>dispersão elástica</b>, com o núcleo intacto.</p>
</div>
<div class="step">
  <h3>Excitação rotacional de núcleos deformados</h3>
  <p>Um empurrão põe a rodar um núcleo esticado (capítulo 1) e fá-lo subir a escada da sua <b>banda rotacional</b>: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. O neutrão pode empurrar o núcleo para cima e o núcleo pode devolver o empurrão, por isso nenhum nível pode ser calculado isoladamente. O motor resolve-os todos ao mesmo tempo: <b>canais acoplados</b>, em que cada canal é um resultado, aqui um nível da banda.</p>
  <div class="btns"><button class="btn" data-act="kick">Subi-lo um nível</button><button class="btn ghost" data-act="rpause">Pausa / continuar</button></div>
  <div class="ctl"><label for="di-beta">Deformação β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>Os arcos mostram que níveis estão ligados: <i>λ</i> = 2, o estiramento global, liga vizinhos; <i>λ</i> = 4, uma saliência mais fina, salta dois. Arrasta <i>β₂</i>: um núcleo mais esticado liga os seus níveis com mais força, e os arcos engrossam. Como a banda é resolvida em conjunto com o neutrão incidente, o motor sabe exatamente quantos neutrões ela leva, e passa só o resto às vias mais lentas dos capítulos seguintes.</p>
</div>
<div class="step">
  <h3>Vibrações de superfície</h3>
  <p>Um núcleo redondo pode ondular, e a energia da ondulação vem em pacotes iguais chamados <b>fonões</b>. Um fonão da ondulação bola–disco (<i>λ</i> = 2) dá o nível 2⁺; dois dão três níveis, 0⁺, 2⁺ e 4⁺, ao dobro da energia. Chegar a eles exige dois empurrões seguidos. O motor resolve estes níveis juntamente com o estado fundamental.</p>
  <div class="ctl"><label for="di-lam">Forma da ondulação λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Um fonão</button><button class="btn ghost" data-act="ph2">Dois fonões</button></div>
  <p>Põe <i>λ</i> = 3 para uma ondulação em forma de pera, cujo primeiro nível é 3⁻. Carrega nos botões para juntar um ou dois fonões.</p>
</div>
<div class="step">
  <h3>Reações diretas num só passo</h3>
  <p>Para a maioria dos níveis a ligação é fraca e basta um empurrão: a <b>DWBA</b> (aproximação de Born de ondas distorcidas). A onda incidente do capítulo 5 empurra o núcleo uma vez, na orla, onde o potencial cai de profundo para zero; a orla brilha onde as cristas batem. A onda circular que se espalha são os neutrões que deixaram o núcleo excitado.</p>
  <div class="ctl"><label for="di-bd">Deformação do nível β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Arrasta <i>β</i>: a orla treme mais e os círculos brilham mais, como <i>β</i>²: o dobro da deformação, quatro vezes mais. O motor tira o <i>β</i> de cada nível de valores medidos, ou de sistemáticas quando não é conhecido. A forma como os neutrões dispersos se repartem pelos ângulos é uma saída extra opcional.</p>
</div>
<div class="step">
  <h3>Ressonâncias gigantes</h3>
  <p>Todos os nucleões podem mover-se em conjunto: respirar, achatar-se e esticar-se, ou oscilar para uma forma de pera. São as <b>ressonâncias gigantes</b>. Neste núcleo de massa média situam-se entre cerca de 7 e 25 MeV, cada uma com vários MeV de largura, demasiado largas para contarem como um só nível; as bossas marcam a <b>energia de excitação</b> de cada uma.</p>
  <p>O motor fixa a intensidade total de cada uma através de uma <b>regra de soma</b>, um limite imposto pela física básica à força com que um núcleo pode responder, e reparte-a como uma bossa acima do último nível conhecido. Estas bossas, mais os empurrões para níveis altos, formam o <b>contínuo coletivo</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Respiração</button><button class="btn ghost" data-act="quad">Achatamento</button><button class="btn ghost" data-act="oct">Pera</button></div>
  <p>A mais conhecida, com os protões a oscilar contra os neutrões (a ressonância gigante dipolar), sobretudo absorve e emite luz, por isso pertence ao capítulo 10.</p>
</div>
<div class="step">
  <h3>Captura direta</h3>
  <p>Um neutrão livre pode cair diretamente numa <b>órbita</b> vazia do poço (uma energia permitida para um neutrão lá dentro) e enviar a energia que sobra como um <em class="g">fotão</em>. O núcleo nunca aquece. Isto é a <b>captura direta</b>. O motor pode calculá-la com o mesmo poço do capítulo 5: a onda livre fora, a órbita ligada dentro e o fotão que as liga. É opcional e está desligada por defeito.</p>
  <div class="btns"><button class="btn" data-act="drop">Deixar cair um neutrão</button></div>
  <p>A captura direta importa sobretudo onde a via habitual, repartir a energia do neutrão, é fraca: núcleos leves e núcleos longe da estabilidade, com poucos níveis e muito espaçados.</p>
</div>
<div class="step">
  <h3>Fluxo direto versus composto</h3>
  <p>O motor reparte a secção eficaz de reação do capítulo 5 por ordem: primeiro as reações diretas, depois as colisões rápidas, e só o que resta forma um núcleo composto. Na imagem cada neutrão tem um de três destinos: <b>direto</b> (roça e segue), rápido (arranca um nucleão antes de a energia se repartir: <b>pré-equilíbrio</b>, capítulo 7) ou engolido (um <b>núcleo composto</b>, capítulo 8). Os montes contam-nos.</p>
  <div class="ctl"><label for="di-e">Energia do neutrão (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrasta a energia e vê os montes a encherem-se de novo. A alguns MeV quase todos os neutrões são engolidos. A dezenas de MeV, as reações diretas e as colisões rápidas juntas levam uma grande parte.</p>
  <div class="aside">No código: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (potencial deformado, canais acoplados para rotores e vibradores), <code>ecis/dwba.py</code> e <code>direct/dwba.py</code> (empurrão único, ressonâncias gigantes, contínuo coletivo), <code>direct/racapcalc.py</code> (captura direta, opcional, desligada por defeito), <code>compound/normalization.py</code> (a contabilidade).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "pele (superfície)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "absorvido: a sua energia reparte-se por todos os nucleões",
  "{#}⁺ level": "nível {#}⁺",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "um empurrão deixa o núcleo em {#}⁺; o neutrão segue",
  "a miss: deflected, nucleus unchanged (elastic)": "falha: desviado, núcleo intacto (elástica)",
  // scene: rotor
  "at rest: {#}⁺": "em repouso: {#}⁺",
  "rotating: {#}⁺": "a rodar: {#}⁺",
  "rotating: {#}⁺ (paused)": "a rodar: {#}⁺ (em pausa)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "níveis resolvidos em conjunto",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "ondulação quadrupolar: bola ↔ disco",
  "octupole ripple: pear ↔ pear": "ondulação octupolar: pera ↔ pera",
  "{#}⁺  no phonon": "{#}⁺  sem fonão",
  "{#}⁺  one phonon": "{#}⁺  um fonão",
  "{#}⁻  one phonon": "{#}⁻  um fonão",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  dois fonões",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  dois fonões",
  "one push": "um empurrão",
  "two pushes": "dois empurrões",
  "two phonons": "dois fonões",
  "equal energy steps": "degraus de energia iguais",
  // scene: DWBA
  "rim: the push happens here": "orla: o empurrão dá-se aqui",
  "incoming wave": "onda incidente",
  "outgoing: nucleus left excited": "emergente: núcleo excitado",
  "outgoing circles: the nucleus left on an excited level": "círculos emergentes: o núcleo ficou num nível excitado",
  "push strength ∝ β²: {#}× that at β = {#}": "força do empurrão ∝ β²: {#}× a de β = {#}",
  // scene: giant resonances
  "breathing": "respiração",
  "squash and stretch": "achatar e esticar",
  "pear": "pera",
  "breathing (monopole)": "respiração (monopolo)",
  "squash and stretch (quadrupole)": "achatar e esticar (quadrupolo)",
  "pear-shaped (octupole), low and high": "em forma de pera (octupolo), baixa e alta",
  "about {#} MeV up": "a cerca de {#} MeV",
  "last known level": "último nível conhecido",
  "excitation energy (MeV) →": "energia de excitação (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "livre: fora do núcleo",
  "empty orbit": "órbita vazia",
  "drops straight in; a photon carries off the spare energy": "cai diretamente; um fotão leva a energia que sobra",
  // scene: ledger
  "direct": "direta",
  "fast (pre-eq.)": "rápida (pré-eq.)",
  "compound": "composto",
  "direct: grazed, flew on": "direta: roçou e seguiu",
  "fast collision: one out at once": "colisão rápida: um sai logo",
  "compound: swallowed": "composto: engolido",
  "{#}% (model {#}%)": "{#}% (modelo {#}%)",
  "{#}% seen · model {#}%": "{#}% visto · modelo {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "neutrões de {#} MeV num núcleo de massa média (frações ilustrativas)",
});
