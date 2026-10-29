/* Simplified Chinese (简体中文): layers (chapter 12). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded
 * first), as in js/ch/layers.js; a missing block or field drops the number, not the sentence. */
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
    return +m[2] >= 1 && +m[2] <= 12 ? `${m[1]} 年 ${+m[2]} 月 ${+m[3]} 日` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="胜 ${T.w}，平 ${T.t}，负 ${T.l}"><div class="w"><b>${T.w}</b><span>胜</span></div><div><b>${T.t}</b><span>平</span></div><div class="l"><b>${T.l}</b><span>负</span></div></div>` : "");
  const libs = LIBS.length ? `主要的评价数据库（${LIBS.join("、")}）` : "主要的评价数据库";
  const engineScore = TE ? `在 ${TE.d} 项这样的比较中，它明显领先 ${TE.w} 项，持平 ${TE.t} 项，落后 ${TE.l} 项。` : "";
  const terraScore = TT ? `与${libs}相比，它在 ${TT.d} 项比较中领先 ${TT.w} 项，持平 ${TT.t} 项，落后 ${TT.l} 项。` : `它与${libs}进行比较。`;

  WT.L.ch.layers = {
    num: "第 21 章", title: "模型如何分层", short: "分层",
    lead: "我们交付的成果是在引擎之上一层一层搭建起来的，而每一层都必须在测量数据面前证明自己的价值。",
    html: `
<div class="step">
  <div class="layer-chip on">使用中</div>
  <h3>第 1 层 · 所有原子核同一条规则</h3>
  <p>蓝线是引擎对某个反应的预测。引擎是最底层：对每个核素使用相同的物理和全局设置，没有任何部分针对单个原子核的截面进行拟合。</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">显示测量数据</button></div>
  <p>这使它可以用测量数据检验，也可以与在相同原子核上运行的其他模型程序比较。但这不是盲测：全局设置是在观察这些比较的过程中选定的。${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">已测试：尚无改进</div>
  <h3>第 2 层 · 每个原子核自己的测量值</h3>
  <p>这一层把全局规则换成每个原子核自己的测量值：它的能级间距 D0、强度函数 S0 和 S1（吸收慢中子的难易程度）、平均 γ 宽度 ⟨Γγ⟩，以及已知的能级。</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">全局规则</button><button class="btn ghost" data-act="ms1" aria-pressed="false">自身测量值</button></div>
  <p>打开它，曲线几乎不动。迄今为止的测试没有发现整体改进：唯一一个能改善阈能附近某个反应的变体，反而让中子俘获变差。因此这一层目前保持关闭。</p>
</div>
<div class="step">
  <div class="layer-chip cand">候选</div>
  <h3>第 3 层 · 追随可靠数据（TERRA）</h3>
  <p>在一个反应已被很好测量的地方，曲线应当追随测量数据。第三层 TERRA 让引擎的曲线在有可靠数据的地方穿过这些数据，在没有数据的地方则退回到引擎本身。</p>
  <div class="ctl"><label for="lay-cov">已测量的能量范围占比 (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore}其中大多数属于样本内比较：TERRA 见过这些测量数据，评价数据库也一样。</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">开发中</div>
  <h3>第 4 层 · 诚实的误差棒</h3>
  <p>最上层在曲线周围加上一条区间带，它应当在大约三次中有两次包含真值（68 % 区间）：在可靠数据约束住的地方较窄，其他地方较宽。</p>
  <div class="ctl"><label for="lay-band">区间宽度 · 落在区间内的测量 (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>拖动滑块，数一数落在区间内的测量点。太窄，区间就宣称了它并不具备的精度；太宽，它就什么也没说明。引擎自身的区间尚未采用：把所有反应合在一起时它是准确的，但还不是对每一类反应都准确。TERRA 带有自己的区间，并已计入上面的比较中。</p>
</div>
<div class="step">
  <h3>当前状况</h3>
  <p>一层只有在经过测量数据检验之后才会被采用；如果没有帮助，就保持关闭。目前引擎已在使用，TERRA 是候选；实测结构层和引擎的不确定度区间仍在测试中。</p>
  <p><a href="scoreboard.html" data-keep-lang>查看完整记分板 →</a> 列出我们未胜出的每一项比较、每个对手，以及如何解读。</p>
  <div class="aside">${ASOF ? `截至 ${ASOF} 的分数，` : "分数"}来自本项目的研究记录。图中的曲线仅作示意。</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · 引擎",
  "{#} · measured structure": "{#} · 实测结构",
  "{#} · TERRA: anchored to data": "{#} · TERRA：锚定数据",
  "{#} · uncertainty band": "{#} · 不确定度区间",
  "measured here": "此处有测量",
  "neutron energy →": "中子能量 →",
  "how often the reaction happens": "反应发生的频繁程度",
  "hollow dots: measurements the engine is compared with": "空心点：与引擎比较的测量数据",
  "own measured values: the line barely moves": "自身测量值：曲线几乎不动",
  "global rule": "全局规则",
  "no measurements: TERRA falls back to the engine": "无测量数据：TERRA 退回引擎",
  "solid: follows the data · dashed: the engine alone": "实线：追随数据 · 虚线：仅引擎",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#}/{#} 个测量点在区间内（目标：约 {#} %）",
  "no measurements to check the band against": "没有可用于检验区间的测量数据",
});
Object.assign(WT.L.ui, { nav_board: "记分板" });
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
