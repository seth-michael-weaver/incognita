/* Japanese: breeding (新しい燃料の増殖) */
WT.L.ch.breeding = {
  num: "レッスン 1", title: "新しい燃料の増殖", short: "増殖",
  html: `
<div class="step">
  <h3>親物質が核分裂性物質になる</h3>
  <p>ウラン238はほとんど分裂しませんが、中性子を捕獲することはできます。そのあと2回のベータ崩壊（そのたびに内部の中性子1個が陽子に変わります）を経ると、分裂しやすいプルトニウム239になります。トリウム232も同じようにしてウラン233になります。</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">ウラン238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">トリウム232</button></div>
</div>
<div class="step">
  <h3>中性子の収支</h3>
  <p>核分裂性燃料に吸収された中性子1個は、<i>η</i>個の新しい中性子を返します。1個は次の核分裂を起こさなければならず、いくつかは失われます。残った分が増殖に使えます。ウラン235と遅い中性子では、燃えた1個あたり新しい核分裂性原子核は約0.6個しかできません。</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">遅い中性子</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">高速中性子</button></div>
</div>
<div class="step">
  <h3>高速中性子で増殖する</h3>
  <p>増殖するには、1個の中性子が連鎖を続け、少なくとも1個が新しい燃料をつくらなければなりません。したがって<i>η</i>は2を損失分より大きく上回る必要があります。高速炉のプルトニウム239では約2.4となり、十分な余裕があります。</p>
  <div class="ctl"><label for="br-l1">失われる中性子</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>遅い中性子でのトリウム</h3>
  <p>遅い中性子では、プルトニウム239は約2.1にとどまりますが、ウラン233は2.29になります。この余裕があるので、中性子の無駄をごく少なくすれば、トリウム炉は遅い中性子でも増殖できます。増殖するまで損失を下げてみましょう。</p>
  <div class="ctl"><label for="br-l2">失われる中性子</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>転換比</h3>
  <p>転換比は、燃えた核分裂性原子核1個あたりにつくられる核分裂性原子核の数です。1より小さければ燃料は少しずつ減っていきます（転換炉。現在の軽水炉がこれにあたります）。1より大きければ、原子炉は最初より多くの燃料をもって運転を終えます（増殖炉）。</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">遅い中性子</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">高速中性子</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "+ n": "+ n",
  "Np{#}": "Np{#}",
  "Pa{#}": "Pa{#}",
  "Pu{#}": "Pu{#}",
  "Th{#}": "Th{#}",
  "U{#}": "U{#}",
  "Th{#} (fertile)": "Th{#}（親物質）",
  "U{#} (fertile)": "U{#}（親物質）",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "a batch of {a} waiting · day {b}": "{a} の一群が待機中 · {b} 日目",
  "{a} waiting: day {b}": "{a} 待機中：{b} 日目",
  "after {#} months, {#} % has become U{#}": "{#} か月後、{#} % が U{#} に",
  "after {#} weeks, {#} % has become Pu{#}": "{#} 週間後、{#} % が Pu{#} に",
  "antineutrino": "反ニュートリノ",
  "electron": "電子",
  "e⁻": "e⁻",
  "breed": "増殖",
  "chain": "連鎖",
  "lost": "損失",
  "catch": "捕獲",
  "breeds: Th{#} → U{#}": "増殖：Th{#} → U{#}",
  "breeds: U{#} → Pu{#}": "増殖：U{#} → Pu{#}",
  "burned {a}": "燃焼 {a}",
  "made {a}": "生成 {a}",
  "conversion ratio {a}: a breeder": "転換比 {a}：増殖炉",
  "conversion ratio {a}: a converter": "転換比 {a}：転換炉",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "転換比 ≈ η − {#} − 損失 = {a}：増殖",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "転換比 ≈ η − {#} − 損失 = {a}：増殖、燃やすより多くの燃料をつくる",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "転換比 ≈ η − {#} − 損失 = {a}：転換",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "転換比 ≈ η − {#} − 損失 = {a}：転換、燃やすより少ない燃料しかつくらない",
  "fast neutrons": "高速中性子",
  "slow neutrons": "遅い中性子",
  "{a} · fast neutrons": "{a} · 高速中性子",
  "{a} · slow neutrons": "{a} · 遅い中性子",
  "fertile": "親物質",
  "fertile: barely splits": "親物質：ほとんど分裂しない",
  "fissile": "核分裂性",
  "fissile: splits easily": "核分裂性：分裂しやすい",
  "illustration": "イメージ図",
  "lost: water, steel, poisons, leakage": "損失：水、鋼、毒物質、漏れ",
  "neutrons out per neutron absorbed in the fuel": "燃料に吸収された中性子1個あたりに出る中性子",
  "neutrons per absorption": "吸収あたりの中性子",
  "next fission": "次の核分裂",
  "next fission: keeps the chain going": "次の核分裂：連鎖を続ける",
  "slow step: Np{#}, half-life {#} d": "遅い段階：Np{#}、半減期 {#} 日",
  "slow step: Pa{#}, half-life {#} d": "遅い段階：Pa{#}、半減期 {#} 日",
  "the slow step is Np{#} (half-life {#} days)": "遅い段階は Np{#}（半減期 {#} 日）",
  "the slow step is Pa{#} (half-life {#} days)": "遅い段階は Pa{#}（半減期 {#} 日）",
  "split": "分裂済み",
  "split (fission products)": "分裂済み（核分裂生成物）",
  "{#} d": "{#} 日",
  "{#} min": "{#} 分",
  "{#} p": "{#} p",
  "{#} protons": "陽子 {#} 個",
  "{#}: breeding line": "{#}：増殖ライン",
  "{a} % now {b}": "{a} % が {b} に",
  "{a} per absorption": "吸収あたり {a}",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
});
