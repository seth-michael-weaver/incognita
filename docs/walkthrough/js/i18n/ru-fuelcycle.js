/* Russian: fuelcycle (Топливный цикл) */
WT.L.ch.fuelcycle = {
  num: "Урок 1", title: "Топливный цикл", short: "Топливный цикл",
  html: `
<div class="step">
  <h3>Добыча урана</h3>
  <p>Руда — это в основном порода, и лишь 0,7 % урана в ней приходится на уран-235, тот, что легко делится.</p>
  <div class="ctl"><label for="fc-g">Содержание урана в руде (%)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>Обогащение — это материальный баланс</h3>
  <p>В виде газа уран разделяют на небольшой поток, обогащённый ураном-235, — топливо, и большой обеднённый — отвал.</p>
  <div class="ctl"><label for="fc-p">Обогащение топлива (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Отвал (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Таблетки, твэлы, сборки</h3>
  <p>Обогащённый уран спекают в керамические таблетки, запаивают в твэлы и собирают в сборки; <a href="#reactor">следующий урок</a> провожает их в активную зону.</p>
  <div class="ctl"><label for="fc-f">Топливо (тонн урана)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Годы в активной зоне</h3>
  <p>За три–шесть лет делится несколько процентов тяжёлых атомов, оставляя продукты деления и немного нового плутония (<a href="#burnup">выгорание</a>).</p>
  <div class="ctl"><label for="fc-b">Выгорание (ГВт·сут на тонну)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Охлаждение, затем два пути</h3>
  <p>Отработавшее топливо остывает в бассейне, а затем в сухих контейнерах; после этого его либо захоранивают глубоко как есть, либо перерабатывают, чтобы снова использовать уран и плутоний (<a href="#waste">отработавшее топливо</a>, <a href="#breeding">воспроизводство</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Открытый цикл</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Переработка</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Convert": "Конверсия",
  "Disposal": "Захоронение",
  "End": "Финал",
  "Enrich": "Обогащение",
  "Fabricate": "Изготовление",
  "Mill": "Переработка руды",
  "Mine": "Добыча",
  "Pool · cask": "Бассейн · контейнер",
  "Reactor": "Реактор",
  "Store": "Хранение",
  "about what a {#} MWe reactor loads in a year": "примерно годовая загрузка реактора {#} МВт(э)",
  "assemblies": "сборки",
  "assemblies of {#} rods": "сборки по {#} твэла",
  "at least {#} years": "не менее {#} лет",
  "cask": "контейнер",
  "decades": "десятилетия",
  "decades in air": "десятилетия на воздухе",
  "deep repository, {#}–{#} m down": "глубинное хранилище, {#}–{#} м под землёй",
  "dry cask": "сухой контейнер",
  "enrich": "обогащение",
  "enrichment plant (UF₆ gas)": "обогатительный завод (газ UF₆)",
  "fission products": "продукты деления",
  "illustration": "иллюстрация",
  "minor actinides": "младшие актиниды",
  "most mines: above {#} %": "большинство рудников: выше {#} %",
  "of electricity from this tonne": "электроэнергии из этой тонны",
  "once-through: the whole tonne is disposed of": "открытый цикл: захоранивается вся тонна",
  "one tonne of fuel: each square is {#} kg": "тонна топлива: каждый квадрат — {#} кг",
  "one tonne: each square {#} kg": "тонна: квадрат = {#} кг",
  "pellets": "таблетки",
  "pellets, {#} cm tall": "таблетки высотой {#} см",
  "plutonium": "плутоний",
  "pool": "бассейн",
  "recycle": "рецикл",
  "repository": "хранилище",
  "repository {#}–{#} m deep": "хранилище на глубине {#}–{#} м",
  "reprocess": "переработка",
  "richest, Canada: up to {#} %": "богатейшие, Канада: до {#} %",
  "rods, about {#} m long": "твэлы длиной около {#} м",
  "rods, {#} m": "твэлы, {#} м",
  "the rest: uranium{#}": "остальное: уран{#}",
  "the whole tonne": "вся тонна",
  "typical discharge {#}–{#}": "обычная выгрузка {#}–{#}",
  "uranium{#}": "уран{#}",
  "uranium{#} (and {#})": "уран{#} (и {#})",
  "{#} U atoms": "{#} атомов U",
  "{#} are U{#}": "из них {#} — U{#}",
  "{#} are uranium{#}": "из них {#} — уран{#}",
  "{#} t used": "{#} т ОЯТ",
  "{#} t used fuel": "{#} т отработавшего топлива",
  "{#} uranium atoms": "{#} атомов урана",
  "≈ a big reactor's yearly reload": "≈ годовая перегрузка большого реактора",
  "≥ {#} years": "≥ {#} лет",
  "{a} t ore": "{a} т руды",
  "{a} t U₃O₈": "{a} т U₃O₈",
  "{a} t UF₆": "{a} т UF₆",
  "{#} t fuel + {a} t tails": "{#} т топлива + {a} т отвала",
  "{a} t UO₂": "{a} т UO₂",
  "pool ≥ {#} years": "бассейн ≥ {#} лет",
  "ore ≈ {a} t · block = {#} t": "руда ≈ {a} т · блок = {#} т",
  "ore for one tonne of fuel: ≈ {a} t  (each block {#} t)": "руда на тонну топлива: ≈ {a} т  (блок = {#} т)",
  "{a} of one block": "{a} одного блока",
  "{a} % U": "{a} % U",
  "grade {a} % U": "содержание {a} % U",
  "natural U {a} kg": "природный U {a} кг",
  "natural uranium {a} kg": "природный уран {a} кг",
  "{a} % U{#}": "{a} % U{#}",
  "fuel {#} kg": "топливо {#} кг",
  "tails {a} kg": "отвал {a} кг",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "питание/топливо = (xp − xt)/(xf − xt) = {a}",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "природный / топливо = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} ЕРР работы разделения на кг топлива",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "работа разделения ≈ {a} ЕРР на кг топлива · беднее отвал: меньше урана, больше работы",
  "{a} t uranium = {b} t UO₂": "{a} т урана = {b} т UO₂",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} т обогащённого урана в виде {b} т керамики из диоксида урана (UO₂)",
  "{a} % of the heavy atoms split": "разделилось {a} % тяжёлых атомов",
  "{a} GWd/t": "{a} ГВт·сут/т",
  "≈ {a} GWh of electricity": "≈ {a} ГВт·ч электроэнергии",
  "reprocessing": "переработка",
  "uranium {a} t": "уран {a} т",
  "plutonium {a} kg": "плутоний {a} кг",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} т МОКС-топлива",
  "fission products + minor actinides {a} kg → ≈ {#} t glass": "продукты деления + младшие актиниды {a} кг → ≈ {#} т стекла",
  "U {a} t → re-enrich": "U {a} т → дообогащение",
  "Pu {a} kg → MOX": "Pu {a} кг → МОКС",
  "{a} kg waste → glass": "{a} кг отходов → стекло",
  "fission prod.": "продукты дел.",
  "minor act.": "младшие акт.",
});
