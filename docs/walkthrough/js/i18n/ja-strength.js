/* Japanese: strength (第25章、光子強度関数の詳細) */
WT.L.ch.strength = {
  num: "第25章", title: "光子強度関数を詳しく", short: "光子強度関数",
  lead: "第10章では、熱い原子核がどんな光子を好むかを見ました。この章では強度関数を式で書き下し、それを透過係数と平均放射幅へとたどり、それが駆動するカスケードを走らせます。",
  html: `
<div class="step">
  <h3>E1：巨大双極子共鳴の裾</h3>
  <p><b>光子強度関数</b><i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>)は、型<i>XL</i>（電気双極子E1、磁気双極子M1など）の光子に対する平均の換算確率です。E1では18 MeV付近の巨大双極子共鳴が支配的ですが、<i>S<sub>n</sub></i>での崩壊に使われるのは1〜7 MeVの光子で、その裾のはるか下のほうです。裾の形こそが問題のすべてです。</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">終状態の温度 T（MeV）</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>破線は標準ローレンツ型（SLO）で、光吸収に当てはめた形です。幅が一定なので、崩壊の窓での強度を2〜5倍過大に評価します。球形核について古くから知られている欠点です。実線は簡略化修正ローレンツ型（<b>SMLO</b>）です。その幅は光子エネルギーと終状態の温度とともに大きくなるので、窓の中の裾は下がりますが、光子エネルギーがゼロでも有限の強度が残ります。崩壊データはそれを必要としています。拡大枠は2 MeVより下のその床を示しています。<i>T</i>を0まで動かすと、床は消えます。</p>
</div>
<div class="step">
  <h3>M1：スピン反転、シザーズ、アップベンド</h3>
  <p>M1の強度はE1より弱いものの、無視はできません。41<i>A</i><sup>−1/3</sup> MeV付近のスピン反転共鳴、変形核で3 MeV付近に現れるシザーズモード（強度はβ²に比例して増える）、そしてアップベンド、すなわちオスロ法のデータと殻模型計算に見られる、光子エネルギーゼロへ向かう上昇です。</p>
  <div class="ctl"><label for="ps-b">変形 β（シザーズ）</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">アップベンド</button></div>
  <p>背後の薄い線はE1です。最も低い光子エネルギー、ここでは約2 MeVより下では、アップベンドによってM1がE1に匹敵するか上回ることがあり（マーカーがその位置を示します）、そのためカスケードの柔らかい端や、安定から遠い原子核の捕獲で重要になります。エンジンの既定のM1は、アップベンドを含むIAEAの推奨値を原子核ごとに表にしたもので、既定のE1は表になったSMLO-2019です。ここでの閉じた式は、それらの表の代わりに使っています。</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p><b>Brink–Axel仮説</b>は、強度は光子エネルギーに依存し、原子核がどこから出発するかには依存しないというものです。<i>S<sub>n</sub></i>にある共鳴にも、4 MeVにある状態にも同じ<i>f</i>が成り立ちます（SMLOは<i>T</i>を通じて弱い依存性を残します）。すると各出発エネルギーからの放出は、透過係数と終状態の密度の積で決まります。</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">出発エネルギー Eₓ（MeV）</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>増加する<i>E</i><sub>γ</sub>³<i>f</i>と減少するρの積は、こぶになります。<i>S<sub>n</sub></i>からでは、ここでは4〜5 MeV付近にピークがあります。それより低い出発点では、出発エネルギーで切れます。接続エネルギーより下ではρが定温度模型の指数関数なので、形はどの出発点からも同じで、切り詰められるだけです。この仮説は、異なる励起エネルギーで取り出した強度を比べることで検証できます。オスロ型の解析が行っているのはまさにそれです。</p>
</div>
<div class="step">
  <h3>平均放射幅</h3>
  <p>s波共鳴（スピン0の標的で<i>J</i><sup>π</sup> = ½⁺）からE1またはM1で到達できるすべての終状態について足し合わせると、それらの平均の全光子幅が得られます。これは数百の原子核について共鳴の形から測定されており、<i>S<sub>n</sub></i>での強度の主な検証手段です。</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">強度にかける倍率</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="8" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>曲線は、幅が光子ごとにどこから来るかを示しています。大部分は3〜7 MeVで、大部分はE1であり、M1は約15 %を加えます。ここではエンジンの表の代わりに閉じた式と模式的な準位密度を使っているので、幅は測定値0.92 eVの約6分の1になります。幅は<i>S<sub>n</sub></i>より下の準位密度と強度の裾にそれほど敏感なのです。エンジンが従うTALYSの既定では、この原子核に対して約1.3 eVになります。スライダーは、評価で当てはめるような単一の全体因子をかけます。約×6で測定値の範囲に収まります。Γ<sub>γ</sub> ≪ Γ<sub>n</sub>のとき、keV領域の捕獲は⟨Γ<sub>γ</sub>⟩にほぼ比例するので、ここでの因子はそのまま(n,γ)の因子になります。TALYSは強度を測定された⟨Γ<sub>γ</sub>⟩に合わせて再規格化できます（<code>gnorm</code>）。INCOGNITAでは、カスケードのすべての原子核に適用するその再規格化は任意のスイッチで、既定ではオフです。</p>
</div>
<div class="step">
  <h3>カスケード</h3>
  <p>最初の光子の後も、同じ規則が繰り返されます。新しいエネルギーごとに次の光子を<i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>)から引き、原子核が既知の準位に達するまで続けます。1つの履歴は数個の光子からなり、それらを合計したスペクトルが、捕獲の後にカロリメータが見るものです。</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">アップベンド</button><button class="btn ghost" data-act="clear">最初からやり直す</button></div>
  <p>アップベンドは柔らかい光子を加え、多重度を少し増やします。エンジンは履歴を引きません。集団をビンからビンへ上から下へと動かすので（第11章）、サンプリングの雑音なしに同じ平均が得られます。</p>
  <div class="aside">コードでは：<code>gamma/strength.py</code>（TALYSが扱うすべての強度模型。既定はSMLO-2019の表と、アップベンドを含むIAEAのM1）、<code>gamma/parameters.py</code>（巨大共鳴の系統式、数表）、<code>gamma/transmission.py</code>（T = 2π E<sup>2L+1</sup> f）、<code>gamma/ggnorm.py</code>（任意：⟨Γγ⟩の規格化）、<code>emission/</code>（カスケード）。図は鉄57に似た原子核について、閉じた式と系統式を使っています。測定された⟨Γγ⟩は⁵⁷FeのRIPL値です。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "Eγ (MeV)": "Eγ (MeV)", "{#} eV": "{#} eV", "Sₙ": "Sₙ",
  // scene 1: E1
  "E{#} strength f (MeV⁻³), A = {#}": "E{#}強度 f（MeV⁻³）、A = {#}",
  "photons that decay uses": "崩壊が使う光子",
  "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR：E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb",
  "dashed: SLO": "破線：SLO",
  "at {#} MeV: SMLO / SLO = {#}": "{#} MeVで SMLO / SLO = {#}",
  "protons against neutrons": "中性子に対して振動する陽子",
  // scene 2: M1
  "M{#} strength f (MeV⁻³), A = {#}": "M{#}強度 f（MeV⁻³）、A = {#}",
  "spin-flip": "スピン反転",
  "scissors, β = {#}": "シザーズ、β = {#}",
  "upbend": "アップベンド",
  "faint: E{#} at T = {#} MeV": "薄い線：E{#}（T = {#} MeV）",
  "M{#} > E{#} below {#} MeV": "M{#} > E{#}（{#} MeV以下）",
  "E{#} dominates at every energy here": "ここではすべてのエネルギーでE{#}が優勢",
  "scissors: the two deformed clouds rock": "シザーズ：変形した2つの雲が揺れ合う",
  // scene 3: Brink-Axel
  "from {#} MeV": "{#} MeVから",
  "peak at Eγ ≈ {#} MeV": "ピーク Eγ ≈ {#} MeV",
  "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "一次スペクトル T(Eγ) ρ(Eₓ − Eγ)、それぞれピークで規格化",
  // scene 4: <Gamma_gamma>
  "share of ⟨Γγ⟩ per MeV of photon energy": "光子エネルギー1 MeVあたりの⟨Γγ⟩への寄与",
  "E{#} (yellow), M{#} (purple, on top)": "E{#}（黄）、M{#}（紫、上に積む）",
  "zoom: Eγ from 0 to 2 MeV": "拡大：Eγ 0〜2 MeV",
  "floor: stays above zero": "床：ゼロより上に残る", "T = {#}: no floor": "T = {#}：床なし",
  "continuum:": "連続領域：", "dark = dense": "濃い = 高密度", "known levels": "既知の準位", "continuum": "連続領域",
  "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "光子エネルギー1 MeVあたりの⟨Γγ⟩への寄与：E{#}（黄）、M{#}（紫、上に積む）",
  "measured {#} eV": "測定値 {#} eV",
  "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "計算値 ⟨Γγ⟩ = {#} meV（E{#} {#} %、M{#} {#} %）",
  // scene 5: cascades
  "all photons from all cascades": "全カスケードの全光子",
  "{#} cascades · mean multiplicity {#}": "カスケード{#}回 · 平均多重度 {#}",
});
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "簡略化修正ローレンツ型。幅が光子エネルギーと終状態の温度とともに大きくなるE1強度関数です。",
    more: "V. Plujkoらが提案し、IAEAの光子強度関数データベース（2019年）ですべての原子核について表になっています。エンジンの既定のE1は、TALYS-2と同じくそのSMLO-2019の表です。",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Brink–Axel仮説", aliases: ["Brink–Axel仮説", "Brink–Axel"],
    short: "光子強度関数は光子エネルギーだけに依存し、光子を放出する状態の励起エネルギーには依存しないという仮定です。",
    more: "これにより、基底状態について測定または計算した1つの強度で、カスケード全体をまかなえます。異なる励起エネルギーで強度を取り出すことで検証され、近似的には成り立ちますが、特定の原子核やエネルギーでのずれについては議論があります。",
    chapter: "strength",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="up" data-act="up2" */

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "zoom: Eγ from {#} to {#} MeV": "拡大：Eγ {#}～{#} MeV",
});
