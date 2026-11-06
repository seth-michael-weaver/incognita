/* Simplified Chinese (简体中文): fuelcycle (核燃料循环) */
WT.L.ch.fuelcycle = {
  num: "第1课", title: "核燃料循环", short: "燃料循环",
  html: `
<div class="step">
  <h3>开采铀矿</h3>
  <p>矿石大部分是岩石，其中的铀只有 0.7 % 是铀-235，即容易裂变的那一种。</p>
  <div class="ctl"><label for="fc-g">矿石品位（% 铀）</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>浓缩是一笔质量平衡账</h3>
  <p>铀以气体形态被分成一小股富含铀-235 的物流，即燃料，和一大股贫化的物流，即尾料。</p>
  <div class="ctl"><label for="fc-p">燃料富集度（% U-235）</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">尾料（% U-235）</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>芯块、燃料棒、组件</h3>
  <p>浓缩铀被烧结成陶瓷芯块，密封进燃料棒，再捆扎成组件；<a href="#reactor">下一课</a>跟随它们进入堆芯。</p>
  <div class="ctl"><label for="fc-f">燃料（吨铀）</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>在堆芯中的岁月</h3>
  <p>在三到六年里，百分之几的重原子发生裂变，留下裂变产物和一些新生成的钚（<a href="#burnup">燃耗</a>）。</p>
  <div class="ctl"><label for="fc-b">燃耗（GWd/吨）</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>冷却，然后两条路</h3>
  <p>乏燃料先在水池中冷却，再放入干式贮存罐；之后要么原样深埋，要么进行后处理，让其中的铀和钚再次利用（<a href="#waste">乏燃料</a>、<a href="#breeding">增殖</a>）。</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">一次通过</button> <button class="btn ghost" data-act="frR" aria-pressed="false">后处理</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Convert": "转化",
  "Disposal": "处置",
  "End": "终点",
  "Enrich": "浓缩",
  "Fabricate": "制造",
  "Mill": "水冶",
  "Mine": "采矿",
  "Pool · cask": "水池 · 贮存罐",
  "Reactor": "反应堆",
  "Store": "贮存",
  "about what a {#} MWe reactor loads in a year": "大约是一座 {#} MWe 反应堆一年的装料量",
  "assemblies": "组件",
  "assemblies of {#} rods": "每个组件 {#} 根棒",
  "at least {#} years": "至少 {#} 年",
  "cask": "贮存罐",
  "decades": "数十年",
  "decades in air": "在空气中数十年",
  "deep repository, {#}–{#} m down": "深地处置库，地下 {#}–{#} m",
  "dry cask": "干式贮存罐",
  "enrich": "浓缩",
  "enrichment plant (UF₆ gas)": "浓缩厂（UF₆ 气体）",
  "fission products": "裂变产物",
  "illustration": "示意图",
  "minor actinides": "次锕系元素",
  "most mines: above {#} %": "多数矿山：{#} % 以上",
  "of electricity from this tonne": "由这一吨发出的电",
  "once-through: the whole tonne is disposed of": "一次通过：整吨都被处置",
  "one tonne of fuel: each square is {#} kg": "一吨燃料：每个方格 {#} kg",
  "one tonne: each square {#} kg": "一吨：每格 {#} kg",
  "pellets": "芯块",
  "pellets, {#} cm tall": "芯块，高 {#} cm",
  "plutonium": "钚",
  "pool": "水池",
  "recycle": "再循环",
  "repository": "处置库",
  "repository {#}–{#} m deep": "处置库深 {#}–{#} m",
  "reprocess": "后处理",
  "richest, Canada: up to {#} %": "最富的在加拿大：高达 {#} %",
  "rods, about {#} m long": "燃料棒，长约 {#} m",
  "rods, {#} m": "燃料棒，{#} m",
  "the rest: uranium{#}": "其余：铀{#}",
  "the whole tonne": "整吨",
  "typical discharge {#}–{#}": "典型卸料燃耗 {#}–{#}",
  "uranium{#}": "铀{#}",
  "uranium{#} (and {#})": "铀{#}（及 {#}）",
  "{#} U atoms": "{#} 个 U 原子",
  "{#} are U{#}": "{#} 个是 U{#}",
  "{#} are uranium{#}": "{#} 个是铀{#}",
  "{#} t used": "{#} t 乏燃料",
  "{#} t used fuel": "{#} t 乏燃料",
  "{#} uranium atoms": "{#} 个铀原子",
  "≈ a big reactor's yearly reload": "≈ 大型反应堆一年的换料量",
  "≥ {#} years": "≥ {#} 年",
  "{a} t ore": "{a} t 矿石",
  "{a} t U₃O₈": "{a} t U₃O₈",
  "{a} t UF₆": "{a} t UF₆",
  "{#} t fuel + {a} t tails": "{#} t 燃料 + {a} t 尾料",
  "{a} t UO₂": "{a} t UO₂",
  "pool ≥ {#} years": "水池 ≥ {#} 年",
  "ore ≈ {a} t · block = {#} t": "矿石 ≈ {a} t · 每块 = {#} t",
  "ore for one tonne of fuel: ≈ {a} t  (each block {#} t)": "一吨燃料所需矿石：≈ {a} t（每块 {#} t）",
  "{a} of one block": "一块的 {a}",
  "{a} % U": "{a} % U",
  "grade {a} % U": "品位 {a} % U",
  "natural U {a} kg": "天然铀 {a} kg",
  "natural uranium {a} kg": "天然铀 {a} kg",
  "{a} % U{#}": "{a} % U{#}",
  "fuel {#} kg": "燃料 {#} kg",
  "tails {a} kg": "尾料 {a} kg",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "给料/燃料 = (xp − xt)/(xf − xt) = {a}",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "天然铀 / 燃料 = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "≈ {a} SWU of separative work per kg of fuel": "每 kg 燃料约需 {a} SWU 分离功",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "分离功 ≈ 每 kg 燃料 {a} SWU · 尾料越贫：用铀越少，分离功越多",
  "{a} t uranium = {b} t UO₂": "{a} t 铀 = {b} t UO₂",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t 浓缩铀，即 {b} t 二氧化铀（UO₂）陶瓷",
  "{a} % of the heavy atoms split": "{a} % 的重原子已裂变",
  "{a} GWd/t": "{a} GWd/t",
  "≈ {a} GWh of electricity": "≈ {a} GWh 电能",
  "reprocessing": "后处理",
  "uranium {a} t": "铀 {a} t",
  "plutonium {a} kg": "钚 {a} kg",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t MOX 燃料",
  "fission products + minor actinides {a} kg → ≈ {#} t glass": "裂变产物 + 次锕系元素 {a} kg → ≈ {#} t 玻璃",
  "U {a} t → re-enrich": "U {a} t → 再浓缩",
  "Pu {a} kg → MOX": "Pu {a} kg → MOX",
  "{a} kg waste → glass": "{a} kg 废物 → 玻璃",
  "fission prod.": "裂变产物",
  "minor act.": "次锕系",
});
