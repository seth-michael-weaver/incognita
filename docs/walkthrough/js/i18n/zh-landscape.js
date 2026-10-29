/* Simplified Chinese: landscape (核素的版图) */
WT.L.ch.landscape = {
  title: "核素的版图", short: "核素图",
  lead: "人类制造过的每一种原子核，都画在一张图上：迄今共 3,338 种，只有 252 种永远不会衰变。",
  html: `
<div class="step">
  <h3>核素图</h3>
  <p>每个小方块是一种在实验中真正观测到的原子核：横向是中子数，纵向是质子数。浅色方块表示已被观测到，但质量尚未称量，只是估计值。<b>深色</b>方块是永不衰变的 252 种。其余的都会瓦解，橙色的转瞬即逝，蓝色的要经过数年才衰变。<em style="font-style:normal;color:var(--proton);font-weight:600">红色</em>一行是你用滑块选中的元素：它所有已知的同位素。</p>
  <div class="ctl"><label for="ls-z">查看元素（质子数 Z）</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>整张核素图上的结合能</h3>
  <p>现在每个方块按其<b>每核子结合能</b>着色，即每个中子或质子被束缚得有多紧（第 3 章）。稳定核位于一条强结合的“山脊”上；偏离它，中子过多或质子过多，结合能就下降。最强的是镍-62。细线标出<b>幻数</b>（8、20、28、50、82、126），这些数目的原子核结合得格外紧。</p>
</div>
<div class="step">
  <h3>朝稳定方向的 β 衰变</h3>
  <p>核子总数相同（<b>质量数</b> A 相同）的原子核，位于图上的一条对角线上，以<em style="font-style:normal;color:var(--proton);font-weight:600">红色</em>显示。从中子过多开始，就像裂变铀核的碎片那样。在 <b>β 衰变</b>中，一个中子变成质子，于是原子核沿着这条线朝结合更紧的中间位置前进一步，一次又一次，直到到达山脊才停下。小图把同一条衰变链画成原子核滚下的山谷。试试 A = 137：这条链经过铯-137，即反应堆事故中长寿命的产物。</p>
  <div class="ctl"><label for="ls-a">质量数 A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>INCOGNITA 的覆盖范围</h3>
  <p>同一张图，按我们的库为每种原子核提供的内容着色。<em style="font-style:normal;color:var(--fission);font-weight:600">绿色</em>：由实测共振评价得到。其余的只有仅由引擎生成的模型文件：<b>深色</b>表示稳定或长寿命（A 级），<em style="font-style:normal;color:var(--accent);font-weight:600">蓝色</em>表示寿命超过一天（B 级），<em style="font-style:normal;color:var(--warm);font-weight:600">橙色</em>表示寿命更短（C 级）。灰色的不在库中（大多是最轻的原子核，还有少数引擎无法计算的）。</p>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "neutrons N →": "中子数 N →",
  "protons Z ↑": "质子数 Z ↑",
  "Fe: all its isotopes": "Fe：它的全部同位素",
  "stable": "稳定",
  "lives years": "寿命数年",
  "gone in a blink": "转瞬即逝",
  "red: Fe (your pick)": "红色：Fe（你的选择）",
  "nickel{#}: most tightly bound": "镍{#}：结合最紧",
  "held most tightly": "结合最紧",
  "middle": "中等",
  "held least": "结合最松",
  "red: the A = {#} chain": "红色：A = {#} 衰变链",
  "A = {#}: deeper = more tightly bound": "A = {#}：越深 = 结合越紧",
  "protons Z →": "质子数 Z →",
  "measured resonances": "实测共振",
  "tier A": "A 级",
  "tier B": "B 级",
  "tier C": "C 级",
  "not in library": "不在库中",
});
