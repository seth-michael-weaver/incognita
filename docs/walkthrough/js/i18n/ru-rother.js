/* Russian: rother (Жидкосолевые и другие реакторы) */
WT.L.ch.rother = {
  num: "Урок 1", title: "Жидкосолевые и другие реакторы", short: "Соли и прочие",
  lead: "Жидкое топливо, крошечные реакторы, реакторы без электричества и один, построенный самой природой.",
  html: `
<div class="step">
  <h3>Жидкосолевой (MSR)</h3>
  <p>Топливо растворено в горячей соли, которая течёт через активную зону.</p>
</div>
<div class="step">
  <h3>Микрореактор</h3>
  <p>От нескольких киловатт до нескольких мегаватт и без насосов: тепло отводят тепловые трубы.</p>
</div>
<div class="step">
  <h3>Исследовательский бассейновый (TRIGA)</h3>
  <p>Небольшая активная зона в открытом бассейне, построенная ради нейтронов, а не электричества.</p>
</div>
<div class="step">
  <h3>С ускорителем (ADS)</h3>
  <p>Зона сама не может поддерживать цепную реакцию; недостающие нейтроны даёт пучок протонов.</p>
</div>
<div class="step">
  <h3>Природный реактор (Окло)</h3>
  <p>Два миллиарда лет назад урановое месторождение в Габоне само стало критическим.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "ADS": "ADS",
  "KRUSTY test, Nevada ({#})": "испытание KRUSTY, Невада ({#})",
  "MSR": "MSR",
  "MSRE, Oak Ridge ({#}–{#}); TMSR-LF{#}, China": "MSRE, Ок-Ридж ({#}–{#}); TMSR-LF{#}, Китай",
  "MYRRHA, Belgium (planned)": "MYRRHA, Бельгия (проект)",
  "Micro": "Микро",
  "Oklo": "Окло",
  "Oklo, Gabon, two billion years ago": "Окло, Габон, два миллиарда лет назад",
  "Stirling engines": "двигатели Стирлинга",
  "TRIGA": "TRIGA",
  "beam off: chain stops": "пучок выключен: цепь гаснет",
  "condenser": "конденсатор",
  "coolant out": "теплоноситель на выходе",
  "electricity": "электричество",
  "fast neutrons · moderator: none · coolant: lead-bismuth": "быстрые нейтроны · замедлитель: нет · теплоноситель: свинец-висмут",
  "fast neutrons · moderator: none · coolant: sodium heat pipes": "быстрые нейтроны · замедлитель: нет · теплоноситель: натриевые тепловые трубы",
  "fast · mod.: none · cool.: lead-bismuth": "быстрые · замедл.: нет · т/н: свинец-висмут",
  "fast · mod.: none · cool.: sodium heat pipes": "быстрые · замедл.: нет · т/н: натриевые тепловые трубы",
  "freeze plug: melts to drain the salt into tanks": "замороженная пробка: плавится, и соль сливается в баки",
  "fuel is dissolved in the salt": "топливо растворено в соли",
  "gen.": "генер.",
  "generator": "генератор",
  "graphite": "графит",
  "graphite moderator, salt in channels": "графитовый замедлитель, соль в каналах",
  "heat exch.": "теплообм.",
  "heat pipes": "тепловые трубы",
  "illustration": "иллюстрация",
  "lead-bismuth": "свинец-висмут",
  "lead-bismuth coolant": "теплоноситель свинец-висмут",
  "moderator": "замедлитель",
  "neutrons": "нейтроны",
  "neutrons for research": "нейтроны для исследований",
  "neutrons for research, isotopes for medicine": "нейтроны для исследований, изотопы для медицины",
  "no turbine": "без турбины",
  "none": "нет",
  "none made": "не вырабатывает",
  "open pool of water, about {#} m deep": "открытый бассейн с водой глубиной около {#} м",
  "open pool, ~{#} m deep": "открытый бассейн, ~{#} м",
  "outlet": "выход",
  "power": "мощность",
  "pressure": "давление",
  "proton accelerator": "ускоритель протонов",
  "proton accelerator (linac)": "ускоритель протонов (линейный)",
  "pulse!": "импульс!",
  "pulse: a burst, then the hot fuel stops it": "импульс: всплеск мощности, затем горячее топливо его гасит",
  "sodium heat pipes carry the heat": "натриевые тепловые трубы отводят тепло",
  "solid core, no pumps, no water": "сплошная зона, без насосов и без воды",
  "solid metal core": "сплошная металлическая зона",
  "spallation target": "спалляционная мишень",
  "spallation target: each proton chips out many neutrons": "спалляционная мишень: каждый протон выбивает много нейтронов",
  "steam gen.": "парогенер.",
  "subcritical core: switch the beam off and the chain stops": "подкритическая зона: выключите пучок, и цепная реакция прекратится",
  "the blue glow is Cherenkov light": "голубое свечение — это излучение Вавилова–Черенкова",
  "the blue glow: Cherenkov light": "голубое свечение Черенкова",
  "the fuel is dissolved in the salt: no fuel rods": "топливо растворено в соли: никаких твэлов",
  "thermal": "тепловые",
  "thermal neutrons · moderator: graphite · coolant: molten salt, fuel dissolved in it": "тепловые нейтроны · замедлитель: графит · теплоноситель: расплав солей с растворённым топливом",
  "thermal neutrons · moderator: water and zirconium hydride · coolant: open pool": "тепловые нейтроны · замедлитель: вода и гидрид циркония · теплоноситель: открытый бассейн",
  "thermal · mod.: graphite · cool.: molten salt, fuel dissolved in it": "тепловые · замедл.: графит · т/н: солевой расплав с топливом",
  "thermal · mod.: water and zirconium hydride · cool.: open pool": "тепловые · замедл.: вода и гидрид циркония · т/н: открытый бассейн",
  "turbine": "турбина",
  "universities, isotopes, neutron beams": "университеты, изотопы, нейтронные пучки",
  "uranium ore when it still held {#} % U{#}": "урановая руда, когда в ней ещё было {#} % U{#}",
  "uranium ore, {#} % U{#}": "урановая руда, {#} % U{#}",
  "water": "вода",
  "water fills the cracks: the chain runs for about {#} minutes": "вода заполняет трещины: цепная реакция идёт около {#} минут",
  "water in: chain runs ~{#} min": "вода есть: цепь идёт ~{#} мин",
  "{#} °C": "{#} °C",
  "~{#} bar": "~{#} бар",
  "~{#} bar (unpressurized)": "~{#} бар (без давления)",
  "~{#} kW": "~{#} кВт",
  "water boiled off: off ~{#} h": "вода выкипела: пауза ~{#} ч",
  "the heat boils the water away: it stops for about {#} hours": "тепло выпаривает воду: реакция стоит около {#} часов",
});
