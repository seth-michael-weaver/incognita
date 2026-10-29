/* Spanish: neutrons (Chapter 5, why reactors run on neutrons) */
WT.es.ch.neutrons = {
  num: "Capítulo 5", title: "Por qué los reactores funcionan con neutrones", short: "Por qué neutrones",
  html: `
<div class="step">
  <p>Un protón es positivo, y también lo son los 82 protones del núcleo. Las cargas iguales se repelen, así que el protón es empujado hacia fuera, y el empuje crece rápido cuanto más se acerca (la flecha). Un protón lento se detiene antes y da la vuelta sin llegar a tocar. Solo por encima de unos 13 MeV supera el empuje; justo por debajo, a veces se cuela igualmente (<b>efecto túnel</b>). El pequeño gráfico muestra el mismo empuje como una colina de energía.</p>
  <div class="ctl"><label for="wn-e1">Energía del protón (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>Un neutrón no tiene carga: entra a cualquier velocidad. Nada lo empuja hacia fuera, así que no hay colina que subir; solo tiene que llegar al núcleo, y entonces la fuerza fuerte lo atrae hacia dentro.</p>
  <div class="ctl"><label for="wn-e2">Energía del neutrón (lento → rápido)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>El deslizador va desde 0,025 eV, la velocidad de un neutrón a temperatura ambiente, hasta 20 MeV, casi mil millones de veces más. Todo el recorrido, el neutrón sigue entrando.</p>
</div>
<div class="step">
  <p>Por eso incluso los neutrones lentos pueden partir uranio en un reactor. Un núcleo de uranio-235 que traga uno se convierte en uranio-236 con un poco de energía extra, suficiente para oscilar, estirarse formando un cuello y romperse en dos. Los dos pedazos salen disparados con unos 200 MeV, y los dos o tres neutrones nuevos que sueltan pueden partir los núcleos siguientes: una reacción en cadena.</p>
</div>`,
};
