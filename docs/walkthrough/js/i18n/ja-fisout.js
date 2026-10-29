/* Japanese: fisout (第14章、核分裂中性子) */
WT.L.ch.fisout = {
  num: "第14章", title: "核分裂中性子", short: "核分裂中性子",
  html: `
<div class="step">
  <p>1回の核分裂で2、3個の中性子が放出され、平均では2.4個です。上の図は1回ずつの核分裂を示しています。ウラン原子核が2つの破片に引き裂かれ、青い球が飛び出します。これが<b>即発</b>中性子で、100万分の1秒よりはるかに短い時間で放出されます。</p>
  <p>左のグラフは、0個、1個、2個、3個…の中性子を放出した核分裂の回数を数えたものです。棒はあなたが起こした核分裂、各棒の上の細い線は測定された割合です。回数を増やすと、棒は線に近づいていきます。</p>
  <div class="btns"><button class="btn" data-act="f100">核分裂100回</button><button class="btn ghost" data-act="f1000">核分裂1000回</button></div>
</div>
<div class="step">
  <p>生まれたときは速く、平均で約2 MeVです。これは室温の原子炉内の遅い中性子の約8000万倍のエネルギーです。右のグラフは、即発中性子をエネルギー別に並べたものです。線は測定された形（ワットスペクトル）で、1 MeV付近の山と、10 MeVまで伸びる長い裾をもちます。</p>
  <p>これほど速い中性子は、ウラン235で次の核分裂をほとんど起こしません。そのため原子炉はまず中性子を減速させます。これは後の章で見ます。</p>
  <div class="btns"><button class="btn" data-act="f100">核分裂100回</button><button class="btn ghost" data-act="f1000">核分裂1000回</button></div>
</div>
<div class="step">
  <p>一部は数秒遅れて出てきます。全中性子の0.65 %です。破片の中には中性子が非常に過剰なものがあり、のちに崩壊したとき、新しくできた原子核が中性子を1個保持できずに手放します。それは崩壊を待つため、多くは数秒後になります。</p>
  <p>下の線は核分裂後の時計で、0.01秒から100秒までを表し、目盛りは1つごとに10倍遅くなります。左の球は、すべての即発中性子が一度に出たものです。小さな点は遅発中性子1個ずつで、待ち時間のあいだ線に沿って進み（時計は20倍に速めています）、最終的に放出された位置に止まります。この少数の遅れた中性子が原子炉を制御可能にしています。連鎖反応の応答を1000分の1秒の単位から秒の単位へと遅くするからです。</p>
  <div class="btns"><button class="btn" data-act="f1000">核分裂1000回</button><button class="btn ghost" data-act="clear">クリア</button></div>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "n + U{#} → two fragments + neutrons": "n + U{#} → 2つの破片 + 中性子",
  "prompt neutrons per fission": "核分裂あたりの即発中性子数",
  "lines: measured shares": "線：測定された割合",
  "mean {#}": "平均 {#}",
  "prompt-neutron energy (MeV)": "即発中性子のエネルギー (MeV)",
  "mean {#} MeV": "平均 {#} MeV",
  "line: measured shape": "線：測定された形",
  "prompt": "即発",
  "time after fission · clock sped up {#}×": "核分裂後の時間 · 時計は {#} 倍速",
  "delayed {#} of {#} ({#} %)": "遅発 {#} / {#}（{#} %）",
  "{#} fissions": "核分裂 {#} 回",
});
