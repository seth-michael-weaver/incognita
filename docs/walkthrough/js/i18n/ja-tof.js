/* Japanese: tof (第17章、飛行時間測定) */
WT.L.ch.tof = {
  num: "第17章", title: "飛行時間測定", short: "ピークの測定",
  html: `
<div class="step">
  <p>中性子の飛行時間からそのエネルギーがわかります。さまざまなエネルギーの中性子を含む短いパルスが線源を出て、空の管を検出器まで一斉に走ります。速いものほど先に着きます。管の長さ<i>L</i>は既知なので、到着時間<i>t</i>から中性子の速さが、速さからエネルギーが求まります。</p>
  <div class="formula">E = (72.3 · L / t)²   （E は eV、L は m、t は μs）</div>
  <p>管の上の時計はパルスからの実際の時間を数えていて、飛行は約1400倍ゆっくり描かれています。管の下では、最後の到着がエネルギーに換算されます。飛行距離をドラッグしてみてください。管が長いほど同じエネルギーがより長い時間に広がるので、それぞれをより細かく区別できます。</p>
  <div class="ctl"><label for="tof-l1">飛行距離（m）</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>薄い試料では、くぼみが断面積をなぞります。ビームの中に試料を置きました。6.7 eV付近では試料の原子核に共鳴があり、中性子をつかまえる（閃光）ので、対応する時刻に届く中性子が減ります。グラフは試料があるときとないときの計数を比べたもので、<b>透過率</b>は、すべての中性子が通り抜けたときに1です。</p>
  <p>点はシミュレーションした計数で、ばらつきも含んでいます。実線は検出器が平均して記録する値、破線は断面積そのものの形です。試料が薄いと、くぼみはその形を写し取ります。</p>
  <div class="ctl"><label for="tof-d1">試料の厚さ（μm）</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>厚い試料では、くぼみが飽和します。ピークのエネルギーでは試料の手前側がすべての中性子を捕らえるので、中心は真っ黒になり、どれだけ厚くしても黒いままです。くぼみは、両側に広がることでしか大きくなれません。これが<b>自己遮蔽</b>で、手前の層が奥の層を遮蔽します。そのため厚い試料は、共鳴のピークよりも裾について多くを教えてくれます。</p>
  <div class="ctl"><label for="tof-d2">試料の厚さ（μm）</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>パルスが長く、飛行距離が短いほど、くぼみはぼやけます。くぼみの幅を決める要因は3つあり、すべてグラフの下に書かれています。共鳴そのものの幅、熱で揺れる試料の原子が各衝突のエネルギーを少しずつぼかすこと（<b>ドップラー</b>広がり）、そして時間のぼやけです。パルスが長いか管が短いと、各到着時間が、したがって各エネルギーが不確かになります。</p>
  <p>パルスを長くするか管を短くしてみてください。くぼみは広く浅くなりますが、取り除かれる中性子の割合はほぼ変わりません。</p>
  <div class="ctl"><label for="tof-p1">パルス幅（μs）</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">飛行距離（m）</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITAは逆向きに進みます。このような測定された計数を取り込み、同じ実験（厚さ、熱、時間のぼやけ）に通したときにそれを再現する共鳴はどれかを問います。ここでは、中性子幅Γ<sub>n</sub>（準位がどれだけ強く中性子を保持するか）が真の値の4倍近い推測から出発し（青い曲線）、曲線が点を通るまで少しずつ変えていきます。</p>
  <p>表示には現在の推測値と<b>ミスフィット</b>が出ます。約1なら、曲線は計数のばらつきが許す限り点に近いことを意味します。実験条件を変えるとフィットは新しい計数からやり直され、ほぼ同じ幅に落ち着きます。点とうまく合わせられないときは、ミスフィットがそれを教えてくれます。</p>
  <div class="ctl"><label for="tof-l3">飛行距離（m）</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">試料の厚さ（μm）</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">パルス幅（μs）</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "pulsed source": "パルス中性子源",
  "detector": "検出器",
  "L = {#} m · clock: {#} ms since the pulse": "L = {#} m · 時計：パルスから {#} ms",
  "transmission": "透過率",
  "cross-section shape (scaled)": "断面積の形（スケール調整）",
  "what the detector records": "検出器が記録する値",
  "simulated counts": "シミュレーションの計数",
  "fast neutrons arrive first, slow ones later: the clock sorts them by energy": "速い中性子が先、遅い中性子が後に着く：時計がエネルギー別に分ける",
  "L = {#} m · clock: {#} µs since the pulse": "L = {#} m · 時計：パルスから {#} µs",
  "last arrival: t = {#} µs → E = ({#} × {#} / {#})² = {#} eV": "最後の到着：t = {#} µs → E = ({#} × {#} / {#})² = {#} eV",
  "last arrival: t = {#} ms → E = ({#} × {#} / {#})² = {#} eV": "最後の到着：t = {#} ms → E = ({#} × {#} / {#})² = {#} eV",
  "sample": "試料",
  "L = {#} m · {#} eV arrives after {#} ms": "L = {#} m · {#} eV は {#} ms 後に到着",
  "sample {#} µm · dip {#} % deep": "試料 {#} µm · くぼみの深さ {#} %",
  "sample {#} µm · dip {#} % deep: black in the centre": "試料 {#} µm · くぼみの深さ {#} %：中心は真っ黒",
  "L = {#} m · {#} eV arrives after {#} µs": "L = {#} m · {#} eV は {#} µs 後に到着",
  "width from timing {#} meV · from heat (Doppler) {#} meV · the resonance's own {#} meV": "時間分解能の幅 {#} meV · 熱（ドップラー）{#} meV · 共鳴自身 {#} meV",
  "the fit's current guess": "フィットの現在の推測",
  "fit: Γn = {#} meV (put into the simulation: {#}) · misfit {#}": "フィット：Γn = {#} meV（シミュレーションの入力値：{#}）· ミスフィット {#}",
});
