/* Russian: blanket (Глава 32, воспроизводящий бланкет и первая стенка) */
WT.L.ch.blanket = {
  num: "Глава 32", title: "Воспроизводящий бланкет и первая стенка", short: "Бланкет",
  lead: "Трития в природе почти нет. Установка на D–T должна сама нарабатывать его из лития с помощью нейтронов, которые рождает её плазма.",
  html: `
<div class="step">
  <h3>Коэффициент воспроизводства трития</h3>
  <p>Каждый нейтрон блуждает, пока его не захватит литий и не образуется тритон. Каждая светящаяся точка — один тритон.</p>
  <div class="ctl"><label for="bk-e">Доля лития-6 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">Толщина бридера (см)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>синтеза</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>Размножение нейтронов в реакции (n,2n)</h3>
  <p>Нейтрон с энергией 14 MeV, попав в свинец, может выбить второй нейтрон: (n,2n). Сравните с одним литием.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">Свинец–литий</button> <button class="btn ghost" data-act="li" aria-pressed="false">Только литий</button></div>
  <div class="ctl"><label for="bk-e2">Доля лития-6 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Гелий и водород в первой стенке</h3>
  <p>Первая стенка принимает на себя весь поток нейтронов 14 MeV. Внутри неё накапливаются гелий и водород — с той скоростью, которую рассчитывает INCOGNITA.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">Сталь</button> <button class="btn ghost" data-act="wW" aria-pressed="false">Вольфрам</button> <button class="btn ghost" data-act="wV" aria-pressed="false">Ванадий</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">Медь</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">Нагрузка на стенку (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">Годы</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">Сечения: библиотека INCOGNITA v0.2 (<code>library/v0.2/channels_v02.parquet</code>), те же кривые, что и в разделе <a href="data.html#Fe-56" data-keep-lang>Все нуклиды</a>.</div>
</div>`,
};
