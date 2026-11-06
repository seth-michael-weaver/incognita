/* Chinese: waste (乏燃料随时间的变化) */
WT.L.ch.waste = {
  num: "第1课", title: "乏燃料随时间的变化", short: "乏燃料",
  html: `
<div class="step">
  <h3>卸出的是什么</h3>
  <p>在堆芯中待了四五年之后，燃料芯块的主要成分仍然是铀。百分之几是<b>裂变产物</b>，即分裂后的原子。约 1 % 是钚，还有微量更重的<b>次锕系元素</b>，例如镅。</p>
  <div class="btns"><button class="btn" data-act="sort">把原子分类</button></div>
</div>
<div class="step">
  <h3>最初的几百年</h3>
  <p>这条曲线把乏燃料被吞食时的危害与制造它所用的铀矿石相比较。起初裂变产物占主导，但它们大多数的半衰期约为 30 年：大约 300 年后，它们就降到矿石水平以下了。</p>
  <div class="ctl"><label for="wst-t1">卸料后的年数</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>接下来是钚</h3>
  <p>留下来的是钚和镅，它们的半衰期从几百年到几万年不等。它们使乏燃料的危害在十万多年里都高于矿石水平。</p>
  <div class="ctl"><label for="wst-t2">卸料后的年数</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>回收与嬗变</h3>
  <p>把钚分离出来作为新燃料烧掉，这段时间就缩短到约一万年。再在快堆中使次锕系元素裂变，剩下的就只有裂变产物：几百年。</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">回收钚</button><button class="btn ghost" data-act="tm" aria-pressed="false">嬗变次锕系元素</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // the pellet
  "Sort the atoms": "把原子分类",
  "Mix them again": "重新混合",
  "uranium": "铀",
  "fission products": "裂变产物",
  "fission prod.": "裂变产物",
  "plutonium": "钚",
  "minor actinides": "次锕系元素",
  "minor act.": "次锕系",
  "~{#} %": "约 {#} %",
  "a used fuel pellet, {#} atoms": "一个用过的燃料芯块，{#} 个原子",
  "a used fuel pellet, {#} atoms shown": "一个用过的燃料芯块，图中画出 {#} 个原子",
  "the glow: fission products are the most radioactive": "发光：裂变产物的放射性最强",
  "the glow: the fission products are by far the most radioactive part": "发光：裂变产物是放射性远远最强的部分",
  // time landscape
  "spent fuel": "乏燃料",
  "spent fuel, one tonne": "乏燃料，一吨",
  "the ore": "矿石",
  "the ore it was made from": "原来的矿石",
  "{#} yr": "{#} 年",
  "uranium ore level": "铀矿石水平",
  "the uranium ore it was made from": "制造它所用的铀矿石",
  "{#} million": "{#}×10⁶",
  "years after unloading (log scale) →": "卸料后的年数（对数坐标）→",
  "hazard vs ore (log)": "危害 / 矿石（对数）",
  "hazard if swallowed, relative to the ore (log scale)": "被吞食时的危害，相对于矿石（对数坐标）",
  "Am, Cm, Np": "Am、Cm、Np",
  "americium, curium…": "镅、锔……",
  "americium": "镅",
  "{#} years: {#} × the ore": "{#} 年：矿石的 {#} 倍",
  "below the ore it came from": "低于原来的矿石",
  "mostly from fission products": "主要来自裂变产物",
  "mostly from plutonium": "主要来自钚",
  "mostly from americium": "主要来自镅",
  "reaches the ore level after ~{#} years": "约 {#} 年后降到矿石水平",
  "recycle + transmute": "回收 + 嬗变",
  "recycle Pu and transmute minor actinides": "回收 Pu 并嬗变次锕系元素",
  "plutonium recycled": "钚已回收",
  "plutonium recycled, minor actinides in the waste": "钚已回收，次锕系元素留在废物中",
  "only minor actinides removed": "只去除次锕系元素",
  "minor actinides removed, plutonium left in": "去除次锕系元素，钚留在其中",
  "spent fuel as it is": "乏燃料原样",
  "spent fuel kept as it is": "乏燃料原样保存",
  "illustrative shape (after OECD-NEA)": "示意性形状（依据 OECD-NEA）",
});
