/* Japanese: feedback (原子炉の安定性とフィードバック) */
WT.L.ch.feedback = {
  num: "レッスン 1", title: "原子炉の安定性とフィードバック", short: "フィードバック",
  html: `
<div class="step">
  <h3>ループ：出力、熱、反応度</h3>
  <p>出力が上がると燃料と水が熱くなり、その温度が反応度<i>ρ</i>を変え、反応度が出力を決めます。反応度をステップ状に加えて、信号がループを一周する様子を見てみましょう。係数が負なら、変化を押し戻します。</p>
  <div class="ctl"><label for="fb-r">反応度ステップ（pcm）</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">挿入</button> <button class="btn ghost" data-act="fbRes">リセット</button></div>
</div>
<div class="step">
  <h3>ドップラー：速いブレーキ</h3>
  <p>燃料が熱くなると、ウラン238が核分裂を起こさずに捕獲する中性子が増えます（<a href="#doppler">ドップラー広がり</a>）。燃料は数秒で熱くなるので、このブレーキが最初に効きます。軽水炉では常に負です。ここではこれが唯一のフィードバックです。</p>
  <div class="ctl"><label for="fb-d">ドップラー係数（pcm/K）</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">挿入</button> <button class="btn ghost" data-act="fbRes">リセット</button></div>
</div>
<div class="step">
  <h3>減速材が加わる</h3>
  <p>温かい水は密度が小さく、中性子をあまりうまく減速できません。通常のホウ素濃度の加圧水型炉では、このため減速材係数も負になります。2つめの、よりゆっくりしたブレーキが働き、出力はより低いところに落ち着きます。</p>
  <div class="ctl"><label for="fb-m">減速材係数（pcm/K）</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">挿入</button> <button class="btn ghost" data-act="fbRes">リセット</button></div>
</div>
<div class="step">
  <h3>フィードバックが正のとき</h3>
  <p>冷却材の項が正で、ドップラーを上回ると、出力が上がるほど反応度が増え、出力は暴走します。軽水炉は係数が負になるように設計されています。低出力時のRBMKのように、正のボイド係数をもちうる設計もありました。</p>
  <div class="ctl"><label for="fb-c">冷却材係数（pcm/K）</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">挿入</button> <button class="btn ghost" data-act="fbRes">リセット</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "+{a} pcm": "+{a} pcm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "Doppler α_D = {a} pcm/K": "ドップラー α_D = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "冷却材 α_C = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "減速材 α_M = {a} pcm/K",
  "inserted ρ_ext = {a}": "挿入した ρ_ext = {a}",
  "P {#} %": "P {#} %",
  "chain": "連鎖",
  "chain reaction": "連鎖反応",
  "heat": "熱",
  "heats water": "水を加熱",
  "fuel +{#} K": "燃料 +{#} K",
  "fuel {#} K": "燃料 {#} K",
  "fuel ΔT +{#} K": "燃料 ΔT +{#} K",
  "fuel ΔT {#} K": "燃料 ΔT {#} K",
  "water +{#} K": "水 +{#} K",
  "water {#} K": "水 {#} K",
  "water ΔT +{#} K": "水 ΔT +{#} K",
  "water ΔT {#} K": "水 ΔT {#} K",
  "illustrative model": "説明用のモデル",
  "last {#} s →": "直近 {#} s →",
  "last {#} seconds →": "直近 {#} 秒 →",
  "power": "出力",
  "power coefficient +{a} pcm per {#} % power: runs away": "出力係数 +{a} pcm（出力 {#} % あたり）：暴走",
  "power coefficient +{a} pcm per {#} %: runs away": "出力係数 +{a} pcm / {#} %：暴走",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "出力係数 {a} pcm（出力 {#} % あたり）：自己安定",
  "power coefficient {a} pcm per {#} %: settles": "出力係数 {a} pcm / {#} %：落ち着く",
  "power ran away · protection would shut it down": "出力が暴走 · 保護系が停止させる",
  "power ran away · in a real plant the protection system would shut it down": "出力が暴走 · 実際のプラントでは保護系が原子炉を停止させる",
  "steady at {#} % · press Insert": "{#} % で一定 · 「挿入」を押す",
  "steady at {#} % power · press Insert to add reactivity": "出力 {#} % で一定 · 「挿入」を押して反応度を加える",
  "αC +": "αC +",
  "αC {#}": "αC {#}",
  "αC −": "αC −",
  "αD −": "αD −",
  "αM +": "αM +",
  "αM {#}": "αM {#}",
  "αM −": "αM −",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
});
