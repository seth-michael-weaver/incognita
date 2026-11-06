/* Chinese: halflife (放射性与半衰期) */
WT.L.ch.halflife = {
  num: "第1课", title: "放射性与半衰期", short: "半衰期",
  lead: "有些原子是不稳定的：它们的原子核迟早会衰变，放出射线，变成别的东西。谁也说不准某一个什么时候衰变，但整块样品却像时钟一样准，准得可以用来对表。",
  html: `
<div class="step">
  <h3>随机衰变的样品</h3>
  <p>每个发光的小球都是一个不稳定的原子核。任何一个都可能在任何时刻衰变，放出一道射线的闪光，然后变成平静、稳定的原子。点一个，让它衰变。</p>
  <div class="btns"><button class="btn" data-act="refill">新样品</button></div>
</div>
<div class="step">
  <h3>减半，再减半</h3>
  <p>谁也说不准下一个是哪一个，但整体却是可以预测的：经过一个<b>半衰期</b>约剩一半，两个半衰期剩四分之一，接着是八分之一。把半衰期调长或调短试试。</p>
  <div class="ctl"><label for="hl-th">半衰期（秒）</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">新样品</button></div>
</div>
<div class="step">
  <h3>原子核没有记忆</h3>
  <p>跟踪一个幸存者。不管它已经存活了多久，它再撑过一个半衰期的概率仍然是二分之一：原子核不会变老。</p>
  <div class="btns"><button class="btn ghost" data-act="tag">换一个跟踪</button><button class="btn ghost" data-act="refill">新样品</button></div>
</div>
<div class="step">
  <h3>真实的半衰期</h3>
  <p>真实同位素的半衰期从几天到几十亿年不等。在这条拉伸过的时间轴上，每种同位素都在自己的半衰期处跌下悬崖。选一种，然后把时间向前拖动。</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">碘-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">铯-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">碳-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">铀-238</button></div>
  <div class="ctl"><label for="hl-t1">经过时间</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>活度：每秒衰变数</h3>
  <p>每种各取一克，并排放置。半衰期短，意味着每秒衰变很多次，但持续不久；半衰期长，则微弱地发光很久很久。拖动时间，看灯一盏接一盏熄灭。</p>
  <div class="ctl"><label for="hl-t2">经过时间</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Cs{#}": "Cs{#}",
  "C{#}": "C{#}",
  "I{#}": "I{#}",
  "U{#}": "U{#}",
  "all": "全部",
  "almost none": "几乎为零",
  "caesium{#}": "铯{#}",
  "carbon{#}": "碳{#}",
  "iodine{#}": "碘{#}",
  "uranium{#}": "铀{#}",
  "caesium{#} · half-life {#} years": "铯{#} · 半衰期 {#} 年",
  "carbon{#} · half-life {#} years": "碳{#} · 半衰期 {#} 年",
  "iodine{#} · half-life {#} days": "碘{#} · 半衰期 {#} 天",
  "uranium{#} · half-life {#} billion years": "铀{#} · 半衰期 {#}×10⁹ 年",
  "chance to last one more: {#} in {#}": "再撑一个半衰期的概率：{#}/{#}",
  "chance to last one more: 1 in 2": "再撑一个半衰期的概率：1/2",
  "drag": "拖动",
  "every survivor has the same {#}-in{#} chance per half-life": "每个幸存者每个半衰期的机会都相同：{#}{#}",
  "every survivor has the same 1-in-2 chance per half-life": "每个幸存者每过一个半衰期，存活机会都是 1/2",
  "fission product": "裂变产物",
  "medicine, fission product": "医学用途、裂变产物",
  "natural uranium": "天然铀",
  "radiocarbon dating": "放射性碳定年",
  "half-lives →": "半衰期数 →",
  "illustrative half-life": "示意性半衰期",
  "it popped: follow another": "它衰变了：换一个跟踪",
  "nuclei left": "剩余原子核",
  "pops per second (log)": "每秒衰变数（对数）",
  "pops per second, {#} gram (each line ×{#})": "每秒衰变数，{#} 克（每条线 ×{#}）",
  "survived {#} half-lives": "已存活 {#} 个半衰期",
  "survived {#} half-lives · still {#} in {#}": "已存活 {#} 个半衰期 · 仍是 {#}/{#}",
  "{#} of {#} still unstable": "{#} / {#} 仍不稳定",
  "{#} of {#} left · half-life {#} s": "剩余 {#} / {#} · 半衰期 {#} s",
  "{#} half-life": "{#} 个半衰期",
  // time spans (fmtT and axis ticks)
  "{#} minutes": "{#} 分钟",
  "{#} hours": "{#} 小时",
  "{#} hour": "{#} 小时",
  "{#} h": "{#} h",
  "{#} days": "{#} 天",
  "{#} day": "{#} 天",
  "{#} d": "{#} 天",
  "{#} months": "{#} 个月",
  "{#} years": "{#} 年",
  "{#} year": "{#} 年",
  "{#} yr": "{#} 年",
  "{#}³ yr": "{#}³ 年",
  "{#}⁶ yr": "{#}⁶ 年",
  "{#}⁹ yr": "{#}⁹ 年",
  "{#} thousand years": "{#} 千年",
  "{#} million years": "{#}×10⁶ 年",
  "{#} billion years": "{#}×10⁹ 年",
  "½ {#} days": "½ {#} 天",
  "½ {#} years": "½ {#} 年",
  "½ {#} billion years": "½ {#}×10⁹ 年",
  "½ {#} bn years": "½ {#}×10⁹ 年",
  "{#} % left after {#} minutes": "剩余 {#} %（{#} 分钟后）",
  "{#} % left after {#} hours": "剩余 {#} %（{#} 小时后）",
  "{#} % left after {#} days": "剩余 {#} %（{#} 天后）",
  "{#} % left after {#} months": "剩余 {#} %（{#} 个月后）",
  "{#} % left after {#} years": "剩余 {#} %（{#} 年后）",
  "{#} % left after {#} thousand years": "剩余 {#} %（{#} 千年后）",
  "{#} % left after {#} million years": "剩余 {#} %（{#}×10⁶ 年后）",
  "{#} % left after {#} billion years": "剩余 {#} %（{#}×10⁹ 年后）",
  "under {#} % left after {#} minutes": "剩余不到 {#} %（{#} 分钟后）",
  "under {#} % left after {#} hours": "剩余不到 {#} %（{#} 小时后）",
  "under {#} % left after {#} days": "剩余不到 {#} %（{#} 天后）",
  "under {#} % left after {#} months": "剩余不到 {#} %（{#} 个月后）",
  "under {#} % left after {#} years": "剩余不到 {#} %（{#} 年后）",
  "under {#} % left after {#} thousand years": "剩余不到 {#} %（{#} 千年后）",
  "under {#} % left after {#} million years": "剩余不到 {#} %（{#}×10⁶ 年后）",
  "under {#} % left after {#} billion years": "剩余不到 {#} %（{#}×10⁹ 年后）",
  "one gram of each, after {#} minutes": "各一克，{#} 分钟后",
  "one gram of each, after {#} hours": "各一克，{#} 小时后",
  "one gram of each, after {#} days": "各一克，{#} 天后",
  "one gram of each, after {#} months": "各一克，{#} 个月后",
  "one gram of each, after {#} years": "各一克，{#} 年后",
  "one gram of each, after {#} thousand years": "各一克，{#} 千年后",
  "one gram of each, after {#} million years": "各一克，{#}×10⁶ 年后",
  "one gram of each, after {#} billion years": "各一克，{#}×10⁹ 年后",
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
