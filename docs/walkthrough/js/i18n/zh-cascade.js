/* Simplified Chinese (简体中文): cascade (chapter 8) */
WT.L.ch.cascade = {
  num: "第 11 章", title: "沿核素图而下", short: "级联",
  lead: "一次发射很少就是终点：留下的原子核往往仍然足够热，可以再次发射。",
  html: `
<div class="step">
  <p>一个中子已经离开复合核（左），它留下的<b>剩余核</b>（右）仍然很热。橙色小球代表能量。剩余核的基态位置更高，高出的正是中子的<b>分离能</b> S<sub>n</sub>，即把它拉出来所需的代价。</p>
  <p>每离开一个中子，小球就下落一段，落差等于该中子的动能。小球停下的位置就是剩余核的<b>激发能</b>，也就是它多余的能量；右侧的点记录每次落点。</p>
  <div class="ctl"><label for="cs-e">中子能量</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>发射出的中子通常很慢，所以大多数落差都很短。蓝点位于虚线所示的中子阈能之上：它们还能再发射第二个中子，即 (n,2n) 反应。低于约 11 MeV 时，没有一个能到达那里。</p>
</div>
<div class="step">
  <h3>在核素图上漫步</h3>
  <p>这些流线是反应在<b>核素图</b>一角上的行走路线。核素图按中子数 N（横向）和质子数 Z（纵向）排列原子核。每条路线都从加框的复合核方格出发；每个方格以终止于此的反应命名。</p>
  <p>发射一个<em class="n">中子</em>向左移一格，一个<em class="p">质子</em>向下移一格，一个<em class="a">α粒子</em>（两个质子、两个中子）沿对角线移两格。流线的宽度表示走这一步的份额；色调和百分比表示反应在哪里终止。</p>
  <div class="ctl"><label for="cs-e4">中子能量</label><input id="cs-e4" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">发射 200 次反应</button></div>
  <p>每一步都要付出 7 到 11 MeV 的分离能，所以即使在 30 MeV，这段路最多也只有三四步。</p>
</div>
<div class="step">
  <h3>自上而下，逐个区间</h3>
  <p>程序从上到下清空每个原子核，每次处理一个能量切片，即一个<b>能量区间</b>。右边是第一次发射后的剩余核；左边是它的子核，少一个中子。橙色小球是在各区间中等待的反应。这里每个区间宽 1 MeV；程序每个原子核大约用 40 个区间，大小按可用能量确定。</p>
  <p>标记扫过一个区间时，每个小球按第 9 章的竞争选择一个出口：一个光子（<em class="g">γ</em>）使它落到更低的区间，一个<em class="n">中子</em>把它移入子核，一个质子或 α 粒子则把它带出画面。低于所有阈能时，光子把剩下的部分带到基态（灰色）。随后再扫子核。</p>
  <div class="ctl"><label for="cs-e3">中子能量</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">重新开始</button></div>
  <p>光子只会向下落，而且每个原子核都在它的子核之前处理完，所以不会有东西落入已经清空的区间。</p>
</div>
<div class="step">
  <h3>为每段历程命名</h3>
  <p>每次演示一个反应：标记在核素图上跳动，每个发射出的粒子落入托盘。装满的托盘给出<b>排他反应道</b>的名称，例如 (n,2n)；光子不计入。程序为每个反应道给出各自的截面（即它发生的可能性，表示为等效的靶面积）。</p>
  <div class="btns"><button class="btn ghost" data-act="next">下一个反应道</button></div>
  <p>逐个浏览。(n,np) 演示两次，一次先发中子，一次先发质子：同一个方格，同一个托盘，同一个反应道。接着，一个虚影氘核（一个质子和一个中子的束缚态）一步跳到同一方格：它的托盘写着 d，这是另一个反应道 (n,d)。</p>
</div>
<div class="step">
  <h3>一切终结之处</h3>
  <p>现在每个方格里都有几层架子：墨色代表<b>基态</b>，绿色（在两个方格中）代表<b>同质异能态</b>，即寿命足够长、可以算作独立产物的激发态。堆的高度就是<b>剩余核产生</b>：反应生成了多少各种原子核。</p>
  <div class="ctl"><label for="cs-e2">中子能量</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">发射 200 次反应</button></div>
  <p>拖动能量：下一批反应使用新能量，旧的堆逐渐淡去。随着能飞出的粒子增多，产物离起点越来越远。每段历程都终止在某层架子上，而活化测量看到的正是这些堆：先辐照样品，再统计每种产物的衰变。</p>
  <div class="aside">代码位置：<code>emission/multiple.py</code>（遍历原子核与区间的循环、γ 级联），<code>emission/feeding.py</code>（链上每个原子核的网格与输入），<code>compound/continuum.py</code>（单个区间的衰变），<code>emission/channels.py</code>（排他反应道、剩余核产生、同质异能分支），<code>emission/binary.py</code>（第一次发射的记账）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // reaction names on the squares (unchanged)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "复合核", "target": "靶核",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "中子数 →",
  // scene 1
  "levels": "能级",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "基态",
  "residual": "剩余核", "residual (one neutron fewer)": "剩余核（少一个中子）",
  "n threshold": "n 阈能", "its neutron threshold": "其中子阈能",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "落差 = 中子动能",
  "{#} % land above the threshold: a second neutron can leave": "{#} % 落在阈能之上：可再发射一个中子",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % 落在阈能之上：可再发射一个中子",
  "all land below the threshold: only photons remain": "全部落在阈能之下：只剩光子",
  "{#} % above threshold: (n,{#}n) possible": "{#} % 高于阈能：可发生 (n,{#}n)",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % 高于阈能：可发生 (n,{#}n)",
  "all below threshold: photons only": "全部低于阈能：只有光子",
  // scene 2
  "incoming neutron: {#} MeV": "入射中子：{#} MeV",
  "shade and % = where reactions end": "色调与 % = 反应终点",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "宽度 = 流量 · 色调与 % = 终止于该核的反应份额",
  // scene 3
  "residual (first step)": "剩余核（第一步）",
  "daughter: n fewer": "子核：少一个 n", "daughter (one neutron fewer)": "子核（少一个中子）",
  "now: {#}–{#} MeV": "当前：{#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "完成：{#} 经质子或 α 离开，其余停在基态",
  "done: everything sits on a ground state": "完成：全部停在基态",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "橙球 = 区间中等待的反应 · 灰色 = 已到基态 · 浅色区间 = 已清空",
  // scene 4
  "collected": "已收集",
  "tray: d": "托盘：d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "氘核落在同一方格，但托盘写着 d：反应道 (n,d)",
  "tray: n n  →  (n,{#}n)": "托盘：n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "托盘：n  →  (n,n′)",
  "tray: p  →  (n,p)": "托盘：p  →  (n,p)",
  "tray: n p  →  (n,np)": "托盘：n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "托盘：n p  →  (n,np) · 同一方格，同一托盘",
  "tray: a  →  (n,α)": "托盘：a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "托盘：n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "托盘为空，只有光子：(n,γ)，俘获",
  "each emitted particle falls into the tray": "每个发射的粒子落入托盘",
  "no particle gets out: only photons": "没有粒子飞出：只有光子",
  "incoming neutron: {#} MeV · channel {#} of {#}": "入射中子：{#} MeV · 反应道 {#}/{#}",
  // scene 5
  "isomer": "同质异能态",
  "batch of {#} at {#} MeV": "{#} 次反应，{#} MeV",
  "ink shelf: ground state · green: isomer": "墨色：基态 · 绿色：同质异能态",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "墨色架：基态 · 绿色架：同质异能态 · 堆高 = 该核的产量",
});
