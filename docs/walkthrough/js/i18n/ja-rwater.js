/* Japanese: rwater (水冷却炉) */
WT.L.ch.rwater = {
  num: "レッスン 1", title: "水冷却炉", short: "水冷却炉",
  lead: "現在の発電用原子炉は、ほとんどが水で冷やされています。違いは、水がどのように熱を運び出すかです。",
  html: `
<div class="step">
  <h3>加圧水型（PWR）</h3>
  <p>高い圧力をかけた水が熱を蒸気発生器へ運び、2つ目のループで蒸気をつくります。</p>
</div>
<div class="step">
  <h3>沸騰水型（BWR）</h3>
  <p>水が炉心の中で沸騰し、その蒸気がそのままタービンへ向かいます。ループは1つだけです。</p>
</div>
<div class="step">
  <h3>重水炉（CANDU）</h3>
  <p>重水は中性子をあまり吸収せずに減速させるので、天然ウランのままで足ります。</p>
</div>
<div class="step">
  <h3>黒鉛と沸騰水（RBMK）</h3>
  <p>黒鉛が中性子を減速させ、水は何百本もの別々の管の中で沸騰します。</p>
</div>
<div class="step">
  <h3>小型モジュール炉（SMR）</h3>
  <p>すべてを1つの容器に収めた小さなPWRで、工場でつくります。</p>
</div>
<div class="step">
  <h3>超臨界圧水（SCWR）</h3>
  <p>221 barを超えると水は沸騰しなくなります。そのためより高温で運転でき、熱をより多く電気に変えられます。</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "BWR": "BWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU、カナダ、インド、ルーマニア、アルゼンチン",
  "Generation IV design, not yet built": "第4世代の設計、まだ建設されていない",
  "NuScale (US), Linglong One (China)": "NuScale（米国）、玲龍1号（中国）",
  "PHWR": "PHWR",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "原子炉の約{#} %、米国・日本・スウェーデン",
  "about {#} in {#} of the world's reactors": "世界の原子炉の約{#}/{#}",
  "all in one vessel": "すべて1つの容器に",
  "boiling water in tubes": "管の中で沸騰する水",
  "boils in the core": "炉心で沸騰",
  "calandria: cool heavy water": "カランドリア：低温の重水",
  "calandria: cool heavy water slows the neutrons": "カランドリア：低温の重水が中性子を減速",
  "condenser": "復水器",
  "control rods from below": "制御棒は下から挿入",
  "coolant out": "冷却材出口",
  "core": "炉心",
  "core, pump-free loop and steam generator in one vessel": "炉心、ポンプなしの循環、蒸気発生器を1つの容器に",
  "electricity": "発電効率",
  "gen.": "発電機",
  "generator": "発電機",
  "graphite": "黒鉛",
  "graphite blocks slow the neutrons": "黒鉛ブロックが中性子を減速",
  "horizontal pressure tubes, refuelled while running": "水平の圧力管、運転中に燃料交換",
  "illustration": "イメージ図",
  "outlet": "出口",
  "pressure": "圧力",
  "pressure tubes": "圧力管",
  "reactor vessel": "原子炉容器",
  "rods from below": "制御棒は下から",
  "steam gen.": "蒸気発生器",
  "steam generator": "蒸気発生器",
  "the Chernobyl type; a few still run in Russia": "チェルノブイリと同型、ロシアで数基が運転中",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "熱中性子 · 減速材：黒鉛 · 冷却材：沸騰水",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "熱中性子 · 減速材：重水 · 冷却材：重水",
  "thermal neutrons · moderator: light water · coolant: boiling water": "熱中性子 · 減速材：軽水 · 冷却材：沸騰水",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "熱中性子 · 減速材：軽水 · 冷却材：超臨界圧水",
  "thermal neutrons · moderator: light water · coolant: water": "熱中性子 · 減速材：軽水 · 冷却材：水",
  "thermal · mod.: graphite · cool.: boiling water": "熱 · 減速：黒鉛 · 冷却：沸騰水",
  "thermal · mod.: heavy water · cool.: heavy water": "熱 · 減速：重水 · 冷却：重水",
  "thermal · mod.: light water · cool.: boiling water": "熱 · 減速：軽水 · 冷却：沸騰水",
  "thermal · mod.: light water · cool.: supercritical water": "熱 · 減速：軽水 · 冷却：超臨界圧水",
  "thermal · mod.: light water · cool.: water": "熱 · 減速：軽水 · 冷却：水",
  "turbine": "タービン",
  "vessel": "容器",
  "water boils in the core": "水が炉心で沸騰する",
  "water boils in ~{#} pressure tubes": "約{#}本の圧力管の中で水が沸騰",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar：沸点より高温でも単一の流体",
  "{#} bar: never boils": "{#} bar：沸騰しない",
  "{#} °C": "{#} °C",
});
