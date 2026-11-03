/* Japanese: gamow (第30章、ガモフピークと点火) */
WT.L.ch.gamow = {
  num: "第30章", title: "ガモフピークと点火", short: "ガモフピーク",
  lead: "熱いプラズマは、狭いエネルギーの窓を通して燃えます。トンネルできるほど速く、しかも効いてくるほど数が多いエネルギーです。",
  html: `
<div class="step">
  <h3>ガモフピーク</h3>
  <p>速い原子核は少なく、速いものほどトンネルしやすくなります。その積が光ります。これがガモフピークです。温度の線をドラッグしてみましょう。</p>
  <div class="ctl"><label for="gw-t">温度 kT（keV）</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · 幅 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>燃料の反応率</h3>
  <p>窓の中を足し合わせると、反応率 ⟨σv⟩ が得られます。装置で到達できるどの温度でも、D–T が圧倒的に勝ちます。</p>
  <div class="ctl"><label for="gw-t2">温度 kT（keV）</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>ローソン条件と点火</h3>
  <p>プラズマをある温度と閉じ込めの位置までドラッグして、放してみましょう。いちばん上の曲線より上なら、自分で高温を保ちます。</p>
  <div class="btns"><button class="btn" data-act="lowgo">弱い装置を試す</button> <button class="btn ghost" data-act="higo">強い装置を試す</button></div>
  <div class="formula">点火：n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
