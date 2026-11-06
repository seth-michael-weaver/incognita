/* Japanese: afterheat (停止後の熱) */
WT.L.ch.afterheat = {
  num: "レッスン 1", title: "停止後の熱", short: "崩壊熱",
  html: `
<div class="step">
  <h3>連鎖が止まる</h3>
  <p>制御棒を落とすと、原子の分裂は1分ほどで止まります。それでも燃料は光り続けます。それまでの分裂で残った破片は放射性で、その崩壊がまだ熱を出しているからです。</p>
  <div class="btns"><button class="btn" data-act="ahDrop">制御棒を落とす</button> <button class="btn ghost" data-act="ahUp">再起動</button></div>
</div>
<div class="step">
  <h3>ゆっくりと弱まる</h3>
  <p>停止直後、この熱は全出力の約6〜7 %です。1時間後には約1 %、1日後には約0.5 %、1週間後には0.25 %になります。割合は小さくても、もとの数字がとても大きいのです。</p>
  <div class="ctl"><label for="ah-t">停止後の経過時間</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>水を流し続ける</h3>
  <p>そのため、炉心は停止後も冷やされます。ポンプが燃料のそばに水を流し続け、熱を運び去ります。ポンプを止めると、熱の行き場がなくなって温度が上がっていきます。</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">ポンプ</button></div>
</div>
<div class="step">
  <h3>ポンプなしで冷やす</h3>
  <p>熱い水は上がり、冷たい水は下がります。炉心より高い位置にあるプールまでループを通せば、ポンプがまったくなくても水は流れ続けます。いくつかの新しい設計は、これに数日間頼ります。</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">ポンプ</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">受動ループ</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "cooler": "冷却器",
  "heat exchanger": "熱交換器",
  "core temperature": "炉心温度",
  "temperature": "温度",
  "decaying fragments": "崩壊する破片",
  "splitting atoms": "原子の分裂",
  "heat from decaying fragments": "崩壊する破片からの熱",
  "heat from splitting atoms": "原子の分裂からの熱",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "{#} MW の炉心では {a} MW、電気ケトル {b} 台分",
  "{#} MW core: {a} MW, like {b} kettles": "{#} MW 炉心：{a} MW、ケトル {b} 台分",
  "heat, as a share of full power": "熱（全出力に対する割合）",
  "heat, share of full power": "熱（全出力比）",
  "illustration": "イメージ図",
  "normal": "通常",
  "too hot": "高温すぎ",
  "pool, up high": "高所のプール",
  "water pool, placed higher": "高い位置に置いた水プール",
  "pump off": "ポンプ停止",
  "pump on": "ポンプ運転",
  "pump running": "ポンプ運転中",
  "pump stopped": "ポンプ停止中",
  "pumps carry the heat away": "ポンプが熱を運び去る",
  "steady": "安定",
  "steady, with no pumps": "ポンプなしで安定",
  "steady: natural circulation carries the heat away": "安定：自然循環が熱を運び去る",
  "steady: the pumps carry the heat away": "安定：ポンプが熱を運び去る",
  "temperature climbing": "温度上昇中",
  "temperature climbing: the heat has nowhere to go": "温度上昇中：熱の行き場がない",
  "too hot: cooling must be restored": "高温すぎ：冷却の回復が必要",
  "too hot: the water would start to boil away; cooling must be restored": "高温すぎ：水が沸騰して失われ始める。冷却の回復が必要",
  "boiling": "沸騰",
  "the water starts to boil": "水が沸騰し始める",
  "the splitting dies away in about a minute": "分裂は約1分で消える",
  "the splitting dies away within about a minute": "分裂は約1分以内に消える",
  "the decay heat stays and fades slowly": "崩壊熱は残り、ゆっくり弱まる",
  "the decay heat stays, and fades only slowly": "崩壊熱は残り、ごくゆっくりとしか弱まらない",
  "full power": "全出力",
  "running at full power": "全出力で運転中",
  "total heat: {a} % of full power": "全体の熱：全出力の {a} %",
  "{a} after shutdown · heat {b} % of full power": "停止から {a} · 熱は全出力の {b} %",
  "{a} after shutdown: {b} % of full power": "停止から {a}：全出力の {b} %",
  "{a} after the rods dropped": "制御棒の落下から {a}",
  "{#} min": "{#} 分",
  "{#} hour": "{#} 時間",
  "{#} day": "{#} 日",
  "{#} week": "{#} 週間",
  "{#} year": "{#} 年",
  "{a} s": "{a} s",
  "{a} min": "{a} 分",
  "{a} hours": "{a} 時間",
  "{a} days": "{a} 日",
  "{a} months": "{a} か月",
});
