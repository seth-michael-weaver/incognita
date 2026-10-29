/* Japanese: doppler (第20章、ドップラー広がり) */
WT.L.ch.doppler = {
  num: "第20章", title: "ドップラー広がり", short: "ドップラー",
  html: `
<div class="step">
  <h3>標的の熱運動</h3>
  <p>燃料が熱くなると、原子はより速く揺れ動きます。中性子が到着したとき、ウラン原子はもはや静止していません。</p>
  <div class="ctl"><label for="dop-t1">燃料温度（K）</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>ドップラー広がり</h3>
  <p>曲線は、ウラン238が中性子を捕獲する確率を中性子のエネルギーに対して描いたものです。高さは標的面積で、単位は<b>バーン</b>です（1バーンは10<sup>−24</sup> cm²で、原子核が中性子に対して示すおおよその大きさです）。原子が動いているため、中性子に正面から出会うものもあれば、逃げていくものもあり、狭いピークはぼやけて、低く幅広くなります。面積は変わりません。</p>
  <div class="ctl"><label for="dop-t2">燃料温度（K）</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>共鳴の自己遮蔽</h3>
  <p>燃料ペレットは厚いものです。影をつけた帯は、各エネルギーでペレットが止める中性子の割合です。ピークの中心は高温でも低温でもすでにすべてを止めているので、ピークが低くなってもそこでは何も失われませんが、広がった裾はより多くを捕らえます。より多くの中性子が核分裂を起こさずに捕獲で失われるため、<i>k</i>はひとりでに下がります。（<i>k</i>は、1回の核分裂が新たに何回の核分裂につながるかを表します。第<a href="#critical">21</a>章で説明します。）</p>
  <div class="ctl"><label for="dop-t3">燃料温度（K）</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "uranium atoms in the fuel": "燃料中のウラン原子",
  "{#} K": "{#} K",
  "caught in the peak": "ピークで捕獲",
  "k": "k",
  "neutron energy (eV) →": "中性子エネルギー (eV) →",
  "capture cross section": "捕獲断面積",
  "peak {#}k barns · Doppler width {#} meV · area unchanged": "ピーク {#}k バーン · ドップラー幅 {#} meV · 面積は不変",
  "all stopped": "すべて止まる",
  "wider wings catch more": "広がった裾がより多く捕らえる",
  "share of neutrons stopped in the fuel": "燃料で止まる中性子の割合",
  "the peak's centre already stops everything; the wider wings catch more": "ピーク中心はすでにすべてを止める。広がった裾がより多く捕らえる",
});
