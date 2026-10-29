/* Portuguese (pt-PT): tof (Capítulo 16, medições por tempo de voo) */
WT.L.ch.tof = {
  num: "Capítulo 16", title: "Medições por tempo de voo", short: "Medir picos",
  html: `
<div class="step">
  <p>O tempo de voo de um neutrão revela a sua energia. Um pulso curto de neutrões com todo o tipo de energias sai da fonte e corre por um tubo vazio até ao detetor; os rápidos chegam primeiro. O comprimento <i>L</i> do tubo é conhecido, pelo que cada tempo de chegada <i>t</i> dá a velocidade do neutrão, e a velocidade dá a sua energia:</p>
  <div class="formula">E = (72,3 · L / t)²   (E em eV, L em metros, t em microssegundos)</div>
  <p>O relógio por cima do tubo conta o tempo real desde o pulso; o voo é desenhado cerca de 1400 vezes mais lento. Por baixo do tubo, a última chegada é convertida numa energia. Arrasta o percurso de voo: um tubo mais longo espalha as mesmas energias por um tempo maior, e cada uma distingue-se com mais finura.</p>
  <div class="ctl"><label for="tof-l1">Percurso de voo (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Amostra fina: o vale reproduz a secção eficaz. Agora há uma amostra no feixe. Perto de 6,7 eV os seus núcleos têm uma ressonância e agarram neutrões (os clarões), pelo que chegam menos no instante correspondente. O gráfico compara as contagens com e sem amostra: a <b>transmissão</b>, igual a 1 quando todos os neutrões passam.</p>
  <p>Os pontos são contagens simuladas, com a sua dispersão; a linha cheia é o que o detetor regista em média; a linha tracejada é a forma da própria secção eficaz. Com uma amostra fina, o vale copia essa forma.</p>
  <div class="ctl"><label for="tof-d1">Espessura da amostra (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Amostra espessa: o vale satura. Na energia do pico, a frente da amostra apanha todos os neutrões, de modo que o centro fica negro e continua negro por mais espessa que a faças; o vale só pode crescer alargando-se para os lados. Isto é a <b>autoblindagem</b>: as camadas da frente protegem as de trás. Uma amostra espessa diz então mais sobre as asas da ressonância do que sobre o seu pico.</p>
  <div class="ctl"><label for="tof-d2">Espessura da amostra (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Pulsos mais longos, voos mais curtos: o vale esbate-se. Três coisas determinam a largura de um vale, todas escritas por baixo do gráfico: a largura própria da ressonância; os átomos da amostra a agitarem-se com o calor, o que esbate um pouco a energia de cada colisão (alargamento de <b>Doppler</b>); e o esbatimento temporal, porque um pulso mais longo ou um tubo mais curto torna cada tempo de chegada, e portanto cada energia, menos certo.</p>
  <p>Alonga o pulso ou encurta o tubo: o vale fica mais largo e mais raso, embora a fração de neutrões que remove se mantenha aproximadamente igual.</p>
  <div class="ctl"><label for="tof-p1">Largura do pulso (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Percurso de voo (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>A INCOGNITA trabalha ao contrário: pega em contagens medidas como estas e pergunta que ressonância, submetida a esta mesma experiência (espessura, calor, esbatimento temporal), as reproduz. Aqui o ajuste parte de uma estimativa cuja largura neutrónica Γ<sub>n</sub> (a força com que o nível retém neutrões) é quase quatro vezes demasiado grande (a curva azul), e altera-a passo a passo até a curva passar pelos pontos.</p>
  <p>O painel mostra a estimativa atual e o <b>desajuste</b>: cerca de 1 significa que a curva está tão perto dos pontos quanto a dispersão das contagens permite. Muda a experiência e o ajuste recomeça, com novas contagens, e acaba perto da mesma largura; onde não consegue acompanhar bem os pontos, o desajuste di-lo.</p>
  <div class="ctl"><label for="tof-l3">Percurso de voo (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Espessura da amostra (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Largura do pulso (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
