/* Japanese: averages (第27章、共鳴から平均へ) */
WT.L.ch.averages = {
  num: "第27章", title: "共鳴から平均へ", short: "共鳴から平均へ",
  lead: "第15章では共鳴列を描きました。ここではそれを断面積として示します。R行列の式、パラメータの背後にある統計、温度の効果、そして多数の共鳴にわたる平均がどのようにハウザー・フェッシュバッハになるかです。",
  html: `
<div class="step">
  <h3>R行列、準位ごとに</h3>
  <p>重い原子核では、数keV以下で複合核の準位が1つずつ現れ、断面積は準位パラメータ、すなわちエネルギー<i>E</i><sub>λ</sub>、換算中性子幅、捕獲幅によって厳密に書かれます。評価では<b>R行列</b>理論を、多くの場合<b>Reich–Moore</b>の形で使います。これは中性子チャネルでの準位間の干渉を保ち、多数の捕獲チャネルを1つの吸収幅として扱います。</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">一準位Breit–Wigner</button></div>
  <p>上の線が全断面積、下の線が捕獲で、スピン0の標的（ウラン238に似たもの）でのs波準位からなる1つの共鳴列についてのものです。準位の間では、共鳴の振幅とポテンシャルの振幅が打ち消し合うところで、全断面積がポテンシャル散乱を下回ります。一準位の形は、振幅ではなく各準位の断面積を足し合わせます。ピークでは近いのですが谷では誤りで、そこでは多数の準位の裾が積み重なり、全断面積が負になることさえあります。</p>
</div>
<div class="step">
  <h3>パラメータの背後にある統計</h3>
  <p>測定のない原子核には共鳴列はなく、平均値だけがあります。<i>D</i>₀、強度関数<i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀、そして⟨Γ<sub>γ</sub>⟩です。残りはランダム行列理論が与えます。同じスピンとパリティの準位の間隔はウィグナー分布に従い、換算中性子幅はポーター・トーマス分布、つまり自由度1のχ²分布に従います。</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = 間隔/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">共鳴列をさらに10個引く</button></div>
  <p>ヒストグラムは、これまでに引いたすべての共鳴列の間隔と幅を集めたもので、曲線は2つの法則です。捕獲幅は数百の光子チャネルにわたる和なのでほとんどゆらがず、固定値として扱います。</p>
</div>
<div class="step">
  <h3>熱がピークをぼかす</h3>
  <p>標的の原子核は動いています。エネルギー<i>E</i>の中性子は、幅Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>)で広がった相対エネルギーで原子核と出会い、各共鳴はその広がりを通して見えます。これが<b>ドップラー広がり</b>です。1つの準位の場合、結果はψ関数、すなわちローレンツ型とガウス型の畳み込みになります。</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">温度（K）</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>拡大した共鳴は、共鳴列の最も低いいくつかのうちで最も強いものです。破線は0 Kでの形です。熱はピークを下げて裾を広げ、捕獲ピークの下の面積は変わりません。厚い試料では、これは中立ではありません。ピークは自己遮蔽されますが裾はされないので、熱い燃料ほど多く捕獲します。これが原子炉のドップラー・フィードバックです。</p>
</div>
<div class="step">
  <h3>平均はハウザー・フェッシュバッハ</h3>
  <p>多数の共鳴で平均すると、捕獲はエネルギーのなめらかな関数になります。窓が共鳴列の上を滑り、その平均が順にプロットされていきます。なめらかな線は、透過係数<i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i>と<i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>によるハウザー・フェッシュバッハの値です。</p>
  <div class="ctl"><label for="av-w">窓の幅（準位数）</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">別の共鳴列</button></div>
  <p>狭い窓は大きくばらつきます。共鳴が少なく、その幅がポーター・トーマス分布に従うからです。広い窓は下の線、すなわち幅ゆらぎ補正を含む線に落ち着きます。上の線、つまり平均の積は、ここでは25〜47パーセント高すぎます。その差は⟨Γ<sub>n</sub>⟩が⟨Γ<sub>γ</sub>⟩の1〜3倍になるところ、約100 eVから1 keVで最大になります（p波やもっと多くのチャネルが開いていれば、補正は小さくなります）。ポーター・トーマス分布の幅をもつ1つの中性子チャネルと固定した捕獲幅に対しては、補正後の値は厳密で、(2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩です。</p>
</div>
<div class="step">
  <h3>分離、非分離、なめらか</h3>
  <p>測定で何が分離できるかはエネルギー分解能で決まり、分解能はエネルギーが上がるほど悪くなります。線は装置から見た断面積で、飛行時間法と同じく<i>E</i><sup>3/2</sup>のように大きくなる分解能で広げられています。低エネルギーでは各準位が孤立していて、そのパラメータを当てはめられます。これが分離共鳴領域です。それより上では準位が融合してゆらぐ帯になり、統計はわかっていても個々のピークはわかりません。これが非分離共鳴領域で、平均パラメータと、自己遮蔽についてはサンプリングした共鳴列からつくる確率テーブルによって記述されます。さらにその上では、ハウザー・フェッシュバッハと光学模型が引き継ぎます。</p>
  <div class="ctl"><label for="av-r">装置の分解能（相対値）</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>INCOGNITAのライブラリには、まだ分離共鳴領域がありません。その曲線は、最低エネルギーまでハウザー・フェッシュバッハの平均です。測定された共鳴が分離されているところでは、<a href="data.html" data-keep-lang>全核種</a>のページがその曲線を平均値として示しています。共鳴パラメータと、それからつくるドップラー広がりを含む点ごとの断面積は、開発中です。</p>
  <div class="aside">コードでは：<code>physics/resonance/ladder.py</code>（ランダム行列の間隔、ポーター・トーマス分布の幅、一準位の断面積、アンサンブル）、<code>ladder_statistics.py</code>（測定された共鳴列で法則を検証）、<code>compound/wfc.py</code>（平均が収束する先の幅ゆらぎ補正）。図のReich–Moore、ψ–χ、分解能の式はここで計算しており、ウラン238に似た説明用のパラメータを使っています。ハウザー・フェッシュバッハのエンジン、したがってライブラリは、共鳴領域の断面積をまだ計算しません。</div>
</div>`,
};
(function () {
  const L = {
    // axes
    "{#} eV": "{#} eV", "{#} keV": "{#} keV", "{#} b": "{#} b", "{#}k b": "{#}k b",
    // scene 1: Reich-Moore vs SLBW
    "potential scattering {#}πR′² ≈ {#} b": "ポテンシャル散乱 {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "Reich–Moore（破線：一準位）",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "一準位Breit–Wigner（破線：Reich–Moore）",
    "total": "全断面積", "capture": "捕獲",
    // scene 2: statistics
    "spacings: Wigner": "間隔：ウィグナー分布",
    "s = spacing / D₀": "s = 間隔 / D₀",
    "reduced neutron widths: Porter–Thomas": "換算中性子幅：ポーター・トーマス分布",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "共鳴列{#}個 · 間隔{#}個",
    "s = {#}": "s = {#}",
    // scene 3: Doppler
    "capture near the {#} eV resonance": "{#} eV共鳴付近の捕獲",
    "area {#} b·eV ({#} K: {#})": "面積 {#} b·eV（{#} K：{#}）",
    "target nuclei at {#} K": "{#} Kの標的原子核",
    "target nuclei at rest": "静止した標的原子核",
    // scene 4: window averages
    "Hauser–Feshbach, no correction": "ハウザー・フェッシュバッハ、補正なし",
    "with width fluctuations": "幅ゆらぎあり",
    "average capture cross section": "平均捕獲断面積",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "準位{#}個（{#} eV付近）：{#} b · HF 補正なし {#} b、補正あり {#} b",
    // scene 5: regions
    "resolved": "分離", "unresolved": "非分離", "averaged": "平均化",
    "Γ = {#} meV · Δ = {#} meV": "Γ = {#} meV · Δ = {#} meV",
    "{#} levels around {#} eV: {#} b": "準位{#}個（{#} eV付近）：{#} b",
    "HF {#} b without, {#} b with the correction": "HF 補正なし {#} b、補正あり {#} b",
    "capture as measured, finite resolution": "有限の分解能で測定した捕獲",
    "dashed: Hauser–Feshbach with fluctuations": "破線：幅ゆらぎを含むハウザー・フェッシュバッハ",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "有限の分解能で測定した捕獲 · 破線：幅ゆらぎを含むハウザー・フェッシュバッハ",
    "resolution reaches D₀/{#} at {#} eV": "分解能が D₀/{#} に達する：{#} eV",
    "resolution reaches D₀/{#} at {#} keV": "分解能が D₀/{#} に達する：{#} keV",
    "time of flight: the arrival time measures the energy": "飛行時間：到着時刻がエネルギーを測る",
  };
  // decade ticks "10⁻¹ b" ... "10⁴ b"
  for (const s of ["⁻¹", "¹", "²", "³", "⁴"]) L[`{#}${s} b`] = `{#}${s} b`;
  // labels that carry cross sections printed as "12 b" or "3.4k b" (each value independently)
  const B = ["{#} b", "{#}k b"];
  for (const a of B) for (const b of B) {
    L[`{#} eV · total ${a} · capture ${b}`] = `{#} eV · 全断面積 ${a} · 捕獲 ${b}`;
    L[`peak ${a} ({#} K: ${b})`] = `ピーク ${a}（{#} K：${b}）`;
    L[`Γ = {#} meV · Δ = {#} meV · peak ${a} ({#} K: ${b})`] = `Γ = {#} meV · Δ = {#} meV · ピーク ${a}（{#} K：${b}）`;
  }
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "R行列理論", aliases: ["R行列"],
    short: "共鳴反応を、チャネル半径の内側での準位エネルギーと換算幅によって厳密に記述し、外側の自由波に接続する理論です。",
    more: "評価では、測定された共鳴にそのパラメータを当てはめます。一準位・多準位のBreit–Wigner形式やReich–Moore形式は、完全な理論の近似です。",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore"],
    short: "重い原子核のほとんどの評価で使われるR行列の近似です。中性子チャネルは厳密に扱い、多数の光子チャネルは準位ごとに1つの吸収幅として扱います。",
    chapter: "averages",
  },
  doppler: {
    term: "ドップラー広がり", aliases: ["ドップラー広がり"],
    short: "標的原子核の熱運動によって共鳴がぼやけることです。ピークは下がり裾は広がりますが、孤立したピークの面積は変わりません。",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "分離共鳴領域と非分離共鳴領域", aliases: ["非分離共鳴領域", "分離共鳴領域"],
    short: "あるエネルギーより下では各共鳴が個別に測定され（分離）、それより上では平均パラメータしかわかりません（非分離）。やがて平均はなめらかになります。",
    more: "非分離共鳴領域では、自己遮蔽を確率テーブル、すなわちサンプリングした共鳴列からつくった断面積の分布で扱います。",
    chapter: "averages",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="bw" data-act="rm" */
