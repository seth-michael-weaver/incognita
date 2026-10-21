/* Spanish: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.es.ui, {
  brand: "Dentro de una reacción nuclear", nav_physics: "La física", nav_data: "Todos los núclidos", nav_board: "Marcador", menu: "Menú", site_nav: "Sitio",
  ways_h: "Más formas de entrar", ways_more: "O sigue bajando: la física empieza aquí ↓",
  way1_k: "Explora", way1_t: "Todos los núclidos", way1_p: "Secciones eficaces predichas para 6168 núclidos junto a cada medida depurada. Busca cualquier isótopo y mira cada conjunto de datos.", way1_go: "Abrir los datos →",
  way2_k: "Compara", way2_t: "Marcador", way2_p: "Cómo se comparan el motor y su producto de datos con otros códigos de reacciones y bibliotecas, juzgados frente a las medidas, con las derrotas primero.", way2_go: "Ver los resultados →",
  way3_k: "Ejecútalo", way3_t: "El código", way3_p: "Todo lo que hay aquí es abierto. Clona el repositorio, consulta cualquier curva o ejecuta el motor tú mismo.", way3_go: "GitHub →",
  title: "Dentro de una reacción nuclear",
  kicker: "Una explicación interactiva del motor de reacciones INCOGNITA",
  h1: "Dentro de una reacción nuclear",
  hero1: "Lanza un neutrón contra un núcleo atómico y algo sale de vuelta. Puede ser el propio neutrón, que rebota. Puede ser un protón, una partícula alfa (un grupo compacto de 2 protones y 2 neutrones) o un destello de luz. Un núcleo pesado puede incluso partirse en dos.",
  hero2: "¿Cuál de estas cosas ocurre, y con qué frecuencia? Esta página recorre, paso a paso, cómo nuestro software responde a esa pregunta. Desplázate hacia abajo y prueba los controles por el camino. Las imágenes siguen la misma física que el motor; los números que muestran son ilustrativos.",
  scrollcue: "Desplázate para empezar ↓",
  hero_tag: "Un neutrón. Un núcleo. Muchas maneras de terminar.",
  hero_fire: "Dispara un neutrón",
  hero_hint: "o haz clic en cualquier parte de la imagen",
  coda_h2: "Dónde vive esto en el código",
  coda_p1: "Cada etapa anterior es un paquete en <code>physics/hf</code>, y el motor los llama en el orden en que acabas de leerlos. El motor es un port de TALYS-2.x, el consolidado código de reacciones. Lo que añade está tras interruptores con nombre dentro de los mismos paquetes: la mayoría están desactivados por defecto, unas pocas correcciones están activadas, y cada una puede devolverse por separado al TALYS original.",
  coda_table: `
    <thead><tr><th>Capítulo</th><th>Qué hace</th><th>Código</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>Masas, niveles, deformación, datos de resonancias</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Modelo óptico, coeficientes de transmisión (con qué facilidad entran y salen las partículas)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Canales acoplados, DWBA, resonancias gigantes, captura directa (opcional)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">4</a></td><td>Preequilibrio: modelo de excitones, captura y arranque de nucleones, emisión múltiple</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Densidades de niveles (estados por MeV), distribución de espín</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td>Elegir una salida (Hauser–Feshbach), fluctuaciones de anchura</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Función de fuerza gamma y transmisión γ; niveles discretos e isómeros</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">8</a></td><td>La cascada de emisiones de partículas y γ, canales exclusivos, residuales</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Barreras de fisión y transmisión</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Espectros de emisión, distribuciones angulares y secciones eficaces doblemente diferenciales (opcional, solo de salida)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Captura en blancos excitados térmicamente y tasas estelares (opcional)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>Incertidumbre con muchas variantes aleatorias (Monte Carlo total)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>El programa que ejecuta las etapas en orden, y núcleos de cálculo opcionales en C para ganar velocidad</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>Todos los valores por defecto y opciones, leídos una vez al inicio; también los parámetros ajustados por núclido de TENDL, aplicados como los aplica TALYS (opcional)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "Añadido más allá de TALYS",
  coda_p_added: "Las filas marcadas como <b>Activado</b> funcionan por defecto, así que una ejecución por defecto ya no coincide exactamente con TALYS; cada una se puede desactivar con una palabra clave o una variable de entorno. El resto queda desactivado salvo que se active.",
  coda_table_added: `
    <thead><tr><th>Capítulo</th><th>Qué cambia</th><th>Código</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">8</a></td><td><b>Activado.</b> Contabilidad del flujo cerrada: residuales conservados hasta 10⁻⁹ mb (TALYS: 10⁻³ mb), residuales un paso más allá de la ventana de cascada de TALYS conservados, hasta 8 de cada partícula emitida en los canales exclusivos, todas las ramas de desexcitación repetidas de un nivel contadas</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Activado.</b> El intervalo superior del primer núcleo compuesto se llena como lo llenan los fotones primarios (con peso E<sub>γ</sub>³), no de forma uniforme</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Activado.</b> Sin elástica compuesta promediada por debajo de las primeras resonancias (menos de 1 keV), donde la elástica es dispersión de potencial</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>Activado.</b> Blancos deformados sin fisión: las salidas de neutrones a niveles fuera de la banda acoplada usan la transmisión de canales acoplados</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td><b>Activado.</b> La emisión alfa ve un potencial que depende de la temperatura del residual; los proyectiles alfa entran con el modelo alfa 6; los potenciales de tritón y helión incluyen el tamaño del proyectil</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td><b>Activado.</b> Transmisión unidimensional exacta a través de cada joroba de la barrera</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td><b>Activado.</b> Los factores de intensidad E1/M1 por núcleo, cuando una ejecución los aporta, se sustituyen por una única función global de la deformación</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Un modo tijera más intenso en núcleos deformados, con sistemáticas más recientes que coinciden con medidas de Oslo (unas 4–5× en actínidos); o una variante que escala su energía e intensidad con la deformación</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Función de fuerza gamma reescalada para que cada núcleo coincida con su intensidad radiativa medida ⟨Γγ⟩/D₀, en todos los núcleos de la cascada, no solo el primero</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Modo tijera más intenso y normalización de ⟨Γγ⟩ solo para los núcleos más pesados (Z ≥ 88), pensados para la captura a energías de keV</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Nuestra propia constante de anchura E1 en lugar de la tabla de TALYS derivada de TENDL (la fija la receta sin datos que distribuimos)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>Intensidad E2 colectiva de las bandas rotacionales en el cuasicontinuo</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Un ajuste regional del pozo óptico para blancos deformados de tierras raras, ajustado a S₀ y S₁ medidos sin datos de captura</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>Las funciones de fuerza neutrónica medidas S₀, S₁ fijan la transmisión de neutrones a baja energía</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>Captura directa en órbitas ligadas, con una corrección del original: en TALYS estándar devuelve cero salvo que también se pidan todas las salidas del modelo óptico</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>El esquema de acoplamiento del blanco (rotor, vibrador, esférico) elegido a partir de sus niveles medidos</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>El continuo empieza donde el esquema de niveles medido deja de estar completo</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>Un nivel cuyo espín listado es imposible para su núcleo (entero en A impar) se trata como un nivel de espín desconocido</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>Densidad de niveles de temperatura constante anclada en la parte completa de los niveles discretos</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>Bandas rotacionales de estados de transición en los puntos de silla de la fisión</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">10</a></td><td>Captura donde solo unas pocas resonancias caen en la ventana estelar: el valor típico de una escalera de resonancias en lugar del promedio</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>Cuatro salvaguardas lejos de la estabilidad: flujo directo limitado por unitariedad, un límite para la energía de Fermi, sin colectividad por defecto en núcleos impar-impar, reparto de espín del preequilibrio normalizado</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "Fuera del motor",
  coda_p_outside: "Algunas partes de la historia funcionan junto al motor y no dentro de él. Las escaleras estadísticas de resonancias del <a href=\"#resonance\">capítulo 10</a> viven en <code>physics/resonance/</code>. Los promedios maxwellianos (MACS) del <a href=\"#measure\">capítulo 11</a> se obtienen después de la ejecución a partir de las curvas de captura del motor, en <code>validation/differential/core.py</code>; en cambio, la captura en blancos excitados térmicamente y la tasa estelar las calcula el propio motor (<code>astro/stellar.py</code>, opcional). La capa de anclaje del <a href=\"#layers\">capítulo 12</a> vive en <code>incognita/terra/</code>.",
  close: "Cerrar",
  chapters: "Capítulos",
  nav_board: "Marcador", nav_data_short: "Datos",
  coda_repo: "El código, la biblioteca y las medidas depuradas son abiertos: <a href=\"https://github.com/seth-michael-weaver/incognita\">seth-michael-weaver/incognita en GitHub</a>. Puedes consultar cualquier predicción en la página <a href=\"data.html?lang=es\">Todos los núclidos</a>, o clonar el repositorio y ejecutarlo.",
  diagram: "Diagrama",
});

Object.assign(WT.es.ui, { pause_sweep: "Pausar el barrido", play_sweep: "Reanudar el barrido" });
