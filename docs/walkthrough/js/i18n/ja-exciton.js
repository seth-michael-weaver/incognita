/* Japanese: exciton (第26章、数値で見るエキシトン模型) */
WT.L.ch.exciton = {
  num: "第26章", title: "数値で見るエキシトン模型", short: "エキシトン模型",
  lead: "第7章では、1つの速い中性子が数回衝突するのを追いました。ここでは、各段階で次に起こるのがさらなる衝突か脱出かを決める速度と、それらが足し合わさってできるスペクトルを示します。",
  html: `
<div class="step">
  <h3>粒子・空孔状態を数える</h3>
  <p>エキシトン模型は、平衡へ向かう途中の原子核を、励起された粒子の数<i>p</i>と空孔の数<i>h</i>（<i>n</i> = <i>p</i> + <i>h</i>）で分類します。標的に入った中性子は<i>p</i> = 1、<i>h</i> = 0から始まり、衝突のたびに対が1つ増えます。各段階で重要なのは、<i>n</i>個のエキシトンの間でエネルギーを分け合う仕方が何通りあるか、すなわち粒子・空孔状態密度です。</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">粒子 p（空孔 p − 1）</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">パウリ補正</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹は、フェルミエネルギー付近の1粒子準位の密度です。<i>A<sub>p,h</sub></i>は<b>パウリ</b>補正です。2つの粒子は同じ準位を共有できないので、最も低い配置にはエネルギーが必要になり、しきい値付近の密度が下がります。曲線は粒子と空孔の数で名づけています。3p2hは粒子3個、空孔2個の意味です。スケッチは、選んだ<i>p</i>の配置を1つずつ、ランダムに描いています。空孔とは、フェルミ準位より下から核子が1個欠けた状態です。</p>
</div>
<div class="step">
  <h3>遷移速度と放出速度</h3>
  <p>各段階からは、2つのことが起こりえます。1つは衝突が新たな対をつくることで、その速度λ<sup>+</sup>はフェルミの黄金律により、行列要素の2乗と到達できる状態の密度の積です。もう1つは粒子が出ていくことで、その速度<i>W</i>は詳細つり合いにより、逆過程の断面積と、出ていく粒子がある場合とない場合の状態密度の比から与えられます。</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">中性子エネルギー（MeV）</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>各段階は粒子と空孔の数で表します（2p1hは粒子2個、空孔1個）。棒は各段階での2つの速度で、対数目盛です。λ<sup>+</sup>は10²² s⁻¹の桁で、<i>W</i>は最初の段階でその約10分の1、段階ごとに減っていきます。新しい対ができるたびに、先頭の粒子が運べるエネルギーが薄まるからです。エンジンはM²をKoning–Duijvestijnの形からとり、これはエキシトンあたりのエネルギーとともに減少します。</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>時間の中の連鎖</h3>
  <p>対を取り除くまれな衝突を無視すると（never-come-back近似）、集団は単純な連鎖に従います。各段階は前の段階から満たされ、次の段階と連続領域へと空になっていきます。棒はそのマスター方程式を解いたもので、時間の単位は10⁻²² sです。</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">中性子エネルギー（MeV）</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>連鎖全体は数×10⁻²² sで終わります。途中で逃げ出す割合が前平衡放出で、残りは、エンジンではTALYSと同じく最大6個の粒子を経たのち、複合核に引き渡されます。時間積分によって各段階に強さτ(<i>n</i>)·<i>P</i>(<i>n</i>)が与えられ、エンジンが計算するのはこの積です。</p>
</div>
<div class="step">
  <h3>高エネルギーの裾</h3>
  <p>放出スペクトルは、集団×寿命×放出速度を段階について足し合わせ、残った分の蒸発を加えたものです。2つの粒子と1つの空孔からなる段階<i>n</i> = 3だけが最も高い出射エネルギーまで届き、そのスペクトルは端点に向かって直線的にしか減りません。後の段階ほど柔らかくなります。</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + 蒸発</div>
  <div class="ctl"><label for="ex-e3">中性子エネルギー（MeV）</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>エネルギーを上げると、スペクトルは硬くなります。前平衡の裾は端点まで伸び、蒸発のこぶは1〜2 MeVにとどまります。約10 MeVより上では、測定された高エネルギー中性子はこの裾がなければ再現できません。</p>
</div>
<div class="step">
  <h3>前平衡の割合</h3>
  <p>放出のうち前平衡の割合は入射エネルギーとともに増え、ここでは5 MeV付近の数パーセントから、40 MeVでの約40パーセントまでになります。それは調整可能な定数1つ、すなわち行列要素の全体の大きさに依存します。相互作用が弱いほど平衡化は遅く、早い段階の放出が増えます。</p>
  <div class="ctl"><label for="ex-c">行列要素の定数 C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>破線はエンジンの既定であるC₁ = 1で、実線はスライダーに従います。C₁を半分にすると、割合は2倍ではなく1.5〜1.9倍になります。各段階の脱出確率はW/λ<sup>+</sup>ではなくW/(λ<sup>+</sup> + W)であり、後の段階まで生き残る原子核も減るからです。</p>
</div>
<div class="step">
  <h3>2成分、そして2度目の脱出</h3>
  <p>エンジンは陽子と中性子を別々に追います（<i>p</i><sub>π</sub>、<i>h</i><sub>π</sub>、<i>p</i><sub>ν</sub>、<i>h</i><sub>ν</sub>）。同種の対と異種の対で異なる行列要素を使い、表面付近の最初の衝突では井戸の深さを小さくし、クラスターにはカルバッハの規則を用います。20 MeVより上では、まだエキシトンを保持している残留核が、平衡化する前に2つ目の速い粒子を放出することも許します。</p>
  <div class="ctl"><label for="ex-e4">中性子エネルギー（MeV）</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>曲線はそれを単純化した模型です。3エキシトン段階からの最初の放出の後、残留核に残った粒子が次の衝突の前に逃げ出す確率を示します。20 MeV以下では小さく、それより上で増えます。エンジンが多重前平衡放出をオンにするのはそこからです。</p>
  <div class="aside">コードでは：<code>density/particle_hole.py</code>（Williamsの密度、パウリ補正と有限井戸補正、1成分と2成分）、<code>preeq/exciton.py</code>（行列要素、放出速度と遷移速度、寿命、never-come-backの解）、<code>preeq/complex.py</code>（カルバッハのピックアップ、ストリッピング、ノックアウト）、<code>preeq/multi.py</code>（多重前平衡放出、既定で20 MeVから）。図は1成分で、逆過程の断面積を模式的に扱い、鉄56に似た標的について描いています。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: state densities
  "E (MeV)": "E (MeV)",
  "ω(p, h, E) per MeV": "ω(p, h, E)（/MeV）",
  "{#}p{#}h": "{#}p{#}h",
  "dashed: no Pauli correction": "破線：パウリ補正なし",
  "Fermi level": "フェルミ準位",
  "{#} particles, {#} holes": "粒子{#}個、空孔{#}個",
  // scene 2: rates
  "rate (s⁻¹)": "速度（s⁻¹）",
  "n = {#}": "n = {#}",
  "W/λ⁺ = {#}": "W/λ⁺ = {#}",
  "blue: λ⁺, the next collision · yellow: W, neutron escape": "青：λ⁺、次の衝突 · 黄：W、中性子の脱出",
  "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
  // scene 3: master equation
  "compound": "複合核",
  "(of {#} % in the end)": "（最終的には{#} %）",
  "emitted before equilibrium: {#} % (of {#} % in the end)": "平衡前に放出：{#} %（最終的には{#} %）",
  "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
  // scene 4: spectrum
  "outgoing neutron energy ε (MeV)": "出射中性子のエネルギー ε（MeV）",
  "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
  "evaporation": "蒸発",
  "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV：{#} %が n = {#} から",
  "pre-equilibrium {#} % of the emission · solid: total": "前平衡は放出の{#} % · 実線：合計",
  // scene 5: share
  "{#} MeV": "{#} MeV",
  "pre-equilibrium share of the emission": "放出に占める前平衡の割合",
  "{#} MeV: {#} %": "{#} MeV：{#} %",
  "C₁ = {#} (dashed: {#})": "C₁ = {#}（破線：{#}）",
  // scene 6: second escape
  "{#} MeV: multiple pre-equilibrium on": "{#} MeV：多重前平衡放出オン",
  "chance of a second fast emission (toy estimate)": "2度目の速い放出の確率（簡易な見積もり）",
  "(2 particles, 1 hole)": "（粒子2個、空孔1個）", "(1 particle, 1 hole)": "（粒子1個、空孔1個）",
  "residual: {#}p{#}h": "残留核：{#}p{#}h",
});
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "never-come-back近似", aliases: ["never-come-back近似", "never-come-back"],
    short: "平衡化の初期には、衝突は粒子・空孔対を増やすだけで、減らすことはないとする近似です。",
    more: "これによりマスター方程式は、段階ごとに積分できる単純な連鎖になります。エキシトン数が平衡値よりはるかに小さいあいだ、つまり前平衡放出が起こる領域で成り立ちます。",
    chapter: "exciton",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="pauli" */

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "({#} particles, {#} hole)": "（粒子 {#}、空孔 {#}）",
  "({#} particle, {#} hole)": "（粒子 {#}、空孔 {#}）",
});
