/* Japanese: blanket (第32章、増殖ブランケットと第一壁) */
WT.L.ch.blanket = {
  num: "第32章", title: "増殖ブランケットと第一壁", short: "ブランケット",
  lead: "トリチウムは自然界にほとんど存在しません。D–T 発電所は、プラズマがつくる中性子を使い、リチウムから自分でトリチウムを増殖しなければなりません。",
  html: `
<div class="step">
  <h3>トリチウム増殖比</h3>
  <p>中性子はさまよい続け、やがてリチウムに捕まって三重陽子を1個つくります。光る点の1つ1つが三重陽子1個です。</p>
  <div class="ctl"><label for="bk-e">リチウム6の割合（%）</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">増殖材の厚さ（cm）</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>核融合</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>(n,2n) による中性子増倍</h3>
  <p>14 MeV の中性子が鉛に当たると、2個目の中性子をたたき出すことがあります。これが (n,2n) です。リチウムだけの場合と比べてみましょう。</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">鉛–リチウム</button> <button class="btn ghost" data-act="li" aria-pressed="false">リチウムのみ</button></div>
  <div class="ctl"><label for="bk-e2">リチウム6の割合（%）</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>第一壁の中のヘリウムと水素</h3>
  <p>第一壁は 14 MeV のビームをまともに受けます。その内部にヘリウムと水素がたまっていきます。たまる速さは INCOGNITA が計算した値です。</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">鋼</button> <button class="btn ghost" data-act="wW" aria-pressed="false">タングステン</button> <button class="btn ghost" data-act="wV" aria-pressed="false">バナジウム</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">銅</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">壁負荷（MW/m²）</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">年数</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">断面積：INCOGNITA のライブラリ v0.2（<code>library/v0.2/channels_v02.parquet</code>）。<a href="data.html#Fe-56" data-keep-lang>全核種</a>と同じ曲線です。</div>
</div>`,
};
