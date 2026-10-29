/* Japanese: landscape (第4章、原子核の地図) */
WT.L.ch.landscape = {
  num: "第4章", title: "原子核の地図", short: "核図表",
  lead: "これまでに人類がつくったすべての原子核を1枚の地図に載せました。現在までに3,338個、永遠に存続するのはそのうち252個だけです。",
  html: `
<div class="step">
  <h3>核図表</h3>
  <p>小さな四角形は、実験で実際に観測された原子核を1つずつ表しています。横軸は中性子数、縦軸は陽子数です。薄い四角形は観測はされたものの質量がまだ測られておらず、推定値しかありません。<b>濃い</b>四角形は決して崩壊しない252個です。残りは崩壊し、オレンジ色は一瞬で、青色は何年もたってから崩壊します。<em style="font-style:normal;color:var(--proton);font-weight:600">赤</em>の行は、スライダーで選んだ元素のすべての既知の同位体です。</p>
  <div class="ctl"><label for="ls-z">元素を見る（陽子数 Z）</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>核図表全体の結合エネルギー</h3>
  <p>今度は各四角形を<b>核子あたりの結合エネルギー</b>、つまり中性子や陽子がどれだけ強く束縛されているか（第3章）で色分けしています。安定な原子核は強い結合の尾根に沿って並びます。そこから離れて中性子や陽子が多すぎると、結合は弱くなります。最も強く結合しているのはニッケル62です。細い線は<b>魔法数</b>（8、20、28、50、82、126）を示しており、この数の原子核は特に強く束縛されています。</p>
</div>
<div class="step">
  <h3>安定へ向かうβ崩壊</h3>
  <p>核子の総数（<b>質量数</b>A）が同じ原子核は、地図上で斜めの線上に並びます。<em style="font-style:normal;color:var(--proton);font-weight:600">赤</em>で示した線です。分裂したウラン原子核の破片のように、中性子が多すぎる状態から出発します。<b>β崩壊</b>では中性子が陽子に変わるので、原子核はその線に沿って、より強く結合した中央へ向かって1つずつ移り、尾根に達して止まるまでこれを繰り返します。小さなグラフは同じ崩壊系列を、原子核が転がり落ちる谷として表しています。A＝137を試してください。この系列は、原子炉事故の長寿命の生成物であるセシウム137を通ります。</p>
  <div class="ctl"><label for="ls-a">質量数 A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>INCOGNITAがカバーする範囲</h3>
  <p>同じ地図を、私たちのライブラリが各原子核について保持している内容で色分けしました。<em style="font-style:normal;color:var(--fission);font-weight:600">緑</em>は、測定された共鳴から評価したものです。それ以外はエンジンだけでつくった模型ファイルで、安定または長寿命のもの（ティアA）は<b>濃色</b>、半減期が1日より長いもの（ティアB）は<em style="font-style:normal;color:var(--accent);font-weight:600">青</em>、それより短いもの（ティアC）は<em style="font-style:normal;color:var(--warm);font-weight:600">オレンジ</em>です。灰色はライブラリにないもの（大部分は最も軽い原子核と、エンジンで計算できない少数の原子核）です。</p>
</div>`,
};
