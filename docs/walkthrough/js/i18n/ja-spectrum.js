/* Japanese: spectrum (高速炉と熱中性子炉) */
WT.L.ch.spectrum = {
  num: "レッスン 4", title: "高速炉と熱中性子炉", short: "高速炉と熱炉",
  html: `
<div class="step">
  <h3>中性子の速さ</h3>
  <p>中性子は約2 MeVの高速で生まれます。軽水炉では、水素と衝突を繰り返して、水の原子そのものと同じくらいの遅さになります。これが<b>熱中性子</b>です。高速炉には減速材がないので、中性子は速いままです。スライダーで両者の間を動かしてみましょう。</p>
  <div class="ctl"><label for="spc-m1">減速の度合い</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>余分な中性子</h3>
  <p><i>η</i>は、燃料の原子核が中性子を1個吸収するごとに返す中性子の数です。1個は連鎖反応を続けるのに使われます。新しい燃料を増殖させるにはもう1個の余裕が必要なので、<i>η</i>は2を十分に上回らなければなりません。プルトニウム239がそれを満たすのは高速中性子の場合だけです。</p>
  <div class="ctl"><label for="spc-m2">減速の度合い</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>残りものを燃やす</h3>
  <p>アメリシウムのような重い残りものは、遅い中性子をほとんど吸収するだけで、より重くなっていきます。高速中性子ははるかに大きな割合を分裂させるので、高速炉ではそれらを燃やすことができます。</p>
  <div class="ctl"><label for="spc-m3">減速の度合い</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>その代償</h3>
  <p>遅い中性子のほうが核分裂を起こす確率がずっと高く、1 MeVでは標的が数百分の1に小さくなります。そのため高速炉の炉心にはずっと濃い燃料が必要で、ウラン235が3〜5 %ではなく、プルトニウムが15〜25 %ほど要ります。</p>
  <div class="ctl"><label for="spc-m4">減速の度合い</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // isotopes
  "U{#}": "U{#}", "Pu{#}": "Pu{#}", "Np{#}": "Np{#}", "Am{#}": "Am{#}", "Cm{#}": "Cm{#}",
  // moderator
  "water reactor: hydrogen slows the neutrons": "軽水炉：水素が中性子を減速させる",
  "water: neutrons slow down": "水：中性子は減速する",
  "fast reactor: sodium barely slows them": "高速炉：ナトリウムはほとんど減速させない",
  "sodium: they stay fast": "ナトリウム：速いまま",
  "partly moderated": "一部減速",
  "no moderator (sodium)": "減速材なし（ナトリウム）",
  "sodium": "ナトリウム",
  "water": "水",
  // spectrum
  "thermal": "熱領域",
  "resonances": "共鳴",
  "slowing down (resonances)": "減速（共鳴）",
  "fast": "高速領域",
  "{#} eV": "{#} eV",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "neutron energy →": "中性子エネルギー →",
  "born ~{#} MeV": "誕生時 約 {#} MeV",
  "born near {#} MeV": "約 {#} MeV で生まれる",
  "most neutrons end up thermal": "大半の中性子は熱中性子になる",
  "most neutrons are slowed all the way to thermal": "大半の中性子は熱中性子まで減速される",
  "most stay between {#} keV and {#} MeV": "大半は {#} keV〜{#} MeV にとどまる",
  "most neutrons stay between {#} keV and {#} MeV": "大半の中性子は {#} keV〜{#} MeV にとどまる",
  "many linger at in-between energies": "多くが中間のエネルギーにとどまる",
  "many neutrons linger at in-between energies": "多くの中性子が中間のエネルギーにとどまる",
  "thermal ≈ {#} eV, ~{#} km/s": "熱 ≈ {#} eV、約 {#} km/s",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "熱中性子：高温の水で kT ≈ {#} eV、約 {#} km/s",
  // eta
  "η = {#}: one to continue, one to breed": "η = {#}：1個は連鎖に、1個は増殖に",
  "average η: U{#} {#} · Pu{#} {#}": "平均 η：U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "このスペクトルで平均：  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  // minor actinides
  "{#} % split": "{#} % が分裂",
  "the rest are captured and grow heavier": "残りは捕獲されて重くなる",
  "the rest are captured: the nucleus just grows heavier": "残りは捕獲され、原子核が重くなるだけ",
  // cross section
  "{#} b": "{#} b",
  "≈ {#} b": "≈ {#} b",
  "Pu{#} fission target": "Pu{#} の核分裂の標的",
  "Pu{#} fission cross section (target size)": "Pu{#} の核分裂断面積（標的の大きさ）",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV：標的は約 {#} 分の1",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "{#} MeV では標的が約 {#} 分の1（{#} eV と比べて）",
  "illustrative shapes": "形は説明用",
});
