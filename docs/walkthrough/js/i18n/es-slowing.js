/* Spanish: slowing (Chapter 19, neutron moderation) */
WT.es.ch.slowing = {
  num: "Capítulo 19", title: "Moderación de neutrones", short: "Frenado",
  html: `
<div class="step">
  <p>Cada rebote contra el hidrógeno cuesta cerca de la mitad de la energía. Un neutrón de fisión empieza con 2 MeV y rebota por el agua. Un núcleo de hidrógeno pesa lo mismo que el neutrón, así que, como las bolas de billar, cada rebote le quita en promedio la mitad de la energía al neutrón.</p>
  <p>El gráfico traza la energía del neutrón tras cada rebote; cada rótulo a lo largo del lateral es mil veces menos energía. Perder la misma fracción cada vez da un descenso en línea recta, la línea discontinua. Tras unos 18 rebotes el neutrón alcanza la energía <b>térmica</b>, 0,025 eV, en la que el agua caliente lo acelera tantas veces como lo frena. El oxígeno es 16 veces más pesado: cada rebote quita solo un poco, y hacen falta más de cien.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Hidrógeno</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Oxígeno</button><button class="btn" data-act="again">Disparar otra vez</button></div>
</div>
<div class="step">
  <p>Por debajo de 1 eV aproximadamente, los enlaces de la molécula dan forma a cada rebote. Cada hidrógeno está atado a su oxígeno (las líneas brillantes). Un neutrón lento ya no golpea un hidrógeno libre: golpea una molécula entera, 18 veces más pesada, así que un rebote simple casi no quita nada.</p>
  <p>También puede hacer que la molécula gire o vibre, pero solo cediéndole una cantidad fija de energía cada vez, 0,06, 0,2 o 0,45 eV (los destellos brillantes). Las moléculas calientes a veces devuelven una cantidad así. En el gráfico, la banda sombreada bajo 1 eV es donde esto importa. Desactiva el enlace para comparar con el hidrógeno libre.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Enlace químico</button><button class="btn" data-act="again">Disparar otra vez</button></div>
</div>
<div class="step">
  <p>Un código de ordenador necesita todo esto como una tabla: la <b>ley de dispersión</b>, el mapa. A lo ancho: la fuerza del golpe, α (el empujón que recibe la molécula; pequeño en un roce, grande en un impacto frontal). De arriba abajo: la energía que el neutrón gana (arriba) o pierde (abajo), β, contada en unidades de la energía térmica del agua, 0,025 eV. Brillante significa probable, pálido significa raro.</p>
  <p>El contorno es lo que un neutrón de la energía elegida puede alcanzar: no puede perder más de lo que tiene, y cada cambio de energía admite solo un intervalo de golpes. Arrastra la energía y el contorno crece o se encoge. Sin enlace, el mapa es el de un gas de hidrógeno libre, una cresta brillante a lo largo de la línea discontinua de retroceso; con enlace, la molécula añade franjas brillantes, sus cantidades fijas de energía. INCOGNITA calcula sus propias leyes para el agua y el berilio: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Energía del neutrón (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Enlace químico</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
