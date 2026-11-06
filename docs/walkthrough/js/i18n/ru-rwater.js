/* Russian: rwater (Реакторы с водяным охлаждением) */
WT.L.ch.rwater = {
  num: "Урок 1", title: "Реакторы с водяным охлаждением", short: "Водяные реакторы",
  lead: "Почти все энергетические реакторы сегодня охлаждаются водой. Различаются они тем, как вода выносит тепло.",
  html: `
<div class="step">
  <h3>Вода под давлением (PWR)</h3>
  <p>Вода под высоким давлением несёт тепло в парогенератор; пар образуется во втором контуре.</p>
</div>
<div class="step">
  <h3>Кипящий реактор (BWR)</h3>
  <p>Вода кипит прямо в активной зоне, и пар идёт сразу на турбину: один контур.</p>
</div>
<div class="step">
  <h3>Тяжёлая вода (CANDU)</h3>
  <p>Тяжёлая вода замедляет нейтроны, почти не поглощая их, поэтому хватает природного урана.</p>
</div>
<div class="step">
  <h3>Графит и кипящая вода (РБМК)</h3>
  <p>Нейтроны замедляет графит; вода кипит в сотнях отдельных каналов.</p>
</div>
<div class="step">
  <h3>Малый модульный (SMR)</h3>
  <p>Небольшой PWR, у которого всё размещено в одном корпусе; его собирают на заводе.</p>
</div>
<div class="step">
  <h3>Сверхкритическая вода (SCWR)</h3>
  <p>Выше 221 бар вода не кипит вовсе, поэтому реактор может работать горячее и превращать в электричество больше тепла.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "BWR": "BWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU; Канада, Индия, Румыния, Аргентина",
  "Generation IV design, not yet built": "проект IV поколения, пока не построен",
  "NuScale (US), Linglong One (China)": "NuScale (США), Linglong One (Китай)",
  "PHWR": "PHWR",
  "PWR": "PWR",
  "RBMK": "РБМК",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "около {#} % реакторов; США, Япония, Швеция",
  "about {#} in {#} of the world's reactors": "около {#} из {#} реакторов в мире",
  "all in one vessel": "всё в одном корпусе",
  "boiling water in tubes": "вода кипит в каналах",
  "boils in the core": "кипит в активной зоне",
  "calandria: cool heavy water": "каландр: холодная тяжёлая вода",
  "calandria: cool heavy water slows the neutrons": "каландр: холодная тяжёлая вода замедляет нейтроны",
  "condenser": "конденсатор",
  "control rods from below": "регулирующие стержни снизу",
  "coolant out": "теплоноситель на выходе",
  "core": "активная зона",
  "core, pump-free loop and steam generator in one vessel": "активная зона, контур без насосов и парогенератор в одном корпусе",
  "electricity": "электричество",
  "gen.": "генер.",
  "generator": "генератор",
  "graphite": "графит",
  "graphite blocks slow the neutrons": "графитовые блоки замедляют нейтроны",
  "horizontal pressure tubes, refuelled while running": "горизонтальные напорные трубы, перегрузка на ходу",
  "illustration": "иллюстрация",
  "outlet": "выход",
  "pressure": "давление",
  "pressure tubes": "напорные трубы",
  "reactor vessel": "корпус реактора",
  "rods from below": "стержни снизу",
  "steam gen.": "парогенер.",
  "steam generator": "парогенератор",
  "the Chernobyl type; a few still run in Russia": "чернобыльский тип; несколько ещё работают в России",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "тепловые нейтроны · замедлитель: графит · теплоноситель: кипящая вода",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "тепловые нейтроны · замедлитель: тяжёлая вода · теплоноситель: тяжёлая вода",
  "thermal neutrons · moderator: light water · coolant: boiling water": "тепловые нейтроны · замедлитель: лёгкая вода · теплоноситель: кипящая вода",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "тепловые нейтроны · замедлитель: лёгкая вода · теплоноситель: сверхкритическая вода",
  "thermal neutrons · moderator: light water · coolant: water": "тепловые нейтроны · замедлитель: лёгкая вода · теплоноситель: вода",
  "thermal · mod.: graphite · cool.: boiling water": "тепловые · замедл.: графит · т/н: кипящая вода",
  "thermal · mod.: heavy water · cool.: heavy water": "тепловые · замедл.: тяжёлая вода · т/н: тяжёлая вода",
  "thermal · mod.: light water · cool.: boiling water": "тепловые · замедл.: лёгкая вода · т/н: кипящая вода",
  "thermal · mod.: light water · cool.: supercritical water": "тепловые · замедл.: лёгкая вода · т/н: сверхкритическая вода",
  "thermal · mod.: light water · cool.: water": "тепловые · замедл.: лёгкая вода · т/н: вода",
  "turbine": "турбина",
  "vessel": "корпус",
  "water boils in the core": "вода кипит в активной зоне",
  "water boils in ~{#} pressure tubes": "вода кипит в ~{#} технологических каналах",
  "{#} bar": "{#} бар",
  "{#} bar: hotter than boiling, still one fluid": "{#} бар: горячее точки кипения, но одна фаза",
  "{#} bar: never boils": "{#} бар: никогда не кипит",
  "{#} °C": "{#} °C",
});
