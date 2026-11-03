/* Simplified Chinese (简体中文): breeding blanket and first wall (chapter 32) */
WT.L.ch.blanket = {
  num: "第 32 章", title: "增殖包层与第一壁", short: "包层",
  lead: "自然界中几乎没有氚。D–T 电站必须用等离子体产生的中子，从锂中自己增殖氚。",
  html: `
<div class="step">
  <h3>氚增殖比</h3>
  <p>每个中子四处游走，直到被锂俘获并产生一个氚核。每个发亮的点就是一个氚核。</p>
  <div class="ctl"><label for="bk-e">锂-6 份额 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">增殖区厚度 (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>聚变</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>(n,2n) 中子倍增</h3>
  <p>14 MeV 中子撞上铅时，可以再打出一个中子：(n,2n)。与只用锂的情况比较。</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">铅锂</button> <button class="btn ghost" data-act="li" aria-pressed="false">仅锂</button></div>
  <div class="ctl"><label for="bk-e2">锂-6 份额 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>第一壁中的氦和氢</h3>
  <p>第一壁承受全部 14 MeV 中子束。氦和氢按 INCOGNITA 计算的速率在其中积累。</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">钢</button> <button class="btn ghost" data-act="wW" aria-pressed="false">钨</button> <button class="btn ghost" data-act="wV" aria-pressed="false">钒</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">铜</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">壁负载 (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">年数</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">截面：INCOGNITA 数据库 v0.2（<code>library/v0.2/channels_v02.parquet</code>），与<a href="data.html#Fe-56" data-keep-lang>全部核素</a>中的曲线相同。</div>
</div>`,
};
