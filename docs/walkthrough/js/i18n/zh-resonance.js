/* Simplified Chinese (简体中文): resonance (chapter 10) */
WT.L.ch.resonance = {
  num: "第 10 章", title: "尖锐的峰", short: "共振",
  lead: "当能量足够低时，中子看到的不再是一个光滑的、平均化的原子核，而是复合核的一个个单独能级。",
  html: `
<div class="step">
  <p>每个峰都是一个<b>共振</b>：复合核的一个能级，能量恰好等于它的中子可以落入其中。峰高是该处的<b>俘获</b>截面（中子被吸收，放出光子），用对数坐标表示；峰宽是共振宽度 Γ，画得比实际宽约一百倍。</p>
  <div class="ctl"><label for="res-e">中子能量 (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>中子沿能量轴跳跃前进；落在哪里，就可能在那里被俘获，伴随一阵光子闪光。在峰上截面高达数千靶恩，俘获几乎必然发生；在峰与峰之间只有几靶恩。拖动能量，让它停在一个峰上，再停在两个峰之间。</p>
</div>
<div class="step">
  <h3>峰与峰保持距离</h3>
  <p>中间一行显示真实能级的分布：自旋和宇称相同的两个能级相互排斥，因此几乎重合的情况很少见。<b>随机矩阵理论</b>描述了这种规律。完全随机的位置（上面一行）则会扎堆并留下空隙。</p>
  <div class="btns"><button class="btn" data-act="again">重新抽取</button></div>
  <p>重新抽取一个新样本。⟨r̃⟩ 比较相邻的两个间距：随机分布约为 0.39，相互排斥的能级约为 0.53；代码采用排斥的规律。把两个序列混在一起，比如两种自旋（下面一行），会部分掩盖这种排斥。</p>
</div>
<div class="step">
  <h3>峰高分散得惊人</h3>
  <p>现在每个峰的高度是它的<b>中子宽度</b> Γ<sub>n</sub>，用线性坐标表示：即该能级与中子耦合的强弱。黄色顶盖是它的 γ 宽度 Γ<sub>γ</sub>，表示它发射光子的快慢；它是数百条光子路径之和，所以对每个能级几乎都一样。</p>
  <div class="btns"><button class="btn" data-act="roll">抽取一个宽度</button><button class="btn ghost" data-act="equal">等宽</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>一个能级分解为中子加靶核只有一种方式，所以它的宽度就像一个钟形曲线随机数的平方。抽一次：小球落在 <i>x</i>，<i>x</i>² 成为下一个峰的高度，同时一个点落入堆中。这一堆在零附近密集，并拖着长长的尾巴，这就是 <b>Porter–Thomas 分布</b>：大多数能级很弱，少数极强。“等宽”则显示一排平均高度的峰。</p>
</div>
<div class="step">
  <h3>由四个数构建的共振序列</h3>
  <p>现在的峰来自你可以设定的四个平均值。对未经测量的原子核，只有这些平均值可以预测：平均间距 <i>D</i><sub>0</sub>；<b>强度函数</b> <i>S</i><sub>0</sub> 和 <i>S</i><sub>1</sub>，即 s 波（正面入射）和 p 波（偏心入射）中子每单位间距的平均中子宽度；以及平均 γ 宽度。代码由此构建一个<b>共振序列</b>：具有这些平均值的一组随机能级。</p>
  <div class="ctl"><label for="res-d0">间距 D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">强度 S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">γ 宽度 ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>拖动 <i>D</i><sub>0</sub>，峰会散开或挤到一起。实心峰是 s 波能级（正宇称），空心峰是 p 波能级（负宇称）。s 波的中子宽度按 √<i>E</i> 增长，p 波按 <i>E</i><sup>3/2</sup> 增长，所以空心峰起初很矮，越往右越高。</p>
</div>
<div class="step">
  <h3>下降到热能区</h3>
  <p>同样的峰，改用对数能量坐标，一直延伸到千分之一 eV。反应堆中的中子通过与轻原子核碰撞而慢化，每次损失的能量比例大致相同，所以这里每一跳的长度都一样。有些中子在途中被峰俘获。</p>
  <div class="btns"><button class="btn" data-act="slow">慢化 10 个中子</button></div>
  <p>穿过这些峰的中子最终停在室温，0.025 eV，即<b>热中子</b>能量，远低于第一个峰。那里的截面（圆盘的面积）是各共振尾部之和，包括刚好低于零的束缚能级；尾部按 1/<i>v</i> 增长（<i>v</i> 为中子速度），所以底部向左升高。慢化途中被俘获的部分由<b>共振积分</b>来衡量：0.5 eV 以上的截面，每个能量以 1/<i>E</i> 加权。</p>
</div>
<div class="step">
  <h3>只有统计规律可以预测</h3>
  <p>每一行都是由同样四个数抽取的一个共振序列，配一个圆盘，其面积是该序列的热中子俘获截面。括号延伸到决定这个值的那个峰，通常是最近的一个；它的距离随序列而变，圆盘的大小相差十倍甚至更多。</p>
  <div class="btns"><button class="btn" data-act="draw1">抽取一个序列</button><button class="btn ghost" data-act="more">抽取 20 个</button></div>
  <p>每个值都落入右侧的堆中。对未经测量的原子核，答案是一个取值分布，而不是一个数，任何更好的模型都无法使它变窄。共振积分是许多峰的总和，分散得较小。在能级间距超过约 10 keV 的地方，例如轻原子核，没有能级靠近热能区：那里的俘获是直接俘获，代码拒绝给出答案。</p>
  <div class="aside">代码位置：<code>physics/resonance/ladder.py</code>（随机矩阵间距、Porter–Thomas 宽度、Breit–Wigner 截面、系综上的热中子俘获与共振积分），<code>ladder_statistics.py</code>（用实测共振序列检验同样的规律），<code>ensemble_runner.py</code>。这些代码在反应程序旁边运行，而不在其内部。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "高度：峰值俘获（对数）· 宽度 Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "峰高：俘获截面（对数坐标）· 宽度：共振宽度 Γ，放大 {#} 倍",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "s 波（+ 宇称）", "p-wave (− parity)": "p 波（− 宇称）",
  "caught {#} times in {#} landings": "{#} 次落点中俘获 {#} 次",
  "each peak: one level of the compound nucleus": "每个峰：复合核的一个能级",
  "each peak: one level of the compound nucleus · about {#} eV apart": "每个峰：复合核的一个能级 · 间隔约 {#} eV",
  // spacing
  "random positions (Poisson)": "随机位置（泊松）",
  "repelling levels (random-matrix)": "相互排斥的能级（随机矩阵）",
  "two repelling sequences mixed": "两个排斥序列混合",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "扎堆与空隙 · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "均匀分开 · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "排斥被部分掩盖 · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "扎堆与空隙 · 间距比 ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "均匀分开 · 间距比 ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "排斥被部分掩盖 · 间距比 ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩：随机 {#}，随机矩阵 {#}",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "各行平均间距相同 · ⟨r̃⟩：随机 {#}，随机矩阵 {#}",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "高度：中子宽度 Γn（线性）",
  "peak height: neutron width Γn, linear scale": "峰高：中子宽度 Γn，线性坐标",
  "yellow: γ width": "黄色：γ 宽度",
  "yellow cap: γ width, nearly the same on every peak": "黄色顶盖：γ 宽度，各峰几乎相同",
  "equal widths: every peak the average": "等宽：每个峰取平均值",
  "rolled widths": "抽取的宽度", "pile of rolled widths": "抽取宽度的分布",
  "× average": "× 平均值", "(in units of the average)": "（以平均值为单位）",
  "dashed: Porter–Thomas": "虚线：Porter–Thomas", "dashed: the Porter–Thomas law": "虚线：Porter–Thomas 分布",
  "bell-curve number x": "钟形曲线随机数 x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "点击“抽取一个宽度”",
  // thermal
  "bound level {#} eV": "束缚能级 {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "{#} eV 处的束缚能级：其尾部抬高此端",
  "resonance integral ≈ {#} b": "共振积分 ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "{#} eV 以上共振积分 ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "途中被峰俘获：{#} · 到达热能区：{#}",
  "each hop: one bounce, the same fraction of energy lost": "每一跳：一次碰撞，损失相同比例的能量",
  // ensemble
  "thermal neutron": "热中子",
  "σ disc": "σ 圆盘", "disc area = σ at {#} eV": "圆盘面积 = {#} eV 处的 σ",
  "{#}k": "{#}k",
  "thermal σ (b)": "热中子 σ (b)", "thermal σ, barns": "热中子 σ，靶恩",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} 个序列 · 热中子 ×{#} · 共振积分 ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · {#} % 的落点被俘获`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · <{#} % 的落点被俘获`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `热中子，{#} eV：σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} 个序列 · 热中子 σ 中位数 ${b}，中间三分之二 ×{#} · 共振积分仅 ×{#}`;
  }
})();
