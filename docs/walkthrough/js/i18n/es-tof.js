/* Spanish: tof (Chapter 17, time-of-flight measurements) */
WT.es.ch.tof = {
  num: "Capítulo 17", title: "Mediciones por tiempo de vuelo", short: "Medir picos",
  html: `
<div class="step">
  <p>El tiempo de vuelo de un neutrón revela su energía. Un pulso corto de neutrones de todas las energías sale de la fuente y corre por un tubo vacío hasta el detector; los rápidos llegan primero. La longitud del tubo <i>L</i> se conoce, así que cada tiempo de llegada <i>t</i> da la velocidad del neutrón, y la velocidad da su energía:</p>
  <div class="formula">E = (72,3 · L / t)²   (E en eV, L en metros, t en microsegundos)</div>
  <p>El reloj sobre el tubo cuenta el tiempo real desde el pulso; el vuelo se dibuja unas 1400 veces más lento. Bajo el tubo, la última llegada se convierte en una energía. Arrastra la distancia de vuelo: un tubo más largo reparte las mismas energías en más tiempo, así que se distingue cada una con más finura.</p>
  <div class="ctl"><label for="tof-l1">Distancia de vuelo (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Muestra delgada: la caída dibuja la sección eficaz. Ahora hay una muestra en el haz. Cerca de 6,7 eV sus núcleos tienen una resonancia y atrapan neutrones (los destellos), así que llegan menos a la hora correspondiente. El gráfico compara los recuentos con y sin muestra: la <b>transmisión</b>, que vale 1 cuando todos los neutrones pasan.</p>
  <p>Los puntos son recuentos simulados, con su dispersión; la línea continua es lo que el detector registra en promedio; la línea discontinua es la forma de la propia sección eficaz. Con una muestra delgada, la caída copia esa forma.</p>
  <div class="ctl"><label for="tof-d1">Espesor de la muestra (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Muestra gruesa: la caída se satura. En la energía del pico, la parte delantera de la muestra atrapa todos los neutrones, así que el centro se vuelve negro y sigue negro por grueso que lo hagas; la caída solo puede crecer ensanchándose hacia los lados. Esto es el <b>autoapantallamiento</b>: las capas delanteras protegen a las traseras. Una muestra gruesa informa entonces más sobre las alas de la resonancia que sobre su pico.</p>
  <div class="ctl"><label for="tof-d2">Espesor de la muestra (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Pulsos más largos, vuelos más cortos: la caída se difumina. Tres cosas fijan la anchura de una caída, todas escritas bajo el gráfico: la anchura propia de la resonancia; los átomos de la muestra agitándose con el calor, que emborrona un poco la energía de cada colisión (ensanchamiento <b>Doppler</b>); y el borrón de la medida del tiempo, porque un pulso más largo o un tubo más corto hace cada tiempo de llegada, y por tanto cada energía, menos precisa.</p>
  <p>Alarga el pulso o acorta el tubo: la caída se hace más ancha y menos profunda, aunque la fracción de neutrones que retira se mantiene más o menos igual.</p>
  <div class="ctl"><label for="tof-p1">Anchura del pulso (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Distancia de vuelo (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA trabaja al revés: toma recuentos medidos como estos y pregunta qué resonancia, sometida a este mismo experimento (espesor, calor, borrón temporal), los reproduce. Aquí el ajuste parte de una suposición cuya anchura neutrónica Γ<sub>n</sub> (con qué fuerza retiene el nivel a los neutrones) es casi cuatro veces demasiado grande (la curva azul), y la cambia paso a paso hasta que la curva pasa por los puntos.</p>
  <p>La lectura muestra la suposición actual y el <b>desajuste</b>: cerca de 1 significa que la curva está tan cerca de los puntos como permite su dispersión de recuento. Cambia el experimento y el ajuste vuelve a empezar, con recuentos nuevos, y llega a una anchura casi igual; donde no consigue igualar bien los puntos, el desajuste lo dice.</p>
  <div class="ctl"><label for="tof-l3">Distancia de vuelo (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Espesor de la muestra (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Anchura del pulso (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
