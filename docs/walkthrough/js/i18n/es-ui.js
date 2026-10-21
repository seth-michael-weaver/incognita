/* Spanish: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.es.ui, {
  title: "Dentro de una reacción nuclear",
  kicker: "Una explicación interactiva del motor de reacciones INCOGNITA",
  h1: "Dentro de una reacción nuclear",
  hero1: "Lanza un neutrón contra un núcleo atómico y algo sale de vuelta. Puede ser el propio neutrón, que rebota. Puede ser un protón, una partícula alfa (un grupo compacto de 2 protones y 2 neutrones) o un destello de luz. Un núcleo pesado puede incluso partirse en dos.",
  hero2: "¿Cuál de estas cosas ocurre, y con qué frecuencia? Esta página recorre, paso a paso, cómo nuestro software responde a esa pregunta. Desplázate hacia abajo y prueba los controles por el camino. Cada animación funciona con la misma física que el código real.",
  scrollcue: "Desplázate para empezar ↓",
  coda_h2: "Dónde vive esto en el código",
  coda_p1: "Cada etapa anterior es un paquete en <code>physics/hf</code>, y el motor los llama en el orden en que acabas de leerlos. Con sus propias opciones desactivadas, el motor reproduce TALYS-2.x, el consolidado código de reacciones del que se portó. Su física añadida está tras opciones con nombre dentro de los mismos paquetes.",
  coda_table: `
    <thead><tr><th>Qué hace</th><th>Paquete</th></tr></thead>
    <tbody>
      <tr><td>Masas, niveles, deformación, datos de resonancias</td><td><code>structure/</code></td></tr>
      <tr><td>Modelo óptico, coeficientes de transmisión (con qué facilidad entran y salen las partículas)</td><td><code>omp/</code></td></tr>
      <tr><td>Canales acoplados, DWBA, resonancias gigantes, captura directa</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td>Preequilibrio: modelo de excitones, Kalbach, emisión múltiple</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td>Densidades de niveles (estados por MeV), distribución de espín</td><td><code>density/</code></td></tr>
      <tr><td>Elegir una salida (Hauser–Feshbach), fluctuaciones de anchura</td><td><code>compound/</code></td></tr>
      <tr><td>Función de fuerza gamma, cascada γ</td><td><code>gamma/</code>, <code>structure/levels.py</code></td></tr>
      <tr><td>La cascada de emisiones, canales exclusivos</td><td><code>emission/</code></td></tr>
      <tr><td>Barreras de fisión y transmisión</td><td><code>fission/</code></td></tr>
      <tr><td>Tasas estelares (promedios maxwellianos)</td><td><code>astro/</code></td></tr>
      <tr><td>Escaleras de resonancias, captura térmica</td><td><code>physics/resonance/</code></td></tr>
    </tbody>
  `,
  close: "Cerrar",
  chapters: "Capítulos",
});

Object.assign(WT.es.ui, { pause_sweep: "Pausar el barrido", play_sweep: "Reanudar el barrido" });
