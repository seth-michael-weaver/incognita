/* Japanese: xenon (キセノン毒作用) */
WT.L.ch.xenon = {
  num: "レッスン 1", title: "キセノン毒作用", short: "キセノン",
  html: `
<div class="step">
  <h3>核分裂がつくる毒物質</h3>
  <p>核分裂の約6.6 %は、ヨウ素135を経てキセノン135になります。キセノン135は知られている中で最も強い中性子吸収体です。2日ほどかけて増え、やがて中性子による燃焼と崩壊で、できるのと同じ速さで消えるようになります。出力が高いほど燃焼も速いので、量は飽和します。</p>
  <div class="ctl"><label for="xe-p1">出力（%）</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>キセノンの谷</h3>
  <p>原子炉を止めると燃焼は止まりますが、すでにできたヨウ素はキセノンに変わり続けます。毒物質は約9時間後に最大になり、制御棒で取り戻せる反応度を上回るので、原子炉は再起動できません。その後2～3日かけて減っていきます。</p>
  <div class="ctl"><label for="xe-th">停止後の時間（h）</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>停止と再起動</h3>
  <p>今度は1秒あたり3時間の速さで実際に動かします。停止してから再起動を試してみましょう。谷の中では拒否されます。しばらくすると、中性子がキセノンを燃やして取り除きます。出力を変えるだけでも、キセノンは何時間も揺れ動きます。</p>
  <div class="ctl"><label for="xe-p3">出力（%）</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">停止</button><button class="btn ghost" data-act="xerestart">再起動</button></div>
</div>
<div class="step">
  <h3>キセノン振動</h3>
  <p>大きな炉心では、左右の両側は弱くしか結びついていません。片側に制御棒を押し込むと、そこでは中性子束が減ってキセノンの燃焼も減るため、出力は反対側へ移り、やがて戻ってきます。周期はおよそ1日です。炉心が大きいほど振動は大きくなり、運転員が抑えなければ成長します。</p>
  <div class="ctl"><label for="xe-wd">炉心の大きさ（m）</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">左側に制御棒を押し込む</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "drag": "ドラッグ",
  "equilibrium {#} %": "平衡 {#} %",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "核分裂 → ヨウ素{#}（{#} h）→ キセノン{#}（{#} h）→ Cs{#}",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "核分裂 → ヨウ素{#}（{#} h）→ キセノン{#}（{#} h）→ Cs{#}  ·  Xe{#} の中性子吸収：{#}×10⁶ バーン",
  "illustration": "イメージ図",
  "left {#} %": "左 {#} %",
  "more power left": "左の出力が大",
  "more power right": "右の出力が大",
  "no restart": "再起動不可",
  "peak {#} % at {#} h": "最大 {#} %（{#} h）",
  "power": "出力",
  "refused: more xenon than spare reactivity": "拒否：キセノンが余裕の反応度を上回る",
  "restarted": "再起動しました",
  "right {#} %": "右 {#} %",
  "running at {#} % · xenon {#} %": "出力 {#} % で運転中 · キセノン {#} %",
  "shut down": "停止",
  "shut down · in the pit · xenon {#} %": "停止中 · 谷の中 · キセノン {#} %",
  "shut down · restart possible · xenon {#} %": "停止中 · 再起動可能 · キセノン {#} %",
  "shut down · in the pit": "停止中 · 谷の中",
  "shut down · restart possible": "停止中 · 再起動可能",
  "shutdown": "停止",
  "spare reactivity": "余裕の反応度",
  "spare reactivity the rods can give": "制御棒で取り戻せる反応度",
  "swing period {#} h · {#} m core: the swing dies away": "振動周期 {#} h · {#} m の炉心：振動は減衰",
  "swing period {#} h · {#} m core: the swing dies away slowly": "振動周期 {#} h · {#} m の炉心：振動はゆっくり減衰",
  "swing period {#} h · {#} m core: the swing grows": "振動周期 {#} h · {#} m の炉心：振動は成長",
  "tap a side to push rods in": "片側をタップして制御棒を挿入",
  "tap the core to restart": "炉心をタップして再起動",
  "tap the core to shut down": "炉心をタップして停止",
  "too poisoned to restart": "毒物質が多すぎて再起動できない",
  "xenon worth (% of k)": "キセノンの反応度価値（k の %）",
  "xenon{#} + n → Xe{#}: {#} million barns": "キセノン{#} + n → Xe{#}：{#}×10⁶ バーン",
  "{#} % power · {#} h after start-up · xenon {#} %": "出力 {#} % · 起動後 {#} h · キセノン {#} %",
  "{#} h": "{#} 時間",
  "{#} h after shutdown · xenon {#} % · cannot restart": "停止後 {#} h · キセノン {#} % · 再起動できない",
  "{#} h after shutdown · xenon {#} % · restart possible": "停止後 {#} h · キセノン {#} % · 再起動可能",
  "{#} m core: push the rods to start a swing": "{#} m の炉心：制御棒を押し込んで振動を起こす",
});
