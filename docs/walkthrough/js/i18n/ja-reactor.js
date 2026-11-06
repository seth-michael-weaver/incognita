/* Japanese: reactor (原子炉が電気をつくるしくみ) */
WT.L.ch.reactor = {
  num: "レッスン 2", title: "原子炉が電気をつくるしくみ", short: "原子炉",
  html: `
<div class="step">
  <h3>燃料</h3>
  <p>ウランは指先ほどの大きさのセラミックのペレットに焼き固められ、長い金属の燃料棒に積み重ねられます。燃料棒は束ねられて燃料集合体になります。ペレット1個で、石炭約1トンを燃やすのとほぼ同じ熱が得られます。</p>
  <div class="ctl"><label for="rea-z">ズームアウト</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>原子の分裂が熱を生む</h3>
  <p>炉心では、分裂するウラン原子が、燃料棒の間を上へ流れる水を温めます。同じ水が中性子を減速させ、さらに多くの原子を分裂させられるようにします。高い圧力のおかげで、325 °Cでも水は沸騰しません。</p>
</div>
<div class="step">
  <h3>蒸気がタービンを回す</h3>
  <p>熱い水は細い管を通して2つ目のループに熱を渡し、そこで水が沸騰します。蒸気はタービンと発電機を回し、その後、冷たい川や海の水で冷やされて水に戻ります。熱のおよそ3分の1が電気になります。</p>
</div>
<div class="step">
  <h3>制御棒</h3>
  <p>制御棒は中性子を吸収します。差し込むと分裂する原子が減り、熱も蒸気も電気も減ります。引き抜くと出力が上がります。</p>
  <div class="ctl"><label for="rea-rod">挿入した制御棒（%）</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // plant schematic
  "reactor": "原子炉",
  "reactor vessel": "原子炉容器",
  "core": "炉心",
  "control rods": "制御棒",
  "steam gen.": "蒸気発生器",
  "steam generator": "蒸気発生器",
  "turbine": "タービン",
  "gen.": "発電機",
  "generator": "発電機",
  "condenser": "復水器",
  "sea or river water": "海水または川の水",
  "{#} °C out": "出口 {#} °C",
  "{#} °C in": "入口 {#} °C",
  "steam ~{#} °C": "蒸気 約 {#} °C",
  "{#} bar: hot, but no boiling": "{#} bar：高温でも沸騰しない",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar の圧力で水は {#} °C でも液体のまま",
  "the water also slows the neutrons": "水は中性子の減速も担う",
  "the water carries the heat and slows the neutrons": "水は熱を運び、中性子を減速させる",
  "heat {#} MW": "熱 {#} MW",
  "electric {#} MW": "電気 {#} MW",
  "electricity {#} MW": "電気出力 {#} MW",
  "chain stopped; fuel still warm (afterheat)": "連鎖停止、燃料はまだ熱い（崩壊熱）",
  "chain reaction stopped; the fuel still gives off afterheat": "連鎖反応は止まったが、燃料はまだ崩壊熱を出している",
  "turbine speed fixed by the grid; more steam, more push": "回転数は送電網で固定、蒸気が多いほど強く押す",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "タービンの回転数は送電網で決まり、蒸気が多いほど強く押す",
  "{#}/{#} of the heat goes to the water": "熱の {#}/{#} は水へ捨てられる",
  "about two thirds of the heat leaves through the condenser": "熱の約3分の2は復水器から捨てられる",
  "illustration": "イメージ図",
  // fuel zoom
  "drag sideways to zoom": "横にドラッグでズーム",
  "drag sideways to zoom out": "横にドラッグでズームアウト",
  "UO₂ pellet, {#} cm": "UO₂ ペレット、{#} cm",
  "uranium oxide pellet, about {#} cm": "酸化ウランのペレット、約 {#} cm",
  "{#} tonne of coal": "石炭 {#} トン",
  "about {#} tonne of coal (or {#} m³ of gas)": "石炭 約 {#} トン（またはガス {#} m³）",
  "same heat, roughly": "ほぼ同じ熱量",
  "fuel rod, ~{#} m": "燃料棒、約 {#} m",
  "fuel rod, about {#} m long": "燃料棒、長さ約 {#} m",
  "~{#} pellets inside": "ペレット約 {#} 個",
  "about {#} pellets in a metal tube": "金属管にペレット約 {#} 個",
  "(not to scale)": "（縮尺は正確でない）",
  "assembly: {#} rods": "集合体：燃料棒 {#} 本",
  "fuel assembly from above: {#} rods": "燃料集合体を上から：燃料棒 {#} 本",
  "rings: control-rod guide tubes": "輪：制御棒案内管",
  "rings: tubes the control rods slide into": "輪：制御棒が入る案内管",
  "core: {#} assemblies": "炉心：集合体 {#} 体",
  "the core from above: {#} assemblies": "炉心を上から：燃料集合体 {#} 体",
  "~{#} rods, ~{#} m across": "燃料棒 約 {#} 本、直径 約 {#} m",
  "about {#} rods in a cylinder about {#} m across": "約 {#} 本の燃料棒が直径約 {#} m の円筒に",
  "pellet": "ペレット",
  "rod": "燃料棒",
  "assembly": "集合体",
});
