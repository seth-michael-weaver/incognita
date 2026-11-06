/* Japanese: sandbox (原子炉をつくる) */
WT.L.ch.sandbox = {
  num: "レッスン 1", title: "原子炉をつくる", short: "原子炉をつくる", lead: "燃料、減速材、冷却材、大きさを選び、連鎖反応が自ら続くかどうかを確かめます。教科書的な簡略モデルです。",
  html: `
<div class="step">
  <h3>四つの因子</h3>
  <p>中性子が漏れなければ、吸収された1個の中性子から<i>k</i><sub>∞</sub> = <i>η f p ε</i>個の新しい中性子が生まれます。この天然ウランの黒鉛パイルはぎりぎり達しています。</p>
</div>
<div class="step">
  <h3>減速材を選ぶ</h3>
  <p>天然ウランでは、重水か黒鉛でなければ<i>k</i><sub>∞</sub>は1を超えません。軽水は中性子をよく減速しますが、吸収しすぎます。</p>
  <div class="btns" role="group" aria-label="減速材"><button class="btn ghost" data-act="mo_h2o">軽水</button> <button class="btn ghost" data-act="mo_d2o">重水</button> <button class="btn ghost" data-act="mo_c">黒鉛</button></div>
  <div class="ctl"><label for="sb-m1">燃料あたりの減速材</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>燃料を濃縮する</h3>
  <p>ウラン235が数パーセントあれば普通の水が使えます。今日の原子炉の多くがそうしているのはそのためです。</p>
  <div class="btns" role="group" aria-label="燃料"><button class="btn ghost" data-act="fu_nat">天然U</button> <button class="btn ghost" data-act="fu_leu">濃縮U</button> <button class="btn ghost" data-act="fu_mox">MOX（Pu）</button> <button class="btn ghost" data-act="fu_th">トリウム + U-233</button></div>
  <div class="ctl"><label for="sb-e1">核分裂性物質の割合（%）</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>大きさと漏れ</h3>
  <p>中性子は表面から逃げるので、<i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)。この天然ウラン黒鉛パイルの縁を破線の円までドラッグしてください。</p>
  <div class="ctl"><label for="sb-r1">炉心半径（m）</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>冷却材が沸騰すると</h3>
  <p>水で冷やす黒鉛炉心では、沸騰すると<i>k</i>が上がります。水は減速するより多く吸収していたからです。チェルノブイリのRBMKの欠陥です。ほかの冷却材も試してください。</p>
  <div class="btns" role="group" aria-label="冷却材"><button class="btn ghost" data-act="co_h2o">水</button> <button class="btn ghost" data-act="co_gas">CO₂ / ヘリウム</button> <button class="btn ghost" data-act="co_na">ナトリウム</button></div>
</div>
<div class="step">
  <h3>自分でつくる</h3>
  <p>何でもありです。高速炉には減速材がなく、ずっと多くの核分裂性燃料が必要です。</p>
  <div class="btns" role="group" aria-label="燃料"><button class="btn ghost" data-act="fu_nat">天然U</button> <button class="btn ghost" data-act="fu_leu">濃縮U</button> <button class="btn ghost" data-act="fu_mox">MOX（Pu）</button> <button class="btn ghost" data-act="fu_th">トリウム + U-233</button></div>
  <div class="ctl"><label for="sb-e2">核分裂性物質の割合（%）</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="減速材"><button class="btn ghost" data-act="mo_none">減速材なし</button> <button class="btn ghost" data-act="mo_h2o">軽水</button> <button class="btn ghost" data-act="mo_d2o">重水</button> <button class="btn ghost" data-act="mo_c">黒鉛</button></div>
  <div class="ctl"><label for="sb-m2">燃料あたりの減速材</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="冷却材"><button class="btn ghost" data-act="co_h2o">水</button> <button class="btn ghost" data-act="co_d2o">重水</button> <button class="btn ghost" data-act="co_gas">CO₂ / ヘリウム</button> <button class="btn ghost" data-act="co_na">ナトリウム</button> <button class="btn ghost" data-act="co_pb">鉛</button> <button class="btn ghost" data-act="co_salt">溶融塩</button></div>
  <div class="ctl"><label for="sb-r2">炉心半径（m）</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "CO₂ / helium gas coolant": "CO₂ / ヘリウムガス冷却材",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX、{#} % プルトニウム{#}",
  "R {#} m": "R {#} m",
  "absorbed in fuel": "燃料に吸収",
  "can never sustain a chain, at any size": "どの大きさでも連鎖を維持できない",
  "caught by fuel": "燃料に捕獲",
  "coolant boils away: k ↑": "冷却材が沸騰して失われる：k ↑",
  "coolant boils: k ↑": "冷却材が沸騰：k ↑",
  "coolant boils: k ≈": "冷却材が沸騰：k ≈",
  "coolant lost: k barely changes": "冷却材喪失：k はほぼ変わらない",
  "coolant lost: k ↑": "冷却材喪失：k ↑",
  "critical size": "臨界寸法",
  "escape capture": "捕獲を逃れる",
  "f": "f",
  "fast fission": "高速核分裂",
  "fission": "核分裂",
  "fuel": "燃料",
  "fuel heats up: k ↓ (Doppler)": "燃料が熱くなる：k ↓（ドップラー）",
  "fuel hotter: k ↓": "燃料が高温：k ↓",
  "graphite moderator": "黒鉛減速材",
  "graphite moderator · CO₂ / helium gas coolant": "黒鉛減速材 · CO₂ / ヘリウムガス冷却材",
  "graphite moderator · water coolant": "黒鉛減速材 · 水冷却材",
  "k": "k",
  "k∞": "k∞",
  "leak": "漏れ",
  "leak out": "漏れ出る",
  "light water moderator": "軽水減速材",
  "light water moderator · water coolant": "軽水減速材 · 水冷却材",
  "mod./cool.": "減速/冷却",
  "moderator, coolant": "減速材、冷却材",
  "natural U": "天然U",
  "natural uranium ({#} % U{#})": "天然ウラン（{#} % U{#}）",
  "never critical": "臨界にならない",
  "no chain, any size": "どの大きさでも連鎖なし",
  "no leakage": "漏れなし",
  "no moderator: a fast reactor · sodium coolant": "減速材なし：高速炉 · ナトリウム冷却材",
  "no moderator: fast": "減速材なし：高速炉",
  "no size is big enough": "どんな大きさでも足りない",
  "p": "p",
  "per fuel absorption": "燃料吸収あたり",
  "radius {#} m": "半径 {#} m",
  "radius {#} m · drag the edge": "半径 {#} m · 縁をドラッグ",
  "simplified model": "簡略化したモデル",
  "simplified one-group model · illustration": "簡略化した1群モデル · イメージ図",
  "stays in": "とどまる",
  "stays in (M² {#} cm²)": "とどまる（M² {#} cm²）",
  "sustains a chain, {#} % to spare (ρ)": "連鎖を維持、余裕 {#} %（ρ）",
  "sustains: +{#} % spare": "維持：余裕 +{#} %",
  "too small: critical at radius {#} m": "小さすぎる：半径 {#} m で臨界",
  "too small: needs {#} m": "小さすぎる：{#} m 必要",
  "uranium, {#} % U{#}": "ウラン、{#} % U{#}",
  "water boils: k ↑": "水が沸騰：k ↑",
  "water boils: k ↓": "水が沸騰：k ↓",
  "water coolant": "水冷却材",
  "water heats or boils: k ↑": "水の昇温・沸騰：k ↑",
  "water heats or boils: k ↓": "水の昇温・沸騰：k ↓",
  "where the neutrons go": "中性子の行き先",
  "{#} % U{#}": "{#} % U{#}",
  "enriched U": "濃縮U",
  "light water": "軽水",
  "heavy water": "重水",
  "lead": "鉛",
  "molten salt": "溶融塩",
  "sodium": "ナトリウム",
  "coolant": "冷却材",
  "= η f, if nothing leaked": "= η f（漏れがなければ）",
  "= η f p ε, if nothing leaked": "= η f p ε（漏れがなければ）",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "とどまる：{#} / ({#} + M²B²)、M² = {#} cm²",
  "neutrons per absorption in fuel": "燃料での吸収1回あたりの中性子",
  "share absorbed in fuel": "燃料に吸収される割合",
  "no slowing down, no resonance loss": "減速なし、共鳴での損失なし",
  "escape capture while slowing": "減速中に捕獲を逃れる",
  "fast fission counted in η": "高速核分裂は η に含む",
  "bonus from fast fission": "高速核分裂による上乗せ",
  "thorium, {#} % U{#}": "トリウム、{#} % U{#}",
  "Th + {#} % U{#}": "Th + {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "ウラン、{#} % U{#}（高濃縮）",
  "critical at {#} m": "{#} m で臨界",
  "coolant heats: k ↑": "冷却材が昇温：k ↑",
  "coolant heats: k ↓": "冷却材が昇温：k ↓",
  "coolant boils away: k ↓": "冷却材が沸騰して失われる：k ↓",
  "coolant lost: k ↓": "冷却材喪失：k ↓",
  "heavy water coolant": "重水冷却材",
  "sodium coolant": "ナトリウム冷却材",
  "lead coolant": "鉛冷却材",
  "molten salt coolant": "溶融塩冷却材",
  "heavy water moderator": "重水減速材",
  "heavy water moderator · heavy water coolant": "重水減速材 · 重水冷却材",
  "heavy water moderator · water coolant": "重水減速材 · 水冷却材",
  "graphite moderator · sodium coolant": "黒鉛減速材 · ナトリウム冷却材",
  "no moderator: a fast reactor · lead coolant": "減速材なし：高速炉 · 鉛冷却材",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "減速材なし：高速炉 · CO₂ / ヘリウムガス冷却材",
  "no moderator: a fast reactor · molten salt coolant": "減速材なし：高速炉 · 溶融塩冷却材",
  "water moderates": "水が減速する",
  "heavy water moderates": "重水が減速する",
  "no moderator, but the water moderates": "減速材なし、ただし水が減速する",
  "no moderator, but the heavy water moderates": "減速材なし、ただし重水が減速する",
});
