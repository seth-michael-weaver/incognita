/* Simplified Chinese (简体中文): spentfuel (乏燃料，逐个核素) */
WT.L.ch.spentfuel = {
  num: "第1课", title: "乏燃料，逐个核素", short: "逐个核素",
  html: `
<div class="step">
  <h3>里面有什么</h3>
  <p>卸料一年后的一吨压水堆燃料（富集度 4.2 %，50 GWd/t）：几乎全部质量是铀，几乎全部活度集中在几千克物质里。</p>
</div>
<div class="step">
  <h3>活度还是放射毒性</h3>
  <p>贝可勒尔计的是衰变次数；希沃特按每次衰变被吞入后的危害加权，这会抬高 α 发射体。</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">活度（Bq）</button> <button class="btn ghost" data-act="mT" aria-pressed="true">放射毒性（Sv）</button></div>
</div>
<div class="step">
  <h3>何时由谁主导</h3>
  <p>悬停或点按一条色带查看名称；沿时间轴拖动来给它们排序。</p>
</div>
<div class="step">
  <h3>回收钚</h3>
  <p>四年后的后处理把钚取出（铀也一并取出）。还剩下多少？</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
</div>
<div class="step">
  <h3>把次锕系元素也取出</h3>
  <p>把镅、锔和镎也取出：这时留下的 1 % 或 0.1 % 决定了所需时间。</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removed</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99.9 %</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "Cm{#}": "Cm{#}",
  "Cs{#}": "Cs{#}",
  "I{#}": "I{#}",
  "NEA {#} + computed": "NEA {#} + 计算",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "Tc{#}": "Tc{#}",
  "activity": "活度",
  "activity after {#} year (log scale)": "{#} 年后的活度（对数坐标）",
  "below the ore after ≈ {#} years": "约 {#} 年后低于铀矿",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "计算值（Bateman 衰变，ICRP{#}）· 色带高度 = 占总量份额",
  "computed · band height = share": "计算值 · 色带高度 = 份额",
  "drag along the time axis · hover a band": "沿时间轴拖动 · 悬停色带",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "核素存量：OECD-NEA {#}（{#} %，{#} GWd/t）+ 计算的裂变产物",
  "mass": "质量",
  "mass (log scale)": "质量（对数坐标）",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "{#} kg 裂变产物大多稳定；活度包含短寿命子体",
  "once-through": "一次通过",
  "once-through (no recycling)": "一次通过（不回收）",
  "ore: {#}×{#}⁵ Sv": "铀矿：{#}×{#}⁵ Sv",
  "other FP": "其他裂变产物",
  "other FP: mostly stable": "其他裂变产物：大多稳定",
  "other fission products": "其他裂变产物",
  "radiotoxicity if swallowed (Sv), relative to the ore": "食入放射毒性（Sv），相对于铀矿",
  "radiotoxicity ÷ ore": "放射毒性 ÷ 铀矿",
  "reprocessing at {#} yr": "第 {#} 年后处理",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "其来源铀矿：{#} t 天然铀 + 子体 = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "此时主要是 Am{#}（{#} %）",
  "then mostly Pb{#} + Po{#} ({#} %)": "此时主要是 Pb{#} + Po{#}（{#} %）",
  "then mostly Sr{#} + Y{#} ({#} %)": "此时主要是 Sr{#} + Y{#}（{#} %）",
  "uranium": "铀",
  "years after unloading (log scale) →": "卸料后的年数（对数坐标）→",
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#}×10⁶",
  "{#} years:": "{#} 年：",
  "{#} yr": "{#} 年",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "other Am, Cm": "其他 Am、Cm",
  "decay daughters (Ra, Pb, Po, Th…)": "衰变子体（Ra、Pb、Po、Th…）",
  "daughters": "子体",
  "still above the ore after a million years": "一百万年后仍高于铀矿",
  "drag the time · tap a band": "拖动时间 · 点按色带",
  "activity ÷ ore": "活度 ÷ 铀矿",
  "activity (Bq), relative to the ore": "活度（Bq），相对于铀矿",
});
