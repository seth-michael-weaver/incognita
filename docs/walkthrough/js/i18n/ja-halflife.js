/* Japanese: halflife (放射能と半減期) */
WT.L.ch.halflife = {
  num: "レッスン 1", title: "放射能と半減期", short: "半減期",
  lead: "不安定な原子もあります。その原子核は遅かれ早かれ崩壊し、放射線を出して別のものに変わります。1個がいつ崩壊するかは誰にも言えませんが、試料全体は時計を合わせられるほど正確な規則に従います。",
  html: `
<div class="step">
  <h3>でたらめに崩壊する試料</h3>
  <p>光る球の1つ1つが不安定な原子核です。どれもいつ崩壊してもおかしくなく、崩壊すると放射線の閃光を出して、落ち着いた安定な原子になります。1つタップして崩壊させてみましょう。</p>
  <div class="btns"><button class="btn" data-act="refill">新しい試料</button></div>
</div>
<div class="step">
  <h3>半分、さらにその半分</h3>
  <p>次にどれが崩壊するかは誰にもわかりませんが、集団としてはふるまいを予測できます。<b>半減期</b>が1回たつと約半分が残り、2回で4分の1、3回で8分の1になります。半減期を長くしたり短くしたりしてみましょう。</p>
  <div class="ctl"><label for="hl-th">半減期（秒）</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">新しい試料</button></div>
</div>
<div class="step">
  <h3>原子核は記憶をもたない</h3>
  <p>生き残った1個を追いかけます。それまでどれだけ長く残っていても、さらに半減期1回分を生き延びる確率はやはり2分の1です。原子核は年をとらないのです。</p>
  <div class="btns"><button class="btn ghost" data-act="tag">別の1個を追う</button><button class="btn ghost" data-act="refill">新しい試料</button></div>
</div>
<div class="step">
  <h3>実際の半減期</h3>
  <p>実際の同位体の半減期は、数日から数十億年にまでわたります。引き伸ばしたこの時間軸の上で、どの同位体も自分の半減期のところで崖のように落ちます。1つ選んで、時間を先へドラッグしてみましょう。</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">ヨウ素131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">セシウム137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">炭素14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">ウラン238</button></div>
  <div class="ctl"><label for="hl-t1">経過時間</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>放射能：1秒あたりの崩壊数</h3>
  <p>それぞれ1グラムずつを並べました。半減期が短いと毎秒たくさん崩壊しますが、長続きしません。半減期が長いと、かすかな光が非常に長く続きます。時間をドラッグして、ランプが1つずつ消えていくのを見てみましょう。</p>
  <div class="ctl"><label for="hl-t2">経過時間</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Cs{#}": "Cs{#}",
  "C{#}": "C{#}",
  "I{#}": "I{#}",
  "U{#}": "U{#}",
  "all": "全部",
  "almost none": "ほぼゼロ",
  "caesium{#}": "セシウム{#}",
  "carbon{#}": "炭素{#}",
  "iodine{#}": "ヨウ素{#}",
  "uranium{#}": "ウラン{#}",
  "caesium{#} · half-life {#} years": "セシウム{#} · 半減期 {#} 年",
  "carbon{#} · half-life {#} years": "炭素{#} · 半減期 {#} 年",
  "iodine{#} · half-life {#} days": "ヨウ素{#} · 半減期 {#} 日",
  "uranium{#} · half-life {#} billion years": "ウラン{#} · 半減期 {#} 十億年",
  "chance to last one more: {#} in {#}": "あと半減期1回もつ確率：{#}/{#}",
  "drag": "ドラッグ",
  "every survivor has the same {#}-in{#} chance per half-life": "生き残りはどれも、半減期ごとに同じ確率 {#}{#}",
  "every survivor has the same 1-in-2 chance per half-life": "生き残りはどれも、半減期ごとに同じ 2 分の 1 の確率",
  "fission product": "核分裂生成物",
  "medicine, fission product": "医療、核分裂生成物",
  "natural uranium": "天然ウラン",
  "radiocarbon dating": "放射性炭素年代測定",
  "half-lives →": "半減期 →",
  "illustrative half-life": "説明用の半減期",
  "it popped: follow another": "崩壊した：別の1個を追う",
  "nuclei left": "残った原子核",
  "pops per second (log)": "毎秒の崩壊数（対数）",
  "pops per second, {#} gram (each line ×{#})": "毎秒の崩壊数、{#} グラム（線ごとに ×{#}）",
  "survived {#} half-lives": "半減期 {#} 回分を生存",
  "survived {#} half-lives · still {#} in {#}": "半減期 {#} 回分を生存 · それでも {#}/{#}",
  "{#} of {#} still unstable": "{#} / {#} 個がまだ不安定",
  "{#} of {#} left · half-life {#} s": "残り {#} / {#} 個 · 半減期 {#} s",
  "{#} half-life": "半減期 {#} 回",
  // time spans (fmtT and axis ticks)
  "{#} minutes": "{#} 分",
  "{#} hours": "{#} 時間",
  "{#} hour": "{#} 時間",
  "{#} h": "{#} 時間",
  "{#} days": "{#} 日",
  "{#} day": "{#} 日",
  "{#} d": "{#} 日",
  "{#} months": "{#} か月",
  "{#} years": "{#} 年",
  "{#} year": "{#} 年",
  "{#} yr": "{#} 年",
  "{#}³ yr": "{#}³ 年",
  "{#}⁶ yr": "{#}⁶ 年",
  "{#}⁹ yr": "{#}⁹ 年",
  "{#} thousand years": "{#} 千年",
  "{#} million years": "{#} 百万年",
  "{#} billion years": "{#} 十億年",
  "½ {#} days": "½ {#} 日",
  "½ {#} years": "½ {#} 年",
  "½ {#} billion years": "½ {#} 十億年",
  "½ {#} bn years": "½ {#} 十億年",
  "{#} % left after {#} minutes": "{#} % が残存（{#} 分後）",
  "{#} % left after {#} hours": "{#} % が残存（{#} 時間後）",
  "{#} % left after {#} days": "{#} % が残存（{#} 日後）",
  "{#} % left after {#} months": "{#} % が残存（{#} か月後）",
  "{#} % left after {#} years": "{#} % が残存（{#} 年後）",
  "{#} % left after {#} thousand years": "{#} % が残存（{#} 千年後）",
  "{#} % left after {#} million years": "{#} % が残存（{#} 百万年後）",
  "{#} % left after {#} billion years": "{#} % が残存（{#} 十億年後）",
  "under {#} % left after {#} minutes": "{#} % 未満が残存（{#} 分後）",
  "under {#} % left after {#} hours": "{#} % 未満が残存（{#} 時間後）",
  "under {#} % left after {#} days": "{#} % 未満が残存（{#} 日後）",
  "under {#} % left after {#} months": "{#} % 未満が残存（{#} か月後）",
  "under {#} % left after {#} years": "{#} % 未満が残存（{#} 年後）",
  "under {#} % left after {#} thousand years": "{#} % 未満が残存（{#} 千年後）",
  "under {#} % left after {#} million years": "{#} % 未満が残存（{#} 百万年後）",
  "under {#} % left after {#} billion years": "{#} % 未満が残存（{#} 十億年後）",
  "one gram of each, after {#} minutes": "それぞれ1グラム、{#} 分後",
  "one gram of each, after {#} hours": "それぞれ1グラム、{#} 時間後",
  "one gram of each, after {#} days": "それぞれ1グラム、{#} 日後",
  "one gram of each, after {#} months": "それぞれ1グラム、{#} か月後",
  "one gram of each, after {#} years": "それぞれ1グラム、{#} 年後",
  "one gram of each, after {#} thousand years": "それぞれ1グラム、{#} 千年後",
  "one gram of each, after {#} million years": "それぞれ1グラム、{#} 百万年後",
  "one gram of each, after {#} billion years": "それぞれ1グラム、{#} 十億年後",
  // activity per gram
  "{#} /s": "{#} /s",
  "~{#} /s": "~{#} /s",
  "{#}×{#}¹ /s": "{#}×{#}¹ /s",
  "{#}×{#}² /s": "{#}×{#}² /s",
  "{#}×{#}³ /s": "{#}×{#}³ /s",
  "{#}×{#}⁴ /s": "{#}×{#}⁴ /s",
  "{#}×{#}⁵ /s": "{#}×{#}⁵ /s",
  "{#}×{#}⁶ /s": "{#}×{#}⁶ /s",
  "{#}×{#}⁷ /s": "{#}×{#}⁷ /s",
  "{#}×{#}⁸ /s": "{#}×{#}⁸ /s",
  "{#}×{#}⁹ /s": "{#}×{#}⁹ /s",
  "{#}×{#}¹⁰ /s": "{#}×{#}¹⁰ /s",
  "{#}×{#}¹¹ /s": "{#}×{#}¹¹ /s",
  "{#}×{#}¹² /s": "{#}×{#}¹² /s",
  "{#}×{#}¹³ /s": "{#}×{#}¹³ /s",
  "{#}×{#}¹⁴ /s": "{#}×{#}¹⁴ /s",
  "{#}×{#}¹⁵ /s": "{#}×{#}¹⁵ /s",
  "{#}×{#}¹⁶ /s": "{#}×{#}¹⁶ /s",
});
