/* Simplified Chinese: preeq (第 7 章，预平衡) */
WT.L.ch.preeq = {
  num: "第 7 章", title: "预平衡发射", short: "预平衡",
  lead: "进入原子核的中子并不会立刻把能量分给所有核子。在最初几次碰撞中，能量大部分集中在一个粒子上，而这个粒子可能直接飞出去。这就是预平衡：“在能量均匀分配之前”的发射。",
  html: `
<div class="step">
  <p>两个势阱，一个装<em class="p">质子</em>，一个装<em class="n">中子</em>。每个小球是处在某个能级上的核子，能级画成梯子的横档；横档从底部一直填满到<b>费米面</b>。位于虚线“自由”线之上的核子有足够的能量逃逸。程序对质子和中子分别追踪。</p>
  <p>入射中子悬在上方，带着全部能量：它自身的能量，加上被俘获时释放的数 MeV（百万电子伏特）。</p>
</div>
<div class="step">
  <h3>粒子–空穴激发</h3>
  <p>快中子撞上“海”中的一个核子，把一部分能量交给它。这个核子跳到一个空横档上，它离开的位置就空了出来：一个<b>空穴</b>（空心圆圈）。所以每次碰撞都产生一个<b>对</b>：多一个被抬起的核子和一个空穴。物理学家把被抬起的核子和空穴合在一起计数，称为<b>激子</b>：第一次碰撞之后有 3 个（2 个被抬起，1 个空穴）。</p>
  <div class="btns"><button class="btn" data-act="collide">碰撞</button><button class="btn ghost" data-act="reset">重新开始</button></div>
  <p>按“碰撞”，观察一次碰撞：俯冲、跳起、留下空穴。多做几次。被撞到的可能是质子，也可能是中子。每碰撞一次，能量就由更多核子分享，所以每个被抬起的核子位置更低，快粒子逃逸的可能性也就更小。</p>
</div>
<div class="step">
  <h3>发射与继续碰撞</h3>
  <p>在每个阶段，最上面的中子要么逃逸（向上箭头，仅当它在自由线之上时），要么再次碰撞（向下箭头）；箭头粗细表示概率。逃逸有多快，可以从逆过程读出：容易吞下某个能量中子的原子核，也容易放出同样能量的中子。吞下有多容易，第 5 章已经算过（这条双向规则称为<b>细致平衡</b>）。碰撞有多快，取决于两个核子相撞有多猛，乘以碰撞之后分享能量的新方式有多少种。</p>
  <div class="ctl"><label for="pe-n">阶段（激子数 n）</label><input id="pe-n" type="range" data-bind="n" min="3" max="11" step="2" value="3" data-instant><output data-show="n" data-fmt="0"></output></div>
  <p>把阶段往上拖。早期一个粒子握有大部分能量，所以逃出的粒子很快。后期能量被摊得很薄，能出来的就很少了。</p>
</div>
<div class="step">
  <h3>预平衡能谱</h3>
  <p>右边的堆积就是<b>能谱</b>：在每个能量上出射多少中子，左边慢，右边快。每个反应沿着链条进行，直到最上面的中子逃逸，颜色表示逃逸的时机：阶段 3 为<em style="font-style:normal;color:var(--warm);font-weight:600">深橙色</em>，越往后越浅；如果是在原子核平静下来之后才出来（第 8 章），则为<em class="n">蓝色</em>。</p>
  <div class="btns"><button class="btn" data-act="run">运行 300 次反应</button></div>
  <p>阶段 3 堆出一个宽而低的穹顶，几乎延伸到最大能量，是唯一能到达那么远的阶段。后面的阶段堆在较低处。蓝色的峰是<b>蒸发</b>：一旦所有核子分享了能量，就只有慢中子零星漏出，就像热液体冒出的蒸汽。</p>
  <div class="ctl"><label for="pe-e">中子能量</label><input id="pe-e" type="range" data-bind="E" min="5" max="60" step="0.5" value="20"><output data-show="E" data-fmt="1"></output></div>
  <p>拖动入射中子的能量：新一批反应开始运行，穹顶延伸得更远。单靠蒸发永远产生不了快中子。</p>
</div>
<div class="step">
  <h3>粒子–空穴态密度</h3>
  <p>计数器逐一列举所有放法：把粒子放到空横档、把空穴开在已填的横档上，使它们的能量之和等于要分享的能量（这里横档间距为 1 MeV）。核子是费米子：两个核子不能占同一个横档，所以粒子必须落在空横档上，空穴只能出现在原来有核子的地方。这就是<b>泡利阻塞</b>。</p>
  <div class="ctl"><label for="pe-u">要分享的能量 (MeV)</label><input id="pe-u" type="range" data-bind="U" min="2" max="16" step="1" value="8" data-instant><output data-show="U" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="addpair">增加一对</button><button class="btn ghost" data-act="droppair">去掉一对</button></div>
  <p>增加一对，计数猛增；提高能量，计数大致按 <i>E</i><sup>n−1</sup> 增长。这个计数就是<b>粒子-空穴态密度</b>，它决定碰撞率：组态越多，碰撞能通向的去处就越多。程序在真实的能级梯子上计数，横档间距只有零点几 MeV，并加入了一个高能时才能看到的限制：空穴不能位于势阱底部之下。</p>
</div>
<div class="step">
  <h3>集团发射</h3>
  <p>小的集团也可以提前离开。在<b>拾取反应</b>中，一个正要出射的质子在表面抓住一个中子，与它一起作为<em class="n">氘核</em>离开；抓住两个则得到氚核或氦-3。在<b>敲出反应</b>中，入射中子击中一个已在表面附近形成的<em class="a">α粒子</em>（两个质子和两个中子），把它敲出去。程序对两者都采用 Kalbach 公式。</p>
  <div class="btns"><button class="btn ghost" data-act="pickup">拾取一个中子 → d</button><button class="btn ghost" data-act="knock">敲出一个 α</button></div>
  <p>按按钮观看一次过程。两者都使氘核和 α 粒子拥有各自的快速尾巴，起点刚好高于把它们各自拉出所需的能量。</p>
</div>
<div class="step">
  <h3>多重预平衡发射</h3>
  <p>在高能下，第一次碰撞也可能交给被撞核子很多能量。当快中子离开时，第二个核子可能仍有超过逃逸所需的 8 MeV（自由线）的能量，于是它也飞出去：一次反应产生两个快粒子。画面一次重放一个反应，并说明每一时刻发生了什么；每个球旁边的数字是它的能量。</p>
  <div class="ctl"><label for="pe-e2">中子能量</label><input id="pe-e2" type="range" data-bind="E" min="5" max="80" step="0.5" value="40"><output data-show="E" data-fmt="1"></output></div>
  <p>拖动能量。在约 20 MeV 以下，第二个核子很少能越过这条线；超过之后，越来越多的反应放出两个快粒子。这就是<b>多次预平衡</b>发射，程序从 20 MeV 起将其计入。没有离开的部分成为下一章的复合核。在几 MeV（计算所用靶核的最高分立能级）以下，程序完全跳过这条链。</p>
  <div class="aside">代码位置：<code>preeq/exciton.py</code>（双组分激子链，碰撞率与逃逸率），<code>density/particle_hole.py</code>（含泡利修正和有限深势阱修正的粒子-空穴态密度），<code>preeq/complex.py</code>（Kalbach 拾取、削裂和 α 敲出），<code>preeq/multi.py</code>（多次预平衡），<code>compound/normalization.py</code>（移交给复合核）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // wells
  "protons": "质子",
  "neutrons": "中子",
  "Fermi": "费米",
  "Fermi surface": "费米面",
  "free": "自由",
  "free: can escape": "自由：可逃逸",
  "all the energy in one nucleon": "全部能量集中在一个核子上",
  "{#} particle, {#} holes": "{#} 个粒子，{#} 个空穴",
  // pairs
  "{#} particle, {#} holes: n = {#}": "{#} 个粒子，{#} 个空穴：n = {#}",
  "{#} particle, {#} hole: n = {#}": "{#} 个粒子，{#} 个空穴：n = {#}",
  "{#} particles, {#} hole: n = {#}": "{#} 个粒子，{#} 个空穴：n = {#}",
  "{#} particles, {#} holes: n = {#}": "{#} 个粒子，{#} 个空穴：n = {#}",
  "protons: {#} lifted, {#} hole": "质子：抬起 {#}，空穴 {#}",
  "protons: {#} lifted, {#} holes": "质子：抬起 {#}，空穴 {#}",
  "neutrons: {#} lifted, {#} hole": "中子：抬起 {#}，空穴 {#}",
  "neutrons: {#} lifted, {#} holes": "中子：抬起 {#}，空穴 {#}",
  "chain ends: the rest becomes a compound nucleus": "链结束：其余形成复合核",
  // fork
  "about {#} MeV above surface": "高于费米面约 {#} MeV",
  "escapes  {#}%": "逃逸  {#}%",
  "collides again  {#}%": "再次碰撞  {#}%",
  "below the free line: it cannot leave": "在自由线之下：无法离开",
  "n = {#}: {#} particles, {#} hole, {#} MeV": "n = {#}：{#} 个粒子，{#} 个空穴，{#} MeV",
  "n = {#}: {#} particles, {#} holes, {#} MeV": "n = {#}：{#} 个粒子，{#} 个空穴，{#} MeV",
  "stage n = {#}: {#} particles and {#} hole share {#} MeV": "阶段 n = {#}：{#} 个粒子和 {#} 个空穴分享 {#} MeV",
  "stage n = {#}: {#} particles and {#} holes share {#} MeV": "阶段 n = {#}：{#} 个粒子和 {#} 个空穴分享 {#} MeV",
  // tail
  "max {#} MeV": "最大 {#} MeV",
  "slow": "慢",
  "fast →": "快 →",
  "stage {#}": "阶段 {#}",
  "chain over: compound": "链结束：复合核",
  "left at:": "离开于：",
  "neutron left at:": "中子离开于：",
  "evaporation": "蒸发",
  "{#} of {#} landed · {#} left during the chain": "已落下 {#}/{#} · 链中离开 {#}",
  // pauli
  "well bottom: no deeper hole": "阱底：空穴不能更深",
  "bottom of the well": "势阱底部",
  "{#} MeV to share": "分享 {#} MeV",
  "{#} particles · {#} hole": "{#} 个粒子 · {#} 个空穴",
  "{#} particles · {#} holes": "{#} 个粒子 · {#} 个空穴",
  "ways, all counted": "种放法，全部计入",
  "arrangements so far": "目前的组态数",
  "one more pair: {#} ways": "再加一对：{#} 种",
  "never two on one rung · holes only where a nucleon was": "一档不容两个 · 空穴只在原有核子处",
  "(first {#} shown as ticks)": "（前 {#} 种以刻度显示）",
  // cluster
  "a deuteron leaves": "一个氘核离开",
  "grabs a neutron at the edge": "在边缘抓住一个中子",
  "a fast proton heads out": "一个快质子向外飞",
  "an α ({#} protons + {#} neutrons) waits at the edge": "一个 α（{#} 个质子 + {#} 个中子）在边缘等待",
  "knocked straight out": "被直接敲出",
  // second
  "first fast neutron": "第一个快中子",
  "second fast proton": "第二个快质子",
  "second fast neutron": "第二个快中子",
  "below the free line: stays": "在自由线之下：留下",
  "below the free line: it stays": "在自由线之下：留下",
  "the rest settles: compound nucleus": "其余趋于平静：复合核",
  "{#} MeV carried in": "带入 {#} MeV",
  "second fast particle in {#} of the last {#} reactions": "第二个快粒子：{#} 次（最近 {#} 次反应）",
});

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "bump {#}: a proton in the sea was hit, jumped up, and left a hole": "碰撞 {#}：海中一个质子被撞上跳，留下一个空穴",
  "bump!": "碰！",
  "hole": "空穴",
  "lifted": "被抬升",
  "free line: more than {#} MeV needed to get out": "自由线：逃出需超过 {#} MeV",
  "a fast neutron comes in with {#} MeV": "一个快中子带着 {#} MeV 射入",
  "bump: it hits a neutron in the sea, which jumps up and leaves a hole": "碰撞：它撞上海中一个中子，该中子上跳并留下空穴",
  "neutron: {#} MeV": "中子：{#} MeV",
});
