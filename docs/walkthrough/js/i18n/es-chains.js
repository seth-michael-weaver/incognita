/* Spanish: chains (Cadenas de desintegración y equilibrio) */
WT.L.ch.chains = {
  num: "Lección 4", title: "Cadenas de desintegración y equilibrio", short: "Cadenas de desintegración",
  html: `
<div class="step">
  <h3>Padre, hijo, nieto</h3>
  <p>A menudo el nuevo núcleo también es inestable. El padre se desintegra en un hijo, que a su vez se desintegra en un nieto estable. Los hijos se acumulan y luego se desvanecen; cuánto se acumulan depende de lo rápido que se desintegran en comparación con el padre.</p>
  <div class="ctl"><label for="ch-t2">Semivida del hijo (s)</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Muestra nueva</button></div>
</div>
<div class="step">
  <h3>Equilibrio secular: radio y radón</h3>
  <p>El radio-226 dura 1600 años; su hijo, el gas radón-222, solo 3,8 días. En un frasco cerrado el radón se acumula hasta que se desintegra tan deprisa como se produce: <i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>), donde λ es la constante de desintegración del radón. Al cabo de unas semanas, los dos se desintegran al mismo ritmo.</p>
  <div class="btns"><button class="btn" data-act="vent">Abrir el frasco</button></div>
</div>
<div class="step">
  <h3>Equilibrio transitorio: la vaca de tecnecio</h3>
  <p>Los hospitales reciben una columna de molibdeno-99 (66 horas) que produce sin parar tecnecio-99m (6 horas), el trazador médico más usado. Se extrae el tecnecio cada mañana y vuelve a crecer, siguiendo al molibdeno, que se apaga despacio.</p>
  <div class="btns"><button class="btn" data-act="milk">Ordeñar el generador</button><button class="btn ghost" data-act="genre">Generador nuevo</button></div>
</div>
<div class="step">
  <h3>Bajando por la cadena del uranio</h3>
  <p>El uranio-238 necesita catorce pasos para convertirse en plomo estable. En esta carta, una desintegración alfa baja dos casillas y se mueve dos a la izquierda; una desintegración beta sube una y se mueve una a la izquierda. En un mineral de uranio antiguo y sin alterar, todos los miembros se desintegran al mismo ritmo.</p>
  <div class="btns"><button class="btn" data-act="next">Siguiente desintegración</button><button class="btn ghost" data-act="restart">Empezar de nuevo</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  /* step 1 */
  "parent {#}": "padre {#}",
  "daughter {#}": "hijo {#}",
  "stable {#}": "estable {#}",
  "parent ({#} s): {#}": "padre ({#} s): {#}",
  "daughter ({#} s): {#}": "hijo ({#} s): {#}",
  "granddaughter (stable): {#}": "nieto (estable): {#}",
  "daughter peaks: {#} %": "máximo del hijo: {#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "semividas ilustrativas",
  /* step 2 */
  "radium{#}": "radio{#}",
  "radon{#} gas": "gas radón{#}",
  "radium": "radio",
  "radium activity": "actividad del radio",
  "radon": "radón",
  "radon activity": "actividad del radón",
  "{#} d": "{#} d",
  "days →": "días →",
  "day {#}: radon at {#} % of radium": "día {#}: radón al {#} % del radio",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(radón) = A(radio) × ({#} − exp(−λt))",
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  /* step 3 */
  "Mo{#}": "Mo{#}",
  "Tc{#}m out": "Tc{#}m extraído",
  "Tc{#}m to the patient": "Tc{#}m al paciente",
  "molybdenum{#}": "molibdeno{#}",
  "dashed: never milked": "discontinua: sin ordeñar",
  "activity": "actividad",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "{#} h desde el último ordeño · Tc{#}m al {#} % del Mo{#}",
  "regrows to its peak in about {#} hours": "vuelve a su máximo en unas {#} horas",
  /* step 4 */
  "neutrons →": "neutrones →",
  "grey: stable": "gris: estable",
  "protons ↑": "protones ↑",
  "alpha: {#} p, {#} n": "alfa: {#} p, {#} n",
  "alpha: loses {#} protons and {#} neutrons": "alfa: pierde {#} protones y {#} neutrones",
  "beta: n → p": "beta: n → p",
  "beta: a neutron becomes a proton": "beta: un neutrón se convierte en protón",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · semivida {#} mil millones de años · luego alfa",
  "Th{#} · half-life {#} days · beta next": "Th{#} · semivida {#} días · luego beta",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · semivida {#} min · luego beta",
  "U{#} · half-life {#} yr · alpha next": "U{#} · semivida {#} años · luego alfa",
  "U-234 · half-life 245,000 yr · alpha next": "U-234 · semivida 245 000 años · luego alfa",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · semivida {#} años · luego alfa",
  "Th-230 · half-life 75,000 yr · alpha next": "Th-230 · semivida 75 000 años · luego alfa",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · semivida {#} años · luego alfa",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · semivida {#} días · luego alfa",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · semivida {#} min · luego alfa",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · semivida {#} min · luego beta",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · semivida {#} min · luego beta",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · semivida {#} µs · luego alfa",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · semivida {#} años · luego beta",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · semivida {#} días · luego beta",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · semivida {#} días · luego alfa",
  "Pb{#}: stable, the chain ends": "Pb{#}: estable, fin de la cadena",
  "step {#} of {#} · tap the nucleus": "paso {#} de {#} · toca el núcleo",
});
