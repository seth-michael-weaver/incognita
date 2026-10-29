/* Portuguese (pt-PT): xsec (Capítulo 2, secção eficaz) */
WT.L.ch.xsec = {
  num: "Capítulo 2", title: "O que é uma secção eficaz?", short: "Secção eficaz",
  html: `
<div class="step">
  <p>Cada disco é a área-alvo de um núcleo: a sua <b>secção eficaz</b>, escrita σ (sigma). A imagem olha de cima para uma folha fina de núcleos, enquanto neutrões chovem sobre ela em pontos aleatórios. Um neutrão que cai dentro de um disco reage com esse núcleo (um clarão laranja); um que cai entre os discos passa direto (limita-se a desvanecer).</p>
  <p>Assim, a fração que reage é simplesmente a fração da folha coberta pelos discos. O pequeno quadrado preto é a unidade de área, um <b>barn</b>, 10⁻²⁴ cm²: a face real de um núcleo mede cerca de um barn.</p>
  <div class="ctl"><label for="xs-e1">Energia do neutrão (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Os neutrões mais lentos veem alvos maiores. O disco não é o tamanho real do núcleo: é o tamanho com que o núcleo atua para um neutrão a esta energia, e um neutrão lento demora-se mais perto do núcleo, pelo que é mais provável ser capturado. Na captura, isto faz σ crescer como 1/velocidade.</p>
  <p>A curva sob a folha é σ em todas as energias (ambas as escalas são logarítmicas); o ponto laranja marca a energia escolhida. Arrasta até aos neutrões mais lentos e vê os discos crescerem e a fração que reage subir.</p>
  <div class="ctl"><label for="xs-e2">Energia do neutrão (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Numa ressonância, o alvo incha. A 7 eV, o neutrão mais o núcleo têm exatamente a energia de um dos níveis do próprio núcleo, e por isso é absorvido com muito mais facilidade: o disco cresce cerca de cinquenta vezes em área, aqui até cerca de 400 barns.</p>
  <p>Afasta-te um pouco dos 7 eV e o disco encolhe logo: o pico da curva é estreito. Os núcleos reais têm muitos picos destes; o Capítulo 1 mostrou o seu código de barras.</p>
  <div class="ctl"><label for="xs-e3">Energia do neutrão (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};
