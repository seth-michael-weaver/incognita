/* Portuguese (pt-PT): fusion (Capítulo 29, terceira parte: dois núcleos leves sobre a colina de Coulomb) */
WT.L.ch.fusion = {
  num: "Capítulo 29", title: "A energia de fusão e a barreira de Coulomb", short: "Fusão",
  lead: "A fusão funciona ao contrário da fissão: dois núcleos leves juntam-se, e o par pesa menos do que as suas partes.",
  html: `
<div class="step">
  <h3>A energia de fusão a partir da curva de ligação</h3>
  <p>Junta dois núcleos leves: se o novo ficar mais acima na curva de ligação, é libertada energia. Depois do máximo do ferro, juntá-los custa energia.</p>
  <div class="ctl"><label for="fu-a">A de cada núcleo leve</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>A barreira de Coulomb e o efeito túnel</h3>
  <p>Puxa o deuterão para trás e larga-o. Os dois núcleos têm carga, por isso a maioria dos disparos ressalta na colina; alguns atravessam-na por efeito túnel.</p>
  <div class="ctl"><label for="fu-e">Impulso (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Disparar</button></div>
</div>
<div class="step">
  <h3>Produtos da reação e valor Q</h3>
  <p>O par unido é mais leve do que as duas partes. A massa que falta sai disparada sob a forma de partículas rápidas.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Taxa de reação termonuclear</h3>
  <p>Num gás quente passam os núcleos mais rápidos. Cada clarão é uma fusão.</p>
  <div class="ctl"><label for="fu-t">Temperatura (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Cobre{#}",
  "Coulomb hill": "Colina de Coulomb",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "pico de Gamow E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · linhas de campo perdidas na parede: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: dispensa aquecimento",
  "Silicon{#} (SiC)": "Silício{#} (SiC)",
  "Steel (iron{#})": "Aço (ferro{#})",
  "Sun's core": "núcleo do Sol",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Tungsténio{#}",
  "Vanadium{#}": "Vanádio{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "após {#} anos a {#} MW/m² · só neutrões de {#} MeV · σ da biblioteca da INCOGNITA v{#}",
  "almost never": "quase nunca",
  "alpha {#} MeV": "alfa {#} MeV",
  "axis, q = {#}": "eixo, q = {#}",
  "binding per nucleon (MeV)": "ligação por nucleão (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "vista de câmara de bolhas, campo magnético a entrar na página: os produtos carregados curvam, o neutrão não deixa rasto",
  "burning on its own": "arde sozinho",
  "cooled down: plasma lost": "arrefeceu: plasma perdido",
  "cooling": "a arrefecer",
  "could not load the library file": "falha ao carregar a biblioteca",
  "deuteron": "deuterão",
  "deuteron {#} keV": "deuterão {#} keV",
  "deuteron: pull back, let go": "deuterão: puxa para trás e larga",
  "drag or tap a point; it runs on its own": "arrasta ou toca num ponto; evolui sozinho",
  "easiest: {a} keV, nτT {b}": "mais fácil: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "bordo: q = {#} · as linhas que o cruzam perdem-se",
  "electron {#} keV": "eletrão {#} keV",
  "energy of the colliding pair (keV)": "energia do par que colide (keV)",
  "few are this fast": "poucos são tão rápidos",
  "fusion rate: {a} the rate at {b} keV": "taxa de fusão: {a} a de {b} keV",
  "grain boundary": "fronteira de grão",
  "heating itself": "aquece-se sozinho",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "o hélio fica e junta-se em bolhas; o hidrogénio difunde-se quase todo para fora",
  "helium {#} appm": "hélio {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "colina a subir: produto das cargas Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "mantém: aquecimento ligado (Q = potência de fusão / aquecimento) · larga: aquecimento desligado, o plasma fica sozinho",
  "hydrogen {#} appm": "hidrogénio {#} appm",
  "ignition (Q = ∞)": "ignição (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · largura {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "autossustentado",
  "laps {#}": "voltas {#}",
  "lead–lithium": "chumbo–lítio",
  "liquid lithium": "lítio líquido",
  "loading INCOGNITA's cross sections…": "a carregar as secções eficazes da INCOGNITA…",
  "missing {#} u  =  {#} MeV out": "faltam {#} u  =  saem {#} MeV",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "negativa: roda ao contrário",
  "neutron escapes": "o neutrão escapa",
  "peak near {#} keV": "pico perto de {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "por neutrão de fusão · {#} neutrões · secções eficazes: ajustes simples",
  "plasma": "plasma",
  "product ×{a}": "produto ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "impulso {a} keV · probabilidade de túnel de frente {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: fecha após {#} volta",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: fecha após {#} voltas",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: nenhuma fração simples, os pontos enchem o círculo",
  "screen radius is logarithmic: {#} fm to {#} fm": "raio no ecrã logarítmico: de {#} fm a {#} fm",
  "shield": "blindagem",
  "tap to fire": "toca para disparar",
  "the cut, flat": "o corte, plano",
  "time slowed {a}×": "tempo abrandado {a}×",
  "tries {#} · fused {#}": "tentativas {#} · fusões {#}",
  "tritium made, by depth": "trítio por profundidade",
  "triton": "tritão",
  "tunnels more easily": "túnel mais fácil",
  "turns at {#} fm": "inverte a {#} fm",
  "wall": "parede",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} cm",
  "{#} in {a}": "{#} em {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} milhões de K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: libertam-se cerca de {c} MeV",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: custa {c} MeV",
  "{a} keV · chance {b}": "{a} keV · probabilidade {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · dois ramos, igualmente prováveis",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ até {b} · {c} voltas por segundo",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ a {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · capturados {#} · escaparam {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
