/* Chinese: xenon (氙中毒) */
WT.L.ch.xenon = {
  num: "第1课", title: "氙中毒", short: "氙",
  html: `
<div class="step">
  <h3>裂变产生的毒物</h3>
  <p>约 6.6 % 的裂变经由碘-135 生成氙-135：已知最强的中子吸收体。它会积累约两天，直到中子燃耗掉它、加上衰变消除它的速度与它生成的速度相当。功率越高，燃耗也越快，所以氙浓度会达到饱和。</p>
  <div class="ctl"><label for="xe-p1">功率（%）</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>碘坑</h3>
  <p>停堆后燃耗停止，但已经生成的碘仍在不断衰变成氙。毒物约九小时后达到峰值，超过控制棒所能补偿的反应性，于是反应堆无法重新启动；它要经过两到三天才会消退。</p>
  <div class="ctl"><label for="xe-th">停堆后的小时数</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>停堆与再启动</h3>
  <p>现在实时运行，每秒三小时。先停堆，再尝试重新启动：处在碘坑中时启动被拒绝；稍后中子会把氙烧掉。仅仅改变功率，也会使氙在数小时内起伏变化。</p>
  <div class="ctl"><label for="xe-p3">功率（%）</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">停堆</button><button class="btn ghost" data-act="xerestart">再启动</button></div>
</div>
<div class="step">
  <h3>氙振荡</h3>
  <p>在大型堆芯中，两侧之间只是松散耦合。把控制棒插入一侧：那里通量降低，烧掉的氙减少，于是功率向另一侧偏移，然后又摆回来，大约每天一次。堆芯越大，摆动越会增长，除非运行人员加以抑制。</p>
  <div class="ctl"><label for="xe-wd">堆芯尺寸（m）</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">把控制棒插入左侧</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // chain line
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "裂变 → 碘{#}（{#} h）→ 氙{#}（{#} h）→ Cs{#}",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "裂变 → 碘{#}（{#} h）→ 氙{#}（{#} h）→ Cs{#}  ·  Xe{#} 吞噬中子：{#} 百万靶",
  "xenon{#} + n → Xe{#}: {#} million barns": "氙{#} + n → Xe{#}：{#} 百万靶",
  "xenon{#}": "氙{#}",
  // plot
  "xenon worth (% of k)": "氙价值（k 的 %）",
  "equilibrium {#} %": "平衡值 {#} %",
  "peak {#} % at {#} h": "峰值 {#} %，在 {#} h",
  "spare reactivity": "剩余反应性",
  "spare reactivity the rods can give": "控制棒可提供的剩余反应性",
  "no restart": "无法启动",
  "too poisoned to restart": "毒物过多，无法再启动",
  "shutdown": "停堆",
  "power": "功率",
  "drag": "拖动",
  "{#} h": "{#} h",
  "more power left": "左侧功率较高",
  "more power right": "右侧功率较高",
  // core
  "left {#} %": "左 {#} %",
  "right {#} %": "右 {#} %",
  "tap a side to push rods in": "点击一侧插入控制棒",
  "tap the core to restart": "点击堆芯再启动",
  "tap the core to shut down": "点击堆芯停堆",
  "shut down": "已停堆",
  "restarted": "已再启动",
  "refused: more xenon than spare reactivity": "被拒绝：氙多于剩余反应性",
  // readouts
  "{#} % power · {#} h after start-up · xenon {#} %": "{#} % 功率 · 启动后 {#} h · 氙 {#} %",
  "{#} h after shutdown · xenon {#} % · restart possible": "停堆后 {#} h · 氙 {#} % · 可以再启动",
  "{#} h after shutdown · xenon {#} % · cannot restart": "停堆后 {#} h · 氙 {#} % · 无法再启动",
  "running at {#} % · xenon {#} %": "以 {#} % 运行 · 氙 {#} %",
  "shut down · in the pit · xenon {#} %": "已停堆 · 处于碘坑中 · 氙 {#} %",
  "shut down · restart possible · xenon {#} %": "已停堆 · 可以再启动 · 氙 {#} %",
  "swing period {#} h · {#} m core: the swing dies away": "摆动周期 {#} h · {#} m 堆芯：摆动逐渐衰减",
  "swing period {#} h · {#} m core: the swing dies away slowly": "摆动周期 {#} h · {#} m 堆芯：摆动缓慢衰减",
  "swing period {#} h · {#} m core: the swing grows": "摆动周期 {#} h · {#} m 堆芯：摆动增长",
  "{#} m core: push the rods to start a swing": "{#} m 堆芯：插入控制棒以引发摆动",
  "illustration": "示意图",
});
