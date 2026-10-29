/* Portuguese (pt-PT): fission (chapter 9) */
WT.L.ch.fission = {
  num: "Capítulo 12", title: "Fissão", short: "Fissão",
  lead: "Os núcleos mais pesados têm uma saída que falta aos mais leves: em vez de lançar uma partícula, o núcleo inteiro rasga-se em dois. Isto é a fissão.",
  html: `
<div class="step">
  <p>Um núcleo pesado comporta-se como uma gota de líquido carregado. A tensão superficial (setas cinzentas) mantém-na redonda; os protões, todos com carga positiva, empurram-na para se separar (setas vermelhas). No urânio, as duas forças estão quase equilibradas.</p>
  <div class="ctl"><label for="fis-d">Estica a gota</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>Arrasta para a esticar e observa o ponto na pequena curva de energia em baixo. Esticá-la acrescenta superfície, o que custa energia, mas espalha a carga, o que liberta energia. Passado o topo da curva ganha a carga: forma-se um pescoço e as metades separam-se com cerca de 200 MeV.</p>
</div>
<div class="step">
  <h3>A superfície de energia potencial</h3>
  <p>A curva é a energia de cada forma, desde redonda (esquerda) até partida (direita). Uma gota líquida lisa dá uma só colina, mas os nucleões preenchem os níveis de energia em grupos, chamados <b>camadas</b>, e nos elementos mais pesados isso escava nela um poço: uma <b>barreira de dupla bossa</b>, onde o núcleo pode demorar-se algum tempo numa forma esticada.</p>
  <p>O motor não dá esta curva por adquirida: lê-a ponto a ponto de um cálculo microscópico da energia em cada deformação (grau de estiramento).</p>
</div>
<div class="step">
  <h3>Penetração da barreira</h3>
  <p>A bola é o núcleo excitado no primeiro vale, à energia de excitação da linha tracejada laranja, abaixo do topo de 6 MeV. Segundo a física clássica nunca pode atravessar; a mecânica quântica permite-lhe passar por <b>efeito túnel</b> pela parte mais escura e proibida, com uma probabilidade <i>T</i> que cai exponencialmente à medida que essa parte engrossa.</p>
  <div class="ctl"><label for="fis-e">Energia de excitação</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>Sobe a energia e vê <i>T</i> crescer à medida que a parte proibida fica mais fina. O atalho dos manuais (Hill–Wheeler) trata o topo como uma parábola (azul tracejada). O motor segue a forma real, mais larga mais abaixo, por isso muito abaixo do topo a sua probabilidade é menor. <i>K</i> mede quanta colina há pelo meio.</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>Estados de transição</h3>
  <p>As portas no topo são os <b>estados de transição</b>, os estados quânticos do núcleo esticado sobre a barreira. Cada um tem um spin e uma paridade (0⁺, 2⁻, …) e funciona como uma porta; a sua fresta iluminada mostra quão aberta está. Um núcleo só passa por portas com o mesmo spin e paridade que ele, e cada uma abre-se aos poucos à medida que a energia ultrapassa a sua altura.</p>
  <div class="ctl"><label for="fis-e2">Energia de excitação</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">Qualquer spin</button><button class="btn ghost" data-act="jp0">Composto 0⁺</button><button class="btn ghost" data-act="jp1">Composto 1⁻</button></div>
  <p>Escolhe um spin e uma paridade: só contam as portas que coincidem, e a abertura total desce. Mais acima, as portas amontoam-se num <b>contínuo</b>, e o motor conta-as pela sua densidade, como faz com os níveis comuns.</p>
</div>
<div class="step">
  <h3>Barreiras de duplo pico</h3>
  <p>Agora as duas colinas, cada uma com a sua porta (o círculo; a parte preenchida indica quão aberta está). Os núcleos chegam da esquerda; os que atravessam a primeira colina ficam presos no poço, a ressaltar entre as portas até saírem por um lado ou pelo outro. As probabilidades combinam-se como resistências em série, por isso é a colina mais difícil que mais decide.</p>
  <div class="ctl"><label for="fis-b">Altura da colina exterior</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>Sobe a colina exterior e vê o fluxo para a fissão estrangular-se, por mais aberta que esteja a porta interior.</p>
</div>
<div class="step">
  <h3>Fissão de múltipla oportunidade</h3>
  <p>O urânio-238 absorve o neutrão e torna-se urânio-239 com excitação <i>E</i>* (linha tracejada). Se não se partir, pode emitir um neutrão; a linha desce, e o urânio-238 que fica, ainda quente, tenta a sua própria barreira: fissão de <b>segunda oportunidade</b>, (n,n′f). Os montes recolhem a forma como cada núcleo acabou.</p>
  <div class="ctl"><label for="fis-en">Energia do neutrão</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>Sobe a energia e as tentativas seguintes começam a ter êxito; uma terceira oportunidade abre-se perto dos 12 MeV. Cada nova oportunidade aparece como um degrau na <b>secção eficaz de fissão</b> medida, a probabilidade de o núcleo se partir: o pequeno gráfico no canto superior direito desenha esses degraus, com a tua energia marcada. O motor calcula com que frequência se parte, não em que fragmentos.</p>
  <div class="aside">No código: <code>fission/wkb.py</code> (o caminho da energia de deformação e os integrais WKB), <code>fission/barriers.py</code> (Hill–Wheeler, estados de transição, a densidade de níveis na barreira), <code>fission/transmission.py</code> (bossas em série, T<sub>fis</sub> por spin e paridade), <code>fission/chain.py</code> (barreiras para cada núcleo da cascata).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "a tensão superficial arredonda-a",
  "the protons push it apart": "os protões afastam-na",
  "a charged drop, nearly round": "uma gota carregada, quase redonda",
  "stretched: more surface, charge further apart": "esticada: mais superfície, carga mais afastada",
  "a neck forms": "forma-se um pescoço",
  "two fragments, carrying about {#} MeV": "dois fragmentos, com cerca de {#} MeV",
  "energy of the drop": "energia da gota",
  // landscape
  "ground state": "estado fundamental", "inner barrier": "barreira interior", "second well": "segundo poço",
  "outer barrier": "barreira exterior", "split (scission)": "partida (cisão)", "one smooth hill": "uma só colina lisa",
  "shell effects carving the second well": "os efeitos de camada escavam o segundo poço",
  "round → stretched → necked → split": "redonda → esticada → com pescoço → partida",
  "stretch (deformation) →": "estiramento (deformação) →",
  // tunnel
  "forbidden zone": "zona proibida",
  "excitation {#} MeV": "excitação {#} MeV",
  "hilltop {#} MeV": "topo {#} MeV",
  "parabola fit": "ajuste parabólico",
  "passes over the top": "passa por cima do topo",
  // gates
  "continuum: a density": "contínuo: uma densidade",
  "continuum of gates: counted as a density": "contínuo de portas: contado como densidade",
  "gates: transition states": "estados de transição",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "todas as portas: abertura total {#}",
  "all gates: total opening {#} + {#} from the continuum": "todas as portas: abertura total {#} + {#} do contínuo",
  "{#}⁺ gates only: total opening {#}": "só portas {#}⁺: abertura total {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "só portas {#}⁺: abertura total {#} + {#} do contínuo",
  "{#}⁻ gates only: total opening {#}": "só portas {#}⁻: abertura total {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "só portas {#}⁻: abertura total {#} + {#} do contínuo",
  // series
  "nuclei arriving →": "núcleos a chegar →",
  "trapped in the well": "presos no poço",
  "fission": "fissão",
  "so far: {#} through, {#} turned back": "até agora: {#} passaram, {#} voltaram atrás",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* acima da figura",
  "fission!": "fissão!",
  "emits a neutron, cools, tries again": "emite um neutrão, arrefece, tenta outra vez",
  "too cool to split: a photon, no fission": "demasiado frio para se partir: um fotão, sem fissão",
  "attempt {#}: barrier {#} % open": "tentativa {#}: barreira {#} % aberta",
  "{#}st chance (n,f)": "{#}.ª oportunidade (n,f)", "{#}nd chance (n,n′f)": "{#}.ª oportunidade (n,n′f)", "{#}rd chance (n,{#}nf)": "{#}.ª oportunidade (n,{#}nf)",
  "{#}st (n,f)": "{#}.ª (n,f)", "{#}nd (n,n′f)": "{#}.ª (n,n′f)", "{#}rd (n,{#}nf)": "{#}.ª (n,{#}nf)",
  "no fission": "sem fissão",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `porta interior T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `porta exterior T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `ambas as colinas: T ≈ ${a}, passa {#} % do que chega`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} forma real · ${b} parábola`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `probabilidade de túnel T ≈ ${a} com a forma real, ${b} com a parábola`;
    }
  }
})();
