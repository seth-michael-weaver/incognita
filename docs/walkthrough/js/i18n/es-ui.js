/* Spanish: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.es.ui, {
  title: "Dentro de una reacción nuclear",
  kicker: "Una explicación interactiva del motor de reacciones INCOGNITA",
  h1: "Dentro de una reacción nuclear",
  hero1: "Lanza un neutrón contra un núcleo atómico y algo sale de vuelta. Puede ser el propio neutrón, que rebota. Puede ser un protón, una partícula alfa (un grupo compacto de 2 protones y 2 neutrones) o un destello de luz. Un núcleo pesado puede incluso partirse en dos.",
  hero2: "¿Cuál de estas cosas ocurre, y con qué frecuencia? Esta página recorre, paso a paso, cómo nuestro software responde a esa pregunta. Desplázate hacia abajo y prueba los controles por el camino. Cada animación funciona con la misma física que el código real.",
  scrollcue: "Desplázate para empezar ↓",
  hero_tag: "Un neutrón. Un núcleo. Muchas maneras de terminar.",
  hero_hint: "Haz clic o toca en cualquier sitio para disparar tu propio neutrón.",
  coda_h2: "Dónde vive esto en el código",
  coda_p1: "Cada etapa anterior es un paquete en <code>physics/hf</code>, y el motor los llama en el orden en que acabas de leerlos. Tal como viene, el motor reproduce TALYS-2.x, el consolidado código de reacciones del que se portó. La física que añade está tras interruptores con nombre dentro de los mismos paquetes, todos desactivados por defecto, así que activar uno cambia exactamente una cosa.",
  coda_table: `
    <thead><tr><th>Capítulo</th><th>Qué hace</th><th>Código</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Masas, niveles, deformación, datos de resonancias</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Modelo óptico, coeficientes de transmisión (con qué facilidad entran y salen las partículas)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Canales acoplados, DWBA, resonancias gigantes, captura directa</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">4</a></td><td>Preequilibrio: modelo de excitones, captura y arranque de nucleones, emisión múltiple</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Densidades de niveles (estados por MeV), distribución de espín</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td>Elegir una salida (Hauser–Feshbach), fluctuaciones de anchura</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Función de fuerza gamma, cascada γ, isómeros</td><td><code>gamma/</code>, <code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">8</a></td><td>La cascada de emisiones, canales exclusivos, residuales</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Barreras de fisión y transmisión</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Incertidumbre con muchas variantes aleatorias (Monte Carlo total)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>Todos los valores por defecto y opciones, leídos una vez al inicio</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Añadido más allá de TALYS",
  coda_p_added: "Cada uno es un interruptor, desactivado salvo que se active, así que una ejecución por defecto sigue coincidiendo con TALYS.",
  coda_table_added: `
    <thead><tr><th>Capítulo</th><th>Qué cambia</th><th>Código</th></tr></thead>
    <tbody>
      <tr><td><a href="#gamma">7</a></td><td>Un modo tijera más intenso en núcleos deformados, con sistemáticas más recientes ajustadas a medidas de Oslo (unas 4–5× en actínidos); o una variante que escala su energía e intensidad con la deformación</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Función de fuerza gamma reescalada para que cada núcleo coincida con su anchura fotónica media medida ⟨Γγ⟩, en todos los núcleos de la cascada, no solo el primero</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Ambas correcciones a la vez para los núcleos más pesados (Z ≥ 88), pensadas para la captura a energías de keV</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Un ajuste regional del pozo óptico para blancos deformados de tierras raras, ajustado a S₀ y S₁ medidos sin datos de captura</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Captura directa en órbitas ligadas, con una corrección del original: en TALYS estándar devuelve cero sin aviso salvo que también se pidan todas las salidas del modelo óptico</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td></td><td>Los parámetros ajustados por núclido que TALYS distribuye con TENDL, aplicados igual que los aplica TALYS</td><td><code>input/fitlib.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "Fuera del motor",
  coda_p_outside: "Dos partes de la historia funcionan junto al motor y no dentro de él. Las escaleras estadísticas de resonancias del <a href=\"#resonance\">capítulo 10</a> viven en <code>physics/resonance/</code>. Los promedios estelares del <a href=\"#measure\">capítulo 11</a> se calculan después de la ejecución a partir de las curvas de captura del motor, en <code>validation/differential/core.py</code>. El motor no calcula distribuciones angulares ni reacciones con blancos excitados térmicamente.",
  close: "Cerrar",
  chapters: "Capítulos",
});

Object.assign(WT.es.ui, { pause_sweep: "Pausar el barrido", play_sweep: "Reanudar el barrido" });
