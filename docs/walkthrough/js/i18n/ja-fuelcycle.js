/* Japanese: fuelcycle (核燃料サイクル) */
WT.L.ch.fuelcycle = {
  num: "レッスン 1", title: "核燃料サイクル", short: "燃料サイクル",
  html: `
<div class="step">
  <h3>ウランを掘り出す</h3>
  <p>鉱石の大部分は岩石で、含まれるウランのうちウラン235、つまり核分裂しやすい種類は0.7 %にすぎません。</p>
  <div class="ctl"><label for="fc-g">鉱石品位（ウラン %）</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>濃縮は物質収支</h3>
  <p>ウランは気体の形で、ウラン235に富む小さな流れ（燃料）と、劣化した大きな流れ（テイルズ）に分けられます。</p>
  <div class="ctl"><label for="fc-p">燃料の濃縮度（% U-235）</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">テイルズ（% U-235）</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>ペレット、燃料棒、集合体</h3>
  <p>濃縮ウランはセラミックのペレットに焼き固められ、燃料棒に封入され、集合体に束ねられます。<a href="#reactor">次のレッスン</a>でそれらを炉心まで追います。</p>
  <div class="ctl"><label for="fc-f">燃料（ウラン トン）</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>炉心での年月</h3>
  <p>3〜6年のあいだに重い原子の数パーセントが分裂し、核分裂生成物と少しの新しいプルトニウムが残ります（<a href="#burnup">燃焼度</a>）。</p>
  <div class="ctl"><label for="fc-b">燃焼度（GWd/トン）</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>冷却、そして二つの道</h3>
  <p>使用済み燃料はプールで、その後乾式キャスクで冷やされます。その後はそのまま地下深くに埋めるか、再処理してウランとプルトニウムを再び使います（<a href="#waste">使用済み燃料</a>、<a href="#breeding">増殖</a>）。</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">ワンススルー</button> <button class="btn ghost" data-act="frR" aria-pressed="false">再処理</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Convert": "転換",
  "Disposal": "処分",
  "End": "最後",
  "Enrich": "濃縮",
  "Fabricate": "加工",
  "Mill": "製錬",
  "Mine": "採掘",
  "Pool · cask": "プール · キャスク",
  "Reactor": "原子炉",
  "Store": "貯蔵",
  "about what a {#} MWe reactor loads in a year": "{#} MWe の原子炉が1年に装荷する量ほど",
  "assemblies": "集合体",
  "assemblies of {#} rods": "燃料棒 {#} 本の集合体",
  "at least {#} years": "少なくとも {#} 年",
  "cask": "キャスク",
  "decades": "数十年",
  "decades in air": "空気中で数十年",
  "deep repository, {#}–{#} m down": "地層処分場、地下 {#}–{#} m",
  "dry cask": "乾式キャスク",
  "enrich": "濃縮",
  "enrichment plant (UF₆ gas)": "濃縮工場（UF₆ ガス）",
  "fission products": "核分裂生成物",
  "illustration": "イメージ図",
  "minor actinides": "マイナーアクチノイド",
  "most mines: above {#} %": "多くの鉱山：{#} % 以上",
  "of electricity from this tonne": "この1トンから得る電力",
  "once-through: the whole tonne is disposed of": "ワンススルー：1トンすべてを処分",
  "one tonne of fuel: each square is {#} kg": "燃料1トン：1マスが {#} kg",
  "one tonne: each square {#} kg": "1トン：1マス {#} kg",
  "pellets": "ペレット",
  "pellets, {#} cm tall": "ペレット、高さ {#} cm",
  "plutonium": "プルトニウム",
  "pool": "プール",
  "recycle": "リサイクル",
  "repository": "処分場",
  "repository {#}–{#} m deep": "処分場 深さ {#}–{#} m",
  "reprocess": "再処理",
  "richest, Canada: up to {#} %": "最も豊富なカナダ：最大 {#} %",
  "rods, about {#} m long": "燃料棒、長さ約 {#} m",
  "rods, {#} m": "燃料棒、{#} m",
  "the rest: uranium{#}": "残り：ウラン{#}",
  "the whole tonne": "1トンすべて",
  "typical discharge {#}–{#}": "典型的な取出し {#}–{#}",
  "uranium{#}": "ウラン{#}",
  "uranium{#} (and {#})": "ウラン{#}（と {#}）",
  "{#} U atoms": "U 原子 {#} 個",
  "{#} are U{#}": "うち {#} 個が U{#}",
  "{#} are uranium{#}": "うち {#} 個がウラン{#}",
  "{#} t used": "使用済み {#} t",
  "{#} t used fuel": "使用済み燃料 {#} t",
  "{#} uranium atoms": "ウラン原子 {#} 個",
  "≈ a big reactor's yearly reload": "≈ 大型炉の年間取替量",
  "≥ {#} years": "≥ {#} 年",
  "{a} t ore": "鉱石 {a} t",
  "{a} t U₃O₈": "U₃O₈ {a} t",
  "{a} t UF₆": "UF₆ {a} t",
  "{#} t fuel + {a} t tails": "燃料 {#} t + テイルズ {a} t",
  "{a} t UO₂": "UO₂ {a} t",
  "pool ≥ {#} years": "プール ≥ {#} 年",
  "ore ≈ {a} t · block = {#} t": "鉱石 ≈ {a} t · 1ブロック = {#} t",
  "ore for one tonne of fuel: ≈ {a} t  (each block {#} t)": "燃料1トン分の鉱石：≈ {a} t（1ブロック {#} t）",
  "{a} of one block": "1ブロックの {a}",
  "{a} % U": "{a} % U",
  "grade {a} % U": "品位 {a} % U",
  "natural U {a} kg": "天然U {a} kg",
  "natural uranium {a} kg": "天然ウラン {a} kg",
  "{a} % U{#}": "{a} % U{#}",
  "fuel {#} kg": "燃料 {#} kg",
  "tails {a} kg": "テイルズ {a} kg",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "供給/燃料 = (xp − xt)/(xf − xt) = {a}",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "天然 / 燃料 = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "≈ {a} SWU of separative work per kg of fuel": "燃料1 kgあたり分離作業量 ≈ {a} SWU",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "分離作業量 ≈ 燃料1 kgあたり {a} SWU · テイルズを下げると：ウランは減り、作業は増える",
  "{a} t uranium = {b} t UO₂": "ウラン {a} t = UO₂ {b} t",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "濃縮ウラン {a} t、二酸化ウラン（UO₂）セラミック {b} t として",
  "{a} % of the heavy atoms split": "重い原子の {a} % が分裂",
  "{a} GWd/t": "{a} GWd/t",
  "≈ {a} GWh of electricity": "≈ {a} GWh の電力",
  "reprocessing": "再処理",
  "uranium {a} t": "ウラン {a} t",
  "plutonium {a} kg": "プルトニウム {a} kg",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t の MOX 燃料",
  "fission products + minor actinides {a} kg → ≈ {#} t glass": "核分裂生成物 + マイナーアクチノイド {a} kg → ≈ {#} t のガラス",
  "U {a} t → re-enrich": "U {a} t → 再濃縮",
  "Pu {a} kg → MOX": "Pu {a} kg → MOX",
  "{a} kg waste → glass": "廃棄物 {a} kg → ガラス",
  "fission prod.": "核分裂生成物",
  "minor act.": "MA",
});
