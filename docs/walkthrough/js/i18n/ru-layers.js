/* Russian: layers (глава 15). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mes = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"][+m[2] - 1];
    return mes ? `${+m[3]} ${mes} ${m[1]} г.` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="победы: ${T.w}, ничьи: ${T.t}, проигрыши: ${T.l}"><div class="w"><b>${T.w}</b><span>победы</span></div><div><b>${T.t}</b><span>ничьи</span></div><div class="l"><b>${T.l}</b><span>проигрыши</span></div></div>` : "");
  const libs = LIBS.length ? `основными библиотеками оценённых данных (${LIBS.join(", ")})` : "основными библиотеками оценённых данных";
  const engineScore = TE ? ` Из ${TE.d} таких сравнений программа явно впереди в ${TE.w}, вничью в ${TE.t} и позади в ${TE.l}.` : "";
  const terraScore = TT ? `В сравнении с ${libs} она впереди в ${TT.w} из ${TT.d} сравнений, вничью в ${TT.t} и позади в ${TT.l}.` : `Она сравнивается с ${libs}.`;

  WT.L.ch.layers = {
    num: "Глава 15", title: "Как модель устроена по слоям", short: "Слои",
    lead: "То, что мы выдаём, строится слоями поверх расчётной программы, и каждый слой должен заслужить своё место в сравнении с измерениями.",
    html: `
<div class="step">
  <div class="layer-chip on">Используется</div>
  <h3>Слой 1 · Одно правило для всех ядер</h3>
  <p>Синяя линия — предсказание программы для одной реакции. Программа — это нижний слой: одна и та же физика и одни и те же глобальные параметры для всех нуклидов, и ничто не подогнано к сечениям какого-либо отдельного ядра.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Показать измерения</button></div>
  <p>Именно это делает её проверяемой — по измерениям и в сравнении с другими модельными кодами, рассчитанными для тех же ядер. Это не слепой тест: глобальные параметры выбирались с оглядкой на эти же сравнения.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Проверен: пока без улучшения</div>
  <h3>Слой 2 · Собственные измерения каждого ядра</h3>
  <p>Этот слой заменяет глобальное правило измеренными значениями для каждого ядра: его средним расстоянием между уровнями D0, силовыми функциями S0 и S1 (насколько легко ядро поглощает медленные нейтроны), средней гамма-шириной ⟨Γγ⟩ и известными энергетическими уровнями.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Глобальное правило</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Собственные измерения</button></div>
  <p>Включите его — и линия едва сдвинется. Проверки пока не выявили общего улучшения: единственный вариант, помогающий реакции вблизи её порога, ухудшает захват нейтронов. Поэтому этот слой пока выключен.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Кандидат</div>
  <h3>Слой 3 · Следовать хорошим данным (TERRA)</h3>
  <p>Там, где реакция хорошо измерена, линия должна следовать измерениям. Третий слой, TERRA, проводит линию программы через хорошие данные там, где они есть, и возвращается к программе там, где их нет.</p>
  <div class="ctl"><label for="lay-cov">Измеренная часть диапазона энергий (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} Большинство из них — на обучающей выборке (in-sample): TERRA видела эти измерения, как и библиотеки.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">В разработке</div>
  <h3>Слой 4 · Честные погрешности</h3>
  <p>Верхний слой окружает линию полосой, которая должна содержать истинное значение примерно в двух случаях из трёх (полоса 68 %): узкой там, где её фиксируют хорошие данные, и шире там, где их нет.</p>
  <div class="ctl"><label for="lay-band">Ширина полосы · измерений внутри (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Перетащите её и посчитайте измерения, попавшие внутрь. Слишком узкая полоса обещает точность, которой нет; слишком широкая ничего не говорит. Собственная полоса программы пока не принята: она верна, если собрать все реакции вместе, но ещё не для каждого семейства реакций. У TERRA свои полосы, и они входят в её сравнения выше.</p>
</div>
<div class="step">
  <h3>Где мы сейчас</h3>
  <p>Слой принимается только после проверки на измерениях и остаётся выключенным, если не помогает. Сегодня программа используется, TERRA — кандидат; слой измеренной структуры и полоса неопределённости программы всё ещё проходят проверку.</p>
  <p><a href="scoreboard.html" data-keep-lang>Полная таблица результатов →</a> Все сравнения, которые мы не выиграли, каждый соперник и как её читать.</p>
  <div class="aside">${ASOF ? `Результаты на ${ASOF}, из` : "Результаты из"} исследовательского журнала проекта. Кривые на рисунке иллюстративные.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · программа",
  "{#} · measured structure": "{#} · измеренная структура",
  "{#} · TERRA: anchored to data": "{#} · TERRA: привязка к данным",
  "{#} · uncertainty band": "{#} · полоса неопределённости",
  "measured here": "измерено здесь",
  "neutron energy →": "энергия нейтрона →",
  "how often the reaction happens": "как часто происходит реакция",
  "hollow dots: measurements the engine is compared with": "полые точки: измерения, с которыми сравнивается программа",
  "own measured values: the line barely moves": "собственные измеренные значения: линия почти не сдвигается",
  "global rule": "глобальное правило",
  "no measurements: TERRA falls back to the engine": "нет измерений: TERRA возвращается к программе",
  "solid: follows the data · dashed: the engine alone": "сплошная: следует данным · штрихи: только программа",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} из {#} измерений внутри полосы (цель: около {#} %)",
  "no measurements to check the band against": "нет измерений для проверки полосы",
});
Object.assign(WT.L.ui, { nav_board: "Таблица результатов" });
