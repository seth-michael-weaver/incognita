/* Japanese: transport (中性子輸送とモンテカルロ法) */
WT.L.ch.transport = {
  num: "レッスン 1", title: "中性子輸送とモンテカルロ法", short: "モンテカルロ",
  html: `
<div class="step">
  <h3>輸送方程式</h3>
  <p>厳密には、中性子は角度中性子束<i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>)についてのボルツマン方程式に従います：<b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′。モンテカルロ法は、中性子を1個ずつ追いかけてこれを解きます。距離<i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>だけ飛び、そこで散乱するか、捕獲されるか、核分裂を起こします。</p>
  <div class="btns"><button class="btn" data-act="trnew">新しい中性子</button></div>
</div>
<div class="step">
  <h3>拡散理論が破綻するところ</h3>
  <p>拡散理論は、中性子束がどの方向にもほぼ同じだと仮定しています。この仮定は、表面から平均自由行程の1、2倍以内や、強い吸収体の中では成り立ちません。一様な線源のある平板で、吸収を大きくしながらモンテカルロ法の中性子束と比べてみましょう。</p>
  <div class="ctl"><label for="tr-pa">吸収 Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>べき乗法</h3>
  <p><i>k</i><sub>eff</sub>を求めるには、各世代の核分裂位置を次の世代の線源にします。<i>k</i>は、出発した中性子1個あたりに記録された核分裂位置の数です。すべての中性子を一方の端に置くという悪い初期推定から始めて、線源が基本モードへ広がっていく様子を見てみましょう。</p>
  <div class="btns"><button class="btn" data-act="trbad">悪い初期推定から再開</button></div>
</div>
<div class="step">
  <h3>線源は収束したか？</h3>
  <p>区間に分けた線源のシャノンエントロピー<i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub>は、線源が落ち着くと横ばいになります。世代の平均をとるのはそれからです。<i>k</i>の誤差幅は、数えたヒストリー数<i>N</i>に対して1/√<i>N</i>で小さくなります。</p>
  <div class="ctl"><label for="tr-n">世代あたりのヒストリー数</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Monte Carlo": "モンテカルロ",
  "amber glow: where collisions pile up": "琥珀色の光：衝突が集中する場所",
  "capture": "捕獲",
  "chance to fly at least s:  e^(−Σₜ s)": "少なくとも s 飛ぶ確率：  e^(−Σₜ s)",
  "diffusion": "拡散",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "拡散とモンテカルロの差：表面で +{#} %、中央で +{#} %",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "拡散とモンテカルロの差：表面で +{#} %、中央で {#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "拡散とモンテカルロの差：表面で {#} %、中央で +{#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "拡散とモンテカルロの差：表面で {#} %、中央で {#} %",
  "fission": "核分裂",
  "fission source · dashed: fundamental mode": "核分裂線源 · 破線：基本モード",
  "flux": "中性子束",
  "generation {#}": "第 {#} 世代",
  "generation {#}: k = {#} · H = {#} bits": "第 {#} 世代：k = {#} · H = {#} ビット",
  "glow: collision density": "光：衝突密度",
  "illustrative one-group data": "説明用の1群データ",
  "inactive  |  active generations": "非アクティブ  |  アクティブ世代",
  "inactive | active": "非アクティブ | アクティブ",
  "infinite medium S/Σₐ": "無限媒質 S/Σₐ",
  "k per generation": "世代ごとの k",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#}（{#} × {#} ヒストリー）· 拡散 {#}",
  "leak": "漏れ",
  "scatter": "散乱",
  "source entropy H (bits)": "線源エントロピー H（ビット）",
  "source · dashed: fundamental mode": "線源 · 破線：基本モード",
  "starting…": "開始中…",
  "tap the slab to drop the whole source there": "平板をタップすると線源全体をそこに置く",
  "tap the slab to start neutrons": "平板をタップして中性子を出す",
  "tap: drop the source there": "タップ：そこに線源を置く",
  "vacuum": "真空",
  "{#} free paths": "{#} 平均自由行程",
  "{#} generations, averaging starts after {#}": "{#} 世代、平均は {#} 世代の後から",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} 平均自由行程",
});
