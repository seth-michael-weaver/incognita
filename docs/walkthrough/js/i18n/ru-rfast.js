/* Russian: rfast (Реакторы на быстрых нейтронах) */
WT.L.ch.rfast = {
  num: "Урок 1", title: "Реакторы на быстрых нейтронах", short: "Быстрые реакторы",
  lead: "Замедлителя нет: нейтроны остаются быстрыми, поэтому реактор может нарабатывать новое топливо и дожигать долгоживущие отходы.",
  html: `
<div class="step">
  <h3>Натриевый (SFR)</h3>
  <p>Жидкий натрий хорошо переносит тепло без давления. Промежуточный натриевый контур отделяет его от воды.</p>
</div>
<div class="step">
  <h3>Свинцовый (LFR)</h3>
  <p>Свинец кипит только при 1750 °C и не горит ни на воздухе, ни в воде.</p>
</div>
<div class="step">
  <h3>Быстрый газовый (GFR)</h3>
  <p>Гелий, плотное топливо и никакого графита: горячо и быстро.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "BN{#} and BN{#} (Russia); EBR-II, Phénix": "БН{#} и БН{#} (Россия); EBR-II, Phénix",
  "BREST-OD{#} (Russia), being built": "БРЕСТ-ОД{#} (Россия), строится",
  "GFR": "GFR",
  "Generation IV; ALLEGRO demonstrator planned": "IV поколение; планируется демонстратор ALLEGRO",
  "LFR": "LFR",
  "SFR": "SFR",
  "a pool of liquid sodium, near atmospheric pressure": "бассейн жидкого натрия, давление почти атмосферное",
  "a pool of molten lead, near atmospheric pressure": "бассейн расплавленного свинца, давление почти атмосферное",
  "condenser": "конденсатор",
  "coolant out": "теплоноситель на выходе",
  "electricity": "электричество",
  "fast core, no moderator": "быстрая зона, без замедлителя",
  "fast neutrons · moderator: none · coolant: helium": "быстрые нейтроны · замедлитель: нет · теплоноситель: гелий",
  "fast neutrons · moderator: none · coolant: liquid lead": "быстрые нейтроны · замедлитель: нет · теплоноситель: жидкий свинец",
  "fast neutrons · moderator: none · coolant: liquid sodium": "быстрые нейтроны · замедлитель: нет · теплоноситель: жидкий натрий",
  "fast · mod.: none · cool.: helium": "быстрые · замедл.: нет · т/н: гелий",
  "fast · mod.: none · cool.: liquid lead": "быстрые · замедл.: нет · т/н: жидкий свинец",
  "fast · mod.: none · cool.: liquid sodium": "быстрые · замедл.: нет · т/н: жидкий натрий",
  "gas turbine": "газовая турбина",
  "gen.": "генер.",
  "generator": "генератор",
  "heat exch.": "теплообм.",
  "heat exchanger": "теплообменник",
  "heat exchangers in the pool": "теплообменники в бассейне",
  "helium": "гелий",
  "helium gas turbine": "гелиевая газовая турбина",
  "helium, {#} bar": "гелий, {#} бар",
  "illustration": "иллюстрация",
  "no moderator": "без замедлителя",
  "no moderator: dense fuel, fast neutrons": "без замедлителя: плотное топливо, быстрые нейтроны",
  "outlet": "выход",
  "pool of liquid sodium": "бассейн жидкого натрия",
  "pool of molten lead": "бассейн расплавленного свинца",
  "precooler": "предохладитель",
  "pressure": "давление",
  "small dense core, no moderator": "маленькая плотная зона, без замедлителя",
  "steam gen.": "парогенер.",
  "steam generator": "парогенератор",
  "steam generators in the pool": "парогенераторы в бассейне",
  "turbine": "турбина",
  "{#} bar": "{#} бар",
  "{#} °C": "{#} °C",
  "~{#} bar": "~{#} бар",
  "~{#} bar (unpressurized)": "~{#} бар (без давления)",
});
