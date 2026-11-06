/* Russian: reactor (Как реактор вырабатывает электричество) */
WT.L.ch.reactor = {
  num: "Урок 1", title: "Как реактор вырабатывает электричество", short: "Реактор",
  html: `
<div class="step">
  <h3>Топливо</h3>
  <p>Уран спекают в керамические таблетки размером с кончик пальца, таблетки складывают в длинные металлические стержни, а стержни собирают в сборки. Одна таблетка даёт примерно столько же тепла, сколько сжигание тонны угля.</p>
  <div class="ctl"><label for="rea-z">Отдалить</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Деление атомов даёт тепло</h3>
  <p>В активной зоне делящиеся атомы урана нагревают воду, которая течёт вверх вдоль стержней. Та же вода замедляет нейтроны, чтобы они могли делить новые атомы. Высокое давление не даёт ей закипеть даже при 325 °C.</p>
</div>
<div class="step">
  <h3>Пар вращает турбину</h3>
  <p>Горячая вода через тонкие трубки передаёт тепло второму контуру, где вода закипает. Пар вращает турбину и генератор, а затем холодная речная или морская вода снова превращает его в воду. Примерно треть тепла становится электричеством.</p>
</div>
<div class="step">
  <h3>Регулирующие стержни</h3>
  <p>Регулирующие стержни поглощают нейтроны. Введите их — и делится меньше атомов: меньше тепла, меньше пара, меньше электричества. Извлеките — и мощность растёт.</p>
  <div class="ctl"><label for="rea-rod">Стержни введены (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "reactor": "реактор",
  "reactor vessel": "корпус реактора",
  "control rods": "регулирующие стержни",
  "core": "активная зона",
  "steam gen.": "парогенер.",
  "steam generator": "парогенератор",
  "turbine": "турбина",
  "gen.": "генер.",
  "generator": "генератор",
  "condenser": "конденсатор",
  "sea or river water": "морская или речная вода",
  "{#} °C out": "выход {#} °C",
  "{#} °C in": "вход {#} °C",
  "steam ~{#} °C": "пар ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} бар: горячо, но без кипения",
  "{#} bar keeps the water liquid at {#} °C": "{#} бар удерживают воду жидкой при {#} °C",
  "the water also slows the neutrons": "вода ещё и замедляет нейтроны",
  "the water carries the heat and slows the neutrons": "вода уносит тепло и замедляет нейтроны",
  "heat {#} MW": "тепло {#} MW",
  "electric {#} MW": "электр. {#} MW",
  "electricity {#} MW": "электричество {#} MW",
  "chain stopped; fuel still warm (afterheat)": "цепь остановлена; топливо ещё греется (остаточное тепло)",
  "chain reaction stopped; the fuel still gives off afterheat": "цепная реакция остановлена; топливо всё ещё выделяет остаточное тепло",
  "turbine speed fixed by the grid; more steam, more push": "скорость турбины задаёт сеть; больше пара — сильнее напор",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "скорость турбины задана сетью; больше пара — сильнее напор",
  "{#}/{#} of the heat goes to the water": "{#}/{#} тепла уходит в воду",
  "about two thirds of the heat leaves through the condenser": "около двух третей тепла уходит через конденсатор",
  "illustration": "иллюстрация",
  "drag sideways to zoom": "тяните вбок для масштаба",
  "drag sideways to zoom out": "тяните вбок, чтобы отдалить",
  "UO₂ pellet, {#} cm": "таблетка UO₂, {#} см",
  "uranium oxide pellet, about {#} cm": "таблетка оксида урана, около {#} см",
  "{#} tonne of coal": "{#} тонна угля",
  "about {#} tonne of coal (or {#} m³ of gas)": "около {#} тонны угля (или {#} м³ газа)",
  "same heat, roughly": "примерно столько же тепла",
  "fuel rod, ~{#} m": "твэл, ~{#} м",
  "fuel rod, about {#} m long": "твэл длиной около {#} м",
  "~{#} pellets inside": "~{#} таблеток внутри",
  "about {#} pellets in a metal tube": "около {#} таблеток в металлической трубке",
  "(not to scale)": "(не в масштабе)",
  "assembly: {#} rods": "сборка: {#} твэла",
  "fuel assembly from above: {#} rods": "тепловыделяющая сборка сверху: {#} твэла",
  "rings: control-rod guide tubes": "кольца: направляющие каналы стержней",
  "rings: tubes the control rods slide into": "кольца: каналы, в которые входят регулирующие стержни",
  "core: {#} assemblies": "зона: {#} сборки",
  "the core from above: {#} assemblies": "активная зона сверху: {#} сборки",
  "~{#} rods, ~{#} m across": "~{#} твэлов, ~{#} м в поперечнике",
  "about {#} rods in a cylinder about {#} m across": "около {#} твэлов в цилиндре около {#} м в поперечнике",
  "pellet": "таблетка",
  "rod": "стержень",
  "assembly": "сборка",
});
