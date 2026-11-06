/* Japanese: kinetics (原子炉動特性：6群と逆時間方程式) */
WT.L.ch.kinetics = {
  num: "レッスン 1", title: "原子炉動特性：6群と逆時間方程式", short: "動特性",
  html: `
<div class="step">
  <h3>遅れて出る中性子の6つの群</h3>
  <p>遅発中性子は、およそ6つの群に分けられる核分裂生成物（先行核）から出てきます。半減期は0.23 sから56 sまでです（Keepin、ウラン235）。放出の大部分は2 s群と22 s群が担い、待機中の在庫の大部分は長寿命の群が抱えています。平均の遅れはΣ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 sです。核分裂を止めて、各群がそれぞれの速さで減っていく様子を見てみましょう。</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">核分裂を止める</button></div>
</div>
<div class="step">
  <h3>逆時間方程式</h3>
  <p>6群の一点炉動特性方程式に<i>n</i> ∝ e<sup><i>ωt</i></sup>を代入すると、<i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>)が得られます。−<i>λ</i><sub>i</sub>にある極で分けられた7本の枝です。<i>ρ</i>のステップは各枝と1回ずつ交わります。最も右の根が安定炉周期<i>T</i> = 1/<i>ω</i><sub>1</sub>を与え、残りの6つは消えていきます。</p>
  <div class="ctl"><label for="ki-r1">反応度 ρ（$）</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>即発跳躍と即発臨界</h3>
  <p>反応度をステップ状に加えると、出力はまず数ミリ秒のうちに<i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>)だけ跳ね上がり、その後は安定炉周期で上昇します。<i>ρ</i> = 1 $では即発中性子だけで臨界となり、炉周期はΛ/(<i>ρ</i> − <i>β</i>)に向かって急激に短くなります。</p>
  <div class="ctl"><label for="ki-r2">反応度 ρ（$）</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>スクラムの後</h3>
  <p>大きな負の反応度を入れると、出力はすぐに約<i>β</i>/(<i>β</i> − <i>ρ</i>)まで落ち、その後は最も長寿命の群の崩壊より速くは下がれません。スクラムがどれほど深くても、炉周期は−1/<i>λ</i><sub>1</sub> ≈ −80 sに近づきます。</p>
  <div class="ctl"><label for="ki-r3">反応度 ρ（$）</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Keepin six-group data": "Keepin の6群データ",
  "Stop fissions": "核分裂を止める",
  "Restart fissions": "核分裂を再開",
  "delayed neutrons out": "放出される遅発中性子",
  "drag the rods in": "制御棒をドラッグして挿入",
  "drag the rods out": "制御棒をドラッグして引き抜く",
  "drag ρ": "ρ をドラッグ",
  "half-life · share emitted": "半減期 · 放出の割合",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "平均の遅れ Σ aᵢ/λᵢ = {#} s · β = {#}（U{#}）",
  "power": "出力",
  "power ×{#} speed": "出力（{#} 倍速）",
  "prompt critical": "即発臨界",
  "prompt critical · period {#} ms (Λ = {#} µs)": "即発臨界 · 炉周期 {#} ms（Λ = {#} µs）",
  "prompt critical · period {#} s (Λ = {#} µs)": "即発臨界 · 炉周期 {#} s（Λ = {#} µs）",
  "prompt critical · period {#} min (Λ = {#} µs)": "即発臨界 · 炉周期 {#} 分（Λ = {#} µs）",
  "prompt critical · period {#} h (Λ = {#} µs)": "即発臨界 · 炉周期 {#} h（Λ = {#} µs）",
  "prompt drop to {#}": "即発降下：{#} まで",
  "prompt jump β/(β−ρ) = {#}": "即発跳躍 β/(β−ρ) = {#}",
  "prompt root": "即発根",
  "prompt root ≈ −(β−ρ)/Λ": "即発根 ≈ −(β−ρ)/Λ",
  "slope e^(−t / {#} s): the {#} s group": "傾き e^(−t / {#} s)：{#} s 群",
  "slope e^(−t/{#} s)": "傾き e^(−t/{#} s)",
  "stable period T = {#}/ω₁ = {#} ms": "安定炉周期 T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "安定炉周期 T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "安定炉周期 T = {#}/ω₁ = {#} 分",
  "stable period T = {#}/ω₁ = {#} h": "安定炉周期 T = {#}/ω₁ = {#} h",
  "ρ = {#}: power stays flat": "ρ = {#}：出力は一定のまま",
  "waiting stock": "待機中の在庫",
  "{#} s": "{#} s",
  "{#} ms": "{#} ms",
  "{#} min": "{#} 分",
  "{#} h": "{#} 時間",
  "{#} s after stopping · delayed emission {#} % of the start": "停止後 {#} s · 遅発中性子の放出は初めの {#} %",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · 安定炉周期 {#} 分",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · 安定炉周期 {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · 安定炉周期 {#} s",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · 安定炉周期 {#} h",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · 安定炉周期 {#} s（極限 {#} s）",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · 安定炉周期 {#} 分（極限 {#} s）",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · 安定炉周期 {#} ms（極限 {#} s）",
  "ω ({#}/s), axis stretched (asinh)": "ω（{#}/s）、軸は引き伸ばし（asinh）",
  "ω ({#}/s), stretched": "ω（{#}/s）、引き伸ばし",
});
