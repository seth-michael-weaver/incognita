/* Japanese: chains (崩壊系列と放射平衡) */
WT.L.ch.chains = {
  num: "レッスン 4", title: "崩壊系列と放射平衡", short: "崩壊系列",
  html: `
<div class="step">
  <h3>親、娘、孫</h3>
  <p>崩壊してできた原子核も不安定なことがよくあります。親核種が崩壊して娘核種になり、娘核種がさらに崩壊して安定な孫核種になります。娘核種はいったん増えてから減っていきます。どこまで増えるかは、親核種と比べてどれだけ速く崩壊するかで決まります。</p>
  <div class="ctl"><label for="ch-t2">娘核種の半減期（s）</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">新しい試料</button></div>
</div>
<div class="step">
  <h3>永続平衡：ラジウムとラドン</h3>
  <p>ラジウム226の半減期は1600年ですが、その娘核種であるラドン222（気体）はわずか3.8日です。密閉した容器の中では、ラドンは生成されるのと同じ速さで崩壊するようになるまで増えていきます。<i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>)、ここでλはラドンの崩壊定数です。数週間たつと、両者は同じ割合で崩壊するようになります。</p>
  <div class="btns"><button class="btn" data-act="vent">容器を開ける</button></div>
</div>
<div class="step">
  <h3>過渡平衡：テクネチウム・カウ</h3>
  <p>病院には、モリブデン99（66時間）を吸着させたカラムが届きます。これは、医療で最も広く使われるトレーサーであるテクネチウム99m（6時間）をつくり続けます。毎朝テクネチウムを洗い出しても、ゆっくり減っていくモリブデンに従って再び増えてきます。</p>
  <div class="btns"><button class="btn" data-act="milk">ミルキングする</button><button class="btn ghost" data-act="genre">新しいジェネレーター</button></div>
</div>
<div class="step">
  <h3>ウラン系列をたどる</h3>
  <p>ウラン238は14段階を経て安定な鉛になります。この図では、アルファ崩壊で下に2つ、左に2つ移り、ベータ崩壊で上に1つ、左に1つ移ります。長い間乱されていない古いウラン鉱石では、系列のどの核種も同じ割合で崩壊しています。</p>
  <div class="btns"><button class="btn" data-act="next">次の崩壊</button><button class="btn ghost" data-act="restart">最初から</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // element symbols (chart rows)
  "Pb": "Pb", "Bi": "Bi", "Po": "Po", "At": "At", "Rn": "Rn", "Fr": "Fr", "Ra": "Ra", "Ac": "Ac", "Th": "Th", "Pa": "Pa", "U": "U",
  // parent, daughter, granddaughter
  "parent ({#} s): {#}": "親（{#} s）：{#}",
  "daughter ({#} s): {#}": "娘（{#} s）：{#}",
  "granddaughter (stable): {#}": "孫（安定）：{#}",
  "parent {#}": "親 {#}",
  "daughter {#}": "娘 {#}",
  "stable {#}": "安定 {#}",
  "daughter peaks: {#} %": "娘の最大：{#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "説明用の半減期",
  // radium jar
  "radium{#}": "ラジウム{#}",
  "radon{#} gas": "ラドン{#}（気体）",
  "radium": "ラジウム",
  "radium activity": "ラジウムの放射能",
  "radon": "ラドン",
  "radon activity": "ラドンの放射能",
  "{#} d": "{#} 日",
  "days →": "日 →",
  "day {#}: radon at {#} % of radium": "{#} 日目：ラドンはラジウムの {#} %",
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(ラドン) = A(ラジウム) × ({#} − exp(−λt))",
  // Mo/Tc generator
  "Mo{#}": "Mo{#}",
  "molybdenum{#}": "モリブデン{#}",
  "Tc{#}m out": "Tc{#}m 取り出し",
  "Tc{#}m to the patient": "Tc{#}m を患者へ",
  "dashed: never milked": "破線：ミルキングしない場合",
  "activity": "放射能",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "前回のミルキングから {#} 時間 · Tc{#}m：{#} %（Mo{#} 比）",
  "regrows to its peak in about {#} hours": "約 {#} 時間で最大まで戻る",
  // U-238 series
  "neutrons →": "中性子 →",
  "protons ↑": "陽子 ↑",
  "grey: stable": "灰色：安定",
  "alpha: loses {#} protons and {#} neutrons": "α崩壊：陽子 {#} 個と中性子 {#} 個を失う",
  "alpha: {#} p, {#} n": "α：{#} p、{#} n",
  "beta: a neutron becomes a proton": "β崩壊：中性子が陽子に変わる",
  "beta: n → p": "β：n → p",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · 半減期 {#} 十億年 · 次はα崩壊",
  "U{#} · half-life {#} yr · alpha next": "U{#} · 半減期 {#} 年 · 次はα崩壊",
  "Th{#} · half-life {#} days · beta next": "Th{#} · 半減期 {#} 日 · 次はβ崩壊",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · 半減期 {#} 年 · 次はα崩壊",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · 半減期 {#} 分 · 次はβ崩壊",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · 半減期 {#} 年 · 次はα崩壊",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · 半減期 {#} 日 · 次はα崩壊",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · 半減期 {#} 分 · 次はα崩壊",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · 半減期 {#} µs · 次はα崩壊",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · 半減期 {#} 日 · 次はα崩壊",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · 半減期 {#} 分 · 次はβ崩壊",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · 半減期 {#} 年 · 次はβ崩壊",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · 半減期 {#} 分 · 次はβ崩壊",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · 半減期 {#} 日 · 次はβ崩壊",
  "Pb{#}: stable, the chain ends": "Pb{#}：安定、系列はここで終わり",
  "step {#} of {#} · tap the nucleus": "ステップ {#}/{#} · 原子核をタップ",
});
