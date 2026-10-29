/* Simplified Chinese: slowing (第 19 章，中子慢化) */
WT.L.ch.slowing = {
  num: "第 19 章", title: "中子慢化", short: "慢化",
  html: `
<div class="step">
  <p>每次与氢碰撞要损失约一半的能量。裂变中子从 2 MeV 出发，在水中反复弹跳。氢原子核与中子质量相同，所以像台球一样，每次碰撞平均带走中子一半的能量。</p>
  <p>图表画出每次碰撞后中子的能量；侧边每个标注的能量是上一个的千分之一。每次损失相同的份额，就形成一条直线下滑，即虚线。大约经过 18 次碰撞，中子达到<b>热</b>能量 0.025 eV，此时温热的水把它加速的次数与使它减速的次数一样多。氧要重 16 倍：每次碰撞只带走一点点，需要一百多次。</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">氢</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">氧</button><button class="btn" data-act="again">再来一次</button></div>
</div>
<div class="step">
  <p>在约 1 eV 以下，分子的化学键决定每次碰撞的结果。每个氢都与它的氧相连（亮线）。慢中子不再撞到自由的氢：它撞到的是整个分子，重 18 倍，所以一次普通的碰撞几乎带不走能量。</p>
  <p>它也可以让分子转动或振动，但每次只能交出固定份额的能量：0.06、0.2 或 0.45 eV（亮闪光）。温热的分子有时会把这样一份能量还回来。在图表上，1 eV 以下的阴影带就是这种效应起作用的地方。关掉化学键，可以与自由氢作比较。</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">化学键</button><button class="btn" data-act="again">再来一次</button></div>
</div>
<div class="step">
  <p>计算程序需要把这一切整理成一张表：<b>散射律</b>，也就是这张图。横向：撞击有多猛，即 α（传给分子的动量；擦边而过时小，正面撞击时大）。纵向：中子获得（向上）或失去（向下）的能量 β，以水的热能 0.025 eV 为单位计数。亮表示可能，淡表示罕见。</p>
  <p>轮廓线是所选能量的中子能够到达的范围：它损失的能量不能超过自身所有，而每一种能量变化只允许一定范围的撞击。拖动能量，轮廓就会扩大或缩小。没有化学键时，这张图是自由氢气体，沿着虚线的反冲线有一条亮脊；有化学键时，分子会增加亮条纹，即它固定的能量份额。INCOGNITA 自己计算了水和铍的散射律：<a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>。</p>
  <div class="ctl"><label for="slo-e">中子能量 (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">化学键</button></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
