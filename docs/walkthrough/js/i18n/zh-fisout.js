/* Simplified Chinese: fisout (第 14 章，裂变中子) */
WT.L.ch.fisout = {
  num: "第 14 章", title: "裂变中子", short: "裂变中子",
  html: `
<div class="step">
  <p>每次裂变释放两三个中子：平均 2.4 个。画面顶部一次演示一个裂变：铀核撕成两块碎片，蓝色小球飞出。这些是<b>瞬发</b>中子，在不到百万分之一秒内就已飞出。</p>
  <p>左侧图表统计有多少次裂变释放了 0、1、2、3 …… 个中子。柱子是你引发的裂变；每根柱子上的细线是实测的份额。多引发几次，柱子就会趋近这些线。</p>
  <div class="btns"><button class="btn" data-act="f100">100 次裂变</button><button class="btn ghost" data-act="f1000">1000 次裂变</button></div>
</div>
<div class="step">
  <p>它们生来就很快：平均约 2 MeV，约是室温反应堆中慢中子能量的 8000 万倍。右侧图表按能量对瞬发中子分类。曲线是实测的形状（Watt 谱）：1 MeV 附近有一个隆起，并有一条延伸到 10 MeV 的长尾。</p>
  <p>这样的快中子很少引起铀-235 的下一次裂变，所以反应堆要先把它们减速，后面的章节会说明。</p>
  <div class="btns"><button class="btn" data-act="f100">100 次裂变</button><button class="btn ghost" data-act="f1000">1000 次裂变</button></div>
</div>
<div class="step">
  <p>有少数中子在数秒之后才出现：占全部中子的 0.65 %。有些碎片的中子太多，以至于它们日后衰变时，新的原子核留不住其中一个中子，就把它放了出来。这要等到衰变发生，常常是几秒之后。</p>
  <p>底部这条线是裂变之后的时钟，从 0.01 s 到 100 s；每个刻度比前一个晚十倍。左边的球是全部瞬发中子，同时飞出。每个小圆点是一个缓发中子：在等待期间沿着这条线移动（时钟加速了 20 倍），最后落在它终于飞出的位置。正是这少数迟到的中子使反应堆可以控制：它们把链式反应的响应时间从千分之几秒拉长到数秒。</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 次裂变</button><button class="btn ghost" data-act="clear">清除</button></div>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "n + U{#} → two fragments + neutrons": "n + U{#} → 两块碎片 + 中子",
  "prompt neutrons per fission": "每次裂变的瞬发中子数",
  "lines: measured shares": "细线：实测份额",
  "mean {#}": "平均 {#}",
  "prompt-neutron energy (MeV)": "瞬发中子能量 (MeV)",
  "mean {#} MeV": "平均 {#} MeV",
  "line: measured shape": "曲线：实测形状",
  "prompt": "瞬发",
  "time after fission · clock sped up {#}×": "裂变后的时间 · 时钟加速 {#} 倍",
  "delayed {#} of {#} ({#} %)": "缓发 {#} / {#}（{#} %）",
  "{#} fissions": "{#} 次裂变",
});
