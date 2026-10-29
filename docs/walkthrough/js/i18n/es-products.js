/* Spanish: products (Chapter 15, fission products and decay heat) */
WT.es.ch.products = {
  num: "Capítulo 15", title: "Productos de fisión y calor de desintegración", short: "Productos de fisión",
  html: `
<div class="step">
  <p>Los pedazos son desiguales: uno ligero y otro pesado. El gráfico muestra, para cada masa de fragmento A (protones más neutrones), la fracción de fisiones que lo produce. Dos jorobas: los pedazos ligeros cerca de A = 95, los pesados cerca de 139. Un reparto equilibrado, cerca de A = 117, es unas cien veces más raro.</p>
  <p>Cada línea discontinua es diez veces más alta que la de debajo, así que las masas raras también se ven. Toca una barra o arrastra el deslizador: abajo están los dos pedazos de esa división. Sus masas suman 234, no 236 (uranio-235 más el neutrón), porque también salen despedidos unos 2,4 neutrones.</p>
  <div class="ctl"><label for="pr-a">A del fragmento ligero</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Sus desintegraciones siguen calentando el combustible después de la parada. Los fragmentos son radiactivos: se desintegran uno tras otro, y cada desintegración libera calor, funcione o no la reacción en cadena.</p>
  <div class="ctl"><label for="pr-t">Tiempo tras la parada</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>Arrastra el tiempo. Un segundo después de que el reactor se detiene, las desintegraciones aún dan cerca del 6 % de la potencia plena; tras un día, cerca de medio por ciento; tras un año, unas centésimas de por ciento, que en un reactor grande siguen siendo casi un megavatio. Por eso el combustible gastado se guarda años en piscinas de enfriamiento. La curva es la regla práctica de Way–Wigner: una fórmula sencilla para las desintegraciones de todos los fragmentos juntos, tras un año de funcionamiento. Las dos escalas saltan un factor diez en cada marca.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "fragment mass number A →": "número másico del fragmento A →",
  "share of fissions that make it (each line ×{#})": "fracción de fisiones que lo producen (cada línea ×{#})",
  "Rb{#} · {#} %": "Rb{#} · {#} %",
  "Xe{#} · {#} %": "Xe{#} · {#} %",
  "+ about {#} neutrons": "+ unos {#} neutrones",
  "{#} % of full power": "{#} % de la potencia plena",
  "≈ {#} MW in a {#} MW reactor · {#} s after shutdown": "≈ {#} MW en un reactor de {#} MW · {#} s tras la parada",
  "{#} min": "{#} min",
  "{#} h": "{#} h",
  "{#} day": "{#} día",
  "{#} yr": "{#} año",
  "time after shutdown (each mark much later) →": "tiempo tras la parada (cada marca mucho después) →",
  "Way–Wigner rule of thumb, after a year at full power": "regla práctica de Way–Wigner, tras un año a plena potencia",
});
